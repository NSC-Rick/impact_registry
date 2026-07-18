"""
Workspace Initialization Orchestrator

Authoritative service for complete project workspace initialization.
Ensures every new project contains a complete, validated Change Impact Registry.
"""
import time
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional, Dict
import uuid as uuid_lib

from database.schema import init_db, get_engine, get_session, ProjectMetadata
from services.workspace_validator import WorkspaceValidator
from services.project_context import ProjectContext, ActiveProject
from services.project_registry import ProjectRegistry, ProjectRegistryEntry


class WorkspaceInitializer:
    """
    Orchestrates complete workspace initialization.
    
    Ensures every new project is fully initialized and validated
    before being opened.
    """
    
    APP_VERSION = "1.0.0"
    
    def __init__(self, workspaces_dir: str = "workspaces"):
        """
        Initialize the workspace initializer.
        
        Args:
            workspaces_dir: Base directory for project workspaces
        """
        self.workspaces_dir = workspaces_dir
        self.validator = WorkspaceValidator()
        self.registry = ProjectRegistry()
        
        # Ensure base directory exists
        Path(self.workspaces_dir).mkdir(parents=True, exist_ok=True)
    
    def initialize(
        self,
        name: str,
        client: str = "",
        description: str = "",
        status: str = "Pre-Implementation",
        starter_library_id: Optional[str] = None
    ) -> Tuple[bool, str, Optional[ActiveProject]]:
        """
        Complete workspace initialization pipeline.
        
        Executes all initialization steps in order:
        1. Create workspace directory
        2. Create SQLite database
        3. Create SQLAlchemy engine
        4. Create session
        5. Create database schema
        6. Verify required tables
        7. Insert project metadata
        8. Import starter library
        9. Verify imported record counts
        10. Register project
        11. Validate workspace
        12. Open project
        
        Args:
            name: Project name
            client: Client name
            description: Project description
            status: Project status
            starter_library_id: Optional starter library to import
            
        Returns:
            Tuple of (success, message, active_project)
        """
        start_time = time.time()
        file_path = None
        
        try:
            print("\n" + "="*60)
            print(f"WORKSPACE INITIALIZATION: {name}")
            print("="*60)
            
            # Step 1: Generate project UUID
            project_uuid = str(uuid_lib.uuid4())
            print(f"\n[STEP 1] Generated UUID: {project_uuid}")
            
            # Step 2: Create workspace directory and file path
            file_name = f"{name}.irp"
            file_path = Path(self.workspaces_dir) / file_name
            print(f"\n[STEP 2] Workspace path: {file_path.absolute()}")
            
            # Check if already exists
            if file_path.exists():
                print(f"[ERROR] Project already exists")
                return False, f"Project '{name}' already exists", None
            
            # Ensure directory exists
            workspace_dir = file_path.parent
            workspace_dir.mkdir(parents=True, exist_ok=True)
            
            if not workspace_dir.exists():
                print(f"[ERROR] Failed to create workspace directory")
                return False, "Failed to create workspace directory", None
            
            print(f"[STEP 2] ✓ Directory created: {workspace_dir.absolute()}")
            
            # Step 3: Create SQLite database and engine
            print(f"\n[STEP 3] Creating database...")
            engine = init_db(str(file_path))
            
            # Verify database file exists
            if not file_path.exists():
                print(f"[ERROR] Database file not created")
                return False, "Database file creation failed", None
            
            file_size = file_path.stat().st_size
            print(f"[STEP 3] ✓ Database created: {file_size} bytes")
            
            # Step 4: Create session
            print(f"\n[STEP 4] Creating database session...")
            session = get_session(engine)
            print(f"[STEP 4] ✓ Session created")
            
            # Step 5: Verify schema was created
            print(f"\n[STEP 5] Verifying schema...")
            schema_valid, schema_msg = self.validator.verify_schema_created(str(file_path))
            
            if not schema_valid:
                print(f"[ERROR] Schema verification failed: {schema_msg}")
                session.close()
                if file_path.exists():
                    file_path.unlink()
                return False, f"Schema verification failed: {schema_msg}", None
            
            print(f"[STEP 5] ✓ {schema_msg}")
            
            # Step 6: Insert project metadata
            print(f"\n[STEP 6] Creating project metadata...")
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
            print(f"[STEP 6] ✓ Project metadata inserted")
            
            # Step 7: Import starter library (if specified)
            library_stats = {}
            if starter_library_id:
                print(f"\n[STEP 7] Importing starter library: {starter_library_id}")
                success, message, library_stats = self._import_starter_library(
                    starter_library_id, session
                )
                
                if not success:
                    print(f"[ERROR] Starter library import failed: {message}")
                    session.close()
                    if file_path.exists():
                        file_path.unlink()
                    return False, f"Starter library import failed: {message}", None
                
                print(f"[STEP 7] ✓ Starter library imported")
                self._log_library_stats(library_stats)
            else:
                print(f"\n[STEP 7] No starter library selected (blank project)")
            
            # Close session before validation
            session.close()
            print(f"\n[STEP 8] Database session closed")
            
            # Step 8: Validate complete workspace
            print(f"\n[STEP 9] Validating workspace...")
            is_valid, validation_msg, missing = self.validator.validate_workspace(str(file_path))
            
            if not is_valid:
                print(f"[ERROR] Workspace validation failed: {validation_msg}")
                print(f"[ERROR] Missing: {missing}")
                if file_path.exists():
                    file_path.unlink()
                return False, f"Workspace validation failed: {validation_msg}", None
            
            print(f"[STEP 9] ✓ Workspace validation passed")
            
            # Get final workspace stats
            final_stats = self.validator.get_workspace_stats(str(file_path))
            self._log_workspace_stats(final_stats)
            
            # Step 9: Register project
            print(f"\n[STEP 10] Registering project...")
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
            print(f"[STEP 10] ✓ Project registered")
            
            # Step 10: Create and activate project
            print(f"\n[STEP 11] Opening project...")
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
            
            ProjectContext.set_active_project(active_project)
            print(f"[STEP 11] ✓ Project activated")
            
            # Calculate initialization time
            duration = time.time() - start_time
            
            print("\n" + "="*60)
            print(f"✓ INITIALIZATION COMPLETE")
            print(f"  Project: {name}")
            print(f"  Duration: {duration:.2f} seconds")
            print("="*60 + "\n")
            
            return True, f"Project '{name}' created successfully", active_project
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"\n[ERROR] Initialization failed:\n{error_details}")
            
            # Cleanup on failure
            if file_path and file_path.exists():
                try:
                    file_path.unlink()
                    print(f"[CLEANUP] Removed incomplete workspace: {file_path}")
                except Exception as cleanup_error:
                    print(f"[CLEANUP ERROR] Failed to remove workspace: {cleanup_error}")
            
            duration = time.time() - start_time
            print(f"\n[FAILED] Initialization failed after {duration:.2f} seconds\n")
            
            user_message = (
                "Project workspace initialization failed.\n\n"
                "The workspace has been cleaned up.\n\n"
                "No incomplete project data remains.\n\n"
                f"Technical details: {str(e)}"
            )
            return False, user_message, None
    
    def _import_starter_library(self, library_id: str, session) -> Tuple[bool, str, Dict]:
        """
        Import a starter library into the project.
        
        Args:
            library_id: Starter library identifier
            session: Database session
            
        Returns:
            Tuple of (success, message, stats)
        """
        try:
            from libraries.starter_library_service import StarterLibraryService
            
            library_service = StarterLibraryService()
            library = library_service.load_library(library_id)
            
            if not library:
                return False, f"Starter library '{library_id}' not found", {}
            
            print(f"  Loading library: {library.name}")
            success, message, stats = library_service.apply_library_to_project(library, session)
            
            return success, message, stats
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"  Library import error:\n{error_details}")
            return False, f"Error importing library: {str(e)}", {}
    
    def _log_library_stats(self, stats: Dict) -> None:
        """Log starter library import statistics"""
        print(f"\n  Library Import Statistics:")
        print(f"    Stakeholder Groups: {stats.get('stakeholder_groups', 0)}")
        print(f"    Organization Units: {stats.get('organization_units', 0)}")
        print(f"    Business Processes: {stats.get('business_processes', 0)}")
        print(f"    Systems: {stats.get('systems', 0)}")
        print(f"    Policies: {stats.get('policies', 0)}")
        print(f"    Change Impacts: {stats.get('impacts', 0)}")
    
    def _log_workspace_stats(self, stats: Dict) -> None:
        """Log final workspace statistics"""
        print(f"\n  Final Workspace Statistics:")
        print(f"    Stakeholder Groups: {stats.get('stakeholder_groups', 0)}")
        print(f"    Organization Units: {stats.get('organization_units', 0)}")
        print(f"    Business Processes: {stats.get('business_processes', 0)}")
        print(f"    Systems: {stats.get('systems', 0)}")
        print(f"    Policies: {stats.get('policies', 0)}")
        print(f"    Change Impacts: {stats.get('impacts', 0)}")
