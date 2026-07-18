"""
Workspace Validator

Validates that a project workspace is fully initialized and operational.
Ensures database schema exists and required tables are present.
"""
from pathlib import Path
from typing import Tuple, List
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError

from database.schema import (
    get_engine, get_session, 
    ProjectMetadata, StakeholderGroup, OrganizationUnit,
    BusinessProcess, System, Policy, Impact
)


class WorkspaceValidator:
    """Validates project workspace initialization"""
    
    # Required tables for a valid workspace
    REQUIRED_TABLES = [
        'project_metadata',
        'stakeholder_groups',
        'organization_units',
        'business_processes',
        'systems',
        'policies',
        'impacts',
        'impact_stakeholder_groups',
        'impact_organization_units',
        'impact_business_processes',
        'impact_systems',
        'impact_policies'
    ]
    
    def __init__(self):
        """Initialize validator"""
        pass
    
    def validate_workspace(self, workspace_path: str) -> Tuple[bool, str, List[str]]:
        """
        Validate a project workspace.
        
        Args:
            workspace_path: Path to the workspace database file
            
        Returns:
            Tuple of (is_valid, message, missing_components)
        """
        missing = []
        
        try:
            # Check 1: Database file exists
            db_path = Path(workspace_path)
            if not db_path.exists():
                return False, "Database file does not exist", ["database_file"]
            
            print(f"[VALIDATOR] Validating workspace: {workspace_path}")
            
            # Check 2: Database connection succeeds
            try:
                engine = get_engine(workspace_path)
                print("[VALIDATOR] ✓ Database connection successful")
            except Exception as e:
                print(f"[VALIDATOR] ✗ Database connection failed: {e}")
                return False, f"Cannot connect to database: {str(e)}", ["database_connection"]
            
            # Check 3: Schema exists and tables are present
            try:
                inspector = inspect(engine)
                existing_tables = inspector.get_table_names()
                print(f"[VALIDATOR] Found {len(existing_tables)} tables")
                
                for required_table in self.REQUIRED_TABLES:
                    if required_table not in existing_tables:
                        missing.append(required_table)
                        print(f"[VALIDATOR] ✗ Missing table: {required_table}")
                
                if missing:
                    return False, f"Missing {len(missing)} required table(s)", missing
                
                print("[VALIDATOR] ✓ All required tables present")
                
            except Exception as e:
                print(f"[VALIDATOR] ✗ Schema inspection failed: {e}")
                return False, f"Cannot inspect schema: {str(e)}", ["schema_inspection"]
            
            # Check 4: Project metadata exists
            try:
                session = get_session(engine)
                metadata = session.query(ProjectMetadata).first()
                session.close()
                
                if not metadata:
                    print("[VALIDATOR] ✗ Project metadata not found")
                    return False, "Project metadata not found", ["project_metadata"]
                
                print(f"[VALIDATOR] ✓ Project metadata found: {metadata.project_name}")
                
            except Exception as e:
                print(f"[VALIDATOR] ✗ Metadata query failed: {e}")
                return False, f"Cannot query metadata: {str(e)}", ["metadata_query"]
            
            # All checks passed
            print("[VALIDATOR] ✓ Workspace validation PASSED")
            return True, "Workspace is valid", []
            
        except Exception as e:
            print(f"[VALIDATOR] ✗ Validation error: {e}")
            return False, f"Validation error: {str(e)}", ["validation_error"]
    
    def verify_schema_created(self, workspace_path: str) -> Tuple[bool, str]:
        """
        Verify that database schema has been created.
        
        Args:
            workspace_path: Path to the workspace database file
            
        Returns:
            Tuple of (success, message)
        """
        try:
            engine = get_engine(workspace_path)
            inspector = inspect(engine)
            existing_tables = inspector.get_table_names()
            
            if len(existing_tables) == 0:
                return False, "No tables found - schema not created"
            
            missing_tables = [t for t in self.REQUIRED_TABLES if t not in existing_tables]
            
            if missing_tables:
                return False, f"Missing tables: {', '.join(missing_tables)}"
            
            return True, f"Schema verified - {len(existing_tables)} tables present"
            
        except Exception as e:
            return False, f"Schema verification failed: {str(e)}"
    
    def get_workspace_stats(self, workspace_path: str) -> dict:
        """
        Get statistics about workspace content.
        
        Args:
            workspace_path: Path to the workspace database file
            
        Returns:
            Dictionary of statistics
        """
        stats = {
            'stakeholder_groups': 0,
            'organization_units': 0,
            'business_processes': 0,
            'systems': 0,
            'policies': 0,
            'impacts': 0
        }
        
        try:
            engine = get_engine(workspace_path)
            session = get_session(engine)
            
            stats['stakeholder_groups'] = session.query(StakeholderGroup).count()
            stats['organization_units'] = session.query(OrganizationUnit).count()
            stats['business_processes'] = session.query(BusinessProcess).count()
            stats['systems'] = session.query(System).count()
            stats['policies'] = session.query(Policy).count()
            stats['impacts'] = session.query(Impact).count()
            
            session.close()
            
        except Exception as e:
            print(f"[VALIDATOR] Error getting stats: {e}")
        
        return stats
