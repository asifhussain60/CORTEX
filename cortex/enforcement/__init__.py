"""cortex.enforcement — Enforcement package.

MIGRATION NOTE (Phase 102-A):
This package is a thin namespace for governance enforcement agents.
The canonical enforcement implementation lives in:
  - cortex/governance/enforcement/  — governance-side enforcement agents
  - cortex/orchestrators/core/enforcement_orchestrator.py — orchestration layer

Active consumers:
  - cortex/mcp/tools/workflow_tools.py  (GovernanceEnforcementAgent)
  - cortex/orchestrators/health/agents/inventory_agent.py

Long-term: absorb into cortex.governance.enforcement namespace (Phase 102-B).
"""
from __future__ import annotations

__all__: list[str] = []
