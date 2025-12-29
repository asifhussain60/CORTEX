"""
Dashboard Reconciliation Package

Industry-standard data reconciliation engine for dashboard metrics.
Ensures accuracy, consistency, and compliance across all dashboard data.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from src.dashboard.reconciliation.reconciliation_engine import ReconciliationEngine
from src.dashboard.reconciliation.models import (
    ReconciliationResult,
    Violation,
    Anomaly,
    AuditTrail,
    ReconciliationMetrics
)

__all__ = [
    'ReconciliationEngine',
    'ReconciliationResult',
    'Violation',
    'Anomaly',
    'AuditTrail',
    'ReconciliationMetrics'
]

__version__ = "1.0.0"
