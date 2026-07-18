"""
Test script for workspace creation pipeline
Tests blank project and starter library project creation
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from services.workspace_service import WorkspaceService

def test_blank_project():
    """Test creating a blank project"""
    print("\n" + "="*60)
    print("TEST 1: Blank Project Creation")
    print("="*60)
    
    workspace = WorkspaceService()
    
    # Clean up any existing test project
    test_project_path = Path("workspaces/Test_Blank_Project.irp")
    if test_project_path.exists():
        test_project_path.unlink()
        print("Cleaned up existing test project")
    
    success, message, active_project = workspace.create_new_project(
        name="Test Blank Project",
        client="Test Client",
        description="Test blank project creation",
        status="Pre-Implementation",
        starter_library_id=None
    )
    
    if success:
        print(f"\n✅ SUCCESS: {message}")
        print(f"   Project UUID: {active_project.uuid}")
        print(f"   Project Path: {active_project.file_path}")
        return True
    else:
        print(f"\n❌ FAILED: {message}")
        return False

def test_erp_library():
    """Test creating a project with ERP starter library"""
    print("\n" + "="*60)
    print("TEST 2: ERP Starter Library Project Creation")
    print("="*60)
    
    workspace = WorkspaceService()
    
    # Clean up any existing test project
    test_project_path = Path("workspaces/Test_ERP_Project.irp")
    if test_project_path.exists():
        test_project_path.unlink()
        print("Cleaned up existing test project")
    
    success, message, active_project = workspace.create_new_project(
        name="Test ERP Project",
        client="Test Client",
        description="Test ERP starter library",
        status="Pre-Implementation",
        starter_library_id="erp"
    )
    
    if success:
        print(f"\n✅ SUCCESS: {message}")
        print(f"   Project UUID: {active_project.uuid}")
        print(f"   Project Path: {active_project.file_path}")
        return True
    else:
        print(f"\n❌ FAILED: {message}")
        return False

def test_vms_library():
    """Test creating a project with VMS/MSP starter library"""
    print("\n" + "="*60)
    print("TEST 3: VMS/MSP Starter Library Project Creation")
    print("="*60)
    
    workspace = WorkspaceService()
    
    # Clean up any existing test project
    test_project_path = Path("workspaces/Test_VMS_Project.irp")
    if test_project_path.exists():
        test_project_path.unlink()
        print("Cleaned up existing test project")
    
    success, message, active_project = workspace.create_new_project(
        name="Test VMS Project",
        client="Test Client",
        description="Test VMS/MSP starter library",
        status="Pre-Implementation",
        starter_library_id="vms_msp"
    )
    
    if success:
        print(f"\n✅ SUCCESS: {message}")
        print(f"   Project UUID: {active_project.uuid}")
        print(f"   Project Path: {active_project.file_path}")
        return True
    else:
        print(f"\n❌ FAILED: {message}")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("WORKSPACE CREATION PIPELINE TESTS")
    print("="*60)
    
    results = []
    
    # Test 1: Blank Project
    results.append(("Blank Project", test_blank_project()))
    
    # Test 2: ERP Library
    results.append(("ERP Library", test_erp_library()))
    
    # Test 3: VMS Library
    results.append(("VMS/MSP Library", test_vms_library()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("="*60 + "\n")
    
    sys.exit(0 if all_passed else 1)
