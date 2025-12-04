#!/bin/bash
# Dashboard Test Runner
# 
# Runs comprehensive test suite for CORTEX Dashboard
# 
# Usage:
#   ./run-tests.sh                 # Run all tests
#   ./run-tests.sh unit            # Run unit tests only
#   ./run-tests.sh integration     # Run integration tests only
#   ./run-tests.sh e2e             # Run E2E tests only
#   ./run-tests.sh coverage        # Run with coverage report

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test directory
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UI_DIR="$(dirname "$TEST_DIR")"

echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     CORTEX Dashboard Test Suite Runner        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo ""

# Check if HTTP server is running
echo -e "${YELLOW}→ Checking HTTP server...${NC}"
if ! lsof -ti:8080 > /dev/null 2>&1; then
    echo -e "${RED}✗ HTTP server not running on port 8080${NC}"
    echo -e "${YELLOW}→ Starting server...${NC}"
    cd "$UI_DIR" && python3 -m http.server 8080 > /dev/null 2>&1 &
    SERVER_PID=$!
    echo -e "${GREEN}✓ Server started (PID: $SERVER_PID)${NC}"
    KILL_SERVER=true
    sleep 2
else
    echo -e "${GREEN}✓ Server already running${NC}"
    KILL_SERVER=false
fi

# Check for node_modules
echo -e "${YELLOW}→ Checking dependencies...${NC}"
cd "$TEST_DIR"
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}→ Installing test dependencies...${NC}"
    npm install
fi
echo -e "${GREEN}✓ Dependencies ready${NC}"

# Determine test type
TEST_TYPE="${1:-all}"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Running Tests: ${TEST_TYPE}${NC}"
echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo ""

# Run tests based on type
case "$TEST_TYPE" in
    unit)
        echo -e "${YELLOW}→ Running unit tests...${NC}"
        npm run test:unit
        ;;
    integration)
        echo -e "${YELLOW}→ Running integration tests...${NC}"
        npm run test:integration
        ;;
    e2e)
        echo -e "${YELLOW}→ Running E2E tests...${NC}"
        npm run test:e2e
        ;;
    coverage)
        echo -e "${YELLOW}→ Running tests with coverage...${NC}"
        npm run test:coverage
        ;;
    all)
        echo -e "${YELLOW}→ Running all tests...${NC}"
        npm test
        ;;
    *)
        echo -e "${RED}✗ Unknown test type: $TEST_TYPE${NC}"
        echo -e "${YELLOW}Usage: $0 [unit|integration|e2e|coverage|all]${NC}"
        exit 1
        ;;
esac

TEST_EXIT_CODE=$?

# Cleanup
if [ "$KILL_SERVER" = true ]; then
    echo ""
    echo -e "${YELLOW}→ Stopping test server...${NC}"
    kill $SERVER_PID 2>/dev/null || true
    echo -e "${GREEN}✓ Server stopped${NC}"
fi

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║            ✓ ALL TESTS PASSED                  ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
else
    echo -e "${RED}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║            ✗ TESTS FAILED                      ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════╝${NC}"
fi

exit $TEST_EXIT_CODE
