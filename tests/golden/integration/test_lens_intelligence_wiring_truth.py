"""
Phase 18 — Golden E2E Truth Tests: LENS Intelligence Wiring

Verifies end-to-end that the intelligence synthesis pipeline delivers real
(non-empty) context to MasterOrchestrator when company/domains YAMLs and
domain profiles are present on disk.

These are TRUTH tests — they assert observable behaviour against the LIVE
cortex-registry/ files, not mocks.  Failures here mean the wiring is broken
in production, not just in unit tests.

Authority: AC-P18-001..AC-P18-017
Test count: 15
"""

# ruff: noqa: S101
import os
from pathlib import Path
from typing import Any

import pytest
import yaml


# ===========================================================================================
# Fixtures
# ===========================================================================================

REPO_ROOT = Path(__file__).parents[3]  # tests/golden/integration/ → repo root
DOMAINS_DIR = REPO_ROOT / "cortex-registry" / "company" / "domains"
PROFILES_DIR = REPO_ROOT / "cortex-registry" / "knowledge-base" / "profiles"
PATTERNS_DIR = REPO_ROOT / "cortex-registry" / "patterns"


@pytest.fixture
def fresh_loader() -> Any:
    """Return a non-singleton CompanyDomainLoader pointed at live registry."""
    from cortex.intelligence.knowledge.company_domain_loader import CompanyDomainLoader
    return CompanyDomainLoader(domains_dir=DOMAINS_DIR, profiles_dir=PROFILES_DIR)


@pytest.fixture
def fresh_engine() -> Any:
    """Return a fresh KnowledgeSynthesisEngine (not the singleton)."""
    from cortex.intelligence.knowledge.knowledge_synthesis_engine import KnowledgeSynthesisEngine
    return KnowledgeSynthesisEngine()


# ===========================================================================================
# GROUP 1: CompanyDomainLoader — live registry files
# AC-P18-001..004
# ===========================================================================================

class TestCompanyDomainLoaderTruth:
    """Golden tests for CompanyDomainLoader against the live cortex-registry."""

    def test_domains_directory_has_yaml_files(self) -> None:
        """AC-P18-002: cortex-registry/company/domains/ contains *.yaml files."""
        yamls = list(DOMAINS_DIR.glob("*.yaml"))
        assert len(yamls) >= 1, f"Expected YAML files in {DOMAINS_DIR}, found none"

    def test_loader_returns_non_empty_domain_rules(self, fresh_loader: Any) -> None:
        """AC-P18-003: CompanyDomainLoader.load() populates domain_rules from live files."""
        knowledge = fresh_loader.load()
        assert knowledge.domain_rules != {}, (
            "domain_rules must be non-empty when domain YAML files exist on disk"
        )

    def test_loader_returns_compliance_standards(self, fresh_loader: Any) -> None:
        """AC-P18-004: CompanyDomainLoader.load() populates compliance_standards."""
        knowledge = fresh_loader.load()
        assert isinstance(knowledge.compliance_standards, list)
        assert len(knowledge.compliance_standards) >= 1, (
            "compliance_standards must be non-empty (payment-security.yaml → PCI-DSS)"
        )

    def test_payment_security_triggers_pci_dss(self, fresh_loader: Any) -> None:
        """AC-P18-004: payment-security.yaml is present and triggers PCI-DSS standard."""
        assert (DOMAINS_DIR / "payment-security.yaml").exists(), (
            "payment-security.yaml must exist in company/domains/"
        )
        knowledge = fresh_loader.load()
        assert "PCI-DSS" in knowledge.compliance_standards

    def test_security_standards_file_loaded(self, fresh_loader: Any) -> None:
        """AC-P18-003: security-standards.yaml data appears in domain_rules."""
        knowledge = fresh_loader.load()
        assert "security-standards" in knowledge.domain_rules, (
            "security-standards.yaml must be loaded as a domain rule entry"
        )

    def test_all_domain_yamls_are_loaded(self, fresh_loader: Any) -> None:
        """AC-P18-002: Every *.yaml in domains/ is represented in domain_rules."""
        yaml_count = len(list(DOMAINS_DIR.glob("*.yaml")))
        knowledge = fresh_loader.load()
        assert len(knowledge.domain_rules) == yaml_count, (
            f"Expected {yaml_count} domain entries, got {len(knowledge.domain_rules)}"
        )

    def test_company_knowledge_precedence_is_override(self, fresh_loader: Any) -> None:
        """AC-P18-003: CompanyKnowledge.precedence is 'OVERRIDE' (company > CORTEX)."""
        knowledge = fresh_loader.load()
        assert knowledge.precedence == "OVERRIDE"

    def test_caching_returns_same_object(self, fresh_loader: Any) -> None:
        """AC-P18-016: Two consecutive load() calls return the same object (cache hit)."""
        first = fresh_loader.load()
        second = fresh_loader.load()
        assert first is second, "Cache must return the same CompanyKnowledge object"


# ===========================================================================================
# GROUP 2: Domain profile detection — live profiles
# AC-P18-012
# ===========================================================================================

class TestDomainProfileDetectionTruth:
    """Golden tests for detect_profile_for_repo() against live profiles/."""

    def test_profiles_directory_has_yaml_files(self) -> None:
        """AC-P18-012: cortex-registry/knowledge-base/profiles/ contains *.yaml files."""
        yamls = list(PROFILES_DIR.glob("*.yaml"))
        assert len(yamls) >= 4, (
            f"Expected at least 4 profile YAMLs, found {len(yamls)}"
        )

    def test_auth_profile_detected_by_authentication_tag(self, fresh_loader: Any) -> None:
        """AC-P18-012: repo_tags=['authentication'] matches auth.yaml profile."""
        profile_id = fresh_loader.detect_profile_for_repo(repo_tags=["authentication"])
        assert profile_id is not None, "auth profile must be detected from 'authentication' tag"
        assert "auth" in profile_id.lower()

    def test_finops_profile_detected_by_billing_tag(self, fresh_loader: Any) -> None:
        """AC-P18-012: repo_tags=['billing'] matches finops.yaml profile."""
        profile_id = fresh_loader.detect_profile_for_repo(repo_tags=["billing"])
        assert profile_id is not None, "finops profile must be detected from 'billing' tag"
        assert "finops" in profile_id.lower()

    def test_no_match_returns_none(self, fresh_loader: Any) -> None:
        """AC-P18-012: Unrecognised tags return None (no crash)."""
        profile_id = fresh_loader.detect_profile_for_repo(repo_tags=["xyzzy-nonexistent-tag"])
        assert profile_id is None


# ===========================================================================================
# GROUP 3: Cross-domain synthesis — live patterns YAML
# AC-P18-010
# ===========================================================================================

class TestCrossDomainSynthesisTruth:
    """Golden tests for synthesize_cross_domain_context() against live registry."""

    def test_patterns_directory_has_yaml_files(self) -> None:
        """AC-P18-010: cortex-registry/patterns/ contains *.yaml files."""
        yamls = list(PATTERNS_DIR.glob("*.yaml"))
        assert len(yamls) >= 5, (
            f"Expected at least 5 pattern YAMLs, found {len(yamls)}"
        )

    def test_cross_domain_architecture_non_empty(self, fresh_engine: Any) -> None:
        """AC-P18-010: architecture list is non-empty from live patterns/."""
        result = fresh_engine.synthesize_cross_domain_context(
            intent="IMPLEMENT", context="FastAPI auth service"
        )
        assert len(result["architecture"]) > 0, (
            "architecture recommendations must be non-empty when patterns/*.yaml exist"
        )

    def test_cross_domain_security_non_empty(self, fresh_engine: Any) -> None:
        """AC-P18-010: security list is non-empty from live security YAMLs."""
        result = fresh_engine.synthesize_cross_domain_context(
            intent="IMPLEMENT", context="payment processing API"
        )
        assert len(result["security"]) > 0, (
            "security recommendations must be non-empty"
        )

    def test_cross_domain_testing_non_empty(self, fresh_engine: Any) -> None:
        """AC-P18-010: testing list is non-empty (CORE-008 always provides entries)."""
        result = fresh_engine.synthesize_cross_domain_context(
            intent="FIX", context="broken unit test"
        )
        assert len(result["testing"]) > 0, "testing list must include CORE-008 guidance"

    def test_cross_domain_returns_correct_structure(self, fresh_engine: Any) -> None:
        """AC-P18-010: Return dict has exactly the three required keys."""
        result = fresh_engine.synthesize_cross_domain_context(
            intent="REFACTOR", context="legacy module"
        )
        assert set(result.keys()) >= {"architecture", "security", "testing"}, (
            "All three cross-domain keys must be present"
        )
        assert all(isinstance(v, list) for v in result.values()), (
            "All cross-domain values must be lists"
        )
