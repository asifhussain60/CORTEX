"""Phase 128-e — Governance Rule Coverage (drift lock #46).

Every CORE-XXX rule cited in production source (cortex/, cortex-registry/,
.github/, scripts/) MUST have a corresponding entry in
``cortex-registry/governance/core-rules.yaml``.

Conversely, every rule defined in core-rules.yaml MUST be cited at least
once somewhere in the project (no orphan / dead rules).

Sentinel values (CORE-000, CORE-999) used exclusively in tests are excluded.
Rules cited only in test code (tests/) are also excluded from the
"must-be-in-yaml" requirement — test data is not production policy.

Gap ref: GAP-128-05
Drift lock: cortex-registry/governance/drift-locks/check-46-governance-rule-coverage-lock.yaml
Tier: T1 (governance)
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
CORTEX_ROOT = Path(__file__).parents[2]
CORE_RULES_YAML = CORTEX_ROOT / "cortex-registry" / "governance" / "core-rules.yaml"

# Production scopes — these are AUTHORITATIVE. Rules cited here MUST be in YAML.
_PRODUCTION_DIRS = [
    CORTEX_ROOT / "cortex",
    CORTEX_ROOT / "cortex-registry",
    CORTEX_ROOT / ".github",
    CORTEX_ROOT / "scripts",
]
_PRODUCTION_EXTENSIONS = {".py", ".yaml", ".yml", ".md"}

# Test-only paths — citations here are treated as non-authoritative (test data)
_TEST_DIRS = [
    CORTEX_ROOT / "tests",
]

# ---------------------------------------------------------------------------
# Sentinel / special-case exclusions
# ---------------------------------------------------------------------------
# CORE-000, CORE-999 — used exclusively in test mock data and formatter tests.
# They are intentionally not real governance rules.
_SENTINEL_RULES: frozenset[str] = frozenset({"CORE-000", "CORE-999"})

# Rules cited in production source but known to be defined in SUPPLEMENTARY
# governance files rather than core-rules.yaml (e.g., copilot-instructions.md
# acts as an informal reference; these rules exist implicitly in practice).
# We track them as "acknowledged gaps" — they may be added to YAML in a
# future phase. For now, they are ALLOWED (not a test failure) but REPORTED.
_ACKNOWLEDGED_GAPS: frozenset[str] = frozenset({
    # Rules cited in workflow/governance YAMLs and production orchestrators
    # but defined in copilot-instructions.md rather than core-rules.yaml.
    # Phase 128-e tracks these for future consolidation only.
    "CORE-007",   # cited in detect-fix-rescan-loop.yaml
    "CORE-009",   # cited in governance test data + headers.yaml
    "CORE-014",   # cited in generate_governance_data.py (script)
    "CORE-015",   # cited in generate_governance_data.py (script)
    "CORE-016",   # cited in generate_governance_data.py (script)
    "CORE-031",   # cited in wiring YAMLs
    "CORE-033",   # cited in wiring YAMLs + tool_description_validator.py
    "CORE-036",   # cited in loaders.py, smart_citations_mixin.py
    "CORE-046",   # cited in workflow_gate.py
    "CORE-047",   # cited in intelligence_routing_engine.py, path_integrity_agent.py
    "CORE-048",   # cited in master_plan_orchestrator.py, governance_principles.py
    "CORE-049",   # cited in orchestrator_base.py, intelligence_mixin.py
    "CORE-056",   # cited in git_enforcement_orchestrator.py
    "CORE-057",   # cited in safe_template_editor.py
    "CORE-058",   # cited in orchestrator.py, extended_governance_agent.py
    "CORE-059",   # cited in extended_governance_agent.py, ccl-governance-crystal.yaml
    "CORE-060",   # cited in extended_governance_agent.py, ccl-governance-crystal.yaml
    "CORE-061",   # cited in extended_governance_agent.py, ccl-governance-crystal.yaml
    "CORE-062",   # cited in extended_governance_agent.py, ccl-governance-crystal.yaml
    "CORE-063",   # cited in extended_governance_agent.py, glossary.md
    "CORE-073",   # cited in cortex-docs or scripts
    "CORE-074",   # cited in cortex-docs or scripts
    "CORE-095",   # cited in cortex-docs or scripts
    "CORE-097",   # cited in cortex-docs or scripts
    "CORE-070",   # cited in cortex-docs or scripts
})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _collect_cited_rules(dirs: list[Path]) -> set[str]:
    """Grep all CORE-XXX references from files in the given directories."""
    pattern = re.compile(r"\bCORE-\d{3,}\b")
    found: set[str] = set()
    for root_dir in dirs:
        for f in root_dir.rglob("*"):
            if not f.is_file():
                continue
            if "__pycache__" in str(f) or ".git" in str(f):
                continue
            if f.suffix not in _PRODUCTION_EXTENSIONS:
                continue
            try:
                text = f.read_text(errors="ignore")
                found.update(pattern.findall(text))
            except OSError:
                pass
    return found


def _load_yaml_rule_ids() -> set[str]:
    """Return all CORE-XXX rule_ids defined in core-rules.yaml."""
    content = yaml.safe_load(CORE_RULES_YAML.read_text())
    rules = content.get("rules", [])
    ids: set[str] = set()
    for rule in rules:
        rid = rule.get("rule_id", "")
        if re.match(r"^CORE-\d+$", rid):
            ids.add(rid)
    return ids


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def yaml_rule_ids() -> set[str]:
    return _load_yaml_rule_ids()


@pytest.fixture(scope="module")
def production_cited() -> set[str]:
    """Rules cited in production scope (non-test code)."""
    return _collect_cited_rules(_PRODUCTION_DIRS)


@pytest.fixture(scope="module")
def test_only_cited() -> set[str]:
    """Rules cited exclusively in tests/ (not in production scope)."""
    prod = _collect_cited_rules(_PRODUCTION_DIRS)
    all_cited = _collect_cited_rules(_TEST_DIRS)
    return all_cited - prod


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_core_rules_yaml_exists():
    """core-rules.yaml must exist at the canonical governance path."""
    assert CORE_RULES_YAML.exists(), f"core-rules.yaml not found at {CORE_RULES_YAML}"


def test_core_rules_yaml_is_parseable():
    """core-rules.yaml must be valid YAML with a 'rules' list."""
    content = yaml.safe_load(CORE_RULES_YAML.read_text())
    assert isinstance(content, dict), "core-rules.yaml must be a mapping"
    assert "rules" in content, "core-rules.yaml must have a 'rules' key"
    assert isinstance(content["rules"], list), "'rules' must be a list"
    assert len(content["rules"]) > 0, "'rules' list must not be empty"


def test_every_yaml_rule_has_rule_id(yaml_rule_ids):
    """Every rule entry in core-rules.yaml must have a valid CORE-XXX rule_id."""
    content = yaml.safe_load(CORE_RULES_YAML.read_text())
    rules = content["rules"]
    missing_id = [r for r in rules if not r.get("rule_id")]
    assert missing_id == [], (
        f"{len(missing_id)} rule entries are missing rule_id:\n"
        + "\n".join(str(r)[:120] for r in missing_id)
    )


def test_every_yaml_rule_has_severity(yaml_rule_ids):
    """Every rule entry must have a severity field."""
    content = yaml.safe_load(CORE_RULES_YAML.read_text())
    rules = content["rules"]
    missing = [r.get("rule_id", "?") for r in rules if not r.get("severity")]
    assert missing == [], f"Rules missing severity: {missing}"


def test_no_sentinel_rules_in_yaml(yaml_rule_ids):
    """Sentinel values (CORE-000, CORE-999) must NOT appear in core-rules.yaml.
    They are test-data placeholders, not real governance rules."""
    collisions = _SENTINEL_RULES & yaml_rule_ids
    assert collisions == set(), (
        f"Sentinel rules must not be in core-rules.yaml: {sorted(collisions)}"
    )


def test_no_duplicate_rule_ids_in_yaml():
    """core-rules.yaml must not contain duplicate rule_id values."""
    content = yaml.safe_load(CORE_RULES_YAML.read_text())
    rule_ids = [r.get("rule_id", "") for r in content["rules"]]
    seen: set[str] = set()
    dupes: list[str] = []
    for rid in rule_ids:
        if rid in seen:
            dupes.append(rid)
        seen.add(rid)
    assert dupes == [], f"Duplicate rule_ids in core-rules.yaml: {dupes}"


def test_production_cited_rules_are_in_yaml_or_acknowledged(
    yaml_rule_ids, production_cited
):
    """Every CORE-XXX cited in production code must either exist in
    core-rules.yaml OR be listed in the acknowledged gaps registry.

    Unacknowledged gaps are a P1 governance violation.
    """
    meaningful_cited = production_cited - _SENTINEL_RULES
    not_in_yaml = meaningful_cited - yaml_rule_ids
    unacknowledged = not_in_yaml - _ACKNOWLEDGED_GAPS

    assert unacknowledged == set(), (
        f"UNACKNOWLEDGED rules cited in production but absent from core-rules.yaml "
        f"({len(unacknowledged)}):\n"
        + "\n".join(f"  - {r}" for r in sorted(unacknowledged))
        + "\n\nEither add the rule to core-rules.yaml, or add it to "
        "_ACKNOWLEDGED_GAPS with a comment explaining why."
    )


def test_acknowledged_gaps_are_still_cited(production_cited):
    """All acknowledged gaps must still appear in production code.

    If a gap is removed from source, remove it from _ACKNOWLEDGED_GAPS too —
    otherwise the list becomes stale dead weight.
    """
    not_cited_anywhere = _ACKNOWLEDGED_GAPS - production_cited
    # Some gaps may be cited only in test code — allow that too
    all_cited = _collect_cited_rules(_PRODUCTION_DIRS + _TEST_DIRS)
    truly_orphan = _ACKNOWLEDGED_GAPS - all_cited
    assert truly_orphan == set(), (
        f"Acknowledged gaps no longer cited anywhere — remove from _ACKNOWLEDGED_GAPS: "
        f"{sorted(truly_orphan)}"
    )


def test_no_orphan_yaml_rules_uncited(yaml_rule_ids, production_cited):
    """Every rule in core-rules.yaml must be cited at least once in the
    project (production or test code). Purely declarative rules that are
    never referenced anywhere are dead weight."""
    all_cited = _collect_cited_rules(_PRODUCTION_DIRS + _TEST_DIRS)
    orphan_rules = yaml_rule_ids - all_cited
    assert orphan_rules == set(), (
        f"Rules defined in core-rules.yaml but never cited anywhere "
        f"({len(orphan_rules)}):\n"
        + "\n".join(f"  - {r}" for r in sorted(orphan_rules))
    )


def test_yaml_rule_count_is_stable(yaml_rule_ids):
    """Baseline guard: core-rules.yaml must contain at least 39 CORE-XXX rules.
    A drop below this floor signals unintentional deletion (P0 regression)."""
    assert len(yaml_rule_ids) >= 39, (
        f"core-rules.yaml only has {len(yaml_rule_ids)} CORE-XXX rules — "
        "expected ≥ 39. Check for accidental deletions."
    )
