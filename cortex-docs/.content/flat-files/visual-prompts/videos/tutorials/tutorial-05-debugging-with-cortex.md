# Tutorial 05 — Debugging with CORTEX

> **Duration:** 9 minutes · **Audience:** Software Engineers
> **Depth:** 🔴 Tutorial — hands-on debugging session with live diagnosis
> **Prerequisites:** Tutorial 01 (installation), concept Video 03 (intelligence engine)
> **Goal:** User encounters a real bug, uses the CORTEX multi-stack debug pipeline to diagnose and fix it — experiencing marker injection, log capture, analysis, fix-plan generation, and cleanup
> **No overlap:** Concept Video 03 explains LENS *analysis capabilities*; this tutorial shows the engineer *using debug tools* on a live bug — the diagnostic experience, not the theory

---

## ⚠️ VISUAL IDENTITY — MANDATORY

> **ALL visuals** must use the CORTEX dark glassmorphism palette. Background: `#0a0e27`. Panels: `rgba(26, 31, 58, 0.7)` with `rgba(255, 255, 255, 0.1)` borders and 10-20px backdrop blur. Primary accent: `#00d4ff` (cyan). Secondary accent: `#7b61ff` (purple). Success: `#00ff88`. Warning: `#ffa500`. Danger: `#ff4444`. Info: `#3b82f6`. Text: `#ffffff` (primary), `#a0a6c0` (secondary). Glow: `0 0 20px rgba(0, 212, 255, 0.3)`. Shadow: `0 8px 32px rgba(0, 0, 0, 0.37)`.
>
> **Logo watermark:** CORTEX logo embossed bottom-right corner, 15-25% opacity, ~6% frame width, throughout entire video.
>
> **Typography:** Space Grotesk (headings, bold, fade-in with upward slide), Inter (body, fade), JetBrains Mono (code/labels, character-by-character reveal).
>
> **Tutorial-specific:** Simulated VS Code UI as a PiP (picture-in-picture) overlay in the bottom-left corner throughout, showing actual commands being typed in Copilot Chat and terminal output.

---

## PROMPT

Create a 9-minute animated tutorial video titled **"Debugging with CORTEX"** using the visual identity above. The viewer will hit a confusing runtime error, use the CORTEX debug pipeline (`/debug`) to inject diagnostic markers, capture logs, receive an AI-generated fix plan, apply the fix, and clean up — all without manually adding print statements or stepping through a debugger.

**Opening hook — jump straight into the problem.** No logos, no intros.

---

### Scene 1 — The Bug Bites (0:00 – 0:50)

**Open on:** A VS Code PiP showing a test run crashing mid-suite. The terminal flashes red:

```
FAILED tests/test_data_pipeline.py::TestTransformStage::test_nested_json_flatten

E   TypeError: unhashable type: 'dict'

    result = transformer.flatten(nested_payload)
>   assert result["metadata.tags"] == ["alpha", "beta"]

tests/test_data_pipeline.py:87: TypeError
```

The error message glows `#ff4444`. A frustration indicator pulses at the top of the screen: **`CONTEXT: 0% — What caused this?`**

**Narration:** *"Unhashable type: dict. Deep inside a data transformer. The stack trace points at line 87 but the bug isn't there — it's somewhere in the flatten logic three layers down. You could scatter print statements. You could attach a debugger and step through fifty iterations. Or..."*

---

### Scene 2 — Launch the Debug Pipeline (0:50 – 2:00)

**PiP: Copilot Chat.** The user types:

```
/debug cortex/data/transformer.py
```

**The DebuggerOrchestrator activates.** A 5-phase pipeline card renders with glassmorphic stages:

```
🔬 DEBUG PIPELINE — cortex/data/transformer.py

Phase 1: INJECT    — Insert diagnostic markers (8 strategies)
Phase 2: CAPTURE   — Run tests, collect annotated output
Phase 3: ANALYZE   — Correlate markers with failure point
Phase 4: FIX-PLAN  — Generate ranked fix proposals
Phase 5: CLEANUP   — Remove all CORTEX_DEBUG markers

Status: Phase 1 starting...
```

**Narration:** *"Five phases. The entire diagnostic process — from hypothesis to fix to cleanup — automated. Let's watch."*

---

### Scene 3 — Phase 1: Marker Injection (2:00 – 3:30)

**The MarkerInjectionEngine** scans `transformer.py`. The file scrolls in a glassmorphic code panel. Strategic debug markers appear at key points, highlighted in amber (`#ffa500`):

```python
def flatten(self, data: dict, prefix: str = "") -> dict:
    # CORTEX_DEBUG[ENTRY]: flatten(prefix={prefix}, keys={list(data.keys())})
    result = {}
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        # CORTEX_DEBUG[BRANCH]: type(value)={type(value).__name__}, full_key={full_key}
        if isinstance(value, dict):
            # CORTEX_DEBUG[RECURSE]: entering nested dict at {full_key}
            nested = self.flatten(value, prefix=full_key)
            result.update(nested)
        elif isinstance(value, list):
            # CORTEX_DEBUG[LIST]: list at {full_key}, len={len(value)}, types={[type(v).__name__ for v in value]}
            result[full_key] = value
        else:
            result[full_key] = value
    # CORTEX_DEBUG[EXIT]: flatten returning {len(result)} keys
    return result
```

**8 strategy badges** appear as markers are injected:
1. ENTRY/EXIT tracing ✅
2. Branch coverage ✅
3. Type inspection ✅
4. Recursion depth ✅
5. Collection profiling ✅
6. Variable snapshots ✅
7. Exception boundaries ✅
8. Timing probes ✅

A counter: **14 markers injected across 3 functions.**

**Narration:** *"Fourteen diagnostic markers, placed at every decision point, recursion boundary, and type transition. No manual placement. No guessing where to look. The eight injection strategies cover the paths most likely to reveal the fault."*

---

### Scene 4 — Phase 2 & 3: Capture and Analyze (3:30 – 5:30)

**Phase 2 — CAPTURE.** The test reruns. Debug output streams in a scrolling glassmorphic log panel:

```
[CORTEX_DEBUG][ENTRY] flatten(prefix=, keys=['id', 'metadata', 'scores'])
[CORTEX_DEBUG][BRANCH] type(value)=str, full_key=id
[CORTEX_DEBUG][BRANCH] type(value)=dict, full_key=metadata
[CORTEX_DEBUG][RECURSE] entering nested dict at metadata
[CORTEX_DEBUG][ENTRY] flatten(prefix=metadata, keys=['tags', 'author', 'nested_config'])
[CORTEX_DEBUG][BRANCH] type(value)=list, full_key=metadata.tags
[CORTEX_DEBUG][LIST] list at metadata.tags, len=2, types=['str', 'str'] ✅
[CORTEX_DEBUG][BRANCH] type(value)=dict, full_key=metadata.nested_config  ← ⚠️
[CORTEX_DEBUG][RECURSE] entering nested dict at metadata.nested_config
[CORTEX_DEBUG][ENTRY] flatten(prefix=metadata.nested_config, keys=['options'])
[CORTEX_DEBUG][BRANCH] type(value)=list, full_key=metadata.nested_config.options
[CORTEX_DEBUG][LIST] list at metadata.nested_config.options, len=3, types=['dict', 'dict', 'dict']  ← 🔴
```

**The smoking gun glows red.** The camera zooms in:

```
types=['dict', 'dict', 'dict']  ← 🔴 LIST CONTAINS DICTS
```

**Phase 3 — ANALYZE.** A glassmorphic diagnosis card assembles:

```
🔍 ROOT CAUSE ANALYSIS

File: cortex/data/transformer.py:47
Function: flatten()
Line: result[full_key] = value  (list branch)

DIAGNOSIS: The list branch stores raw list values without inspecting
their contents. When a list contains dict elements, downstream code
attempts to use them as dict keys (line 87 assertion), causing
"unhashable type: dict".

CORRELATION:
  marker [LIST] at metadata.nested_config.options
  → types=['dict', 'dict', 'dict']
  → this list passes through un-flattened
  → downstream hash operation fails

CONFIDENCE: 94%
```

**Narration:** *"The list at `metadata.nested_config.options` contains dictionaries. The flatten function stores the raw list without processing those nested dicts. When downstream code tries to compare or hash the result — TypeError. Found in under a minute. No print statements. No stepping."*

---

### Scene 5 — Phase 4: Fix Plan (5:30 – 7:00)

**A ranked fix proposal card renders:**

```
🛠️ FIX PLAN — Ranked by confidence & scope

FIX 1 (Recommended — Confidence: 96%):
  Add recursive handling for lists containing dicts.
  When a list element is a dict, flatten it with an indexed prefix.

  result[f"{full_key}[{i}].{nested_key}"] = nested_val

  Impact: 1 file, 8 lines added
  Risk: LOW — additive change, no existing behaviour modified
  Tests: All 8 existing tests remain green + 1 new test needed

FIX 2 (Alternative — Confidence: 78%):
  Stringify dict elements in lists.
  Simpler but lossy — nested structure is destroyed.
  Impact: 1 file, 2 lines
  Risk: MEDIUM — data fidelity loss

FIX 3 (Conservative — Confidence: 70%):
  Raise explicit error when lists contain non-primitive types.
  Safest but doesn't solve the feature requirement.
```

The user selects **Fix 1**. CORTEX applies the change:

```python
elif isinstance(value, list):
    for i, item in enumerate(value):
        if isinstance(item, dict):
            nested = self.flatten(item, prefix=f"{full_key}[{i}]")
            result.update(nested)
        else:
            result[full_key] = value
            break
    else:
        if not value:
            result[full_key] = value
```

**Rerun tests:**

```
tests/test_data_pipeline.py ... 8 PASSED ✅ in 0.3s
```

**All green.** The heartbeat trace shifts from red to green.

**Narration:** *"Three options, ranked by confidence and risk. The recommended fix adds recursive handling — eight lines, no existing behaviour changed, all tests pass. The diagnosis that would have taken an hour of printf debugging took CORTEX forty-five seconds."*

---

### Scene 6 — Phase 5: Cleanup (7:00 – 7:45)

**PiP shows Copilot Chat:**

```
/debug-cleanup
```

**The AutoCleanupManager activates.** A sweep animation runs through `transformer.py`, removing all 14 `CORTEX_DEBUG` markers:

```
🧹 CLEANUP COMPLETE

  Markers removed: 14/14
  Files cleaned: 1
  Production-ready: ✅
  Diff verification: no functional code changed
```

**A before/after diff** shows the file — only the real fix remains. All diagnostic markers are gone.

**Narration:** *"Fourteen markers injected. Fourteen markers removed. The only change left is the fix. Production-ready. No debug residue. No forgotten print statements."*

---

### Scene 7 — The Debug Arc (7:45 – 8:30)

**Camera pulls back.** The 5-phase pipeline shows as a completed timeline:

```
INJECT → CAPTURE → ANALYZE → FIX-PLAN → CLEANUP
 (14)     (run)     (94%)     (Fix 1)     (14/14)
```

Each phase node lights up in sequence. Total time: **~3 minutes of human interaction**.

**A comparison panel:**

| Traditional Debugging | CORTEX Debug Pipeline |
|---|---|
| Scatter print statements (~10 min) | 14 markers placed strategically (2 sec) |
| Read through hundreds of log lines | Root cause correlated automatically |
| Guess → test → guess → test | 94% confidence diagnosis on first pass |
| Forget to remove debug prints | Automated cleanup — zero residue |
| **~45 min average** | **~3 min interaction** |

---

### Scene 8 — Close (8:30 – 9:00)

**Closing text** (Space Grotesk):
**"Debug smarter. Ship cleaner. Move on to the next challenge."**

**Vision callback:**
> *"Every hour your team spends chasing bugs is an hour they aren't building what your customers actually need. CORTEX cuts the chase."*

Logo pulse. End card.

---

## Notes

- This tutorial demonstrates the **DebuggerOrchestrator** and its 5-phase pipeline — a differentiating CORTEX capability.
- The bug is realistic and relatable: nested dict in a list causing a downstream TypeError. Engineers have all been there.
- The 8 injection strategies (ENTRY/EXIT, branch, type inspection, recursion, collection profiling, variable snapshots, exception boundaries, timing) should be visually distinct with different amber shades.
- **Key emotional beat**: Scene 4's zoom on `types=['dict', 'dict', 'dict']` — the moment the viewer sees the bug found automatically.
- Auto-cleanup (Phase 5) is a trust-building moment — demonstrates CORTEX leaves no mess behind.
- Sound design: bug crash = discordant tone; marker injection = rapid tapping; root cause zoom = low revelation tone; fix application = satisfying click; cleanup sweep = whoosh; all-green = ascending chime.
- Code is syntactically correct Python with proper CORTEX conventions.
