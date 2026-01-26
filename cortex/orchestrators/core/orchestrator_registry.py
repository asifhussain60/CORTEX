"""
Orchestrator Registry - DEPRECATED Bridge Adapter (AC-CONSOLIDATION-001)

⚠️  DEPRECATED: This module is a bridge adapter only.
    All orchestrator wiring uses DatabaseBackedRegistry (CORE-035 SSOT).

CANONICAL REGISTRY:
-------------------
    from cortex.orchestrators.core.database_registry import (
        DatabaseBackedRegistry,
        get_database_registry,
    )

This bridge adapter provides backward compatibility ONLY for:
- Legacy imports from this module
- Domain-based queries
- Pattern matching

All new code should import directly from database_registry.

Migration:
    OLD: from cortex.orchestrators.core.orchestrator_registry import OrchestratorRegistry
    NEW: from cortex.orchestrators.core.database_registry import get_database_registry

Author: Asif Hussain
AC-CONSOLIDATION: AC-CONSOLIDATION-001
"""

import warnings
import re
from typing import Dict, List, Optional, Any, Pattern
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RegistryQuery:
    """Query result (DEPRECATED - use DatabaseBackedRegistry instead)"""
    domain: Optional[str] = None
    pattern: Optional[str] = None
    results: List[Dict[str, Any]] = field(default_factory=list)
    total_count: int = 0
    matched_count: int = 0
    query_time: Optional[str] = None


class OrchestratorRegistry:
    """
    DEPRECATED Bridge adapter for backward compatibility.
    
    This singleton provides legacy interface to DatabaseBackedRegistry.
    Use DatabaseBackedRegistry directly in new code.
    """
    
    _instance: Optional['OrchestratorRegistry'] = None
    
    def __init__(self):
        """Initialize with deprecation warning"""
        warnings.warn(
            "OrchestratorRegistry is deprecated. Use DatabaseBackedRegistry from "
            "cortex.orchestrators.core.database_registry instead.",
            DeprecationWarning,
            stacklevel=2
        )
        self.created_at = datetime.now().isoformat()
    
    @classmethod
    def instance(cls) -> 'OrchestratorRegistry':
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton (for testing)"""
        cls._instance = None
    
    def get_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Get orchestrators by domain (DEPRECATED)"""
        from cortex.orchestrators.core.database_registry import get_database_registry
        registry = get_database_registry()
        all_orchestrators = registry.get_all_orchestrators()
        return [
            {"name": name, "instance": orch}
            for name, orch in all_orchestrators.items()
        ]
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all orchestrators (DEPRECATED)"""
        from cortex.orchestrators.core.database_registry import get_database_registry
        registry = get_database_registry()
        all_orchestrators = registry.get_all_orchestrators()
        return [
            {"name": name, "instance": orch}
            for name, orch in all_orchestrators.items()
        ]
    
    def query(
        self,
        domain_pattern: Optional[str] = None,
        capability: Optional[str] = None,
        version: Optional[str] = None
    ) -> RegistryQuery:
        """Query orchestrators (DEPRECATED)"""
        query_start = datetime.now()
        filtered = self.get_all()
        
        if domain_pattern:
            domain_regex = self._pattern_to_regex(domain_pattern)
            filtered = [
                o for o in filtered
                if domain_regex.match(str(o.get("name", "")))
            ]
        
        query_end = datetime.now()
        duration = (query_end - query_start).total_seconds()
        
        return RegistryQuery(
            domain=domain_pattern,
            pattern=domain_pattern,
            results=filtered,
            total_count=len(self.get_all()),
            matched_count=len(filtered),
            query_time=f"{duration:.6f}s"
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics (DEPRECATED)"""
        orchestrators = self.get_all()
        return {
            "total_orchestrators": len(orchestrators),
            "created_at": self.created_at,
        }
    
    @staticmethod
    def _pattern_to_regex(pattern: str) -> Pattern[str]:
        """Convert wildcard pattern to regex"""
        escaped = re.escape(pattern)
        regex_pattern = escaped.replace(r"\*", ".*")
        regex_pattern = f"^{regex_pattern}$"
        return re.compile(regex_pattern, re.IGNORECASE)
