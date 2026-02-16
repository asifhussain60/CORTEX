"""
CORTEX Health Orchestrator Configuration

Tuned configuration to reduce false positives and focus on genuine issues.

Phase: PHASE-95
"""

# Duplicate Detection Configuration
DUPLICATE_DETECTION = {
    "check_python": True,
    "check_yaml": True,
    "similarity_threshold": 0.8,
    "exclude_patterns": [
        "*/_archives/*",
        "*/_workspaces/*",
        "*/.venv/*",
        "*/.git/*",
        "*/tests/*",
        "*/__pycache__/*",
        "*/.mypy_cache/*",
    ],
}

# Stub Detection Configuration
STUB_DETECTION = {
    "loc_threshold": 200,  # Files under 200 LOC
    "complexity_threshold": 5,  # McCabe complexity < 5
    "stub_indicator_threshold": 3,  # Require 3+ indicators to flag
    "exclude_patterns": [
        "*/_archives/*",
        "*/_workspaces/*",
        "*/.venv/*",
        "*/.git/*",
        "*/tests/*",
        "*/test_*.py",
        "*/__pycache__/*",
        "*/__init__.py",  # Package markers (often minimal)
        "*/conftest.py",  # Test configs
        "*/models.py",  # Data models (legitimately simple)
        "*/bootstrap.py",  # Bootstrap (minimal by design)
        "*/*_metrics.py",  # Metrics collectors
    ],
}

# Path Integrity Configuration
PATH_INTEGRITY = {
    # ONLY list DEPRECATED paths that were migrated
    # Empty list = no deprecated paths currently
    "old_paths": [],
    
    "registry_root": "cortex-registry",
    
    # Only check project-specific imports (avoid stdlib/third-party false positives)
    "import_prefixes": ["cortex", "cortex_", "company"],
    
    "exclude_patterns": [
        "*/_archives/*",
        "*/_workspaces/*",
        "*/.venv/*",
        "*/.git/*",
        "*/__pycache__/*",
    ],
}

# Version Cleanup Configuration
VERSION_CLEANUP = {
    "version_patterns": [
        "_v[0-9]+",
        "-v[0-9]+",
        "_old",
        "_legacy",
        "_backup",
        "_deprecated",
    ],
    "exclude_patterns": [
        "*/_archives/*",
        "*/_workspaces/*",
        "*/.venv/*",
        "*/.git/*",
    ],
}

# Test Coverage Configuration
TEST_COVERAGE = {
    "require_tests": True,
    "source_dirs": ["cortex", "cortex_brain", "cortex_lens"],
    "test_dirs": ["tests"],
    "exclude_patterns": [
        "*/_archives/*",
        "*/_workspaces/*",
        "*/.venv/*",
        "*/.git/*",
        "*/__init__.py",
        "*/conftest.py",
    ],
}

# Registry Consistency Configuration
REGISTRY_CONSISTENCY = {
    "registry_root": "cortex-registry",
    "schema_validation": True,
    "check_yaml_syntax": True,
}

# MCP Auto-Healing Configuration
MCP_AUTO_HEALING = {
    "check_mcp_availability": True,
    "check_dependencies": True,
    "check_requirements_format": True,
    "auto_fix_enabled": False,  # Manual fixes for safety
}
