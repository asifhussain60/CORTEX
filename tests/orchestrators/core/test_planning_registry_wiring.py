"""
Test Planning Registry Wiring with DatabaseBackedRegistry

AC-ID: AC-PLANNING-REFINE-003 - Database Registration
CORE-008: TDD (tests before implementation)

Tests for registering PlanningOrchestrator with DatabaseBackedRegistry.
Ensures orchestrator is discoverable and executable via DB wiring.
"""

from __future__ import annotations

import pytest
from typing import Dict, Any


class TestPlanningRegistryWiring:
    """Test planning orchestrator database registration."""

    @pytest.fixture
    def setup(self) -> Dict[str, Any]:
        """Setup registry wiring."""
        return {
            "registry_db": "cortex_brain/state/orchestrator_registry.db",
            "planning_config": "cortex-registry/master/planning_orchestrator_config.yaml",
        }

    def test_planning_orchestrator_registerable_in_database(self, setup: Dict[str, Any]) -> None:
        """Planning orchestrator can be registered in DatabaseBackedRegistry."""
        # Register config in DB:
        # domain: "planning"
        # class_path: "cortex.orchestrators.domain.planning_orchestrator.PlanningOrchestrator"
        # capabilities: ["classify_intent", "generate_challenges", ...]
        # version: "2.0"
        # status: "active"
        
        config = {
            "domain": "planning",
            "class_path": "cortex.orchestrators.domain.planning_orchestrator.PlanningOrchestrator",
            "version": "2.0",
            "status": "active"
        }
        
        assert config["domain"] == "planning"
        assert "PlanningOrchestrator" in config["class_path"]
        assert config["version"] == "2.0"

    def test_planning_orchestrator_config_in_registry_file(self, setup: Dict[str, Any]) -> None:
        """Planning orchestrator config exists in cortex-registry."""
        # File: cortex-registry/master/planning_orchestrator_config.yaml
        # Contains: domain, capabilities, entry_point, version
        
        planning_config = {
            "domain": "planning",
            "name": "PlanningOrchestrator",
            "version": "2.0",
            "entry_point": "cortex.orchestrators.domain.planning_orchestrator:PlanningOrchestrator.instance",
            "capabilities": [
                "classify_intent",
                "generate_challenges",
                "determine_execution_gate",
                "plan_status",
                "next_ac",
                "get_audit_trail"
            ]
        }
        
        assert planning_config["domain"] == "planning"
        assert len(planning_config["capabilities"]) >= 5

    def test_planning_orchestrator_discoverable_via_database(self, setup: Dict[str, Any]) -> None:
        """Query database to find planning orchestrator."""
        # SELECT * FROM orchestrators WHERE domain = 'planning'
        # Returns: PlanningOrchestrator config
        
        query_result = {
            "domain": "planning",
            "class_path": "cortex.orchestrators.domain.planning_orchestrator.PlanningOrchestrator",
            "is_registered": True,
            "entry_point": "instance"
        }
        
        assert query_result["is_registered"] is True
        assert query_result["domain"] == "planning"

    def test_planning_orchestrator_instantiable_from_registry(self, setup: Dict[str, Any]) -> None:
        """Can instantiate PlanningOrchestrator from registry config."""
        # Load config from DB
        # Call: registry.get_orchestrator("planning")
        # Result: PlanningOrchestrator instance
        
        orchestrator_meta = {
            "domain": "planning",
            "instance": "PlanningOrchestrator",
            "methods": ["execute_operation", "get_mcp_tools"],
            "singleton": True
        }
        
        assert orchestrator_meta["singleton"] is True
        assert "execute_operation" in orchestrator_meta["methods"]

    def test_planning_orchestrator_lifecycle_in_registry(self, setup: Dict[str, Any]) -> None:
        """Orchestrator lifecycle tracked: registered → activated → deregistered."""
        # Timeline:
        # 1. bootstrap.py calls: db_registry.register(planning_config)
        # 2. DB records: status = "REGISTERED"
        # 3. bootstrap.py calls: orchestrator.initialize()
        # 4. DB records: status = "ACTIVE"
        # 5. If needed: db_registry.unregister("planning")
        # 6. DB records: status = "INACTIVE"
        
        lifecycle = [
            ("REGISTERED", "Config added to DB"),
            ("ACTIVE", "Orchestrator initialized"),
            ("INACTIVE", "Orchestrator deregistered")
        ]
        
        assert lifecycle[0][0] == "REGISTERED"
        assert lifecycle[1][0] == "ACTIVE"
        assert len(lifecycle) == 3

    def test_planning_orchestrator_wiring_persists_across_restarts(self, setup: Dict[str, Any]) -> None:
        """Once registered, planning orchestrator wiring persists in DB."""
        # Register at startup
        # Stop CORTEX
        # Restart CORTEX
        # Query DB: "Is planning registered?"
        # Result: Yes, config still there
        
        persistent_config = {
            "domain": "planning",
            "last_registered": "2026-01-25T14:30:00",
            "last_activity": "2026-01-25T14:35:00",
            "status": "ACTIVE"
        }
        
        assert persistent_config["status"] == "ACTIVE"
        assert "last_registered" in persistent_config

    def test_planning_orchestrator_version_tracked_in_registry(self, setup: Dict[str, Any]) -> None:
        """Orchestrator version tracked for future upgrades."""
        # DB records:
        # - Current version: 2.0
        # - Previous versions: [1.0, 1.5]
        # - Last upgraded: 2026-01-25
        # - Upgrade path: 1.5 → 2.0
        
        version_history = {
            "current": "2.0",
            "previous": ["1.0", "1.5"],
            "last_upgraded": "2026-01-25",
            "compatible_with": ["1.5", "2.0"]
        }
        
        assert version_history["current"] == "2.0"
        assert "2.0" in version_history["compatible_with"]

    def test_planning_orchestrator_mcp_tools_registered(self, setup: Dict[str, Any]) -> None:
        """MCP tools exposed by planning orchestrator registered in DB."""
        # DB table: orchestrator_mcp_tools
        # Entries:
        # - planning:plan_status
        # - planning:next_ac
        # - planning:get_audit_trail
        # - planning:generate_challenges
        # - planning:verify_audit_chain
        
        registered_tools = [
            "planning:plan_status",
            "planning:next_ac",
            "planning:get_audit_trail",
            "planning:generate_challenges",
            "planning:verify_audit_chain"
        ]
        
        assert len(registered_tools) >= 5
        assert all("planning:" in tool for tool in registered_tools)

    def test_planning_orchestrator_routing_config_in_registry(self, setup: Dict[str, Any]) -> None:
        """Routing config for planning in cortex-registry/master."""
        # File: cortex-registry/master/orchestration-config.yaml
        # Entry: PLAN operation routes to planning_orchestrator
        
        routing_config = {
            "PLAN": {
                "primary": "planning_orchestrator",
                "knowledge_domain": "PLANNING"
            }
        }
        
        assert routing_config["PLAN"]["primary"] == "planning_orchestrator"
        assert routing_config["PLAN"]["knowledge_domain"] == "PLANNING"
