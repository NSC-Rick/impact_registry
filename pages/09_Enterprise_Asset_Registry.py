import streamlit as st
from datetime import datetime
from database.schema import init_db, get_session, get_engine
from services.repository import Repository

st.set_page_config(page_title="Enterprise Asset Registry", page_icon="🏢", layout="wide")

engine = init_db()
session = get_session(engine)
repo = Repository(session)

st.title("🏢 Enterprise Asset Registry")
st.markdown("### Centralized Registry of Reusable Organizational Assets")

if 'current_project_id' not in st.session_state:
    st.warning("⚠️ Please select or create a project in the Setup page first")
    st.stop()

project_id = st.session_state['current_project_id']
project = repo.get_project(project_id)

st.info(f"📁 **Project:** {project.name}")

st.sidebar.markdown("### 🔍 Search & Filter")

search_query = st.sidebar.text_input(
    "🔎 Search Assets",
    placeholder="Asset name...",
    help="Search across all enterprise assets"
)

filter_type = st.sidebar.multiselect(
    "Asset Type",
    ["Stakeholder Group", "Organization Unit", "Business Process", "System", "Policy"],
    default=["Stakeholder Group", "Organization Unit", "Business Process", "System", "Policy"]
)

filter_status = st.sidebar.multiselect(
    "Status",
    ["Active", "Inactive", "Retired"],
    default=["Active"]
)

if st.sidebar.button("🔄 Clear Filters"):
    st.rerun()

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Overview",
    "👥 Stakeholder Groups",
    "🏛️ Organization Units",
    "🔄 Business Processes",
    "💻 Systems",
    "📋 Policies"
])

def get_related_impact_count(asset_type, asset_id):
    impacts = repo.list_impacts(project_id)
    count = 0
    
    if asset_type == "Stakeholder Group":
        count = sum(1 for i in impacts if asset_id in i.stakeholder_group_ids)
    elif asset_type == "Organization Unit":
        count = sum(1 for i in impacts if asset_id in i.organization_unit_ids)
    elif asset_type == "Business Process":
        count = sum(1 for i in impacts if asset_id in i.business_process_ids)
    elif asset_type == "System":
        count = sum(1 for i in impacts if asset_id in i.system_ids)
    elif asset_type == "Policy":
        count = sum(1 for i in impacts if asset_id in i.policy_ids)
    
    return count

def filter_assets(assets, asset_type_name):
    filtered = assets
    
    if search_query:
        search_lower = search_query.lower()
        filtered = [a for a in filtered if search_lower in a.name.lower()]
    
    if asset_type_name not in filter_type:
        filtered = []
    
    if hasattr(filtered[0] if filtered else type('obj', (), {'status': None}), 'status'):
        filtered = [a for a in filtered if (a.status or 'Active') in filter_status]
    
    return filtered

with tab1:
    st.markdown("### Enterprise Asset Overview")
    
    stakeholder_groups = repo.list_stakeholder_groups(project_id)
    organization_units = repo.list_organization_units(project_id)
    business_processes = repo.list_business_processes(project_id)
    systems = repo.list_systems(project_id)
    policies = repo.list_policies(project_id)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Stakeholder Groups", len(stakeholder_groups))
    with col2:
        st.metric("Organization Units", len(organization_units))
    with col3:
        st.metric("Business Processes", len(business_processes))
    with col4:
        st.metric("Systems", len(systems))
    with col5:
        st.metric("Policies", len(policies))
    
    total_assets = len(stakeholder_groups) + len(organization_units) + len(business_processes) + len(systems) + len(policies)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Assets by Type")
        
        asset_counts = {
            'Stakeholder Groups': len(stakeholder_groups),
            'Organization Units': len(organization_units),
            'Business Processes': len(business_processes),
            'Systems': len(systems),
            'Policies': len(policies)
        }
        
        import pandas as pd
        counts_df = pd.DataFrame([
            {'Type': k, 'Count': v}
            for k, v in asset_counts.items()
        ])
        
        st.bar_chart(counts_df.set_index('Type'))
        st.dataframe(counts_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("#### 🔗 Most Referenced Assets")
        
        all_assets = []
        
        for sg in stakeholder_groups:
            count = get_related_impact_count("Stakeholder Group", sg.id)
            if count > 0:
                all_assets.append({
                    'Asset': sg.name,
                    'Type': 'Stakeholder Group',
                    'Impact Count': count
                })
        
        for ou in organization_units:
            count = get_related_impact_count("Organization Unit", ou.id)
            if count > 0:
                all_assets.append({
                    'Asset': ou.name,
                    'Type': 'Organization Unit',
                    'Impact Count': count
                })
        
        for bp in business_processes:
            count = get_related_impact_count("Business Process", bp.id)
            if count > 0:
                all_assets.append({
                    'Asset': bp.name,
                    'Type': 'Business Process',
                    'Impact Count': count
                })
        
        for sys in systems:
            count = get_related_impact_count("System", sys.id)
            if count > 0:
                all_assets.append({
                    'Asset': sys.name,
                    'Type': 'System',
                    'Impact Count': count
                })
        
        for pol in policies:
            count = get_related_impact_count("Policy", pol.id)
            if count > 0:
                all_assets.append({
                    'Asset': pol.name,
                    'Type': 'Policy',
                    'Impact Count': count
                })
        
        if all_assets:
            assets_df = pd.DataFrame(all_assets)
            assets_df = assets_df.sort_values('Impact Count', ascending=False).head(10)
            
            st.dataframe(assets_df, use_container_width=True, hide_index=True)
        else:
            st.info("No assets linked to impacts yet")
    
    st.markdown("---")
    
    st.markdown("### 💡 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Create Stakeholder Group", use_container_width=True):
            st.session_state['create_asset_type'] = 'Stakeholder Group'
            st.rerun()
    
    with col2:
        if st.button("➕ Create Business Process", use_container_width=True):
            st.session_state['create_asset_type'] = 'Business Process'
            st.rerun()
    
    with col3:
        if st.button("➕ Create System", use_container_width=True):
            st.session_state['create_asset_type'] = 'System'
            st.rerun()

with tab2:
    st.markdown("### 👥 Stakeholder Groups")
    
    stakeholder_groups = repo.list_stakeholder_groups(project_id)
    filtered_sgs = filter_assets(stakeholder_groups, "Stakeholder Group")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"**Showing {len(filtered_sgs)} of {len(stakeholder_groups)} stakeholder groups**")
    
    with col2:
        if st.button("➕ New Stakeholder Group", use_container_width=True):
            st.session_state['show_sg_form'] = True
    
    if st.session_state.get('show_sg_form', False):
        st.markdown("---")
        st.markdown("#### Create New Stakeholder Group")
        
        with st.form("new_sg_form"):
            name = st.text_input("Name*", placeholder="e.g., Finance Team")
            description = st.text_area("Description", placeholder="Brief description of this stakeholder group")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                size = st.number_input("Size", min_value=0, value=0, help="Approximate number of people")
            with col2:
                influence = st.selectbox("Influence", ["", "Low", "Medium", "High"])
            with col3:
                status = st.selectbox("Status", ["Active", "Inactive", "Retired"], index=0)
            
            notes = st.text_area("Notes", placeholder="Additional information...")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("✅ Create", type="primary", use_container_width=True):
                    if name:
                        sg = repo.create_stakeholder_group(project_id, name, description, size, influence)
                        
                        session.query(repo.session.query(repo.session.bind.execute(
                            f"UPDATE stakeholder_groups SET status = '{status}', notes = '{notes}' WHERE id = {sg.id}"
                        )))
                        session.commit()
                        
                        st.success(f"✅ Created '{name}'")
                        st.session_state['show_sg_form'] = False
                        st.rerun()
                    else:
                        st.error("Name is required")
            
            with col2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state['show_sg_form'] = False
                    st.rerun()
    
    st.markdown("---")
    
    if filtered_sgs:
        for sg in filtered_sgs:
            impact_count = get_related_impact_count("Stakeholder Group", sg.id)
            
            with st.expander(f"**{sg.name}** ({impact_count} impacts)", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    if sg.description:
                        st.markdown(f"**Description:** {sg.description}")
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.caption(f"Size: {sg.size or 'Not set'}")
                    with col_b:
                        st.caption(f"Influence: {sg.influence or 'Not set'}")
                    with col_c:
                        status_emoji = {"Active": "🟢", "Inactive": "🟡", "Retired": "🔴"}
                        st.caption(f"{status_emoji.get(sg.status or 'Active', '⚪')} {sg.status or 'Active'}")
                    
                    if hasattr(sg, 'notes') and sg.notes:
                        st.markdown(f"**Notes:** {sg.notes}")
                
                with col2:
                    st.metric("Related Impacts", impact_count)
                    
                    if impact_count > 0:
                        if st.button(f"🔍 View Impacts", key=f"view_sg_{sg.id}"):
                            st.session_state['drill_through_filter'] = {'stakeholder_group': sg.name}
                            st.switch_page("pages/08_Analyze_Workspace.py")
    else:
        st.info("No stakeholder groups match the current filters")

with tab3:
    st.markdown("### 🏛️ Organization Units")
    
    organization_units = repo.list_organization_units(project_id)
    filtered_ous = filter_assets(organization_units, "Organization Unit")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"**Showing {len(filtered_ous)} of {len(organization_units)} organization units**")
    
    with col2:
        if st.button("➕ New Organization Unit", use_container_width=True):
            st.session_state['show_ou_form'] = True
    
    if st.session_state.get('show_ou_form', False):
        st.markdown("---")
        st.markdown("#### Create New Organization Unit")
        
        with st.form("new_ou_form"):
            name = st.text_input("Name*", placeholder="e.g., North America Sales")
            description = st.text_area("Description")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                parent_unit = st.text_input("Parent Unit")
            with col2:
                head_of_unit = st.text_input("Head of Unit")
            with col3:
                status = st.selectbox("Status", ["Active", "Inactive", "Retired"], index=0)
            
            notes = st.text_area("Notes")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("✅ Create", type="primary", use_container_width=True):
                    if name:
                        repo.create_organization_unit(project_id, name, description, parent_unit, head_of_unit)
                        st.success(f"✅ Created '{name}'")
                        st.session_state['show_ou_form'] = False
                        st.rerun()
            
            with col2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state['show_ou_form'] = False
                    st.rerun()
    
    st.markdown("---")
    
    if filtered_ous:
        for ou in filtered_ous:
            impact_count = get_related_impact_count("Organization Unit", ou.id)
            
            with st.expander(f"**{ou.name}** ({impact_count} impacts)", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    if ou.description:
                        st.markdown(f"**Description:** {ou.description}")
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if ou.parent_unit:
                            st.caption(f"Parent: {ou.parent_unit}")
                    with col_b:
                        if ou.head_of_unit:
                            st.caption(f"Head: {ou.head_of_unit}")
                    with col_c:
                        status_emoji = {"Active": "🟢", "Inactive": "🟡", "Retired": "🔴"}
                        st.caption(f"{status_emoji.get(ou.status or 'Active', '⚪')} {ou.status or 'Active'}")
                
                with col2:
                    st.metric("Related Impacts", impact_count)
                    
                    if impact_count > 0:
                        if st.button(f"🔍 View Impacts", key=f"view_ou_{ou.id}"):
                            st.session_state['drill_through_filter'] = {'organization_unit': ou.name}
                            st.switch_page("pages/08_Analyze_Workspace.py")
    else:
        st.info("No organization units match the current filters")

with tab4:
    st.markdown("### 🔄 Business Processes")
    
    business_processes = repo.list_business_processes(project_id)
    filtered_bps = filter_assets(business_processes, "Business Process")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"**Showing {len(filtered_bps)} of {len(business_processes)} business processes**")
    
    with col2:
        if st.button("➕ New Business Process", use_container_width=True):
            st.session_state['show_bp_form'] = True
    
    if st.session_state.get('show_bp_form', False):
        st.markdown("---")
        st.markdown("#### Create New Business Process")
        
        with st.form("new_bp_form"):
            name = st.text_input("Name*", placeholder="e.g., Order to Cash")
            description = st.text_area("Description")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                process_owner = st.text_input("Process Owner")
            with col2:
                criticality = st.selectbox("Criticality", ["", "Low", "Medium", "High", "Critical"])
            with col3:
                status = st.selectbox("Status", ["Active", "Inactive", "Retired"], index=0)
            
            notes = st.text_area("Notes")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("✅ Create", type="primary", use_container_width=True):
                    if name:
                        repo.create_business_process(project_id, name, description, process_owner, criticality)
                        st.success(f"✅ Created '{name}'")
                        st.session_state['show_bp_form'] = False
                        st.rerun()
            
            with col2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state['show_bp_form'] = False
                    st.rerun()
    
    st.markdown("---")
    
    if filtered_bps:
        for bp in filtered_bps:
            impact_count = get_related_impact_count("Business Process", bp.id)
            
            with st.expander(f"**{bp.name}** ({impact_count} impacts)", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    if bp.description:
                        st.markdown(f"**Description:** {bp.description}")
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if bp.process_owner:
                            st.caption(f"Owner: {bp.process_owner}")
                    with col_b:
                        st.caption(f"Criticality: {bp.criticality or 'Not set'}")
                    with col_c:
                        status_emoji = {"Active": "🟢", "Inactive": "🟡", "Retired": "🔴"}
                        st.caption(f"{status_emoji.get(bp.status or 'Active', '⚪')} {bp.status or 'Active'}")
                
                with col2:
                    st.metric("Related Impacts", impact_count)
                    
                    if impact_count > 0:
                        if st.button(f"🔍 View Impacts", key=f"view_bp_{bp.id}"):
                            st.session_state['drill_through_filter'] = {'business_process': bp.name}
                            st.switch_page("pages/08_Analyze_Workspace.py")
    else:
        st.info("No business processes match the current filters")

with tab5:
    st.markdown("### 💻 Systems")
    
    systems = repo.list_systems(project_id)
    filtered_systems = filter_assets(systems, "System")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"**Showing {len(filtered_systems)} of {len(systems)} systems**")
    
    with col2:
        if st.button("➕ New System", use_container_width=True):
            st.session_state['show_sys_form'] = True
    
    if st.session_state.get('show_sys_form', False):
        st.markdown("---")
        st.markdown("#### Create New System")
        
        with st.form("new_sys_form"):
            name = st.text_input("Name*", placeholder="e.g., SAP ERP")
            description = st.text_area("Description")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                system_owner = st.text_input("System Owner")
            with col2:
                vendor = st.text_input("Vendor")
            with col3:
                criticality = st.selectbox("Criticality", ["", "Low", "Medium", "High", "Critical"])
            with col4:
                status = st.selectbox("Status", ["Active", "Inactive", "Retired"], index=0)
            
            notes = st.text_area("Notes")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("✅ Create", type="primary", use_container_width=True):
                    if name:
                        repo.create_system(project_id, name, description, system_owner, vendor, criticality)
                        st.success(f"✅ Created '{name}'")
                        st.session_state['show_sys_form'] = False
                        st.rerun()
            
            with col2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state['show_sys_form'] = False
                    st.rerun()
    
    st.markdown("---")
    
    if filtered_systems:
        for sys in filtered_systems:
            impact_count = get_related_impact_count("System", sys.id)
            
            with st.expander(f"**{sys.name}** ({impact_count} impacts)", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    if sys.description:
                        st.markdown(f"**Description:** {sys.description}")
                    
                    col_a, col_b, col_c, col_d = st.columns(4)
                    with col_a:
                        if sys.system_owner:
                            st.caption(f"Owner: {sys.system_owner}")
                    with col_b:
                        if sys.vendor:
                            st.caption(f"Vendor: {sys.vendor}")
                    with col_c:
                        st.caption(f"Criticality: {sys.criticality or 'Not set'}")
                    with col_d:
                        status_emoji = {"Active": "🟢", "Inactive": "🟡", "Retired": "🔴"}
                        st.caption(f"{status_emoji.get(sys.status or 'Active', '⚪')} {sys.status or 'Active'}")
                
                with col2:
                    st.metric("Related Impacts", impact_count)
                    
                    if impact_count > 0:
                        if st.button(f"🔍 View Impacts", key=f"view_sys_{sys.id}"):
                            st.session_state['drill_through_filter'] = {'system': sys.name}
                            st.switch_page("pages/08_Analyze_Workspace.py")
    else:
        st.info("No systems match the current filters")

with tab6:
    st.markdown("### 📋 Policies")
    
    policies = repo.list_policies(project_id)
    filtered_policies = filter_assets(policies, "Policy")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"**Showing {len(filtered_policies)} of {len(policies)} policies**")
    
    with col2:
        if st.button("➕ New Policy", use_container_width=True):
            st.session_state['show_pol_form'] = True
    
    if st.session_state.get('show_pol_form', False):
        st.markdown("---")
        st.markdown("#### Create New Policy")
        
        with st.form("new_pol_form"):
            name = st.text_input("Name*", placeholder="e.g., Data Privacy Policy")
            description = st.text_area("Description")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                policy_owner = st.text_input("Policy Owner")
            with col2:
                effective_date = st.date_input("Effective Date")
            with col3:
                status = st.selectbox("Status", ["Active", "Inactive", "Retired"], index=0)
            
            notes = st.text_area("Notes")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("✅ Create", type="primary", use_container_width=True):
                    if name:
                        repo.create_policy(project_id, name, description, policy_owner, 
                                         datetime.combine(effective_date, datetime.min.time()))
                        st.success(f"✅ Created '{name}'")
                        st.session_state['show_pol_form'] = False
                        st.rerun()
            
            with col2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state['show_pol_form'] = False
                    st.rerun()
    
    st.markdown("---")
    
    if filtered_policies:
        for pol in filtered_policies:
            impact_count = get_related_impact_count("Policy", pol.id)
            
            with st.expander(f"**{pol.name}** ({impact_count} impacts)", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    if pol.description:
                        st.markdown(f"**Description:** {pol.description}")
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if pol.policy_owner:
                            st.caption(f"Owner: {pol.policy_owner}")
                    with col_b:
                        if pol.effective_date:
                            st.caption(f"Effective: {pol.effective_date.strftime('%Y-%m-%d')}")
                    with col_c:
                        status_emoji = {"Active": "🟢", "Inactive": "🟡", "Retired": "🔴"}
                        st.caption(f"{status_emoji.get(pol.status or 'Active', '⚪')} {pol.status or 'Active'}")
                
                with col2:
                    st.metric("Related Impacts", impact_count)
                    
                    if impact_count > 0:
                        if st.button(f"🔍 View Impacts", key=f"view_pol_{pol.id}"):
                            st.session_state['drill_through_filter'] = {'policy': pol.name}
                            st.switch_page("pages/08_Analyze_Workspace.py")
    else:
        st.info("No policies match the current filters")

st.markdown("---")
st.markdown("### 💡 Enterprise Asset Best Practices")
st.markdown("""
- **Create assets early** - Establish enterprise assets during project setup
- **Reuse, don't recreate** - Search before creating new assets
- **Keep it simple** - Focus on name and description, optional attributes as needed
- **Status management** - Mark assets as Inactive or Retired rather than deleting
- **View related impacts** - Understand which impacts reference each asset
- **Maintain traceability** - Enterprise assets enable organizational intelligence
""")
