# Tier 0 Governance Rules Update

**Date:** 2025-11-17  
**Updated By:** GitHub Copilot (following user instructions)  
**File Modified:** `cortex-brain/brain-protection-rules.yaml`  
**Total Rules:** 22 → 24 (+2 new rules)

---

## Summary

Added two new governance rules to CORTEX Tier 0 (Layer 3: SOLID Compliance) to improve code quality and repository organization.

---

## New Rules Added

### 1. NO_EMOJIS_IN_SCRIPTS (Rule #23)

**Priority:** Layer 3 (SOLID Compliance)  
**Severity:** Warning  
**Rule ID:** `NO_EMOJIS_IN_SCRIPTS`

**Purpose:**  
Prevents emojis in generated scripts (Python, PowerShell, Bash, etc.) to ensure maximum compatibility and professional standards.

**Detection:**
- Triggers when generating scripts (.py, .ps1, .sh)
- Detects emoji usage in code content
- Scans for common emojis: ✅, ❌, ⚠️, 🔍, 📊, 🧠

**Rationale:**
1. **Encoding Issues:** UTF-8 not universal, some terminals can't render
2. **Terminal Compatibility:** Legacy systems, CI/CD logs may show broken characters
3. **Professional Standards:** Scripts are code, not social media
4. **Copy/Paste Problems:** Email/docs may corrupt emojis

**Alternatives:**
- Use plain text markers: `[OK]`, `[FAIL]`, `[WARN]`
- Use ASCII symbols: `+`, `-`, `*`, `!`
- Use logging levels: `INFO`, `ERROR`, `WARNING`

**Example:**
```python
# ❌ BAD
print("✅ Test passed")
print("❌ Test failed")

# ✅ GOOD
print("[OK] Test passed")
print("[FAIL] Test failed")
```

---

### 2. NO_ROOT_SUMMARY_DOCUMENTS (Rule #24)

**Priority:** Layer 3 (SOLID Compliance)  
**Severity:** Warning  
**Rule ID:** `NO_ROOT_SUMMARY_DOCUMENTS`

**Purpose:**  
Enforces CORTEX document organization mandate - all summary/report documents must be in `cortex-brain/documents/` with proper categorization.

**Detection:**
- Triggers when creating .md files in repository root
- Detects summary markers: "summary", "report", "analysis", "status"
- Validates file paths against expected structure

**Rationale:**
1. **Repository Clutter:** Too many root-level docs make repo unnavigable
2. **Loss of Context:** No categorization = hard to find documents
3. **Merge Conflicts:** Multiple summaries in root cause collisions
4. **Violates CORTEX Mandate:** Structured system already exists

**Required Structure:**
```
cortex-brain/documents/
├── reports/              # Implementation completion, status reports
├── analysis/             # Deep investigations, performance analysis
├── summaries/            # Quick overviews, daily progress
├── investigations/       # Research, architecture investigations
├── planning/             # Roadmaps, implementation plans
├── conversation-captures/ # Strategic conversation captures
└── implementation-guides/ # How-to guides, integration docs
```

**Alternatives:**
- Use `cortex-brain/documents/reports/` for completion reports
- Use `cortex-brain/documents/analysis/` for investigations
- Use `cortex-brain/documents/summaries/` for quick overviews
- See `cortex-brain/documents/README.md` for full guidelines

**Example:**
```
❌ BAD:
d:\PROJECTS\CORTEX\INVESTIGATION-ANALYSIS-REPORT.md

✅ GOOD:
d:\PROJECTS\CORTEX\cortex-brain\documents\analysis\INVESTIGATION-ANALYSIS-REPORT.md
```

---

## Priority Assignment

Both rules assigned to **Layer 3: SOLID Compliance** at priority level 3.

**Why Layer 3?**
- Code quality and style standards
- Repository organization standards
- Not architectural integrity (Layer 1-2)
- Not hemisphere specialization (Layer 4)
- Not critical safety violations (Layer 5 SKULL)

**Severity: Warning (not Blocked)**
- Allows override if user explicitly requests
- Provides education through alternatives
- Enforces best practices without being draconian

---

## Integration Points

### Brain Protector Agent
- Detects violations during file creation
- Challenges with alternatives
- References this rationale in challenges

### Response Templates
- Updated to discourage emoji usage in code
- Guide users to proper document locations
- Auto-suggest correct paths

### Documentation
- Updated CORTEX.prompt.md with mandatory document organization rules
- Added enforcement note to setup guides
- Referenced in technical-reference.md

---

## Testing

**Required Tests:**
1. `test_no_emojis_in_scripts()` - Verify emoji detection in .py, .ps1, .sh
2. `test_no_root_summaries()` - Verify path validation for .md files
3. `test_brain_protector_challenges()` - Verify Brain Protector enforces rules

**Test Location:** `tests/tier0/test_brain_protector.py`

---

## Metrics

**Before Update:**
- Total Rules: 22
- Layers: 6
- Code Quality Rules: 4

**After Update:**
- Total Rules: 24
- Layers: 6
- Code Quality Rules: 6 (+2)

---

## Rollout

**Immediate Effect:**
- Brain Protector will start enforcing these rules
- Challenges will appear during file creation
- No breaking changes (warnings only)

**User Communication:**
- No announcement needed (warnings are self-explanatory)
- Alternatives provided in challenge messages
- Documentation updated for reference

---

## Related Documents

- **Brain Protection Rules:** `cortex-brain/brain-protection-rules.yaml`
- **Document Organization:** `cortex-brain/documents/README.md`
- **Entry Point Instructions:** `.github/prompts/CORTEX.prompt.md`
- **Technical Reference:** `prompts/shared/technical-reference.md`

---

## Author Notes

**Decision Rationale:**

1. **Emoji Rule:**
   - User explicitly requested
   - Addresses real compatibility issues
   - Aligns with professional coding standards
   - Warning severity allows exceptions when justified

2. **Summary Document Rule:**
   - User explicitly requested
   - CORTEX already has document organization system
   - Prevents repository clutter
   - Warning severity provides flexibility

3. **Priority Assignment:**
   - Layer 3 appropriate for code quality standards
   - Not critical safety issues (Layer 5)
   - Not architectural boundaries (Layers 1-2)
   - Consistent with existing style rules

---

**Status:** ✅ COMPLETE  
**Next Steps:** Test integration with Brain Protector agent  
**Validation:** Rules added successfully, count updated (22 → 24)
