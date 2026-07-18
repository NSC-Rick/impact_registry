"""
Distribution Analyzer

Analyzes distribution of impacts across dimensions.
"""

from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.schema import Impact
from analysis.analysis_models import DistributionAnalysisResult, AnalysisFinding


class DistributionAnalyzer:
    """
    Analyzes distribution of impacts across various dimensions.
    
    Evaluates:
    - Distribution by severity
    - Distribution by category
    - Distribution by status
    - Distribution by area of change
    - Identifies hotspots
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def analyze(self) -> DistributionAnalysisResult:
        """
        Perform distribution analysis.
        
        Returns:
            DistributionAnalysisResult with distributions and findings
        """
        findings = []
        
        # Get all impacts
        impacts = self.session.query(Impact).all()
        total_impacts = len(impacts)
        
        if total_impacts == 0:
            return DistributionAnalysisResult(
                total_impacts=0,
                findings=[AnalysisFinding(
                    severity="Info",
                    category="No Data",
                    title="No impacts to analyze",
                    description="The registry contains no change impacts.",
                    recommendation="Begin documenting change impacts."
                )]
            )
        
        # Distribution by severity
        by_severity = {}
        for impact in impacts:
            severity = impact.severity or "Unassigned"
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        # Check for severity distribution issues
        if "Unassigned" in by_severity and by_severity["Unassigned"] > total_impacts * 0.2:
            findings.append(AnalysisFinding(
                severity="Medium",
                category="Distribution Issue",
                title=f"{by_severity['Unassigned']} impact(s) without severity",
                description="More than 20% of impacts lack severity classification.",
                recommendation="Assign severity levels to enable proper risk assessment."
            ))
        
        if "Critical" in by_severity and by_severity["Critical"] > total_impacts * 0.3:
            findings.append(AnalysisFinding(
                severity="Info",
                category="Distribution Pattern",
                title=f"{by_severity['Critical']} critical impact(s) identified",
                description="Over 30% of impacts are classified as Critical. This may indicate significant change scope.",
                recommendation="Review critical impacts to ensure proper mitigation strategies."
            ))
        
        # Distribution by category
        by_category = {}
        for impact in impacts:
            category = impact.category or "Uncategorized"
            by_category[category] = by_category.get(category, 0) + 1
        
        if "Uncategorized" in by_category and by_category["Uncategorized"] > total_impacts * 0.2:
            findings.append(AnalysisFinding(
                severity="Medium",
                category="Distribution Issue",
                title=f"{by_category['Uncategorized']} impact(s) without category",
                description="More than 20% of impacts lack category classification.",
                recommendation="Assign categories to enable pattern analysis."
            ))
        
        # Distribution by status
        by_status = {}
        for impact in impacts:
            status = impact.status or "No Status"
            by_status[status] = by_status.get(status, 0) + 1
        
        if "Draft" in by_status and by_status["Draft"] > total_impacts * 0.5:
            findings.append(AnalysisFinding(
                severity="Low",
                category="Distribution Pattern",
                title=f"{by_status['Draft']} impact(s) in Draft status",
                description="Over 50% of impacts are still in Draft status.",
                recommendation="Review and approve impacts to progress them through the workflow."
            ))
        
        # Distribution by area of change
        by_area_of_change = {}
        for impact in impacts:
            area = impact.area_of_change or "Unspecified"
            by_area_of_change[area] = by_area_of_change.get(area, 0) + 1
        
        # Identify hotspots (areas with high concentration)
        hotspots = []
        for area, count in by_area_of_change.items():
            if area != "Unspecified" and count > total_impacts * 0.2:
                hotspots.append({
                    'dimension': 'Area of Change',
                    'value': area,
                    'count': count,
                    'percentage': round((count / total_impacts) * 100, 1)
                })
        
        # Identify stakeholder hotspots
        stakeholder_impact_counts = {}
        for impact in impacts:
            for sg in impact.stakeholder_groups:
                stakeholder_impact_counts[sg.name] = stakeholder_impact_counts.get(sg.name, 0) + 1
        
        for sg_name, count in stakeholder_impact_counts.items():
            if count > total_impacts * 0.3:
                hotspots.append({
                    'dimension': 'Stakeholder Group',
                    'value': sg_name,
                    'count': count,
                    'percentage': round((count / total_impacts) * 100, 1)
                })
        
        if hotspots:
            hotspot_desc = ", ".join([f"{h['value']} ({h['count']} impacts)" for h in hotspots[:3]])
            findings.append(AnalysisFinding(
                severity="Info",
                category="Hotspot Identified",
                title=f"{len(hotspots)} impact hotspot(s) identified",
                description=f"High concentration of impacts in: {hotspot_desc}",
                recommendation="Focus change management efforts on these high-impact areas."
            ))
        
        return DistributionAnalysisResult(
            total_impacts=total_impacts,
            by_severity=by_severity,
            by_category=by_category,
            by_status=by_status,
            by_area_of_change=by_area_of_change,
            hotspots=hotspots,
            findings=findings
        )
