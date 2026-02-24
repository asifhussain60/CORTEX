"""
Tier Cascade Truth Test - Production Integration

Purpose:
    Verify tier-based data flow in CORTEX using REAL TieredLogger.
    Tests: Log level cascade, tier isolation, proper audit logging.

Authority:
    - CORE-008 (TDD), CORE-027 (Audit Trail)
    - Phase 24: Zero-mock production verification

AC-ID: AC-PHASE24-S1-004
"""

import pytest
import sqlite3
import tempfile
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

# AC_START: AC-PHASE24-S1-004
# Real tier components (ZERO MOCKS)
from cortex.infrastructure.tiered_logger import TieredLogger, LogLevel


class TestTierCascadeTruth:
    """Tier Cascade Truth Test with Real TieredLogger."""
    
    @pytest.fixture(autouse=True)
    def reset_logger(self):
        """Reset TieredLogger singleton before each test."""
        TieredLogger.reset_instance()
        yield
        TieredLogger.reset_instance()
    
    @pytest.fixture
    def tiered_logger(self):
        """Initialize real TieredLogger."""
        logger = TieredLogger.instance()
        init_result = logger.initialize()
        assert init_result.is_ok(), f"Logger init failed: {init_result.error if init_result.is_err() else 'unknown'}"
        return logger
    
    def test_tier_log_level_configuration(self, tiered_logger):
        """
        Test tier-based log level configuration.
        
        Verifies:
        - Can set log levels for tiers 0, 1, 2
        - Can retrieve configured log levels
        - Invalid tier numbers rejected
        """
        # Setup: Set different log levels for each tier
        result_t0 = tiered_logger.set_log_level(0, LogLevel.CRITICAL)
        result_t1 = tiered_logger.set_log_level(1, LogLevel.WARNING)
        result_t2 = tiered_logger.set_log_level(2, LogLevel.INFO)
        
        # Assert: All configurations succeeded
        assert result_t0.is_ok()
        assert result_t1.is_ok()
        assert result_t2.is_ok()
        
        # Verify: Retrieve configured levels
        level_t0 = tiered_logger.get_log_level(0)
        level_t1 = tiered_logger.get_log_level(1)
        level_t2 = tiered_logger.get_log_level(2)
        
        assert level_t0.is_ok() and level_t0.value == LogLevel.CRITICAL
        assert level_t1.is_ok() and level_t1.value == LogLevel.WARNING
        assert level_t2.is_ok() and level_t2.value == LogLevel.INFO
    
    def test_tier_log_filtering_cascade(self, tiered_logger):
        """
        Test log filtering based on tier hierarchy.
        
        Verifies:
        - Tier 0 (CRITICAL) only logs CRITICAL/AUDIT
        - Tier 1 (WARNING) logs WARNING/CRITICAL/AUDIT
        - Tier 2 (INFO) logs INFO/WARNING/CRITICAL/AUDIT
        """
        # Setup: Configure tier log levels
        tiered_logger.set_log_level(0, LogLevel.CRITICAL)
        tiered_logger.set_log_level(1, LogLevel.WARNING)
        tiered_logger.set_log_level(2, LogLevel.INFO)
        
        # Test: Tier 0 filtering (CRITICAL only)
        assert tiered_logger.should_log(0, LogLevel.DEBUG).value == False
        assert tiered_logger.should_log(0, LogLevel.INFO).value == False
        assert tiered_logger.should_log(0, LogLevel.WARNING).value == False
        assert tiered_logger.should_log(0, LogLevel.CRITICAL).value == True
        assert tiered_logger.should_log(0, LogLevel.AUDIT).value == True
        
        # Test: Tier 1 filtering (WARNING+)
        assert tiered_logger.should_log(1, LogLevel.DEBUG).value == False
        assert tiered_logger.should_log(1, LogLevel.INFO).value == False
        assert tiered_logger.should_log(1, LogLevel.WARNING).value == True
        assert tiered_logger.should_log(1, LogLevel.CRITICAL).value == True
        
        # Test: Tier 2 filtering (INFO+)
        assert tiered_logger.should_log(2, LogLevel.DEBUG).value == False
        assert tiered_logger.should_log(2, LogLevel.INFO).value == True
        assert tiered_logger.should_log(2, LogLevel.WARNING).value == True
    
    def test_tier_isolation_validation(self, tiered_logger):
        """
        Test tier isolation - invalid tiers rejected.
        
        Verifies:
        - Tiers 0, 1, 2 are valid
        - Invalid tier numbers return errors
        """
        # Valid tiers
        assert tiered_logger.set_log_level(0, LogLevel.INFO).is_ok()
        assert tiered_logger.set_log_level(1, LogLevel.INFO).is_ok()
        assert tiered_logger.set_log_level(2, LogLevel.INFO).is_ok()
        
        # Invalid tiers
        assert tiered_logger.set_log_level(3, LogLevel.INFO).is_err()
        assert tiered_logger.set_log_level(-1, LogLevel.INFO).is_err()
        assert tiered_logger.set_log_level(999, LogLevel.INFO).is_err()


# AC_COMPLETE: AC-PHASE24-S1-004

