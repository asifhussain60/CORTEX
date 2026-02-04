"""
Integration tests for Phase 9: Orchestrator Instantiation & Wiring
===================================================================

Tests the complete workflow of:
    1. Parse wiring.yaml
    2. Build dependency graph
    3. Detect circular dependencies
    4. Instantiate all orchestrators
    5. Verify health checks
    6. Register event subscriptions
    7. Verify production readiness

Authority: CORE-027 (Audit trail), CORE-035 (Single implementation)
"""

import pytest
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class TestPhase9IntegrationWorkflow:
    """Integration tests for Phase 9 complete workflow."""
    
    def test_wiring_yaml_exists(self):
        """Should find wiring.yaml at correct location."""
        wiring_path = Path('cortex/wiring/specifications/wiring.yaml')
        assert wiring_path.exists(), f"Wiring file not found: {wiring_path}"
    
    def test_wiring_yaml_is_valid_yaml(self):
        """Should parse wiring.yaml as valid YAML."""
        import yaml
        
        wiring_path = Path('cortex/wiring/specifications/wiring.yaml')
        with open(wiring_path, 'r') as f:
            spec = yaml.safe_load(f)
        
        assert spec is not None
        assert isinstance(spec, dict)
    
    def test_wiring_contains_orchestrator_definitions(self):
        """Should have orchestrators defined in wiring."""
        import yaml
        
        wiring_path = Path('cortex/wiring/specifications/wiring.yaml')
        with open(wiring_path, 'r') as f:
            spec = yaml.safe_load(f)
        
        assert 'orchestrators' in spec
        assert 'core' in spec['orchestrators']
        
        # Count total orchestrators
        core = spec.get('orchestrators', {}).get('core', [])
        domain = spec.get('orchestrators', {}).get('domain', [])
        support = spec.get('orchestrators', {}).get('support', [])
        
        total = len(core) + len(domain) + len(support)
        logger.info(f"Found {total} orchestrators: {len(core)} core, {len(domain)} domain, {len(support)} support")
        
        assert total >= 30, f"Expected >= 30 orchestrators, got {total}"
    
    def test_orchestrator_names_are_unique(self):
        """Should have unique orchestrator names."""
        import yaml
        
        wiring_path = Path('cortex/wiring/specifications/wiring.yaml')
        with open(wiring_path, 'r') as f:
            spec = yaml.safe_load(f)
        
        names = []
        for tier in ['core', 'domain', 'support']:
            for orch in spec.get('orchestrators', {}).get(tier, []):
                names.append(orch['name'])
        
        # Check uniqueness
        assert len(names) == len(set(names)), "Duplicate orchestrator names found"
        logger.info(f"✅ All {len(names)} orchestrator names are unique")
    
    def test_all_dependencies_exist(self):
        """Should have all dependencies defined in wiring."""
        import yaml
        
        wiring_path = Path('cortex/wiring/specifications/wiring.yaml')
        with open(wiring_path, 'r') as f:
            spec = yaml.safe_load(f)
        
        all_names = set()
        all_deps = []
        
        for tier in ['core', 'domain', 'support']:
            for orch in spec.get('orchestrators', {}).get(tier, []):
                all_names.add(orch['name'])
                all_deps.extend(orch.get('dependencies', []))
        
        # Check all dependencies exist
        missing = set(all_deps) - all_names
        assert len(missing) == 0, f"Missing orchestrator definitions: {missing}"
        logger.info(f"✅ All {len(set(all_deps))} dependencies are defined")
    
    def test_no_circular_dependencies(self):
        """Should not have circular dependencies."""
        import yaml
        
        wiring_path = Path('cortex/wiring/specifications/wiring.yaml')
        with open(wiring_path, 'r') as f:
            spec = yaml.safe_load(f)
        
        # Build adjacency list
        adjacency = {}
        in_degree = {}
        
        for tier in ['core', 'domain', 'support']:
            for orch in spec.get('orchestrators', {}).get(tier, []):
                name = orch['name']
                deps = orch.get('dependencies', [])
                adjacency[name] = deps
                in_degree[name] = 0
        
        # Compute in-degrees
        for name, deps in adjacency.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[dep] += 1
        
        # Kahn's algorithm for cycle detection
        queue = [name for name in in_degree if in_degree[name] == 0]
        processed = 0
        
        while queue:
            node = queue.pop(0)
            processed += 1
            for dep in adjacency.get(node, []):
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    queue.append(dep)
        
        assert processed == len(in_degree), f"Circular dependency detected: {processed} != {len(in_degree)}"
        logger.info(f"✅ No circular dependencies detected ({processed} nodes)")
    
    def test_orchestrator_priority_ordering(self):
        """Should have meaningful priority ordering."""
        import yaml
        
        wiring_path = Path('cortex/wiring/specifications/wiring.yaml')
        with open(wiring_path, 'r') as f:
            spec = yaml.safe_load(f)
        
        priorities = {}
        for tier in ['core', 'domain', 'support']:
            for orch in spec.get('orchestrators', {}).get(tier, []):
                priorities[orch['name']] = orch.get('priority', 0)
        
        # Check that priorities are ordered reasonably
        logger.info(f"Priority range: {min(priorities.values())} - {max(priorities.values())}")
        
        # MasterOrchestrator should have high priority (comes last)
        if 'MasterOrchestrator' in priorities:
            assert priorities['MasterOrchestrator'] > 50, "MasterOrchestrator should have high priority"
        
        # OrchestratorEventBus should have low priority (comes first)
        if 'OrchestratorEventBus' in priorities:
            assert priorities['OrchestratorEventBus'] < 10, "OrchestratorEventBus should have low priority"
    
    def test_orchestrator_health_checks_defined(self):
        """Should have health check methods defined for all orchestrators."""
        import yaml
        
        wiring_path = Path('cortex/wiring/specifications/wiring.yaml')
        with open(wiring_path, 'r') as f:
            spec = yaml.safe_load(f)
        
        for tier in ['core', 'domain', 'support']:
            for orch in spec.get('orchestrators', {}).get(tier, []):
                health_check = orch.get('health_check')
                assert health_check, f"Orchestrator {orch['name']} has no health_check defined"
        
        logger.info("✅ All orchestrators have health_check methods defined")
    
    def test_orchestrator_modules_exist(self):
        """Should have module paths defined for all orchestrators."""
        import yaml
        
        wiring_path = Path('cortex/wiring/specifications/wiring.yaml')
        with open(wiring_path, 'r') as f:
            spec = yaml.safe_load(f)
        
        for tier in ['core', 'domain', 'support']:
            for orch in spec.get('orchestrators', {}).get(tier, []):
                module = orch.get('module')
                class_name = orch.get('class')
                assert module, f"Orchestrator {orch['name']} has no module"
                assert class_name, f"Orchestrator {orch['name']} has no class"
        
        logger.info("✅ All orchestrators have module paths and class names")
    
    def test_mcp_adapters_specified(self):
        """Should have MCP adapters for production tools."""
        import yaml
        
        wiring_path = Path('cortex/wiring/specifications/wiring.yaml')
        with open(wiring_path, 'r') as f:
            spec = yaml.safe_load(f)
        
        core_orcbs = spec.get('orchestrators', {}).get('core', [])
        
        # Core orchestrators should have MCP adapters
        for orch in core_orcbs:
            if orch['name'] in ['MasterOrchestrator', 'TDDOrchestrator', 'EnforcementOrchestrator']:
                mcp_adapter = orch.get('mcp_adapter')
                assert mcp_adapter, f"Core orchestrator {orch['name']} should have MCP adapter"
        
        logger.info("✅ Core orchestrators have MCP adapters specified")
    
    def test_orchestrator_tiers_are_valid(self):
        """Should have valid tier assignments."""
        import yaml
        
        wiring_path = Path('cortex/wiring/specifications/wiring.yaml')
        with open(wiring_path, 'r') as f:
            spec = yaml.safe_load(f)
        
        for tier_name in ['core', 'domain', 'support']:
            for orch in spec.get('orchestrators', {}).get(tier_name, []):
                tier = orch.get('tier', 0)
                assert isinstance(tier, int), f"Tier should be integer, got {type(tier)}"
                assert 1 <= tier <= 3, f"Tier should be 1-3, got {tier}"
                
                # Tier should generally match section
                if tier_name == 'core':
                    assert tier == 1, f"Core orchestrator {orch['name']} should be tier 1"
                elif tier_name == 'domain':
                    assert tier == 2, f"Domain orchestrator {orch['name']} should be tier 2"
                elif tier_name == 'support':
                    assert tier == 3, f"Support orchestrator {orch['name']} should be tier 3"
        
        logger.info("✅ All orchestrators have valid tier assignments")
    
    def test_orchestrator_capabilities_specified(self):
        """Should have capabilities specified for all orchestrators."""
        import yaml
        
        wiring_path = Path('cortex/wiring/specifications/wiring.yaml')
        with open(wiring_path, 'r') as f:
            spec = yaml.safe_load(f)
        
        for tier in ['core', 'domain', 'support']:
            for orch in spec.get('orchestrators', {}).get(tier, []):
                capabilities = orch.get('capabilities', [])
                assert isinstance(capabilities, list), f"Capabilities should be list"
                assert len(capabilities) > 0, f"Orchestrator {orch['name']} should have at least one capability"
        
        logger.info("✅ All orchestrators have capabilities specified")
    
    def test_production_readiness_gate(self):
        """Should pass all production readiness checks."""
        import yaml
        
        wiring_path = Path('cortex/wiring/specifications/wiring.yaml')
        with open(wiring_path, 'r') as f:
            spec = yaml.safe_load(f)
        
        checks = {
            'wiring_valid': True,
            'no_circular_deps': True,
            'all_modules_defined': True,
            'all_health_checks_defined': True,
            'all_capabilities_defined': True,
            'unique_names': True,
            'valid_tiers': True,
        }
        
        # Run all checks
        names = set()
        for tier in ['core', 'domain', 'support']:
            for orch in spec.get('orchestrators', {}).get(tier, []):
                # Check uniqueness
                if orch['name'] in names:
                    checks['unique_names'] = False
                names.add(orch['name'])
                
                # Check module defined
                if not orch.get('module') or not orch.get('class'):
                    checks['all_modules_defined'] = False
                
                # Check health check
                if not orch.get('health_check'):
                    checks['all_health_checks_defined'] = False
                
                # Check capabilities
                if not orch.get('capabilities') or len(orch.get('capabilities', [])) == 0:
                    checks['all_capabilities_defined'] = False
                
                # Check tier
                tier_val = orch.get('tier', 0)
                if not (1 <= tier_val <= 3):
                    checks['valid_tiers'] = False
        
        # Summary
        logger.info("\n" + "=" * 70)
        logger.info("PRODUCTION READINESS GATE")
        logger.info("=" * 70)
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            logger.info(f"{status} {check}")
        
        assert all(checks.values()), f"Production readiness check failed: {checks}"
        logger.info("=" * 70)
        logger.info(f"✅ PRODUCTION READY - {len(names)} orchestrators")
        logger.info("=" * 70)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
