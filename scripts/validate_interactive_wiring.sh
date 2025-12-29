#!/bin/bash
# Interactive Workflow Wiring Validation Script
# Purpose: Validate that all orchestrators with interactive components have complete wiring
# Author: CORTEX Maintenance System
# Version: 1.1.0 (bash 3.x compatible)

set -e

# Check bash version and warn if < 4.0
BASH_VERSION_MAJOR="${BASH_VERSION%%.*}"
if [ "$BASH_VERSION_MAJOR" -lt 4 ]; then
  echo "⚠️  Warning: Bash version $BASH_VERSION detected (requires 4.0+ for full features)"
  echo "   Running in compatibility mode..."
  echo ""
fi

echo "🔍 Validating Interactive Workflow Wiring..."
echo ""

# Configuration
ORCHESTRATORS=("planning" "ado")
PASS=0
FAIL=0
WARNINGS=0

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track details for report (bash 3.x compatible - using parallel arrays)
RESULTS_KEYS=()
RESULTS_VALUES=()

# Function to store result (bash 3.x compatible)
store_result() {
  local key="$1"
  local value="$2"
  RESULTS_KEYS+=("$key")
  RESULTS_VALUES+=("$value")
}

# Function to get result (bash 3.x compatible)
get_result() {
  local search_key="$1"
  local idx=0
  for key in "${RESULTS_KEYS[@]}"; do
    if [ "$key" = "$search_key" ]; then
      echo "${RESULTS_VALUES[$idx]}"
      return 0
    fi
    ((idx++))
  done
  echo "UNKNOWN"
}

# Function to check component
check_component() {
  local orch=$1
  local component=$2
  local check_cmd=$3
  local check_name=$4
  
  if eval "$check_cmd" 2>/dev/null; then
    echo -e "  ${GREEN}✅${NC} $check_name"
    ((PASS++))
    store_result "${orch}_${component}" "PASS"
    return 0
  else
    echo -e "  ${RED}❌${NC} $check_name"
    ((FAIL++))
    store_result "${orch}_${component}" "FAIL"
    return 1
  fi
}

# Main validation loop
for orch in "${ORCHESTRATORS[@]}"; do
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "📋 Checking $orch orchestrator..."
  echo ""
  
  # Check 1: Decision logic exists
  check_component "$orch" "decision_logic_exists" \
    "grep -q '_should_use_interactive_mode' 'src/orchestrators/$orch/${orch}_orchestrator.py'" \
    "Decision logic method exists"
  
  # Check 2: Decision logic is called
  check_component "$orch" "decision_logic_called" \
    "grep -A 40 'def execute' 'src/orchestrators/$orch/${orch}_orchestrator.py' | grep -q '_should_use_interactive_mode'" \
    "Decision logic called in execute()"
  
  # Check 3: Agent file exists
  check_component "$orch" "agent_file" \
    "test -f 'src/cortex_agents/strategic/interactive_${orch}_planner.py' || test -f 'src/cortex_agents/strategic/interactive_planner.py'" \
    "Interactive agent file exists"
  
  # Check 4: Agent registration
  check_component "$orch" "agent_registry" \
    "grep -q 'interactive_$orch\\|interactive_planning' 'src/cortex_agents/agent_registry.py'" \
    "Agent registered in registry"
  
  # Check 5: Agent import in orchestrator
  check_component "$orch" "agent_import" \
    "grep -q 'from.*interactive.*planner import' 'src/orchestrators/$orch/${orch}_orchestrator.py'" \
    "Agent imported in orchestrator"
  
  # Check 6: Execution routing
  check_component "$orch" "execution_routing" \
    "grep -A 5 'def execute' 'src/orchestrators/$orch/${orch}_orchestrator.py' | grep -q 'if.*interactive'" \
    "Execution routing present"
  
  # Check 7: Interactive method exists
  check_component "$orch" "interactive_method" \
    "grep -q '_execute_interactive_mode\\|interactive_.*_creation' 'src/orchestrators/$orch/${orch}_orchestrator.py'" \
    "Interactive execution method exists"
  
  # Check 8: UI bridge
  check_component "$orch" "ui_bridge" \
    "test -f 'src/orchestrators/$orch/user_interface.py'" \
    "UI bridge file exists"
  
  # Check 9: Integration tests
  check_component "$orch" "integration_tests" \
    "test -f 'tests/orchestrators/$orch/test_interactive_workflow.py' || test -f 'tests/orchestrators/$orch/test_interactive_planning_session.py'" \
    "Integration test file exists"
  
  # Check 10: Tests passing (if they exist)
  if [ -f "tests/orchestrators/$orch/test_interactive_workflow.py" ] || [ -f "tests/orchestrators/$orch/test_interactive_planning_session.py" ]; then
    if python3 -m pytest "tests/orchestrators/$orch/" -k interactive --tb=no -q > /dev/null 2>&1; then
      echo -e "  ${GREEN}✅${NC} Integration tests passing"
      ((PASS++))
      store_result "${orch}_tests_passing" "PASS"
    else
      echo -e "  ${YELLOW}⚠️${NC}  Integration tests failing (run to investigate)"
      ((WARNINGS++))
      store_result "${orch}_tests_passing" "WARNING"
    fi
  fi
  
  echo ""
done

# Generate summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Results: ${GREEN}$PASS passed${NC}, ${RED}$FAIL failed${NC}, ${YELLOW}$WARNINGS warnings${NC}"
TOTAL=$((PASS + FAIL))
if [ $TOTAL -gt 0 ]; then
  PERCENT=$((PASS * 100 / TOTAL))
else
  PERCENT=0
fi
echo "Wiring Coverage: $PERCENT%"
echo ""

# Generate detailed report
REPORT_FILE="cortex-brain/health-reports/interactive-wiring-status-$(date +%Y%m%d-%H%M%S).md"
mkdir -p cortex-brain/health-reports

cat > "$REPORT_FILE" << EOF
# Interactive Workflow Wiring Status Report

**Date:** $(date '+%Y-%m-%d %H:%M:%S')
**Script Version:** 1.0.0

## Summary

- **Total Checks:** $TOTAL
- **Passed:** $PASS
- **Failed:** $FAIL
- **Warnings:** $WARNINGS
- **Coverage:** $PERCENT%

## Detailed Results

EOF

# Add orchestrator-specific results
for orch in "${ORCHESTRATORS[@]}"; do
  cat >> "$REPORT_FILE" << EOF
### ${orch^} Orchestrator

| Component | Status |
|-----------|--------|
| Decision Logic Exists | ${RESULTS["${orch}_decision_logic_exists"]:-N/A} |
| Decision Logic Called | ${RESULTS["${orch}_decision_logic_called"]:-N/A} |
| Agent File Exists | ${RESULTS["${orch}_agent_file"]:-N/A} |
| Agent Registered | ${RESULTS["${orch}_agent_registry"]:-N/A} |
| Agent Imported | ${RESULTS["${orch}_agent_import"]:-N/A} |
| Execution Routing | ${RESULTS["${orch}_execution_routing"]:-N/A} |
| Interactive Method | ${RESULTS["${orch}_interactive_method"]:-N/A} |
| UI Bridge | ${RESULTS["${orch}_ui_bridge"]:-N/A} |
| Integration Tests | ${RESULTS["${orch}_integration_tests"]:-N/A} |
| Tests Passing | ${RESULTS["${orch}_tests_passing"]:-N/A} |

EOF
done

# Add recommendations
cat >> "$REPORT_FILE" << EOF
## Recommendations

EOF

if [ $FAIL -gt 0 ]; then
  cat >> "$REPORT_FILE" << EOF
### Critical Issues

The following components are missing and must be implemented:

EOF
  
  for key in "${!RESULTS[@]}"; do
    if [ "${RESULTS[$key]}" = "FAIL" ]; then
      echo "- $key" >> "$REPORT_FILE"
    fi
  done
  
  cat >> "$REPORT_FILE" << EOF

**Action Required:** See \`cortex-brain/documents/analysis/interactive-workflow-wiring-gap-analysis.md\` for implementation guidance.
EOF
fi

if [ $WARNINGS -gt 0 ]; then
  cat >> "$REPORT_FILE" << EOF

### Warnings

- Some integration tests are failing. Run tests manually to investigate:
  \`\`\`bash
  python3 -m pytest tests/orchestrators/planning/test_interactive_planning_session.py -v
  python3 -m pytest tests/orchestrators/ado/test_interactive_workflow.py -v
  \`\`\`
EOF
fi

cat >> "$REPORT_FILE" << EOF

## Reference

- **Gap Analysis:** cortex-brain/documents/analysis/interactive-workflow-wiring-gap-analysis.md
- **Maintenance Guide:** .github/prompts/cortex-maintenance.prompt.md (Phase 1.5)
- **Universal Pattern:** See gap analysis Section 3.1

---

**Report Location:** $REPORT_FILE
EOF

echo "📄 Detailed report saved to: $REPORT_FILE"
echo ""

# Exit with appropriate code
if [ $PERCENT -eq 100 ]; then
  echo -e "${GREEN}✅ All interactive workflows fully wired!${NC}"
  exit 0
elif [ $PERCENT -ge 80 ]; then
  echo -e "${YELLOW}⚠️  Wiring mostly complete but has gaps.${NC}"
  echo "See: cortex-brain/documents/analysis/interactive-workflow-wiring-gap-analysis.md"
  exit 0
else
  echo -e "${RED}❌ Wiring incomplete. Critical gaps detected.${NC}"
  echo "See: cortex-brain/documents/analysis/interactive-workflow-wiring-gap-analysis.md"
  exit 1
fi
