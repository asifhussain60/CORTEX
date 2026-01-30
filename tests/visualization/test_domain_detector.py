"""Test Domain Auto-Detection (STATIC-VIZ-006)."""
from cortex.visualization.domain_detector import DomainDetector

def test_github():
    detector = DomainDetector()
    assert detector.detect("https://github.com/org/repo") == "org"

def test_override():
    detector = DomainDetector()
    assert detector.detect("https://github.com/org/repo", override="custom") == "custom"
