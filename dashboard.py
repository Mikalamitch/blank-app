# dashboard.py
import streamlit as st
import requests
import pandas as pd
import time
import datetime

# ==============================
# CONFIGURATION
# ==============================
st.set_page_config(
    page_title="AI Threat Detection Dashboard",
    layout="wide"
)

API_URL = "http://127.0.0.1:8000/get_latest_threats"  # FastAPI endpoint
REFRESH_INTERVAL = 5  # seconds between refreshes

# ==============================
# PAGE HEADER
# ==============================
st.title("🛡 Autonomous AI Threat Response Dashboard")
st.caption("Powered by osquery • Zeek • Isolation Forest / Amber • Gemini")

# ==============================
# DATA FETCH FUNCTION
# ==============================
def fetch_threat_data():
    """Pull latest AI-reviewed threat data from FastAPI backend."""
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Cannot connect to backend: {e}")
        return pd.DataFrame()

# ==============================
# AUTO-REFRESH LOOP
# ==============================
while True:
    # Clear and re-render dashboard each loop
    st.empty()

    # Fetch data
    data = fetch_threat_data()
    # Convert ISO timestamp to simpler readable format
    if 'timestamp' in data.columns:
        data['timestamp'] = pd.to_datetime(data['timestamp'], errors='coerce').dt.strftime("%b %d, %Y %I:%M %p")


    if data.empty:
        st.info("No AI-reviewed threats yet. Waiting for anomaly events...")
    else:
        # --- KPI / METRICS SECTION ---
        st.subheader("📊 System Overview")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Reviewed Events", len(data))
        col2.metric("Max Gemini Confidence", f"{data['gemini_confidence'].max() * 100:.2f}%")
        col3.metric("Recent Threat Source", data['source'].iloc[0])

        st.markdown("---")

        # --- DATA TABLE SECTION ---
        st.subheader("🧠 AI-Reviewed Threat Logs")

        df_display = data[[
            'timestamp', 'source', 'event_type',
            'anomaly_score', 'gemini_confidence',
            'mitigation_suggestion', 'raw_data'
        ]].rename(columns={
            'timestamp': 'Timestamp',
            'source': 'Source',
            'event_type': 'Event Type',
            'anomaly_score': 'ML Score',
            'gemini_confidence': 'Gemini Confidence',
            'mitigation_suggestion': 'Mitigation Suggestion',
            'raw_data': 'Raw Event Log'
        })

        # Apply color styling
        def color_confidence(val):
            if isinstance(val, (int, float)):
                if val > 0.8:
                    return 'background-color: #ff4c4c; color: white'  # High
                elif val > 0.5:
                    return 'background-color: orange'  # Medium
                elif val > 0.2:
                    return 'background-color: yellow'  # Low
            return ''

        st.dataframe(
            df_display.style.applymap(color_confidence, subset=['Gemini Confidence']),
            use_container_width=True,
            height=500
        )

    # --- FOOTER ---
    st.markdown("---")
    st.caption(f"🔁 Auto-refresh every {REFRESH_INTERVAL} seconds • Data source: FastAPI @ {API_URL}")
    st.caption(f"Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Wait before refresh
    time.sleep(REFRESH_INTERVAL)

    # Rerun the script
    st.rerun()
