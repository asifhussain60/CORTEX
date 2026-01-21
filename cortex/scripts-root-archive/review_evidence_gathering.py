#!/usr/bin/env python3
"""
CORTEX System Review: Comprehensive Gap Analysis
Gathers evidence by analyzing:
1. Test file structure and coverage
2. Code implementation status
3. Roadmap claims vs actual code
4. Completion verification
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict
import subprocess

CORTEX_ROOT = Path(r'd:\PROJECTS\CORTEX')
ROADMAP_FILE = CORTEX_ROOT / '_workspaces' / 'roadmap' / 'cortex-impl-map.yaml'

print("\n" + "=" * 90)
print("CORTEX COMPREHENSIVE SYSTEM REVIEW")
print("Evidence Gathering Phase")
print("=" * 90)

# ============================================================================
# SECTION 1: TEST INVENTORY & COLLECTION STATUS
# ============================================================================
print("\n" + "=" * 90)
print("SECTION 1: TEST INVENTORY & COLLECTION")
print("=" * 90)

test_count = 0
test_files = 0
test_dirs = defaultdict(int)

for root, dirs, files in os.walk(CORTEX_ROOT / 'tests'):
    for file in files:
        if file.startswith('test_') and file.endswith('.py'):
            test_files += 1
            rel_path = Path(root).relative_to(CORTEX_ROOT / 'tests')
            test_dir = str(rel_path).split(os.sep)[0] if str(rel_path) != '.' else 'root'
            test_dirs[test_dir] += 1

print(f"Total test files: {test_files}")
print(f"Test directory breakdown:")
for dir_name in sorted(test_dirs.keys()):
    print(f"  - {dir_name:20} : {test_dirs[dir_name]:4} files")

# ============================================================================
# SECTION 2: CODE IMPLEMENTATION ANALYSIS
# ============================================================================
print("\n" + "=" * 90)
print("SECTION 2: CODE IMPLEMENTATION STATUS")
print("=" * 90)

def analyze_python_file(filepath):
    """Analyze a Python file for implementation status"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Count lines
        lines = content.split('\n')
        total_lines = len(lines)
        code_lines = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
        
        # Check for implementation status
        has_docstring = '"""' in content or "'''" in content
        has_type_hints = '->' in content or ': ' in content
        has_pass_only = content.count('pass') > 0
        has_todo = 'TODO' in content or 'FIXME' in content or 'NotImplementedError' in content
        
        # Count functions and classes
        functions = len(re.findall(r'^\s*def\s+\w+', content, re.MULTILINE))
        classes = len(re.findall(r'^\s*class\s+\w+', content, re.MULTILINE))
        
        return {
            'total_lines': total_lines,
            'code_lines': code_lines,
            'has_docstring': has_docstring,
            'has_type_hints': has_type_hints,
            'has_pass_only': has_pass_only,
            'has_todo': has_todo,
            'functions': functions,
            'classes': classes
        }
    except Exception as e:
        return None

# Analyze cortex/ package
cortex_stats = {
    'total_files': 0,
    'total_lines': 0,
    'files_with_implementation': 0,
    'files_stub_only': 0,
    'files_with_todo': 0,
    'total_functions': 0,
    'total_classes': 0
}

for root, dirs, files in os.walk(CORTEX_ROOT / 'cortex'):
    # Skip __pycache__
    if '__pycache__' in root:
        continue
    
    for file in files:
        if file.endswith('.py') and not file.startswith('__'):
            filepath = Path(root) / file
            analysis = analyze_python_file(filepath)
            
            if analysis:
                cortex_stats['total_files'] += 1
                cortex_stats['total_lines'] += analysis['total_lines']
                cortex_stats['total_functions'] += analysis['functions']
                cortex_stats['total_classes'] += analysis['classes']
                
                if analysis['has_todo']:
                    cortex_stats['files_with_todo'] += 1
                
                if analysis['code_lines'] > 50:  # Non-trivial implementation
                    cortex_stats['files_with_implementation'] += 1
                elif analysis['has_pass_only']:
                    cortex_stats['files_stub_only'] += 1

print(f"cortex/ package analysis:")
print(f"  Total Python files:        {cortex_stats['total_files']}")
print(f"  Total lines of code:       {cortex_stats['total_lines']:,}")
print(f"  Total classes:             {cortex_stats['total_classes']}")
print(f"  Total functions/methods:   {cortex_stats['total_functions']}")
print(f"  Files with implementation: {cortex_stats['files_with_implementation']}")
print(f"  Stub files (pass only):    {cortex_stats['files_stub_only']}")
print(f"  Files with TODO/FIXME:     {cortex_stats['files_with_todo']}")

# ============================================================================
# SECTION 3: PHASE COMPLETION VERIFICATION
# ============================================================================
print("\n" + "=" * 90)
print("SECTION 3: PHASE COMPLETION CLAIMS")
print("=" * 90)

# Parse roadmap
import yaml
try:
    with open(ROADMAP_FILE, 'r') as f:
        roadmap = yaml.safe_load(f)
    
    phases_implemented = roadmap['phases_implementation_status'].get('implemented', {})
    phases_in_progress = roadmap['phases_implementation_status'].get('in_progress', {})
    phases_not_started = roadmap['phases_implementation_status'].get('not_started', {})
    
    print(f"\nPhases by status in roadmap:")
    print(f"  Implemented:   {len(phases_implemented.get('phases', []))}")
    print(f"  In Progress:   {len(phases_in_progress.get('phases', []))}")
    print(f"  Not Started:   {len(phases_not_started.get('phases', []))}")
    
    print(f"\n📋 IMPLEMENTED PHASES CLAIMED:")
    for phase in phases_implemented.get('phases', []):
        phase_id = phase.get('id', 'UNKNOWN')
        title = phase.get('title', 'N/A')
        completion_date = phase.get('completion_date', 'N/A')
        test_count = phase.get('tests', 0)
        print(f"  ✅ {phase_id:40} | Tests: {test_count:4} | Completed: {completion_date}")
    
    print(f"\n🔄 IN PROGRESS PHASES:")
    for phase in phases_in_progress.get('phases', []):
        phase_id = phase.get('id', 'UNKNOWN')
        title = phase.get('title', 'N/A')
        status = phase.get('status', 'N/A')
        print(f"  ⏳ {phase_id:40} | Status: {status}")

except Exception as e:
    print(f"⚠️  Error parsing roadmap: {e}")

# ============================================================================
# SECTION 4: TEST EXECUTION STATUS
# ============================================================================
print("\n" + "=" * 90)
print("SECTION 4: TEST EXECUTION VERIFICATION")
print("=" * 90)
print("Running pytest collection to verify test integrity...")

result = subprocess.run(
    [r'C:\Users\asifh\AppData\Local\Programs\Python\Python313\python.exe', '-m', 'pytest', 
     'tests/', '--co', '-q'],
    cwd=str(CORTEX_ROOT),
    capture_output=True,
    text=True,
    timeout=60
)

# Parse output
output_lines = result.stdout.split('\n')
for line in output_lines[-20:]:
    if line.strip():
        print(f"  {line}")

if result.returncode != 0 and 'error' in result.stdout.lower():
    print(f"\n⚠️  Collection errors detected:")
    for line in output_lines:
        if 'error' in line.lower() or 'ERROR' in line:
            print(f"  {line}")

# ============================================================================
# SECTION 5: CRITICAL FILES EXISTENCE CHECK
# ============================================================================
print("\n" + "=" * 90)
print("SECTION 5: CRITICAL INFRASTRUCTURE VERIFICATION")
print("=" * 90)

critical_files = {
    'Governance DB': CORTEX_ROOT / 'cortex_brain' / 'state' / 'governance.db',
    'Core Rules': CORTEX_ROOT / 'cortex_brain' / 'tier0' / 'governance' / 'core-rules.yaml',
    'MCP Server': CORTEX_ROOT / 'cortex' / 'mcp' / 'server.py',
    'Intent Router': CORTEX_ROOT / 'cortex' / 'intent_router' / '__init__.py',
    'Orchestrators': CORTEX_ROOT / 'cortex' / 'orchestrators' / 'core.py',
}

for name, path in critical_files.items():
    exists = path.exists()
    status = "✅" if exists else "❌"
    size_info = ""
    if exists and path.is_file():
        size_info = f" ({path.stat().st_size:,} bytes)"
    print(f"  {status} {name:20} : {path.relative_to(CORTEX_ROOT)}{size_info}")

print("\n" + "=" * 90)
print("Evidence gathering complete. Ready for detailed analysis.")
print("=" * 90)
