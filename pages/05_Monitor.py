import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database.schema import init_db, get_session, get_engine
from services.repository import Repository
from services.analytics import AnalyticsService

st.set_page_config(page_title="Monitor", page_icon="📈", layout="wide")

engine = init_db()
session = get_session(engine)
repo = Repository(session)
analytics = AnalyticsService(session)

st.title("📈 Monitor")
st.markdown("### Track Progress and Coverage")

if 'current_project_id' not in st.session_state:
    st.warning("⚠️ Please select or create a project in the Setup page first")
    st.stop()

project_id = st.session_state['current_project_id']
project = repo.get_project(project_id)

st.info(f"📁 Current Project: **{project.name}**")

impacts = repo.list_impacts(project_id)

tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Change Assets", "Status Tracking", "Export"])

with tab1:
    st.subheader("Project Dashboard")
    
    summary = analytics.get_impact_summary(project_id)
    coverage = analytics.get_coverage_metrics(project_id)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Impacts", summary['total'])
    with col2:
        st.metric("Coverage", f"{coverage['coverage_percentage']}%")
    with col3:
        approved = summary['by_status'].get('Approved', 0)
        st.metric("Approved", approved)
    with col4:
        closed = summary['by_status'].get('Closed', 0)
        completion_pct = (closed / summary['total'] * 100) if summary['total'] > 0 else 0
        st.metric("Completion", f"{completion_pct:.0f}%")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Status Distribution")
        if summary['by_status']:
            status_df = pd.DataFrame([
                {'Status': k, 'Count': v}
                for k, v in summary['by_status'].items()
            ])
            st.bar_chart(status_df.set_index('Status'))
        else:
            st.info("No status data available")
    
    with col2:
        st.markdown("#### Enrichment Progress")
        enrichment_data = pd.DataFrame([
            {'Metric': 'Stakeholder Groups', 'Count': coverage['with_stakeholder_groups']},
            {'Metric': 'Org Units', 'Count': coverage['with_organization_units']},
            {'Metric': 'Processes', 'Count': coverage['with_business_processes']},
            {'Metric': 'Systems', 'Count': coverage['with_systems']},
            {'Metric': 'Policies', 'Count': coverage['with_policies']}
        ])
        st.bar_chart(enrichment_data.set_index('Metric'))
    
    st.markdown("---")
    
    st.markdown("#### Recent Activity")
    recent_impacts = sorted(impacts, key=lambda x: x.updated_at or x.created_at, reverse=True)[:10]
    
    if recent_impacts:
        for impact in recent_impacts:
            update_time = impact.updated_at or impact.created_at
            time_ago = datetime.utcnow() - update_time
            
            if time_ago < timedelta(hours=1):
                time_str = f"{int(time_ago.total_seconds() / 60)} minutes ago"
            elif time_ago < timedelta(days=1):
                time_str = f"{int(time_ago.total_seconds() / 3600)} hours ago"
            else:
                time_str = f"{time_ago.days} days ago"
            
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{impact.impact_number}** - {impact.description[:60]}...")
            with col2:
                st.caption(f"Status: {impact.status}")
            with col3:
                st.caption(time_str)
    else:
        st.info("No recent activity")

with tab2:
    st.subheader("Change Assets Status")
    st.markdown("Monitor deliverables and artifacts across all impacts")
    
    all_assets = []
    for impact in impacts:
        assets = repo.list_change_assets(impact.id)
        for asset in assets:
            all_assets.append({
                'Impact': impact.impact_number,
                'Asset Name': asset.asset_name,
                'Type': asset.asset_type,
                'Status': asset.status,
                'Owner': asset.owner or 'Unassigned',
                'Description': asset.description
            })
    
    if all_assets:
        assets_df = pd.DataFrame(all_assets)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Assets", len(all_assets))
        with col2:
            complete = len([a for a in all_assets if a['Status'] == 'Complete'])
            st.metric("Complete", complete)
        with col3:
            in_progress = len([a for a in all_assets if a['Status'] == 'In Progress'])
            st.metric("In Progress", in_progress)
        with col4:
            planned = len([a for a in all_assets if a['Status'] == 'Planned'])
            st.metric("Planned", planned)
        
        st.markdown("---")
        
        filter_status = st.selectbox(
            "Filter by Status",
            ["All", "Planned", "In Progress", "Review", "Complete"]
        )
        
        if filter_status != "All":
            filtered_df = assets_df[assets_df['Status'] == filter_status]
        else:
            filtered_df = assets_df
        
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        
        st.markdown("#### Assets by Type")
        type_counts = assets_df['Type'].value_counts()
        st.bar_chart(type_counts)
    else:
        st.info("No change assets defined yet. Add them in the Enrich page.")

with tab3:
    st.subheader("Status Tracking")
    st.markdown("Track impact progression through workflow stages")
    
    if impacts:
        status_data = []
        for impact in impacts:
            status_data.append({
                'Impact Number': impact.impact_number,
                'Description': impact.description[:50] + '...',
                'Category': impact.category or 'Unspecified',
                'Severity': impact.severity or 'Unspecified',
                'Status': impact.status,
                'Updated': (impact.updated_at or impact.created_at).strftime('%Y-%m-%d')
            })
        
        status_df = pd.DataFrame(status_data)
        
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            filter_status = st.multiselect(
                "Filter by Status",
                ["Draft", "Under Review", "Approved", "Closed"],
                default=["Draft", "Under Review"]
            )
        with filter_col2:
            filter_severity = st.multiselect(
                "Filter by Severity",
                ["Low", "Medium", "High", "Critical", "Unspecified"],
                default=["High", "Critical"]
            )
        
        filtered_df = status_df
        if filter_status:
            filtered_df = filtered_df[filtered_df['Status'].isin(filter_status)]
        if filter_severity:
            filtered_df = filtered_df[filtered_df['Severity'].isin(filter_severity)]
        
        st.write(f"Showing {len(filtered_df)} of {len(status_df)} impacts")
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        st.markdown("#### Status Flow")
        st.markdown("""
        **Recommended Workflow:**
        1. **Draft** → Initial capture
        2. **Under Review** → Enrichment and validation
        3. **Approved** → Ready for action
        4. **Closed** → Addressed and complete
        """)
        
        workflow_metrics = pd.DataFrame([
            {'Stage': 'Draft', 'Count': summary['by_status'].get('Draft', 0)},
            {'Stage': 'Under Review', 'Count': summary['by_status'].get('Under Review', 0)},
            {'Stage': 'Approved', 'Count': summary['by_status'].get('Approved', 0)},
            {'Stage': 'Closed', 'Count': summary['by_status'].get('Closed', 0)}
        ])
        
        st.bar_chart(workflow_metrics.set_index('Stage'))
    else:
        st.info("No impacts to track")

with tab4:
    st.subheader("Export Data")
    st.markdown("Download impact data for reporting and analysis")
    
    if impacts:
        export_data = []
        for impact in impacts:
            sgs = repo.list_stakeholder_groups(project_id)
            ous = repo.list_organization_units(project_id)
            bps = repo.list_business_processes(project_id)
            systems = repo.list_systems(project_id)
            policies = repo.list_policies(project_id)
            
            sg_names = [sg.name for sg in sgs if sg.id in impact.stakeholder_group_ids]
            ou_names = [ou.name for ou in ous if ou.id in impact.organization_unit_ids]
            bp_names = [bp.name for bp in bps if bp.id in impact.business_process_ids]
            sys_names = [sys.name for sys in systems if sys.id in impact.system_ids]
            pol_names = [pol.name for pol in policies if pol.id in impact.policy_ids]
            
            export_data.append({
                'Impact Number': impact.impact_number,
                'Description': impact.description,
                'Category': impact.category,
                'Severity': impact.severity,
                'Likelihood': impact.likelihood,
                'Readiness': impact.readiness,
                'Resistance': impact.resistance,
                'Status': impact.status,
                'Mitigation Strategy': impact.mitigation_strategy,
                'Stakeholder Groups': '; '.join(sg_names),
                'Organization Units': '; '.join(ou_names),
                'Business Processes': '; '.join(bp_names),
                'Systems': '; '.join(sys_names),
                'Policies': '; '.join(pol_names),
                'Created': (impact.created_at or datetime.utcnow()).strftime('%Y-%m-%d'),
                'Updated': (impact.updated_at or datetime.utcnow()).strftime('%Y-%m-%d')
            })
        
        export_df = pd.DataFrame(export_data)
        
        st.markdown("#### Preview")
        st.dataframe(export_df.head(10), use_container_width=True, hide_index=True)
        
        st.markdown("#### Download Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv_data = export_df.to_csv(index=False)
            st.download_button(
                "📥 Download CSV",
                csv_data,
                f"{project.name.replace(' ', '_')}_impacts_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv",
                use_container_width=True
            )
        
        with col2:
            excel_buffer = pd.ExcelWriter('temp.xlsx', engine='openpyxl')
            export_df.to_excel(excel_buffer, index=False, sheet_name='Impacts')
            excel_buffer.close()
            
            st.info("Excel export available via CSV conversion")
        
        st.markdown("---")
        
        st.markdown("#### Summary Report")
        
        report = f"""
# Impact Registry Report
**Project:** {project.name}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Summary
- Total Impacts: {summary['total']}
- Coverage: {coverage['coverage_percentage']}%
- Approved: {summary['by_status'].get('Approved', 0)}
- Closed: {summary['by_status'].get('Closed', 0)}

## By Category
"""
        for category, count in summary['by_category'].items():
            report += f"- {category or 'Unspecified'}: {count}\n"
        
        report += "\n## By Severity\n"
        for severity, count in summary['by_severity'].items():
            report += f"- {severity or 'Unspecified'}: {count}\n"
        
        st.download_button(
            "📥 Download Summary Report (Markdown)",
            report,
            f"{project.name.replace(' ', '_')}_summary_{datetime.now().strftime('%Y%m%d')}.md",
            "text/markdown",
            use_container_width=True
        )
    else:
        st.info("No data to export")

st.markdown("---")
st.markdown("### 📊 Monitoring Best Practices")
st.markdown("""
- **Daily:** Check recent activity and new impacts
- **Weekly:** Review status progression and asset completion
- **Monthly:** Analyze coverage metrics and export reports
- **Milestone:** Generate comprehensive reports for stakeholders
""")
