# Design Document 33: Active Narrator Voice & Complete Story Regeneration

**Status:** IN_PROGRESS  
**Phase:** 5.0 (Story System Enhancement)  
**Priority:** HIGH  
**Created:** 2025-11-09  
**Dependencies:** Doc Refresh Plugin, Brain Protection Rules

---

## Problem Statement

### Current Issues

1. **Passive Narrator Voice** - Story reads like clinical documentation instead of energetic storytelling
   - ❌ "Asif Codeinstein designed a system..."  
   - ❌ "He wrote routines for..."  
   - ❌ "One evening, while reviewing..."

2. **Incremental Updates Create Inconsistency** - Patching sections leaves:
   - Redundant descriptions of deprecated features
   - Inconsistent capability claims across chapters
   - Narrative gaps and flow breaks
   - Legacy cruft confusing readers

3. **Story Doesn't Reflect Reality** - Current story may describe:
   - Features that were removed
   - Old architectures that were refactored
   - Approaches that were deprecated
   - Missing new major features

---

## Solution: Dual Enhancement

### Enhancement 1: Active Narrator Voice Enforcement

**Principle:** Story is told by an ENERGETIC third-person narrator (not clinical observer, not first-person memoir)

#### Detection Patterns

**Passive Voice Indicators:**
```regex
# Clinical verbs
(Asif Codeinstein|He) (designed|created|wrote|implemented|developed)

# Documentary markers  
One (evening|morning|day|night), while
After (completing|finishing)
, while reviewing
During the
```

**Active Voice Examples:**
```markdown
✅ "So Asif built a system..."
✅ "He grabbed his keyboard and coded..."
✅ "That evening, knee-deep in diagrams..."
✅ "Three hours later, coffee-fueled and delirious..."
```

#### Transformation Templates

| Passive Pattern | Active Transformation | Why |
|----------------|----------------------|-----|
| `designed a system` | `So Asif built a system` | Adds momentum |
| `wrote routines for` | `grabbed keyboard and coded` | Shows action |
| `One evening, while` | `That evening, knee-deep in` | Vivid scene |
| `After completing X` | `X complete, Asif leaned back` | Present tense |
| `made a decision` | `stared at screen and decided` | Shows moment |

---

### Enhancement 2: Complete Story Regeneration

**Principle:** Generate entire story from design state, not incremental patches

#### Source of Truth Options

1. **`design_documents`** (Default) - Tell the story of what CORTEX 2.0 IS/WILL BE
   - Use: During active development, pre-release
   - Includes: Designed but not-yet-implemented features
   - Benefit: Story drives vision, marketing can start early

2. **`implemented_code`** - Tell the story of what EXISTS NOW
   - Use: Post-release, stable releases
   - Includes: Only shipped, tested features  
   - Benefit: 100% accurate to current reality

3. **`mixed`** - Design for in-progress, implementation for complete
   - Use: Rolling releases, continuous deployment
   - Includes: Clear labeling of status
   - Benefit: Transparency about roadmap

#### Story Generation Pipeline

```
Design Documents 
    ↓
Feature Inventory Extraction
    ↓
Deprecated Section Detection
    ↓
Story Structure Generation
    ↓
Consistency Validation
    ↓
Active Voice Transformation
    ↓
Complete Story Output
```

#### Feature Inventory Structure

```python
{
    "feature_id": "conversation_state",
    "name": "Conversation State Checkpoints",
    "status": "implemented",  # or "designed", "in_progress"
    "phase": "Part 2, Chapter 7",
    "milestones": [
        "Checkpoint on window blur",
        "Resume from crash",
        "15-minute auto-save"
    ],
    "dependencies": ["tier1_memory", "sqlite_backend"],
    "removes": ["manual_capture_only"],  # What it replaces
    "comedy_hooks": [
        "Battery death trauma",
        "Lost 3 hours of work",
        "Time machine for conversations"
    ]
}
```

#### Consistency Validation Checks

1. **Feature Continuity** - Don't mention feature in Ch.2 if introduced in Ch.5
2. **Capability Claims** - All claimed capabilities exist in feature inventory
3. **Deprecation Cleanup** - Remove sections about removed features
4. **Timeline Logic** - Events happen in chronological design order
5. **Character Arc** - Asif's knowledge grows progressively (doesn't forget)

---

## Implementation

### Brain Protection Rule

**File:** `cortex-brain/brain-protection-rules.yaml`

```yaml
- rule_id: "ACTIVE_NARRATOR_VOICE"
  name: "Active Narrator Voice (Not Passive Documentation)"
  severity: "warning"
  description: "Story uses passive/clinical narrator voice"
  
  detection:
    passive_verbs:
      - "Asif Codeinstein designed"
      - "He wrote routines"
    documentary_markers:
      - "One evening, while"
      - "After completing"
```

### Doc Refresh Plugin Enhancement

**File:** `src/plugins/doc_refresh_plugin.py`

**New Config Options:**
```python
"full_story_regeneration": True,  # Generate complete story
"story_source_of_truth": "design_documents",  # or "implemented_code" or "mixed"
"consistency_validation": True,  # Validate cross-chapter consistency
"remove_deprecated_sections": True,  # Clean up obsolete content
"enforce_active_narrator": True,  # Apply voice rules
```

**New Methods:**
```python
_regenerate_complete_story()  # Full story from design state
_extract_feature_inventory()  # Build from design docs
_detect_deprecated_sections()  # Find obsolete content
_build_story_structure_from_design()  # Generate chapter outline
_validate_story_consistency()  # Check cross-chapter logic
_generate_story_transformation_plan()  # Create execution plan
```

---

## Story Structure Template

### Part 1: The Awakening (Chapters 1-5)
**Design Features:** Tier 1 Memory, Dual Hemisphere, Tier 2 Learning, Rule #22

```
Chapter 1: The Intern Who Forgot
  - Problem: Goldfish attention span
  - Solution: Tier 1 (SQLite memory)
  - Status: [Check feature_inventory]

Chapter 2: The Brain That Built Garbage  
  - Problem: Remembers but no judgment
  - Solution: Dual hemisphere split
  - Status: [Check feature_inventory]

Chapter 3: The Intern Who Started Learning
  - Problem: Repeats same questions
  - Solution: Tier 2 pattern learning
  - Status: [Check feature_inventory]
  
Chapter 4: The Brain That Said "No"
  - Problem: No quality control
  - Solution: Rule #22 (challenge bad ideas)
  - Status: [Check feature_inventory]

Chapter 5: The Partner
  - Transformation complete: Intern → Partner
  - Status: Sum of Part 1 features
```

### Part 2: The Evolution to 2.0 (Chapters 6-11)
**Design Features:** Modular Architecture, Conversation State, Plugin System, Self-Review, Workflow Pipelines, Knowledge Boundaries

### Part 3: The Extension Era (Chapters 12-15)
**Design Features:** VS Code Extension, Token Optimization, External Monitor, Checkpoints, Active Capture

---

## Validation Criteria

### Story Quality Checks

1. **Voice Consistency** - 100% active narrator throughout
2. **Feature Accuracy** - All mentioned features exist in inventory
3. **No Deprecated Content** - Zero references to removed features
4. **Narrative Flow** - Smooth transitions, no gaps
5. **Comedy Preservation** - Humor maintained in transformations
6. **Technical Accuracy** - Correct capability descriptions

### Test Cases

```python
def test_story_reflects_design_state():
    """Story should match design document feature list"""
    story_features = extract_features_from_story()
    design_features = load_feature_inventory()
    assert story_features == design_features

def test_no_deprecated_features():
    """Story should not mention removed features"""
    deprecated = ["KDS", "old_memory_system", "monolithic_entry"]
    story_text = load_story()
    for feature in deprecated:
        assert feature not in story_text

def test_active_narrator_voice():
    """All narration should be active voice"""
    passive_patterns = ["designed a", "wrote routines", "One evening, while"]
    story_text = load_story()
    violations = find_passive_voice(story_text, passive_patterns)
    assert len(violations) == 0
```

---

## Example: Before vs After

### Before (Incremental Patch):
```markdown
## Chapter 7: The State Machine

Asif Codeinstein designed a system to save conversation snapshots...

[Rest of story may mention old conversation tracking method]
[Chapter 3 might still reference deprecated KDS system]
[No mention of ambient capture added in Chapter 13]
```

### After (Complete Regeneration):
```markdown
## Chapter 7: The State Machine

So Asif built a system to save conversation snapshots...

[All chapters consistent with CORTEX 2.0 design]
[No KDS references - replaced with Tier 1]  
[Ambient capture referenced in Ch.7 as "coming later"]
[Complete feature continuity Part 1 → Part 2 → Part 3]
```

---

## Benefits

### For Readers
- ✅ Coherent narrative start to finish
- ✅ No confusing deprecated sections
- ✅ Accurate capability descriptions
- ✅ Energetic storytelling throughout

### For Maintainers  
- ✅ Single regeneration vs. dozens of patches
- ✅ Automated consistency validation
- ✅ Clear source of truth (design docs)
- ✅ No manual deprecation tracking

### For Marketing
- ✅ Story can reflect upcoming features (with labels)
- ✅ Vision-driven narrative
- ✅ Always up-to-date with product state

---

## Migration Path

### Phase 1: Detection (Current)
- ✅ Brain protection rule added
- ✅ Passive voice detection working
- 🔄 Inventory extraction logic (in progress)

### Phase 2: Validation  
- Consistency checks implementation
- Test suite for story quality
- Deprecated section detection

### Phase 3: Generation
- Complete story regeneration
- Active voice transformation
- Automated update pipeline

### Phase 4: Continuous Sync
- Git hook: Regenerate on design doc changes
- CI/CD: Validate story on every commit
- Auto-PR: Story updates for review

---

## Configuration Example

```json
{
  "doc_refresh_plugin": {
    "full_story_regeneration": true,
    "story_source_of_truth": "design_documents",
    "consistency_validation": true,
    "remove_deprecated_sections": true,
    "enforce_active_narrator": true,
    "active_narrator_auto_fix": false,
    "backup_before_refresh": true
  }
}
```

---

## Success Metrics

- **Voice Quality:** 0 passive narrator violations
- **Feature Accuracy:** 100% match with feature inventory
- **Consistency Score:** 0 timeline/capability conflicts
- **Maintenance Time:** <5 min to regenerate entire story
- **Reader Clarity:** No "wait, didn't Chapter 3 say..." confusion

---

## Related Documents

- `cortex-brain/brain-protection-rules.yaml` - Voice enforcement rules
- `src/plugins/doc_refresh_plugin.py` - Story regeneration logic
- `docs/story/CORTEX-STORY/Awakening Of CORTEX.md` - Target story file
- `cortex-brain/cortex-2.0-design/00-INDEX.md` - Feature inventory source

---

**Status:** Design Complete, Implementation In Progress  
**Next:** Implement feature inventory extraction and story structure generation
