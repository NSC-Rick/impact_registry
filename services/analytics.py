from typing import Dict, List, Tuple
from sqlalchemy import func
from sqlalchemy.orm import Session
from database.schema import Impact, StakeholderGroup, OrganizationUnit, BusinessProcess, System, Policy

class AnalyticsService:
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_impact_summary(self, project_id=None) -> Dict:
        total_impacts = self.session.query(Impact).count()
        
        by_category = self.session.query(
            Impact.category, func.count(Impact.id)
        ).group_by(Impact.category).all()
        
        by_severity = self.session.query(
            Impact.severity, func.count(Impact.id)
        ).group_by(Impact.severity).all()
        
        by_status = self.session.query(
            Impact.status, func.count(Impact.id)
        ).group_by(Impact.status).all()
        
        return {
            'total': total_impacts,
            'by_category': dict(by_category),
            'by_severity': dict(by_severity),
            'by_status': dict(by_status)
        }
    
    def get_coverage_metrics(self, project_id=None) -> Dict:
        impacts = self.session.query(Impact).all()
        
        total = len(impacts)
        if total == 0:
            return {
                'total_impacts': 0,
                'with_stakeholder_groups': 0,
                'with_organization_units': 0,
                'with_business_processes': 0,
                'with_systems': 0,
                'with_policies': 0,
                'coverage_percentage': 0
            }
        
        with_sg = sum(1 for i in impacts if len(i.stakeholder_groups) > 0)
        with_ou = sum(1 for i in impacts if len(i.organization_units) > 0)
        with_bp = sum(1 for i in impacts if len(i.business_processes) > 0)
        with_sys = sum(1 for i in impacts if len(i.systems) > 0)
        with_pol = sum(1 for i in impacts if len(i.policies) > 0)
        
        enriched = sum(1 for i in impacts if (
            len(i.stakeholder_groups) > 0 or
            len(i.organization_units) > 0 or
            len(i.business_processes) > 0 or
            len(i.systems) > 0 or
            len(i.policies) > 0
        ))
        
        return {
            'total_impacts': total,
            'with_stakeholder_groups': with_sg,
            'with_organization_units': with_ou,
            'with_business_processes': with_bp,
            'with_systems': with_sys,
            'with_policies': with_pol,
            'enriched_impacts': enriched,
            'coverage_percentage': round((enriched / total) * 100, 1) if total > 0 else 0
        }
    
    def get_risk_matrix(self, project_id=None) -> List[Tuple]:
        impacts = self.session.query(Impact).all()
        
        matrix = []
        for impact in impacts:
            if impact.severity and impact.likelihood:
                matrix.append((
                    impact.id,
                    impact.impact_number,
                    impact.description[:50],
                    impact.severity,
                    impact.likelihood
                ))
        
        return matrix
    
    def get_stakeholder_impact_count(self, project_id=None) -> List[Tuple]:
        results = self.session.query(
            StakeholderGroup.name,
            func.count(Impact.id)
        ).join(
            Impact.stakeholder_groups
        ).group_by(
            StakeholderGroup.name
        ).all()
        
        return results
    
    def get_process_impact_count(self, project_id=None) -> List[Tuple]:
        results = self.session.query(
            BusinessProcess.name,
            func.count(Impact.id)
        ).join(
            Impact.business_processes
        ).group_by(
            BusinessProcess.name
        ).all()
        
        return results
    
    def get_system_impact_count(self, project_id=None) -> List[Tuple]:
        results = self.session.query(
            System.name,
            func.count(Impact.id)
        ).join(
            Impact.systems
        ).group_by(
            System.name
        ).all()
        
        return results
