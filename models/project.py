from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class ProjectMetadataDTO:
    """Data transfer object for project metadata"""
    id: Optional[int] = None
    project_name: str = ""
    client_name: str = ""
    program_name: str = ""
    description: str = ""
    sponsor: str = ""
    change_manager: str = ""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: str = "Active"
    registry_version: str = "1.0"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_orm(cls, orm_obj):
        if orm_obj is None:
            return None
        return cls(
            id=orm_obj.id,
            project_name=orm_obj.project_name,
            client_name=orm_obj.client_name,
            program_name=orm_obj.program_name,
            description=orm_obj.description,
            sponsor=orm_obj.sponsor,
            change_manager=orm_obj.change_manager,
            start_date=orm_obj.start_date,
            end_date=orm_obj.end_date,
            status=orm_obj.status,
            registry_version=orm_obj.registry_version,
            created_at=orm_obj.created_at,
            updated_at=orm_obj.updated_at
        )

# Legacy alias for backward compatibility
ProjectDTO = ProjectMetadataDTO
