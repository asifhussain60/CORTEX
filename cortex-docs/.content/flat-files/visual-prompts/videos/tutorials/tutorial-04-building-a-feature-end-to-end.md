# Tutorial 04 — Building a Feature End-to-End

> **Duration:** 10 minutes · **Audience:** Software Engineers
> **Depth:** 🔴 Tutorial — complete hands-on build session
> **Prerequisites:** Tutorials 01-02, concept Videos 02 (request lifecycle) + 05 (TDD)
> **Goal:** User builds a real feature from requirement to governed commit, experiencing the full CORTEX pipeline in their hands
> **No overlap:** Concept Video 05 explains TDD *philosophy*; this tutorial shows the engineer *doing it* with a real feature, including intent routing, governance enforcement, and the commit — the full arc, not just the TDD cycle

---

## ⚠️ VISUAL IDENTITY — MANDATORY

> **ALL visuals** must use the CORTEX dark glassmorphism palette. Background: `#0a0e27`. Panels: `rgba(26, 31, 58, 0.7)` with `rgba(255, 255, 255, 0.1)` borders and 10-20px backdrop blur. Primary accent: `#00d4ff` (cyan). Secondary accent: `#7b61ff` (purple). Success: `#00ff88`. Warning: `#ffa500`. Danger: `#ff4444`. Info: `#3b82f6`. Text: `#ffffff` (primary), `#a0a6c0` (secondary). Glow: `0 0 20px rgba(0, 212, 255, 0.3)`. Shadow: `0 8px 32px rgba(0, 0, 0, 0.37)`.
>
> **Logo watermark:** CORTEX logo embossed bottom-right corner, 15-25% opacity, ~6% frame width, throughout entire video.
>
> **Typography:** Space Grotesk (headings, bold, fade-in with upward slide), Inter (body, fade), JetBrains Mono (code/labels, character-by-character reveal).
>
> **Tutorial-specific:** Simulated VS Code UI as a PiP (picture-in-picture) overlay in the bottom-left corner throughout, showing actual commands being typed in Copilot Chat.

---

## PROMPT

Create a 10-minute animated tutorial video titled **"Building a Feature End-to-End"** using the visual identity above. The viewer will build a password strength validator from requirement to governed commit — experiencing every stage of the CORTEX pipeline through their own hands.

**Opening hook — no CORTEX introduction.** Start in the middle of the action.

---

### Scene 1 — The Requirement Lands (0:00 – 0:45)

**Open on:** A glassmorphic Jira-style ticket sliding into frame. No preamble, no logo animation — we're already at work.

```
TICKET-2847: Password Strength Validator
Priority: P1
Acceptance Criteria:
  - Minimum 8 characters
  - At least one uppercase, one lowercase, one digit, one symbol
  - Return strength score: weak / medium / strong
  - Reject common passwords (top-100 list)
```

The ticket casts a soft cyan shadow. A VS Code PiP panel opens in the bottom-left corner.

**Narration:** *"A ticket lands. In most teams, the next 30 minutes are spent figuring out where to start, what to test, and how to structure the code. Watch what happens when CORTEX is involved."*

---

### Scene 2 — Ask CORTEX for a Challenge (0:45 – 2:00)

**PiP shows Copilot Chat.** The user types:

```
/challenge Implement a password strength validator with scoring, minimum requirements, and common password rejection
```

**The `cortex_challenge` tool activates.** A glassmorphic analysis card renders:

```
⚔️ CHALLENGE ANALYSIS

Risk: 0.3 (LOW) | Scope: 2 files | Intent: IMPLEMENT

| Approach | Pros | Cons | ROI |
|----------|------|------|-----|
| A: Single function with regex | Simple, fast | Hard to extend, brittle regex | 🟡 |
| B: Strategy pattern with pluggable rules | Extensible, testable per rule | Slightly more code upfront | 🟢 |
| C: External library (zxcvbn) | Battle-tested | Heavy dependency for one feature | 🟡 |

Recommendation: Approach B — aligns with CORE-035 (single canonical),
each rule is independently testable (CORE-008 friendly).
```

**Narration:** *"Before writing a single line of code, CORTEX has already evaluated three approaches and recommended the one most aligned with the team's engineering standards. That decision, which often takes a 30-minute meeting, happened in two seconds."*

The user types: `proceed with B`

---

### Scene 3 — RED: Write the Failing Tests (2:00 – 4:00)

**The TDD heartbeat line** appears at the bottom of the screen — RED phase indicator pulses.

**PiP shows the engineer creating** `tests/test_password_validator.py`. The test file builds with characteristic CORTEX style:

```python
import pytest
from cortex.auth.password_validator import validate_password, PasswordStrength


class TestPasswordMinimumRequirements:
    """Tests for minimum password requirements."""

    def test_rejects_short_password(self) -> None:
        """Passwords under 8 characters must be rejected."""
        result = validate_password("Ab1!xyz")
        assert result.is_valid is False
        assert "minimum 8 characters" in result.errors

    def test_requires_uppercase(self) -> None:
        """Must contain at least one uppercase letter."""
        result = validate_password("abcdefg1!")
        assert result.is_valid is False

    def test_requires_digit(self) -> None:
        """Must contain at least one digit."""
        result = validate_password("Abcdefgh!")
        assert result.is_valid is False

    def test_requires_symbol(self) -> None:
        """Must contain at least one special character."""
        result = validate_password("Abcdefg1")
        assert result.is_valid is False


class TestPasswordStrengthScoring:
    """Tests for strength scoring algorithm."""

    def test_minimum_valid_is_weak(self) -> None:
        """A password that barely passes is weak."""
        result = validate_password("Abcdefg1!")
        assert result.strength == PasswordStrength.WEAK

    def test_long_varied_is_strong(self) -> None:
        """A long password with high variety is strong."""
        result = validate_password("C0mpl3x!P@ssw0rd#2026")
        assert result.strength == PasswordStrength.STRONG


class TestCommonPasswordRejection:
    """Tests for common password blocklist."""

    def test_rejects_password123(self) -> None:
        """Common passwords must be rejected regardless of format."""
        result = validate_password("Password123!")
        assert result.is_valid is False
        assert "common password" in result.errors
```

**Governance badges appear** as the code renders:
- CORE-011 ✅ Type hints present
- CORE-012 ✅ Docstrings on every test
- CORE-028 ✅ snake_case naming

**PiP terminal runs:** `make test-changed`

```
FAILED test_rejects_short_password - ModuleNotFoundError
FAILED test_requires_uppercase - ModuleNotFoundError
FAILED test_requires_digit - ModuleNotFoundError
... 8 FAILED in 0.1s
```

All red. The heartbeat line shows a red peak. A glassmorphic card pulses:

> *"Eight failing tests. Eight precise definitions of what 'done' looks like. The exam paper is written. Now solve it."*

---

### Scene 4 — GREEN: Implement the Minimum (4:00 – 6:30)

**GREEN phase indicator pulses.** Heartbeat line transitions.

**PiP shows** `cortex/auth/password_validator.py` being created. The strategy pattern builds:

```python
"""Password strength validator with pluggable rule strategy."""
from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import List, Protocol


class PasswordStrength(enum.Enum):
    """Password strength classification."""
    WEAK = "weak"
    MEDIUM = "medium"
    STRONG = "strong"


@dataclass
class ValidationResult:
    """Result of password validation."""
    is_valid: bool
    strength: PasswordStrength
    errors: List[str] = field(default_factory=list)
    score: int = 0


class PasswordRule(Protocol):
    """Protocol for pluggable password rules."""
    def check(self, password: str) -> str | None: ...


class MinLengthRule:
    """Enforce minimum password length."""
    def check(self, password: str) -> str | None:
        if len(password) < 8:
            return "minimum 8 characters required"
        return None


class CommonPasswordRule:
    """Reject passwords from the top-100 common list."""
    _COMMON = {"password123", "123456789", "qwerty123", ...}

    def check(self, password: str) -> str | None:
        if password.lower().rstrip("!@#$%") in self._COMMON:
            return "common password detected"
        return None

# ... remaining rules and validate_password() function ...
```

**Key moment** — the animation pauses on the `Protocol` class:

**Narration:** *"Notice the strategy pattern. Each rule is a separate class with one job. Easy to test individually, easy to add new rules later. This is the approach CORTEX recommended, and it's already paying off — each test maps to one rule."*

**PiP terminal:** `make test-changed`

```
PASSED test_rejects_short_password ✅
PASSED test_requires_uppercase ✅
PASSED test_requires_digit ✅
PASSED test_requires_symbol ✅
PASSED test_minimum_valid_is_weak ✅
PASSED test_long_varied_is_strong ✅
PASSED test_rejects_password123 ✅
... 8 PASSED in 0.2s
```

Green cascade. Heartbeat shows green peak. Ascending chime.

---

### Scene 5 — BLUE: Refactor with Confidence (6:30 – 7:15)

**BLUE phase indicator.** Quick refactoring montage:

1. Extract `_COMMON_PASSWORDS` to a separate `data/common_passwords.txt` file
2. Add a `__all__` export to the module
3. Consolidate rule registration into a `DEFAULT_RULES` list

**Each change → rerun tests → all green.** The confidence is absolute. The heartbeat trace shows a steady blue peak.

**Narration:** *"Refactoring with a green test suite isn't bravery — it's certainty. Every change is verified in under a second."*

---

### Scene 6 — The Governance Gate (7:15 – 8:30)

**PiP shows the terminal:**

```bash
git add cortex/auth/ tests/test_password_validator.py
git commit -m "feat(auth): add password strength validator with pluggable rule strategy"
```

**The EnforcementOrchestrator activates.** A glassmorphic shield scanner sweeps the staged files:

- CORE-008 (TDD): Tests created before implementation? → `git log` timestamps confirm test file committed first → ✅
- CORE-011 (Type Hints): All function signatures typed? → ✅
- CORE-012 (Docstrings): All public APIs documented? → ✅
- CORE-028 (snake_case): File names checked → ✅
- CORE-035 (No duplicates): No existing password validator in codebase? → ✅
- CORE-064 (Sweep Completeness): All acceptance criteria covered? → ✅

**38 rules cascade green.** The shield opens. Commit proceeds.

**AC marker logs:**
```
AC_START: AC-IMPLEMENT-20260227T143500
Feature: password_validator | Tests: 8 | Coverage: 100%
Approach: strategy_pattern (challenge-recommended)
AC_COMPLETE: AC-IMPLEMENT-20260227T143500 ✅ (847ms)
```

---

### Scene 7 — The Complete Arc (8:30 – 9:15)

**Camera pulls back.** A glassmorphic timeline shows the entire session as a horizontal flow:

```
Ticket   →   Challenge   →   RED     →   GREEN   →   BLUE   →   Commit
(0:00)       (0:45)         (2:00)      (4:00)      (6:30)     (7:15)
```

Each phase node glows its signature color. Total time: **~8 minutes** from ticket to governed commit.

**Comparison panel** (glassmorphic split):

| Without CORTEX | With CORTEX |
|---|---|
| 30 min debating approach in Slack | 2 sec: challenge analysis |
| Forgot to write tests for edge cases | 8 tests written first — every edge covered |
| Reviewer finds missing type hints | Governance caught it at commit |
| No traceability | AC markers log every decision |
| **~2 hours** | **~8 minutes** |

---

### Scene 8 — Close (9:15 – 10:00)

**Narration:** *"Eight minutes. From ticket to production-ready, governed, tested code. Not because you typed faster — because you stopped doing the work CORTEX does better."*

**Closing text** (Space Grotesk):
**"Think about the product. Let CORTEX think about the process."**

**Vision callback:**
> *"That two-hour feature cycle you just compressed into eight minutes? Multiply it by every engineer, every day, every sprint. That's the real ROI."*

Logo pulse. End card.

---

## Notes

- This tutorial is the **signature walkthrough** — the one that converts skeptics. Every scene demonstrates tangible time savings.
- The password validator feature is practical and relatable — every engineer has built one.
- Code is syntactically correct Python following all CORTEX conventions.
- The comparison panel (Scene 7) is the emotional peak — viewers see the before/after side by side.
- NO concept re-explanations. TDD rhythm is shown but not re-taught (Video 05). Governance is enforced but not re-explained (Video 04). Forward references only.
- Sound design: ticket arrival = subtle notification; challenge delivery = soft impact; test cascade = rhythmic tapping; green cascade = ascending; commit success = satisfying lock-click.
