"""
Governance Drift Checker for CORTEX System Optimization

Analyzes governance.yaml for rule ordering drift and inefficiencies.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

from pathlib import Path
from typing import Dict, Any
import logging
import yaml

logger = logging.getLogger(__name__)


class GovernanceDriftChecker:
    """
    Checks governance.yaml for ordering drift and inefficiencies.
    
    Monitors:
    - Rule position drift (rules moved from optimal positions)
    - Forward reference count (rules referencing later rules)
    - File bloat (excessive line count)
    - Orphaned rules (never referenced by other rules)
    - Missing metadata (copilot_position, reference_count missing)
    """
    
    # Optimal rule ordering (based on dependency graph and usage frequency)
    OPTIMAL_ORDER = [
        'DEFINITION_OF_DONE', 'DEFINITION_OF_READY', 'BRAIN_PROTECTION',
        'TEST_FIRST_TDD', 'CHALLENGE_USER_CHANGES_TO_BRAIN',
        'SINGLE_RESPONSIBILITY_PRINCIPLE', 'INTERFACE_SEGREGATION_PRINCIPLE',
        'DEPENDENCY_INVERSION_PRINCIPLE', 'DESIGN_PATTERNS_OVER_IMPROVISATION',
        'MODULAR_STRUCTURE', 'HEMISPHERE_SEPARATION', 'PLUGIN_ARCHITECTURE_FIRST',
        'TIER_BOUNDARIES', 'FIFO_QUEUE_MANAGEMENT', 'PATTERN_DECAY',
        'ANOMALY_DETECTION', 'DEV_CONTEXT_THROTTLING',
        'AUTO_BRAIN_STATE_UPDATE', 'AUTO_RECORDING', 'AUTO_GIT_COMMIT',
        'CHECKPOINT_STRATEGY', 'YAML_FOR_PLANNING', 'DUAL_INTERFACE',
        'LIVE_DESIGN_DOC', 'DELETE_NOT_ARCHIVE', 'ONE_PROMPT_PER_FILE',
        'GOVERNANCE_SELF_ENFORCEMENT', 'SYSTEM_LIMITS'
    ]
    
    def __init__(self, project_root: Path, validation_cache=None):
        self.project_root = project_root
        self._validation_cache = validation_cache
    
    def check(self) -> Dict[str, Any]:
        """
        Check governance.yaml for drift and inefficiencies.
        
        Returns:
            Dict with has_issues, issues list, health_score, and recommendations
        """
        governance_path = self.project_root / "src" / "tier0" / "governance.yaml"
        
        if not governance_path.exists():
            return {
                'has_issues': True,
                'issues': ["CRITICAL: governance.yaml not found"],
                'health_score': 0.0,
                'recommendations': ["Create governance.yaml in src/tier0/"]
            }
        
        # Try cache first
        if self._validation_cache:
            cache_key = "governance_drift_analysis"
            cached_result = self._validation_cache.get(
                "optimize",
                cache_key,
                files=[governance_path]
            )
            
            if cached_result is not None:
                logger.info("✅ Governance drift analysis retrieved from cache")
                return cached_result
        
        logger.info("🔄 Running governance drift analysis...")
        
        issues = []
        recommendations = []
        
        try:
            # Load governance rules
            with open(governance_path, 'r', encoding='utf-8') as f:
                governance = yaml.safe_load(f)
            
            rules = governance.get('rules', [])
            if not rules:
                return {
                    'has_issues': True,
                    'issues': ["CRITICAL: No rules found in governance.yaml"],
                    'health_score': 0.0,
                    'recommendations': ["Add governance rules"]
                }
            
            # Check 1: Rule position drift
            actual_order = [rule.get('id') for rule in rules]
            position_drifts = []
            
            for idx, rule_id in enumerate(actual_order, start=1):
                if rule_id in self.OPTIMAL_ORDER:
                    optimal_pos = self.OPTIMAL_ORDER.index(rule_id) + 1
                    if abs(idx - optimal_pos) > 3:  # More than 3 positions off
                        position_drifts.append(f"{rule_id}: actual pos {idx}, optimal pos {optimal_pos} (drift: {idx - optimal_pos})")
            
            if position_drifts:
                issues.append(f"POSITION DRIFT: {len(position_drifts)} rules out of optimal position")
                recommendations.append(f"Reorder {len(position_drifts)} drifted rules to optimal positions")
            
            # Check 2: Forward reference count
            forward_refs = []
            rule_ids = {rule.get('id'): idx for idx, rule in enumerate(rules)}
            
            for idx, rule in enumerate(rules):
                rule_id = rule.get('id')
                referenced_by = rule.get('referenced_by', [])
                
                for ref_id in referenced_by:
                    if ref_id in rule_ids:
                        ref_idx = rule_ids[ref_id]
                        if ref_idx < idx:  # Referencing rule appears BEFORE current rule
                            forward_refs.append(f"{ref_id} → {rule_id} (forward: {idx - ref_idx} positions)")
            
            if len(forward_refs) > 3:
                issues.append(f"FORWARD REFERENCES: {len(forward_refs)} detected (target: <3)")
                recommendations.append(f"Reduce forward references from {len(forward_refs)} to <3")
            
            # Check 3: File bloat
            with open(governance_path, 'r', encoding='utf-8') as f:
                line_count = len(f.readlines())
            
            if line_count > 1500:
                issues.append(f"FILE BLOAT: {line_count} lines (target: <1200)")
                recommendations.append("Remove redundant comments or split into focused sections")
            
            # Check 4: Orphaned rules
            all_referenced = set()
            for rule in rules:
                all_referenced.update(rule.get('referenced_by', []))
            
            orphaned = [rule.get('id') for rule in rules if rule.get('id') not in all_referenced and rule.get('reference_count', 0) == 0]
            
            if orphaned:
                issues.append(f"ORPHANED RULES: {len(orphaned)} never referenced")
                recommendations.append(f"Review orphaned rules: {', '.join(orphaned[:3])}")
            
            # Check 5: Missing metadata
            missing_metadata = []
            for rule in rules:
                rule_id = rule.get('id')
                if 'copilot_position' not in rule:
                    missing_metadata.append(f"{rule_id}: missing copilot_position")
                if 'reference_count' not in rule:
                    missing_metadata.append(f"{rule_id}: missing reference_count")
            
            if missing_metadata:
                issues.append(f"MISSING METADATA: {len(missing_metadata)} fields missing")
                recommendations.append(f"Add copilot_position and reference_count to all rules")
            
            # Calculate health score
            health_score = 100.0
            health_score -= len(position_drifts) * 2.0
            health_score -= max(0, len(forward_refs) - 3) * 5.0
            health_score -= max(0, (line_count - 1200) / 30)
            health_score -= len(orphaned) * 3.0
            health_score -= len(missing_metadata) * 1.0
            health_score = max(0.0, min(100.0, health_score))
            
            result = {
                'has_issues': len(issues) > 0,
                'issues': issues,
                'health_score': health_score,
                'recommendations': recommendations,
                'position_drifts': len(position_drifts),
                'forward_refs': len(forward_refs),
                'orphaned_rules': len(orphaned)
            }
            
            # Cache the result
            if self._validation_cache:
                self._validation_cache.set(
                    "optimize",
                    "governance_drift_analysis",
                    result,
                    files=[governance_path],
                    ttl_seconds=3600
                )
                logger.info("✅ Governance drift analysis cached")
            
            return result
        
        except Exception as e:
            logger.error(f"Governance drift check failed: {e}", exc_info=True)
            return {
                'has_issues': True,
                'issues': [f"ERROR: {str(e)}"],
                'health_score': 0.0,
                'recommendations': ["Fix governance.yaml parsing errors"]
            }
