"""
KSE loaders — YAML loading and extraction functions.

Phase 103-g: extracted from knowledge_synthesis_engine.py (1,567L) god-object.
"""
from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml

logger = logging.getLogger(__name__)

# Canonical INDEX.yaml path (GAP-57-01)
KNOWLEDGE_INDEX_PATH: str = str(
    Path(__file__).parent.parent.parent.parent.parent
    / "cortex-registry"
    / "knowledge"
    / "INDEX.yaml"
)

_INTENT_MAPPINGS: Dict[str, List[str]] = {
    "IMPLEMENT": [
        "testing-validation/tdd-best-practices.yaml",
        "backend-python/clean-code.yaml",
        "security/secure-coding-practices.yaml",
        "architecture/engineering-design-patterns.yaml",
        "architecture/engineering-solid-principles.yaml",
    ],
    "FIX": [
        "testing-validation/tdd-best-practices.yaml",
        "backend-python/code-review.yaml",
        "security/secure-coding-practices.yaml",
        "architecture/engineering-anti-patterns.yaml",
        "backend-python/refactoring.yaml",
    ],
    "REFACTOR": [
        "backend-python/refactoring.yaml",
        "architecture/engineering-solid-principles.yaml",
        "architecture/refactoring-quality-standards.yaml",
        "backend-python/clean-code.yaml",
        "architecture/engineering-anti-patterns.yaml",
    ],
    "ANALYZE": [
        "backend-python/code-review.yaml",
        "architecture/engineering-anti-patterns.yaml",
        "devops-infrastructure/monitoring-observability.yaml",
        "performance-optimization/profiling-analysis.yaml",
        "architecture/refactoring-quality-standards.yaml",
    ],
    "AUDIT": [
        "security/secure-coding-practices.yaml",
        "backend-python/code-review.yaml",
        "devops-infrastructure/monitoring-observability.yaml",
        "architecture/engineering-solid-principles.yaml",
        "architecture/engineering-anti-patterns.yaml",
    ],
    "DESIGN": [
        "architecture/engineering-design-patterns.yaml",
        "architecture/engineering-solid-principles.yaml",
        "architecture/engineering-anti-patterns.yaml",
        "architecture/refactoring-quality-standards.yaml",
    ],
    "SECURITY": [
        "security/secure-coding-practices.yaml",
        "backend-python/code-review.yaml",
        "testing-validation/tdd-best-practices.yaml",
    ],
    "PERFORMANCE": [
        "performance-optimization/profiling-analysis.yaml",
        "devops-infrastructure/monitoring-observability.yaml",
        "architecture/engineering-anti-patterns.yaml",
    ],
}


def get_core_rules() -> Dict[str, Any]:
    """Return CORE governance rules as fallback."""
    return {
        "CORE-008": "TDD First - Write tests before implementation",
        "CORE-011": "Type Hints - All functions must have type annotations",
        "CORE-012": "Google-style Docstrings - Document all public methods",
        "CORE-013": "No Bare Except - Always specify exception types",
        "CORE-026": "Git Checkpoint - Commit before major changes",
        "CORE-027": "Audit Trail - Log AC_START and AC_COMPLETE",
        "CORE-029": "Response Header - Include CORTEX header in responses",
        "CORE-030": "Implementation Truth - Verify code, not docs",
        "CORE-035": "Single Implementation - One canonical implementation",
        "CORE-036": "Industry Standards - Comply with 12-Factor, SOLID, Clean Code, OWASP",
    }


def map_intent_to_yamls(intent_type: str, index_data: Dict[str, Any]) -> List[str]:
    """Map intent type to applicable YAML file paths."""
    upper = intent_type.upper()
    if upper in _INTENT_MAPPINGS:
        return list(_INTENT_MAPPINGS[upper])
    return keyword_fallback_matching(intent_type, index_data)


def keyword_fallback_matching(intent_type: str, index_data: Dict[str, Any]) -> List[str]:
    """Fallback keyword-based matching when intent not explicitly mapped."""
    yaml_paths = []
    intent_lower = intent_type.lower()
    for cat_key in [
        "architecture", "backend-python", "security", "testing-validation",
        "performance-optimization", "devops-infrastructure",
        "migration", "operational-patterns", "governance", "profiles", "repositories",
    ]:
        for guide in index_data.get(cat_key, {}).get("guides", []):
            if any(intent_lower in kw.lower() for kw in guide.get("keywords", [])):
                yaml_paths.append(guide["path"])
    return yaml_paths[:5]


def extract_practices_from_yaml(yaml_data: Dict[str, Any], yaml_path: str) -> Dict[str, Any]:
    """Extract practices/rules/patterns from loaded YAML file."""
    practices: Dict[str, Any] = {}
    try:
        # v2.0 top-level blocks
        for block, prefix in [
            ("company_context", "company"),
            ("cortex_standards", "CORTEX_STD"),
            ("cortex_solid_gate", "SOLID_GATE"),
            ("automated_gate", "AUTO_GATE"),
            ("infrastructure_stack", "INFRA"),
            ("cortex_native_patterns", "PATTERN"),
            ("srp_targets", "SRP"),
        ]:
            if block in yaml_data and isinstance(yaml_data[block], dict):
                for k, v in yaml_data[block].items():
                    if isinstance(v, (str, int, float)):
                        practices[f"{prefix}:{k}"] = str(v)

        if "owasp_mitigations" in yaml_data:
            for oid, entry in yaml_data["owasp_mitigations"].items():
                if isinstance(entry, dict):
                    m = entry.get("mitigation") or entry.get("description", "")
                    if m:
                        practices[f"OWASP:{oid}"] = m

        if "slo_thresholds" in yaml_data:
            for k, v in yaml_data["slo_thresholds"].items():
                if isinstance(v, (int, float)):
                    practices[f"SLO:{k}"] = f"{v}ms threshold"

        if "severity" in yaml_data and isinstance(yaml_data["severity"], dict):
            for level, desc in yaml_data["severity"].items():
                if isinstance(desc, str):
                    practices[f"SEVERITY:{level}"] = desc

        if "cortex_anti_patterns" in yaml_data:
            for k, entry in yaml_data["cortex_anti_patterns"].items():
                if isinstance(entry, dict):
                    desc = entry.get("description", "")
                    fix = entry.get("fix", "")
                    practices[f"ANTI_PATTERN:{k}"] = f"{desc} Fix: {fix}".strip()

        # v1.0 strategies
        if "three_laws" in yaml_data and isinstance(yaml_data["three_laws"], dict):
            for k, v in yaml_data["three_laws"].items():
                if isinstance(v, dict) and "statement" in v:
                    practices[f"TDD:{k}"] = v["statement"]

        if "best_practices" in yaml_data:
            bp = yaml_data["best_practices"]
            if isinstance(bp, dict):
                for cat, cat_data in bp.items():
                    if isinstance(cat_data, dict):
                        for k, v in cat_data.items():
                            if isinstance(v, dict):
                                practices[f"{cat}:{k}"] = (v.get("description") or v.get("guideline") or str(v))[:100]
                            elif isinstance(v, str):
                                practices[f"{cat}:{k}"] = v
            elif isinstance(bp, list):
                for i, item in enumerate(bp):
                    if isinstance(item, dict):
                        k = item.get("name") or item.get("id") or f"BP{i}"
                        practices[k] = (item.get("description") or item.get("guideline") or str(item))[:100]

        for list_key, id_fields in [("practices", ["id", "name"]), ("rules", ["id", "name"]), ("patterns", ["name", "id"]), ("guidelines", ["name"])]:
            if list_key in yaml_data and isinstance(yaml_data[list_key], list):
                for i, item in enumerate(yaml_data[list_key]):
                    if isinstance(item, dict):
                        k = next((item[f] for f in id_fields if f in item), f"{yaml_path}:{list_key[0].upper()}{i}")
                        v = item.get("description") or item.get("guideline") or item.get("when_to_use") or item.get("name")
                        if v:
                            practices[k] = v
                    elif isinstance(item, str):
                        practices[f"{yaml_path}:{list_key[0].upper()}{i}"] = item

    except Exception as e:
        logger.warning(f"Failed to extract practices from {yaml_path}: {e}")
    return practices


def load_cortex_best_practices(
    intent_type: str,
    cache: Dict[str, Tuple[float, Dict[str, Any]]],
    index_path_override: str = "",
) -> Dict[str, Any]:
    """Load applicable CORTEX best practices from registry YAMLs."""
    cache_key = f"cortex_practices_{intent_type}"
    entry = cache.get(cache_key)
    if entry:
        ts, data = entry
        if time.time() - ts < 300:
            return data

    practices: Dict[str, Any] = {}
    try:
        path = Path(index_path_override or KNOWLEDGE_INDEX_PATH)
        if not path.exists():
            logger.warning(f"INDEX.yaml not found at {path}, using CORE rules only")
            return get_core_rules()

        with open(path, "r", encoding="utf-8") as f:
            index_data = yaml.safe_load(f) or {}

        yaml_paths = map_intent_to_yamls(intent_type, index_data)
        loaded = 0
        for rel_path in yaml_paths:
            full = path.parent / rel_path
            if full.exists():
                try:
                    with open(full, "r", encoding="utf-8") as f:
                        extracted = extract_practices_from_yaml(yaml.safe_load(f) or {}, rel_path)
                        practices.update(extracted)
                        loaded += 1
                except Exception as e:
                    logger.warning(f"Failed to load {rel_path}: {e}")

        practices.update(get_core_rules())
        logger.info(f"Loaded {len(practices)} practices from {loaded} YAML files for {intent_type}")
        cache[cache_key] = (time.time(), practices)
    except Exception as e:
        logger.error(f"Failed to load CORTEX best practices: {e}")
        practices = get_core_rules()

    return practices
