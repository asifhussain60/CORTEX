"""TDD tests for phase-m2-a ContextValidator."""

from pathlib import Path

import pytest


@pytest.fixture()
def validator():
    from cortex.core.context_validator import ContextValidator

    return ContextValidator()


def test_context_validator_validates_required_keys(validator) -> None:
    context = {"intent": "implement"}

    missing = validator.get_missing_keys(context)

    assert missing == ["files"]
    is_valid, errors = validator.validate(context)
    assert is_valid is False
    assert any("Missing required keys" in err for err in errors)


def test_context_validator_accepts_valid_context(validator) -> None:
    context = {"intent": "implement", "files": ["cortex/core/context_validator.py"]}

    is_valid, errors = validator.validate(context)

    assert is_valid is True
    assert errors == []


def test_context_validator_detects_stale_refs(validator) -> None:
    context = {
        "intent": "fix",
        "files": [
            "cortex/core/context_validator.py",
            "cortex/does/not/exist.py",
        ],
    }

    is_valid, errors = validator.validate(context)

    assert is_valid is False
    assert any("Stale file references" in err for err in errors)


def test_context_validator_is_valid_proxy(validator) -> None:
    valid_context = {"intent": "query", "files": []}
    invalid_context = {"files": []}

    assert validator.is_valid(valid_context) is True
    assert validator.is_valid(invalid_context) is False


def test_context_validator_rejects_non_dict(validator) -> None:
    is_valid, errors = validator.validate("not-a-dict")

    assert is_valid is False
    assert errors == ["Context must be a dictionary"]
