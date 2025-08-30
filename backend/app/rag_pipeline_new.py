"""
Enhanced RAG Pipeline for AI Resume Bot
Provides intelligent responses using OpenAI for better user experience
"""

import os
from typing import List, Dict, Any
from sqlalchemy.orm import sessionmaker
from openai import OpenAI
from dotenv import load_dotenv

from .database import SessionLocal, Project, Experience, Skill, Education, Certificate

# Load environment variables
load_dotenv()

class EnhancedRAGPipeline:
    """Enhanced RAG Pipeline with improved responses"""
    
    def __init__(self):
        """Initialize the RAG pipeline"""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = None
        
        if self.openai_api_key:
            try:
                self.openai_client = OpenAI(api_key=self.openai_api_key)
                print("OpenAI client initialized successfully")
            except Exception as e:
                print(f"Error initializing OpenAI: {e}")
    
    def answer_query(self, query: str) -> Dict[str, Any]:
        """Answer a query using enhanced database search and AI"""
        try:
            # Get all data from database
            db_session = SessionLocal()
            
            # Fetch all data
            projects = db_session.query(Project).all()
            experiences = db_session.query(Experience).all()
            skills = db_session.query(Skill).all()
            education = db_session.query(Education).all()
            certificates = db_session.query(Certificate).all()
            
            db_session.close()
            
            # Create context based on query
            query_lower = query.lower()
            context_parts = []
            sources = []
            
            # Add relevant projects
            if any(word in query_lower for word in ['project', 'projects', 'built', 'created', 'developed']):
                context_parts.append("**PROJECTS:**")
                for project in projects:
                    context_parts.append(f"- {project.title}: {project.description}")
                    context_parts.append(f"  Technologies: {', '.join(project.tech_stack)}")
                    if project.repo_url:
                        context_parts.append(f"  Repository: {project.repo_url}")
                    context_parts.append("")
                    sources.append({'type': 'project', 'title': project.title, 'score': 0.9})
            
            # Add relevant experience
            if any(word in query_lower for word in ['experience', 'work', 'job', 'role', 'company']):
                context_parts.append("**EXPERIENCE:**")
                for exp in experiences:
                    context_parts.append(f"- {exp.role} at {exp.company}")
                    context_parts.append(f"  Duration: {exp.start_date} to {exp.end_date or 'Present'}")
                    context_parts.append(f"  Location: {exp.location}")
                    for desc in exp.description:
                        context_parts.append(f"  • {desc}")
                    context_parts.append("")
                    sources.append({'type': 'experience', 'title': f"{exp.role} at {exp.company}", 'score': 0.9})
            
            # Add relevant skills
            if any(word in query_lower for word in ['skill', 'skills', 'technology', 'technologies', 'programming', 'language']):
                context_parts.append("**SKILLS:**")
                # Group skills by category
                skills_by_category = {}
                for skill in skills:
                    if skill.category not in skills_by_category:
                        skills_by_category[skill.category] = []
                    skills_by_category[skill.category].append(skill.name)
                
                for category, skill_list in skills_by_category.items():
                    context_parts.append(f"- {category}: {', '.join(skill_list)}")
                context_parts.append("")
                sources.append({'type': 'skill', 'title': f"{len(skills)} Technical Skills", 'score': 0.9})
            
            # Add education
            if any(word in query_lower for word in ['education', 'degree', 'university', 'college', 'study']):
                context_parts.append("**EDUCATION:**")
                for edu in education:
                    context_parts.append(f"- {edu.degree}")
                    context_parts.append(f"  Institution: {edu.institution}")
                    context_parts.append(f"  Location: {edu.location}")
                    context_parts.append(f"  Duration: {edu.start_date} to {edu.end_date or 'Present'}")
                    for desc in edu.description:
                        context_parts.append(f"  • {desc}")
                    context_parts.append("")
                    sources.append({'type': 'education', 'title': edu.degree, 'score': 0.9})
            
            # Add certificates
            if any(word in query_lower for word in ['certificate', 'certification', 'certified']):
                context_parts.append("**CERTIFICATIONS:**")
                for cert in certificates:
                    context_parts.append(f"- {cert.title}")
                    context_parts.append(f"  Issuer: {cert.issuer}")
                    context_parts.append(f"  Date: {cert.issue_date}")
                    if cert.description:
                        context_parts.append(f"  Description: {cert.description}")
                    if cert.credential_url:
                        context_parts.append(f"  URL: {cert.credential_url}")
                    context_parts.append("")
                    sources.append({'type': 'certificate', 'title': cert.title, 'score': 0.9})
            
            # If no specific context found, add overview
            if not context_parts:
                context_parts.append("**PROFESSIONAL OVERVIEW:**")
                context_parts.append(f"Projects: {len(projects)} innovative projects")
                context_parts.append(f"Experience: {len(experiences)} professional roles")
                context_parts.append(f"Skills: {len(skills)} technical skills")
                context_parts.append(f"Education: {len(education)} academic qualifications")
                context_parts.append(f"Certifications: {len(certificates)} professional certifications")
                context_parts.append("")
                
                # Add top 3 projects as sample
                context_parts.append("**TOP PROJECTS:**")
                for project in projects[:3]:
                    context_parts.append(f"- {project.title}: {project.description[:100]}...")
                    sources.append({'type': 'project', 'title': project.title, 'score': 0.8})
            
            context = "\n".join(context_parts)
            
            # Use OpenAI to generate response
            if self.openai_client and context:
                try:
                    prompt = f"""You are an AI assistant representing Anurag Kushwaha, a skilled software engineer and AI specialist. 

Based on the following professional information, answer the user's question in a natural, detailed, and engaging way:

{context}

User Question: {query}

Instructions:
- Provide a comprehensive, specific answer
- Use natural, conversational language
- Include specific details, technologies, and achievements
- Be confident and professional
- Structure your response clearly with bullet points or sections when appropriate
- Don't mention that you're looking at provided information - answer as if you are representing Anurag

Answer:"""

                    response = self.openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=800,
                        temperature=0.7
                    )
                    
                    answer = response.choices[0].message.content.strip()
                    
                    return {
                        "answer": answer,
                        "sources": sources[:5]  # Limit sources
                    }
                    
                except Exception as e:
                    print(f"OpenAI error: {e}")
                    # Fall back to manual response
            
            # Manual fallback response
            if not context_parts:
                answer = f"""I'd be happy to help you learn about Anurag Kushwaha's professional background!

**Overview:**
• **Projects**: {len(projects)} innovative projects including AI/ML systems, web platforms, and blockchain applications
• **Experience**: {len(experiences)} professional roles focusing on software engineering and AI development
• **Skills**: {len(skills)} technical skills across programming languages, frameworks, and tools
• **Education**: Computer Science engineering from IIIT Kalyani
• **Certifications**: {len(certificates)} professional certifications from Oracle and other providers

Feel free to ask about specific projects, technologies, or experiences!"""
            else:
                # Create a basic response from context
                answer = f"Here's what I can tell you about that:\n\n{context[:500]}..."
            
            return {
                "answer": answer,
                "sources": sources[:3] if sources else [{"type": "overview", "title": "Professional Summary", "score": 1.0}]
            }
            
        except Exception as e:
            print(f"Error in answer_query: {e}")
            return {
                "answer": "I apologize, but I'm experiencing some technical difficulties right now. Please try asking your question again in a moment.",
                "sources": []
            }

# Create global instance
rag_pipeline = EnhancedRAGPipeline()
