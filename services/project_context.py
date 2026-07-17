"""
Project Context Service

Provides centralized access to the active project throughout the application.
All pages must retrieve project information through this service.

This is the single source of truth for project identity.
"""

import streamlit as st
from typing import Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ActiveProject:
    """Active project context"""
    uuid: str
    name: str
    client: str
    description: str
    status: str
    file_path: str
    created_at: datetime
    last_modified: datetime
    last_opened: datetime
    version: str


class ProjectContext:
    """
    Centralized project context service.
    
    Provides the single source of truth for the active project.
    All pages should use this service to access project information.
    """
    
    SESSION_KEY = 'active_project_context'
    
    @classmethod
    def set_active_project(cls, project: ActiveProject) -> None:
        """Set the active project in session state"""
        st.session_state[cls.SESSION_KEY] = project
        st.session_state['current_project'] = project.name  # Backward compatibility
        st.session_state['last_opened'] = datetime.utcnow()
    
    @classmethod
    def get_active_project(cls) -> Optional[ActiveProject]:
        """Get the active project from session state"""
        return st.session_state.get(cls.SESSION_KEY)
    
    @classmethod
    def has_active_project(cls) -> bool:
        """Check if there is an active project"""
        return cls.SESSION_KEY in st.session_state and st.session_state[cls.SESSION_KEY] is not None
    
    @classmethod
    def clear_active_project(cls) -> None:
        """Clear the active project (close workspace)"""
        if cls.SESSION_KEY in st.session_state:
            del st.session_state[cls.SESSION_KEY]
        if 'current_project' in st.session_state:
            del st.session_state['current_project']
    
    @classmethod
    def get_project_name(cls) -> Optional[str]:
        """Get the active project name"""
        project = cls.get_active_project()
        return project.name if project else None
    
    @classmethod
    def get_project_uuid(cls) -> Optional[str]:
        """Get the active project UUID"""
        project = cls.get_active_project()
        return project.uuid if project else None
    
    @classmethod
    def get_project_status(cls) -> Optional[str]:
        """Get the active project status"""
        project = cls.get_active_project()
        return project.status if project else None
    
    @classmethod
    def get_project_file_path(cls) -> Optional[str]:
        """Get the active project file path"""
        project = cls.get_active_project()
        return project.file_path if project else None
    
    @classmethod
    def update_last_opened(cls) -> None:
        """Update the last opened timestamp"""
        project = cls.get_active_project()
        if project:
            project.last_opened = datetime.utcnow()
            cls.set_active_project(project)
