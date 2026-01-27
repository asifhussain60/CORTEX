"""
Mode Controller - Production Mode Control (AR-005)

Determines runtime mode from CORTEX_ENV environment variable.
Controls whether governance can be bypassed:
- PRODUCTION: No bypasses allowed, strictest enforcement
- DEVELOPMENT: Allows carefully controlled bypasses for testing
- TEST: Allows mock/fixture bypasses

Features:
- Mode detection from CORTEX_ENV
- Mode validation and enforcement
- Startup logging
- Thread-safe access

Author: Asif Hussain
"""

import logging
import os
import threading
from enum import Enum
from typing import Optional

from cortex.brain.core.result import Result, Ok, Err


class RuntimeMode(Enum):
    """Runtime mode enumeration."""
    PRODUCTION = "production"
    DEVELOPMENT = "development"
    TEST = "test"


class ModeController:
    """
    Controller for runtime mode management.
    
    Thread-safe singleton for determining and enforcing runtime mode.
    """
    
    _instance: Optional['ModeController'] = None
    _lock = threading.Lock()
    
    def __init__(self, mode: Optional[str] = None):
        """
        Initialize mode controller.
        
        Args:
            mode: Override mode (for testing). If None, reads from CORTEX_ENV.
        """
        self._mode: Optional[RuntimeMode] = None
        self._logger = logging.getLogger(__name__)
        
        if mode is not None:
            # Direct initialization (for testing)
            self._mode = self._parse_mode(mode).unwrap_or(RuntimeMode.DEVELOPMENT)
        else:
            # Initialize from environment
            env_mode = os.environ.get("CORTEX_ENV", "development").lower()
            self._mode = self._parse_mode(env_mode).unwrap_or(RuntimeMode.DEVELOPMENT)
    
    @classmethod
    def instance(cls) -> 'ModeController':
        """Get singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton instance (for testing)."""
        with cls._lock:
            cls._instance = None
    
    def _parse_mode(self, mode_str: str) -> Result[RuntimeMode]:
        """Parse mode string to RuntimeMode enum."""
        mode_lower = mode_str.lower().strip()
        
        for mode in RuntimeMode:
            if mode.value == mode_lower:
                return Ok(mode)
        
        return Err(f"Invalid mode: {mode_str}. Must be one of: production, development, test")
    
    def get_mode(self) -> RuntimeMode:
        """
        Get current runtime mode.
        
        Returns:
            RuntimeMode enum value
        """
        return self._mode
    
    def is_production(self) -> bool:
        """Check if in production mode."""
        return self._mode == RuntimeMode.PRODUCTION
    
    def is_development(self) -> bool:
        """Check if in development mode."""
        return self._mode == RuntimeMode.DEVELOPMENT
    
    def is_test(self) -> bool:
        """Check if in test mode."""
        return self._mode == RuntimeMode.TEST
    
    def allows_bypass(self) -> bool:
        """
        Check if governance bypass is allowed.
        
        Returns:
            True if bypass allowed (not in production), False if strict enforcement required
        """
        return self._mode != RuntimeMode.PRODUCTION
    
    def log_startup(self) -> None:
        """Log mode at startup."""
        self._logger.info(
            f"CORTEX initialized in {self._mode.value} mode",
            extra={
                "component": "mode_controller",
                "mode": self._mode.value,
                "allows_bypass": self.allows_bypass(),
            }
        )
    
    def __repr__(self) -> str:
        """String representation."""
        return f"ModeController(mode={self._mode.value})"
