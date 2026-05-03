import streamlit as st
from rangeanalysis3 import process_ev_data
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="EV Dashboard", layout="wide")

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

uploaded_file = st.sidebar.file_uploader(
    "Upload Excel File",
    type=["xlsx", "xls"]
)

# ==============================
# REPORT FUNCTION (UPDATED)
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
if uploaded_file:

    if st.button("🚀 Run Analysis"):

        with st.spinner("Processing..."):
            results = process_ev_data(uploaded_file, vehicle_type)

        if results is None:
            st.error("No valid trip detected")
        else:
            st.success("Analysis Complete")

            # ==============================
            # MAIN METRICS
            # ==============================
            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Start SOC", f"{results['start_soc']:.2f}")
            col2.metric("End SOC", f"{results['end_soc']:.2f}")
            col3.metric("Distance", f"{results['total_km']:.2f}")
            col4.metric("Payload", f"{results['payload']:.2f}")

            col5, col6, col7, col8 = st.columns(4)

            col5.metric("Energy/km", f"{results['energy_per_km']:.2f}")
            col6.metric("SOC Used", f"{results['soc_consumed']:.2f}")
            col7.metric("Avg Current", f"{results['avg_current']:.2f}")
            col8.metric("Mileage", 
                f"{results['approx_mileage_energy']:.2f}" 
                if results['approx_mileage_energy'] else "N/A"
            )

            # ==============================
            # 🔥 MODE-WISE KM + %
            # ==============================
            st.subheader("⚙ Mode-wise Analysis")

            total = results['total_km']

            eco_km = results['mode_distance']['Economy']
            thu_km = results['mode_distance']['Thunder']
            rhi_km = results['mode_distance']['Rhino']

            eco = (eco_km / total) * 100 if total else 0
            thu = (thu_km / total) * 100 if total else 0
            rhi = (rhi_km / total) * 100 if total else 0

            colA, colB, colC = st.columns(3)

            colA.metric(
                "Economy",
                f"{eco_km:.2f} km",
                f"{eco:.1f}%"
            )

            colB.metric(
                "Thunder",
                f"{thu_km:.2f} km",
                f"{thu:.1f}%"
            )

            colC.metric(
                "Rhino",
                f"{rhi_km:.2f} km",
                f"{rhi:.1f}%"
            )

            # ==============================
            # DOWNLOAD REPORT
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
st.markdown("---")
st.markdown("### 👨‍💻 Developed by Aditya Thangapandi")