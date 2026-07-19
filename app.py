"""
Impact Registry - Application Shell

Defines explicit navigation architecture and launches the application.
Replaces Streamlit's automatic page discovery with controlled navigation.
"""
import streamlit as st
from config import Config

# Print startup diagnostics to console
Config.print_startup_diagnostics()

# Validate workspace on startup
is_valid, message = Config.validate_workspace()
if not is_valid:
    st.error("⚠️ **Persistent Workspace Storage Unavailable**")
    st.error(message)
    st.warning("Projects cannot be saved until storage is available.")
    st.info("Please check deployment configuration and ensure persistent disk is mounted.")
    st.stop()

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
