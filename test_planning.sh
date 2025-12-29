#!/bin/bash
# Quick Test Runner for Planning Orchestrator
# Usage: ./test_planning.sh [category]

set -e

CORTEX_ROOT="/Users/asifhussain/PROJECTS/CORTEX"
cd "$CORTEX_ROOT"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Planning Orchestrator Test Suite${NC}"
echo -e "${BLUE}========================================${NC}\n"

case "${1:-all}" in
    
    "interactive")
        echo -e "${GREEN}Running Interactive Planning Tests (18 tests)${NC}"
        python3 -m pytest tests/orchestrators/planning/test_interactive_planning_session.py -v
        ;;
    
    "toolkit")
        echo -e "${GREEN}Running Toolkit Integration Tests (9 tests)${NC}"
        python3 -m pytest tests/orchestrators/planning/test_toolkit_integration.py -v
        ;;
    
    "tdd")
        echo -e "${GREEN}Running TDD Workflow Tests (18 tests)${NC}"
        python3 -m pytest tests/orchestrators/planning/test_planning_orchestrator_tdd_manifest.py -v
        ;;
    
    "intelligence")
        echo -e "${GREEN}Running Intelligence Layer Tests (40+ tests)${NC}"
        python3 -m pytest tests/orchestrators/planning/intelligence/ -v
        ;;
    
    "quick")
        echo -e "${GREEN}Running Quick Smoke Tests (27 tests)${NC}"
        python3 -m pytest \
            tests/orchestrators/planning/test_interactive_planning_session.py \
            tests/orchestrators/planning/test_toolkit_integration.py \
            -v --tb=short
        ;;
    
    "coverage")
        echo -e "${GREEN}Running with Coverage Report${NC}"
        python3 -m pytest tests/orchestrators/planning/ \
            --cov=src/orchestrators/planning \
            --cov-report=html \
            --cov-report=term-missing
        echo -e "\n${YELLOW}Coverage report generated: htmlcov/index.html${NC}"
        ;;
    
    "failed")
        echo -e "${GREEN}Re-running Previously Failed Tests${NC}"
        python3 -m pytest tests/orchestrators/planning/ --lf -v
        ;;
    
    "all")
        echo -e "${GREEN}Running ALL Planning Tests (441+ tests)${NC}"
        python3 -m pytest tests/orchestrators/planning/ -v --tb=short
        ;;
    
    "help")
        echo -e "${YELLOW}Usage: ./test_planning.sh [category]${NC}\n"
        echo "Categories:"
        echo "  interactive  - Interactive planning session tests (18 tests)"
        echo "  toolkit      - Toolkit integration tests (9 tests)"
        echo "  tdd          - TDD workflow tests (18 tests)"
        echo "  intelligence - Intelligence layer tests (40+ tests)"
        echo "  quick        - Quick smoke tests (27 tests)"
        echo "  coverage     - Run with coverage report"
        echo "  failed       - Re-run only failed tests"
        echo "  all          - Run complete test suite (441+ tests)"
        echo "  help         - Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./test_planning.sh interactive"
        echo "  ./test_planning.sh quick"
        echo "  ./test_planning.sh coverage"
        ;;
    
    *)
        echo -e "${YELLOW}Unknown category: $1${NC}"
        echo "Run './test_planning.sh help' for usage"
        exit 1
        ;;
esac

echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}✅ Test run complete!${NC}"
echo -e "${BLUE}========================================${NC}"
