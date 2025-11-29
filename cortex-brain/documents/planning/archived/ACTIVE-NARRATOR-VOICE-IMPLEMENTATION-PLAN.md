# Active Narrator Voice & Complete Story Regeneration
## Implementation Status & Plan

**Date:** 2025-11-09  
**Feature:** Active Narrator Voice Enforcement + Complete Story Regeneration  
**Phase:** CORTEX 2.0 Core Enhancement  
**Status:** 🔄 IN PROGRESS (40% Complete)

---

## 🎯 Core Principle

**Problem:** Story has passive/clinical narrator voice + incremental patches created inconsistency  
**Solution:** Active narrator enforcement + complete story regeneration from design state

### What We're Fixing

❌ **Before:**
- "Asif Codeinstein designed a system..." ← Reads like Wikipedia
- Story patched incrementally → deprecated sections remain
- Mentions features that were removed
- Inconsistent capabilities across chapters

✅ **After:**
- "So Asif built a system..." ← Energetic storytelling
- Story regenerated completely → coherent start-to-finish
- Only current/intended features mentioned
- Perfect consistency validated automatically

---

## ✅ Completed Work

### 1. Brain Protection Rule Added ✅
**File:** `cortex-brain/brain-protection-rules.yaml`

**Rule:** `ACTIVE_NARRATOR_VOICE`
- Detects passive voice: "designed", "created", "wrote", "implemented"
- Detects documentary markers: "One evening, while...", "After completing..."
- Provides active alternatives: "So X built...", "grabbed keyboard and..."
- Includes rationale and transformation templates

**Integration:** Works with existing brain protection system (22 rules passing)

---

### 2. Plugin Configuration Enhanced ✅
**File:** `src/plugins/doc_refresh_plugin.py`

**New Config Options:**
```python
"enforce_active_narrator": True  # Enable voice checks
"active_narrator_auto_fix": False  # Manual review first
"full_story_regeneration": True  # Complete regen (not patches)
"story_source_of_truth": "design_documents"  # Design-driven
"consistency_validation": True  # Validate cross-chapter
"remove_deprecated_sections": True  # Clean obsolete content
```

---

### 3. Design Document Created ✅
**File:** `cortex-brain/cortex-2.0-design/33-active-narrator-voice-and-story-regeneration.md`

**Contents:**
- Problem statement and rationale
- Detection patterns (passive vs. active)
- Transformation templates
- Story structure template (Parts 1-3)
- Validation criteria
- Test cases
- Before/after examples
- Implementation phases

---

## 🔄 In Progress

### 4. Complete Regeneration System 🔄
**Status:** Architecture designed, implementation started

**Components Needed:**
1. Feature Inventory Extraction
   - Parse design documents (`cortex-2.0-design/*.md`)
   - Build feature database with status (implemented/designed/in-progress)
   - Track dependencies and what each feature replaces

2. Deprecated Section Detection
   - Compare existing story vs. feature inventory
   - Flag sections describing removed features
   - Identify inconsistent capability claims

3. Story Structure Generation
   - Build chapter outline from feature inventory
   - Ensure chronological flow (design order)
   - Place features in correct chapters (Part 1/2/3)

4. Consistency Validation
   - Feature continuity checks
   - Timeline logic validation
   - Capability claim verification
   - Character arc progression

5. Active Voice Transformation
   - Apply detection patterns from brain protection rule
   - Transform passive → active using templates
   - Preserve third-person perspective
   - Maintain comedy and technical accuracy

---

## 📋 Remaining Tasks

### 5. Implement Core Methods (Priority: HIGH)
**File:** `src/plugins/doc_refresh_plugin.py`

```python
# Methods to implement:
_regenerate_complete_story()  # Main orchestrator
_extract_feature_inventory()  # Parse design docs
_detect_deprecated_sections()  # Find obsolete content
_build_story_structure_from_design()  # Generate outline
_validate_story_consistency()  # Cross-chapter checks
_analyze_narrator_voice_complete()  # Full voice analysis
_generate_story_transformation_plan()  # Execution plan
_apply_active_voice_transformations()  # Do the work
```

**Estimated:** 4-6 hours of focused implementation

---

### 6. Automated Testing (Priority: HIGH)
**File:** `tests/tier0/test_active_narrator_voice.py`

**Test Cases:**
```python
test_passive_voice_detection()  # Catches "designed", "wrote routines"
test_active_voice_allowed()  # Allows "So Asif built", "grabbed"
test_documentary_markers()  # Catches "One evening, while"
test_preserves_third_person()  # Keeps "Asif Codeinstein", "He"
test_transformation_templates()  # Validates conversions
test_story_feature_inventory_match()  # Story reflects design
test_no_deprecated_features()  # No obsolete content
test_cross_chapter_consistency()  # Timeline logic valid
```

**Estimated:** 2-3 hours

---

### 7. Plugin Documentation Update (Priority: MEDIUM)
**File:** `docs/plugins/doc-refresh-plugin.md`

**Sections to Add:**
- Active Narrator Voice Enforcement
- Complete Story Regeneration Mode
- Source of Truth Options (design vs. implementation)
- Consistency Validation
- Configuration Guide

**Estimated:** 1 hour

---

### 8. Story Regeneration Execution (Priority: HIGH)
**File:** `docs/story/CORTEX-STORY/Awakening Of CORTEX.md`

**Process:**
1. Run feature inventory extraction
2. Generate story structure from design
3. Validate consistency
4. Apply active voice transformations
5. Review transformation plan
6. Execute full regeneration
7. Validate output (tests pass)

**Estimated:** 2-3 hours (mostly review time)

---

## 🎯 Implementation Sequence

### Week 1: Core Implementation
- [ ] Day 1-2: Implement feature inventory extraction
- [ ] Day 2-3: Implement story structure generation
- [ ] Day 3-4: Implement consistency validation
- [ ] Day 4-5: Implement active voice transformation

### Week 2: Testing & Validation
- [ ] Day 1-2: Write automated tests
- [ ] Day 2-3: Run tests, fix issues
- [ ] Day 3-4: Generate transformation plan
- [ ] Day 4-5: Review and refine plan

### Week 3: Execution & Documentation
- [ ] Day 1-2: Execute story regeneration
- [ ] Day 2-3: Manual review and adjustments
- [ ] Day 3-4: Update plugin documentation
- [ ] Day 4-5: Final validation and deployment

---

## 📊 Progress Tracking

### Overall Status: 40% Complete

**Completed (40%):**
- ✅ Brain protection rule (10%)
- ✅ Plugin configuration (10%)
- ✅ Design document (20%)

**In Progress (30%):**
- 🔄 Core implementation (0% → target 30%)

**Remaining (30%):**
- ⏳ Automated testing (15%)
- ⏳ Documentation update (5%)
- ⏳ Story regeneration (10%)

---

## 🔍 Validation Checklist

When implementation complete, verify:

- [ ] Brain protection rule detects passive voice correctly
- [ ] Feature inventory matches design documents
- [ ] No deprecated features in story
- [ ] Cross-chapter consistency validated
- [ ] Active narrator voice throughout
- [ ] Third-person perspective preserved
- [ ] Comedy and technical accuracy maintained
- [ ] All tests passing (including new voice tests)
- [ ] Documentation updated
- [ ] Story regenerated successfully

---

## 🚀 Next Immediate Steps

1. **Implement `_extract_feature_inventory()`**
   - Parse `cortex-2.0-design/*.md` files
   - Extract feature names, status, phase
   - Build structured inventory

2. **Implement `_detect_deprecated_sections()`**
   - Compare story text vs. inventory
   - Flag removed feature mentions
   - Return list of obsolete sections

3. **Implement `_build_story_structure_from_design()`**
   - Map features to chapters
   - Generate outline with milestones
   - Ensure chronological flow

4. **Create test suite**
   - Validate detection patterns
   - Test transformations
   - Verify consistency checks

---

## 📖 Example Transformation

### Input (Passive):
```markdown
Asif Codeinstein designed a system to save conversation snapshots—like 
bookmarks in a choose-your-own-adventure novel. Every time a conversation 
paused, CORTEX would remember exactly where it left off.
```

### Output (Active):
```markdown
So Asif built a system to save conversation snapshots—like bookmarks in a 
choose-your-own-adventure novel. Every time a conversation paused, CORTEX 
would remember exactly where it left off, what had been done, and what came next.
```

**Changes:**
- "designed" → "So...built" (adds momentum)
- Preserves: Third-person, technical accuracy, comedy setup

---

## 🎓 Key Learnings

1. **Story = Source of Truth:** Don't patch incrementally, regenerate completely
2. **Voice = Energy:** Active narrator makes story engaging (not clinical)
3. **Consistency = Trust:** Readers notice when Ch.3 contradicts Ch.7
4. **Design-Driven:** Story can reflect intended state (with labels)
5. **Automated Validation:** Catch issues before human review

---

## 🔗 Related Files

**Core Implementation:**
- `cortex-brain/brain-protection-rules.yaml` - Voice enforcement rule
- `src/plugins/doc_refresh_plugin.py` - Story regeneration logic
- `cortex-brain/cortex-2.0-design/33-active-narrator-voice-and-story-regeneration.md` - Design doc

**Test Files:**
- `tests/tier0/test_active_narrator_voice.py` - Voice tests (to be created)
- `tests/tier0/test_brain_protector.py` - Existing protection tests (22 passing)

**Documentation:**
- `docs/plugins/doc-refresh-plugin.md` - Plugin docs (to be updated)
- `.github/copilot-instructions.md` - Baseline context (mentions plugins)

**Target:**
- `docs/story/CORTEX-STORY/Awakening Of CORTEX.md` - Story to regenerate

---

**Last Updated:** 2025-11-09  
**Next Review:** After core implementation complete  
**Owner:** CORTEX Doc Refresh Plugin Team
