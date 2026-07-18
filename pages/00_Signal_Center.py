import streamlit as st

st.set_page_config(page_title="Signal Center", page_icon="📡", layout="wide")

from database.schema import get_session, get_engine
from signal_center.signal_dashboard import SignalDashboard
from signal_center.sensor_models import SensorStatus, SignalPriority

# Try to import Plotly, but don't fail if unavailable
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("⚠️ Plotly not available. Using standard metrics instead of gauges.")

# Check for active project workspace
if 'current_project' not in st.session_state or st.session_state['current_project'] is None:
    st.warning("⚠️ Please open a project workspace first")
    st.info("Return to the home page to create or open a project workspace")
    st.stop()

current_project = st.session_state['current_project']
engine = get_engine(current_project)
session = get_session(engine)

st.title("📡 Change Impact Signal Center")
st.markdown("### What deserves your attention right now?")

# Generate dashboard with error handling
try:
    with st.spinner("Reading sensors..."):
        signal_dashboard = SignalDashboard(session)
        dashboard = signal_dashboard.generate_dashboard()
except Exception as e:
    st.error(f"⚠️ Unable to generate Signal Center dashboard: {str(e)}")
    st.info("The Signal Center requires registry data to function. Please ensure your project has been initialized correctly.")
    st.markdown("---")
    st.markdown("### Quick Actions")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📝 Capture Impacts", use_container_width=True):
            st.switch_page("pages/02_Capture.py")
    with col2:
        if st.button("🔧 Setup", use_container_width=True):
            st.switch_page("pages/01_Setup.py")
    with col3:
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("app.py")
    st.stop()

# Registry Health Header
st.markdown("---")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.markdown("## Registry Health")
    
    # Try to create gauge chart, fall back to metrics if Plotly unavailable
    if PLOTLY_AVAILABLE:
        try:
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=dashboard.registry_health_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': f"Grade: {dashboard.registry_health_grade}", 'font': {'size': 24}},
                delta={'reference': 80, 'increasing': {'color': "green"}},
                gauge={
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': "darkblue"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 60], 'color': '#ffcccc'},
                        {'range': [60, 80], 'color': '#fff4cc'},
                        {'range': [80, 100], 'color': '#ccffcc'}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            
            fig.update_layout(
                height=250,
                margin=dict(l=20, r=20, t=50, b=20),
                font={'size': 16}
            )
            
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            # Graceful degradation if gauge rendering fails
            st.error(f"Unable to render gauge: {str(e)}")
            st.metric(
                "Registry Health Score",
                f"{dashboard.registry_health_score:.1f}/100",
                help="Overall registry health score"
            )
            st.metric("Grade", dashboard.registry_health_grade)
    else:
        # Fallback to standard metrics when Plotly not available
        st.metric(
            "Registry Health Score",
            f"{dashboard.registry_health_score:.1f}/100",
            help="Overall registry health score"
        )
        st.metric("Grade", dashboard.registry_health_grade)

with col2:
    st.markdown("### Status")
    status_emoji = dashboard.registry_health_status.value
    if dashboard.registry_health_status == SensorStatus.HEALTHY:
        st.success(f"✅ **Healthy**")
    elif dashboard.registry_health_status == SensorStatus.WARNING:
        st.warning(f"⚠️ **Needs Attention**")
    else:
        st.error(f"🔴 **Critical**")
    
    st.metric("Score", f"{dashboard.registry_health_score:.1f}/100")

with col3:
    st.markdown("### Signals")
    if dashboard.critical_signal_count > 0:
        st.error(f"🔴 {dashboard.critical_signal_count} Critical")
    if dashboard.high_signal_count > 0:
        st.warning(f"🟠 {dashboard.high_signal_count} High Priority")
    st.info(f"📋 {dashboard.total_signal_count} Total")

st.markdown("---")

# Sensors Grid
st.markdown("## Sensors")

# Row 1: Integrity, Coverage, Traceability
col1, col2, col3 = st.columns(3)

with col1:
    integrity = dashboard.integrity_reading
    st.markdown(f"### {integrity.get_status_emoji()} Data Integrity")
    st.metric("Score", f"{integrity.score:.1f}/100")
    st.caption(f"{integrity.status_text}")
    
    if integrity.records_with_issues > 0:
        st.warning(f"⚠️ {integrity.records_with_issues} record(s) with issues")
    
    if integrity.missing_fields_count > 0:
        st.caption(f"📝 {integrity.missing_fields_count} missing field(s)")
    if integrity.duplicate_count > 0:
        st.caption(f"🔄 {integrity.duplicate_count} duplicate(s)")
    
    if st.button("View Details", key="integrity_details"):
        st.session_state['sensor_drill_down'] = 'integrity'
        st.switch_page("pages/04_Analyze.py")

with col2:
    coverage = dashboard.coverage_reading
    st.markdown(f"### {coverage.get_status_emoji()} Coverage")
    st.metric("Score", f"{coverage.score:.1f}/100")
    st.caption(f"{coverage.status_text}")
    
    st.metric("Coverage", f"{coverage.coverage_percentage:.1f}%")
    
    if coverage.uncovered_stakeholders:
        st.caption(f"👥 {len(coverage.uncovered_stakeholders)} uncovered stakeholder(s)")
    if coverage.uncovered_org_units:
        st.caption(f"🏢 {len(coverage.uncovered_org_units)} uncovered org unit(s)")
    
    if st.button("View Details", key="coverage_details"):
        st.session_state['sensor_drill_down'] = 'coverage'
        st.switch_page("pages/04_Analyze.py")

with col3:
    traceability = dashboard.traceability_reading
    st.markdown(f"### {traceability.get_status_emoji()} Traceability")
    st.metric("Score", f"{traceability.score:.1f}/100")
    st.caption(f"{traceability.status_text}")
    
    st.metric("Traceability", f"{traceability.traceability_percentage:.1f}%")
    
    if traceability.orphaned_impacts > 0:
        st.error(f"🔴 {traceability.orphaned_impacts} orphaned impact(s)")
    if traceability.impacts_without_stakeholders > 0:
        st.caption(f"👥 {traceability.impacts_without_stakeholders} without stakeholders")
    
    if st.button("View Details", key="traceability_details"):
        st.session_state['sensor_drill_down'] = 'traceability'
        st.switch_page("pages/04_Analyze.py")

st.markdown("---")

# Row 2: Ownership, Distribution, Freshness
col1, col2, col3 = st.columns(3)

with col1:
    ownership = dashboard.ownership_reading
    st.markdown(f"### {ownership.get_status_emoji()} Ownership")
    st.metric("Score", f"{ownership.score:.1f}/100")
    st.caption(f"{ownership.status_text}")
    
    st.metric("Assigned", f"{ownership.ownership_percentage:.1f}%")
    
    if ownership.impacts_without_owner > 0:
        st.warning(f"⚠️ {ownership.impacts_without_owner} unassigned impact(s)")
    
    if st.button("View Details", key="ownership_details"):
        st.session_state['sensor_drill_down'] = 'ownership'
        st.switch_page("pages/04_Analyze.py")

with col2:
    distribution = dashboard.distribution_reading
    st.markdown(f"### {distribution.get_status_emoji()} Distribution")
    st.caption("Informational")
    
    st.metric("Total Impacts", distribution.total_impacts)
    
    if distribution.hotspots:
        st.info(f"🔥 {len(distribution.hotspots)} hotspot(s) identified")
    
    # Show severity distribution
    if distribution.by_severity:
        critical_count = distribution.by_severity.get('Critical', 0)
        high_count = distribution.by_severity.get('High', 0)
        if critical_count > 0:
            st.caption(f"🔴 {critical_count} Critical")
        if high_count > 0:
            st.caption(f"🟠 {high_count} High")
    
    if st.button("View Details", key="distribution_details"):
        st.session_state['sensor_drill_down'] = 'distribution'
        st.switch_page("pages/04_Analyze.py")

with col3:
    freshness = dashboard.freshness_reading
    st.markdown(f"### {freshness.get_status_emoji()} Freshness")
    st.metric("Score", f"{freshness.score:.1f}/100")
    st.caption(f"{freshness.status_text}")
    
    st.metric("Fresh", f"{freshness.freshness_percentage:.1f}%")
    
    if freshness.stale_impacts > 0:
        st.warning(f"⚠️ {freshness.stale_impacts} stale impact(s)")
    if freshness.recently_modified > 0:
        st.caption(f"✏️ {freshness.recently_modified} recently modified")
    
    if st.button("View Details", key="freshness_details"):
        st.session_state['sensor_drill_down'] = 'freshness'
        st.switch_page("pages/04_Analyze.py")

st.markdown("---")

# Recommendations Panel
if dashboard.critical_signals or dashboard.high_signals:
    st.markdown("## 🎯 Recommendations")
    
    # Critical signals
    if dashboard.critical_signals:
        st.markdown("### 🔴 Critical Priority")
        for signal in dashboard.critical_signals[:3]:  # Top 3
            with st.expander(f"**{signal.title}**", expanded=True):
                st.markdown(signal.description)
                if signal.action:
                    st.info(f"💡 **Action:** {signal.action}")
                if signal.affected_count > 0:
                    st.caption(f"Affects {signal.affected_count} record(s)")
    
    # High priority signals
    if dashboard.high_signals:
        st.markdown("### 🟠 High Priority")
        for signal in dashboard.high_signals[:3]:  # Top 3
            with st.expander(f"**{signal.title}**"):
                st.markdown(signal.description)
                if signal.action:
                    st.info(f"💡 **Action:** {signal.action}")
                if signal.affected_count > 0:
                    st.caption(f"Affects {signal.affected_count} record(s)")
    
    st.markdown("---")

# Quick Actions
st.markdown("## ⚡ Quick Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📝 Capture Impacts", use_container_width=True):
        st.switch_page("pages/02_Capture.py")

with col2:
    if st.button("🔗 Enrich Impacts", use_container_width=True):
        st.switch_page("pages/03_Enrich.py")

with col3:
    if st.button("📊 View Analysis", use_container_width=True):
        st.switch_page("pages/04_Analyze.py")

with col4:
    if st.button("📈 Monitor Progress", use_container_width=True):
        st.switch_page("pages/05_Monitor.py")

st.markdown("---")
st.caption(f"📁 Project: {current_project}")
st.caption("Signal Center provides real-time registry health monitoring. Sensors update automatically based on current registry state.")
