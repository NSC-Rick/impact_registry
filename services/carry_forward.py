from typing import List, Dict
from sqlalchemy.orm import Session
from database.schema import Project, Impact, StakeholderGroup, OrganizationUnit, BusinessProcess, System, Policy

class CarryForwardService:
    
    def __init__(self, session: Session):
        self.session = session
    
    def carry_forward_enterprise_assets(self, source_project_id: int, target_project_id: int) -> Dict[str, int]:
        counts = {
            'stakeholder_groups': 0,
            'organization_units': 0,
            'business_processes': 0,
            'systems': 0,
            'policies': 0
        }
        
        source_sgs = self.session.query(StakeholderGroup).filter(
            StakeholderGroup.project_id == source_project_id
        ).all()
        for sg in source_sgs:
            new_sg = StakeholderGroup(
                project_id=target_project_id,
                name=sg.name,
                description=sg.description,
                size=sg.size,
                influence=sg.influence
            )
            self.session.add(new_sg)
            counts['stakeholder_groups'] += 1
        
        source_ous = self.session.query(OrganizationUnit).filter(
            OrganizationUnit.project_id == source_project_id
        ).all()
        for ou in source_ous:
            new_ou = OrganizationUnit(
                project_id=target_project_id,
                name=ou.name,
                description=ou.description,
                parent_unit=ou.parent_unit,
                head_of_unit=ou.head_of_unit
            )
            self.session.add(new_ou)
            counts['organization_units'] += 1
        
        source_bps = self.session.query(BusinessProcess).filter(
            BusinessProcess.project_id == source_project_id
        ).all()
        for bp in source_bps:
            new_bp = BusinessProcess(
                project_id=target_project_id,
                name=bp.name,
                description=bp.description,
                process_owner=bp.process_owner,
                criticality=bp.criticality
            )
            self.session.add(new_bp)
            counts['business_processes'] += 1
        
        source_systems = self.session.query(System).filter(
            System.project_id == source_project_id
        ).all()
        for sys in source_systems:
            new_sys = System(
                project_id=target_project_id,
                name=sys.name,
                description=sys.description,
                system_owner=sys.system_owner,
                vendor=sys.vendor,
                criticality=sys.criticality
            )
            self.session.add(new_sys)
            counts['systems'] += 1
        
        source_policies = self.session.query(Policy).filter(
            Policy.project_id == source_project_id
        ).all()
        for pol in source_policies:
            new_pol = Policy(
                project_id=target_project_id,
                name=pol.name,
                description=pol.description,
                policy_owner=pol.policy_owner,
                effective_date=pol.effective_date
            )
            self.session.add(new_pol)
            counts['policies'] += 1
        
        self.session.commit()
        return counts
    
    def suggest_similar_impacts(self, description: str, project_id: int, limit: int = 5) -> List[Impact]:
        impacts = self.session.query(Impact).filter(
            Impact.project_id == project_id
        ).all()
        
        scored_impacts = []
        desc_lower = description.lower()
        words = set(desc_lower.split())
        
        for impact in impacts:
            impact_words = set(impact.description.lower().split())
            common_words = words.intersection(impact_words)
            score = len(common_words)
            if score > 0:
                scored_impacts.append((score, impact))
        
        scored_impacts.sort(reverse=True, key=lambda x: x[0])
        return [impact for score, impact in scored_impacts[:limit]]
