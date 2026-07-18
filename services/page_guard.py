"""
Page Guard

Validates workspace before allowing pages to load.
Prevents pages from attempting to query non-existent tables.
"""
import streamlit as st
from services.project_context import ProjectContext
from services.workspace_validator import WorkspaceValidator


def require_valid_workspace():
    """
    Workspace guard - ensures a valid workspace is active before page loads.
    
    Call this at the top of every practitioner page.
    
    Validates:
    - Active project exists
    - Workspace file exists
    - Database schema is complete
    - Required tables present
    - Project metadata exists
    
    If validation fails, redirects to Home with error message.
    """
    # Check if project is active
    if not ProjectContext.has_active_project():
        st.error("⚠️ No valid project workspace is currently available.")
        st.info("""
        **No Active Project**
        
        Please create a new project or open an existing project from the Home page.
        """)
        
        if st.button("🏠 Go to Home", use_container_width=True):
            st.switch_page("pages/00_Home.py")
        
        st.stop()
    
    # Get active project
    active_project = ProjectContext.get_active_project()
    
    # Validate workspace
    validator = WorkspaceValidator()
    is_valid, message, missing = validator.validate_workspace(active_project.file_path)
    
    if not is_valid:
        st.error("⚠️ Workspace Validation Failed")
        
        st.warning(f"**Issue:** {message}")
        
        if missing:
            st.error(f"**Missing Components:** {', '.join(missing)}")
        
        st.info("""
        **Workspace Incomplete**
        
        This project workspace is corrupted or incomplete.
        The workspace initialization did not complete successfully.
        
        **Recommended Actions:**
        1. Return to Home and create a new project
        2. Or restore from a backup if available
        """)
        
        # Provide action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🏠 Return to Home", use_container_width=True):
                ProjectContext.clear_active_project()
                st.switch_page("pages/00_Home.py")
        with col2:
            if st.button("🔄 Retry Validation", use_container_width=True):
                st.rerun()
        with col3:
            if st.button("📋 View Details", use_container_width=True):
                with st.expander("Validation Details", expanded=True):
                    st.code(f"""
Project: {active_project.name}
File: {active_project.file_path}
Status: {message}
Missing: {missing if missing else 'None'}
                    """)
        
        st.stop()
    
    # Workspace is valid, allow page to continue
    return True


def get_validated_session():
    """
    Get a validated database session for the active project.
    
    Returns:
        SQLAlchemy session for the active project
        
    Raises:
        Redirects to Home if no valid workspace
    """
    require_valid_workspace()
    
    from database.schema import get_engine, get_session
    
    active_project = ProjectContext.get_active_project()
    engine = get_engine(active_project.file_path)
    session = get_session(engine)
    
    return session
