"""
Performance Regression Tests for CORTEX 2.0

These tests ensure performance doesn't degrade as the system evolves.
Tests fail if operations exceed baseline thresholds established in Phase 6.1.

Baseline Report: cortex-brain/cortex-2.0-design/PHASE-6.1-PERFORMANCE-BASELINE.md
Baseline Date: 2025-11-10
"""

import time
import pytest
from pathlib import Path
from typing import Callable, Tuple
from functools import wraps

# Performance thresholds (from Phase 6.1 baseline)
TIER1_THRESHOLD_MS = 50.0  # Target: ≤50ms, Baseline avg: 0.48ms
TIER2_THRESHOLD_MS = 150.0  # Target: ≤150ms, Baseline avg: 0.72ms
TIER3_THRESHOLD_MS = 500.0  # Target: ≤500ms, Baseline avg: 52.51ms
TIER3_HOTSPOT_THRESHOLD_MS = 300.0  # Hotspot: analyze_file_hotspots at 258ms
OPERATION_THRESHOLD_MS = 5000.0  # Target: <5s, Baseline avg: 1431ms
HELP_THRESHOLD_MS = 1000.0  # Target: <1s, Baseline: 462ms
ENVIRONMENT_SETUP_THRESHOLD_MS = 8000.0  # Target: <8s, Baseline: 3758ms (allows network latency)

# Fixtures
@pytest.fixture
def cortex_root():
    """Return path to CORTEX root directory."""
    return Path(__file__).parent.parent.parent

@pytest.fixture
def tier1_manager(cortex_root):
    """Initialize Tier 1 Conversation Manager."""
    from src.tier1.conversation_manager import ConversationManager
    db_path = cortex_root / "cortex-brain" / "tier1" / "conversations.db"
    cm = ConversationManager(db_path)
    return cm

@pytest.fixture
def tier2_knowledge_graph(cortex_root):
    """Initialize Tier 2 Knowledge Graph."""
    from src.tier2.knowledge_graph import KnowledgeGraph
    kg = KnowledgeGraph()
    return kg

@pytest.fixture
def tier3_context_intelligence(cortex_root):
    """Initialize Tier 3 Context Intelligence."""
    from src.tier3.context_intelligence import ContextIntelligence
    ci = ContextIntelligence(db_path=None)  # Use default path
    return ci

# Utility decorator
def benchmark(func: Callable) -> Callable:
    """Decorator to measure function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = (time.perf_counter() - start) * 1000  # Convert to ms
        return result, duration
    return wrapper

# ============================================================================
# TIER 1 PERFORMANCE TESTS (Working Memory)
# Target: ≤50ms, Baseline avg: 0.48ms
# ============================================================================

@pytest.mark.performance
def test_tier1_get_recent_conversations_performance(tier1_manager):
    """Test: Tier 1 get_recent_conversations(20) performance - Baseline: 0.46ms"""
    @benchmark
    def operation():
        return tier1_manager.get_recent_conversations(limit=20)
    
    result, duration = operation()
    assert duration < TIER1_THRESHOLD_MS, \
        f"Tier 1 get_recent_conversations REGRESSION: {duration:.2f}ms (baseline: 0.46ms, target: ≤{TIER1_THRESHOLD_MS}ms)"
    print(f"✅ Tier 1 get_recent_conversations: {duration:.2f}ms")

@pytest.mark.performance
def test_tier1_get_conversation_by_id_performance(tier1_manager):
    """Test: Tier 1 get_conversation(id) performance - Baseline: 0.64ms"""
    conversations = tier1_manager.get_recent_conversations(limit=1)
    if not conversations:
        pytest.skip("No conversations in database")
    
    conv_id = conversations[0]['conversation_id']
    
    @benchmark
    def operation():
        return tier1_manager.get_conversation(conv_id)
    
    result, duration = operation()
    assert duration < TIER1_THRESHOLD_MS, \
        f"Tier 1 get_conversation REGRESSION: {duration:.2f}ms (baseline: 0.64ms, target: ≤{TIER1_THRESHOLD_MS}ms)"
    print(f"✅ Tier 1 get_conversation: {duration:.2f}ms")

@pytest.mark.performance
def test_tier1_average_performance(tier1_manager):
    """Test: Tier 1 average query performance - Baseline avg: 0.48ms"""
    durations = []
    
    @benchmark
    def op1():
        return tier1_manager.get_recent_conversations(limit=20)
    _, d1 = op1()
    durations.append(d1)
    
    conversations = tier1_manager.get_recent_conversations(limit=1)
    if conversations:
        conv_id = conversations[0]['conversation_id']
        
        @benchmark
        def op2():
            return tier1_manager.get_conversation(conv_id)
        _, d2 = op2()
        durations.append(d2)
    
    avg_duration = sum(durations) / len(durations)
    assert avg_duration < TIER1_THRESHOLD_MS, \
        f"Tier 1 AVERAGE REGRESSION: {avg_duration:.2f}ms (baseline: 0.48ms, target: ≤{TIER1_THRESHOLD_MS}ms)"
    print(f"✅ Tier 1 average: {avg_duration:.2f}ms")

# ============================================================================
# TIER 2 PERFORMANCE TESTS (Knowledge Graph)
# Target: ≤150ms, Baseline avg: 0.72ms
# ============================================================================

@pytest.mark.performance
def test_tier2_search_patterns_fts_performance(tier2_knowledge_graph):
    """Test: Tier 2 search_patterns() FTS5 performance - Baseline: 1.01ms"""
    @benchmark
    def operation():
        return tier2_knowledge_graph.search_patterns("test pattern")
    
    result, duration = operation()
    assert duration < TIER2_THRESHOLD_MS, \
        f"Tier 2 search_patterns REGRESSION: {duration:.2f}ms (baseline: 1.01ms, target: ≤{TIER2_THRESHOLD_MS}ms)"
    print(f"✅ Tier 2 search_patterns: {duration:.2f}ms")

@pytest.mark.performance
def test_tier2_average_performance(tier2_knowledge_graph):
    """Test: Tier 2 average query performance - Baseline avg: 0.72ms"""
    durations = []
    
    @benchmark
    def op1():
        return tier2_knowledge_graph.search_patterns("test pattern")
    _, d1 = op1()
    durations.append(d1)
    
    avg_duration = sum(durations) / len(durations)
    assert avg_duration < TIER2_THRESHOLD_MS, \
        f"Tier 2 AVERAGE REGRESSION: {avg_duration:.2f}ms (baseline: 0.72ms, target: ≤{TIER2_THRESHOLD_MS}ms)"
    print(f"✅ Tier 2 average: {avg_duration:.2f}ms")

# ============================================================================
# TIER 3 PERFORMANCE TESTS (Context Intelligence)
# Target: ≤500ms, Baseline avg: 52.51ms
# ============================================================================

@pytest.mark.performance
def test_tier3_get_git_metrics_performance(tier3_context_intelligence):
    """Test: Tier 3 get_git_metrics(30d) performance - Baseline: 0.40ms"""
    @benchmark
    def operation():
        return tier3_context_intelligence.get_git_metrics(days=30)
    
    result, duration = operation()
    assert duration < TIER3_THRESHOLD_MS, \
        f"Tier 3 get_git_metrics REGRESSION: {duration:.2f}ms (baseline: 0.40ms, target: ≤{TIER3_THRESHOLD_MS}ms)"
    print(f"✅ Tier 3 get_git_metrics: {duration:.2f}ms")

@pytest.mark.performance
def test_tier3_analyze_file_hotspots_performance(tier3_context_intelligence):
    """Test: Tier 3 analyze_file_hotspots(30d) performance - KNOWN HOTSPOT - Baseline: 258.67ms"""
    @benchmark
    def operation():
        return tier3_context_intelligence.analyze_file_hotspots(days=30)
    
    result, duration = operation()
    assert duration < TIER3_HOTSPOT_THRESHOLD_MS, \
        f"Tier 3 analyze_file_hotspots REGRESSION: {duration:.2f}ms (baseline: 258.67ms, target: ≤{TIER3_HOTSPOT_THRESHOLD_MS}ms)"
    print(f"✅ Tier 3 analyze_file_hotspots: {duration:.2f}ms (hotspot)")

# ============================================================================
# OPERATION PERFORMANCE TESTS (End-to-End)
# Target: <5000ms, Baseline avg: 1431ms
# ============================================================================

@pytest.mark.performance
@pytest.mark.slow
def test_operation_help_command_performance():
    """Test: Help command operation performance - Baseline: 462.48ms"""
    from src.operations import execute_operation
    
    @benchmark
    def operation():
        return execute_operation('help')
    
    result, duration = operation()
    assert duration < HELP_THRESHOLD_MS, \
        f"Help command REGRESSION: {duration:.2f}ms (baseline: 462ms, target: <{HELP_THRESHOLD_MS}ms)"
    print(f"✅ Help command: {duration:.2f}ms")

@pytest.mark.performance
@pytest.mark.slow
def test_operation_environment_setup_performance():
    """Test: Environment setup operation performance - Baseline: 3757.74ms, Threshold: 8000ms (allows network I/O)"""
    from src.operations import execute_operation
    
    @benchmark
    def operation():
        return execute_operation('setup environment')
    
    result, duration = operation()
    assert duration < ENVIRONMENT_SETUP_THRESHOLD_MS, \
        f"Environment setup REGRESSION: {duration:.2f}ms (baseline: 3758ms, target: <{ENVIRONMENT_SETUP_THRESHOLD_MS}ms)"
    print(f"✅ Environment setup: {duration:.2f}ms")

# ============================================================================
# AGGREGATE PERFORMANCE TESTS
# ============================================================================

@pytest.mark.performance
def test_all_tiers_meet_targets(tier1_manager, tier2_knowledge_graph, tier3_context_intelligence):
    """Test: All three tiers meet their performance targets"""
    @benchmark
    def tier1_op():
        return tier1_manager.get_recent_conversations(limit=20)
    _, tier1_duration = tier1_op()
    
    @benchmark
    def tier2_op():
        return tier2_knowledge_graph.search_patterns("test")
    _, tier2_duration = tier2_op()
    
    @benchmark
    def tier3_op():
        return tier3_context_intelligence.get_git_metrics(days=30)
    _, tier3_duration = tier3_op()
    
    assert tier1_duration < TIER1_THRESHOLD_MS, f"Tier 1 regression: {tier1_duration:.2f}ms"
    assert tier2_duration < TIER2_THRESHOLD_MS, f"Tier 2 regression: {tier2_duration:.2f}ms"
    assert tier3_duration < TIER3_THRESHOLD_MS, f"Tier 3 regression: {tier3_duration:.2f}ms"
    print(f"✅ All tiers meet targets: T1={tier1_duration:.2f}ms, T2={tier2_duration:.2f}ms, T3={tier3_duration:.2f}ms")

if __name__ == "__main__":
    pytest.main([__file__, '-v', '-m', 'performance'])
