#!/usr/bin/env python3
"""
YAML Validation Test Suite
Tests all YAML files in cortex-registry for parse errors and structural issues.
"""

import yaml
import sys
import pytest
from pathlib import Path
from collections import Counter


@pytest.fixture(params=list((Path(__file__).parent.parent.parent).rglob("*.yaml")))
def file_path(request):
    """Parametrize all YAML files in cortex-registry."""
    return request.param


def test_yaml_file(file_path):
    """Test a single YAML file for validity."""
    errors = []
    warnings = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for common issues before parsing
        lines = content.split('\n')
        
        # Check for duplicate keys in same section
        section_keys = {}
        current_indent = -1
        for i, line in enumerate(lines, 1):
            stripped = line.lstrip()
            if not stripped or stripped.startswith('#'):
                continue
                
            indent = len(line) - len(stripped)
            
            if ':' in stripped and not stripped.startswith('-'):
                key = stripped.split(':')[0].strip()
                
                # Reset tracking if indent decreased
                if indent <= current_indent:
                    section_keys = {}
                    
                current_indent = indent
                
                # Check for duplicate
                if key in section_keys:
                    errors.append(f"Line {i}: Duplicate key '{key}' (first seen at line {section_keys[key]})")
                else:
                    section_keys[key] = i
        
        # Try to parse YAML
        data = yaml.safe_load(content)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'data': data
        }
        
    except yaml.YAMLError as e:
        error_msg = str(e)
        if hasattr(e, 'problem_mark'):
            mark = e.problem_mark
            error_msg = f"Line {mark.line + 1}, Column {mark.column + 1}: {e.problem}"
        errors.append(error_msg)
        
        return {
            'valid': False,
            'errors': errors,
            'warnings': warnings,
            'data': None
        }
    except Exception as e:
        errors.append(f"Unexpected error: {str(e)}")
        return {
            'valid': False,
            'errors': errors,
            'warnings': warnings,
            'data': None
        }

def find_duplicate_keys_in_dict(d, path="", duplicates=None):
    """Recursively find duplicate keys in nested dictionaries."""
    if duplicates is None:
        duplicates = []
    
    if isinstance(d, dict):
        key_counts = Counter(d.keys())
        for key, count in key_counts.items():
            if count > 1:
                duplicates.append(f"{path}.{key}" if path else key)
        
        for key, value in d.items():
            new_path = f"{path}.{key}" if path else key
            find_duplicate_keys_in_dict(value, new_path, duplicates)
    
    elif isinstance(d, list):
        for i, item in enumerate(d):
            find_duplicate_keys_in_dict(item, f"{path}[{i}]", duplicates)
    
    return duplicates

def validate_registry():
    """Validate all YAML files in cortex-registry."""
    registry_path = Path(__file__).parent.parent.parent
    
    print("="*70)
    print("CORTEX Registry YAML Validation Test Suite")
    print("="*70)
    
    # Test cortex-master.yaml first
    master_file = registry_path / "cortex-master.yaml"
    print(f"\n🔍 Testing: {master_file.name}")
    print("-"*70)
    
    result = test_yaml_file(master_file)
    
    if result['valid']:
        print("✅ VALID")
        data = result['data']
        if 'phase_status' in data:
            ps = data['phase_status']
            print(f"   Sections: {list(ps.keys())}")
            print(f"   Completed: {len(ps.get('completed', []))} phases")
            print(f"   Active: {len(ps.get('active', []))} phases")
            print(f"   Consolidated: {len(ps.get('consolidated', []))} phases")
    else:
        print("❌ INVALID")
        for error in result['errors']:
            print(f"   ERROR: {error}")
        for warning in result['warnings']:
            print(f"   WARNING: {warning}")
    
    # Test all phase YAML files
    phase_dirs = [
        registry_path / "_cortex-master" / "phases",
        registry_path / "phases"
    ]
    
    all_results = {}
    total_valid = 0
    total_invalid = 0
    
    for phase_dir in phase_dirs:
        if not phase_dir.exists():
            continue
            
        phase_files = sorted(phase_dir.rglob("*.yaml"))
        
        if not phase_files:
            continue
            
        print(f"\n📁 Testing phase files in: {phase_dir.relative_to(registry_path)}")
        print("-"*70)
        
        for phase_file in phase_files:
            result = test_yaml_file(phase_file)
            rel_path = phase_file.relative_to(registry_path)
            all_results[str(rel_path)] = result
            
            if result['valid']:
                total_valid += 1
                print(f"✅ {rel_path}")
            else:
                total_invalid += 1
                print(f"❌ {rel_path}")
                for error in result['errors'][:2]:  # Show first 2 errors
                    print(f"     {error}")
    
    # Test all other YAML files
    print(f"\n📁 Testing remaining YAML files")
    print("-"*70)
    
    all_yaml = sorted(registry_path.rglob("*.yaml"))
    tested_files = set(all_results.keys())
    
    for yaml_file in all_yaml:
        if '.venv' in str(yaml_file) or 'node_modules' in str(yaml_file):
            continue
            
        rel_path = yaml_file.relative_to(registry_path)
        
        if str(rel_path) in tested_files or rel_path.name == 'cortex-master.yaml':
            continue
        
        result = test_yaml_file(yaml_file)
        all_results[str(rel_path)] = result
        
        if result['valid']:
            total_valid += 1
        else:
            total_invalid += 1
            print(f"❌ {rel_path}")
            for error in result['errors'][:1]:
                print(f"     {error}")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"✅ Valid:   {total_valid}")
    print(f"❌ Invalid: {total_invalid}")
    print(f"📊 Total:   {total_valid + total_invalid}")
    
    if total_invalid == 0:
        print("\n🎉 ALL YAML FILES ARE VALID!")
        print("🚀 Ready to load in YAML Reader")
        return 0
    else:
        print(f"\n⚠️  {total_invalid} files need fixing")
        return 1

if __name__ == "__main__":
    sys.exit(validate_registry())
