import streamlit as st
from rangeanalysis3 import process_ev_data
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="EV Dashboard", layout="wide")

# ==============================
# UI
# ==============================
st.markdown("""
<style>
.card {
    padding:15px;
    border-radius:12px;
    background:rgba(255,255,255,0.05);
    border:1px solid rgba(255,255,255,0.1);
    text-align:center;
    margin-bottom:10px;
}
.card:hover {
    transform:scale(1.03);
    transition:0.3s;
}
</style>
""", unsafe_allow_html=True)

st.title("🚗 EV Range Analysis")
st.caption("Developed by Aditya Thangapandi")

# ==============================
# SIDEBAR
# ==============================
vehicle_type = st.sidebar.selectbox(
    "Vehicle",
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
            "Start Time": t["start_time"],
            "End Time": t["end_time"],
            "Start SOC": round(t["start_soc"], 2),
            "End SOC": round(t["end_soc"], 2),
            "SOC Used": round(t["soc_used"], 2),
            "Distance (km)": round(t["distance"], 2),
            "Energy/km": round(t["energy_per_km"], 2),
            "Avg Current": round(t["avg_current"], 2),
            "Payload": round(t["payload"], 2),
            "Economy KM": round(t["mode"]["eco"], 2),
            "Thunder KM": round(t["mode"]["thu"], 2),
            "Rhino KM": round(t["mode"]["rhi"], 2)
        })

    df = pd.DataFrame(data)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)

    return output.getvalue()

# ==============================
# MAIN
# ==============================
if uploaded_file:

    if st.button("Run Analysis"):

        try:
            trips = process_ev_data(uploaded_file, vehicle_type)
        except Exception as e:
            st.error(e)
            st.stop()

        if not trips:
            st.error("No trips detected")
        else:

            # ==============================
            # TIMELINE
            # ==============================
            st.subheader("🕒 Trip Timeline")

            timeline = []
            for i, t in enumerate(trips):
                timeline.append({
                    "Trip": f"Trip {i+1}",
                    "Start": t["start_time"],
                    "End": t["end_time"],
                    "Distance": round(t["distance"], 2),
                    "SOC Used": round(t["soc_used"], 2)
                })

            st.dataframe(pd.DataFrame(timeline), use_container_width=True)

            # ==============================
            # SELECT TRIP
            # ==============================
            index = st.selectbox(
                "Select Trip",
                range(len(trips)),
                format_func=lambda x: f"Trip {x+1}"
            )

            t = trips[index]

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Distance", f"{t['distance']:.2f} km")
            col2.metric("SOC Used", f"{t['soc_used']:.2f}")
            col3.metric("Efficiency", f"{t['energy_per_km']:.2f}")
            col4.metric("Avg Current", f"{t['avg_current']:.2f}")

            # ==============================
            # MODE
            # ==============================
            total = t['distance']

            eco = t['mode']['eco']
            thu = t['mode']['thu']
            rhi = t['mode']['rhi']

            colA, colB, colC = st.columns(3)

            colA.metric("Economy", f"{eco:.2f}", f"{(eco/total*100 if total else 0):.1f}%")
            colB.metric("Thunder", f"{thu:.2f}", f"{(thu/total*100 if total else 0):.1f}%")
            colC.metric("Rhino", f"{rhi:.2f}", f"{(rhi/total*100 if total else 0):.1f}%")

            # ==============================
            # DOWNLOAD
            # ==============================
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
st.markdown("Developed by Aditya Thangapandi")
