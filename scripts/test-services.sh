#!/bin/bash

# Test all services connectivity and functionality

set -e

echo "🧪 Testing Synthesize.io Services..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if services are running
echo "1️⃣  Checking if services are running..."

# Check PostgreSQL
if docker ps | grep -q synthesize-postgres; then
    echo -e "${GREEN}✅ PostgreSQL container is running${NC}"
    
    # Test PostgreSQL connection
    if docker exec synthesize-postgres pg_isready -U synthesize > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PostgreSQL is accepting connections${NC}"
    else
        echo -e "${RED}❌ PostgreSQL is not ready${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ PostgreSQL container is not running${NC}"
    echo "   Run: docker-compose up -d postgres"
    exit 1
fi

# Check Redis
if docker ps | grep -q synthesize-redis; then
    echo -e "${GREEN}✅ Redis container is running${NC}"
    
    # Test Redis connection
    if docker exec synthesize-redis redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Redis is accepting connections${NC}"
    else
        echo -e "${RED}❌ Redis is not ready${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Redis container is not running${NC}"
    echo "   Run: docker-compose up -d redis"
    exit 1
fi

echo ""
echo "2️⃣  Testing API endpoints..."

# Wait a moment for API to be ready
sleep 2

# Test FastAPI health endpoint
API_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000")
if [ "$API_HEALTH" = "200" ]; then
    echo -e "${GREEN}✅ FastAPI /health endpoint responding (200)${NC}"
else
    echo -e "${YELLOW}⚠️  FastAPI /health endpoint not responding (got $API_HEALTH)${NC}"
    echo "   This is expected if API is not started yet"
fi

# Test FastAPI root endpoint
API_ROOT=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ 2>/dev/null || echo "000")
if [ "$API_ROOT" = "200" ]; then
    echo -e "${GREEN}✅ FastAPI root endpoint responding (200)${NC}"
else
    echo -e "${YELLOW}⚠️  FastAPI root endpoint not responding (got $API_ROOT)${NC}"
    echo "   Start API with: cd apps/api && source venv/bin/activate && uvicorn app.main:app --reload"
fi

# Test API docs
API_DOCS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs 2>/dev/null || echo "000")
if [ "$API_DOCS" = "200" ]; then
    echo -e "${GREEN}✅ FastAPI /docs endpoint responding (200)${NC}"
else
    echo -e "${YELLOW}⚠️  FastAPI /docs endpoint not responding${NC}"
fi

echo ""
echo "3️⃣  Testing frontend applications..."

# Test Web App
WEB_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "000")
if [ "$WEB_STATUS" = "200" ] || [ "$WEB_STATUS" = "304" ]; then
    echo -e "${GREEN}✅ User Web App responding at http://localhost:3000${NC}"
else
    echo -e "${YELLOW}⚠️  User Web App not responding (got $WEB_STATUS)${NC}"
    echo "   Start with: pnpm dev:web"
fi

# Test Admin Portal
ADMIN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3001 2>/dev/null || echo "000")
if [ "$ADMIN_STATUS" = "200" ] || [ "$ADMIN_STATUS" = "304" ]; then
    echo -e "${GREEN}✅ Admin Portal responding at http://localhost:3001${NC}"
else
    echo -e "${YELLOW}⚠️  Admin Portal not responding (got $ADMIN_STATUS)${NC}"
    echo "   Start with: pnpm dev:admin"
fi

echo ""
echo "4️⃣  Checking database connectivity..."

# Test database connection from Python
DB_TEST=$(docker exec synthesize-postgres psql -U synthesize -d synthesizedb -c "SELECT 1" 2>&1 || echo "failed")
if echo "$DB_TEST" | grep -q "1 row"; then
    echo -e "${GREEN}✅ Database query successful${NC}"
else
    echo -e "${RED}❌ Database query failed${NC}"
    exit 1
fi

# Check if tables exist
TABLES=$(docker exec synthesize-postgres psql -U synthesize -d synthesizedb -c "\dt" 2>&1 || echo "")
if [ -n "$TABLES" ]; then
    echo -e "${GREEN}✅ Database tables exist${NC}"
else
    echo -e "${YELLOW}⚠️  No tables found. Run migrations: pnpm db:migrate${NC}"
fi

echo ""
echo "5️⃣  Testing Redis functionality..."

# Test Redis SET/GET
docker exec synthesize-redis redis-cli SET test_key "test_value" > /dev/null
REDIS_GET=$(docker exec synthesize-redis redis-cli GET test_key)
if [ "$REDIS_GET" = "test_value" ]; then
    echo -e "${GREEN}✅ Redis SET/GET working${NC}"
    docker exec synthesize-redis redis-cli DEL test_key > /dev/null
else
    echo -e "${RED}❌ Redis SET/GET failed${NC}"
    exit 1
fi

echo ""
echo "📊 Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Infrastructure:"
echo "  ✅ PostgreSQL: Running and connected"
echo "  ✅ Redis: Running and functional"
echo ""
echo "Applications:"
if [ "$API_ROOT" = "200" ]; then
    echo "  ✅ FastAPI Backend: http://localhost:8000"
else
    echo "  ⚠️  FastAPI Backend: Not started"
fi

if [ "$WEB_STATUS" = "200" ] || [ "$WEB_STATUS" = "304" ]; then
    echo "  ✅ User Web App: http://localhost:3000"
else
    echo "  ⚠️  User Web App: Not started"
fi

if [ "$ADMIN_STATUS" = "200" ] || [ "$ADMIN_STATUS" = "304" ]; then
    echo "  ✅ Admin Portal: http://localhost:3001"
else
    echo "  ⚠️  Admin Portal: Not started"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$API_ROOT" = "200" ] && ([ "$WEB_STATUS" = "200" ] || [ "$WEB_STATUS" = "304" ]) && ([ "$ADMIN_STATUS" = "200" ] || [ "$ADMIN_STATUS" = "304" ]); then
    echo -e "${GREEN}🎉 All services are running and connected!${NC}"
else
    echo -e "${YELLOW}⚠️  Some services are not running. Start them with: pnpm dev${NC}"
fi

echo ""
