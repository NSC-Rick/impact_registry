"""
Registry Health Calculator

Calculates overall registry health score from component analyses.
"""

from analysis.analysis_models import (
    RegistryHealthResult,
    IntegrityAnalysisResult,
    CoverageAnalysisResult,
    OwnershipAnalysisResult,
    TraceabilityAnalysisResult,
    DistributionAnalysisResult,
    FreshnessAnalysisResult,
    AnalysisFinding
)
from datetime import datetime


class HealthCalculator:
    """
    Calculates overall registry health from component scores.
    
    Weighting:
    - Data Integrity: 30%
    - Coverage: 25%
    - Traceability: 20%
    - Ownership: 15%
    - Freshness: 10%
    """
    
    # Score weights
    INTEGRITY_WEIGHT = 0.30
    COVERAGE_WEIGHT = 0.25
    TRACEABILITY_WEIGHT = 0.20
    OWNERSHIP_WEIGHT = 0.15
    FRESHNESS_WEIGHT = 0.10
    
    def calculate_health(
        self,
        integrity_result: IntegrityAnalysisResult,
        coverage_result: CoverageAnalysisResult,
        ownership_result: OwnershipAnalysisResult,
        traceability_result: TraceabilityAnalysisResult,
        distribution_result: DistributionAnalysisResult,
        freshness_result: FreshnessAnalysisResult
    ) -> RegistryHealthResult:
        """
        Calculate overall registry health.
        
        Args:
            integrity_result: Integrity analysis results
            coverage_result: Coverage analysis results
            ownership_result: Ownership analysis results
            traceability_result: Traceability analysis results
            distribution_result: Distribution analysis results
            freshness_result: Freshness analysis results
            
        Returns:
            RegistryHealthResult with overall score and grade
        """
        # Calculate weighted overall score
        overall_score = (
            integrity_result.score * self.INTEGRITY_WEIGHT +
            coverage_result.score * self.COVERAGE_WEIGHT +
            traceability_result.score * self.TRACEABILITY_WEIGHT +
            ownership_result.score * self.OWNERSHIP_WEIGHT +
            freshness_result.score * self.FRESHNESS_WEIGHT
        )
        
        overall_score = round(overall_score, 1)
        
        # Determine health grade
        health_grade = self._get_health_grade(overall_score)
        
        # Collect all findings
        all_findings = []
        all_findings.extend(integrity_result.findings)
        all_findings.extend(coverage_result.findings)
        all_findings.extend(ownership_result.findings)
        all_findings.extend(traceability_result.findings)
        all_findings.extend(distribution_result.findings)
        all_findings.extend(freshness_result.findings)
        
        # Count findings by severity
        critical_findings = sum(1 for f in all_findings if f.severity == "Critical")
        high_findings = sum(1 for f in all_findings if f.severity == "High")
        
        # Generate top recommendations
        recommendations = self._generate_recommendations(
            integrity_result,
            coverage_result,
            ownership_result,
            traceability_result,
            freshness_result,
            all_findings
        )
        
        return RegistryHealthResult(
            overall_score=overall_score,
            health_grade=health_grade,
            integrity_score=integrity_result.score,
            coverage_score=coverage_result.score,
            ownership_score=ownership_result.score,
            traceability_score=traceability_result.score,
            freshness_score=freshness_result.score,
            integrity_result=integrity_result,
            coverage_result=coverage_result,
            ownership_result=ownership_result,
            traceability_result=traceability_result,
            distribution_result=distribution_result,
            freshness_result=freshness_result,
            total_findings=len(all_findings),
            critical_findings=critical_findings,
            high_findings=high_findings,
            recommendations=recommendations,
            analyzed_at=datetime.utcnow()
        )
    
    def _get_health_grade(self, score: float) -> str:
        """
        Convert score to letter grade.
        
        Args:
            score: Overall health score (0-100)
            
        Returns:
            Letter grade (A, B, C, D, F)
        """
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _generate_recommendations(
        self,
        integrity_result: IntegrityAnalysisResult,
        coverage_result: CoverageAnalysisResult,
        ownership_result: OwnershipAnalysisResult,
        traceability_result: TraceabilityAnalysisResult,
        freshness_result: FreshnessAnalysisResult,
        all_findings: list
    ) -> list:
        """
        Generate prioritized recommendations.
        
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Prioritize critical and high severity findings
        critical_findings = [f for f in all_findings if f.severity == "Critical"]
        high_findings = [f for f in all_findings if f.severity == "High"]
        
        # Add critical recommendations first
        for finding in critical_findings[:3]:  # Top 3 critical
            if finding.recommendation:
                recommendations.append(f"🔴 {finding.recommendation}")
        
        # Add high priority recommendations
        for finding in high_findings[:3]:  # Top 3 high
            if finding.recommendation and finding.recommendation not in [r[2:] for r in recommendations]:
                recommendations.append(f"🟠 {finding.recommendation}")
        
        # Add score-based recommendations
        if integrity_result.score < 70:
            recommendations.append("🟠 Focus on data integrity: Address missing required fields and duplicates.")
        
        if coverage_result.score < 70:
            recommendations.append("🟠 Improve coverage: Link impacts to stakeholders and organizational assets.")
        
        if traceability_result.score < 70:
            recommendations.append("🟠 Enhance traceability: Establish relationships between impacts and organizational elements.")
        
        if freshness_result.score < 70:
            recommendations.append("🟡 Update stale records: Review and refresh impacts not modified recently.")
        
        # Limit to top 5 recommendations
        return recommendations[:5]
