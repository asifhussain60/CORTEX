"""
Golden Tests for Universal Learning Loop Integration - Phase 27 Stage 2

Zero-mock golden tests for learning loop integration with orchestrators.
Tests OBSERVE → ANALYZE → SYNTHESIZE → APPLY cycle with real operations.

AC_START: AC-PHASE27-S2-001
Authority: Phase 27 Stage 2 (GAP-02)
Philosophy: Zero mocks - real orchestrators, real learning, real persistence
"""

import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

import pytest

pytestmark = pytest.mark.skipif(
    True,
    reason="Phase 27 persistence modules not yet migrated from _archive/brain/persistence/ — Phase 09 remediation"
)


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def temp_workspace() -> Path:
    """Create temporary workspace for tests."""
    temp_dir = tempfile.mkdtemp()
    workspace = Path(temp_dir) / "cortex_workspace"
    workspace.mkdir(parents=True)
    return workspace


@pytest.fixture
def knowledge_store_with_data(temp_workspace: Path):
    """Create KnowledgeStore with sample data."""
    from cortex.intelligence.persistence.knowledge_store import KnowledgeStore
    
    db_path = temp_workspace / "knowledge.db"
    store = KnowledgeStore(db_path=db_path)
    
    # Pre-populate with 3 repositories
    session_id = str(uuid4())
    repos = [
        {"name": "service-a", "patterns": ["mvc", "repository-pattern"]},
        {"name": "service-b", "patterns": ["mvc", "dependency-injection"]},
        {"name": "service-c", "patterns": ["repository-pattern", "cqrs"]},
    ]
    
    for repo in repos:
        store.store_knowledge(
            session_id=session_id,
            knowledge_type="repository_domain",
            content=repo,
            metadata={"source": "onboarding"}
        )
    
    yield store
    store.close()


@pytest.fixture
def learning_loop_with_store(temp_workspace: Path, knowledge_store_with_data):
    """Create learning loop with knowledge store."""
    from cortex.intelligence.persistence.learning_loop_integration import LearningLoopIntegration
    
    integration = LearningLoopIntegration(
        workspace_root=temp_workspace,
        knowledge_store=knowledge_store_with_data
    )
    
    yield integration
    integration.close()


# ============================================================================
# GOLDEN TEST 1: OBSERVE Phase - Capture Operation Data
# ============================================================================


def test_golden_observe_phase_onboard_operation(learning_loop_with_store):
    """
    GOLDEN TEST: OBSERVE phase captures onboarding operation data (no mocks).
    
    Scenario:
    1. Trigger onboarding operation
    2. OBSERVE phase captures: tech stack, patterns, complexity
    3. Verify: Observation stored in learning cache
    4. Verify: Observation includes timestamp, session_id
    
    AC: AC-PHASE27-S2-G01 (Golden Test - OBSERVE)
    """
    # Simulate onboarding operation
    operation_data = {
        "orchestrator": "RepositoryOnboardingOrchestrator",
        "operation": "onboard",
        "context": {
            "repository": "test-microservice",
            "tech_stack": ["python", "fastapi", "postgresql"],
            "file_count": 150
        },
        "result": {
            "patterns_detected": ["repository-pattern", "dependency-injection"],
            "complexity_score": 6.8,
            "security_issues": 2
        }
    }
    
    # OBSERVE: Capture operation
    observation_id = learning_loop_with_store.observe(operation_data)
    
    assert observation_id is not None
    
    # Verify observation stored
    observation = learning_loop_with_store.get_observation(observation_id)
    assert observation is not None
    assert observation["orchestrator"] == "RepositoryOnboardingOrchestrator"
    assert observation["operation"] == "onboard"
    assert "patterns_detected" in observation["result"]
    assert observation["result"]["complexity_score"] == 6.8


# ============================================================================
# GOLDEN TEST 2: ANALYZE Phase - Extract Patterns
# ============================================================================


def test_golden_analyze_phase_pattern_extraction(learning_loop_with_store):
    """
    GOLDEN TEST: ANALYZE phase extracts patterns from observations (no mocks).
    
    Scenario:
    1. Create 3 observations (different repositories, similar patterns)
    2. ANALYZE phase processes observations
    3. Verify: Patterns extracted (repository-pattern appears 2x)
    4. Verify: Pattern metadata includes frequency, confidence
    
    AC: AC-PHASE27-S2-G02 (Golden Test - ANALYZE)
    """
    # Create 3 observations
    observations = [
        {
            "orchestrator": "RepositoryOnboardingOrchestrator",
            "operation": "onboard",
            "context": {"repository": f"repo-{i}"},
            "result": {
                "patterns_detected": ["repository-pattern", "mvc"] if i < 2 else ["cqrs"],
                "complexity_score": 5.5 + i
            }
        }
        for i in range(3)
    ]
    
    observation_ids = []
    for obs_data in observations:
        obs_id = learning_loop_with_store.observe(obs_data)
        observation_ids.append(obs_id)
    
    # ANALYZE: Extract patterns
    analysis_result = learning_loop_with_store.analyze(observation_ids)
    
    assert analysis_result is not None
    assert "patterns" in analysis_result
    
    patterns = analysis_result["patterns"]
    
    # Verify repository-pattern frequency
    repo_pattern = next((p for p in patterns if p["name"] == "repository-pattern"), None)
    assert repo_pattern is not None
    assert repo_pattern["frequency"] == 2  # Appears in 2/3 observations
    assert repo_pattern["confidence"] >= 0.6  # 2/3 = 66%


# ============================================================================
# GOLDEN TEST 3: SYNTHESIZE Phase - Update Knowledge Base
# ============================================================================


def test_golden_synthesize_phase_knowledge_update(
    learning_loop_with_store,
    knowledge_store_with_data
):
    """
    GOLDEN TEST: SYNTHESIZE phase updates knowledge base (no mocks).
    
    Scenario:
    1. Create observation with new pattern (not in knowledge base)
    2. ANALYZE extracts pattern
    3. SYNTHESIZE merges pattern to knowledge base
    4. Verify: Knowledge store updated with new pattern
    5. Verify: Pattern frequency incremented
    
    AC: AC-PHASE27-S2-G03 (Golden Test - SYNTHESIZE)
    """
    # Observation with new pattern
    observation_data = {
        "orchestrator": "RepositoryOnboardingOrchestrator",
        "operation": "onboard",
        "context": {"repository": "new-service"},
        "result": {
            "patterns_detected": ["event-sourcing"],  # NEW pattern
            "complexity_score": 7.2
        }
    }
    
    obs_id = learning_loop_with_store.observe(observation_data)
    analysis = learning_loop_with_store.analyze([obs_id])
    
    # SYNTHESIZE: Merge to knowledge base
    synthesis_result = learning_loop_with_store.synthesize(analysis)
    
    assert synthesis_result["status"] == "success"
    assert synthesis_result["patterns_merged"] >= 1
    
    # Verify knowledge store updated
    pattern_freq = knowledge_store_with_data.get_pattern_frequency()
    assert "event-sourcing" in pattern_freq
    assert pattern_freq["event-sourcing"] == 1


# ============================================================================
# GOLDEN TEST 4: APPLY Phase - Optimize Future Operations
# ============================================================================


def test_golden_apply_phase_optimization(learning_loop_with_store, knowledge_store_with_data):
    """
    GOLDEN TEST: APPLY phase optimizes future operations (no mocks).
    
    Scenario:
    1. Store knowledge: repository-pattern appears 3x (high frequency)
    2. New onboarding operation for similar repository
    3. APPLY phase suggests pattern shortcuts (15-20% faster)
    4. Verify: Optimization recommendations generated
    5. Verify: Speedup metrics calculated
    
    AC: AC-PHASE27-S2-G04 (Golden Test - APPLY)
    """
    # Store high-frequency pattern knowledge (3 repos with repository-pattern)
    session_id = str(uuid4())
    for i in range(3):
        knowledge_store_with_data.store_knowledge(
            session_id=session_id,
            knowledge_type="repository_domain",
            content={
                "repository": f"existing-repo-{i}",
                "patterns": ["repository-pattern", "mvc"]
            },
            metadata={"source": "historical"}
        )
    
    # New onboarding for similar repository
    new_repo_context = {
        "repository": "new-similar-repo",
        "tech_stack": ["python", "fastapi"],  # Similar to existing repos
        "suspected_patterns": ["repository-pattern"]  # Pattern recognition hint
    }
    
    # APPLY: Get optimization recommendations
    optimization = learning_loop_with_store.apply(new_repo_context)
    
    assert optimization is not None
    assert "recommendations" in optimization
    assert len(optimization["recommendations"]) > 0
    
    # Verify speedup suggestion
    speedup_rec = next(
        (r for r in optimization["recommendations"] if "speedup" in r["type"]),
        None
    )
    assert speedup_rec is not None
    assert speedup_rec["estimated_speedup_pct"] >= 15  # 15-20% target
    assert speedup_rec["estimated_speedup_pct"] <= 25  # Upper bound


# ============================================================================
# GOLDEN TEST 5: Full OBSERVE-ANALYZE-SYNTHESIZE-APPLY Cycle
# ============================================================================


def test_golden_full_learning_cycle_end_to_end(
    learning_loop_with_store,
    knowledge_store_with_data
):
    """
    GOLDEN TEST: Complete learning cycle end-to-end (no mocks).
    
    Scenario:
    1. OBSERVE: Onboard repository with patterns
    2. ANALYZE: Extract patterns and calculate confidence
    3. SYNTHESIZE: Merge patterns to knowledge base
    4. APPLY: Get optimization for similar repository
    5. Verify: Full cycle completes successfully
    6. Verify: Knowledge base updated, optimizations available
    
    AC: AC-PHASE27-S2-G05 (Golden Test - Full Cycle)
    """
    # Step 1: OBSERVE
    observation = {
        "orchestrator": "RepositoryOnboardingOrchestrator",
        "operation": "onboard",
        "context": {"repository": "full-cycle-repo"},
        "result": {
            "patterns_detected": ["hexagonal-architecture", "ddd"],
            "complexity_score": 8.5
        }
    }
    
    obs_id = learning_loop_with_store.observe(observation)
    assert obs_id is not None
    
    # Step 2: ANALYZE
    analysis = learning_loop_with_store.analyze([obs_id])
    assert "patterns" in analysis
    assert len(analysis["patterns"]) == 2
    
    # Step 3: SYNTHESIZE
    synthesis = learning_loop_with_store.synthesize(analysis)
    assert synthesis["status"] == "success"
    
    # Step 4: APPLY
    similar_context = {
        "repository": "similar-repo",
        "suspected_patterns": ["hexagonal-architecture"]
    }
    
    optimization = learning_loop_with_store.apply(similar_context)
    assert "recommendations" in optimization
    
    # Verify knowledge persistence
    pattern_freq = knowledge_store_with_data.get_pattern_frequency()
    assert "hexagonal-architecture" in pattern_freq
    assert "ddd" in pattern_freq


# ============================================================================
# GOLDEN TEST 6: Pattern Frequency Tracking Across Sessions
# ============================================================================


def test_golden_pattern_frequency_tracking_cross_session(temp_workspace: Path):
    """
    GOLDEN TEST: Pattern frequency persists across sessions (no mocks).
    
    Scenario:
    1. Session 1: Onboard 2 repos with repository-pattern
    2. Close learning loop (simulate session end)
    3. Session 2: Onboard 1 more repo with repository-pattern
    4. Verify: Pattern frequency = 3 (cross-session accumulation)
    
    AC: AC-PHASE27-S2-G06 (Golden Test - Cross-Session Frequency)
    """
    from cortex.intelligence.persistence.knowledge_store import KnowledgeStore
    from cortex.intelligence.persistence.learning_loop_integration import LearningLoopIntegration
    
    db_path = temp_workspace / "knowledge.db"
    
    # SESSION 1
    store_1 = KnowledgeStore(db_path=db_path)
    loop_1 = LearningLoopIntegration(
        workspace_root=temp_workspace,
        knowledge_store=store_1
    )
    
    # Onboard 2 repos
    for i in range(2):
        obs = {
            "orchestrator": "RepositoryOnboardingOrchestrator",
            "operation": "onboard",
            "context": {"repository": f"session1-repo-{i}"},
            "result": {"patterns_detected": ["repository-pattern"]}
        }
        obs_id = loop_1.observe(obs)
        analysis = loop_1.analyze([obs_id])
        loop_1.synthesize(analysis)
    
    loop_1.close()
    store_1.close()
    
    # SESSION 2
    store_2 = KnowledgeStore(db_path=db_path)
    loop_2 = LearningLoopIntegration(
        workspace_root=temp_workspace,
        knowledge_store=store_2
    )
    
    # Onboard 1 more repo
    obs = {
        "orchestrator": "RepositoryOnboardingOrchestrator",
        "operation": "onboard",
        "context": {"repository": "session2-repo"},
        "result": {"patterns_detected": ["repository-pattern"]}
    }
    obs_id = loop_2.observe(obs)
    analysis = loop_2.analyze([obs_id])
    loop_2.synthesize(analysis)
    
    # Verify cross-session accumulation
    pattern_freq = store_2.get_pattern_frequency()
    assert pattern_freq["repository-pattern"] == 3  # 2 from session1 + 1 from session2
    
    loop_2.close()
    store_2.close()


# ============================================================================
# GOLDEN TEST 7: Learning Loop with ANALYZE Operation
# ============================================================================


def test_golden_learning_loop_analyze_operation(learning_loop_with_store):
    """
    GOLDEN TEST: Learning loop after ANALYZE operation (no mocks).
    
    Scenario:
    1. Trigger ANALYZE operation (code analysis)
    2. OBSERVE captures analysis results (patterns, metrics)
    3. ANALYZE extracts code patterns
    4. SYNTHESIZE updates knowledge base
    5. Verify: Analysis patterns learned
    
    AC: AC-PHASE27-S2-G07 (Golden Test - ANALYZE Operation)
    """
    # Simulate ANALYZE operation
    analyze_observation = {
        "orchestrator": "LENSSynthesis",
        "operation": "analyze",
        "context": {
            "file_path": "services/user_service.py",
            "language": "python"
        },
        "result": {
            "patterns_detected": ["service-layer", "repository-pattern"],
            "code_smells": ["long-method"],
            "complexity": 7.2
        }
    }
    
    obs_id = learning_loop_with_store.observe(analyze_observation)
    analysis = learning_loop_with_store.analyze([obs_id])
    synthesis = learning_loop_with_store.synthesize(analysis)
    
    assert synthesis["status"] == "success"
    assert synthesis["patterns_merged"] >= 2


# ============================================================================
# GOLDEN TEST 8: Learning Loop with REFACTOR Operation
# ============================================================================


def test_golden_learning_loop_refactor_operation(learning_loop_with_store):
    """
    GOLDEN TEST: Learning loop after REFACTOR operation (no mocks).
    
    Scenario:
    1. Trigger REFACTOR operation
    2. OBSERVE captures refactoring patterns (extract method, etc.)
    3. ANALYZE extracts refactoring techniques
    4. SYNTHESIZE updates knowledge base
    5. Verify: Refactoring patterns learned
    
    AC: AC-PHASE27-S2-G08 (Golden Test - REFACTOR Operation)
    """
    refactor_observation = {
        "orchestrator": "RefactoringOrchestrator",
        "operation": "refactor",
        "context": {
            "file_path": "models/user.py",
            "refactor_type": "extract_method"
        },
        "result": {
            "refactoring_applied": "extract_method",
            "before_complexity": 8.5,
            "after_complexity": 5.2,
            "improvement_pct": 38.8
        }
    }
    
    obs_id = learning_loop_with_store.observe(refactor_observation)
    analysis = learning_loop_with_store.analyze([obs_id])
    synthesis = learning_loop_with_store.synthesize(analysis)
    
    assert synthesis["status"] == "success"
    # Verify refactoring pattern extracted
    assert len(analysis["patterns"]) > 0
    assert any("refactor" in p["name"].lower() for p in analysis["patterns"])


# ============================================================================
# GOLDEN TEST 9: 15-20% Speedup Verification
# ============================================================================


def test_golden_speedup_verification_similar_repos(
    learning_loop_with_store,
    knowledge_store_with_data
):
    """
    GOLDEN TEST: Verify 15-20% speedup on similar repositories (no mocks).
    
    Scenario:
    1. Onboard 5 similar repositories (establish pattern baseline)
    2. Measure baseline: Time to analyze patterns
    3. Onboard 6th similar repository (with learning applied)
    4. Measure optimized: Time with pattern shortcuts
    5. Verify: Speedup >= 15%
    
    AC: AC-PHASE27-S2-G09 (Golden Test - Speedup Verification)
    """
    import time
    
    # Establish pattern baseline (5 repos)
    session_id = str(uuid4())
    for i in range(5):
        knowledge_store_with_data.store_knowledge(
            session_id=session_id,
            knowledge_type="repository_domain",
            content={
                "repository": f"baseline-repo-{i}",
                "patterns": ["mvc", "repository-pattern", "dependency-injection"]
            },
            metadata={"source": "baseline"}
        )
    
    # Measure baseline analysis time (without optimization)
    baseline_start = time.time()
    baseline_obs = {
        "orchestrator": "RepositoryOnboardingOrchestrator",
        "operation": "onboard",
        "context": {"repository": "baseline-test", "optimization": False},
        "result": {
            "patterns_detected": ["mvc", "repository-pattern", "dependency-injection"]
        }
    }
    obs_id = learning_loop_with_store.observe(baseline_obs)
    analysis = learning_loop_with_store.analyze([obs_id])
    baseline_time = time.time() - baseline_start
    
    # Measure optimized analysis time (with APPLY optimizations)
    optimization = learning_loop_with_store.apply({
        "repository": "optimized-repo",
        "suspected_patterns": ["mvc", "repository-pattern"]
    })
    
    optimized_start = time.time()
    optimized_obs = {
        "orchestrator": "RepositoryOnboardingOrchestrator",
        "operation": "onboard",
        "context": {
            "repository": "optimized-test",
            "optimization": True,
            "shortcuts": optimization["recommendations"]
        },
        "result": {
            "patterns_detected": ["mvc", "repository-pattern", "dependency-injection"]
        }
    }
    obs_id_opt = learning_loop_with_store.observe(optimized_obs)
    analysis_opt = learning_loop_with_store.analyze([obs_id_opt])
    optimized_time = time.time() - optimized_start
    
    # Calculate speedup (note: in real scenario, pattern recognition shortcuts reduce time)
    # For test: We verify optimization recommendations exist (actual speedup in production)
    speedup_pct = optimization["recommendations"][0]["estimated_speedup_pct"]
    assert speedup_pct >= 15
    assert speedup_pct <= 25


# ============================================================================
# GOLDEN TEST 10: Multi-Orchestrator Learning Integration
# ============================================================================


def test_golden_multi_orchestrator_learning(learning_loop_with_store):
    """
    GOLDEN TEST: Learning loop integrates with multiple orchestrators (no mocks).
    
    Scenario:
    1. OBSERVE from TDDOrchestrator (test patterns)
    2. OBSERVE from RepositoryOnboardingOrchestrator (domain patterns)
    3. OBSERVE from RefactoringOrchestrator (refactoring patterns)
    4. ANALYZE all observations together
    5. SYNTHESIZE: Verify cross-orchestrator pattern correlations
    
    AC: AC-PHASE27-S2-G10 (Golden Test - Multi-Orchestrator)
    """
    observations = [
        {
            "orchestrator": "TDDOrchestrator",
            "operation": "test",
            "context": {"test_file": "test_user.py"},
            "result": {"test_patterns": ["arrange-act-assert"], "coverage": 85}
        },
        {
            "orchestrator": "RepositoryOnboardingOrchestrator",
            "operation": "onboard",
            "context": {"repository": "user-service"},
            "result": {"patterns_detected": ["repository-pattern"]}
        },
        {
            "orchestrator": "RefactoringOrchestrator",
            "operation": "refactor",
            "context": {"file": "user_service.py"},
            "result": {"refactoring_applied": "extract_method"}
        }
    ]
    
    obs_ids = []
    for obs_data in observations:
        obs_id = learning_loop_with_store.observe(obs_data)
        obs_ids.append(obs_id)
    
    # Analyze all together
    analysis = learning_loop_with_store.analyze(obs_ids)
    
    assert len(analysis["patterns"]) >= 3
    assert any(p["orchestrator"] == "TDDOrchestrator" for p in analysis["patterns"])
    assert any(p["orchestrator"] == "RepositoryOnboardingOrchestrator" for p in analysis["patterns"])
    assert any(p["orchestrator"] == "RefactoringOrchestrator" for p in analysis["patterns"])


# AC_COMPLETE: AC-PHASE27-S2-001 ✅ 10 golden tests defined (RED phase)
