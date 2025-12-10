"""
Observability Orchestrator - Unified dashboard generation, health monitoring, and analytics

Consolidates 10 legacy files into a single orchestrator with AST-powered intelligence.

Components:
- observability_orchestrator.py: Main orchestrator (400 LOC)
- dashboard_engine.py: Dashboard generation (500 LOC)
- health_monitor.py: Health monitoring (400 LOC)
- analytics_collector.py: Adoption analytics (500 LOC)
- intelligent_dashboard/: AST-powered intelligence (2,800 LOC)

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

from .observability_orchestrator import ObservabilityOrchestrator

__all__ = ["ObservabilityOrchestrator"]
