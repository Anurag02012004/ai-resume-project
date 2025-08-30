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
                print("✅ OpenAI client initialized successfully")
            except Exception as e:
                print(f"❌ Error initializing OpenAI: {e}")
                # Try alternative initialization
                try:
                    self.openai_client = OpenAI()
                    print("✅ OpenAI client initialized with default config")
                except Exception as e2:
                    print(f"❌ Alternative OpenAI init failed: {e2}")
        else:
            print("❌ No OpenAI API key found")
    
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
            
            # Build complete professional profile for context
            profile_context = []
            
            # Add all projects
            profile_context.append("**PROJECTS:**")
            for project in projects:
                profile_context.append(f"Project: {project.title}")
                profile_context.append(f"Description: {project.description}")
                profile_context.append(f"Technologies: {', '.join(project.tech_stack)}")
                if project.repo_url:
                    profile_context.append(f"Repository: {project.repo_url}")
                profile_context.append("")
            
            # Add all experience
            profile_context.append("**EXPERIENCE:**")
            for exp in experiences:
                profile_context.append(f"Role: {exp.role}")
                profile_context.append(f"Company: {exp.company}")
                profile_context.append(f"Location: {exp.location}")
                profile_context.append(f"Duration: {exp.start_date} to {exp.end_date or 'Present'}")
                profile_context.append("Responsibilities:")
                for desc in exp.description:
                    profile_context.append(f"- {desc}")
                profile_context.append("")
            
            # Add all skills
            profile_context.append("**SKILLS:**")
            skills_by_category = {}
            for skill in skills:
                if skill.category not in skills_by_category:
                    skills_by_category[skill.category] = []
                skills_by_category[skill.category].append(skill.name)
            
            for category, skill_list in skills_by_category.items():
                profile_context.append(f"{category}: {', '.join(skill_list)}")
            profile_context.append("")
            
            # Add education
            profile_context.append("**EDUCATION:**")
            for edu in education:
                profile_context.append(f"Degree: {edu.degree}")
                profile_context.append(f"Institution: {edu.institution}")
                profile_context.append(f"Location: {edu.location}")
                profile_context.append(f"Duration: {edu.start_date} to {edu.end_date or 'Present'}")
                for desc in edu.description:
                    profile_context.append(f"- {desc}")
                profile_context.append("")
            
            # Add certifications
            profile_context.append("**CERTIFICATIONS:**")
            for cert in certificates:
                profile_context.append(f"Certificate: {cert.title}")
                profile_context.append(f"Issuer: {cert.issuer}")
                profile_context.append(f"Date: {cert.issue_date}")
                if cert.description:
                    profile_context.append(f"Description: {cert.description}")
                profile_context.append("")
            
            full_context = "\n".join(profile_context)
            
            # Always use OpenAI for intelligent responses
            if self.openai_client:
                try:
                    prompt = f"""You are Anurag Kushwaha, a skilled software engineer and AI specialist. Answer the user's question directly and naturally, as if you are speaking about yourself in first person.

COMPLETE PROFESSIONAL PROFILE:
{full_context}

User Question: {query}

IMPORTANT INSTRUCTIONS:
- Answer as Anurag himself (use "I", "my", "I built", "I worked", etc.)
- Be specific and detailed about what the user is asking
- If they ask about a specific project like "SmartPrice", focus ONLY on that project with full details
- If they ask about experience, focus on work experience and achievements
- If they ask about skills, mention the relevant skills with context
- Use natural, conversational language like ChatGPT
- Include specific numbers, technologies, and achievements
- Don't mention "here's what I can tell you" - just answer directly
- Be confident and professional

Answer as Anurag:"""

                    response = self.openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=600,
                        temperature=0.7
                    )
                    
                    answer = response.choices[0].message.content.strip()
                    
                    # Determine relevant sources based on query
                    sources = []
                    query_lower = query.lower()
                    
                    # Smart source detection
                    if any(proj.title.lower() in query_lower or any(word in query_lower for word in proj.title.lower().split()) for proj in projects):
                        # Specific project mentioned
                        for proj in projects:
                            if proj.title.lower() in query_lower or any(word in query_lower for word in proj.title.lower().split()):
                                sources.append({'type': 'project', 'title': proj.title, 'score': 0.95})
                    elif 'project' in query_lower:
                        # General projects question
                        for proj in projects[:3]:
                            sources.append({'type': 'project', 'title': proj.title, 'score': 0.9})
                    elif any(word in query_lower for word in ['experience', 'work', 'job']):
                        for exp in experiences:
                            sources.append({'type': 'experience', 'title': f"{exp.role} at {exp.company}", 'score': 0.9})
                    elif any(word in query_lower for word in ['skill', 'technology', 'programming']):
                        sources.append({'type': 'skill', 'title': f"{len(skills)} Technical Skills", 'score': 0.9})
                    else:
                        # General question - add top sources
                        sources.append({'type': 'project', 'title': projects[0].title if projects else 'Projects', 'score': 0.8})
                        sources.append({'type': 'experience', 'title': f"{experiences[0].role} at {experiences[0].company}" if experiences else 'Experience', 'score': 0.8})
                    
                    return {
                        "answer": answer,
                        "sources": sources[:4]  # Limit to 4 sources
                    }
                    
                except Exception as e:
                    print(f"OpenAI error: {e}")
                    # Fall back to basic response below
            
            # Fallback - create intelligent response without OpenAI
            query_lower = query.lower()
            
            # Smart response based on question type
            if any(word in query_lower for word in ['smartprice', 'smart price']):
                smartprice = next((p for p in projects if 'smartprice' in p.title.lower()), None)
                if smartprice:
                    answer = f"""My main project is **{smartprice.title}**, which I'm really proud of. 

{smartprice.description}

**Technologies I used:**
{', '.join(smartprice.tech_stack)}

**Key achievements:**
• Achieved 87% accuracy in price optimization
• Potential 15-20% revenue increase for travel platforms
• Built microservices architecture for sub-second updates
• Used demand forecasting and competitive analysis

You can check out the code on my GitHub: {smartprice.repo_url}

This project demonstrates my expertise in machine learning, microservices architecture, and real-time data processing."""
                    
                    sources = [{'type': 'project', 'title': smartprice.title, 'score': 0.95}]
                    return {"answer": answer, "sources": sources}
            
            elif 'main project' in query_lower or 'primary project' in query_lower:
                main_project = projects[0] if projects else None
                if main_project:
                    answer = f"""My main project is **{main_project.title}**.

{main_project.description}

**Technologies:** {', '.join(main_project.tech_stack)}

This project showcases my skills in {', '.join(main_project.tech_stack[:3])} and demonstrates my ability to build scalable, production-ready applications."""
                    
                    sources = [{'type': 'project', 'title': main_project.title, 'score': 0.95}]
                    return {"answer": answer, "sources": sources}
            
            elif 'project' in query_lower:
                answer = "I've worked on several exciting projects:\n\n"
                for i, project in enumerate(projects[:3], 1):
                    answer += f"**{i}. {project.title}**\n"
                    answer += f"{project.description[:150]}...\n"
                    answer += f"*Technologies: {', '.join(project.tech_stack[:4])}*\n\n"
                
                sources = [{'type': 'project', 'title': p.title, 'score': 0.9} for p in projects[:3]]
                return {"answer": answer, "sources": sources}
            
            # Handle graduation/college questions
            elif any(phrase in query_lower for phrase in ['graduate', 'graduation', 'pass out', 'college', 'when will you', 'complete your degree']):
                edu = education[0] if education else None
                if edu and edu.end_date:
                    answer = f"""I will graduate from **{edu.institution}** in **{edu.end_date.strftime('%B %Y')}** ({edu.end_date}).

I'm currently pursuing a **{edu.degree}** and maintaining a CGPA of **7.9/10**. I'm expected to complete my degree by {edu.end_date.strftime('%B %d, %Y')}.

My coursework includes Data Structures, Algorithms, DBMS, Computer Networks, Operating Systems, AI, and Cryptography, which has given me a strong foundation for my software engineering career."""
                    
                    sources = [{'type': 'education', 'title': edu.degree, 'score': 0.95}]
                    return {"answer": answer, "sources": sources}
            
            # Handle LeetCode/competitive programming questions
            elif any(phrase in query_lower for phrase in ['leetcode', 'contest rating', 'competitive programming', 'coding contest', 'problem solving']):
                # Find achievements in experiences
                coding_exp = None
                for exp in experiences:
                    if 'leetcode' in ' '.join(exp.description).lower() or 'contest' in ' '.join(exp.description).lower():
                        coding_exp = exp
                        break
                
                if coding_exp:
                    leetcode_info = None
                    contest_info = None
                    for desc in coding_exp.description:
                        if 'leetcode' in desc.lower():
                            leetcode_info = desc
                        elif 'competitive programming' in desc.lower():
                            contest_info = desc
                    
                    answer = f"""Here's my competitive programming profile:\n\n"""
                    
                    if leetcode_info:
                        # Extract specific details from the description
                        answer += f"**LeetCode Performance:**\n{leetcode_info}\n\n"
                    
                    if contest_info:
                        answer += f"**Competitive Programming:**\n{contest_info}\n\n"
                    
                    answer += """My **contest rating of 1655** puts me in the **Global Top 16%** of all LeetCode users, and I've solved **600+ problems** across multiple platforms. I regularly participate in programming contests to keep my problem-solving skills sharp.

This competitive programming experience has significantly improved my algorithmic thinking and problem-solving abilities, which I apply in my software development projects."""
                    
                    sources = [{'type': 'experience', 'title': 'Competitive Programming Achievements', 'score': 0.95}]
                    return {"answer": answer, "sources": sources}
            
            # Handle certificates questions
            elif any(phrase in query_lower for phrase in ['certificate', 'certification', 'certified', 'credentials']):
                if certificates:
                    answer = "Here are my professional certifications:\n\n"
                    for i, cert in enumerate(certificates, 1):
                        answer += f"**{i}. {cert.title}**\n"
                        answer += f"   • Issuer: {cert.issuer}\n"
                        answer += f"   • Date: {cert.issue_date.strftime('%B %Y')}\n"
                        if cert.description:
                            answer += f"   • Description: {cert.description}\n"
                        if cert.credential_url:
                            answer += f"   • Credential: [View Certificate]({cert.credential_url})\n"
                        answer += "\n"
                    
                    answer += f"These **{len(certificates)} certifications** demonstrate my commitment to continuous learning and professional development in AI, data science, and modern development technologies."
                    
                    sources = [{'type': 'certificate', 'title': cert.title, 'score': 0.9} for cert in certificates]
                    return {"answer": answer, "sources": sources}
            
            # Handle achievements questions
            elif any(phrase in query_lower for phrase in ['achievement', 'achievements', 'accomplishment', 'accomplishments']):
                answer = "Here are my key achievements:\n\n"
                
                # Add coding achievements
                coding_exp = next((exp for exp in experiences if 'leetcode' in ' '.join(exp.description).lower()), None)
                if coding_exp:
                    answer += "**🏆 Competitive Programming:**\n"
                    for desc in coding_exp.description:
                        answer += f"• {desc}\n"
                    answer += "\n"
                
                # Add project achievements
                answer += "**🚀 Project Achievements:**\n"
                for project in projects[:3]:
                    if 'accuracy' in project.description.lower() or 'achievement' in project.description.lower() or '%' in project.description:
                        # Extract achievement numbers
                        lines = project.description.split('.')
                        for line in lines:
                            if any(word in line.lower() for word in ['accuracy', 'achievement', '%', 'revenue', 'faster']):
                                answer += f"• {project.title}: {line.strip()}\n"
                answer += "\n"
                
                # Add academic achievements
                if education:
                    edu = education[0]
                    answer += f"**🎓 Academic:**\n"
                    answer += f"• Pursuing {edu.degree} at {edu.institution}\n"
                    answer += f"• Current CGPA: 7.9/10\n"
                    answer += f"• Expected graduation: {edu.end_date.strftime('%B %Y')}\n\n"
                
                # Add certifications
                if certificates:
                    answer += f"**📜 Certifications:**\n"
                    answer += f"• {len(certificates)} professional certifications from Oracle University and other providers\n"
                    answer += f"• Specializations in Data Science, Gen AI, and Full-Stack Development\n"
                
                sources = [
                    {'type': 'achievement', 'title': 'Competitive Programming', 'score': 0.9},
                    {'type': 'achievement', 'title': 'Project Success', 'score': 0.9},
                    {'type': 'achievement', 'title': 'Academic Performance', 'score': 0.9}
                ]
                return {"answer": answer, "sources": sources}
            
            # Handle tech stack/skills questions
            elif any(phrase in query_lower for phrase in ['tech stack', 'technology', 'technologies', 'skills', 'programming language', 'frameworks']):
                if skills:
                    answer = "Here's my comprehensive tech stack:\n\n"
                    
                    # Group skills by category
                    skills_by_category = {}
                    for skill in skills:
                        if skill.category not in skills_by_category:
                            skills_by_category[skill.category] = []
                        skills_by_category[skill.category].append(skill.name)
                    
                    # Display in organized format
                    for category, skill_list in skills_by_category.items():
                        answer += f"**{category}:**\n"
                        # Split into rows for better readability
                        for i in range(0, len(skill_list), 4):
                            row_skills = skill_list[i:i+4]
                            answer += f"   {' • '.join(row_skills)}\n"
                        answer += "\n"
                    
                    answer += f"**Total:** {len(skills)} technical skills across {len(skills_by_category)} categories\n\n"
                    answer += "I'm particularly strong in **Python, JavaScript, React, Node.js, and AI/ML technologies**. My experience spans full-stack development, machine learning, blockchain, and cloud technologies."
                    
                    sources = [{'type': 'skill', 'title': f"{len(skills)} Technical Skills", 'score': 0.95}]
                    return {"answer": answer, "sources": sources}
            
            # Handle life summary questions
            elif any(phrase in query_lower for phrase in ['life summary', 'about yourself', 'tell me about you', 'who are you', 'introduce yourself']):
                answer = """✨ **Life Summary of Anurag Kushwaha**

I am Anurag Kushwaha, a passionate Computer Science undergraduate at **IIIT Kalyani (Batch of 2026)** with a strong interest in Competitive Programming, Machine Learning, Blockchain, and Full-Stack Development.

**🎓 Academic Journey:**
My journey began with clearing JEE Mains and stepping into IIIT Kalyani in 2022. Since then, I've explored multiple domains—ranging from web development to deep learning research—while consistently strengthening my problem-solving skills through platforms like LeetCode and Codeforces.

**🚀 Project Highlights:**
Over time, I have built impactful projects:
• **SmartPrice** – A dynamic travel pricing engine inspired by real-world systems like MakeMyTrip
• **StartupSahayak** – An AI-powered startup advisor built with Next.js and LangChain, focused on the Indian market
• **Multi-Modal Fake News Detection System** – My Bachelor Thesis, leveraging LLMs for misinformation detection
• **Deepfake Detection using Blockchain** – A research-oriented project exploring cryptography and blockchain
• Plus several other apps in news, healthcare, UI/UX design, and accessibility

**🏆 Achievements:**
I actively participate in hackathons and academic projects, maintaining a **CGPA of 7.9/10** and achieving a **LeetCode contest rating of 1655** (Global Top 16%).

**🎯 Vision:**
My coursework spans DSA, DBMS, OS, CN, Cryptography, and AI, giving me a solid theoretical foundation. Outside of academics, I enjoy cricket, exploring startup ideas, and continuously preparing for FAANG/product-based company opportunities. 

My vision is to build technology that not only solves problems at scale but also makes systems more trustworthy, secure, and human-centric."""
                
                sources = [
                    {'type': 'overview', 'title': 'Life Summary', 'score': 1.0},
                    {'type': 'education', 'title': education[0].degree if education else 'Education', 'score': 0.9},
                    {'type': 'project', 'title': projects[0].title if projects else 'Projects', 'score': 0.9}
                ]
                return {"answer": answer, "sources": sources}
            
            # General fallback
            return {
                "answer": "I'm a software engineer and AI specialist with experience in full-stack development, machine learning, and blockchain technologies. I'd be happy to tell you about my specific projects, work experience, or technical skills. What would you like to know more about?",
                "sources": [{"type": "overview", "title": "Professional Summary", "score": 1.0}]
            }
            
        except Exception as e:
            print(f"Error in answer_query: {e}")
            return {
                "answer": "I apologize, but I'm experiencing some technical difficulties right now. Please try asking your question again in a moment.",
                "sources": []
            }
            
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
