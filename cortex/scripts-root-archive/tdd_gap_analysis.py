"""
TDD Gap Analysis for CORTEX
Identifies tests that import non-existent 'src.' modules
"""
import os
import re
from pathlib import Path
from collections import defaultdict

def analyze_test_imports():
    """Scan all test files for src.* imports and verify existence"""
    
    test_dir = Path("tests")
    cortex_dir = Path("cortex")
    src_imports = defaultdict(list)
    
    # Pattern to match src.* imports
    import_pattern = re.compile(r'from\s+src\.([a-zA-Z0-9_.]+)\s+import|import\s+src\.([a-zA-Z0-9_.]+)')
    
    # Scan all test files
    for test_file in test_dir.rglob("*.py"):
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for match in import_pattern.finditer(content):
                module_path = match.group(1) or match.group(2)
                src_imports[module_path].append(str(test_file.relative_to(Path.cwd())))
        except Exception as e:
            print(f"Error reading {test_file}: {e}")
    
    # Check which modules exist in cortex/
    missing_modules = {}
    existing_modules = {}
    
    for module_path, test_files in src_imports.items():
        # Convert src.X.Y.Z to cortex/X/Y/Z.py
        cortex_path = cortex_dir / module_path.replace('.', '/')
        py_file = cortex_path.with_suffix('.py')
        init_file = cortex_path / '__init__.py'
        
        if py_file.exists() or init_file.exists():
            existing_modules[module_path] = test_files
        else:
            missing_modules[module_path] = test_files
    
    return missing_modules, existing_modules, len(src_imports)

def main():
    print("=" * 80)
    print("CORTEX TDD Gap Analysis")
    print("=" * 80)
    print()
    
    missing, existing, total = analyze_test_imports()
    
    print(f"Total unique src.* imports: {total}")
    print(f"Existing implementations: {len(existing)}")
    print(f"Missing implementations: {len(missing)}")
    print()
    
    if missing:
        print("=" * 80)
        print("MISSING IMPLEMENTATIONS (TDD Gaps)")
        print("=" * 80)
        print()
        
        # Group by top-level module
        by_category = defaultdict(list)
        for module_path, test_files in sorted(missing.items()):
            category = module_path.split('.')[0]
            by_category[category].append((module_path, test_files))
        
        for category in sorted(by_category.keys()):
            print(f"\n{category.upper()}/")
            print("-" * 80)
            for module_path, test_files in sorted(by_category[category]):
                print(f"\n  Module: src.{module_path}")
                expected_path = f"cortex/{module_path.replace('.', '/')}.py"
                print(f"  Expected: {expected_path}")
                print(f"  Tests ({len(test_files)}):")
                for test_file in sorted(set(test_files))[:5]:  # Show max 5
                    print(f"    - {test_file}")
                if len(test_files) > 5:
                    print(f"    ... and {len(test_files) - 5} more")
        
        print()
        print("=" * 80)
        print(f"SUMMARY: {len(missing)} missing implementations")
        print("=" * 80)
    
    # Generate YAML report
    yaml_report = generate_yaml_report(missing, existing)
    with open('reports/analysis/tdd-gap-analysis.yaml', 'w') as f:
        f.write(yaml_report)
    print("\nReport saved to: reports/analysis/tdd-gap-analysis.yaml")

def generate_yaml_report(missing, existing):
    """Generate YAML report of findings"""
    from datetime import datetime
    
    yaml = f"""# TDD Gap Analysis Report
# Generated: {datetime.now().isoformat()}

metadata:
  title: "CORTEX TDD Implementation Gap Analysis"
  date: "{datetime.now().strftime('%Y-%m-%d')}"
  total_src_imports: {len(missing) + len(existing)}
  implemented: {len(existing)}
  missing: {len(missing)}
  status: "TDD_GAPS_IDENTIFIED"

summary:
  description: |
    Analysis of test files importing 'src.*' modules that don't exist
    in the consolidated 'cortex/' package structure.
    
  findings:
    - Tests written following TDD principles
    - Implementations missing after consolidation
    - All modules need migration from conceptual 'src/' to actual 'cortex/'

missing_implementations:
"""
    
    by_category = defaultdict(list)
    for module_path in sorted(missing.keys()):
        category = module_path.split('.')[0]
        by_category[category].append(module_path)
    
    for category in sorted(by_category.keys()):
        yaml += f"\n  {category}:\n"
        for module_path in sorted(by_category[category]):
            test_count = len(missing[module_path])
            expected = f"cortex/{module_path.replace('.', '/')}.py"
            yaml += f"    - module: \"{module_path}\"\n"
            yaml += f"      expected_path: \"{expected}\"\n"
            yaml += f"      test_count: {test_count}\n"
            yaml += f"      status: \"NOT_IMPLEMENTED\"\n"
    
    yaml += f"""
production_readiness:
  priority: "P0-CRITICAL"
  impact: "Blocks production deployment"
  recommendation: |
    1. Create implementation phase: impl-tdd-gaps-remediation.yaml
    2. Implement missing modules in cortex/ package
    3. Update all test imports from 'src.*' to 'cortex.*'
    4. Verify test pass rate >=98%
    
  estimated_effort:
    modules: {len(missing)}
    tests_affected: {sum(len(files) for files in missing.values())}
    implementation: "5-10 days"
    testing: "2-3 days"
"""
    
    return yaml

if __name__ == "__main__":
    main()
