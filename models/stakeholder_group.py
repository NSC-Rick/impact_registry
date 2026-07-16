from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class StakeholderGroupDTO:
    id: Optional[int] = None
    project_id: Optional[int] = None
    name: str = ""
    description: str = ""
    size: Optional[int] = None
    influence: str = ""
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
            size=orm_obj.size,
            influence=orm_obj.influence,
            created_at=orm_obj.created_at
        )
