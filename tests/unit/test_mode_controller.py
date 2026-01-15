"""
Mode Controller Tests - TDD for AR-005

Tests for production mode control:
- Mode detection from CORTEX_ENV
- Production mode prevents all governance bypass
- Mode logged at startup

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
import os
from unittest.mock import patch

import pytest

from src.core.mode_controller import ModeController, RuntimeMode


@pytest.mark.ac("AR-005-01")
class TestEnvModeDetection:
    """Test mode detection from CORTEX_ENV environment variable."""
    
    def test_env_mode_detection_production(self):
        """AC-AR-005-01: Mode should be detected from CORTEX_ENV variable."""
        ModeController.reset_instance()
        with patch.dict(os.environ, {"CORTEX_ENV": "production"}):
            controller = ModeController()
            assert controller.get_mode() == RuntimeMode.PRODUCTION
    
    def test_env_mode_detection_development(self):
        """Should detect development mode from CORTEX_ENV."""
        ModeController.reset_instance()
        with patch.dict(os.environ, {"CORTEX_ENV": "development"}):
            controller = ModeController()
            assert controller.get_mode() == RuntimeMode.DEVELOPMENT
    
    def test_env_mode_detection_test(self):
        """Should detect test mode from CORTEX_ENV."""
        ModeController.reset_instance()
        with patch.dict(os.environ, {"CORTEX_ENV": "test"}):
            controller = ModeController()
            assert controller.get_mode() == RuntimeMode.TEST
    
    def test_default_mode_when_not_set(self):
        """Should default to development mode when CORTEX_ENV not set."""
        ModeController.reset_instance()
        with patch.dict(os.environ, {}, clear=True):
            # Make sure CORTEX_ENV is not in environment
            os.environ.pop("CORTEX_ENV", None)
            controller = ModeController()
            assert controller.get_mode() == RuntimeMode.DEVELOPMENT
    
    def test_case_insensitive_mode_detection(self):
        """Mode detection should be case-insensitive."""
        ModeController.reset_instance()
        with patch.dict(os.environ, {"CORTEX_ENV": "PRODUCTION"}):
            controller = ModeController()
            assert controller.get_mode() == RuntimeMode.PRODUCTION
    
    def test_whitespace_trimmed(self):
        """Whitespace in CORTEX_ENV should be trimmed."""
        ModeController.reset_instance()
        with patch.dict(os.environ, {"CORTEX_ENV": "  development  "}):
            controller = ModeController()
            assert controller.get_mode() == RuntimeMode.DEVELOPMENT


@pytest.mark.ac("AR-005-02")
class TestProductionNoBypass:
    """Test that production mode prevents all governance bypass."""
    
    def test_production_no_bypass(self):
        """AC-AR-005-02: PRODUCTION mode prevents all governance bypass."""
        ModeController.reset_instance()
        controller = ModeController(mode="production")
        assert controller.is_production()
        assert not controller.allows_bypass()
    
    def test_development_allows_bypass(self):
        """Development mode allows bypass."""
        ModeController.reset_instance()
        controller = ModeController(mode="development")
        assert controller.is_development()
        assert controller.allows_bypass()
    
    def test_test_allows_bypass(self):
        """Test mode allows bypass."""
        ModeController.reset_instance()
        controller = ModeController(mode="test")
        assert controller.is_test()
        assert controller.allows_bypass()


@pytest.mark.ac("AR-005-03")
class TestModeLogging:
    """Test mode logging at startup."""
    
    def test_mode_logged_startup(self, caplog):
        """AC-AR-005-03: Mode should be logged at startup."""
        ModeController.reset_instance()
        controller = ModeController(mode="production")
        
        with caplog.at_level(logging.INFO):
            controller.log_startup()
        
        assert "production mode" in caplog.text.lower()
        assert "mode_controller" in caplog.text or "cortex" in caplog.text.lower()
    
    def test_development_mode_logged(self, caplog):
        """Development mode should be logged."""
        ModeController.reset_instance()
        controller = ModeController(mode="development")
        
        with caplog.at_level(logging.INFO):
            controller.log_startup()
        
        assert "development mode" in caplog.text.lower()
    
    def test_logging_includes_bypass_info(self, caplog):
        """Logging should include bypass allowance information."""
        ModeController.reset_instance()
        controller = ModeController(mode="production")
        
        with caplog.at_level(logging.INFO):
            controller.log_startup()
        
        # Log should contain the main message and bypass info in extra fields
        assert len(caplog.records) > 0
        # Check that the extra dict contains bypass info
        log_record = caplog.records[0]
        assert hasattr(log_record, 'allows_bypass')
        assert log_record.allows_bypass is False


class TestModeControllerSingleton:
    """Test singleton pattern of ModeController."""
    
    def test_singleton_instance(self):
        """Should return same instance on multiple calls."""
        ModeController.reset_instance()
        instance1 = ModeController.instance()
        instance2 = ModeController.instance()
        assert instance1 is instance2
    
    def test_reset_instance(self):
        """Should create new instance after reset."""
        ModeController.reset_instance()
        instance1 = ModeController.instance()
        ModeController.reset_instance()
        instance2 = ModeController.instance()
        assert instance1 is not instance2


class TestModeControllerUtilities:
    """Test utility methods of ModeController."""
    
    def test_is_production(self):
        """Should correctly identify production mode."""
        controller = ModeController(mode="production")
        assert controller.is_production()
        assert not controller.is_development()
        assert not controller.is_test()
    
    def test_is_development(self):
        """Should correctly identify development mode."""
        controller = ModeController(mode="development")
        assert controller.is_development()
        assert not controller.is_production()
        assert not controller.is_test()
    
    def test_is_test(self):
        """Should correctly identify test mode."""
        controller = ModeController(mode="test")
        assert controller.is_test()
        assert not controller.is_production()
        assert not controller.is_development()
    
    def test_repr(self):
        """Should have readable string representation."""
        controller = ModeController(mode="production")
        repr_str = repr(controller)
        assert "ModeController" in repr_str
        assert "production" in repr_str
