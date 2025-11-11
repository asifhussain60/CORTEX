# Story Refresh Operation - Redesign Plan

**Date:** November 10, 2025  
**Status:** Planning Phase  
**Problem:** Current story refresh just copies a short template. Needs to update full narrative stories with latest CORTEX 2.0 implementation.

---

## 🎯 Objectives

1. **Load FULL story files** from `docs/story/CORTEX-STORY/` (not the short template)
2. **Extract current CORTEX 2.0 status** from codebase
3. **Weave implementation details** into narrative using Asif Codeinstein's comedic style
4. **Update all three story files:**
   - `Awakening Of CORTEX.md` (narrative story - 1,659 lines, 58KB)
   - `Technical-CORTEX.md` (technical deep-dive - 67KB)
   - `Image-Prompts.md` (diagram generation prompts - 45KB)
5. **Generate human-readable summaries:**
   - Rule book summary (from `brain-protection-rules.yaml`)
   - Feature list summary (from `cortex-operations.yaml`)
6. **Delete the short version** (`docs/awakening-of-cortex.md`) to avoid confusion

---

## 📊 Data Sources to Extract

### 1. Implementation Status
**Source:** `cortex-operations.yaml`
- Total operations: 14
- Total modules: 97
- Modules implemented: 37 (38%)
- Operations status (READY, PARTIAL, PENDING, PLANNED)

### 2. Brain Protection Rules
**Source:** `cortex-brain/brain-protection-rules.yaml`
- SKULL rules (4 critical)
- Layer 1-6 rules
- Rule #22 details
- Enforcement mechanisms

### 3. Plugin System
**Source:** `src/plugins/` directory
- Active plugins
- Plugin capabilities
- Hook system
- Extensibility features

### 4. Workflow Pipeline
**Source:** `cortex-operations.yaml` operations
- DAG workflows
- Phase transitions
- Checkpoint/resume capabilities

### 5. Performance Metrics
**Source:** Code comments, docstrings
- Tier 1: <50ms target
- Tier 2: <150ms target
- Tier 3: <200ms target
- Token reduction: 97.2%

### 6. Modular Architecture
**Source:** File structure analysis
- Module count
- Lines of code per file
- Refactoring results

---

## 🏗️ New Module Design

### Module 1: `extract_cortex_status_module.py`
**Purpose:** Extract current implementation status from codebase

**Inputs:**
- `project_root`

**Outputs:**
- `cortex_status` (dict):
  - operations (list with status)
  - modules (implemented/total counts)
  - plugins (active plugins)
  - rules (SKULL + protection layers)
  - performance_metrics (targets/actuals)
  - file_structure (module sizes)

**Logic:**
1. Parse `cortex-operations.yaml`
2. Parse `brain-protection-rules.yaml`
3. Scan `src/plugins/` for active plugins
4. Count modules and implementation status
5. Extract performance targets from docstrings

---

### Module 2: `load_full_story_files_module.py`
**Purpose:** Load all three story files from CORTEX-STORY directory

**Inputs:**
- `project_root`

**Outputs:**
- `awakening_story` (str): Full narrative
- `technical_story` (str): Technical deep-dive
- `image_prompts` (str): Diagram prompts

**Logic:**
1. Load `docs/story/CORTEX-STORY/Awakening Of CORTEX.md`
2. Load `docs/story/CORTEX-STORY/Technical-CORTEX.md`
3. Load `docs/story/CORTEX-STORY/Image-Prompts.md`
4. Validate structure (chapter markers, sections)

---

### Module 3: `weave_narrative_updates_module.py`
**Purpose:** Update Awakening Of CORTEX.md with new implementation details

**Inputs:**
- `awakening_story` (original content)
- `cortex_status` (extracted data)

**Outputs:**
- `updated_awakening_story` (str): Updated narrative

**Logic:**
1. **Identify update points** (chapter markers, interludes)
2. **Generate narrative snippets** in Asif Codeinstein's style:
   - "The operation system that actually works" (new operations)
   - "The plugin revolution" (plugin system)
   - "The files that lost weight" (modular refactor)
   - "The conversation that remembered everything" (state management)
3. **Insert/update sections** maintaining comedic tone
4. **Update statistics** in interludes (module counts, performance)

**Narrative Style Guidelines:**
- Self-deprecating humor ("What could possibly go wrong?")
- Technical frustration comedy (coffee-fueled late nights)
- Character voice: Asif Codeinstein (mad scientist)
- CORTEX voice: Increasingly sentient, slightly sarcastic
- Whiteboard archaeology format for technical evolution

---

### Module 4: `update_technical_deep_dive_module.py`
**Purpose:** Update Technical-CORTEX.md with current architecture

**Inputs:**
- `technical_story` (original content)
- `cortex_status` (extracted data)

**Outputs:**
- `updated_technical_story` (str): Updated technical docs

**Logic:**
1. **Update implementation status** (percentages, completion)
2. **Update module counts** in architecture diagrams
3. **Update performance metrics** (actual vs target)
4. **Update plugin list** (active plugins)
5. **Update operation table** (status indicators)
6. **Preserve code examples** and diagrams

---

### Module 5: `update_image_prompts_module.py`
**Purpose:** Update Image-Prompts.md with new diagrams needed

**Inputs:**
- `image_prompts` (original content)
- `cortex_status` (extracted data)

**Outputs:**
- `updated_image_prompts` (str): Updated prompt collection

**Logic:**
1. **Add new diagram prompts** for:
   - Plugin system architecture
   - Workflow pipeline DAG
   - State machine (conversation lifecycle)
   - Modular file structure comparison
2. **Update existing prompts** with new module counts
3. **Maintain prompt format** (technical, professional style)

---

### Module 6: `generate_rule_summary_module.py`
**Purpose:** Create human-readable rule book summary

**Inputs:**
- `cortex_status['rules']`

**Outputs:**
- `rule_summary.md` (new file)

**Logic:**
1. Extract all SKULL rules
2. Extract Layer 1-6 rules
3. Format as readable list with explanations
4. Add "Why this matters" sections
5. Include enforcement mechanisms

---

### Module 7: `generate_feature_summary_module.py`
**Purpose:** Create human-readable feature list

**Inputs:**
- `cortex_status['operations']`
- `cortex_status['modules']`

**Outputs:**
- `feature_summary.md` (new file)

**Logic:**
1. List all operations with natural language triggers
2. Group by category (onboarding, environment, documentation, etc.)
3. Show implementation status with visual indicators
4. Add "What it does" explanations
5. Include usage examples

---

### Module 8: `save_updated_stories_module.py`
**Purpose:** Write all updated content back to files

**Inputs:**
- `updated_awakening_story`
- `updated_technical_story`
- `updated_image_prompts`
- `rule_summary`
- `feature_summary`

**Outputs:**
- Updated files in `docs/story/CORTEX-STORY/`
- New summary files

**Logic:**
1. Create timestamped backups in `.backups/`
2. Write updated story files
3. Write new summary files
4. Validate all files written correctly

---

### Module 9: `remove_short_version_module.py`
**Purpose:** Delete the incorrect short version

**Inputs:**
- `project_root`

**Outputs:**
- None (destructive operation)

**Logic:**
1. Delete `docs/awakening-of-cortex.md`
2. Update any references pointing to old file
3. Add redirect comment to `prompts/shared/story.md`

---

## 🔄 Updated Operation Definition

```yaml
refresh_cortex_story:
  name: Refresh CORTEX Story
  description: Update full narrative story files with latest CORTEX 2.0 implementation
  natural_language:
    - refresh story
    - update story
    - weave latest changes into story
  modules:
    - extract_cortex_status
    - load_full_story_files
    - weave_narrative_updates
    - update_technical_deep_dive
    - update_image_prompts
    - generate_rule_summary
    - generate_feature_summary
    - save_updated_stories
    - remove_short_version
  profiles:
    quick:
      modules:
        - extract_cortex_status
        - load_full_story_files
        - weave_narrative_updates
        - save_updated_stories
    standard:
      modules:
        - extract_cortex_status
        - load_full_story_files
        - weave_narrative_updates
        - update_technical_deep_dive
        - generate_rule_summary
        - generate_feature_summary
        - save_updated_stories
    full:
      modules:
        - extract_cortex_status
        - load_full_story_files
        - weave_narrative_updates
        - update_technical_deep_dive
        - update_image_prompts
        - generate_rule_summary
        - generate_feature_summary
        - save_updated_stories
        - remove_short_version
```

---

## 🎨 Narrative Weaving Examples

### Example 1: Plugin System Chapter

**Insertion Point:** After "Chapter 8: The Plugin That Saved Christmas"

**Generated Content:**
```markdown
## Chapter 8: The Plugin That Saved Christmas

[Existing narrative...]

And that's when Asif Codeinstein had his revelation: "CORTEX doesn't need to do everything. It needs to let OTHER PEOPLE do things."

He spent the next weekend building the plugin system — a way for teams to extend CORTEX without touching its brain.

> "It's like giving people Legos instead of a concrete block," he explained to CORTEX.

> "**I prefer 'modular architecture' but Legos works too,**" CORTEX replied.

**The Results Were Immediate:**
- Cleanup Plugin: Removes temp files (no core changes needed)
- Documentation Plugin: Auto-refreshes docs (no core changes needed)
- Self-Review Plugin: Health checks (no core changes needed)

Teams could add features WITHOUT breaking CORTEX's brain.

Core stayed clean. Extensions stayed isolated. Everyone stayed sane.

> "**I'm basically an app store now,**" CORTEX said proudly.

"Don't push it."

---

**Current Stats (November 2025):**
- 7 active plugins
- 0 core modifications required
- 60% reduction in core bloat
- Asif's sanity: Moderately preserved
```

---

## 📋 Implementation Checklist

- [ ] Create 9 new modules in `src/operations/modules/`
- [ ] Update `cortex-operations.yaml` with new operation definition
- [ ] Write tests for each module
- [ ] Test narrative weaving with mock data
- [ ] Validate comedic tone matches Asif Codeinstein's voice
- [ ] Execute full story refresh
- [ ] Verify all three files updated correctly
- [ ] Verify summaries generated
- [ ] Verify short version deleted
- [ ] Update CORTEX.prompt.md references

---

## ⚠️ Critical Considerations

1. **Preserve Narrative Voice:** All updates must match Asif Codeinstein's style
2. **Respect Story Structure:** Don't break chapter flow
3. **Maintain Comedy:** Technical updates should be funny
4. **Update Statistics:** All numbers must be current
5. **Backup Everything:** Create timestamped backups before changes
6. **Test Thoroughly:** Validate narrative coherence after weaving

---

**Next Steps:**
1. Review this plan with user
2. Implement modules one by one
3. Test with small changes first
4. Execute full story refresh
5. Validate results

