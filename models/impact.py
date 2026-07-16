from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

@dataclass
class ImpactDTO:
    id: Optional[int] = None
    project_id: Optional[int] = None
    impact_number: str = ""
    title: str = ""
    description: str = ""
    area_of_change: str = ""
    notes: str = ""
    category: str = ""
    severity: str = ""
    likelihood: str = ""
    readiness: str = ""
    resistance: str = ""
    mitigation_strategy: str = ""
    status: str = "Draft"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    stakeholder_group_ids: List[int] = field(default_factory=list)
    organization_unit_ids: List[int] = field(default_factory=list)
    business_process_ids: List[int] = field(default_factory=list)
    system_ids: List[int] = field(default_factory=list)
    policy_ids: List[int] = field(default_factory=list)
    
    @classmethod
    def from_orm(cls, orm_obj):
        if orm_obj is None:
            return None
        return cls(
            id=orm_obj.id,
            project_id=orm_obj.project_id,
            impact_number=orm_obj.impact_number,
            title=orm_obj.title or "",
            description=orm_obj.description,
            area_of_change=orm_obj.area_of_change or "",
            notes=orm_obj.notes or "",
            category=orm_obj.category,
            severity=orm_obj.severity,
            likelihood=orm_obj.likelihood,
            readiness=orm_obj.readiness,
            resistance=orm_obj.resistance,
            mitigation_strategy=orm_obj.mitigation_strategy,
            status=orm_obj.status,
            created_at=orm_obj.created_at,
            updated_at=orm_obj.updated_at,
            stakeholder_group_ids=[sg.id for sg in orm_obj.stakeholder_groups],
            organization_unit_ids=[ou.id for ou in orm_obj.organization_units],
            business_process_ids=[bp.id for bp in orm_obj.business_processes],
            system_ids=[s.id for s in orm_obj.systems],
            policy_ids=[p.id for p in orm_obj.policies]
        )
