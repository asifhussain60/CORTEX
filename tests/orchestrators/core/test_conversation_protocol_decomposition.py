"""TDD RED — Phase 103-h: conversation_protocol.py decomposition.

GAP-103-08: conversation_protocol.py (1,538L) → sub-package with phase mixins.
CORE-008: tests written before implementation.
"""
# ruff: noqa: S101
from __future__ import annotations

import pathlib
import pytest

CP_PKG = pathlib.Path("cortex/orchestrators/core/conversation_protocol")
CP_FLAT = pathlib.Path("cortex/orchestrators/core/conversation_protocol.py")


class TestConversationProtocolPackageStructure:

    def test_cp_is_package_not_flat_file(self) -> None:
        assert CP_PKG.is_dir(), "conversation_protocol/ sub-package not found"
        assert not CP_FLAT.exists(), "flat conversation_protocol.py must be removed"

    @pytest.mark.parametrize("module", [
        "__init__.py",
        "models.py",
        "protocol.py",
        "governance_mixin.py",
        "comprehension_mixin.py",
    ])
    def test_expected_module_exists(self, module: str) -> None:
        assert (CP_PKG / module).exists(), f"conversation_protocol/{module} not found"

    def test_protocol_under_1000_lines(self) -> None:
        target = CP_PKG / "protocol.py"
        lines = len(target.read_text().splitlines())
        assert lines < 1000, f"protocol.py is {lines}L — must be < 1000L"


class TestConversationProtocolImports:

    def test_models_importable(self) -> None:
        from cortex.orchestrators.core.conversation_protocol import (
            RequestComplexityClassifier,
            RoundContext,
        )
        assert RequestComplexityClassifier is not None
        assert RoundContext is not None

    def test_protocol_importable(self) -> None:
        from cortex.orchestrators.core.conversation_protocol import (
            ConversationProtocol,
        )
        assert ConversationProtocol is not None

    def test_backwards_compat_all_symbols(self) -> None:
        import cortex.orchestrators.core.conversation_protocol as pkg
        expected = [
            "RequestComplexityClassifier",
            "RoundContext",
            "ConversationProtocol",
        ]
        for sym in expected:
            assert hasattr(pkg, sym), f"conversation_protocol package missing: {sym}"
