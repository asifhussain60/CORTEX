"""
Phase 19 — TDD RED Tests: Registry Expansion + Cleanup

All tests written BEFORE implementation (CORE-008 mandate).
Covers Sub-Phases A (architecture YAML), B (repo onboarding), C (stale pruning), D (metric baselines).

Authority: AC-P19-001..AC-P19-012
Coverage: 12 golden-style tests that verify registry folder contents and consumption
"""

# ruff: noqa: S101
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).parents[3]
ARCH_YAML = REPO_ROOT / "cortex-registry" / "knowledge-base" / "architecture" / "architecture-best-practices.yaml"
PROFILES_DIR = REPO_ROOT / "cortex-registry" / "knowledge-base" / "profiles"
REPO_YAML = REPO_ROOT / "cortex-registry" / "company" / "repos" / "cortex" / "repository.yaml"
BASELINES_DIR = REPO_ROOT / "cortex-registry" / "metrics" / "baselines"
SECURITY_OPS_YAML = PROFILES_DIR / "security-ops.yaml"


# ===========================================================================================
# AC-P19-001: architecture-best-practices.yaml exists and is non-empty
# ===========================================================================================

def test_architecture_best_practices_yaml_exists() -> None:
    """AC-P19-001: cortex-registry/knowledge-base/architecture/architecture-best-practices.yaml exists."""
    assert ARCH_YAML.exists(), f"Expected {ARCH_YAML} to exist"


def test_architecture_yaml_is_non_empty() -> None:
    """AC-P19-001: architecture-best-practices.yaml has non-empty patterns list."""
    assert ARCH_YAML.exists(), "YAML must exist before checking contents"
    data = yaml.safe_load(ARCH_YAML.read_text(encoding="utf-8"))
    patterns = data.get("patterns", [])
    assert len(patterns) >= 4, f"Expected ≥4 patterns, got {len(patterns)}"


def test_architecture_yaml_has_required_keys() -> None:
    """AC-P19-001: architecture-best-practices.yaml has metadata and patterns keys."""
    assert ARCH_YAML.exists()
    data = yaml.safe_load(ARCH_YAML.read_text(encoding="utf-8"))
    assert "metadata" in data, "Must have metadata block"
    assert "patterns" in data, "Must have patterns list"


# ===========================================================================================
# AC-P19-002: KnowledgeSynthesisEngine loads architecture YAML for IMPLEMENT/DESIGN intents
# ===========================================================================================

def test_synthesis_engine_loads_architecture_yaml_for_implement() -> None:
    """AC-P19-002: KnowledgeSynthesisEngine._load_architecture_patterns() returns non-empty for IMPLEMENT."""
    from cortex.intelligence.knowledge.knowledge_synthesis_engine import KnowledgeSynthesisEngine

    engine = KnowledgeSynthesisEngine()
    assert hasattr(engine, "_load_architecture_patterns"), (
        "KnowledgeSynthesisEngine must have _load_architecture_patterns()"
    )
    patterns = engine._load_architecture_patterns(intent="IMPLEMENT")
    assert len(patterns) > 0, "Must return architecture patterns for IMPLEMENT intent"


def test_synthesis_engine_loads_architecture_yaml_for_design() -> None:
    """AC-P19-002: _load_architecture_patterns() returns non-empty for DESIGN intent."""
    from cortex.intelligence.knowledge.knowledge_synthesis_engine import KnowledgeSynthesisEngine

    engine = KnowledgeSynthesisEngine()
    patterns = engine._load_architecture_patterns(intent="DESIGN")
    assert len(patterns) > 0, "Must return architecture patterns for DESIGN intent"


# ===========================================================================================
# AC-P19-003: All 7 domain profiles loaded (including new security-ops)
# ===========================================================================================

def test_security_ops_profile_exists() -> None:
    """AC-P19-003: security-ops.yaml profile file exists in knowledge-base/profiles/."""
    assert SECURITY_OPS_YAML.exists(), f"Expected {SECURITY_OPS_YAML}"


def test_seven_domain_profiles_present() -> None:
    """AC-P19-003: profiles/ directory contains 7 profiles (original 6 + security-ops)."""
    profiles = list(PROFILES_DIR.glob("*.yaml"))
    assert len(profiles) >= 7, (
        f"Expected ≥7 profile YAMLs (auth/finops/devops/ml/healthcare/legal/security-ops), "
        f"found {len(profiles)}: {[p.name for p in profiles]}"
    )


def test_security_ops_profile_has_valid_structure() -> None:
    """AC-P19-003: security-ops.yaml has profile.id, profile.tags, and rules blocks."""
    assert SECURITY_OPS_YAML.exists()
    data = yaml.safe_load(SECURITY_OPS_YAML.read_text(encoding="utf-8"))
    profile = data.get("profile", {})
    assert profile.get("id"), "Must have profile.id"
    assert profile.get("tags"), "Must have profile.tags"
    assert data.get("rules"), "Must have rules list"


# ===========================================================================================
# AC-P19-004: repository.yaml has architecture_type != "unknown"
# ===========================================================================================

def test_repository_yaml_architecture_type_not_unknown() -> None:
    """AC-P19-004: cortex/repository.yaml architecture_type is not 'unknown'."""
    assert REPO_YAML.exists(), f"Expected {REPO_YAML}"
    data = yaml.safe_load(REPO_YAML.read_text(encoding="utf-8"))
    arch_type = data.get("analysis", {}).get("architecture_type", "unknown")
    assert arch_type != "unknown", (
        f"architecture_type should not be 'unknown' after onboarding refresh, got: {arch_type}"
    )


# ===========================================================================================
# AC-P19-006: metrics/baselines/ populated with test count baseline
# ===========================================================================================

def test_metrics_baselines_directory_has_yaml() -> None:
    """AC-P19-006: cortex-registry/metrics/baselines/ contains at least one *.yaml."""
    yamls = list(BASELINES_DIR.glob("*.yaml"))
    assert len(yamls) >= 1, (
        f"Expected ≥1 baseline YAML in {BASELINES_DIR}, found none"
    )


def test_test_count_baseline_yaml_exists() -> None:
    """AC-P19-006: test-count-baseline.yaml exists in metrics/baselines/."""
    baseline = BASELINES_DIR / "test-count-baseline.yaml"
    assert baseline.exists(), f"Expected {baseline}"


def test_test_count_baseline_has_valid_threshold() -> None:
    """AC-P19-006: test-count-baseline.yaml has test_count and drift_threshold_pct fields."""
    baseline = BASELINES_DIR / "test-count-baseline.yaml"
    assert baseline.exists()
    data = yaml.safe_load(baseline.read_text(encoding="utf-8"))
    assert "test_count" in data, "Must have test_count field"
    assert "drift_threshold_pct" in data, "Must have drift_threshold_pct field"
    assert isinstance(data["drift_threshold_pct"], (int, float))
    assert 0 < data["drift_threshold_pct"] <= 100
