"""
Execution mode enumeration and utilities

Author: Asif Hussain
Version: 1.0
Created: December 21, 2025
"""

from enum import Enum
from typing import Dict


class ExecutionMode(Enum):
    """
    Execution mode types for adaptive operation execution
    
    Modes:
        HUMAN_IN_LOOP: Pause after each step for manual approval (safest)
        SUPERVISED: Auto-validate, require final approval (balanced)
        AUTONOMOUS: Full end-to-end with self-healing (fastest)
    """
    
    HUMAN_IN_LOOP = "human_in_loop"
    SUPERVISED = "supervised"
    AUTONOMOUS = "autonomous"
    
    @property
    def description(self) -> str:
        """Get human-readable description of mode"""
        descriptions = {
            self.HUMAN_IN_LOOP: "Pause after each step (learning/debugging)",
            self.SUPERVISED: "Auto-validate, manual approval (default)",
            self.AUTONOMOUS: "Full E2E with self-healing"
        }
        return descriptions[self]
    
    @property
    def risk_tolerance(self) -> float:
        """
        Get risk tolerance level for mode
        
        Returns:
            float: 0.0 (most cautious) to 1.0 (most aggressive)
        """
        tolerance = {
            self.HUMAN_IN_LOOP: 0.0,
            self.SUPERVISED: 0.5,
            self.AUTONOMOUS: 1.0
        }
        return tolerance[self]
    
    @property
    def speed_multiplier(self) -> float:
        """
        Get relative speed multiplier for mode
        
        Returns:
            float: 1.0 (slowest) to 5.0 (fastest)
        """
        speed = {
            self.HUMAN_IN_LOOP: 1.0,   # Slowest (manual approvals)
            self.SUPERVISED: 2.5,       # Medium
            self.AUTONOMOUS: 5.0        # Fastest (no pauses)
        }
        return speed[self]
    
    def to_dict(self) -> Dict[str, any]:
        """Convert mode to dictionary representation"""
        return {
            "mode": self.value,
            "description": self.description,
            "risk_tolerance": self.risk_tolerance,
            "speed_multiplier": self.speed_multiplier
        }
    
    def __str__(self) -> str:
        return f"{self.value}: {self.description}"
