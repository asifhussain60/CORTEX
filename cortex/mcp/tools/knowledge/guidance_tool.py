# © 2025-2026 Asif Hussain. All rights reserved.
# AC-ID: AC-MCP-008 - TDD Guidance Tool
"""
MCP Tool: Get TDD Guidance for Module Implementation

AC-MCP-008: get_tdd_guidance_for_module
Purpose: Provide context-aware implementation guidance during TDD development

This tool queries the knowledge ecosystem (tier0/tier1/tier2 rules + tier3 synthesis)
to return applicable best practices, governance requirements, and domain-specific
patterns for a given module.

Authority: cortex_brain/tier3/knowledge/synthesis-config.yaml
CORE Governance:
  - CORE-008: TDD enforcement (tests before code)
  - CORE-011: Type safety (100% type hints)
  - CORE-012: Documentation (Google docstrings)
  - CORE-013: Exception handling (specific, no bare except)
"""

from typing import Dict, List, Any, Optional
from cortex.mcp.decorators import mcp_tool
from cortex.brain.core.knowledge_guidance_engine import (
    get_guidance_engine,
    GuidanceEntry,
    TierLevel
)


@mcp_tool(
    name="get_tdd_guidance_for_module",
    description="Get comprehensive TDD guidance for module implementation with tier-based precedence",
    parameters={
        "module_path": {
            "type": "string",
            "description": "Module path (e.g., 'cortex.orchestrators.domain_brain', 'cortex.knowledge.best_practices')",
            "required": True
        },
        "context": {
            "type": "object",
            "description": "Optional execution context with domain, operation_type, priority, etc.",
            "required": False,
            "properties": {
                "domain": {"type": "string", "description": "Domain name (overrides auto-detection)"},
                "operation_type": {"type": "string", "description": "Type of operation: 'implementation', 'refactoring', 'testing', etc."},
                "priority": {"type": "string", "description": "Priority level: 'P0-CRITICAL', 'P1-HIGH', 'P2-MEDIUM', 'P3-LOW'"},
                "related_domains": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Related domains for cross-domain pattern synthesis"
                }
            }
        }
    }
)
def get_tdd_guidance_for_module(
    module_path: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Get comprehensive TDD implementation guidance for a module.
    
    This tool integrates guidance from multiple sources in precedence order:
    1. Domain-specific overrides (company rules)
    2. TIER 0 governance rules (immutable core)
    3. TIER 1 governance rules (domain-specific)
    4. TIER 2 engineering standards
    5. CORTEX best practices (defaults)
    
    Plus cross-domain synthesis from tier3 knowledge engine.
    
    Args:
        module_path: Module path (e.g., "cortex.orchestrators.domain_brain")
        context: Optional execution context with domain, operation_type, etc.
    
    Returns:
        Dict containing:
            - module_path: Input module path
            - module_name: Extracted module name
            - domain: Detected or provided domain
            - guidance_entries: List of applicable guidance with tier info
            - tier_0_rules: Applicable TIER 0 (immutable) rules
            - tier_1_rules: Applicable TIER 1 (domain-specific) rules
            - tier_2_rules: Applicable TIER 2 (engineering) rules
            - domain_rules: Domain-specific override rules (highest precedence)
            - best_practices_guides: Applicable best practices YAML files
            - synthesis_insights: Cross-domain patterns from tier3
            - guidance_confidence: Confidence score (0.0-1.0)
            - generated_at: ISO timestamp when guidance was generated
            - summary: Human-readable summary of critical guidance
    
    Raises:
        ValueError: If module_path is empty or invalid
    
    Example:
        guidance = get_tdd_guidance_for_module(
            module_path="cortex.orchestrators.master_orchestrator",
            context={
                "domain": "orchestrators",
                "operation_type": "implementation",
                "priority": "P0-CRITICAL"
            }
        )
        
        # Returns:
        {
            "module_path": "cortex.orchestrators.master_orchestrator",
            "module_name": "master_orchestrator",
            "domain": "orchestrators",
            "guidance_entries": [
                {
                    "category": "tdd_discipline",
                    "title": "CORE-008: Test-Driven Development",
                    "priority": 1,
                    "tier": "TIER_0",
                    "related_rules": ["CORE-008", "CORE-027"]
                },
                ...
            ],
            "tier_0_rules": ["CORE-001", "CORE-008", "CORE-011", "CORE-012", "CORE-013"],
            "domain_rules": [],
            "best_practices_guides": [
                "best-practices/testing-validation/tdd-best-practices.yaml",
                "best-practices/architecture/ddd-bounded-contexts.yaml"
            ],
            "guidance_confidence": 0.95,
            "summary": "5 CRITICAL rules (TIER 0) + TDD discipline + 2 guides"
        }
    """
    if not module_path or not isinstance(module_path, str):
        raise ValueError("module_path must be non-empty string")
    
    # Get guidance engine singleton
    engine = get_guidance_engine()
    
    # Get comprehensive guidance for module
    guidance = engine.get_guidance_for_module(module_path, context)
    
    # Convert guidance entries to dict format
    guidance_entries_dict = []
    for entry in sorted(
        guidance.guidance_entries,
        key=lambda x: (x.tier.value, x.priority)
    ):
        guidance_entries_dict.append({
            "category": entry.category.value,
            "title": entry.title,
            "description": entry.description,
            "priority": entry.priority,
            "tier": entry.tier.name,
            "source": entry.source,
            "confidence": entry.confidence,
            "domain_specific": entry.domain_specific,
            "patterns": entry.patterns,
            "related_rules": entry.related_rules
        })
    
    # Build summary
    critical_count = sum(1 for e in guidance.guidance_entries if e.priority == 1)
    tier_0_count = len(guidance.tier_0_rules)
    domain_override_count = len(guidance.domain_rules)
    
    summary_parts = []
    if critical_count > 0:
        summary_parts.append(f"{critical_count} CRITICAL rules")
    if tier_0_count > 0:
        summary_parts.append(f"{tier_0_count} TIER 0 requirements")
    if domain_override_count > 0:
        summary_parts.append(f"{domain_override_count} domain overrides")
    if guidance.best_practices_guides:
        summary_parts.append(f"{len(guidance.best_practices_guides)} guides")
    
    summary = " + ".join(summary_parts) if summary_parts else "No specific guidance found"
    
    return {
        "module_path": guidance.module_path,
        "module_name": guidance.module_name,
        "domain": guidance.domain,
        "guidance_entries": guidance_entries_dict,
        "tier_0_rules": guidance.tier_0_rules,
        "tier_1_rules": guidance.tier_1_rules,
        "tier_2_rules": guidance.tier_2_rules,
        "domain_rules": guidance.domain_rules,
        "best_practices_guides": guidance.best_practices_guides,
        "synthesis_insights": guidance.synthesis_insights,
        "guidance_confidence": guidance.guidance_confidence,
        "generated_at": guidance.generated_at,
        "summary": summary,
        "recommended_reading_order": [
            entry["title"]
            for entry in guidance_entries_dict[:3]
        ]
    }
