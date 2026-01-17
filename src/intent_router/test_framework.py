"""AC-PHX-007-11: Testing Framework"""
from typing import Dict, List, Any

class TestFramework:
    """Testing framework for intent router.
    
    Note: This class is named TestFramework for clarity but is NOT a pytest test class.
    The __test__ = False marker prevents pytest from collecting it as a test.
    """
    __test__ = False  # Prevents pytest collection
    
    def __init__(self) -> None:
        self.test_suites: Dict[str, List[Any]] = {}
    
    def register_suite(self, name: str, tests: List[Any]) -> None:
        """Register test suite."""
        self.test_suites[name] = tests
    
    def get_test_count(self) -> int:
        """Get total test count."""
        return sum(len(tests) for tests in self.test_suites.values())
