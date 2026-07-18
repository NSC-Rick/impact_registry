"""
Sensor Framework

Converts analysis results into sensor readings and signals.
"""

from analysis.analysis_models import RegistryHealthResult
from signal_center.sensor_models import (
    SensorReading, SensorStatus, Signal, SignalPriority,
    IntegritySensorReading, CoverageSensorReading,
    OwnershipSensorReading, TraceabilitySensorReading,
    DistributionSensorReading, FreshnessSensorReading
)
from typing import List


class SensorFramework:
    """
    Framework for converting analysis results into sensor readings.
    
    Sensors contain no analysis logic - they visualize analysis results.
    """
    
    @staticmethod
    def _get_status_from_score(score: float) -> SensorStatus:
        """
        Convert score to sensor status.
        
        Args:
            score: Score from 0-100
            
        Returns:
            SensorStatus
        """
        if score >= 80:
            return SensorStatus.HEALTHY
        elif score >= 60:
            return SensorStatus.WARNING
        else:
            return SensorStatus.CRITICAL
    
    @staticmethod
    def _get_status_text(status: SensorStatus, score: float) -> str:
        """Get human-readable status text"""
        if status == SensorStatus.HEALTHY:
            return "Healthy"
        elif status == SensorStatus.WARNING:
            return "Needs Attention"
        elif status == SensorStatus.CRITICAL:
            return "Critical"
        else:
            return "Unknown"
    
    @staticmethod
    def _convert_finding_to_signal(finding) -> Signal:
        """Convert analysis finding to signal"""
        priority_map = {
            "Critical": SignalPriority.CRITICAL,
            "High": SignalPriority.HIGH,
            "Medium": SignalPriority.MEDIUM,
            "Low": SignalPriority.LOW,
            "Info": SignalPriority.INFO
        }
        
        return Signal(
            priority=priority_map.get(finding.severity, SignalPriority.INFO),
            title=finding.title,
            description=finding.description,
            action=finding.recommendation,
            affected_count=len(finding.affected_records) if finding.affected_records else 0,
            affected_records=finding.affected_records if finding.affected_records else [],
            drill_down_page="Enrich"
        )
    
    @classmethod
    def create_integrity_sensor(cls, health_result: RegistryHealthResult) -> IntegritySensorReading:
        """
        Create integrity sensor reading.
        
        Args:
            health_result: Complete registry health result
            
        Returns:
            IntegritySensorReading
        """
        integrity = health_result.integrity_result
        score = integrity.score
        status = cls._get_status_from_score(score)
        
        # Convert findings to signals
        signals = [cls._convert_finding_to_signal(f) for f in integrity.findings]
        
        # Calculate metrics
        missing_fields_count = sum(integrity.missing_required_fields.values())
        duplicate_count = len(integrity.duplicate_impacts)
        invalid_values_count = len(integrity.invalid_values)
        
        return IntegritySensorReading(
            sensor_name="Data Integrity",
            score=score,
            status=status,
            status_text=cls._get_status_text(status, score),
            signals=signals,
            metrics={
                'total_records': integrity.total_records,
                'clean_records': integrity.total_records - integrity.records_with_issues,
                'issues_found': integrity.records_with_issues
            },
            total_records=integrity.total_records,
            records_with_issues=integrity.records_with_issues,
            missing_fields_count=missing_fields_count,
            duplicate_count=duplicate_count,
            invalid_values_count=invalid_values_count
        )
    
    @classmethod
    def create_coverage_sensor(cls, health_result: RegistryHealthResult) -> CoverageSensorReading:
        """Create coverage sensor reading"""
        coverage = health_result.coverage_result
        score = coverage.score
        status = cls._get_status_from_score(score)
        
        signals = [cls._convert_finding_to_signal(f) for f in coverage.findings]
        
        # Calculate coverage percentage
        if coverage.total_impacts > 0:
            coverage_pct = (coverage.impacts_with_stakeholders / coverage.total_impacts) * 100
        else:
            coverage_pct = 0.0
        
        return CoverageSensorReading(
            sensor_name="Coverage",
            score=score,
            status=status,
            status_text=cls._get_status_text(status, score),
            signals=signals,
            metrics={
                'stakeholder_coverage': coverage.impacts_with_stakeholders,
                'org_unit_coverage': coverage.impacts_with_org_units,
                'process_coverage': coverage.impacts_with_processes
            },
            total_impacts=coverage.total_impacts,
            impacts_with_stakeholders=coverage.impacts_with_stakeholders,
            impacts_with_org_units=coverage.impacts_with_org_units,
            uncovered_stakeholders=coverage.uncovered_stakeholders,
            uncovered_org_units=coverage.uncovered_org_units,
            coverage_percentage=round(coverage_pct, 1)
        )
    
    @classmethod
    def create_ownership_sensor(cls, health_result: RegistryHealthResult) -> OwnershipSensorReading:
        """Create ownership sensor reading"""
        ownership = health_result.ownership_result
        score = ownership.score
        status = cls._get_status_from_score(score)
        
        signals = [cls._convert_finding_to_signal(f) for f in ownership.findings]
        
        # Calculate ownership percentage
        if ownership.total_impacts > 0:
            ownership_pct = ((ownership.total_impacts - ownership.impacts_without_owner) / ownership.total_impacts) * 100
        else:
            ownership_pct = 100.0
        
        return OwnershipSensorReading(
            sensor_name="Ownership",
            score=score,
            status=status,
            status_text=cls._get_status_text(status, score),
            signals=signals,
            metrics={
                'assigned': ownership.total_impacts - ownership.impacts_without_owner,
                'unassigned': ownership.impacts_without_owner
            },
            total_impacts=ownership.total_impacts,
            impacts_without_owner=ownership.impacts_without_owner,
            ownership_percentage=round(ownership_pct, 1)
        )
    
    @classmethod
    def create_traceability_sensor(cls, health_result: RegistryHealthResult) -> TraceabilitySensorReading:
        """Create traceability sensor reading"""
        traceability = health_result.traceability_result
        score = traceability.score
        status = cls._get_status_from_score(score)
        
        signals = [cls._convert_finding_to_signal(f) for f in traceability.findings]
        
        # Calculate traceability percentage
        if traceability.total_impacts > 0:
            trace_pct = ((traceability.total_impacts - traceability.impacts_without_stakeholders) / traceability.total_impacts) * 100
        else:
            trace_pct = 100.0
        
        return TraceabilitySensorReading(
            sensor_name="Traceability",
            score=score,
            status=status,
            status_text=cls._get_status_text(status, score),
            signals=signals,
            metrics={
                'with_stakeholders': traceability.total_impacts - traceability.impacts_without_stakeholders,
                'with_assets': traceability.total_impacts - traceability.impacts_without_assets,
                'orphaned': len(traceability.orphaned_impact_ids)
            },
            total_impacts=traceability.total_impacts,
            impacts_without_stakeholders=traceability.impacts_without_stakeholders,
            impacts_without_assets=traceability.impacts_without_assets,
            orphaned_impacts=len(traceability.orphaned_impact_ids),
            traceability_percentage=round(trace_pct, 1)
        )
    
    @classmethod
    def create_distribution_sensor(cls, health_result: RegistryHealthResult) -> DistributionSensorReading:
        """Create distribution sensor reading"""
        distribution = health_result.distribution_result
        
        # Distribution sensor doesn't have a score, use 100 as default
        score = 100.0
        status = SensorStatus.HEALTHY
        
        signals = [cls._convert_finding_to_signal(f) for f in distribution.findings]
        
        return DistributionSensorReading(
            sensor_name="Distribution",
            score=score,
            status=status,
            status_text="Informational",
            signals=signals,
            metrics={
                'total': distribution.total_impacts,
                'hotspots': len(distribution.hotspots)
            },
            total_impacts=distribution.total_impacts,
            by_severity=distribution.by_severity,
            by_category=distribution.by_category,
            by_status=distribution.by_status,
            hotspots=distribution.hotspots
        )
    
    @classmethod
    def create_freshness_sensor(cls, health_result: RegistryHealthResult) -> FreshnessSensorReading:
        """Create freshness sensor reading"""
        freshness = health_result.freshness_result
        score = freshness.score
        status = cls._get_status_from_score(score)
        
        signals = [cls._convert_finding_to_signal(f) for f in freshness.findings]
        
        # Calculate freshness percentage
        if freshness.total_impacts > 0:
            fresh_pct = ((freshness.total_impacts - freshness.stale_impacts) / freshness.total_impacts) * 100
        else:
            fresh_pct = 100.0
        
        return FreshnessSensorReading(
            sensor_name="Freshness",
            score=score,
            status=status,
            status_text=cls._get_status_text(status, score),
            signals=signals,
            metrics={
                'recent_activity': freshness.recently_modified,
                'stale': freshness.stale_impacts,
                'average_age': freshness.average_age_days
            },
            total_impacts=freshness.total_impacts,
            recently_created=freshness.recently_created,
            recently_modified=freshness.recently_modified,
            stale_impacts=freshness.stale_impacts,
            average_age_days=freshness.average_age_days,
            freshness_percentage=round(fresh_pct, 1)
        )
