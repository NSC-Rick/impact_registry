"""
Debug script to trace database file creation

Investigates why workspaces/test.irp is not being created.
"""
import os
from pathlib import Path
from sqlalchemy import create_engine, inspect

def debug_database_creation():
    """Debug database file creation step by step"""
    
    print("\n" + "="*60)
    print("DATABASE CREATION DEBUG")
    print("="*60 + "\n")
    
    # Step 1: Check current working directory
    cwd = os.getcwd()
    print(f"[DEBUG] Current working directory:")
    print(f"        {cwd}\n")
    
    # Step 2: Define workspace directory
    workspaces_dir = "workspaces"
    print(f"[DEBUG] Workspace directory (relative): {workspaces_dir}")
    
    # Step 3: Check if workspace directory exists
    workspace_path = Path(workspaces_dir)
    print(f"[DEBUG] Workspace path object: {workspace_path}")
    print(f"[DEBUG] Workspace absolute path: {workspace_path.absolute()}")
    print(f"[DEBUG] Workspace exists: {workspace_path.exists()}")
    
    if not workspace_path.exists():
        print(f"[DEBUG] Creating workspace directory...")
        workspace_path.mkdir(parents=True, exist_ok=True)
        print(f"[DEBUG] Directory created: {workspace_path.exists()}")
    
    # Step 4: Check directory is writable
    print(f"\n[DEBUG] Testing write permissions...")
    test_file = workspace_path / "test_write.txt"
    try:
        test_file.write_text("test")
        print(f"[DEBUG] ✓ Directory is writable")
        test_file.unlink()
        print(f"[DEBUG] ✓ Test file removed")
    except Exception as e:
        print(f"[DEBUG] ✗ Write failed: {e}")
        return False
    
    # Step 5: Define database file path
    db_filename = "test.irp"
    db_file_path = workspace_path / db_filename
    
    print(f"\n[DEBUG] Database file path (relative): {db_file_path}")
    print(f"[DEBUG] Database file path (absolute): {db_file_path.absolute()}")
    print(f"[DEBUG] Database file exists: {db_file_path.exists()}")
    
    # Step 6: Create SQLAlchemy engine
    print(f"\n[DEBUG] Creating SQLAlchemy engine...")
    
    # Test different path formats
    path_variants = [
        str(db_file_path),
        str(db_file_path.absolute()),
        f"{workspaces_dir}/{db_filename}",
        f"workspaces\\{db_filename}",
    ]
    
    for i, path_variant in enumerate(path_variants, 1):
        print(f"\n[DEBUG] Variant {i}: {path_variant}")
        
        # Clean up any existing file
        if db_file_path.exists():
            db_file_path.unlink()
            print(f"[DEBUG]   Cleaned up existing file")
        
        try:
            # Create engine
            connection_string = f'sqlite:///{path_variant}'
            print(f"[DEBUG]   Connection string: {connection_string}")
            
            engine = create_engine(connection_string, echo=False)
            print(f"[DEBUG]   ✓ Engine created")
            
            # Try to connect
            with engine.connect() as conn:
                print(f"[DEBUG]   ✓ Connection successful")
            
            # Check if file was created
            print(f"[DEBUG]   File exists after connect: {db_file_path.exists()}")
            
            if db_file_path.exists():
                file_size = db_file_path.stat().st_size
                print(f"[DEBUG]   ✓ File created: {file_size} bytes")
                print(f"[DEBUG]   ✓ File location: {db_file_path.absolute()}")
                
                # Try creating a table
                from database.schema import Base
                print(f"[DEBUG]   Creating schema...")
                Base.metadata.create_all(engine)
                
                # Inspect tables
                inspector = inspect(engine)
                tables = inspector.get_table_names()
                print(f"[DEBUG]   ✓ Schema created: {len(tables)} tables")
                
                # Check file size after schema
                new_size = db_file_path.stat().st_size
                print(f"[DEBUG]   ✓ File size after schema: {new_size} bytes")
                
                print(f"\n[SUCCESS] Variant {i} WORKS!")
                print(f"          Use path format: {path_variant}")
                
                # Clean up
                db_file_path.unlink()
                return True
            else:
                print(f"[DEBUG]   ✗ File NOT created")
                
                # Check if it was created elsewhere
                print(f"[DEBUG]   Searching for database file...")
                for root, dirs, files in os.walk('.'):
                    for file in files:
                        if file == db_filename:
                            found_path = os.path.join(root, file)
                            print(f"[DEBUG]   Found at: {os.path.abspath(found_path)}")
                
        except Exception as e:
            print(f"[DEBUG]   ✗ Failed: {e}")
    
    print(f"\n[FAILED] No variant successfully created the database file")
    return False

if __name__ == "__main__":
    import sys
    success = debug_database_creation()
    sys.exit(0 if success else 1)
