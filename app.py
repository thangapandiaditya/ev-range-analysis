import streamlit as st
from rangeanalysis3 import process_ev_data
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="EV Dashboard", layout="wide")

# ==============================
# HEADER
# ==============================
st.title("🚗 EV Range Analysis")
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
# MOBILE DETECTION
# ==============================
is_mobile = st.session_state.get("is_mobile", False)

# ==============================
# MAIN
# ==============================
if uploaded_file:

    if st.button("🚀 Run Analysis"):

        with st.spinner("Processing..."):
            results = process_ev_data(uploaded_file, vehicle_type)

        if results is None:
            st.error("❌ No valid trip detected")
        else:
            st.success("✅ Analysis Complete")

            mileage = results["approx_mileage_energy"]
            mileage_display = f"{mileage:.2f}" if mileage else "N/A"

            # ==============================
            # 📱 MOBILE LAYOUT (STACKED)
            # ==============================
            if st.checkbox("📱 Mobile View", value=True):

                st.subheader("📊 Trip Overview")

                st.metric("Start SOC", f"{results['start_soc']:.2f}%")
                st.metric("End SOC", f"{results['end_soc']:.2f}%")
                st.metric("Distance", f"{results['total_km']:.2f} km")
                st.metric("Payload", f"{results['payload']:.2f}")

                st.metric("Energy/km", f"{results['energy_per_km']:.2f}")
                st.metric("SOC Used", f"{results['soc_consumed']:.2f}")
                st.metric("Avg Current", f"{results['avg_current']:.2f} A")
                st.metric("Mileage", mileage_display)

                st.subheader("⚙ Mode Analysis")

                total = results['total_km']

                eco = results['mode_distance']['Economy']
                thu = results['mode_distance']['Thunder']
                rhi = results['mode_distance']['Rhino']

                st.metric("Economy", f"{eco:.2f} km", f"{(eco/total*100 if total else 0):.1f}%")
                st.metric("Thunder", f"{thu:.2f} km", f"{(thu/total*100 if total else 0):.1f}%")
                st.metric("Rhino", f"{rhi:.2f} km", f"{(rhi/total*100 if total else 0):.1f}%")

            # ==============================
            # 💻 DESKTOP LAYOUT
            # ==============================
            else:

                st.subheader("📊 Trip Overview")

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Start SOC", f"{results['start_soc']:.2f}%")
                col2.metric("End SOC", f"{results['end_soc']:.2f}%")
                col3.metric("Distance", f"{results['total_km']:.2f} km")
                col4.metric("Payload", f"{results['payload']:.2f}")

                col5, col6, col7, col8 = st.columns(4)
                col5.metric("Energy/km", f"{results['energy_per_km']:.2f}")
                col6.metric("SOC Used", f"{results['soc_consumed']:.2f}")
                col7.metric("Avg Current", f"{results['avg_current']:.2f} A")
                col8.metric("Mileage", mileage_display)

                st.subheader("⚙ Mode Analysis")

                total = results['total_km']

                eco = results['mode_distance']['Economy']
                thu = results['mode_distance']['Thunder']
                rhi = results['mode_distance']['Rhino']

                colA, colB, colC = st.columns(3)
                colA.metric("Economy", f"{eco:.2f} km", f"{(eco/total*100 if total else 0):.1f}%")
                colB.metric("Thunder", f"{thu:.2f} km", f"{(thu/total*100 if total else 0):.1f}%")
                colC.metric("Rhino", f"{rhi:.2f} km", f"{(rhi/total*100 if total else 0):.1f}%")

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
st.markdown("---")
st.markdown("### 👨‍💻 Developed by Aditya Thangapandi")
