import streamlit as st
from datetime import datetime
import os

from database.schema import get_session, get_engine, ProjectMetadata
from services.workspace_service import WorkspaceService
from services.project_context import ProjectContext

st.title("🏠 Impact Registry")
st.markdown("### Home")

# Initialize workspace service
workspace = WorkspaceService()

# Discover projects on every page load (filesystem-based discovery)
# This ensures projects are always found after app restart
discovered_count = workspace.discover_projects()
if discovered_count > 0:
    print(f"\n[HOME] Discovered {discovered_count} new project(s)")

# Log all loaded projects
all_projects = workspace.registry.list_projects()
if all_projects:
    print(f"\nLoaded Projects ({len(all_projects)}):")
    for project in all_projects:
        print(f"  ✓ {project.name}")
    print()

# Display current project info if active
if ProjectContext.has_active_project():
    active_project = ProjectContext.get_active_project()
    st.info(f"📂 **Current Project:** {active_project.name}")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📡 Signal Center", use_container_width=True):
            st.switch_page("pages/01_Signal_Center.py")
    with col2:
        if st.button("✍️ Capture", use_container_width=True):
            st.switch_page("pages/03_Capture.py")
    with col3:
        if st.button("🔗 Enrich", use_container_width=True):
            st.switch_page("pages/04_Enrich.py")
    with col4:
        if st.button("📊 Analyze", use_container_width=True):
            st.switch_page("pages/05_Analyze.py")
    
    st.markdown("---")

# Show welcome section if no active project
if not ProjectContext.has_active_project():
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## Welcome to Impact Registry")
        st.markdown("""
        **Impact Registry** is a practitioner-first tool for capturing, enriching, analyzing, 
        and monitoring organizational change impacts.
        
        Each **Project Workspace** is an independent, self-contained repository of change knowledge 
        for a single implementation project.
        
        **To begin:** Create a new project or open an existing project workspace.
        """)
    
    with col2:
        st.markdown("## Quick Start")
        st.markdown("""
        1. **New Project** - Start fresh
        2. **Open Project** - Continue work
        3. **Recent Projects** - Quick access
        """)
    
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📁 Recent Projects", "➕ New Project", "📂 Open Project"])
    
    with tab1:
        st.markdown("### Recent Projects")
        
        recent_projects = workspace.get_recent_projects(limit=10)
        
        if recent_projects:
            for proj in recent_projects:
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                
                with col1:
                    st.markdown(f"**{proj.name}**")
                    if proj.client:
                        st.caption(f"Client: {proj.client}")
                
                with col2:
                    st.caption(f"Status: {proj.status}")
                
                with col3:
                    last_opened = datetime.fromisoformat(proj.last_opened)
                    st.caption(f"Opened: {last_opened.strftime('%Y-%m-%d')}")
                
                with col4:
                    if st.button("Open", key=f"open_recent_{proj.uuid}"):
                        success, message, active_project = workspace.open_project(proj.uuid)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
        else:
            st.info("No recent projects. Create a new project to get started.")
    
    with tab2:
        st.markdown("### Create New Project")
        
        # Initialize wizard state
        if 'wizard_step' not in st.session_state:
            st.session_state['wizard_step'] = 1
        if 'wizard_data' not in st.session_state:
            st.session_state['wizard_data'] = {}
        
        # Step indicator
        steps = ["Project Info", "Starter Library", "Review", "Create"]
        current_step = st.session_state['wizard_step']
        
        cols = st.columns(4)
        for i, step_name in enumerate(steps, 1):
            with cols[i-1]:
                if i < current_step:
                    st.markdown(f"✅ **{step_name}**")
                elif i == current_step:
                    st.markdown(f"▶️ **{step_name}**")
                else:
                    st.markdown(f"⚪ {step_name}")
        
        st.markdown("---")
        
        # Step 1: Project Information
        if current_step == 1:
            st.markdown("#### Step 1: Project Information")
            
            with st.form("wizard_step1"):
                project_name = st.text_input(
                    "Project Name*",
                    value=st.session_state['wizard_data'].get('project_name', ''),
                    help="Unique name for this project workspace"
                )
                client_name = st.text_input(
                    "Client Name",
                    value=st.session_state['wizard_data'].get('client_name', ''),
                    help="Client organization name"
                )
                description = st.text_area(
                    "Project Description",
                    value=st.session_state['wizard_data'].get('description', ''),
                    help="Brief description of the implementation"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    industry = st.selectbox(
                        "Industry",
                        ["", "Healthcare", "Financial Services", "Manufacturing", "Retail", "Technology", "Government", "Other"],
                        index=0
                    )
                with col2:
                    project_type = st.selectbox(
                        "Project Type",
                        ["", "ERP Implementation", "VMS/MSP", "HR Transformation", "Finance Transformation", "Supply Chain", "Other"],
                        index=0
                    )
                
                status = st.selectbox(
                    "Project Status",
                    ["Pre-Implementation", "Planning", "In Progress", "On Hold", "Completed", "Archived"],
                    help="Current project status"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    cancel = st.form_submit_button("Cancel")
                with col2:
                    next_step = st.form_submit_button("Next →", type="primary")
                
                if cancel:
                    st.session_state['wizard_step'] = 1
                    st.session_state['wizard_data'] = {}
                    st.rerun()
                
                if next_step:
                    if not project_name:
                        st.error("Project Name is required")
                    else:
                        st.session_state['wizard_data']['project_name'] = project_name
                        st.session_state['wizard_data']['client_name'] = client_name
                        st.session_state['wizard_data']['description'] = description
                        st.session_state['wizard_data']['industry'] = industry
                        st.session_state['wizard_data']['project_type'] = project_type
                        st.session_state['wizard_data']['status'] = status
                        st.session_state['wizard_step'] = 2
                        st.rerun()
        
        # Step 2: Select Starter Library
        elif current_step == 2:
            st.markdown("#### Step 2: Select Starter Library")
            st.markdown("Choose a starter library to populate your project with baseline content.")
            
            from libraries.starter_library_service import StarterLibraryService
            library_service = StarterLibraryService()
            libraries = library_service.list_libraries()
            
            if not libraries:
                st.warning("No starter libraries found. Creating blank project.")
                st.session_state['wizard_data']['library_id'] = None
                st.session_state['wizard_step'] = 3
                st.rerun()
            
            # Display library options
            selected_library = st.session_state['wizard_data'].get('library_id', 'blank')
            
            for library in libraries:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"### {library.name}")
                        st.markdown(library.description)
                        
                        if library.id != 'blank':
                            summary = library.get_summary()
                            st.caption(
                                f"📊 {summary['impacts']} Impacts • "
                                f"{summary['stakeholder_groups']} Stakeholder Groups • "
                                f"{summary['business_processes']} Business Processes"
                            )
                    
                    with col2:
                        if st.button("Select", key=f"select_{library.id}", use_container_width=True):
                            st.session_state['wizard_data']['library_id'] = library.id
                            st.session_state['wizard_data']['library_name'] = library.name
                            selected_library = library.id
                    
                    st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Back"):
                    st.session_state['wizard_step'] = 1
                    st.rerun()
            with col2:
                if st.button("Next →", type="primary"):
                    if 'library_id' not in st.session_state['wizard_data']:
                        st.error("Please select a starter library")
                    else:
                        st.session_state['wizard_step'] = 3
                        st.rerun()
        
        # Step 3: Review Summary
        elif current_step == 3:
            st.markdown("#### Step 3: Review Summary")
            
            data = st.session_state['wizard_data']
            
            st.markdown("**Project Information:**")
            st.write(f"- **Name:** {data.get('project_name')}")
            st.write(f"- **Client:** {data.get('client_name', 'Not specified')}")
            st.write(f"- **Description:** {data.get('description', 'Not specified')}")
            st.write(f"- **Industry:** {data.get('industry', 'Not specified')}")
            st.write(f"- **Project Type:** {data.get('project_type', 'Not specified')}")
            st.write(f"- **Status:** {data.get('status')}")
            
            st.markdown("---")
            
            st.markdown("**Starter Library:**")
            library_name = data.get('library_name', 'Blank Project')
            st.write(f"- **Selected:** {library_name}")
            
            if data.get('library_id') and data.get('library_id') != 'blank':
                from libraries.starter_library_service import StarterLibraryService
                library_service = StarterLibraryService()
                library = library_service.load_library(data['library_id'])
                
                if library:
                    summary = library.get_summary()
                    st.markdown("**Content to Import:**")
                    st.write(f"- {summary['stakeholder_groups']} Stakeholder Groups")
                    st.write(f"- {summary['organization_units']} Organization Units")
                    st.write(f"- {summary['business_processes']} Business Processes")
                    st.write(f"- {summary['systems']} Systems")
                    st.write(f"- {summary['policies']} Policies")
                    st.write(f"- {summary['impacts']} Change Impacts")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Back"):
                    st.session_state['wizard_step'] = 2
                    st.rerun()
            with col2:
                if st.button("Create Project Workspace", type="primary"):
                    st.session_state['wizard_step'] = 4
                    st.rerun()
        
        # Step 4: Create Workspace
        elif current_step == 4:
            st.markdown("#### Step 4: Creating Workspace...")
            
            data = st.session_state['wizard_data']
            
            with st.spinner("Creating project workspace..."):
                success, message, active_project = workspace.create_new_project(
                    name=data['project_name'],
                    client=data.get('client_name', ''),
                    description=data.get('description', ''),
                    status=data.get('status', 'Pre-Implementation'),
                    starter_library_id=data.get('library_id')
                )
                
                if success:
                    st.success(f"✅ {message}")
                    
                    if data.get('library_id') and data.get('library_id') != 'blank':
                        st.info(f"📚 Starter library '{data.get('library_name')}' applied successfully")
                    
                    # Reset wizard
                    st.session_state['wizard_step'] = 1
                    st.session_state['wizard_data'] = {}
                    
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("← Back to Review"):
                            st.session_state['wizard_step'] = 3
                            st.rerun()
                    with col2:
                        if st.button("Cancel"):
                            st.session_state['wizard_step'] = 1
                            st.session_state['wizard_data'] = {}
                            st.rerun()
    
    with tab3:
        st.markdown("### Open Existing Project")
        
        all_projects = workspace.registry.list_projects()
        
        if all_projects:
            st.markdown(f"**{len(all_projects)} project workspace(s) available:**")
            
            for proj in all_projects:
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                
                with col1:
                    st.markdown(f"**{proj.name}**")
                    if proj.client:
                        st.caption(f"Client: {proj.client}")
                
                with col2:
                    st.caption(f"Status: {proj.status}")
                
                with col3:
                    modified = datetime.fromisoformat(proj.last_modified)
                    st.caption(f"Modified: {modified.strftime('%Y-%m-%d')}")
                
                with col4:
                    if st.button("Open", key=f"open_all_{proj.uuid}"):
                        success, message, active_project = workspace.open_project(proj.uuid)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
        else:
            st.info("No projects found. Create a new project to get started.")

else:
    # Get active project from context
    active_project = ProjectContext.get_active_project()
    
    if not active_project:
        st.error("Active project context lost. Please reopen the project.")
        ProjectContext.clear_active_project()
        st.rerun()
    
    # Display workspace status bar
    st.success(f"✅ **Project Workspace:** {active_project.name}")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if active_project.client:
            st.caption(f"**Client:** {active_project.client}")
    with col2:
        st.caption(f"**Status:** {active_project.status}")
    with col3:
        st.caption(f"**Last Opened:** {active_project.last_opened.strftime('%Y-%m-%d %H:%M')}")
    with col4:
        st.caption(f"**Version:** {active_project.version}")
    
    st.markdown("---")
    
    st.markdown("""
    ### Practitioner Workflow
    
    Use the sidebar to navigate through the Impact Registry workflow:
    
    1. **Setup** - Configure enterprise assets
    2. **Capture** - Record impacts quickly
    3. **Enrich** - Add traceability and context
    4. **Analyze** - Understand patterns and risks
    5. **Monitor** - Track progress and coverage
    
    👈 Select a workspace from the sidebar to begin.
    """)
    
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("💾 Save Project", use_container_width=True):
            success, message = workspace.save_project()
            if success:
                st.success(message)
            else:
                st.error(message)
    
    with col2:
        if st.button("📋 Save As...", use_container_width=True):
            st.session_state['show_save_as'] = True
    
    with col3:
        if st.button("🔄 Switch Project", use_container_width=True):
            success, message = workspace.close_project()
            if success:
                st.info(message)
            st.rerun()
    
    with col4:
        if st.button("📤 Export", use_container_width=True):
            st.info("Export functionality available in Setup workspace")
    
    # Save As dialog
    if st.session_state.get('show_save_as', False):
        with st.form("save_as_form"):
            st.markdown("### Save Project As")
            new_name = st.text_input("New Project Name*")
            
            col1, col2 = st.columns(2)
            with col1:
                save_as = st.form_submit_button("Save As", type="primary")
            with col2:
                cancel = st.form_submit_button("Cancel")
            
            if save_as and new_name:
                success, message, new_project = workspace.save_project_as(new_name)
                if success:
                    st.success(message)
                    st.session_state['show_save_as'] = False
                    st.rerun()
                else:
                    st.error(message)
            
            if cancel:
                st.session_state['show_save_as'] = False
                st.rerun()

st.markdown("---")
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("**Design Principles:** Practitioner First • Project Isolation • Coverage, not Execution • Traceability • Enterprise Assets • Carry Forward")
with col2:
    st.markdown(f"**Version:** {workspace.APP_VERSION}")
