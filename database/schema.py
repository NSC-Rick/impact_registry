from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os
import json

Base = declarative_base()

impact_stakeholder_groups = Table(
    'impact_stakeholder_groups',
    Base.metadata,
    Column('impact_id', Integer, ForeignKey('impacts.id'), primary_key=True),
    Column('stakeholder_group_id', Integer, ForeignKey('stakeholder_groups.id'), primary_key=True)
)

impact_organization_units = Table(
    'impact_organization_units',
    Base.metadata,
    Column('impact_id', Integer, ForeignKey('impacts.id'), primary_key=True),
    Column('organization_unit_id', Integer, ForeignKey('organization_units.id'), primary_key=True)
)

impact_business_processes = Table(
    'impact_business_processes',
    Base.metadata,
    Column('impact_id', Integer, ForeignKey('impacts.id'), primary_key=True),
    Column('business_process_id', Integer, ForeignKey('business_processes.id'), primary_key=True)
)

impact_systems = Table(
    'impact_systems',
    Base.metadata,
    Column('impact_id', Integer, ForeignKey('impacts.id'), primary_key=True),
    Column('system_id', Integer, ForeignKey('systems.id'), primary_key=True)
)

impact_policies = Table(
    'impact_policies',
    Base.metadata,
    Column('impact_id', Integer, ForeignKey('impacts.id'), primary_key=True),
    Column('policy_id', Integer, ForeignKey('policies.id'), primary_key=True)
)

class ProjectMetadata(Base):
    """Stores project metadata within the project workspace database"""
    __tablename__ = 'project_metadata'
    
    id = Column(Integer, primary_key=True)
    project_uuid = Column(String(36), unique=True)  # UUID for project identity
    project_name = Column(String(255), nullable=False)
    client_name = Column(String(255))
    program_name = Column(String(255))
    description = Column(Text)
    sponsor = Column(String(255))
    change_manager = Column(String(255))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String(50), default='Pre-Implementation')  # Updated default
    registry_version = Column(String(50), default='1.0')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Backward compatibility alias
Project = ProjectMetadata

class Impact(Base):
    __tablename__ = 'impacts'
    
    id = Column(Integer, primary_key=True)
    impact_number = Column(String(50))
    title = Column(String(255))
    description = Column(Text, nullable=False)
    area_of_change = Column(String(100))
    notes = Column(Text)
    category = Column(String(100))
    severity = Column(String(50))
    likelihood = Column(String(50))
    readiness = Column(String(50))
    resistance = Column(String(50))
    mitigation_strategy = Column(Text)
    status = Column(String(50), default='Draft')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    stakeholder_groups = relationship('StakeholderGroup', secondary=impact_stakeholder_groups, back_populates='impacts')
    organization_units = relationship('OrganizationUnit', secondary=impact_organization_units, back_populates='impacts')
    business_processes = relationship('BusinessProcess', secondary=impact_business_processes, back_populates='impacts')
    systems = relationship('System', secondary=impact_systems, back_populates='impacts')
    policies = relationship('Policy', secondary=impact_policies, back_populates='impacts')
    source_evidences = relationship('SourceEvidence', back_populates='impact', cascade='all, delete-orphan')
    change_assets = relationship('ChangeAsset', back_populates='impact', cascade='all, delete-orphan')

class StakeholderGroup(Base):
    __tablename__ = 'stakeholder_groups'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    size = Column(Integer)
    influence = Column(String(50))
    status = Column(String(50), default='Active')
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    impacts = relationship('Impact', secondary=impact_stakeholder_groups, back_populates='stakeholder_groups')

class OrganizationUnit(Base):
    __tablename__ = 'organization_units'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    parent_unit = Column(String(255))
    head_of_unit = Column(String(255))
    status = Column(String(50), default='Active')
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    impacts = relationship('Impact', secondary=impact_organization_units, back_populates='organization_units')

class BusinessProcess(Base):
    __tablename__ = 'business_processes'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    process_owner = Column(String(255))
    criticality = Column(String(50))
    status = Column(String(50), default='Active')
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    impacts = relationship('Impact', secondary=impact_business_processes, back_populates='business_processes')

class System(Base):
    __tablename__ = 'systems'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    system_owner = Column(String(255))
    vendor = Column(String(255))
    criticality = Column(String(50))
    status = Column(String(50), default='Active')
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    impacts = relationship('Impact', secondary=impact_systems, back_populates='systems')

class Policy(Base):
    __tablename__ = 'policies'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    policy_owner = Column(String(255))
    effective_date = Column(DateTime)
    status = Column(String(50), default='Active')
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    impacts = relationship('Impact', secondary=impact_policies, back_populates='policies')

class SourceEvidence(Base):
    __tablename__ = 'source_evidences'
    
    id = Column(Integer, primary_key=True)
    impact_id = Column(Integer, ForeignKey('impacts.id'), nullable=False)
    source_type = Column(String(100))
    source_reference = Column(String(500))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    impact = relationship('Impact', back_populates='source_evidences')

class ChangeAsset(Base):
    __tablename__ = 'change_assets'
    
    id = Column(Integer, primary_key=True)
    impact_id = Column(Integer, ForeignKey('impacts.id'), nullable=False)
    asset_type = Column(String(100))
    asset_name = Column(String(255))
    description = Column(Text)
    status = Column(String(50))
    owner = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    impact = relationship('Impact', back_populates='change_assets')

def get_project_path(project_name):
    """Get the file path for a project workspace"""
    safe_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_name = safe_name.replace(' ', '_')
    return f'projects/{safe_name}.irp'

def get_engine(project_path=None):
    """
    Get database engine for a specific project workspace.
    
    Args:
        project_path: Full path to database file, or None for legacy default
        
    Returns:
        SQLAlchemy engine
    """
    if project_path is None:
        # Fallback for legacy code
        db_path = 'database/sqlite.db'
    elif os.path.isabs(project_path) or '/' in project_path or '\\' in project_path:
        # Full path or relative path with directory - use as-is
        db_path = project_path
    else:
        # Just a name - use legacy projects/ directory
        db_path = get_project_path(project_path)
    
    # Ensure parent directory exists
    db_dir = os.path.dirname(db_path)
    if db_dir:  # Only create if there's a directory component
        os.makedirs(db_dir, exist_ok=True)
        print(f"[INIT] Workspace directory: {os.path.abspath(db_dir)}")
    
    print(f"[INIT] Database path: {os.path.abspath(db_path)}")
    return create_engine(f'sqlite:///{db_path}', echo=False)

def init_db(project_path=None):
    """
    Initialize database for a project workspace.
    
    Creates complete SQLite schema and verifies all required tables exist.
    
    Args:
        project_path: Full path to database file, or None for legacy default
        
    Returns:
        SQLAlchemy engine
        
    Raises:
        RuntimeError: If schema creation fails or required tables missing
    """
    print("[INIT] Initializing database...")
    engine = get_engine(project_path)
    
    # Determine database file path for verification
    if project_path:
        db_path = project_path if os.path.isabs(project_path) or '/' in project_path or '\\' in project_path else get_project_path(project_path)
    else:
        db_path = 'database/sqlite.db'
    
    # Verify Base.metadata has tables registered
    print(f"[INIT] Base.metadata contains {len(Base.metadata.tables)} table definitions:")
    for table_name in sorted(Base.metadata.tables.keys()):
        print(f"[INIT]   - {table_name}")
    
    # Execute schema creation (this creates the SQLite file)
    print("[INIT] Executing Base.metadata.create_all(engine)...")
    try:
        Base.metadata.create_all(engine)
        print("[INIT] ✓ create_all() completed")
    except Exception as e:
        print(f"[ERROR] Schema creation failed: {e}")
        raise RuntimeError(f"Failed to create schema: {e}")
    
    # NOW verify database file was created
    print(f"[INIT] Verifying database file creation...")
    if not os.path.exists(db_path):
        print(f"[ERROR] Database file was not created: {os.path.abspath(db_path)}")
        raise RuntimeError(f"Database file not created: {db_path}")
    
    file_size = os.path.getsize(db_path)
    print(f"[INIT] ✓ Database file created: {os.path.abspath(db_path)}")
    print(f"[INIT] ✓ File size: {file_size} bytes")
    
    # Verify tables were created
    print("[INIT] Verifying schema...")
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if not tables:
        print("[ERROR] No tables found after create_all()")
        raise RuntimeError("Schema creation failed - no tables created")
    
    print(f"[INIT] ✓ Schema verified - {len(tables)} tables created")
    
    # Define required tables (must match actual Base models)
    required_tables = {
        'project_metadata',
        'impacts',
        'stakeholder_groups',
        'organization_units',
        'business_processes',
        'systems',
        'policies',
        'source_evidences',
        'change_assets'
    }
    
    # Check for required tables
    print("[INIT] Checking required tables:")
    missing_tables = []
    for table in sorted(required_tables):
        if table in tables:
            print(f"[INIT]   ✓ {table}")
        else:
            print(f"[INIT]   ✗ {table} - MISSING")
            missing_tables.append(table)
    
    # Check for association tables
    association_tables = [
        'impact_stakeholder_groups',
        'impact_organization_units',
        'impact_business_processes',
        'impact_systems',
        'impact_policies'
    ]
    
    print("[INIT] Checking association tables:")
    for table in association_tables:
        if table in tables:
            print(f"[INIT]   ✓ {table}")
        else:
            print(f"[INIT]   ⚠ {table} - missing (optional)")
    
    # Fail if required tables missing
    if missing_tables:
        print(f"[ERROR] Required tables missing: {', '.join(missing_tables)}")
        raise RuntimeError(f"Schema incomplete - missing required tables: {', '.join(missing_tables)}")
    
    print(f"[INIT] ✓ All required tables present")
    print(f"[INIT] Complete table list: {', '.join(sorted(tables))}")
    
    return engine

def get_session(engine):
    """Get database session"""
    Session = sessionmaker(bind=engine)
    return Session()

def list_projects():
    """List all available project workspaces"""
    projects_dir = 'projects'
    if not os.path.exists(projects_dir):
        return []
    
    projects = []
    for filename in os.listdir(projects_dir):
        if filename.endswith('.irp'):
            project_name = filename[:-4].replace('_', ' ')
            file_path = os.path.join(projects_dir, filename)
            stat = os.stat(file_path)
            projects.append({
                'name': project_name,
                'filename': filename,
                'path': file_path,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime)
            })
    
    return sorted(projects, key=lambda x: x['modified'], reverse=True)

def get_recent_projects(max_count=5):
    """Get recently modified projects"""
    all_projects = list_projects()
    return all_projects[:max_count]

def archive_project(project_name):
    """Move project to archives folder"""
    source = get_project_path(project_name)
    if not os.path.exists(source):
        return False
    
    os.makedirs('archives', exist_ok=True)
    safe_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_name = safe_name.replace(' ', '_')
    dest = f'archives/{safe_name}.irp'
    
    import shutil
    shutil.move(source, dest)
    return True

def delete_project(project_name):
    """Delete a project workspace"""
    project_path = get_project_path(project_name)
    if os.path.exists(project_path):
        os.remove(project_path)
        return True
    return False

def export_project(project_name, export_path):
    """Export project to a specified location"""
    source = get_project_path(project_name)
    if not os.path.exists(source):
        return False
    
    import shutil
    shutil.copy2(source, export_path)
    return True
