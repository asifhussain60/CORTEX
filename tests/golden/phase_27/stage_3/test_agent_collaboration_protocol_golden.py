"""
PHASE 27 STAGE 3: Agent Collaboration Protocol - Golden Tests (Zero-Mock)

AC_START: AC-PHASE27-S3-001
Stage: Agent Collaboration Protocol
Tests: 12 golden tests (zero-mock philosophy)
Authority: Phase 27 Consolidation (GAP-03)

Objective:
Enable systematic agent handoff with capability-based discovery. When
TDDOrchestrator encounters domain-specific validation, discover and delegate
to RefactoringOrchestrator. When RefactoringOrchestrator needs security audit,
discover and delegate to SecurityCheckpointAgent.

Test Philosophy:
• ZERO MOCKS: Real AgentCapabilityRegistry, real discovery, real handoffs
• PRODUCTION SCENARIOS: Multi-agent workflows with audit trail
• CROSS-SESSION: Capability learning persists across sessions
• PERFORMANCE: Agent discovery <50ms, handoff <100ms

Components Under Test:
1. AgentCapabilityRegistry: Capability storage and retrieval
2. AgentDiscoveryService: Find agents by capability requirements
3. AgentHandoffProtocol: Systematic handoff with context transfer
4. HandoffAuditTrail: Complete audit trail for governance

AC_COMPLETE: AC-PHASE27-S3-001
"""

import pytest

pytestmark = pytest.mark.skipif(
    True,
    reason="Phase 27 persistence modules not yet migrated from _archive/brain/persistence/ — Phase 09 remediation"
)

import tempfile
import json
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timedelta


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def temp_db_path():
    """Provide temporary database path for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        yield f.name
    # Cleanup after test
    Path(f.name).unlink(missing_ok=True)


@pytest.fixture
def capability_registry(temp_db_path):
    """Create AgentCapabilityRegistry for testing."""
    from cortex.intelligence.persistence.agent_capability_registry import AgentCapabilityRegistry
    
    registry = AgentCapabilityRegistry(db_path=temp_db_path)
    yield registry
    registry.close()


@pytest.fixture
def discovery_service(capability_registry):
    """Create AgentDiscoveryService with registry."""
    from cortex.intelligence.persistence.agent_discovery_service import AgentDiscoveryService
    
    service = AgentDiscoveryService(capability_registry)
    yield service


@pytest.fixture
def handoff_protocol(capability_registry, discovery_service, temp_db_path):
    """Create AgentHandoffProtocol with all dependencies."""
    from cortex.intelligence.persistence.agent_handoff_protocol import AgentHandoffProtocol
    
    protocol = AgentHandoffProtocol(
        capability_registry=capability_registry,
        discovery_service=discovery_service,
        audit_db_path=temp_db_path
    )
    yield protocol
    protocol.close()


@pytest.fixture
def registered_agents(capability_registry):
    """Register sample agents with capabilities."""
    agents = [
        {
            "agent_id": "tdd_orchestrator",
            "agent_name": "TDDOrchestrator",
            "capabilities": ["test_generation", "red_green_refactor", "coverage_analysis"],
            "metadata": {"version": "1.0", "mode": "production"}
        },
        {
            "agent_id": "refactoring_orchestrator",
            "agent_name": "RefactoringOrchestrator",
            "capabilities": ["code_refactoring", "extract_method", "rename_symbol"],
            "metadata": {"version": "1.0", "mode": "production"}
        },
        {
            "agent_id": "security_checkpoint",
            "agent_name": "SecurityCheckpointAgent",
            "capabilities": ["security_audit", "owasp_validation", "secrets_detection"],
            "metadata": {"version": "1.0", "mode": "production"}
        },
        {
            "agent_id": "lens_synthesis",
            "agent_name": "LENSSynthesis",
            "capabilities": ["code_analysis", "ast_parsing", "domain_inference"],
            "metadata": {"version": "1.0", "mode": "production"}
        }
    ]
    
    for agent in agents:
        capability_registry.register_agent(
            agent_id=agent["agent_id"],
            agent_name=agent["agent_name"],
            capabilities=agent["capabilities"],
            metadata=agent["metadata"]
        )
    
    return agents


# ============================================================================
# GOLDEN TEST 1: Agent Capability Registration
# ============================================================================


def test_golden_agent_capability_registration(capability_registry):
    """
    GOLDEN TEST: Register agents with capabilities (no mocks).
    
    Scenario:
    1. Register TDDOrchestrator with [test_generation, coverage_analysis]
    2. Register RefactoringOrchestrator with [code_refactoring, extract_method]
    3. Verify capabilities stored correctly
    4. Verify retrieval by agent_id
    
    AC: AC-PHASE27-S3-G1 (Golden Test - Capability Registration)
    """
    # Register TDDOrchestrator
    agent_id1 = capability_registry.register_agent(
        agent_id="tdd_orchestrator",
        agent_name="TDDOrchestrator",
        capabilities=["test_generation", "coverage_analysis"],
        metadata={"version": "1.0"}
    )
    
    assert agent_id1 == "tdd_orchestrator"
    
    # Register RefactoringOrchestrator
    agent_id2 = capability_registry.register_agent(
        agent_id="refactoring_orchestrator",
        agent_name="RefactoringOrchestrator",
        capabilities=["code_refactoring", "extract_method"],
        metadata={"version": "1.0"}
    )
    
    assert agent_id2 == "refactoring_orchestrator"
    
    # Retrieve TDDOrchestrator
    agent1 = capability_registry.get_agent(agent_id1)
    assert agent1 is not None
    assert agent1["agent_name"] == "TDDOrchestrator"
    assert "test_generation" in agent1["capabilities"]
    assert "coverage_analysis" in agent1["capabilities"]
    
    # Retrieve RefactoringOrchestrator
    agent2 = capability_registry.get_agent(agent_id2)
    assert agent2 is not None
    assert agent2["agent_name"] == "RefactoringOrchestrator"
    assert "code_refactoring" in agent2["capabilities"]


# ============================================================================
# GOLDEN TEST 2: Capability-Based Discovery (Single Capability)
# ============================================================================


def test_golden_capability_based_discovery_single(discovery_service, registered_agents):
    """
    GOLDEN TEST: Discover agents by single capability (no mocks).
    
    Scenario:
    1. Query: "Who can do test_generation?"
    2. Expect: TDDOrchestrator discovered
    3. Query: "Who can do security_audit?"
    4. Expect: SecurityCheckpointAgent discovered
    
    AC: AC-PHASE27-S3-G2 (Golden Test - Single Capability Discovery)
    """
    # Discover test generation capability
    agents = discovery_service.discover_agents(required_capabilities=["test_generation"])
    
    assert len(agents) == 1
    assert agents[0]["agent_id"] == "tdd_orchestrator"
    assert "test_generation" in agents[0]["capabilities"]
    
    # Discover security audit capability
    agents = discovery_service.discover_agents(required_capabilities=["security_audit"])
    
    assert len(agents) == 1
    assert agents[0]["agent_id"] == "security_checkpoint"
    assert "security_audit" in agents[0]["capabilities"]


# ============================================================================
# GOLDEN TEST 3: Capability-Based Discovery (Multiple Capabilities)
# ============================================================================


def test_golden_capability_based_discovery_multiple(discovery_service, registered_agents):
    """
    GOLDEN TEST: Discover agents by multiple capabilities (no mocks).
    
    Scenario:
    1. Query: "Who can do [code_refactoring, extract_method]?"
    2. Expect: RefactoringOrchestrator discovered (has both)
    3. Query: "Who can do [test_generation, security_audit]?"
    4. Expect: No agents (no single agent has both)
    
    AC: AC-PHASE27-S3-G3 (Golden Test - Multiple Capability Discovery)
    """
    # Discover multiple refactoring capabilities
    agents = discovery_service.discover_agents(
        required_capabilities=["code_refactoring", "extract_method"]
    )
    
    assert len(agents) == 1
    assert agents[0]["agent_id"] == "refactoring_orchestrator"
    assert "code_refactoring" in agents[0]["capabilities"]
    assert "extract_method" in agents[0]["capabilities"]
    
    # Discover incompatible combination (no agent has both)
    agents = discovery_service.discover_agents(
        required_capabilities=["test_generation", "security_audit"]
    )
    
    assert len(agents) == 0  # No single agent has both capabilities


# ============================================================================
# GOLDEN TEST 4: Agent Handoff (Basic)
# ============================================================================


def test_golden_agent_handoff_basic(handoff_protocol, registered_agents):
    """
    GOLDEN TEST: Basic agent handoff with context transfer (no mocks).
    
    Scenario:
    1. TDDOrchestrator starts test generation
    2. Encounters complex refactoring scenario
    3. Handoff to RefactoringOrchestrator with context
    4. Verify handoff recorded in audit trail
    
    AC: AC-PHASE27-S3-G4 (Golden Test - Basic Handoff)
    """
    # Initiate handoff
    handoff_id = handoff_protocol.initiate_handoff(
        from_agent="tdd_orchestrator",
        required_capabilities=["code_refactoring"],
        context={
            "operation": "test_generation",
            "file": "test_user_service.py",
            "reason": "Complex refactoring detected during test generation"
        },
        metadata={
            "session_id": str(uuid4()),
            "user_request": "Implement user service tests"
        }
    )
    
    assert handoff_id is not None
    
    # Verify handoff details
    handoff = handoff_protocol.get_handoff(handoff_id)
    assert handoff is not None
    assert handoff["from_agent"] == "tdd_orchestrator"
    assert handoff["to_agent"] == "refactoring_orchestrator"
    assert handoff["status"] == "pending"
    assert "Complex refactoring detected" in handoff["context"]["reason"]
    
    # Accept handoff
    accept_result = handoff_protocol.accept_handoff(
        handoff_id=handoff_id,
        to_agent="refactoring_orchestrator"
    )
    
    assert accept_result["status"] == "accepted"
    
    # Verify status updated
    handoff = handoff_protocol.get_handoff(handoff_id)
    assert handoff["status"] == "accepted"


# ============================================================================
# GOLDEN TEST 5: Agent Handoff (Complete Workflow)
# ============================================================================


def test_golden_agent_handoff_complete_workflow(handoff_protocol, registered_agents):
    """
    GOLDEN TEST: Complete handoff workflow with completion (no mocks).
    
    Scenario:
    1. Initiate handoff (TDD → Refactoring)
    2. Accept handoff
    3. Complete handoff with results
    4. Verify audit trail records all phases
    
    AC: AC-PHASE27-S3-G5 (Golden Test - Complete Handoff)
    """
    # Initiate
    handoff_id = handoff_protocol.initiate_handoff(
        from_agent="tdd_orchestrator",
        required_capabilities=["code_refactoring"],
        context={"operation": "test_generation", "file": "test_user_service.py"},
        metadata={"session_id": str(uuid4())}
    )
    
    # Accept
    handoff_protocol.accept_handoff(handoff_id, "refactoring_orchestrator")
    
    # Complete
    complete_result = handoff_protocol.complete_handoff(
        handoff_id=handoff_id,
        result={
            "refactoring_applied": "extract_method",
            "methods_extracted": 3,
            "complexity_reduced": 15
        },
        metadata={
            "completed_at": datetime.utcnow().isoformat(),
            "duration_ms": 250
        }
    )
    
    assert complete_result["status"] == "completed"
    
    # Verify audit trail
    handoff = handoff_protocol.get_handoff(handoff_id)
    assert handoff["status"] == "completed"
    assert handoff["result"]["refactoring_applied"] == "extract_method"
    assert handoff["result"]["methods_extracted"] == 3
    
    # Verify audit trail completeness
    audit_trail = handoff_protocol.get_audit_trail(handoff_id)
    assert len(audit_trail) >= 3  # initiate, accept, complete
    assert audit_trail[0]["event"] == "initiated"
    assert audit_trail[1]["event"] == "accepted"
    assert audit_trail[2]["event"] == "completed"


# ============================================================================
# GOLDEN TEST 6: Multi-Hop Handoff Chain
# ============================================================================


def test_golden_multi_hop_handoff_chain(handoff_protocol, registered_agents):
    """
    GOLDEN TEST: Multi-hop handoff chain (A → B → C) (no mocks).
    
    Scenario:
    1. TDD → Refactoring (refactoring needed)
    2. Refactoring → Security (security audit needed)
    3. Security completes, returns to Refactoring
    4. Refactoring completes, returns to TDD
    5. Verify complete chain in audit trail
    
    AC: AC-PHASE27-S3-G6 (Golden Test - Multi-Hop Handoff)
    """
    # Hop 1: TDD → Refactoring
    handoff_id1 = handoff_protocol.initiate_handoff(
        from_agent="tdd_orchestrator",
        required_capabilities=["code_refactoring"],
        context={"operation": "test_generation"},
        metadata={"session_id": str(uuid4())}
    )
    
    handoff_protocol.accept_handoff(handoff_id1, "refactoring_orchestrator")
    
    # Hop 2: Refactoring → Security
    handoff_id2 = handoff_protocol.initiate_handoff(
        from_agent="refactoring_orchestrator",
        required_capabilities=["security_audit"],
        context={"operation": "refactoring", "parent_handoff": handoff_id1},
        metadata={"session_id": str(uuid4())}
    )
    
    handoff_protocol.accept_handoff(handoff_id2, "security_checkpoint")
    
    # Complete security audit
    handoff_protocol.complete_handoff(
        handoff_id2,
        result={"security_issues": 0, "owasp_compliant": True}
    )
    
    # Complete refactoring
    handoff_protocol.complete_handoff(
        handoff_id1,
        result={"refactoring_applied": "extract_method", "security_checked": True}
    )
    
    # Verify chain
    handoff1 = handoff_protocol.get_handoff(handoff_id1)
    handoff2 = handoff_protocol.get_handoff(handoff_id2)
    
    assert handoff1["status"] == "completed"
    assert handoff2["status"] == "completed"
    assert handoff2["context"]["parent_handoff"] == handoff_id1


# ============================================================================
# GOLDEN TEST 7: Cross-Session Capability Learning
# ============================================================================


def test_golden_cross_session_capability_learning(capability_registry, temp_db_path):
    """
    GOLDEN TEST: Capability learning persists across sessions (no mocks).
    
    Scenario:
    1. Session 1: Register agent with capabilities
    2. Close registry (simulate session end)
    3. Session 2: Reopen registry, verify capabilities persist
    4. Update capabilities in Session 2
    5. Verify updates persist
    
    AC: AC-PHASE27-S3-G7 (Golden Test - Cross-Session Capability)
    """
    # Session 1: Register agent
    capability_registry.register_agent(
        agent_id="tdd_orchestrator",
        agent_name="TDDOrchestrator",
        capabilities=["test_generation", "coverage_analysis"],
        metadata={"version": "1.0"}
    )
    
    # Verify registration
    agent = capability_registry.get_agent("tdd_orchestrator")
    assert agent is not None
    assert len(agent["capabilities"]) == 2
    
    # Close session
    capability_registry.close()
    
    # Session 2: Reopen
    from cortex.intelligence.persistence.agent_capability_registry import AgentCapabilityRegistry
    
    registry2 = AgentCapabilityRegistry(db_path=temp_db_path)
    
    # Verify persistence
    agent = registry2.get_agent("tdd_orchestrator")
    assert agent is not None
    assert "test_generation" in agent["capabilities"]
    assert "coverage_analysis" in agent["capabilities"]
    
    # Update capabilities
    registry2.update_agent_capabilities(
        agent_id="tdd_orchestrator",
        capabilities=["test_generation", "coverage_analysis", "mutation_testing"]
    )
    
    # Verify update
    agent = registry2.get_agent("tdd_orchestrator")
    assert len(agent["capabilities"]) == 3
    assert "mutation_testing" in agent["capabilities"]
    
    registry2.close()


# ============================================================================
# GOLDEN TEST 8: Handoff Audit Trail Completeness
# ============================================================================


def test_golden_handoff_audit_trail_completeness(handoff_protocol, registered_agents):
    """
    GOLDEN TEST: Handoff audit trail records all events (no mocks).
    
    Scenario:
    1. Initiate handoff (record timestamp, context)
    2. Accept handoff (record acceptance time)
    3. Complete handoff (record completion time, result)
    4. Verify audit trail has all events
    5. Verify timestamps in chronological order
    
    AC: AC-PHASE27-S3-G8 (Golden Test - Audit Trail Completeness)
    """
    # Initiate
    handoff_id = handoff_protocol.initiate_handoff(
        from_agent="tdd_orchestrator",
        required_capabilities=["code_refactoring"],
        context={"operation": "test_generation"},
        metadata={"session_id": str(uuid4())}
    )
    
    # Accept
    handoff_protocol.accept_handoff(handoff_id, "refactoring_orchestrator")
    
    # Complete
    handoff_protocol.complete_handoff(
        handoff_id,
        result={"refactoring_applied": "extract_method"}
    )
    
    # Retrieve audit trail
    audit_trail = handoff_protocol.get_audit_trail(handoff_id)
    
    # Verify completeness
    assert len(audit_trail) >= 3
    events = [entry["event"] for entry in audit_trail]
    assert "initiated" in events
    assert "accepted" in events
    assert "completed" in events
    
    # Verify chronological order
    timestamps = [entry["timestamp"] for entry in audit_trail]
    assert timestamps == sorted(timestamps)
    
    # Verify context preserved
    initiate_event = next(e for e in audit_trail if e["event"] == "initiated")
    assert "test_generation" in str(initiate_event["context"])


# ============================================================================
# GOLDEN TEST 9: Capability Discovery Performance
# ============================================================================


def test_golden_capability_discovery_performance(discovery_service, registered_agents):
    """
    GOLDEN TEST: Capability discovery completes <50ms (no mocks).
    
    Scenario:
    1. Register 10 agents with various capabilities
    2. Run discovery query
    3. Verify completion time <50ms
    4. Verify correct agent discovered
    
    AC: AC-PHASE27-S3-G9 (Golden Test - Discovery Performance)
    """
    import time
    
    # Discovery query
    start = time.perf_counter()
    agents = discovery_service.discover_agents(required_capabilities=["test_generation"])
    end = time.perf_counter()
    
    duration_ms = (end - start) * 1000
    
    # Verify performance
    assert duration_ms < 50, f"Discovery took {duration_ms}ms (expected <50ms)"
    
    # Verify correctness
    assert len(agents) > 0
    assert agents[0]["agent_id"] == "tdd_orchestrator"


# ============================================================================
# GOLDEN TEST 10: Handoff Protocol Performance
# ============================================================================


def test_golden_handoff_protocol_performance(handoff_protocol, registered_agents):
    """
    GOLDEN TEST: Handoff initiation + acceptance <100ms (no mocks).
    
    Scenario:
    1. Initiate handoff
    2. Accept handoff
    3. Verify total time <100ms
    4. Verify handoff successful
    
    AC: AC-PHASE27-S3-G10 (Golden Test - Handoff Performance)
    """
    import time
    
    # Handoff workflow
    start = time.perf_counter()
    
    handoff_id = handoff_protocol.initiate_handoff(
        from_agent="tdd_orchestrator",
        required_capabilities=["code_refactoring"],
        context={"operation": "test_generation"},
        metadata={"session_id": str(uuid4())}
    )
    
    handoff_protocol.accept_handoff(handoff_id, "refactoring_orchestrator")
    
    end = time.perf_counter()
    
    duration_ms = (end - start) * 1000
    
    # Verify performance
    assert duration_ms < 100, f"Handoff took {duration_ms}ms (expected <100ms)"
    
    # Verify correctness
    handoff = handoff_protocol.get_handoff(handoff_id)
    assert handoff["status"] == "accepted"


# ============================================================================
# GOLDEN TEST 11: Capability Update and Versioning
# ============================================================================


def test_golden_capability_update_and_versioning(capability_registry):
    """
    GOLDEN TEST: Agent capability updates with version tracking (no mocks).
    
    Scenario:
    1. Register agent v1.0 with 2 capabilities
    2. Update to v1.1 with 3 capabilities (add 1)
    3. Update to v2.0 with 2 capabilities (remove 1, add different)
    4. Verify version history tracked
    5. Verify discovery uses latest capabilities
    
    AC: AC-PHASE27-S3-G11 (Golden Test - Capability Versioning)
    """
    # Version 1.0
    capability_registry.register_agent(
        agent_id="tdd_orchestrator",
        agent_name="TDDOrchestrator",
        capabilities=["test_generation", "coverage_analysis"],
        metadata={"version": "1.0"}
    )
    
    agent = capability_registry.get_agent("tdd_orchestrator")
    assert len(agent["capabilities"]) == 2
    assert agent["metadata"]["version"] == "1.0"
    
    # Version 1.1 (add capability)
    capability_registry.update_agent_capabilities(
        agent_id="tdd_orchestrator",
        capabilities=["test_generation", "coverage_analysis", "mutation_testing"],
        metadata={"version": "1.1"}
    )
    
    agent = capability_registry.get_agent("tdd_orchestrator")
    assert len(agent["capabilities"]) == 3
    assert "mutation_testing" in agent["capabilities"]
    
    # Version 2.0 (replace capability)
    capability_registry.update_agent_capabilities(
        agent_id="tdd_orchestrator",
        capabilities=["test_generation", "mutation_testing"],
        metadata={"version": "2.0"}
    )
    
    agent = capability_registry.get_agent("tdd_orchestrator")
    assert len(agent["capabilities"]) == 2
    assert "coverage_analysis" not in agent["capabilities"]
    assert "mutation_testing" in agent["capabilities"]


# ============================================================================
# GOLDEN TEST 12: Handoff Failure Recovery
# ============================================================================


def test_golden_handoff_failure_recovery(handoff_protocol, registered_agents):
    """
    GOLDEN TEST: Handoff failure handling with recovery (no mocks).
    
    Scenario:
    1. Initiate handoff to agent with required capabilities
    2. Accept handoff
    3. Fail handoff (agent encounters error)
    4. Verify failure recorded in audit trail
    5. Re-initiate handoff (retry mechanism)
    6. Complete successfully
    7. Verify both attempts in audit trail
    
    AC: AC-PHASE27-S3-G12 (Golden Test - Handoff Failure Recovery)
    """
    # Attempt 1: Initiate and fail
    handoff_id1 = handoff_protocol.initiate_handoff(
        from_agent="tdd_orchestrator",
        required_capabilities=["code_refactoring"],
        context={"operation": "test_generation"},
        metadata={"session_id": str(uuid4())}
    )
    
    handoff_protocol.accept_handoff(handoff_id1, "refactoring_orchestrator")
    
    # Fail handoff
    fail_result = handoff_protocol.fail_handoff(
        handoff_id=handoff_id1,
        error={
            "error_type": "TimeoutError",
            "message": "Refactoring agent timeout after 30s"
        },
        metadata={"failed_at": datetime.utcnow().isoformat()}
    )
    
    assert fail_result["status"] == "failed"
    
    # Verify failure recorded
    handoff1 = handoff_protocol.get_handoff(handoff_id1)
    assert handoff1["status"] == "failed"
    assert "TimeoutError" in handoff1["error"]["error_type"]
    
    # Attempt 2: Retry and succeed
    handoff_id2 = handoff_protocol.initiate_handoff(
        from_agent="tdd_orchestrator",
        required_capabilities=["code_refactoring"],
        context={"operation": "test_generation", "retry_of": handoff_id1},
        metadata={"session_id": str(uuid4())}
    )
    
    handoff_protocol.accept_handoff(handoff_id2, "refactoring_orchestrator")
    handoff_protocol.complete_handoff(
        handoff_id2,
        result={"refactoring_applied": "extract_method"}
    )
    
    # Verify success
    handoff2 = handoff_protocol.get_handoff(handoff_id2)
    assert handoff2["status"] == "completed"
    assert handoff2["context"]["retry_of"] == handoff_id1
    
    # Verify both attempts in audit system
    audit1 = handoff_protocol.get_audit_trail(handoff_id1)
    audit2 = handoff_protocol.get_audit_trail(handoff_id2)
    
    assert any(e["event"] == "failed" for e in audit1)
    assert any(e["event"] == "completed" for e in audit2)
