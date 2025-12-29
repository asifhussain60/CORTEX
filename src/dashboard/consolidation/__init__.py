"""
Consolidation Package

Data quality and cross-validation for dashboard metrics.
"""

from .data_consolidator import DataConsolidator, ConsolidatedScore, Recommendation
from .sql_injection_scanner import SQLInjectionScanner

__all__ = ['DataConsolidator', 'ConsolidatedScore', 'Recommendation', 'SQLInjectionScanner']
