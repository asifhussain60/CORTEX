# NotebookLM Video Prompt — CU-01 — What Good Engineering Habits Feel Like (Curious Users)

**Target length:** 8–11 minutes
**Audience:** Curious learners, early-career developers, bootcamp grads — people who write code but want to understand professional-grade engineering habits
**Narrator gender:** Female (CU-01 — odd position in series, per VBP-017)
**Visual theme:** Dark-blue glassmorphism · "Learning journey" progression · Warm white text, gentle cyan highlights
**Series position:** Discovery video — the only video framing CORTEX as a learning scaffold, not a production tool

---

## ⚠️ ZERO-OVERLAP DECLARATION
This video exclusively owns:
- The "learning scaffold" framing: CORTEX as a system that teaches engineering habits, not just enforces them
- The beginner's journey from "what do I do next?" to "I have a repeatable process"
- Plain-English analogy for every technical concept (one analogy per concept — VBP-010)
- The curiosity hook: why professional engineering disciplines exist, not just what they are

Does NOT repeat: architecture internals (Video 03), TDD mechanics for engineers (SE-01), governance enforcement model (Video 02), sprint outcomes (PO-01).

---

## Steering Prompt
*Paste into NotebookLM → Customize → Steering Prompt:*

> "Create an 8–11 minute learning-focused video for curious and early-career developers who want to understand what professional software engineering habits feel like. Use CORTEX as the lens — but teach the *habits* (TDD, systematic validation, workflow thinking, testing pyramid), not the product. Every technical concept must be introduced with a single, grounded real-world analogy before any technical language. Tone: a warm, calm mentor who explains 'why' before 'what'. No jargon without definition. Use only the provided sources."

---

## Ground-truth constraints
- This video teaches *habits*: TDD, workflow thinking, testing pyramid, validation discipline
- CORTEX is the scaffold that makes these habits automatic — not a replacement for understanding them
- Every technical concept gets one analogy before the technical explanation (VBP-010 — one per concept, max)
- Do not imply CORTEX teaches everything automatically — it provides structure and guardrails; the developer still decides
- Safe, honest framing: CORTEX helps you learn faster by giving you a framework to practice within
- Never use: "revolutionary", "game-changing", "magical", "automatic fix"

---

## Visual ingredients
Upload as PNG/JPG:
1. `cortex-docs/assets/diagrams/07-testing-testing-strategy-pyramid.md` — test pyramid (Scene 3)
2. `cortex-docs/assets/diagrams/05-workflow-tdd-cycle-and-fsm.md` — TDD cycle simplified (Scene 4)
3. `cortex-docs/assets/image-prompts/learner/01-learning-journey-map.prompt.md` — learning map (Scene 2)
4. `cortex-docs/assets/image-prompts/learner/02-knowledge-concept-map.prompt.md` — concept relationships (Scene 5)

**Cinematic treatment — Learning journey progression:**
The visual metaphor is a journey along a lit path in a dark environment — each concept learned lights another lamp along the path. When the video starts, only the first lamp is lit. By the end, the full path is illuminated. This is gentle and aspirational — not aggressive or overwhelming. The camera always moves forward along the path, never backward.

---

## Scene-by-scene breakdown

**SCENE 1 — "The 'What Do I Do Next?' Problem" [0:00–1:30]**
Visual: A single developer at a laptop. A new empty file open. Cursor blinking. No one is telling them what to do next.
No CORTEX. Just the blank canvas.
Narrator (female, mentor-tone): *"Every developer knows this feeling. You understand the requirement. You can write code. But the process — the sequence of steps that makes your code trustworthy — nobody handed you that."*
The blank file fades. A lit lamp appears on a dark path. Text beneath: `"Start here."`
VBP-002 hook: the opening visual is the developer's feeling, not the tool.

**SCENE 2 — "Workflows Are Recipes" [1:30–3:00]**
Analogy card (glassmorphic pill, warm white text on dark): `"A workflow is a recipe. It doesn't make you a chef — but it means you know what to do next."`
Visual: A recipe card materialises — but instead of ingredients, it shows: Think → Write Test → Implement → Verify → Validate → Done.
Each step lights a lamp along the path as the camera moves forward.
Narrator: *"A workflow isn't magic. It's a sequence of decisions, written down, so you don't have to reinvent the process for every feature. CORTEX provides workflow templates — YAML files that define the sequence. You don't have to design the process from scratch."*
YAML config card appears briefly: `implement-workflow.yaml` — just the step names visible, not the full syntax. Keeps it accessible.

**SCENE 3 — "The Testing Pyramid — Your Trust Gauge" [3:00–5:00]**
Analogy card: `"Tests are not bureaucracy. They are proof. Like a bridge load test — you test before the bridge opens, not after the truck falls."`
Visual: Test pyramid diagram — but each tier explained in plain English, bottom to top, one tier at a time:
  Base — Unit/Changed: `"Fast, specific. Run after every change. Are the gears turning?"`
  Middle — Smoke: `"Broad, quick. Run before you share. Does the engine start?"`
  Top — Integration/Golden: `"End-to-end. Run before release. Does the whole car drive?"`
Camera moves up the pyramid as each tier lights. The lamp path glows brighter with each tier explained.
Narrator: *"You don't run the top tier on every save — that would be slow. You don't run only the top tier — that misses small breaks. The pyramid tells you which test to run at which moment. CORTEX makes this decision automatic."*

**SCENE 4 — "TDD in Plain English" [5:00–7:30]**
Analogy card: `"TDD is writing the question before writing the answer. If you don't know what the correct answer looks like, how do you know when you're done?"`
Visual: Simplified TDD cycle (not the full FSM — just three coloured circles in sequence):
  🔴 RED — *"Write a test that describes what you want. Run it. It fails. That's correct."*
  🟢 GREEN — *"Write the simplest code that makes the test pass. Nothing more."*
  🔵 REFACTOR — *"Improve the code. The test still passes. You didn't break anything. That's the proof."*

Lamp path: three lamps light in RED, GREEN, BLUE as each phase narrates.
Narrator: *"The test failing first is not a mistake. It's evidence that the test is real. If you write the test and it passes immediately — without any implementation — the test is testing nothing."*
Simple code panel appears (pseudocode level, not framework-specific):
```
# First: the question
def test_greeting_includes_name():
    assert greet("Alice") == "Hello, Alice!"

# Then: the answer
def greet(name):
    return f"Hello, {name}!"
```

**SCENE 5 — "What CORTEX Gives You" [7:30–9:30]**
Visual: The learning journey map materialises — the full lit path visible for the first time. All lamps glowing.
Narrator: *"CORTEX doesn't make you a better developer by itself. It gives you a framework to practice within. The workflow tells you what to do next. The test gate stops you from skipping steps. The convergence check confirms you're actually done — not just done for now."*
Three habit cards materialise as glassmorphic panels:
  `"I have a process"` — workflow templates give you the sequence
  `"I know when I'm done"` — governance gates define done objectively
  `"I can explain my work"` — audit trace shows every decision
Narrator close: *"That's what professional engineering habits feel like. Not perfection — repeatability. Not 'I hope this works' — 'I can show you why it works.'"*
Final lamp on path fully illuminates. Path is complete.

**SCENE 6 — "Where to Start" [9:30–End]**
Visual: A simple three-step card — warm, not overwhelming:
  Step 1: `make test-smoke` — run this after every commit. Takes 60 seconds.
  Step 2: Write one failing test before your next feature. Run `make test-changed`.
  Step 3: When you're ready — run `/audit fix` and read the output. It will tell you what to learn next.
Narrator: *"You don't have to understand CORTEX fully to benefit from it. Run the smoke test. Write the failing test. The framework will show you where the gaps are. That's the learning."*

---

## Audio direction
- Warm ambient: soft melodic synth — more musical than the technical videos, lighter in texture
- Lamp lighting: a gentle bell tone each time a lamp illuminates on the path
- No industrial sound design — this is a learning environment, not a data centre
- Narrator pace: slower than the engineering videos — allow time for analogies to land

---

## Production note
Use NotebookLM for narrative + learning-journey slides. The lamp-path visual can be illustrated as a series of slides with progressive circle reveals — NotebookLM handles this well. The pseudocode in Scene 4 is intentionally language-agnostic to stay accessible; do not replace it with framework-specific code.
