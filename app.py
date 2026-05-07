import streamlit as st
from rangeanalysis3 import process_ev_data
import pandas as pd
from io import BytesIO

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="EV Dashboard",
    layout="wide"
)

# ==============================
# PREMIUM CSS
# ==============================
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(135deg,#0f172a,#111827);
    color: white;
}

/* Fade animation */
.fade {
    opacity: 0;
    transform: translateY(10px);
    animation: fadeUp 0.7s forwards;
}

@keyframes fadeUp {
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Card */
.card {
    padding: 18px;
    border-radius: 18px;
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.12);
    text-align: center;
    transition: all 0.3s ease;
    margin-bottom: 15px;
}

/* Hover effect */
.card:hover {
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 10px 25px rgba(0,0,0,0.25);
}

/* Title */
.card-title {
    font-size: 13px;
    opacity: 0.7;
    margin-bottom: 6px;
}

/* Value */
.card-value {
    font-size: 24px;
    font-weight: bold;
}

/* Progress Bar */
.bar {
    height: 7px;
    border-radius: 10px;
    background: rgba(255,255,255,0.08);
    margin-top: 10px;
    overflow: hidden;
}

.bar-fill {
    height: 100%;
    border-radius: 10px;
    background: linear-gradient(
        90deg,
        #38bdf8,
        #6366f1
    );
    animation: fillBar 1.5s forwards;
}

@keyframes fillBar {
    from {width:0%;}
}

/* Button */
.stButton>button {
    width: 100%;
    border-radius: 12px;
    border: none;
    background: linear-gradient(
        90deg,
        #2563eb,
        #7c3aed
    );
    color: white;
    font-weight: bold;
    padding: 12px;
    transition: 0.3s;
}

.stButton>button:hover {
    transform: scale(1.02);
}

/* Download button */
.stDownloadButton>button {
    width: 100%;
    border-radius: 12px;
    border: none;
    background: linear-gradient(
        90deg,
        #059669,
        #10b981
    );
    color: white;
    font-weight: bold;
    padding: 12px;
}

/* Mobile optimization */
@media (max-width:768px){

    .card {
        padding: 14px;
    }

    .card-value {
        font-size: 18px;
    }

    h2 {
        font-size: 24px !important;
    }
}

</style>
""", unsafe_allow_html=True)

# ==============================
# HEADER
# ==============================
st.markdown("""
<h2 class='fade'>
🚗 EV Range Analysis Dashboard
</h2>
""", unsafe_allow_html=True)

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
# EXPORT REPORT
# ==============================
def generate_excel_report(results):

    df = pd.DataFrame({

        "Metric": [

            "Start SOC",
            "End SOC",
            "SOC Used",
            "Distance",
            "Energy/km",
            "Avg Current",
            "Payload",
            "Mileage (SOC)",
            "Mileage (Energy)",
            "Economy KM",
            "Thunder KM",
            "Rhino KM"
        ],

        "Value": [

            results['start_soc'],
            results['end_soc'],
            results['soc_consumed'],
            results['total_km'],
            results['energy_per_km'],
            results['avg_current'],
            results['payload'],
            results['approx_mileage_soc'],
            results['approx_mileage_energy'],
            results['mode_distance']['Economy'],
            results['mode_distance']['Thunder'],
            results['mode_distance']['Rhino']
        ]
    })

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine='openpyxl'
    ) as writer:

        df.to_excel(
            writer,
            index=False
        )

    return output.getvalue()

# ==============================
# CARD FUNCTION
# ==============================
def card(title, value):

    st.markdown(f"""
    <div class="card fade">

        <div class="card-title">
            {title}
        </div>

        <div class="card-value">
            {value}
        </div>

    </div>
    """, unsafe_allow_html=True)

# ==============================
# MODE CARD
# ==============================
def mode_card(title, km, percent):

    st.markdown(f"""
    <div class="card fade">

        <div class="card-title">
            {title}
        </div>

        <div class="card-value">
            {km:.2f} km
        </div>

        <div style="font-size:12px;opacity:0.7;">
            {percent:.1f}%
        </div>

        <div class="bar">
            <div class="bar-fill"
                 style="width:{percent}%">
            </div>
        </div>

    </div>
    """, unsafe_allow_html=True)

# ==============================
# MAIN
# ==============================
if uploaded_file:

    if st.button("🚀 Run Analysis"):

        with st.spinner("Processing..."):

            results = process_ev_data(
                uploaded_file,
                vehicle_type
            )

        # ==============================
        # NO TRIP
        # ==============================
        if results is None:

            st.error("❌ No valid trip detected")

        # ==============================
        # SUCCESS
        # ==============================
        else:

            st.success("✅ Analysis Complete")

            mileage = results[
                "approx_mileage_energy"
            ]

            mileage_display = (
                f"{mileage:.2f}"
                if mileage else "N/A"
            )

            # ==============================
            # MAIN METRICS
            # ==============================
            st.subheader("📊 Trip Overview")

            cols = st.columns(4)

            with cols[0]:
                card(
                    "Start SOC",
                    f"{results['start_soc']:.2f}%"
                )

            with cols[1]:
                card(
                    "End SOC",
                    f"{results['end_soc']:.2f}%"
                )

            with cols[2]:
                card(
                    "Distance",
                    f"{results['total_km']:.2f} km"
                )

            with cols[3]:
                card(
                    "Payload",
                    f"{results['payload']:.2f}"
                )

            cols = st.columns(4)

            with cols[0]:
                card(
                    "Energy/km",
                    f"{results['energy_per_km']:.2f}"
                )

            with cols[1]:
                card(
                    "SOC Used",
                    f"{results['soc_consumed']:.2f}"
                )

            with cols[2]:
                card(
                    "Avg Current",
                    f"{results['avg_current']:.2f} A"
                )

            with cols[3]:
                card(
                    "Mileage",
                    mileage_display
                )

            # ==============================
            # MODE ANALYSIS
            # ==============================
            st.subheader("⚙ Mode-wise Analysis")

            total = results['total_km']

            eco = results['mode_distance']['Economy']
            thu = results['mode_distance']['Thunder']
            rhi = results['mode_distance']['Rhino']

            eco_p = (
                (eco / total) * 100
                if total else 0
            )

            thu_p = (
                (thu / total) * 100
                if total else 0
            )

            rhi_p = (
                (rhi / total) * 100
                if total else 0
            )

            cols = st.columns(3)

            with cols[0]:
                mode_card(
                    "Economy",
                    eco,
                    eco_p
                )

            with cols[1]:
                mode_card(
                    "Thunder",
                    thu,
                    thu_p
                )

            with cols[2]:
                mode_card(
                    "Rhino",
                    rhi,
                    rhi_p
                )

            # ==============================
            # DOWNLOAD
            # ==============================
            file = generate_excel_report(
                results
            )

            st.download_button(
                "📥 Download Report",
                file,
                "EV_Report.xlsx"
            )

# ==============================
# FOOTER
# ==============================
st.markdown("---")

st.markdown("""
<div style='text-align:center;opacity:0.7;'>

👨‍💻 Developed by Aditya Thangapandi

</div>
""", unsafe_allow_html=True)
