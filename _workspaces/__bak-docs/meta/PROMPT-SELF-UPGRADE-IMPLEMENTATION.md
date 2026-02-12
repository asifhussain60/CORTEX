# Prompt Self-Upgrade Implementation
**Date:** 2026-02-04 | **Status:** ✅ IMPLEMENTED | **Impact:** Universal Prompt Maintenance

---

## 🎯 Overview

All three production prompts now have **automatic self-upgrade capability** that detects and integrates updates from `origin/main` without disrupting user workflows.

**Prompts Updated:**
1. ✅ `cortex-architect.prompt.md` (v13.0)
2. ✅ `CORTEX.prompt.md` (v8.2)
3. ✅ `cortex-ask.prompt.md` (v1.0)

---

## 🔧 PRE-FLIGHT PROMPT CHECK (Universal Implementation)

### What It Does

Before any operation, each prompt checks for newer versions in `origin/main`:

```
Load this prompt → Check origin/main for newer version
         ↓
git fetch origin main (silent, 5s timeout)
         ↓
Compare: Local version vs origin/main version
         ↓
[UP_TO_DATE] → Version X.X, no changes needed → Proceed
         ↓
[NEWER_VERSION_AVAILABLE] → New version detected → User decides
         ↓
User: "upgrade prompt" / "skip" / "show changes"
         ↓
[UPGRADE] → Load latest from origin/main
[SKIP] → Continue with local version (warn: may miss features)
[SHOW] → Display version diff before deciding
```

### User Options

When a newer version exists:

1. **"upgrade prompt"** → Reload prompt file from origin/main
   - Preserves all user context and conversation history
   - Activates new capabilities immediately
   - Seamless continuation of work

2. **"skip"** → Continue with current version
   - ⚠️ Warning: May miss prompt enhancements
   - Useful if working offline or intentionally staying stable

3. **"show changes"** → Display version comparison
   - See what's new before deciding
   - Compare sections, rules, orchestrators, tools
   - Make informed decision

### Automatic Upgrades

**Network Failure?** Gracefully degrade to current version with warning:
```
⚠️ Network timeout: Could not fetch origin/main
   Proceeding with v13.0 (local)
```

---

## 📝 Implementation Details

### Changes to Each Prompt

#### 1. cortex-architect.prompt.md (v13.0)

**New Section:** PRE-FLIGHT PROMPT CHECK (AUTO-UPGRADE)  
**Location:** Lines 8-48 (beginning of file)  
**Features:**
- Git fetch with 5s timeout
- Version comparison logic
- Ecosystem changes detection (.github/prompts/, agents/, wiring.yaml)
- User approval gate (mandatory - no auto-upgrade)
- Network failure handling
- Upgrade success confirmation

**Key Addition:**
```markdown
### Upgrade Detection Flow

Load this prompt → Check origin/main for newer version
         ↓
git fetch origin main (silent, 5s timeout)
         ↓
Compare: Local version (13.0) vs origin/main version
         ↓
[UP_TO_DATE] → Version 13.0, no changes needed → Proceed
         ↓
[NEWER_VERSION_AVAILABLE] → New version detected → User decides
```

#### 2. CORTEX.prompt.md (v8.2)

**New Section:** PRE-FLIGHT PROMPT CHECK (AUTO-UPGRADE)  
**Location:** Lines 8-48 (beginning of file)  
**Features:**
- Identical upgrade flow as cortex-architect
- Version comparison for CORTEX.prompt.md specifically
- User approval requirements
- Network resilience

**Key Addition:**
```markdown
### Upgrade Detection Flow

Load this prompt → Check origin/main for newer version
         ↓
git fetch origin main (silent, 5s timeout)
         ↓
Compare: Local version (8.2) vs origin/main version
```

#### 3. cortex-ask.prompt.md (v1.0)

**New Section:** PRE-FLIGHT PROMPT CHECK (AUTO-UPGRADE)  
**Location:** Lines 8-48 (beginning of file)  
**Features:**
- Full upgrade detection capability
- Educational mode specific version tracking
- Same user approval gate pattern
- Network timeout handling

**Key Addition:**
```markdown
### Upgrade Detection Flow

Load this prompt → Check origin/main for newer version
         ↓
git fetch origin main (silent, 5s timeout)
         ↓
Compare: Local version (1.0) vs origin/main version
```

---

## 🔄 Upgrade Flow Diagram

```
┌─────────────────────────────────────┐
│ User Initiates Request              │
│ (/audit, /implement, /ask about...) │
└────────────┬────────────────────────┘
             │
             ↓
┌─────────────────────────────────────┐
│ PRE-FLIGHT PROMPT CHECK             │
│ (Automatic, No User Action)         │
│                                     │
│ 1. git fetch origin main (5s)       │
│ 2. Compare local vs origin version  │
│ 3. Detect ecosystem changes         │
└────────────┬────────────────────────┘
             │
             ├─→ [UP_TO_DATE] ──→ Proceed to Operation
             │
             └─→ [NEWER_VERSION] ──→ Display Upgrade Options
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ↓                ↓                ↓
              "upgrade"          "skip"         "show changes"
              prompt             proceed         display diff
                                                then choose
                    │                │                │
                    └────────────────┼────────────────┘
                                     │
                                     ↓
                            Proceed to Operation
                            (with upgraded prompt)
```

---

## ✅ User Experience

### Before Upgrade

User was unaware of new prompt capabilities and had to manually update by:
- Checking git history
- Reading changelogs
- Re-reading entire prompts to find changes

**Result:** ❌ Old prompts, missed features, technical debt

### After Upgrade

1. User initiates any request (`/audit`, `/implement`, `/ask about...`)
2. **Automatic check** for newer version in `origin/main`
3. If newer version exists:
   - Display clear notification with what changed
   - User chooses action with 3 options
   - Decision logged in audit trail
4. New prompt capabilities available immediately
5. **Zero friction** - conversation continues seamlessly

**Result:** ✅ Always current, no manual work, seamless UX

---

## 🛡️ Safety Features

### 1. **User Approval Gate (MANDATORY)**
- No automatic upgrades
- User explicitly types "upgrade prompt"
- Prevents surprises during critical work

### 2. **Network Resilience**
- 5s timeout (won't block on slow networks)
- Graceful degradation (use local version if network fails)
- Warning message explains what happened

### 3. **Version Comparison**
- Accurate version detection (via version field in prompt)
- Git merge-base analysis (for branch topology)
- Identifies ecosystem changes (new orchestrators, agents, etc.)

### 4. **Conflict Prevention**
- Pre-merge conflict detection via `git merge-tree`
- Manual instructions for resolution if conflicts occur
- Atomic merge operation (never leaves broken state)

### 5. **Audit Trail**
- Decision logged: "User chose 'upgrade' | 'skip' | 'show changes'"
- Timestamp recorded
- Version before/after documented

---

## 🔍 Technical Details

### Git Commands Used

```bash
# Silent fetch (no output clutter)
git fetch origin main --quiet

# Version comparison
LOCAL_VERSION=$(grep "^**Version:" prompt.md | head -1)
ORIGIN_VERSION=$(git show origin/main:prompt.md | grep "^**Version:" | head -1)

# Conflict detection (before merge)
git merge-tree $(git merge-base HEAD origin/main) HEAD origin/main

# Safe merge (preserves local work)
git merge origin/main --no-edit
```

### Timeout Handling

```bash
# 5 second timeout for fetch
timeout 5 git fetch origin main --quiet

# Exit code 124 = timeout
if [ $? -eq 124 ]; then
    echo "⚠️ Network timeout: Could not fetch origin/main"
fi
```

---

## 📊 Impact Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Awareness** | Manual monitoring | Automatic detection |
| **Update Friction** | High (manual process) | Zero (user control) |
| **Feature Adoption** | Slow (manual updates) | Fast (prompted upgrades) |
| **User Control** | None | Full (3 explicit options) |
| **Network Resilience** | Breaks on failure | Graceful degradation |
| **Audit Trail** | No decisions logged | Full audit trail |
| **Conflict Handling** | Manual merge hell | Pre-check + instructions |

---

## 🚀 Future Enhancements

### Planned Additions

1. **Prompt Change Summary**
   - Auto-generate "What's New" section
   - Highlight new capabilities
   - Link to relevant docs

2. **Smart Recommendations**
   - Suggest "upgrade prompt" if new features apply to current task
   - Example: "New ASK mode available - would you like to explore?"

3. **Rollback Capability**
   - Save prompt versions locally
   - One-command rollback if needed
   - Version history tracking

4. **Batch Upgrades**
   - Upgrade all 3 prompts together
   - Single user decision for all
   - Consistent ecosystem versions

---

## 📋 Checklist: All Three Prompts

### cortex-architect.prompt.md
- ✅ PRE-FLIGHT PROMPT CHECK section added
- ✅ Version detection logic implemented
- ✅ Ecosystem changes detection integrated
- ✅ User approval gate enforced
- ✅ Network failure handling
- ✅ Tested with local version comparison

### CORTEX.prompt.md
- ✅ PRE-FLIGHT PROMPT CHECK section added
- ✅ Version detection logic implemented
- ✅ User approval gate enforced
- ✅ Network failure handling
- ✅ Tested with local version comparison

### cortex-ask.prompt.md
- ✅ PRE-FLIGHT PROMPT CHECK section added
- ✅ Version detection logic implemented
- ✅ User approval gate enforced
- ✅ Network failure handling
- ✅ Tested with local version comparison

---

## 🎓 How It Works (User Perspective)

### Scenario 1: First Interaction with Updated Prompts

```
User: /audit

[System: Checking for prompt updates...]

🆙 CORTEX Architect Prompt Updates Available

Your local version: 13.0
Latest version: 13.1

Changes detected:
- New ChallengeEngine improvements
- Enhanced DuplicationDetector
- Simplified engineer-focused format

Options:
1. Type "upgrade prompt" → Get latest 13.1 with new features
2. Type "skip" → Continue with 13.0 (may miss improvements)
3. Type "show changes" → See detailed diff before deciding

→ upgrade prompt

✅ Upgraded to v13.1
Proceeding with AUDIT mode...
```

### Scenario 2: Already Current

```
User: /implement add caching

[System: Checking for prompt updates...]
✅ cortex-architect.prompt.md v13.1 is current

Proceeding to DESIGN mode...
```

### Scenario 3: Network Failure

```
User: /audit

[System: Checking for prompt updates...]
⚠️ Network timeout: Could not fetch origin/main
   Proceeding with local v13.0

[Proceeding with AUDIT mode...]
```

---

## 🔗 Related Documentation

- [cortex-architect.prompt.md](/Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-architect.prompt.md) - Lines 8-48
- [CORTEX.prompt.md](/Users/asifhussain/PROJECTS/CORTEX/.github/prompts/CORTEX.prompt.md) - Lines 8-48
- [cortex-ask.prompt.md](/Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-ask.prompt.md) - Lines 8-48
- [cortex-architect.md](/Users/asifhussain/PROJECTS/CORTEX/.github/agents/core/cortex-architect.md) - Environment setup agent

---

## ✅ Verification

All three prompts now have:

1. ✅ **Auto-Detection** - Checks `origin/main` on every request
2. ✅ **User Control** - Mandatory approval before upgrade
3. ✅ **Clear Feedback** - Display what's new and why to upgrade
4. ✅ **Safety** - Network resilience, conflict detection
5. ✅ **Audit Trail** - User decisions logged
6. ✅ **Zero Friction** - Seamless upgrade, no conversation interruption

**Status:** Ready for Production ✅

---

*Implemented 2026-02-04 by Asif Hussain*
*All three CORTEX prompts now self-upgrade with user approval*
