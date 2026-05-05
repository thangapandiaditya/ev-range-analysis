import streamlit as st
from rangeanalysis3 import process_ev_data
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="EV Dashboard", layout="wide")

# ==============================
# 🎨 PREMIUM DARK + MOBILE CSS
# ==============================
st.markdown("""
<style>

/* Global */
html, body, [class*="css"] {
    background-color: #0f172a;
    color: #e2e8f0;
}

/* Cards */
.card {
    background: linear-gradient(145deg, #1e293b, #0f172a);
    padding: 16px;
    border-radius: 14px;
    text-align: center;
    box-shadow: 0 6px 15px rgba(0,0,0,0.4);
    margin-bottom: 10px;
}

/* Title */
.section {
    font-size: 20px;
    font-weight: 600;
    margin-top: 20px;
    color: #38bdf8;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
    .card {
        padding: 12px;
        font-size: 14px;
    }
}

/* Footer */
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
st.title("🚗 EV Range Analytics")
st.caption("Premium Dashboard • Aditya Thangapandi")

# ==============================
# SIDEBAR
# ==============================
st.sidebar.header("⚙ Settings")

vehicle_type = st.sidebar.selectbox(
    "Select Vehicle",
    ["turbo", "storm", "hiload"]
)

uploaded_files = st.sidebar.file_uploader(
    "Upload Trips",
    type=["xlsx", "xls"],
    accept_multiple_files=True
)

# ==============================
# REPORT
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
# 🤖 AI SUGGESTIONS
# ==============================
def generate_ai_insight(r):
    insights = []

    if r["energy_per_km"] > 13:
        insights.append("⚠ High energy consumption — aggressive driving")

    if r["avg_current"] < -40:
        insights.append("⚡ High current draw — check load or driving style")

    if r["mode_distance"]["Thunder"] > r["mode_distance"]["Economy"]:
        insights.append("🚀 Heavy Thunder mode usage — reducing range")

    if r["approx_mileage_energy"] and r["approx_mileage_energy"] < 100:
        insights.append("📉 Low mileage — battery efficiency is low")

    if len(insights) == 0:
        insights.append("✅ Driving pattern looks efficient")

    return insights

# ==============================
# MAIN
# ==============================
if uploaded_files:

    if st.button("🚀 Analyze Trips"):

        all_results = []

        for file in uploaded_files:
            with st.spinner(f"Processing {file.name}..."):
                result = process_ev_data(file, vehicle_type)

                if result:
                    result["file_name"] = file.name
                    all_results.append(result)

        if not all_results:
            st.error("No valid trips found")
        else:
            st.success("Analysis Complete")

            # ==============================
            # SHOW FIRST TRIP
            # ==============================
            r = all_results[0]

            st.markdown('<div class="section">📊 Trip Overview</div>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            col1.markdown(f'<div class="card">Start SOC<br><b>{r["start_soc"]:.2f}%</b></div>', unsafe_allow_html=True)
            col2.markdown(f'<div class="card">End SOC<br><b>{r["end_soc"]:.2f}%</b></div>', unsafe_allow_html=True)

            col3, col4 = st.columns(2)

            col3.markdown(f'<div class="card">Distance<br><b>{r["total_km"]:.2f} km</b></div>', unsafe_allow_html=True)
            col4.markdown(f'<div class="card">Payload<br><b>{r["payload"]:.2f}</b></div>', unsafe_allow_html=True)

            mileage = r["approx_mileage_energy"]
            mileage_display = f"{mileage:.2f}" if mileage else "0.00"

            col5, col6 = st.columns(2)

            col5.markdown(f'<div class="card">Energy/km<br><b>{r["energy_per_km"]:.2f}</b></div>', unsafe_allow_html=True)
            col6.markdown(f'<div class="card">Mileage<br><b>{mileage_display}</b></div>', unsafe_allow_html=True)

            # ==============================
            # MODE
            # ==============================
            st.markdown('<div class="section">⚙ Mode Analysis</div>', unsafe_allow_html=True)

            total = r['total_km']

            eco_km = r['mode_distance']['Economy']
            thu_km = r['mode_distance']['Thunder']
            rhi_km = r['mode_distance']['Rhino']

            eco = (eco_km / total) * 100 if total else 0
            thu = (thu_km / total) * 100 if total else 0
            rhi = (rhi_km / total) * 100 if total else 0

            c1, c2, c3 = st.columns(3)

            c1.markdown(f'<div class="card">Economy<br><b>{eco_km:.2f} km</b><br>{eco:.1f}%</div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="card">Thunder<br><b>{thu_km:.2f} km</b><br>{thu:.1f}%</div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="card">Rhino<br><b>{rhi_km:.2f} km</b><br>{rhi:.1f}%</div>', unsafe_allow_html=True)

            # ==============================
            # 🤖 AI INSIGHTS
            # ==============================
            st.markdown('<div class="section">🤖 AI Insights</div>', unsafe_allow_html=True)

            insights = generate_ai_insight(r)

            for i in insights:
                st.info(i)

            # ==============================
            # MULTI TRIP
            # ==============================
            st.markdown('<div class="section">📊 Multi Trip Comparison</div>', unsafe_allow_html=True)

            df_compare = pd.DataFrame([{
                "Trip": x["file_name"],
                "Distance": round(x["total_km"], 2),
                "Mileage": round(x["approx_mileage_energy"], 2) if x["approx_mileage_energy"] else 0
            } for x in all_results])

            st.dataframe(df_compare, use_container_width=True)

            # ==============================
            # DOWNLOAD
            # ==============================
            file = generate_excel_report(r)

            st.download_button("📥 Download Report", file, "EV_Report.xlsx")

# ==============================
# FOOTER
# ==============================
st.markdown("""
<div class="footer">
🚗 EV Analytics Dashboard <br>
Developed by <b>Aditya Thangapandi</b>
</div>
""", unsafe_allow_html=True)
