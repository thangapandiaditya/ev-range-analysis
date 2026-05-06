import pandas as pd

# ==============================
# MAIN FUNCTION
# ==============================
def process_ev_data(file, vehicle_type):

    df = pd.read_excel(file)

    # ==============================
    # CLEAN COLUMN NAMES
    # ==============================
    df.columns = df.columns.str.strip().str.lower()

    # ==============================
    # AUTO DETECT COLUMNS
    # ==============================
    column_map = {
        "batteryStateOfCharge": ["soc", "battery soc", "stateofcharge"],
        "packCurrent": ["current", "pack current", "battery current"],
        "packVoltage": ["voltage", "pack voltage"],
        "odometer": ["odo", "odometer"],
        "batteryEnergy": ["energy", "battery energy"],
        "driveMode": ["mode", "drive mode"],
        "timestamp": ["time", "timestamp", "date"]
    }

    def find_column(possible_names):
        for name in possible_names:
            for col in df.columns:
                if name in col:
                    return col
        return None

    mapped = {}
    for key, names in column_map.items():
        col = find_column(names)
        if col:
            mapped[key] = col

    # ==============================
    # REQUIRED CHECK
    # ==============================
    required = ["packCurrent", "batteryStateOfCharge", "odometer"]

    for r in required:
        if r not in mapped:
            raise Exception(f"Missing column: {r}")

    # ==============================
    # RENAME
    # ==============================
    df = df.rename(columns={
        mapped.get("batteryStateOfCharge"): "batteryStateOfCharge",
        mapped.get("packCurrent"): "packCurrent",
        mapped.get("packVoltage"): "packVoltage",
        mapped.get("odometer"): "odometer",
        mapped.get("batteryEnergy"): "batteryEnergy",
        mapped.get("driveMode"): "driveMode",
        mapped.get("timestamp"): "timestamp"
    })

    df = df.dropna().reset_index(drop=True)

    # ==============================
    # MULTI TRIP DETECTION
    # ==============================
    trips = []
    in_trip = False

    START_THRESHOLD = -2
    END_THRESHOLD = -1

    for i in range(1, len(df)):

        current = df.loc[i, 'packCurrent']

        # START
        if not in_trip and current < START_THRESHOLD:
            in_trip = True
            start_index = i

        # END
        elif in_trip and current > END_THRESHOLD:
            end_index = i

            trip_df = df.loc[start_index:end_index].copy()

            if len(trip_df) > 30:
                trip = calculate_trip(trip_df, vehicle_type)
                if trip:
                    trips.append(trip)

            in_trip = False

    # LAST TRIP FIX
    if in_trip:
        trip_df = df.loc[start_index:].copy()
        if len(trip_df) > 30:
            trip = calculate_trip(trip_df, vehicle_type)
            if trip:
                trips.append(trip)

    return trips


# ==============================
# CALCULATE SINGLE TRIP
# ==============================
def calculate_trip(df, vehicle_type):

    start_soc = df.iloc[0]['batteryStateOfCharge']
    end_soc = df.iloc[-1]['batteryStateOfCharge']
    soc_used = start_soc - end_soc

    start_odo = df.iloc[0]['odometer']
    end_odo = df.iloc[-1]['odometer']
    distance = end_odo - start_odo

    if distance < 1:
        return None

    start_energy = df.iloc[0].get('batteryEnergy', 0)
    end_energy = df.iloc[-1].get('batteryEnergy', 0)
    energy_used = start_energy - end_energy

    avg_current = df['packCurrent'].mean()
    energy_per_km = energy_used / distance if distance > 0 else 0

    payload_map = {
        "turbo": 14,
        "storm": 11.538,
        "hiload": 7.45
    }

    payload = energy_per_km * payload_map.get(vehicle_type, 14)

    eco = df[df['driveMode'] == 'economy']['odometer'].diff().sum() if 'driveMode' in df else 0
    thu = df[df['driveMode'] == 'thunder']['odometer'].diff().sum() if 'driveMode' in df else 0
    rhi = df[df['driveMode'] == 'rhino']['odometer'].diff().sum() if 'driveMode' in df else 0

    start_time = df.iloc[0].get('timestamp', '')
    end_time = df.iloc[-1].get('timestamp', '')

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
