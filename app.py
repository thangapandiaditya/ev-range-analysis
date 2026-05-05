import streamlit as st
from rangeanalysis3 import process_ev_data
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="EV Dashboard", layout="wide")

# ==============================
# ✨ PREMIUM CSS + ANIMATION
# ==============================
st.markdown("""
<style>

/* Smooth fade animation */
.fade-in {
    animation: fadeIn 0.8s ease-in-out;
}
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(10px);}
    to {opacity: 1; transform: translateY(0);}
}

/* Card */
.card {
    padding: 16px;
    border-radius: 12px;
    text-align: center;
    border: 1px solid rgba(128,128,128,0.2);
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(10px);
    transition: all 0.25s ease;
}

/* Hover effect */
.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.2);
}

/* Title */
.card-title {
    font-size: 13px;
    opacity: 0.7;
}

.card-value {
    font-size: 22px;
    font-weight: bold;
}

/* Mobile responsive */
@media (max-width: 768px) {
    .card-value {
        font-size: 18px;
    }
}

</style>
""", unsafe_allow_html=True)

# ==============================
# HEADER
# ==============================
st.markdown("<h2 class='fade-in'>🚗 EV Range Analysis Dashboard</h2>", unsafe_allow_html=True)
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
# CARD FUNCTION
# ==============================
def card(title, value):
    st.markdown(f"""
    <div class="card fade-in">
        <div class="card-title">{title}</div>
        <div class="card-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

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
            # 📊 METRICS (AUTO RESPONSIVE)
            # ==============================
            st.subheader("📊 Trip Overview")

            cols = st.columns(4)
            with cols[0]: card("Start SOC", f"{results['start_soc']:.2f}%")
            with cols[1]: card("End SOC", f"{results['end_soc']:.2f}%")
            with cols[2]: card("Distance", f"{results['total_km']:.2f} km")
            with cols[3]: card("Payload", f"{results['payload']:.2f}")

            cols = st.columns(4)
            with cols[0]: card("Energy/km", f"{results['energy_per_km']:.2f}")
            with cols[1]: card("SOC Used", f"{results['soc_consumed']:.2f}")
            with cols[2]: card("Avg Current", f"{results['avg_current']:.2f} A")
            with cols[3]: card("Mileage", mileage_display)

            # ==============================
            # ⚙ MODE ANALYSIS
            # ==============================
            st.subheader("⚙ Mode-wise Analysis")

            total = results['total_km']

            eco = results['mode_distance']['Economy']
            thu = results['mode_distance']['Thunder']
            rhi = results['mode_distance']['Rhino']

            eco_p = (eco / total) * 100 if total else 0
            thu_p = (thu / total) * 100 if total else 0
            rhi_p = (rhi / total) * 100 if total else 0

            cols = st.columns(3)
            with cols[0]: card("Economy", f"{eco:.2f} km ({eco_p:.1f}%)")
            with cols[1]: card("Thunder", f"{thu:.2f} km ({thu_p:.1f}%)")
            with cols[2]: card("Rhino", f"{rhi:.2f} km ({rhi_p:.1f}%)")

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
st.markdown("<div style='text-align:center;'>👨‍💻 Developed by Aditya Thangapandi</div>", unsafe_allow_html=True)
