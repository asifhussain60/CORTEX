#!/bin/bash
# CORTEX Test Performance Auditing - Quick Reference
# ====================================================
#
# This is a quick reference for test auditing commands.
# Full documentation: docs/TEST-PERFORMANCE-AUDITING.md

cat << 'EOF'

╔════════════════════════════════════════════════════════════════════════════╗
║        CORTEX Test Performance Auditing - Quick Reference (v1.0)          ║
╚════════════════════════════════════════════════════════════════════════════╝

🎯 PROBLEM SOLVED:
   ✓ Tests no longer hang indefinitely
   ✓ Automatic detection of slow/hanging tests
   ✓ Real-time performance visibility
   ✓ Enterprise audit trail for all executions

═══════════════════════════════════════════════════════════════════════════════

📊 QUICK COMMANDS:

1. RUN TESTS WITH AUDIT:
   $ ./scripts/test-audit.sh run tests/unit/core/
   
2. SHOW SLOWEST TESTS:
   $ ./scripts/test-audit.sh slow
   
3. SHOW HANGING TESTS:
   $ ./scripts/test-audit.sh hanging
   
4. ANALYZE WITH THRESHOLD:
   $ ./scripts/test-audit.sh analyze --threshold 2.0
   
5. GENERATE REPORT:
   $ ./scripts/test-audit.sh report
   
6. WATCH LOGS LIVE:
   $ ./scripts/test-audit.sh logs

═══════════════════════════════════════════════════════════════════════════════

📁 KEY FILES:

Audit Log:      test_audit_trail.log
Database:       cortex_brain/state/test_audit.db
Report:         test_performance_report.json
Docs:           docs/TEST-PERFORMANCE-AUDITING.md

═══════════════════════════════════════════════════════════════════════════════

⏱️  THRESHOLDS:

Slow Test:      >1.0 second    (yellow warning)
Very Slow:      >5.0 seconds   (red alert - investigate)
Timeout:        30.0 seconds   (default, configurable)

═══════════════════════════════════════════════════════════════════════════════

🔧 INTEGRATION:

Pytest automatically loads audit plugin via tests/conftest.py
No additional configuration needed - just run tests!

═══════════════════════════════════════════════════════════════════════════════

💡 EXAMPLES:

# Find tests slower than 2 seconds
./scripts/test-audit.sh run tests/ && ./scripts/test-audit.sh analyze --threshold 2.0

# Run specific test module with audit
./scripts/test-audit.sh run tests/unit/orchestrator/ -v

# Find hanging tests from previous run
./scripts/test-audit.sh hanging

# Clear all audit data
./scripts/test-audit.sh clear

═══════════════════════════════════════════════════════════════════════════════

For full documentation, see: docs/TEST-PERFORMANCE-AUDITING.md

EOF
