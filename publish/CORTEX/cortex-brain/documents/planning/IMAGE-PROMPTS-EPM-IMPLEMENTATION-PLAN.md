# Image Prompts EPM Integration - Implementation Plan

**Purpose:** Integrate image prompt generation into EPM "Generate Documentation" with diagram structure support  
**Author:** Asif Hussain  
**Date:** November 16, 2025  
**Status:** 🚀 READY FOR IMPLEMENTATION  
**Estimated Time:** 3.5 hours

---

## 📋 Executive Summary

This implementation plan consolidates:
1. **Image prompt generation** (from archived refresh-docs operation)
2. **Diagram structure** (from November 15 design: prompts, narratives, generated images)
3. **EPM integration** (single entry point for all documentation)
4. **MkDocs compatibility** (Git Pages publishing ready)

**Result:** One command generates all documentation including AI-ready image prompts organized in the proper structure for Copilot to merge generated images.

---

## 🎯 Requirements Summary

### User Requirements (From Today)
✅ Generate image prompts as part of "Generate Documentation" entry point  
✅ All documents in same location for MkDocs/Git Pages publishing  
✅ Include diagram structure from yesterday's design  
✅ Support Copilot image merging workflow

### Technical Requirements (From Analysis)
✅ EPM-compatible module following existing patterns  
✅ Dry-run support with validation  
✅ YAML-driven configuration  
✅ 6 diagram types (tier, agent, plugin, memory, coordination, basement)  
✅ Gemini-optimized prompts (single-paragraph format)

### Design Requirements (From November 15)
✅ Organized directory structure: `prompts/`, `narratives/`, `generated/`  
✅ Consistent naming: `##-diagram-name-[prompt|narrative|v1.png]`  
✅ Visual design standards (color palette, typography, layout principles)  
✅ Version tracking for generated images

---

## 🏗️ Architecture Design

### Integration Point: EPM Stage 3 (Parallel Execution)

**Why Stage 3?**
- Runs in parallel with diagram generation (Mermaid)
- Both create visual assets for documentation
- Similar execution patterns (generate files, validate output)
- No dependencies on page generation (Stage 4)

### Directory Structure

```
docs/
├── assets/
│   └── image-prompts/                  # EPM-generated prompts
│       ├── Image-Prompts.md            # Master document (all prompts)
│       ├── prompts/                    # Individual AI prompts
│       │   ├── 01-tier-architecture.md
│       │   ├── 02-agent-system.md
│       │   ├── 03-plugin-architecture.md
│       │   ├── 04-memory-flow.md
│       │   ├── 05-coordination.md
│       │   └── 06-basement-scene.md
│       ├── narratives/                 # Explanatory content
│       │   ├── 01-tier-architecture.md
│       │   ├── 02-agent-system.md
│       │   ├── 03-plugin-architecture.md
│       │   ├── 04-memory-flow.md
│       │   ├── 05-coordination.md
│       │   └── 06-basement-scene.md
│       └── generated/                  # Copilot-generated images
│           ├── .gitkeep
│           ├── 01-tier-architecture-v1.png
│           ├── 02-agent-system-v1.png
│           ├── 03-plugin-architecture-v1.png
│           ├── 04-memory-flow-v1.png
│           ├── 05-coordination-v1.png
│           └── 06-basement-scene-v1.png
├── images/                             # Other documentation images
│   └── diagrams/
│       └── architectural/
└── story/                              # CORTEX story documentation
```

**Key Design Decisions:**
- `docs/assets/image-prompts/` - MkDocs-compatible location
- `prompts/` - Individual files for easy Copilot workflow
- `narratives/` - Paired explanations for each diagram
- `generated/` - Reserved for Copilot-created images
- `Image-Prompts.md` - Master document linking all prompts

---

## 📦 Module Implementation

### File: `src/epm/modules/image_prompt_generator.py`

**Class:** `ImagePromptGenerator(BaseEPMModule)`

**Key Methods:**
```python
def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
    """Generate image prompts with diagram structure support"""
    
def _generate_master_document(self) -> str:
    """Create Image-Prompts.md with all prompts"""
    
def _generate_individual_prompt(self, diagram_type: str) -> str:
    """Create individual prompt file in prompts/"""
    
def _generate_narrative(self, diagram_type: str) -> str:
    """Create explanatory narrative in narratives/"""
    
def _create_directory_structure(self) -> None:
    """Set up prompts/, narratives/, generated/ folders"""
    
def _generate_tier_diagram_prompt(self) -> str:
    """Tier 0-3 architecture diagram"""
    
def _generate_agent_diagram_prompt(self) -> str:
    """10 specialist agents (LEFT/RIGHT brain)"""
    
def _generate_plugin_diagram_prompt(self) -> str:
    """Hub-and-spoke plugin system"""
    
def _generate_memory_flow_prompt(self) -> str:
    """Conversation → Pattern → Context"""
    
def _generate_coordination_prompt(self) -> str:
    """Multi-agent collaboration sequence"""
    
def _generate_basement_scene_prompt(self) -> str:
    """Origin story illustration"""
```

**Data Sources:**
- `cortex-brain/capabilities.yaml` (tier definitions)
- `cortex-brain/module-definitions.yaml` (agent specifications)
- `cortex-brain/plugin-system.yaml` (plugin architecture)
- Feature inventory context (from EPM)

---

## ⚙️ Configuration Schema

### File: `cortex-brain/doc-generation-config/page-definitions.yaml`

```yaml
image_prompts:
  enabled: true
  output_path: "docs/assets/image-prompts"
  
  master_document:
    filename: "Image-Prompts.md"
    title: "CORTEX Image Generation Prompts"
    description: "AI-ready prompts for generating CORTEX architecture diagrams"
    
  structure:
    prompts_dir: "prompts"           # Individual AI prompts
    narratives_dir: "narratives"     # Explanatory content
    generated_dir: "generated"       # Copilot-generated images
    
  diagrams:
    - id: "01-tier-architecture"
      name: "Brain Tiers Architecture"
      type: "architecture"
      aspect_ratio: "16:9"
      priority: "critical"
      description: "4-tier memory system (Tier 0-3)"
      
    - id: "02-agent-system"
      name: "Dual-Hemisphere Agent System"
      type: "architecture"
      aspect_ratio: "1:1"
      priority: "critical"
      description: "10 specialist agents (LEFT/RIGHT brain)"
      
    - id: "03-plugin-architecture"
      name: "Plugin Architecture"
      type: "architecture"
      aspect_ratio: "1:1"
      priority: "high"
      description: "Hub-and-spoke zero-footprint plugins"
      
    - id: "04-memory-flow"
      name: "Memory Flow Diagram"
      type: "process"
      aspect_ratio: "16:9"
      priority: "high"
      description: "Conversation → Pattern → Context lifecycle"
      
    - id: "05-coordination"
      name: "Agent Coordination"
      type: "sequence"
      aspect_ratio: "9:16"
      priority: "medium"
      description: "Multi-agent collaboration workflow"
      
    - id: "06-basement-scene"
      name: "Basement Scene (Origin Story)"
      type: "narrative"
      aspect_ratio: "16:9"
      priority: "medium"
      description: "Asif in basement with code and coffee"
      
  visual_style:
    color_palette:
      tier0: "#6B46C1"    # Deep Purple (Instinct)
      tier1: "#3B82F6"    # Bright Blue (Working Memory)
      tier2: "#10B981"    # Emerald Green (Knowledge)
      tier3: "#F59E0B"    # Warm Orange (Context)
      primary: "#2E86AB"  # CORTEX brand blue
      accent: "#F77F00"   # Warning orange
      neutral: "#6C757D"  # Supporting gray
      
    typography:
      headings: "Inter Bold, 18-24pt"
      body: "Inter Regular, 12-14pt"
      code: "JetBrains Mono, 11pt"
      
    layout_principles:
      - "Left-to-right for processes"
      - "Top-to-bottom for hierarchies"
      - "Circular layouts for cycles"
      - "Grid-based alignment"
      
  ai_generation:
    target: "Google Gemini"
    format: "single_paragraph"
    style: "gothic cyberpunk technical aesthetic"
    emphasis: "Clear labels, clean architecture, professional"
```

---

## 🔄 EPM Pipeline Integration

### Modified: `src/epm/doc_generator.py`

**Stage 3 Enhancement:**
```python
# Stage 3: Visual Asset Generation (Parallel)
async def _stage3_visual_assets(self):
    """Generate diagrams and image prompts in parallel"""
    
    tasks = []
    
    # Existing: Mermaid diagram generation
    if self.config.get('diagrams', {}).get('enabled'):
        tasks.append(self.diagram_generator.execute())
    
    # NEW: Image prompt generation
    if self.config.get('image_prompts', {}).get('enabled'):
        tasks.append(self.image_prompt_generator.execute())
    
    # Execute in parallel
    results = await asyncio.gather(*tasks)
    
    return {
        'stage': 3,
        'name': 'Visual Asset Generation',
        'results': results,
        'status': 'complete'
    }
```

**Module Registration:**
```python
def __init__(self, config_path: str):
    # ... existing initialization ...
    
    # NEW: Register image prompt generator
    self.image_prompt_generator = ImagePromptGenerator(
        config=self.config,
        dry_run=self.dry_run
    )
```

---

## 📝 Output Structure

### Master Document: `Image-Prompts.md`

```markdown
# CORTEX Image Generation Prompts

**Purpose:** AI-ready prompts for generating CORTEX architecture diagrams  
**Target:** Google Gemini image generation  
**Style:** Gothic cyberpunk technical aesthetic with clean architecture  
**Date:** {{generated_date}}

---

## 🎨 Visual Style Guide

**Color Palette:**
- Tier 0 (Instinct): #6B46C1 (Deep Purple)
- Tier 1 (Working Memory): #3B82F6 (Bright Blue)
- Tier 2 (Knowledge): #10B981 (Emerald Green)
- Tier 3 (Context): #F59E0B (Warm Orange)

**Typography:** Inter headings, JetBrains Mono for code

**Layout:** Clean, professional, grid-based alignment

---

## 📊 Diagram 1: Brain Tiers Architecture

**Aspect Ratio:** 16:9 landscape  
**Priority:** CRITICAL  
**File:** [01-tier-architecture.md](prompts/01-tier-architecture.md)  
**Narrative:** [Understanding the 4-Tier System](narratives/01-tier-architecture.md)  
**Generated Image:** `generated/01-tier-architecture-v1.png`

### Prompt

[Full single-paragraph Gemini-optimized prompt here]

---

[Repeat for diagrams 2-6]

---

## 🚀 Usage Workflow

1. **Review Prompts:** Read individual files in `prompts/` directory
2. **Generate Images:** Paste prompts into Google Gemini
3. **Save Images:** Store in `generated/` directory (format: `##-diagram-name-v1.png`)
4. **Read Narratives:** Understand context in `narratives/` directory
5. **Integrate Docs:** Reference images in MkDocs pages

---

**Generated by:** CORTEX EPM Documentation Generator  
**Version:** 2.0  
**Date:** {{timestamp}}
```

### Individual Prompt File: `prompts/01-tier-architecture.md`

```markdown
# Tier Architecture Diagram Prompt

**Diagram ID:** 01-tier-architecture  
**Aspect Ratio:** 16:9 landscape  
**Priority:** CRITICAL  
**Target:** Google Gemini

---

## Prompt

Create a professional diagram showing CORTEX's 4-tier memory architecture in a vertical stack layout. Tier 0 (Instinct) at the foundation in deep purple (#6B46C1) contains immutable governance rules displayed as hexagonal shields labeled "TDD Enforcement", "Definition of Ready", "Definition of Done", "Brain Protection" arranged in a fortress-like pattern. Tier 1 (Working Memory) above in bright blue (#3B82F6) shows a circular FIFO queue with 20 conversation slots, with 18 filled (gray) and 2 empty (white), arrows showing "Oldest In" and "New Conversation" flow, labeled "Last 20 Conversations" with "Performance: <50ms" metric. Tier 2 (Knowledge Graph) in emerald green (#10B981) displays an interconnected network of nodes representing patterns, workflows, and file relationships, with pulsing connections showing active learning, labeled "Pattern Learning" with "Confidence: 0.85" and "Performance: <150ms" metrics. Tier 3 (Context Intelligence) at top in warm orange (#F59E0B) shows git commit history as a timeline with file hotspots highlighted in red, code health metrics displayed as gauges (Coverage: 76%, Build Success: 97%), and session analytics as a productivity graph, labeled "Git Analysis & Session Metrics" with "Performance: <200ms" metric. Clean arrows flow upward showing data progression from instinct → memory → patterns → context. Use Inter Bold typography for tier labels (24pt), Inter Regular for descriptions (14pt), and JetBrains Mono for metrics (11pt). Include subtle gothic cyberpunk aesthetic with circuit board patterns in background, neon glow on connections, but maintain professional clean architecture suitable for technical documentation. Grid-based alignment, clear visual hierarchy, no clutter.

---

## Visual Elements Checklist

- [ ] 4-tier vertical stack layout
- [ ] Tier 0: Purple foundation with governance shields
- [ ] Tier 1: Blue circular FIFO queue (20 slots)
- [ ] Tier 2: Green knowledge graph network
- [ ] Tier 3: Orange git/session analytics
- [ ] Performance metrics visible (<50ms, <150ms, <200ms)
- [ ] Clean upward data flow arrows
- [ ] Gothic cyberpunk aesthetic (subtle)
- [ ] Professional typography (Inter + JetBrains Mono)
- [ ] Grid-based alignment

---

**Narrative:** See [narratives/01-tier-architecture.md](../narratives/01-tier-architecture.md)  
**Generated Image:** `../generated/01-tier-architecture-v1.png`
```

### Narrative File: `narratives/01-tier-architecture.md`

```markdown
# Understanding CORTEX's 4-Tier Brain Architecture

**Diagram:** 01-tier-architecture  
**Audience:** Developers, Solutions Architects  
**Complexity:** HIGH (Technical Detail)

---

## What This Diagram Shows

This diagram illustrates CORTEX's cognitive architecture modeled after the human brain's memory systems. Just like your brain has different types of memory (instinctive reflexes, working memory, long-term knowledge, contextual awareness), CORTEX implements four specialized tiers that work together to solve GitHub Copilot's amnesia problem.

---

## Tier Breakdown

### Tier 0: Instinct (Deep Purple Foundation)
**Purpose:** Immutable core principles that never change

Think of this as your brain's autonomic nervous system - the rules you can't override like breathing or blinking. CORTEX's Tier 0 contains fundamental principles:
- Test-Driven Development (RED → GREEN → REFACTOR)
- Definition of Ready (clear requirements before starting)
- Definition of Done (zero errors, zero warnings)
- Brain Protection (challenge risky changes to CORTEX core)

**Why Immutable?** These are the DNA of CORTEX. Changing them would fundamentally alter what CORTEX is.

**Storage:** `governance/rules.md` (never moves, never expires)

---

### Tier 1: Working Memory (Bright Blue FIFO Queue)
**Purpose:** Remember recent conversations (last 20)

This is CORTEX's solution to Copilot's "Make it purple" amnesia problem. When you say "Make it purple," CORTEX checks Tier 1 and remembers you were talking about a button 5 minutes ago.

**How It Works:**
- Stores last 20 conversations in chronological order
- FIFO queue: When conversation #21 starts, #1 gets archived
- Tracks entities: files mentioned, classes created, methods modified
- Performance target: <50ms query time (actual: 18ms ⚡)

**Storage:** SQLite database (`tier1/conversations.db`) + JSON Lines

**Real-World Example:**
```
You: "Add a pulse animation to the FAB button"
[CORTEX stores: FAB button, pulse animation, HostControlPanel.razor]

You: "Make it purple"
CORTEX: ✅ "Applying purple color to FAB button"
         (knows "it" = FAB button from 5 minutes ago)
```

---

### Tier 2: Knowledge Graph (Emerald Green Network)
**Purpose:** Learn patterns from past work

This is where CORTEX gets smarter with every project. It's like your brain's long-term memory that helps you recognize "I've done something similar before."

**What Gets Learned:**
- Intent patterns: "add a button" → PLAN intent (85% confidence)
- File relationships: `AuthService.cs` often modified with `AuthTests.cs` (78% co-modification)
- Workflow templates: invoice_export_workflow (94% success rate)
- Correction history: Prevent "wrong file" mistakes

**Pattern Decay:** Unused patterns lose confidence over time (5% per 30 days unused). Keeps knowledge fresh.

**Performance:** <150ms pattern search (actual: 92ms ⚡)

**Real-World Example:**
```
Week 1: You implement invoice export feature
        CORTEX learns: invoice_export_workflow pattern

Week 4: You need receipt export feature
        CORTEX: "This is similar to invoice export (85% match).
                Reuse same workflow?"
        Result: 60% faster delivery ⚡
```

---

### Tier 3: Context Intelligence (Warm Orange Analytics)
**Purpose:** Holistic view of your development process

This tier understands your project health and your own productivity patterns. It's like having a personal productivity coach.

**Analyzes:**
- Git commit velocity (how fast are you shipping?)
- File hotspots (which files change too often? unstable!)
- Code health metrics (test coverage, build success rate)
- Session productivity (when are you most effective?)

**Performance:** <200ms analysis (actual: 156ms ⚡)

**Proactive Warnings:**
```
⚠️ File Alert: HostControlPanel.razor is a hotspot (28% churn)
   Recommendation: Add extra testing before changes

✅ Optimal Time: 10am-12pm sessions have 94% success rate
   Current Time: 2:30pm (81% success historically)
   Suggestion: Schedule complex work for morning
```

---

## How The Tiers Work Together

**Scenario:** You're implementing user authentication

1. **Tier 0** enforces: Must have clear requirements (Definition of Ready)
2. **Tier 1** remembers: Your last conversation about AuthService.cs
3. **Tier 2** suggests: "Similar to invoice validation pattern (78% match)"
4. **Tier 3** warns: "AuthService.cs is a hotspot - add extra tests"

**Result:** Faster, safer, smarter development with continuous learning

---

## Key Takeaways

✅ **Tier 0:** DNA of CORTEX (never changes)  
✅ **Tier 1:** Recent memory (last 20 conversations)  
✅ **Tier 2:** Pattern learning (gets smarter over time)  
✅ **Tier 3:** Context awareness (project health + productivity)

**Performance:** All tiers exceed targets (18ms, 92ms, 156ms ⚡)  
**Storage:** Local-first (SQLite + YAML, no cloud dependencies)  
**Intelligence:** Modeled after human brain's memory systems

---

## For Leadership

**Executive Summary:** CORTEX implements a four-tier memory system that solves GitHub Copilot's amnesia problem, learns from past work, and provides proactive development guidance. Performance targets exceeded across all tiers with 97.2% token optimization achieved.

**Business Value:**
- Eliminates context repetition (saves developer time)
- Pattern reuse accelerates delivery (60% faster on similar features)
- Proactive warnings prevent bugs (fewer production issues)
- Continuous learning improves over time (no manual training needed)

---

**Related:**
- [Agent System Diagram](02-agent-system.md) - How agents use these tiers
- [Memory Flow Diagram](04-memory-flow.md) - Data lifecycle through tiers
- [Technical Reference](../../../prompts/shared/technical-reference.md) - API documentation

**Generated by:** CORTEX EPM Documentation Generator  
**Version:** 2.0  
**Date:** {{timestamp}}
```

---

## 🧪 Implementation Steps

### Step 1: Create Image Prompt Generator Module (1.5 hours)

**File:** `src/epm/modules/image_prompt_generator.py`

**Tasks:**
1. Copy logic from `cortex-brain/archives/obsolete-content-20251116_092210/generate_image_prompts_doc_module.py`
2. Adapt to EPM `BaseEPMModule` interface
3. Update data sources to use EPM feature inventory
4. Add directory structure creation (`prompts/`, `narratives/`, `generated/`)
5. Implement individual file generation (not just master document)
6. Add narrative generation for each diagram
7. Add dry-run support
8. Add validation (check required data exists)

**Success Criteria:**
- Module initializes without errors
- Dry-run generates file list (no actual writes)
- Live mode creates all files correctly
- Validation catches missing data

---

### Step 2: Integrate into EPM Pipeline (45 minutes)

**File:** `src/epm/doc_generator.py`

**Tasks:**
1. Import `ImagePromptGenerator`
2. Register in `__init__` method
3. Add to Stage 3 (parallel with diagram generation)
4. Wire configuration from `page-definitions.yaml`
5. Add error handling
6. Update execution summary

**Success Criteria:**
- EPM runs without errors (dry-run)
- Stage 3 shows both diagram + image prompt execution
- Configuration loads correctly
- Parallel execution works

---

### Step 3: Configuration Setup (30 minutes)

**File:** `cortex-brain/doc-generation-config/page-definitions.yaml`

**Tasks:**
1. Add `image_prompts` section (schema above)
2. Configure 6 diagram specifications
3. Set visual style guide
4. Define output paths
5. Set profiles (quick, standard, comprehensive)
6. Validate YAML syntax

**Success Criteria:**
- YAML validates without errors
- EPM loads configuration successfully
- All required fields present
- Profiles work correctly

---

### Step 4: Test Individual Module (30 minutes)

**Test File:** `tests/epm/modules/test_image_prompt_generator.py`

**Test Cases:**
1. Module initialization
2. Directory structure creation
3. Master document generation
4. Individual prompt file generation
5. Narrative file generation
6. Dry-run mode
7. Validation (missing data)
8. Error handling

**Success Criteria:**
- All tests pass
- Coverage ≥80%
- Dry-run produces expected output
- Validation catches errors

---

### Step 5: Integration Testing (45 minutes)

**Test Scenarios:**
1. Run EPM with `quick` profile (image prompts disabled)
2. Run EPM with `standard` profile (image prompts enabled)
3. Run EPM with `comprehensive` profile (all diagrams)
4. Verify output in `docs/assets/image-prompts/`
5. Check file structure matches specification
6. Validate MkDocs compatibility
7. Test Copilot workflow (paste prompt, generate image, save)

**Success Criteria:**
- All profiles execute successfully
- Output files in correct locations
- Directory structure matches design
- MkDocs can reference generated files
- Copilot can generate images from prompts

---

### Step 6: Documentation Updates (30 minutes)

**Files to Update:**
1. `README.md` - Add image prompt generation feature
2. `prompts/shared/operations-reference.md` - Update "Generate Documentation"
3. `docs/operations/generate-documentation.md` - Add usage examples
4. `cortex-brain/documents/planning/CORTEX-3.0-ROADMAP.yaml` - Mark complete

**Success Criteria:**
- Documentation reflects new capability
- Usage examples clear and complete
- Roadmap updated

---

## ✅ Success Criteria

### Functional Requirements
- ✅ Image prompts generated as part of EPM "Generate Documentation"
- ✅ All documents in `docs/` directory for MkDocs publishing
- ✅ Directory structure matches November 15 design (prompts, narratives, generated)
- ✅ 6 diagram types supported (tier, agent, plugin, memory, coordination, basement)
- ✅ Gemini-optimized single-paragraph prompts
- ✅ Individual prompt files for easy Copilot workflow
- ✅ Narratives paired with each diagram
- ✅ `generated/` folder ready for Copilot image output

### Technical Requirements
- ✅ EPM module follows existing patterns
- ✅ Dry-run mode supported
- ✅ YAML configuration driven
- ✅ Error handling and validation
- ✅ Performance targets met (<200ms generation)
- ✅ Test coverage ≥80%

### User Experience
- ✅ One command generates everything: `cortex generate documentation`
- ✅ Clear output showing what was generated
- ✅ Easy Copilot workflow: copy prompt → generate image → save
- ✅ Organized structure (no hunting for files)
- ✅ MkDocs can immediately reference generated prompts

### Documentation Quality
- ✅ Master document (`Image-Prompts.md`) comprehensive
- ✅ Individual prompts spelling-checked and technically accurate
- ✅ Narratives explain each diagram for both leadership and developers
- ✅ Visual style guide consistent with CORTEX brand
- ✅ Usage workflow clearly documented

---

## 🎯 Execution Plan

### Preparation (15 minutes)
1. Review archived image prompt module
2. Confirm EPM module patterns
3. Validate YAML schema
4. Set up test environment

### Implementation (3.5 hours)
1. **Step 1:** Create module (1.5 hours)
2. **Step 2:** Integrate into EPM (45 minutes)
3. **Step 3:** Configuration setup (30 minutes)
4. **Step 4:** Test module (30 minutes)
5. **Step 5:** Integration testing (45 minutes)
6. **Step 6:** Documentation (30 minutes)

### Validation (30 minutes)
1. Run full EPM generation (comprehensive profile)
2. Verify all files created correctly
3. Test Copilot image generation workflow
4. Validate MkDocs integration
5. Commit changes with semantic message

**Total Time:** 4 hours 15 minutes

---

## 🔄 Copilot Image Workflow (After Implementation)

### Step 1: Generate Documentation
```bash
cortex generate documentation --profile comprehensive
```

**Output:**
```
✅ Generated: docs/assets/image-prompts/Image-Prompts.md
✅ Generated: docs/assets/image-prompts/prompts/01-tier-architecture.md
✅ Generated: docs/assets/image-prompts/prompts/02-agent-system.md
... (6 prompts total)
✅ Generated: docs/assets/image-prompts/narratives/01-tier-architecture.md
... (6 narratives total)
✅ Created: docs/assets/image-prompts/generated/ (ready for images)
```

### Step 2: Generate Images with Copilot
1. Open `docs/assets/image-prompts/prompts/01-tier-architecture.md`
2. Copy single-paragraph prompt
3. Paste into Google Gemini (or GitHub Copilot with Gemini backend)
4. Generate image
5. Download as `01-tier-architecture-v1.png`
6. Save to `docs/assets/image-prompts/generated/`

### Step 3: Reference in MkDocs
```markdown
# Brain Architecture

CORTEX implements a 4-tier memory system:

![Brain Tiers Architecture](assets/image-prompts/generated/01-tier-architecture-v1.png)

*See [narrative](assets/image-prompts/narratives/01-tier-architecture.md) for explanation*
```

### Step 4: Iterate if Needed
- If image needs adjustments, update prompt in `prompts/` directory
- Re-generate with Copilot
- Save new version as `01-tier-architecture-v2.png`
- Update MkDocs reference

---

## 🚀 Benefits of This Implementation

### For Users
✅ **One Command:** All documentation generated together  
✅ **Organized:** Clear directory structure, easy to navigate  
✅ **Copilot-Friendly:** Individual prompt files ready to paste  
✅ **MkDocs-Ready:** All files in correct location for publishing

### For CORTEX
✅ **Consolidation:** No separate refresh-docs operation needed  
✅ **Consistency:** Image prompts follow EPM patterns  
✅ **Maintainability:** Configuration-driven (easy to add diagrams)  
✅ **Extensibility:** Easy to add more diagram types

### For Documentation
✅ **Complete:** Prompts + narratives + generated images in one place  
✅ **Professional:** Follows November 15 design standards  
✅ **Publishable:** Git Pages compatible out of the box  
✅ **Versioned:** Image versions tracked (v1, v2, etc.)

---

## 📊 Comparison: Before vs After

### Before This Implementation
```
❌ Image prompts in archived refresh-docs operation
❌ Separate workflow from EPM documentation generator
❌ No diagram structure (prompts, narratives, generated)
❌ Manual file organization required
❌ Scattered across multiple locations
```

### After This Implementation
```
✅ Image prompts integrated into EPM "Generate Documentation"
✅ Single workflow for all documentation
✅ Complete diagram structure (November 15 design)
✅ Automatic file organization
✅ All in docs/ directory for MkDocs
```

---

## 🔗 Related Documentation

| Document | Purpose |
|----------|---------|
| `IMAGE-PROMPTS-EPM-INTEGRATION-ANALYSIS.md` | Investigation findings (today) |
| `00-DIAGRAM-ORCHESTRATOR.md` | Diagram structure design (Nov 15) |
| `01-DIAGRAM-IDENTIFICATION.md` | Diagram requirements (Nov 15) |
| `src/epm/doc_generator.py` | EPM orchestrator (integration point) |
| `page-definitions.yaml` | EPM configuration (add image_prompts) |

---

## ✅ Approval Checklist

Before implementation begins:
- [ ] User has reviewed this implementation plan
- [ ] Estimated time (3.5 hours) is acceptable
- [ ] Diagram structure from November 15 is confirmed correct
- [ ] MkDocs output location (`docs/assets/image-prompts/`) approved
- [ ] Copilot image workflow makes sense
- [ ] Success criteria are clear and complete

**Ready to proceed?** Say "begin implementation" to start Step 1.

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary  
**Version:** 1.0  
**Status:** 🚀 READY FOR IMPLEMENTATION  
**Estimated Time:** 3.5 hours

---

*This implementation plan consolidates image prompt generation, diagram structure design, and EPM integration into a single unified documentation generation system.*
