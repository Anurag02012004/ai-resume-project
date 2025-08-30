# 🚀 Deployment Guide

This guide covers deployment options for the AI-Powered Resume application.

## 📋 Prerequisites

- Docker and Docker Compose installed
- API keys for OpenAI (required), Pinecone and Cohere (optional)
- Git repository access

## 🏠 Local Development

### Quick Start
```bash
# Clone and setup
git clone <your-repo-url>
cd ai-resume-project
./setup.sh
```

### Manual Setup
```bash
# 1. Environment files
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local

# 2. Edit backend/.env with your API keys
# OPENAI_API_KEY=your_key_here

# 3. Start services
docker-compose up --build

# 4. Seed database
docker-compose exec backend python -m app.seed

# 5. Optional: Sync vector database
curl -X POST http://localhost:8000/api/v1/sync-vector-db
```

## ☁️ Cloud Deployment

### Option 1: Vercel + Railway (Recommended)

#### Frontend on Vercel
1. Push code to GitHub
2. Connect repository to Vercel
3. Set environment variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app
   ```
4. Deploy automatically

#### Backend on Railway
1. Create new Railway project
2. Connect GitHub repository
3. Deploy from `/backend` directory
4. Add PostgreSQL database service
5. Set environment variables:
   ```
   DATABASE_URL=postgresql://user:pass@host:port/dbname
   OPENAI_API_KEY=your_openai_key
   PINECONE_API_KEY=your_pinecone_key (optional)
   COHERE_API_KEY=your_cohere_key (optional)
   PINECONE_INDEX_NAME=resume-index
   PINECONE_ENVIRONMENT=gcp-starter
   ```

### Option 2: Full Docker Deployment

#### VPS/Cloud Server
```bash
# 1. Clone repository
git clone <your-repo-url>
cd ai-resume-project

# 2. Copy production compose file
cp docker-compose.prod.yml docker-compose.yml

# 3. Set environment variables
cp backend/.env.example backend/.env
# Edit with your API keys

# 4. Deploy
docker-compose up -d --build

# 5. Setup database
docker-compose exec backend python -m app.seed
```

#### AWS ECS/Azure Container Instances
Use the provided Dockerfiles to build and push images to your container registry.

### Option 3: Kubernetes

Create Kubernetes manifests using the Docker images. Example structure:
```
k8s/
├── namespace.yaml
├── configmap.yaml
├── secret.yaml
├── postgres.yaml
├── backend.yaml
├── frontend.yaml
└── ingress.yaml
```

## 🔧 Configuration

### Required Environment Variables

#### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname

# AI Services
OPENAI_API_KEY=your_openai_key  # Required

# Optional (for enhanced AI features)
PINECONE_API_KEY=your_pinecone_key
COHERE_API_KEY=your_cohere_key
PINECONE_INDEX_NAME=resume-index
PINECONE_ENVIRONMENT=gcp-starter
```

#### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

### API Keys Setup

#### OpenAI (Required)
1. Visit https://platform.openai.com/api-keys
2. Create new API key
3. Add to backend/.env as OPENAI_API_KEY

#### Pinecone (Optional - for enhanced vector search)
1. Visit https://www.pinecone.io/
2. Create free account and get API key
3. Create index with dimension 1536
4. Add to backend/.env

#### Cohere (Optional - for improved reranking)
1. Visit https://dashboard.cohere.ai/
2. Get free API key
3. Add to backend/.env

## 📊 Monitoring & Health Checks

### Health Check Endpoints
- Backend: `GET /api/v1/health`
- Database: `GET /api/v1/profile` (tests DB connection)

### Monitoring Script
```bash
./health-check.sh
```

### Logs
```bash
# Local development
docker-compose logs -f

# Production
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 🔒 Security Considerations

### Production Security
1. **Environment Variables**: Never commit .env files
2. **CORS**: Update CORS settings in production
3. **Database**: Use strong passwords and restrict access
4. **API Keys**: Use environment-specific keys
5. **HTTPS**: Always use HTTPS in production

### Recommended Production Settings
```python
# In backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domains
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## 🚀 Performance Optimization

### Backend
- Use connection pooling for database
- Implement caching for frequently accessed data
- Add rate limiting for API endpoints
- Use async/await for I/O operations

### Frontend
- Enable Next.js caching
- Optimize images and assets
- Implement lazy loading
- Use CDN for static assets

### Database
- Add indexes for frequently queried fields
- Regular database maintenance
- Monitor query performance

## 🔧 Troubleshooting

### Common Issues

#### "Connection refused" errors
- Check if services are running: `docker-compose ps`
- Verify port mappings
- Check firewall settings

#### Database connection issues
- Verify DATABASE_URL format
- Check database credentials
- Ensure database is accessible

#### AI API errors
- Verify API keys are correct
- Check API key permissions
- Monitor API usage limits

#### Build failures
- Clear Docker cache: `docker system prune`
- Check Dockerfile syntax
- Verify all files are copied correctly

### Debug Commands
```bash
# View service status
docker-compose ps

# Check logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db

# Access container shell
docker-compose exec backend bash
docker-compose exec frontend sh

# Reset everything
docker-compose down -v
docker system prune -f
docker-compose up --build
```

## 📈 Scaling

### Horizontal Scaling
- Use load balancer for multiple backend instances
- Implement session storage (Redis)
- Use managed database services

### Vertical Scaling
- Increase container resources
- Optimize database queries
- Use caching layers

### CDN Integration
- Serve static assets via CDN
- Implement edge caching
- Use geographic distribution

## 🔄 CI/CD Pipeline

### GitHub Actions Example
```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Railway
        run: |
          # Your deployment script
```

### Automated Testing
- Unit tests for backend API
- Integration tests for database
- E2E tests for frontend
- Performance testing

---

## 📞 Support

For deployment issues:
1. Check this guide first
2. Review logs for error messages
3. Verify all environment variables
4. Test API endpoints individually
5. Check resource usage and limits

Remember to test thoroughly in a staging environment before production deployment!
