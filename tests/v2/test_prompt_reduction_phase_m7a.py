"""Phase M7-a guardrails for prompt/template surface reduction."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def test_m7a_architect_prompt_reduced_and_modes_preserved() -> None:
    """Architect prompt stays compact and keeps 13 execution modes."""
    path = REPO_ROOT / ".github/prompts/cortex-architect.prompt.md"
    assert path.exists()

    text = path.read_text(encoding="utf-8")
    assert _line_count(path) <= 700

    required_modes = [
        "AUDIT",
        "IMPLEMENT",
        "FIX",
        "REFACTOR",
        "DESIGN",
        "PLAN",
        "QUERY",
        "DIGEST",
        "INVESTIGATE",
        "REPHRASE",
        "VACUUM",
        "HEALTH",
        "DEBUG",
    ]
    for mode in required_modes:
        assert mode in text

    assert ".github/skills/cortex/SKILL.md" in text
    assert ".github/templates/cortex-response-templates.md" in text


def test_m7a_response_templates_reduced_and_ssot_contract_kept() -> None:
    """Response templates remain compact and keep golden format + quote library rules."""
    path = REPO_ROOT / ".github/templates/cortex-response-templates.md"
    assert path.exists()

    text = path.read_text(encoding="utf-8")
    assert _line_count(path) <= 1000

    assert "Response Header — Canonical Spec" in text
    assert "5-Section Golden Format" in text
    assert "Quote Library" in text
    assert "120 approved quotes" in text


def test_m7a_copilot_instructions_reduced_and_header_contract_kept() -> None:
    """Copilot instructions remain compact and preserve mandatory header/assembly rules."""
    path = REPO_ROOT / ".github/copilot-instructions.md"
    assert path.exists()

    text = path.read_text(encoding="utf-8")
    assert _line_count(path) <= 300

    assert "RESPONSE HEADER — MANDATORY" in text
    assert "COMPOSABLE RESPONSE RULES" in text
    assert "CORE-RESP-001" in text
