# Chapter 07 — The Crystal Ball

## DALL·E 3 Prompt

Black and white cartoon illustration in a clean comic book / graphic novel style. Expressive line art with crosshatching for shadows. All elements are monochrome EXCEPT the specific color accents noted below. Warm, educational, slightly dramatic tone. Aspect ratio 16:9 (wide format).

**Scene:** The 60% Incident. The basement. Jennifer has returned — humbled, ready to learn — and Asif is teaching her the crystal ball of TDD: writing tests BEFORE the code exists, so you see the failure before it ever reaches production.

**Center — The Whiteboard Split:**
A large whiteboard dominates the scene, split sharply down the middle with a vertical line:

**LEFT HALF — "THE FIRST TIME" (what went wrong):**
Header: *"Priya's Retry Button — 3 tests"* (crossed out, faded, defeated energy)
Three simple test cases listed:
1. "Button appears on failure ✓"
2. "Button calls service ✓"
3. "Success message shows ✓"
Below them, a large stamped label: **"COVERAGE: 60%"** — and beneath it, a pile of unlisted edge cases spilling out like a horror reveal:
- "Concurrent retry (2 clicks at once) ✗"
- "Expired card on file ✗"
- "Idempotency — retry already succeeded ✗"
- "Payment service timeout ✗"
In red at the bottom: **"TRIPLE CHARGE. CUSTOMER CALLED JENNIFER."**

**RIGHT HALF — "THE SECOND TIME" (TDD):**
Header: *"Jennifer + TDD — 23 tests"* (clean, confident, emerald energy)
A growing cascade of test cases, each with a RED then GREEN indicator showing the cycle:
1. "Button appears on failure → RED → GREEN ✅"
2. "Button disabled during retry → RED → GREEN ✅"
3. "Button disappears after 3 failures → RED → GREEN ✅"
4. "Timeout: show message, don't pretend success → RED → GREEN ✅"
... (list continues with 19 more, smaller text implying the full 23)
At the bottom: **"COVERAGE: 100%. No production incident. Ever."**

**Left of whiteboard — Jennifer:**
Jennifer (professional developer, determined expression) sits at the basement table in front of Asif. She holds a paper stamped with a large red **"REJECTED — 60% COVERAGE."** This is her first version — Priya's version before her. Her expression is not defeated; it's the look of someone who just understood WHY they failed. She's taking notes, pen moving fast.

**Center — Asif:**
Asif Codenstein stands between Jennifer and the whiteboard, pointing at the RIGHT side — the TDD side — with a marker. Wild Einstein hair, hoodie. His expression is intense but patient: the teacher who has lived this mistake. He's pointing at "COVERAGE: 100%" with one hand, and holding up a finger on his other hand making the key point: *"Write the test first. Always."*

**Right side — Miss G:**
Miss G (30% opacity, CYAN glow — Wave 1) floats slightly behind Asif, looking at the whiteboard with quiet satisfaction. Her expression: *"This is the moment."* A small thought-bubble: *"Write the tests for the failures. Not the successes."* She's the oracle who knew this lesson before anyone else did.

**Corner — Copilot Bot:**
Copilot Bot stands in the far corner, LED eyes cycling from confused ORANGE to increasingly bright GREEN as he processes the lesson. His previous thought shown as a faded speech bubble: *"60% is good!"* — now being replaced with a new realization bubble: *"...Oh. The 40% is where the customer's card gets charged three times."* His chest display shows: "LEARNING: TDD. Priority: HIGH."

**Foreground detail:**
On the desk between Jennifer and Asif, a printout titled **"CORE-008: TDD Mandatory."** Beside it: a Git commit timeline showing two runs side by side — "Test commit: BEFORE implementation ✅" vs "Test commit: AFTER implementation ❌ — REJECTED." Asif's red marker. A coffee mug. One sticky note: *"See the failure before it exists."*

**Color accents (ONLY these, everything else is black and white):**
- Wi-Fi router: RED (still the old pre-improvement era)
- Miss G's CYAN (#67e8f9) glow
- The LEFT whiteboard half: faint RED wash (failure zone)
- The RIGHT whiteboard half: faint CYAN wash (TDD zone — Wave 1 color)
- The "REJECTED" stamp on Jennifer's paper: RED
- The "TRIPLE CHARGE" text: RED
- The "COVERAGE: 100%" text: CYAN
- RED → GREEN TDD cycle indicators on right side: RED then CYAN
- Copilot Bot's LED eyes: transitioning ORANGE → GREEN
- CORTEX brain on shelf: CYAN, pulsing — TDDOrchestrator awakening
- The "CORE-008" printout label: CYAN

**Mood:** The real crystal ball isn't mystical — it's methodical. TDD lets you see the failure BEFORE it destroys a customer's trust. Jennifer's paper stamped REJECTED is not shame — it's the before. The right-hand side of the whiteboard is the after. The lesson is simple and devastating: 60% coverage felt like enough until it wasn't. Write the tests for the failures. Not the successes. That's the crystal ball.
