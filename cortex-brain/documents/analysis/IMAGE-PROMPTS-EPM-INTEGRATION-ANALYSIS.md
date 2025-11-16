# Image Prompts EPM Integration Analysis

**Purpose:** Analyze and plan integration of image prompt generation into EPM Documentation Generator  
**Date:** November 16, 2025  
**Status:** Investigation Complete - Ready for Integration  
**Author:** Asif Hussain

---

## 🔍 Investigation Summary

### What Was Found

The **refresh-docs operation** (created November 15, 2025) includes a sophisticated **image prompt generation system** that creates Gemini-compatible prompts for technical system diagrams. This functionality was archived during the Phase B cleanup but represents valuable capability.

**Key Files Discovered:**
- `generate_image_prompts_module.py` - Basic prompt generator
- `generate_image_prompts_doc_module.py` - Advanced architecture-driven generator
- Git commits showing creation: `5a68987`, `f1d073c`, `3d6185e`

---

## 📊 Current Image Prompt System

### Features

**1. Architecture-Driven Generation**
- Extracts data from `feature_inventory` context
- Generates prompts based on actual CORTEX architecture
- Includes tiers, agents, plugins, memory flows

**2. Six Core Diagrams**

| Diagram | Purpose | Aspect Ratio | Complexity |
|---------|---------|--------------|------------|
| **Tier Architecture** | 4-tier brain system | 16:9 (landscape) | Medium |
| **Agent System** | 10 specialist agents (LEFT/RIGHT brain) | 1:1 (square) | High |
| **Plugin Architecture** | Hub-and-spoke extensibility | 1:1 (square) | Medium |
| **Memory Flow** | Conversation → Knowledge transformation | 16:9 (landscape) | High |
| **Agent Coordination** | Multi-agent collaboration sequence | 9:16 (portrait) | High |
| **Basement Scene** | Origin story illustration | 16:9 (landscape) | Creative |

**3. Style Guide**
- Consistent color palette (purple, blue, green, orange)
- Tier-specific colors for visual consistency
- Typography guidelines
- Layout conventions

**4. Gemini Optimization**
- Single-paragraph prompts (Gemini's preferred format)
- Technical specifications embedded
- Style directives included
- Clear visual requirements

---

## 🎯 Integration Plan

### Goal
Include image prompt generation in the **EPM Documentation Generator** (`src/epm/doc_generator.py`) as an optional stage.

### Approach

**Phase 1: Module Creation (1-2 hours)**
1. Create `src/epm/modules/image_prompt_generator.py`
2. Extract logic from archived modules
3. Adapt to EPM architecture (follows EPM patterns)
4. Add to EPM module registry

**Phase 2: Integration (30 minutes)**
1. Update `doc_generator.py` to include image prompts stage
2. Add configuration option in `page-definitions.yaml`
3. Wire into 6-stage pipeline (add as Stage 7 or optional)

**Phase 3: Configuration (15 minutes)**
1. Add section to `cortex-brain/doc-generation-config/page-definitions.yaml`
2. Define output paths and settings
3. Make optional (enabled via profile)

**Phase 4: Testing (30 minutes)**
1. Run EPM doc generator with image prompts enabled
2. Verify output structure
3. Validate Gemini compatibility

---

## 🏗️ Proposed Architecture

### New Module Structure

```
src/epm/modules/
├── validation_engine.py
├── cleanup_manager.py
├── diagram_generator.py
├── page_generator.py
├── cross_reference_builder.py
└── image_prompt_generator.py  # NEW
```

### Module Interface

```python
class ImagePromptGenerator:
    """
    Generate Gemini-compatible image prompts for CORTEX architecture.
    
    Integrates with EPM pipeline to create visual system documentation.
    """
    
    def __init__(self, root_path: Path, dry_run: bool = False):
        self.root_path = root_path
        self.dry_run = dry_run
    
    def generate_prompts(
        self, 
        architecture_data: Dict,
        output_path: Path
    ) -> Dict:
        """
        Generate image prompts document.
        
        Args:
            architecture_data: Extracted from capabilities.yaml + module_definitions.yaml
            output_path: Where to write Image-Prompts.md
        
        Returns:
            Generation report with paths, prompt count, validation
        """
```

### Pipeline Integration

**Current EPM Pipeline (6 stages):**
1. Pre-Flight Validation
2. Destructive Cleanup
3. Diagram Generation (Mermaid)
4. Page Generation
5. Cross-Reference & Navigation
6. Post-Generation Validation

**Proposed Integration:**

**Option A: Add as Stage 7 (Sequential)**
```
Stage 7: Image Prompt Generation
   ├─ Extract architecture data
   ├─ Generate 6 diagram prompts
   ├─ Write to docs/assets/image-prompts/
   └─ Update MkDocs navigation
```

**Option B: Include in Stage 3 (Parallel with Mermaid)**
```
Stage 3: Visual Asset Generation
   ├─ Mermaid Diagrams (existing)
   └─ Image Prompts (NEW)
```

**Recommendation:** Option B (parallel execution, semantic grouping)

---

## 📝 Configuration Schema

Add to `page-definitions.yaml`:

```yaml
# Image Prompt Generation Settings
image_prompts:
  enabled: true  # Enable/disable image prompt generation
  output_path: docs/assets/image-prompts/
  
  # Diagram configuration
  diagrams:
    - name: "Tier Architecture"
      enabled: true
      aspect_ratio: "16:9"
      complexity: "medium"
    
    - name: "Agent System"
      enabled: true
      aspect_ratio: "1:1"
      complexity: "high"
    
    - name: "Plugin Architecture"
      enabled: true
      aspect_ratio: "1:1"
      complexity: "medium"
    
    - name: "Memory Flow"
      enabled: true
      aspect_ratio: "16:9"
      complexity: "high"
    
    - name: "Agent Coordination"
      enabled: true
      aspect_ratio: "9:16"
      complexity: "high"
    
    - name: "Basement Scene"
      enabled: false  # Optional narrative scene
      aspect_ratio: "16:9"
      complexity: "creative"
  
  # Style settings
  style:
    color_palette:
      tier0: "#6B46C1"  # Deep Purple
      tier1: "#3B82F6"  # Bright Blue
      tier2: "#10B981"  # Emerald Green
      tier3: "#F59E0B"  # Warm Orange
    
    font_family: "Sans-serif"
    layout_direction: "top-to-bottom"
  
  # Output settings
  output_format: "markdown"
  include_usage_instructions: true
  include_style_guide: true
  
  # MkDocs integration
  add_to_navigation: true
  nav_section: "Visual Assets"
```

---

## 🔄 Data Flow

### Architecture Data Extraction

**Source Files:**
- `cortex-brain/capabilities.yaml` → Tiers, features
- `cortex-brain/module-definitions.yaml` → Agents, modules
- `package.json` / `setup.py` → Plugins

**Extraction Logic:**
```python
def extract_architecture_data(root_path: Path) -> Dict:
    """Extract architecture data for image prompt generation."""
    
    # Load capabilities (tiers, features)
    capabilities = load_yaml(root_path / "cortex-brain/capabilities.yaml")
    
    # Load module definitions (agents, operations)
    modules = load_yaml(root_path / "cortex-brain/module-definitions.yaml")
    
    # Extract structure
    return {
        "tiers": capabilities.get("tiers", []),
        "agents": modules.get("agents", []),
        "plugins": discover_plugins(root_path),
        "version": capabilities.get("version", "2.0"),
        "timestamp": datetime.now().isoformat()
    }
```

### Prompt Generation Pipeline

```
Extract Data → Generate Style Guide → Generate Tier Prompt → 
Generate Agent Prompt → Generate Plugin Prompt → Generate Flow Prompt → 
Generate Coordination Prompt → (Optional) Basement Scene → 
Write File → Validate Output
```

---

## 🎨 Output Structure

### Generated File: `docs/assets/image-prompts/Image-Prompts.md`

**Contents:**
1. **Header** - Title, version, generation date
2. **Style Guide** - Color palette, typography, layout conventions
3. **Diagram 1** - Tier Architecture (with Gemini prompt)
4. **Diagram 2** - Agent System (with Gemini prompt)
5. **Diagram 3** - Plugin Architecture (with Gemini prompt)
6. **Diagram 4** - Memory Flow (with Gemini prompt)
7. **Diagram 5** - Agent Coordination (with Gemini prompt)
8. **Diagram 6** - Basement Scene (optional, with Gemini prompt)
9. **Usage Instructions** - How to use prompts with Gemini
10. **Footer** - Related docs, settings

### Example Prompt Format

```markdown
## 📊 Diagram 1: The 4-Tier Brain Architecture

**Prompt for Gemini:**

\```
Create a vertical architecture diagram showing CORTEX's 4-tier brain system:

- **Tier 0**: Instinct (YAML governance rules)
- **Tier 1**: Working Memory (SQLite conversations)
- **Tier 2**: Knowledge Graph (YAML patterns)
- **Tier 3**: Context Intelligence (SQLite metrics)

Visual requirements:
- Stack tiers vertically from bottom (Tier 0) to top (Tier 3)
- Each tier is a rectangular box with rounded corners
- Use the color palette: Tier 0 (purple), Tier 1 (blue), Tier 2 (green), Tier 3 (orange)
- Show upward arrows between tiers indicating data flow
- Label each tier with name and storage type
- Add small icons: Tier 0 (shield), Tier 1 (database), Tier 2 (graph), Tier 3 (chart)
- Style: Modern, technical, clean lines
- Format: Wide landscape (16:9 aspect ratio)
\```

**Expected output**: Vertical stack diagram with clear tier separation and data flow arrows.
```

---

## 📊 Benefits

### Why Include This in EPM?

**1. Complete Documentation**
- Text documentation alone is insufficient for complex systems
- Visual diagrams enhance understanding
- Gemini prompts enable rapid visual iteration

**2. Architecture Consistency**
- Generated from actual CORTEX structure
- Always reflects current implementation
- No manual diagram maintenance

**3. Onboarding Value**
- New users understand system faster with visuals
- Diagrams complement written documentation
- Reduces "explain the architecture" questions

**4. Marketing & Presentation**
- Professional diagrams for presentations
- Blog post illustrations
- GitHub README visuals
- Conference talks

**5. Living Documentation**
- Regenerate when architecture changes
- Version-controlled prompts
- Audit trail of architectural evolution

---

## ⚠️ Implementation Considerations

### Challenges

**1. Data Extraction**
- Need reliable parsing of capabilities.yaml
- Agent discovery from multiple sources
- Plugin detection logic

**2. Prompt Quality**
- Gemini prompt optimization is iterative
- May need tweaking for best results
- Style consistency requires careful formatting

**3. Optional Feature**
- Must not break existing EPM pipeline
- Should be easily disabled
- Performance impact minimal

**4. Output Location**
- Coordinate with existing docs structure
- MkDocs navigation integration
- Asset organization

### Solutions

**1. Robust Data Extraction**
```python
def safe_extract(yaml_path: Path, key: str, default: Any) -> Any:
    """Safely extract data with fallback."""
    try:
        data = load_yaml(yaml_path)
        return data.get(key, default)
    except Exception as e:
        logger.warning(f"Failed to extract {key}: {e}")
        return default
```

**2. Configurable Prompts**
- Store prompt templates separately
- Allow customization without code changes
- Validate generated prompts before writing

**3. Profile-Based Activation**
```python
# Only run if profile includes image_prompts
if context.get('profile') == 'comprehensive' or context.get('generate_image_prompts'):
    image_prompt_result = self.image_prompt_generator.generate(...)
```

**4. Validation**
```python
def validate_prompts(content: str) -> List[str]:
    """Validate generated prompts."""
    issues = []
    
    if len(content) < 1000:
        issues.append("Prompt content too short")
    
    if not re.search(r'Diagram \d+:', content):
        issues.append("Missing diagram sections")
    
    if not re.search(r'Visual requirements:', content):
        issues.append("Missing visual requirements")
    
    return issues
```

---

## 🚀 Execution Plan

### Implementation Steps

**Step 1: Extract Module Code (30 min)**
- Copy logic from archived `generate_image_prompts_doc_module.py`
- Adapt to EPM architecture patterns
- Remove dependencies on old operation framework

**Step 2: Create EPM Module (45 min)**
- File: `src/epm/modules/image_prompt_generator.py`
- Implement EPM-compatible interface
- Add error handling and validation
- Include dry-run mode support

**Step 3: Update EPM Orchestrator (30 min)**
- File: `src/epm/doc_generator.py`
- Add Stage 7 or integrate into Stage 3
- Wire configuration
- Add to execution pipeline

**Step 4: Configuration (15 min)**
- Update `page-definitions.yaml`
- Add image prompt settings
- Document configuration options

**Step 5: Testing (30 min)**
- Run with `--profile comprehensive`
- Verify output structure
- Test Gemini compatibility
- Validate MkDocs integration

**Step 6: Documentation (15 min)**
- Update EPM README
- Add usage examples
- Document configuration options

**Total Estimated Time: 2.5 hours**

---

## ✅ Success Criteria

**Integration is successful when:**

1. ✅ EPM generates `Image-Prompts.md` without errors
2. ✅ Document includes all 6 diagrams (or configured subset)
3. ✅ Prompts are Gemini-compatible (single paragraph, clear specs)
4. ✅ Style guide included with consistent color palette
5. ✅ MkDocs navigation updated automatically
6. ✅ Optional (can be disabled without breaking pipeline)
7. ✅ Dry-run mode supported
8. ✅ Validation catches malformed output
9. ✅ Generation completes in <10 seconds
10. ✅ Rollback works correctly on error

---

## 📚 Related Documents

**Source Investigation:**
- Git commit: `5a68987` - "feat(docs): Major documentation restructure with EPM doc generator"
- Archived module: `cortex-brain/archives/.../generate_image_prompts_doc_module.py`

**EPM Documentation:**
- `src/epm/doc_generator.py` - Main orchestrator
- `cortex-brain/doc-generation-config/page-definitions.yaml` - Configuration
- `docs/operations/entry-point-modules.md` - EPM guide

**Image Prompt Examples:**
- See archived docs-backup folders for generated examples
- Check git history for commit `f1d073c` for full structure

---

## 🎯 Next Steps

**To proceed with integration:**

1. **Approve this analysis**
   - Review proposed architecture
   - Confirm integration approach
   - Validate success criteria

2. **Execute implementation**
   - Follow 6-step execution plan
   - Track time per step
   - Document issues encountered

3. **Test thoroughly**
   - Generate with EPM
   - Paste prompts into Gemini
   - Verify diagram quality
   - Check MkDocs rendering

4. **Document & Deploy**
   - Update EPM documentation
   - Add to operations guide
   - Commit to CORTEX-3.0 branch

---

**Analysis Complete:** Ready for integration decision

**Recommendation:** ✅ **PROCEED** - High value feature, low implementation risk, clear path forward

**Estimated ROI:**
- Implementation: 2.5 hours
- Value: Complete visual documentation system
- Maintenance: Minimal (architecture-driven, auto-generated)

---

**Author:** Asif Hussain  
**Date:** November 16, 2025  
**Status:** Investigation Complete - Awaiting Integration Approval  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.
