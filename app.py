import streamlit as st
from rangeanalysis3 import process_ev_data
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="EV Dashboard", layout="wide")

# ==============================
# SIMPLE CLEAN CARD STYLE
# ==============================
def card(title, value):
    st.markdown(
        f"""
        <div style="
            background-color:#1e293b;
            padding:15px;
            border-radius:10px;
            text-align:center;
            border:1px solid #334155;
        ">
            <div style="font-size:14px;color:#94a3b8;">{title}</div>
            <div style="font-size:22px;font-weight:bold;">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ==============================
# HEADER
# ==============================
st.title("🚗 EV Range Dashboard")
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
    "Upload Trips",
    type=["xlsx", "xls"],
    accept_multiple_files=True
)

# ==============================
# REPORT FUNCTION
# ==============================
def generate_excel_report(r):
    df = pd.DataFrame({
        "Metric": [
            "Start SOC","End SOC","SOC Used","Avg Current",
            "Distance","Energy/km","Payload",
            "Mileage (SOC)","Mileage (Energy)",
            "Economy KM","Thunder KM","Rhino KM"
        ],
        "Value": [
            r['start_soc'], r['end_soc'],
            r['soc_consumed'], r['avg_current'],
            r['total_km'], r['energy_per_km'],
            r['payload'],
            r['approx_mileage_soc'],
            r['approx_mileage_energy'],
            r['mode_distance']['Economy'],
            r['mode_distance']['Thunder'],
            r['mode_distance']['Rhino']
        ]
    })

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)

    return output.getvalue()

# ==============================
# AI INSIGHTS (SIMPLE + CLEAN)
# ==============================
def ai_insight(r):
    if r["energy_per_km"] > 13:
        return "⚠ High consumption detected"
    elif r["avg_current"] < -40:
        return "⚡ Heavy load usage"
    else:
        return "✅ Efficient driving"

# ==============================
# MAIN
# ==============================
if uploaded_files:

    if st.button("🚀 Analyze"):

        results_list = []

        for file in uploaded_files:
            res = process_ev_data(file, vehicle_type)
            if res:
                res["file"] = file.name
                results_list.append(res)

        if not results_list:
            st.error("No valid data")
        else:
            r = results_list[0]

            st.subheader("📊 Overview")

            c1, c2, c3, c4 = st.columns(4)
            with c1: card("Start SOC", f"{r['start_soc']:.2f}%")
            with c2: card("End SOC", f"{r['end_soc']:.2f}%")
            with c3: card("Distance", f"{r['total_km']:.2f} km")
            with c4: card("Payload", f"{r['payload']:.2f}")

            c5, c6, c7, c8 = st.columns(4)
            mileage = r["approx_mileage_energy"]
            mileage_disp = f"{mileage:.2f}" if mileage else "0"

            with c5: card("Energy/km", f"{r['energy_per_km']:.2f}")
            with c6: card("SOC Used", f"{r['soc_consumed']:.2f}")
            with c7: card("Avg Current", f"{r['avg_current']:.2f}")
            with c8: card("Mileage", mileage_disp)

            # ==============================
            # MODE
            # ==============================
            st.subheader("⚙ Mode Usage")

            total = r['total_km']

            eco = r['mode_distance']['Economy']
            thu = r['mode_distance']['Thunder']
            rhi = r['mode_distance']['Rhino']

            c1, c2, c3 = st.columns(3)

            with c1:
                card("Economy", f"{eco:.2f} km ({(eco/total*100 if total else 0):.1f}%)")
            with c2:
                card("Thunder", f"{thu:.2f} km ({(thu/total*100 if total else 0):.1f}%)")
            with c3:
                card("Rhino", f"{rhi:.2f} km ({(rhi/total*100 if total else 0):.1f}%)")

            # ==============================
            # AI
            # ==============================
            st.subheader("🤖 Insight")
            st.info(ai_insight(r))

            # ==============================
            # MULTI TRIP
            # ==============================
            st.subheader("📊 Comparison")

            df = pd.DataFrame([{
                "Trip": x["file"],
                "Distance": round(x["total_km"], 2),
                "Mileage": round(x["approx_mileage_energy"], 2) if x["approx_mileage_energy"] else 0
            } for x in results_list])

            st.dataframe(df, use_container_width=True)

            # ==============================
            # DOWNLOAD
            # ==============================
            file = generate_excel_report(r)
            st.download_button("📥 Download Report", file, "EV_Report.xlsx")

# ==============================
# FOOTER
# ==============================
st.markdown("---")
st.caption("EV Analytics • Aditya Thangapandi")
