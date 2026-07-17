"""
Workspace Service

Handles workspace operations: New, Open, Save, Save As.
Integrates with ProjectContext and ProjectRegistry.
"""

import os
import shutil
import uuid as uuid_lib
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from database.schema import get_engine, get_session, ProjectMetadata, init_db
from services.project_context import ProjectContext, ActiveProject
from services.project_registry import ProjectRegistry, ProjectRegistryEntry


class WorkspaceService:
    """
    Workspace management service.
    
    Handles:
    - New Project
    - Open Project
    - Save
    - Save As
    - Close
    """
    
    WORKSPACES_DIR = "workspaces"
    APP_VERSION = "1.0.0"
    
    def __init__(self):
        """Initialize workspace service"""
        self.registry = ProjectRegistry()
        self._ensure_workspaces_dir()
    
    def _ensure_workspaces_dir(self) -> None:
        """Ensure workspaces directory exists"""
        Path(self.WORKSPACES_DIR).mkdir(exist_ok=True)
    
    def create_new_project(
        self,
        name: str,
        client: str = "",
        description: str = "",
        status: str = "Pre-Implementation"
    ) -> Tuple[bool, str, Optional[ActiveProject]]:
        """
        Create a new project workspace.
        
        Args:
            name: Project name
            client: Client name
            description: Project description
            status: Project status
            
        Returns:
            Tuple of (success, message, active_project)
        """
        try:
            # Generate UUID
            project_uuid = str(uuid_lib.uuid4())
            
            # Create file path
            file_name = f"{name}.irp"
            file_path = Path(self.WORKSPACES_DIR) / file_name
            
            # Check if file already exists
            if file_path.exists():
                return False, f"Project '{name}' already exists", None
            
            # Create database
            engine = get_engine(str(file_path))
            init_db(engine)
            session = get_session(engine)
            
            # Create project metadata
            now = datetime.utcnow()
            metadata = ProjectMetadata(
                project_uuid=project_uuid,
                project_name=name,
                client_name=client,
                description=description,
                status=status,
                registry_version=self.APP_VERSION,
                created_at=now,
                updated_at=now
            )
            session.add(metadata)
            session.commit()
            session.close()
            
            # Create registry entry
            registry_entry = ProjectRegistryEntry(
                uuid=project_uuid,
                name=name,
                client=client,
                description=description,
                status=status,
                created_at=now.isoformat(),
                last_modified=now.isoformat(),
                last_opened=now.isoformat(),
                file_path=str(file_path.absolute()),
                app_version=self.APP_VERSION
            )
            self.registry.add_project(registry_entry)
            
            # Create active project
            active_project = ActiveProject(
                uuid=project_uuid,
                name=name,
                client=client,
                description=description,
                status=status,
                file_path=str(file_path.absolute()),
                created_at=now,
                last_modified=now,
                last_opened=now,
                version=self.APP_VERSION
            )
            
            # Set as active project
            ProjectContext.set_active_project(active_project)
            
            return True, f"Project '{name}' created successfully", active_project
            
        except Exception as e:
            return False, f"Error creating project: {str(e)}", None
    
    def open_project(self, project_uuid: str) -> Tuple[bool, str, Optional[ActiveProject]]:
        """
        Open an existing project.
        
        Args:
            project_uuid: Project UUID
            
        Returns:
            Tuple of (success, message, active_project)
        """
        try:
            # Get project from registry
            registry_entry = self.registry.get_project(project_uuid)
            if not registry_entry:
                return False, "Project not found in registry", None
            
            # Check if file exists
            file_path = Path(registry_entry.file_path)
            if not file_path.exists():
                return False, f"Project file not found: {file_path}", None
            
            # Load project metadata from database
            engine = get_engine(str(file_path))
            session = get_session(engine)
            metadata = session.query(ProjectMetadata).first()
            
            if not metadata:
                session.close()
                return False, "Project metadata not found in database", None
            
            # Update registry last opened
            self.registry.update_last_opened(project_uuid)
            
            # Create active project
            now = datetime.utcnow()
            active_project = ActiveProject(
                uuid=project_uuid,
                name=metadata.project_name,
                client=metadata.client_name or "",
                description=metadata.description or "",
                status=metadata.status or "Pre-Implementation",
                file_path=str(file_path.absolute()),
                created_at=metadata.created_at or now,
                last_modified=metadata.updated_at or now,
                last_opened=now,
                version=metadata.registry_version or self.APP_VERSION
            )
            
            session.close()
            
            # Set as active project
            ProjectContext.set_active_project(active_project)
            
            return True, f"Project '{active_project.name}' opened successfully", active_project
            
        except Exception as e:
            return False, f"Error opening project: {str(e)}", None
    
    def save_project(self) -> Tuple[bool, str]:
        """
        Save the current project.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            active_project = ProjectContext.get_active_project()
            if not active_project:
                return False, "No active project to save"
            
            # Update last modified
            now = datetime.utcnow()
            active_project.last_modified = now
            
            # Update registry
            self.registry.update_project(
                active_project.uuid,
                name=active_project.name,
                client=active_project.client,
                description=active_project.description,
                status=active_project.status,
                last_modified=now.isoformat()
            )
            
            # Update project metadata in database
            engine = get_engine(active_project.file_path)
            session = get_session(engine)
            metadata = session.query(ProjectMetadata).first()
            
            if metadata:
                metadata.project_name = active_project.name
                metadata.client_name = active_project.client
                metadata.description = active_project.description
                metadata.status = active_project.status
                metadata.updated_at = now
                session.commit()
            
            session.close()
            
            # Update context
            ProjectContext.set_active_project(active_project)
            
            return True, f"Project '{active_project.name}' saved successfully"
            
        except Exception as e:
            return False, f"Error saving project: {str(e)}"
    
    def save_project_as(self, new_name: str) -> Tuple[bool, str, Optional[ActiveProject]]:
        """
        Save the current project with a new name.
        
        Args:
            new_name: New project name
            
        Returns:
            Tuple of (success, message, active_project)
        """
        try:
            active_project = ProjectContext.get_active_project()
            if not active_project:
                return False, "No active project to save", None
            
            # Create new file path
            new_file_name = f"{new_name}.irp"
            new_file_path = Path(self.WORKSPACES_DIR) / new_file_name
            
            # Check if file already exists
            if new_file_path.exists():
                return False, f"Project '{new_name}' already exists", None
            
            # Copy database file
            shutil.copy2(active_project.file_path, new_file_path)
            
            # Generate new UUID
            new_uuid = str(uuid_lib.uuid4())
            
            # Update project metadata in new database
            engine = get_engine(str(new_file_path))
            session = get_session(engine)
            metadata = session.query(ProjectMetadata).first()
            
            if metadata:
                metadata.project_name = new_name
                metadata.updated_at = datetime.utcnow()
                session.commit()
            
            session.close()
            
            # Create new registry entry
            now = datetime.utcnow()
            registry_entry = ProjectRegistryEntry(
                uuid=new_uuid,
                name=new_name,
                client=active_project.client,
                description=active_project.description,
                status=active_project.status,
                created_at=now.isoformat(),
                last_modified=now.isoformat(),
                last_opened=now.isoformat(),
                file_path=str(new_file_path.absolute()),
                app_version=self.APP_VERSION
            )
            self.registry.add_project(registry_entry)
            
            # Create new active project
            new_active_project = ActiveProject(
                uuid=new_uuid,
                name=new_name,
                client=active_project.client,
                description=active_project.description,
                status=active_project.status,
                file_path=str(new_file_path.absolute()),
                created_at=now,
                last_modified=now,
                last_opened=now,
                version=self.APP_VERSION
            )
            
            # Set as active project
            ProjectContext.set_active_project(new_active_project)
            
            return True, f"Project saved as '{new_name}'", new_active_project
            
        except Exception as e:
            return False, f"Error saving project as: {str(e)}", None
    
    def close_project(self) -> Tuple[bool, str]:
        """
        Close the current project.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            active_project = ProjectContext.get_active_project()
            if not active_project:
                return False, "No active project to close"
            
            project_name = active_project.name
            
            # Save before closing
            self.save_project()
            
            # Clear active project
            ProjectContext.clear_active_project()
            
            return True, f"Project '{project_name}' closed successfully"
            
        except Exception as e:
            return False, f"Error closing project: {str(e)}"
    
    def get_recent_projects(self, limit: int = 10) -> list:
        """
        Get recent projects.
        
        Args:
            limit: Maximum number of projects to return
            
        Returns:
            List of recent projects
        """
        return self.registry.list_recent_projects(limit)
    
    def discover_projects(self) -> int:
        """
        Discover projects in workspaces directory.
        
        Returns:
            Number of projects discovered
        """
        return self.registry.discover_projects(self.WORKSPACES_DIR)
