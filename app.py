"""
Impact Registry - Application Shell

Defines explicit navigation architecture and launches the application.
Replaces Streamlit's automatic page discovery with controlled navigation.
"""
import streamlit as st

# Configure application
st.set_page_config(
    page_title="Impact Registry",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define explicit navigation
home_page = st.Page("pages/00_Home.py", title="Home", icon="🏠", default=True)
signal_center_page = st.Page("pages/01_Signal_Center.py", title="Signal Center", icon="📡")
setup_page = st.Page("pages/02_Setup.py", title="Setup", icon="⚙️")
capture_page = st.Page("pages/03_Capture.py", title="Capture", icon="✍️")
enrich_page = st.Page("pages/04_Enrich.py", title="Enrich", icon="🔗")
analyze_page = st.Page("pages/05_Analyze.py", title="Analyze", icon="📊")
monitor_page = st.Page("pages/06_Monitor.py", title="Monitor", icon="📈")

# Create navigation
navigation = st.navigation([
    home_page,
    signal_center_page,
    setup_page,
    capture_page,
    enrich_page,
    analyze_page,
    monitor_page
])

# Run the selected page
navigation.run()
