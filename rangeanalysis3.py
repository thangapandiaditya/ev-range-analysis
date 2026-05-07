import pandas as pd
import streamlit as st

@st.cache_data
def process_ev_data(file, vehicle_type="turbo"):

    # ==============================
    # READ ONLY REQUIRED COLUMNS
    # ==============================
    columns_needed = [
        'batteryCurrent',
        'batteryStateOfCharge',
        'odometer',
        'batteryAvailableEnergy',
        'batteryTotalVoltage',
        'vehicleStatus'
    ]

    df = pd.read_excel(file, usecols=columns_needed)
    df = df.reset_index(drop=True)

    # ==============================
    # VEHICLE CONFIG
    # ==============================
    VEHICLE_PAYLOAD_FACTOR = {
        "turbo": 9.0909,
        "storm": 11.53846153846154,
        "hiload": 7.45
    }

    # ==============================
    # PARAMETERS
    # ==============================
    MIN_CURRENT = -0.5
    CHARGE_THRESHOLD = 5
    CHARGE_WINDOW = 30

    # ==============================
    # FIND TRIP START
    # ==============================
    start_index = None

    for i in range(1, len(df)):
        current = df.loc[i, 'batteryCurrent']
        odo_diff = df.loc[i, 'odometer'] - df.loc[i-1, 'odometer']

        if current < MIN_CURRENT and odo_diff > 0:
            start_index = i
            break

    if start_index is None:
        return None

    # BACKTRACK (include full start)
    for j in range(start_index, 0, -1):
        if df.loc[j, 'batteryStateOfCharge'] >= df.loc[start_index, 'batteryStateOfCharge']:
            start_index = j
        else:
            break

    # ==============================
    # FIND TRIP END
    # ==============================
    end_index = len(df) - 1

    for i in range(start_index, len(df) - CHARGE_WINDOW):
        window = df.loc[i:i+CHARGE_WINDOW]

        if (window['batteryCurrent'] > CHARGE_THRESHOLD).sum() > CHARGE_WINDOW * 0.7:
            end_index = i - 1
            break

    # ==============================
    # EXTRACT TRIP
    # ==============================
    trip = df.loc[start_index:end_index].reset_index(drop=True)

    # ==============================
    # CALCULATIONS
    # ==============================
    start_soc = trip['batteryStateOfCharge'].iloc[0]
    end_soc = trip['batteryStateOfCharge'].iloc[-1]
    soc_consumed = start_soc - end_soc

    start_odo = trip['odometer'].iloc[0]
    end_odo = trip['odometer'].iloc[-1]
    total_km = end_odo - start_odo

    start_energy = trip['batteryAvailableEnergy'].iloc[0]
    end_energy = trip['batteryAvailableEnergy'].iloc[-1]
    energy_consumed = start_energy - end_energy

    energy_per_km = energy_consumed / total_km if total_km > 0 else 0

    avg_current = trip['batteryCurrent'].mean()

    # ==============================
    # PAYLOAD
    # ==============================
    factor = VEHICLE_PAYLOAD_FACTOR.get(vehicle_type.lower(), 9.0909)
    payload = factor * energy_per_km

    # ==============================
    # MODE DISTANCE
    # ==============================
    mode_distance = {'Economy': 0, 'Thunder': 0, 'Rhino': 0}

    for i in range(1, len(trip)):
        mode = str(trip.loc[i-1, 'vehicleStatus']).lower()
        dist = trip.loc[i, 'odometer'] - trip.loc[i-1, 'odometer']

        if "eco" in mode:
            mode_distance['Economy'] += dist
        elif "thunder" in mode:
            mode_distance['Thunder'] += dist
        elif "rhino" in mode:
            mode_distance['Rhino'] += dist

    # ==============================
    # MILEAGE
    # ==============================
    approx_mileage_soc = (total_km / soc_consumed) * 100 if soc_consumed > 0 else None
    approx_mileage_energy = (start_energy / energy_per_km) if energy_per_km > 0 else None

    return {
        "start_soc": start_soc,
        "end_soc": end_soc,
        "soc_consumed": soc_consumed,
        "avg_current": avg_current,
        "total_km": total_km,
        "energy_per_km": energy_per_km,
        "payload": payload,
        "approx_mileage_soc": approx_mileage_soc,
        "approx_mileage_energy": approx_mileage_energy,
        "mode_distance": mode_distance
    }
