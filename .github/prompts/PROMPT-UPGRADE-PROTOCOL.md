# CORTEX Prompt Auto-Upgrade Protocol
**Version:** 1.1 | **Updated:** 2026-02-07 | **Authority:** Continuous Evolution | **Status:** ✅ ACTIVE

---

## 🎯 Overview

All CORTEX prompts now support automatic self-upgrade detection. When loaded, each prompt checks origin/main for newer versions and offers upgrade options without blocking execution.

**Affected Prompts:**
- ✅ `cortex-architect.prompt.md` (v15.0) — QUERY mode consolidation
- ✅ `CORTEX.prompt.md` (v8.2)
- ❌ `cortex-ask.prompt.md` — **DELETED (consolidated into QUERY mode v15.0)**

---

## 🔄 How It Works

### Automatic Detection (No User Action Required)

```
1. Prompt loads from local filesystem
2. Detects version number from header
3. Runs: git fetch origin main (5s timeout, silent)
4. Compares: Local version vs origin/main version
5. Shows upgrade options IF version mismatch detected
```

### User Decision Points

**If no newer version exists:**
```
✅ UP-TO-DATE
Proceed immediately with current version
No confirmation needed
```

**If newer version exists:**
```
🆙 NEWER VERSION AVAILABLE

Options:
1. Type "upgrade prompt" → Download latest from origin/main
2. Type "skip" → Continue with current version (⚠️ may miss features)
3. Type "show changes" → Display version diff before deciding
```

### Upgrade Strategy

**On "upgrade prompt":**
- Load latest prompt file from origin/main
- Replace current prompt with upgraded version
- Display: "✅ Upgraded from v{old} → v{new}"
- Show: Key changes + new capabilities
- Proceed: Continue with upgraded version

**On "skip":**
- Continue with current version
- Show warning: "⚠️ Developing against v{version} (newer v{new} available in origin/main)"
- Log: Version mismatch for future reference

**On "show changes":**
- Display side-by-side diff
- Show: Section changes, new features, deprecated items
- Await: User decision (upgrade/skip/cancel)

---

## 🛡️ Safety Features

### Network Failure Handling
```
If git fetch fails (timeout, offline, etc.):
- Gracefully degrade to current version
- Show warning: "⚠️ Could not check for updates (network issue)"
- Proceed: Continue with current version
- No blocking, no retry loops
```

### Version Detection
```
Format: **Version:** {major}.{minor} | **Updated:** YYYY-MM-DD

Examples:
- cortex-architect.prompt.md: Version 15.0
- CORTEX.prompt.md: Version 8.2
```

### Timeout Protection
```
git fetch timeout: 5 seconds
- No hanging if network is slow
- Gracefully degrade if timeout occurs
- Proceed immediately if successful
```

---

## 📋 Prompt-Specific Details

### cortex-architect.prompt.md (v13.0)

**Purpose:** Quad-mode system (PRE-FLIGHT/AUDIT/DESIGN/DIGEST) for enterprise AI

**Upgrade Triggers:**
- New architectural patterns
- Enhanced challenge system
- Additional orchestrators
- Prompt coherence improvements
- DIGEST mode enhancements

**Section:** "🔧 PRE-FLIGHT PROMPT CHECK (AUTO-UPGRADE)" (after title, before PURPOSE & VISION)

---

### CORTEX.prompt.md (v8.2)

**Purpose:** Master Orchestrator production prompt for MCP-first SaaS

**Upgrade Triggers:**
- New orchestrator registrations
- Enhanced governance rules
- MCP tool additions
- Security improvements

**Section:** "🔧 PRE-FLIGHT PROMPT CHECK (AUTO-UPGRADE)" (after title, before System Identity)

---

### ~~cortex-ask.prompt.md (v1.0)~~ — **DELETED in v15.0**

**Status:** Functionality consolidated into cortex-architect.prompt.md QUERY mode

**Migration:** All educational, verification, and list capabilities now available via `/query` command in cortex-architect

---

## 🔍 Git-Based Versioning

### Version Comparison Logic

```python
def should_upgrade():
    """Determine if prompt upgrade is available."""
    
    # 1. Parse local version from file header
    local_version = extract_version(prompt_file_path)
    
    # 2. Fetch latest from origin/main
    git_fetch_origin_main(timeout=5)
    
    # 3. Parse remote version
    remote_version = extract_version_from_origin_main(prompt_name)
    
    # 4. Compare semantic versioning
    if remote_version > local_version:
        return True  # Upgrade available
    
    return False  # Already up-to-date
```

### Version Ordering

```
Semantic versioning: MAJOR.MINOR
- 1.0 < 1.1 < 1.2 < 2.0
- 8.2 < 8.3 < 9.0
- 13.0 < 13.1 < 14.0

Compare: origin/main version vs local version
```

---

## 🚀 User Workflow

### Scenario 1: No Upgrade Available

```
User types: /audit

System:
1. Load cortex-architect.prompt.md (v13.0)
2. Check origin/main → v13.0 (same)
3. Status: ✅ Up-to-date
4. Proceed immediately with AUDIT mode
```

### Scenario 2: Upgrade Available

```
User types: /implement new-feature

System:
1. Load cortex-architect.prompt.md (v13.0)
2. Check origin/main → v13.1 (newer)
3. Show: "🆙 CORTEX Architect v13.1 available"
4. Offer options: upgrade / skip / show changes
5. Await user choice

User types: upgrade prompt

System:
1. Load v13.1 from origin/main
2. Display: "✅ Upgraded v13.0 → v13.1"
3. Show changes: New sections, enhanced capabilities
4. Proceed with DESIGN mode using v13.1
```

### Scenario 3: Network Failure

```
User types: /design refactoring-task

System:
1. Load cortex-architect.prompt.md (v13.0)
2. Check origin/main → [timeout after 5s]
3. Show: "⚠️ Could not check for updates (network)"
4. Proceed immediately with v13.0
5. No blocking, no retry attempts
```

---

## 🔧 Implementation Details

### Files Modified

**Three prompt files enhanced:**

1. `/Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-architect.prompt.md`
   - Added PRE-FLIGHT PROMPT CHECK section (31 lines)
   - Placed: Right after title, before PURPOSE & VISION
   - Status: ✅ Complete

2. `/Users/asifhussain/PROJECTS/CORTEX/.github/prompts/CORTEX.prompt.md`
   - Added PRE-FLIGHT PROMPT CHECK section (31 lines)
   - Placed: Right after title, before System Identity
   - Status: ✅ Complete

3. ~~`/Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-ask.prompt.md`~~
   - **DELETED in v15.0** — Consolidated into cortex-architect QUERY mode
   - Migration: All functionality preserved in unified QUERY mode

### Section Template

Active prompts (cortex-architect, CORTEX) use identical structure:

```markdown
## 🔧 PRE-FLIGHT PROMPT CHECK (AUTO-UPGRADE)

**AUTOMATIC EXECUTION:** Before any operation, this prompt checks for newer versions in origin/main

### Upgrade Detection Flow
[Flowchart showing detection → comparison → decision]

### Auto-Upgrade Options
[User choices: upgrade / skip / show changes]
```

---

## 📊 Benefits

| Benefit | Impact |
|---------|--------|
| **Always Current** | Users automatically get latest prompts + features |
| **Non-Blocking** | Network failures don't prevent operation |
| **User Control** | Users decide when to upgrade (not forced) |
| **Transparent** | Clear upgrade options + change visibility |
| **Cross-Prompt** | Consistent behavior across all three prompts |
| **Global** | Works from any chat/session (not restricted to cortex-plan) |

---

## 🎯 Next Steps

### For Users

1. **Continue as Normal:** All three prompts automatically check for updates
2. **When Prompted:** Choose upgrade/skip based on your needs
3. **Show Changes:** Review modifications before upgrading
4. **Version Tracking:** Verify your prompt version in header

### For CORTEX Developers

1. **Update Prompts:** Push new versions to origin/main
2. **Update Version Number:** Bump MAJOR.MINOR in header
3. **Document Changes:** Add to CHANGELOG section (if exists)
4. **Test Upgrades:** Verify version comparison logic works

### For Integration

1. **Agent Integration:** cortex-architect loads PRE-FLIGHT PROMPT CHECK automatically
2. **MCP Tool:** cortex_verify_environment already handles branch topology analysis
3. **No New Tools Needed:** Existing git + file-read mechanisms sufficient

---

## ⚠️ Known Limitations

| Limitation | Workaround |
|------------|-----------|
| Network failures → Degrade to current version | Check origin/main manually via git |
| Merge conflicts → Manual resolution required | User must resolve git conflicts |
| Multiple prompts → Check each independently | All three check automatically, no synchronization |

---

## 🔄 Version History

### v1.0 (2026-02-04)
- ✅ Initial implementation for three prompts
- ✅ Auto-upgrade detection with user control
- ✅ Network failure graceful degradation
- ✅ Consistent structure across all prompts

---

## 🔗 Related

- **cortex-architect.prompt.md** — PRE-FLIGHT PROMPT CHECK section (v15.0 - QUERY mode consolidation)
- **CORTEX.prompt.md** — PRE-FLIGHT PROMPT CHECK section
- ~~**cortex-ask.prompt.md**~~ — **DELETED** (consolidated into cortex-architect QUERY mode)
- **cortex-environment-setup.md** — Environment validation (parallel system)

---

*"Keep prompts fresh. Evolve continuously. Let users decide when to upgrade."*

✅ **Status:** Active prompts (cortex-architect, CORTEX) support automatic self-upgrade with user control.
