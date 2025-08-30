#!/bin/bash

# API Testing Script for AI Resume Backend
BASE_URL="http://localhost:8000"

echo "🧪 Testing AI Resume API endpoints..."
echo "Base URL: $BASE_URL"
echo ""

# Test 1: Health Check
echo "1. Testing health endpoint..."
response=$(curl -s -w "%{http_code}" "$BASE_URL/api/v1/health")
http_code=${response: -3}
body=${response%???}

if [ "$http_code" = "200" ]; then
    echo "✅ Health check passed"
    echo "   Response: $body"
else
    echo "❌ Health check failed (HTTP $http_code)"
    echo "   Response: $body"
fi
echo ""

# Test 2: Profile Data
echo "2. Testing profile endpoint..."
response=$(curl -s -w "%{http_code}" "$BASE_URL/api/v1/profile")
http_code=${response: -3}
body=${response%???}

if [ "$http_code" = "200" ]; then
    echo "✅ Profile data retrieved successfully"
    # Count projects, experiences, skills
    projects=$(echo "$body" | grep -o '"projects":\[' | wc -l)
    experiences=$(echo "$body" | grep -o '"experiences":\[' | wc -l)
    skills=$(echo "$body" | grep -o '"skills":\[' | wc -l)
    echo "   Found data sections: projects($projects), experiences($experiences), skills($skills)"
else
    echo "❌ Profile data failed (HTTP $http_code)"
    echo "   Response: $body"
fi
echo ""

# Test 3: Query Resume
echo "3. Testing query endpoint..."
query_data='{"query": "What programming languages do you know?"}'
response=$(curl -s -w "%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d "$query_data" \
    "$BASE_URL/api/v1/query-resume")
    
http_code=${response: -3}
body=${response%???}

if [ "$http_code" = "200" ]; then
    echo "✅ Query processed successfully"
    # Extract answer length
    answer_length=$(echo "$body" | grep -o '"answer":"[^"]*"' | sed 's/"answer":"//;s/"//' | wc -c)
    echo "   Answer length: $answer_length characters"
else
    echo "❌ Query failed (HTTP $http_code)"
    echo "   Response: $body"
fi
echo ""

# Test 4: Individual endpoints
echo "4. Testing individual endpoints..."

endpoints=("projects" "experiences" "skills")
for endpoint in "${endpoints[@]}"; do
    echo "   Testing $endpoint..."
    response=$(curl -s -w "%{http_code}" "$BASE_URL/api/v1/$endpoint")
    http_code=${response: -3}
    
    if [ "$http_code" = "200" ]; then
        echo "   ✅ $endpoint endpoint working"
    else
        echo "   ❌ $endpoint endpoint failed (HTTP $http_code)"
    fi
done
echo ""

# Test 5: Root endpoint
echo "5. Testing root endpoint..."
response=$(curl -s -w "%{http_code}" "$BASE_URL/")
http_code=${response: -3}
body=${response%???}

if [ "$http_code" = "200" ]; then
    echo "✅ Root endpoint working"
    echo "   API version info retrieved"
else
    echo "❌ Root endpoint failed (HTTP $http_code)"
fi
echo ""

# Test 6: Error handling
echo "6. Testing error handling..."
response=$(curl -s -w "%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d '{"query": ""}' \
    "$BASE_URL/api/v1/query-resume")
    
http_code=${response: -3}

if [ "$http_code" = "400" ]; then
    echo "✅ Error handling working (empty query rejected)"
else
    echo "⚠️ Error handling may need attention (HTTP $http_code)"
fi
echo ""

echo "🎉 API testing complete!"
echo ""
echo "📖 View API documentation at: $BASE_URL/docs"
echo "🔄 ReDoc documentation at: $BASE_URL/redoc"
