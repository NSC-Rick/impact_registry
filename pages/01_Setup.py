import streamlit as st
from datetime import datetime
from database.schema import init_db, get_session, get_engine
from services.repository import Repository
from services.carry_forward import CarryForwardService
from models.project import ProjectDTO

st.set_page_config(page_title="Setup", page_icon="⚙️", layout="wide")

engine = init_db()
session = get_session(engine)
repo = Repository(session)
carry_forward = CarryForwardService(session)

st.title("⚙️ Setup")
st.markdown("### Configure Project and Enterprise Assets")

tab1, tab2, tab3 = st.tabs(["Project", "Enterprise Assets", "Carry Forward"])

with tab1:
    st.subheader("Project Configuration")
    
    projects = repo.list_projects()
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if projects:
            project_options = {f"{p.name} (ID: {p.id})": p.id for p in projects}
            selected_project = st.selectbox(
                "Select Project",
                options=list(project_options.keys()),
                key="project_selector"
            )
            if selected_project:
                project_id = project_options[selected_project]
                st.session_state['current_project_id'] = project_id
        else:
            st.info("No projects found. Create your first project below.")
    
    with col2:
        if st.button("➕ New Project", use_container_width=True):
            st.session_state['show_new_project_form'] = True
    
    if st.session_state.get('show_new_project_form', False):
        st.markdown("---")
        st.subheader("Create New Project")
        
        with st.form("new_project_form"):
            name = st.text_input("Project Name*", placeholder="e.g., ERP Implementation")
            description = st.text_area("Description", placeholder="Brief project overview")
            
            col1, col2 = st.columns(2)
            with col1:
                sponsor = st.text_input("Sponsor", placeholder="Executive sponsor name")
                start_date = st.date_input("Start Date")
            with col2:
                change_manager = st.text_input("Change Manager", placeholder="Your name")
                end_date = st.date_input("End Date")
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("Create Project", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("Cancel", use_container_width=True)
            
            if submit and name:
                project_dto = ProjectDTO(
                    name=name,
                    description=description,
                    sponsor=sponsor,
                    change_manager=change_manager,
                    start_date=datetime.combine(start_date, datetime.min.time()),
                    end_date=datetime.combine(end_date, datetime.min.time()),
                    status="Active"
                )
                new_project = repo.create_project(project_dto)
                st.success(f"✅ Project '{new_project.name}' created successfully!")
                st.session_state['current_project_id'] = new_project.id
                st.session_state['show_new_project_form'] = False
                st.rerun()
            
            if cancel:
                st.session_state['show_new_project_form'] = False
                st.rerun()
    
    if 'current_project_id' in st.session_state:
        st.markdown("---")
        project = repo.get_project(st.session_state['current_project_id'])
        if project:
            st.subheader("Project Details")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Project Name", project.name)
                st.metric("Sponsor", project.sponsor or "Not set")
                st.metric("Status", project.status)
            with col2:
                st.metric("Change Manager", project.change_manager or "Not set")
                if project.start_date:
                    st.metric("Start Date", project.start_date.strftime("%Y-%m-%d"))
                if project.end_date:
                    st.metric("End Date", project.end_date.strftime("%Y-%m-%d"))

with tab2:
    if 'current_project_id' not in st.session_state:
        st.warning("⚠️ Please select or create a project first")
    else:
        project_id = st.session_state['current_project_id']
        
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
                            repo.create_stakeholder_group(project_id, name, description, size, influence)
                            st.success(f"✅ Added '{name}'")
                            st.rerun()
            
            groups = repo.list_stakeholder_groups(project_id)
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
                            repo.create_organization_unit(project_id, name, description, parent_unit, head_of_unit)
                            st.success(f"✅ Added '{name}'")
                            st.rerun()
            
            units = repo.list_organization_units(project_id)
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
                            repo.create_business_process(project_id, name, description, process_owner, criticality)
                            st.success(f"✅ Added '{name}'")
                            st.rerun()
            
            processes = repo.list_business_processes(project_id)
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
                            repo.create_system(project_id, name, description, system_owner, vendor, criticality)
                            st.success(f"✅ Added '{name}'")
                            st.rerun()
            
            systems = repo.list_systems(project_id)
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
                                project_id, name, description, policy_owner,
                                datetime.combine(effective_date, datetime.min.time())
                            )
                            st.success(f"✅ Added '{name}'")
                            st.rerun()
            
            policies = repo.list_policies(project_id)
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

with tab3:
    st.subheader("Carry Forward Assets")
    st.markdown("Copy enterprise assets from a previous project to accelerate setup.")
    
    if 'current_project_id' not in st.session_state:
        st.warning("⚠️ Please select or create a project first")
    else:
        projects = repo.list_projects()
        source_projects = [p for p in projects if p.id != st.session_state['current_project_id']]
        
        if source_projects:
            source_project_options = {f"{p.name} (ID: {p.id})": p.id for p in source_projects}
            selected_source = st.selectbox(
                "Select Source Project",
                options=list(source_project_options.keys())
            )
            
            if st.button("🔄 Carry Forward Assets", type="primary"):
                source_id = source_project_options[selected_source]
                target_id = st.session_state['current_project_id']
                
                with st.spinner("Copying assets..."):
                    counts = carry_forward.carry_forward_enterprise_assets(source_id, target_id)
                
                st.success("✅ Assets carried forward successfully!")
                st.json(counts)
        else:
            st.info("No other projects available to carry forward from")
