#!/usr/bin/env python3
"""Test all CORTEX 2.0 operations comprehensively."""

from src.operations import execute_operation, list_operations
from pathlib import Path

print("=" * 70)
print("CORTEX 2.0 - Comprehensive Operations Test")
print("=" * 70)

# Test each operation
tests = [
    {
        'name': 'Environment Setup',
        'command': 'setup environment',
        'profile': 'minimal',
        'expected_modules': 6
    },
    {
        'name': 'Story Refresh',
        'command': 'refresh story',
        'profile': 'quick',
        'expected_modules': 3
    },
    {
        'name': 'Workspace Cleanup (Safe)',
        'command': 'cleanup workspace',
        'profile': 'safe',
        'expected_modules': 3
    },
    {
        'name': 'Workspace Cleanup (Standard)',
        'command': 'cleanup',
        'profile': 'standard',
        'expected_modules': 5
    },
]

results = []

for test in tests:
    print(f"\n{'='*70}")
    print(f"Testing: {test['name']}")
    print(f"Command: {test['command']} (profile: {test['profile']})")
    print('-' * 70)
    
    try:
        report = execute_operation(test['command'], profile=test['profile'])
        
        success = '✅' if report.success else '❌'
        modules_ok = '✅' if len(report.modules_executed) == test['expected_modules'] else f"⚠️  (expected {test['expected_modules']})"
        
        print(f"Status: {success}")
        print(f"Modules Executed: {len(report.modules_executed)} {modules_ok}")
        print(f"  → {', '.join(report.modules_executed)}")
        print(f"Duration: {report.total_duration_seconds:.2f}s")
        
        if report.errors:
            print(f"Errors: {len(report.errors)}")
            for error in report.errors[:3]:
                print(f"  ❌ {error}")
        
        results.append({
            'test': test['name'],
            'success': report.success,
            'modules': len(report.modules_executed),
            'duration': report.total_duration_seconds
        })
    
    except Exception as e:
        print(f"❌ Exception: {e}")
        results.append({
            'test': test['name'],
            'success': False,
            'modules': 0,
            'duration': 0
        })

# Summary
print(f"\n{'='*70}")
print("Test Summary")
print('=' * 70)

total_tests = len(results)
passed_tests = sum(1 for r in results if r['success'])
total_modules = sum(r['modules'] for r in results)
total_duration = sum(r['duration'] for r in results)

print(f"\n✅ Tests Passed: {passed_tests}/{total_tests}")
print(f"📦 Total Modules Executed: {total_modules}")
print(f"⏱️  Total Duration: {total_duration:.2f}s")

print(f"\n{'Operation':<35} {'Status':<10} {'Modules':<10} {'Time'}")
print('-' * 70)
for r in results:
    status = '✅ PASS' if r['success'] else '❌ FAIL'
    print(f"{r['test']:<35} {status:<10} {r['modules']:<10} {r['duration']:.2f}s")

print('\n' + '=' * 70)
if passed_tests == total_tests:
    print("🎉 ALL TESTS PASSED - CORTEX 2.0 Operations Validated!")
else:
    print(f"⚠️  {total_tests - passed_tests} test(s) failed")
print('=' * 70)
