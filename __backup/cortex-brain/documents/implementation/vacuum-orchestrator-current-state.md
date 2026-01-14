# Vacuum Orchestrator - Current State vs. Your Requested Enhancements

## 📊 WHAT IT CURRENTLY DOES (v2.0.0)

### Current Capabilities:

#### 1. **Governance Violation Detection** ✅
- **Uppercase filename detection** - Finds files not in kebab-case (except allowed patterns)
- **Root-level document detection** - Finds documents that shouldn't be at root of `cortex-brain/documents`
- **Duplicate file detection** - Uses MD5 hashing to find identical files
- **Large file detection** - Reports files >1000 lines (CORE-001 enforcement)

#### 2. **File Organization** ✅
- **Categorization system** - Maps content type to folder (architecture/, planning/, reports/, etc.)
- **Kebab-case conversion** - Has function `to_kebab_case()` that converts filenames
- **AC-ID protection** - Skips renaming AC-{CATEGORY}-{NNN} patterns

#### 3. **Remediation Execution** ✅
- **Duplicate removal** - Deletes duplicates, keeps best version
- **File movement** - Moves misplaced files to proper subfolders
- **File renaming** - Renames files to kebab-case
- **Dry-run capability** - Preview mode before executing changes

#### 4. **Reporting** ✅
- **Action logging** - Tracks all operations
- **Error logging** - Captures failures
- **Violation breakdown** - By type and severity
- **Summary report** - Prints full operation results

---

## 🎯 YOUR REQUESTED ADDITIONS (NOT YET IMPLEMENTED)

### Enhancement 1: **Smart Consolidation** ⏳ NEW
**What you need:** Detect similar documents and consolidate them while preserving content

**Current state:**
- Detects duplicates (exact hash matches)
- No logic for "similar" documents (e.g., different versions, overlapping content)

**What needs to be added:**
```python
# NEW: Similarity detection (fuzzy matching)
def _detect_similar_documents(self) -> Dict[str, List[Path]]:
    """Find documents with similar names/content using fuzzy matching"""
    # Use difflib.SequenceMatcher to find %90+ similar content
    # Group by similarity threshold
    # Preserve the most comprehensive version
    pass

# NEW: Content merge strategy
def _consolidate_similar_documents(self, similar_groups):
    """When consolidating similar docs, merge their content intelligently"""
    # Determine which version to keep (newest? most comprehensive?)
    # Archive other versions with timestamp suffix
    # Update references in other files
    pass
```

**Your spec:**
> "consolidate similar documents without losing content"

**Implementation approach:**
- Use `difflib.SequenceMatcher` for fuzzy content matching
- Group documents by >85% similarity
- Keep the most recently updated or most comprehensive version
- Archive others to `docs/archive/consolidated/` with timestamp suffix
- Track consolidation in manifest

---

### Enhancement 2: **Intelligent File Relocation** ⏳ NEW
**What you need:** Move files to appropriate tier folders (tier0, tier1, tier2, tier3) based on content

**Current state:**
- Moves documents to `cortex-brain/documents/{category}/` subfolders
- Has hardcoded category rules
- No knowledge of tier structure (tier0/governance, tier1/tracking, etc.)

**What needs to be added:**
```python
# NEW: Tier-aware categorization
class TierAwareCategorizer:
    """Categorizes files to appropriate cortex-brain tier"""
    
    TIER_RULES = {
        "tier0": [
            r".*governance.*",  # governance/ files
            r".*core-rules.*",  # core rules
            r".*skull.*",       # SKULL rules
            r"AC-INDEX.*",      # AC registry
        ],
        "tier1": [
            r".*progress.*",       # progress tracking
            r".*acceptance.*",     # acceptance criteria
            r".*tracking.*",       # tracking data
            r".*state.*",          # state files
        ],
        "tier2": [
            r".*standards.*",      # engineering standards
            r".*practices.*",      # engineering practices
            r".*patterns.*",       # code patterns
        ],
        "tier3": [
            r".*knowledge.*",      # domain knowledge
            r".*patterns.*",       # learned patterns
            r".*insights.*",       # insights
        ]
    }
    
    def categorize_to_tier(self, file_path: Path) -> str:
        """Return 'tier0', 'tier1', 'tier2', or 'tier3'"""
        pass
```

**Your spec:**
> "relocate files appropriately"

**Implementation approach:**
- Add tier detection rules based on filename/content patterns
- Organize files: `cortex-brain/{tier0,tier1,tier2,tier3}/{category}/{file}`
- Preserve `documents/` structure for narrative docs (architecture, planning, etc.)
- Update import references after relocation

---

### Enhancement 3: **Kebab-case Naming with Governance Enforcement** ✅ PARTIALLY DONE
**What you need:** Rename all files to kebab-case following CORE-005 governance

**Current state:**
- `to_kebab_case()` function exists
- Applies during duplicate removal and reorganization
- Has exception list for AC-IDs and markdown standards (README, LICENSE, CHANGELOG)

**What needs improvement:**
```python
# ENHANCE: Stricter governance validation
def validate_against_core_005(self, filename: str) -> Tuple[bool, str]:
    """Validate filename against CORE-005 rules"""
    # Check: no uppercase except allowed
    # Check: no spaces (only hyphens/underscores)
    # Check: no special chars (except hyphens, dots, underscores)
    # Check: no consecutive hyphens
    # Return: (valid, reason_if_invalid)
    pass

# ENHANCE: Pre/post-conversion verification
def verify_kebab_case_conversion(self, original: str, converted: str) -> bool:
    """Ensure conversion didn't break AC-ID preservation or lose info"""
    pass
```

**Your spec:**
> "rename files to kebab-case following filenaming governance rules"

**Current gap:** Validation is implicit, not explicit. Need to add verification step.

---

### Enhancement 4: **Selective Deletion Intelligence** ⏳ PARTIAL
**What you need:** Delete informational reports but preserve analysis documents and critical files

**Current state:**
- Deletes only exact duplicates (hash matches)
- No deletion logic for similar/redundant files
- Protected paths list but no semantic understanding

**What needs to be added:**
```python
# NEW: File purpose detection
class FilePurposeClassifier:
    """Classify file purpose: informational vs. actionable vs. critical"""
    
    # Patterns that indicate ACTIONABLE documents (preserve)
    ACTIONABLE_PATTERNS = [
        r".*FUNCTIONAL-ANALYSIS.*",     # Analysis documents
        r".*IMPLEMENTATION.*",          # Implementation guides
        r".*PROGRESS.*",                # Progress tracking
        r".*EVIDENCE.*",                # Evidence bundles
        r".*RECOVERY-PLAN.*",           # Recovery strategies
        r".*ROADMAP.*",                 # Project roadmaps
    ]
    
    # Patterns that indicate INFORMATIONAL only (safe to delete)
    INFORMATIONAL_PATTERNS = [
        r".*TEMP.*",
        r".*DRAFT.*",
        r".*WORKING.*",
        r".*OLD.*",
        r".*BACKUP.*",
        r".*ARCHIVE.*",
        r".*[0-9]{8}.*",  # Timestamped versions
    ]
    
    def classify_file(self, file_path: Path) -> str:
        """Return 'actionable', 'informational', or 'critical'"""
        pass

# NEW: Smart deletion filter
def _classify_deletion_candidate(self, file_path: Path) -> Tuple[bool, str]:
    """Determine if file can be safely deleted"""
    # Actionable docs → NEVER delete
    # Critical files (tier0, tier1) → NEVER delete
    # Informational + old versions → safe to delete
    # Return: (can_delete, reason)
    pass
```

**Your spec:**
> "delete reports that are informational, but not actionable analysis documents"

**Specific example from your request:**
> "but not #file:CORTEX-BRAIN-FUNCTIONAL-ANALYSIS.md type reports that require work"

**Implementation approach:**
- Add semantic classification (actionable vs. informational)
- Never delete files with `ANALYSIS`, `IMPLEMENTATION`, `RECOVERY`, `ROADMAP` patterns
- Safe to delete files with `DRAFT`, `TEMP`, `OLD`, timestamped versions
- Query ACL (Acceptable Content List) before deleting governance/tracking files
- Require explicit confirmation for high-severity deletions

---

## 🔄 Enhancement Dependencies

```
1. Smart Consolidation
   ├─ Depends on: Similarity detection algorithm
   └─ Enables: Content preservation during cleanup

2. Tier-Aware Relocation
   ├─ Depends on: Tier categorization rules
   ├─ Depends on: Reference updating
   └─ Enables: Proper organization by tier

3. Kebab-case Governance
   ├─ Depends on: CORE-005 rule enforcement
   ├─ Works with: All other enhancements
   └─ Enables: Consistent naming

4. Selective Deletion ⭐ PREREQUISITE FOR SAFE EXECUTION
   ├─ Depends on: File classification system
   ├─ Requires: Must be added FIRST before executing vacuum
   └─ Prevents: Accidental deletion of critical analysis docs
```

---

## 📋 Implementation Checklist

### Phase 1: Selective Deletion Intelligence (MUST BE FIRST) ✅
```
- [ ] Add FilePurposeClassifier class
- [ ] Add ACTIONABLE_PATTERNS (preserve: ANALYSIS, IMPLEMENTATION, etc.)
- [ ] Add INFORMATIONAL_PATTERNS (safe to delete: TEMP, DRAFT, etc.)
- [ ] Add _classify_deletion_candidate() method
- [ ] Add deletion safety checks with user confirmation
- [ ] Test with CORTEX-BRAIN-FUNCTIONAL-ANALYSIS.md (should be protected)
```

### Phase 2: Smart Consolidation Intelligence ⏳
```
- [ ] Add similarity detection using difflib.SequenceMatcher
- [ ] Add _detect_similar_documents() method
- [ ] Add consolidation manifest generation
- [ ] Archive similar documents to docs/archive/consolidated/
- [ ] Update references to point to consolidated version
```

### Phase 3: Tier-Aware Relocation Intelligence ⏳
```
- [ ] Add TierAwareCategorizer class
- [ ] Add TIER_RULES mapping
- [ ] Add categorize_to_tier() method
- [ ] Update file move logic to respect tier structure
- [ ] Add reference path updates for moved files
```

### Phase 4: Enhanced Governance Validation ⏳
```
- [ ] Add validate_against_core_005() method
- [ ] Add verify_kebab_case_conversion() method
- [ ] Add pre/post conversion checks
- [ ] Add strict validation reporting
```

### Phase 5: Full Execution & Verification ⏳
```
- [ ] Integration testing with all enhancements
- [ ] Dry-run on full repository
- [ ] Verify CORTEX-BRAIN-FUNCTIONAL-ANALYSIS.md is protected
- [ ] Execute on live repository
- [ ] Verify all references updated
```

---

## 🎯 Your Specific Request Summary

**What you asked for:**
1. ✅ **Already exists** - Kebab-case renaming
2. ✅ **Already exists** - Duplicate detection & removal
3. ✅ **Already exists** - File reorganization
4. ⏳ **NEEDS ADDITION** - Smart consolidation (similar docs)
5. ⏳ **NEEDS ADDITION** - Tier-aware relocation
6. ⏳ **NEEDS ADDITION** - Selective deletion (preserve analysis docs, delete temp reports)

**Priority order for additions:**
1. **First:** Selective deletion (so we don't accidentally delete CORTEX-BRAIN-FUNCTIONAL-ANALYSIS.md)
2. **Second:** Smart consolidation (reduce document sprawl)
3. **Third:** Tier-aware relocation (organize by governance tier)
4. **Fourth:** Enhanced governance validation (strict CORE-005 enforcement)

---

## 📌 Key Preservation Rules to Add

Based on your specification:

```yaml
# Files that MUST be preserved (never delete)
never_delete_patterns:
  - "*FUNCTIONAL-ANALYSIS*"       # ← Your specific request
  - "*IMPLEMENTATION*"
  - "*RECOVERY-PLAN*"
  - "*ROADMAP*"
  - "*PROGRESS*"
  - "*EVIDENCE*"
  - "AC-INDEX*"
  - "*core-rules*"
  - "progress-tracker*"

# Files that ARE safe to delete
safe_to_delete_patterns:
  - "*TEMP*"
  - "*DRAFT*"
  - "*OLD*"
  - "*WORKING*"
  - "*[0-9]{8}*"           # Timestamped versions
  - "scripts/misc/*"
  - "*backup*"
```

---

## 🚀 Next Steps

**Shall I proceed with:**
1. ✅ Add selective deletion intelligence first (safeguard phase)
2. ✅ Add smart consolidation logic
3. ✅ Add tier-aware relocation
4. ✅ Then execute full vacuum on repository

**Confirmation needed for:**
- Use `difflib.SequenceMatcher` with 85% similarity threshold? (can adjust)
- Archive similar docs to `docs/archive/consolidated/`? (location OK?)
- Require user confirmation before deleting anything? (safety check)
- Should tier relocation be optional or mandatory? (phase recommendation)

Ready when you are!
