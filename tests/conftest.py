"""
Pytest Configuration and Shared Fixtures

Provides common test fixtures for all CORTEX tests.

Copyright © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import pytest
import sqlite3
import tempfile
import os
from pathlib import Path
from datetime import datetime
from typing import Generator

# Import agent framework
from src.cortex_agents.base_agent import AgentRequest, AgentResponse, BaseAgent
from src.cortex_agents.agent_types import IntentType, Priority

# ============================================================================
# DEPENDENCY DETECTION
# ============================================================================

# Check for optional dependencies
try:
    import sklearn
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

try:
    import torch
    HAS_PYTORCH = True
except ImportError:
    HAS_PYTORCH = False


# ============================================================================
# PYTEST HOOKS FOR AUTO-CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Fast unit tests (<100ms)")
    config.addinivalue_line("markers", "integration: Integration tests (100ms-1s)")
    config.addinivalue_line("markers", "slow: Slow tests (>1s)")
    config.addinivalue_line("markers", "requires_sklearn: Tests requiring scikit-learn")
    config.addinivalue_line("markers", "requires_pytorch: Tests requiring PyTorch")


def pytest_collection_modifyitems(config, items):
    """Auto-skip tests based on missing dependencies."""
    skip_sklearn = pytest.mark.skip(reason="scikit-learn not installed")
    skip_pytorch = pytest.mark.skip(reason="PyTorch not installed")
    
    for item in items:
        if "requires_sklearn" in item.keywords and not HAS_SKLEARN:
            item.add_marker(skip_sklearn)
        if "requires_pytorch" in item.keywords and not HAS_PYTORCH:
            item.add_marker(skip_pytorch)


# ============================================================================
# Agent Framework Fixtures
# ============================================================================

@pytest.fixture
def sample_agent_request() -> AgentRequest:
    """Create a sample agent request for testing"""
    return AgentRequest(
        intent="test_intent",
        context={"file": "test.py", "action": "create"},
        user_message="Create a test file",
        conversation_id="test-conv-123",
        priority=Priority.NORMAL.value
    )


@pytest.fixture
def sample_agent_response() -> AgentResponse:
    """Create a sample agent response for testing"""
    return AgentResponse(
        success=True,
        result={"status": "completed"},
        message="Test operation successful",
        agent_name="TestAgent",
        duration_ms=123.45
    )


@pytest.fixture
def mock_tier1_api():
    """Mock Tier 1 API for agent testing"""
    class MockTier1API:
        def __init__(self):
            self.conversations = {}
        
        def start_conversation(self, title: str) -> str:
            conv_id = f"conv-{len(self.conversations)}"
            self.conversations[conv_id] = {
                "title": title,
                "messages": []
            }
            return conv_id
        
        def process_message(self, conv_id: str, role: str, content: str):
            if conv_id in self.conversations:
                self.conversations[conv_id]["messages"].append({
                    "role": role,
                    "content": content,
                    "timestamp": datetime.now()
                })
        
        def get_conversation(self, conv_id: str):
            return self.conversations.get(conv_id)
    
    return MockTier1API()


@pytest.fixture
def mock_tier2_kg():
    """Mock Tier 2 Knowledge Graph for agent testing"""
    class MockKnowledgeGraph:
        def __init__(self):
            self.patterns = []
        
        def search(self, query: str, limit: int = 10):
            # Simple mock search - check if pattern title words appear in query
            query_lower = query.lower()
            results = []
            for p in self.patterns:
                title_lower = p.get("title", "").lower()
                # Check if any significant words from title appear in query
                title_words = set(title_lower.split())
                query_words = set(query_lower.split())
                # If at least 50% of title words are in query, it's a match
                if title_words and len(title_words & query_words) >= len(title_words) * 0.5:
                    results.append(p)
            return results[:limit]
        
        def add_pattern(self, pattern_type: str, title: str, content: str):
            self.patterns.append({
                "type": pattern_type,
                "title": title,
                "content": content,
                "confidence": 1.0,
                "created_at": datetime.now()
            })
        
        def get_pattern(self, pattern_id: int):
            if 0 <= pattern_id < len(self.patterns):
                return self.patterns[pattern_id]
            return None
    
    return MockKnowledgeGraph()


@pytest.fixture
def mock_tier3_context():
    """Mock Tier 3 Context Intelligence for agent testing"""
    class MockContextIntelligence:
        def __init__(self):
            self.metrics = {
                "commits": 100,
                "velocity": 15.5,
                "hotspots": []
            }
        
        def get_context_summary(self):
            return {
                "total_commits": self.metrics["commits"],
                "average_velocity": self.metrics["velocity"],
                "file_hotspots": self.metrics["hotspots"]
            }
        
        def update_all_metrics(self, days: int = 30):
            # Mock update
            pass
        
        def get_file_hotspots(self, limit: int = 10):
            return self.metrics["hotspots"][:limit]
    
    return MockContextIntelligence()


@pytest.fixture
def mock_tier_apis(mock_tier1_api, mock_tier2_kg, mock_tier3_context):
    """Provide all three tier APIs together"""
    return {
        "tier1_api": mock_tier1_api,
        "tier2_kg": mock_tier2_kg,
        "tier3_context": mock_tier3_context
    }


class MockAgent(BaseAgent):
    """Mock agent for testing BaseAgent functionality"""
    
    def can_handle(self, request: AgentRequest) -> bool:
        return request.intent == "test_intent"
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        return AgentResponse(
            success=True,
            result={"handled": True},
            message=f"Handled request: {request.user_message}",
            agent_name=self.name
        )


@pytest.fixture
def mock_agent(mock_tier1_api, mock_tier2_kg, mock_tier3_context):
    """Create a mock agent instance for testing"""
    return MockAgent(
        name="MockAgent",
        tier1_api=mock_tier1_api,
        tier2_kg=mock_tier2_kg,
        tier3_context=mock_tier3_context
    )


# ============================================================================
# Database Fixtures (from existing tier tests)
# ============================================================================

@pytest.fixture
def temp_db() -> Generator[str, None, None]:
    """Create a temporary database file with proper cleanup.
    
    Uses in-memory database for parallel tests to avoid Windows file locking.
    Falls back to temp file for tests that require file-based DB.
    """
    # Check if running in parallel mode (pytest-xdist)
    worker_id = os.environ.get('PYTEST_XDIST_WORKER', None)
    
    if worker_id:
        # Use in-memory DB for parallel execution
        path = ":memory:"
        yield path
    else:
        # Use temp file for serial execution
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        try:
            yield path
        finally:
            # Ensure file is closed and deleted
            try:
                if os.path.exists(path):
                    os.remove(path)
            except PermissionError:
                # File still locked, try again after brief pause
                import time
                time.sleep(0.1)
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except PermissionError:
                    pass  # Best effort cleanup


@pytest.fixture
def db_connection(temp_db: str) -> Generator[sqlite3.Connection, None, None]:
    """Create a SQLite database connection with proper cleanup."""
    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        # Ensure connection is properly closed
        try:
            conn.close()
        except Exception:
            pass  # Best effort cleanup


@pytest.fixture
def in_memory_db() -> Generator[sqlite3.Connection, None, None]:
    """Create an in-memory database connection.
    
    Preferred for unit tests to avoid file locking issues on Windows.
    """
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        try:
            conn.close()
        except Exception:
            pass


@pytest.fixture
def temp_brain(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary CORTEX brain directory structure.
    
    Provides a complete brain directory with tier0/tier1/tier2/tier3 subdirs.
    Used by integration tests that need full brain structure.
    """
    brain_root = tmp_path / "cortex-brain"
    brain_root.mkdir(parents=True)
    
    # Create tier directories
    (brain_root / "tier0").mkdir()
    (brain_root / "tier1").mkdir()
    (brain_root / "tier2").mkdir()
    (brain_root / "tier3").mkdir()
    
    yield brain_root
    
    # Cleanup is automatic via tmp_path fixture


# ============================================================================
# File System Fixtures
# ============================================================================

@pytest.fixture
def temp_workspace() -> Generator[Path, None, None]:
    """Create a temporary workspace directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        yield workspace


@pytest.fixture
def sample_files(temp_workspace: Path):
    """Create sample files in workspace"""
    files = {
        "main.py": "def main():\n    print('Hello')\n",
        "test_main.py": "def test_main():\n    assert True\n",
        "README.md": "# Test Project\n"
    }
    
    for filename, content in files.items():
        file_path = temp_workspace / filename
        file_path.write_text(content)
    
    return temp_workspace


# ============================================================================
# PERFORMANCE MONITORING (Added 2025-11-11)
# ============================================================================

@pytest.fixture(autouse=True)
def monitor_test_performance(request):
    '''Monitor test execution time and warn on slow tests.'''
    import time
    start_time = time.time()
    yield
    duration = time.time() - start_time
    markers = [mark.name for mark in request.node.iter_markers()]
    if 'unit' in markers and duration > 0.1:
        print(f'\n⚠️  SLOW UNIT TEST: {request.node.name} took {duration:.3f}s')
    elif 'integration' in markers and duration > 1.0:
        print(f'\n⚠️  SLOW INTEGRATION: {request.node.name} took {duration:.3f}s')
