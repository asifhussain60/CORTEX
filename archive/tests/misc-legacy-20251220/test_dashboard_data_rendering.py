#!/usr/bin/env python3
"""
TDD Test: Dashboard Data Rendering

RED PHASE: Test that dashboard data is properly embedded and accessible.
This test should FAIL initially, proving the bug exists.

Author: Asif Hussain
"""

import json
import re
from pathlib import Path


def test_dashboard_has_embedded_data():
    """Test that dashboardData object is embedded in HTML"""
    dashboard_path = Path("cortex-brain/documents/onboarded-apps/noor-canvas/dashboard.html")
    
    assert dashboard_path.exists(), f"Dashboard not found: {dashboard_path}"
    
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: dashboardData variable exists
    assert 'const dashboardData' in content, "Missing 'const dashboardData' declaration"
    
    # Test 2: Extract and parse embedded data
    pattern = r'const dashboardData\s*=\s*(\{[\s\S]*?\n\s*\});'
    match = re.search(pattern, content)
    assert match, "Could not extract dashboardData from HTML"
    
    data_str = match.group(1)
    data = json.loads(data_str)
    
    # Test 3: Required top-level keys present
    required_keys = ['project_info', 'quality', 'security', 'architecture', 
                     'techstack', 'recommendations', 'metadata', 'overview', 'visualizations']
    for key in required_keys:
        assert key in data, f"Missing required key: {key}"
    
    # Test 4: Visualizations has forceGraph data
    assert 'visualizations' in data, "Missing visualizations section"
    assert 'forceGraph' in data['visualizations'], "Missing forceGraph in visualizations"
    
    force_graph = data['visualizations']['forceGraph']
    assert 'nodes' in force_graph, "forceGraph missing 'nodes'"
    assert 'links' in force_graph, "forceGraph missing 'links'"
    
    # Test 5: D3 data structure is populated
    nodes = force_graph['nodes']
    links = force_graph['links']
    
    assert isinstance(nodes, list), "nodes should be a list"
    assert isinstance(links, list), "links should be a list"
    assert len(nodes) > 0, f"Expected nodes, got empty list (architecture has 8680 nodes)"
    assert len(links) > 0, f"Expected links, got empty list"
    
    print(f"✅ Test passed: {len(nodes)} nodes, {len(links)} links")
    return True


def test_d3_visualization_script_exists():
    """Test that D3.js visualization initialization code is present"""
    dashboard_path = Path("cortex-brain/documents/onboarded-apps/noor-canvas/dashboard.html")
    
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: D3.js library loaded
    assert 'd3js.org' in content or 'd3.v7' in content, "D3.js library not loaded"
    
    # Test 2: Force graph initialization code exists
    assert 'forceSimulation' in content, "D3 forceSimulation code missing"
    assert 'forceLink' in content, "D3 forceLink code missing"
    
    # Test 3: Graph container element exists
    assert 'id="architecture-graph"' in content, "Missing #architecture-graph container"
    
    print("✅ D3 visualization code present")
    return True


def test_architecture_data_structure():
    """Test that architecture.json has correct D3 format"""
    arch_path = Path("cortex-brain/documents/onboarded-apps/noor-canvas/architecture.json")
    
    assert arch_path.exists(), f"architecture.json not found"
    
    with open(arch_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Test 1: Has d3_data section
    assert 'd3_data' in data, "Missing d3_data in architecture.json"
    
    d3_data = data['d3_data']
    assert 'nodes' in d3_data, "d3_data missing 'nodes'"
    assert 'links' in d3_data, "d3_data missing 'links'"
    
    # Test 2: Nodes have required fields
    nodes = d3_data['nodes']
    assert len(nodes) > 0, "d3_data nodes is empty"
    
    sample_node = nodes[0]
    required_fields = ['id', 'name', 'type']
    for field in required_fields:
        assert field in sample_node, f"Node missing field: {field}"
    
    # Test 3: Links have required fields
    links = d3_data['links']
    if len(links) > 0:
        sample_link = links[0]
        link_fields = ['source', 'target']
        for field in link_fields:
            assert field in sample_link, f"Link missing field: {field}"
    
    print(f"✅ Architecture data valid: {len(nodes)} nodes, {len(links)} links")
    return True


if __name__ == '__main__':
    print("=" * 70)
    print("TDD RED PHASE: Dashboard Data Rendering Tests")
    print("=" * 70)
    print("\nThese tests should FAIL, proving the bug exists.\n")
    
    tests = [
        ("Embedded Data Structure", test_dashboard_has_embedded_data),
        ("D3 Visualization Code", test_d3_visualization_script_exists),
        ("Architecture Data Format", test_architecture_data_structure)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            test_func()
            results.append((test_name, "PASS"))
        except AssertionError as e:
            print(f"❌ FAILED: {e}")
            results.append((test_name, f"FAIL: {e}"))
        except Exception as e:
            print(f"💥 ERROR: {e}")
            results.append((test_name, f"ERROR: {e}"))
    
    print("\n" + "=" * 70)
    print("TEST RESULTS")
    print("=" * 70)
    for test_name, result in results:
        status = "✅" if result == "PASS" else "❌"
        print(f"{status} {test_name}: {result}")
    
    total_pass = sum(1 for _, r in results if r == "PASS")
    print(f"\nPassed: {total_pass}/{len(tests)}")
