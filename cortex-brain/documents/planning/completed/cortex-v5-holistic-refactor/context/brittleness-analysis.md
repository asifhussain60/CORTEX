# CORTEX Brittleness Analysis

**Created:** January 2, 2026  
**Phase:** 0 - Foundation Setup (Task 0.3)  
**Purpose:** Catalog known issues and failure points across all components

---

## Executive Summary

Current CORTEX architecture exhibits **7 critical brittleness categories** affecting reliability, maintainability, and user experience. Most issues stem from hybrid control flow ambiguity and lack of centralized state management.

**Severity Scale:**
- 🔴 **CRITICAL:** System-breaking, requires immediate fix
- 🟡 **HIGH:** Major usability impact, frequent workarounds needed
- 🟢 **MEDIUM:** Minor inconvenience, has workarounds

---

## 1. State Management Brittleness 🔴 CRITICAL

### Issue: No Transactional State Updates

**Problem:** All state stored in individual YAML/JSON files without ACID guarantees.

**Failure Scenarios:**
- Planning workflow crashes mid-execution → Corrupted `progress-tracker.json`
- Concurrent operations → File write conflicts
- System crash → Lost in-memory state

**Example Failure:**
```
User: Create plan for authentication
CORTEX: [Phase 1 complete, writes progress.json]
CORTEX: [Phase 2 starts...]
System Crash
CORTEX: [Restart] - No way to resume from Phase 2
```

**Impact:** Users must manually restart workflows from beginning.

**Root Cause:** File-based state without transaction boundaries.

---

## 2. Orchestrator Control Flow Ambiguity 🔴 CRITICAL

### Issue: Unclear Execution Ownership

**Problem:** AUTONOMOUS orchestrators claim independence but require CORTEX interpretation.

**Ambiguity Points:**

| Orchestrator | Claimed Behavior | Actual Behavior |
|--------------|------------------|-----------------|
| Planning System | Self-executing | CORTEX reads manifest, executes steps |
| ADO Operations | Generates work items | CORTEX calls agent methods |
| Vacuum | Deep cleanup | CORTEX follows prompt instructions |
| Cleanup | Cache management | CORTEX runs maintenance phase 2 |

**Confusion:**
- Users unsure when to intervene
- Developers unsure where to add logic (Python vs manifest)
- Manifests contain both config AND instructions

**Example Manifest (Hybrid):**
```yaml
# Configuration
folder_structure:
  root: "planning/active/{name}/"
  
# Instructions (should be in Python!)
execution_steps:
  - "Search workspace for relevant files"
  - "Create folder structure"
  - "Generate master plan using template"
```

**Impact:** Maintenance nightmare - logic scattered across files.

---

## 3. Failure Recovery Absence 🔴 CRITICAL

### Issue: No Automatic Resumption

**Problem:** When workflows fail, no mechanism to resume from last successful phase.

**Failed Recovery Scenarios:**

```
Planning Orchestrator
├─ Phase 1: Context Discovery ✅
├─ Phase 2: Architecture Analysis ✅
├─ Phase 3: Plan Generation ❌ [CRASH]
├─ Phase 4: Folder Creation ⏸️ (never ran)
└─ Phase 5: Validation ⏸️ (never ran)

User must: Manually determine what succeeded, restart workflow
System should: Resume from Phase 3 automatically
```

**No Checkpoint System:**
- No state snapshots before each phase
- No rollback capability
- No "last known good" state

**Impact:** Hours of lost work on complex workflows.

---

## 4. Configuration Parsing Difficulty 🟡 HIGH

### Issue: Manifests Mix Data and Natural Language

**Problem:** Manifests contain prose instructions that can't be parsed programmatically.

**Unparseable Examples:**

```yaml
# From planning-system-4.0-manifest.yaml
instructions: |
  1. Use semantic_search to find relevant files
  2. Read each file and extract key patterns
  3. Summarize findings in context/discovery.md
  4. If no files found, ask user for guidance
```

This requires CORTEX to interpret English, not a program to parse data.

**Should Be:**
```yaml
# Config-only approach
context_discovery:
  tool: "semantic_search"
  output_file: "context/discovery.md"
  fallback_action: "request_user_input"
```

**Impact:** Can't build generic orchestrator execution engine.

---

## 5. Intent Classification Fragility 🟡 HIGH

### Issue: Keyword-Based Pattern Matching

**Problem:** Intent router uses exact string matching, easily broken.

**Current Pattern Matching:**
```python
if "plan" in user_request.lower() and "create" in user_request.lower():
    return "planning_system"
```

**Failure Cases:**
- `"I need to devise a strategy"` → Not matched (no "plan" keyword)
- `"plan a meeting"` → Wrongly triggers planning orchestrator
- Typos → No match
- Synonyms → No match

**Solution Exists:** `LLMIntentClassifier` but not primary method.

**Impact:** Users must learn exact command phrases.

---

## 6. Base Class Inconsistency 🟡 HIGH

### Issue: No Shared Patterns Across Orchestrators

**Problem:** Each orchestrator implements common operations differently.

**Inconsistent Patterns:**

| Operation | Upgrade Orch | Planning Orch | Git Checkpoint |
|-----------|--------------|---------------|----------------|
| **Load Config** | `self.load_yaml()` | `yaml.safe_load()` | Hardcoded |
| **Create Artifact** | `write_file()` | `Path().write_text()` | `git tag` |
| **Progress Tracking** | Session state | JSON file | Git log |
| **Error Handling** | Try/except | None | Print to console |

**No Shared Interface:**
```python
# No common base for:
- Configuration loading
- Artifact creation
- Progress tracking
- Checkpoint creation
- Error handling
```

**Impact:** Code duplication, hard to maintain, no guaranteed patterns.

---

## 7. Testing Gap 🟡 HIGH

### Issue: ~60% Coverage with No Integration Tests

**Problem:** Missing tests for critical failure scenarios.

**Untested Scenarios:**
- ❌ Orchestrator state recovery after crash
- ❌ Concurrent planning workflows
- ❌ Manifest schema validation
- ❌ Agent error propagation
- ❌ File system race conditions
- ❌ Transaction rollback

**Test Organization Issues:**
- Tests scattered across multiple directories
- No clear naming conventions
- Integration tests missing entirely

**Impact:** Regressions slip through, production bugs frequent.

---

## 8. Filename Standard Violations 🟢 MEDIUM

### Issue: Files Exceed 20 Character Limit

**Problem:** Many files have long names making navigation difficult.

**Violators:**
```
❌ planning_orchestrator_implementation.py (38 chars)
❌ onboarding_acknowledgment_orchestrator.py (40 chars)
❌ autonomous_execution_engine.py (29 chars)
❌ application_health_orchestrator.py (33 chars)
```

**Solution:** Implemented in Phase 0 (`file_name.py` utility)

**Impact:** Minor - affects readability, fixed by utility.

---

## 9. Documentation Sync Lag 🟢 MEDIUM

### Issue: Code Changes Outpace Documentation

**Problem:** CORTEX.prompt.md references orchestrators that don't exist.

**Stale References:**
- Planning System v5 (doesn't exist yet)
- ADO Orchestrator v2 (scattered logic)
- BaseOrchestrator v4.1 (not implemented)
- MCP protocol layer (not built)

**Impact:** Users confused by capabilities that don't exist.

---

## 10. No Universal Invocation Protocol 🟡 HIGH

### Issue: Each Orchestrator Has Unique Calling Pattern

**Problem:** No standardized way to invoke orchestrators.

**Current Patterns:**

```python
# Pattern 1: Direct instantiation
orch = PlanningOrchestrator(config_path)
result = orch.execute(user_request)

# Pattern 2: Function call
result = git_checkpoint_orchestrator.create_checkpoint(name)

# Pattern 3: Agent method
result = ado_agent.create_work_item(details)

# Pattern 4: CORTEX tool call
# (happens in Copilot Chat, not programmatic)
```

**No Common Interface:**
- Can't iterate over orchestrators programmatically
- Can't build generic retry logic
- Can't track metrics uniformly

**Impact:** Each orchestrator requires custom integration code.

---

## Brittleness Score Card

| Component | State | Recovery | Config | Invocation | Testing | Overall |
|-----------|-------|----------|--------|------------|---------|---------|
| Planning System | 🔴 | 🔴 | 🟡 | 🟡 | 🔴 | **CRITICAL** |
| ADO Operations | 🔴 | 🔴 | 🟡 | 🔴 | 🔴 | **CRITICAL** |
| Vacuum | 🔴 | 🔴 | 🟡 | 🔴 | 🔴 | **CRITICAL** |
| Cleanup | 🟡 | 🟡 | 🟢 | 🟡 | 🟡 | **HIGH** |
| TDD Mastery | 🟢 | N/A | 🟢 | 🟡 | 🟢 | **MEDIUM** |
| Debug Orch | 🟢 | N/A | 🟢 | 🟡 | 🟢 | **MEDIUM** |
| Agents | 🟢 | N/A | 🟡 | 🟢 | 🟡 | **MEDIUM** |

**Legend:**
- 🔴 CRITICAL: Immediate fix required
- 🟡 HIGH: Significant improvement needed
- 🟢 MEDIUM: Minor improvements

---

## Root Cause Analysis

### Primary Issue: Hybrid Architecture Decision

**Original Design:** Mix Python execution with natural language manifests for flexibility.

**Unintended Consequences:**
1. Execution logic fragmented across files
2. No clear ownership of workflow steps
3. Parsing manifests requires AI interpretation
4. Can't build generic execution engine
5. Testing becomes nearly impossible

**Why It Happened:** Early CORTEX prioritized rapid prototyping over architecture rigor.

---

## v5.0 Solution Mapping

| Brittleness | v5.0 Solution |
|-------------|---------------|
| **State Management** | SQLite with ACID transactions |
| **Control Flow** | Pure Python orchestrators, config-only manifests |
| **Failure Recovery** | State snapshots + automatic resumption |
| **Config Parsing** | YAML data structures only |
| **Intent Classification** | LLM-based with fallback |
| **Base Class** | BaseOrchestrator v4.1 with shared patterns |
| **Testing** | 100% coverage requirement |
| **Filename Standards** | `file_name.py` utility enforcement |
| **Documentation** | Auto-generated from code |
| **Invocation** | MCP protocol (universal) |

---

## Mitigation Priority (Before v5)

### Immediate (Days)
1. ✅ Implement `file_name.py` (Done in Phase 0)
2. Document known failure scenarios
3. Add error messages with recovery hints

### Short-term (Weeks)
1. Build MCP protocol layer (Phase 1)
2. Create SQLite state database (Phase 2)
3. Implement BaseOrchestrator v4.1 (Phase 3)

### Long-term (Months)
1. Migrate all orchestrators to v5 (Phase 6)
2. Achieve 100% test coverage (Phase 8)
3. Deprecate hybrid patterns (Phase 10)

---

**Status:** ✅ Task 0.3 (Brittleness Analysis) Complete  
**Next:** Complete orchestrator and agent inventory documents
