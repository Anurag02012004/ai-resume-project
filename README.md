# AI-Powered Interactive Resume

A modern, intelligent resume platform that combines traditional resume display with AI-powered query capabilities using Retrieval-Augmented Generation (RAG).

## 🚀 Features

- **Interactive Resume Display**: Beautiful, responsive UI showcasing projects, experience, and skills
- **AI Chat Assistant**: Query resume content using natural language with RAG pipeline
- **Professional UI**: Modern design with Tailwind CSS and smooth animations
- **Real-time Responses**: Fast AI responses with source citations
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Docker Support**: Easy deployment with Docker Compose

## 🏗️ Architecture Overview

### Frontend
- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **State Management**: React Hooks

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL with SQLAlchemy 2.0
- **Vector Database**: Pinecone
- **AI Models**:
  - Embeddings: OpenAI text-embedding-3-small
  - Reranker: Cohere rerank-english-v2.0
  - Text Generation: Contextual responses with fallback support

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Development**: Hot reload for both frontend and backend
- **Production Ready**: Optimized for deployment on Vercel and Railway

## 🛠️ Local Setup

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ai-resume-project
```

### 2. Backend Setup
```bash
# Copy environment template
cp backend/.env.example backend/.env

# Edit the .env file with your API keys
# Required: OPENAI_API_KEY
# Optional: PINECONE_API_KEY, COHERE_API_KEY
```

### 3. Frontend Setup
```bash
# Copy environment template
cp frontend/.env.local.example frontend/.env.local

# The default API URL should work for local development
```

### 4. Start with Docker Compose
```bash
# Start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 5. Initialize Database
```bash
# Seed the database with sample data
docker-compose exec backend python -m app.seed

# Optional: Sync vector database (requires Pinecone API key)
curl -X POST http://localhost:8000/api/v1/sync-vector-db
```

### 6. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🚀 Deployment

### Frontend (Vercel)
1. Connect your GitHub repository to Vercel
2. Set environment variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
   ```
3. Deploy automatically on push to main branch

### Backend (Railway)
1. Connect your GitHub repository to Railway
2. Set environment variables:
   ```
   DATABASE_URL=postgresql://user:pass@host:port/dbname
   OPENAI_API_KEY=your_openai_key
   PINECONE_API_KEY=your_pinecone_key
   COHERE_API_KEY=your_cohere_key
   PINECONE_INDEX_NAME=resume-index
   PINECONE_ENVIRONMENT=gcp-starter
   ```
3. Deploy from the `/backend` directory

### Database (Railway)
1. Add a PostgreSQL database service
2. Use the provided DATABASE_URL in your backend environment

## 📚 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message and API info |
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/profile` | Complete profile data |
| POST | `/api/v1/query-resume` | AI-powered resume queries |
| POST | `/api/v1/sync-vector-db` | Sync data to vector database |
| GET | `/api/v1/projects` | Get all projects |
| GET | `/api/v1/experiences` | Get all experiences |
| GET | `/api/v1/skills` | Get all skills |

## 🤖 RAG Pipeline

The AI assistant uses a sophisticated Retrieval-Augmented Generation pipeline:

1. **Data Processing**: Resume data is chunked and embedded using OpenAI's text-embedding-3-small
2. **Vector Storage**: Embeddings stored in Pinecone for fast similarity search
3. **Query Processing**: User queries are embedded and matched against stored vectors
4. **Reranking**: Cohere's rerank-english-v2.0 improves result relevance
5. **Response Generation**: Contextual responses generated with source citations
6. **Fallback Mode**: Works without vector database using keyword matching

## 🎯 Key Features

### Smart Query Handling
- Context-aware responses based on resume content
- Source citations for transparency
- Graceful handling of off-topic queries
- Fallback responses when AI services are unavailable

### Professional UI
- Clean, modern design inspired by top portfolio sites
- Responsive layout for all device sizes
- Smooth animations and transitions
- Intuitive tab-based navigation

### Robust Backend
- Comprehensive error handling
- Retry logic for API calls
- Database connection pooling
- CORS configuration for development

## 🔧 Development

### Running Frontend Only
```bash
cd frontend
npm install
npm run dev
```

### Running Backend Only
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Database Management
```bash
# Reset and reseed database
docker-compose exec backend python -m app.seed

# Access PostgreSQL
docker-compose exec db psql -U user -d mydatabase
```

## 📝 Customization

### Adding Your Data
1. Edit `backend/app/seed.py` with your personal information
2. Run the seed script: `docker-compose exec backend python -m app.seed`
3. Sync vector database: `curl -X POST http://localhost:8000/api/v1/sync-vector-db`

### Styling Changes
- Modify `frontend/app/globals.css` for global styles
- Update `frontend/tailwind.config.js` for custom themes
- Edit `frontend/app/page.jsx` for layout changes

## 🔒 Security Notes

- All API keys are loaded from environment variables
- CORS is configured for development (update for production)
- Database connections use connection pooling
- Input validation on all API endpoints

## 🐛 Troubleshooting

### Common Issues
1. **Database Connection**: Ensure PostgreSQL is running and credentials are correct
2. **API Keys**: Verify all required API keys are set in environment variables
3. **Port Conflicts**: Change ports in docker-compose.yml if needed
4. **Build Errors**: Clear Docker cache with `docker system prune`

### Logs
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs db
```

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review Docker logs
3. Ensure all environment variables are set correctly
4. Verify API keys are valid and have sufficient quota

## 🏆 Remarks

This project demonstrates modern full-stack development with:
- Clean architecture and separation of concerns
- Production-ready containerization
- Comprehensive error handling
- Scalable RAG implementation
- Professional UI/UX design
- Robust API design with proper validation

The application gracefully handles missing API keys and provides fallback functionality, ensuring a smooth user experience even with minimal configuration.

---

**Live Demo**: https://accomplished-contentment-production.up.railway.app
