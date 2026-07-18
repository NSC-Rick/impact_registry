"""
Coverage Analyzer

Evaluates which organizational areas have documented impacts.
"""

from typing import Dict, List
from sqlalchemy.orm import Session
from database.schema import Impact, StakeholderGroup, OrganizationUnit, BusinessProcess, System
from analysis.analysis_models import CoverageAnalysisResult, AnalysisFinding


class CoverageAnalyzer:
    """
    Analyzes coverage of impacts across organizational dimensions.
    
    Evaluates:
    - Stakeholder group coverage
    - Organization unit coverage
    - Business process coverage
    - System coverage
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def analyze(self) -> CoverageAnalysisResult:
        """
        Perform comprehensive coverage analysis.
        
        Returns:
            CoverageAnalysisResult with score and findings
        """
        findings = []
        
        # Get all impacts
        impacts = self.session.query(Impact).all()
        total_impacts = len(impacts)
        
        if total_impacts == 0:
            return CoverageAnalysisResult(
                score=0.0,
                total_impacts=0,
                impacts_with_stakeholders=0,
                impacts_with_org_units=0,
                impacts_with_processes=0,
                impacts_with_systems=0,
                findings=[AnalysisFinding(
                    severity="Critical",
                    category="No Data",
                    title="No impacts documented",
                    description="The registry contains no change impacts.",
                    recommendation="Begin documenting change impacts in the Capture page."
                )]
            )
        
        # Count impacts with relationships
        impacts_with_stakeholders = sum(1 for i in impacts if len(i.stakeholder_groups) > 0)
        impacts_with_org_units = sum(1 for i in impacts if len(i.organization_units) > 0)
        impacts_with_processes = sum(1 for i in impacts if len(i.business_processes) > 0)
        impacts_with_systems = sum(1 for i in impacts if len(i.systems) > 0)
        
        # Stakeholder coverage
        stakeholder_coverage = {}
        all_stakeholders = self.session.query(StakeholderGroup).all()
        uncovered_stakeholders = []
        
        for sg in all_stakeholders:
            impact_count = len([i for i in impacts if sg in i.stakeholder_groups])
            stakeholder_coverage[sg.name] = impact_count
            if impact_count == 0:
                uncovered_stakeholders.append(sg.name)
        
        if uncovered_stakeholders:
            findings.append(AnalysisFinding(
                severity="Medium",
                category="Coverage Gap",
                title=f"{len(uncovered_stakeholders)} stakeholder group(s) without impacts",
                description=f"The following stakeholder groups have no documented impacts: {', '.join(uncovered_stakeholders[:5])}{'...' if len(uncovered_stakeholders) > 5 else ''}",
                recommendation="Review whether these stakeholder groups are truly unaffected or if impacts need to be documented."
            ))
        
        # Organization unit coverage
        org_unit_coverage = {}
        all_org_units = self.session.query(OrganizationUnit).all()
        uncovered_org_units = []
        
        for ou in all_org_units:
            impact_count = len([i for i in impacts if ou in i.organization_units])
            org_unit_coverage[ou.name] = impact_count
            if impact_count == 0:
                uncovered_org_units.append(ou.name)
        
        if uncovered_org_units:
            findings.append(AnalysisFinding(
                severity="Medium",
                category="Coverage Gap",
                title=f"{len(uncovered_org_units)} organization unit(s) without impacts",
                description=f"The following organization units have no documented impacts: {', '.join(uncovered_org_units[:5])}{'...' if len(uncovered_org_units) > 5 else ''}",
                recommendation="Review whether these organization units are truly unaffected or if impacts need to be documented."
            ))
        
        # Business process coverage
        process_coverage = {}
        all_processes = self.session.query(BusinessProcess).all()
        uncovered_processes = []
        
        for bp in all_processes:
            impact_count = len([i for i in impacts if bp in i.business_processes])
            process_coverage[bp.name] = impact_count
            if impact_count == 0:
                uncovered_processes.append(bp.name)
        
        if uncovered_processes:
            findings.append(AnalysisFinding(
                severity="Low",
                category="Coverage Gap",
                title=f"{len(uncovered_processes)} business process(es) without impacts",
                description=f"The following business processes have no documented impacts: {', '.join(uncovered_processes[:5])}{'...' if len(uncovered_processes) > 5 else ''}",
                recommendation="Review whether these business processes are truly unaffected."
            ))
        
        # Check for impacts without any relationships
        impacts_without_any = []
        for impact in impacts:
            if (len(impact.stakeholder_groups) == 0 and
                len(impact.organization_units) == 0 and
                len(impact.business_processes) == 0 and
                len(impact.systems) == 0):
                impacts_without_any.append(impact.id)
        
        if impacts_without_any:
            findings.append(AnalysisFinding(
                severity="High",
                category="Coverage Gap",
                title=f"{len(impacts_without_any)} impact(s) without any relationships",
                description="These impacts are not linked to any stakeholders, org units, processes, or systems.",
                affected_records=impacts_without_any,
                recommendation="Enrich these impacts by linking them to affected organizational elements."
            ))
        
        # Calculate coverage score
        score = self._calculate_score(
            total_impacts=total_impacts,
            impacts_with_stakeholders=impacts_with_stakeholders,
            impacts_with_org_units=impacts_with_org_units,
            impacts_with_processes=impacts_with_processes,
            impacts_with_systems=impacts_with_systems,
            uncovered_stakeholders=len(uncovered_stakeholders),
            total_stakeholders=len(all_stakeholders),
            uncovered_org_units=len(uncovered_org_units),
            total_org_units=len(all_org_units)
        )
        
        return CoverageAnalysisResult(
            score=score,
            total_impacts=total_impacts,
            impacts_with_stakeholders=impacts_with_stakeholders,
            impacts_with_org_units=impacts_with_org_units,
            impacts_with_processes=impacts_with_processes,
            impacts_with_systems=impacts_with_systems,
            stakeholder_coverage=stakeholder_coverage,
            org_unit_coverage=org_unit_coverage,
            process_coverage=process_coverage,
            uncovered_stakeholders=uncovered_stakeholders,
            uncovered_org_units=uncovered_org_units,
            findings=findings
        )
    
    def _calculate_score(
        self,
        total_impacts: int,
        impacts_with_stakeholders: int,
        impacts_with_org_units: int,
        impacts_with_processes: int,
        impacts_with_systems: int,
        uncovered_stakeholders: int,
        total_stakeholders: int,
        uncovered_org_units: int,
        total_org_units: int
    ) -> float:
        """
        Calculate coverage score.
        
        Weights:
        - 40% impacts with stakeholders
        - 30% impacts with org units
        - 20% stakeholder coverage
        - 10% org unit coverage
        
        Returns:
            Score from 0-100
        """
        if total_impacts == 0:
            return 0.0
        
        # Impact enrichment scores
        stakeholder_ratio = impacts_with_stakeholders / total_impacts
        org_unit_ratio = impacts_with_org_units / total_impacts
        
        # Asset coverage scores
        stakeholder_coverage_ratio = 1.0
        if total_stakeholders > 0:
            stakeholder_coverage_ratio = (total_stakeholders - uncovered_stakeholders) / total_stakeholders
        
        org_unit_coverage_ratio = 1.0
        if total_org_units > 0:
            org_unit_coverage_ratio = (total_org_units - uncovered_org_units) / total_org_units
        
        # Weighted score
        score = (
            stakeholder_ratio * 40 +
            org_unit_ratio * 30 +
            stakeholder_coverage_ratio * 20 +
            org_unit_coverage_ratio * 10
        )
        
        return round(score, 1)
