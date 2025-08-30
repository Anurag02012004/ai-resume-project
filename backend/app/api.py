from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .database import get_db, Project, Experience, Skill, Education, Certificate
from .models import (
    ProjectSchema, ExperienceSchema, SkillSchema, EducationSchema, CertificateSchema,
    ProfileData, QueryRequest, QueryResponse, HealthResponse
)
from .rag_pipeline import rag_pipeline

# Create API router
router = APIRouter(prefix="/api/v1", tags=["resume"])

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="AI Resume API is running successfully"
    )

@router.get("/profile", response_model=ProfileData)
async def get_profile(db: Session = Depends(get_db)):
    """Get complete profile data including projects, experiences, skills, education, and certificates"""
    try:
        # Fetch all data from database
        projects = db.query(Project).all()
        experiences = db.query(Experience).all()
        skills = db.query(Skill).all()
        education = db.query(Education).all()
        certificates = db.query(Certificate).all()
        
        # Convert to Pydantic models
        projects_data = [ProjectSchema.model_validate(project) for project in projects]
        experiences_data = [ExperienceSchema.model_validate(exp) for exp in experiences]
        skills_data = [SkillSchema.model_validate(skill) for skill in skills]
        education_data = [EducationSchema.model_validate(edu) for edu in education]
        certificates_data = [CertificateSchema.model_validate(cert) for cert in certificates]
        
        return ProfileData(
            projects=projects_data,
            experiences=experiences_data,
            skills=skills_data,
            education=education_data,
            certificates=certificates_data
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching profile data: {str(e)}"
        )

@router.post("/query-resume", response_model=QueryResponse)
async def query_resume(request: QueryRequest):
    """Query the resume using RAG pipeline"""
    try:
        # Validate query
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Query cannot be empty"
            )
        
        # Process query through RAG pipeline
        result = rag_pipeline.answer_query(request.query)
        
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

@router.post("/sync-vector-db")
async def sync_vector_database():
    """Sync database content to vector database"""
    try:
        result = rag_pipeline.sync_vector_db()
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=500,
                detail=result["message"]
            )
        
        return {
            "message": "Vector database sync completed successfully",
            "details": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error syncing vector database: {str(e)}"
        )

@router.get("/projects", response_model=List[ProjectSchema])
async def get_projects(db: Session = Depends(get_db)):
    """Get all projects"""
    try:
        projects = db.query(Project).all()
        return [ProjectSchema.model_validate(project) for project in projects]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching projects: {str(e)}"
        )

@router.get("/experiences", response_model=List[ExperienceSchema])
async def get_experiences(db: Session = Depends(get_db)):
    """Get all work experiences"""
    try:
        experiences = db.query(Experience).all()
        return [ExperienceSchema.model_validate(exp) for exp in experiences]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching experiences: {str(e)}"
        )

@router.get("/skills", response_model=List[SkillSchema])
async def get_skills(db: Session = Depends(get_db)):
    """Get all skills"""
    try:
        skills = db.query(Skill).all()
        return [SkillSchema.model_validate(skill) for skill in skills]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching skills: {str(e)}"
        )

@router.get("/education", response_model=List[EducationSchema])
async def get_education(db: Session = Depends(get_db)):
    """Get all education"""
    try:
        education = db.query(Education).all()
        return [EducationSchema.model_validate(edu) for edu in education]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching education: {str(e)}"
        )
