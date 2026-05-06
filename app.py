import streamlit as st
from rangeanalysis3 import process_ev_data
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="EV Dashboard", layout="wide")

# ==============================
# PREMIUM UI
# ==============================
st.markdown("""
<style>
.card {
    padding:16px;
    border-radius:14px;
    background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.15);
    text-align:center;
    transition:0.3s;
}
.card:hover {
    transform: translateY(-5px) scale(1.02);
}
.card-title {
    font-size:13px;
    opacity:0.7;
}
.card-value {
    font-size:22px;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

st.title("🚗 EV Range Analysis Dashboard")
st.caption("Developed by Aditya Thangapandi")

# ==============================
# SIDEBAR
# ==============================
vehicle_type = st.sidebar.selectbox(
    "Select Vehicle",
    ["turbo", "storm", "hiload"]
)

uploaded_file = st.sidebar.file_uploader("Upload Excel", type=["xlsx"])

# ==============================
# EXPORT FUNCTION
# ==============================
def export_all_trips(trips):

    data = []

    for i, t in enumerate(trips):
        data.append({
            "Trip": f"Trip {i+1}",
            "Start SOC": t["start_soc"],
            "End SOC": t["end_soc"],
            "SOC Used": t["soc_consumed"],
            "Distance": t["total_km"],
            "Energy/km": t["energy_per_km"],
            "Avg Current": t["avg_current"],
            "Payload": t["payload"],
            "Economy KM": t["mode_distance"]["Economy"],
            "Thunder KM": t["mode_distance"]["Thunder"],
            "Rhino KM": t["mode_distance"]["Rhino"]
        })

    df = pd.DataFrame(data)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)

    return output.getvalue()

# ==============================
# CARD UI
# ==============================
def card(title, value):
    st.markdown(f"""
    <div class="card">
        <div class="card-title">{title}</div>
        <div class="card-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

# ==============================
# MAIN
# ==============================
if uploaded_file:

    if st.button("🚀 Run Analysis"):

        trips = process_ev_data(uploaded_file, vehicle_type)

        if not trips:
            st.error("❌ No trips detected")
        else:
            st.success(f"✅ {len(trips)} Trips Detected")

            index = st.selectbox(
                "Select Trip",
                range(len(trips)),
                format_func=lambda x: f"Trip {x+1}"
            )

            t = trips[index]

            cols = st.columns(4)
            with cols[0]: card("Start SOC", f"{t['start_soc']:.2f}%")
            with cols[1]: card("End SOC", f"{t['end_soc']:.2f}%")
            with cols[2]: card("Distance", f"{t['total_km']:.2f} km")
            with cols[3]: card("Payload", f"{t['payload']:.2f}")

            cols = st.columns(4)
            with cols[0]: card("Energy/km", f"{t['energy_per_km']:.2f}")
            with cols[1]: card("SOC Used", f"{t['soc_consumed']:.2f}")
            with cols[2]: card("Avg Current", f"{t['avg_current']:.2f} A")
            mileage = t["approx_mileage_energy"]
            with cols[3]: card("Mileage", f"{mileage:.2f}" if mileage else "N/A")

            total = t['total_km']

            eco = t['mode_distance']['Economy']
            thu = t['mode_distance']['Thunder']
            rhi = t['mode_distance']['Rhino']

            cols = st.columns(3)
            with cols[0]: card("Economy", f"{eco:.2f} km ({eco/total*100:.1f}%)" if total else "0")
            with cols[1]: card("Thunder", f"{thu:.2f} km ({thu/total*100:.1f}%)" if total else "0")
            with cols[2]: card("Rhino", f"{rhi:.2f} km ({rhi/total*100:.1f}%)" if total else "0")

            file = export_all_trips(trips)

            st.download_button(
                "📥 Download All Trips Report",
                file,
                "All_Trips_Report.xlsx"
            )

# ==============================
# FOOTER
# ==============================
st.markdown("---")
st.markdown("👨‍💻 Developed by Aditya Thangapandi")
