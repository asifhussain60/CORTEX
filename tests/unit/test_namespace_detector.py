import pytest

from src.agents.namespace_detector import NamespaceDetector, NamespaceType


@pytest.mark.unit
def test_detects_cortex_framework_question_high_confidence():
    det = NamespaceDetector()
    msg = "What's the CORTEX system status and brain health today?"
    res = det.detect_namespace(msg)
    assert res.primary_namespace == NamespaceType.CORTEX_FRAMEWORK
    assert res.confidence >= 0.7
    assert not res.requires_clarification


@pytest.mark.unit
def test_detects_workspace_code_context():
    det = NamespaceDetector()
    msg = "How is my code quality and test coverage right now?"
    res = det.detect_namespace(msg)
    assert res.primary_namespace == NamespaceType.WORKSPACE_CODE
    assert res.confidence >= 0.7
    assert not res.requires_clarification


@pytest.mark.unit
def test_ambiguous_requires_clarification():
    det = NamespaceDetector()
    msg = "How is the code?"
    res = det.detect_namespace(msg)
    assert res.primary_namespace in (NamespaceType.AMBIGUOUS, NamespaceType.WORKSPACE_CODE)
    assert res.requires_clarification or res.confidence < 0.7
    # If clarification suggested, ensure it's non-empty
    if res.requires_clarification:
        assert res.suggested_clarification
