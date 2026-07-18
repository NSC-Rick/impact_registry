"""
Traceability Analyzer

Evaluates traceability and relationship completeness.
"""

from typing import List
from sqlalchemy.orm import Session
from database.schema import Impact
from analysis.analysis_models import TraceabilityAnalysisResult, AnalysisFinding


class TraceabilityAnalyzer:
    """
    Analyzes traceability of impacts to organizational elements.
    
    Evaluates:
    - Impacts without stakeholders
    - Impacts without assets (org units, processes, systems)
    - Impacts without category
    - Orphaned records
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def analyze(self) -> TraceabilityAnalysisResult:
        """
        Perform traceability analysis.
        
        Returns:
            TraceabilityAnalysisResult with score and findings
        """
        findings = []
        
        # Get all impacts
        impacts = self.session.query(Impact).all()
        total_impacts = len(impacts)
        
        if total_impacts == 0:
            return TraceabilityAnalysisResult(
                score=100.0,
                total_impacts=0,
                impacts_without_stakeholders=0,
                impacts_without_assets=0,
                impacts_without_category=0,
                findings=[]
            )
        
        # Check for impacts without stakeholders
        impacts_without_stakeholders = []
        for impact in impacts:
            if len(impact.stakeholder_groups) == 0:
                impacts_without_stakeholders.append(impact.id)
        
        if impacts_without_stakeholders:
            findings.append(AnalysisFinding(
                severity="High",
                category="Missing Traceability",
                title=f"{len(impacts_without_stakeholders)} impact(s) without stakeholders",
                description="Impacts must be traced to affected stakeholder groups for proper change management.",
                affected_records=impacts_without_stakeholders,
                recommendation="Link impacts to stakeholder groups in the Enrich page."
            ))
        
        # Check for impacts without any assets
        impacts_without_assets = []
        for impact in impacts:
            if (len(impact.organization_units) == 0 and
                len(impact.business_processes) == 0 and
                len(impact.systems) == 0 and
                len(impact.policies) == 0):
                impacts_without_assets.append(impact.id)
        
        if impacts_without_assets:
            findings.append(AnalysisFinding(
                severity="Medium",
                category="Missing Traceability",
                title=f"{len(impacts_without_assets)} impact(s) without organizational assets",
                description="Impacts should be traced to affected org units, processes, systems, or policies.",
                affected_records=impacts_without_assets,
                recommendation="Link impacts to organizational assets in the Enrich page."
            ))
        
        # Check for impacts without category
        impacts_without_category = []
        for impact in impacts:
            if not impact.category or impact.category.strip() == "":
                impacts_without_category.append(impact.id)
        
        if impacts_without_category:
            findings.append(AnalysisFinding(
                severity="Medium",
                category="Missing Classification",
                title=f"{len(impacts_without_category)} impact(s) without category",
                description="Impact category helps classify and analyze change types.",
                affected_records=impacts_without_category,
                recommendation="Assign categories to all impacts (Process Change, Technology Change, etc.)."
            ))
        
        # Check for impacts without area of change
        impacts_without_area = []
        for impact in impacts:
            if not impact.area_of_change or impact.area_of_change.strip() == "":
                impacts_without_area.append(impact.id)
        
        if impacts_without_area:
            findings.append(AnalysisFinding(
                severity="Low",
                category="Missing Classification",
                title=f"{len(impacts_without_area)} impact(s) without area of change",
                description="Area of change helps organize impacts by domain.",
                affected_records=impacts_without_area,
                recommendation="Assign area of change to all impacts."
            ))
        
        # Identify orphaned impacts (no relationships at all)
        orphaned_impact_ids = []
        for impact in impacts:
            if (len(impact.stakeholder_groups) == 0 and
                len(impact.organization_units) == 0 and
                len(impact.business_processes) == 0 and
                len(impact.systems) == 0 and
                len(impact.policies) == 0):
                orphaned_impact_ids.append(impact.id)
        
        if orphaned_impact_ids:
            findings.append(AnalysisFinding(
                severity="Critical",
                category="Orphaned Records",
                title=f"{len(orphaned_impact_ids)} orphaned impact(s) found",
                description="These impacts have no relationships to any organizational elements.",
                affected_records=orphaned_impact_ids,
                recommendation="Establish traceability by linking to stakeholders and assets."
            ))
        
        # Calculate traceability score
        score = self._calculate_score(
            total_impacts=total_impacts,
            impacts_without_stakeholders=len(impacts_without_stakeholders),
            impacts_without_assets=len(impacts_without_assets),
            impacts_without_category=len(impacts_without_category),
            orphaned_impacts=len(orphaned_impact_ids)
        )
        
        return TraceabilityAnalysisResult(
            score=score,
            total_impacts=total_impacts,
            impacts_without_stakeholders=len(impacts_without_stakeholders),
            impacts_without_assets=len(impacts_without_assets),
            impacts_without_category=len(impacts_without_category),
            orphaned_impact_ids=orphaned_impact_ids,
            findings=findings
        )
    
    def _calculate_score(
        self,
        total_impacts: int,
        impacts_without_stakeholders: int,
        impacts_without_assets: int,
        impacts_without_category: int,
        orphaned_impacts: int
    ) -> float:
        """
        Calculate traceability score.
        
        Weights:
        - 50% stakeholder traceability
        - 30% asset traceability
        - 20% classification completeness
        
        Returns:
            Score from 0-100
        """
        if total_impacts == 0:
            return 100.0
        
        # Component scores
        stakeholder_ratio = (total_impacts - impacts_without_stakeholders) / total_impacts
        asset_ratio = (total_impacts - impacts_without_assets) / total_impacts
        category_ratio = (total_impacts - impacts_without_category) / total_impacts
        
        # Weighted score
        base_score = (
            stakeholder_ratio * 50 +
            asset_ratio * 30 +
            category_ratio * 20
        )
        
        # Heavy penalty for orphaned impacts
        orphan_penalty = (orphaned_impacts / total_impacts) * 30
        
        final_score = max(0, base_score - orphan_penalty)
        
        return round(final_score, 1)
