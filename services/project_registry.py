"""
Project Registry Service

Maintains a persistent registry of all available projects.
Registry survives application restarts and browser refreshes.

Stores:
- Project UUID
- Project Name
- Client
- Description
- Status
- Created Date
- Last Modified
- Last Opened
- File Location
- Application Version
"""

import json
import os
from typing import List, Optional, Dict
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class ProjectRegistryEntry:
    """Project registry entry"""
    uuid: str
    name: str
    client: str
    description: str
    status: str
    created_at: str
    last_modified: str
    last_opened: str
    file_path: str
    app_version: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ProjectRegistryEntry':
        """Create from dictionary"""
        return cls(**data)


class ProjectRegistry:
    """
    Persistent project registry.
    
    Maintains a JSON file containing all available projects.
    Registry persists across application restarts.
    """
    
    REGISTRY_FILE = "project_registry.json"
    APP_VERSION = "1.0.0"
    
    def __init__(self, registry_path: Optional[str] = None):
        """
        Initialize project registry.
        
        Args:
            registry_path: Path to registry file. Defaults to workspaces directory.
        """
        if registry_path is None:
            workspaces_dir = Path("workspaces")
            workspaces_dir.mkdir(exist_ok=True)
            registry_path = workspaces_dir / self.REGISTRY_FILE
        
        self.registry_path = Path(registry_path)
        self._ensure_registry_exists()
    
    def _ensure_registry_exists(self) -> None:
        """Ensure registry file exists"""
        if not self.registry_path.exists():
            self._save_registry([])
    
    def _load_registry(self) -> List[ProjectRegistryEntry]:
        """Load registry from disk"""
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [ProjectRegistryEntry.from_dict(entry) for entry in data]
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_registry(self, entries: List[ProjectRegistryEntry]) -> None:
        """Save registry to disk"""
        data = [entry.to_dict() for entry in entries]
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def add_project(self, entry: ProjectRegistryEntry) -> None:
        """Add a project to the registry"""
        entries = self._load_registry()
        
        # Remove existing entry with same UUID if exists
        entries = [e for e in entries if e.uuid != entry.uuid]
        
        # Add new entry
        entries.append(entry)
        
        self._save_registry(entries)
    
    def update_project(self, uuid: str, **kwargs) -> bool:
        """
        Update a project in the registry.
        
        Args:
            uuid: Project UUID
            **kwargs: Fields to update
            
        Returns:
            True if updated, False if not found
        """
        entries = self._load_registry()
        
        for entry in entries:
            if entry.uuid == uuid:
                for key, value in kwargs.items():
                    if hasattr(entry, key):
                        setattr(entry, key, value)
                
                # Always update last_modified
                entry.last_modified = datetime.utcnow().isoformat()
                
                self._save_registry(entries)
                return True
        
        return False
    
    def get_project(self, uuid: str) -> Optional[ProjectRegistryEntry]:
        """Get a project by UUID"""
        entries = self._load_registry()
        for entry in entries:
            if entry.uuid == uuid:
                return entry
        return None
    
    def get_project_by_name(self, name: str) -> Optional[ProjectRegistryEntry]:
        """Get a project by name"""
        entries = self._load_registry()
        for entry in entries:
            if entry.name == name:
                return entry
        return None
    
    def list_projects(self) -> List[ProjectRegistryEntry]:
        """List all projects"""
        return self._load_registry()
    
    def list_recent_projects(self, limit: int = 10) -> List[ProjectRegistryEntry]:
        """
        List recent projects sorted by last opened.
        
        Args:
            limit: Maximum number of projects to return
            
        Returns:
            List of recent projects
        """
        entries = self._load_registry()
        
        # Sort by last_opened descending
        entries.sort(key=lambda e: e.last_opened, reverse=True)
        
        return entries[:limit]
    
    def remove_project(self, uuid: str) -> bool:
        """
        Remove a project from the registry.
        
        Args:
            uuid: Project UUID
            
        Returns:
            True if removed, False if not found
        """
        entries = self._load_registry()
        original_count = len(entries)
        
        entries = [e for e in entries if e.uuid != uuid]
        
        if len(entries) < original_count:
            self._save_registry(entries)
            return True
        
        return False
    
    def update_last_opened(self, uuid: str) -> bool:
        """
        Update the last opened timestamp.
        
        Args:
            uuid: Project UUID
            
        Returns:
            True if updated, False if not found
        """
        return self.update_project(uuid, last_opened=datetime.utcnow().isoformat())
    
    def discover_projects(self, workspaces_dir: str = "workspaces") -> int:
        """
        Discover .irp files in workspaces directory and add to registry.
        
        Args:
            workspaces_dir: Directory to scan for .irp files
            
        Returns:
            Number of projects discovered
        """
        workspaces_path = Path(workspaces_dir)
        if not workspaces_path.exists():
            return 0
        
        discovered = 0
        existing_entries = self._load_registry()
        existing_paths = {e.file_path for e in existing_entries}
        
        for irp_file in workspaces_path.glob("*.irp"):
            file_path = str(irp_file.absolute())
            
            # Skip if already in registry
            if file_path in existing_paths:
                continue
            
            # Extract project name from filename
            project_name = irp_file.stem
            
            # Create registry entry
            import uuid as uuid_lib
            entry = ProjectRegistryEntry(
                uuid=str(uuid_lib.uuid4()),
                name=project_name,
                client="",
                description="",
                status="Pre-Implementation",
                created_at=datetime.fromtimestamp(irp_file.stat().st_ctime).isoformat(),
                last_modified=datetime.fromtimestamp(irp_file.stat().st_mtime).isoformat(),
                last_opened=datetime.fromtimestamp(irp_file.stat().st_atime).isoformat(),
                file_path=file_path,
                app_version=self.APP_VERSION
            )
            
            self.add_project(entry)
            discovered += 1
        
        return discovered
