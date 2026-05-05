import streamlit as st
from rangeanalysis3 import process_ev_data
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="EV Dashboard", layout="wide")

# ==============================
# 🎨 PREMIUM CSS
# ==============================
st.markdown("""
<style>
body {
    background-color: #0f172a;
}

.metric-card {
    background-color: #1e293b;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    color: white;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
}

.section-title {
    font-size: 22px;
    font-weight: bold;
    margin-top: 20px;
    color: #38bdf8;
}

.footer {
    text-align: center;
    padding: 20px;
    color: gray;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# HEADER
# ==============================
st.title("🚗 EV Range Analysis Dashboard")
st.caption("Developed by Aditya Thangapandi")

# ==============================
# SIDEBAR
# ==============================
st.sidebar.header("⚙ Settings")

vehicle_type = st.sidebar.selectbox(
    "Select Vehicle",
    ["turbo", "storm", "hiload"]
)

uploaded_files = st.sidebar.file_uploader(
    "Upload Excel Files",
    type=["xlsx", "xls"],
    accept_multiple_files=True
)

# ==============================
# REPORT FUNCTION
# ==============================
def generate_excel_report(results):
    df = pd.DataFrame({
        "Metric": [
            "Start SOC","End SOC","SOC Used","Avg Current",
            "Distance","Energy/km","Payload",
            "Mileage (SOC)","Mileage (Energy)",
            "Economy KM","Thunder KM","Rhino KM"
        ],
        "Value": [
            results['start_soc'], results['end_soc'],
            results['soc_consumed'], results['avg_current'],
            results['total_km'], results['energy_per_km'],
            results['payload'],
            results['approx_mileage_soc'],
            results['approx_mileage_energy'],
            results['mode_distance']['Economy'],
            results['mode_distance']['Thunder'],
            results['mode_distance']['Rhino']
        ]
    })

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)

    return output.getvalue()

# ==============================
# MAIN
# ==============================
if uploaded_files:

    if st.button("🚀 Run Analysis"):

        all_results = []

        for file in uploaded_files:
            with st.spinner(f"Processing {file.name}..."):
                result = process_ev_data(file, vehicle_type)

                if result:
                    result["file_name"] = file.name
                    all_results.append(result)

        if len(all_results) == 0:
            st.error("No valid trips detected")
        else:
            st.success("✅ Analysis Complete")

            # ==============================
            # SHOW FIRST TRIP (DETAIL VIEW)
            # ==============================
            results = all_results[0]

            st.markdown('<p class="section-title">📊 Trip Overview</p>', unsafe_allow_html=True)

            col1, col2, col3, col4 = st.columns(4)

            col1.markdown(f'<div class="metric-card">Start SOC<br><b>{results["start_soc"]:.2f}%</b></div>', unsafe_allow_html=True)
            col2.markdown(f'<div class="metric-card">End SOC<br><b>{results["end_soc"]:.2f}%</b></div>', unsafe_allow_html=True)
            col3.markdown(f'<div class="metric-card">Distance<br><b>{results["total_km"]:.2f} km</b></div>', unsafe_allow_html=True)
            col4.markdown(f'<div class="metric-card">Payload<br><b>{results["payload"]:.2f}</b></div>', unsafe_allow_html=True)

            col5, col6, col7, col8 = st.columns(4)

            col5.markdown(f'<div class="metric-card">Energy/km<br><b>{results["energy_per_km"]:.2f}</b></div>', unsafe_allow_html=True)
            col6.markdown(f'<div class="metric-card">SOC Used<br><b>{results["soc_consumed"]:.2f}</b></div>', unsafe_allow_html=True)
            col7.markdown(f'<div class="metric-card">Avg Current<br><b>{results["avg_current"]:.2f} A</b></div>', unsafe_allow_html=True)
            col8.markdown(f'<div class="metric-card">Mileage<br><b>{results["approx_mileage_energy"]:.2f if results["approx_mileage_energy"] else 0}</b></div>', unsafe_allow_html=True)

            # ==============================
            # MODE ANALYSIS
            # ==============================
            st.markdown('<p class="section-title">⚙ Mode-wise Performance</p>', unsafe_allow_html=True)

            total = results['total_km']

            eco_km = results['mode_distance']['Economy']
            thu_km = results['mode_distance']['Thunder']
            rhi_km = results['mode_distance']['Rhino']

            eco = (eco_km / total) * 100 if total else 0
            thu = (thu_km / total) * 100 if total else 0
            rhi = (rhi_km / total) * 100 if total else 0

            colA, colB, colC = st.columns(3)

            colA.markdown(f'<div class="metric-card">Economy<br><b>{eco_km:.2f} km</b><br>{eco:.1f}%</div>', unsafe_allow_html=True)
            colB.markdown(f'<div class="metric-card">Thunder<br><b>{thu_km:.2f} km</b><br>{thu:.1f}%</div>', unsafe_allow_html=True)
            colC.markdown(f'<div class="metric-card">Rhino<br><b>{rhi_km:.2f} km</b><br>{rhi:.1f}%</div>', unsafe_allow_html=True)

            # ==============================
            # MULTI-TRIP COMPARISON
            # ==============================
            st.markdown('<p class="section-title">📊 Multi-Trip Comparison</p>', unsafe_allow_html=True)

            comparison_data = []

            for r in all_results:
                comparison_data.append({
                    "Trip": r["file_name"],
                    "Distance": round(r["total_km"], 2),
                    "Energy/km": round(r["energy_per_km"], 2),
                    "Mileage": round(r["approx_mileage_energy"], 2) if r["approx_mileage_energy"] else 0
                })

            df_compare = pd.DataFrame(comparison_data)
            st.dataframe(df_compare, use_container_width=True)

            # ==============================
            # DOWNLOAD
            # ==============================
            file = generate_excel_report(results)

            st.download_button(
                "📥 Download Report",
                file,
                "EV_Report.xlsx"
            )

# ==============================
# FOOTER
# ==============================
st.markdown("""
<div class="footer">
🚗 EV Analytics Dashboard <br>
Developed by <b>Aditya Thangapandi</b>
</div>
""", unsafe_allow_html=True)
