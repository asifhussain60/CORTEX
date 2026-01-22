#!/bin/bash
# CORTEX Test Execution Wrapper - Optimized for Multi-Core Machines
# Provides convenient shortcuts for various test strategies
#
# Usage:
#   ./scripts/run_tests.sh smoke          # Fast baseline (< 30s)
#   ./scripts/run_tests.sh fast           # Unit tests only (2-3min on 4 cores)
#   ./scripts/run_tests.sh standard       # Default comprehensive (5-8min on 4 cores)
#   ./scripts/run_tests.sh comprehensive  # All tests including e2e (10-15min)
#   ./scripts/run_tests.sh debug          # Single test debugging (serial mode)
#   ./scripts/run_tests.sh profile        # Performance profiling (20 slowest)
#   ./scripts/run_tests.sh analyze        # Full test suite analysis

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Detect number of CPU cores (auto-scale parallelism)
if [[ "$OSTYPE" == "darwin"* ]]; then
    CORES=$(sysctl -n hw.ncpu)
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    CORES=$(nproc)
else
    CORES=4  # Fallback
fi

print_header() {
    echo -e "${BLUE}════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

case "${1:-standard}" in
    smoke)
        print_header "SMOKE TESTS: Baseline Health Check (~30 seconds)"
        echo "Running minimal test set for rapid regression detection..."
        echo "Cores: $CORES"
        python3 -m pytest tests/unit \
            -m "smoke or (unit and not slow)" \
            -n auto \
            --dist loadscope \
            --tb=line \
            -q \
            --maxfail=3
        print_success "Smoke tests completed"
        ;;
        
    fast)
        print_header "FAST TESTS: Essential Unit Tests (~2-3 minutes on $CORES cores)"
        echo "Running unit + essential tests (excluding slow/integration)..."
        python3 -m pytest tests/unit \
            -m "not slow and not integration" \
            -n auto \
            --dist loadscope \
            --tb=short \
            --maxfail=5
        print_success "Fast tests completed"
        ;;
        
    standard)
        print_header "STANDARD TESTS: Default Comprehensive (~5-8 minutes on $CORES cores)"
        echo "Running full unit test suite with auto-parallelization..."
        python3 -m pytest tests/unit \
            -n auto \
            --dist loadscope \
            --tb=short \
            --maxfail=5 \
            -v
        print_success "Standard tests completed"
        ;;
        
    comprehensive)
        print_header "COMPREHENSIVE TESTS: All Tests Including E2E (~10-15 minutes)"
        echo "Running ALL tests (unit, integration, e2e)..."
        python3 -m pytest tests/ \
            -n auto \
            --dist loadscope \
            --tb=short \
            --maxfail=5 \
            -v
        print_success "Comprehensive tests completed"
        ;;
        
    serial)
        print_header "SERIAL DEBUGGING MODE: Single-threaded Execution"
        echo "Running tests without parallelization (debugging)..."
        echo "Useful for: troubleshooting race conditions, debugging, -x stop on first failure"
        python3 -m pytest tests/unit \
            -n 0 \
            -x \
            --tb=long \
            -vv
        ;;
        
    profile)
        print_header "PERFORMANCE PROFILE: Test Timing Analysis"
        echo "Analyzing and ranking top 20 slowest tests..."
        python3 -m pytest tests/unit \
            --tb=no \
            -q \
            --durations=20 \
            --durations-min=0.1
        ;;
        
    analyze)
        print_header "TEST SUITE ANALYSIS: Comprehensive Health Report"
        echo "Analyzing test collection and performance characteristics..."
        python3 scripts/test_optimization_suite.py analyze --all --verbose
        ;;
        
    cleanup)
        print_header "TEST CLEANUP: Identify Obsolete/Broken Tests"
        echo "Scanning for tests with outdated imports or patterns..."
        python3 scripts/test_optimization_suite.py cleanup
        ;;
        
    strategies)
        print_header "AVAILABLE TEST STRATEGIES"
        python3 scripts/test_optimization_suite.py strategies
        ;;
        
    ac)
        print_header "AC-COMPLIANCE TESTS: Audit Trail Verification"
        echo "Running tests tagged with AC-IDs for governance verification..."
        python3 -m pytest tests/ \
            -m ac \
            -n auto \
            --tb=short \
            -v
        print_success "AC compliance tests completed"
        ;;
        
    mcp)
        print_header "MCP PROTOCOL TESTS: Compliance Verification"
        echo "Running MCP protocol compliance tests..."
        python3 -m pytest tests/unit/mcp \
            -n auto \
            --dist loadscope \
            -v
        print_success "MCP protocol tests completed"
        ;;
        
    governance)
        print_header "GOVERNANCE TESTS: Compliance & Audit"
        echo "Running governance and compliance verification tests..."
        python3 -m pytest tests/unit/domain_brain \
            -m "ac or governance" \
            -n auto \
            --tb=short \
            -v
        print_success "Governance tests completed"
        ;;
        
    coverage)
        print_header "COVERAGE REPORT: Test Coverage Analysis"
        echo "Generating code coverage report..."
        python3 -m pytest tests/unit \
            --cov=cortex \
            --cov-report=html \
            --cov-report=term-missing \
            -n auto \
            --tb=short
        print_success "Coverage report generated (check htmlcov/index.html)"
        ;;
        
    *)
        echo "CORTEX Test Execution Wrapper - Optimized Testing"
        echo ""
        echo "Usage: $0 {strategy}"
        echo ""
        echo "📊 STRATEGIES:"
        echo "  smoke           - Baseline health check (<30s) - USE FOR: Quick regression detection"
        echo "  fast            - Unit tests only (2-3min) - USE FOR: Development iteration"
        echo "  standard        - Default comprehensive (5-8min) - USE FOR: Pre-commit validation"
        echo "  comprehensive   - All tests including e2e (10-15min) - USE FOR: Release verification"
        echo "  serial          - Debugging mode (sequential) - USE FOR: Troubleshooting"
        echo "  profile         - Performance analysis - USE FOR: Optimization"
        echo "  analyze         - Full health report - USE FOR: Planning"
        echo ""
        echo "🎯 SPECIALIZED:"
        echo "  ac              - AC compliance tests - USE FOR: Audit verification"
        echo "  mcp             - MCP protocol tests - USE FOR: Protocol validation"
        echo "  governance      - Governance compliance - USE FOR: Compliance checks"
        echo "  coverage        - Coverage report - USE FOR: Metrics"
        echo "  cleanup         - Identify broken tests - USE FOR: Maintenance"
        echo "  strategies      - Show all strategies - USE FOR: Reference"
        echo ""
        echo "⚙️  SYSTEM INFO:"
        echo "  Detected cores: $CORES"
        echo "  Parallelism: auto (pytest-xdist will scale to $CORES workers)"
        echo ""
        echo "💡 EXAMPLES:"
        echo "  # Quick regression check during development"
        echo "  $0 smoke"
        echo ""
        echo "  # Before committing code"
        echo "  $0 fast"
        echo ""
        echo "  # Before creating a PR"
        echo "  $0 standard"
        echo ""
        echo "  # Before release"
        echo "  $0 comprehensive"
        echo ""
        exit 0
        ;;
esac

exit $?
