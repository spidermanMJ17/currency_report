import streamlit as st
import requests
from datetime import datetime

BACKEND_URL = "http://localhost:8000/analyze"

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

CURRENCIES = [
    "USDINR",
    "EURUSD",
    "USDJPY",
    "USDBRL",
    "USDAUD",
    "USDMXN",
    "USDZAR",
    "USDPHP"
]

current_year = datetime.now().year
YEARS = list(range(2020, current_year))

st.set_page_config(
    page_title="Financial Analyst",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Financial Analysis Report")
st.markdown("Select a month and year to generate a comprehensive market analysis report.")

col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

with col1:
    selected_month = st.selectbox("📅 Select Month", MONTHS, index=datetime.now().month - 1)

with col2:
    selected_year = st.selectbox("🗓️ Select Year", YEARS, index=YEARS.index(current_year))

with col4:
    selected_pair = st.selectbox("select currency", CURRENCIES)

with col3:
    st.markdown("<br>", unsafe_allow_html=True)
    generate = st.button("🚀 Generate Report", use_container_width=True)

st.divider()

if generate:
    with st.spinner(f"Generating analysis for {selected_month} {selected_year}... This may take a moment ⏳"):
        try:
            response = requests.post(
                BACKEND_URL,
                json={"month": selected_month, "year": selected_year, "currency": selected_pair},
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()
            st.success(f"✅ Report generated for **{selected_pair} {selected_month} {selected_year}**")
            st.markdown(data["result"])
        except requests.exceptions.ConnectionError:
            st.error("❌ Could not connect to the backend. Make sure `backend.py` is running on port 8000.")
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. The analysis is taking too long — try again.")
        except requests.exceptions.HTTPError as e:
            st.error(f"❌ Backend error: {e}")
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")