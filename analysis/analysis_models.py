"""
Analysis Models

Data structures for registry analysis results.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class AnalysisFinding:
    """Individual analysis finding"""
    severity: str  # Critical, High, Medium, Low, Info
    category: str
    title: str
    description: str
    affected_records: List[int] = field(default_factory=list)
    recommendation: str = ""


@dataclass
class IntegrityAnalysisResult:
    """Data integrity analysis results"""
    score: float  # 0-100
    total_records: int
    records_with_issues: int
    findings: List[AnalysisFinding] = field(default_factory=list)
    missing_required_fields: Dict[str, int] = field(default_factory=dict)
    duplicate_impacts: List[Dict] = field(default_factory=list)
    duplicate_assets: Dict[str, List[Dict]] = field(default_factory=dict)
    invalid_values: List[Dict] = field(default_factory=list)


@dataclass
class CoverageAnalysisResult:
    """Coverage analysis results"""
    score: float  # 0-100
    total_impacts: int
    impacts_with_stakeholders: int
    impacts_with_org_units: int
    impacts_with_processes: int
    impacts_with_systems: int
    stakeholder_coverage: Dict[str, int] = field(default_factory=dict)
    org_unit_coverage: Dict[str, int] = field(default_factory=dict)
    process_coverage: Dict[str, int] = field(default_factory=dict)
    uncovered_stakeholders: List[str] = field(default_factory=list)
    uncovered_org_units: List[str] = field(default_factory=list)
    findings: List[AnalysisFinding] = field(default_factory=list)


@dataclass
class OwnershipAnalysisResult:
    """Ownership analysis results"""
    score: float  # 0-100
    total_impacts: int
    impacts_without_owner: int
    impacts_without_lead: int
    unassigned_impact_ids: List[int] = field(default_factory=list)
    findings: List[AnalysisFinding] = field(default_factory=list)


@dataclass
class TraceabilityAnalysisResult:
    """Traceability analysis results"""
    score: float  # 0-100
    total_impacts: int
    impacts_without_stakeholders: int
    impacts_without_assets: int
    impacts_without_category: int
    orphaned_impact_ids: List[int] = field(default_factory=list)
    findings: List[AnalysisFinding] = field(default_factory=list)


@dataclass
class DistributionAnalysisResult:
    """Distribution analysis results"""
    total_impacts: int
    by_severity: Dict[str, int] = field(default_factory=dict)
    by_category: Dict[str, int] = field(default_factory=dict)
    by_status: Dict[str, int] = field(default_factory=dict)
    by_area_of_change: Dict[str, int] = field(default_factory=dict)
    hotspots: List[Dict] = field(default_factory=list)
    findings: List[AnalysisFinding] = field(default_factory=list)


@dataclass
class FreshnessAnalysisResult:
    """Freshness analysis results"""
    score: float  # 0-100
    total_impacts: int
    recently_created: int  # Last 7 days
    recently_modified: int  # Last 7 days
    stale_impacts: int  # Not modified in 30+ days
    stale_impact_ids: List[int] = field(default_factory=list)
    average_age_days: float = 0.0
    findings: List[AnalysisFinding] = field(default_factory=list)


@dataclass
class RegistryHealthResult:
    """Overall registry health assessment"""
    overall_score: float  # 0-100
    health_grade: str  # A, B, C, D, F
    integrity_score: float
    coverage_score: float
    ownership_score: float
    traceability_score: float
    freshness_score: float
    
    # Detailed results
    integrity_result: Optional[IntegrityAnalysisResult] = None
    coverage_result: Optional[CoverageAnalysisResult] = None
    ownership_result: Optional[OwnershipAnalysisResult] = None
    traceability_result: Optional[TraceabilityAnalysisResult] = None
    distribution_result: Optional[DistributionAnalysisResult] = None
    freshness_result: Optional[FreshnessAnalysisResult] = None
    
    # Summary
    total_findings: int = 0
    critical_findings: int = 0
    high_findings: int = 0
    recommendations: List[str] = field(default_factory=list)
    
    analyzed_at: datetime = field(default_factory=datetime.utcnow)
    
    def get_health_grade(self) -> str:
        """Calculate health grade from score"""
        if self.overall_score >= 90:
            return "A"
        elif self.overall_score >= 80:
            return "B"
        elif self.overall_score >= 70:
            return "C"
        elif self.overall_score >= 60:
            return "D"
        else:
            return "F"
