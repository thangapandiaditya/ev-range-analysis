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
.fade {
    animation: fadeUp 0.6s ease;
}
@keyframes fadeUp {
    from {opacity:0; transform:translateY(10px);}
    to {opacity:1; transform:translateY(0);}
}

.card {
    padding:16px;
    border-radius:12px;
    background:rgba(255,255,255,0.05);
    backdrop-filter:blur(10px);
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

# ==============================
# HEADER
# ==============================
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
# CARD FUNCTION
# ==============================
def card(title, value):
    st.markdown(f"""
    <div class="card fade">
        <b>{title}</b><br>
        <h3>{value}</h3>
    </div>
    """, unsafe_allow_html=True)

# ==============================
# MAIN
# ==============================
if uploaded_file:

    if st.button("Run Analysis"):

        trips = process_ev_data(uploaded_file, vehicle_type)

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
                    "SOC Used": round(t["soc_used"], 2),
                    "Distance": round(t["distance"], 2),
                    "Efficiency": round(t["energy_per_km"], 2)
                })

            df = pd.DataFrame(timeline)
            st.dataframe(df, use_container_width=True)

            # ==============================
            # SELECT TRIP
            # ==============================
            index = st.selectbox(
                "Select Trip",
                range(len(trips)),
                format_func=lambda x: f"Trip {x+1}"
            )

            trip = trips[index]

            st.subheader(f"📊 Trip {index+1} Details")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Distance", f"{trip['distance']:.2f} km")
            col2.metric("SOC Used", f"{trip['soc_used']:.2f}")
            col3.metric("Efficiency", f"{trip['energy_per_km']:.2f}")
            col4.metric("Avg Current", f"{trip['avg_current']:.2f}")

            # ==============================
            # MODE
            # ==============================
            st.subheader("⚙ Mode Distribution")

            total = trip['distance']

            eco = trip['mode']['eco']
            thu = trip['mode']['thu']
            rhi = trip['mode']['rhi']

            colA, colB, colC = st.columns(3)

            colA.metric("Economy", f"{eco:.2f}", f"{(eco/total*100 if total else 0):.1f}%")
            colB.metric("Thunder", f"{thu:.2f}", f"{(thu/total*100 if total else 0):.1f}%")
            colC.metric("Rhino", f"{rhi:.2f}", f"{(rhi/total*100 if total else 0):.1f}%")

# ==============================
# FOOTER
# ==============================
st.markdown("---")
st.markdown("Developed by Aditya Thangapandi")
