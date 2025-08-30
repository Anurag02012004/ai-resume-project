import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ARRAY, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/mydatabase")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

class Project(Base):
    """SQLAlchemy model for projects"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    repo_url = Column(String)
    tech_stack = Column(ARRAY(String), nullable=False)

class Experience(Base):
    """SQLAlchemy model for work experience"""
    __tablename__ = "experiences"
    
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    description = Column(ARRAY(String), nullable=False)

class Skill(Base):
    """SQLAlchemy model for skills"""
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)

class Education(Base):
    """SQLAlchemy model for education"""
    __tablename__ = "education"
    
    id = Column(Integer, primary_key=True, index=True)
    institution = Column(String, nullable=False)
    degree = Column(String, nullable=False)
    location = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    description = Column(ARRAY(String), nullable=False)

class Certificate(Base):
    """SQLAlchemy model for certificates"""
    __tablename__ = "certificates"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    issuer = Column(String, nullable=False)
    issue_date = Column(Date, nullable=False)
    credential_url = Column(String)
    description = Column(String)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
