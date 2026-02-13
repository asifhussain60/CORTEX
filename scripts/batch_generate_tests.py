"""Batch test generation for 60 orchestrators using ScaffolderIntelligenceAdapter.

AC_START: AC-WAVE2-S2-002
Description: Generate 600 tests (10 per orchestrator) using Test Intelligence
Authority: WAVE-2 Stage 2
"""

import json
from pathlib import Path
from typing import List, Dict, Any

from cortex.testing.scaffolder_intelligence_adapter import (
    ScaffolderIntelligenceAdapter,
    OrchestratorSpec,
)


def load_orchestrator_specs() -> List[Dict[str, Any]]:
    """Load pre-extracted orchestrator specs from JSON."""
    specs_file = Path("cortex-registry/_cortex-master/orchestrator_specs.json")
    
    if not specs_file.exists():
        raise FileNotFoundError(
            f"Orchestrator specs not found: {specs_file}\n"
            "Run: python scripts/generate_batch_specs.py"
        )
    
    with open(specs_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def convert_to_orchestrator_specs(specs_dicts: List[Dict[str, Any]]) -> List[OrchestratorSpec]:
    """Convert JSON dicts to OrchestratorSpec objects."""
    specs = []
    
    for spec_dict in specs_dicts:
        spec = OrchestratorSpec(
            name=spec_dict['name'],
            domain=spec_dict.get('category', 'unknown'),
            tier=spec_dict.get('tier', 1),
            capabilities=spec_dict.get('capabilities', []),
            stages=spec_dict.get('stages', []),
            hooks=list(spec_dict.get('hooks', {}).keys()),
            integrations=list(spec_dict.get('integration_points', {}).keys()),
            mcp_tools=[],
        )
        specs.append(spec)
    
    return specs


def generate_batch_tests(specs: List[OrchestratorSpec], target_count: int = 10):
    """Generate tests for all orchestrators in batch.
    
    Args:
        specs: List of OrchestratorSpec objects
        target_count: Tests per orchestrator (default: 10)
    """
    print(f"🚀 WAVE-2 Stage 2: Batch Test Generation")
    print(f"   Orchestrators: {len(specs)}")
    print(f"   Target: {len(specs) * target_count} tests ({target_count} per orchestrator)")
    print()
    
    # Initialize adapter
    adapter = ScaffolderIntelligenceAdapter()
    
    # Generate batch
    print("📋 Generating test suites...")
    results = adapter.generate_batch(specs, target_count_per_orchestrator=target_count)
    
    # Statistics
    total_tests = 0
    total_lines = 0
    failed = []
    
    for name, suite in results.items():
        if suite.test_count > 0:
            total_tests += suite.test_count
            total_lines += suite.total_lines
            print(f"   ✅ {name}: {suite.test_count} tests, {suite.total_lines} lines")
        else:
            failed.append(name)
            print(f"   ❌ {name}: Failed to generate tests")
    
    print()
    print(f"📊 Generation Summary:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Total Lines: {total_lines:,}")
    print(f"   Success: {len(specs) - len(failed)}/{len(specs)} orchestrators")
    print(f"   Failed: {len(failed)}")
    
    if failed:
        print()
        print("❌ Failed orchestrators:")
        for name in failed:
            print(f"   - {name}")
    
    return results


def write_test_files(results: Dict[str, Any]):
    """Write generated test suites to files.
    
    Args:
        results: Dict of orchestrator_name -> TestSuite
    """
    print()
    print("📝 Writing test files...")
    
    test_dir = Path("tests/unit/orchestrators/generated")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    written = 0
    for name, suite in results.items():
        if suite.test_count == 0:
            continue
        
        # Convert CamelCase to snake_case for filename
        filename = ''.join(['_' + c.lower() if c.isupper() else c for c in name]).lstrip('_')
        test_file = test_dir / f"test_{filename}.py"
        
        # Combine all test code from ComposedTest objects
        all_test_code = []
        all_test_code.append('"""Auto-generated tests for {}."""\n'.format(name))
        all_test_code.append('import pytest\n\n')
        
        for test in suite.tests:
            all_test_code.append(test.test_code)
            all_test_code.append('\n\n')
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(''.join(all_test_code))
        
        written += 1
        print(f"   ✅ {test_file}")
    
    print()
    print(f"✅ Wrote {written} test files to {test_dir}")


def main():
    """Main execution."""
    # Load specs
    print("📖 Loading orchestrator specifications...")
    specs_dicts = load_orchestrator_specs()
    specs = convert_to_orchestrator_specs(specs_dicts)
    print(f"   Loaded {len(specs)} specs")
    print()
    
    # Generate tests
    results = generate_batch_tests(specs, target_count=10)
    
    # Write to files
    write_test_files(results)
    
    print()
    print("🎉 WAVE-2 Stage 2: Batch generation complete!")
    return results


if __name__ == "__main__":
    results = main()

# AC_COMPLETE: AC-WAVE2-S2-002 ✅
