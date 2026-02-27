# Video Prompt 05 — TDD Mastery

> **Duration:** 9 minutes · **Audience:** Software Engineers
> **Depth:** 🔴 Developer-level — real code, real test output, real cycle
> **No overlap:** Image prompt-05 shows the TDD heartbeat as a static ECG waveform; this video shows a complete TDD implementation session from blank file to passing tests

---

## ⚠️ VISUAL IDENTITY — MANDATORY

> **ALL visuals** must use the CORTEX dark glassmorphism palette. Background: `#0a0e27`. Panels: `rgba(26, 31, 58, 0.7)` with `rgba(255, 255, 255, 0.1)` borders and 10-20px backdrop blur. Primary accent: `#00d4ff` (cyan). Secondary accent: `#7b61ff` (purple). Success: `#00ff88`. Warning: `#ffa500`. Danger: `#ff4444`. Info: `#3b82f6`. Text: `#ffffff` (primary), `#a0a6c0` (secondary). Glow: `0 0 20px rgba(0, 212, 255, 0.3)`. Shadow: `0 8px 32px rgba(0, 0, 0, 0.37)`.
>
> **Logo watermark:** CORTEX logo embossed bottom-right corner, 15-25% opacity, ~6% frame width, throughout entire video.
>
> **Typography:** Space Grotesk (headings, bold, fade-in with upward slide), Inter (body, fade), JetBrains Mono (code/labels, character-by-character reveal).

---

## PROMPT

Create a 9-minute animated explainer video titled **"TDD Mastery"** using the visual identity above. Walk through a complete TDD session inside CORTEX — from receiving a requirement to shipping tested, governed code.

### Scene 1 — The TDD Philosophy (0:00 – 1:30)

**Open on:** A glassmorphic split screen.

**Left side — "Code First" (anti-pattern):**
- Developer writes `def calculate_discount(price, tier):` and a full implementation.
- Then writes tests — but the tests are reverse-engineered to match the code.
- A red warning label appears: "Tests confirm what IS, not what SHOULD BE."
- The panel dims, stamped with a muted red X.

**Right side — "Test First" (CORTEX way):**
- Developer writes `def test_gold_tier_gets_20_percent():` first — the test fails (red).
- Then writes minimum implementation — test passes (green).
- Then refactors — still green.
- The panel glows cyan, stamped with ✅.

**Analogy overlay** (`#a0a6c0`): *"Building a house: Code-First is like building walls, then drawing blueprints to match. Test-First is drawing blueprints, then building walls that fit."*

**The TDD Heartbeat line** appears at the bottom — a continuous ECG trace that will pulse throughout the entire video:
- 🔴 RED peak when writing a failing test
- 🟢 GREEN peak when implementation passes
- 🔵 BLUE peak when refactoring

**Narration:** "CORE-008: Tests before implementation. No exceptions. This isn't a preference — it's a governance rule."

### Scene 2 — The Requirement Arrives (1:30 – 2:30)

**A glassmorphic task card** slides in from the top:

```
Feature: Discount Calculator
- Bronze customers: 5% discount
- Silver customers: 10% discount
- Gold customers: 20% discount
- Invalid tier: raise ValueError
```

**The TDDOrchestrator** materializes as a glassmorphic workflow controller — a panel with three phase indicators (RED, GREEN, BLUE), currently all dimmed.

- The task card feeds into the TDDOrchestrator.
- The orchestrator's first phase indicator lights up: **RED**.
- File tree on the left shows two files being created:
  - `tests/test_discount.py` (glowing red border)
  - `cortex/discount.py` (dimmed, empty)

**Analogy overlay:** *"The exam proctor hands out the test paper before the student starts studying."*

### Scene 3 — RED Phase: Write the Failing Test (2:30 – 4:00)

**The RED phase indicator pulses.** Heartbeat line shows a red peak.

**Test file builds character by character** in a glassmorphic code panel (JetBrains Mono, left side):

```python
import pytest
from cortex.discount import calculate_discount


class TestDiscountCalculator:
    """Tests for the discount calculator."""

    def test_bronze_tier_gets_5_percent(self) -> None:
        """Bronze customers receive 5% discount."""
        assert calculate_discount(100.0, "bronze") == 95.0

    def test_silver_tier_gets_10_percent(self) -> None:
        """Silver customers receive 10% discount."""
        assert calculate_discount(100.0, "silver") == 90.0

    def test_gold_tier_gets_20_percent(self) -> None:
        """Gold customers receive 20% discount."""
        assert calculate_discount(100.0, "gold") == 80.0

    def test_invalid_tier_raises_error(self) -> None:
        """Invalid tier should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown tier"):
            calculate_discount(100.0, "platinum")
```

**Governance annotations** appear as floating badges next to the code:
- Line `def test_bronze_tier_gets_5_percent(self) -> None:` → CORE-011 ✅ (type hint present)
- Docstrings → CORE-012 ✅
- File name `test_discount.py` → CORE-028 ✅ (snake_case)

**Run tests animation:**
- Terminal panel slides in from the right: `make test-changed`
- Output appears line by line:
  ```
  tests/test_discount.py::test_bronze_tier_gets_5_percent FAILED ❌
  tests/test_discount.py::test_silver_tier_gets_10_percent FAILED ❌
  tests/test_discount.py::test_gold_tier_gets_20_percent FAILED ❌
  tests/test_discount.py::test_invalid_tier_raises_error FAILED ❌
  4 failed in 0.3s
  ```
- Each FAILED line flashes red. The overall status bar turns red.
- **This is correct.** A glassmorphic info card appears: "4 tests failing = RED phase complete. We know exactly what success looks like."

**Analogy overlay:** *"Writing the exam questions and answer key before the student studies. Now we know precisely what 'passing' means."*

### Scene 4 — GREEN Phase: Minimum Implementation (4:00 – 5:30)

**The GREEN phase indicator lights up.** Heartbeat line shows a green peak.

**Implementation file builds** in a second code panel (right side):

```python
def calculate_discount(price: float, tier: str) -> float:
    """Calculate discounted price based on customer tier.

    Args:
        price: Original price.
        tier: Customer tier ('bronze', 'silver', 'gold').

    Returns:
        Discounted price.

    Raises:
        ValueError: If tier is not recognized.
    """
    discounts = {
        "bronze": 0.05,
        "silver": 0.10,
        "gold": 0.20,
    }
    if tier not in discounts:
        raise ValueError(f"Unknown tier: {tier}")
    return price * (1 - discounts[tier])
```

**Governance badges** appear again: CORE-011 ✅, CORE-012 ✅, CORE-028 ✅.

**Run tests again:**
- Terminal: `make test-changed`
- Output:
  ```
  tests/test_discount.py::test_bronze_tier_gets_5_percent PASSED ✅
  tests/test_discount.py::test_silver_tier_gets_10_percent PASSED ✅
  tests/test_discount.py::test_gold_tier_gets_20_percent PASSED ✅
  tests/test_discount.py::test_invalid_tier_raises_error PASSED ✅
  4 passed in 0.2s
  ```
- Each PASSED line flashes green. The status bar turns green. A pleasant chime plays.

**Analogy overlay:** *"Study the material, then take the exam. All answers correct — minimum effective study."*

### Scene 5 — BLUE Phase: Refactor with Confidence (5:30 – 6:45)

**The BLUE phase indicator lights up.** Heartbeat line shows a blue peak.

**Refactoring animation** — the implementation code transforms:

1. **Extract constant:** `discounts` dict moves to module level as `TIER_DISCOUNTS` (animated slide upward).
2. **Add edge case test:** A new test appears in the test file:
   ```python
   def test_zero_price_returns_zero(self) -> None:
       """Zero price should return zero regardless of tier."""
       assert calculate_discount(0.0, "gold") == 0.0
   ```
3. **Run tests:** 5 passed ✅ (the new test also passes — zero times anything is zero).

**The point:** Code changed, tests still green. Confidence is absolute.

**Analogy overlay:** *"Rearranging furniture in a room — the room still works, it just flows better."*

### Scene 6 — The TDD Rhythm: Multiple Cycles (6:45 – 7:45)

**Time-lapse montage** showing 3 more rapid TDD cycles:

1. **Cycle 2:** Add `test_negative_price_raises_error` (RED) → Add validation (GREEN) → Extract validator (BLUE)
2. **Cycle 3:** Add `test_case_insensitive_tier` (RED) → Add `.lower()` (GREEN) → Clean up (BLUE)
3. **Cycle 4:** Add `test_custom_discount_override` (RED) → Add optional parameter (GREEN) → Simplify (BLUE)

Each cycle is compressed to ~20 seconds. The heartbeat line traces: red-green-blue, red-green-blue, red-green-blue — a steady, confident rhythm.

**Show the growing test count** in a glassmorphic counter: 4 → 5 → 6 → 7 → 8 tests. Coverage: 100%.

**Analogy overlay:** *"A musician practicing scales — the rhythm becomes automatic, and every note is deliberate."*

### Scene 7 — TDD + Governance Integration (7:45 – 8:30)

**The completed code is ready to commit.** Show the integration:

1. `git commit` triggers → EnforcementOrchestrator scans
2. CORE-008 check: "Tests exist AND were written before implementation?" → ✅ (git blame timestamps confirm test file was created first)
3. CORE-064 check: "All discount tiers covered?" → ✅ (sweep catalogue exhausted)
4. All 38 rules: ✅ green cascade

**AC markers log:**
```
AC_START: AC-TDD-20260227T160045
Cycles: 4 | Tests: 8 | Coverage: 100%
AC_COMPLETE: AC-TDD-20260227T160045 ✅ (12,450ms)
```

**Narration:** "TDD isn't just a practice in CORTEX — it's a governed, measured, logged process. Every cycle is tracked."

### Scene 8 — The Payoff (8:30 – 9:00)

**Split screen comparison:**

| Without TDD | With TDD |
|---|---|
| 47% test coverage | 100% test coverage |
| 12 production bugs/month | 0 production bugs/month |
| "I think it works" | "I can prove it works" |
| Hours debugging regressions | Seconds to pinpoint failures |

Each row animates: left side in dim amber, right side in bright green.

**Closing text** (Space Grotesk): **"Tests aren't proof that your code works. Tests are the definition of what 'works' means."**

Logo pulse. End card.

---

## Notes

- Image prompt-05 shows TDD as a static ECG heartbeat with three colored peaks. This video shows a **complete TDD session** with real code being written, tests running, and the cycle repeating — completely different content.
- Real Python code is shown — syntactically correct, follows CORTEX conventions (type hints, docstrings, snake_case).
- The heartbeat line at the bottom is a persistent visual element throughout — it ties back to the image prompt's concept but extends it into motion.
- Sound design: typing = soft mechanical keyboard clicks; test fail = low tone; test pass = pleasant chime; full green = ascending arpeggio.
- The refactoring phase must show tests still passing AFTER changes — this is the key confidence moment.
