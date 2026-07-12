#!/bin/bash

echo "==================================="
echo "Testing Synthesize.io API Workflow"
echo "==================================="
echo ""

# Wait for API to be ready
echo "⏳ Waiting for API to be ready..."
sleep 3

# Test 1: Health Check
echo "1️⃣  Testing API Health..."
curl -s http://localhost:8000/health | jq '.' || echo "❌ API not responding"
echo ""

# Test 2: Get API Documentation
echo "2️⃣  Checking API Documentation..."
curl -s http://localhost:8000/docs | head -n 5
echo "✅ API docs available at http://localhost:8000/docs"
echo ""

# Test 3: Register a new user
echo "3️⃣  Testing User Registration..."
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "name": "Test User"
  }')
echo "$REGISTER_RESPONSE" | jq '.'
echo ""

# Test 4: Login
echo "4️⃣  Testing User Login..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }')
echo "$LOGIN_RESPONSE" | jq '.'

# Extract token
TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token // empty')
if [ -z "$TOKEN" ]; then
  echo "❌ Failed to get auth token"
  exit 1
fi
echo "✅ Got auth token: ${TOKEN:0:20}..."
echo ""

# Test 5: Get User Profile
echo "5️⃣  Testing Get User Profile..."
curl -s http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN" | jq '.'
echo ""

# Test 6: Create Dataset
echo "6️⃣  Testing Create Dataset..."
DATASET_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/datasets \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Customer Data",
    "description": "Sample customer dataset for testing",
    "schema_definition": [
      {
        "name": "customer_id",
        "display_name": "Customer ID",
        "field_type": "uuid",
        "is_nullable": false,
        "is_unique": true
      },
      {
        "name": "email",
        "display_name": "Email Address",
        "field_type": "email",
        "is_nullable": false,
        "is_unique": true
      },
      {
        "name": "name",
        "display_name": "Full Name",
        "field_type": "name",
        "is_nullable": false,
        "is_unique": false
      }
    ]
  }')
echo "$DATASET_RESPONSE" | jq '.'

DATASET_ID=$(echo "$DATASET_RESPONSE" | jq -r '.id // empty')
if [ -z "$DATASET_ID" ]; then
  echo "❌ Failed to create dataset"
  exit 1
fi
echo "✅ Created dataset with ID: $DATASET_ID"
echo ""

# Test 7: List Datasets
echo "7️⃣  Testing List Datasets..."
curl -s http://localhost:8000/api/v1/datasets \
  -H "Authorization: Bearer $TOKEN" | jq '.'
echo ""

# Test 8: Create Generation Job
echo "8️⃣  Testing Create Generation Job..."
JOB_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/jobs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"dataset_id\": \"$DATASET_ID\",
    \"rows_requested\": 100
  }")
echo "$JOB_RESPONSE" | jq '.'

JOB_ID=$(echo "$JOB_RESPONSE" | jq -r '.id // empty')
if [ -z "$JOB_ID" ]; then
  echo "❌ Failed to create job"
else
  echo "✅ Created job with ID: $JOB_ID"
fi
echo ""

# Test 9: Check Job Status
echo "9️⃣  Testing Get Job Status..."
sleep 2
curl -s http://localhost:8000/api/v1/jobs/$JOB_ID \
  -H "Authorization: Bearer $TOKEN" | jq '.'
echo ""

# Test 10: Get Usage Stats
echo "🔟 Testing Get Usage Stats..."
curl -s http://localhost:8000/api/v1/users/me/stats \
  -H "Authorization: Bearer $TOKEN" | jq '.'
echo ""

echo "==================================="
echo "✅ Workflow Testing Complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "- Visit http://localhost:3000 for Web App"
echo "- Visit http://localhost:3001 for Admin Dashboard"
echo "- Visit http://localhost:8000/docs for API Documentation"
