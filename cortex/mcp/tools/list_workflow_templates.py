"""cortex_list_workflow_templates — MCP tool for workflow template discovery.

Exposes the workflow template catalogue to Copilot Chat, enabling users to
discover available templates by category, view template details, and understand
which orchestrators consume which templates.

Phase: 23 — Workflow Template Injection (AC-P23-008)
CORE: CORE-011 (type hints), CORE-012 (docstrings), CORE-035 (single canonical)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def cortex_list_workflow_templates(
    category: Optional[str] = None,
    template_id: Optional[str] = None,
    orchestrator_context: Optional[Any] = None,
) -> Dict[str, Any]:
    """List available workflow templates from the CORTEX template registry.

    Supports three query modes:
    1. **List all**: No args — returns full catalogue summary.
    2. **Filter by category**: ``category="tdd"`` — returns templates in that category.
    3. **Load specific**: ``template_id="tdd/feature-implementation"`` — returns full template.

    Args:
        category:
            Optional category filter (e.g., 'tdd', 'security', 'lifecycle',
            'quality', 'frontend', 'backend', 'governance', 'maintenance').
        template_id:
            Optional specific template ID to load in full detail.
        orchestrator_context:
            MCP orchestrator context (optional, for routing validation).

    Returns:
        Dict with 'status', 'templates' (list), 'count', and 'orchestrator_mapping'.

    Examples:
        >>> result = cortex_list_workflow_templates()
        >>> result["count"]  # total templates available
        >>> result = cortex_list_workflow_templates(category="tdd")
        >>> result = cortex_list_workflow_templates(template_id="tdd/feature-implementation")
    """
    # Guard orchestrator context (allows direct test invocation)
    if orchestrator_context is not None:
        try:
            from cortex.mcp.tools._shared import validate_orchestrator_context
            validate_orchestrator_context(orchestrator_context)
        except ImportError:
            pass

    try:
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin

        mixin = WorkflowTemplateMixin()

        # Mode 3: Load specific template
        if template_id:
            try:
                template = mixin.load_template(template_id)
                return {
                    "status": "success",
                    "mode": "detail",
                    "template": template,
                    "count": 1,
                    "orchestrator_mapping": WorkflowTemplateMixin.TEMPLATE_ORCHESTRATOR_MAP,
                }
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e),
                    "count": 0,
                    "available_templates": [
                        t["id"] for t in mixin.discover_templates()
                    ],
                }

        # Mode 1 or 2: List templates (optionally filtered by category)
        templates = mixin.discover_templates(category=category)
        company_templates = mixin.discover_company_templates()

        return {
            "status": "success",
            "mode": "list",
            "templates": templates,
            "count": len(templates),
            "company_templates": company_templates,
            "company_count": len(company_templates),
            "categories": sorted(set(t.get("category", "general") for t in templates)),
            "orchestrator_mapping": WorkflowTemplateMixin.TEMPLATE_ORCHESTRATOR_MAP,
        }

    except Exception as e:
        logger.exception("cortex_list_workflow_templates failed")
        return {
            "status": "error",
            "error": str(e),
            "count": 0,
        }
