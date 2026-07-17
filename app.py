import streamlit as st
from datetime import datetime
import os

from database.schema import get_session, get_engine, ProjectMetadata
from services.workspace_service import WorkspaceService
from services.project_context import ProjectContext

st.set_page_config(
    page_title="Impact Registry - Project Workspace",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎯 Impact Registry")
st.markdown("### Project Workspace Management")

# Initialize workspace service
workspace = WorkspaceService()

# Discover projects on startup
if 'projects_discovered' not in st.session_state:
    workspace.discover_projects()
    st.session_state['projects_discovered'] = True

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
        
        with st.form("new_project_form"):
            project_name = st.text_input("Project Name*", help="Unique name for this project workspace")
            client_name = st.text_input("Client Name", help="Client organization name")
            description = st.text_area("Project Description", help="Brief description of the implementation")
            
            status = st.selectbox(
                "Project Status",
                ["Pre-Implementation", "Planning", "In Progress", "On Hold", "Completed", "Archived"],
                help="Current project status"
            )
            
            submitted = st.form_submit_button("Create Project Workspace", type="primary")
            
            if submitted:
                if not project_name:
                    st.error("Project Name is required")
                else:
                    success, message, active_project = workspace.create_new_project(
                        name=project_name,
                        client=client_name,
                        description=description,
                        status=status
                    )
                    
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
    
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
st.markdown("**Design Principles:** Practitioner First • Project Isolation • Coverage, not Execution • Traceability • Enterprise Assets • Carry Forward")
