#!/bin/bash
# Test Performance Auditor - CLI Wrapper
# ========================================
#
# Identifies and reports on hanging/slow tests using enterprise audit logging
#
# Usage:
#   ./scripts/test-audit.sh run [pytest args]          # Run tests with audit
#   ./scripts/test-audit.sh report                      # Generate report
#   ./scripts/test-audit.sh analyze --threshold 1.0    # Analyze slow tests
#   ./scripts/test-audit.sh slow                        # Show slowest tests
#   ./scripts/test-audit.sh hanging                     # Show hanging tests
#
# Examples:
#   ./scripts/test-audit.sh run tests/unit/core/
#   ./scripts/test-audit.sh run tests/ -k "test_conversation"
#   ./scripts/test-audit.sh slow
#   ./scripts/test-audit.sh analyze --threshold 2.0

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
AUDIT_DB="${PROJECT_ROOT}/cortex_brain/state/test_audit.db"
AUDIT_LOG="${PROJECT_ROOT}/test_audit_trail.log"
PERFORMANCE_REPORT="${PROJECT_ROOT}/test_performance_report.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

function print_header() {
    echo -e "${BOLD}${BLUE}══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}${BLUE}$1${NC}"
    echo -e "${BOLD}${BLUE}══════════════════════════════════════════════════════════════${NC}"
}

function print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

function print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

function print_error() {
    echo -e "${RED}❌ $1${NC}"
}

function show_help() {
    cat << 'EOF'

╔════════════════════════════════════════════════════════════════════════════╗
║          CORTEX Test Performance Auditor - Enterprise Logging              ║
╚════════════════════════════════════════════════════════════════════════════╝

Track, identify, and fix hanging and slow tests using structured audit logging.

COMMANDS:
  run [args...]       Run tests with real-time performance audit
                      Examples:
                        ./test-audit.sh run tests/unit/core/
                        ./test-audit.sh run tests/ -k "orchestrator"

  report              Generate detailed performance report
                      Output: test_performance_report.json

  analyze [opts]      Analyze test performance with threshold
                      Options: --threshold SECONDS (default: 0.5)
                      Example: ./test-audit.sh analyze --threshold 2.0

  slow                Show top 20 slowest tests
  
  hanging             Show hanging/errored tests
  
  logs                Tail real-time audit log
  
  clear               Clear audit database and logs
  
  help                Show this help message

EXAMPLES:

  1. Run tests and audit performance:
     $ ./test-audit.sh run tests/unit/intent_router/
     
  2. View slowest tests from previous run:
     $ ./test-audit.sh slow
     
  3. Find tests slower than 2 seconds:
     $ ./test-audit.sh analyze --threshold 2.0
     
  4. Watch audit log in real-time:
     $ ./test-audit.sh logs
     
  5. Run specific test with audit:
     $ ./test-audit.sh run tests/ -k "test_conversation_protocol"

AUDIT FILES:
  📊 Database:  ${AUDIT_DB}
  📋 Log:       ${AUDIT_LOG}
  📈 Report:    ${PERFORMANCE_REPORT}

EOF
}

case "${1:-help}" in
    run)
        shift
        print_header "🚀 Running Tests with Performance Audit"
        echo "📝 Audit log: ${AUDIT_LOG}"
        echo "💾 Database:  ${AUDIT_DB}"
        echo ""
        
        # Run pytest with audit plugin
        python3 -m pytest "$@" --tb=short || true
        
        echo ""
        print_header "📊 Test Performance Summary"
        python3 "$SCRIPT_DIR/test-performance-auditor.py" analyze || true
        ;;
    
    report)
        print_header "📈 Generating Performance Report"
        python3 "$SCRIPT_DIR/test-performance-auditor.py" report
        print_success "Report generated: ${PERFORMANCE_REPORT}"
        ;;
    
    analyze)
        shift
        print_header "🔍 Analyzing Test Performance"
        python3 "$SCRIPT_DIR/test-performance-auditor.py" analyze "$@"
        ;;
    
    slow)
        print_header "🐢 Top 20 Slowest Tests"
        if [ ! -f "$AUDIT_LOG" ]; then
            print_error "No audit log found. Run tests first: ./test-audit.sh run"
            exit 1
        fi
        
        echo ""
        grep "SLOW TEST\|VERY SLOW" "$AUDIT_LOG" | tail -20
        echo ""
        print_warning "Tip: Use './test-audit.sh run [test_pattern]' to run specific tests"
        ;;
    
    hanging)
        print_header "🚨 Hanging/Errored Tests"
        if [ ! -f "$AUDIT_LOG" ]; then
            print_error "No audit log found. Run tests first: ./test-audit.sh run"
            exit 1
        fi
        
        echo ""
        grep "ERROR\|TIMEOUT" "$AUDIT_LOG" | tail -20
        echo ""
        ;;
    
    logs)
        print_header "📋 Real-Time Audit Log"
        if [ ! -f "$AUDIT_LOG" ]; then
            print_warning "Audit log not yet created. Run tests first."
            exit 1
        fi
        tail -f "$AUDIT_LOG"
        ;;
    
    clear)
        print_header "🗑️  Clearing Audit Data"
        rm -f "$AUDIT_DB" "$AUDIT_LOG" "$PERFORMANCE_REPORT"
        print_success "Audit data cleared"
        ;;
    
    help|-h|--help)
        show_help
        ;;
    
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
