#!/bin/bash
# CORTEX Phase E Progress Dashboard
# Real-time tracking of TDD implementation progress

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

# Configuration
PHASE_E_MODULES=125
PHASE_START_DATE="2026-01-24"  # Will be set when Phase E starts
TARGET_DAYS=20
TARGET_DAILY_RATE=6.25  # 125 modules / 20 days

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║         CORTEX Phase E Progress Dashboard            ║"
echo "╠════════════════════════════════════════════════════════╣"

# Test metrics
echo "║ 📊 Collecting test metrics...                         ║"

TESTS_COLLECTED=$(cd "$PROJECT_ROOT" && python3 -m pytest --collect-only -q 2>&1 | grep -oP '\d+(?= tests? collected)' | head -1 || echo "0")
COLLECTION_ERRORS=$(cd "$PROJECT_ROOT" && python3 -m pytest --collect-only -q 2>&1 | grep -c "ERROR" || echo "0")

# Run quick test to get passing count (with timeout)
TESTS_PASSING=0
if [ -f "tests/unit/" ]; then
    TESTS_PASSING=$(cd "$PROJECT_ROOT" && timeout 30 python3 -m pytest tests/unit/ -q --tb=no -x 2>&1 | grep -oP '\d+(?= passed)' | head -1 || echo "0")
fi

# Implementation metrics
MODULES_IMPLEMENTED=0
if git log --since="$PHASE_START_DATE" --oneline 2>/dev/null | grep -q "module:"; then
    MODULES_IMPLEMENTED=$(git log --since="$PHASE_START_DATE" --oneline | grep -c "✅ module:" || echo "0")
fi

# Calculate days elapsed
CURRENT_DATE=$(date +%s)
START_DATE_SECONDS=$(date -jf "%Y-%m-%d" "$PHASE_START_DATE" +%s 2>/dev/null || date +%s)
DAYS_ELAPSED=$(( (CURRENT_DATE - START_DATE_SECONDS) / 86400 ))

# Prevent division by zero
if [ $DAYS_ELAPSED -lt 1 ]; then
    DAYS_ELAPSED=1
fi

# Calculate progress
PROGRESS_PCT=$(( MODULES_IMPLEMENTED * 100 / PHASE_E_MODULES ))
DAILY_RATE=$(awk "BEGIN {printf \"%.2f\", $MODULES_IMPLEMENTED / $DAYS_ELAPSED}")
DAYS_REMAINING=$(awk "BEGIN {if ($DAILY_RATE > 0) printf \"%.1f\", ($PHASE_E_MODULES - $MODULES_IMPLEMENTED) / $DAILY_RATE; else print \"N/A\"}")

# Calculate test pass rate
if [ $TESTS_COLLECTED -gt 0 ]; then
    PASS_RATE=$(awk "BEGIN {printf \"%.1f\", $TESTS_PASSING * 100 / $TESTS_COLLECTED}")
else
    PASS_RATE="0.0"
fi

echo "╠════════════════════════════════════════════════════════╣"
echo "║                  IMPLEMENTATION STATUS                 ║"
echo "╠════════════════════════════════════════════════════════╣"

# Format output with proper spacing
printf "║ Modules Implemented: %3d / %3d (%3d%%)                  ║\n" $MODULES_IMPLEMENTED $PHASE_E_MODULES $PROGRESS_PCT
printf "║ Days Elapsed:        %3d / %3d                          ║\n" $DAYS_ELAPSED $TARGET_DAYS
printf "║ Daily Rate:          %.2f modules/day (target: %.2f)    ║\n" $DAILY_RATE $TARGET_DAILY_RATE
printf "║ Est. Days Remaining: %-8s                           ║\n" "$DAYS_REMAINING"

echo "╠════════════════════════════════════════════════════════╣"
echo "║                    TEST METRICS                        ║"
echo "╠════════════════════════════════════════════════════════╣"

printf "║ Tests Collected:     %4d                              ║\n" $TESTS_COLLECTED
printf "║ Collection Errors:   %4d                              ║\n" $COLLECTION_ERRORS
printf "║ Tests Passing:       %4d                              ║\n" $TESTS_PASSING
printf "║ Pass Rate:           %5.1f%%                           ║\n" $PASS_RATE

echo "╠════════════════════════════════════════════════════════╣"
echo "║                   STATUS INDICATORS                    ║"
echo "╠════════════════════════════════════════════════════════╣"

# Status checks
if [ $COLLECTION_ERRORS -eq 0 ]; then
    echo "║ ✅ Collection: Healthy                                 ║"
else
    echo "║ ⚠️  Collection: $COLLECTION_ERRORS errors (needs attention)         ║"
fi

# Check pass rate
PASS_RATE_INT=$(echo "$PASS_RATE" | cut -d. -f1)
if [ $PASS_RATE_INT -ge 98 ]; then
    echo "║ ✅ Pass Rate: Excellent (≥98%)                         ║"
elif [ $PASS_RATE_INT -ge 90 ]; then
    echo "║ ⚠️  Pass Rate: Good but below target                   ║"
else
    echo "║ 🚨 Pass Rate: Needs attention (<90%)                   ║"
fi

# Check daily velocity
DAILY_RATE_INT=$(echo "$DAILY_RATE" | cut -d. -f1)
if [ $DAYS_ELAPSED -gt 3 ] && [ $DAILY_RATE_INT -lt 5 ]; then
    echo "║ 🚨 ALERT: Daily rate below target (target: 6-8/day)   ║"
elif [ $DAILY_RATE_INT -ge 6 ]; then
    echo "║ ✅ Velocity: On track or ahead                         ║"
else
    echo "║ ⚠️  Velocity: Slightly behind target                   ║"
fi

# Check projected completion
if [ "$DAYS_REMAINING" != "N/A" ]; then
    DAYS_REMAINING_INT=$(echo "$DAYS_REMAINING" | cut -d. -f1)
    TOTAL_PROJECTED=$(( DAYS_ELAPSED + DAYS_REMAINING_INT ))
    
    if [ $TOTAL_PROJECTED -gt 25 ]; then
        echo "║ 🚨 WARNING: Projected completion exceeds 20-day target ║"
    elif [ $TOTAL_PROJECTED -le 20 ]; then
        echo "║ ✅ Timeline: On track for 20-day completion            ║"
    else
        echo "║ ⚠️  Timeline: Slightly behind (projected: ${TOTAL_PROJECTED}d)       ║"
    fi
fi

echo "╠════════════════════════════════════════════════════════╣"
echo "║                   PHASE E SUB-PHASES                   ║"
echo "╠════════════════════════════════════════════════════════╣"

# Estimate sub-phase status based on module count
if [ $MODULES_IMPLEMENTED -eq 0 ]; then
    echo "║ Current: E1 - Setup & Analysis                        ║"
elif [ $MODULES_IMPLEMENTED -le 5 ]; then
    echo "║ Current: E2 - P0 Critical (5 modules)                 ║"
    printf "║          Progress: %d/5 complete                        ║\n" $MODULES_IMPLEMENTED
elif [ $MODULES_IMPLEMENTED -le 20 ]; then
    echo "║ Current: E3 - P1 High Priority (15 modules)           ║"
    printf "║          Progress: %d/15 complete                       ║\n" $(( MODULES_IMPLEMENTED - 5 ))
elif [ $MODULES_IMPLEMENTED -le 55 ]; then
    echo "║ Current: E4 - P2 Medium Priority (35 modules)         ║"
    printf "║          Progress: %d/35 complete                       ║\n" $(( MODULES_IMPLEMENTED - 20 ))
elif [ $MODULES_IMPLEMENTED -le 125 ]; then
    echo "║ Current: E5 - P3 Lower Priority (70 modules)          ║"
    printf "║          Progress: %d/70 complete                       ║\n" $(( MODULES_IMPLEMENTED - 55 ))
else
    echo "║ Current: E6 - Final Validation                        ║"
fi

echo "╚════════════════════════════════════════════════════════╝"

# Summary recommendations
echo ""
if [ $COLLECTION_ERRORS -gt 0 ]; then
    echo -e "${YELLOW}📌 RECOMMENDATION: Fix $COLLECTION_ERRORS collection errors first${NC}"
fi

if [ $DAYS_ELAPSED -gt 3 ] && [ $DAILY_RATE_INT -lt 5 ]; then
    echo -e "${YELLOW}📌 RECOMMENDATION: Increase daily velocity to meet timeline${NC}"
fi

if [ $PASS_RATE_INT -lt 90 ]; then
    echo -e "${YELLOW}📌 RECOMMENDATION: Focus on fixing failing tests${NC}"
fi

# Export metrics for CI/CD
if [ "$1" == "--export" ]; then
    cat > /tmp/phase_e_metrics.json << EOF
{
  "modules_implemented": $MODULES_IMPLEMENTED,
  "modules_total": $PHASE_E_MODULES,
  "progress_pct": $PROGRESS_PCT,
  "days_elapsed": $DAYS_ELAPSED,
  "daily_rate": $DAILY_RATE,
  "tests_collected": $TESTS_COLLECTED,
  "collection_errors": $COLLECTION_ERRORS,
  "tests_passing": $TESTS_PASSING,
  "pass_rate": $PASS_RATE
}
EOF
    echo ""
    echo "📊 Metrics exported to: /tmp/phase_e_metrics.json"
fi

echo ""
