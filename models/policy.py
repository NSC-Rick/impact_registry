from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class PolicyDTO:
    id: Optional[int] = None
    project_id: Optional[int] = None
    name: str = ""
    description: str = ""
    policy_owner: str = ""
    effective_date: Optional[datetime] = None
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
            policy_owner=orm_obj.policy_owner,
            effective_date=orm_obj.effective_date,
            created_at=orm_obj.created_at
        )
