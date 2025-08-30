# 🚀 Quick Start Guide

Get your AI-Powered Resume up and running in 5 minutes!

## ⚡ Prerequisites

- Docker and Docker Compose installed
- OpenAI API key (get one at https://platform.openai.com/api-keys)

## 🏃‍♂️ Quick Setup

1. **Clone and setup**:
   ```bash
   git clone <your-repo-url>
   cd ai-resume-project
   ./setup.sh
   ```

2. **Add your OpenAI API key**:
   ```bash
   # Edit the backend environment file
   nano backend/.env
   
   # Add your key:
   OPENAI_API_KEY=your_openai_key_here
   ```

3. **Restart to apply changes**:
   ```bash
   docker-compose restart
   ```

4. **Test the application**:
   ```bash
   ./test-api.sh
   ```

## 🌐 Access Your Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🎯 What You Get

✅ **Professional Resume Display**
- Clean, responsive design
- Projects, experience, and skills sections
- Mobile-friendly interface

✅ **AI Chat Assistant**
- Natural language queries about your resume
- Context-aware responses
- Source citations for transparency

✅ **Robust Backend API**
- FastAPI with automatic documentation
- PostgreSQL database
- RAG pipeline for intelligent responses

## 🔧 Customization

### Add Your Own Data
Edit `backend/app/seed.py` with your information, then:
```bash
docker-compose exec backend python -m app.seed
```

### Enhanced AI Features (Optional)
Add these to `backend/.env` for better AI performance:
```bash
PINECONE_API_KEY=your_pinecone_key
COHERE_API_KEY=your_cohere_key
```

## 🆘 Need Help?

1. **Check if services are running**: `docker-compose ps`
2. **View logs**: `docker-compose logs -f`
3. **Reset everything**: `docker-compose down -v && docker-compose up --build`
4. **Test API**: `./test-api.sh`

## 🚀 Ready for Production?

See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment options including Vercel and Railway.

---

**That's it!** Your AI-powered resume is now live and ready to impress! 🎉
