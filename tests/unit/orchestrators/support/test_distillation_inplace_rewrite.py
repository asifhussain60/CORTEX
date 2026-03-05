"""
RED tests — DistillationOrchestrator in-place file rewrite + dense output format.

BUG-DISTILL-001: distill() has no file_path param → cannot rewrite source file
BUG-DISTILL-002: _PromptSynthesiser emits verbose prose headers → not dense signal format

TDD contract (CORE-008): all tests MUST FAIL before the fix is applied.
"""
from __future__ import annotations

import os
import tempfile
import pytest


def _orch():
    from cortex.orchestrators.support.distillation_orchestrator import DistillationOrchestrator
    return DistillationOrchestrator()


# ---------------------------------------------------------------------------
# BUG-DISTILL-001: in-place file rewrite
# ---------------------------------------------------------------------------

class TestDistillInPlaceRewrite:
    """distill() must accept file_path and overwrite the source file with compressed content."""

    def test_distill_accepts_file_path_kwarg(self):
        """distill() must accept a file_path keyword argument without raising TypeError."""
        orch = _orch()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("User: I want to build a task API.\nAgent: FastAPI?\nUser: Yes.\n")
            path = f.name
        try:
            # Must not raise TypeError for unknown kwarg
            result = orch.distill(conversation="User: build a task API\n", file_path=path)
            assert result is not None
        finally:
            os.unlink(path)

    def test_distill_rewrites_source_file_when_file_path_given(self):
        """When file_path is provided, the file must be overwritten with distilled content."""
        orch = _orch()
        original = (
            "User: I want to build a REST API.\n"
            "Agent: FastAPI?\n"
            "User: Yes. Must have JWT auth.\n"
            "Agent: Postgres backend too?\n"
            "User: Yes. No rate limiting needed.\n"
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(original)
            path = f.name
        try:
            result = orch.distill(conversation=original, file_path=path)
            assert result.success is True
            with open(path, "r") as f:
                written = f.read()
            # File must be rewritten — content must differ from original
            assert written != original
            # Must not be empty
            assert len(written.strip()) > 0
        finally:
            os.unlink(path)

    def test_distill_file_content_shorter_than_original(self):
        """Rewritten file must be shorter than the original — distillation compresses."""
        orch = _orch()
        original = (
            "User: I want to build a REST API for managing tasks.\n"
            "Agent: Sure, shall we use FastAPI?\n"
            "User: Yes. It must support JWT auth and have a Postgres backend.\n"
            "Agent: Understood. Any rate-limiting requirements?\n"
            "User: No. Keep it simple. No rate limiting. FastAPI, JWT, Postgres.\n"
            "Agent: Great. Should we add tests?\n"
            "User: Yes, pytest. Aim for 90% coverage.\n"
        ) * 5  # repeat to make it clearly larger
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(original)
            path = f.name
        try:
            result = orch.distill(conversation=original, file_path=path)
            assert result.success is True
            with open(path, "r") as f:
                written = f.read()
            assert len(written) < len(original), (
                f"Rewritten file ({len(written)} chars) must be shorter than original ({len(original)} chars)"
            )
        finally:
            os.unlink(path)

    def test_distill_no_file_path_does_not_touch_filesystem(self):
        """When file_path is not given, distill() must not write any file."""
        orch = _orch()
        result = orch.distill(conversation="User: build a task API\nAgent: FastAPI?\nUser: Yes.\n")
        assert result.success is True
        # No side-effect: result carries content only
        assert result.distilled_prompt is not None

    def test_distill_result_has_file_written_flag_when_path_given(self):
        """DistillationResult.metadata must include 'file_written': True when path was given."""
        orch = _orch()
        original = "User: build a task API\nAgent: FastAPI?\nUser: Yes. JWT auth required.\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(original)
            path = f.name
        try:
            result = orch.distill(conversation=original, file_path=path)
            assert result.success is True
            assert result.metadata.get("file_written") is True
            assert result.metadata.get("file_path") == path
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# BUG-DISTILL-002: dense output format
# ---------------------------------------------------------------------------

class TestDistillDenseOutputFormat:
    """_PromptSynthesiser must emit dense signal format, not verbose prose headers."""

    def test_output_has_no_verbose_markdown_headers(self):
        """Output must NOT contain verbose section headers like '## Goals', '## Decisions Made'."""
        orch = _orch()
        conversation = (
            "User: I want to build a REST API.\n"
            "Agent: FastAPI?\n"
            "User: Yes. JWT auth. Postgres. No rate limiting.\n"
            "Agent: Confirmed.\n"
        )
        result = orch.distill(conversation=conversation)
        assert result.success is True
        # Verbose headers must be absent
        assert "## Goals" not in result.distilled_prompt
        assert "## Decisions Made" not in result.distilled_prompt
        assert "## Constraints" not in result.distilled_prompt
        assert "## Context" not in result.distilled_prompt

    def test_output_has_no_generated_by_header(self):
        """Output must NOT contain the '# Distilled Prompt' preamble header."""
        orch = _orch()
        conversation = "User: build a task API\nAgent: FastAPI?\nUser: Yes. JWT.\n"
        result = orch.distill(conversation=conversation)
        assert result.success is True
        assert "# Distilled Prompt" not in result.distilled_prompt
        assert "Generated by CORTEX" not in result.distilled_prompt

    def test_output_is_compact_single_block(self):
        """Output must be a compact block — no multi-paragraph section separation."""
        orch = _orch()
        conversation = (
            "User: I need a FastAPI REST API with JWT auth and Postgres.\n"
            "Agent: Should we add rate limiting?\n"
            "User: No. Keep it simple. pytest coverage 90%.\n"
        )
        result = orch.distill(conversation=conversation)
        assert result.success is True
        # Should not have more than 2 consecutive blank lines (no section breaks)
        assert "\n\n\n" not in result.distilled_prompt

    def test_output_preserves_key_signals(self):
        """Distilled output must retain the core signals from the conversation."""
        orch = _orch()
        conversation = (
            "User: I want to build a REST API for managing tasks.\n"
            "Agent: FastAPI?\n"
            "User: Yes. Must support JWT auth and Postgres backend.\n"
            "Agent: Rate limiting?\n"
            "User: No rate limiting. pytest, 90% coverage.\n"
        )
        result = orch.distill(conversation=conversation)
        assert result.success is True
        prompt = result.distilled_prompt.lower()
        # At least some key signals must survive distillation
        assert any(kw in prompt for kw in ["api", "jwt", "postgres", "rest", "task"])

    def test_output_shorter_than_input(self):
        """Distilled prompt must be shorter than the original conversation."""
        orch = _orch()
        conversation = (
            "User: I want to build a REST API for managing tasks.\n"
            "Agent: Sure, shall we use FastAPI?\n"
            "User: Yes. It must support JWT auth and have a Postgres backend.\n"
            "Agent: Understood. Any rate-limiting requirements?\n"
            "User: No. Keep it simple.\n"
        )
        result = orch.distill(conversation=conversation)
        assert result.success is True
        assert len(result.distilled_prompt) < len(conversation), (
            f"distilled ({len(result.distilled_prompt)}) must be shorter than original ({len(conversation)})"
        )


# ---------------------------------------------------------------------------
# BUG-DISTILL-003: fidelity — do NOT truncate decisions at 120 chars
# ---------------------------------------------------------------------------

class TestDistillFidelityNoTruncation:
    """Key decisions and goals must NOT be truncated mid-sentence for compression."""

    def test_long_decision_is_not_truncated_with_ellipsis(self):
        """A decision longer than 120 chars must be preserved in full — NOT cut with '…'."""
        orch = _orch()
        long_decision = (
            "User: We decided to use FastAPI with JWT authentication, "
            "Postgres as the primary database, Redis for caching, "
            "and pytest with 90% coverage threshold for all new modules."
        )
        result = orch.distill(conversation=long_decision)
        assert result.success is True
        # Must not truncate key words
        assert "postgres" in result.distilled_prompt.lower()
        assert "redis" in result.distilled_prompt.lower()
        assert "pytest" in result.distilled_prompt.lower()
        assert "90%" in result.distilled_prompt

    def test_decision_content_not_cut_mid_sentence(self):
        """Distilled output must not end a decision item with '…' (truncation marker)."""
        orch = _orch()
        conversation = (
            "User: The system must use FastAPI, JWT auth, Postgres, Redis caching, "
            "pytest 90% coverage, and Docker for deployment with no rate limiting imposed.\n"
            "Agent: Confirmed, I will implement all of those.\n"
        )
        result = orch.distill(conversation=conversation)
        assert result.success is True
        # '…' as truncation marker must not appear — full text or smart summary
        assert "…" not in result.distilled_prompt

    def test_user_goal_fully_preserved_across_roles(self):
        """User-stated goals must be fully captured even if the statement spans multiple lines."""
        orch = _orch()
        conversation = (
            "asifhussain60: I want to:\n"
            "1. Build a FastAPI REST API\n"
            "2. Add JWT authentication\n"
            "3. Use Postgres as the database\n"
            "4. Add Redis caching\n"
            "5. Deploy with Docker\n"
            "GitHub Copilot: Understood. I will implement all five requirements.\n"
        )
        result = orch.distill(conversation=conversation)
        assert result.success is True
        prompt = result.distilled_prompt.lower()
        # All 5 requirements must survive — nothing silently dropped
        assert "fastapi" in prompt
        assert "jwt" in prompt
        assert "postgres" in prompt
        assert "redis" in prompt
        assert "docker" in prompt


# ---------------------------------------------------------------------------
# BUG-DISTILL-004: role-aware extraction — user turns dominate signal
# ---------------------------------------------------------------------------

class TestDistillRoleAwareExtraction:
    """User turns (asifhussain60 / User) must dominate signal extraction.
    Copilot/Agent turns must only contribute confirmed outcomes — not narration."""

    def test_copilot_response_headers_not_classified_as_context(self):
        """CORTEX response header lines ('# 🧠 CORTEX Building…') must NOT appear in output."""
        orch = _orch()
        conversation = (
            "asifhussain60: Fix the distillation orchestrator.\n"
            "GitHub Copilot: # 🧠 CORTEX Building\n"
            "**Author:** Asif Hussain | © 2025–2026\n"
            "> *'Make it work before making it fast.'*\n"
            "---\n"
            "The fix involves three changes to the segmenter.\n"
        )
        result = orch.distill(conversation=conversation)
        assert result.success is True
        # Header noise must not appear in output
        assert "🧠" not in result.distilled_prompt
        assert "Author:" not in result.distilled_prompt
        assert "© 2025" not in result.distilled_prompt

    def test_user_imperative_dominates_over_copilot_narration(self):
        """User instruction turns must produce more signal lines than Copilot narration turns."""
        orch = _orch()
        # 2 user imperatives, 3 Copilot narration paragraphs
        conversation = (
            "asifhussain60: Build a FastAPI app with JWT and Postgres.\n"
            "GitHub Copilot: # 🧠 CORTEX Building\n"
            "I will now create the project structure. First I read the existing files. "
            "Then I will scaffold the FastAPI application. "
            "The implementation will include JWT middleware and Postgres ORM integration. "
            "Let me start with the directory layout.\n"
            "asifhussain60: Add Redis caching. No rate limiting.\n"
            "GitHub Copilot: # 🧠 CORTEX Building\n"
            "I am now implementing Redis caching. I will skip rate limiting as instructed. "
            "The cache layer will wrap the database calls transparently.\n"
        )
        result = orch.distill(conversation=conversation)
        assert result.success is True
        prompt = result.distilled_prompt.lower()
        # Both user imperatives must appear in output
        assert "fastapi" in prompt
        assert "jwt" in prompt
        assert "postgres" in prompt
        assert "redis" in prompt

    def test_output_does_not_include_cortex_mode_phrases(self):
        """Mode phrases like 'CORTEX Building', 'CORTEX Fixing' must not appear in output."""
        orch = _orch()
        conversation = (
            "asifhussain60: Fix the segmenter.\n"
            "GitHub Copilot: # 🧠 CORTEX Fixing\n"
            "**Author:** Asif Hussain\n"
            "I will fix the segmenter by improving the role-aware extraction.\n"
            "asifhussain60: Good. Also add tests.\n"
            "GitHub Copilot: # 🧠 CORTEX Building\n"
            "I will now write the RED tests first per CORE-008.\n"
        )
        result = orch.distill(conversation=conversation)
        assert result.success is True
        assert "CORTEX Fixing" not in result.distilled_prompt
        assert "CORTEX Building" not in result.distilled_prompt

    def test_compression_preserves_minimum_80_percent_of_user_keywords(self):
        """At least 80% of unique keywords from user turns must survive in the distilled output."""
        orch = _orch()
        user_keywords = ["fastapi", "jwt", "postgres", "redis", "docker", "pytest", "90%"]
        conversation = (
            "asifhussain60: Use FastAPI, JWT auth, Postgres, Redis, Docker deployment.\n"
            "GitHub Copilot: # 🧠 CORTEX Building\n"
            "I will scaffold the project with all those components.\n"
            "asifhussain60: pytest coverage must be 90%.\n"
            "GitHub Copilot: # 🧠 CORTEX Building\n"
            "I will configure pytest with a 90% threshold.\n"
        )
        result = orch.distill(conversation=conversation)
        assert result.success is True
        prompt = result.distilled_prompt.lower()
        found = [kw for kw in user_keywords if kw in prompt]
        coverage = len(found) / len(user_keywords)
        assert coverage >= 0.8, (
            f"Only {len(found)}/{len(user_keywords)} user keywords preserved ({coverage:.0%}). "
            f"Missing: {[kw for kw in user_keywords if kw not in prompt]}"
        )
