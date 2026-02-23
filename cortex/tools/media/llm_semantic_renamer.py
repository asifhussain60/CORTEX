"""
cortex/tools/media/llm_semantic_renamer.py

LLM-powered semantic filename normalization for Plex video libraries.

Uses OpenAI GPT-4 or Anthropic Claude to generate meaningful filenames
from raw video titles. Example: "Chad Alva does Jojo Kiss" → "Chad Does Jojo"

Provides:
- Natural language understanding of performer names and actions
- Confidence scoring for automated vs. human-review decisions
- Content filtering to block inappropriate names
- Fallback to rule-based renaming on low confidence or API failure
- Rate limiting and cost controls

CORE-011: Type hints on all functions.
CORE-012: Google-style docstrings.
CORE-028: snake_case naming.

AC_START: AC-LLM-SEMANTIC-RENAMER-2026-02-23
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers."""

    IN_CONTEXT = "in_context"  # Use current VS Code Copilot conversation
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


@dataclass
class RenameProposal:
    """LLM-generated rename proposal."""

    original_name: str
    proposed_name: str
    confidence: float  # 0.0 - 1.0
    reasoning: str
    provider: str = ""


class LLMSemanticRenamer:
    """
    LLM-powered semantic filename normalization.

    Uses GPT-4 or Claude to generate meaningful, human-readable
    filenames from raw video titles.

    Attributes:
        provider: LLM provider (OpenAI or Anthropic).
        api_key: API key for provider.
        min_confidence: Minimum confidence threshold (0.0-1.0).
        enable_content_filter: Enable content filtering layer.
        enable_fallback: Fallback to rule-based on failure.
        rate_limit_per_second: Max API requests per second.
    """

    DEFAULT_PROMPT_TEMPLATE = """You are a filename normalization assistant for a video library.

Your task: Generate a clean, meaningful filename from the input title.

Rules:
1. Preserve performer names (first name + last initial is fine if long)
2. Use natural verb forms: "does" instead of "do", "kisses" instead of "kiss"
3. Remove redundant words like "action", "scene", "video"
4. Keep it concise (under 50 characters)
5. Use proper capitalization
6. Remove dates, resolutions (1080p), studio suffixes

Input filename: {input_filename}

Output as JSON:
{{
  "proposed_name": "...",
  "confidence": 0.95,
  "reasoning": "..."
}}

Confidence guidelines:
- 0.90-1.00: High confidence (clear names, simple structure)
- 0.70-0.89: Medium confidence (some ambiguity)
- 0.00-0.69: Low confidence (unclear, needs human review)
"""

    def __init__(
        self,
        provider: LLMProvider = LLMProvider.IN_CONTEXT,
        api_key: Optional[str] = None,
        model: str = "gpt-4",
        min_confidence: float = 0.85,
        enable_content_filter: bool = True,
        enable_fallback: bool = True,
        rate_limit_per_second: int = 5,
    ) -> None:
        """
        Initialize LLMSemanticRenamer.

        Args:
            provider: LLM provider (OpenAI or Anthropic).
            api_key: API key for provider.
            model: Model name (e.g., "gpt-4", "claude-3-opus").
            min_confidence: Minimum confidence threshold.
            enable_content_filter: Enable content filtering.
            enable_fallback: Fallback to rules on failure.
            rate_limit_per_second: Max requests per second.
        """
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.min_confidence = min_confidence
        self.enable_content_filter = enable_content_filter
        self.enable_fallback = enable_fallback
        self.rate_limit_per_second = rate_limit_per_second

        self._last_request_time = 0.0

        # Initialize provider client
        if provider == LLMProvider.IN_CONTEXT:
            # No initialization needed - will use current conversation context
            pass
        elif provider == LLMProvider.OPENAI:
            try:
                import openai

                self.openai = openai
                if api_key:
                    self.openai.api_key = api_key
            except ImportError:
                logger.error("OpenAI package not installed. Run: pip install openai")
                raise

        elif provider == LLMProvider.ANTHROPIC:
            try:
                import anthropic

                self.anthropic = anthropic
                if api_key:
                    self.anthropic_client = anthropic.Anthropic(api_key=api_key)
            except ImportError:
                logger.error(
                    "Anthropic package not installed. Run: pip install anthropic"
                )
                raise

    def _build_prompt(self, filename: str) -> str:
        """
        Build prompt for LLM.

        Args:
            filename: Input filename.

        Returns:
            Formatted prompt string.
        """
        return self.DEFAULT_PROMPT_TEMPLATE.format(input_filename=filename)

    def _rate_limit(self) -> None:
        """Enforce rate limiting."""
        if self.rate_limit_per_second <= 0:
            return

        time_since_last = time.time() - self._last_request_time
        min_interval = 1.0 / self.rate_limit_per_second

        if time_since_last < min_interval:
            time.sleep(min_interval - time_since_last)

        self._last_request_time = time.time()

    def _call_openai(self, prompt: str) -> Optional[Dict]:
        """
        Call OpenAI API.

        Args:
            prompt: Prompt text.

        Returns:
            Parsed JSON response or None on error.
        """
        try:
            self._rate_limit()

            response = self.openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a filename normalization assistant.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=200,
            )

            content = response.choices[0].message.content
            return json.loads(content)

        except Exception as exc:
            logger.error(f"OpenAI API error: {exc}")
            return None

    def _call_anthropic(self, prompt: str) -> Optional[Dict]:
        """
        Call Anthropic API.

        Args:
            prompt: Prompt text.

        Returns:
            Parsed JSON response or None on error.
        """
        try:
            self._rate_limit()

            response = self.anthropic_client.messages.create(
                model=self.model,
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}],
            )

            content = response.content[0].text
            return json.loads(content)

        except Exception as exc:
            logger.error(f"Anthropic API error: {exc}")
            return None

    def _apply_content_filter(self, proposed_name: str) -> bool:
        """
        Content filter to block inappropriate names.

        Args:
            proposed_name: Proposed filename.

        Returns:
            True if safe, False if blocked.
        """
        if not self.enable_content_filter:
            return True

        # Basic filter (expand as needed)
        blocked_words = ["explicit", "inappropriate", "offensive"]

        lower_name = proposed_name.lower()
        for word in blocked_words:
            if word in lower_name:
                logger.warning(f"Content filter blocked: {proposed_name}")
                return False

        return True

    def propose_rename(self, filename: str) -> Optional[RenameProposal]:
        """
        Propose semantic rename for filename.

        Args:
            filename: Original filename.

        Returns:
            RenameProposal or None if confidence too low or error.
        """
        logger.info(f"Proposing rename for: {filename}")

        prompt = self._build_prompt(filename)

        # Call LLM provider
        if self.provider == LLMProvider.IN_CONTEXT:
            # For in-context mode, return None (caller should use format_batch_prompt)
            logger.info("IN_CONTEXT mode: use format_batch_prompt() for VS Code integration")
            return None
        elif self.provider == LLMProvider.OPENAI:
            response = self._call_openai(prompt)
        elif self.provider == LLMProvider.ANTHROPIC:
            response = self._call_anthropic(prompt)
        else:
            logger.error(f"Unsupported provider: {self.provider}")
            return None

        if not response:
            return None

        # Parse response
        proposed_name = response.get("proposed_name", "")
        confidence = response.get("confidence", 0.0)
        reasoning = response.get("reasoning", "")

        # Preserve file extension
        original_ext = Path(filename).suffix
        if not proposed_name.endswith(original_ext):
            proposed_name += original_ext

        # Apply content filter
        if not self._apply_content_filter(proposed_name):
            return None

        # Check confidence threshold
        if confidence < self.min_confidence:
            logger.info(
                f"Confidence {confidence:.2f} below threshold {self.min_confidence}"
            )
            return None

        return RenameProposal(
            original_name=filename,
            proposed_name=proposed_name,
            confidence=confidence,
            reasoning=reasoning,
            provider=self.provider.value,
        )

    def propose_rename_with_fallback(self, filename: str) -> Optional[RenameProposal]:
        """
        Propose rename with fallback to rule-based.

        Args:
            filename: Original filename.

        Returns:
            RenameProposal (LLM or rule-based).
        """
        # Try LLM first
        proposal = self.propose_rename(filename)

        if proposal:
            return proposal

        # Fallback to rule-based
        if self.enable_fallback:
            logger.info(f"Falling back to rule-based for: {filename}")
            return self._rule_based_rename(filename)

        return None

    def _rule_based_rename(self, filename: str) -> Optional[RenameProposal]:
        """
        Fallback rule-based renaming.

        Args:
            filename: Original filename.

        Returns:
            RenameProposal using simple rules.
        """
        # Simple rule-based transformations
        from cortex.tools.media.generic_metadata_extractor import FilenameNormalizer

        normalizer = FilenameNormalizer()
        normalized = normalizer.normalize(filename)

        return RenameProposal(
            original_name=filename,
            proposed_name=normalized,
            confidence=0.70,  # Lower confidence for rules
            reasoning="Rule-based normalization (LLM fallback)",
            provider="rule-based",
        )

    def batch_propose_renames(
        self,
        filenames: List[str],
    ) -> Dict[str, Optional[RenameProposal]]:
        """
        Generate rename proposals for batch of files.

        Args:
            filenames: List of filenames.

        Returns:
            Dict mapping filename to RenameProposal.
        """
        proposals: Dict[str, Optional[RenameProposal]] = {}

        for filename in filenames:
            proposal = self.propose_rename_with_fallback(filename)
            proposals[filename] = proposal

        return proposals

    def format_batch_prompt(self, filenames: List[str]) -> str:
        """
        Format batch rename prompt for in-context LLM (VS Code Copilot).

        Use this in VS Code to get rename proposals from current conversation.

        Args:
            filenames: List of filenames to rename.

        Returns:
            Formatted prompt string to send to LLM.
        """
        prompt = f"""I need semantic filename normalization for {len(filenames)} Plex video files.

Rules:
1. Preserve performer names (first name + last initial if long)
2. Use natural verb forms: "does" instead of "do", "kisses" instead of "kiss"
3. Remove redundant words like "action", "scene", "video"
4. Keep it concise (under 50 characters)
5. Use proper capitalization
6. Remove dates, resolutions (1080p), studio suffixes

Filenames:
"""
        for i, filename in enumerate(filenames[:20], 1):  # Limit to 20 for context
            prompt += f"{i}. {filename}\n"

        prompt += """\n
Please provide rename proposals in JSON format:
{
  "proposals": [
    {
      "original": "Chad Alva does Jojo Kiss.mp4",
      "proposed": "Chad Does Jojo.mp4",
      "confidence": 0.95,
      "reasoning": "Natural verb form, preserves actor names"
    }
  ]
}
"""
        return prompt

    def parse_batch_response(self, response_json: str) -> Dict[str, Optional[RenameProposal]]:
        """
        Parse LLM response from in-context batch prompt.

        Args:
            response_json: JSON response from LLM.

        Returns:
            Dict mapping original filename to RenameProposal.
        """
        try:
            data = json.loads(response_json)
            proposals_dict: Dict[str, Optional[RenameProposal]] = {}

            for item in data.get("proposals", []):
                original = item.get("original", "")
                proposed = item.get("proposed", "")
                confidence = item.get("confidence", 0.0)
                reasoning = item.get("reasoning", "")

                # Preserve file extension
                original_ext = Path(original).suffix
                if not proposed.endswith(original_ext):
                    proposed += original_ext

                # Apply content filter
                if not self._apply_content_filter(proposed):
                    continue

                # Check confidence threshold
                if confidence < self.min_confidence:
                    continue

                proposals_dict[original] = RenameProposal(
                    original_name=original,
                    proposed_name=proposed,
                    confidence=confidence,
                    reasoning=reasoning,
                    provider="in_context",
                )

            return proposals_dict

        except json.JSONDecodeError as exc:
            logger.error(f"Failed to parse LLM response: {exc}")
            return {}


# AC_COMPLETE: AC-LLM-SEMANTIC-RENAMER-2026-02-23 ✅ (214ms)
