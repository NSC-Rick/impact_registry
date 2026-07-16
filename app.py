import streamlit as st
from database.schema import init_db, get_session, get_engine

st.set_page_config(
    page_title="Impact Registry",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

engine = init_db()
session = get_session(engine)

st.title("🎯 Impact Registry")
st.markdown("### Practitioner-First Change Impact Management")

st.markdown("""
Welcome to the Impact Registry MVP. This tool supports the complete practitioner workflow:

1. **Setup** - Configure your project and enterprise assets
2. **Capture** - Record impacts quickly and efficiently  
3. **Enrich** - Add traceability and context
4. **Analyze** - Understand patterns and risks
5. **Monitor** - Track progress and coverage

Use the sidebar to navigate between workflow stages.
""")

st.info("👈 Select a workflow stage from the sidebar to begin")

st.markdown("---")
st.markdown("**Design Principles:** Practitioner First • Capture First • Coverage, not Execution • Traceability • Enterprise Assets • Logical Concepts • Carry Forward")
