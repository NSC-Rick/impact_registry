from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class SystemDTO:
    id: Optional[int] = None
    project_id: Optional[int] = None
    name: str = ""
    description: str = ""
    system_owner: str = ""
    vendor: str = ""
    criticality: str = ""
    created_at: Optional[datetime] = None
    
    @classmethod
    def from_orm(cls, orm_obj):
        if orm_obj is None:
            return None
        return cls(
            id=orm_obj.id,
            project_id=orm_obj.project_id,
            name=orm_obj.name,
            description=orm_obj.description,
            system_owner=orm_obj.system_owner,
            vendor=orm_obj.vendor,
            criticality=orm_obj.criticality,
            created_at=orm_obj.created_at
        )
