"""Test for CORE-036: Runtime Resilience Configuration"""
import pytest
from cortex.core.governance.runtime_resilience import (
    RuntimeResilienceManager,
    ResilienceLevel,
)

class TestRuntimeResilience:
    def test_initialization(self):
        manager = RuntimeResilienceManager()
        assert manager.config.level == ResilienceLevel.NORMAL
    
    def test_set_resilience_level(self):
        manager = RuntimeResilienceManager()
        manager.set_resilience_level(ResilienceLevel.STRICT)
        assert manager.config.level == ResilienceLevel.STRICT
    
    def test_get_config(self):
        manager = RuntimeResilienceManager()
        config = manager.get_config()
        assert config.max_retries == 3
