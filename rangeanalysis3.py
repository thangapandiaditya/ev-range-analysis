import pandas as pd
import streamlit as st

@st.cache_data
def process_ev_data(file, vehicle_type="turbo"):

    df = pd.read_excel(file)
    df = df.reset_index(drop=True)

    # ==============================
    # CONFIG
    # ==============================
    VEHICLE_PAYLOAD_FACTOR = {
        "turbo": 9.0909,
        "storm": 11.53846153846154,
        "hiload": 7.45
    }

    # ==============================
    # PARAMETERS (IMPORTANT)
    # ==============================
    MIN_SOC_DROP = 0.2
    MIN_DISTANCE = 1

    trips = []
    start_index = 0

    # ==============================
    # MULTI TRIP SPLIT (SOC BASED)
    # ==============================
    for i in range(1, len(df)):

        soc_now = df.loc[i, 'batteryStateOfCharge']
        soc_prev = df.loc[i-1, 'batteryStateOfCharge']

        odo_now = df.loc[i, 'odometer']
        odo_prev = df.loc[i-1, 'odometer']

        # CONDITION → SOC INCREASE (charging or reset)
        if soc_now > soc_prev + MIN_SOC_DROP:

            end_index = i - 1

            trip_df = df.loc[start_index:end_index].reset_index(drop=True)

            if len(trip_df) > 30:
                result = calculate_trip(trip_df, vehicle_type)
                if result:
                    trips.append(result)

            start_index = i

    # LAST TRIP
    trip_df = df.loc[start_index:].reset_index(drop=True)
    if len(trip_df) > 30:
        result = calculate_trip(trip_df, vehicle_type)
        if result:
            trips.append(result)

    return trips


# ==============================
# SAME CALCULATION (NO CHANGE)
# ==============================
def calculate_trip(trip, vehicle_type):

    start_soc = trip['batteryStateOfCharge'].iloc[0]
    end_soc = trip['batteryStateOfCharge'].iloc[-1]
    soc_consumed = start_soc - end_soc

    start_odo = trip['odometer'].iloc[0]
    end_odo = trip['odometer'].iloc[-1]
    total_km = end_odo - start_odo

    if total_km < 1:
        return None

    start_energy = trip['batteryAvailableEnergy'].iloc[0]
    end_energy = trip['batteryAvailableEnergy'].iloc[-1]
    energy_consumed = start_energy - end_energy

    energy_per_km = energy_consumed / total_km if total_km > 0 else 0
    avg_current = trip['batteryCurrent'].mean()

    VEHICLE_PAYLOAD_FACTOR = {
        "turbo": 9.0909,
        "storm": 11.53846153846154,
        "hiload": 7.45
    }

    payload = VEHICLE_PAYLOAD_FACTOR.get(vehicle_type.lower(), 9.0909) * energy_per_km

    # MODE DISTANCE
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
