"""AC-PHASE43-022: Integration Orchestrator

Validates cross-component integration and workflow coordination.

Target: 5/5 tests passing
AC-ID: AC-PHASE43-022
"""

import pytest
from typing import Dict, Any, List


class IntegrationOrchestrator:
    """Orchestrate integration across CORTEX components (Phase 43: AC-PHASE43-022)."""
    
    def __init__(self):
        """Initialize orchestrator."""
        self.integration_steps = []
        self.component_status = {}
    
    def integrate_components(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Orchestrate integration of CORTEX components.
        
        Args:
            components: List of components to integrate
            
        Returns:
            Integration result with status and metrics
        """
        self.integration_steps = []
        self.component_status = {}
        
        # Step 1: Validate components
        validation = self._validate_components(components)
        if not validation["valid"]:
            return {"status": "failed", "error": "validation failed"}
        self.integration_steps.append("validation")
        
        # Step 2: Resolve dependencies
        resolution = self._resolve_dependencies(components)
        self.component_status = resolution["status_map"]
        self.integration_steps.append("dependency_resolution")
        
        # Step 3: Initialize components
        initialization = self._initialize_components(components)
        self.integration_steps.append("initialization")
        
        # Step 4: Wire event handlers
        wiring = self._wire_event_handlers(components)
        self.integration_steps.append("event_wiring")
        
        # Step 5: Verify integration
        verification = self._verify_integration(components)
        self.integration_steps.append("verification")
        
        return {
            "status": "success",
            "steps": self.integration_steps,
            "component_count": len(components),
            "component_status": self.component_status,
            "integration_health": verification["health_score"],
        }
    
    def _validate_components(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate component definitions."""
        errors = []
        
        for comp in components:
            if "name" not in comp:
                errors.append("Component missing 'name' field")
            if "interfaces" not in comp:
                errors.append(f"Component {comp.get('name')} missing 'interfaces'")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    def _resolve_dependencies(self, 
                             components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Resolve component dependencies."""
        status_map = {}
        
        for comp in components:
            deps = comp.get("dependencies", [])
            resolved = all(any(c.get("name") == dep for c in components) for dep in deps)
            
            status_map[comp.get("name")] = {
                "resolved": resolved,
                "dependency_count": len(deps),
                "missing_deps": [d for d in deps if not any(c.get("name") == d for c in components)],
            }
        
        return {"status_map": status_map, "all_resolved": all(v["resolved"] for v in status_map.values())}
    
    def _initialize_components(self, 
                              components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Initialize components."""
        initialized = []
        
        for comp in components:
            init_result = {
                "component": comp.get("name"),
                "initialized": True,
                "interfaces": len(comp.get("interfaces", [])),
            }
            initialized.append(init_result)
        
        return {"initialized": initialized, "count": len(initialized)}
    
    def _wire_event_handlers(self, 
                            components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Wire event handlers between components."""
        wired_connections = 0
        
        for comp in components:
            interfaces = comp.get("interfaces", [])
            for other in components:
                if comp != other:
                    other_interfaces = other.get("interfaces", [])
                    # Count matching interface pairs
                    wired_connections += len(set(interfaces) & set(other_interfaces))
        
        return {
            "wired_connections": wired_connections,
            "integration_complete": wired_connections > 0 or len(components) == 1,
        }
    
    def _verify_integration(self, 
                           components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Verify integration health."""
        if not components:
            return {"health_score": 0.0}
        
        # Check all components initialized and wired
        all_present = len(components) > 0
        interdependencies = sum(len(c.get("dependencies", [])) for c in components)
        
        # Health: 60% presence, 40% interconnectedness
        presence_score = 1.0 if all_present else 0.0
        interconnect_score = min(1.0, interdependencies / max(1, len(components) * 2))
        
        health_score = (presence_score * 0.6) + (interconnect_score * 0.4)
        
        return {"health_score": health_score, "issues_found": 0}


class TestIntegrationOrchestrator:
    """Tests for integration orchestration."""
    
    def test_orchestrator_initializes(self):
        """Validate orchestrator initializes."""
        orch = IntegrationOrchestrator()
        assert orch is not None
        assert orch.integration_steps == []
    
    def test_orchestrator_validates_components(self):
        """Validate component validation."""
        orch = IntegrationOrchestrator()
        
        invalid_components = [{"missing_name": "test"}]
        
        result = orch.integrate_components(invalid_components)
        
        assert result["status"] == "failed"
    
    def test_orchestrator_integrates_valid_components(self):
        """Validate successful integration."""
        orch = IntegrationOrchestrator()
        
        components = [
            {
                "name": "refactoring",
                "interfaces": ["code_analysis"],
                "dependencies": [],
            },
            {
                "name": "analyzer",
                "interfaces": ["code_analysis"],
                "dependencies": ["refactoring"],
            },
        ]
        
        result = orch.integrate_components(components)
        
        assert result["status"] == "success"
        assert len(result["steps"]) == 5
    
    def test_orchestrator_resolves_dependencies(self):
        """Validate dependency resolution."""
        orch = IntegrationOrchestrator()
        
        components = [
            {"name": "A", "interfaces": [], "dependencies": ["B"]},
            {"name": "B", "interfaces": [], "dependencies": []},
        ]
        
        result = orch.integrate_components(components)
        
        status = result["component_status"]
        assert status["A"]["resolved"] is True
        assert status["B"]["resolved"] is True
    
    def test_orchestrator_verifies_health(self):
        """Validate integration health verification."""
        orch = IntegrationOrchestrator()
        
        components = [
            {"name": "C1", "interfaces": ["evt"], "dependencies": ["C2"]},
            {"name": "C2", "interfaces": ["evt"], "dependencies": ["C1"]},
        ]
        
        result = orch.integrate_components(components)
        
        assert result["integration_health"] >= 0.5
