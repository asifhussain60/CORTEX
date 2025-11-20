# DALL-E Prompt: Documentation Generation Pipeline

## Visual Composition
- **Layout:** Left-to-right horizontal pipeline with vertical quality gates
- **Orientation:** Landscape (16:9 aspect ratio)
- **Flow Direction:** Source content → Processing stages → Multiple output formats
- **Quality Gates:** Vertical validation checkpoints between stages

## Color Palette
- **Source Stage:** Teal (#20c997) - Content collection
- **Analysis Stage:** Blue (#4d96ff) - Content processing
- **Generation Stage:** Purple (#9b59b6) - Document creation
- **Validation Stage:** Orange (#ff8c42) - Quality checks
- **Distribution Stage:** Green (#28a745) - Output delivery
- **Quality Gates:** Red (#dc3545) for failures, Green (#28a745) for passes
- **Background:** White (#ffffff) with subtle document grid pattern
- **Arrows:** Gradient flow from stage color to next stage color

## Components & Elements

### Stage 1: Source Content Collection (Teal)
- **Position:** 5% from left
- **Visual:** Rounded rectangle (200px x 150px)
- **Label:** "CONTENT SOURCES"
- **Icon:** Multiple document stack icon
- **Sub-components:**
  - "Code Files" (file icon, Python/JS logos)
  - "README.md" (markdown icon)
  - "API Docs" (swagger/openapi icon)
  - "Docstrings" (comment block icon)
  - "Type Hints" (type annotation symbol)
- **Input:** Multiple colored arrows from top (representing various sources)
- **Progress:** Loading bar showing "Scanning 127 files..."

### Stage 2: Content Analysis (Blue)
- **Position:** 25% from left
- **Visual:** Rounded rectangle (220px x 160px)
- **Label:** "ANALYSIS & EXTRACTION"
- **Icon:** Magnifying glass over code
- **Sub-components:**
  - "Parse Structure" (AST tree icon)
  - "Extract Metadata" (tag icon)
  - "Link Analysis" (network graph icon)
  - "Relationship Mapping" (flowchart icon)
  - "Cross-References" (link chain icon)
- **Processing:** Animated gear icon indicating active processing
- **Output:** Structured data flow to next stage

### Quality Gate 1: Structure Validation
- **Position:** Between Analysis and Generation (42% from left)
- **Visual:** Vertical bar with checkpoint indicator
- **Label:** "STRUCTURE CHECK"
- **Icon:** Shield with checkmark/X
- **Checks:**
  - "Complete Metadata?" ✓
  - "Valid Links?" ✓
  - "Orphaned Sections?" ⚠
- **Status Display:** Traffic light (green/yellow/red)
- **Path Split:** 
  - Green arrow → Continue to Generation
  - Red arrow → Loop back to Analysis

### Stage 3: Document Generation (Purple)
- **Position:** 50% from left
- **Visual:** Rounded rectangle (240px x 170px)
- **Label:** "DOCUMENT GENERATION"
- **Icon:** Document with magic wand
- **Sub-components:**
  - "Markdown Rendering" (MD icon)
  - "Mermaid Diagrams" (flowchart preview)
  - "Code Examples" (code block with syntax highlight)
  - "Navigation Tree" (tree structure)
  - "Search Index" (magnifying glass + index icon)
  - "Cross-Reference Links" (hyperlink icon)
- **Templates:** Small thumbnail previews of doc templates
- **Status:** "Generating 43 pages..."

### Quality Gate 2: Content Validation
- **Position:** After Generation (67% from left)
- **Visual:** Vertical bar (taller than Gate 1)
- **Label:** "QUALITY ASSURANCE"
- **Icon:** Clipboard with checklist
- **Validation Checks:**
  - "Broken Links?" ✓ Pass (0 found)
  - "Missing Images?" ⚠ Warning (2 missing)
  - "Accessibility (WCAG AA)?" ✓ Pass
  - "Spelling/Grammar?" ✓ Pass
  - "Code Syntax?" ✓ Pass
- **Status Panel:** 
  - "✓ 95% checks passed"
  - "⚠ 2 warnings"
  - "✗ 0 critical errors"

### Stage 4: Multi-Format Distribution (Green)
- **Position:** 80% from left
- **Visual:** Rounded rectangle (200px x 180px)
- **Label:** "OUTPUT FORMATS"
- **Icon:** Multiple document types fanning out
- **Output Formats (Branching Paths):**
  - **HTML/MkDocs** (top branch)
    - Icon: Globe icon
    - Label: "docs.myproject.com"
    - Status: "✓ Built in 12.4s"
  - **PDF** (middle branch)
    - Icon: PDF document icon
    - Label: "documentation.pdf"
    - Status: "✓ 247 pages"
  - **Markdown** (middle-low branch)
    - Icon: MD file icon
    - Label: "docs/*.md"
    - Status: "✓ Raw files"
  - **JSON API** (bottom branch)
    - Icon: JSON icon
    - Label: "api/docs.json"
    - Status: "✓ Searchable"

### Final Stage: Deployment & Access (Right Edge)
- **Position:** 95% from left
- **Visual:** Cloud icon with multiple access points
- **Label:** "LIVE DOCUMENTATION"
- **Access Methods:**
  - "Web Browser" (Chrome icon)
  - "VS Code Extension" (VS Code icon)
  - "API Client" (Postman/curl icon)
  - "CI/CD Pipeline" (GitHub Actions icon)
- **Metrics Display:**
  - "Last Updated: 2 min ago"
  - "Build Time: 18.7s"
  - "Size: 12.4 MB"

## Pipeline Infrastructure

### Progress Tracker (Top)
- **Position:** Spanning 10-90% of width, at 15% height
- **Visual:** Horizontal progress bar with stage markers
- **Current Stage:** Highlighted/glowing segment
- **Completed Stages:** Green checkmarks
- **Pending Stages:** Gray/unfilled
- **Overall Progress:** "Stage 3 of 4 (75%)"

### Error Recovery System (Bottom)
- **Position:** Bottom 10% of canvas
- **Visual:** Red maintenance track
- **Label:** "ERROR RECOVERY & RETRY"
- **Components:**
  - "Error Logger" (file icon with red X)
  - "Rollback Handler" (undo arrow icon)
  - "Retry Queue" (circular arrows with "3x max")
- **Connection:** Red arrows from quality gates to recovery system

### Live Metrics Panel (Bottom-Right)
- **Position:** 5% from bottom, 5% from right
- **Visual:** Small dashboard panel (180px x 120px)
- **Label:** "PIPELINE METRICS"
- **Metrics:**
  - "⏱ Total Time: 18.7s"
  - "📄 Pages: 43"
  - "🔗 Links: 287 (0 broken)"
  - "📊 Diagrams: 12"
  - "✓ Quality: 95%"

## Data Flow Visualization

### Primary Flow (Green Path)
- **Style:** Solid arrows with gradient colors
- **Width:** 4px
- **Flow Indicators:** Small animated dots traveling along arrows
- **Labels:** Data packet counts ("127 files", "43 pages")

### Quality Gate Decisions
- **Pass Path:** Bright green arrows (3px solid)
- **Fail Path:** Red dashed arrows looping back
- **Warning Path:** Orange arrows with caution symbol

### Parallel Processing (Stage 3)
- **Visual:** Stage 3 splits into 3 parallel sub-processes
- **Representation:** Multiple thin arrows branching out
- **Convergence:** Arrows merge before Quality Gate 2

## Typography & Labels

### Stage Headers
- **Font:** Bold sans-serif, 20pt
- **Color:** White on colored stage background
- **Position:** Top of each stage box
- **Style:** ALL CAPS

### Sub-component Labels
- **Font:** Regular sans-serif, 11pt
- **Color:** Dark gray (#2c3e50)
- **Position:** Inside stages, vertically stacked
- **Icon Prefix:** 16px icon before each label

### Quality Gate Labels
- **Font:** Bold sans-serif, 16pt
- **Color:** Black (#000000)
- **Position:** On vertical bars
- **Orientation:** Vertical text (rotated 90°)

### Metrics Labels
- **Font:** Mono sans-serif, 10pt
- **Color:** Dark gray (#495057)
- **Format:** "Key: Value" with emoji prefix

## Technical Accuracy

### Documentation Sources
- Code files (Python, JavaScript, TypeScript)
- README and markdown files
- API documentation (OpenAPI/Swagger)
- Inline docstrings and comments
- Type annotations and interfaces

### Analysis Process
- Abstract Syntax Tree (AST) parsing
- Metadata extraction (authors, versions, licenses)
- Link and cross-reference resolution
- Relationship mapping between modules/classes
- Dependency graph generation

### Generation Process
- Markdown rendering with extensions
- Mermaid diagram generation from code
- Code syntax highlighting (language-specific)
- Navigation tree from document structure
- Full-text search index creation

### Quality Assurance
- Broken link detection (internal + external)
- WCAG AA accessibility compliance
- Spelling and grammar checks
- Code syntax validation
- Image reference validation

### Output Formats
- **HTML/MkDocs:** Static site generator output
- **PDF:** Print-ready documentation
- **Markdown:** Raw source files
- **JSON API:** Searchable structured data

## Style & Aesthetic
- **Design Language:** Modern DevOps pipeline meets documentation workflow
- **Detail Level:** High - show internal processes and metrics
- **Visual Metaphor:** Manufacturing pipeline + content publishing
- **Clean:** Professional documentation tooling aesthetic
- **Informative:** Metrics and status visible at all stages

## Mood & Atmosphere
- **Automated & Efficient:** Fast, reliable doc generation
- **Quality-Focused:** Multiple validation gates ensure accuracy
- **Transparent:** Clear visibility into process and metrics
- **Developer-Friendly:** Technical but approachable

## Output Specifications
- **Resolution:** 2560x1440 (2K)
- **Format:** PNG with transparency
- **DPI:** 300
- **Accessibility:** WCAG AA contrast
- **File Size:** <550KB

## Usage Context
- **Developer Documentation:** Explaining doc generation workflow
- **CI/CD Documentation:** Automated documentation pipelines
- **Tool Documentation:** How doc generators work
- **Process Documentation:** Documentation best practices

## DALL-E Generation Instruction

**Primary Prompt:**
"Create professional horizontal documentation generation pipeline diagram. Left-to-right flow with 4 main stages as rounded rectangles (200-240px x 150-180px): Content Sources (teal #20c997), Analysis (blue #4d96ff), Generation (purple #9b59b6), Distribution (green #28a745). Each stage shows internal sub-components with icons. Two vertical quality gate checkpoints between stages (red/green traffic lights). Progress tracker bar at top showing 75% complete. Error recovery system at bottom (red maintenance track). Final cloud deployment stage at right with 4 access methods (web, VS Code, API, CI/CD). Live metrics panel bottom-right showing build time 18.7s, 43 pages, 287 links, 95% quality score. Show data flow arrows with animated dots. Include parallel processing split in Generation stage. Clean white background with document grid pattern. Modern DevOps pipeline aesthetic with professional documentation tooling style."

**Refinement Prompt:**
"Add more detail to quality gate checkpoints (show specific checks: broken links, accessibility, spelling). Include small thumbnail previews of document templates in Generation stage. Add animated gear icons to Analysis stage. Show traffic light status indicators (green/yellow/red) at quality gates. Include version/timestamp labels on output formats. Add warning badge (⚠ 2 warnings) on Quality Gate 2. Make data flow arrows gradient-colored (blend from stage to stage colors)."