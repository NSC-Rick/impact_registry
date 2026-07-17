from typing import List, Optional
from sqlalchemy.orm import Session
from database.schema import (
    Project, Impact, StakeholderGroup, OrganizationUnit, 
    BusinessProcess, System, Policy, SourceEvidence, ChangeAsset
)
from models.project import ProjectDTO
from models.impact import ImpactDTO

class Repository:
    def __init__(self, session: Session):
        self.session = session
    
    def create_project(self, project_dto: ProjectDTO) -> ProjectDTO:
        project = Project(
            name=project_dto.name,
            description=project_dto.description,
            sponsor=project_dto.sponsor,
            change_manager=project_dto.change_manager,
            start_date=project_dto.start_date,
            end_date=project_dto.end_date,
            status=project_dto.status
        )
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)
        return ProjectDTO.from_orm(project)
    
    def get_project(self, project_id: int) -> Optional[ProjectDTO]:
        project = self.session.query(Project).filter(Project.id == project_id).first()
        return ProjectDTO.from_orm(project)
    
    def list_projects(self) -> List[ProjectDTO]:
        projects = self.session.query(Project).all()
        return [ProjectDTO.from_orm(p) for p in projects]
    
    def update_project(self, project_dto: ProjectDTO) -> ProjectDTO:
        project = self.session.query(Project).filter(Project.id == project_dto.id).first()
        if project:
            project.name = project_dto.name
            project.description = project_dto.description
            project.sponsor = project_dto.sponsor
            project.change_manager = project_dto.change_manager
            project.start_date = project_dto.start_date
            project.end_date = project_dto.end_date
            project.status = project_dto.status
            self.session.commit()
            self.session.refresh(project)
        return ProjectDTO.from_orm(project)
    
    def create_impact(self, impact_dto: ImpactDTO) -> ImpactDTO:
        impact = Impact(
            impact_number=impact_dto.impact_number,
            title=impact_dto.title,
            description=impact_dto.description,
            area_of_change=impact_dto.area_of_change,
            notes=impact_dto.notes,
            category=impact_dto.category,
            severity=impact_dto.severity,
            likelihood=impact_dto.likelihood,
            readiness=impact_dto.readiness,
            resistance=impact_dto.resistance,
            mitigation_strategy=impact_dto.mitigation_strategy,
            status=impact_dto.status
        )
        self.session.add(impact)
        self.session.commit()
        self.session.refresh(impact)
        return ImpactDTO.from_orm(impact)
    
    def get_impact(self, impact_id: int) -> Optional[ImpactDTO]:
        impact = self.session.query(Impact).filter(Impact.id == impact_id).first()
        return ImpactDTO.from_orm(impact)
    
    def list_impacts(self, project_id: Optional[int] = None) -> List[ImpactDTO]:
        impacts = self.session.query(Impact).all()
        return [ImpactDTO.from_orm(i) for i in impacts]
    
    def update_impact(self, impact_dto: ImpactDTO) -> ImpactDTO:
        impact = self.session.query(Impact).filter(Impact.id == impact_dto.id).first()
        if impact:
            impact.impact_number = impact_dto.impact_number
            impact.title = impact_dto.title
            impact.description = impact_dto.description
            impact.area_of_change = impact_dto.area_of_change
            impact.notes = impact_dto.notes
            impact.category = impact_dto.category
            impact.severity = impact_dto.severity
            impact.likelihood = impact_dto.likelihood
            impact.readiness = impact_dto.readiness
            impact.resistance = impact_dto.resistance
            impact.mitigation_strategy = impact_dto.mitigation_strategy
            impact.status = impact_dto.status
            
            impact.stakeholder_groups = []
            for sg_id in impact_dto.stakeholder_group_ids:
                sg = self.session.query(StakeholderGroup).filter(StakeholderGroup.id == sg_id).first()
                if sg:
                    impact.stakeholder_groups.append(sg)
            
            impact.organization_units = []
            for ou_id in impact_dto.organization_unit_ids:
                ou = self.session.query(OrganizationUnit).filter(OrganizationUnit.id == ou_id).first()
                if ou:
                    impact.organization_units.append(ou)
            
            impact.business_processes = []
            for bp_id in impact_dto.business_process_ids:
                bp = self.session.query(BusinessProcess).filter(BusinessProcess.id == bp_id).first()
                if bp:
                    impact.business_processes.append(bp)
            
            impact.systems = []
            for s_id in impact_dto.system_ids:
                s = self.session.query(System).filter(System.id == s_id).first()
                if s:
                    impact.systems.append(s)
            
            impact.policies = []
            for p_id in impact_dto.policy_ids:
                p = self.session.query(Policy).filter(Policy.id == p_id).first()
                if p:
                    impact.policies.append(p)
            
            self.session.commit()
            self.session.refresh(impact)
        return ImpactDTO.from_orm(impact)
    
    def delete_impact(self, impact_id: int) -> bool:
        impact = self.session.query(Impact).filter(Impact.id == impact_id).first()
        if impact:
            self.session.delete(impact)
            self.session.commit()
            return True
        return False
    
    def supersede_impact(self, impact_id: int) -> bool:
        impact = self.session.query(Impact).filter(Impact.id == impact_id).first()
        if impact:
            impact.status = "Superseded"
            self.session.commit()
            return True
        return False
    
    def create_stakeholder_group(self, project_id, name: str, description: str = "", 
                                size: int = 0, influence: str = "") -> StakeholderGroup:
        sg = StakeholderGroup(
            name=name,
            description=description,
            size=size,
            influence=influence
        )
        self.session.add(sg)
        self.session.commit()
        self.session.refresh(sg)
        return sg
    
    def list_stakeholder_groups(self, project_id=None) -> List[StakeholderGroup]:
        return self.session.query(StakeholderGroup).all()
    
    def create_organization_unit(self, project_id, name: str, description: str = "",
                                parent_unit: str = "", head_of_unit: str = "") -> OrganizationUnit:
        ou = OrganizationUnit(
            name=name,
            description=description,
            parent_unit=parent_unit,
            head_of_unit=head_of_unit
        )
        self.session.add(ou)
        self.session.commit()
        self.session.refresh(ou)
        return ou
    
    def list_organization_units(self, project_id=None) -> List[OrganizationUnit]:
        return self.session.query(OrganizationUnit).all()
    
    def create_business_process(self, project_id, name: str, description: str = "",
                               process_owner: str = "", criticality: str = "") -> BusinessProcess:
        bp = BusinessProcess(
            name=name,
            description=description,
            process_owner=process_owner,
            criticality=criticality
        )
        self.session.add(bp)
        self.session.commit()
        self.session.refresh(bp)
        return bp
    
    def list_business_processes(self, project_id=None) -> List[BusinessProcess]:
        return self.session.query(BusinessProcess).all()
    
    def create_system(self, project_id, name: str, description: str = "",
                     system_owner: str = "", vendor: str = "", criticality: str = "") -> System:
        sys = System(
            name=name,
            description=description,
            system_owner=system_owner,
            vendor=vendor,
            criticality=criticality
        )
        self.session.add(sys)
        self.session.commit()
        self.session.refresh(sys)
        return sys
    
    def list_systems(self, project_id=None) -> List[System]:
        return self.session.query(System).all()
    
    def create_policy(self, project_id, name: str, description: str = "",
                     policy_owner: str = "", effective_date = None) -> Policy:
        pol = Policy(
            name=name,
            description=description,
            policy_owner=policy_owner,
            effective_date=effective_date
        )
        self.session.add(pol)
        self.session.commit()
        self.session.refresh(pol)
        return pol
    
    def list_policies(self, project_id=None) -> List[Policy]:
        return self.session.query(Policy).all()
    
    def create_source_evidence(self, impact_id: int, source_type: str, 
                              source_reference: str, notes: str = "") -> SourceEvidence:
        se = SourceEvidence(
            impact_id=impact_id,
            source_type=source_type,
            source_reference=source_reference,
            notes=notes
        )
        self.session.add(se)
        self.session.commit()
        self.session.refresh(se)
        return se
    
    def list_source_evidences(self, impact_id: int) -> List[SourceEvidence]:
        return self.session.query(SourceEvidence).filter(
            SourceEvidence.impact_id == impact_id
        ).all()
    
    def create_change_asset(self, impact_id: int, asset_type: str, asset_name: str,
                           description: str = "", status: str = "", owner: str = "") -> ChangeAsset:
        ca = ChangeAsset(
            impact_id=impact_id,
            asset_type=asset_type,
            asset_name=asset_name,
            description=description,
            status=status,
            owner=owner
        )
        self.session.add(ca)
        self.session.commit()
        self.session.refresh(ca)
        return ca
    
    def list_change_assets(self, impact_id: int) -> List[ChangeAsset]:
        return self.session.query(ChangeAsset).filter(
            ChangeAsset.impact_id == impact_id
        ).all()
