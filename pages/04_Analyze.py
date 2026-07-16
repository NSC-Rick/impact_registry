import streamlit as st
import pandas as pd
from database.schema import init_db, get_session, get_engine
from services.repository import Repository
from services.analytics import AnalyticsService

st.set_page_config(page_title="Analyze", page_icon="📊", layout="wide")

engine = init_db()
session = get_session(engine)
repo = Repository(session)
analytics = AnalyticsService(session)

st.title("📊 Analyze")
st.markdown("### Understand Patterns and Risks")

if 'current_project_id' not in st.session_state:
    st.warning("⚠️ Please select or create a project in the Setup page first")
    st.stop()

project_id = st.session_state['current_project_id']
project = repo.get_project(project_id)

st.info(f"📁 Current Project: **{project.name}**")

impacts = repo.list_impacts(project_id)

if not impacts:
    st.warning("⚠️ No impacts found. Please capture impacts first in the Capture page.")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs(["Summary", "Risk Matrix", "Coverage", "Traceability"])

with tab1:
    st.subheader("Impact Summary")
    
    summary = analytics.get_impact_summary(project_id)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Impacts", summary['total'])
    with col2:
        draft_count = summary['by_status'].get('Draft', 0)
        st.metric("Draft", draft_count)
    with col3:
        approved_count = summary['by_status'].get('Approved', 0)
        st.metric("Approved", approved_count)
    with col4:
        closed_count = summary['by_status'].get('Closed', 0)
        st.metric("Closed", closed_count)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### By Category")
        if summary['by_category']:
            category_df = pd.DataFrame([
                {'Category': k or 'Unspecified', 'Count': v}
                for k, v in summary['by_category'].items()
            ])
            st.bar_chart(category_df.set_index('Category'))
            st.dataframe(category_df, use_container_width=True, hide_index=True)
        else:
            st.info("No category data available")
    
    with col2:
        st.markdown("#### By Severity")
        if summary['by_severity']:
            severity_df = pd.DataFrame([
                {'Severity': k or 'Unspecified', 'Count': v}
                for k, v in summary['by_severity'].items()
            ])
            
            severity_order = ['Critical', 'High', 'Medium', 'Low', 'Unspecified']
            severity_df['Order'] = severity_df['Severity'].apply(
                lambda x: severity_order.index(x) if x in severity_order else 999
            )
            severity_df = severity_df.sort_values('Order').drop('Order', axis=1)
            
            st.bar_chart(severity_df.set_index('Severity'))
            st.dataframe(severity_df, use_container_width=True, hide_index=True)
        else:
            st.info("No severity data available")

with tab2:
    st.subheader("Risk Matrix")
    st.markdown("Impacts plotted by Severity and Likelihood")
    
    risk_matrix = analytics.get_risk_matrix(project_id)
    
    if risk_matrix:
        matrix_df = pd.DataFrame(risk_matrix, columns=['ID', 'Number', 'Description', 'Severity', 'Likelihood'])
        
        severity_map = {'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 4}
        likelihood_map = {'Low': 1, 'Medium': 2, 'High': 3}
        
        matrix_df['Severity_Num'] = matrix_df['Severity'].map(severity_map)
        matrix_df['Likelihood_Num'] = matrix_df['Likelihood'].map(likelihood_map)
        
        st.markdown("#### Risk Distribution")
        
        risk_counts = matrix_df.groupby(['Severity', 'Likelihood']).size().reset_index(name='Count')
        
        pivot_table = risk_counts.pivot(index='Severity', columns='Likelihood', values='Count').fillna(0)
        
        severity_order = ['Critical', 'High', 'Medium', 'Low']
        likelihood_order = ['Low', 'Medium', 'High']
        
        pivot_table = pivot_table.reindex(severity_order, fill_value=0)
        pivot_table = pivot_table.reindex(columns=likelihood_order, fill_value=0)
        
        st.dataframe(pivot_table, use_container_width=True)
        
        st.markdown("#### High Risk Impacts")
        high_risk = matrix_df[
            (matrix_df['Severity_Num'] >= 3) & (matrix_df['Likelihood_Num'] >= 2)
        ].sort_values(['Severity_Num', 'Likelihood_Num'], ascending=False)
        
        if not high_risk.empty:
            for _, row in high_risk.iterrows():
                with st.expander(f"**{row['Number']}** - {row['Description']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Severity", row['Severity'])
                    with col2:
                        st.metric("Likelihood", row['Likelihood'])
                    
                    if st.button(f"View Details", key=f"view_{row['ID']}"):
                        st.session_state['edit_impact_id'] = row['ID']
                        st.switch_page("pages/03_Enrich.py")
        else:
            st.success("✅ No high-risk impacts identified")
    else:
        st.info("No impacts with both Severity and Likelihood specified")

with tab3:
    st.subheader("Coverage Metrics")
    st.markdown("Track how well impacts are enriched with traceability")
    
    coverage = analytics.get_coverage_metrics(project_id)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Impacts", coverage['total_impacts'])
    with col2:
        st.metric("Enriched Impacts", coverage['enriched_impacts'])
    with col3:
        st.metric("Coverage %", f"{coverage['coverage_percentage']}%")
    
    st.markdown("---")
    
    st.markdown("#### Enrichment Breakdown")
    
    enrichment_data = pd.DataFrame([
        {'Asset Type': 'Stakeholder Groups', 'Count': coverage['with_stakeholder_groups']},
        {'Asset Type': 'Organization Units', 'Count': coverage['with_organization_units']},
        {'Asset Type': 'Business Processes', 'Count': coverage['with_business_processes']},
        {'Asset Type': 'Systems', 'Count': coverage['with_systems']},
        {'Asset Type': 'Policies', 'Count': coverage['with_policies']}
    ])
    
    st.bar_chart(enrichment_data.set_index('Asset Type'))
    st.dataframe(enrichment_data, use_container_width=True, hide_index=True)
    
    if coverage['coverage_percentage'] < 50:
        st.warning("⚠️ Coverage is below 50%. Consider enriching more impacts with traceability.")
    elif coverage['coverage_percentage'] < 80:
        st.info("📈 Good progress! Continue enriching impacts to improve coverage.")
    else:
        st.success("✅ Excellent coverage! Most impacts have traceability.")

with tab4:
    st.subheader("Traceability Analysis")
    st.markdown("Understand which enterprise assets are most affected")
    
    analysis_tab1, analysis_tab2, analysis_tab3 = st.tabs([
        "Stakeholder Groups", "Business Processes", "Systems"
    ])
    
    with analysis_tab1:
        st.markdown("#### Impacts by Stakeholder Group")
        sg_counts = analytics.get_stakeholder_impact_count(project_id)
        
        if sg_counts:
            sg_df = pd.DataFrame(sg_counts, columns=['Stakeholder Group', 'Impact Count'])
            sg_df = sg_df.sort_values('Impact Count', ascending=False)
            
            st.bar_chart(sg_df.set_index('Stakeholder Group'))
            st.dataframe(sg_df, use_container_width=True, hide_index=True)
            
            top_sg = sg_df.iloc[0]
            st.info(f"📌 Most affected: **{top_sg['Stakeholder Group']}** with {top_sg['Impact Count']} impacts")
        else:
            st.info("No stakeholder group traceability data available")
    
    with analysis_tab2:
        st.markdown("#### Impacts by Business Process")
        bp_counts = analytics.get_process_impact_count(project_id)
        
        if bp_counts:
            bp_df = pd.DataFrame(bp_counts, columns=['Business Process', 'Impact Count'])
            bp_df = bp_df.sort_values('Impact Count', ascending=False)
            
            st.bar_chart(bp_df.set_index('Business Process'))
            st.dataframe(bp_df, use_container_width=True, hide_index=True)
            
            top_bp = bp_df.iloc[0]
            st.info(f"📌 Most affected: **{top_bp['Business Process']}** with {top_bp['Impact Count']} impacts")
        else:
            st.info("No business process traceability data available")
    
    with analysis_tab3:
        st.markdown("#### Impacts by System")
        sys_counts = analytics.get_system_impact_count(project_id)
        
        if sys_counts:
            sys_df = pd.DataFrame(sys_counts, columns=['System', 'Impact Count'])
            sys_df = sys_df.sort_values('Impact Count', ascending=False)
            
            st.bar_chart(sys_df.set_index('System'))
            st.dataframe(sys_df, use_container_width=True, hide_index=True)
            
            top_sys = sys_df.iloc[0]
            st.info(f"📌 Most affected: **{top_sys['System']}** with {top_sys['Impact Count']} impacts")
        else:
            st.info("No system traceability data available")

st.markdown("---")
st.markdown("### 💡 Analysis Insights")

insights = []

if summary['total'] < 10:
    insights.append("📝 Consider capturing more impacts to get better analytical insights")
elif summary['total'] >= 50:
    insights.append("✅ Good impact coverage - you have sufficient data for meaningful analysis")

if coverage['coverage_percentage'] < 30:
    insights.append("🔗 Low traceability - enrich impacts with enterprise assets to improve analysis")

draft_pct = (summary['by_status'].get('Draft', 0) / summary['total'] * 100) if summary['total'] > 0 else 0
if draft_pct > 50:
    insights.append(f"📋 {draft_pct:.0f}% of impacts are still in Draft status - consider reviewing and approving")

high_severity = summary['by_severity'].get('High', 0) + summary['by_severity'].get('Critical', 0)
if high_severity > 0:
    insights.append(f"⚠️ {high_severity} high/critical severity impacts require attention")

if insights:
    for insight in insights:
        st.markdown(f"- {insight}")
else:
    st.success("✅ Your impact registry is well-maintained!")
