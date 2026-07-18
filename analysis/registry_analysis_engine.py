"""
Registry Analysis Engine

Main orchestrator for registry quality and health analysis.
"""

from sqlalchemy.orm import Session
from analysis.integrity_analyzer import IntegrityAnalyzer
from analysis.coverage_analyzer import CoverageAnalyzer
from analysis.ownership_analyzer import OwnershipAnalyzer
from analysis.traceability_analyzer import TraceabilityAnalyzer
from analysis.distribution_analyzer import DistributionAnalyzer
from analysis.freshness_analyzer import FreshnessAnalyzer
from analysis.health_calculator import HealthCalculator
from analysis.analysis_models import RegistryHealthResult


class RegistryAnalysisEngine:
    """
    Main engine for analyzing registry quality and health.
    
    Coordinates all analysis modules and produces comprehensive
    registry health assessment.
    
    This engine is UI-agnostic and returns structured results
    that can be consumed by:
    - Analyze page
    - Future Signal Center
    - Reports
    - Export functions
    - API endpoints
    """
    
    def __init__(self, session: Session):
        """
        Initialize analysis engine.
        
        Args:
            session: SQLAlchemy session for database access
        """
        self.session = session
        
        # Initialize analyzers
        self.integrity_analyzer = IntegrityAnalyzer(session)
        self.coverage_analyzer = CoverageAnalyzer(session)
        self.ownership_analyzer = OwnershipAnalyzer(session)
        self.traceability_analyzer = TraceabilityAnalyzer(session)
        self.distribution_analyzer = DistributionAnalyzer(session)
        self.freshness_analyzer = FreshnessAnalyzer(session)
        
        # Initialize health calculator
        self.health_calculator = HealthCalculator()
    
    def analyze_registry(self) -> RegistryHealthResult:
        """
        Perform comprehensive registry analysis.
        
        Executes all analysis modules and calculates overall health.
        
        Returns:
            RegistryHealthResult with complete analysis
        """
        # Run all analyses
        integrity_result = self.integrity_analyzer.analyze()
        coverage_result = self.coverage_analyzer.analyze()
        ownership_result = self.ownership_analyzer.analyze()
        traceability_result = self.traceability_analyzer.analyze()
        distribution_result = self.distribution_analyzer.analyze()
        freshness_result = self.freshness_analyzer.analyze()
        
        # Calculate overall health
        health_result = self.health_calculator.calculate_health(
            integrity_result=integrity_result,
            coverage_result=coverage_result,
            ownership_result=ownership_result,
            traceability_result=traceability_result,
            distribution_result=distribution_result,
            freshness_result=freshness_result
        )
        
        return health_result
    
    def analyze_integrity(self):
        """Run integrity analysis only"""
        return self.integrity_analyzer.analyze()
    
    def analyze_coverage(self):
        """Run coverage analysis only"""
        return self.coverage_analyzer.analyze()
    
    def analyze_ownership(self):
        """Run ownership analysis only"""
        return self.ownership_analyzer.analyze()
    
    def analyze_traceability(self):
        """Run traceability analysis only"""
        return self.traceability_analyzer.analyze()
    
    def analyze_distribution(self):
        """Run distribution analysis only"""
        return self.distribution_analyzer.analyze()
    
    def analyze_freshness(self):
        """Run freshness analysis only"""
        return self.freshness_analyzer.analyze()
