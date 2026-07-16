from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os

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

class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    sponsor = Column(String(255))
    change_manager = Column(String(255))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String(50), default='Active')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    impacts = relationship('Impact', back_populates='project', cascade='all, delete-orphan')

class Impact(Base):
    __tablename__ = 'impacts'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
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
    
    project = relationship('Project', back_populates='impacts')
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
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
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
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
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
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
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
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
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
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
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

def get_engine(db_path='database/sqlite.db'):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return create_engine(f'sqlite:///{db_path}', echo=False)

def init_db(db_path='database/sqlite.db'):
    engine = get_engine(db_path)
    Base.metadata.create_all(engine)
    return engine

def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()
