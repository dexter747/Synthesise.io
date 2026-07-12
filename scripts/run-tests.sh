#!/bin/bash

# Comprehensive Test Runner for Synthesize.io API
# ================================================
# Runs all tests with coverage reporting

set -e

echo "🧪 Synthesize.io - Comprehensive Test Suite"
echo "==========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Change to API directory
cd "$(dirname "$0")/../apps/api"

# Activate virtual environment
if [ -f "../../.venv/bin/activate" ]; then
    source ../../.venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

echo -e "${BLUE}📋 Test Plan:${NC}"
echo "  1. Unit Tests"
echo "  2. Integration Tests"
echo "  3. API Endpoint Tests"
echo "  4. Service Layer Tests"
echo "  5. Coverage Report"
echo ""

# Function to run tests with reporting
run_test_suite() {
    local name=$1
    local path=$2
    local marker=$3
    
    echo -e "${YELLOW}▶ Running $name...${NC}"
    
    if [ -n "$marker" ]; then
        pytest "$path" -m "$marker" -v --tb=short || {
            echo -e "${RED}✗ $name failed${NC}"
            return 1
        }
    else
        pytest "$path" -v --tb=short || {
            echo -e "${RED}✗ $name failed${NC}"
            return 1
        }
    fi
    
    echo -e "${GREEN}✓ $name passed${NC}"
    echo ""
}

# Track overall success
OVERALL_SUCCESS=true

# 1. Unit Tests
echo -e "${BLUE}═══════════════════════════════════${NC}"
echo -e "${BLUE}  UNIT TESTS${NC}"
echo -e "${BLUE}═══════════════════════════════════${NC}"
run_test_suite "Unit Tests" "tests/unit/" "" || OVERALL_SUCCESS=false

# 2. Service Tests
echo -e "${BLUE}═══════════════════════════════════${NC}"
echo -e "${BLUE}  SERVICE LAYER TESTS${NC}"
echo -e "${BLUE}═══════════════════════════════════${NC}"
run_test_suite "Auth Service" "tests/test_auth.py" "" || OVERALL_SUCCESS=false
run_test_suite "User Service" "tests/test_users.py" "" || OVERALL_SUCCESS=false
run_test_suite "Dataset Service" "tests/test_datasets.py" "" || OVERALL_SUCCESS=false
run_test_suite "Subscription Service" "tests/test_subscriptions.py" "" || OVERALL_SUCCESS=false
run_test_suite "API Keys Service" "tests/test_api_keys.py" "" || OVERALL_SUCCESS=false
run_test_suite "Webhooks Service" "tests/test_webhooks.py" "" || OVERALL_SUCCESS=false

# 3. Data Factory Tests
echo -e "${BLUE}═══════════════════════════════════${NC}"
echo -e "${BLUE}  DATA FACTORY TESTS${NC}"
echo -e "${BLUE}═══════════════════════════════════${NC}"
run_test_suite "Data Factory Endpoints" "tests/test_data_factory.py" "" || OVERALL_SUCCESS=false

# 4. Integration Tests
echo -e "${BLUE}═══════════════════════════════════${NC}"
echo -e "${BLUE}  INTEGRATION TESTS${NC}"
echo -e "${BLUE}═══════════════════════════════════${NC}"
run_test_suite "Integration Tests" "tests/integration/" "integration" || OVERALL_SUCCESS=false

# 5. Admin Tests
echo -e "${BLUE}═══════════════════════════════════${NC}"
echo -e "${BLUE}  ADMIN & MONITORING TESTS${NC}"
echo -e "${BLUE}═══════════════════════════════════${NC}"
run_test_suite "Admin Endpoints" "tests/test_admin.py" "" || OVERALL_SUCCESS=false
run_test_suite "Monitoring" "tests/test_monitoring.py" "" || OVERALL_SUCCESS=false

# 6. Coverage Report
echo -e "${BLUE}═══════════════════════════════════${NC}"
echo -e "${BLUE}  COVERAGE REPORT${NC}"
echo -e "${BLUE}═══════════════════════════════════${NC}"
echo -e "${YELLOW}▶ Generating coverage report...${NC}"

pytest tests/ \
    --cov=app \
    --cov-report=html \
    --cov-report=term \
    --cov-report=json \
    -v \
    --tb=short \
    || OVERALL_SUCCESS=false

echo ""
echo -e "${GREEN}Coverage report generated at: htmlcov/index.html${NC}"
echo ""

# Summary
echo -e "${BLUE}═══════════════════════════════════${NC}"
echo -e "${BLUE}  TEST SUMMARY${NC}"
echo -e "${BLUE}═══════════════════════════════════${NC}"

if [ "$OVERALL_SUCCESS" = true ]; then
    echo -e "${GREEN}✓ All test suites passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Open htmlcov/index.html to view detailed coverage"
    echo "  2. Review any warnings or deprecations"
    echo "  3. Proceed to user acceptance testing"
    exit 0
else
    echo -e "${RED}✗ Some test suites failed${NC}"
    echo ""
    echo "Please:"
    echo "  1. Review the errors above"
    echo "  2. Fix failing tests"
    echo "  3. Re-run the test suite"
    exit 1
fi
