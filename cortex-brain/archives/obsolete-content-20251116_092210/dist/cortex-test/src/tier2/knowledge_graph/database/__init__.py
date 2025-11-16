"""
Knowledge Graph Database Package

Handles database schema and connections.
"""

from .schema import DatabaseSchema
from .connection import ConnectionManager

__all__ = ['DatabaseSchema', 'ConnectionManager']
