import pandas as pd

def process_ev_data(file_path):
    df = pd.read_excel(file_path)
    df = df.reset_index(drop=True)

    # ==============================
    # PARAMETERS
    # ==============================
    MIN_CURRENT = -0.5
    CHARGE_THRESHOLD = 5
    CHARGE_WINDOW = 30

    # ==============================
    # 1. FIND REAL TRIP START
    # ==============================
    start_index = None

    for i in range(1, len(df)):
        current = df.loc[i, 'batteryCurrent']
        odo_diff = df.loc[i, 'odometer'] - df.loc[i-1, 'odometer']

        if current < MIN_CURRENT and odo_diff > 0:
            start_index = i
            break

    if start_index is None:
        print("❌ No valid trip start found")
        return None

    # ==============================
    # 2. BACKTRACK TO GET FULL START
    # ==============================
    for j in range(start_index, 0, -1):
        if df.loc[j, 'batteryStateOfCharge'] >= df.loc[start_index, 'batteryStateOfCharge']:
            start_index = j
        else:
            break

    # ==============================
    # 3. FIND TRIP END (CHARGING)
    # ==============================
    end_index = len(df) - 1

    for i in range(start_index, len(df) - CHARGE_WINDOW):
        window = df.loc[i:i+CHARGE_WINDOW]

        if (window['batteryCurrent'] > CHARGE_THRESHOLD).sum() > CHARGE_WINDOW * 0.7:
            end_index = i - 1
            break

    # ==============================
    # 4. EXTRACT FULL TRIP
    # ==============================
    trip = df.loc[start_index:end_index].reset_index(drop=True)

    print("\nDEBUG FULL TRIP:")
    print("Rows:", len(trip))
    print("Start SOC:", trip['batteryStateOfCharge'].iloc[0])
    print("End SOC:", trip['batteryStateOfCharge'].iloc[-1])

    # ==============================
    # 5. MAIN CALCULATIONS (FULL TRIP)
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

    energy_per_km = energy_consumed / total_km if total_km != 0 else 0

    start_voltage = trip['batteryTotalVoltage'].iloc[0]
    end_voltage = trip['batteryTotalVoltage'].iloc[-1]
    avg_voltage = trip['batteryTotalVoltage'].mean()

    payload = 9.0909 * energy_per_km

    # ==============================
    # 6. AVERAGE CURRENT (FULL TRIP)
    # ==============================
    avg_current = trip['batteryCurrent'].mean()

    # ==============================
    # 7. MODE-WISE DISTANCE
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
    # 8. APPROX MILEAGE (SOC BASED)
    # ==============================
    approx_mileage_soc = (total_km / soc_consumed) * 100 if soc_consumed != 0 else 0

    # ==============================
    # 9. APPROX MILEAGE (ENERGY)
    # ==============================
    approx_mileage_energy = (start_energy / energy_per_km) if energy_per_km != 0 else 0

    # ==============================
    # 10. OUTPUT (DEBUG)
    # ==============================
    print("\n========== EV RANGE ANALYSIS ==========")

    print(f"Start SOC: {start_soc:.2f}")
    print(f"End SOC: {end_soc:.2f}")
    print(f"SOC Consumed: {soc_consumed:.2f}")

    print(f"\nAverage Current: {avg_current:.2f}")

    print(f"\nStart Odometer: {start_odo:.2f}")
    print(f"End Odometer: {end_odo:.2f}")
    print(f"Total Distance (km): {total_km:.2f}")

    print(f"\nStart Energy: {start_energy:.2f}")
    print(f"End Energy: {end_energy:.2f}")
    print(f"Energy Consumed: {energy_consumed:.2f}")

    print(f"\nEnergy per km: {energy_per_km:.4f}")

    print(f"\nStart Voltage: {start_voltage:.2f}")
    print(f"End Voltage: {end_voltage:.2f}")
    print(f"Average Voltage: {avg_voltage:.2f}")

    print(f"\nPayload: {payload:.2f}")

    print(f"\nApprox Mileage (SOC): {approx_mileage_soc:.2f} km")
    print(f"Approx Mileage (Energy): {approx_mileage_energy:.2f} km")

    print("\n------ Mode-wise Distance ------")
    for mode, dist in mode_distance.items():
        print(f"{mode}: {dist:.2f} km")

    print("=====================================")

    # ==============================
    # 11. RETURN VALUES (FOR FRONTEND)
    # ==============================
    return {
        "start_soc": start_soc,
        "end_soc": end_soc,
        "soc_consumed": soc_consumed,
        "avg_current": avg_current,
        "start_odo": start_odo,
        "end_odo": end_odo,
        "total_km": total_km,
        "start_energy": start_energy,
        "end_energy": end_energy,
        "energy_consumed": energy_consumed,
        "energy_per_km": energy_per_km,
        "start_voltage": start_voltage,
        "end_voltage": end_voltage,
        "avg_voltage": avg_voltage,
        "payload": payload,
        "approx_mileage_soc": approx_mileage_soc,
        "approx_mileage_energy": approx_mileage_energy,
        "mode_distance": mode_distance
    }