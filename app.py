import streamlit as st
from database.schema import init_db, get_session, get_engine, list_projects, get_recent_projects, ProjectMetadata
from datetime import datetime
import os

st.set_page_config(
    page_title="Impact Registry - Project Workspace",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎯 Impact Registry")
st.markdown("### Project Workspace Management")

if 'current_project' not in st.session_state:
    st.session_state['current_project'] = None

if st.session_state['current_project'] is None:
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
        
        recent_projects = get_recent_projects(max_count=10)
        
        if recent_projects:
            for proj in recent_projects:
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"**{proj['name']}**")
                    st.caption(f"Modified: {proj['modified'].strftime('%Y-%m-%d %H:%M')}")
                
                with col2:
                    size_kb = proj['size'] / 1024
                    st.caption(f"Size: {size_kb:.1f} KB")
                
                with col3:
                    if st.button("Open", key=f"open_recent_{proj['name']}"):
                        st.session_state['current_project'] = proj['name']
                        st.rerun()
        else:
            st.info("No recent projects. Create a new project to get started.")
    
    with tab2:
        st.markdown("### Create New Project")
        
        with st.form("new_project_form"):
            project_name = st.text_input("Project Name*", help="Unique name for this project workspace")
            client_name = st.text_input("Client Name", help="Client organization name")
            program_name = st.text_input("Program Name", help="Program or initiative name")
            description = st.text_area("Project Description", help="Brief description of the implementation")
            
            col1, col2 = st.columns(2)
            with col1:
                sponsor = st.text_input("Executive Sponsor")
                start_date = st.date_input("Start Date")
            with col2:
                change_manager = st.text_input("Change Manager")
                end_date = st.date_input("End Date")
            
            submitted = st.form_submit_button("Create Project Workspace")
            
            if submitted:
                if not project_name:
                    st.error("Project Name is required")
                else:
                    existing_projects = list_projects()
                    if any(p['name'].lower() == project_name.lower() for p in existing_projects):
                        st.error(f"Project '{project_name}' already exists. Choose a different name.")
                    else:
                        engine = init_db(project_name)
                        session = get_session(engine)
                        
                        metadata = ProjectMetadata(
                            project_name=project_name,
                            client_name=client_name,
                            program_name=program_name,
                            description=description,
                            sponsor=sponsor,
                            change_manager=change_manager,
                            start_date=datetime.combine(start_date, datetime.min.time()) if start_date else None,
                            end_date=datetime.combine(end_date, datetime.min.time()) if end_date else None,
                            registry_version='1.0',
                            status='Active'
                        )
                        session.add(metadata)
                        session.commit()
                        session.close()
                        
                        st.session_state['current_project'] = project_name
                        st.success(f"✅ Project '{project_name}' created successfully!")
                        st.rerun()
    
    with tab3:
        st.markdown("### Open Existing Project")
        
        all_projects = list_projects()
        
        if all_projects:
            st.markdown(f"**{len(all_projects)} project workspace(s) available:**")
            
            for proj in all_projects:
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                
                with col1:
                    st.markdown(f"**{proj['name']}**")
                
                with col2:
                    st.caption(f"Modified: {proj['modified'].strftime('%Y-%m-%d')}")
                
                with col3:
                    size_kb = proj['size'] / 1024
                    st.caption(f"{size_kb:.1f} KB")
                
                with col4:
                    if st.button("Open", key=f"open_all_{proj['name']}"):
                        st.session_state['current_project'] = proj['name']
                        st.rerun()
        else:
            st.info("No projects found. Create a new project to get started.")

else:
    current_project = st.session_state['current_project']
    
    engine = get_engine(current_project)
    session = get_session(engine)
    
    metadata = session.query(ProjectMetadata).first()
    
    st.success(f"✅ **Project Workspace:** {current_project}")
    
    if metadata:
        col1, col2, col3 = st.columns(3)
        with col1:
            if metadata.client_name:
                st.caption(f"**Client:** {metadata.client_name}")
        with col2:
            if metadata.program_name:
                st.caption(f"**Program:** {metadata.program_name}")
        with col3:
            st.caption(f"**Status:** {metadata.status}")
    
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
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save Project", use_container_width=True):
            st.success("Project automatically saved")
    
    with col2:
        if st.button("� Switch Project", use_container_width=True):
            st.session_state['current_project'] = None
            st.rerun()
    
    with col3:
        if st.button("📤 Export Project", use_container_width=True):
            st.info("Export functionality available in Setup workspace")
    
    session.close()

st.markdown("---")
st.markdown("**Design Principles:** Practitioner First • Project Isolation • Coverage, not Execution • Traceability • Enterprise Assets • Carry Forward")
