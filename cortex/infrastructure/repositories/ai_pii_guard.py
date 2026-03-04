"""
AIPIIGuard — strip personally-identifiable information from extracted AI context.

Phase 121 Sub-phase B | GAP-121-07.
Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
           CORE-028 (snake_case), CORE-035 (single canonical implementation).

Strips:
  - Email addresses
  - Internal / private URLs (non-public hostname patterns)
  - Author attribution lines (Author: Name, Maintained by: Name, Owner: Name)
Preserves:
  - Technical content (code patterns, identifiers, standards text)
  - Public URLs (github.com, pypi.org, etc.)
"""
from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

# ── Compiled patterns ─────────────────────────────────────────────────────────

_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

# Internal / private URLs: URLs whose hostnames contain internal TLDs or
# corporate-looking patterns (.corp, .internal, .local, .lan, or non-public
# single-label hostnames).  Public hosts like github.com are excluded.
_INTERNAL_URL_RE = re.compile(
    r"https?://(?:[a-zA-Z0-9.\-]+\.(?:corp|internal|local|lan|intra|int|net\.corp)"
    r"|[a-zA-Z0-9\-]+(?:\.[a-zA-Z0-9\-]+){0,2}(?:/[^\s]*)?)"
    r"\b",
    re.IGNORECASE,
)

# Exclude well-known public domains from URL redaction
_PUBLIC_DOMAINS = frozenset({
    "github.com", "gitlab.com", "bitbucket.org", "pypi.org",
    "npmjs.com", "docs.python.org", "stackoverflow.com",
    "microsoft.com", "google.com", "amazon.com", "azure.com",
})

# Author / attribution lines
_AUTHOR_RE = re.compile(
    r"(?:Author|Maintained by|Owner|Maintainer|Created by|Written by)\s*[:\-]\s*(.+)",
    re.IGNORECASE,
)


class AIPIIGuard:
    """
    Strip PII from extracted AI instruction text.

    Applies a set of targeted regex passes to remove email addresses,
    internal URLs, and author attribution patterns, while preserving all
    technical content (variable names, coding standards, architectural rules).

    Example::

        guard = AIPIIGuard()
        clean = guard.sanitize("Contact admin@example.com for help.")
    """

    def sanitize(self, text: str) -> str:
        """
        Strip PII from *text*.

        Args:
            text: Raw text that may contain emails, internal URLs, author names.

        Returns:
            Sanitised text with PII replaced by ``[REDACTED]``.
        """
        text = self._strip_emails(text)
        text = self._strip_internal_urls(text)
        text = self._strip_author_patterns(text)
        return text

    # ── Private helpers ───────────────────────────────────────────────────────

    def _strip_emails(self, text: str) -> str:
        """Replace all email addresses with ``[REDACTED]``."""
        return _EMAIL_RE.sub("[REDACTED]", text)

    def _strip_internal_urls(self, text: str) -> str:
        """
        Replace internal / non-public URLs with ``[REDACTED]``.

        Public domains (github.com, pypi.org, etc.) are preserved.
        """
        def _replace_if_internal(match: re.Match) -> str:
            url = match.group(0)
            # Extract hostname
            host_match = re.match(r"https?://([^/\s]+)", url, re.IGNORECASE)
            if not host_match:
                return "[REDACTED]"
            hostname = host_match.group(1).lower()
            if any(hostname == pub or hostname.endswith("." + pub) for pub in _PUBLIC_DOMAINS):
                return url  # preserve public URL
            return "[REDACTED]"

        return _INTERNAL_URL_RE.sub(_replace_if_internal, text)

    def _strip_author_patterns(self, text: str) -> str:
        """Replace author attribution lines with ``[REDACTED]``."""
        return _AUTHOR_RE.sub(
            lambda m: m.group(0).replace(m.group(1), "[REDACTED]"),
            text,
        )


__all__ = ["AIPIIGuard"]
