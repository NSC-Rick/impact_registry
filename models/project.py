from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class ProjectDTO:
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    sponsor: str = ""
    change_manager: str = ""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: str = "Active"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_orm(cls, orm_obj):
        if orm_obj is None:
            return None
        return cls(
            id=orm_obj.id,
            name=orm_obj.name,
            description=orm_obj.description,
            sponsor=orm_obj.sponsor,
            change_manager=orm_obj.change_manager,
            start_date=orm_obj.start_date,
            end_date=orm_obj.end_date,
            status=orm_obj.status,
            created_at=orm_obj.created_at,
            updated_at=orm_obj.updated_at
        )
