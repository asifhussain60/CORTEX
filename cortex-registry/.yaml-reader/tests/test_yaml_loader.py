#!/usr/bin/env python3
"""
Golden Test: YAML Reader Application Validation
Tests that master-index.yaml loads successfully in both Python and JavaScript parsers.
"""

import json
import subprocess
import sys
from pathlib import Path

import yaml


def test_python_yaml_parse():
    """Test 1: Python YAML parser (PyYAML) - baseline validation."""
    yaml_path = Path(__file__).parent.parent / "master-index.yaml"
    
    print("🔬 Test 1: Python YAML Parser (PyYAML)")
    print(f"   File: {yaml_path}")
    
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        assert data is not None, "YAML data is None"
        assert isinstance(data, dict), f"Expected dict, got {type(data)}"
        assert 'metadata' in data, "Missing 'metadata' key"
        assert 'phase_status' in data, "Missing 'phase_status' key"
        
        print(f"   ✅ PASSED: {len(data)} top-level keys")
        return True
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False


def test_javascript_yaml_parse():
    """Test 2: JavaScript YAML parser (js-yaml) - matches browser environment."""
    yaml_path = Path(__file__).parent.parent / "master-index.yaml"
    vendor_path = Path(__file__).parent / "vendor" / "js-yaml.min.js"
    
    print("\n🔬 Test 2: JavaScript YAML Parser (js-yaml)")
    print(f"   File: {yaml_path}")
    print(f"   Parser: {vendor_path}")
    
    if not vendor_path.exists():
        print(f"   ⚠️  SKIPPED: js-yaml.min.js not found")
        return None
    
    # Create a Node.js test script
    test_script = f"""
const fs = require('fs');
const jsyaml = require('{vendor_path.absolute()}');

try {{
    const content = fs.readFileSync('{yaml_path.absolute()}', 'utf8');
    const data = jsyaml.load(content);
    
    if (!data) {{
        console.log('ERROR: YAML data is null');
        process.exit(1);
    }}
    
    if (typeof data !== 'object') {{
        console.log('ERROR: Expected object, got ' + typeof data);
        process.exit(1);
    }}
    
    if (!data.metadata) {{
        console.log('ERROR: Missing metadata key');
        process.exit(1);
    }}
    
    if (!data.phase_status) {{
        console.log('ERROR: Missing phase_status key');
        process.exit(1);
    }}
    
    const keys = Object.keys(data).length;
    console.log('SUCCESS:' + keys);
    process.exit(0);
}} catch (error) {{
    console.log('ERROR:' + error.message);
    console.log('STACK:' + error.stack);
    process.exit(1);
}}
"""
    
    try:
        result = subprocess.run(
            ['node', '-e', test_script],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            if output.startswith('SUCCESS:'):
                keys = output.split(':')[1]
                print(f"   ✅ PASSED: {keys} top-level keys")
                return True
            else:
                print(f"   ❌ FAILED: Unexpected output: {output}")
                return False
        else:
            error_msg = result.stdout.strip()
            if error_msg.startswith('ERROR:'):
                error = error_msg.split('ERROR:', 1)[1]
                print(f"   ❌ FAILED: {error}")
                if 'STACK:' in result.stdout:
                    stack = result.stdout.split('STACK:', 1)[1].strip()
                    print(f"   Stack trace:\n{stack}")
            else:
                print(f"   ❌ FAILED: {result.stdout}")
                if result.stderr:
                    print(f"   stderr: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"   ❌ FAILED: Test timed out after 10s")
        return False
    except FileNotFoundError:
        print(f"   ⚠️  SKIPPED: Node.js not found")
        return None
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False


def test_yaml_structure_completeness():
    """Test 3: Validate YAML structure matches expected schema."""
    yaml_path = Path(__file__).parent.parent / "master-index.yaml"
    
    print("\n🔬 Test 3: YAML Structure Completeness")
    
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        required_keys = ['metadata', 'phase_status', 'execution_order', 
                        'production_readiness', 'summary']
        missing = [key for key in required_keys if key not in data]
        
        if missing:
            print(f"   ❌ FAILED: Missing keys: {missing}")
            return False
        
        # Validate phase_status structure
        phase_status = data['phase_status']
        expected_sections = ['completed', 'active', 'planned', 'consolidated', 'deferred']
        missing_sections = [s for s in expected_sections if s not in phase_status]
        
        if missing_sections:
            print(f"   ❌ FAILED: Missing phase_status sections: {missing_sections}")
            return False
        
        # Count phases
        completed_count = len(phase_status.get('completed', []))
        active_count = len(phase_status.get('active', []))
        planned_count = len(phase_status.get('planned', []))
        
        print(f"   ✅ PASSED: {completed_count} completed, {active_count} active, {planned_count} planned")
        return True
        
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False


def test_yaml_no_duplicate_keys():
    """Test 4: Detect duplicate keys (Python parser silently overwrites)."""
    yaml_path = Path(__file__).parent.parent / "master-index.yaml"
    
    print("\n🔬 Test 4: No Duplicate Keys (Manual Scan)")
    
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Track phase IDs
        phase_ids = []
        in_completed = False
        
        for i, line in enumerate(lines, 1):
            if 'completed:' in line and line.strip().startswith('completed:'):
                in_completed = True
                continue
            
            if in_completed and line.strip().startswith('- id:'):
                phase_id = line.split('"')[1] if '"' in line else None
                if phase_id:
                    if phase_id in phase_ids:
                        print(f"   ❌ FAILED: Duplicate phase ID '{phase_id}' at line {i}")
                        return False
                    phase_ids.append(phase_id)
            
            if in_completed and line.strip() and not line.strip().startswith((' ', '-', '#')):
                in_completed = False
        
        print(f"   ✅ PASSED: {len(phase_ids)} unique phase IDs")
        return True
        
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False


def main():
    """Run all tests and report results."""
    print("=" * 70)
    print("🧪 CORTEX YAML Reader - Golden Test Suite")
    print("=" * 70)
    print()
    
    results = []
    
    # Run tests
    results.append(("Python YAML Parse", test_python_yaml_parse()))
    results.append(("JavaScript YAML Parse", test_javascript_yaml_parse()))
    results.append(("YAML Structure", test_yaml_structure_completeness()))
    results.append(("No Duplicate Keys", test_yaml_no_duplicate_keys()))
    
    # Report
    print()
    print("=" * 70)
    print("📊 Test Results")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    skipped = sum(1 for _, result in results if result is None)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result is True else "⚠️  SKIP" if result is None else "❌ FAIL"
        print(f"  {status}  {test_name}")
    
    print()
    print(f"Total: {passed}/{total} passed, {failed} failed, {skipped} skipped")
    
    if failed > 0:
        print()
        print("❌ TEST SUITE FAILED")
        sys.exit(1)
    elif passed > 0:
        print()
        print("✅ TEST SUITE PASSED")
        sys.exit(0)
    else:
        print()
        print("⚠️  ALL TESTS SKIPPED")
        sys.exit(2)


if __name__ == '__main__':
    main()
