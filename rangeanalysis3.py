import pandas as pd

# ==============================
# MAIN FUNCTION (MULTI TRIP)
# ==============================
def process_ev_data(file, vehicle_type):

    df = pd.read_excel(file)

    # 🔁 Rename columns (adjust if needed)
    df = df.rename(columns={
        'SOC': 'batteryStateOfCharge',
        'Current': 'packCurrent',
        'Voltage': 'packVoltage',
        'Odo': 'odometer',
        'Energy': 'batteryEnergy',
        'Mode': 'driveMode',
        'Time': 'timestamp'
    })

    df = df.dropna().reset_index(drop=True)

    trips = []
    in_trip = False

    # ==============================
    # DETECT MULTIPLE DISCHARGE
    # ==============================
    for i in range(1, len(df)):

        current = df.loc[i, 'packCurrent']

        # START TRIP
        if not in_trip and current < 0:
            in_trip = True
            start_index = i

        # END TRIP
        elif in_trip and current >= 0:
            end_index = i

            trip_df = df.loc[start_index:end_index].copy()

            if len(trip_df) > 20:  # ignore noise
                trip = calculate_trip(trip_df, vehicle_type)
                if trip:
                    trips.append(trip)

            in_trip = False

    return trips


# ==============================
# SINGLE TRIP CALCULATION
# ==============================
def calculate_trip(df, vehicle_type):

    start_soc = df.iloc[0]['batteryStateOfCharge']
    end_soc = df.iloc[-1]['batteryStateOfCharge']
    soc_used = start_soc - end_soc

    start_odo = df.iloc[0]['odometer']
    end_odo = df.iloc[-1]['odometer']
    distance = end_odo - start_odo

    start_energy = df.iloc[0]['batteryEnergy']
    end_energy = df.iloc[-1]['batteryEnergy']
    energy_used = start_energy - end_energy

    avg_current = df['packCurrent'].mean()

    energy_per_km = energy_used / distance if distance > 0 else 0

    avg_voltage = df['packVoltage'].mean()

    # ==============================
    # PAYLOAD
    # ==============================
    payload_map = {
        "turbo": 14,
        "storm": 11.538,
        "hiload": 7.45
    }

    payload = energy_per_km * payload_map.get(vehicle_type, 14)

    # ==============================
    # MODE DISTANCE
    # ==============================
    eco = df[df['driveMode'] == 'Economy']['odometer'].diff().sum()
    thu = df[df['driveMode'] == 'Thunder']['odometer'].diff().sum()
    rhi = df[df['driveMode'] == 'Rhino']['odometer'].diff().sum()

    # ==============================
    # TIME
    # ==============================
    start_time = df.iloc[0]['timestamp']
    end_time = df.iloc[-1]['timestamp']

    return {
        "start_time": start_time,
        "end_time": end_time,
        "start_soc": start_soc,
        "end_soc": end_soc,
        "soc_used": soc_used,
        "distance": distance,
        "energy_per_km": energy_per_km,
        "payload": payload,
        "avg_current": avg_current,
        "mode": {
            "eco": eco if eco else 0,
            "thu": thu if thu else 0,
            "rhi": rhi if rhi else 0
        }
    }
