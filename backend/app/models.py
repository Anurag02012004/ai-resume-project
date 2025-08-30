from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class ProjectSchema(BaseModel):
    """Pydantic model for Project data validation"""
    id: int
    title: str
    description: str
    repo_url: Optional[str] = None
    tech_stack: List[str]
    
    class Config:
        from_attributes = True

class ExperienceSchema(BaseModel):
    """Pydantic model for Experience data validation"""
    id: int
    role: str
    company: str
    location: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: List[str]
    
    class Config:
        from_attributes = True

class SkillSchema(BaseModel):
    """Pydantic model for Skill data validation"""
    id: int
    name: str
    category: str
    
    class Config:
        from_attributes = True

class EducationSchema(BaseModel):
    """Pydantic model for Education data validation"""
    id: int
    institution: str
    degree: str
    location: str
    start_date: date
    end_date: Optional[date] = None
    description: List[str]
    
    class Config:
        from_attributes = True

class CertificateSchema(BaseModel):
    """Pydantic model for Certificate data validation"""
    id: int
    title: str
    issuer: str
    issue_date: date
    credential_url: Optional[str] = None
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

class ProfileData(BaseModel):
    """Combined profile data response"""
    projects: List[ProjectSchema]
    experiences: List[ExperienceSchema]
    skills: List[SkillSchema]
    education: List[EducationSchema]
    certificates: List[CertificateSchema]

class QueryRequest(BaseModel):
    """Request model for RAG queries"""
    query: str

class QueryResponse(BaseModel):
    """Response model for RAG queries"""
    answer: str
    sources: List[dict]
    
class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str
