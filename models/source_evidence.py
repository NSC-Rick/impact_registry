from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class SourceEvidenceDTO:
    id: Optional[int] = None
    impact_id: Optional[int] = None
    source_type: str = ""
    source_reference: str = ""
    notes: str = ""
    created_at: Optional[datetime] = None
    
    @classmethod
    def from_orm(cls, orm_obj):
        if orm_obj is None:
            return None
        return cls(
            id=orm_obj.id,
            impact_id=orm_obj.impact_id,
            source_type=orm_obj.source_type,
            source_reference=orm_obj.source_reference,
            notes=orm_obj.notes,
            created_at=orm_obj.created_at
        )
