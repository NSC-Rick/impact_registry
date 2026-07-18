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
    Page guard that ensures a valid workspace is active.
    
    Call this at the top of every practitioner page.
    If validation fails, redirects to Home with error message.
    """
    # Check if project is active
    if not ProjectContext.has_active_project():
        st.error("⚠️ No active project. Please open or create a project.")
        st.info("Redirecting to Home...")
        st.switch_page("pages/00_Home.py")
        st.stop()
    
    # Get active project
    active_project = ProjectContext.get_active_project()
    
    # Validate workspace
    validator = WorkspaceValidator()
    is_valid, message, missing = validator.validate_workspace(active_project.file_path)
    
    if not is_valid:
        st.error(f"⚠️ Workspace validation failed: {message}")
        
        if missing:
            st.warning(f"Missing components: {', '.join(missing)}")
        
        st.info("""
        **Workspace initialization is incomplete.**
        
        This project workspace may be corrupted or incomplete.
        Please complete project creation or restore a valid project.
        """)
        
        # Provide action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🏠 Return to Home", use_container_width=True):
                ProjectContext.clear_active_project()
                st.switch_page("pages/00_Home.py")
        with col2:
            if st.button("🔄 Try Again", use_container_width=True):
                st.rerun()
        
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
