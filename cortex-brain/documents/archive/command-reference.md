# 📖 CORTEX Command Reference

**Version:** 4.0.0  
**Author:** Asif Hussain  
**Purpose:** Quick reference for all CORTEX operations

---

## 🎯 Command Syntax

CORTEX uses **natural language**, not slash commands.

✅ **Correct:**
```
plan user authentication
start tdd
system maintenance
```

❌ **Incorrect:**
```
/plan user-auth
/tdd start
/maintenance
```

---

## 📋 Core Commands

### Planning Operations

#### Create New Plan
```
plan [feature name]
plan "user authentication feature"
plan "add payment processing"
```

**Output:**
```
cortex-brain/documents/planning/active/{feature-name}/
├── 00-master-plan.md
├── context/
├── reports/
├── artifacts/
└── tracking/progress-tracker.json
```

**Orchestrator:** Planning System  
**Manifest:** `planning-system-4.0-manifest.yaml`

---

#### Create ADO Work Item
```
plan ado [story description]
plan ado "user story for login feature"
ado feature "implement search functionality"
```

**Output:** ADO-formatted work item with acceptance criteria

**Orchestrator:** ADO Operations  
**Manifest:** `ado-planning-manifest.yaml`

---

### TDD Workflow

#### Start TDD Session
```
start tdd
start tdd for calculator functions
tdd [component name]
```

**Workflow:**
1. 🔴 **RED:** Write failing test
2. 🟢 **GREEN:** Implement minimal code
3. 🔵 **REFACTOR:** Improve quality

**Enforcement:** SKULL rule `TDD_ENFORCEMENT`

---

#### Continue TDD
```
continue tdd
next tdd phase
```

**Moves to next phase:** RED → GREEN → REFACTOR

---

#### Complete TDD Session
```
complete tdd
finish tdd
```

**Creates:** Git checkpoint with passing tests

---

### System Maintenance

#### Run Health Check
```
system maintenance
healthcheck
maintenance
```

**Phases:**
1. Discovery (analyze codebase)
2. Validation (check compliance)
3. Planning (identify fixes)
4. Implementation (make changes)
5. Testing (verify fixes)
6. Documentation (update reports)

**Output:** `cortex-brain/health-reports/maintenance-report-{date}.md`

---

### Code Sanitization

#### Sanitize Directory
```
sanitize [directory]
sanitize src/
make generic src/config/
anonymize tests/fixtures/
```

**Removes:**
- Company names
- API keys
- Personal data
- Proprietary information

**Output:** Sanitized codebase with generic placeholders

**Orchestrator:** Sanitization  
**Manifest:** `code-sanitization-manifest.yaml`

---

### System Refinement

#### Run Refinement Pipeline
```
refine
improve cortex
optimize system
```

**Phases:**
1. Discovery (scan for issues)
2. Validation (check standards)
3. Planning (design improvements)
4. Implementation (apply fixes)
5. Testing (verify quality)
6. Documentation (update docs)
7. Retrospective (lessons learned)

**Output:** Improved codebase + lessons learned

**Orchestrator:** Refinement  
**Manifest:** `refinement-orchestrator-manifest.yaml`

---

### Help & Documentation

#### Get Help
```
help
show commands
what can you do?
```

**Output:** List of all available operations with examples

---

#### Get Version
```
version
what version is this?
```

**Output:** CORTEX version info

---

## 🔧 Advanced Commands

### System Operations

#### Align System
```
align
align orchestrators
```

**Purpose:** Synchronize orchestrators with manifests

---

#### Optimize System
```
optimize
optimize tokens
```

**Purpose:** Apply token optimization patterns

---

#### Cleanup System
```
cleanup
remove duplicates
```

**Purpose:** Remove orphaned/duplicate code

---

### Discovery & Search

#### Search Codebase
```
search [query]
find implementations of [interface]
show usages of [function]
```

**Purpose:** Semantic search with context awareness

---

#### Discover Plans
```
discover plans
show existing plans
list active plans
```

**Output:** Lists all plans in `planning/active/`

**Enforcement:** SKULL rule `HOLISTIC_DISCOVERY`

---

## 🎨 Response Format Control

CORTEX adapts response complexity automatically, but you can request specific formats:

#### Quick Answer
```
quick: [question]
brief: [question]
```

**Response Tier:** INSTANT (<50 tokens)

---

#### Detailed Explanation
```
explain: [concept]
detail: [concept]
```

**Response Tier:** STRUCTURED (200-600 tokens)

---

#### Comprehensive Report
```
full report on [topic]
comprehensive analysis of [system]
```

**Response Tier:** COMPREHENSIVE (600+ tokens)

---

## 📊 Progress Tracking

#### Check Plan Status
```
status of [plan name]
show progress for [plan name]
```

**Output:** Current phase, completed tasks, blockers

**Source:** `tracking/progress-tracker.json`

---

#### Update Plan Status
```
complete phase [N] of [plan name]
mark task [ID] done in [plan name]
```

**Updates:** `progress-tracker.json` with new status

---

## 🔍 Context Commands

#### Set Context
```
working on [feature]
focus on [directory]
```

**Effect:** Narrows CORTEX scope to specified area

---

#### Clear Context
```
clear context
reset focus
```

**Effect:** Removes context filters

---

## 🛡️ SKULL Enforcement Commands

#### Validate TDD
```
validate tdd
check test coverage
```

**Checks:** All implementations have tests

---

#### Check Duplication
```
check for duplicates
find similar code
```

**Enforcement:** `HOLISTIC_DISCOVERY`

---

#### Verify Isolation
```
verify git isolation
check cortex boundaries
```

**Enforcement:** `GIT_ISOLATION`

---

## 🎯 Common Workflows

### Workflow 1: New Feature Development

```
1. plan "new feature name"
2. start tdd
3. [write test] → [implement] → [refactor]
4. complete tdd
5. system maintenance
```

---

### Workflow 2: Code Review & Improvement

```
1. review [file/directory]
2. refine
3. validate tdd
4. system maintenance
```

---

### Workflow 3: Project Onboarding

```
1. help
2. system maintenance
3. discover plans
4. plan "first feature"
5. start tdd
```

---

## 🔗 Command Aliases

| Command | Aliases |
|---------|---------|
| `plan` | `create plan`, `make plan` |
| `start tdd` | `begin tdd`, `tdd start` |
| `system maintenance` | `healthcheck`, `maintenance`, `health` |
| `sanitize` | `make generic`, `anonymize` |
| `refine` | `improve`, `optimize` |
| `help` | `show commands`, `what can you do` |

---

## 📚 Command Categories

### By Frequency

**Daily Use:**
- `plan [feature]`
- `start tdd`
- `help`

**Weekly Use:**
- `system maintenance`
- `discover plans`
- `status of [plan]`

**Monthly Use:**
- `refine`
- `sanitize`
- `align`

---

### By Tier (Tiered Router)

**Tier 1 - INSTANT (<2 sec):**
- `help`
- `version`

**Tier 2 - LIGHTWEIGHT (<10 sec):**
- `status of [plan]`
- `validate tdd`

**Tier 3 - DOCUMENTED (10-60 min):**
- `plan [feature]`
- `start tdd`

**Tier 4 - COMPLEX (>1 hour):**
- `refine`
- `system maintenance`
- `sanitize [large directory]`

---

## 🚨 Error Messages & Fixes

### "Command not recognized"

**Fix:**
```
help  # View correct syntax
```

**Common Cause:** Using slash commands instead of natural language

---

### "SKULL violation: TDD_ENFORCEMENT"

**Fix:**
```
start tdd  # Begin with test first
```

**Cause:** Attempted implementation without test

---

### "Plan already exists"

**Fix:**
```
discover plans  # View existing plans
```

**Enforcement:** `HOLISTIC_DISCOVERY` prevents duplicates

---

### "Planning folder not created"

**Fix:**
```
system maintenance  # Check system health
```

**Possible Cause:** Toolkit not accessible

---

## 📖 Related Documentation

- **Intent Router:** `.github/prompts/CORTEX.prompt.md`
- **Operation Guides:** `.github/prompts/modules/`
- **Orchestrator Manifests:** `cortex-brain/manifests/orchestrators/`
- **SKULL Rules:** `cortex-brain/brain-protection-rules.yaml`
- **Web Docs:** https://asifhussain60.github.io/CORTEX/

---

## 🔄 Update Frequency

This command reference is automatically updated when:
- New orchestrators are added
- CORTEX.prompt.md is modified
- Operation manifests change

**Last Updated:** 2025-12-29  
**Version:** 4.0.0

---

**Copyright © 2025 Asif Hussain. All rights reserved.**
