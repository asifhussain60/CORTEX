"""
Phase 18 Sub-Phase A — TDD RED Tests: CompanyDomainLoader

Tests written BEFORE implementation (CORE-008 mandate).
All tests must FAIL (ImportError / AttributeError) before company_domain_loader.py exists.

Authority: AC-P18-001 through AC-P18-004, AC-P18-012, AC-P18-016
Coverage: 10 unit tests for CompanyDomainLoader
"""

# ruff: noqa: S101
import time
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest
import yaml


# ===========================================================================================
# AC-P18-001: Importable from canonical module path
# ===========================================================================================

def test_company_domain_loader_is_importable() -> None:
    """AC-P18-001: CompanyDomainLoader importable from cortex.intelligence.knowledge."""
    from cortex.intelligence.knowledge.company_domain_loader import CompanyDomainLoader  # noqa: F401


def test_load_function_is_importable() -> None:
    """AC-P18-001: get_company_domain_loader factory importable from canonical module."""
    from cortex.intelligence.knowledge.company_domain_loader import get_company_domain_loader  # noqa: F401


# ===========================================================================================
# AC-P18-002: Reads all *.yaml from cortex-registry/company/domains/
# ===========================================================================================

def test_load_reads_all_domain_yamls(tmp_path: Path) -> None:
    """AC-P18-002: Loader reads every *.yaml file in the company domains directory."""
    from cortex.intelligence.knowledge.company_domain_loader import CompanyDomainLoader

    # Arrange — two minimal domain YAML files
    (tmp_path / "security-standards.yaml").write_text(
        "name: security\nstandards:\n  authentication:\n  - Use OAuth 2.0\n"
    )
    (tmp_path / "payment-security.yaml").write_text(
        "name: payment\nstandards:\n  authorization:\n  - PCI-DSS required\n"
    )

    loader = CompanyDomainLoader(domains_dir=tmp_path)
    knowledge = loader.load()

    assert "security-standards" in knowledge.domain_rules or len(knowledge.domain_rules) >= 2


def test_load_ignores_non_yaml_files(tmp_path: Path) -> None:
    """AC-P18-002: Loader ignores .txt and .md files in domains directory."""
    from cortex.intelligence.knowledge.company_domain_loader import CompanyDomainLoader

    (tmp_path / "notes.txt").write_text("irrelevant text")
    (tmp_path / "README.md").write_text("# docs")
    (tmp_path / "security-standards.yaml").write_text(
        "name: security\nstandards:\n  auth:\n  - Use TLS\n"
    )

    loader = CompanyDomainLoader(domains_dir=tmp_path)
    knowledge = loader.load()

    # Only 1 YAML → exactly 1 domain entry
    assert len(knowledge.domain_rules) == 1


def test_load_with_empty_directory_returns_empty_knowledge(tmp_path: Path) -> None:
    """AC-P18-002: Empty domains directory → CompanyKnowledge with empty domain_rules."""
    from cortex.intelligence.knowledge.company_domain_loader import CompanyDomainLoader

    loader = CompanyDomainLoader(domains_dir=tmp_path)
    knowledge = loader.load()

    assert knowledge.domain_rules == {}
    assert knowledge.compliance_standards == []


# ===========================================================================================
# AC-P18-003: Populates CompanyKnowledge.domain_rules (non-empty dict)
# ===========================================================================================

def test_domain_rules_contains_standards_data(tmp_path: Path) -> None:
    """AC-P18-003: domain_rules dict contains parsed standards from each YAML."""
    from cortex.intelligence.knowledge.company_domain_loader import CompanyDomainLoader

    (tmp_path / "api-design.yaml").write_text(
        "name: api-design\nstandards:\n  versioning:\n  - Use /v1/ prefix\n  - Semantic versioning\n"
    )

    loader = CompanyDomainLoader(domains_dir=tmp_path)
    knowledge = loader.load()

    assert len(knowledge.domain_rules) > 0
    # At least one key should map to a non-empty value
    assert any(v for v in knowledge.domain_rules.values())


# ===========================================================================================
# AC-P18-004: Populates CompanyKnowledge.compliance_standards (non-empty list)
# ===========================================================================================

def test_payment_yaml_sets_pci_dss_compliance(tmp_path: Path) -> None:
    """AC-P18-004: payment-security.yaml triggers PCI-DSS in compliance_standards."""
    from cortex.intelligence.knowledge.company_domain_loader import CompanyDomainLoader

    (tmp_path / "payment-security.yaml").write_text(
        "name: payment-security\nstandards:\n  authorization:\n  - PCI-DSS required\n"
    )

    loader = CompanyDomainLoader(domains_dir=tmp_path)
    knowledge = loader.load()

    assert "PCI-DSS" in knowledge.compliance_standards


def test_security_yaml_sets_security_compliance(tmp_path: Path) -> None:
    """AC-P18-004: security-standards.yaml triggers SECURITY in compliance_standards."""
    from cortex.intelligence.knowledge.company_domain_loader import CompanyDomainLoader

    (tmp_path / "security-standards.yaml").write_text(
        "name: security-standards\nstandards:\n  authentication:\n  - Use MFA\n"
    )

    loader = CompanyDomainLoader(domains_dir=tmp_path)
    knowledge = loader.load()

    assert len(knowledge.compliance_standards) >= 1


# ===========================================================================================
# AC-P18-016: 5-minute TTL cache (CORE-035 canonical cache pattern)
# ===========================================================================================

def test_loader_caches_result_on_second_call(tmp_path: Path) -> None:
    """AC-P18-016: Second call to load() returns cached CompanyKnowledge (same object)."""
    from cortex.intelligence.knowledge.company_domain_loader import CompanyDomainLoader

    (tmp_path / "security-standards.yaml").write_text(
        "name: security-standards\nstandards:\n  auth:\n  - Use OAuth\n"
    )

    loader = CompanyDomainLoader(domains_dir=tmp_path)
    first = loader.load()
    second = loader.load()

    # Same object identity — no re-read from disk
    assert first is second


def test_loader_has_ttl_attribute(tmp_path: Path) -> None:
    """AC-P18-016: Loader exposes cache_ttl_seconds attribute (5 min = 300s)."""
    from cortex.intelligence.knowledge.company_domain_loader import CompanyDomainLoader

    loader = CompanyDomainLoader(domains_dir=tmp_path)

    assert hasattr(loader, "cache_ttl_seconds")
    assert loader.cache_ttl_seconds == 300


def test_loader_cache_expires_after_ttl(tmp_path: Path) -> None:
    """AC-P18-016: Stale cache (past TTL) triggers fresh read from disk."""
    from cortex.intelligence.knowledge.company_domain_loader import CompanyDomainLoader

    (tmp_path / "security-standards.yaml").write_text(
        "name: security-standards\nstandards:\n  auth:\n  - Use OAuth\n"
    )

    loader = CompanyDomainLoader(domains_dir=tmp_path)
    first = loader.load()

    # Manually expire the cache
    loader._cache_timestamp = 0.0

    # Write a new file — fresh load should pick it up
    (tmp_path / "payment-security.yaml").write_text(
        "name: payment-security\nstandards:\n  payments:\n  - PCI-DSS\n"
    )
    second = loader.load()

    # Different object after expiry
    assert first is not second


# ===========================================================================================
# AC-P18-012: Domain profile tag-matching (auth/finops/devops/ml/healthcare/legal)
# ===========================================================================================

def test_detect_profile_by_tags_returns_matching_profile(tmp_path: Path) -> None:
    """AC-P18-012: detect_profile_for_repo() returns profile name when repo tags match."""
    from cortex.intelligence.knowledge.company_domain_loader import CompanyDomainLoader

    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()

    # Minimal auth profile YAML
    (profiles_dir / "auth.yaml").write_text(
        "profile:\n  id: auth-v1.0\n  tags:\n  - authentication\n  - identity\n"
    )
    (profiles_dir / "finops.yaml").write_text(
        "profile:\n  id: finops-v1.0\n  tags:\n  - finance\n  - billing\n"
    )

    loader = CompanyDomainLoader(
        domains_dir=tmp_path,
        profiles_dir=profiles_dir,
    )
    result = loader.detect_profile_for_repo(repo_tags=["billing", "cost-management"])

    assert result == "finops-v1.0"
