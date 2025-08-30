#!/bin/bash

# AI-Powered Resume Setup Script
echo "🚀 Setting up AI-Powered Resume Application..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create environment files if they don't exist
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend environment file..."
    cp backend/.env.example backend/.env
    echo "✅ Backend .env created. Please edit it with your API keys."
fi

if [ ! -f frontend/.env.local ]; then
    echo "📝 Creating frontend environment file..."
    cp frontend/.env.local.example frontend/.env.local
    echo "✅ Frontend .env.local created."
fi

echo "🐳 Starting Docker containers..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if backend is running
if curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo "✅ Backend is running on http://localhost:8000"
else
    echo "⚠️ Backend might not be ready yet. Check logs with: docker-compose logs backend"
fi

# Seed the database
echo "🌱 Seeding database with sample data..."
docker-compose exec -T backend python -m app.seed

echo "🎉 Setup complete!"
echo ""
echo "🔗 URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "💡 Next steps:"
echo "1. Edit backend/.env with your API keys (OpenAI, Pinecone, Cohere)"
echo "2. Restart containers: docker-compose restart"
echo "3. Sync vector database: curl -X POST http://localhost:8000/api/v1/sync-vector-db"
echo ""
echo "📖 View logs: docker-compose logs -f"
echo "🛑 Stop services: docker-compose down"
