"""
Impact Registry - Main Entry Point

This file serves as the application launcher and immediately redirects
to the Home page to avoid showing 'app' in the navigation sidebar.
"""
import streamlit as st

# Redirect to Home page immediately
st.switch_page("pages/00_Home.py")
