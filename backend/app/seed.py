"""
Seeder script to pre-populate PostgreSQL database with Anurag Kushwaha's resume data
following his LaTeX resume structure.
"""

import os
import sys
from datetime import date
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database models
from app.database import Base, engine, Skill, Project, Experience, Education, Certificate

# Load environment variables
load_dotenv()

def seed_database():
    """Seed the database with Anurag's resume data"""
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Avoid reseeding if already populated
        if db.query(Skill).count() > 0:
            logger.info("Database already seeded. Skipping.")
            return
        # ------------------ Education ------------------
        education = [
            Education(
                institution="Indian Institute of Information Technology, Kalyani",
                degree="Bachelor of Technology in Computer Science and Engineering",
                location="Kalyani, West Bengal, India",
                start_date=date(2022, 7, 1),
                end_date=date(2026, 5, 31),
                description=[
                    "CGPA: 7.9/10 (as of Semester 6)",
                    "Coursework: Data Structures, Algorithms, DBMS, Computer Networks, OS, AI, Cryptography"
                ]
            )
        ]
        db.add_all(education)
        
        # ------------------ Technical Skills ------------------
        skills = [
            Skill(name="C", category="Programming Language"),
            Skill(name="C++", category="Programming Language"),
            Skill(name="Python", category="Programming Language"),
            Skill(name="Java", category="Programming Language"),
            Skill(name="JavaScript", category="Programming Language"),
            Skill(name="SQL", category="Programming Language"),
            Skill(name="React.js", category="Frontend Framework"),
            Skill(name="Next.js", category="Frontend Framework"),
            Skill(name="Node.js", category="Backend Framework"),
            Skill(name="Express.js", category="Backend Framework"),
            Skill(name="Flask", category="Backend Framework"),
            Skill(name="FastAPI", category="Backend Framework"),
            Skill(name="Django", category="Backend Framework"),
            Skill(name="Spring Boot", category="Backend Framework"),
            Skill(name="PostgreSQL", category="Database"),
            Skill(name="MySQL", category="Database"),
            Skill(name="SQLite", category="Database"),
            Skill(name="MongoDB", category="Database"),
            Skill(name="Redis", category="Database/Cache"),
            Skill(name="AWS", category="Cloud"),
            Skill(name="Docker", category="DevOps"),
            Skill(name="Git", category="DevOps"),
            Skill(name="Firebase", category="Cloud"),
            Skill(name="Scikit-learn", category="AI/ML"),
            Skill(name="PyTorch", category="AI/ML"),
            Skill(name="TensorFlow", category="AI/ML"),
            Skill(name="Hugging Face", category="AI/ML"),
            Skill(name="OpenCV", category="AI/ML"),
            Skill(name="NLTK", category="AI/ML"),
        ]
        db.add_all(skills)
        
        # ------------------ Projects ------------------
        projects = [
            Project(
                title="SmartPrice – Dynamic Travel Pricing Engine",
                description="""ML-powered dynamic pricing system for travel platforms using demand forecasting 
                and competitive analysis. Achieved 87% accuracy in price optimization with potential 15-20% 
                revenue increase. Built microservices with Apache Kafka + Redis for sub-second updates.""",
                repo_url="https://github.com/Anurag02012004/TravelPricing",
                tech_stack=["Python", "TensorFlow", "Redis", "Apache Kafka"]
            ),
            Project(
                title="StartupSahayak",
                description="""LLM-based virtual assistant for evaluating startup ideas and guiding entrepreneurs 
                across ideation, funding, legal, and MVP development. Integrated LangChain with OpenAI API.""",
                repo_url="https://github.com/Anurag02012004/StartupSahayak",
                tech_stack=["React.js", "Node.js", "Express.js", "LangChain", "OpenAI API"]
            ),
            Project(
                title="Deepfake Detection System",
                description="""Developed deep learning system to detect AI-generated fake videos using CNN + RNN 
                architectures. Achieved 90%+ accuracy on benchmark datasets.""",
                repo_url="https://github.com/Anurag02012004/Deepfake-Detecter/tree/master",
                tech_stack=["Python", "TensorFlow", "Solydity","PQC"]
            ),
            Project(
                title="Recruitment Automation System",
                description="""Built a complete recruitment automation pipeline integrating Airtable + Python scripts + LLMs. Automates candidate data collection, compression, shortlisting, and AI-driven enrichment for faster hiring.""",
                repo_url="https://github.com/Anurag02012004/Multi-Table-Data-Model",
                tech_stack=["Python", "TensorFlow", "OpenCV", "Flask"]
            ),
            # Project(
            #     title="RecyClique",
            #     description="""Waste management app that gamifies recycling. Enabled users to track waste disposal, 
            #     earn points, and contribute to sustainability goals.""",
            #     repo_url="https://github.com/Anurag02012004/RecyClique",
            #     tech_stack=["React Native", "Firebase", "Node.js"]
            # ),
            Project(
                title="World Latest News App",
                description="""Mobile app delivering latest global news with personalized feeds using 
                NewsAPI + React Native. Features included offline mode and push notifications.""",
                repo_url="https://github.com/Anurag02012004/NewsWithAnurag",
                tech_stack=["React Native", "Redux", "Node.js", "NewsAPI"]
            )
            # Project(
            #     title="Rugrawasa",
            #     description="""Blockchain-based decentralized rental platform enabling transparent 
            #     and secure house rental agreements on Ethereum.""",
            #     repo_url="https://github.com/Anurag02012004/Rugrawasa",
            #     tech_stack=["Solidity", "Hardhat", "Ethers.js", "React.js"]
            # )
        ]
        db.add_all(projects)
        
        # ------------------ Experience & Research ------------------
        experiences = [
            Experience(
                role="Deep Learning Researcher",
                company="IIIT Kalyani - Research Project",
                location="Kalyani, India",
                start_date=date(2025, 1, 1),
                end_date=date(2025, 5, 31),
                description=[
                    "Developed a multi-modal fake news detection system using transformer models (BERT, RoBERTa) + computer vision.",
                    "Implemented ensemble learning combining text + image verification with 92% accuracy.",
                    "Optimized performance using distributed training + GPU acceleration (45% faster inference).",
                    "Published findings in research symposium and contributed to open-source ML community."
                ]
            )
        ]
        db.add_all(experiences)
        
        # ------------------ Achievements ------------------
        achievements = [
            Experience(
                role="Achievements & Coding Profile",
                company="Self",
                location="Online",
                start_date=None,
                end_date=None,
                description=[
                    "LeetCode: Solved 600+(accross multiple platform) problems | Global Top 16% | Contest Rating 1655",
                    "Competitive Programming: Regular participant in Multiple contests"
                ]
            )
        ]
        db.add_all(achievements)
        
        # ------------------ Certificates ------------------
        certificates = [
            Certificate(
                title="Data Science Professional",
                issuer="Oracle University",
                issue_date=date(2025, 7, 14),
                credential_url="https://drive.google.com/file/d/1s3p1vENZEiPoMhMK02a5fFDZ3Xo3HFiJ/view?usp=sharing",
                description="Professional certification in Data Science fundamentals and advanced techniques"
            ),
            Certificate(
                title="Gen AI Professional",
                issuer="Oracle University", 
                issue_date=date(2024, 8, 14),
                credential_url="https://drive.google.com/file/d/1ieGZnxknXUWtUz8EnXjjj3gTAA0ESYkH/view?usp=sharing",
                description="Specialization in Generative AI technologies and applications"
            ),
            Certificate(
                title="Fusion AI Agent Studio Foundations Associate",
                issuer="Oracle University",
                issue_date=date(2024, 8, 20), 
                credential_url="https://drive.google.com/file/d/1nzO2xyd55V6Kb2nevvByfx7OBoBpVSKI/view?usp=sharing",
                description="Foundation level certification in AI Agent development using Oracle Fusion"
            ),
            Certificate(
                title="React Native & React with NodeJS, MongoDB, ReactJS",
                issuer="Oak Academy",
                issue_date=date(2024, 3, 1),
                credential_url="https://www.udemy.com/certificate/UC-ReactNativeCert/",
                description="Comprehensive full-stack development course covering modern web and mobile technologies"
            )
        ]
        db.add_all(certificates)
        
        # Commit to DB
        db.commit()
        logger.info("Database seeded successfully with Anurag's structured resume data!")
    
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
