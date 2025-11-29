"""
Shared fixtures for performance tests.
"""

import asyncio
import os
import pytest
import tempfile
from pathlib import Path

from src.infrastructure.persistence.db_context import DatabaseContext
from src.infrastructure.migrations.migration_runner import MigrationRunner
from src.infrastructure.persistence.unit_of_work import UnitOfWork


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the entire test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def perf_database():
    """Create a temporary test database with migrations for performance tests."""
    # Create temp directory and database file
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "perf_test.db")
    
    # Initialize database context
    db_context = DatabaseContext(db_path)
    
    # Run migrations synchronously
    migrations_dir = Path(__file__).parent.parent.parent / "src" / "infrastructure" / "migrations"
    runner = MigrationRunner(db_path, str(migrations_dir))
    asyncio.run(runner.migrate())
    
    yield db_context
    
    # Cleanup
    asyncio.run(db_context.close())
    if os.path.exists(db_path):
        os.remove(db_path)
    os.rmdir(temp_dir)


@pytest.fixture
def perf_unit_of_work(perf_database):
    """Create a unit of work instance for performance tests."""
    return UnitOfWork(perf_database)


@pytest.fixture
def sample_conversations():
    """Generate sample conversation data for benchmarking."""
    conversations = []
    for i in range(100):
        conversations.append({
            "conversation_id": f"perf_conv_{i:04d}",
            "title": f"Performance Test Conversation {i}",
            "content": f"This is test conversation number {i} for performance benchmarking. " * 10,
            "file_path": f"/perf/test_{i}.md",
            "quality_score": 0.75 + (i % 25) * 0.01,
            "entity_count": 5 + (i % 10)
        })
    return conversations


@pytest.fixture
def sample_patterns():
    """Generate sample pattern data for benchmarking."""
    patterns = []
    for i in range(100):
        patterns.append({
            "pattern_id": f"perf_pattern_{i:04d}",
            "pattern_name": f"Performance Test Pattern {i}",
            "pattern_type": "design_pattern" if i % 2 == 0 else "best_practice",
            "pattern_content": f"This is test pattern content for benchmarking. " * 10,
            "source_conversation_id": f"perf_conv_{i:04d}",
            "namespace": f"perf.namespace_{i % 5}",
            "confidence_score": 0.70 + (i % 30) * 0.01,
            "tags": [f"tag_{i % 10}", f"category_{i % 5}"]
        })
    return patterns
