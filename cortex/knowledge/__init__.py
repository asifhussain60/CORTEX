"""
CORTEX Knowledge System
=======================

Unified knowledge repository for best practices, patterns, and domain expertise.

Components:
- best-practices/: 35+ YAML guides organized by technology stack and concern
- protocol/: Knowledge protocol definitions

Note: best-practices uses hyphen (kebab-case) per file naming policy.
Access YAML files directly via pathlib, not Python imports.

Examples::

    from pathlib import Path
    import yaml

    # Load guides directly
    guides_dir = Path(__file__).parent / "best-practices"
    with open(guides_dir / "python-backend.yaml") as f:
        guide = yaml.safe_load(f)

Authority: cortex_brain/tier3/knowledge/
Version: 2.1
Updated: 2026-01-28
"""

# No imports from best-practices (YAML files, not Python modules)

__all__: list[str] = []
