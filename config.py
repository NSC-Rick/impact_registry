"""
Application Configuration

Centralized configuration for Impact Registry.
Handles environment-specific settings including workspace storage paths.
"""

import os
from pathlib import Path


class Config:
    """Application configuration with environment variable support"""
    
    # Workspace Storage Configuration
    # ================================
    
    # Primary workspace directory
    # - Local Development: ./workspaces
    # - Render Production: /var/data/workspaces (persistent disk mount)
    WORKSPACE_ROOT = os.environ.get("WORKSPACE_ROOT", "workspaces")
    
    # Application Metadata
    # ====================
    APP_VERSION = "1.0.0"
    APP_NAME = "Impact Registry"
    
    # Database Configuration
    # ======================
    DATABASE_EXTENSION = ".irp"  # Impact Registry Project
    
    # Registry Configuration
    # ======================
    REGISTRY_FILENAME = "project_registry.json"
    
    @classmethod
    def get_workspace_path(cls) -> Path:
        """
        Get the workspace directory path.
        
        Returns:
            Path object for workspace directory
        """
        return Path(cls.WORKSPACE_ROOT)
    
    @classmethod
    def get_registry_path(cls) -> Path:
        """
        Get the project registry file path.
        
        Returns:
            Path object for registry file
        """
        return cls.get_workspace_path() / cls.REGISTRY_FILENAME
    
    @classmethod
    def ensure_workspace_exists(cls) -> None:
        """
        Ensure workspace directory exists.
        Creates directory if it doesn't exist.
        """
        workspace_path = cls.get_workspace_path()
        workspace_path.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate_workspace(cls) -> tuple[bool, str]:
        """
        Validate workspace directory is accessible and writable.
        
        Returns:
            Tuple of (is_valid, message)
        """
        workspace_path = cls.get_workspace_path()
        
        # Check if directory exists
        if not workspace_path.exists():
            try:
                workspace_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                return False, f"Cannot create workspace directory: {e}"
        
        # Check if directory is readable
        if not os.access(workspace_path, os.R_OK):
            return False, f"Workspace directory is not readable: {workspace_path}"
        
        # Check if directory is writable
        if not os.access(workspace_path, os.W_OK):
            return False, f"Workspace directory is not writable: {workspace_path}"
        
        return True, "Workspace directory is accessible"
    
    @classmethod
    def get_startup_info(cls) -> dict:
        """
        Get startup configuration information.
        
        Returns:
            Dictionary with startup configuration details
        """
        workspace_path = cls.get_workspace_path()
        is_valid, message = cls.validate_workspace()
        
        # Count existing projects
        project_count = 0
        if workspace_path.exists():
            project_count = len(list(workspace_path.glob(f"*{cls.DATABASE_EXTENSION}")))
        
        return {
            "app_name": cls.APP_NAME,
            "app_version": cls.APP_VERSION,
            "workspace_root": str(workspace_path.absolute()),
            "workspace_valid": is_valid,
            "workspace_message": message,
            "project_count": project_count,
            "database_extension": cls.DATABASE_EXTENSION,
            "is_production": cls.WORKSPACE_ROOT != "workspaces"
        }
    
    @classmethod
    def print_startup_diagnostics(cls) -> None:
        """Print startup diagnostics to console"""
        info = cls.get_startup_info()
        
        print("\n" + "=" * 60)
        print(f"{info['app_name']} Startup")
        print("=" * 60)
        print()
        print(f"Version: {info['app_version']}")
        print(f"Environment: {'Production' if info['is_production'] else 'Development'}")
        print()
        print(f"Workspace Root:")
        print(f"  {info['workspace_root']}")
        print()
        print(f"Persistent Storage:")
        if info['workspace_valid']:
            print(f"  ✓ Available")
        else:
            print(f"  ✗ Unavailable - {info['workspace_message']}")
        print()
        print(f"Projects Found: {info['project_count']}")
        print()
        print("=" * 60)
        print()
