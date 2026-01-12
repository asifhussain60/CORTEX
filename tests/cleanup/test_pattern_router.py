import pytest
from src.orchestrators.core.pattern_router import PatternRouter

class TestPatternRouter:
    def test_route_capability_request(self):
        router = PatternRouter()
        result = router.route({'capability': 'test'})
        assert result is not None
    
    def test_router_returns_handler(self):
        router = PatternRouter()
        result = router.get_handler('cleanup')
        assert result is not None or callable(result)
