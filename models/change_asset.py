from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class ChangeAssetDTO:
    id: Optional[int] = None
    impact_id: Optional[int] = None
    asset_type: str = ""
    asset_name: str = ""
    description: str = ""
    status: str = ""
    owner: str = ""
    created_at: Optional[datetime] = None
    
    @classmethod
    def from_orm(cls, orm_obj):
        if orm_obj is None:
            return None
        return cls(
            id=orm_obj.id,
            impact_id=orm_obj.impact_id,
            asset_type=orm_obj.asset_type,
            asset_name=orm_obj.asset_name,
            description=orm_obj.description,
            status=orm_obj.status,
            owner=orm_obj.owner,
            created_at=orm_obj.created_at
        )
