"""
Shared fixtures for CORTEX integration tests.

Provides common test infrastructure including:
- Temporary project directories
- Brain database initialization
- Mock configurations
- Test data generators
- Pre-test configuration validation
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Generator, Dict, Any
import pytest
import sqlite3


def pytest_configure(config):
    """
    Run configuration validation before test suite starts.
    
    This prevents running tests against invalid configuration,
    catching brittleness issues before expensive integration tests run.
    """
    # Skip validation if --no-config-validation flag present
    if config.getoption("--no-config-validation", default=False):
        print("\n⚠️  Skipping configuration validation (--no-config-validation)")
        return
    
    print("\n🔍 Validating orchestrator configuration...")
    
    # Run validation script
    script_path = Path(__file__).parent.parent.parent / "scripts" / "validate_orchestrator_config.py"
    
    if not script_path.exists():
        print(f"⚠️  Validation script not found: {script_path}")
        return
    
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("\n" + result.stdout)
        print("\n❌ Configuration validation failed. Fix errors before running tests.")
        print("   To skip validation: pytest --no-config-validation")
        sys.exit(1)
    
    print("✅ Configuration validation passed\n")


def pytest_addoption(parser):
    """Add custom command-line options."""
    parser.addoption(
        "--no-config-validation",
        action="store_true",
        default=False,
        help="Skip configuration validation before running tests"
    )


@pytest.fixture
def temp_project() -> Generator[str, None, None]:
    """Create a temporary project directory for testing."""
    temp_dir = tempfile.mkdtemp(prefix="cortex_test_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_brain(temp_project: str) -> Generator[str, None, None]:
    """Create a temporary brain directory with initialized databases."""
    brain_path = os.path.join(temp_project, "cortex-brain")
    os.makedirs(brain_path, exist_ok=True)
    
    # Create tier directories
    for tier in ["tier0", "tier1", "tier2", "tier3"]:
        os.makedirs(os.path.join(brain_path, tier), exist_ok=True)
    
    # Initialize Tier 1 database
    tier1_db = os.path.join(brain_path, "tier1", "working_memory.db")
    conn = sqlite3.connect(tier1_db)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            user_message TEXT,
            assistant_response TEXT,
            intent TEXT,
            context TEXT
        )
    """)
    conn.commit()
    conn.close()
    
    # Initialize Tier 2 database
    tier2_db = os.path.join(brain_path, "tier2", "knowledge_graph.db")
    conn = sqlite3.connect(tier2_db)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_type TEXT NOT NULL,
            description TEXT,
            confidence REAL DEFAULT 0.5,
            usage_count INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    
    # Initialize Tier 3 database
    tier3_db = os.path.join(brain_path, "tier3", "development_context.db")
    conn = sqlite3.connect(tier3_db)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL,
            metric_type TEXT NOT NULL,
            value REAL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    
    yield brain_path
    # Cleanup handled by temp_project fixture


@pytest.fixture
def mock_config(temp_project: str) -> Dict[str, Any]:
    """Provide mock CORTEX configuration."""
    return {
        "machines": {
            "test-machine": {
                "rootPath": temp_project,
                "brainPath": os.path.join(temp_project, "cortex-brain")
            }
        },
        "current_machine": "test-machine",
        "version": "3.8.1"
    }


@pytest.fixture
def sample_planning_request() -> Dict[str, Any]:
    """Sample planning request data."""
    return {
        "feature_name": "User Authentication",
        "description": "Implement JWT-based authentication",
        "acceptance_criteria": [
            "Users can login with email/password",
            "JWT tokens expire after 24 hours",
            "Refresh tokens supported"
        ],
        "technical_notes": "Use bcrypt for password hashing"
    }


@pytest.fixture
def sample_tdd_session() -> Dict[str, Any]:
    """Sample TDD session data."""
    return {
        "session_id": "tdd-test-001",
        "feature": "User Registration",
        "current_phase": "RED",
        "test_file": "tests/test_user_registration.py",
        "implementation_file": "src/auth/registration.py",
        "test_count": 3,
        "passing_tests": 0
    }


@pytest.fixture
def sample_learning_event() -> Dict[str, Any]:
    """Sample learning event data."""
    return {
        "event_type": "operation_failure",
        "operation_name": "deploy",
        "severity": "high",
        "problem": "Connection timeout during deployment",
        "context": {
            "environment": "production",
            "retry_count": 3,
            "timeout_seconds": 30
        },
        "solution": "Increase timeout to 60 seconds",
        "confidence": 0.85
    }


@pytest.fixture
def cleanup_test_files(temp_project: str):
    """Cleanup any test files created during integration tests."""
    yield
    # Post-test cleanup
    test_artifacts = [
        "test_output.json",
        "test_report.html",
        "coverage.xml"
    ]
    for artifact in test_artifacts:
        artifact_path = os.path.join(temp_project, artifact)
        if os.path.exists(artifact_path):
            os.remove(artifact_path)
