import pandas as pd
import tkinter as tk
from tkinter import filedialog

def process_ev_data(file_path):
    df = pd.read_excel(file_path)

    # Keep order (VERY IMPORTANT)
    df = df.reset_index(drop=True)

    # ==============================
    # 1. FILTER ALL NEGATIVE VALUES
    # ==============================
    df_filtered = df[df['batteryCurrent'] < 0].copy()

    if len(df_filtered) == 0:
        print("❌ No negative values found")
        return

    # ==============================
    # 🔥 FIX: USE MAX & MIN SOC
    # ==============================
    start_soc = df_filtered['batteryStateOfCharge'].max()
    end_soc = df_filtered['batteryStateOfCharge'].min()
    soc_consumed = start_soc - end_soc

    # ==============================
    # AVERAGE CURRENT
    # ==============================
    avg_current = df_filtered['batteryCurrent'].mean()

    # ==============================
    # DISTANCE (IMPORTANT FIX)
    # ==============================
    start_odo = df_filtered['odometer'].min()
    end_odo = df_filtered['odometer'].max()
    total_km = end_odo - start_odo

    # ==============================
    # ENERGY
    # ==============================
    start_energy = df_filtered['batteryAvailableEnergy'].max()
    end_energy = df_filtered['batteryAvailableEnergy'].min()
    energy_consumed = start_energy - end_energy

    energy_per_km = energy_consumed / total_km if total_km != 0 else 0

    # ==============================
    # PAYLOAD
    # ==============================
    payload = 9.0909 * energy_per_km

    # ==============================
    # MODE DISTANCE (ROW-WISE)
    # ==============================
    mode_distance = {'Economy': 0, 'Thunder': 0, 'Rhino': 0}

    for i in range(1, len(df_filtered)):
        mode = str(df_filtered.iloc[i-1]['vehicleStatus']).lower()
        dist = df_filtered.iloc[i]['odometer'] - df_filtered.iloc[i-1]['odometer']

        if "eco" in mode:
            mode_distance['Economy'] += dist
        elif "thunder" in mode:
            mode_distance['Thunder'] += dist
        elif "rhino" in mode:
            mode_distance['Rhino'] += dist

    # ==============================
    # MILEAGE
    # ==============================
    approx_mileage_soc = (total_km / soc_consumed) * 100 if soc_consumed != 0 else 0
    approx_mileage_energy = (start_energy / energy_per_km) if energy_per_km != 0 else 0

    # ==============================
    # OUTPUT
    # ==============================
    print("\n========== EV RANGE ANALYSIS ==========")

    print(f"Start SOC: {start_soc}")
    print(f"End SOC: {end_soc}")
    print(f"SOC Consumed: {soc_consumed:.2f}")

    print(f"\nAverage Current: {avg_current:.2f}")

    print(f"\nTotal Distance (km): {total_km:.2f}")

    print(f"\nEnergy Consumed: {energy_consumed:.2f}")
    print(f"Energy/km: {energy_per_km:.4f}")

    print(f"\nPayload: {payload:.2f}")

    print(f"\nApprox Mileage (SOC): {approx_mileage_soc:.2f} km")
    print(f"Approx Mileage (Energy): {approx_mileage_energy:.2f} km")

    print("\n------ Mode-wise Distance ------")
    for mode, dist in mode_distance.items():
        print(f"{mode}: {dist:.2f} km")

    print("=====================================")


# FILE PICKER
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Select Excel File",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )

    if file_path:
        process_ev_data(file_path)
    else:
        print("❌ No file selected")