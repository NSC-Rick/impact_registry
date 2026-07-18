"""
Signal Center Dashboard

Orchestrates all sensors and creates the complete dashboard state.
"""

from sqlalchemy.orm import Session
from analysis.registry_analysis_engine import RegistryAnalysisEngine
from signal_center.sensor_framework import SensorFramework
from signal_center.sensor_models import (
    SignalCenterDashboard, SensorStatus, SignalPriority
)


class SignalDashboard:
    """
    Signal Center Dashboard orchestrator.
    
    Coordinates analysis engine and sensor framework to produce
    the complete Signal Center dashboard state.
    """
    
    def __init__(self, session: Session):
        """
        Initialize Signal Dashboard.
        
        Args:
            session: SQLAlchemy session
        """
        self.session = session
        self.analysis_engine = RegistryAnalysisEngine(session)
        self.sensor_framework = SensorFramework()
    
    def generate_dashboard(self) -> SignalCenterDashboard:
        """
        Generate complete Signal Center dashboard.
        
        Returns:
            SignalCenterDashboard with all sensor readings and signals
        """
        # Run complete registry analysis
        health_result = self.analysis_engine.analyze_registry()
        
        # Create sensor readings
        integrity_reading = self.sensor_framework.create_integrity_sensor(health_result)
        coverage_reading = self.sensor_framework.create_coverage_sensor(health_result)
        ownership_reading = self.sensor_framework.create_ownership_sensor(health_result)
        traceability_reading = self.sensor_framework.create_traceability_sensor(health_result)
        distribution_reading = self.sensor_framework.create_distribution_sensor(health_result)
        freshness_reading = self.sensor_framework.create_freshness_sensor(health_result)
        
        # Collect all signals
        all_signals = []
        all_signals.extend(integrity_reading.signals)
        all_signals.extend(coverage_reading.signals)
        all_signals.extend(ownership_reading.signals)
        all_signals.extend(traceability_reading.signals)
        all_signals.extend(distribution_reading.signals)
        all_signals.extend(freshness_reading.signals)
        
        # Filter signals by priority
        critical_signals = [s for s in all_signals if s.priority == SignalPriority.CRITICAL]
        high_signals = [s for s in all_signals if s.priority == SignalPriority.HIGH]
        
        # Determine overall registry health status
        registry_status = self._determine_registry_status(health_result.overall_score)
        
        return SignalCenterDashboard(
            registry_health_score=health_result.overall_score,
            registry_health_grade=health_result.health_grade,
            registry_health_status=registry_status,
            integrity_reading=integrity_reading,
            coverage_reading=coverage_reading,
            ownership_reading=ownership_reading,
            traceability_reading=traceability_reading,
            distribution_reading=distribution_reading,
            freshness_reading=freshness_reading,
            all_signals=all_signals,
            critical_signals=critical_signals,
            high_signals=high_signals,
            total_signal_count=len(all_signals),
            critical_signal_count=len(critical_signals),
            high_signal_count=len(high_signals)
        )
    
    def _determine_registry_status(self, score: float) -> SensorStatus:
        """Determine overall registry status from score"""
        if score >= 80:
            return SensorStatus.HEALTHY
        elif score >= 60:
            return SensorStatus.WARNING
        else:
            return SensorStatus.CRITICAL
