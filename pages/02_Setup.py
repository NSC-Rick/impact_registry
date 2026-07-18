import streamlit as st
import os
from datetime import datetime
from database.schema import init_db, get_session, get_engine, ProjectMetadata
from services.repository import Repository
from services.project_context import ProjectContext
from models.project import ProjectMetadataDTO

# Check for active project workspace using ProjectContext
if not ProjectContext.has_active_project():
    st.warning("⚠️ Please open a project workspace first")
    st.info("Return to the home page to create or open a project workspace")
    st.stop()

# Get active project from ProjectContext
active_project = ProjectContext.get_active_project()
print(f"\n[SETUP] Database: {os.path.abspath(active_project.file_path)}")

engine = get_engine(active_project.file_path)
session = get_session(engine)
repo = Repository(session)

st.title("⚙️ Setup")
st.markdown("### Configure Project and Enterprise Assets")

# Get project metadata
metadata = session.query(ProjectMetadata).first()

tab1, tab2 = st.tabs(["Project", "Enterprise Assets"])

with tab1:
    st.subheader("Current Project Workspace")
    st.success(f"📁 **{current_project}**")
    
    if metadata:
        st.markdown("---")
        
        # Edit mode toggle
        if 'edit_project' not in st.session_state:
            st.session_state['edit_project'] = False
        
        if not st.session_state['edit_project']:
            # Display mode
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Client", metadata.client_name or "Not set")
                st.metric("Sponsor", metadata.sponsor or "Not set")
            with col2:
                st.metric("Program", metadata.program_name or "Not set")
                st.metric("Change Manager", metadata.change_manager or "Not set")
            with col3:
                st.metric("Status", metadata.status)
                if metadata.start_date:
                    st.metric("Start Date", metadata.start_date.strftime("%Y-%m-%d"))
            
            if metadata.description:
                st.markdown("**Description:**")
                st.write(metadata.description)
            
            if st.button("✏️ Edit Project", use_container_width=True):
                st.session_state['edit_project'] = True
                st.rerun()
        
        else:
            # Edit mode
            with st.form("edit_project_form"):
                st.markdown("#### Edit Project Details")
                
                client_name = st.text_input("Client Name", value=metadata.client_name or "")
                program_name = st.text_input("Program Name", value=metadata.program_name or "")
                description = st.text_area("Description", value=metadata.description or "")
                
                col1, col2 = st.columns(2)
                with col1:
                    sponsor = st.text_input("Executive Sponsor", value=metadata.sponsor or "")
                    start_date = st.date_input("Start Date", value=metadata.start_date.date() if metadata.start_date else datetime.now().date())
                with col2:
                    change_manager = st.text_input("Change Manager", value=metadata.change_manager or "")
                    end_date = st.date_input("End Date", value=metadata.end_date.date() if metadata.end_date else datetime.now().date())
                
                status = st.selectbox("Status", ["Active", "On Hold", "Completed", "Archived"], 
                                     index=["Active", "On Hold", "Completed", "Archived"].index(metadata.status) if metadata.status in ["Active", "On Hold", "Completed", "Archived"] else 0)
                
                col1, col2 = st.columns(2)
                with col1:
                    save = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
                with col2:
                    cancel = st.form_submit_button("Cancel", use_container_width=True)
                
                if save:
                    metadata.client_name = client_name
                    metadata.program_name = program_name
                    metadata.description = description
                    metadata.sponsor = sponsor
                    metadata.change_manager = change_manager
                    metadata.start_date = datetime.combine(start_date, datetime.min.time())
                    metadata.end_date = datetime.combine(end_date, datetime.min.time())
                    metadata.status = status
                    metadata.updated_at = datetime.utcnow()
                    
                    session.commit()
                    st.success("✅ Project updated successfully!")
                    st.session_state['edit_project'] = False
                    st.rerun()
                
                if cancel:
                    st.session_state['edit_project'] = False
                    st.rerun()

with tab2:
    st.subheader("Enterprise Assets")
    st.markdown("Define the organizational elements that will be referenced when enriching impacts.")
    
    asset_tab1, asset_tab2, asset_tab3, asset_tab4, asset_tab5 = st.tabs([
        "Stakeholder Groups", "Organization Units", "Business Processes", "Systems", "Policies"
    ])
    
    with asset_tab1:
        st.markdown("#### Stakeholder Groups")
        
        with st.expander("➕ Add Stakeholder Group"):
            with st.form("new_stakeholder_group"):
                name = st.text_input("Group Name*", placeholder="e.g., Finance Team")
                description = st.text_area("Description")
                col1, col2 = st.columns(2)
                with col1:
                    size = st.number_input("Size", min_value=0, value=0)
                with col2:
                    influence = st.selectbox("Influence", ["", "Low", "Medium", "High"])
                
                if st.form_submit_button("Add Group"):
                    if name:
                        repo.create_stakeholder_group(None, name, description, size, influence)
                        st.success(f"✅ Added '{name}'")
                        st.rerun()
        
        groups = repo.list_stakeholder_groups(None)
        if groups:
            for group in groups:
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"**{group.name}**")
                        if group.description:
                            st.caption(group.description)
                    with col2:
                        st.caption(f"Size: {group.size}")
                    with col3:
                        st.caption(f"Influence: {group.influence}")
                    st.markdown("---")
        else:
            st.info("No stakeholder groups defined yet")
        
    with asset_tab2:
        st.markdown("#### Organization Units")
        
        with st.expander("➕ Add Organization Unit"):
            with st.form("new_org_unit"):
                name = st.text_input("Unit Name*", placeholder="e.g., North America Sales")
                description = st.text_area("Description")
                col1, col2 = st.columns(2)
                with col1:
                    parent_unit = st.text_input("Parent Unit")
                with col2:
                    head_of_unit = st.text_input("Head of Unit")
                
                if st.form_submit_button("Add Unit"):
                    if name:
                        repo.create_organization_unit(None, name, description, parent_unit, head_of_unit)
                        st.success(f"✅ Added '{name}'")
                        st.rerun()
        
        units = repo.list_organization_units(None)
        if units:
            for unit in units:
                with st.container():
                    col1, col2 = st.columns([3, 2])
                    with col1:
                        st.write(f"**{unit.name}**")
                        if unit.description:
                            st.caption(unit.description)
                    with col2:
                        if unit.head_of_unit:
                            st.caption(f"Head: {unit.head_of_unit}")
                    st.markdown("---")
        else:
            st.info("No organization units defined yet")
        
    with asset_tab3:
        st.markdown("#### Business Processes")
        
        with st.expander("➕ Add Business Process"):
            with st.form("new_business_process"):
                name = st.text_input("Process Name*", placeholder="e.g., Order to Cash")
                description = st.text_area("Description")
                col1, col2 = st.columns(2)
                with col1:
                    process_owner = st.text_input("Process Owner")
                with col2:
                    criticality = st.selectbox("Criticality", ["", "Low", "Medium", "High", "Critical"])
                
                if st.form_submit_button("Add Process"):
                    if name:
                        repo.create_business_process(None, name, description, process_owner, criticality)
                        st.success(f"✅ Added '{name}'")
                        st.rerun()
        
        processes = repo.list_business_processes(None)
        if processes:
            for process in processes:
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"**{process.name}**")
                        if process.description:
                            st.caption(process.description)
                    with col2:
                        st.caption(f"Criticality: {process.criticality}")
                    with col3:
                        if process.process_owner:
                            st.caption(f"Owner: {process.process_owner}")
                    st.markdown("---")
        else:
            st.info("No business processes defined yet")
        
    with asset_tab4:
        st.markdown("#### Systems")
        
        with st.expander("➕ Add System"):
            with st.form("new_system"):
                name = st.text_input("System Name*", placeholder="e.g., SAP ERP")
                description = st.text_area("Description")
                col1, col2, col3 = st.columns(3)
                with col1:
                    system_owner = st.text_input("System Owner")
                with col2:
                    vendor = st.text_input("Vendor")
                with col3:
                    criticality = st.selectbox("Criticality", ["", "Low", "Medium", "High", "Critical"])
                
                if st.form_submit_button("Add System"):
                    if name:
                        repo.create_system(None, name, description, system_owner, vendor, criticality)
                        st.success(f"✅ Added '{name}'")
                        st.rerun()
        
        systems = repo.list_systems(None)
        if systems:
            for system in systems:
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"**{system.name}**")
                        if system.description:
                            st.caption(system.description)
                    with col2:
                        if system.vendor:
                            st.caption(f"Vendor: {system.vendor}")
                    with col3:
                        st.caption(f"Criticality: {system.criticality}")
                    st.markdown("---")
        else:
            st.info("No systems defined yet")
        
    with asset_tab5:
        st.markdown("#### Policies")
        
        with st.expander("➕ Add Policy"):
            with st.form("new_policy"):
                name = st.text_input("Policy Name*", placeholder="e.g., Data Privacy Policy")
                description = st.text_area("Description")
                col1, col2 = st.columns(2)
                with col1:
                    policy_owner = st.text_input("Policy Owner")
                with col2:
                    effective_date = st.date_input("Effective Date")
                
                if st.form_submit_button("Add Policy"):
                    if name:
                        repo.create_policy(
                            None, name, description, policy_owner,
                            datetime.combine(effective_date, datetime.min.time())
                        )
                        st.success(f"✅ Added '{name}'")
                        st.rerun()
        
        policies = repo.list_policies(None)
        if policies:
            for policy in policies:
                with st.container():
                    col1, col2 = st.columns([3, 2])
                    with col1:
                        st.write(f"**{policy.name}**")
                        if policy.description:
                            st.caption(policy.description)
                    with col2:
                        if policy.effective_date:
                            st.caption(f"Effective: {policy.effective_date.strftime('%Y-%m-%d')}")
                    st.markdown("---")
        else:
            st.info("No policies defined yet")
