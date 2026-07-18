"""
Test script for WPP-012H - Database Schema Initialization Verification

Verifies that schema creation works correctly and all required tables are created.
"""
import os
import sys
from pathlib import Path

def test_schema_creation():
    """Test that schema is created correctly"""
    print("\n" + "="*60)
    print("WPP-012H: Database Schema Initialization Verification")
    print("="*60 + "\n")
    
    # Import after path setup
    from database.schema import init_db, Base
    from sqlalchemy import inspect
    
    # Create test database
    test_db_path = "test_schema_verification.db"
    
    # Clean up any existing test database
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
        print(f"[CLEANUP] Removed existing test database\n")
    
    try:
        print("[TEST] Creating database schema...")
        print(f"[TEST] Database path: {test_db_path}\n")
        
        # Initialize database
        engine = init_db(test_db_path)
        
        print("\n[TEST] Verifying database file...")
        if os.path.exists(test_db_path):
            file_size = os.path.getsize(test_db_path)
            print(f"[TEST] ✓ Database file exists: {file_size} bytes")
        else:
            print(f"[TEST] ✗ Database file does not exist")
            return False
        
        print("\n[TEST] Inspecting schema...")
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"[TEST] Found {len(tables)} tables:")
        for table in sorted(tables):
            print(f"[TEST]   - {table}")
        
        # Verify required tables
        required_tables = {
            'project_metadata',
            'impacts',
            'stakeholder_groups',
            'organization_units',
            'business_processes',
            'systems',
            'policies',
            'settings'
        }
        
        print(f"\n[TEST] Checking required tables:")
        all_present = True
        for table in sorted(required_tables):
            if table in tables:
                print(f"[TEST]   ✓ {table}")
            else:
                print(f"[TEST]   ✗ {table} - MISSING")
                all_present = False
        
        # Verify Base.metadata
        print(f"\n[TEST] Verifying Base.metadata:")
        print(f"[TEST]   Tables in metadata: {len(Base.metadata.tables)}")
        for table_name in sorted(Base.metadata.tables.keys()):
            print(f"[TEST]     - {table_name}")
        
        # Check column details for key tables
        print(f"\n[TEST] Checking table structures:")
        
        for table_name in ['project_metadata', 'impacts', 'stakeholder_groups']:
            if table_name in tables:
                columns = inspector.get_columns(table_name)
                print(f"[TEST]   {table_name}: {len(columns)} columns")
                for col in columns:
                    print(f"[TEST]     - {col['name']} ({col['type']})")
        
        print("\n" + "="*60)
        if all_present:
            print("✓ SCHEMA VERIFICATION PASSED")
            print("  All required tables created successfully")
        else:
            print("✗ SCHEMA VERIFICATION FAILED")
            print("  Some required tables are missing")
        print("="*60 + "\n")
        
        return all_present
        
    except Exception as e:
        import traceback
        print(f"\n[ERROR] Schema verification failed:")
        print(traceback.format_exc())
        return False
        
    finally:
        # Clean up test database
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
            print(f"[CLEANUP] Removed test database\n")

if __name__ == "__main__":
    success = test_schema_creation()
    sys.exit(0 if success else 1)
