#!/bin/bash

# Health check script for backend service
echo "🔍 Checking backend health..."

# Check if backend is responding
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health)

if [ $response -eq 200 ]; then
    echo "✅ Backend is healthy (HTTP $response)"
    
    # Check database connection
    db_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/profile)
    
    if [ $db_response -eq 200 ]; then
        echo "✅ Database connection is healthy"
    else
        echo "⚠️ Database connection issue (HTTP $db_response)"
    fi
    
else
    echo "❌ Backend is not responding (HTTP $response)"
    exit 1
fi

echo "🎉 All systems operational!"
