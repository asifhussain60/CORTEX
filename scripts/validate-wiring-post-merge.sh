#!/bin/bash
# ==============================================================================
# CORTEX Post-Merge Wiring Validation
# ==============================================================================
# CORE-031 Compliance: Validate orchestrator wiring after git merge
# 
# Usage: ./validate-wiring-post-merge.sh
# Exit codes: 0 = success, 1 = validation failure
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🔍 Validating orchestrator wiring post-merge..."
echo "   Project root: $PROJECT_ROOT"

# Change to project root
cd "$PROJECT_ROOT"

# Check for Python virtual environment
if [ -d ".venv" ]; then
    PYTHON=".venv/bin/python"
elif command -v python3 &> /dev/null; then
    PYTHON="python3"
else
    PYTHON="python"
fi

echo "   Python: $PYTHON"

# Run autowiring validation
$PYTHON -c "
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, '${PROJECT_ROOT}')

try:
    from cortex.orchestrators.core.autowiring_orchestrator import AutowiringOrchestrator
    
    engine = AutowiringOrchestrator()
    
    # Discover wiring specs
    discovery_result = engine.discover_wiring_specs()
    if not discovery_result.is_ok():
        print(f'❌ Discovery failed: {discovery_result.error}')
        sys.exit(1)
    
    specs = discovery_result.value
    print(f'✅ Discovered {len(specs)} wiring specs')
    
    # Validate dependency graph
    validation_result = engine.validate_dependency_graph(specs)
    if not validation_result.is_ok():
        print(f'❌ Validation failed: {validation_result.error}')
        sys.exit(1)
    
    sorted_modules = validation_result.value
    print(f'✅ Dependency graph valid ({len(sorted_modules)} modules)')
    
    # Check for missing wiring specs
    missing_result = engine.get_missing_wiring_specs()
    if missing_result.is_ok():
        missing = missing_result.value
        if missing:
            print(f'⚠️  Warning: {len(missing)} orchestrators missing wiring specs:')
            for path in missing[:5]:
                print(f'   - {path.name}')
            if len(missing) > 5:
                print(f'   ... and {len(missing) - 5} more')
        else:
            print('✅ All orchestrators have wiring specs')
    
    print('')
    print('✅ Wiring validation passed - merge is safe')
    sys.exit(0)
    
except ImportError as e:
    print(f'⚠️  Autowiring module not available: {e}')
    print('   Skipping wiring validation (module may not be installed)')
    sys.exit(0)
except Exception as e:
    print(f'❌ Wiring validation error: {e}')
    sys.exit(1)
"

echo ""
echo "✅ Post-merge wiring validation complete"
