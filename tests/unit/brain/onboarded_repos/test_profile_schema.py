"""
Tests for Repository Profile Schema (Phase 28.1.1)
TDD RED Phase - Tests written BEFORE implementation

Test Coverage:
- Profile schema validation (required fields)
- Profile serialization (to/from YAML)
- Profile deserialization (from YAML)
- Loose coupling metadata validation
- Tech stack validation
- Security metadata validation
"""

import pytest
from datetime import datetime
from pathlib import Path
from pydantic import ValidationError


def test_repository_profile_schema_validation():
    """Test that RepositoryProfile requires all mandatory fields."""
    from cortex_brain.onboarded_repos.profile_schema import RepositoryProfile
    
    # RED: Should fail - no required fields provided
    with pytest.raises(ValidationError) as exc_info:
        RepositoryProfile()
    
    # Validate that missing fields are reported
    errors = exc_info.value.errors()
    required_fields = {'name', 'path', 'onboarded_at'}
    missing_fields = {e['loc'][0] for e in errors if e['type'] == 'missing'}
    
    assert required_fields.issubset(missing_fields), \
        f"Missing required fields: {required_fields - missing_fields}"


def test_repository_profile_minimal_valid():
    """Test minimal valid RepositoryProfile creation."""
    from cortex_brain.onboarded_repos.profile_schema import RepositoryProfile
    
    # RED: Should pass with minimal required fields
    profile = RepositoryProfile(
        name="TEST_REPO",
        path="/path/to/repo",
        onboarded_at=datetime.now()
    )
    
    assert profile.name == "TEST_REPO"
    assert profile.path == "/path/to/repo"
    assert profile.exists is True  # Default value
    assert profile.tech_stack is not None  # Should have default empty structure


def test_repository_profile_with_tech_stack():
    """Test RepositoryProfile with tech stack information."""
    from cortex_brain.onboarded_repos.profile_schema import (
        RepositoryProfile,
        TechStack
    )
    
    # RED: Should create profile with tech stack
    profile = RepositoryProfile(
        name="PYTHON_REPO",
        path="/path/to/python/repo",
        onboarded_at=datetime.now(),
        tech_stack=TechStack(
            primary_language="Python",
            languages=["Python", "YAML"],
            frameworks=["FastAPI", "Pydantic"],
            dependencies=["pyyaml>=6.0", "pydantic>=2.0"]
        )
    )
    
    assert profile.tech_stack.primary_language == "Python"
    assert len(profile.tech_stack.languages) == 2
    assert "FastAPI" in profile.tech_stack.frameworks


def test_repository_profile_to_yaml():
    """Test RepositoryProfile serialization to YAML."""
    from cortex_brain.onboarded_repos.profile_schema import RepositoryProfile
    
    # RED: Should serialize to valid YAML string
    profile = RepositoryProfile(
        name="KSESSIONS",
        path="/Users/asifhussain/PROJECTS/KSESSIONS",
        onboarded_at=datetime(2026, 2, 6, 10, 30, 0)
    )
    
    yaml_str = profile.to_yaml()
    
    assert isinstance(yaml_str, str)
    assert "name: KSESSIONS" in yaml_str
    assert "path: /Users/asifhussain/PROJECTS/KSESSIONS" in yaml_str
    assert "onboarded_at:" in yaml_str


def test_repository_profile_from_yaml():
    """Test RepositoryProfile deserialization from YAML."""
    from cortex_brain.onboarded_repos.profile_schema import RepositoryProfile
    
    # RED: Should deserialize from YAML string
    yaml_content = """
name: KSESSIONS
path: /Users/asifhussain/PROJECTS/KSESSIONS
onboarded_at: 2026-02-06T10:30:00
exists: true
tech_stack:
  primary_language: Python
  languages:
    - Python
    - YAML
  frameworks:
    - FastAPI
  dependencies:
    - pyyaml>=6.0
"""
    
    profile = RepositoryProfile.from_yaml(yaml_content)
    
    assert profile.name == "KSESSIONS"
    assert profile.path == "/Users/asifhussain/PROJECTS/KSESSIONS"
    assert profile.tech_stack.primary_language == "Python"


def test_repository_profile_loose_coupling_metadata():
    """Test loose coupling metadata in profile."""
    from cortex_brain.onboarded_repos.profile_schema import (
        RepositoryProfile,
        LooseCoupling
    )
    
    # RED: Should include loose coupling metadata
    profile = RepositoryProfile(
        name="DELETABLE_REPO",
        path="/tmp/deletable",
        onboarded_at=datetime.now(),
        loose_coupling=LooseCoupling(
            referenced_by_cortex=True,
            deletion_safe=True,
            fallback_strategy="use_cached_profile"
        )
    )
    
    assert profile.loose_coupling.deletion_safe is True
    assert profile.loose_coupling.fallback_strategy == "use_cached_profile"


def test_repository_profile_company_domains_detection():
    """Test company domains structure detection."""
    from cortex_brain.onboarded_repos.profile_schema import (
        RepositoryProfile,
        RepositoryStructure
    )
    
    # RED: Should detect company domains
    profile = RepositoryProfile(
        name="KSESSIONS",
        path="/path/to/ksessions",
        onboarded_at=datetime.now(),
        structure=RepositoryStructure(
            has_company_domains=True,
            company_domains_path="company/domains/",
            domains_detected=["security/", "testing/", "api-standards/"]
        )
    )
    
    assert profile.structure.has_company_domains is True
    assert len(profile.structure.domains_detected) == 3
    assert "security/" in profile.structure.domains_detected


def test_repository_profile_security_metadata():
    """Test security metadata in profile."""
    from cortex_brain.onboarded_repos.profile_schema import (
        RepositoryProfile,
        SecurityMetadata
    )
    
    # RED: Should include security baseline
    profile = RepositoryProfile(
        name="SECURE_REPO",
        path="/path/to/secure",
        onboarded_at=datetime.now(),
        security=SecurityMetadata(
            secrets_management="environment variables",
            auth_pattern="JWT + OAuth2",
            vulnerabilities_detected=0,
            last_scan=datetime.now()
        )
    )
    
    assert profile.security.vulnerabilities_detected == 0
    assert profile.security.auth_pattern == "JWT + OAuth2"


def test_repository_profile_standards():
    """Test standards detection in profile."""
    from cortex_brain.onboarded_repos.profile_schema import (
        RepositoryProfile,
        Standards
    )
    
    # RED: Should include coding standards
    profile = RepositoryProfile(
        name="STANDARDS_REPO",
        path="/path/to/standards",
        onboarded_at=datetime.now(),
        standards=Standards(
            coding_style="black + mypy + pylint",
            security_baseline="OWASP Top 10 compliant",
            test_patterns="TDD with pytest",
            api_patterns="RESTful + OpenAPI 3.0"
        )
    )
    
    assert profile.standards.coding_style == "black + mypy + pylint"
    assert profile.standards.test_patterns == "TDD with pytest"


def test_repository_profile_validation_timestamps():
    """Test validation timestamp updates."""
    from cortex_brain.onboarded_repos.profile_schema import RepositoryProfile
    
    # RED: Should track validation timestamps
    profile = RepositoryProfile(
        name="TRACKED_REPO",
        path="/path/to/tracked",
        onboarded_at=datetime.now()
    )
    
    # Update last validated
    new_validation_time = datetime.now()
    profile.last_validated = new_validation_time
    
    assert profile.last_validated == new_validation_time
    assert profile.last_validated > profile.onboarded_at
