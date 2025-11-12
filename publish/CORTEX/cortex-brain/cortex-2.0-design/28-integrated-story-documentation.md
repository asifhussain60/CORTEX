# CORTEX 2.0: Integrated Story Documentation System

**Document:** 28-integrated-story-documentation.md  
**Version:** 2.0.0-alpha  
**Created:** 2025-11-07  
**Status:** Design Phase  
**Component:** Documentation Refresh Plugin Enhancement

---

## 🎯 Purpose

Automatically generate and maintain a rich, integrated "Awakening of CORTEX" story that combines:
- Narrative storytelling (from `Awakening Of CORTEX.md`)
- Technical deep-dives (from `Technical-CORTEX.md`)
- Generated images (from `Image-Prompts.md` via Gemini)

**Goal:** Create a seamless reading experience where images and technical details are intelligently woven into the story narrative, organized into 5 Acts.

---

## 📋 Requirements

### User Requirements
1. **Intelligent Weaving** - Not sequential blocks; images and technical details flow naturally within narrative
2. **Image Matching** - Images generated from Gemini prompts automatically matched and embedded
3. **5-Act Structure** - Condense 11 chapters into 5 logical Acts (no content loss)
4. **Zero Manual Work** - Fully automated when "refresh documentation" is called
5. **Preservation** - Documentation refresh preserves 5-Act structure on updates

### Design Requirements
1. **Marker-Based System** - Source files annotated with placement markers
2. **Fuzzy Image Matching** - Match images by filename patterns, not exact names
3. **Graceful Degradation** - Handle missing images/technical sections elegantly
4. **Validation** - Report missing assets without breaking generation
5. **Admonition Styling** - Use Material Design admonitions for technical callouts

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│         Integrated Story Generation System                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Source Files (Annotated)                     │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │ Awakening Of CORTEX.md (WITH MARKERS)              │  │   │
│  │  │   <!-- ACT:1:START -->                             │  │   │
│  │  │   <!-- IMAGE:asifinstein-character -->             │  │   │
│  │  │   <!-- TECH:5-tier-memory -->                      │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │ Technical-CORTEX.md (WITH SECTION IDs)             │  │   │
│  │  │   <!-- ID:5-tier-memory -->                        │  │   │
│  │  │   ## 5-Tier Memory System                          │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │ images/image-mapping.yaml (CONFIGURATION)          │  │   │
│  │  │   marker: asifinstein-character                    │  │   │
│  │  │   patterns: [asifinstein*, mad*scientist*]         │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ↓                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         scripts/generate_integrated_story.py              │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │ 1. Parse source files                              │  │   │
│  │  │ 2. Load image mapping configuration                │  │   │
│  │  │ 3. Scan images/ folder for new files               │  │   │
│  │  │ 4. Fuzzy match images to markers                   │  │   │
│  │  │ 5. Extract technical sections by ID                │  │   │
│  │  │ 6. Process markers in story:                       │  │   │
│  │  │    - IMAGE: embed with caption                     │  │   │
│  │  │    - TECH: insert admonition callout               │  │   │
│  │  │    - ACT: create Act header                        │  │   │
│  │  │ 7. Generate integrated story                       │  │   │
│  │  │ 8. Validate (report missing assets)                │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ↓                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         docs/story/awakening-integrated.md                │   │
│  │                  (GENERATED OUTPUT)                       │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │ # ACT 1: THE AWAKENING                             │  │   │
│  │  │                                                     │  │   │
│  │  │ Story narrative flows...                           │  │   │
│  │  │                                                     │  │   │
│  │  │ ![Asifinstein](images/asifinstein-mad-scientist...) │  │   │
│  │  │                                                     │  │   │
│  │  │ !!! info "The Memory Problem"                      │  │   │
│  │  │     Technical explanation...                       │  │   │
│  │  │                                                     │  │   │
│  │  │ More story...                                      │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ↓                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │    Documentation Refresh Plugin (ENHANCED)                │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │ ON_DOC_REFRESH trigger:                            │  │   │
│  │  │   1. Run generate_integrated_story.py              │  │   │
│  │  │   2. Validate integrity                            │  │   │
│  │  │   3. Report status                                 │  │   │
│  │  │   4. Rebuild MkDocs site                           │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 File Structure

### Source Files (docs/story/CORTEX-STORY/)

```
docs/story/CORTEX-STORY/
├── Awakening Of CORTEX.md          ← Modified with markers
├── Technical-CORTEX.md             ← Modified with section IDs
├── Image-Prompts.md                ← Unchanged (reference only)
├── History.MD                      ← Unchanged (reference only)
├── images/
│   ├── image-mapping.yaml          ← NEW: Image configuration
│   ├── asifinstein-mad-scientist.png     (user adds after Gemini generation)
│   ├── copilot-pre-cortex.png           (user adds)
│   ├── cortex-1.0-awakened.png          (user adds)
│   └── ...
└── .backups/                       ← Existing backups
```

### Generated Output

```
docs/story/
├── awakening-integrated.md         ← GENERATED: Integrated story
└── integrated-story-status.md      ← GENERATED: Validation report
```

### Script

```
scripts/
└── generate_integrated_story.py    ← NEW: Generation script
```

---

## 🏷️ Marker System

### Story Markers (Awakening Of CORTEX.md)

#### Act Boundaries
```markdown
<!-- ACT:1:START -->
<!-- ACT:1:END -->
```

#### Image Markers
```markdown
<!-- IMAGE:asifinstein-character -->
```

#### Technical Markers
```markdown
<!-- TECH:5-tier-memory -->
```

### Example Annotated Story

```markdown
# The Awakening of CORTEX

<!-- ACT:1:START -->

## Intro: The Basement, the Madman, and the Brainless Beast

In a moldy basement somewhere in suburban New Jersey...

<!-- IMAGE:asifinstein-character -->

...surrounded by 47 coffee mugs in various states of decay. **Asifinstein** toiled endlessly.

A mad scientist by passion, software engineer by profession...

<!-- IMAGE:copilot-pre-cortex -->

But something was... off. Copilot had **no memory**. No judgment. No brain.

<!-- TECH:5-tier-memory -->

Ask it to build a login page? Done.  
Ask it five minutes later to add a logout?

> "Who are you again? Also, what's a page?"

<!-- ACT:1:END -->
```

### Technical Section IDs (Technical-CORTEX.md)

```markdown
<!-- ID:5-tier-memory -->
## 🗄️ 5-Tier Memory System

### Purpose
Enable CORTEX to maintain context across conversations...

[Technical content...]

<!-- END:5-tier-memory -->
```

---

## 📝 Image Mapping Configuration

### File: images/image-mapping.yaml

```yaml
# Image mapping configuration for integrated story generation

version: "1.0"
images:
  - marker: asifinstein-character
    prompt_title: "1. Asifinstein - The Mad Scientist"
    patterns:
      - "asifinstein*"
      - "mad*scientist*"
      - "character*1*"
    caption: "Asifinstein: The mad scientist in his natural habitat"
    act: 1
    placement: "after_paragraph_introducing_asifinstein"
    alt_text: "Cartoon illustration of Asifinstein, a mad scientist surrounded by coffee mugs and monitors"
  
  - marker: copilot-pre-cortex
    prompt_title: "2. Copilot (Pre-CORTEX) - The Amnesiac Intern"
    patterns:
      - "copilot*pre*"
      - "amnesiac*intern*"
      - "character*2*"
    caption: "Copilot: Brilliant but forgetful, before receiving a brain"
    act: 1
    placement: "when_copilot_first_described"
    alt_text: "Robot character made of server racks with confused expression and question marks"
  
  - marker: cortex-1.0-awakened
    prompt_title: "3. CORTEX 1.0 - The Awakened Partner"
    patterns:
      - "cortex*1*"
      - "awakened*"
      - "character*3*"
    caption: "CORTEX 1.0: Awakened and aware, with glowing brain"
    act: 2
    placement: "when_brain_first_activated"
    alt_text: "Robot with glowing translucent brain dome showing neural activity"
  
  - marker: 5-tier-memory-diagram
    prompt_title: "7. 5-Tier Memory System (Vertical Cross-Section)"
    patterns:
      - "5*tier*"
      - "memory*system*"
      - "vertical*cross*"
    caption: "The 5-Tier Memory System: From Instinct to Event Stream"
    act: 1
    placement: "after_memory_discussion"
    alt_text: "Vertical diagram showing 5 layers of CORTEX memory architecture"
  
  - marker: dual-hemisphere-architecture
    prompt_title: "6. Dual-Hemisphere Architecture (Detailed)"
    patterns:
      - "dual*hemisphere*"
      - "right*brain*left*brain*"
      - "architecture*split*"
    caption: "Right Brain (Strategic) vs Left Brain (Tactical)"
    act: 2
    placement: "when_hemispheres_introduced"
    alt_text: "Split-screen diagram showing right brain planning vs left brain execution"
  
  - marker: plugin-system-architecture
    prompt_title: "8. Plugin System Architecture"
    patterns:
      - "plugin*system*"
      - "plugin*architecture*"
      - "modular*plugins*"
    caption: "Plugin System: Extensibility without core bloat"
    act: 4
    placement: "chapter_8_plugin_discussion"
    alt_text: "Diagram of CORTEX core with surrounding plugin modules"
  
  - marker: workflow-pipeline-dag
    prompt_title: "9. Workflow Pipeline System (DAG Visualization)"
    patterns:
      - "workflow*pipeline*"
      - "dag*"
      - "pipeline*dag*"
    caption: "Workflow Pipelines: Declarative task orchestration"
    act: 5
    placement: "chapter_10_workflow_discussion"
    alt_text: "DAG flowchart showing workflow stages and dependencies"
  
  - marker: self-review-dashboard
    prompt_title: "11. Performance Optimization Results"
    patterns:
      - "performance*"
      - "self*review*"
      - "dashboard*"
    caption: "Self-Review System: CORTEX maintains itself"
    act: 4
    placement: "chapter_9_self_review_discussion"
    alt_text: "Dashboard with performance gauges and health metrics"
  
  # Add remaining 8+ images from Image-Prompts.md
  # ...

# Fuzzy matching configuration
matching:
  min_confidence: 0.7
  case_sensitive: false
  allow_version_suffixes: true  # asifinstein_v2.png matches asifinstein*
  
# Fallback behavior
fallbacks:
  missing_image_placeholder: true
  placeholder_text: "<!-- TODO: Generate image '{marker}' from Image-Prompts.md -->"
  log_missing_images: true
```

---

## 🎭 5-Act Structure

### Act Organization (Preserves All 11 Chapters)

```yaml
acts:
  1:
    title: "THE AWAKENING"
    subtitle: "From Goldfish to Genius"
    chapters:
      - "Intro: The Basement, the Madman, and the Brainless Beast"
      - "Chapter 1: The Intern Who Forgot He Was an Intern"
      - "Chapter 2: The Brain That Built Garbage"
    key_concepts:
      - "Memory problem"
      - "Dual-hemisphere architecture"
      - "Strategic vs Tactical thinking"
    technical_sections:
      - "5-tier-memory"
      - "dual-hemisphere-architecture"
    images:
      - "asifinstein-character"
      - "copilot-pre-cortex"
      - "cortex-1.0-awakened"
      - "5-tier-memory-diagram"
      - "dual-hemisphere-architecture"
  
  2:
    title: "THE LEARNING"
    subtitle: "From Mistakes to Mastery"
    chapters:
      - "Chapter 3: The Intern Who Started Learning... Too Well"
      - "Chapter 4: The Brain That Said 'No'"
    key_concepts:
      - "Pattern learning"
      - "Rule #22 (Brain Protector)"
      - "Challenge bad ideas"
    technical_sections:
      - "knowledge-graph"
      - "brain-protector"
      - "rule-compliance"
    images:
      - "knowledge-graph-neural-network"
      - "brain-protector-challenge"
  
  3:
    title: "THE PARTNERSHIP"
    subtitle: "From Tool to Teammate"
    chapters:
      - "Chapter 5: The Partner"
      - "Chapter 6: The Files That Got Too Fat"
    key_concepts:
      - "Co-development relationship"
      - "Modular architecture"
      - "File size discipline"
    technical_sections:
      - "modular-architecture"
      - "file-size-reduction"
    images:
      - "file-size-comparison"
      - "modular-structure"
  
  4:
    title: "THE EVOLUTION"
    subtitle: "From 1.0 to 2.0"
    chapters:
      - "Chapter 7: The Conversation That Disappeared"
      - "Chapter 8: The Plugin That Saved Christmas"
      - "Chapter 9: The System That Fixed Itself"
    key_concepts:
      - "Conversation state management"
      - "Plugin system"
      - "Self-review and auto-fix"
    technical_sections:
      - "conversation-state"
      - "plugin-system"
      - "self-review-system"
    images:
      - "conversation-state-machine"
      - "plugin-system-architecture"
      - "self-review-dashboard"
  
  5:
    title: "THE MASTERY"
    subtitle: "The Future of CORTEX"
    chapters:
      - "Chapter 10: The Workflow That Wrote Itself"
      - "Chapter 11: The Brain That Knew Too Much"
      - "Epilogue Part 2: The Partner Evolved"
    key_concepts:
      - "Workflow pipelines"
      - "Knowledge boundaries"
      - "Complete evolution"
    technical_sections:
      - "workflow-pipeline-system"
      - "knowledge-boundaries"
      - "performance-optimization"
    images:
      - "workflow-pipeline-dag"
      - "knowledge-boundary-enforcement"
      - "evolution-timeline"
```

---

## 🛠️ Implementation: Generation Script

### Script: scripts/generate_integrated_story.py

**Key Features:**
1. **Marker Processing** - Parse story and replace markers
2. **Fuzzy Image Matching** - Match filenames to patterns
3. **Technical Extraction** - Extract relevant sections
4. **Admonition Formatting** - Create Material Design callouts
5. **Act Organization** - Structure into 5 Acts with navigation
6. **Validation** - Report missing assets
7. **Graceful Degradation** - Handle missing images/sections

**Pseudo-Implementation:**

```python
class IntegratedStoryGenerator:
    def __init__(self, source_dir: Path, output_dir: Path):
        self.source_dir = source_dir  # docs/story/CORTEX-STORY/
        self.output_dir = output_dir  # docs/story/
        self.images_dir = source_dir / "images"
        
        # Load configurations
        self.image_mapping = self._load_image_mapping()
        self.act_structure = self._load_act_structure()
        
        # State
        self.image_cache = {}
        self.technical_cache = {}
        self.missing_assets = []
    
    def generate(self) -> Path:
        """Generate integrated story"""
        # 1. Scan for new images
        self._discover_images()
        
        # 2. Parse source files
        story_content = self._parse_story_file()
        technical_sections = self._parse_technical_file()
        
        # 3. Process markers
        integrated_content = self._process_markers(
            story_content,
            technical_sections
        )
        
        # 4. Organize into Acts
        final_content = self._organize_into_acts(integrated_content)
        
        # 5. Write output
        output_path = self.output_dir / "awakening-integrated.md"
        output_path.write_text(final_content)
        
        # 6. Generate validation report
        self._generate_validation_report()
        
        return output_path
    
    def _discover_images(self):
        """Scan images/ folder and match to markers"""
        for image_file in self.images_dir.glob("*.png"):
            # Try to match against all patterns
            matched_marker = self._fuzzy_match_image(image_file.name)
            
            if matched_marker:
                self.image_cache[matched_marker] = image_file
                print(f"✓ Matched: {image_file.name} → {matched_marker}")
            else:
                print(f"? Unknown: {image_file.name} (no matching marker)")
    
    def _fuzzy_match_image(self, filename: str) -> Optional[str]:
        """Fuzzy match image filename to marker using patterns"""
        filename_lower = filename.lower()
        
        for marker, config in self.image_mapping.items():
            patterns = config['patterns']
            
            for pattern in patterns:
                # Convert glob pattern to regex
                regex_pattern = pattern.replace('*', '.*')
                
                if re.match(regex_pattern, filename_lower):
                    confidence = self._calculate_confidence(
                        filename_lower, 
                        pattern
                    )
                    
                    if confidence >= 0.7:  # Min confidence threshold
                        return marker
        
        return None
    
    def _process_markers(self, story: str, technical: Dict) -> str:
        """Process all markers in story"""
        lines = story.split('\n')
        output = []
        
        for line in lines:
            # Check for markers
            if '<!-- IMAGE:' in line:
                marker = self._extract_marker(line, 'IMAGE')
                output.append(self._embed_image(marker))
            
            elif '<!-- TECH:' in line:
                marker = self._extract_marker(line, 'TECH')
                output.append(self._embed_technical(marker, technical))
            
            elif '<!-- ACT:' in line and ':START' in line:
                act_num = self._extract_act_number(line)
                output.append(self._create_act_header(act_num))
            
            else:
                output.append(line)
        
        return '\n'.join(output)
    
    def _embed_image(self, marker: str) -> str:
        """Embed image with caption"""
        if marker not in self.image_cache:
            # Missing image - use placeholder
            self.missing_assets.append(('image', marker))
            return f"<!-- TODO: Generate image '{marker}' from Image-Prompts.md -->\n"
        
        image_file = self.image_cache[marker]
        config = self.image_mapping[marker]
        
        # Relative path from docs/story/
        rel_path = f"CORTEX-STORY/images/{image_file.name}"
        
        return f"""
![{config['alt_text']}]({rel_path})
*{config['caption']}*
"""
    
    def _embed_technical(self, marker: str, technical: Dict) -> str:
        """Embed technical content as admonition"""
        if marker not in technical:
            # Missing technical section
            self.missing_assets.append(('technical', marker))
            return f"<!-- TODO: Add technical section '{marker}' -->\n"
        
        section = technical[marker]
        
        # Extract title and first 2 paragraphs
        title = section['title']
        summary = section['summary']  # First 2 paragraphs
        
        # Create expandable admonition
        return f"""
??? info "{title}"
    {summary}
    
    **[Read full technical details →](../Technical-CORTEX.md#{marker})**
"""
    
    def _create_act_header(self, act_num: int) -> str:
        """Create Act header with navigation"""
        act = self.act_structure[act_num]
        
        return f"""
---

# ACT {act_num}: {act['title']}
*{act['subtitle']}*

**Chapters:**
{self._format_chapter_list(act['chapters'])}

**Key Concepts:** {', '.join(act['key_concepts'])}

---
"""
    
    def _generate_validation_report(self):
        """Generate validation report"""
        report = [
            "# Integrated Story Validation Report",
            f"**Generated:** {datetime.now().isoformat()}",
            "",
            "## Summary",
            f"- Images embedded: {len(self.image_cache)}/{len(self.image_mapping)}",
            f"- Technical sections linked: {len(self.technical_cache)}/{len(self._get_required_technical())}",
            f"- Missing assets: {len(self.missing_assets)}",
            ""
        ]
        
        if self.missing_assets:
            report.append("## Missing Assets")
            report.append("")
            
            for asset_type, marker in self.missing_assets:
                if asset_type == 'image':
                    config = self.image_mapping[marker]
                    report.append(f"- 🖼️ Image: `{marker}`")
                    report.append(f"  - Prompt: {config['prompt_title']}")
                    report.append(f"  - Expected patterns: {config['patterns']}")
                    report.append("")
                else:
                    report.append(f"- 📄 Technical: `{marker}`")
                    report.append("")
        
        else:
            report.append("✅ All assets present!")
        
        # Write report
        report_path = self.output_dir / "integrated-story-status.md"
        report_path.write_text('\n'.join(report))
```

---

## 🔌 Documentation Refresh Plugin Integration

### Enhanced Plugin: src/plugins/documentation_plugin.py

```python
class Plugin(BasePlugin):
    """Auto-refresh documentation plugin (ENHANCED)"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute documentation refresh"""
        
        # 1. Run integrated story generation
        generator = IntegratedStoryGenerator(
            source_dir=Path("docs/story/CORTEX-STORY"),
            output_dir=Path("docs/story")
        )
        
        try:
            output_path = generator.generate()
            
            # 2. Validate integrity
            validation_report = self._validate_integrated_story(output_path)
            
            # 3. Update MkDocs navigation
            self.doc_manager.update_mkdocs_config(backup=True)
            
            # 4. Rebuild MkDocs site
            self._rebuild_mkdocs()
            
            return {
                "success": True,
                "message": "Documentation refreshed successfully",
                "integrated_story": str(output_path),
                "validation": validation_report
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Integrated story generation failed"
            }
```

---

## 🎨 Admonition Styles

### Material Design Admonitions

```markdown
# Inline info box (technical callouts)
!!! info "The Memory Problem"
    Early AI coding assistants operated statelessly - each request was isolated.
    Without persistent memory (Tier 1 Working Memory), context was lost between 
    conversations, forcing users to repeat information constantly.
    
    **Technical Deep-Dive:** See [5-Tier Memory System](../Technical-CORTEX.md#5-tier-memory)

# Expandable details (longer technical content)
??? note "Technical Deep-Dive: Plugin System"
    Click to expand full technical specification...
    
    [Full technical content here]

# Side note (brief annotations)
!!! note inline end
    Tier 1 Memory stores last 20 conversations in SQLite with FTS5 search.
```

---

## 🚀 User Workflow

### Step-by-Step Process

1. **User generates images in Gemini** using prompts from `Image-Prompts.md`
2. **User saves images** to `docs/story/CORTEX-STORY/images/` with any reasonable filename
   - Example: `asifinstein_mad_scientist_v2.png`
3. **User says:** "Refresh documentation"
4. **System executes:**
   - Scans images folder
   - Fuzzy matches: `asifinstein_mad_scientist_v2.png` → marker `asifinstein-character` (90% confidence)
   - Extracts technical section `5-tier-memory` from Technical-CORTEX.md
   - Processes markers in Awakening Of CORTEX.md
   - Embeds image at `<!-- IMAGE:asifinstein-character -->` marker
   - Inserts technical admonition at `<!-- TECH:5-tier-memory -->` marker
   - Generates `docs/story/awakening-integrated.md`
   - Creates validation report
   - Rebuilds MkDocs site
5. **Result:** Integrated story updated, image embedded, technical content woven in

---

## ✅ Success Criteria

1. **Zero Manual Work** - User only generates/saves images, everything else automated ✅
2. **Intelligent Weaving** - Images/technical content flow naturally in narrative ✅
3. **Fuzzy Matching** - Works with any reasonable image filename ✅
4. **5-Act Preservation** - Structure maintained across updates ✅
5. **Graceful Degradation** - Missing images/sections don't break generation ✅
6. **Validation Reporting** - Clear report of missing assets ✅

---

## 📊 Benefits

### For Users
- ✅ No manual document editing
- ✅ Just generate images, drop in folder
- ✅ Say "refresh" and done
- ✅ Beautiful integrated story automatically

### For Readers
- ✅ Seamless reading experience
- ✅ Images at perfect narrative moments
- ✅ Technical details when needed
- ✅ 5-Act structure easy to navigate

### For Maintenance
- ✅ Update source files independently
- ✅ Add new images anytime
- ✅ Regenerate integrated story on-demand
- ✅ Validation ensures quality

---

## 🎯 Integration with CORTEX 2.0

### Dependencies
- **06-documentation-system.md** - Base documentation manager
- **02-plugin-system.md** - Plugin architecture
- **23-modular-entry-point.md** - Entry point integration

### Implementation Priority
- **Phase:** Documentation & Tooling (Phase 4)
- **Priority:** MEDIUM (nice-to-have, not critical)
- **Estimated Effort:** 12-16 hours
  - Add markers to source files: 2-3 hrs
  - Create image mapping YAML: 1-2 hrs
  - Build generation script: 6-8 hrs
  - Enhance documentation plugin: 2-3 hrs
  - Testing & validation: 1 hr

---

## 🚦 Implementation Roadmap

### Phase 1: Source File Annotation (2-3 hours)
1. Add Act markers to `Awakening Of CORTEX.md`
2. Add image markers (10-15 strategic locations)
3. Add technical markers (8-10 locations)
4. Add section IDs to `Technical-CORTEX.md`
5. Create backup of original files

### Phase 2: Configuration (1-2 hours)
1. Create `images/image-mapping.yaml`
2. Map all 16 image prompts to markers
3. Define fuzzy matching patterns
4. Set fallback behavior

### Phase 3: Generation Script (6-8 hours)
1. Implement marker parsing
2. Implement fuzzy image matching
3. Implement technical section extraction
4. Implement admonition formatting
5. Implement Act organization
6. Implement validation reporting

### Phase 4: Plugin Integration (2-3 hours)
1. Enhance documentation plugin
2. Add integrated story generation trigger
3. Add validation step
4. Add MkDocs rebuild

### Phase 5: Testing (1 hour)
1. Test with no images (graceful degradation)
2. Test with partial images
3. Test with all images
4. Test fuzzy matching with various filenames
5. Validate 5-Act structure preserved

**Total Time:** 12-16 hours

---

## 📝 Notes

### Design Decision: Why 5 Acts, Not 5 Chapters?

**Problem:** Compressing 11 chapters to 5 = 60% content loss

**Solution:** Organize 11 chapters into 5 Acts (groupings)
- ✅ Preserves all 11 chapters (no content loss)
- ✅ Logical 5-part structure for navigation
- ✅ Better storytelling flow (acts have themes)
- ✅ Easier to weave technical content per Act

### Design Decision: Markers vs. AI Detection

**Why markers?**
- ✅ Precise control over placement
- ✅ No AI guesswork (deterministic)
- ✅ Easy to adjust manually
- ✅ Clear documentation of intent

**Why not AI detection?**
- ❌ Unpredictable placement
- ❌ May interrupt narrative flow
- ❌ Hard to debug when wrong
- ❌ Context-dependent (fragile)

### Design Decision: Fuzzy Matching vs. Exact Names

**Why fuzzy matching?**
- ✅ User-friendly (any reasonable name works)
- ✅ Handles versions (image_v2.png)
- ✅ Resilient to typos
- ✅ Gemini may add suffixes to filenames

---

## 🎉 Summary

This design provides a **fully automated system** for generating rich, integrated story documentation that combines narrative, technical content, and images in a seamless reading experience.

**Key Features:**
- ✅ Marker-based placement system
- ✅ Fuzzy image matching
- ✅ 5-Act structure (preserves 11 chapters)
- ✅ Material Design admonitions
- ✅ Validation reporting
- ✅ Zero manual work after setup

**User Experience:**
1. Generate images in Gemini
2. Save to images/ folder
3. Say "refresh documentation"
4. **Done** - integrated story updated

**Implementation:** 12-16 hours, Medium priority, Phase 4 (Documentation & Tooling)

---

**Status:** Design Complete ✅  
**Ready for Implementation:** After Phase 3 (Core Features)  
**Next Steps:**
1. Add to `00-INDEX.md` under Documentation section
2. Schedule for Phase 4 implementation
3. Create marker annotation task
