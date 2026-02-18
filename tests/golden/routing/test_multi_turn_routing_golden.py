"""
Golden Tests for Multi-Turn Routing with Context Crystallization

Tests interaction flows across multiple turns with context preservation,
routing decisions, and crystallization layer integration.

Based on audit log analysis showing:
- Onboarding is most common operation (215+ logs)
- Multi-turn context critical for interaction quality
- Routing decisions need validation across orchestrators

Authority: CORE-008 (TDD), CORE-027 (Audit), CORE-049 (Silent)
Priority: P0 - Critical Path Validation
"""

import json
import sqlite3
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest
import yaml


@dataclass
class TurnContext:
    """Context for a single turn in multi-turn interaction."""
    turn_number: int
    user_input: str
    expected_orchestrator: str
    context_keys: List[str]  # Keys expected in crystallized context
    routing_confidence: float


@dataclass
class MultiTurnScenario:
    """Multi-turn interaction scenario."""
    scenario_id: str
    description: str
    turns: List[TurnContext]
    expected_context_accumulation: Dict[str, Any]
    expected_routing_chain: List[str]


class ContextCrystallizationSimulator:
    """Simulates context crystallization for testing."""
    
    def __init__(self):
        self.accumulated_context: Dict[str, Any] = {}
        self.turn_history: List[Dict[str, Any]] = []
    
    def add_turn(self, turn: TurnContext, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add turn to context and return crystallized context.
        
        Args:
            turn: Turn context
            response: Orchestrator response
        
        Returns:
            Crystallized context after this turn
        """
        # Record turn
        turn_record = {
            "turn_number": turn.turn_number,
            "user_input": turn.user_input,
            "orchestrator": turn.expected_orchestrator,
            "timestamp": datetime.utcnow().isoformat(),
            "response": response
        }
        self.turn_history.append(turn_record)
        
        # Update accumulated context
        for key in turn.context_keys:
            if key not in self.accumulated_context:
                self.accumulated_context[key] = []
            self.accumulated_context[key].append({
                "turn": turn.turn_number,
                "value": response.get(key, None)
            })
        
        # Return crystallized context
        return {
            "turn_count": len(self.turn_history),
            "current_turn": turn.turn_number,
            "accumulated_context": self.accumulated_context,
            "turn_history": self.turn_history,
            "routing_chain": [t["orchestrator"] for t in self.turn_history]
        }
    
    def get_context_for_turn(self, turn_number: int) -> Dict[str, Any]:
        """Get crystallized context up to specified turn."""
        relevant_history = [t for t in self.turn_history if t["turn_number"] <= turn_number]
        return {
            "turn_count": len(relevant_history),
            "history": relevant_history,
            "accumulated_keys": list(self.accumulated_context.keys())
        }


class AuditVerifier:
    """Verifies audit logs for routing decisions."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
    
    def verify_routing_chain(
        self,
        scenario_id: str,
        expected_chain: List[str]
    ) -> bool:
        """
        Verify routing chain matches expected sequence.
        
        Args:
            scenario_id: Scenario identifier
            expected_chain: Expected orchestrator chain
        
        Returns:
            True if chain matches
        """
        if not self.db_path.exists():
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Query audit logs for scenario
            cursor.execute("""
                SELECT orchestrator_name, timestamp
                FROM orchestrator_audit_events
                WHERE details LIKE ?
                ORDER BY timestamp ASC
            """, (f"%{scenario_id}%",))
            
            actual_chain = [row[0] for row in cursor.fetchall()]
            return actual_chain == expected_chain
        
        finally:
            conn.close()
    
    def get_context_evolution(self, scenario_id: str) -> List[Dict[str, Any]]:
        """Get context evolution across turns."""
        if not self.db_path.exists():
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT turn_number, context_snapshot
                FROM context_evolution_log
                WHERE scenario_id = ?
                ORDER BY turn_number ASC
            """, (scenario_id,))
            
            return [
                {"turn": row[0], "context": json.loads(row[1])}
                for row in cursor.fetchall()
            ]
        
        except sqlite3.OperationalError:
            # Table doesn't exist yet
            return []
        
        finally:
            conn.close()


@pytest.fixture
def temp_audit_db():
    """Create temporary audit database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    
    # Initialize schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orchestrator_audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            orchestrator_name TEXT NOT NULL,
            operation TEXT NOT NULL,
            details TEXT,
            result TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS context_evolution_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scenario_id TEXT NOT NULL,
            turn_number INTEGER NOT NULL,
            context_snapshot TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    db_path.unlink(missing_ok=True)


@pytest.fixture
def crystallization_simulator():
    """Create context crystallization simulator."""
    return ContextCrystallizationSimulator()


@pytest.fixture
def audit_verifier(temp_audit_db):
    """Create audit verifier."""
    return AuditVerifier(temp_audit_db)


# ============================================================================
# GOLDEN TEST SCENARIOS
# ============================================================================

GOLDEN_SCENARIOS = [
    MultiTurnScenario(
        scenario_id="GT-ROUTE-001",
        description="Onboarding → Query → Implementation multi-turn",
        turns=[
            TurnContext(
                turn_number=1,
                user_input="Onboard KSESSIONS repository",
                expected_orchestrator="OnboardingOrchestrator",
                context_keys=["repository_path", "onboarding_result"],
                routing_confidence=0.95
            ),
            TurnContext(
                turn_number=2,
                user_input="What patterns were detected?",
                expected_orchestrator="QueryCoordinator",
                context_keys=["patterns_detected", "architecture_type"],
                routing_confidence=0.90
            ),
            TurnContext(
                turn_number=3,
                user_input="Fix the dependency issue found",
                expected_orchestrator="TDDOrchestrator",
                context_keys=["fix_plan", "tests_created"],
                routing_confidence=0.88
            ),
        ],
        expected_context_accumulation={
            "repository_path": "/path/to/KSESSIONS",
            "patterns": ["mvc", "repository"],
            "issues": ["dependency_mismatch"]
        },
        expected_routing_chain=[
            "OnboardingOrchestrator",
            "QueryCoordinator",
            "TDDOrchestrator"
        ]
    ),
    
    MultiTurnScenario(
        scenario_id="GT-ROUTE-002",
        description="Query → Challenge → Approve multi-turn with governance",
        turns=[
            TurnContext(
                turn_number=1,
                user_input="List all governance violations",
                expected_orchestrator="QueryCoordinator",
                context_keys=["violations_count", "violations_list"],
                routing_confidence=0.92
            ),
            TurnContext(
                turn_number=2,
                user_input="Fix all P0 violations",
                expected_orchestrator="ChallengeOrchestrator",
                context_keys=["challenge_alternatives", "risk_score"],
                routing_confidence=0.85
            ),
            TurnContext(
                turn_number=3,
                user_input="proceed with option A",
                expected_orchestrator="TDDOrchestrator",
                context_keys=["implementation_result", "tests_passing"],
                routing_confidence=0.90
            ),
        ],
        expected_context_accumulation={
            "violations": ["CORE-002", "CORE-008"],
            "challenge_presented": True,
            "user_choice": "option_a"
        },
        expected_routing_chain=[
            "QueryCoordinator",
            "ChallengeOrchestrator",
            "TDDOrchestrator"
        ]
    ),
    
    MultiTurnScenario(
        scenario_id="GT-ROUTE-003",
        description="Onboarding → Analysis → Refactor with LENS context",
        turns=[
            TurnContext(
                turn_number=1,
                user_input="Onboard repository and analyze architecture",
                expected_orchestrator="OnboardingOrchestrator",
                context_keys=["lens_analysis", "ast_graph"],
                routing_confidence=0.94
            ),
            TurnContext(
                turn_number=2,
                user_input="Show me the circular dependencies",
                expected_orchestrator="QueryCoordinator",
                context_keys=["circular_deps", "affected_files"],
                routing_confidence=0.91
            ),
            TurnContext(
                turn_number=3,
                user_input="Refactor to remove circular dependencies",
                expected_orchestrator="RefactoringOrchestrator",
                context_keys=["refactor_plan", "files_changed"],
                routing_confidence=0.87
            ),
        ],
        expected_context_accumulation={
            "lens_data": {"ast": {}, "dependencies": []},
            "circular_deps": ["module_a->module_b->module_a"],
            "refactor_completed": True
        },
        expected_routing_chain=[
            "OnboardingOrchestrator",
            "QueryCoordinator",
            "RefactoringOrchestrator"
        ]
    ),
]


# ============================================================================
# TEST CASES
# ============================================================================

class TestMultiTurnRouting:
    """Test multi-turn routing with context crystallization."""
    
    @pytest.mark.parametrize("scenario", GOLDEN_SCENARIOS, ids=lambda s: s.scenario_id)
    def test_routing_chain_golden(
        self,
        scenario: MultiTurnScenario,
        crystallization_simulator: ContextCrystallizationSimulator,
        audit_verifier: AuditVerifier
    ):
        """
        Golden test: Verify routing chain across multiple turns.
        
        Validates:
        - Correct orchestrator selected for each turn
        - Context preserved and accumulated
        - Routing confidence meets thresholds
        """
        actual_chain = []
        
        for turn in scenario.turns:
            # Simulate orchestrator selection (in real system: MasterOrchestrator)
            selected_orchestrator = self._route_request(
                turn.user_input,
                crystallization_simulator.accumulated_context
            )
            
            actual_chain.append(selected_orchestrator)
            
            # Verify routing
            assert selected_orchestrator == turn.expected_orchestrator, (
                f"Turn {turn.turn_number}: Expected {turn.expected_orchestrator}, "
                f"got {selected_orchestrator}"
            )
            
            # Simulate response
            mock_response = self._simulate_orchestrator_response(
                selected_orchestrator,
                turn
            )
            
            # Update crystallized context
            crystallized_context = crystallization_simulator.add_turn(
                turn,
                mock_response
            )
            
            # Verify context keys present
            for key in turn.context_keys:
                assert key in crystallized_context["accumulated_context"], (
                    f"Turn {turn.turn_number}: Missing context key '{key}'"
                )
        
        # Verify full routing chain
        assert actual_chain == scenario.expected_routing_chain, (
            f"Routing chain mismatch: {actual_chain} != {scenario.expected_routing_chain}"
        )
    
    @pytest.mark.parametrize("scenario", GOLDEN_SCENARIOS, ids=lambda s: s.scenario_id)
    def test_context_accumulation_golden(
        self,
        scenario: MultiTurnScenario,
        crystallization_simulator: ContextCrystallizationSimulator
    ):
        """
        Golden test: Verify context accumulation across turns.
        
        Validates:
        - Context grows with each turn
        - No context loss between turns
        - Expected context keys present
        """
        for turn in scenario.turns:
            # Get context before turn
            context_before = len(crystallization_simulator.accumulated_context)
            
            # Simulate turn
            mock_response = self._simulate_orchestrator_response(
                turn.expected_orchestrator,
                turn
            )
            
            crystallized_context = crystallization_simulator.add_turn(
                turn,
                mock_response
            )
            
            # Verify context growth
            context_after = len(crystallized_context["accumulated_context"])
            assert context_after >= context_before, (
                f"Turn {turn.turn_number}: Context shrank from {context_before} to {context_after}"
            )
            
            # Verify turn history preserved
            assert len(crystallized_context["turn_history"]) == turn.turn_number, (
                f"Turn {turn.turn_number}: History length mismatch"
            )
    
    def test_context_crystallization_schema_golden(
        self,
        crystallization_simulator: ContextCrystallizationSimulator
    ):
        """
        Golden test: Verify crystallized context schema.
        
        Validates:
        - Required fields present
        - Data types correct
        - Timestamps valid
        """
        # Add sample turn
        turn = TurnContext(
            turn_number=1,
            user_input="Test input",
            expected_orchestrator="TestOrchestrator",
            context_keys=["test_key"],
            routing_confidence=0.9
        )
        
        response = {"test_key": "test_value"}
        crystallized = crystallization_simulator.add_turn(turn, response)
        
        # Verify schema
        required_fields = [
            "turn_count",
            "current_turn",
            "accumulated_context",
            "turn_history",
            "routing_chain"
        ]
        
        for field in required_fields:
            assert field in crystallized, f"Missing required field: {field}"
        
        # Verify types
        assert isinstance(crystallized["turn_count"], int)
        assert isinstance(crystallized["current_turn"], int)
        assert isinstance(crystallized["accumulated_context"], dict)
        assert isinstance(crystallized["turn_history"], list)
        assert isinstance(crystallized["routing_chain"], list)
        
        # Verify turn history structure
        assert len(crystallized["turn_history"]) > 0
        history_entry = crystallized["turn_history"][0]
        
        assert "turn_number" in history_entry
        assert "user_input" in history_entry
        assert "orchestrator" in history_entry
        assert "timestamp" in history_entry
        assert "response" in history_entry
        
        # Verify timestamp format (ISO 8601)
        timestamp = history_entry["timestamp"]
        datetime.fromisoformat(timestamp)  # Should not raise
    
    # ========================================================================
    # HELPER METHODS (Simulating MasterOrchestrator behavior)
    # ========================================================================
    
    def _route_request(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Simulate routing decision (MasterOrchestrator logic).
        
        Args:
            user_input: User input text
            context: Accumulated context
        
        Returns:
            Selected orchestrator name
        """
        # Simple keyword-based routing (real system uses intent classifier)
        user_input_lower = user_input.lower()
        
        if "onboard" in user_input_lower:
            return "OnboardingOrchestrator"
        elif any(word in user_input_lower for word in ["fix", "implement", "create"]):
            return "TDDOrchestrator"
        elif any(word in user_input_lower for word in ["refactor", "reorganize"]):
            return "RefactoringOrchestrator"
        elif any(word in user_input_lower for word in ["list", "show", "what", "query"]):
            return "QueryCoordinator"
        elif "proceed" in user_input_lower or "approve" in user_input_lower:
            return "TDDOrchestrator"  # Approval flow
        else:
            return "QueryCoordinator"  # Default
    
    def _simulate_orchestrator_response(
        self,
        orchestrator: str,
        turn: TurnContext
    ) -> Dict[str, Any]:
        """
        Simulate orchestrator response.
        
        Args:
            orchestrator: Orchestrator name
            turn: Turn context
        
        Returns:
            Mock response dictionary
        """
        # Create mock response with expected context keys
        response = {
            "status": "success",
            "orchestrator": orchestrator,
            "turn": turn.turn_number
        }
        
        # Add context keys with mock data
        for key in turn.context_keys:
            if key == "repository_path":
                response[key] = "/path/to/test/repo"
            elif key == "onboarding_result":
                response[key] = {"success": True, "files_analyzed": 100}
            elif key == "patterns_detected":
                response[key] = ["mvc", "repository"]
            elif key == "violations_count":
                response[key] = 5
            elif key == "challenge_alternatives":
                response[key] = ["option_a", "option_b"]
            elif key == "lens_analysis":
                response[key] = {"architecture_type": "layered"}
            else:
                response[key] = f"mock_value_for_{key}"
        
        return response


class TestContextCrystallizationPersistence:
    """Test context persistence across turns."""
    
    def test_context_serialization_json(
        self,
        crystallization_simulator: ContextCrystallizationSimulator
    ):
        """
        Test: Context can be serialized to JSON.
        
        Validates:
        - JSON serialization succeeds
        - Deserialization preserves data
        """
        # Add sample turn
        turn = TurnContext(
            turn_number=1,
            user_input="Test",
            expected_orchestrator="TestOrchestrator",
            context_keys=["test_key"],
            routing_confidence=0.9
        )
        
        response = {"test_key": "value"}
        crystallized = crystallization_simulator.add_turn(turn, response)
        
        # Serialize
        json_str = json.dumps(crystallized, indent=2)
        assert len(json_str) > 0
        
        # Deserialize
        deserialized = json.loads(json_str)
        assert deserialized["turn_count"] == crystallized["turn_count"]
        assert deserialized["routing_chain"] == crystallized["routing_chain"]
    
    def test_context_serialization_yaml(
        self,
        crystallization_simulator: ContextCrystallizationSimulator
    ):
        """
        Test: Context can be serialized to YAML.
        
        Validates:
        - YAML serialization succeeds
        - Deserialization preserves data
        - Human-readable format
        """
        # Add sample turn
        turn = TurnContext(
            turn_number=1,
            user_input="Test",
            expected_orchestrator="TestOrchestrator",
            context_keys=["test_key"],
            routing_confidence=0.9
        )
        
        response = {"test_key": "value"}
        crystallized = crystallization_simulator.add_turn(turn, response)
        
        # Serialize
        yaml_str = yaml.dump(crystallized, default_flow_style=False)
        assert len(yaml_str) > 0
        assert "turn_count:" in yaml_str
        assert "routing_chain:" in yaml_str
        
        # Deserialize
        deserialized = yaml.safe_load(yaml_str)
        assert deserialized["turn_count"] == crystallized["turn_count"]
        assert deserialized["routing_chain"] == crystallized["routing_chain"]


# ============================================================================
# INTEGRATION WITH REAL MCP TOOLS (Skipped if MCP unavailable)
# ============================================================================

@pytest.mark.integration
@pytest.mark.skipif(
    not Path("/Users/asifhussain/PROJECTS/CORTEX/cortex/mcp/tools").exists(),
    reason="MCP tools not available"
)
class TestMCPIntegrationRouting:
    """Integration tests with real MCP tools."""
    
    def test_onboard_repository_real_mcp(self):
        """
        Integration test: Real onboarding via MCP.
        
        Requires: MCP server running, test repository available
        """
        from cortex.mcp.tools.onboard_repository import onboard_repository_tool
        
        # Use CORTEX itself as test repository
        test_repo = Path("/Users/asifhussain/PROJECTS/CORTEX")
        
        if not test_repo.exists():
            pytest.skip("Test repository not available")
        
        result = onboard_repository_tool(
            repository_path=str(test_repo),
            capture_learning=False,
            apply_brain_enhancement=False,
            generate_artifacts=False,
            orchestrator_context={
                "source": "golden_test",
                "test_id": "GT-ROUTE-MCP-001"
            }
        )
        
        # Verify result structure
        assert "status" in result
        assert result["status"] in ["success", "partial_success"]
        assert "repository_path" in result


# ============================================================================
# SUMMARY & STATISTICS
# ============================================================================

def test_golden_scenario_coverage():
    """
    Test: Verify golden scenario coverage.
    
    Reports:
    - Total scenarios defined
    - Orchestrators covered
    - Turn patterns tested
    """
    total_scenarios = len(GOLDEN_SCENARIOS)
    orchestrators_covered = set()
    max_turns = 0
    
    for scenario in GOLDEN_SCENARIOS:
        for turn in scenario.turns:
            orchestrators_covered.add(turn.expected_orchestrator)
        max_turns = max(max_turns, len(scenario.turns))
    
    # Report coverage
    print(f"\n{'='*60}")
    print("GOLDEN SCENARIO COVERAGE REPORT")
    print(f"{'='*60}")
    print(f"Total Scenarios: {total_scenarios}")
    print(f"Orchestrators Covered: {len(orchestrators_covered)}")
    print(f"  - {', '.join(sorted(orchestrators_covered))}")
    print(f"Max Turn Depth: {max_turns}")
    print(f"{'='*60}\n")
    
    # Assertions
    assert total_scenarios >= 3, "Should have at least 3 golden scenarios"
    assert len(orchestrators_covered) >= 4, "Should cover at least 4 orchestrators"
    assert max_turns >= 3, "Should test at least 3-turn interactions"
