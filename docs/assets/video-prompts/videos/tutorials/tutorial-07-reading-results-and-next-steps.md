# NotebookLM Video Prompt -- Tutorial 07 -- Reading Results Like an Expert

**Target length:** ~6 minutes
**Audience:** Users who have run /audit fix at least once and want to understand the output deeply
**Visual Theme:** Warm amber/gold glassmorphism (tutorial series accent)
**Prerequisite:** Tutorial 06 complete (first /audit fix run done)
**Narrator gender:** Female (T07 -- odd)
**Goal:** Viewer can read any CORTEX output panel and extract the three things that matter: severity, scope, next action

---

## ZERO-OVERLAP DECLARATION
This tutorial exclusively owns:
- The output interpretation framework: severity map, scope identification, next-action extraction
- SQLite audit trace reading: what AC markers mean and how to read the orchestrator trace
- The "four panels assemble" opening: result grid materialising one panel at a time
- The expert reading habit: what to look at first, what to ignore, what to act on immediately

Does NOT repeat: command catalogue (T02), running the audit (T06), installation (T01), onboarding (T04), VS Code navigation (T05).

---

## Steering Prompt
Paste into NotebookLM Customize - Steering Prompt:

"Create a ~6 minute tutorial on reading CORTEX audit output like an expert. Cover: the severity map (P0/P1/P2/P3), how to scope a violation to its source file, how to read the AC marker trace in the SQLite database, and what 'zero P0/P1' means as a production readiness signal. Narration must build the viewer's interpretive skill -- not describe what is on screen. Use only provided sources."

---

## NARRATION RULE -- MANDATORY
The narrator never describes output text aloud. Every narration line builds interpretive skill: what this pattern means, why this severity matters, what this trace record proves.

---

## Cinematic treatment -- "Four Panels Assemble"

**Unique opening (result grid -- T07's visual identity):**
The environment is amber-lit and silent. An empty 2x2 grid of glassmorphic panel frames appears.
The frames are empty -- just outlines. Each panel label appears:
  Top-left: "Violations"
  Top-right: "Test Results"
  Bottom-left: "AC Trace"
  Bottom-right: "Production Readiness Score"
Then, one by one, each panel fills with content -- appearing as if data is being loaded into a dashboard:
  Violations panel: severity table with P0/P1/P2/P3 counts
  Test results: pass/fail bars
  AC trace: three rows of AC markers
  Readiness score: a percentage gauge
On-screen label: "Every CORTEX run produces these four panels. Knowing how to read them is the skill."
This is T07's visual identity: the complete output dashboard materialising, establishing that the tutorial is about interpretation, not execution.

### Visual Physics
- 2x2 panel grid: glassmorphic amber-outlined frames
- Panel fill: data types in character by character (not animated slide-in -- typed in)
- Active panel: elevated slightly with amber spotlight; others remain visible at 80% opacity
- Severity colour coding: P0 = red, P1 = amber, P2 = yellow, P3 = grey

---

## Scene-by-scene breakdown

**SCENE 1 -- "Four Panels Assemble" [0:00-0:45]**
Empty grid. Panels fill one by one.
Narrator: "Every /audit fix run leaves a result. Most users look at the number of violations. Experts look at the severity distribution first, the scope second, and the AC trace last. By the end of this tutorial, that will be your reading order."

**SCENE 2 -- "The Severity Map" [0:45-2:30]**
Violations panel spotlighted. Severity table:
  P0: 0 (green -- no blocking violations)
  P1: 3 (amber -- significant, must resolve before release)
  P2: 11 (yellow -- advisory, address before next sprint)
  P3: 24 (grey -- informational, track but do not block on)
Narrator: "P0 means this codebase cannot be released in its current state. If you see P0 violations, they are the only thing that matters. P1 means release is blocked pending resolution. P2 and P3 are your improvement backlog -- important, but not blocking. Zero P0/P1 is the production readiness signal."
Lower-third: "Zero P0/P1 = production ready. Not zero violations -- zero P0/P1."

**SCENE 3 -- "Scoping a Violation" [2:30-4:00]**
A P1 violation card expands:
  Rule: CORE-011 -- Missing type hint
  File: cortex/api/status_endpoint.py
  Line: 47
  Function: get_status
  Fix applied: return type annotation added
Narrator: "A violation without a scope is noise. A violation with a file and line is an action item. When you review a P1, check three things: which rule, which file, which function. That tells you the blast radius. A type hint violation in a private utility is different from one in a public API endpoint."

**SCENE 4 -- "Reading the AC Trace" [4:00-5:00]**
AC trace panel spotlighted. Three rows:
  AC-API-001 | AC_START | get_status | 09:14:23.441
  AC-API-001 | AC_COMPLETE | get_status | 09:14:23.609 | 168ms | status=success
  AC-CORE-042 | AC_COMPLETE | EnforcementOrchestrator | 09:14:24.001 | 392ms | violations=0
Narrator: "The AC trace is proof of work. AC_START without a matching AC_COMPLETE is a governance violation -- it means an orchestrator exited unexpectedly. The timing column shows performance. The status column shows outcome. A status=success with 0 violations is your green light."
Lower-third: "AC_START without AC_COMPLETE = P0 governance violation. Always."

**SCENE 5 -- "The Production Readiness Score" [5:00-5:45]**
Readiness score panel: 94%.
Breakdown card:
  P0 violations: 0 (full weight)
  P1 violations: 3 remaining (-6%)
  Test coverage: 87% (satisfactory)
  AC trace integrity: clean (no orphaned starts)
Narrator: "The readiness score is not a grade. It is a deployment gate. 100% with zero P0/P1 and clean AC traces means the system passed all mandatory checks. 94% means three P1 violations remain. The score will not matter to your production pipeline -- the P1 count will."

**SCENE 6 -- "Your Reading Order" [5:45-End]**
All four panels visible simultaneously. Camera highlights each in reading order:
  1. P0 count -- if not zero, stop here
  2. P1 count -- if not zero, review each violation before release
  3. AC trace -- confirm no orphaned AC_START entries
  4. Coverage -- advisory but important trend
Narrator: "That is the expert reading order. Four panels, thirty seconds. You will know whether this codebase is ready for release before you read a single violation detail. That is the skill."
Outro card: "Series complete. You are ready to work with CORTEX."
Final frame: all tutorials listed as a progress map -- T01 through T07 with amber checkmarks.

---

## Audio direction
- Panel fill: soft typing sound as each panel's data appears
- Severity red (P0): a brief sharp alert tone -- even at 0, the sound acknowledges what it would mean
- AC_COMPLETE row highlight: the clean series bell tone -- final use in the tutorial series
- Outro music: the series theme, slightly elevated -- completion moment

---

## Production note
Scene 6 is the series finale moment -- the "you are ready" payoff. The tone must be earned, not triumphant. The viewer has watched 7 tutorials; the narrator's delivery should reflect that this is a skill acquired over time, not a tool mastered in an afternoon. The amber checkmarks on the T01-T07 progress map should light one by one as the credits roll.
