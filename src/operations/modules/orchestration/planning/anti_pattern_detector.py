"""
Anti-Pattern Detection for Planning System 3.0

Prevents repeated mistakes by checking plans against historical failures.

Part of Phase 4: Historical Context Integration
Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""
from typing import Dict, List, Any
import logging
from pathlib import Path
import yaml

class AntiPatternDetector:
    """Detects anti-patterns in planning phase."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.anti_pattern_db = self._load_anti_patterns()
    
    def _load_anti_patterns(self) -> Dict[str, Any]:
        """
        Load anti-pattern database from knowledge graph.
        
        Returns:
            Dict of known anti-patterns with severity and impact
        """
        # Load from knowledge-graph.yaml if exists, otherwise use defaults
        kg_path = Path("cortex-brain/knowledge-graph.yaml")
        
        default_patterns = {
            'skip_red_phase': {
                'severity': 'critical',
                'description': 'Skipping RED phase in TDD',
                'occurrences': 0,
                'impact': 'Tests that never fail = untested code',
                'detection_rules': ['missing_red_phase', 'no_failing_tests']
            },
            'premature_optimization': {
                'severity': 'high',
                'description': 'Optimizing before working implementation',
                'occurrences': 0,
                'impact': 'Wasted effort, increased complexity',
                'detection_rules': ['optimization_before_implementation']
            },
            'monolithic_phase': {
                'severity': 'high',
                'description': 'Phase >24h without checkpoints',
                'occurrences': 0,
                'impact': 'Risk of failure, hard to roll back',
                'detection_rules': ['phase_duration_exceeds_24h']
            },
            'missing_acceptance_criteria': {
                'severity': 'high',
                'description': 'Plan lacks acceptance criteria',
                'occurrences': 0,
                'impact': 'Unclear success conditions, scope creep',
                'detection_rules': ['no_acceptance_criteria']
            },
            'untested_implementation': {
                'severity': 'critical',
                'description': 'Implementation without test coverage',
                'occurrences': 0,
                'impact': 'Unknown bugs, regression risk',
                'detection_rules': ['no_test_phase', 'missing_coverage_target']
            }
        }
        
        if kg_path.exists():
            try:
                with open(kg_path, 'r') as f:
                    kg_data = yaml.safe_load(f)
                    # Extract anti-patterns from knowledge graph if present
                    patterns = kg_data.get('anti_patterns', {})
                    if patterns:
                        default_patterns.update(patterns)
            except Exception as e:
                self.logger.warning(f"Could not load anti-patterns from knowledge graph: {e}")
        
        return default_patterns
    
    def scan_plan(self, plan: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Scan plan for anti-patterns.
        
        Args:
            plan: Plan dictionary with phases, requirements, etc.
        
        Returns:
            List of detected anti-patterns with recommendations
        """
        warnings = []
        
        # Check for monolithic phases
        for phase in plan.get('phases', []):
            estimated_hours = phase.get('estimated_hours', 0)
            if estimated_hours > 24:
                warnings.append({
                    'type': 'monolithic_phase',
                    'severity': 'high',
                    'phase': phase.get('name', 'Unknown'),
                    'message': f"Phase '{phase.get('name')}' exceeds 24h ({estimated_hours}h)",
                    'recommendation': 'Split into sub-phases with checkpoints every 8-12h',
                    'pattern_id': 'monolithic_phase'
                })
        
        # Check for missing TDD steps
        if plan.get('requires_tdd', False) or plan.get('complexity', 'MEDIUM') in ['HIGH', 'CRITICAL']:
            phases = [p.get('name', '').lower() for p in plan.get('phases', [])]
            has_red = any('red' in p or 'test' in p or 'failing' in p for p in phases)
            
            if not has_red:
                warnings.append({
                    'type': 'skip_red_phase',
                    'severity': 'critical',
                    'message': 'TDD required but no RED phase detected',
                    'recommendation': 'Add RED phase (write failing tests) before implementation',
                    'pattern_id': 'skip_red_phase'
                })
        
        # Check for missing acceptance criteria
        if not plan.get('acceptance_criteria') and not plan.get('success_criteria'):
            warnings.append({
                'type': 'missing_acceptance_criteria',
                'severity': 'high',
                'message': 'Plan lacks clear acceptance criteria',
                'recommendation': 'Define specific, measurable acceptance criteria',
                'pattern_id': 'missing_acceptance_criteria'
            })
        
        # Check for untested implementation
        has_test_phase = any('test' in p.get('name', '').lower() 
                            for p in plan.get('phases', []))
        has_coverage_target = plan.get('coverage_target') or plan.get('test_coverage_threshold')
        
        if not has_test_phase and not has_coverage_target:
            warnings.append({
                'type': 'untested_implementation',
                'severity': 'critical',
                'message': 'No test phase or coverage target defined',
                'recommendation': 'Add test phase with ≥80% coverage target',
                'pattern_id': 'untested_implementation'
            })
        
        # Log detected patterns
        if warnings:
            self.logger.warning(f"Detected {len(warnings)} anti-patterns in plan")
            for warning in warnings:
                self.logger.warning(f"  - {warning['type']}: {warning['message']}")
        
        return warnings
    
    def get_anti_pattern_summary(self) -> Dict[str, Any]:
        """
        Get summary of all known anti-patterns.
        
        Returns:
            Dict with anti-pattern statistics
        """
        return {
            'total_patterns': len(self.anti_pattern_db),
            'critical_patterns': len([p for p in self.anti_pattern_db.values() 
                                     if p.get('severity') == 'critical']),
            'high_patterns': len([p for p in self.anti_pattern_db.values() 
                                 if p.get('severity') == 'high']),
            'patterns': self.anti_pattern_db
        }
