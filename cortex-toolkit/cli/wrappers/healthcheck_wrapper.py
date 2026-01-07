#!/usr/bin/env python3
"""
CORTEX Healthcheck CLI Wrapper

Command-line interface for CORTEX system health monitoring.

Features:
- Brain tier health checks (Tier 0-3)
- Database performance metrics
- Cache hit rates and optimization
- Memory usage and patterns
- Operation success rates
- System recommendations

Usage:
    python scripts/cli_wrappers/healthcheck_wrapper.py
    python scripts/cli_wrappers/healthcheck_wrapper.py --output json
    python scripts/cli_wrappers/healthcheck_wrapper.py --verbose

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import sys
from pathlib import Path

# Add CORTEX root to path
CORTEX_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(CORTEX_ROOT))

from .base_wrapper import BaseCLIWrapper, main_template
from src.operations.healthcheck_operation import HealthCheckOperation


class HealthcheckWrapper(BaseCLIWrapper):
    """CLI wrapper for CORTEX health check."""
    
    def get_orchestrator(self):
        """Get healthcheck operation."""
        return HealthCheckOperation()
    
    def get_operation_name(self) -> str:
        """Get operation name."""
        return "CORTEX Health Check"
    
    def format_text_output(self, result) -> str:
        """Format healthcheck result as human-readable text."""
        from src.operations.base_operation_module import OperationStatus
        
        lines = []
        lines.append(f"\n{'='*70}")
        lines.append(f"  🏥 CORTEX Health Check")
        lines.append(f"{'='*70}\n")
        
        # Status
        if result.status == OperationStatus.SUCCESS:
            lines.append("Status: ✓ HEALTHY")
        else:
            lines.append("Status: ✗ UNHEALTHY")
        
        # Overall Score
        if result.data and 'overall_score' in result.data:
            score = result.data['overall_score']
            lines.append(f"Overall Score: {score}/100")
            
            # Health indicator
            if score >= 90:
                lines.append("Health: 🟢 EXCELLENT")
            elif score >= 75:
                lines.append("Health: 🟡 GOOD")
            elif score >= 50:
                lines.append("Health: 🟠 FAIR")
            else:
                lines.append("Health: 🔴 POOR")
        
        # Brain Health
        if result.data and 'brain_health' in result.data:
            lines.append("\n" + "="*70)
            lines.append("BRAIN HEALTH")
            lines.append("="*70)
            
            brain = result.data['brain_health']
            for tier, tier_data in brain.items():
                if isinstance(tier_data, dict):
                    status_icon = "✓" if tier_data.get('healthy', False) else "✗"
                    lines.append(f"\n{status_icon} {tier.replace('_', ' ').title()}")
                    for key, value in tier_data.items():
                        if key != 'healthy':
                            lines.append(f"  {key}: {value}")
        
        # Database Health
        if result.data and 'database_health' in result.data:
            lines.append("\n" + "="*70)
            lines.append("DATABASE HEALTH")
            lines.append("="*70)
            
            db = result.data['database_health']
            for key, value in db.items():
                lines.append(f"  {key}: {value}")
        
        # Cache Health
        if result.data and 'cache_health' in result.data:
            lines.append("\n" + "="*70)
            lines.append("CACHE HEALTH")
            lines.append("="*70)
            
            cache = result.data['cache_health']
            for key, value in cache.items():
                lines.append(f"  {key}: {value}")
        
        # System Metrics
        if result.data and 'system_metrics' in result.data:
            lines.append("\n" + "="*70)
            lines.append("SYSTEM METRICS")
            lines.append("="*70)
            
            metrics = result.data['system_metrics']
            for key, value in metrics.items():
                lines.append(f"  {key}: {value}")
        
        # Recommendations
        if result.data and 'recommendations' in result.data:
            recommendations = result.data['recommendations']
            if recommendations:
                lines.append("\n" + "="*70)
                lines.append(f"💡 RECOMMENDATIONS ({len(recommendations)})")
                lines.append("="*70)
                for i, rec in enumerate(recommendations, 1):
                    if isinstance(rec, dict):
                        priority = rec.get('priority', 'MEDIUM')
                        message = rec.get('message', 'No message')
                        lines.append(f"  {i}. [{priority}] {message}")
                    else:
                        lines.append(f"  {i}. {rec}")
        
        # Warnings
        if result.warnings:
            lines.append("\n" + "="*70)
            lines.append(f"⚠️  WARNINGS ({len(result.warnings)})")
            lines.append("="*70)
            for warning in result.warnings:
                lines.append(f"  {warning}")
        
        # Errors
        if result.errors:
            lines.append("\n" + "="*70)
            lines.append(f"❌ ERRORS ({len(result.errors)})")
            lines.append("="*70)
            for error in result.errors:
                lines.append(f"  {error}")
        
        lines.append(f"\n{'='*70}\n")
        return '\n'.join(lines)


if __name__ == '__main__':
    sys.exit(main_template(HealthcheckWrapper))
