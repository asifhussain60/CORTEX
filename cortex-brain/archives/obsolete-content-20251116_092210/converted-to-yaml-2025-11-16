# CORTEX Documentation Refresh Command

**Purpose:** Comprehensive documentation update workflow that analyzes recent development changes and refreshes all documentation accordingly.

**Version:** 1.0  
**Created:** November 7, 2025  
**Status:** 🎯 ACTIVE

---

## 🎯 Command Invocation

```markdown
#file:prompts/user/refresh-docs.md

Refresh CORTEX documentation based on recent development changes.
```

**Optional Parameters:**
```markdown
#file:prompts/user/refresh-docs.md --since="2025-11-01" --depth=full --deploy=true

Refresh with specific start date, full depth analysis, and auto-deploy to GitHub Pages.
```

---

## 🔄 Workflow Overview

### Four-File Documentation Structure

CORTEX documentation follows a four-file architecture:

1. **Awakening Of CORTEX.md** - Narrative story (95% story, 5% concepts)
   - Path: `docs\story\CORTEX-STORY\Awakening Of CORTEX.md`
   - Purpose: Human-centered story of CORTEX development
   - Style: First person "I", emotional arc, vision-focused
   - Content: NO code blocks, NO technical stats, examples in narrative

2. **Technical-CORTEX.md** - Technical documentation (100% technical)
   - Path: `docs\story\CORTEX-STORY\Technical-CORTEX.md`
   - Purpose: Granular technical details of entire system
   - Style: Professional technical documentation
   - Content: Code, APIs, metrics, architecture, specifications

3. **Image-Prompts.md** - AI image generation prompts
   - Path: `docs\story\CORTEX-STORY\Image-Prompts.md`
   - Purpose: Generate schematic diagrams and technical illustrations
   - Style: Detailed AI prompts with gothic cyberpunk technical aesthetic
   - Content: Based on Technical-CORTEX.md, append-only (preserve existing)

4. **History.md** - Development timeline
   - Path: `docs\project\History.md`
   - Purpose: Chronicle technical decisions and milestones
   - Style: First person "I", chronological
   - Content: Technical details, motivation, challenges, outcomes

**Integration:**
- Story references images from `/docs/assets/images/`
- Images generated from Image-Prompts.md
- Technical docs provide source material for prompts
- History tracks when features were added

### Workflow Diagram

```mermaid
graph TB
    Start[User Invokes refresh-docs.md] --> Git[Git Analysis]
    Git --> Scan[Codebase Scan]
    Scan --> Compare[Compare with Docs]
    Compare --> Decision{Changes Detected?}
    
    Decision -->|Yes| Story[Update Awakening Story]
    Decision -->|No| Skip[No updates needed]
    
    Story --> Technical[Update Technical-CORTEX]
    Technical --> Images[Review Image Needs]
    Images --> Diagrams{New Diagrams Needed?}
    
    Diagrams -->|Yes| Gemini[Generate Prompts in Image-Prompts.md]
    Diagrams -->|No| History[Update History.md]
    Gemini --> History
    
    History --> Build[Build MkDocs]
    Build --> Test[Test Locally]
    Test --> Deploy{Auto-Deploy?}
    
    Deploy -->|Yes| GHPages[Deploy to GitHub Pages]
    Deploy -->|No| Complete[Complete]
    GHPages --> Complete
    Skip --> Complete
    
    style Start fill:#9c27b0,stroke:#fff,color:#fff
    style Complete fill:#4caf50,stroke:#fff,color:#fff
    style Decision fill:#ff9800,stroke:#fff,color:#fff
    style Diagrams fill:#ff9800,stroke:#fff,color:#fff
```

---

## 📋 Phase 1: Git Analysis & Change Detection

### 1.1 Analyze Recent Commits

**Query Git History:**
```bash
# Get commits since last docs deployment
git log --since="2025-11-01" --oneline --stat

# Get changed files
git diff HEAD~10 --name-only

# Get commit messages for context
git log --since="2025-11-01" --pretty=format:"%h - %an, %ar : %s"
```

**What to Extract:**
- ✅ New files created
- ✅ Modified files (especially in `CORTEX/src/`)
- ✅ Deleted/moved files
- ✅ Commit messages indicating features/fixes
- ✅ Test files changes (indicate new functionality)
- ✅ Configuration changes

**CORTEX Action:**
```yaml
tier3_query: recent_development_activity
output:
  - commit_count: int
  - files_changed: list
  - feature_commits: list (feat:, fix:, docs:)
  - test_additions: list
  - architecture_changes: list
```

### 1.2 Identify Documentation Gaps

**Compare Git Changes with Documentation:**

```python
# Pseudocode for gap detection
recent_changes = get_git_changes(since_date)
documented_features = scan_docs("docs/")

gaps = []
for change in recent_changes:
    if change.type == "new_feature":
        if not documented_in_story(change):
            gaps.append({
                "type": "story_missing",
                "feature": change.name,
                "files": change.files
            })
        if not documented_in_technical(change):
            gaps.append({
                "type": "technical_missing",
                "feature": change.name
            })
        if needs_diagram(change):
            gaps.append({
                "type": "diagram_missing",
                "feature": change.name,
                "diagram_type": infer_diagram_type(change)
            })

return gaps
```

**Output:**
```yaml
documentation_gaps:
  - type: story_missing
    feature: "Tier 3 context intelligence"
    impact: high
    files: [tier3/context_collector.py, tier3/metrics_analyzer.py]
  
  - type: technical_missing
    feature: "Auto-learning triggers"
    impact: medium
    files: [brain/learning_loop.py]
  
  - type: diagram_missing
    feature: "Protection system layers"
    diagram_type: shield_layers
    impact: high
```

---

## 📋 Phase 2: Story Update ("The Awakening of CORTEX")

### 2.1 Target Files

The documentation refresh process updates these specific story files:

1. **`docs\story\CORTEX-STORY\Awakening Of CORTEX.md`**
   - 95% narrative story, 5% high-level technical concepts
   - NO code blocks, NO technical stats, NO low-level details
   - Functionality weaved into story narrative using examples
   - Use first person "I" (not Asifinstein or any other name)
   - Maintain emotional arc and vision-focused narrative

2. **`docs\story\CORTEX-STORY\Technical-CORTEX.md`**
   - Granular technical details of CORTEX system
   - Complete architecture documentation
   - Code examples, API references, technical specifications
   - Performance metrics and benchmarks
   - Implementation details at component level

3. **`docs\story\CORTEX-STORY\Image-Prompts.md`**
   - AI prompts for generating schematic diagrams and illustrations
   - Based on Technical-CORTEX.md content
   - Flowcharts, structure diagrams, visual representations
   - Collapsed version combines narrative with generated images from `/docs/assets/images/` folder

4. **`docs\project\History.md`** (if exists, otherwise create)
   - Technical development history timeline
   - Use first person "I" throughout
   - Chronicle of technical decisions and milestones
   - NO placeholder names (Asifinstein, etc.)

### 2.2 Review Story Completeness

**Check if Recent Features Mentioned:**
```yaml
story_chapters:
  - chapter: 1
    title: "The Problem - Copilot's Amnesia"
    coverage: complete
    needs_update: false
  
  - chapter: 2
    title: "The Solution - Dual-Hemisphere Brain"
    coverage: partial
    needs_update: true
    missing: ["Agent specialization details", "Corpus callosum message formats"]
  
  - chapter: 3
    title: "The Memory System - Five Tiers"
    coverage: good
    needs_update: false
  
  - chapter: 4
    title: "Protection & Discovery"
    coverage: excellent
    needs_update: false
  
  - chapter: 5
    title: "Grand Activation"
    coverage: complete
    needs_update: false
```

### 2.3 Update Story Content

**Update Rules for Awakening Of CORTEX.md:**
- ✅ 95% narrative story, 5% high-level technical concepts
- ❌ NO code blocks allowed
- ❌ NO technical statistics or performance metrics
- ❌ NO low-level implementation details
- ✅ Weave CORTEX capabilities into story using examples
- ✅ Use first person "I" consistently
- ✅ Maintain emotional arc (frustration → clarity → ambition → success)
- ✅ Show system intelligence through narrative scenes, not specs
- ✅ Keep vision and human element central

**Update Rules for Technical-CORTEX.md:**
- ✅ Complete granular technical details
- ✅ Architecture diagrams and flowcharts
- ✅ Code blocks and API references
- ✅ Performance metrics and benchmarks
- ✅ Implementation details at component level
- ✅ Configuration examples
- ✅ Testing procedures

**If Updates Needed:**

**Template for Story Integration (Awakening Of CORTEX.md):**
```markdown
<!-- Insert into appropriate chapter -->

## [Chapter Section Title]

[Narrative text in first person, describing the challenge or vision]

I stared at the screen, watching the pattern emerge. The system wasn't just 
remembering—it was learning. Each conversation built upon the last, creating 
a tapestry of context that grew richer with every interaction.

[Continue narrative, weaving in capability naturally through story]

The breakthrough came when I realized [technical insight told as story moment].

[More narrative showing the outcome through experience, not specs]

```

**Template for Technical Documentation (Technical-CORTEX.md):**
```markdown
<!-- Insert into appropriate section -->

## [Feature/Component Name]

### Overview
**Purpose:** [Clear technical purpose]  
**Location:** `path/to/file.py`  
**Dependencies:** [List]  
**Status:** ✅ Implemented / 🔄 In Progress / 📋 Planned

### Architecture

```mermaid
graph TD
    [Detailed component diagram]
```

### Implementation Details

**Core Components:**
- Component 1: [Technical description]
- Component 2: [Technical description]

**Data Flow:**
1. Step 1: [Detailed technical step]
2. Step 2: [Detailed technical step]

### Code Examples

```python
from cortex.component import feature

# Example usage with detailed comments
result = feature.execute(
    param1="value",
    param2=42
)
# Output: [expected output]
```

### Performance Metrics
- Query time: <50ms (p95)
- Memory usage: <10MB
- Throughput: 1000 ops/sec

### Configuration
```yaml
component_name:
  setting1: value
  setting2: value
```

### Testing Coverage
- Unit tests: ✅ 95%
- Integration tests: ✅ 90%
- Test files: `tests/test_component.py`

```

**Template for Image Prompts (Image-Prompts.md):**
```markdown
<!-- Append new prompts, don't replace existing -->

---

## [Feature Name] - Visualization Request

**Date:** [YYYY-MM-DD]  
**Based On:** Technical-CORTEX.md Section [X.Y]  
**Image Type:** [Diagram/Flowchart/Schematic/Illustration]

**Purpose:**
Visualize [specific aspect] of the CORTEX system to illustrate [concept].

**Detailed Prompt for AI:**
```
Create a [type] showing:

Main Elements:
- [Element 1 with detailed description]
- [Element 2 with detailed description]
- [Element 3 with detailed description]

Visual Style:
- Gothic cyberpunk aesthetic
- Dark background with neon accents
- Technical schematic overlay
- Brain hemisphere motif if relevant

Color Palette:
- Primary: Deep purple (#9c27b0)
- Secondary: Electric blue (#00bcd4)
- Accent: Neon green (#4caf50)
- Background: Dark gray (#1e1e1e)

Layout:
[Describe spatial arrangement]

Labels and Annotations:
- Clear component labels
- Flow direction indicators
- Connection lines showing data flow

Style Reference:
Similar to existing CORTEX technical illustrations with 
brain architecture, layered system diagrams, and dramatic 
lighting effects.
```

**Placement:** 
- File: Technical-CORTEX.md
- Section: [Specific section]
- Alternative Text: [Accessibility description]

**Output Filename:** `cortex-[feature-name]-[diagram-type].png`  
**Target Location:** `docs/assets/images/`

---
```

**Template for History.md Updates:**
```markdown
<!-- Add to chronological timeline -->

## [YYYY-MM-DD] - [Feature/Milestone Name]

I implemented [feature description in first person].

**Technical Details:**
- [Detail 1]
- [Detail 2]
- [Detail 3]

**Motivation:**
[Why this was needed, in first person]

**Challenges:**
[Technical challenges encountered, in first person]

**Outcome:**
[Results and impact, in first person]

**Files Modified:**
- `path/to/file1.py`
- `path/to/file2.py`

---
```

**CORTEX Action:**
```python
def update_story(gaps):
    for gap in gaps:
        if gap.type == "story_missing":
            # Update Awakening Of CORTEX.md (narrative only)
            story_chapter = determine_chapter(gap.feature)
            narrative = generate_narrative(
                feature=gap.feature,
                style="first_person_narrative",  # Changed from "asifinstein_voice"
                tone="visionary_and_emotional",
                technical_level="high_level_concepts_only"  # No code/stats
            )
            
            insert_into_file(
                file="docs/story/CORTEX-STORY/Awakening Of CORTEX.md",
                chapter=story_chapter,
                content=narrative,
                position="contextual"
            )
            
            # Update Technical-CORTEX.md (granular details)
            technical_section = determine_technical_section(gap.feature)
            technical_content = generate_technical_doc(
                feature=gap.feature,
                include_code=True,
                include_metrics=True,
                include_diagrams=True,
                granularity="detailed"
            )
            
            insert_into_file(
                file="docs/story/CORTEX-STORY/Technical-CORTEX.md",
                section=technical_section,
                content=technical_content,
                position="appropriate"
            )
            
            # Update Image-Prompts.md (AI generation prompts)
            if needs_visualization(gap.feature):
                image_prompt = generate_image_prompt(
                    feature=gap.feature,
                    based_on="Technical-CORTEX.md content",
                    style="gothic_cyberpunk_technical",
                    diagram_type=infer_diagram_type(gap.feature)
                )
                
                append_to_file(
                    file="docs/story/CORTEX-STORY/Image-Prompts.md",
                    content=image_prompt,
                    mode="append_only"  # Never replace existing prompts
                )
            
            # Update History.md (technical timeline)
            history_entry = generate_history_entry(
                feature=gap.feature,
                perspective="first_person",  # Use "I"
                include_technical_details=True,
                include_motivation=True
            )
            
            append_to_file(
                file="docs/project/History.md",
                content=history_entry,
                mode="chronological"
            )
```

### 2.3 Story Quality Checks

**Validation for Awakening Of CORTEX.md:**
- ✅ 95% story / 5% technical ratio maintained
- ✅ First person "I" used consistently (no character names)
- ✅ No code blocks in narrative
- ✅ No technical statistics in prose
- ✅ Capabilities shown through examples in narrative
- ✅ Emotional arc preserved (frustration → clarity → ambition)
- ✅ Vision and human element central
- ✅ Seamless flow between sections

**Validation for Technical-CORTEX.md:**
- ✅ Complete granular technical coverage
- ✅ Code examples present and functional
- ✅ Performance metrics included
- ✅ Architecture diagrams accurate
- ✅ API references complete
- ✅ Configuration examples provided
- ✅ Testing procedures documented

**Validation for Image-Prompts.md:**
- ✅ Prompts based on Technical-CORTEX.md content
- ✅ Clear visual descriptions
- ✅ Gothic cyberpunk style maintained
- ✅ Placement locations specified
- ✅ Output filenames follow convention
- ✅ Prompts appended, not replaced
- ✅ Existing prompts preserved

**Validation for History.md:**
- ✅ First person "I" used throughout
- ✅ Chronological order maintained
- ✅ Technical details included
- ✅ Motivation and challenges documented
- ✅ Files modified listed
- ✅ No placeholder character names

**Overall Quality Checks:**
- ✅ Images placed contextually in Technical-CORTEX.md
- ✅ Image files exist in `/docs/assets/images/` folder
- ✅ Cross-references between story and technical docs
- ✅ Seamless flow (no hard section breaks)
- ✅ Technical accuracy verified against codebase
- ✅ No duplicate content between story and technical docs

---

## 📋 Phase 3: Technical Documentation Update

### 3.1 Scan Documentation Structure

**Inventory Current Docs:**
```yaml
technical_docs:
  architecture:
    - system-overview.md (status: current)
    - dual-hemispheres.md (status: needs_update)
    - three-tier-brain.md (status: current)
  
  tiers:
    - tier0-governance.md (status: current)
    - tier1-working-memory.md (status: current)
    - tier2-knowledge-graph.md (status: needs_update)
    - tier3-context.md (status: needs_update)
  
  agents:
    - overview.md (status: needs_update)
    - intent-router.md (status: current)
    - work-planner.md (status: current)
    - code-executor.md (status: missing)
    - test-generator.md (status: missing)
    # ... etc
  
  api:
    - governance-engine.md (status: missing)
    - tier1-api.md (status: missing)
    - tier2-api.md (status: missing)
    - tier3-api.md (status: missing)
```

### 3.2 Update Technical Docs

**For Each Gap:**

**Template: New Technical Doc**
```markdown
# [Feature/Component Name]

## Overview
- **Purpose:** [Clear purpose]
- **Location:** `path/to/file.py`
- **Dependencies:** [List]
- **Status:** ✅ Implemented / 🔄 In Progress / 📋 Planned

## Architecture

```mermaid
graph TD
    [Component diagram]
```

## API Reference

### `function_name(param1, param2)`

**Purpose:** [Description]

**Parameters:**
- `param1` (type): Description
- `param2` (type): Description

**Returns:** `type` - Description

**Example:**
```python
from cortex.component import function_name

result = function_name(
    param1="value",
    param2=42
)
# Output: [expected output]
```

## Configuration

```yaml
component_name:
  setting1: value
  setting2: value
```

## Testing

**Test Coverage:** 95%  
**Test Files:**
- `tests/test_component.py`

**Key Tests:**
- ✅ Test basic functionality
- ✅ Test error handling
- ✅ Test edge cases

## Performance

**Benchmarks:**
- Query time: <50ms (p95)
- Memory usage: <10MB
- Throughput: 1000 ops/sec

## Troubleshooting

### Issue: [Common problem]
**Symptoms:** [What users see]  
**Solution:** [How to fix]

## See Also
- [Related Doc 1](../path/to/doc1.md)
- [Related Doc 2](../path/to/doc2.md)
```

### 3.3 Update Existing Docs

**CORTEX Action:**
```python
def update_technical_docs(gaps):
    for gap in gaps:
        if gap.type == "technical_missing":
            # Create new doc
            doc = generate_technical_doc(
                feature=gap.feature,
                files=gap.files,
                template="standard_technical"
            )
            save_doc(doc, path=determine_doc_path(gap))
        
        elif gap.type == "technical_outdated":
            # Update existing
            existing_doc = load_doc(gap.doc_path)
            updates = generate_updates(gap)
            merge_updates(existing_doc, updates)
            save_doc(existing_doc)
```

---

## 📋 Phase 4: Image & Diagram Analysis

### 4.1 Identify Visual Needs

**Scan for Diagram Opportunities:**
```python
def identify_diagram_needs(recent_changes):
    diagram_needs = []
    
    for change in recent_changes:
        # Architecture changes need diagrams
        if change.affects_architecture:
            diagram_needs.append({
                "type": "architecture_diagram",
                "feature": change.name,
                "diagram_format": "mermaid",
                "priority": "high"
            })
        
        # New workflows need sequence diagrams
        if change.adds_workflow:
            diagram_needs.append({
                "type": "sequence_diagram",
                "feature": change.name,
                "diagram_format": "mermaid",
                "priority": "medium"
            })
        
        # Complex concepts need illustrations
        if change.complexity == "high":
            diagram_needs.append({
                "type": "conceptual_illustration",
                "feature": change.name,
                "diagram_format": "ai_generated",
                "priority": "high"
            })
    
    return diagram_needs
```

### 4.2 Generate Mermaid Diagrams

**For Technical Diagrams:**
```markdown
<!-- Automatically generate and insert -->

```mermaid
graph TB
    [Auto-generated based on code analysis]
```
```

**CORTEX Action:**
```python
def generate_mermaid(feature, diagram_type):
    if diagram_type == "architecture":
        components = analyze_components(feature)
        return mermaid_architecture(components)
    
    elif diagram_type == "sequence":
        workflow = analyze_workflow(feature)
        return mermaid_sequence(workflow)
    
    elif diagram_type == "flow":
        logic = analyze_logic(feature)
        return mermaid_flowchart(logic)
```

### 4.3 Generate Gemini Image Prompts

**Target File:** `docs\story\CORTEX-STORY\Image-Prompts.md`

**Only for Conceptual/Technical Diagrams:**

**CORTEX Action:**
```python
def generate_gemini_prompts(diagram_needs):
    prompts = []
    
    for need in diagram_needs:
        if need.diagram_format == "ai_generated":
            prompt = create_gemini_prompt(
                feature=need.feature,
                style="gothic_cyberpunk_technical",
                based_on="Technical-CORTEX.md content",
                elements=extract_visual_elements(need),
                diagram_type=need.diagram_type  # flowchart, schematic, etc.
            )
            prompts.append(prompt)
    
    # APPEND to Image-Prompts.md (never replace existing)
    append_to_file(
        path="docs/story/CORTEX-STORY/Image-Prompts.md",
        content=prompts,
        mode="append_only",
        section="NEW_PROMPTS_" + current_date()
    )
    
    print(f"✅ Added {len(prompts)} new prompts to Image-Prompts.md")
    print(f"⚠️ Existing prompts preserved (append-only mode)")
```

**Prompt Template:**
```markdown
---

## NEW PROMPTS - [Date]

### [Feature Name] Visualization

**Prompt ID:** IMG-[DATE]-[NUMBER]  
**Based On:** Technical-CORTEX.md Section [X.Y]  
**Diagram Type:** [Flowchart/Schematic/Architecture/Illustration]  
**Style:** Gothic cyberpunk technical

**Purpose:**
Illustrate [specific technical concept] from the CORTEX system documentation.

**Detailed Prompt:**
```
Create a [diagram type] showing [feature/concept]:

Main Components:
- [Component 1]: [Detailed visual description]
- [Component 2]: [Detailed visual description]
- [Component 3]: [Detailed visual description]

Visual Structure:
- Layout: [Spatial arrangement description]
- Flow: [Data/process flow indicators]
- Connections: [How components connect]
- Layers: [If applicable, layer structure]

Technical Elements:
- Labels: [Component labels and annotations]
- Arrows: [Direction and flow indicators]
- Boundaries: [System/module boundaries]
- Legend: [If needed, legend elements]

Color Palette:
- Primary: Deep purple (#9c27b0)
- Secondary: Electric blue (#00bcd4)
- Accent: Neon green (#4caf50) for active elements
- Background: Dark gray (#1e1e1e) / Deep blue (#0a0e27)
- Lines: Light cyan (#80deea)

Visual Style:
- Gothic cyberpunk aesthetic
- Technical schematic overlay
- Dramatic lighting with neon accents
- Clean, readable typography
- Professional diagram quality
- Brain hemisphere motif if relevant

Style Reference: 
Technical diagrams similar to existing CORTEX documentation 
images, with clear structure, dramatic atmosphere, and 
gothic-cyberpunk fusion.
```

**Placement:** 
- File: `docs/story/CORTEX-STORY/Technical-CORTEX.md`
- Section: [Specific section name]
- Context: [Where this appears in technical docs]

**Alternative Text:** [Accessibility description for screen readers]

**Output Filename:** `cortex-[feature-name]-[diagram-type].png`  
**Target Location:** `docs/assets/images/`

**Integration Note:**
This diagram visualizes technical content from Technical-CORTEX.md. 
The collapsed version in Awakening Of CORTEX.md will reference 
this image to enhance the narrative without adding technical details.

---
```

---

## 📋 Phase 5: Build & Test

### 5.1 Build MkDocs Site

**CORTEX Action:**
```bash
# Clean build to ensure no stale content
mkdocs build --clean

# Check for build errors
if [ $? -ne 0 ]; then
    echo "❌ Build failed - review errors"
    exit 1
fi

echo "✅ Build successful"

# Automatically launch local server for review
echo "🚀 Launching local documentation server..."
mkdocs serve

# Server will start at http://localhost:8000
# Opens automatically in default browser
```

**PowerShell Alternative:**
```powershell
# Clean build
mkdocs build --clean

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed - review errors" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Build successful" -ForegroundColor Green

# Launch local server and open in browser
Write-Host "🚀 Launching local documentation server..." -ForegroundColor Cyan
Start-Process "http://localhost:8000"
mkdocs serve
```

### 5.2 Local Testing

**Automated Checks:**
```python
def test_documentation():
    checks = []
    
    # Link validation
    checks.append(validate_all_links())
    
    # Image validation
    checks.append(validate_all_images())
    
    # Mermaid diagram rendering
    checks.append(validate_mermaid_diagrams())
    
    # Navigation completeness
    checks.append(validate_navigation())
    
    # Search functionality
    checks.append(test_search_index())
    
    # Responsive design
    checks.append(test_responsive_layout())
    
    # Accessibility
    checks.append(run_accessibility_audit())
    
    return all(checks)
```

**Manual Testing Checklist:**
```markdown
## Local Testing Checklist

**Server Status:** ✅ Running at `http://localhost:8000`  
**Browser:** Automatically opened for review

**Note:** Server launched automatically after successful build. 
         Press Ctrl+C to stop server when review complete.

### Visual Tests
- [ ] Navigation tabs visible on load
- [ ] Story uses Comic Sans font
- [ ] Technical sections use monospace
- [ ] Images load and display correctly
- [ ] Mermaid diagrams render
- [ ] Scroll design on home page works
- [ ] Headers properly sized (h2 > h3 > h4)

### Functionality Tests
- [ ] Search finds relevant content
- [ ] All internal links work
- [ ] All external links work (if any)
- [ ] Code copy buttons work
- [ ] Tabs switch correctly
- [ ] Admonitions expand/collapse
- [ ] Mobile menu works
- [ ] Print view acceptable

### Content Tests
- [ ] No emojis in story prose
- [ ] Technical accuracy verified
- [ ] Code examples are complete
- [ ] API docs match implementation
- [ ] Diagrams accurately represent code

### Cross-Browser Tests
- [ ] Chrome
- [ ] Firefox
- [ ] Edge
- [ ] Safari (if available)
- [ ] Mobile browser

### Performance Tests
- [ ] Page load < 2 seconds
- [ ] Search response < 500ms
- [ ] Images optimized (< 500KB each)
```

---

## 📋 Phase 6: Deployment

### 6.1 Pre-Deployment Checks

**Validation:**
```yaml
pre_deployment:
  - check: build_successful
    status: required
  - check: no_broken_links
    status: required
  - check: images_optimized
    status: recommended
  - check: accessibility_score > 90
    status: recommended
  - check: lighthouse_performance > 80
    status: recommended
```

### 6.2 Deploy to GitHub Pages

**Manual Deployment:**
```bash
# Deploy to gh-pages branch
mkdocs gh-deploy --force

# Verify deployment
echo "Visit: https://asifhussain60.github.io/CORTEX/"
```

**Automated Deployment (if --deploy=true):**
```python
def auto_deploy():
    # Pre-flight checks
    if not all_checks_pass():
        print("❌ Pre-deployment checks failed")
        return False
    
    # Deploy
    result = subprocess.run(
        ["mkdocs", "gh-deploy", "--force"],
        capture_output=True
    )
    
    if result.returncode != 0:
        print(f"❌ Deployment failed: {result.stderr}")
        return False
    
    print("✅ Deployed to GitHub Pages")
    print("🌐 URL: https://asifhussain60.github.io/CORTEX/")
    
    # Wait for GitHub Pages to build (usually 1-2 minutes)
    time.sleep(120)
    
    # Verify live site
    verify_live_site()
    
    return True
```

### 6.3 Post-Deployment Verification

**Automated Verification:**
```python
def verify_live_site():
    base_url = "https://asifhussain60.github.io/CORTEX/"
    
    checks = [
        verify_page_loads(base_url),
        verify_search_works(base_url),
        verify_navigation(base_url),
        verify_images_load(base_url),
        verify_no_404s(base_url)
    ]
    
    if all(checks):
        print("✅ Live site verified")
    else:
        print("⚠️ Some checks failed - review manually")
```

---

## 📋 Phase 7: Report Generation

### 7.1 Create Update Report

**Template:**
```markdown
# Documentation Refresh Report
**Date:** [Current Date]  
**Duration:** [Elapsed Time]  
**Triggered By:** #file:prompts/user/refresh-docs.md

---

## � Summary

**Git Analysis:**
- Commits analyzed: [count]
- Date range: [start] to [end]
- Files changed: [count]
- Feature commits: [count]

**Documentation Updates:**
- Story updates: [count]
- Technical docs updated: [count]
- New technical docs: [count]
- Diagrams generated: [count]
- Gemini prompts created: [count]

**Build & Review:**
- Build status: ✅ SUCCESS
- Local server: 🚀 LAUNCHED at http://localhost:8000
- Browser: ✅ OPENED for review
- Ready for manual review before deployment

**Deployment:**
- Auto-deploy: ⏭️ SKIPPED (manual review first)
- Next step: Review at localhost, then deploy with --deploy=true if satisfied

---

## 📝 Changes Made

### Story Updates: "The Awakening of CORTEX"
**File:** `docs\story\CORTEX-STORY\Awakening Of CORTEX.md`

| Chapter | Update | Lines Changed | Style |
|---------|--------|---------------|-------|
| Chapter 2 | Added agent specialization narrative | +45 | First person, no code |
| Chapter 4 | Updated protection layer story | +32 | First person, no code |

**Compliance:**
- ✅ 95% story / 5% technical ratio maintained
- ✅ No code blocks or technical stats
- ✅ First person "I" used consistently

### Technical Documentation
**File:** `docs\story\CORTEX-STORY\Technical-CORTEX.md`

| Section | Action | Status | Details |
|---------|--------|--------|---------|
| Agent System | Updated | ✅ Complete | Added code examples, API refs |
| Protection Layers | Updated | ✅ Complete | Added architecture diagrams |
| Context Intelligence | Created | ✅ Complete | Full technical specification |

**Compliance:**
- ✅ Granular technical details included
- ✅ Code examples functional and tested
- ✅ Performance metrics documented

### Image Prompts
**File:** `docs\story\CORTEX-STORY\Image-Prompts.md`

| Prompt ID | Feature | Diagram Type | Status |
|-----------|---------|--------------|--------|
| IMG-20251108-001 | Agent routing system | Flowchart | ✅ Added |
| IMG-20251108-002 | Protection layers | Schematic | ✅ Added |
| IMG-20251108-003 | Context intelligence | Architecture | ✅ Added |

**Compliance:**
- ✅ Prompts appended (existing prompts preserved)
- ✅ Based on Technical-CORTEX.md content
- ✅ Gothic cyberpunk technical style
- ✅ Placement locations specified

### History Updates
**File:** `docs\project\History.md`

| Date | Milestone | Status |
|------|-----------|--------|
| 2025-11-08 | Documentation refresh system | ✅ Added |
| 2025-11-07 | Agent specialization complete | ✅ Added |

**Compliance:**
- ✅ First person "I" used throughout
- ✅ Chronological order maintained
- ✅ Technical details documented

### Diagrams & Images
| Type | Count | Location |
|------|-------|----------|
| Mermaid diagrams | 3 | Technical-CORTEX.md |
| Gemini prompts (new) | 3 | Image-Prompts.md |
| Generated images | 0 | Awaiting AI generation |

---

## ✅ Validation Results

**Build:**
- Clean build: ✅ PASS
- Build time: 12.3 seconds
- Warnings: 0
- Errors: 0

**Testing:**
- Links validated: ✅ PASS (247/247)
- Images validated: ✅ PASS (23/23)
- Mermaid rendering: ✅ PASS (15/15)
- Search index: ✅ PASS
- Accessibility: ✅ PASS (score: 94/100)

**Deployment:**
- GitHub Pages: ✅ DEPLOYED
- Live site verified: ✅ PASS
- Response time: 1.2s (< 2s target)

---

## 🎯 Next Actions

1. **Review new Gemini prompts** in `cortex-gemini-image-prompts.md`
2. **Generate AI images** using the prompts
3. **Place images** in documentation (paths provided in prompts)
4. **Monitor live site** for any issues
5. **Schedule next refresh** in [timeframe]

---

## 📊 Metrics

**Documentation Completeness:**
- Story: 100% ✅
- Architecture docs: 95% ✅
- API reference: 78% 🟡 (in progress)
- Guides: 85% ✅

**Quality Scores:**
- Technical accuracy: 98/100
- Readability: 92/100
- Visual appeal: 89/100
- Accessibility: 94/100

---

**Report Generated:** [Timestamp]  
**CORTEX Version:** v5.0  
**Next Refresh:** [Recommended date]

---
```

### 7.2 Save Report

**CORTEX Action:**
```python
def save_refresh_report(report):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"docs-refresh-report-{timestamp}.md"
    
    # Save to reports directory
    save_to_file(
        path=f"reports/{filename}",
        content=report
    )
    
    # Also update latest report
    save_to_file(
        path="reports/latest-refresh-report.md",
        content=report
    )
    
    print(f"📋 Report saved: reports/{filename}")
```

---

## 🎨 Enhancement Features

### Enhancement 1: Smart Content Analysis

**Analyze Documentation Quality:**
```python
def analyze_doc_quality(doc_path):
    content = read_file(doc_path)
    
    metrics = {
        "readability": calculate_readability(content),
        "completeness": check_completeness(content),
        "technical_accuracy": verify_against_code(content),
        "example_coverage": count_code_examples(content),
        "link_health": validate_links(content),
        "image_usage": analyze_images(content)
    }
    
    suggestions = generate_improvement_suggestions(metrics)
    
    return {
        "metrics": metrics,
        "score": calculate_overall_score(metrics),
        "suggestions": suggestions
    }
```

### Enhancement 2: Automated Screenshot Generation

**Generate Screenshots of UI:**
```python
def generate_screenshots():
    """Use Playwright to capture UI screenshots"""
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Capture key pages
        screenshots = [
            ("home", "http://localhost:8000/"),
            ("story-ch1", "http://localhost:8000/story/chapter-1/"),
            ("architecture", "http://localhost:8000/architecture/"),
            # ... etc
        ]
        
        for name, url in screenshots:
            page.goto(url)
            page.screenshot(
                path=f"docs/assets/screenshots/{name}.png",
                full_page=True
            )
        
        browser.close()
```

### Enhancement 3: Intelligent Cross-Referencing

**Automatically Add "See Also" Links:**
```python
def add_cross_references(doc_path):
    content = read_file(doc_path)
    keywords = extract_keywords(content)
    
    # Find related documents
    related_docs = []
    for other_doc in all_docs():
        if has_similar_keywords(other_doc, keywords):
            related_docs.append(other_doc)
    
    # Add "See Also" section if not exists
    if "## See Also" not in content:
        see_also = generate_see_also_section(related_docs)
        content = append_section(content, see_also)
        save_file(doc_path, content)
```

### Enhancement 4: Version Comparison

**Show What Changed Since Last Refresh:**
```python
def compare_with_previous_version():
    current_docs = snapshot_docs()
    previous_docs = load_snapshot("last_refresh")
    
    diff = {
        "added": [],
        "modified": [],
        "deleted": [],
        "moved": []
    }
    
    for doc in current_docs:
        if doc not in previous_docs:
            diff["added"].append(doc)
        elif doc.content != previous_docs[doc].content:
            diff["modified"].append({
                "doc": doc,
                "lines_changed": calculate_diff(doc, previous_docs[doc])
            })
    
    return diff
```

### Enhancement 5: Documentation Health Dashboard

**Generate HTML Dashboard:**
```html
<!-- Auto-generated dashboard -->
<!DOCTYPE html>
<html>
<head>
    <title>CORTEX Documentation Health</title>
</head>
<body>
    <h1>Documentation Health Dashboard</h1>
    
    <div class="metric-card">
        <h2>Overall Score</h2>
        <div class="score">92/100</div>
    </div>
    
    <div class="metric-card">
        <h2>Coverage</h2>
        <div class="progress-bar">
            <div class="progress" style="width: 95%">95%</div>
        </div>
    </div>
    
    <div class="metric-card">
        <h2>Recent Updates</h2>
        <ul>
            <li>Chapter 2 updated (2 hours ago)</li>
            <li>API docs added (5 hours ago)</li>
            <li>3 diagrams generated (1 day ago)</li>
        </ul>
    </div>
    
    <!-- More metrics... -->
</body>
</html>
```

### Enhancement 6: AI-Powered Summaries

**Generate Executive Summaries:**
```python
def generate_executive_summary(doc_path):
    content = read_file(doc_path)
    
    # Use Gemini API to generate summary
    summary = gemini_api.generate_summary(
        content=content,
        style="executive",
        max_length=200
    )
    
    # Add to document
    insert_summary_box(doc_path, summary)
```

### Enhancement 7: Automated Glossary Building

**Extract and Define Terms:**
```python
def build_glossary():
    all_docs = scan_documentation()
    technical_terms = extract_technical_terms(all_docs)
    
    glossary = {}
    for term in technical_terms:
        definition = generate_definition(term, all_docs)
        usage_examples = find_usage_examples(term, all_docs)
        
        glossary[term] = {
            "definition": definition,
            "examples": usage_examples,
            "see_also": find_related_terms(term)
        }
    
    # Generate glossary page
    create_glossary_page(glossary)
```

### Enhancement 8: Changelog Generation

**Auto-Generate Changelog:**
```markdown
# Documentation Changelog

## [2025-11-07] - Documentation Refresh

### Added
- New section on Tier 3 context intelligence
- API reference for governance engine
- 3 new Mermaid diagrams

### Changed
- Updated "The Awakening" Chapter 2 with agent details
- Enhanced protection system documentation
- Improved code examples in all API docs

### Fixed
- Broken links in architecture section
- Image sizing issues in mobile view
- Mermaid diagram rendering in dark mode

### Deprecated
- Old KDS references (moved to legacy section)
```

---

## 📊 Parameters & Configuration

### Command Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--since` | date | "last_refresh" | Start date for git analysis |
| `--depth` | enum | "smart" | Analysis depth: quick/smart/full |
| `--deploy` | bool | false | Auto-deploy to GitHub Pages |
| `--report` | bool | true | Generate refresh report |
| `--test` | bool | true | Run automated tests |
| `--verbose` | bool | false | Show detailed progress |

### Configuration File

**Create `cortex.docs.config.yaml`:**
```yaml
documentation:
  refresh:
    # Git analysis
    git:
      default_since: "last_refresh"  # or specific date
      include_branches: ["main", "cortex-migration"]
      exclude_paths: ["_archive/*", "backup/*"]
    
    # Documentation structure
    story:
      path: "docs/story/CORTEX-STORY/Awakening Of CORTEX.md"
      auto_update: true
      style:
        ratio: "95% story, 5% concepts"
        perspective: "first_person"  # Use "I"
        allow_code_blocks: false
        allow_technical_stats: false
        maintain_emotional_arc: true
        weave_capabilities_in_narrative: true
    
    technical:
      path: "docs/story/CORTEX-STORY/Technical-CORTEX.md"
      auto_update: true
      style:
        granularity: "detailed"
        include_code_examples: true
        include_metrics: true
        include_api_references: true
        include_architecture_diagrams: true
      additional_paths:
        - "docs/architecture/"
        - "docs/tiers/"
        - "docs/agents/"
        - "docs/api/"
      template: "docs/templates/technical-doc-template.md"
      require_examples: true
      require_api_ref: true
    
    image_prompts:
      path: "docs/story/CORTEX-STORY/Image-Prompts.md"
      auto_update: true
      mode: "append_only"  # Never replace existing prompts
      style: "gothic_cyberpunk_technical"
      based_on: "Technical-CORTEX.md"
      image_dir: "docs/assets/images/"
      filename_convention: "cortex-[feature]-[type].png"
    
    history:
      path: "docs/project/History.md"
      auto_update: true
      style:
        perspective: "first_person"  # Use "I"
        chronological: true
        include_technical_details: true
        include_motivation: true
        include_challenges: true
        include_outcomes: true
        no_character_names: true  # No Asifinstein, etc.
    
    images:
      image_dir: "docs/assets/images/"
      filename_convention: "cortex-[feature]-[type].png"
    
    diagrams:
      mermaid:
        auto_generate: true
        theme: "dark"
      formats: ["mermaid", "plantuml"]
    
    # Testing
    testing:
      link_validation: true
      image_validation: true
      mermaid_rendering: true
      accessibility_check: true
      min_accessibility_score: 90
    
    # Deployment
    deployment:
      auto_deploy: false  # Require manual approval
      branch: "gh-pages"
      verify_after_deploy: true
    
    # Reporting
    reporting:
      generate_report: true
      report_dir: "reports/"
      keep_history: true
      max_reports: 50  # Keep last 50 refresh reports
```

---

## 🎯 Usage Examples

### Example 1: Quick Refresh (Default)
```markdown
#file:prompts/user/refresh-docs.md

Refresh CORTEX documentation based on recent development changes.
```

**What Happens:**
1. ✅ Analyzes git changes since last refresh
2. ✅ Smart depth (only update what changed)
3. ✅ Builds documentation
4. ✅ **Launches mkdocs serve at http://localhost:8000**
5. ✅ **Opens browser automatically for review**
6. ✅ Generates report
7. ⏭️ No auto-deploy (requires manual approval after review)

**Next Steps After Review:**
- ✅ If satisfied: Run with `--deploy=true` or manually deploy
- 🔄 If changes needed: Press Ctrl+C, make edits, run refresh again

---

### Example 2: Full Refresh with Deployment
```markdown
#file:prompts/user/refresh-docs.md --since="2025-11-01" --depth=full --deploy=true

Full documentation refresh from November 1st and deploy to GitHub Pages.
```

**What Happens:**
1. Analyzes ALL changes since Nov 1
2. Full depth analysis (review everything)
3. Updates story, technical docs, diagrams
4. Generates new Gemini prompts if needed
5. Builds and tests locally
6. Auto-deploys to GitHub Pages
7. Generates comprehensive report

---

### Example 3: Quick Check (No Changes)
```markdown
#file:prompts/user/refresh-docs.md --depth=quick --test=false

Quick check if documentation needs updates.
```

**What Happens:**
1. Quick git analysis (last 5 commits)
2. Report gaps only
3. No actual updates
4. No testing
5. Quick report of what needs attention

---

## ✅ Success Criteria

**Documentation Refresh Complete When:**

**Story Files:**
- ✅ `Awakening Of CORTEX.md` updated with recent features (95% story, 5% high-level concepts)
- ✅ First person "I" used consistently in story (no character names)
- ✅ No code blocks or technical stats in narrative
- ✅ Emotional arc and vision maintained

**Technical Files:**
- ✅ `Technical-CORTEX.md` updated with granular technical details
- ✅ All recent features documented with code examples
- ✅ Architecture diagrams accurate and complete
- ✅ API references match implementation
- ✅ Performance metrics included

**Image Files:**
- ✅ `Image-Prompts.md` contains new AI generation prompts
- ✅ Prompts based on Technical-CORTEX.md content
- ✅ Existing prompts preserved (append-only)
- ✅ Placement locations specified for each prompt
- ✅ Gothic cyberpunk technical style maintained

**History Files:**
- ✅ `History.md` updated with latest technical milestones
- ✅ First person "I" used throughout history entries
- ✅ Chronological order maintained
- ✅ Technical decisions and challenges documented

**Build & Deployment:**
- ✅ No broken links
- ✅ All images optimized and placed in `/docs/assets/images/`
- ✅ Build successful
- ✅ Tests pass (if enabled)
- ✅ Report generated
- ✅ Deployed (if requested)

**Quality Checks:**
- ✅ No duplicate content between story and technical docs
- ✅ Cross-references accurate
- ✅ Technical accuracy verified against codebase
- ✅ Image filenames follow convention (`cortex-[feature]-[type].png`)
- ✅ All four core files synchronized and consistent

---

## 🔄 Integration with CORTEX Brain

**Brain Learning:**
```yaml
# Logged to events.jsonl
event:
  type: documentation_refresh
  timestamp: 2025-11-07T14:30:00Z
  duration: 45 minutes
  files_updated: 12
  diagrams_created: 3
  deployment: true
  
# Updates Tier 2 knowledge
pattern:
  name: documentation_refresh_workflow
  confidence: 0.95
  success_count: 12
  average_duration: 42 minutes
  
# Updates Tier 3 metrics
metrics:
  last_docs_refresh: 2025-11-07T14:30:00Z
  docs_health_score: 92/100
  docs_completeness: 95%
```

---

## 📚 Related Commands

- `#file:prompts/user/cortex.md` - Main CORTEX entry point
- `#file:prompts/user/test-cortex.md` - Run CORTEX tests
- `#file:prompts/user/deploy-docs.md` - Deploy docs only (no refresh)
- `#file:prompts/user/validate-docs.md` - Validate docs health

## 📖 Target Files Reference

**Core Documentation Files:**
1. **Story:** `docs\story\CORTEX-STORY\Awakening Of CORTEX.md`
2. **Technical:** `docs\story\CORTEX-STORY\Technical-CORTEX.md`
3. **Image Prompts:** `docs\story\CORTEX-STORY\Image-Prompts.md`
4. **History:** `docs\project\History.md`

**Supporting Files:**
- Images: `docs\assets\images\` (generated from prompts)
- Templates: `docs\templates\technical-doc-template.md`
- Additional technical docs: `docs\architecture\`, `docs\tiers\`, `docs\agents\`, `docs\api\`

**Integration:**
- Story file references images from assets folder
- Image prompts based on technical documentation
- History tracks when features were added to both story and technical docs
- Collapsed version combines story narrative with generated images

---

**Status:** 🎯 READY TO USE  
**Version:** 1.0  
**Last Updated:** November 7, 2025

---

**END OF DOCUMENTATION REFRESH COMMAND**
