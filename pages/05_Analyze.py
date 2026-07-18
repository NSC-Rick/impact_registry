import streamlit as st
import os
import pandas as pd
from database.schema import get_session, get_engine, ProjectMetadata
from services.project_context import ProjectContext
from analysis.registry_analysis_engine import RegistryAnalysisEngine

# Check for active project workspace using ProjectContext
if not ProjectContext.has_active_project():
    st.warning("⚠️ Please open a project workspace first")
    st.info("Return to the home page to create or open a project workspace")
    st.stop()

# Get active project from ProjectContext
active_project = ProjectContext.get_active_project()
print(f"\n[ANALYZE] Database: {os.path.abspath(active_project.file_path)}")

engine = get_engine(active_project.file_path)
session = get_session(engine)

# Get project metadata
metadata = session.query(ProjectMetadata).first()

st.title("📊 Analyze")
st.markdown("### Registry Quality & Health Analysis")
st.success(f"📁 **{active_project.name}**")

# Initialize Registry Analysis Engine
with st.spinner("Analyzing registry..."):
    analysis_engine = RegistryAnalysisEngine(session)
    health_result = analysis_engine.analyze_registry()

# Display Registry Health Score
st.markdown("---")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Registry Health",
        f"{health_result.overall_score:.1f}",
        help="Overall registry health score (0-100)"
    )
    if health_result.health_grade == "A":
        st.success(f"Grade: {health_result.health_grade}")
    elif health_result.health_grade == "B":
        st.info(f"Grade: {health_result.health_grade}")
    elif health_result.health_grade == "C":
        st.warning(f"Grade: {health_result.health_grade}")
    else:
        st.error(f"Grade: {health_result.health_grade}")

with col2:
    st.metric(
        "Data Integrity",
        f"{health_result.integrity_score:.1f}",
        help="Data quality and completeness (30% weight)"
    )

with col3:
    st.metric(
        "Coverage",
        f"{health_result.coverage_score:.1f}",
        help="Organizational coverage (25% weight)"
    )

with col4:
    st.metric(
        "Traceability",
        f"{health_result.traceability_score:.1f}",
        help="Relationship completeness (20% weight)"
    )

with col5:
    st.metric(
        "Freshness",
        f"{health_result.freshness_score:.1f}",
        help="Data recency (10% weight)"
    )

st.markdown("---")

# Display Key Findings
if health_result.critical_findings > 0 or health_result.high_findings > 0:
    st.markdown("### ⚠️ Key Findings")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if health_result.critical_findings > 0:
            st.error(f"🔴 {health_result.critical_findings} Critical Issue(s)")
    with col2:
        if health_result.high_findings > 0:
            st.warning(f"🟠 {health_result.high_findings} High Priority Issue(s)")
    with col3:
        st.info(f"📋 {health_result.total_findings} Total Finding(s)")
    
    st.markdown("---")

# Display Recommendations
if health_result.recommendations:
    st.markdown("### 💡 Recommendations")
    for rec in health_result.recommendations:
        st.markdown(f"- {rec}")
    st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Integrity",
    "Coverage",
    "Traceability",
    "Distribution",
    "Freshness"
])

with tab1:
    st.subheader("Data Integrity Analysis")
    st.markdown(f"**Score: {health_result.integrity_score:.1f}/100**")
    
    integrity = health_result.integrity_result
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Records", integrity.total_records)
    with col2:
        st.metric("Records with Issues", integrity.records_with_issues)
    
    st.markdown("---")
    
    if integrity.missing_required_fields:
        st.markdown("#### Missing Required Fields")
        missing_df = pd.DataFrame([
            {'Field': k, 'Missing Count': v}
            for k, v in integrity.missing_required_fields.items()
        ])
        st.dataframe(missing_df, use_container_width=True, hide_index=True)
    
    if integrity.duplicate_impacts:
        st.markdown("#### Duplicate Impact Numbers")
        st.warning(f"{len(integrity.duplicate_impacts)} duplicate impact number(s) found")
        for dup in integrity.duplicate_impacts[:5]:
            st.caption(f"Impact Number: {dup['impact_number']} ({dup['count']} records)")
    
    if integrity.duplicate_assets:
        st.markdown("#### Duplicate Assets")
        for asset_type, duplicates in integrity.duplicate_assets.items():
            st.warning(f"{len(duplicates)} duplicate {asset_type.replace('_', ' ')}")
    
    if integrity.findings:
        st.markdown("#### Integrity Findings")
        for finding in integrity.findings:
            severity_icon = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🔵", "Info": "ℹ️"}
            icon = severity_icon.get(finding.severity, "")
            with st.expander(f"{icon} {finding.title}"):
                st.markdown(f"**Category:** {finding.category}")
                st.markdown(f"**Description:** {finding.description}")
                if finding.recommendation:
                    st.info(f"💡 **Recommendation:** {finding.recommendation}")

with tab2:
    st.subheader("Coverage Analysis")
    st.markdown(f"**Score: {health_result.coverage_score:.1f}/100**")
    
    coverage = health_result.coverage_result
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Impacts", coverage.total_impacts)
    with col2:
        st.metric("With Stakeholders", coverage.impacts_with_stakeholders)
    with col3:
        st.metric("With Org Units", coverage.impacts_with_org_units)
    with col4:
        st.metric("With Processes", coverage.impacts_with_processes)
    
    st.markdown("---")
    
    if coverage.stakeholder_coverage:
        st.markdown("#### Stakeholder Group Coverage")
        sg_df = pd.DataFrame([
            {'Stakeholder Group': k, 'Impact Count': v}
            for k, v in coverage.stakeholder_coverage.items()
        ]).sort_values('Impact Count', ascending=False)
        st.dataframe(sg_df, use_container_width=True, hide_index=True)
    
    if coverage.uncovered_stakeholders:
        st.warning(f"⚠️ {len(coverage.uncovered_stakeholders)} stakeholder group(s) without impacts")
        with st.expander("View uncovered stakeholder groups"):
            for sg in coverage.uncovered_stakeholders:
                st.caption(f"- {sg}")
    
    if coverage.uncovered_org_units:
        st.warning(f"⚠️ {len(coverage.uncovered_org_units)} organization unit(s) without impacts")
        with st.expander("View uncovered organization units"):
            for ou in coverage.uncovered_org_units:
                st.caption(f"- {ou}")
    
    if coverage.findings:
        st.markdown("#### Coverage Findings")
        for finding in coverage.findings:
            severity_icon = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🔵", "Info": "ℹ️"}
            icon = severity_icon.get(finding.severity, "")
            with st.expander(f"{icon} {finding.title}"):
                st.markdown(f"**Description:** {finding.description}")
                if finding.recommendation:
                    st.info(f"💡 **Recommendation:** {finding.recommendation}")

with tab3:
    st.subheader("Traceability Analysis")
    st.markdown(f"**Score: {health_result.traceability_score:.1f}/100**")
    
    traceability = health_result.traceability_result
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Impacts", traceability.total_impacts)
    with col2:
        st.metric("Without Stakeholders", traceability.impacts_without_stakeholders)
    with col3:
        st.metric("Without Assets", traceability.impacts_without_assets)
    with col4:
        st.metric("Without Category", traceability.impacts_without_category)
    
    st.markdown("---")
    
    if traceability.orphaned_impact_ids:
        st.error(f"🔴 {len(traceability.orphaned_impact_ids)} orphaned impact(s) with no relationships")
        st.caption("These impacts have no links to stakeholders, org units, processes, systems, or policies.")
    
    if traceability.findings:
        st.markdown("#### Traceability Findings")
        for finding in traceability.findings:
            severity_icon = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🔵", "Info": "ℹ️"}
            icon = severity_icon.get(finding.severity, "")
            with st.expander(f"{icon} {finding.title}"):
                st.markdown(f"**Description:** {finding.description}")
                if finding.affected_records:
                    st.caption(f"Affected Records: {len(finding.affected_records)} impact(s)")
                if finding.recommendation:
                    st.info(f"💡 **Recommendation:** {finding.recommendation}")

with tab4:
    st.subheader("Distribution Analysis")
    
    distribution = health_result.distribution_result
    
    st.metric("Total Impacts", distribution.total_impacts)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### By Severity")
        if distribution.by_severity:
            severity_df = pd.DataFrame([
                {'Severity': k, 'Count': v}
                for k, v in distribution.by_severity.items()
            ])
            st.bar_chart(severity_df.set_index('Severity'))
            st.dataframe(severity_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("#### By Category")
        if distribution.by_category:
            category_df = pd.DataFrame([
                {'Category': k, 'Count': v}
                for k, v in distribution.by_category.items()
            ])
            st.bar_chart(category_df.set_index('Category'))
            st.dataframe(category_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    st.markdown("#### By Status")
    if distribution.by_status:
        status_df = pd.DataFrame([
            {'Status': k, 'Count': v}
            for k, v in distribution.by_status.items()
        ])
        st.dataframe(status_df, use_container_width=True, hide_index=True)
    
    if distribution.hotspots:
        st.markdown("#### Impact Hotspots")
        st.info("Areas with high concentration of impacts")
        for hotspot in distribution.hotspots:
            st.markdown(f"- **{hotspot['dimension']}:** {hotspot['value']} ({hotspot['count']} impacts, {hotspot['percentage']}%)")

with tab5:
    st.subheader("Freshness Analysis")
    st.markdown(f"**Score: {health_result.freshness_score:.1f}/100**")
    
    freshness = health_result.freshness_result
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Impacts", freshness.total_impacts)
    with col2:
        st.metric("Created (7 days)", freshness.recently_created)
    with col3:
        st.metric("Modified (7 days)", freshness.recently_modified)
    with col4:
        st.metric("Stale (30+ days)", freshness.stale_impacts)
    
    st.markdown("---")
    
    st.metric("Average Age (days)", f"{freshness.average_age_days:.1f}")
    
    if freshness.stale_impacts > 0:
        st.warning(f"⚠️ {freshness.stale_impacts} impact(s) not updated in 30+ days")
    
    if freshness.findings:
        st.markdown("#### Freshness Findings")
        for finding in freshness.findings:
            severity_icon = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🔵", "Info": "ℹ️"}
            icon = severity_icon.get(finding.severity, "")
            with st.expander(f"{icon} {finding.title}"):
                st.markdown(f"**Description:** {finding.description}")
                if finding.recommendation:
                    st.info(f"💡 **Recommendation:** {finding.recommendation}")

st.markdown("---")
st.caption(f"Analysis completed at: {health_result.analyzed_at.strftime('%Y-%m-%d %H:%M:%S')} UTC")
