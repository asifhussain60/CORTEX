"""
Test: Master Orchestrator Routing for ADO v2

Quick validation that master orchestrator routes ADO commands to v2.
"""

import re
import yaml
from pathlib import Path


def test_ado_v2_routing():
    """Test: ADO v2 routing patterns in master orchestrator."""
    
    # Load master orchestrator config
    config_path = Path(__file__).parents[4] / "cortex-brain" / "config" / "master-orchestrator.yaml"
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    routing_rules = config['routing_rules']
    
    # Test cases: (input_command, expected_orchestrator, expected_mode)
    test_cases = [
        ("ado wizard user authentication", "ado_orchestrator_v2", "wizard"),
        ("ado interactive login feature", "ado_orchestrator_v2", "wizard"),
        ("ado story implement JWT auth", "ado_orchestrator_v2", "auto"),
        ("ado feature payment gateway", "ado_orchestrator_v2", "auto"),
        ("azure devops new feature", "ado_orchestrator_v2", "auto"),
    ]
    
    print("\\n🔍 Testing ADO v2 Routing Patterns\\n")
    
    for command, expected_orch, expected_mode in test_cases:
        matched = False
        
        for rule in routing_rules:
            pattern = rule['pattern']
            
            if rule['match_type'] == 'regex':
                if re.match(pattern, command, re.IGNORECASE):
                    orchestrator = rule['orchestrator']
                    mode = rule['metadata'].get('mode', 'auto')
                    
                    # Verify match
                    status = "✅" if orchestrator == expected_orch and mode == expected_mode else "❌"
                    print(f"{status} '{command}'")
                    print(f"   → Orchestrator: {orchestrator} (expected: {expected_orch})")
                    print(f"   → Mode: {mode} (expected: {expected_mode})")
                    print(f"   → Priority: {rule['priority']}")
                    print()
                    
                    matched = True
                    
                    assert orchestrator == expected_orch, f"Wrong orchestrator: {orchestrator}"
                    assert mode == expected_mode, f"Wrong mode: {mode}"
                    
                    break
        
        if not matched:
            print(f"❌ '{command}' - NO MATCH FOUND")
            print()
            assert False, f"No routing rule matched: {command}"
    
    print("✅ All routing tests passed!")


def test_ado_v2_registry():
    """Test: ADO v2 registered in MCP server config."""
    
    registry_path = Path(__file__).parents[4] / "cortex-brain" / "config" / "mcp-server.yaml"
    
    with open(registry_path, 'r') as f:
        config = yaml.safe_load(f)
    
    orchestrators = config['orchestrators']
    
    print("\\n🔍 Testing ADO v2 Registry Entry\\n")
    
    # Check for ado_orchestrator_v2
    assert 'ado_orchestrator_v2' in orchestrators, "ado_orchestrator_v2 not in registry"
    
    ado_v2 = orchestrators['ado_orchestrator_v2']
    
    # Verify fields
    assert ado_v2['class'] == 'ADOOrchestratorV2', f"Wrong class: {ado_v2['class']}"
    assert ado_v2['module'] == 'src.orchestrators.ado.v2.ado_orchestrator_v2', f"Wrong module: {ado_v2['module']}"
    assert ado_v2['config'] == 'cortex-brain/manifests/orchestrators/ado-orchestrator-v2.yaml', f"Wrong config: {ado_v2['config']}"
    assert ado_v2['type'] == 'autonomous', f"Wrong type: {ado_v2['type']}"
    assert ado_v2['version'] == '2.0.0', f"Wrong version: {ado_v2['version']}"
    assert 'auto' in ado_v2['modes'], "Missing 'auto' mode"
    assert 'wizard' in ado_v2['modes'], "Missing 'wizard' mode"
    
    print("✅ Registry Entry Validated:")
    print(f"   Class: {ado_v2['class']}")
    print(f"   Module: {ado_v2['module']}")
    print(f"   Config: {ado_v2['config']}")
    print(f"   Type: {ado_v2['type']}")
    print(f"   Version: {ado_v2['version']}")
    print(f"   Modes: {ado_v2['modes']}")
    print()


if __name__ == "__main__":
    try:
        test_ado_v2_routing()
        test_ado_v2_registry()
        print("\\n🎉 All Master Orchestrator tests passed!\\n")
    except AssertionError as e:
        print(f"\\n❌ Test failed: {e}\\n")
        exit(1)
    except Exception as e:
        print(f"\\n❌ Error: {e}\\n")
        exit(1)
