"""
Starter Library Service

Manages loading, creating, and applying starter libraries to new projects.
"""

import json
import os
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from libraries.starter_library_models import StarterLibrary
from database.schema import (
    StakeholderGroup, OrganizationUnit, BusinessProcess,
    System, Policy, Impact
)


class StarterLibraryService:
    """
    Service for managing starter libraries.
    
    Handles:
    - Loading libraries from JSON files
    - Listing available libraries
    - Applying libraries to new projects
    - Creating/exporting libraries
    """
    
    LIBRARIES_DIR = "libraries/templates"
    
    def __init__(self):
        """Initialize starter library service"""
        self._ensure_libraries_dir()
    
    def _ensure_libraries_dir(self) -> None:
        """Ensure libraries directory exists"""
        Path(self.LIBRARIES_DIR).mkdir(parents=True, exist_ok=True)
    
    def list_libraries(self) -> List[StarterLibrary]:
        """
        List all available starter libraries.
        
        Returns:
            List of StarterLibrary objects
        """
        libraries = []
        libraries_path = Path(self.LIBRARIES_DIR)
        
        for json_file in libraries_path.glob("*.json"):
            try:
                library = self.load_library(json_file.stem)
                if library:
                    libraries.append(library)
            except Exception as e:
                print(f"Error loading library {json_file}: {e}")
        
        return libraries
    
    def load_library(self, library_id: str) -> Optional[StarterLibrary]:
        """
        Load a starter library by ID.
        
        Args:
            library_id: Library identifier (filename without .json)
            
        Returns:
            StarterLibrary object or None if not found
        """
        library_path = Path(self.LIBRARIES_DIR) / f"{library_id}.json"
        
        if not library_path.exists():
            return None
        
        try:
            with open(library_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return StarterLibrary.from_dict(data)
        except Exception as e:
            print(f"Error loading library {library_id}: {e}")
            return None
    
    def save_library(self, library: StarterLibrary) -> Tuple[bool, str]:
        """
        Save a starter library to disk.
        
        Args:
            library: StarterLibrary object to save
            
        Returns:
            Tuple of (success, message)
        """
        try:
            library_path = Path(self.LIBRARIES_DIR) / f"{library.id}.json"
            
            # Update timestamp
            library.updated_at = datetime.utcnow().isoformat()
            
            with open(library_path, 'w', encoding='utf-8') as f:
                json.dump(library.to_dict(), f, indent=2, ensure_ascii=False)
            
            return True, f"Library '{library.name}' saved successfully"
        
        except Exception as e:
            return False, f"Error saving library: {str(e)}"
    
    def apply_library_to_project(
        self,
        library: StarterLibrary,
        session: Session
    ) -> Tuple[bool, str, Dict]:
        """
        Apply a starter library to a new project.
        
        Copies all library content into the project database.
        
        Args:
            library: StarterLibrary to apply
            session: SQLAlchemy session for the project database
            
        Returns:
            Tuple of (success, message, stats)
        """
        try:
            stats = {
                'stakeholder_groups': 0,
                'organization_units': 0,
                'business_processes': 0,
                'systems': 0,
                'policies': 0,
                'impacts': 0
            }
            
            # Track name-to-ID mappings for relationships
            sg_map = {}  # stakeholder group name -> ID
            ou_map = {}  # organization unit name -> ID
            bp_map = {}  # business process name -> ID
            sys_map = {}  # system name -> ID
            pol_map = {}  # policy name -> ID
            
            # Import Stakeholder Groups
            for sg_template in library.stakeholder_groups:
                sg = StakeholderGroup(
                    name=sg_template.name,
                    description=sg_template.description,
                    size=sg_template.size,
                    influence=sg_template.influence,
                    notes=sg_template.notes
                )
                session.add(sg)
                session.flush()  # Get ID
                sg_map[sg_template.name] = sg.id
                stats['stakeholder_groups'] += 1
            
            # Import Organization Units
            for ou_template in library.organization_units:
                ou = OrganizationUnit(
                    name=ou_template.name,
                    description=ou_template.description,
                    parent_unit=ou_template.parent_unit,
                    head_of_unit=ou_template.head_of_unit,
                    notes=ou_template.notes
                )
                session.add(ou)
                session.flush()
                ou_map[ou_template.name] = ou.id
                stats['organization_units'] += 1
            
            # Import Business Processes
            for bp_template in library.business_processes:
                bp = BusinessProcess(
                    name=bp_template.name,
                    description=bp_template.description,
                    process_owner=bp_template.process_owner,
                    criticality=bp_template.criticality,
                    notes=bp_template.notes
                )
                session.add(bp)
                session.flush()
                bp_map[bp_template.name] = bp.id
                stats['business_processes'] += 1
            
            # Import Systems
            for sys_template in library.systems:
                sys = System(
                    name=sys_template.name,
                    description=sys_template.description,
                    system_owner=sys_template.system_owner,
                    vendor=sys_template.vendor,
                    criticality=sys_template.criticality,
                    notes=sys_template.notes
                )
                session.add(sys)
                session.flush()
                sys_map[sys_template.name] = sys.id
                stats['systems'] += 1
            
            # Import Policies
            for pol_template in library.policies:
                pol = Policy(
                    name=pol_template.name,
                    description=pol_template.description,
                    policy_owner=pol_template.policy_owner,
                    notes=pol_template.notes
                )
                session.add(pol)
                session.flush()
                pol_map[pol_template.name] = pol.id
                stats['policies'] += 1
            
            # Import Impacts with relationships
            for imp_template in library.impacts:
                impact = Impact(
                    impact_number=imp_template.impact_number,
                    title=imp_template.title,
                    description=imp_template.description,
                    area_of_change=imp_template.area_of_change,
                    category=imp_template.category,
                    severity=imp_template.severity,
                    likelihood=imp_template.likelihood,
                    notes=imp_template.notes,
                    status='Draft'
                )
                session.add(impact)
                session.flush()
                
                # Add relationships
                for sg_name in imp_template.stakeholder_groups:
                    if sg_name in sg_map:
                        sg = session.query(StakeholderGroup).filter_by(id=sg_map[sg_name]).first()
                        if sg:
                            impact.stakeholder_groups.append(sg)
                
                for ou_name in imp_template.organization_units:
                    if ou_name in ou_map:
                        ou = session.query(OrganizationUnit).filter_by(id=ou_map[ou_name]).first()
                        if ou:
                            impact.organization_units.append(ou)
                
                for bp_name in imp_template.business_processes:
                    if bp_name in bp_map:
                        bp = session.query(BusinessProcess).filter_by(id=bp_map[bp_name]).first()
                        if bp:
                            impact.business_processes.append(bp)
                
                for sys_name in imp_template.systems:
                    if sys_name in sys_map:
                        sys_obj = session.query(System).filter_by(id=sys_map[sys_name]).first()
                        if sys_obj:
                            impact.systems.append(sys_obj)
                
                for pol_name in imp_template.policies:
                    if pol_name in pol_map:
                        pol = session.query(Policy).filter_by(id=pol_map[pol_name]).first()
                        if pol:
                            impact.policies.append(pol)
                
                stats['impacts'] += 1
            
            # Commit all changes
            session.commit()
            
            return True, f"Library '{library.name}' applied successfully", stats
        
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Library application error:\n{error_details}")  # Log for developers
            session.rollback()
            return False, f"Error applying library: {str(e)}", {}
    
    def create_library_from_project(
        self,
        library_id: str,
        library_name: str,
        description: str,
        session: Session,
        industry: str = "",
        project_type: str = ""
    ) -> Tuple[bool, str, Optional[StarterLibrary]]:
        """
        Create a new starter library from an existing project.
        
        Args:
            library_id: Unique library identifier
            library_name: Display name
            description: Library description
            session: SQLAlchemy session for the source project
            industry: Industry classification
            project_type: Project type classification
            
        Returns:
            Tuple of (success, message, library)
        """
        try:
            from libraries.starter_library_models import (
                LibraryStakeholderGroup, LibraryOrganizationUnit,
                LibraryBusinessProcess, LibrarySystem, LibraryPolicy,
                LibraryImpact
            )
            
            # Extract stakeholder groups
            stakeholder_groups = []
            for sg in session.query(StakeholderGroup).all():
                stakeholder_groups.append(LibraryStakeholderGroup(
                    name=sg.name,
                    description=sg.description or "",
                    size=sg.size or 0,
                    influence=sg.influence or "",
                    notes=sg.notes or ""
                ))
            
            # Extract organization units
            organization_units = []
            for ou in session.query(OrganizationUnit).all():
                organization_units.append(LibraryOrganizationUnit(
                    name=ou.name,
                    description=ou.description or "",
                    parent_unit=ou.parent_unit or "",
                    head_of_unit=ou.head_of_unit or "",
                    notes=ou.notes or ""
                ))
            
            # Extract business processes
            business_processes = []
            for bp in session.query(BusinessProcess).all():
                business_processes.append(LibraryBusinessProcess(
                    name=bp.name,
                    description=bp.description or "",
                    process_owner=bp.process_owner or "",
                    criticality=bp.criticality or "",
                    notes=bp.notes or ""
                ))
            
            # Extract systems
            systems = []
            for sys in session.query(System).all():
                systems.append(LibrarySystem(
                    name=sys.name,
                    description=sys.description or "",
                    system_owner=sys.system_owner or "",
                    vendor=sys.vendor or "",
                    criticality=sys.criticality or "",
                    notes=sys.notes or ""
                ))
            
            # Extract policies
            policies = []
            for pol in session.query(Policy).all():
                policies.append(LibraryPolicy(
                    name=pol.name,
                    description=pol.description or "",
                    policy_owner=pol.policy_owner or "",
                    notes=pol.notes or ""
                ))
            
            # Extract impacts
            impacts = []
            for imp in session.query(Impact).all():
                impacts.append(LibraryImpact(
                    impact_number=imp.impact_number,
                    title=imp.title or "",
                    description=imp.description,
                    area_of_change=imp.area_of_change or "",
                    category=imp.category or "",
                    severity=imp.severity or "",
                    likelihood=imp.likelihood or "",
                    notes=imp.notes or "",
                    stakeholder_groups=[sg.name for sg in imp.stakeholder_groups],
                    organization_units=[ou.name for ou in imp.organization_units],
                    business_processes=[bp.name for bp in imp.business_processes],
                    systems=[sys.name for sys in imp.systems],
                    policies=[pol.name for pol in imp.policies]
                ))
            
            # Extract unique categories
            categories = list(set(imp.category for imp in session.query(Impact).all() if imp.category))
            
            # Create library
            library = StarterLibrary(
                id=library_id,
                name=library_name,
                description=description,
                industry=industry,
                project_type=project_type,
                version="1.0",
                created_at=datetime.utcnow().isoformat(),
                updated_at=datetime.utcnow().isoformat(),
                stakeholder_groups=stakeholder_groups,
                organization_units=organization_units,
                business_processes=business_processes,
                systems=systems,
                policies=policies,
                impacts=impacts,
                categories=categories
            )
            
            # Save library
            success, message = self.save_library(library)
            
            if success:
                return True, message, library
            else:
                return False, message, None
        
        except Exception as e:
            return False, f"Error creating library: {str(e)}", None
