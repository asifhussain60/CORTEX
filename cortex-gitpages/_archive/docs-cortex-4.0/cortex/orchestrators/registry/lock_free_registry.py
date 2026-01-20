"""
Lock-Free Orchestrator Registry (AC-STATE-002-04).

Thread-safe registry using copy-on-write and atomic reference swaps
for lock-free read operations with <1μs P99 latency.

Author: Asif Hussain
Copyright © 2026 Asif Hussain. All rights reserved.
"""

import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class OrchestratorInfo:
    """Orchestrator metadata."""
    name: str
    version: str
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RegistryMetrics:
    """Registry operation metrics."""
    total_registrations: int = 0
    total_unregistrations: int = 0
    total_lookups: int = 0


class DuplicateRegistrationError(Exception):
    """Raised on duplicate registration when not idempotent."""
    pass


class LockFreeRegistry:
    """
    Lock-free orchestrator registry using copy-on-write.
    
    Reads are lock-free and use immutable snapshots.
    Writes are synchronized but create new snapshots atomically.
    """
    
    def __init__(self):
        """Initialize lock-free registry."""
        self._snapshot: Dict[str, OrchestratorInfo] = {}
        self._generation = 0
        self._write_lock = threading.Lock()
        self._metrics = RegistryMetrics()
    
    def register(self, orchestrator_id: str, info: OrchestratorInfo) -> None:
        """
        Register an orchestrator (creates new snapshot).
        
        Args:
            orchestrator_id: Unique orchestrator identifier
            info: Orchestrator information
        """
        with self._write_lock:
            # Copy-on-write: create new snapshot
            new_snapshot = dict(self._snapshot)
            new_snapshot[orchestrator_id] = info
            
            # Atomic swap
            self._snapshot = new_snapshot
            self._generation += 1
            self._metrics.total_registrations += 1
    
    def unregister(self, orchestrator_id: str) -> bool:
        """
        Unregister an orchestrator.
        
        Args:
            orchestrator_id: Orchestrator to remove
            
        Returns:
            True if removed, False if not found
        """
        with self._write_lock:
            if orchestrator_id not in self._snapshot:
                return False
            
            # Copy-on-write
            new_snapshot = dict(self._snapshot)
            del new_snapshot[orchestrator_id]
            
            # Atomic swap
            self._snapshot = new_snapshot
            self._generation += 1
            self._metrics.total_unregistrations += 1
            return True
    
    def lookup(self, orchestrator_id: str) -> Optional[OrchestratorInfo]:
        """
        Lookup orchestrator (lock-free read).
        
        Args:
            orchestrator_id: Orchestrator to find
            
        Returns:
            OrchestratorInfo if found, None otherwise
        """
        # Lock-free read from current snapshot
        snapshot = self._snapshot
        self._metrics.total_lookups += 1
        return snapshot.get(orchestrator_id)
    
    def list_all(self) -> List[OrchestratorInfo]:
        """
        List all registered orchestrators (lock-free).
        
        Returns:
            List of all orchestrator info
        """
        # Lock-free read from current snapshot
        snapshot = self._snapshot
        return list(snapshot.values())
    
    def get_generation(self) -> int:
        """
        Get current registry generation for cache invalidation.
        
        Returns:
            Generation counter
        """
        return self._generation
    
    def get_metrics(self) -> Dict[str, int]:
        """
        Get registry metrics.
        
        Returns:
            Metrics dictionary
        """
        return {
            "total_registrations": self._metrics.total_registrations,
            "total_unregistrations": self._metrics.total_unregistrations,
            "total_lookups": self._metrics.total_lookups,
            "current_count": len(self._snapshot),
            "generation": self._generation,
        }
