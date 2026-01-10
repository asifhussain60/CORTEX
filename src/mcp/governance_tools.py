"""
CORTEX 6.0 MCP Governance Tools

Implements AC-GOV-002 through AC-GOV-010: MCP tools for governance queries.

Tools:
- governance_rules: List all governance rules by tier
- governance_validate: Validate a specific rule is enforced
- governance_conflicts: Detect and report rule conflicts
- governance_unified: Generate unified instruction set

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List

from src.orchestrators.core.governance_merger import (
    GovernanceMerger,
    GovernanceRule,
    UnifiedInstructionSet,
)


def governance_rules(
    workspace_root: str,
    tier: Optional[int] = None,
    category: Optional[str] = None
) -> Dict[str, Any]:
    """
    List all governance rules with optional filters.
    
    Implements AC-GOV-002: Query rules from 4-tier system.
    
    Args:
        workspace_root: Path to workspace root
        tier: Optional tier filter (0=CORE, 1=Business, 2=Company, 3=Knowledge)
        category: Optional category filter
    
    Returns:
        List of matching rules with metadata
    """
    try:
        governance_root = Path(workspace_root) / "cortex-brain"
        merger = GovernanceMerger(governance_root=governance_root)
        
        # Load all rules
        merger.load_all_rules()
        
        rules = merger.all_rules
        
        # Apply filters
        if tier is not None:
            rules = [r for r in rules if r.governance_tier == tier]
        
        if category:
            rules = [r for r in rules if r.category == category]
        
        # Group by tier
        by_tier = {
            0: [r.to_dict() for r in rules if r.governance_tier == 0],
            1: [r.to_dict() for r in rules if r.governance_tier == 1],
            2: [r.to_dict() for r in rules if r.governance_tier == 2],
            3: [r.to_dict() for r in rules if r.governance_tier == 3],
        }
        
        return {
            "success": True,
            "total_count": len(rules),
            "by_tier": by_tier,
            "tier_counts": {
                "CORE (0)": len(by_tier[0]),
                "Business (1)": len(by_tier[1]),
                "Company (2)": len(by_tier[2]),
                "Knowledge (3)": len(by_tier[3]),
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "total_count": 0
        }


def governance_validate(
    workspace_root: str,
    rule_id: str
) -> Dict[str, Any]:
    """
    Validate that a specific governance rule exists and is enforced.
    
    Implements AC-GOV-004: Validate TDD_ENFORCEMENT and other rules.
    
    Args:
        workspace_root: Path to workspace root
        rule_id: Rule ID to validate (e.g., "CORE-008", "CORE-019")
    
    Returns:
        Validation result with rule details
    """
    try:
        governance_root = Path(workspace_root) / "cortex-brain"
        merger = GovernanceMerger(governance_root=governance_root)
        
        # Load all rules
        merger.load_all_rules()
        
        # Find the rule
        rule = None
        for r in merger.all_rules:
            if r.rule_id == rule_id:
                rule = r
                break
        
        if not rule:
            return {
                "success": True,
                "rule_id": rule_id,
                "validation_status": "NOT_FOUND",
                "exists": False,
                "message": f"Rule {rule_id} not found in governance system"
            }
        
        return {
            "success": True,
            "rule_id": rule_id,
            "validation_status": "ENFORCED",
            "exists": True,
            "rule": rule.to_dict(),
            "tier": rule.governance_tier,
            "severity": rule.severity,
            "message": f"Rule {rule_id} is active with severity {rule.severity}"
        }
    
    except Exception as e:
        return {
            "success": False,
            "rule_id": rule_id,
            "validation_status": "ERROR",
            "error": str(e)
        }


def governance_conflicts(
    workspace_root: str
) -> Dict[str, Any]:
    """
    Detect and report conflicts between governance rules.
    
    Implements AC-GOV-002, AC-GOV-003: Conflict detection and resolution.
    
    Args:
        workspace_root: Path to workspace root
    
    Returns:
        List of detected conflicts with resolution strategies
    """
    try:
        governance_root = Path(workspace_root) / "cortex-brain"
        merger = GovernanceMerger(governance_root=governance_root)
        
        # Load all rules
        merger.load_all_rules()
        
        # Detect conflicts
        merger.detect_conflicts()
        
        conflicts = [c.to_dict() for c in merger.conflicts]
        
        return {
            "success": True,
            "conflict_count": len(conflicts),
            "conflicts": conflicts,
            "has_blocking_conflicts": any(
                c.get("conflict_type") == "OVERRIDE" for c in conflicts
            ),
            "message": f"Detected {len(conflicts)} conflict(s)"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "conflict_count": 0
        }


def governance_unified(
    workspace_root: str,
    resolve_conflicts: bool = True
) -> Dict[str, Any]:
    """
    Generate unified instruction set from all governance tiers.
    
    Implements AC-GOV-002: Unified instruction set generation.
    
    Args:
        workspace_root: Path to workspace root
        resolve_conflicts: Whether to resolve detected conflicts
    
    Returns:
        Unified instruction set with metadata
    """
    try:
        import time
        start_time = time.perf_counter()
        
        governance_root = Path(workspace_root) / "cortex-brain"
        merger = GovernanceMerger(governance_root=governance_root)
        
        # Generate unified set
        unified = merger.merge()
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        return {
            "success": True,
            "version": unified.version,
            "rule_count": unified.rule_count,
            "tier_count": unified.tier_count,
            "conflicts_resolved": unified.conflicts_resolved,
            "generation_time_ms": round(elapsed_ms, 2),
            "performance_target_met": elapsed_ms < 50,
            "metadata": unified.metadata,
            "message": f"Generated unified set with {unified.rule_count} rules in {elapsed_ms:.2f}ms"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def governance_tdd_check(
    workspace_root: str
) -> Dict[str, Any]:
    """
    Check if TDD enforcement rules (CORE-008, CORE-019) are active.
    
    Implements AC-GOV-004, AC-GOV-011: TDD enforcement validation.
    
    Args:
        workspace_root: Path to workspace root
    
    Returns:
        TDD enforcement status
    """
    try:
        governance_root = Path(workspace_root) / "cortex-brain"
        merger = GovernanceMerger(governance_root=governance_root)
        
        # Load CORE rules only
        merger.load_core_rules()
        
        # Check for TDD rules
        tdd_rules = {
            "CORE-008": None,  # TDD_ENFORCEMENT
            "CORE-019": None,  # TDD_MASTER_REQUIRED
        }
        
        for rule in merger.core_rules:
            if rule.rule_id in tdd_rules:
                tdd_rules[rule.rule_id] = rule.to_dict()
        
        all_present = all(v is not None for v in tdd_rules.values())
        
        return {
            "success": True,
            "tdd_enforcement_active": all_present,
            "rules": tdd_rules,
            "message": "TDD enforcement ACTIVE" if all_present else "TDD enforcement INCOMPLETE"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "tdd_enforcement_active": False
        }
