"""
Dashboard data adapters package
Supports JSON, SQLite, and PostgreSQL backends
"""

from cortex.dashboards.adapters.json_adapter import JSONAdapter

__all__ = ["JSONAdapter"]
