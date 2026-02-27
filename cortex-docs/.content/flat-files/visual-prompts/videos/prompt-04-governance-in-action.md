# Video Prompt 04 — Governance in Action

> **Duration:** 8 minutes · **Audience:** Software Engineers, Tech Leads
> **Depth:** 🔴 Developer-level — shows real rules, real violations, real enforcement
> **No overlap:** Image prompt-04 shows a static shield wall; this video shows governance *catching a violation, blocking a commit, and guiding the fix*

---

## ⚠️ VISUAL IDENTITY — MANDATORY

> **ALL visuals** must use the CORTEX dark glassmorphism palette. Background: `#0a0e27`. Panels: `rgba(26, 31, 58, 0.7)` with `rgba(255, 255, 255, 0.1)` borders and 10-20px backdrop blur. Primary accent: `#00d4ff` (cyan). Secondary accent: `#7b61ff` (purple). Success: `#00ff88`. Warning: `#ffa500`. Danger: `#ff4444`. Info: `#3b82f6`. Text: `#ffffff` (primary), `#a0a6c0` (secondary). Glow: `0 0 20px rgba(0, 212, 255, 0.3)`. Shadow: `0 8px 32px rgba(0, 0, 0, 0.37)`.
>
> **Logo watermark:** CORTEX logo embossed bottom-right corner, 15-25% opacity, ~6% frame width, throughout entire video.
>
> **Typography:** Space Grotesk (headings, bold, fade-in with upward slide), Inter (body, fade), JetBrains Mono (code/labels, character-by-character reveal).

---

## PROMPT

Create an 8-minute animated explainer video titled **"Governance in Action"** using the visual identity above. Show CORTEX's governance system as a living enforcement mechanism — not bureaucracy, but automated quality assurance.

### Scene 1 — Why Governance? (0:00 – 1:15)

**Open on:** A glassmorphic code panel. Code is being written — it looks fine. Developer hits "commit."

**Then reality hits:** Three panels appear simultaneously showing the consequences of ungoverned code:
1. A function without type hints → runtime TypeError in production (red flash)
2. A file named `myHelper.py` (camelCase) → import confusion, IDE autocomplete fails (amber flash)
3. Code committed without tests → regression found by a customer (red flash, expanding shockwave)

Each panel has a "cost" counter: hours of debugging, customer trust lost, team velocity hit.

**Analogy overlay** (`#a0a6c0`): *"A city without building codes — structures go up fast, but collapse unpredictably. Governance is the building code for software."*

**Narration:** "Governance isn't red tape. It's the difference between code that works today and code that works next year."

### Scene 2 — The 38 CORE Rules (1:15 – 2:45)

**The YAML registry materializes.** A file tree shows the governance rule definitions opening to reveal YAML files organized by tier.

**Rule categories emerge as glassmorphic columns:**

| Column | Color | Sample Rules |
|--------|-------|-------------|
| **Quality** | Cyan (`#00d4ff`) | CORE-011 (Type Hints), CORE-012 (Docstrings), CORE-028 (snake_case) |
| **Process** | Purple (`#7b61ff`) | CORE-008 (TDD First), CORE-064 (Sweep Completeness), CORE-048 (Validation Gate) |
| **Output** | Green (`#00ff88`) | CORE-002 (Inline Output), CORE-049 (Silent Execution) |
| **Architecture** | Amber (`#ffa500`) | CORE-035 (No Duplicates), CORE-011 (Type Hints — architecture integrity) |

Each column builds upward — rules stack like bricks in a wall. When all 38 are placed, the wall shimmers and transforms into the **shield barrier** (callback to Video 02, Station 4).

**Analogy overlay:** *"38 specific, measurable building codes — not opinions, not guidelines. Rules with teeth."*

**Animated detail for 3 key rules:**

- **CORE-008 (TDD):** Red heartbeat pulse → text: "Write failing test BEFORE implementation. No exceptions."
- **CORE-064 (Sweep Completeness):** A checklist with items checking off → text: "Every fix audit must exhaust its FULL catalogue. No partial sweeps."
- **CORE-002 (Inline Output):** A `.md` file icon with red X → text: "All output stays inline. Never create report files."

### Scene 3 — EnforcementOrchestrator: The Living Enforcer (2:45 – 4:30)

**The EnforcementOrchestrator appears** as a glassmorphic sentinel figure — not a person, but an abstract guardian shape made of connected glass panels with a cyan core.

**Pre-commit hook animation:**

1. Developer types `git commit -m "feat: add user validation"` in a glassmorphic terminal.
2. The commit triggers the **pre-commit hook** — visualized as the sentinel's eyes opening (two cyan circles).
3. The sentinel scans the staged files — each file passes through a row of 38 rule checkpoints.

**File-by-file scan (animated):**

- `validation.py` enters the scan tunnel:
  - CORE-011 (Type Hints): Function `validate_email(email)` → ❌ Missing type hint → Red badge. The sentinel's arm extends, blocks the file.
  - A glassmorphic violation card appears:
    ```
    VIOLATION: CORE-011
    File: validation.py:24
    Issue: Missing type hint on parameter 'email'
    Fix: def validate_email(email: str) -> bool:
    Severity: P1
    ```
  - The card has a red left border (`#ff4444`), glass background, JetBrains Mono code.

- `test_validation.py` enters the scan tunnel:
  - All 38 rules: ✅✅✅ — green cascade. File passes through.

**Analogy overlay:** *"Airport security X-ray — every piece of luggage is scanned. If something's flagged, it gets inspected before you board."*

**Narration:** "The EnforcementOrchestrator runs at pre-commit. Every. Single. Time. You can't bypass it — and that's the point."

### Scene 4 — The Fix Loop (4:30 – 6:00)

**The blocked file loops back.** Show the developer's screen:

1. The violation card is displayed. The fix suggestion is highlighted in cyan.
2. Developer applies the fix — character-by-character typing animation:
   ```python
   def validate_email(email: str) -> bool:
   ```
3. Developer re-commits. The sentinel scans again.
4. CORE-011: ✅ Green flash. All 38: ✅. Shield opens.

**But wait — CORE-064 (Sweep Completeness) triggers:**
- The sentinel notices there are 3 OTHER functions in the same file without type hints.
- A glassmorphic "Sweep Catalogue" card appears listing all 4 functions.
- **CORE-064 requires ALL to be fixed** — not just the one that was caught first.

**Analogy overlay:** *"The health inspector doesn't just check one dish — if they find an issue in the kitchen, they inspect EVERYTHING."*

- Developer fixes all 4. Re-commits. Full green cascade. Shield opens. Commit succeeds with green pulse and chime.

**AC markers appear** in a glassmorphic terminal panel:
```
AC_START: AC-GOVERNANCE-[timestamp]
...38 rules checked, 0 violations...
AC_COMPLETE: AC-GOVERNANCE-[timestamp] ✅ (890ms)
```

### Scene 5 — Three Enforcement Points (6:00 – 7:00)

**A timeline appears** — three enforcement checkpoints on a horizontal glassmorphic rail:

1. **Pre-Commit** (left) — EnforcementOrchestrator at `git commit` time
   - Icon: Shield with git branch symbol
   - "Catches violations before they enter version control"

2. **CI Pipeline** (center) — GitHub Actions / CI gate
   - Icon: Cloud with checkmark
   - "Validates across the full test suite in clean environment"

3. **Runtime** (right) — `cortex_validate` MCP tool
   - Icon: Radar pulse
   - "On-demand compliance check during development"

Arrows connect all three: "Same 38 rules, three checkpoints, zero escapes."

**Analogy overlay:** *"Three locks on the vault — key card at the lobby, fingerprint at the door, PIN at the safe. Redundant protection."*

### Scene 6 — The Governed Codebase (7:00 – 8:00)

**Camera pulls back** to a bird's-eye view of the entire codebase as a glassmorphic city grid.

- Every building (module) has a small green shield icon — governed.
- Traffic (commits) flows through the streets — each passing through shield checkpoints.
- The city is orderly, consistent, well-lit (cyan/purple glow).

**Contrast panel** (brief, 10 seconds): Show the same city without governance — buildings are different heights, some are dark, traffic is chaotic, a building collapses (red particles).

**Back to governed city.** Stats overlay:
- 38 rules active
- 3 enforcement points
- 0 partial sweeps allowed
- Every violation logged to the persistent audit trail

**Closing text** (Space Grotesk): **"Governance isn't overhead. It's the foundation everything else stands on."**

**Vision callback:**
> *"Thirty-eight rules your team will never have to remember, debate, or manually enforce again. That argument in the code review? Settled. Permanently."*

Logo pulse. End card.

---

## Notes

- Image prompt-04 shows governance as a static medieval shield wall. This video shows governance **actively catching a violation, blocking a commit, and enforcing a sweep** — completely different content.
- CORTEX rule IDs (CORE-008, CORE-011, CORE-064 etc.) are used throughout — these are the public-facing rule identifiers.
- The violation card format matches actual CORTEX output (file path, line number, severity, fix suggestion).
- Sound design: sentinel scanning = electronic sweep; violation = low warning tone; pass = pleasant chime; full green cascade = ascending arpeggio.
