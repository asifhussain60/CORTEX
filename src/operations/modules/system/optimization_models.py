"""
System Optimization Data Models

Data classes for system optimization metrics and health reporting.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any


@dataclass
class OptimizationMetrics:
    """Comprehensive optimization metrics from all phases."""
    # Phase 1: Design Sync
    design_drift_resolved: int = 0
    modules_synced: int = 0
    status_files_consolidated: int = 0
    
    # Phase 2: Code Health
    obsolete_tests_identified: int = 0
    dead_code_removed: int = 0
    coverage_gaps_identified: int = 0
    
    # Phase 3: Brain Tuning
    tier_violations_fixed: int = 0
    low_confidence_patterns_pruned: int = 0
    duplicate_patterns_merged: int = 0
    protection_rules_validated: bool = False
    
    # Phase 4: Entry Point Alignment
    orchestrators_aligned: int = 0
    commands_registered: int = 0
    entry_points_synced: int = 0
    
    # Phase 5: Test Suite Optimization
    tests_removed: int = 0
    tests_fixed: int = 0
    final_pass_rate: float = 0.0
    skull_007_compliant: bool = False
    
    # Phase 7: Governance Health Check
    governance_drift_score: float = 100.0
    governance_position_drifts: int = 0
    governance_forward_refs: int = 0
    governance_orphaned_rules: int = 0
    
    # Overall
    total_improvements: int = 0
    execution_time_seconds: float = 0.0
    errors_encountered: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class SystemHealthReport:
    """Comprehensive system health report."""
    timestamp: datetime
    overall_health: str  # excellent, good, fair, poor, critical
    health_score: float  # 0.0 to 100.0
    metrics: OptimizationMetrics
    recommendations: List[str] = field(default_factory=list)
    next_actions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'overall_health': self.overall_health,
            'health_score': self.health_score,
            'metrics': {
                'design_sync': {
                    'drift_resolved': self.metrics.design_drift_resolved,
                    'modules_synced': self.metrics.modules_synced,
                    'status_files_consolidated': self.metrics.status_files_consolidated
                },
                'code_health': {
                    'obsolete_tests_identified': self.metrics.obsolete_tests_identified,
                    'dead_code_removed': self.metrics.dead_code_removed,
                    'coverage_gaps_identified': self.metrics.coverage_gaps_identified
                },
                'brain_tuning': {
                    'tier_violations_fixed': self.metrics.tier_violations_fixed,
                    'patterns_pruned': self.metrics.low_confidence_patterns_pruned,
                    'patterns_merged': self.metrics.duplicate_patterns_merged,
                    'protection_rules_validated': self.metrics.protection_rules_validated
                },
                'entry_point_alignment': {
                    'orchestrators_aligned': self.metrics.orchestrators_aligned,
                    'commands_registered': self.metrics.commands_registered,
                    'entry_points_synced': self.metrics.entry_points_synced
                },
                'test_suite': {
                    'tests_removed': self.metrics.tests_removed,
                    'tests_fixed': self.metrics.tests_fixed,
                    'final_pass_rate': self.metrics.final_pass_rate,
                    'skull_007_compliant': self.metrics.skull_007_compliant
                },
                'governance': {
                    'health_score': self.metrics.governance_drift_score,
                    'position_drifts': self.metrics.governance_position_drifts,
                    'forward_refs': self.metrics.governance_forward_refs,
                    'orphaned_rules': self.metrics.governance_orphaned_rules
                }
            },
            'total_improvements': self.metrics.total_improvements,
            'execution_time': self.metrics.execution_time_seconds,
            'errors': self.metrics.errors_encountered,
            'warnings': self.metrics.warnings,
            'recommendations': self.recommendations,
            'next_actions': self.next_actions
        }
