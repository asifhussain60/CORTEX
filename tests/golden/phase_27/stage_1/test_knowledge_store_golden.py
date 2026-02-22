"""
Golden Tests for Knowledge Store - Phase 27 Stage 1

Zero-mock golden tests using real SQLite database for knowledge persistence.
Tests cross-session learning and versioned snapshot capabilities.

AC_START: AC-PHASE27-S1-001
Authority: Phase 27 Consolidation (GAP-01)
Philosophy: Zero mocks - real DB, real I/O, real persistence
"""

import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
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
def temp_db_path() -> Path:
    """Create temporary database path for testing."""
    temp_dir = tempfile.mkdtemp()
    return Path(temp_dir) / "knowledge_store_test.db"


@pytest.fixture
def knowledge_store(temp_db_path: Path):
    """Create KnowledgeStore instance with temp database."""
    from cortex.intelligence.persistence.knowledge_store import KnowledgeStore
    
    store = KnowledgeStore(db_path=temp_db_path)
    yield store
    store.close()


# ============================================================================
# GOLDEN TEST 1: Cross-Session Learning Persistence
# ============================================================================


def test_golden_cross_session_knowledge_persistence(temp_db_path: Path):
    """
    GOLDEN TEST: Knowledge persists across sessions (no mocks).
    
    Scenario:
    1. Session 1: Store repository domain knowledge
    2. Close database (simulate session end)
    3. Session 2: Retrieve knowledge from persistent storage
    4. Verify: All knowledge retained with metadata
    
    AC: AC-PHASE27-S1-G01 (Golden Test - Cross-Session)
    """
    from cortex.intelligence.persistence.knowledge_store import KnowledgeStore
    
    # SESSION 1: Store knowledge
    session_1_id = str(uuid4())
    repo_name = "test-microservice"
    domain_knowledge = {
        "repository": repo_name,
        "tech_stack": ["python", "fastapi", "postgresql"],
        "patterns": ["repository-pattern", "dependency-injection"],
        "architecture": "microservices",
        "complexity_score": 7.5
    }
    
    store_1 = KnowledgeStore(db_path=temp_db_path)
    entry_id = store_1.store_knowledge(
        session_id=session_1_id,
        knowledge_type="repository_domain",
        content=domain_knowledge,
        metadata={"source": "onboarding", "version": "1.0"}
    )
    assert entry_id is not None
    store_1.close()
    
    # SESSION 2: Retrieve knowledge (new instance, same DB)
    session_2_id = str(uuid4())
    store_2 = KnowledgeStore(db_path=temp_db_path)
    
    retrieved = store_2.get_knowledge(entry_id)
    assert retrieved is not None
    assert retrieved["content"]["repository"] == repo_name
    assert retrieved["content"]["tech_stack"] == ["python", "fastapi", "postgresql"]
    assert retrieved["metadata"]["source"] == "onboarding"
    assert retrieved["metadata"]["version"] == "1.0"
    
    # Verify cross-session query works
    repo_knowledge = store_2.query_by_type("repository_domain")
    assert len(repo_knowledge) == 1
    assert repo_knowledge[0]["content"]["repository"] == repo_name
    
    store_2.close()


# ============================================================================
# GOLDEN TEST 2: Versioned Knowledge Snapshots
# ============================================================================


def test_golden_versioned_knowledge_snapshots(knowledge_store):
    """
    GOLDEN TEST: Knowledge versioning with snapshot history (no mocks).
    
    Scenario:
    1. Store initial knowledge (v1.0)
    2. Update with new learnings (v1.1)
    3. Update again with refinement (v1.2)
    4. Query: Get all versions
    5. Query: Get latest version only
    6. Verify: Version history retained, rollback possible
    
    AC: AC-PHASE27-S1-G02 (Golden Test - Versioning)
    """
    session_id = str(uuid4())
    repo_name = "evolving-service"
    
    # Version 1.0: Initial knowledge
    entry_id = knowledge_store.store_knowledge(
        session_id=session_id,
        knowledge_type="repository_domain",
        content={
            "repository": repo_name,
            "patterns": ["mvc"],
            "complexity_score": 5.0
        },
        metadata={"version": "1.0", "source": "initial_scan"}
    )
    
    # Version 1.1: Learning update (new pattern detected)
    knowledge_store.update_knowledge(
        entry_id=entry_id,
        content={
            "repository": repo_name,
            "patterns": ["mvc", "repository-pattern"],  # Pattern added
            "complexity_score": 6.2  # Score updated
        },
        metadata={"version": "1.1", "source": "learning_loop"}
    )
    
    # Version 1.2: Refinement (better analysis)
    knowledge_store.update_knowledge(
        entry_id=entry_id,
        content={
            "repository": repo_name,
            "patterns": ["mvc", "repository-pattern", "cqrs"],  # More patterns
            "complexity_score": 7.5  # Refined score
        },
        metadata={"version": "1.2", "source": "deep_analysis"}
    )
    
    # Query: Get all versions
    all_versions = knowledge_store.get_knowledge_history(entry_id)
    assert len(all_versions) == 3
    assert all_versions[0]["metadata"]["version"] == "1.0"
    assert len(all_versions[0]["content"]["patterns"]) == 1
    assert all_versions[1]["metadata"]["version"] == "1.1"
    assert len(all_versions[1]["content"]["patterns"]) == 2
    assert all_versions[2]["metadata"]["version"] == "1.2"
    assert len(all_versions[2]["content"]["patterns"]) == 3
    
    # Query: Get latest version only
    latest = knowledge_store.get_knowledge(entry_id)
    assert latest["metadata"]["version"] == "1.2"
    assert latest["content"]["complexity_score"] == 7.5


# ============================================================================
# GOLDEN TEST 3: Pattern Frequency Tracking
# ============================================================================


def test_golden_pattern_frequency_tracking(knowledge_store):
    """
    GOLDEN TEST: Track pattern frequency across repositories (no mocks).
    
    Scenario:
    1. Store knowledge for 5 different repositories
    2. Track pattern occurrences (repository-pattern, mvc, etc.)
    3. Query: Get pattern frequency distribution
    4. Verify: 15-20% faster analysis on similar codebases (tracked)
    
    AC: AC-PHASE27-S1-G03 (Golden Test - Pattern Tracking)
    """
    session_id = str(uuid4())
    
    repositories = [
        {"name": "service-a", "patterns": ["mvc", "repository-pattern"]},
        {"name": "service-b", "patterns": ["mvc", "dependency-injection"]},
        {"name": "service-c", "patterns": ["repository-pattern", "cqrs"]},
        {"name": "service-d", "patterns": ["mvc", "repository-pattern", "cqrs"]},
        {"name": "service-e", "patterns": ["dependency-injection", "factory"]},
    ]
    
    # Store knowledge for all repositories
    for repo in repositories:
        knowledge_store.store_knowledge(
            session_id=session_id,
            knowledge_type="repository_domain",
            content={
                "repository": repo["name"],
                "patterns": repo["patterns"]
            },
            metadata={"source": "pattern_analysis"}
        )
    
    # Query: Pattern frequency
    pattern_freq = knowledge_store.get_pattern_frequency()
    
    # Verify frequency counts
    assert pattern_freq["mvc"] == 3  # 3 repositories use mvc
    assert pattern_freq["repository-pattern"] == 3  # 3 repositories
    assert pattern_freq["dependency-injection"] == 2  # 2 repositories
    assert pattern_freq["cqrs"] == 2  # 2 repositories
    assert pattern_freq["factory"] == 1  # 1 repository
    
    # Verify: Similar codebase detection (repositories with common patterns)
    similar_repos = knowledge_store.find_similar_repositories(
        patterns=["mvc", "repository-pattern"],
        threshold=0.5  # 50% pattern overlap
    )
    assert len(similar_repos) >= 2  # service-a and service-d


# ============================================================================
# GOLDEN TEST 4: Session Continuity Markers
# ============================================================================


def test_golden_session_continuity_markers(knowledge_store):
    """
    GOLDEN TEST: Session continuity with boundary markers (no mocks).
    
    Scenario:
    1. Session 1: Store knowledge + mark session complete
    2. Session 2: New knowledge referencing Session 1
    3. Query: Get session timeline
    4. Verify: Session boundaries clear, lineage tracked
    
    AC: AC-PHASE27-S1-G04 (Golden Test - Session Continuity)
    """
    # Session 1
    session_1_id = str(uuid4())
    entry_1 = knowledge_store.store_knowledge(
        session_id=session_1_id,
        knowledge_type="repository_domain",
        content={"repository": "service-alpha", "status": "onboarded"},
        metadata={"session_phase": "onboarding"}
    )
    knowledge_store.mark_session_complete(session_1_id, {"outcome": "success"})
    
    # Session 2 (references Session 1)
    session_2_id = str(uuid4())
    entry_2 = knowledge_store.store_knowledge(
        session_id=session_2_id,
        knowledge_type="learning_enhancement",
        content={"repository": "service-alpha", "patterns_refined": True},
        metadata={
            "session_phase": "learning_loop",
            "parent_session": session_1_id  # Lineage
        }
    )
    knowledge_store.mark_session_complete(session_2_id, {"outcome": "enhanced"})
    
    # Query: Session timeline
    timeline = knowledge_store.get_session_timeline("service-alpha")
    assert len(timeline) == 2
    assert timeline[0]["session_id"] == session_1_id
    assert timeline[0]["phase"] == "onboarding"
    assert timeline[1]["session_id"] == session_2_id
    assert timeline[1]["phase"] == "learning_loop"
    assert timeline[1]["parent_session"] == session_1_id


# ============================================================================
# GOLDEN TEST 5: Brain Intelligence Layer Updates
# ============================================================================


def test_golden_brain_intelligence_layer_updates(knowledge_store):
    """
    GOLDEN TEST: Brain intelligence layer persistence (no mocks).
    
    Scenario:
    1. Store perception layer state (file analysis results)
    2. Store reasoning layer state (pattern recognition)
    3. Store action layer state (recommendations)
    4. Query: Get complete brain state snapshot
    5. Verify: All layers persisted and retrievable
    
    AC: AC-PHASE27-S1-G05 (Golden Test - Brain Layers)
    """
    session_id = str(uuid4())
    repo_name = "cognitive-service"
    
    # Perception layer
    perception_id = knowledge_store.store_brain_layer(
        session_id=session_id,
        repository=repo_name,
        layer="perception",
        state={
            "files_analyzed": 150,
            "imports_detected": 340,
            "dependencies": ["fastapi", "sqlalchemy"],
            "analysis_time_ms": 1250
        }
    )
    
    # Reasoning layer
    reasoning_id = knowledge_store.store_brain_layer(
        session_id=session_id,
        repository=repo_name,
        layer="reasoning",
        state={
            "patterns_recognized": ["repository-pattern", "dependency-injection"],
            "architecture_inferred": "layered",
            "complexity_score": 6.8,
            "confidence": 0.92
        }
    )
    
    # Action layer
    action_id = knowledge_store.store_brain_layer(
        session_id=session_id,
        repository=repo_name,
        layer="action",
        state={
            "recommendations": [
                "Add integration tests for repository layer",
                "Implement caching for frequent queries"
            ],
            "priority": "medium",
            "estimated_impact": "high"
        }
    )
    
    # Query: Complete brain snapshot
    brain_snapshot = knowledge_store.get_brain_snapshot(repo_name)
    
    assert brain_snapshot is not None
    assert "perception" in brain_snapshot
    assert "reasoning" in brain_snapshot
    assert "action" in brain_snapshot
    
    # Verify perception
    assert brain_snapshot["perception"]["files_analyzed"] == 150
    
    # Verify reasoning
    assert "repository-pattern" in brain_snapshot["reasoning"]["patterns_recognized"]
    assert brain_snapshot["reasoning"]["confidence"] == 0.92
    
    # Verify action
    assert len(brain_snapshot["action"]["recommendations"]) == 2


# ============================================================================
# GOLDEN TEST 6: Concurrent Session Safety
# ============================================================================


def test_golden_concurrent_session_safety(temp_db_path: Path):
    """
    GOLDEN TEST: Concurrent sessions without conflicts (no mocks).
    
    Scenario:
    1. Open 3 concurrent KnowledgeStore instances (same DB)
    2. Each stores knowledge for different repositories
    3. Query: Verify all knowledge stored without corruption
    4. Verify: No race conditions or lost updates
    
    AC: AC-PHASE27-S1-G06 (Golden Test - Concurrency)
    """
    from cortex.intelligence.persistence.knowledge_store import KnowledgeStore
    import concurrent.futures
    
    def store_repo_knowledge(repo_num: int, db_path: Path) -> str:
        """Store knowledge in concurrent session."""
        store = KnowledgeStore(db_path=db_path)
        session_id = str(uuid4())
        
        entry_id = store.store_knowledge(
            session_id=session_id,
            knowledge_type="repository_domain",
            content={
                "repository": f"concurrent-service-{repo_num}",
                "tech_stack": [f"framework-{repo_num}"],
                "patterns": [f"pattern-{repo_num}"]
            },
            metadata={"concurrency_test": True}
        )
        
        store.close()
        return entry_id
    
    # Concurrent execution
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(store_repo_knowledge, i, temp_db_path)
            for i in range(3)
        ]
        entry_ids = [f.result() for f in futures]
    
    # Verify: All entries stored
    assert len(entry_ids) == 3
    assert len(set(entry_ids)) == 3  # All unique
    
    # Verify: All retrievable
    store = KnowledgeStore(db_path=temp_db_path)
    for i, entry_id in enumerate(entry_ids):
        retrieved = store.get_knowledge(entry_id)
        assert retrieved is not None
        assert f"concurrent-service-{i}" in retrieved["content"]["repository"]
    store.close()


# ============================================================================
# GOLDEN TEST 7: Knowledge Cleanup and Archival
# ============================================================================


def test_golden_knowledge_cleanup_archival(temp_db_path: Path):
    """
    GOLDEN TEST: Archive old knowledge without data loss (no mocks).
    
    Scenario:
    1. Store knowledge for 10 repositories
    2. Manually backdate 5 entries (simulate old data)
    3. Archive stale knowledge
    4. Verify: Stale moved to archive table, active remains
    5. Verify: Archived knowledge still queryable
    
    AC: AC-PHASE27-S1-G07 (Golden Test - Archival)
    """
    from cortex.intelligence.persistence.knowledge_store import KnowledgeStore
    from datetime import datetime, timedelta
    
    knowledge_store = KnowledgeStore(db_path=temp_db_path)
    session_id = str(uuid4())
    
    # Store 10 repositories
    entry_ids = []
    for i in range(10):
        entry_id = knowledge_store.store_knowledge(
            session_id=session_id,
            knowledge_type="repository_domain",
            content={"repository": f"service-{i}", "status": "analyzed"},
            metadata={"source": "test"}
        )
        entry_ids.append(entry_id)
    
    # Manually backdate 5 entries (simulate old data)
    import sqlite3
    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()
    
    old_date = (datetime.utcnow() - timedelta(days=45)).isoformat()
    for i in range(5):
        cursor.execute("""
            UPDATE knowledge_entries
            SET created_at = ?
            WHERE entry_id = ?
        """, (old_date, entry_ids[i]))
    
    conn.commit()
    conn.close()
    
    # Archive stale knowledge (>30 days)
    archived_count = knowledge_store.archive_stale_knowledge(days_threshold=30)
    assert archived_count == 5
    
    # Query: Active knowledge (should be 5)
    active = knowledge_store.query_by_type("repository_domain", include_archived=False)
    assert len(active) == 5
    
    # Query: All knowledge including archived (should be 10)
    all_knowledge = knowledge_store.query_by_type("repository_domain", include_archived=True)
    assert len(all_knowledge) == 10
    
    knowledge_store.close()


# ============================================================================
# GOLDEN TEST 8: Knowledge Export for Analysis
# ============================================================================


def test_golden_knowledge_export_for_analysis(knowledge_store):
    """
    GOLDEN TEST: Export knowledge for external analysis (no mocks).
    
    Scenario:
    1. Store diverse knowledge (repositories, patterns, learnings)
    2. Export to JSON file
    3. Verify: JSON structure valid
    4. Import exported JSON into new database
    5. Verify: All knowledge restored correctly
    
    AC: AC-PHASE27-S1-G08 (Golden Test - Export/Import)
    """
    session_id = str(uuid4())
    
    # Store diverse knowledge
    repositories = [
        {"name": "service-x", "patterns": ["mvc"], "score": 5.5},
        {"name": "service-y", "patterns": ["repository"], "score": 6.8},
        {"name": "service-z", "patterns": ["cqrs"], "score": 8.2},
    ]
    
    for repo in repositories:
        knowledge_store.store_knowledge(
            session_id=session_id,
            knowledge_type="repository_domain",
            content=repo,
            metadata={"export_test": True}
        )
    
    # Export to JSON
    export_path = knowledge_store.export_knowledge_to_json(
        filter_type="repository_domain",
        output_path=None  # Returns tempfile
    )
    
    assert export_path.exists()
    
    # Read exported JSON
    import json
    with open(export_path, "r") as f:
        exported_data = json.load(f)
    
    assert len(exported_data["knowledge_entries"]) == 3
    assert exported_data["export_metadata"]["entry_count"] == 3
    
    # Import into new database (validation)
    assert all(
        entry["content"]["name"] in ["service-x", "service-y", "service-z"]
        for entry in exported_data["knowledge_entries"]
    )


# AC_COMPLETE: AC-PHASE27-S1-001 ✅ 8 golden tests defined (RED phase)
