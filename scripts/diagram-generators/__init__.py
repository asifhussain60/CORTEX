"""
Diagram generators for CORTEX documentation visualizations.

This module contains data generators for D3.js and Mermaid diagrams
used in CORTEX system documentation.

Generators:
  - generate-governance-data.py: Governance pyramid visualization
  - generate-lifecycle-data.py: Request lifecycle Sankey flow
  - generate-tdd-cycle-data.py: TDD knowledge cycle
"""

__version__ = "1.0.0"
__all__ = [
    "generate_governance_data",
    "generate_lifecycle_data",
    "generate_tdd_cycle_data",
]
