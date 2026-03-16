"""Phase M15 tests for tutorial mode settings and renderer behavior."""

from __future__ import annotations

from pathlib import Path

import yaml

from cortex.orchestrators.core.tutorial_mode_renderer import (
    TutorialModeRenderer,
    TutorialRenderRequest,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_m15_tutorial_mode_settings_contract() -> None:
    """Settings contract exposes on/auto/off with expert default off."""
    settings = yaml.safe_load(
        (REPO_ROOT / "cortex-registry/core/tutorial-mode-settings.yaml").read_text(encoding="utf-8")
    )
    assert settings["states"] == ["on", "auto", "off"]
    assert settings["default_state"] == "auto"
    assert settings["expert_default_state"] == "off"
    assert settings["sticky_preference"] is True
    assert settings["per_request_override"] is True


def test_m15_tutorial_renderer_state_behavior() -> None:
    """Renderer returns tutorial block only for allowed state/context combinations."""
    renderer = TutorialModeRenderer()

    on_result = renderer.render(
        TutorialRenderRequest(
            mode="on",
            is_expert_user=True,
            explicit_teach_intent=False,
            operational_summary="phase complete",
        )
    )
    assert on_result is not None

    auto_expert_result = renderer.render(
        TutorialRenderRequest(
            mode="auto",
            is_expert_user=True,
            explicit_teach_intent=True,
            operational_summary="phase complete",
        )
    )
    assert auto_expert_result is None

    auto_teach_result = renderer.render(
        TutorialRenderRequest(
            mode="auto",
            is_expert_user=False,
            explicit_teach_intent=True,
            operational_summary="phase complete",
        )
    )
    assert auto_teach_result is not None

    off_result = renderer.render(
        TutorialRenderRequest(
            mode="off",
            is_expert_user=False,
            explicit_teach_intent=True,
            operational_summary="phase complete",
        )
    )
    assert off_result is None
