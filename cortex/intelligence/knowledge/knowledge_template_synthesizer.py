"""KnowledgeTemplateSynthesizer — generates CORTEX-format knowledge YAML templates.

Produces a 5-category best-practices knowledge YAML for a given domain and intent.
Output is always valid YAML parseable by ``yaml.safe_load()``.

Phase: 135-b (GAP-135-03)
CORE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
      CORE-035 (single canonical implementation)
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

import yaml

logger = logging.getLogger(__name__)

# ── Five canonical best-practice categories ───────────────────────────────────
_CATEGORIES: List[str] = [
    "Architecture",
    "Testing",
    "Performance",
    "Security",
    "Pitfalls",
]

# Per-domain seed content (graceful degradation to generic if domain unknown)
_DOMAIN_SEEDS: Dict[str, Dict[str, List[str]]] = {
    "testing-validation": {
        "Architecture": ["Separate test concerns into unit / integration / e2e layers", "Keep tests independent and hermetic"],
        "Testing": ["Follow RED-GREEN-REFACTOR strictly", "Use parameterized tests to cover edge cases"],
        "Performance": ["Run unit tests in parallel", "Mock external I/O to keep tests fast"],
        "Security": ["Never commit real credentials in test fixtures", "Test authorization boundaries explicitly"],
        "Pitfalls": ["Avoid testing implementation details", "Do not share mutable state between tests"],
    },
    "security": {
        "Architecture": ["Enforce least privilege at every layer", "Apply defence-in-depth"],
        "Testing": ["Include SAST / DAST in CI pipeline", "Test authentication and authorization paths explicitly"],
        "Performance": ["Benchmark cryptographic operations", "Cache access-control decisions where safe"],
        "Security": ["Follow OWASP Top 10 checklist", "Rotate secrets on a defined schedule"],
        "Pitfalls": ["Never roll your own crypto", "Avoid logging sensitive data"],
    },
    "backend-python": {
        "Architecture": ["Apply SOLID principles", "Use dependency injection for testability"],
        "Testing": ["Achieve ≥80% branch coverage on business logic", "Write contract tests for integrations"],
        "Performance": ["Profile before optimizing", "Use async I/O for network-bound operations"],
        "Security": ["Validate all external inputs via Pydantic", "Use parameterized queries — never string interpolation"],
        "Pitfalls": ["Avoid mutable default arguments", "Do not suppress bare except clauses"],
    },
    "architecture": {
        "Architecture": ["Prefer explicit over implicit boundaries", "Document architectural decisions in ADRs"],
        "Testing": ["Write architectural fitness tests", "Use contract tests for bounded contexts"],
        "Performance": ["Design for horizontal scaling from day one", "Measure before adding caching layers"],
        "Security": ["Apply zero-trust network model", "Audit third-party dependencies regularly"],
        "Pitfalls": ["Avoid big-ball-of-mud coupling", "Do not let bounded contexts share databases directly"],
    },
}

_GENERIC_SEEDS: Dict[str, List[str]] = {
    "Architecture": ["Apply separation of concerns", "Define clear module boundaries"],
    "Testing": ["Test behaviour, not implementation", "Cover happy path and edge cases"],
    "Performance": ["Measure first, optimize second", "Cache at the right layer"],
    "Security": ["Validate all inputs", "Follow principle of least privilege"],
    "Pitfalls": ["Avoid premature optimization", "Do not ignore error cases"],
}


class KnowledgeTemplateSynthesizer:
    """Generates CORTEX-format knowledge YAML templates for a given domain.

    Produces a YAML string with:
    - ``title``, ``domain`` top-level fields
    - ``best_practices`` list of 5 category dicts (Architecture / Testing /
      Performance / Security / Pitfalls)
    - ``cortex_alignment`` block (source / phase / intent / confidence)

    Usage::

        synth = KnowledgeTemplateSynthesizer()
        yaml_str = synth.synthesize(domain="security", intent="AUDIT")
        parsed = yaml.safe_load(yaml_str)  # always valid
    """

    def synthesize(self, domain: str, intent: str = "IMPLEMENT") -> str:
        """Generate a CORTEX knowledge YAML string for *domain*.

        Args:
            domain: Target knowledge domain (e.g. ``"security"``, ``"backend-python"``).
            intent: Triggering intent context (e.g. ``"IMPLEMENT"``, ``"AUDIT"``).

        Returns:
            YAML string with ``title``, ``domain``, ``best_practices``, and
            ``cortex_alignment`` sections.
        """
        seeds = _DOMAIN_SEEDS.get(domain, _GENERIC_SEEDS)

        best_practices: List[Dict[str, Any]] = []
        for category in _CATEGORIES:
            items = seeds.get(category, _GENERIC_SEEDS.get(category, ["Apply best practices"]))
            best_practices.append({"category": category, "items": list(items)})

        doc: Dict[str, Any] = {
            "title": f"{domain.replace('-', ' ').title()} Best Practices",
            "domain": domain,
            "best_practices": best_practices,
            "cortex_alignment": {
                "source": "synthesized",
                "phase": "135",
                "intent": intent,
                "confidence": 0.70,
            },
        }

        return yaml.dump(doc, default_flow_style=False, allow_unicode=True)
