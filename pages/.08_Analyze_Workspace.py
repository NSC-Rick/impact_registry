import streamlit as st
import pandas as pd
from datetime import datetime
from database.schema import init_db, get_session, get_engine
from services.repository import Repository
from services.analytics import AnalyticsService

st.set_page_config(page_title="Analyze Workspace", page_icon="📊", layout="wide")

engine = init_db()
session = get_session(engine)
repo = Repository(session)
analytics = AnalyticsService(session)

st.title("📊 Analyze Workspace")
st.markdown("### Transform Registry Data into Organizational Intelligence")

if 'current_project_id' not in st.session_state:
    st.warning("⚠️ Please select or create a project in the Setup page first")
    st.stop()

project_id = st.session_state['current_project_id']
project = repo.get_project(project_id)

st.info(f"📁 **Project:** {project.name}")

impacts = repo.list_impacts(project_id)

if not impacts:
    st.warning("⚠️ No impacts found. Please capture impacts first.")
    st.stop()

stakeholder_groups = repo.list_stakeholder_groups(project_id)
organization_units = repo.list_organization_units(project_id)
business_processes = repo.list_business_processes(project_id)
systems = repo.list_systems(project_id)
policies = repo.list_policies(project_id)

st.sidebar.markdown("### 🔍 Filters & Search")

search_query = st.sidebar.text_input(
    "🔎 Search",
    placeholder="Impact ID, keyword, asset name...",
    help="Search across all fields"
)

st.sidebar.markdown("#### Filter by:")

filter_status = st.sidebar.multiselect(
    "Status",
    ["Draft", "Under Review", "Approved", "Superseded"],
    default=["Draft", "Approved"]
)

filter_sg = st.sidebar.multiselect(
    "Stakeholder Group",
    [sg.name for sg in stakeholder_groups]
)

filter_bp = st.sidebar.multiselect(
    "Business Process",
    [bp.name for bp in business_processes]
)

filter_sys = st.sidebar.multiselect(
    "System",
    [sys.name for sys in systems]
)

filtered_impacts = impacts.copy()

if filter_status:
    filtered_impacts = [i for i in filtered_impacts if i.status in filter_status]

if filter_sg:
    sg_ids = [sg.id for sg in stakeholder_groups if sg.name in filter_sg]
    filtered_impacts = [i for i in filtered_impacts if any(sg_id in i.stakeholder_group_ids for sg_id in sg_ids)]

if filter_bp:
    bp_ids = [bp.id for bp in business_processes if bp.name in filter_bp]
    filtered_impacts = [i for i in filtered_impacts if any(bp_id in i.business_process_ids for bp_id in bp_ids)]

if filter_sys:
    sys_ids = [sys.id for sys in systems if sys.name in filter_sys]
    filtered_impacts = [i for i in filtered_impacts if any(sys_id in i.system_ids for sys_id in sys_ids)]

if search_query:
    search_lower = search_query.lower()
    filtered_impacts = [
        i for i in filtered_impacts
        if (search_lower in i.impact_number.lower() if i.impact_number else False) or
           (search_lower in i.title.lower() if i.title else False) or
           (search_lower in i.description.lower() if i.description else False)
    ]

st.sidebar.markdown(f"**Showing:** {len(filtered_impacts)} of {len(impacts)} impacts")

if st.sidebar.button("🔄 Clear All Filters"):
    st.rerun()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "🏢 Enterprise Assets",
    "📦 Coverage Analysis",
    "🔍 Impact Explorer",
    "🏥 Registry Health"
])

with tab1:
    st.markdown("### Overview Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Impacts", len(filtered_impacts))
    with col2:
        approved = len([i for i in filtered_impacts if i.status == "Approved"])
        st.metric("Approved", approved)
    with col3:
        draft = len([i for i in filtered_impacts if i.status == "Draft"])
        st.metric("Draft", draft)
    with col4:
        with_coverage = sum(1 for i in filtered_impacts if len(repo.list_change_assets(i.id)) > 0)
        coverage_pct = (with_coverage / len(filtered_impacts) * 100) if filtered_impacts else 0
        st.metric("Coverage", f"{coverage_pct:.0f}%")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Impacts by Status")
        
        status_counts = {}
        for impact in filtered_impacts:
            status_counts[impact.status] = status_counts.get(impact.status, 0) + 1
        
        if status_counts:
            status_df = pd.DataFrame([
                {'Status': k, 'Count': v}
                for k, v in status_counts.items()
            ])
            
            st.bar_chart(status_df.set_index('Status'))
            
            for status, count in status_counts.items():
                if st.button(f"🔍 View {status} ({count})", key=f"status_{status}"):
                    st.session_state['drill_through_filter'] = {'status': status}
                    st.session_state['active_tab'] = 'Impact Explorer'
                    st.rerun()
    
    with col2:
        st.markdown("#### 📂 Impacts by Area of Change")
        
        area_counts = {}
        for impact in filtered_impacts:
            area = impact.area_of_change or "Unspecified"
            area_counts[area] = area_counts.get(area, 0) + 1
        
        if area_counts:
            area_df = pd.DataFrame([
                {'Area': k, 'Count': v}
                for k, v in sorted(area_counts.items(), key=lambda x: x[1], reverse=True)
            ])
            
            st.bar_chart(area_df.set_index('Area'))
            
            st.dataframe(area_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    st.markdown("#### 🎯 Primary Business Questions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**How many approved impacts exist?**")
        approved_count = len([i for i in filtered_impacts if i.status == "Approved"])
        st.markdown(f"➜ **{approved_count}** approved impacts")
        
        st.markdown("**Which impacts have no coverage?**")
        no_coverage = []
        for impact in filtered_impacts:
            assets = repo.list_change_assets(impact.id)
            if len(assets) == 0:
                no_coverage.append(impact)
        st.markdown(f"➜ **{len(no_coverage)}** impacts without change assets")
        if st.button("🔍 View Impacts Without Coverage"):
            st.session_state['drill_through_filter'] = {'no_coverage': True}
            st.session_state['active_tab'] = 'Impact Explorer'
            st.rerun()
    
    with col2:
        st.markdown("**Which impacts have no Source Evidence?**")
        no_evidence = []
        for impact in filtered_impacts:
            evidences = repo.list_source_evidences(impact.id)
            if len(evidences) == 0:
                no_evidence.append(impact)
        st.markdown(f"➜ **{len(no_evidence)}** impacts without source evidence")
        if st.button("🔍 View Impacts Without Evidence"):
            st.session_state['drill_through_filter'] = {'no_evidence': True}
            st.session_state['active_tab'] = 'Impact Explorer'
            st.rerun()
        
        st.markdown("**Which Stakeholder Groups are affected most?**")
        if stakeholder_groups:
            sg_counts = analytics.get_stakeholder_impact_count(project_id)
            if sg_counts:
                top_sg = max(sg_counts, key=lambda x: x[1])
                st.markdown(f"➜ **{top_sg[0]}** with {top_sg[1]} impacts")

with tab2:
    st.markdown("### Enterprise Asset Analysis")
    
    analysis_tab1, analysis_tab2, analysis_tab3, analysis_tab4 = st.tabs([
        "Stakeholder Groups",
        "Business Processes",
        "Systems",
        "Policies"
    ])
    
    with analysis_tab1:
        st.markdown("#### 👥 Stakeholder Groups")
        
        if stakeholder_groups:
            sg_impact_counts = []
            for sg in stakeholder_groups:
                count = sum(1 for i in filtered_impacts if sg.id in i.stakeholder_group_ids)
                sg_impact_counts.append({
                    'Stakeholder Group': sg.name,
                    'Impact Count': count,
                    'Size': sg.size or 0,
                    'Influence': sg.influence or 'Not set'
                })
            
            sg_df = pd.DataFrame(sg_impact_counts)
            sg_df = sg_df.sort_values('Impact Count', ascending=False)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("**Impact Count by Stakeholder Group**")
                chart_df = sg_df[sg_df['Impact Count'] > 0]
                if not chart_df.empty:
                    st.bar_chart(chart_df.set_index('Stakeholder Group')['Impact Count'])
            
            with col2:
                st.markdown("**Top 5 Most Affected**")
                top_5 = sg_df.head(5)
                for _, row in top_5.iterrows():
                    if row['Impact Count'] > 0:
                        if st.button(f"{row['Stakeholder Group']} ({row['Impact Count']})", 
                                   key=f"sg_{row['Stakeholder Group']}",
                                   use_container_width=True):
                            st.session_state['drill_through_filter'] = {'stakeholder_group': row['Stakeholder Group']}
                            st.session_state['active_tab'] = 'Impact Explorer'
                            st.rerun()
            
            st.markdown("---")
            st.markdown("**Complete Analysis**")
            st.dataframe(sg_df, use_container_width=True, hide_index=True)
        else:
            st.info("No stakeholder groups defined")
    
    with analysis_tab2:
        st.markdown("#### 🔄 Business Processes")
        
        if business_processes:
            bp_impact_counts = []
            for bp in business_processes:
                count = sum(1 for i in filtered_impacts if bp.id in i.business_process_ids)
                bp_impact_counts.append({
                    'Business Process': bp.name,
                    'Impact Count': count,
                    'Criticality': bp.criticality or 'Not set',
                    'Owner': bp.process_owner or 'Not set'
                })
            
            bp_df = pd.DataFrame(bp_impact_counts)
            bp_df = bp_df.sort_values('Impact Count', ascending=False)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("**Impact Count by Business Process**")
                chart_df = bp_df[bp_df['Impact Count'] > 0]
                if not chart_df.empty:
                    st.bar_chart(chart_df.set_index('Business Process')['Impact Count'])
            
            with col2:
                st.markdown("**Top 5 Most Impacted**")
                top_5 = bp_df.head(5)
                for _, row in top_5.iterrows():
                    if row['Impact Count'] > 0:
                        if st.button(f"{row['Business Process']} ({row['Impact Count']})", 
                                   key=f"bp_{row['Business Process']}",
                                   use_container_width=True):
                            st.session_state['drill_through_filter'] = {'business_process': row['Business Process']}
                            st.session_state['active_tab'] = 'Impact Explorer'
                            st.rerun()
            
            st.markdown("---")
            st.markdown("**Complete Analysis**")
            st.dataframe(bp_df, use_container_width=True, hide_index=True)
            
            st.markdown("#### 🎯 High Criticality Processes")
            critical_bp = bp_df[bp_df['Criticality'].isin(['High', 'Critical'])]
            if not critical_bp.empty:
                st.dataframe(critical_bp, use_container_width=True, hide_index=True)
            else:
                st.info("No high criticality processes identified")
        else:
            st.info("No business processes defined")
    
    with analysis_tab3:
        st.markdown("#### 💻 Systems")
        
        if systems:
            sys_impact_counts = []
            for sys in systems:
                count = sum(1 for i in filtered_impacts if sys.id in i.system_ids)
                sys_impact_counts.append({
                    'System': sys.name,
                    'Impact Count': count,
                    'Criticality': sys.criticality or 'Not set',
                    'Vendor': sys.vendor or 'Not set'
                })
            
            sys_df = pd.DataFrame(sys_impact_counts)
            sys_df = sys_df.sort_values('Impact Count', ascending=False)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("**Impact Count by System**")
                chart_df = sys_df[sys_df['Impact Count'] > 0]
                if not chart_df.empty:
                    st.bar_chart(chart_df.set_index('System')['Impact Count'])
            
            with col2:
                st.markdown("**Top 5 Most Impacted**")
                top_5 = sys_df.head(5)
                for _, row in top_5.iterrows():
                    if row['Impact Count'] > 0:
                        if st.button(f"{row['System']} ({row['Impact Count']})", 
                                   key=f"sys_{row['System']}",
                                   use_container_width=True):
                            st.session_state['drill_through_filter'] = {'system': row['System']}
                            st.session_state['active_tab'] = 'Impact Explorer'
                            st.rerun()
            
            st.markdown("---")
            st.markdown("**Complete Analysis**")
            st.dataframe(sys_df, use_container_width=True, hide_index=True)
        else:
            st.info("No systems defined")
    
    with analysis_tab4:
        st.markdown("#### 📋 Policies")
        
        if policies:
            pol_impact_counts = []
            for pol in policies:
                count = sum(1 for i in filtered_impacts if pol.id in i.policy_ids)
                pol_impact_counts.append({
                    'Policy': pol.name,
                    'Impact Count': count,
                    'Owner': pol.policy_owner or 'Not set'
                })
            
            pol_df = pd.DataFrame(pol_impact_counts)
            pol_df = pol_df.sort_values('Impact Count', ascending=False)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("**Impact Count by Policy**")
                chart_df = pol_df[pol_df['Impact Count'] > 0]
                if not chart_df.empty:
                    st.bar_chart(chart_df.set_index('Policy')['Impact Count'])
            
            with col2:
                st.markdown("**Top 5 Most Referenced**")
                top_5 = pol_df.head(5)
                for _, row in top_5.iterrows():
                    if row['Impact Count'] > 0:
                        if st.button(f"{row['Policy']} ({row['Impact Count']})", 
                                   key=f"pol_{row['Policy']}",
                                   use_container_width=True):
                            st.session_state['drill_through_filter'] = {'policy': row['Policy']}
                            st.session_state['active_tab'] = 'Impact Explorer'
                            st.rerun()
            
            st.markdown("---")
            st.markdown("**Complete Analysis**")
            st.dataframe(pol_df, use_container_width=True, hide_index=True)
        else:
            st.info("No policies defined")

with tab3:
    st.markdown("### Coverage Analysis")
    
    st.markdown("#### 📦 Change Assets by Type")
    
    all_change_assets = []
    for impact in filtered_impacts:
        assets = repo.list_change_assets(impact.id)
        for asset in assets:
            all_change_assets.append({
                'Type': asset.asset_type,
                'Name': asset.asset_name,
                'Status': asset.status,
                'Impact': impact.impact_number
            })
    
    if all_change_assets:
        assets_df = pd.DataFrame(all_change_assets)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Assets by Type**")
            type_counts = assets_df['Type'].value_counts()
            st.bar_chart(type_counts)
            
            st.dataframe(
                pd.DataFrame({'Type': type_counts.index, 'Count': type_counts.values}),
                use_container_width=True,
                hide_index=True
            )
        
        with col2:
            st.markdown("**Assets by Status**")
            status_counts = assets_df['Status'].value_counts()
            st.bar_chart(status_counts)
            
            st.dataframe(
                pd.DataFrame({'Status': status_counts.index, 'Count': status_counts.values}),
                use_container_width=True,
                hide_index=True
            )
        
        st.markdown("---")
        
        st.markdown("#### 🎯 Coverage Distribution")
        
        coverage_data = []
        for impact in filtered_impacts:
            assets = repo.list_change_assets(impact.id)
            coverage_data.append({
                'Impact': impact.impact_number,
                'Title': impact.title or impact.description[:50],
                'Asset Count': len(assets),
                'Status': impact.status
            })
        
        coverage_df = pd.DataFrame(coverage_data)
        coverage_df = coverage_df.sort_values('Asset Count', ascending=False)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_coverage = coverage_df['Asset Count'].mean()
            st.metric("Avg Assets per Impact", f"{avg_coverage:.1f}")
        with col2:
            max_coverage = coverage_df['Asset Count'].max()
            st.metric("Max Assets", int(max_coverage))
        with col3:
            no_coverage = len(coverage_df[coverage_df['Asset Count'] == 0])
            st.metric("No Coverage", no_coverage)
        
        st.markdown("**Top 10 Most Covered Impacts**")
        st.dataframe(coverage_df.head(10), use_container_width=True, hide_index=True)
        
        st.markdown("**All Change Assets**")
        st.dataframe(assets_df, use_container_width=True, hide_index=True)
    else:
        st.info("No change assets defined yet")

with tab4:
    st.markdown("### Impact Explorer")
    
    if 'drill_through_filter' in st.session_state:
        drill_filter = st.session_state['drill_through_filter']
        
        if 'status' in drill_filter:
            st.info(f"🔍 Filtered by Status: **{drill_filter['status']}**")
            explorer_impacts = [i for i in filtered_impacts if i.status == drill_filter['status']]
        elif 'stakeholder_group' in drill_filter:
            st.info(f"🔍 Filtered by Stakeholder Group: **{drill_filter['stakeholder_group']}**")
            sg = next((s for s in stakeholder_groups if s.name == drill_filter['stakeholder_group']), None)
            if sg:
                explorer_impacts = [i for i in filtered_impacts if sg.id in i.stakeholder_group_ids]
            else:
                explorer_impacts = filtered_impacts
        elif 'business_process' in drill_filter:
            st.info(f"🔍 Filtered by Business Process: **{drill_filter['business_process']}**")
            bp = next((b for b in business_processes if b.name == drill_filter['business_process']), None)
            if bp:
                explorer_impacts = [i for i in filtered_impacts if bp.id in i.business_process_ids]
            else:
                explorer_impacts = filtered_impacts
        elif 'system' in drill_filter:
            st.info(f"🔍 Filtered by System: **{drill_filter['system']}**")
            sys = next((s for s in systems if s.name == drill_filter['system']), None)
            if sys:
                explorer_impacts = [i for i in filtered_impacts if sys.id in i.system_ids]
            else:
                explorer_impacts = filtered_impacts
        elif 'policy' in drill_filter:
            st.info(f"🔍 Filtered by Policy: **{drill_filter['policy']}**")
            pol = next((p for p in policies if p.name == drill_filter['policy']), None)
            if pol:
                explorer_impacts = [i for i in filtered_impacts if pol.id in i.policy_ids]
            else:
                explorer_impacts = filtered_impacts
        elif 'no_coverage' in drill_filter:
            st.info("🔍 Filtered by: **Impacts Without Coverage**")
            explorer_impacts = []
            for impact in filtered_impacts:
                assets = repo.list_change_assets(impact.id)
                if len(assets) == 0:
                    explorer_impacts.append(impact)
        elif 'no_evidence' in drill_filter:
            st.info("🔍 Filtered by: **Impacts Without Source Evidence**")
            explorer_impacts = []
            for impact in filtered_impacts:
                evidences = repo.list_source_evidences(impact.id)
                if len(evidences) == 0:
                    explorer_impacts.append(impact)
        else:
            explorer_impacts = filtered_impacts
        
        if st.button("🔄 Clear Drill-Through Filter"):
            del st.session_state['drill_through_filter']
            st.rerun()
    else:
        explorer_impacts = filtered_impacts
    
    st.markdown(f"**Showing {len(explorer_impacts)} impacts**")
    
    if explorer_impacts:
        for impact in explorer_impacts:
            with st.expander(f"**{impact.impact_number}** - {impact.title or impact.description[:60]}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    if impact.title:
                        st.markdown(f"**Title:** {impact.title}")
                    st.markdown(f"**Description:** {impact.description}")
                    if impact.area_of_change:
                        st.caption(f"Area: {impact.area_of_change}")
                
                with col2:
                    st.caption(f"Status: {impact.status}")
                    if impact.severity:
                        st.caption(f"Severity: {impact.severity}")
                    
                    assets = repo.list_change_assets(impact.id)
                    st.caption(f"Coverage: {len(assets)} assets")
                
                if len(impact.stakeholder_group_ids) > 0 or len(impact.business_process_ids) > 0 or len(impact.system_ids) > 0:
                    st.markdown("**Relationships:**")
                    
                    if impact.stakeholder_group_ids:
                        sg_names = [sg.name for sg in stakeholder_groups if sg.id in impact.stakeholder_group_ids]
                        st.write(f"- Stakeholders: {', '.join(sg_names)}")
                    
                    if impact.business_process_ids:
                        bp_names = [bp.name for bp in business_processes if bp.id in impact.business_process_ids]
                        st.write(f"- Processes: {', '.join(bp_names)}")
                    
                    if impact.system_ids:
                        sys_names = [sys.name for sys in systems if sys.id in impact.system_ids]
                        st.write(f"- Systems: {', '.join(sys_names)}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✏️ Enrich", key=f"enrich_{impact.id}"):
                        st.session_state['edit_impact_id'] = impact.id
                        st.switch_page("pages/07_Enrichment_Workspace.py")
                with col2:
                    if st.button(f"📊 Details", key=f"details_{impact.id}"):
                        st.session_state['edit_impact_id'] = impact.id
                        st.switch_page("pages/04_Enrich.py")
    else:
        st.info("No impacts match the current filters")

with tab5:
    st.markdown("### Registry Health")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total = len(filtered_impacts)
        st.metric("Total Impacts", total)
    
    with col2:
        with_title = sum(1 for i in filtered_impacts if i.title and i.title.strip())
        title_pct = (with_title / total * 100) if total > 0 else 0
        st.metric("With Title", f"{title_pct:.0f}%")
    
    with col3:
        with_sg = sum(1 for i in filtered_impacts if len(i.stakeholder_group_ids) > 0)
        sg_pct = (with_sg / total * 100) if total > 0 else 0
        st.metric("With Stakeholders", f"{sg_pct:.0f}%")
    
    with col4:
        with_coverage = 0
        for impact in filtered_impacts:
            assets = repo.list_change_assets(impact.id)
            if len(assets) > 0:
                with_coverage += 1
        coverage_pct = (with_coverage / total * 100) if total > 0 else 0
        st.metric("With Coverage", f"{coverage_pct:.0f}%")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Completeness Metrics")
        
        completeness_data = []
        
        completeness_data.append({
            'Metric': 'Title',
            'Count': with_title,
            'Percentage': f"{title_pct:.0f}%"
        })
        
        completeness_data.append({
            'Metric': 'Stakeholder Groups',
            'Count': with_sg,
            'Percentage': f"{sg_pct:.0f}%"
        })
        
        with_ou = sum(1 for i in filtered_impacts if len(i.organization_unit_ids) > 0)
        ou_pct = (with_ou / total * 100) if total > 0 else 0
        completeness_data.append({
            'Metric': 'Organization Units',
            'Count': with_ou,
            'Percentage': f"{ou_pct:.0f}%"
        })
        
        with_bp = sum(1 for i in filtered_impacts if len(i.business_process_ids) > 0)
        bp_pct = (with_bp / total * 100) if total > 0 else 0
        completeness_data.append({
            'Metric': 'Business Processes',
            'Count': with_bp,
            'Percentage': f"{bp_pct:.0f}%"
        })
        
        with_sys = sum(1 for i in filtered_impacts if len(i.system_ids) > 0)
        sys_pct = (with_sys / total * 100) if total > 0 else 0
        completeness_data.append({
            'Metric': 'Systems',
            'Count': with_sys,
            'Percentage': f"{sys_pct:.0f}%"
        })
        
        completeness_data.append({
            'Metric': 'Change Assets',
            'Count': with_coverage,
            'Percentage': f"{coverage_pct:.0f}%"
        })
        
        with_evidence = 0
        for impact in filtered_impacts:
            evidences = repo.list_source_evidences(impact.id)
            if len(evidences) > 0:
                with_evidence += 1
        evidence_pct = (with_evidence / total * 100) if total > 0 else 0
        completeness_data.append({
            'Metric': 'Source Evidence',
            'Count': with_evidence,
            'Percentage': f"{evidence_pct:.0f}%"
        })
        
        completeness_df = pd.DataFrame(completeness_data)
        st.dataframe(completeness_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("#### 🏥 Health Score")
        
        health_score = (
            title_pct * 0.15 +
            sg_pct * 0.20 +
            bp_pct * 0.15 +
            sys_pct * 0.15 +
            coverage_pct * 0.25 +
            evidence_pct * 0.10
        )
        
        if health_score >= 80:
            health_color = "🟢"
            health_status = "Excellent"
        elif health_score >= 60:
            health_color = "🟡"
            health_status = "Good"
        elif health_score >= 40:
            health_color = "🟠"
            health_status = "Fair"
        else:
            health_color = "🔴"
            health_status = "Needs Improvement"
        
        st.markdown(f"### {health_color} {health_score:.0f}%")
        st.markdown(f"**Status:** {health_status}")
        
        st.markdown("---")
        
        st.markdown("**Recommendations:**")
        
        if title_pct < 80:
            st.write("- ⚠️ Add titles to more impacts")
        if sg_pct < 70:
            st.write("- ⚠️ Link more impacts to stakeholder groups")
        if coverage_pct < 60:
            st.write("- ⚠️ Define change assets for more impacts")
        if evidence_pct < 70:
            st.write("- ⚠️ Document source evidence")
        
        if health_score >= 80:
            st.success("✅ Registry is in excellent health!")
    
    st.markdown("---")
    
    st.markdown("#### 📊 Registry Gaps")
    
    gap_col1, gap_col2 = st.columns(2)
    
    with gap_col1:
        st.markdown("**Impacts Missing Key Elements**")
        
        no_title = [i for i in filtered_impacts if not i.title or not i.title.strip()]
        st.write(f"- No Title: **{len(no_title)}**")
        
        no_sg = [i for i in filtered_impacts if len(i.stakeholder_group_ids) == 0]
        st.write(f"- No Stakeholder Groups: **{len(no_sg)}**")
        
        no_coverage_list = []
        for impact in filtered_impacts:
            assets = repo.list_change_assets(impact.id)
            if len(assets) == 0:
                no_coverage_list.append(impact)
        st.write(f"- No Coverage: **{len(no_coverage_list)}**")
        
        no_evidence_list = []
        for impact in filtered_impacts:
            evidences = repo.list_source_evidences(impact.id)
            if len(evidences) == 0:
                no_evidence_list.append(impact)
        st.write(f"- No Source Evidence: **{len(no_evidence_list)}**")
    
    with gap_col2:
        st.markdown("**Concentration of Change**")
        
        if stakeholder_groups:
            sg_counts = [(sg.name, sum(1 for i in filtered_impacts if sg.id in i.stakeholder_group_ids)) 
                        for sg in stakeholder_groups]
            sg_counts.sort(key=lambda x: x[1], reverse=True)
            
            if sg_counts and sg_counts[0][1] > 0:
                st.write(f"- Top Stakeholder: **{sg_counts[0][0]}** ({sg_counts[0][1]} impacts)")
        
        if business_processes:
            bp_counts = [(bp.name, sum(1 for i in filtered_impacts if bp.id in i.business_process_ids)) 
                        for bp in business_processes]
            bp_counts.sort(key=lambda x: x[1], reverse=True)
            
            if bp_counts and bp_counts[0][1] > 0:
                st.write(f"- Top Process: **{bp_counts[0][0]}** ({bp_counts[0][1]} impacts)")
        
        if systems:
            sys_counts = [(sys.name, sum(1 for i in filtered_impacts if sys.id in i.system_ids)) 
                         for sys in systems]
            sys_counts.sort(key=lambda x: x[1], reverse=True)
            
            if sys_counts and sys_counts[0][1] > 0:
                st.write(f"- Top System: **{sys_counts[0][0]}** ({sys_counts[0][1]} impacts)")

st.markdown("---")
st.markdown("### 💡 Analysis Tips")
st.markdown("""
- **Use filters** - Narrow analysis to specific areas of interest
- **Click counts** - Drill through to underlying impact records
- **Search** - Find specific impacts or assets quickly
- **Explore relationships** - Understand how change connects across the organization
- **Monitor health** - Track registry quality over time
""")
