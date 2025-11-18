#!/usr/bin/env python3
"""Test capability coverage validation against real CORTEX capabilities.yaml"""

from pathlib import Path
from src.epm.modules.validation_engine import ValidationEngine

def main():
    # Create validator for current workspace
    workspace_root = Path('.')
    validator = ValidationEngine(workspace_root)
    
    # Run validation
    print("Running capability coverage validation...")
    is_valid, report = validator.validate_documentation_coverage(coverage_threshold=0.80)
    
    # Display results
    print("\n" + "="*70)
    print("CAPABILITY COVERAGE VALIDATION REPORT")
    print("="*70)
    print(f"\nValidation Status: {'✓ PASS' if is_valid else '❌ FAIL'}")
    print(f"Coverage Rate: {report['coverage_rate']*100:.1f}%")
    print(f"Documented Capabilities: {report['documented_capabilities']}/{report['total_capabilities']}")
    print(f"Threshold: {report['threshold']*100:.0f}%")
    
    if report['documented_list']:
        print(f"\n✓ Documented Capabilities ({len(report['documented_list'])}):")
        for cap in report['documented_list']:
            print(f"  - {cap['name']} ({cap['id']}) [{cap['status']}]")
    
    if report['undocumented_list']:
        print(f"\n❌ Missing Documentation ({len(report['undocumented_list'])}):")
        for cap in report['undocumented_list']:
            print(f"  - {cap['name']} ({cap['id']}) [{cap['status']}]")
            if cap['expected_docs']:
                for doc in cap['expected_docs']:
                    print(f"    Expected: docs/{doc}")
    
    print(f"\nTotal documents found: {report['total_docs_found']}")
    print(f"Expected document patterns: {report['expected_doc_patterns']}")
    print("="*70)
    
    return 0 if is_valid else 1

if __name__ == '__main__':
    exit(main())
