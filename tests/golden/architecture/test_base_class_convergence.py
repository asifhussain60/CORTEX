"""
Golden tests for Sub-Phase D: Base Class Convergence.

Validates that all 21 wired orchestrators satisfy the wiring contract's
``validation.required_methods`` and ``validation.optional_methods``.

Authority: Phase 13 Sub-Phase D, CORE-008 (TDD), CORE-011, CORE-012
Test Count: 7 golden tests
"""

import importlib
from typing import Any, Dict, List
from unittest.mock import MagicMock

import pytest
import yaml


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def wiring_spec() -> Dict[str, Any]:
    """Load the wiring specification."""
    with open("cortex/core/wiring/specifications/wiring.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def all_orchestrator_entries(wiring_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Flatten all orchestrator entries across tiers."""
    entries: List[Dict[str, Any]] = []
    for tier_name in ("core", "domain", "support"):
        entries.extend(wiring_spec["orchestrators"].get(tier_name, []))
    return entries


@pytest.fixture(scope="module")
def required_methods(wiring_spec: Dict[str, Any]) -> List[str]:
    """Required methods from wiring contract."""
    return wiring_spec["validation"]["required_methods"]


@pytest.fixture(scope="module")
def optional_methods(wiring_spec: Dict[str, Any]) -> List[str]:
    """Optional methods from wiring contract."""
    return wiring_spec["validation"]["optional_methods"]


def _safe_instantiate(cls: type) -> Any:
    """Instantiate an orchestrator, injecting mock args if needed."""
    try:
        return cls()
    except TypeError:
        pass
    # Needs constructor args — inject mocks
    import inspect
    sig = inspect.signature(cls.__init__)
    params = list(sig.parameters.values())
    args_needed = [p for p in params[1:] if p.default is inspect.Parameter.empty]
    if not args_needed:
        return cls()
    mocks = {p.name: MagicMock() for p in args_needed}
    return cls(**mocks)


# ---------------------------------------------------------------------------
# Test Class
# ---------------------------------------------------------------------------

class TestBaseClassConvergence:
    """Validate all wired orchestrators satisfy the protocol contract."""

    def test_all_orchestrators_importable(
        self, all_orchestrator_entries: List[Dict[str, Any]]
    ) -> None:
        """Every wired orchestrator module must be importable."""
        failures: List[str] = []
        for entry in all_orchestrator_entries:
            try:
                importlib.import_module(entry["module"])
            except ImportError as exc:
                failures.append(f"{entry['name']}: {exc}")

        assert not failures, f"Import failures:\n" + "\n".join(failures)

    def test_all_orchestrators_class_exists(
        self, all_orchestrator_entries: List[Dict[str, Any]]
    ) -> None:
        """Every wired orchestrator class must exist in its module."""
        failures: List[str] = []
        for entry in all_orchestrator_entries:
            mod = importlib.import_module(entry["module"])
            if not hasattr(mod, entry["class"]):
                failures.append(f"{entry['name']}: class {entry['class']} not in {entry['module']}")

        assert not failures, f"Missing classes:\n" + "\n".join(failures)

    def test_all_orchestrators_have_required_methods(
        self,
        all_orchestrator_entries: List[Dict[str, Any]],
        required_methods: List[str],
    ) -> None:
        """Every wired orchestrator class must define all required methods."""
        failures: List[str] = []
        for entry in all_orchestrator_entries:
            mod = importlib.import_module(entry["module"])
            cls = getattr(mod, entry["class"])
            missing = [m for m in required_methods if not hasattr(cls, m)]
            if missing:
                failures.append(f"{entry['name']}: missing {missing}")

        assert not failures, (
            f"Required methods missing:\n" + "\n".join(failures)
        )

    def test_all_orchestrators_have_health_check(
        self, all_orchestrator_entries: List[Dict[str, Any]]
    ) -> None:
        """Every wired orchestrator class must have a health_check method."""
        failures: List[str] = []
        for entry in all_orchestrator_entries:
            mod = importlib.import_module(entry["module"])
            cls = getattr(mod, entry["class"])
            if not hasattr(cls, "health_check"):
                failures.append(entry["name"])

        assert not failures, f"Missing health_check:\n" + "\n".join(failures)

    def test_all_orchestrators_instantiable(
        self, all_orchestrator_entries: List[Dict[str, Any]]
    ) -> None:
        """Every wired orchestrator must be instantiable (with mock args if needed)."""
        failures: List[str] = []
        for entry in all_orchestrator_entries:
            mod = importlib.import_module(entry["module"])
            cls = getattr(mod, entry["class"])
            try:
                _safe_instantiate(cls)
            except Exception as exc:
                failures.append(f"{entry['name']}: {exc}")

        assert not failures, f"Instantiation failures:\n" + "\n".join(failures)

    def test_get_name_returns_string(
        self, all_orchestrator_entries: List[Dict[str, Any]]
    ) -> None:
        """get_name() must return a non-empty string for all orchestrators."""
        failures: List[str] = []
        for entry in all_orchestrator_entries:
            mod = importlib.import_module(entry["module"])
            cls = getattr(mod, entry["class"])
            try:
                instance = _safe_instantiate(cls)
                name = instance.get_name()
                if not isinstance(name, str) or not name:
                    failures.append(f"{entry['name']}: get_name() returned {name!r}")
            except Exception as exc:
                failures.append(f"{entry['name']}: {exc}")

        assert not failures, f"get_name failures:\n" + "\n".join(failures)

    def test_health_check_returns_dict_with_status(
        self, all_orchestrator_entries: List[Dict[str, Any]]
    ) -> None:
        """health_check() must return dict with 'status' key."""
        failures: List[str] = []
        for entry in all_orchestrator_entries:
            mod = importlib.import_module(entry["module"])
            cls = getattr(mod, entry["class"])
            try:
                instance = _safe_instantiate(cls)
                result = instance.health_check()
                if not isinstance(result, dict) or "status" not in result:
                    failures.append(f"{entry['name']}: health_check() returned {result!r}")
            except Exception as exc:
                failures.append(f"{entry['name']}: {exc}")

        assert not failures, f"health_check failures:\n" + "\n".join(failures)
