"""
Starter Library Data Models

Defines the structure for starter libraries that provide baseline content
for new Impact Registry projects.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class LibraryStakeholderGroup:
    """Stakeholder group template"""
    name: str
    description: str = ""
    size: int = 0
    influence: str = ""
    notes: str = ""


@dataclass
class LibraryOrganizationUnit:
    """Organization unit template"""
    name: str
    description: str = ""
    parent_unit: str = ""
    head_of_unit: str = ""
    notes: str = ""


@dataclass
class LibraryBusinessProcess:
    """Business process template"""
    name: str
    description: str = ""
    process_owner: str = ""
    criticality: str = ""
    notes: str = ""


@dataclass
class LibrarySystem:
    """System template"""
    name: str
    description: str = ""
    system_owner: str = ""
    vendor: str = ""
    criticality: str = ""
    notes: str = ""


@dataclass
class LibraryPolicy:
    """Policy template"""
    name: str
    description: str = ""
    policy_owner: str = ""
    notes: str = ""


@dataclass
class LibraryImpact:
    """Change impact template"""
    impact_number: str
    title: str
    description: str
    area_of_change: str = ""
    category: str = ""
    severity: str = ""
    likelihood: str = ""
    notes: str = ""
    stakeholder_groups: List[str] = field(default_factory=list)  # Names, not IDs
    organization_units: List[str] = field(default_factory=list)
    business_processes: List[str] = field(default_factory=list)
    systems: List[str] = field(default_factory=list)
    policies: List[str] = field(default_factory=list)


@dataclass
class StarterLibrary:
    """
    Complete starter library definition.
    
    Contains all baseline content for a new project.
    """
    id: str
    name: str
    description: str
    industry: str = ""
    project_type: str = ""
    version: str = "1.0"
    created_at: str = ""
    updated_at: str = ""
    display_order: int = 999  # Lower numbers appear first, 999 = default/unordered
    
    # Enterprise Assets
    stakeholder_groups: List[LibraryStakeholderGroup] = field(default_factory=list)
    organization_units: List[LibraryOrganizationUnit] = field(default_factory=list)
    business_processes: List[LibraryBusinessProcess] = field(default_factory=list)
    systems: List[LibrarySystem] = field(default_factory=list)
    policies: List[LibraryPolicy] = field(default_factory=list)
    
    # Change Impacts
    impacts: List[LibraryImpact] = field(default_factory=list)
    
    # Metadata
    categories: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StarterLibrary':
        """Create from dictionary"""
        # Convert nested dictionaries to dataclass instances
        stakeholder_groups = [LibraryStakeholderGroup(**sg) for sg in data.get('stakeholder_groups', [])]
        organization_units = [LibraryOrganizationUnit(**ou) for ou in data.get('organization_units', [])]
        business_processes = [LibraryBusinessProcess(**bp) for bp in data.get('business_processes', [])]
        systems = [LibrarySystem(**sys) for sys in data.get('systems', [])]
        policies = [LibraryPolicy(**pol) for pol in data.get('policies', [])]
        impacts = [LibraryImpact(**imp) for imp in data.get('impacts', [])]
        
        return cls(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            industry=data.get('industry', ''),
            project_type=data.get('project_type', ''),
            version=data.get('version', '1.0'),
            created_at=data.get('created_at', ''),
            updated_at=data.get('updated_at', ''),
            display_order=data.get('display_order', 999),
            stakeholder_groups=stakeholder_groups,
            organization_units=organization_units,
            business_processes=business_processes,
            systems=systems,
            policies=policies,
            impacts=impacts,
            categories=data.get('categories', [])
        )
    
    def get_summary(self) -> Dict:
        """Get summary statistics for the library"""
        return {
            'stakeholder_groups': len(self.stakeholder_groups),
            'organization_units': len(self.organization_units),
            'business_processes': len(self.business_processes),
            'systems': len(self.systems),
            'policies': len(self.policies),
            'impacts': len(self.impacts),
            'categories': len(self.categories)
        }
