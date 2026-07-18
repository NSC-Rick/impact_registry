"""
Freshness Analyzer

Evaluates recency and staleness of registry data.
"""

from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from database.schema import Impact
from analysis.analysis_models import FreshnessAnalysisResult, AnalysisFinding


class FreshnessAnalyzer:
    """
    Analyzes freshness of registry data.
    
    Evaluates:
    - Recently created impacts
    - Recently modified impacts
    - Stale impacts (not modified in 30+ days)
    - Average age of impacts
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def analyze(self) -> FreshnessAnalysisResult:
        """
        Perform freshness analysis.
        
        Returns:
            FreshnessAnalysisResult with score and findings
        """
        findings = []
        
        # Get all impacts
        impacts = self.session.query(Impact).all()
        total_impacts = len(impacts)
        
        if total_impacts == 0:
            return FreshnessAnalysisResult(
                score=100.0,
                total_impacts=0,
                recently_created=0,
                recently_modified=0,
                stale_impacts=0,
                findings=[]
            )
        
        now = datetime.utcnow()
        seven_days_ago = now - timedelta(days=7)
        thirty_days_ago = now - timedelta(days=30)
        
        recently_created = 0
        recently_modified = 0
        stale_impacts = []
        total_age_days = 0
        
        for impact in impacts:
            # Check creation date
            if impact.created_at and impact.created_at >= seven_days_ago:
                recently_created += 1
            
            # Check modification date
            if impact.updated_at and impact.updated_at >= seven_days_ago:
                recently_modified += 1
            
            # Check for stale impacts
            if impact.updated_at:
                if impact.updated_at < thirty_days_ago:
                    stale_impacts.append(impact.id)
                
                # Calculate age
                age = (now - impact.created_at).days if impact.created_at else 0
                total_age_days += age
            else:
                # No update timestamp - consider stale
                stale_impacts.append(impact.id)
        
        average_age_days = total_age_days / total_impacts if total_impacts > 0 else 0
        
        # Generate findings
        if len(stale_impacts) > total_impacts * 0.5:
            findings.append(AnalysisFinding(
                severity="Medium",
                category="Stale Data",
                title=f"{len(stale_impacts)} impact(s) not updated in 30+ days",
                description="Over 50% of impacts have not been reviewed or updated recently.",
                affected_records=stale_impacts,
                recommendation="Review and update stale impacts to ensure accuracy and relevance."
            ))
        elif len(stale_impacts) > total_impacts * 0.3:
            findings.append(AnalysisFinding(
                severity="Low",
                category="Stale Data",
                title=f"{len(stale_impacts)} impact(s) not updated in 30+ days",
                description="A significant portion of impacts have not been reviewed recently.",
                affected_records=stale_impacts,
                recommendation="Consider periodic review cycles to keep the registry current."
            ))
        
        if recently_created > 0:
            findings.append(AnalysisFinding(
                severity="Info",
                category="Recent Activity",
                title=f"{recently_created} impact(s) created in last 7 days",
                description="Active documentation is occurring.",
                recommendation="Continue capturing new impacts as they are identified."
            ))
        
        if recently_modified > 0:
            findings.append(AnalysisFinding(
                severity="Info",
                category="Recent Activity",
                title=f"{recently_modified} impact(s) modified in last 7 days",
                description="Registry is being actively maintained.",
                recommendation="Maintain regular review and update cycles."
            ))
        
        if recently_created == 0 and recently_modified == 0:
            findings.append(AnalysisFinding(
                severity="Medium",
                category="No Recent Activity",
                title="No impacts created or modified in last 7 days",
                description="The registry shows no recent activity.",
                recommendation="Ensure the registry is being actively maintained and updated."
            ))
        
        # Calculate freshness score
        score = self._calculate_score(
            total_impacts=total_impacts,
            recently_modified=recently_modified,
            stale_impacts=len(stale_impacts),
            average_age_days=average_age_days
        )
        
        return FreshnessAnalysisResult(
            score=score,
            total_impacts=total_impacts,
            recently_created=recently_created,
            recently_modified=recently_modified,
            stale_impacts=len(stale_impacts),
            stale_impact_ids=stale_impacts,
            average_age_days=round(average_age_days, 1),
            findings=findings
        )
    
    def _calculate_score(
        self,
        total_impacts: int,
        recently_modified: int,
        stale_impacts: int,
        average_age_days: float
    ) -> float:
        """
        Calculate freshness score.
        
        Factors:
        - Recent modification activity (40%)
        - Staleness ratio (40%)
        - Average age (20%)
        
        Returns:
            Score from 0-100
        """
        if total_impacts == 0:
            return 100.0
        
        # Recent activity score
        activity_ratio = recently_modified / total_impacts
        activity_score = min(activity_ratio * 2, 1.0) * 40  # Cap at 50% activity
        
        # Staleness score
        fresh_ratio = (total_impacts - stale_impacts) / total_impacts
        staleness_score = fresh_ratio * 40
        
        # Age score (newer is better, penalize if average age > 60 days)
        age_score = 20
        if average_age_days > 60:
            age_penalty = min((average_age_days - 60) / 60, 1.0) * 20
            age_score = max(0, age_score - age_penalty)
        
        final_score = activity_score + staleness_score + age_score
        
        return round(final_score, 1)
