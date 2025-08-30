import os
import json
import time
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from tenacity import retry, stop_after_attempt, wait_exponential
import pinecone
import cohere
from openai import OpenAI
from dotenv import load_dotenv

from .database import SessionLocal, Project, Experience, Skill, Education

# Load environment variables
load_dotenv()

class RAGPipeline:
    """Retrieval-Augmented Generation pipeline for resume queries"""
    
    def __init__(self):
        self.pinecone_client = None
        self.cohere_client = None
        self.openai_client = None
        self.index = None
        self.initialize_clients()
    
    def initialize_clients(self):
        """Initialize Pinecone, Cohere, and OpenAI clients"""
        try:
            # Initialize Pinecone
            pinecone_api_key = os.getenv("PINECONE_API_KEY")
            if pinecone_api_key:
                pinecone.init(
                    api_key=pinecone_api_key,
                    environment=os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")
                )
                index_name = os.getenv("PINECONE_INDEX_NAME", "resume-index")
                
                # Create index if it doesn't exist
                if index_name not in pinecone.list_indexes():
                    pinecone.create_index(
                        name=index_name,
                        dimension=1536,  # OpenAI text-embedding-3-small dimension
                        metric="cosine"
                    )
                
                self.index = pinecone.Index(index_name)
            
            # Initialize Cohere
            cohere_api_key = os.getenv("COHERE_API_KEY")
            if cohere_api_key:
                self.cohere_client = cohere.Client(cohere_api_key)
            
            # Initialize OpenAI
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if openai_api_key:
                self.openai_client = OpenAI(api_key=openai_api_key)
                
        except Exception as e:
            print(f"Error initializing clients: {e}")
    
    def format_data_for_rag(self, db_session: Session) -> List[Dict[str, Any]]:
        """Format database data into documents for RAG pipeline"""
        documents = []
        
        # Format projects
        projects = db_session.query(Project).all()
        for project in projects:
            doc_text = f"""
            Project: {project.title}
            Description: {project.description}
            Technologies: {', '.join(project.tech_stack)}
            Repository: {project.repo_url or 'Not specified'}
            """
            
            documents.append({
                'text': doc_text.strip(),
                'metadata': {
                    'source_id': project.id,
                    'type': 'project',
                    'title': project.title
                }
            })
        
        # Format experiences
        experiences = db_session.query(Experience).all()
        for exp in experiences:
            doc_text = f"""
            Position: {exp.role} at {exp.company}
            Duration: {exp.start_date} to {exp.end_date or 'Present'}
            Responsibilities: {' '.join(exp.description)}
            """
            
            documents.append({
                'text': doc_text.strip(),
                'metadata': {
                    'source_id': exp.id,
                    'type': 'experience',
                    'title': f"{exp.role} at {exp.company}"
                }
            })
        
        # Format skills
        skills = db_session.query(Skill).all()
        skill_categories = {}
        for skill in skills:
            if skill.category not in skill_categories:
                skill_categories[skill.category] = []
            skill_categories[skill.category].append(skill.name)
        
        for category, skill_list in skill_categories.items():
            doc_text = f"""
            Skill Category: {category}
            Skills: {', '.join(skill_list)}
            """
            
            documents.append({
                'text': doc_text.strip(),
                'metadata': {
                    'source_id': f"skills_{category}",
                    'type': 'skills',
                    'title': f"{category} Skills"
                }
            })
        
        # Format education
        education = db_session.query(Education).all()
        for edu in education:
            doc_text = f"""
            Education: {edu.degree} at {edu.institution}
            Location: {edu.location}
            Duration: {edu.start_date} to {edu.end_date or 'Present'}
            Details: {' '.join(edu.description)}
            """
            
            documents.append({
                'text': doc_text.strip(),
                'metadata': {
                    'source_id': edu.id,
                    'type': 'education',
                    'title': f"{edu.degree} at {edu.institution}"
                }
            })
        
        return documents
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 150) -> List[str]:
        """Simple text chunking implementation"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
            
            if start >= len(text):
                break
        
        return chunks
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI API with retry logic"""
        if not self.openai_client:
            raise Exception("OpenAI client not initialized")
        
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            raise
    
    def sync_vector_db(self):
        """Sync database content to vector database"""
        if not self.index:
            print("Pinecone index not available. Skipping vector sync.")
            return {"status": "skipped", "reason": "Pinecone not configured"}
        
        try:
            db_session = SessionLocal()
            documents = self.format_data_for_rag(db_session)
            
            vectors_to_upsert = []
            
            for doc in documents:
                # Chunk the document if it's too long
                chunks = self.chunk_text(doc['text'])
                
                for i, chunk in enumerate(chunks):
                    # Get embedding for the chunk
                    embedding = self.get_embedding(chunk)
                    
                    # Create unique ID for the chunk
                    vector_id = f"{doc['metadata']['type']}_{doc['metadata']['source_id']}_{i}"
                    
                    # Prepare metadata
                    metadata = {
                        **doc['metadata'],
                        'chunk_index': i,
                        'text': chunk
                    }
                    
                    vectors_to_upsert.append({
                        'id': vector_id,
                        'values': embedding,
                        'metadata': metadata
                    })
            
            # Upsert vectors in batches
            batch_size = 100
            for i in range(0, len(vectors_to_upsert), batch_size):
                batch = vectors_to_upsert[i:i + batch_size]
                self.index.upsert(vectors=batch)
            
            db_session.close()
            
            return {
                "status": "success",
                "documents_processed": len(documents),
                "vectors_upserted": len(vectors_to_upsert)
            }
            
        except Exception as e:
            print(f"Error syncing vector database: {e}")
            return {"status": "error", "message": str(e)}
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def answer_query(self, query: str) -> Dict[str, Any]:
        """Answer a query using the RAG pipeline"""
        try:
            if not self.index or not self.openai_client:
                # Fallback to database-only search
                return self._fallback_answer(query)
            
            # Get query embedding
            query_embedding = self.get_embedding(query)
            
            # Search Pinecone for similar chunks
            search_results = self.index.query(
                vector=query_embedding,
                top_k=5,
                include_metadata=True
            )
            
            if not search_results.matches:
                return {
                    "answer": "I couldn't find relevant information to answer your question. Please try rephrasing your query or ask about specific topics like projects, experience, or skills.",
                    "sources": []
                }
            
            # Extract text chunks and metadata
            chunks = []
            sources = []
            
            for match in search_results.matches:
                chunks.append(match.metadata['text'])
                sources.append({
                    'type': match.metadata['type'],
                    'title': match.metadata['title'],
                    'score': float(match.score)
                })
            
            # Rerank using Cohere if available
            if self.cohere_client:
                try:
                    rerank_response = self.cohere_client.rerank(
                        model="rerank-english-v2.0",
                        query=query,
                        documents=chunks,
                        top_k=2
                    )
                    
                    # Use reranked results
                    reranked_chunks = []
                    reranked_sources = []
                    
                    for result in rerank_response.results:
                        reranked_chunks.append(chunks[result.index])
                        reranked_sources.append(sources[result.index])
                    
                    chunks = reranked_chunks
                    sources = reranked_sources
                    
                except Exception as e:
                    print(f"Reranking failed, using original results: {e}")
            
            # Generate answer using the available context
            context = "\n\n".join(chunks)
            
            # Construct a comprehensive prompt
            prompt = f"""You are a helpful AI assistant representing a professional's resume. Based ONLY on the context provided below, answer the user's question about this person's background, experience, projects, and skills.

Guidelines:
- Only use information from the provided context
- Be specific and detailed in your response
- If the question is unrelated to professional background/resume, politely state that you can only answer questions about professional experience, projects, and skills
- At the end of your answer, cite the sources you used in the format [Source 1], [Source 2], etc.
- If you cannot answer based on the context, say so clearly

Context:
{context}

Question: {query}

Answer:"""

            # Since Gemini API isn't available, we'll provide a structured response
            # based on keyword matching and context analysis
            answer = self._generate_contextual_answer(query, chunks, sources)
            
            return {
                "answer": answer,
                "sources": sources
            }
            
        except Exception as e:
            print(f"Error in answer_query: {e}")
            return {
                "answer": "I apologize, but I encountered an error while processing your question. Please try again or rephrase your query.",
                "sources": []
            }
    
    def _generate_contextual_answer(self, query: str, chunks: List[str], sources: List[dict]) -> str:
        """Generate a detailed, contextual answer using OpenAI API"""
        try:
            if self.openai_client:
                # Create a comprehensive context from chunks
                context = "\n\n".join(chunks)
                
                # Enhanced prompt for better, more specific responses
                prompt = f"""You are an AI assistant helping to answer questions about Anurag Kushwaha's professional background. 

Based ONLY on the context provided below, answer the user's question in a detailed, specific, and helpful manner.

Guidelines:
1. FOCUS SPECIFICALLY on what the user is asking about - if they ask about a particular project, provide detailed information about THAT project
2. Be comprehensive but relevant - include technical details, achievements, and specific accomplishments
3. If they ask about a specific technology, project, or skill, elaborate on how it was used and what was achieved
4. Provide concrete examples and quantifiable results when available
5. Maintain a professional yet engaging tone
6. If the question cannot be answered from the context, clearly state what information is available instead

Context:
{context}

User Question: {query}

Please provide a detailed, specific answer:"""

                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful AI assistant that provides detailed, specific answers about a professional's background based on provided context."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.7
                )
                
                return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
        
        # Fallback to enhanced keyword-based response
        return self._generate_enhanced_fallback_answer(query, chunks, sources)
    
    def _generate_enhanced_fallback_answer(self, query: str, chunks: List[str], sources: List[dict]) -> str:
        """Enhanced fallback answer generation with better specificity"""
        query_lower = query.lower()
        
        # Check if query is resume-related
        resume_keywords = [
            'experience', 'project', 'skill', 'work', 'job', 'role', 'company', 
            'technology', 'programming', 'development', 'education', 'background',
            'qualification', 'achievement', 'responsibility', 'tech', 'software',
            'about', 'tell', 'what', 'how', 'describe', 'explain'
        ]
        
        if not any(keyword in query_lower for keyword in resume_keywords):
            return """I can only answer questions related to professional experience, projects, skills, and career background. 
            
Please ask me about:
• Specific projects (e.g., "Tell me about the SmartPrice project")
• Technical skills and technologies used
• Work experience and roles
• Educational background
• Professional achievements and accomplishments"""
        
        # Enhanced matching for specific project/topic queries
        specific_matches = []
        general_matches = []
        
        # Look for specific project names or technologies
        project_keywords = ['smartprice', 'startupsahayak', 'deepfake', 'travel', 'pricing', 'detection']
        tech_keywords = ['python', 'tensorflow', 'react', 'node', 'langchain', 'openai', 'redis', 'kafka']
        
        for i, chunk in enumerate(chunks):
            chunk_lower = chunk.lower()
            source = sources[i] if i < len(sources) else None
            
            # Check for specific matches
            query_words = query_lower.split()
            relevance_score = 0
            
            for word in query_words:
                if len(word) > 2:  # Ignore short words
                    if word in chunk_lower:
                        relevance_score += 2 if word in project_keywords or word in tech_keywords else 1
            
            if relevance_score > 0:
                specific_matches.append((chunk, source, relevance_score))
            else:
                general_matches.append((chunk, source, 0.5))
        
        # Sort by relevance
        specific_matches.sort(key=lambda x: x[2], reverse=True)
        
        # Generate response based on matches
        if specific_matches:
            answer_parts = []
            used_sources = []
            
            # Use top specific matches
            for chunk, source, score in specific_matches[:2]:
                if source:
                    if 'project' in source['type'].lower():
                        answer_parts.append(f"**{source['title']}**\n{chunk.strip()}")
                    else:
                        answer_parts.append(f"**{source['title']}**\n{chunk.strip()}")
                    used_sources.append(source['title'])
                else:
                    answer_parts.append(chunk.strip())
            
            if 'project' in query_lower and specific_matches:
                intro = "Here's detailed information about the project(s) you asked about:\n\n"
            elif any(tech in query_lower for tech in tech_keywords):
                intro = "Here's information about the technology/skill you asked about:\n\n"
            else:
                intro = "Based on your question, here's the relevant information:\n\n"
            
            answer = intro + "\n\n".join(answer_parts)
            
            if used_sources:
                answer += f"\n\n*Sources: {', '.join(used_sources)}*"
            
            return answer
        
        elif general_matches:
            # Provide general information
            answer_parts = []
            for chunk, source, _ in general_matches[:2]:
                answer_parts.append(chunk.strip())
            
            return "Based on the available information:\n\n" + "\n\n".join(answer_parts)
        
        else:
            return """I couldn't find specific information to answer your question. However, I can help you with:

• **Projects**: SmartPrice (Dynamic Travel Pricing), StartupSahayak (LLM Assistant), Deepfake Detection System
• **Technologies**: Python, TensorFlow, React.js, Node.js, LangChain, OpenAI API, Redis, Apache Kafka
• **Experience**: Software development, AI/ML projects, full-stack development
• **Skills**: Programming languages, frameworks, databases, cloud technologies

Please ask about any specific project, technology, or aspect of the professional background!"""
    
    def _fallback_answer(self, query: str) -> Dict[str, Any]:
        """Enhanced fallback method when vector search isn't available"""
        db_session = SessionLocal()
        documents = self.format_data_for_rag(db_session)
        db_session.close()
        
        query_lower = query.lower()
        
        # Enhanced keyword matching with comprehensive scoring
        relevant_docs = []
        
        for doc in documents:
            score = 0
            doc_text_lower = doc['text'].lower()
            
            # Calculate relevance score with better matching
            query_words = [word for word in query_lower.split() if len(word) > 2]
            for word in query_words:
                if word in doc_text_lower:
                    # Higher score for exact matches and important terms
                    if word in ['project', 'projects', 'work', 'experience', 'skill', 'skills', 'education', 'certificate']:
                        score += 2
                    elif word in ['smartprice', 'startupsahayak', 'deepfake', 'python', 'tensorflow', 'react', 'nodejs', 'ai', 'ml']:
                        score += 3
                    else:
                        score += 1
            
            # Special handling for common questions
            if any(phrase in query_lower for phrase in ['what projects', 'projects you', 'tell me about', 'experience', 'skills']):
                if doc['metadata']['type'] in ['project', 'experience', 'skill']:
                    score += 2
            
            if score > 0:
                relevant_docs.append((doc, score))
        
        # Sort by relevance score
        relevant_docs.sort(key=lambda x: x[1], reverse=True)
        
        if relevant_docs:
            # Always use OpenAI for better responses
            if self.openai_client:
                try:
                    # Get top relevant documents
                    top_docs = [doc[0] for doc in relevant_docs[:5]]
                    context = "\n\n".join([doc['text'] for doc in top_docs])
                    
                    # Create a comprehensive prompt
                    prompt = f"""You are an AI assistant representing Anurag Kushwaha, a skilled software engineer and AI specialist. Answer the user's question in a natural, conversational way using the provided information. Be specific, detailed, and engaging.

Professional Information:
{context}

User Question: {query}

Instructions:
- Provide a detailed, specific answer focused on what the user asked
- Use natural, conversational language like ChatGPT
- Include specific details, technologies, achievements, and numbers when available
- If asking about projects, describe each project's purpose, technologies, and impact
- If asking about experience, mention specific roles, companies, and accomplishments
- If asking about skills, categorize them and provide context on how they're used
- Be confident and professional while being helpful and informative
- Don't say "I couldn't find" - instead work with the available information

Answer:"""

                    response = self.openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=800,
                        temperature=0.7
                    )
                    
                    answer = response.choices[0].message.content.strip()
                    
                    # Create sources from relevant docs
                    sources = []
                    for doc, score in relevant_docs[:3]:
                        sources.append({
                            'type': doc['metadata']['type'],
                            'title': doc['metadata']['title'],
                            'score': score / 10.0  # Normalize score
                        })
                    
                    return {
                        "answer": answer,
                        "sources": sources
                    }
                
                except Exception as e:
                    print(f"Error generating OpenAI response: {e}")
                    # Fall through to manual response below
            
            # Manual response generation if OpenAI fails
            if 'project' in query_lower:
                project_docs = [doc for doc, score in relevant_docs if doc['metadata']['type'] == 'project'][:3]
                if project_docs:
                    answer = "Here are the key projects I've worked on:\n\n"
                    for doc in project_docs:
                        answer += f"• **{doc['metadata']['title']}**: {doc['text'][:200]}...\n\n"
                    
                    sources = [{'type': doc['metadata']['type'], 'title': doc['metadata']['title'], 'score': 0.8} 
                              for doc in project_docs]
                    
                    return {"answer": answer, "sources": sources}
        
        # Default response with database summary
        return {
            "answer": f"""I'd be happy to help you learn about Anurag Kushwaha's professional background! 

**Quick Overview:**
• **Projects**: 7 innovative projects including SmartPrice (ML-powered pricing engine), StartupSahayak (AI assistant), and Deepfake Detection System
• **Experience**: Software engineering roles with focus on AI/ML and full-stack development  
• **Skills**: 29+ technical skills across Python, AI/ML, React, Node.js, databases, and cloud technologies
• **Education**: B.Tech in Computer Science from IIIT Kalyani
• **Certifications**: 4 professional certifications including Data Science and Gen AI from Oracle

Feel free to ask about any specific project, technology, or experience! For example:
- "Tell me about the SmartPrice project"
- "What AI/ML experience do you have?"
- "What programming languages do you know?"
- "Describe your work experience"
""",
            "sources": [{"type": "overview", "title": "Professional Summary", "score": 1.0}]
        }
        
        # Enhanced keyword matching with comprehensive scoring
        relevant_docs = []
        
        for doc in documents:
            score = 0
            doc_text_lower = doc['text'].lower()
            
            # Calculate relevance score with better matching
            query_words = [word for word in query_lower.split() if len(word) > 2]
            for word in query_words:
                if word in doc_text_lower:
                    # Higher score for exact matches and important terms
                    if word in ['project', 'projects', 'work', 'experience', 'skill', 'skills', 'education', 'certificate']:
                        score += 2
                    elif word in ['smartprice', 'startupsahayak', 'deepfake', 'python', 'tensorflow', 'react', 'nodejs', 'ai', 'ml']:
                        score += 3
                    else:
                        score += 1
            
            # Special handling for common questions
            if any(phrase in query_lower for phrase in ['what projects', 'projects you', 'tell me about', 'experience', 'skills']):
                if doc['metadata']['type'] in ['project', 'experience', 'skill']:
                    score += 2
            
            if score > 0:
                relevant_docs.append((doc, score))
        
        # Sort by relevance score
        relevant_docs.sort(key=lambda x: x[1], reverse=True)
        
        if relevant_docs:
            # Always use OpenAI for better responses
            if self.openai_client:
                try:
                    # Get top relevant documents
                    top_docs = [doc[0] for doc in relevant_docs[:5]]
                    context = "\n\n".join([doc['text'] for doc in top_docs])
                    
                    # Create a comprehensive prompt
                    prompt = f"""You are an AI assistant representing Anurag Kushwaha, a skilled software engineer and AI specialist. Answer the user's question in a natural, conversational way using the provided information. Be specific, detailed, and engaging.

Professional Information:
{context}

User Question: {query}

Instructions:
- Provide a detailed, specific answer focused on what the user asked
- Use natural, conversational language like ChatGPT
- Include specific details, technologies, achievements, and numbers when available
- If asking about projects, describe each project's purpose, technologies, and impact
- If asking about experience, mention specific roles, companies, and accomplishments
- If asking about skills, categorize them and provide context on how they're used
- Be confident and professional while being helpful and informative
- Don't say "I couldn't find" - instead work with the available information

Answer:"""

                    response = self.openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=800,
                        temperature=0.7
                    )
                    
                    answer = response.choices[0].message.content.strip()
                    
                    # Create sources from relevant docs
                    sources = []
                    for doc, score in relevant_docs[:3]:
                        sources.append({
                            'type': doc['metadata']['type'],
                            'title': doc['metadata']['title'],
                            'score': score / 10.0  # Normalize score
                        })
                    
                    return {
                        "answer": answer,
                        "sources": sources
                    }
                
                except Exception as e:
                    print(f"Error generating OpenAI response: {e}")
                    # Fall through to manual response below
            
            # Manual response generation if OpenAI fails
            if 'project' in query_lower:
                project_docs = [doc for doc, score in relevant_docs if doc['metadata']['type'] == 'project'][:3]
                if project_docs:
                    answer = "Here are the key projects I've worked on:\n\n"
                    for doc in project_docs:
                        answer += f"• **{doc['metadata']['title']}**: {doc['text'][:200]}...\n\n"
                    
                    sources = [{'type': doc['metadata']['type'], 'title': doc['metadata']['title'], 'score': 0.8} 
                              for doc in project_docs]
                    
                    return {"answer": answer, "sources": sources}
            
            elif any(word in query_lower for word in ['experience', 'work', 'job']):
                exp_docs = [doc for doc, score in relevant_docs if doc['metadata']['type'] == 'experience'][:3]
                if exp_docs:
                    answer = "Here's my professional experience:\n\n"
                    for doc in exp_docs:
                        answer += f"• **{doc['metadata']['title']}**: {doc['text'][:200]}...\n\n"
                    
                    sources = [{'type': doc['metadata']['type'], 'title': doc['metadata']['title'], 'score': 0.8} 
                              for doc in exp_docs]
                    
                    return {"answer": answer, "sources": sources}
            
            elif 'skill' in query_lower:
                skill_docs = [doc for doc, score in relevant_docs if doc['metadata']['type'] == 'skill']
                if skill_docs:
                    answer = "Here are my technical skills organized by category:\n\n"
                    # Group skills by category
                    skills_by_category = {}
                    for doc in skill_docs:
                        # Extract skill info from text
                        lines = doc['text'].split('\n')
                        for line in lines:
                            if 'Category:' in line and 'Skill:' in line:
                                parts = line.split('Category:')
                                if len(parts) > 1:
                                    skill_part = parts[0].replace('Skill:', '').strip()
                                    category_part = parts[1].strip()
                                    if category_part not in skills_by_category:
                                        skills_by_category[category_part] = []
                                    skills_by_category[category_part].append(skill_part)
                    
                    for category, skills in skills_by_category.items():
                        answer += f"**{category}**: {', '.join(skills)}\n\n"
                    
                    sources = [{'type': 'skill', 'title': f"{len(skill_docs)} Skills", 'score': 0.9}]
                    return {"answer": answer, "sources": sources}
        
        # Default response with database summary
        return {
            "answer": f"""I'd be happy to help you learn about Anurag Kushwaha's professional background! 

**Quick Overview:**
• **Projects**: 7 innovative projects including SmartPrice (ML-powered pricing engine), StartupSahayak (AI assistant), and Deepfake Detection System
• **Experience**: Software engineering roles with focus on AI/ML and full-stack development  
• **Skills**: 29+ technical skills across Python, AI/ML, React, Node.js, databases, and cloud technologies
• **Education**: B.Tech in Computer Science from IIIT Kalyani
• **Certifications**: 4 professional certifications including Data Science and Gen AI from Oracle

Feel free to ask about any specific project, technology, or experience! For example:
- "Tell me about the SmartPrice project"
- "What AI/ML experience do you have?"
- "What programming languages do you know?"
- "Describe your work experience"
""",
            "sources": [{"type": "overview", "title": "Professional Summary", "score": 1.0}]
        }

                    response = self.openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are an AI assistant providing detailed information about a professional's background."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=800,
                        temperature=0.7
                    )
                    
                    sources = []
                    for doc, _ in relevant_docs[:3]:
                        sources.append({
                            'type': doc['metadata']['type'],
                            'title': doc['metadata']['title'],
                            'score': 0.8
                        })
                    
                    return {
                        "answer": response.choices[0].message.content.strip(),
                        "sources": sources
                    }
                    
                except Exception as e:
                    print(f"OpenAI fallback error: {e}")
            
            # Enhanced fallback without OpenAI
            answer_parts = []
            sources = []
            
            for doc, score in relevant_docs[:2]:  # Use top 2 matches
                if doc['metadata']['type'] == 'project':
                    answer_parts.append(f"**{doc['metadata']['title']}**\n{doc['text'].strip()}")
                else:
                    answer_parts.append(f"**{doc['metadata']['title']}**\n{doc['text'].strip()}")
                
                sources.append({
                    'type': doc['metadata']['type'],
                    'title': doc['metadata']['title'],
                    'score': score / 10  # Normalize score
                })
            
            if 'project' in query_lower:
                intro = "Here's detailed information about the relevant project(s):\n\n"
            elif any(tech in query_lower for tech in ['python', 'javascript', 'react', 'tensorflow']):
                intro = "Here's information about the technology/skill:\n\n"
            else:
                intro = "Based on your question, here's the relevant information:\n\n"
            
            answer = intro + "\n\n".join(answer_parts)
            return {"answer": answer, "sources": sources}
        else:
            return {
                "answer": """I couldn't find specific information for your question. However, I can help you learn about:

**🚀 Featured Projects:**
• **SmartPrice** - ML-powered dynamic travel pricing system with 87% accuracy
• **StartupSahayak** - LLM-based virtual assistant for startup idea evaluation  
• **Deepfake Detection** - Deep learning system with 90%+ accuracy

**💻 Technical Expertise:**
• Programming: Python, JavaScript, Java, C++, SQL
• AI/ML: TensorFlow, PyTorch, OpenCV, Scikit-learn
• Web Development: React.js, Next.js, Node.js, Express.js
• Databases: PostgreSQL, MongoDB, Redis

**🎓 Education:**
• BTech in Computer Science from IIIT Kalyani (CGPA: 8.0/10)

Please ask about any specific project, technology, or experience!""",
                "sources": []
            }

# Global RAG pipeline instance
rag_pipeline = RAGPipeline()
