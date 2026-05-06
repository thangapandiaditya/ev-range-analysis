import pandas as pd

def process_ev_data(file, vehicle_type):

    df = pd.read_excel(file)

    # ==============================
    # CLEAN COLUMN NAMES
    # ==============================
    df.columns = df.columns.str.strip().str.lower()

    print("Detected Columns:", df.columns.tolist())  # DEBUG

    # ==============================
    # SAFE COLUMN DETECTION
    # ==============================
    def get_col(possible):
        for col in df.columns:
            for name in possible:
                if name in col:
                    return col
        return None

    soc_col = get_col(["soc"])
    current_col = get_col(["current"])
    voltage_col = get_col(["voltage"])
    odo_col = get_col(["odo"])
    energy_col = get_col(["energy"])
    mode_col = get_col(["mode"])
    time_col = get_col(["time", "date"])

    # ==============================
    # VALIDATION
    # ==============================
    if not soc_col or not current_col or not odo_col:
        raise Exception(f"""
❌ Required columns missing!

Detected columns:
{df.columns.tolist()}

👉 Make sure your file has:
- SOC
- Current
- ODO
""")

    # ==============================
    # RENAME SAFELY
    # ==============================
    df = df.rename(columns={
        soc_col: "batteryStateOfCharge",
        current_col: "packCurrent",
        odo_col: "odometer"
    })

    if voltage_col:
        df.rename(columns={voltage_col: "packVoltage"}, inplace=True)
    if energy_col:
        df.rename(columns={energy_col: "batteryEnergy"}, inplace=True)
    if mode_col:
        df.rename(columns={mode_col: "driveMode"}, inplace=True)
    if time_col:
        df.rename(columns={time_col: "timestamp"}, inplace=True)

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

        if not in_trip and current < START_THRESHOLD:
            in_trip = True
            start_index = i

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
# CALCULATE TRIP
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

    energy_used = 0
    if "batteryEnergy" in df:
        energy_used = df.iloc[0]['batteryEnergy'] - df.iloc[-1]['batteryEnergy']

    avg_current = df['packCurrent'].mean()
    energy_per_km = energy_used / distance if distance > 0 else 0

    payload_map = {
        "turbo": 14,
        "storm": 11.538,
        "hiload": 7.45
    }

    payload = energy_per_km * payload_map.get(vehicle_type, 14)

    eco = thu = rhi = 0

    if "driveMode" in df:
        eco = df[df['driveMode'].str.lower() == 'economy']['odometer'].diff().sum()
        thu = df[df['driveMode'].str.lower() == 'thunder']['odometer'].diff().sum()
        rhi = df[df['driveMode'].str.lower() == 'rhino']['odometer'].diff().sum()

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
