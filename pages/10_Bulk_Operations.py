import streamlit as st
from datetime import datetime
from database.schema import init_db, get_session, get_engine
from services.repository import Repository
from models.impact import ImpactDTO

st.set_page_config(page_title="Bulk Operations", page_icon="⚙️", layout="wide")

engine = init_db()
session = get_session(engine)
repo = Repository(session)

st.title("⚙️ Bulk Operations Workspace")
st.markdown("### Efficient Multi-Impact Operations")

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

if 'selected_impact_ids' not in st.session_state:
    st.session_state['selected_impact_ids'] = []

st.sidebar.markdown("### 🔍 Filter Impacts")

filter_status = st.sidebar.multiselect(
    "Status",
    ["Draft", "Under Review", "Approved", "Superseded"],
    default=["Draft", "Approved"]
)

stakeholder_groups = repo.list_stakeholder_groups(project_id)
organization_units = repo.list_organization_units(project_id)
business_processes = repo.list_business_processes(project_id)
systems = repo.list_systems(project_id)
policies = repo.list_policies(project_id)

filter_sg = st.sidebar.multiselect(
    "Stakeholder Group",
    [sg.name for sg in stakeholder_groups]
)

filter_bp = st.sidebar.multiselect(
    "Business Process",
    [bp.name for bp in business_processes]
)

search_query = st.sidebar.text_input(
    "🔎 Search",
    placeholder="Impact ID, title, description..."
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

if search_query:
    search_lower = search_query.lower()
    filtered_impacts = [
        i for i in filtered_impacts
        if (search_lower in i.impact_number.lower() if i.impact_number else False) or
           (search_lower in i.title.lower() if i.title else False) or
           (search_lower in i.description.lower() if i.description else False)
    ]

st.sidebar.markdown(f"**Filtered:** {len(filtered_impacts)} of {len(impacts)}")

if st.sidebar.button("🔄 Clear Filters"):
    st.rerun()

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.markdown(f"### Select Impacts ({len(st.session_state['selected_impact_ids'])} selected)")

with col2:
    if st.button("✅ Select All Filtered", use_container_width=True):
        st.session_state['selected_impact_ids'] = [i.id for i in filtered_impacts]
        st.rerun()

with col3:
    if st.button("❌ Clear Selection", use_container_width=True):
        st.session_state['selected_impact_ids'] = []
        st.rerun()

st.markdown("---")

tab1, tab2 = st.tabs(["📋 Select Impacts", "⚙️ Bulk Operations"])

with tab1:
    st.markdown("### Impact Selection")
    
    if filtered_impacts:
        for impact in filtered_impacts:
            is_selected = impact.id in st.session_state['selected_impact_ids']
            
            col1, col2 = st.columns([1, 20])
            
            with col1:
                if st.checkbox("", value=is_selected, key=f"select_{impact.id}", label_visibility="collapsed"):
                    if impact.id not in st.session_state['selected_impact_ids']:
                        st.session_state['selected_impact_ids'].append(impact.id)
                else:
                    if impact.id in st.session_state['selected_impact_ids']:
                        st.session_state['selected_impact_ids'].remove(impact.id)
            
            with col2:
                with st.container():
                    col_a, col_b, col_c = st.columns([3, 1, 1])
                    
                    with col_a:
                        st.markdown(f"**{impact.impact_number}** - {impact.title or impact.description[:60]}")
                    
                    with col_b:
                        st.caption(f"Status: {impact.status}")
                    
                    with col_c:
                        change_assets = repo.list_change_assets(impact.id)
                        st.caption(f"Assets: {len(change_assets)}")
                
                st.markdown("---")
    else:
        st.info("No impacts match the current filters")

with tab2:
    st.markdown("### Bulk Operations")
    
    selected_count = len(st.session_state['selected_impact_ids'])
    
    if selected_count == 0:
        st.warning("⚠️ No impacts selected. Please select impacts from the 'Select Impacts' tab.")
    else:
        st.success(f"✅ **{selected_count} impacts selected** for bulk operations")
        
        operation_tab1, operation_tab2, operation_tab3, operation_tab4 = st.tabs([
            "📊 Status Change",
            "🏢 Enterprise Assets",
            "📦 Change Assets",
            "📝 Notes"
        ])
        
        with operation_tab1:
            st.markdown("#### Bulk Status Change")
            st.markdown(f"Apply status change to **{selected_count} selected impacts**")
            
            with st.form("bulk_status_form"):
                new_status = st.selectbox(
                    "New Status",
                    ["Draft", "Under Review", "Approved", "Superseded"]
                )
                
                st.markdown("---")
                st.markdown("**Preview:**")
                st.info(f"Set Status = **{new_status}** for {selected_count} impacts")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.form_submit_button("✅ Apply Status Change", type="primary", use_container_width=True):
                        for impact_id in st.session_state['selected_impact_ids']:
                            impact = repo.get_impact(impact_id)
                            if impact:
                                impact.status = new_status
                                repo.update_impact(impact)
                        
                        st.success(f"✅ Updated {selected_count} impacts to {new_status}")
                        st.session_state['selected_impact_ids'] = []
                        st.rerun()
                
                with col2:
                    if st.form_submit_button("Cancel", use_container_width=True):
                        pass
        
        with operation_tab2:
            st.markdown("#### Bulk Enterprise Asset Assignment")
            st.markdown(f"Assign enterprise assets to **{selected_count} selected impacts**")
            
            asset_operation = st.radio(
                "Operation Type",
                ["Assign (Add)", "Replace (Overwrite)", "Remove"],
                horizontal=True
            )
            
            with st.form("bulk_enterprise_assets_form"):
                asset_type = st.selectbox(
                    "Asset Type",
                    ["Stakeholder Groups", "Organization Units", "Business Processes", "Systems", "Policies"]
                )
                
                if asset_type == "Stakeholder Groups":
                    if stakeholder_groups:
                        sg_options = {sg.name: sg.id for sg in stakeholder_groups}
                        selected_assets = st.multiselect(
                            "Select Stakeholder Groups",
                            options=list(sg_options.keys())
                        )
                    else:
                        selected_assets = []
                        st.info("No stakeholder groups defined")
                
                elif asset_type == "Organization Units":
                    if organization_units:
                        ou_options = {ou.name: ou.id for ou in organization_units}
                        selected_assets = st.multiselect(
                            "Select Organization Units",
                            options=list(ou_options.keys())
                        )
                    else:
                        selected_assets = []
                        st.info("No organization units defined")
                
                elif asset_type == "Business Processes":
                    if business_processes:
                        bp_options = {bp.name: bp.id for bp in business_processes}
                        selected_assets = st.multiselect(
                            "Select Business Processes",
                            options=list(bp_options.keys())
                        )
                    else:
                        selected_assets = []
                        st.info("No business processes defined")
                
                elif asset_type == "Systems":
                    if systems:
                        sys_options = {sys.name: sys.id for sys in systems}
                        selected_assets = st.multiselect(
                            "Select Systems",
                            options=list(sys_options.keys())
                        )
                    else:
                        selected_assets = []
                        st.info("No systems defined")
                
                elif asset_type == "Policies":
                    if policies:
                        pol_options = {pol.name: pol.id for pol in policies}
                        selected_assets = st.multiselect(
                            "Select Policies",
                            options=list(pol_options.keys())
                        )
                    else:
                        selected_assets = []
                        st.info("No policies defined")
                
                st.markdown("---")
                st.markdown("**Preview:**")
                
                if selected_assets:
                    if asset_operation == "Assign (Add)":
                        st.info(f"**Assign** {asset_type}: {', '.join(selected_assets)} to {selected_count} impacts")
                    elif asset_operation == "Replace (Overwrite)":
                        st.warning(f"**Replace** {asset_type} with: {', '.join(selected_assets)} for {selected_count} impacts")
                    else:
                        st.warning(f"**Remove** {asset_type}: {', '.join(selected_assets)} from {selected_count} impacts")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.form_submit_button("✅ Apply Changes", type="primary", use_container_width=True):
                        if selected_assets:
                            for impact_id in st.session_state['selected_impact_ids']:
                                impact = repo.get_impact(impact_id)
                                if impact:
                                    if asset_type == "Stakeholder Groups":
                                        asset_ids = [sg_options[name] for name in selected_assets]
                                        if asset_operation == "Assign (Add)":
                                            impact.stakeholder_group_ids = list(set(impact.stakeholder_group_ids + asset_ids))
                                        elif asset_operation == "Replace (Overwrite)":
                                            impact.stakeholder_group_ids = asset_ids
                                        else:
                                            impact.stakeholder_group_ids = [id for id in impact.stakeholder_group_ids if id not in asset_ids]
                                    
                                    elif asset_type == "Organization Units":
                                        asset_ids = [ou_options[name] for name in selected_assets]
                                        if asset_operation == "Assign (Add)":
                                            impact.organization_unit_ids = list(set(impact.organization_unit_ids + asset_ids))
                                        elif asset_operation == "Replace (Overwrite)":
                                            impact.organization_unit_ids = asset_ids
                                        else:
                                            impact.organization_unit_ids = [id for id in impact.organization_unit_ids if id not in asset_ids]
                                    
                                    elif asset_type == "Business Processes":
                                        asset_ids = [bp_options[name] for name in selected_assets]
                                        if asset_operation == "Assign (Add)":
                                            impact.business_process_ids = list(set(impact.business_process_ids + asset_ids))
                                        elif asset_operation == "Replace (Overwrite)":
                                            impact.business_process_ids = asset_ids
                                        else:
                                            impact.business_process_ids = [id for id in impact.business_process_ids if id not in asset_ids]
                                    
                                    elif asset_type == "Systems":
                                        asset_ids = [sys_options[name] for name in selected_assets]
                                        if asset_operation == "Assign (Add)":
                                            impact.system_ids = list(set(impact.system_ids + asset_ids))
                                        elif asset_operation == "Replace (Overwrite)":
                                            impact.system_ids = asset_ids
                                        else:
                                            impact.system_ids = [id for id in impact.system_ids if id not in asset_ids]
                                    
                                    elif asset_type == "Policies":
                                        asset_ids = [pol_options[name] for name in selected_assets]
                                        if asset_operation == "Assign (Add)":
                                            impact.policy_ids = list(set(impact.policy_ids + asset_ids))
                                        elif asset_operation == "Replace (Overwrite)":
                                            impact.policy_ids = asset_ids
                                        else:
                                            impact.policy_ids = [id for id in impact.policy_ids if id not in asset_ids]
                                    
                                    repo.update_impact(impact)
                            
                            st.success(f"✅ Updated {selected_count} impacts")
                            st.session_state['selected_impact_ids'] = []
                            st.rerun()
                        else:
                            st.error("Please select at least one asset")
                
                with col2:
                    if st.form_submit_button("Cancel", use_container_width=True):
                        pass
        
        with operation_tab3:
            st.markdown("#### Bulk Change Asset Assignment")
            st.markdown(f"Assign change assets to **{selected_count} selected impacts**")
            
            with st.form("bulk_change_assets_form"):
                asset_type_ca = st.selectbox(
                    "Asset Type",
                    ["Training", "Communication", "QRG", "FAQ", "Job Aid", "Manager Toolkit", "Process Document", "Video", "eLearning", "Other"]
                )
                
                asset_name = st.text_input(
                    "Asset Name*",
                    placeholder="e.g., End User Training"
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    asset_status = st.selectbox(
                        "Status",
                        ["Planned", "In Progress", "Review", "Complete"],
                        index=0
                    )
                
                with col2:
                    asset_owner = st.text_input("Owner", placeholder="Person responsible")
                
                description = st.text_area(
                    "Description",
                    placeholder="Brief description of this deliverable..."
                )
                
                st.markdown("---")
                st.markdown("**Preview:**")
                
                if asset_name:
                    st.info(f"**Create** {asset_type_ca}: '{asset_name}' for {selected_count} impacts")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.form_submit_button("✅ Create for All Selected", type="primary", use_container_width=True):
                        if asset_name:
                            for impact_id in st.session_state['selected_impact_ids']:
                                repo.create_change_asset(
                                    impact_id,
                                    asset_type_ca,
                                    asset_name,
                                    description,
                                    asset_status,
                                    asset_owner
                                )
                            
                            st.success(f"✅ Created '{asset_name}' for {selected_count} impacts")
                            st.session_state['selected_impact_ids'] = []
                            st.rerun()
                        else:
                            st.error("Asset name is required")
                
                with col2:
                    if st.form_submit_button("Cancel", use_container_width=True):
                        pass
            
            st.markdown("---")
            st.markdown("#### Quick Add Common Assets")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("+ End User Training", use_container_width=True):
                    for impact_id in st.session_state['selected_impact_ids']:
                        repo.create_change_asset(impact_id, "Training", "End User Training", "", "Planned", "")
                    st.success(f"✅ Added to {selected_count} impacts")
                    st.session_state['selected_impact_ids'] = []
                    st.rerun()
                
                if st.button("+ Quick Reference Guide", use_container_width=True):
                    for impact_id in st.session_state['selected_impact_ids']:
                        repo.create_change_asset(impact_id, "QRG", "Quick Reference Guide", "", "Planned", "")
                    st.success(f"✅ Added to {selected_count} impacts")
                    st.session_state['selected_impact_ids'] = []
                    st.rerun()
            
            with col2:
                if st.button("+ Manager Training", use_container_width=True):
                    for impact_id in st.session_state['selected_impact_ids']:
                        repo.create_change_asset(impact_id, "Training", "Manager Training", "", "Planned", "")
                    st.success(f"✅ Added to {selected_count} impacts")
                    st.session_state['selected_impact_ids'] = []
                    st.rerun()
                
                if st.button("+ FAQ", use_container_width=True):
                    for impact_id in st.session_state['selected_impact_ids']:
                        repo.create_change_asset(impact_id, "FAQ", "Frequently Asked Questions", "", "Planned", "")
                    st.success(f"✅ Added to {selected_count} impacts")
                    st.session_state['selected_impact_ids'] = []
                    st.rerun()
            
            with col3:
                if st.button("+ Change Announcement", use_container_width=True):
                    for impact_id in st.session_state['selected_impact_ids']:
                        repo.create_change_asset(impact_id, "Communication", "Change Announcement", "", "Planned", "")
                    st.success(f"✅ Added to {selected_count} impacts")
                    st.session_state['selected_impact_ids'] = []
                    st.rerun()
                
                if st.button("+ Job Aid", use_container_width=True):
                    for impact_id in st.session_state['selected_impact_ids']:
                        repo.create_change_asset(impact_id, "Job Aid", "Step-by-Step Guide", "", "Planned", "")
                    st.success(f"✅ Added to {selected_count} impacts")
                    st.session_state['selected_impact_ids'] = []
                    st.rerun()
        
        with operation_tab4:
            st.markdown("#### Bulk Notes Operations")
            st.markdown(f"Manage notes for **{selected_count} selected impacts**")
            
            notes_operation = st.radio(
                "Operation Type",
                ["Append Notes", "Replace Notes"],
                horizontal=True
            )
            
            with st.form("bulk_notes_form"):
                notes_text = st.text_area(
                    "Notes",
                    placeholder="Enter notes to append or replace...",
                    height=100
                )
                
                st.markdown("---")
                st.markdown("**Preview:**")
                
                if notes_text:
                    if notes_operation == "Append Notes":
                        st.info(f"**Append** notes to {selected_count} impacts")
                    else:
                        st.warning(f"**Replace** notes for {selected_count} impacts")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.form_submit_button("✅ Apply Notes", type="primary", use_container_width=True):
                        if notes_text:
                            for impact_id in st.session_state['selected_impact_ids']:
                                impact = repo.get_impact(impact_id)
                                if impact:
                                    if notes_operation == "Append Notes":
                                        existing_notes = impact.notes or ""
                                        if existing_notes:
                                            impact.notes = f"{existing_notes}\n\n{notes_text}"
                                        else:
                                            impact.notes = notes_text
                                    else:
                                        impact.notes = notes_text
                                    
                                    repo.update_impact(impact)
                            
                            st.success(f"✅ Updated notes for {selected_count} impacts")
                            st.session_state['selected_impact_ids'] = []
                            st.rerun()
                        else:
                            st.error("Please enter notes")
                
                with col2:
                    if st.form_submit_button("Cancel", use_container_width=True):
                        pass
        
        st.markdown("---")
        
        st.markdown("### ⚠️ Bulk Delete (Draft Only)")
        
        draft_selected = []
        for impact_id in st.session_state['selected_impact_ids']:
            impact = repo.get_impact(impact_id)
            if impact and impact.status == "Draft":
                draft_selected.append(impact_id)
        
        if draft_selected:
            st.warning(f"**{len(draft_selected)} Draft impacts** selected for deletion")
            
            with st.form("bulk_delete_form"):
                st.error("⚠️ **Warning:** This action cannot be undone!")
                
                confirm_text = st.text_input(
                    "Type 'DELETE' to confirm",
                    placeholder="DELETE"
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.form_submit_button("🗑️ Delete Draft Impacts", type="secondary", use_container_width=True):
                        if confirm_text == "DELETE":
                            for impact_id in draft_selected:
                                repo.delete_impact(impact_id)
                            
                            st.success(f"✅ Deleted {len(draft_selected)} draft impacts")
                            st.session_state['selected_impact_ids'] = []
                            st.rerun()
                        else:
                            st.error("Please type 'DELETE' to confirm")
                
                with col2:
                    if st.form_submit_button("Cancel", use_container_width=True):
                        pass
        else:
            st.info("Only Draft impacts can be bulk deleted. No Draft impacts in current selection.")

st.markdown("---")
st.markdown("### 💡 Bulk Operations Best Practices")
st.markdown("""
- **Filter first** - Narrow down to the impacts you want to modify
- **Select carefully** - Review your selection before applying operations
- **Preview changes** - Always review the preview before applying
- **Start small** - Test with a few impacts before bulk operations on many
- **Use quick add** - Common change assets available for one-click bulk assignment
- **Append vs. Replace** - Choose carefully when updating notes or relationships
""")
