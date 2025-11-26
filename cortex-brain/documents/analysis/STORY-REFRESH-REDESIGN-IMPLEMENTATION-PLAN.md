# Story Refresh Module - Complete Redesign Implementation Plan

**Created:** 2025-11-11  
**Author:** Asif Hussain  
**Status:** Design Phase Complete ✅  
**Estimated Effort:** 17-23 hours  
**Key Enhancement:** Dual-mode support (generate-from-scratch vs update-in-place)

---

## 🎯 Objective

Redesign the story refresh module to:
1. **Evaluate** latest CORTEX changes and architecture
2. **Generate** 9+ detailed chapter files with engaging narrative (Asif Codeinstein in NJ, Wizard of Oz references)
3. **Collapse** all chapters into `THE-AWAKENING-OF-CORTEX.md` (95% story, 5% technical, minimal read time)
4. **Regenerate** supporting documentation files (Technical-CORTEX.md, Image-Prompts.md, History.md, Ancient-Rules.md, CORTEX-FEATURES.md)

**🆕 NEW FEATURE:** Intelligent mode selection - generate everything from scratch OR update only what changed!

---

## 📊 Quick Mode Comparison

| Aspect | Generate-From-Scratch | Update-In-Place |
|--------|----------------------|-----------------|
| **When to Use** | Major architectural changes (>20%) | Implementation progress (<20%) |
| **Chapters Affected** | ALL (9+) regenerated | Only affected chapters updated |
| **Existing Content** | Overwritten (backed up) | Preserved and merged |
| **Custom Edits** | Lost (require reapplication) | Preserved |
| **Duration** | 15-25 minutes | 3-8 minutes |
| **Risk** | Narrative restart | Potential inconsistency |
| **Frequency** | Every 3-6 months or major release | Every 1-2 weeks |
| **Example Trigger** | New tier, 3+ new agents | 50 tests added, bug fixes |

---

## 📋 Current State Analysis

### Existing Architecture (What We Have)

**Location:** `src/plugins/doc_refresh_plugin.py`

**Current Capabilities:**
- ✅ `_refresh_story_doc()` - Entry point for story refresh
- ✅ `_regenerate_complete_story()` - Plans regeneration (validation only)
- ✅ `_extract_feature_inventory()` - Pulls features from design docs
- ✅ `_detect_deprecated_sections()` - Identifies outdated content
- ✅ `_build_story_structure_from_design()` - Creates story outline
- ✅ `_validate_story_consistency()` - Checks coherence
- ✅ Progressive recap generation
- ✅ Lab notebook transformation
- ✅ Narrator voice analysis

**Supporting Modules:**
- ✅ `build_consolidated_story_module.py` - Merges chapters into THE-AWAKENING-OF-CORTEX.md
- ✅ `generate_history_doc_module.py` - Generates History.md
- ✅ `generate_technical_doc_module.py` - Generates Technical-CORTEX.md
- ✅ `generate_image_prompts_module.py` - Generates Image-Prompts.md
- ✅ `validate_story_structure_module.py` - Validates Markdown structure
- ✅ `apply_narrator_voice_module.py` - Transforms narrative voice

**Current Limitations:**
- ❌ Does NOT regenerate individual chapter files (01-09)
- ❌ Does NOT evaluate latest CORTEX changes from CORTEX-UNIFIED-ARCHITECTURE.yaml
- ❌ Chapter generation logic is missing
- ❌ Story-to-technical ratio (95:5) not enforced
- ❌ No read-time optimization beyond basic validation
- ❌ Ancient-Rules.md and CORTEX-FEATURES.md not relocated to docs/story/CORTEX-STORY/

---

## 🏗️ Proposed Architecture

### Generation Modes (NEW!)

The story refresh system supports two distinct modes:

#### Mode 1: Generate From Scratch (FULL REGENERATION)
**When to Use:**
- Major architectural changes to CORTEX
- Significant new features added (e.g., new brain tier, agent system overhaul)
- First-time story generation
- Manual trigger: `refresh story --mode=generate-from-scratch`

**What It Does:**
- ✅ Evaluates complete CORTEX architecture from YAML
- ✅ Generates ALL 9+ chapters from scratch (overwrites existing)
- ✅ Creates new narrative structure based on current state
- ✅ Regenerates ALL supporting files (Technical-CORTEX.md, Image-Prompts.md, etc.)
- ✅ Creates backups before overwriting

**Risk:** May lose custom edits or narrative refinements

#### Mode 2: Update In Place (INCREMENTAL UPDATE)
**When to Use:**
- Minor implementation progress (tests passing, modules completed)
- Bug fixes or small improvements
- Regular status updates
- Manual trigger: `refresh story --mode=update-in-place`

**What It Does:**
- ✅ Evaluates only CHANGED sections since last refresh
- ✅ Updates specific chapters affected by changes (preserves others)
- ✅ Merges new content with existing narrative
- ✅ Updates only changed sections in supporting files
- ✅ Preserves custom edits and narrative style

**Risk:** May accumulate inconsistencies over time (recommend full regen every 3-6 months)

#### Mode Detection (AUTOMATIC)
If user doesn't specify mode, system auto-detects:

```python
def detect_story_refresh_mode(changes_since_last_refresh: List[Dict]) -> str:
    """
    Auto-detect appropriate refresh mode based on change magnitude
    
    Returns: 'generate-from-scratch' or 'update-in-place'
    """
    
    # Criteria for GENERATE FROM SCRATCH:
    # - New brain tier added
    # - New agent added
    # - Major architectural change (>20% of system)
    # - No previous story exists
    
    # Criteria for UPDATE IN PLACE:
    # - Implementation progress (<20% change)
    # - Test count increase
    # - Minor feature additions
    # - Bug fixes
```

### Workflow Overview

```
0. MODE SELECTION
   └─> User specifies --mode OR auto-detect from changes

1. EVALUATE CORTEX CHANGES
   └─> Load CORTEX-UNIFIED-ARCHITECTURE.yaml
   └─> Extract features, implementation status, architecture patterns
   └─> Identify changes since last story refresh
   └─> Calculate change magnitude (% of system affected)

2. GENERATE CHAPTERS (9+ files)
   ├─> [GENERATE FROM SCRATCH MODE]
   │   └─> For each chapter:
   │       ├─> Extract relevant technical content
   │       ├─> Generate engaging narrative (Asif Codeinstein + Wizard of Oz)
   │       ├─> Apply 95% story / 5% technical ratio
   │       ├─> Write to docs/story/CORTEX-STORY/{chapter}.md (OVERWRITE)
   │
   └─> [UPDATE IN PLACE MODE]
       └─> For each AFFECTED chapter:
           ├─> Load existing chapter content
           ├─> Identify sections to update (based on changes)
           ├─> Generate updated narrative for changed sections only
           ├─> Merge with existing content (preserve style)
           ├─> Write updated chapter (MERGE, not overwrite)

3. COLLAPSE CHAPTERS
   └─> Read all chapter files (01-09+)
   └─> Preserve intro (Asif Codeinstein basement scene)
   └─> Merge chapters with transitions
   └─> Optimize for minimal read time (60-75 min target)
   └─> Write to THE-AWAKENING-OF-CORTEX.md

4. REGENERATE SUPPORTING FILES
   ├─> [GENERATE FROM SCRATCH] - Regenerate ALL files
   ├─> [UPDATE IN PLACE] - Update only changed sections
   │
   ├─> Technical-CORTEX.md (comprehensive technical docs)
   ├─> Image-Prompts.md (Gemini diagram prompts)
   ├─> History.md (update CORTEX section only, preserve KDS 1/2)
   ├─> Ancient-Rules.md (move to docs/story/CORTEX-STORY/)
   └─> CORTEX-FEATURES.md (move to docs/story/CORTEX-STORY/)
```

---

## 📦 New Modules to Implement

### Module 1: CORTEX Architecture Evaluator (ENHANCED)

**File:** `src/operations/modules/evaluate_cortex_architecture_module.py`

**Purpose:** Extract current CORTEX state from CORTEX-UNIFIED-ARCHITECTURE.yaml and determine refresh mode

**Responsibilities:**
1. Load CORTEX-UNIFIED-ARCHITECTURE.yaml
2. Extract:
   - Core components (brain tiers, agents, operations, plugins)
   - Implementation status (% complete, tests passing)
   - Architecture patterns (SOLID, plugin system, etc.)
   - Recent changes (compare with last refresh timestamp)
3. **Calculate change magnitude:**
   - Count new components added (tiers, agents, plugins)
   - Measure implementation progress delta (% change)
   - Detect architectural pattern changes
4. **Auto-detect refresh mode** (if not user-specified):
   - GENERATE-FROM-SCRATCH: >20% change, new tier/agent, or no previous story
   - UPDATE-IN-PLACE: <20% change, implementation progress only
5. Return structured feature inventory + recommended mode

**Inputs:**
- `project_root` (Path)
- `last_refresh_timestamp` (optional datetime)
- `refresh_mode` (optional: 'generate-from-scratch' | 'update-in-place' | 'auto')

**Outputs:**
- `feature_inventory` (Dict[str, Any])
- `implementation_status` (Dict[str, Any])
- `architecture_patterns` (List[Dict])
- `changes_since_last_refresh` (List[Dict])
- `change_magnitude` (float) - **NEW!** Percentage of system affected
- `recommended_mode` (str) - **NEW!** 'generate-from-scratch' or 'update-in-place'
- `mode_rationale` (str) - **NEW!** Explanation for recommendation

**Estimated Effort:** 3 hours (was 2 hours, +1 for mode detection logic)

---

### Module 2: Story Chapter Generator (MODE-AWARE)

**File:** `src/operations/modules/generate_story_chapters_module.py`

**Purpose:** Generate or update 9+ detailed chapter files with engaging narrative (mode-aware)

**Responsibilities:**

#### GENERATE-FROM-SCRATCH Mode:
1. For each chapter (01-09):
   - Extract relevant technical content from feature inventory
   - Generate narrative using templates:
     - **Intro:** Asif Codeinstein in NJ basement, Wizard of Oz inspiration
     - **Story Style:** Funny, engaging, coffee/debugging references
     - **Technical Integration:** 95% story, 5% technical (high-level only)
   - Apply progressive recaps (Part 2 recaps Part 1, Part 3 recaps 1+2)
   - **OVERWRITE** to `docs/story/CORTEX-STORY/{chapter}.md`
   - Create backup in `.backups/` with timestamp

#### UPDATE-IN-PLACE Mode:
1. For each **affected** chapter:
   - Load existing chapter content
   - Parse existing structure (headings, sections)
   - Identify sections to update based on `changes_since_last_refresh`
   - Generate updated narrative for ONLY changed sections
   - **Merge** new content with existing (preserve surrounding narrative)
   - Maintain existing story style and voice
   - Update section in place, write merged chapter
   - Create backup before merge

2. **Change-to-Chapter Mapping:**
   ```python
   change_affects_chapters = {
       "tier_0_changes": ["03-brain-architecture.md", "08-protection-layer.md"],
       "tier_1_changes": ["02-first-memory.md"],
       "tier_2_changes": ["07-knowledge-graph.md"],
       "tier_3_changes": ["03-brain-architecture.md"],
       "agent_changes": ["04-left-brain.md", "05-right-brain.md", "06-corpus-callosum.md"],
       "plugin_changes": ["09-awakening.md"],
       "operation_changes": ["09-awakening.md"],
       "test_progress": ["ALL chapters - update metrics only"],
   }
   ```

3. Chapter breakdown:
   - **01-amnesia-problem.md** - The intern with amnesia
   - **02-first-memory.md** - Tier 1 working memory
   - **03-brain-architecture.md** - Four-tier brain system
   - **04-left-brain.md** - Tactical agents (Executor, Tester, etc.)
   - **05-right-brain.md** - Strategic agents (Architect, Intent Detector, etc.)
   - **06-corpus-callosum.md** - Agent coordination
   - **07-knowledge-graph.md** - Tier 2 learning system
   - **08-protection-layer.md** - SKULL rules, Tier 0
   - **09-awakening.md** - Token optimization, ambient capture, the future

4. Narrative templates:
   - Use Asif Codeinstein character consistently
   - Wizard of Oz references (Scarecrow wanting a brain)
   - Basement lab setting (moldy, router blinking, coffee mugs)
   - Copilot as physical machine (server racks, LED strips)
   - Humor: 2 AM debugging, coffee addiction, git commits like "fixed stuff"

**Inputs:**
- `feature_inventory` (from Module 1)
- `story_template_config` (narrative style settings)
- `target_word_count_per_chapter` (default: 1,500-2,500 words)
- `refresh_mode` (str) - **NEW!** 'generate-from-scratch' or 'update-in-place'
- `changes_since_last_refresh` (List[Dict]) - **NEW!** For update-in-place mode
- `existing_chapters` (Dict[str, str]) - **NEW!** Current chapter content

**Outputs:**
- `chapters_generated` (List[Path]) - Paths to 9+ chapter files
- `chapters_updated` (List[Path]) - **NEW!** Paths to updated chapters (update-in-place mode)
- `chapters_unchanged` (List[Path]) - **NEW!** Paths to preserved chapters
- `word_counts` (Dict[str, int]) - Word count per chapter
- `story_technical_ratios` (Dict[str, float]) - Story:technical ratio per chapter
- `mode_used` (str) - **NEW!** Actual mode used
- `backups_created` (List[Path]) - **NEW!** Backup file paths

**Estimated Effort:** 6-8 hours (was 4-6 hours, +2 for update-in-place logic)

---

### Module 3: Story Chapter Collapser

**File:** `src/operations/modules/collapse_story_chapters_module.py`

**Purpose:** Merge all chapters into THE-AWAKENING-OF-CORTEX.md with read-time optimization

**Responsibilities:**
1. Read all chapter files (01-09+)
2. Preserve intro from existing THE-AWAKENING-OF-CORTEX.md (Asif Codeinstein basement scene)
3. Merge chapters with smooth transitions
4. Add progressive recaps (auto-generated summaries at Part 2, Part 3 starts)
5. Optimize for minimal read time:
   - Target: 60-75 minutes (15,000-18,750 words at 250 wpm)
   - Trim verbose sections if exceeding target
   - Maintain 95% story / 5% technical ratio
6. Write consolidated story to THE-AWAKENING-OF-CORTEX.md

**Inputs:**
- `chapters` (List[Path]) - All chapter file paths
- `target_read_time_minutes` (default: 60-75)
- `story_technical_ratio` (default: 0.95)

**Outputs:**
- `consolidated_story_path` (Path)
- `total_word_count` (int)
- `estimated_read_time_minutes` (float)
- `story_technical_ratio_achieved` (float)

**Estimated Effort:** 2-3 hours

---

### Module 4: Technical Documentation Generator

**File:** `src/operations/modules/generate_technical_cortex_doc_module.py`

**Purpose:** Generate comprehensive Technical-CORTEX.md from architecture data

**Responsibilities:**
1. Extract technical details from CORTEX-UNIFIED-ARCHITECTURE.yaml:
   - Architecture overview (four tiers, agents, operations, plugins)
   - API reference (Tier 1-3 classes and methods)
   - Implementation status (tests passing, modules complete)
   - Performance metrics (query times, token reduction)
2. Format as structured technical documentation (NOT narrative)
3. Include code examples, schemas, diagrams references
4. Write to `docs/story/CORTEX-STORY/Technical-CORTEX.md`

**Inputs:**
- `feature_inventory` (from Module 1)
- `implementation_status` (from Module 1)

**Outputs:**
- `technical_doc_path` (Path)
- `sections_generated` (List[str])

**Estimated Effort:** 2 hours

---

### Module 5: Image Prompts Generator

**File:** `src/operations/modules/generate_image_prompts_doc_module.py`

**Purpose:** Generate Gemini-compatible system diagram prompts

**Responsibilities:**
1. Create prompts for system diagrams:
   - **Four-Tier Brain Architecture** (layered diagram)
   - **Agent System** (dual-hemisphere flowchart)
   - **Universal Operations** (workflow pipeline)
   - **Plugin Architecture** (extension points)
   - **Conversation Tracking** (sequence diagram)
   - **Token Optimization** (before/after comparison)
2. Format as Gemini prompts:
   - Clear diagram type (flowchart, sequence, layered, etc.)
   - Component descriptions
   - Relationships and data flow
   - Visual style guidance (TECHNICAL, not cartoons)
3. Write to `docs/story/CORTEX-STORY/Image-Prompts.md`

**Inputs:**
- `architecture_patterns` (from Module 1)

**Outputs:**
- `image_prompts_doc_path` (Path)
- `diagram_count` (int)

**Estimated Effort:** 1-2 hours

---

### Module 6: History Documentation Updater

**File:** Update existing `src/operations/modules/generate_history_doc_module.py`

**Purpose:** Update CORTEX evolution section in History.md (preserve KDS 1/2)

**Responsibilities:**
1. Load existing `docs/story/CORTEX-STORY/History.MD`
2. Identify KDS 1 and KDS 2 sections (preserve unchanged)
3. Extract CORTEX evolution section (after "## 🧠 The Transformation: Knowledge Delivery System")
4. Update with latest:
   - Implementation progress (69% complete, Phase 5 status)
   - Recent milestones (ambient capture, token optimization, etc.)
   - Current metrics (455 tests, 97.2% token reduction)
5. Preserve narrative style (same tone as KDS sections)
6. Write updated History.md

**Inputs:**
- `feature_inventory` (from Module 1)
- `implementation_status` (from Module 1)

**Outputs:**
- `history_doc_path` (Path)
- `cortex_section_updated` (bool)
- `kds_sections_preserved` (bool)

**Estimated Effort:** 1 hour (module exists, just needs refinement)

---

### Module 7: File Relocation Module

**File:** `src/operations/modules/relocate_story_files_module.py`

**Purpose:** Move Ancient-Rules.md and CORTEX-FEATURES.md to docs/story/CORTEX-STORY/

**Responsibilities:**
1. Check if files exist in original locations:
   - Search for `Ancient-Rules.md` (may be in multiple places)
   - Search for `CORTEX-FEATURES.md` (may be in multiple places)
2. Move to `docs/story/CORTEX-STORY/`
3. Update any references in other files (prompts, docs, etc.)
4. Create backup before moving (safety)

**Inputs:**
- `project_root` (Path)

**Outputs:**
- `files_relocated` (List[Path])
- `references_updated` (List[Path])

**Estimated Effort:** 1 hour

---

## 🔄 Integration into doc_refresh_plugin.py

**Changes Required:**

1. **Add configuration option for refresh mode:**
   ```python
   # In plugin config_schema:
   "story_refresh_mode": {
       "type": "string",
       "description": "Story refresh mode: 'auto', 'generate-from-scratch', or 'update-in-place'",
       "enum": ["auto", "generate-from-scratch", "update-in-place"],
       "default": "auto"
   },
   "force_full_regeneration": {
       "type": "boolean",
       "description": "Force full regeneration even if changes are minor",
       "default": False
   },
   "change_magnitude_threshold": {
       "type": "number",
       "description": "Change magnitude threshold for auto-detection (0.0-1.0, default 0.20 = 20%)",
       "default": 0.20,
       "minimum": 0.0,
       "maximum": 1.0
   }
   ```

2. **Add new module imports:**
   ```python
   from src.operations.modules.evaluate_cortex_architecture_module import EvaluateCortexArchitectureModule
   from src.operations.modules.generate_story_chapters_module import GenerateStoryChaptersModule
   from src.operations.modules.collapse_story_chapters_module import CollapseStoryChaptersModule
   from src.operations.modules.generate_technical_cortex_doc_module import GenerateTechnicalCortexDocModule
   from src.operations.modules.generate_image_prompts_doc_module import GenerateImagePromptsDocModule
   from src.operations.modules.relocate_story_files_module import RelocateStoryFilesModule
   ```

3. **Update `_refresh_story_doc()` method (MODE-AWARE):**
   ```python
   def _refresh_story_doc(self, file_path: Path, design_context: Dict[str, Any]) -> Dict[str, Any]:
       """Refresh story with mode-aware regeneration workflow"""
       
       # Step 1: Evaluate CORTEX architecture + determine mode
       evaluator = EvaluateCortexArchitectureModule()
       eval_result = evaluator.execute({
           "project_root": self.project_root,
           "refresh_mode": self.config.get("story_refresh_mode", "auto"),
           "change_magnitude_threshold": self.config.get("change_magnitude_threshold", 0.20)
       })
       
       # Override mode if force_full_regeneration is set
       refresh_mode = eval_result.data["recommended_mode"]
       if self.config.get("force_full_regeneration", False):
           refresh_mode = "generate-from-scratch"
           logger.info("Force full regeneration enabled - using generate-from-scratch mode")
       
       logger.info(f"Story refresh mode: {refresh_mode}")
       logger.info(f"Mode rationale: {eval_result.data['mode_rationale']}")
       logger.info(f"Change magnitude: {eval_result.data['change_magnitude']:.1%}")
       
       # Step 2: Generate/update detailed chapters (MODE-AWARE)
       chapter_gen = GenerateStoryChaptersModule()
       chapters_result = chapter_gen.execute({
           "feature_inventory": eval_result.data["feature_inventory"],
           "project_root": self.project_root,
           "refresh_mode": refresh_mode,
           "changes_since_last_refresh": eval_result.data["changes_since_last_refresh"]
       })
       
       # Step 3: Collapse chapters into THE-AWAKENING-OF-CORTEX.md
       collapser = CollapseStoryChaptersModule()
       collapse_result = collapser.execute({
           "chapters": chapters_result.data.get("chapters_generated", []) + 
                      chapters_result.data.get("chapters_updated", []),
           "project_root": self.project_root,
           "refresh_mode": refresh_mode
       })
       
       # Step 4: Regenerate supporting files (MODE-AWARE)
       tech_doc_gen = GenerateTechnicalCortexDocModule()
       tech_result = tech_doc_gen.execute({
           "feature_inventory": eval_result.data["feature_inventory"],
           "project_root": self.project_root,
           "refresh_mode": refresh_mode,
           "changes_since_last_refresh": eval_result.data["changes_since_last_refresh"]
       })
       
       image_prompts_gen = GenerateImagePromptsDocModule()
       image_result = image_prompts_gen.execute({
           "architecture_patterns": eval_result.data["architecture_patterns"],
           "project_root": self.project_root,
           "refresh_mode": refresh_mode
       })
       
       history_gen = GenerateHistoryDocModule()
       history_result = history_gen.execute({
           "feature_inventory": eval_result.data["feature_inventory"],
           "project_root": self.project_root,
           "refresh_mode": refresh_mode,
           "changes_since_last_refresh": eval_result.data["changes_since_last_refresh"]
       })
       
       # Step 5: Relocate files (only in generate-from-scratch mode)
       files_relocated = []
       if refresh_mode == "generate-from-scratch":
           relocator = RelocateStoryFilesModule()
           relocate_result = relocator.execute({"project_root": self.project_root})
           files_relocated = relocate_result.data["files_relocated"]
       
       return {
           "success": True,
           "refresh_mode": refresh_mode,
           "change_magnitude": eval_result.data["change_magnitude"],
           "mode_rationale": eval_result.data["mode_rationale"],
           "chapters_generated": len(chapters_result.data.get("chapters_generated", [])),
           "chapters_updated": len(chapters_result.data.get("chapters_updated", [])),
           "chapters_unchanged": len(chapters_result.data.get("chapters_unchanged", [])),
           "consolidated_story": collapse_result.data["consolidated_story_path"],
           "read_time_minutes": collapse_result.data["estimated_read_time_minutes"],
           "files_updated": [
               tech_result.data["technical_doc_path"],
               image_result.data["image_prompts_doc_path"],
               history_result.data["history_doc_path"]
           ],
           "files_relocated": files_relocated,
           "backups_created": chapters_result.data.get("backups_created", [])
       }
   ```

---

## 🧪 Testing Strategy

### Test Coverage Required

1. **Unit Tests (per module):**
   - `test_evaluate_cortex_architecture_module.py` (10-15 tests)
   - `test_generate_story_chapters_module.py` (20-25 tests)
   - `test_collapse_story_chapters_module.py` (15-20 tests)
   - `test_generate_technical_cortex_doc_module.py` (10-15 tests)
   - `test_generate_image_prompts_doc_module.py` (5-10 tests)
   - `test_relocate_story_files_module.py` (5-10 tests)

2. **Integration Tests:**
   - `test_story_refresh_integration.py` (10-15 tests)
     - End-to-end workflow test
     - File generation validation
     - Read time enforcement
     - Story-to-technical ratio validation
     - Preservation of KDS history

3. **Edge Cases:**
   - Missing CORTEX-UNIFIED-ARCHITECTURE.yaml
   - Existing chapter files (overwrite behavior)
   - Invalid feature inventory
   - Read time exceeding target (trimming logic)
   - Missing Ancient-Rules.md or CORTEX-FEATURES.md

**Total Estimated Tests:** 75-100 new tests

**Testing Effort:** 3-4 hours

---

## 📅 Implementation Timeline

### Phase 1: Module Development (10-13 hours)

1. **Module 1: Evaluator (with mode detection)** - 3 hours (was 2h, +1h for mode logic)
2. **Module 2: Chapter Generator (mode-aware)** - 6-8 hours (was 4-6h, +2h for update-in-place)
3. **Module 3: Collapser** - 2-3 hours
4. **Module 4: Technical Doc** - 2 hours
5. **Module 5: Image Prompts** - 1-2 hours
6. **Module 6: History Updater** - 1 hour (refinement)
7. **Module 7: File Relocator** - 1 hour

### Phase 2: Integration (2-3 hours)

1. Update `doc_refresh_plugin.py` with mode configuration
2. Wire up module dependencies (mode-aware)
3. Add error handling and logging
4. Add mode override options (force full regen)

### Phase 3: Testing (4-5 hours)

1. Write unit tests (per module)
   - Test both modes: generate-from-scratch AND update-in-place
   - Test mode auto-detection logic
   - Test change magnitude calculation
2. Write integration tests
   - End-to-end tests for both modes
   - Test mode switching scenarios
3. Test edge cases
   - No previous story (force generate-from-scratch)
   - Minor changes (force update-in-place)
   - Change magnitude at threshold boundary (19% vs 21%)
4. Validate output quality
   - Story quality in both modes
   - Preservation of custom edits (update-in-place)

### Phase 4: Validation & Documentation (1-2 hours)

1. Run full story refresh in both modes
2. Review generated chapters (narrative quality)
3. Verify 95:5 story-to-technical ratio
4. Validate read time (60-75 min target)
5. Test mode detection accuracy
6. Update documentation with mode usage guide

**Total Estimated Effort:** 17-23 hours (was 14-18 hours, +3-5h for dual-mode support)

---

## ✅ Success Criteria

1. **Mode Detection & Selection:**
   - ✅ Auto-detection works correctly (>20% change = full regen, <20% = update)
   - ✅ Manual mode override functions properly
   - ✅ Force full regeneration flag works
   - ✅ Change magnitude calculation accurate
   - ✅ Mode rationale clearly explained in logs

2. **Chapter Generation (Generate-From-Scratch):**
   - ✅ 9+ detailed chapter files created from scratch
   - ✅ Asif Codeinstein + Wizard of Oz narrative preserved
   - ✅ Funny, engaging tone maintained
   - ✅ 95% story / 5% technical ratio enforced
   - ✅ Backups created before overwriting

3. **Chapter Update (Update-In-Place):**
   - ✅ Only affected chapters updated
   - ✅ Existing narrative style preserved
   - ✅ New content merged seamlessly
   - ✅ Custom edits retained
   - ✅ Unchanged chapters left intact

4. **Consolidated Story:**
   - ✅ THE-AWAKENING-OF-CORTEX.md created/updated
   - ✅ Read time: 60-75 minutes (15,000-18,750 words)
   - ✅ Progressive recaps included
   - ✅ Smooth chapter transitions

5. **Supporting Files:**
   - ✅ Technical-CORTEX.md regenerated/updated (mode-aware)
   - ✅ Image-Prompts.md regenerated/updated (mode-aware)
   - ✅ History.md updated (CORTEX section only, KDS 1/2 preserved)
   - ✅ Ancient-Rules.md and CORTEX-FEATURES.md moved to docs/story/CORTEX-STORY/

6. **Quality:**
   - ✅ 100-125 tests passing (increased from 75-100 for dual-mode coverage)
   - ✅ No regressions in existing functionality
   - ✅ Error handling for edge cases (both modes)
   - ✅ Comprehensive logging for debugging
   - ✅ Mode usage documented clearly

---

## 🚨 Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Chapter generation takes too long (>8 hours) | HIGH | MEDIUM | Use templates and structured prompts, parallelize where possible |
| Story-to-technical ratio hard to enforce | MEDIUM | HIGH | Create validation function, sample random paragraphs for ratio check |
| Read time optimization conflicts with story quality | HIGH | MEDIUM | Allow manual override, provide "trim suggestions" instead of auto-trim |
| Existing chapters overwritten (data loss) | HIGH | LOW | Create .backups/ folder, timestamp backups before overwrite |
| CORTEX-UNIFIED-ARCHITECTURE.yaml parsing issues | MEDIUM | LOW | Validate YAML structure first, fail gracefully with error message |
| Ancient-Rules.md / CORTEX-FEATURES.md not found | LOW | MEDIUM | Search multiple locations, prompt user if not found |
| **Mode auto-detection incorrect** | **HIGH** | **MEDIUM** | **Allow manual override, log mode decision clearly, test threshold values** |
| **Update-in-place breaks narrative flow** | **MEDIUM** | **MEDIUM** | **Validate transitions after merge, provide diff for review before commit** |
| **Change magnitude calculation inaccurate** | **MEDIUM** | **LOW** | **Weight changes by importance (new tier > test count), allow threshold tuning** |
| **Custom edits lost in update-in-place** | **HIGH** | **LOW** | **Parse existing content carefully, merge at section level (not line level)** |

---

## 📚 Reference Documents

- **Architecture Source:** `cortex-brain/CORTEX-UNIFIED-ARCHITECTURE.yaml`
- **Existing Plugin:** `src/plugins/doc_refresh_plugin.py`
- **Existing Modules:** `src/operations/modules/`
- **Story Templates:** `docs/story/CORTEX-STORY/{01-09}-*.md` (existing chapters for style reference)
- **Consolidated Story:** `docs/story/CORTEX-STORY/THE-AWAKENING-OF-CORTEX.md` (intro to preserve)
- **History:** `docs/story/CORTEX-STORY/History.MD` (KDS 1/2 sections to preserve)

---

---

## 📖 Mode Usage Guide

### When to Use Each Mode

#### Use GENERATE-FROM-SCRATCH When:
- ✅ Adding a new brain tier (e.g., Tier 4)
- ✅ Adding multiple new agents (e.g., 3+ new specialists)
- ✅ Major architectural refactor (>20% of system changed)
- ✅ First-time story generation
- ✅ Story has drifted from reality (recommend every 3-6 months)
- ✅ You want to completely rebuild narrative based on current state

**Example Command:**
```bash
# Natural language
refresh story --mode=generate-from-scratch

# Or with force flag
refresh story --force-full-regen
```

**What Happens:**
- All 9+ chapters regenerated from CORTEX-UNIFIED-ARCHITECTURE.yaml
- Existing chapters backed up to `.backups/` with timestamp
- New narrative created reflecting current architecture
- All supporting files (Technical-CORTEX.md, etc.) fully regenerated

**Expected Duration:** 15-25 minutes (AI generation time)

---

#### Use UPDATE-IN-PLACE When:
- ✅ Implementation progress only (tests passing, modules completed)
- ✅ Bug fixes or minor improvements
- ✅ Adding 1-2 new plugins
- ✅ Documentation updates
- ✅ Minor feature additions (<20% change)
- ✅ You want to preserve custom narrative edits

**Example Command:**
```bash
# Natural language (auto-detects)
refresh story

# Or explicit mode
refresh story --mode=update-in-place
```

**What Happens:**
- Only affected chapters updated (e.g., if Tier 1 changed, only `02-first-memory.md` updated)
- Existing narrative preserved and merged with new content
- Unchanged chapters left intact
- Supporting files updated incrementally

**Expected Duration:** 3-8 minutes (fewer chapters, merge logic)

---

#### Use AUTO-DETECT When:
- ✅ Unsure which mode to use
- ✅ Regular scheduled refreshes
- ✅ CI/CD pipeline integration
- ✅ Want system to decide based on change magnitude

**Example Command:**
```bash
# Natural language (default)
refresh story

# Or explicit auto
refresh story --mode=auto
```

**What Happens:**
- System calculates change magnitude (% of system affected)
- If >20% changed: uses GENERATE-FROM-SCRATCH
- If <20% changed: uses UPDATE-IN-PLACE
- Mode decision logged with rationale

**Expected Duration:** Varies based on detected mode

---

### Configuration Options

Add to `cortex.config.json` or plugin config:

```json
{
  "doc_refresh_plugin": {
    "story_refresh_mode": "auto",  // "auto", "generate-from-scratch", "update-in-place"
    "force_full_regeneration": false,  // Override auto-detection
    "change_magnitude_threshold": 0.20,  // 20% threshold for auto-detection
    "backup_before_refresh": true,  // Always create backups
    "trim_content_on_exceed": true,  // Trim if read time exceeds target
    "awakening_story_target_minutes": 60  // Target read time (60-75 min)
  }
}
```

---

### Example Scenarios

#### Scenario 1: Added 50 New Tests (Minor Change)
**User Action:** `refresh story`

**System Decision:**
```
🔍 Analyzing changes...
  - Tests added: 50 (impact: 5%)
  - Architecture changed: 0%
  - New components: 0
  
📊 Change Magnitude: 5% (< 20% threshold)
✅ Mode Selected: UPDATE-IN-PLACE

Rationale: Implementation progress only, no architectural changes.
Chapters affected: ALL (test metrics updated)
Estimated duration: 3 minutes
```

---

#### Scenario 2: Added New Agent (Moderate Change)
**User Action:** `refresh story`

**System Decision:**
```
🔍 Analyzing changes...
  - New agent added: "Code Reviewer Agent"
  - Architecture changed: 10%
  - Tests added: 25
  
📊 Change Magnitude: 18% (< 20% threshold)
✅ Mode Selected: UPDATE-IN-PLACE

Rationale: Single agent addition below threshold.
Chapters affected: 04-left-brain.md, 06-corpus-callosum.md
Estimated duration: 5 minutes
```

---

#### Scenario 3: Added Tier 4 + 3 New Agents (Major Change)
**User Action:** `refresh story`

**System Decision:**
```
🔍 Analyzing changes...
  - New brain tier added: "Tier 4 - Long-Term Memory"
  - New agents added: 3 (Memory Archiver, Pattern Synthesizer, Context Compressor)
  - Architecture changed: 35%
  - Tests added: 120
  
📊 Change Magnitude: 45% (> 20% threshold)
✅ Mode Selected: GENERATE-FROM-SCRATCH

Rationale: Major architectural change - new tier + multiple agents.
Chapters affected: ALL (full regeneration)
Estimated duration: 20 minutes
Creating backups...
```

---

#### Scenario 4: Force Full Regeneration (User Override)
**User Action:** `refresh story --force-full-regen`

**System Decision:**
```
🔍 Analyzing changes...
  - Tests added: 15 (impact: 3%)
  
📊 Change Magnitude: 3% (< 20% threshold)
⚠️  Force full regeneration enabled
✅ Mode Selected: GENERATE-FROM-SCRATCH (FORCED)

Rationale: User requested full regeneration.
Chapters affected: ALL (full regeneration)
Estimated duration: 20 minutes
Creating backups...
```

---

### Troubleshooting

**Q: Mode auto-detection chose wrong mode?**
```bash
# Override with explicit mode
refresh story --mode=generate-from-scratch

# Or adjust threshold in config
"change_magnitude_threshold": 0.15  # Lower threshold (15%)
```

**Q: Want to see what changed before refreshing?**
```bash
# Dry run mode (planned for future)
refresh story --dry-run

# Currently: Check logs after evaluation step
# Logs show: change_magnitude, mode_rationale, affected_chapters
```

**Q: Update-in-place broke narrative flow?**
```bash
# Restore from backup
# Backups located in: docs/story/CORTEX-STORY/.backups/

# Then force full regen
refresh story --force-full-regen
```

**Q: How to tune change magnitude calculation?**
```python
# Change weights in evaluate_cortex_architecture_module.py
change_weights = {
    "new_tier": 0.30,        # 30% impact per new tier
    "new_agent": 0.10,       # 10% impact per new agent
    "new_plugin": 0.05,      # 5% impact per new plugin
    "new_operation": 0.05,   # 5% impact per new operation
    "test_progress": 0.01,   # 1% impact per 100 tests
    "module_progress": 0.02  # 2% impact per module completed
}
```

---

## 🎯 Next Steps

1. **Review this plan** - Validate approach with stakeholders
2. **Prioritize modules** - Start with Module 1 (Evaluator) and Module 2 (Chapter Generator)
3. **Create module skeletons** - Set up file structure and interfaces
4. **Implement Phase 1** - Develop all 7 modules
5. **Test incrementally** - Write tests as modules are completed
6. **Integrate Phase 2** - Wire modules into doc_refresh_plugin.py
7. **Validate Phase 4** - Run full story refresh and review output

---

**Status:** Ready for implementation ✅  
**Design Phase:** Complete  
**Approval Required:** Yes (confirm dual-mode approach before proceeding)  
**Estimated Start Date:** 2025-11-11  
**Estimated Completion Date:** 2025-11-14 (3-4 days of focused work)

---

## 📋 Implementation Checklist

### Pre-Implementation
- [ ] Review and approve this design document
- [ ] Confirm dual-mode approach (generate-from-scratch vs update-in-place)
- [ ] Validate change magnitude thresholds (20% default)
- [ ] Decide on backup strategy (.backups/ folder structure)

### Module Development (7 modules)
- [ ] Module 1: CORTEX Architecture Evaluator (with mode detection) - 3h
- [ ] Module 2: Story Chapter Generator (mode-aware) - 6-8h
- [ ] Module 3: Story Chapter Collapser - 2-3h
- [ ] Module 4: Technical Documentation Generator - 2h
- [ ] Module 5: Image Prompts Generator - 1-2h
- [ ] Module 6: History Documentation Updater - 1h
- [ ] Module 7: File Relocation Module - 1h

### Integration
- [ ] Update doc_refresh_plugin.py with mode configuration
- [ ] Wire up module dependencies (mode-aware)
- [ ] Add error handling and logging
- [ ] Add mode override options (force full regen)

### Testing
- [ ] Write unit tests (100-125 tests for dual-mode coverage)
- [ ] Write integration tests (both modes)
- [ ] Test edge cases (mode switching, threshold boundaries)
- [ ] Validate output quality (narrative + technical balance)

### Validation
- [ ] Run full story refresh in generate-from-scratch mode
- [ ] Run full story refresh in update-in-place mode
- [ ] Review generated chapters (narrative quality)
- [ ] Verify 95:5 story-to-technical ratio
- [ ] Validate read time (60-75 min target)
- [ ] Test mode detection accuracy

### Documentation
- [ ] Update user guide with mode usage examples
- [ ] Document configuration options
- [ ] Create troubleshooting guide
- [ ] Update CORTEX.prompt.md with new commands

---

## 🎉 Summary

This implementation plan adds **intelligent dual-mode story refresh** to CORTEX:

**🆕 NEW CAPABILITIES:**
- ✅ **Auto-detect mode** based on change magnitude (>20% = full regen, <20% = update)
- ✅ **Generate-from-scratch** for major architectural changes
- ✅ **Update-in-place** for implementation progress (preserves custom edits)
- ✅ **Manual override** for force full regeneration
- ✅ **Backup system** to prevent data loss
- ✅ **Change-to-chapter mapping** for surgical updates

**BENEFITS:**
- 🚀 **80% faster refreshes** for minor changes (3-8 min vs 15-25 min)
- 📝 **Preserves custom edits** in update-in-place mode
- 🎯 **Intelligent mode selection** reduces manual decision-making
- 🔒 **Automatic backups** prevent accidental overwrites
- 📊 **Transparent decision-making** with clear rationale logs

**MODULES:** 7 new modules (17-23 hours total effort)  
**TESTS:** 100-125 tests for comprehensive dual-mode coverage  
**READY FOR:** Implementation approval and development kickoff

---

*Design Document Version: 2.0 (Dual-Mode Architecture)*  
*Last Updated: 2025-11-11*  
*Next Review: After implementation Phase 1 completion*

