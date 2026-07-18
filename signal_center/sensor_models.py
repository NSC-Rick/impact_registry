"""
Signal Center Sensor Models

Data structures for sensors and signals.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class SensorStatus(Enum):
    """Sensor health status"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class SignalPriority(Enum):
    """Signal priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Signal:
    """Individual signal from a sensor"""
    priority: SignalPriority
    title: str
    description: str
    action: str = ""
    affected_count: int = 0
    affected_records: List[int] = field(default_factory=list)
    drill_down_page: str = ""


@dataclass
class SensorReading:
    """
    Base sensor reading.
    
    All sensors produce a reading with:
    - Score (0-100)
    - Status (healthy/warning/critical)
    - Signals (actionable items)
    - Metrics (key numbers)
    """
    sensor_name: str
    score: float  # 0-100
    status: SensorStatus
    status_text: str
    signals: List[Signal] = field(default_factory=list)
    metrics: Dict[str, any] = field(default_factory=dict)
    
    def get_status_color(self) -> str:
        """Get color for status"""
        if self.status == SensorStatus.HEALTHY:
            return "green"
        elif self.status == SensorStatus.WARNING:
            return "orange"
        elif self.status == SensorStatus.CRITICAL:
            return "red"
        else:
            return "gray"
    
    def get_status_emoji(self) -> str:
        """Get emoji for status"""
        if self.status == SensorStatus.HEALTHY:
            return "✅"
        elif self.status == SensorStatus.WARNING:
            return "⚠️"
        elif self.status == SensorStatus.CRITICAL:
            return "🔴"
        else:
            return "❓"


@dataclass
class IntegritySensorReading(SensorReading):
    """Data integrity sensor reading"""
    total_records: int = 0
    records_with_issues: int = 0
    missing_fields_count: int = 0
    duplicate_count: int = 0
    invalid_values_count: int = 0


@dataclass
class CoverageSensorReading(SensorReading):
    """Coverage sensor reading"""
    total_impacts: int = 0
    impacts_with_stakeholders: int = 0
    impacts_with_org_units: int = 0
    uncovered_stakeholders: List[str] = field(default_factory=list)
    uncovered_org_units: List[str] = field(default_factory=list)
    coverage_percentage: float = 0.0


@dataclass
class OwnershipSensorReading(SensorReading):
    """Ownership sensor reading"""
    total_impacts: int = 0
    impacts_without_owner: int = 0
    ownership_percentage: float = 0.0


@dataclass
class TraceabilitySensorReading(SensorReading):
    """Traceability sensor reading"""
    total_impacts: int = 0
    impacts_without_stakeholders: int = 0
    impacts_without_assets: int = 0
    orphaned_impacts: int = 0
    traceability_percentage: float = 0.0


@dataclass
class DistributionSensorReading(SensorReading):
    """Distribution sensor reading"""
    total_impacts: int = 0
    by_severity: Dict[str, int] = field(default_factory=dict)
    by_category: Dict[str, int] = field(default_factory=dict)
    by_status: Dict[str, int] = field(default_factory=dict)
    hotspots: List[Dict] = field(default_factory=list)


@dataclass
class FreshnessSensorReading(SensorReading):
    """Freshness sensor reading"""
    total_impacts: int = 0
    recently_created: int = 0
    recently_modified: int = 0
    stale_impacts: int = 0
    average_age_days: float = 0.0
    freshness_percentage: float = 0.0


@dataclass
class SignalCenterDashboard:
    """Complete Signal Center dashboard state"""
    registry_health_score: float
    registry_health_grade: str
    registry_health_status: SensorStatus
    
    integrity_reading: IntegritySensorReading
    coverage_reading: CoverageSensorReading
    ownership_reading: OwnershipSensorReading
    traceability_reading: TraceabilitySensorReading
    distribution_reading: DistributionSensorReading
    freshness_reading: FreshnessSensorReading
    
    all_signals: List[Signal] = field(default_factory=list)
    critical_signals: List[Signal] = field(default_factory=list)
    high_signals: List[Signal] = field(default_factory=list)
    
    total_signal_count: int = 0
    critical_signal_count: int = 0
    high_signal_count: int = 0
