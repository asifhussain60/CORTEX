"""
CORTEX 4.0 Mock Data for Testing

Provides sample data structures for testing CORTEX components.

⚠️ IMPORTANT: This data is for CORTEX INTERNAL TESTS ONLY.
"""

from datetime import datetime
from typing import Dict, List, Any


def sample_conversation() -> Dict[str, Any]:
    """Sample conversation data."""
    return {
        "id": "conv_001",
        "timestamp": datetime.now().isoformat(),
        "user_message": "plan user authentication",
        "assistant_response": "I'll create a feature plan...",
        "context": {
            "operation": "planning",
            "complexity": "HIGH"
        }
    }


def sample_pattern() -> Dict[str, Any]:
    """Sample knowledge pattern."""
    return {
        "id": "pattern_001",
        "pattern_type": "authentication",
        "pattern_name": "JWT with bcrypt",
        "namespace": "user-app",
        "context": {
            "libraries": ["jsonwebtoken", "bcrypt"],
            "files_involved": ["auth_service.py", "jwt_utils.py"]
        },
        "success_rate": 0.95,
        "usage_count": 12
    }


def sample_git_metrics() -> Dict[str, Any]:
    """Sample git metrics."""
    return {
        "total_commits": 156,
        "active_branches": 3,
        "last_commit": datetime.now().isoformat(),
        "hotspots": [
            {"file": "src/main.py", "changes": 45},
            {"file": "src/utils.py", "changes": 32}
        ]
    }


def sample_orchestrator_phases() -> List[Dict[str, Any]]:
    """Sample orchestrator phase definitions."""
    return [
        {"name": "validate", "order": 1, "required": True},
        {"name": "analyze", "order": 2, "required": True},
        {"name": "execute", "order": 3, "required": True},
        {"name": "cleanup", "order": 4, "required": False}
    ]


def sample_validation_errors() -> List[str]:
    """Sample validation errors."""
    return [
        "Missing required parameter: feature_name",
        "Invalid complexity level: ULTRA (expected HIGH, MEDIUM, LOW)",
        "Configuration file not found: cortex.config.json"
    ]


def sample_test_results() -> Dict[str, Any]:
    """Sample test execution results."""
    return {
        "total_tests": 150,
        "passed": 145,
        "failed": 3,
        "skipped": 2,
        "duration": 12.5,
        "coverage": 87.3,
        "failures": [
            {
                "test": "test_authentication_flow",
                "error": "AssertionError: Expected 200, got 401"
            }
        ]
    }
