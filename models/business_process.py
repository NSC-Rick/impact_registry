from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class BusinessProcessDTO:
    id: Optional[int] = None
    project_id: Optional[int] = None
    name: str = ""
    description: str = ""
    process_owner: str = ""
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
            process_owner=orm_obj.process_owner,
            criticality=orm_obj.criticality,
            created_at=orm_obj.created_at
        )
