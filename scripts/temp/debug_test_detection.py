"""Debug test coverage detection."""
import sys
from pathlib import Path

# Add src to path
cortex_root = Path(__file__).parent
sys.path.insert(0, str(cortex_root / "src"))

from validation.test_coverage_validator import TestCoverageValidator
from discovery.orchestrator_scanner import OrchestratorScanner

# Initialize
project_root = cortex_root
validator = TestCoverageValidator(project_root)
scanner = OrchestratorScanner(project_root)

# Discover orchestrators
orchestrators_dict = scanner.discover()
orchestrators = [
    {
        'name': name,
        'file_path': info['path'],
        'module_path': info['module_path']
    }
    for name, info in orchestrators_dict.items()
]
print(f"Found {len(orchestrators)} orchestrators\n")

# Test critical orchestrators
critical = [
    "HolisticCleanupOrchestrator",
    "SetupEPMOrchestrator",
    "ADOWorkItemOrchestrator",
    "DemoOrchestrator",
    "UnifiedEntryPointOrchestrator"
]

for name in critical:
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print('='*60)
    
    # Find orchestrator info
    orch_info = orchestrators_dict.get(name)
    if not orch_info:
        print(f"❌ Not found in discovered orchestrators")
        continue
    
    print(f"✓ Module: {orch_info['module_path']}")
    print(f"✓ File: {orch_info['path']}")
    
    # Check test coverage using actual method
    result = validator.get_test_coverage(name, "orchestrator")
    print(f"\n📊 Test Coverage Result:")
    print(f"  Has Tests: {result.get('has_tests', False)}")
    print(f"  Coverage: {result.get('coverage_pct', 0)}%")
    print(f"  Test File: {result.get('test_file', 'Not found')}")
    print(f"  Test Count: {result.get('test_count', 0)}")
    print(f"  Status: {result.get('status', 'unknown')}")
    
    # Check benchmark file exists
    snake_name = validator._snake_case(name)
    benchmark_file = project_root / "tests" / "performance" / f"test_{snake_name}_benchmarks.py"
    print(f"\n🚀 Performance Benchmarks:")
    print(f"  Benchmark File: {benchmark_file.relative_to(project_root) if benchmark_file.exists() else 'Not found'}")
    print(f"  Exists: {benchmark_file.exists()}")
