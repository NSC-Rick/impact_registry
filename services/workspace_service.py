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
from services.workspace_validator import WorkspaceValidator
from services.workspace_initializer import WorkspaceInitializer
from config import Config


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
    
    def __init__(self):
        """Initialize workspace service"""
        self.registry = ProjectRegistry()
        Config.ensure_workspace_exists()
    
    @property
    def WORKSPACES_DIR(self) -> str:
        """Get workspace directory from config"""
        return Config.WORKSPACE_ROOT
    
    @property
    def APP_VERSION(self) -> str:
        """Get app version from config"""
        return Config.APP_VERSION
    
    def create_new_project(
        self,
        name: str,
        client: str = "",
        description: str = "",
        status: str = "Pre-Implementation",
        starter_library_id: Optional[str] = None
    ) -> Tuple[bool, str, Optional[ActiveProject]]:
        """
        Create a new project workspace using the initialization orchestrator.
        
        Args:
            name: Project name
            client: Client name
            description: Project description
            status: Project status
            starter_library_id: Optional starter library to import
            
        Returns:
            Tuple of (success, message, active_project)
        """
        # Delegate to workspace initializer orchestrator
        initializer = WorkspaceInitializer(self.WORKSPACES_DIR)
        return initializer.initialize(
            name=name,
            client=client,
            description=description,
            status=status,
            starter_library_id=starter_library_id
        )
    
    def _legacy_create_new_project(
        self,
        name: str,
        client: str = "",
        description: str = "",
        status: str = "Pre-Implementation",
        starter_library_id: Optional[str] = None
    ) -> Tuple[bool, str, Optional[ActiveProject]]:
        """
        Legacy create method - replaced by WorkspaceInitializer.
        Kept for reference only.
        """
        try:
            print(f"\n=== Creating Project: {name} ===")
            
            # Generate UUID
            project_uuid = str(uuid_lib.uuid4())
            print(f"Generated UUID: {project_uuid}")
            
            # Create file path
            file_name = f"{name}.irp"
            file_path = Path(self.WORKSPACES_DIR) / file_name
            print(f"[WORKSPACE] Project file path: {file_path}")
            print(f"[WORKSPACE] Absolute path: {file_path.absolute()}")
            
            # Check if file already exists
            if file_path.exists():
                print(f"[ERROR] Project file already exists")
                return False, f"Project '{name}' already exists", None
            
            # Ensure workspace directory exists
            workspace_dir = file_path.parent
            print(f"[WORKSPACE] Ensuring directory exists: {workspace_dir.absolute()}")
            workspace_dir.mkdir(parents=True, exist_ok=True)
            
            if not workspace_dir.exists():
                print(f"[ERROR] Failed to create workspace directory")
                return False, "Failed to create workspace directory", None
            
            print(f"[WORKSPACE] Directory confirmed: {workspace_dir.absolute()}")
            
            # Create database
            print("[WORKSPACE] Initializing database...")
            engine = init_db(str(file_path))
            
            # Verify database file was created
            if not file_path.exists():
                print(f"[ERROR] Database file was not created: {file_path}")
                return False, "Database file creation failed", None
            
            print(f"[WORKSPACE] Database file created: {file_path.absolute()}")
            print(f"[WORKSPACE] Database file size: {file_path.stat().st_size} bytes")
            
            # Create session
            print("[WORKSPACE] Creating database session...")
            session = get_session(engine)
            print("[WORKSPACE] Database initialized successfully")
            
            # Create project metadata
            print("Creating project metadata...")
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
            print("Project metadata created")
            
            # Apply starter library if specified
            if starter_library_id:
                print(f"Loading starter library: {starter_library_id}")
                from libraries.starter_library_service import StarterLibraryService
                library_service = StarterLibraryService()
                library = library_service.load_library(starter_library_id)
                
                if library:
                    print(f"Applying library '{library.name}' to project...")
                    success, message, stats = library_service.apply_library_to_project(library, session)
                    if not success:
                        print(f"ERROR: Library application failed: {message}")
                        session.close()
                        # Clean up created file
                        if file_path.exists():
                            file_path.unlink()
                        return False, f"Error applying library: {message}", None
                    print(f"Library applied successfully: {stats}")
                else:
                    print(f"WARNING: Library '{starter_library_id}' not found")
            
            session.close()
            print("Database session closed")
            
            # Validate workspace
            print("Validating workspace...")
            validator = WorkspaceValidator()
            is_valid, validation_message, missing = validator.validate_workspace(str(file_path))
            
            if not is_valid:
                print(f"ERROR: Workspace validation failed: {validation_message}")
                print(f"Missing components: {missing}")
                # Clean up failed workspace
                if file_path.exists():
                    file_path.unlink()
                    print("Cleaned up invalid workspace")
                return False, f"Workspace validation failed: {validation_message}", None
            
            print(f"✓ Workspace validation passed: {validation_message}")
            
            # Get workspace stats
            stats = validator.get_workspace_stats(str(file_path))
            print(f"Workspace stats: {stats}")
            
            # Create registry entry
            print("Registering project...")
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
            print("Project registered in registry")
            
            # Create active project
            print("Opening workspace...")
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
            print(f"Project '{name}' created and opened successfully")
            print("=== Project Creation Complete ===\n")
            
            return True, f"Project '{name}' created successfully", active_project
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Project creation error:\n{error_details}")  # Log for developers
            
            # User-friendly message
            user_message = (
                "Project could not be created.\n\n"
                "The workspace initialization encountered an unexpected error.\n\n"
                "No project data has been saved.\n\n"
                f"Technical details: {str(e)}"
            )
            return False, user_message, None
    
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
            
            # Validate workspace before opening
            validator = WorkspaceValidator()
            is_valid, validation_message, missing = validator.validate_workspace(str(file_path))
            
            if not is_valid:
                error_msg = (
                    f"Workspace validation failed: {validation_message}\n\n"
                    f"This project workspace may be corrupted or incomplete.\n\n"
                    f"Missing components: {', '.join(missing) if missing else 'Unknown'}"
                )
                return False, error_msg, None
            
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
