"""
Ownership Analyzer

Evaluates ownership and accountability assignments.
"""

from typing import List
from sqlalchemy.orm import Session
from database.schema import Impact
from analysis.analysis_models import OwnershipAnalysisResult, AnalysisFinding


class OwnershipAnalyzer:
    """
    Analyzes ownership assignments for impacts.
    
    Note: Current schema doesn't have explicit owner/lead fields.
    This analyzer checks for notes/descriptions that might indicate ownership.
    Future schema updates can add dedicated owner fields.
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def analyze(self) -> OwnershipAnalysisResult:
        """
        Perform ownership analysis.
        
        Returns:
            OwnershipAnalysisResult with score and findings
        """
        findings = []
        
        # Get all impacts
        impacts = self.session.query(Impact).all()
        total_impacts = len(impacts)
        
        if total_impacts == 0:
            return OwnershipAnalysisResult(
                score=100.0,
                total_impacts=0,
                impacts_without_owner=0,
                impacts_without_lead=0,
                findings=[]
            )
        
        # Check for ownership indicators in notes
        # This is a placeholder - in future, dedicated owner fields should be added
        impacts_without_notes = []
        impacts_without_owner = 0
        
        for impact in impacts:
            if not impact.notes or impact.notes.strip() == "":
                impacts_without_notes.append(impact.id)
                impacts_without_owner += 1
        
        if impacts_without_notes:
            findings.append(AnalysisFinding(
                severity="Medium",
                category="Missing Ownership",
                title=f"{len(impacts_without_notes)} impact(s) without notes",
                description="Impacts lack notes that could document ownership, accountability, or additional context.",
                affected_records=impacts_without_notes,
                recommendation="Add notes to document impact owners, change leads, or other accountability information."
            ))
        
        # Check for impacts without status
        impacts_without_status = []
        for impact in impacts:
            if not impact.status or impact.status.strip() == "":
                impacts_without_status.append(impact.id)
        
        if impacts_without_status:
            findings.append(AnalysisFinding(
                severity="Low",
                category="Missing Status",
                title=f"{len(impacts_without_status)} impact(s) without status",
                description="Impact status helps track accountability and progress.",
                affected_records=impacts_without_status,
                recommendation="Assign status to all impacts (Draft, In Review, Approved, etc.)."
            ))
        
        # Calculate ownership score
        score = self._calculate_score(
            total_impacts=total_impacts,
            impacts_without_owner=impacts_without_owner,
            findings=findings
        )
        
        return OwnershipAnalysisResult(
            score=score,
            total_impacts=total_impacts,
            impacts_without_owner=impacts_without_owner,
            impacts_without_lead=0,  # Placeholder - no lead field in current schema
            unassigned_impact_ids=impacts_without_notes,
            findings=findings
        )
    
    def _calculate_score(
        self,
        total_impacts: int,
        impacts_without_owner: int,
        findings: List[AnalysisFinding]
    ) -> float:
        """
        Calculate ownership score.
        
        Returns:
            Score from 0-100
        """
        if total_impacts == 0:
            return 100.0
        
        # Base score from assigned impacts
        assigned_ratio = (total_impacts - impacts_without_owner) / total_impacts
        base_score = assigned_ratio * 100
        
        # Deduct for findings
        penalty = sum(5 for f in findings if f.severity in ["High", "Medium"])
        
        final_score = max(0, base_score - penalty)
        
        return round(final_score, 1)
