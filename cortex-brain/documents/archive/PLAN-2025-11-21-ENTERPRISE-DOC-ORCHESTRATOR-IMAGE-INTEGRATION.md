# 🧠 CORTEX Enterprise Documentation Orchestrator - Image Integration Plan

**Plan ID:** PLAN-2025-11-21-ENTERPRISE-DOC-ORCHESTRATOR-IMAGE-INTEGRATION  
**Created:** November 21, 2025  
**Status:** Active Planning  
**Category:** Documentation Infrastructure  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.

---

## 🎯 Objective

Integrate 14 ChatGPT-generated PNG diagram images into the CORTEX Enterprise Documentation Orchestrator pipeline, organize them by category, configure MkDocs for proper display, and enhance the orchestrator to validate and reference images contextually in generated documentation.

---

## 📊 Discovery Summary

### Found Assets

**14 ChatGPT-Generated PNG Files** in `docs/images/diagrams/`

**Current Structure:**
```
docs/images/diagrams/
├── 01-tier-architecture-prompt.png
├── 02-agent-coordination-prompt.png
├── 03-information-flow-prompt.png
├── 04-conversation-tracking-prompt.png
├── 05-plugin-system-prompt.png
├── 06-brain-protection-prompt.png
├── 07-operation-pipeline-prompt.png
├── 08a-setup-orchestration-prompt.png
├── 08b-setup-orchestration-prompt.png
├── 09-documentation-generation-prompt.png
├── 10-feature-planning-prompt.png
├── 11-testing-strategy-prompt.png
├── 12-deployment-pipeline-prompt.png
├── 14-system-architecture-prompt.png
├── architectural/     (exists, empty)
├── integration/       (exists, empty)
├── operational/       (exists, empty)
└── strategic/         (exists, empty)
```

### Image-to-Component Mapping

| Image File | Category | DALL-E Prompt | Narrative | Documentation Pages |
|------------|----------|---------------|-----------|---------------------|
| 01-tier-architecture-prompt.png | Architectural | `docs/diagrams/prompts/01-*.md` | `docs/diagrams/narratives/01-*.md` | Architecture overview |
| 02-agent-coordination-prompt.png | Architectural | `docs/diagrams/prompts/02-*.md` | `docs/diagrams/narratives/02-*.md` | Agent system guide |
| 14-system-architecture-prompt.png | Architectural | `docs/diagrams/prompts/14-*.md` | `docs/diagrams/narratives/14-*.md` | System design |
| 03-information-flow-prompt.png | Integration | `docs/diagrams/prompts/03-*.md` | `docs/diagrams/narratives/03-*.md` | Data flow guide |
| 04-conversation-tracking-prompt.png | Integration | `docs/diagrams/prompts/04-*.md` | `docs/diagrams/narratives/04-*.md` | Tracking system |
| 05-plugin-system-prompt.png | Integration | `docs/diagrams/prompts/05-*.md` | `docs/diagrams/narratives/05-*.md` | Plugin architecture |
| 07-operation-pipeline-prompt.png | Operational | `docs/diagrams/prompts/07-*.md` | `docs/diagrams/narratives/07-*.md` | Operations guide |
| 08a-setup-orchestration-prompt.png | Operational | `docs/diagrams/prompts/08a-*.md` | `docs/diagrams/narratives/08a-*.md` | Setup workflow |
| 08b-setup-orchestration-prompt.png | Operational | `docs/diagrams/prompts/08b-*.md` | `docs/diagrams/narratives/08b-*.md` | Setup workflow |
| 09-documentation-generation-prompt.png | Operational | `docs/diagrams/prompts/09-*.md` | `docs/diagrams/narratives/09-*.md` | Doc generation |
| 06-brain-protection-prompt.png | Strategic | `docs/diagrams/prompts/06-*.md` | `docs/diagrams/narratives/06-*.md` | Brain protection |
| 10-feature-planning-prompt.png | Strategic | `docs/diagrams/prompts/10-*.md` | `docs/diagrams/narratives/10-*.md` | Planning system |
| 11-testing-strategy-prompt.png | Strategic | `docs/diagrams/prompts/11-*.md` | `docs/diagrams/narratives/11-*.md` | Testing strategy |
| 12-deployment-pipeline-prompt.png | Strategic | `docs/diagrams/prompts/12-*.md` | `docs/diagrams/narratives/12-*.md` | Deployment guide |

---

## 🔄 Complete Orchestrator Architecture

### All 8 Components (Including New Image Component)

#### ✅ Component 1: Mermaid Diagrams (14 diagrams)
**Status:** UNCHANGED  
**Output:** `docs/diagrams/mermaid/*.md`  
**Purpose:** Architecture, data flow, agent coordination, plugin system

#### ✅ Component 2: DALL-E Prompts (14 prompts)
**Status:** UNCHANGED  
**Output:** `docs/diagrams/prompts/*.md` (500-800 word enhanced prompts)  
**Purpose:** Visual specifications for AI image generation via ChatGPT

#### 🔄 Component 3: Image Files (14 PNG files) - **NEW INTEGRATION**
**Status:** ACTIVE INTEGRATION  
**Current Location:** `docs/images/diagrams/*.png`  
**Target Structure:**
```
docs/images/diagrams/
├── architectural/
│   ├── 01-tier-architecture-prompt.png
│   ├── 02-agent-coordination-prompt.png
│   └── 14-system-architecture-prompt.png
├── integration/
│   ├── 03-information-flow-prompt.png
│   ├── 04-conversation-tracking-prompt.png
│   └── 05-plugin-system-prompt.png
├── operational/
│   ├── 07-operation-pipeline-prompt.png
│   ├── 08a-setup-orchestration-prompt.png
│   ├── 08b-setup-orchestration-prompt.png
│   └── 09-documentation-generation-prompt.png
└── strategic/
    ├── 06-brain-protection-prompt.png
    ├── 10-feature-planning-prompt.png
    ├── 11-testing-strategy-prompt.png
    └── 12-deployment-pipeline-prompt.png
```

**MkDocs Integration:**
- Images referenced in documentation pages via relative paths
- Material theme handles responsive display
- Alt text from DALL-E prompt titles
- Organized by diagram category

#### ✅ Component 4: Narratives (14 narratives)
**Status:** UNCHANGED  
**Output:** `docs/diagrams/narratives/*.md`  
**Purpose:** Explanatory texts matching diagrams and images

#### ⚠️ Component 5: Story Component (1 story + 13 chapters)
**Status:** MASTER SOURCE RELOCATION (separate plan)  
**Output:** `docs/story/CORTEX-STORY/THE-AWAKENING-OF-CORTEX.md` + chapters/  
**Purpose:** "The Awakening of CORTEX" narrative

#### ✅ Component 6: Executive Summary
**Status:** UNCHANGED  
**Output:** `docs/EXECUTIVE-SUMMARY.md`  
**Purpose:** Complete feature list from Git analysis + YAML discovery

#### ✅ Component 7: Image Guidance
**Status:** ENHANCED (image usage examples)  
**Output:** `docs/diagrams/README.md`  
**Purpose:** Instructions for using DALL-E prompts and integrating images

#### ✅ Component 8: MkDocs Site Builder
**Status:** ENHANCED (image-aware navigation)  
**Output:** Complete static site with navigation  
**Purpose:** Compile all components into publishable documentation

---

## 📋 Implementation Plan

### Phase 1: Image Organization (30 minutes)

#### Task 1.1: Move Images to Category Folders

**PowerShell Commands:**
```powershell
# Verify category folders exist (should already exist)
$categories = @('architectural', 'integration', 'operational', 'strategic')
foreach ($cat in $categories) {
    $path = "docs\images\diagrams\$cat"
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Force -Path $path
        Write-Host "✅ Created: $path"
    } else {
        Write-Host "✅ Exists: $path"
    }
}

# Move architectural diagrams
Move-Item 'docs\images\diagrams\01-tier-architecture-prompt.png' 'docs\images\diagrams\architectural\' -Force
Move-Item 'docs\images\diagrams\02-agent-coordination-prompt.png' 'docs\images\diagrams\architectural\' -Force
Move-Item 'docs\images\diagrams\14-system-architecture-prompt.png' 'docs\images\diagrams\architectural\' -Force
Write-Host "✅ Moved 3 architectural diagrams"

# Move integration diagrams
Move-Item 'docs\images\diagrams\03-information-flow-prompt.png' 'docs\images\diagrams\integration\' -Force
Move-Item 'docs\images\diagrams\04-conversation-tracking-prompt.png' 'docs\images\diagrams\integration\' -Force
Move-Item 'docs\images\diagrams\05-plugin-system-prompt.png' 'docs\images\diagrams\integration\' -Force
Write-Host "✅ Moved 3 integration diagrams"

# Move operational diagrams
Move-Item 'docs\images\diagrams\07-operation-pipeline-prompt.png' 'docs\images\diagrams\operational\' -Force
Move-Item 'docs\images\diagrams\08a-setup-orchestration-prompt.png' 'docs\images\diagrams\operational\' -Force
Move-Item 'docs\images\diagrams\08b-setup-orchestration-prompt.png' 'docs\images\diagrams\operational\' -Force
Move-Item 'docs\images\diagrams\09-documentation-generation-prompt.png' 'docs\images\diagrams\operational\' -Force
Write-Host "✅ Moved 4 operational diagrams"

# Move strategic diagrams
Move-Item 'docs\images\diagrams\06-brain-protection-prompt.png' 'docs\images\diagrams\strategic\' -Force
Move-Item 'docs\images\diagrams\10-feature-planning-prompt.png' 'docs\images\diagrams\strategic\' -Force
Move-Item 'docs\images\diagrams\11-testing-strategy-prompt.png' 'docs\images\diagrams\strategic\' -Force
Move-Item 'docs\images\diagrams\12-deployment-pipeline-prompt.png' 'docs\images\diagrams\strategic\' -Force
Write-Host "✅ Moved 4 strategic diagrams"

Write-Host "`n✅ All 14 images organized into categories"
```

**Validation:**
```powershell
# Verify all images moved
$expected = @(
    'docs\images\diagrams\architectural\01-tier-architecture-prompt.png',
    'docs\images\diagrams\architectural\02-agent-coordination-prompt.png',
    'docs\images\diagrams\architectural\14-system-architecture-prompt.png',
    'docs\images\diagrams\integration\03-information-flow-prompt.png',
    'docs\images\diagrams\integration\04-conversation-tracking-prompt.png',
    'docs\images\diagrams\integration\05-plugin-system-prompt.png',
    'docs\images\diagrams\operational\07-operation-pipeline-prompt.png',
    'docs\images\diagrams\operational\08a-setup-orchestration-prompt.png',
    'docs\images\diagrams\operational\08b-setup-orchestration-prompt.png',
    'docs\images\diagrams\operational\09-documentation-generation-prompt.png',
    'docs\images\diagrams\strategic\06-brain-protection-prompt.png',
    'docs\images\diagrams\strategic\10-feature-planning-prompt.png',
    'docs\images\diagrams\strategic\11-testing-strategy-prompt.png',
    'docs\images\diagrams\strategic\12-deployment-pipeline-prompt.png'
)

$missing = @()
foreach ($file in $expected) {
    if (-not (Test-Path $file)) {
        $missing += $file
    }
}

if ($missing.Count -eq 0) {
    Write-Host "✅ All 14 images verified in correct locations"
} else {
    Write-Host "❌ Missing images:"
    $missing | ForEach-Object { Write-Host "   - $_" }
}
```

#### Task 1.2: Create Image Metadata Catalog

**File:** `docs/images/diagrams/IMAGE-CATALOG.yaml`

```yaml
# CORTEX Documentation Image Catalog
# Auto-generated metadata for ChatGPT-generated diagram images
# Copyright © 2024-2025 Asif Hussain. All rights reserved.

metadata:
  version: "1.0"
  last_updated: "2025-11-21"
  total_images: 14
  categories:
    - architectural
    - integration
    - operational
    - strategic

images:
  - id: "01-tier-architecture"
    file: "architectural/01-tier-architecture-prompt.png"
    title: "CORTEX Tier Architecture"
    category: architectural
    size: "1920x1080"
    aspect_ratio: "16:9"
    generation_date: "2025-11"
    prompt_file: "docs/diagrams/prompts/01-tier-architecture-prompt.md"
    narrative_file: "docs/diagrams/narratives/01-tier-architecture-narrative.md"
    mermaid_file: "docs/diagrams/mermaid/01-tier-architecture.md"
    used_in_pages:
      - "docs/architecture/tier-system.md"
      - "docs/index.md"
    alt_text: "CORTEX four-tier architecture diagram showing Tier 0 (Brain Protection), Tier 1 (Working Memory), Tier 2 (Knowledge Graph), and Tier 3 (Development Context)"

  - id: "02-agent-coordination"
    file: "architectural/02-agent-coordination-prompt.png"
    title: "Agent Coordination System"
    category: architectural
    size: "1920x1080"
    aspect_ratio: "16:9"
    generation_date: "2025-11"
    prompt_file: "docs/diagrams/prompts/02-agent-coordination-prompt.md"
    narrative_file: "docs/diagrams/narratives/02-agent-coordination-narrative.md"
    mermaid_file: "docs/diagrams/mermaid/02-agent-coordination.md"
    used_in_pages:
      - "docs/architecture/agents.md"
      - "docs/AGENTS-GUIDE.md"
    alt_text: "CORTEX agent coordination diagram showing 10 specialized agents communicating via Corpus Callosum"

  - id: "14-system-architecture"
    file: "architectural/14-system-architecture-prompt.png"
    title: "Complete System Architecture"
    category: architectural
    size: "1920x1080"
    aspect_ratio: "16:9"
    generation_date: "2025-11"
    prompt_file: "docs/diagrams/prompts/14-system-architecture-prompt.md"
    narrative_file: "docs/diagrams/narratives/14-system-architecture-narrative.md"
    mermaid_file: "docs/diagrams/mermaid/14-system-architecture.md"
    used_in_pages:
      - "docs/architecture/overview.md"
      - "docs/TECHNICAL-REFERENCE.md"
    alt_text: "CORTEX complete system architecture showing all components, data flows, and integration points"

  - id: "03-information-flow"
    file: "integration/03-information-flow-prompt.png"
    title: "Information Flow Pipeline"
    category: integration
    size: "1920x1080"
    aspect_ratio: "16:9"
    generation_date: "2025-11"
    prompt_file: "docs/diagrams/prompts/03-information-flow-prompt.md"
    narrative_file: "docs/diagrams/narratives/03-information-flow-narrative.md"
    mermaid_file: "docs/diagrams/mermaid/03-information-flow.md"
    used_in_pages:
      - "docs/integration/data-flow.md"
    alt_text: "CORTEX information flow diagram showing data movement through tiers and agents"

  - id: "04-conversation-tracking"
    file: "integration/04-conversation-tracking-prompt.png"
    title: "Conversation Tracking System"
    category: integration
    size: "1920x1080"
    aspect_ratio: "16:9"
    generation_date: "2025-11"
    prompt_file: "docs/diagrams/prompts/04-conversation-tracking-prompt.md"
    narrative_file: "docs/diagrams/narratives/04-conversation-tracking-narrative.md"
    mermaid_file: "docs/diagrams/mermaid/04-conversation-tracking.md"
    used_in_pages:
      - "docs/integration/tracking.md"
      - "docs/TRACKING-GUIDE.md"
    alt_text: "CORTEX conversation tracking system showing capture, storage, and context injection"

  - id: "05-plugin-system"
    file: "integration/05-plugin-system-prompt.png"
    title: "Plugin System Architecture"
    category: integration
    size: "1920x1080"
    aspect_ratio: "16:9"
    generation_date: "2025-11"
    prompt_file: "docs/diagrams/prompts/05-plugin-system-prompt.md"
    narrative_file: "docs/diagrams/narratives/05-plugin-system-narrative.md"
    mermaid_file: "docs/diagrams/mermaid/05-plugin-system.md"
    used_in_pages:
      - "docs/integration/plugins.md"
      - "docs/PLUGIN-SYSTEM.md"
    alt_text: "CORTEX plugin system showing extension points, lifecycle management, and plugin registry"

  - id: "07-operation-pipeline"
    file: "operational/07-operation-pipeline-prompt.png"
    title: "Operation Execution Pipeline"
    category: operational
    size: "1920x1080"
    aspect_ratio: "16:9"
    generation_date: "2025-11"
    prompt_file: "docs/diagrams/prompts/07-operation-pipeline-prompt.md"
    narrative_file: "docs/diagrams/narratives/07-operation-pipeline-narrative.md"
    mermaid_file: "docs/diagrams/mermaid/07-operation-pipeline.md"
    used_in_pages:
      - "docs/operations/pipeline.md"
      - "docs/OPERATIONS-REFERENCE.md"
    alt_text: "CORTEX operation pipeline showing request routing, module execution, and result handling"

  - id: "08a-setup-orchestration"
    file: "operational/08a-setup-orchestration-prompt.png"
    title: "Setup Orchestration (Part 1)"
    category: operational
    size: "1920x1080"
    aspect_ratio: "16:9"
    generation_date: "2025-11"
    prompt_file: "docs/diagrams/prompts/08a-setup-orchestration-prompt.md"
    narrative_file: "docs/diagrams/narratives/08a-setup-orchestration-narrative.md"
    mermaid_file: "docs/diagrams/mermaid/08a-setup-orchestration.md"
    used_in_pages:
      - "docs/operations/setup.md"
      - "docs/SETUP-GUIDE.md"
    alt_text: "CORTEX setup orchestration workflow showing environment detection and configuration"

  - id: "08b-setup-orchestration"
    file: "operational/08b-setup-orchestration-prompt.png"
    title: "Setup Orchestration (Part 2)"
    category: operational
    size: "1920x1080"
    aspect_ratio: "16:9"
    generation_date: "2025-11"
    prompt_file: "docs/diagrams/prompts/08b-setup-orchestration-prompt.md"
    narrative_file: "docs/diagrams/narratives/08b-setup-orchestration-narrative.md"
    mermaid_file: "docs/diagrams/mermaid/08b-setup-orchestration.md"
    used_in_pages:
      - "docs/operations/setup.md"
      - "docs/SETUP-GUIDE.md"
    alt_text: "CORTEX setup orchestration workflow showing brain initialization and validation"

  - id: "09-documentation-generation"
    file: "operational/09-documentation-generation-prompt.png"
    title: "Documentation Generation Pipeline"
    category: operational
    size: "1920x1080"
    aspect_ratio: "16:9"
    generation_date: "2025-11"
    prompt_file: "docs/diagrams/prompts/09-documentation-generation-prompt.md"
    narrative_file: "docs/diagrams/narratives/09-documentation-generation-narrative.md"
    mermaid_file: "docs/diagrams/mermaid/09-documentation-generation.md"
    used_in_pages:
      - "docs/operations/documentation.md"
    alt_text: "CORTEX documentation generation showing Enterprise Orchestrator pipeline stages"

  - id: "06-brain-protection"
    file: "strategic/06-brain-protection-prompt.png"
    title: "Brain Protection Rules (Tier 0)"
    category: strategic
    size: "1920x1080"
    aspect_ratio: "16:9"
    generation_date: "2025-11"
    prompt_file: "docs/diagrams/prompts/06-brain-protection-prompt.md"
    narrative_file: "docs/diagrams/narratives/06-brain-protection-narrative.md"
    mermaid_file: "docs/diagrams/mermaid/06-brain-protection.md"
    used_in_pages:
      - "docs/architecture/brain-protection.md"
    alt_text: "CORTEX brain protection rules showing SKULL principles and validation layers"

  - id: "10-feature-planning"
    file: "strategic/10-feature-planning-prompt.png"
    title: "Interactive Feature Planning"
    category: strategic
    size: "1920x1080"
    aspect_ratio: "16:9"
    generation_date: "2025-11"
    prompt_file: "docs/diagrams/prompts/10-feature-planning-prompt.md"
    narrative_file: "docs/diagrams/narratives/10-feature-planning-narrative.md"
    mermaid_file: "docs/diagrams/mermaid/10-feature-planning.md"
    used_in_pages:
      - "docs/planning/feature-planning.md"
      - "docs/HELP-PLAN-FEATURE.md"
    alt_text: "CORTEX feature planning workflow showing interactive Q&A, phase breakdown, and Work Planner integration"

  - id: "11-testing-strategy"
    file: "strategic/11-testing-strategy-prompt.png"
    title: "Testing Strategy Framework"
    category: strategic
    size: "1920x1080"
    aspect_ratio: "16:9"
    generation_date: "2025-11"
    prompt_file: "docs/diagrams/prompts/11-testing-strategy-prompt.md"
    narrative_file: "docs/diagrams/narratives/11-testing-strategy-narrative.md"
    mermaid_file: "docs/diagrams/mermaid/11-testing-strategy.md"
    used_in_pages:
      - "docs/testing/strategy.md"
    alt_text: "CORTEX testing strategy showing pragmatic testing approach, skip-if-needed policy, and quality thresholds"

  - id: "12-deployment-pipeline"
    file: "strategic/12-deployment-pipeline-prompt.png"
    title: "Deployment & Publishing Pipeline"
    category: strategic
    size: "1920x1080"
    aspect_ratio: "16:9"
    generation_date: "2025-11"
    prompt_file: "docs/diagrams/prompts/12-deployment-pipeline-prompt.md"
    narrative_file: "docs/diagrams/narratives/12-deployment-pipeline-narrative.md"
    mermaid_file: "docs/diagrams/mermaid/12-deployment-pipeline.md"
    used_in_pages:
      - "docs/deployment/pipeline.md"
    alt_text: "CORTEX deployment pipeline showing build, validation, GitHub Pages publishing, and rollback procedures"

# Category Statistics
statistics:
  architectural: 3
  integration: 3
  operational: 4
  strategic: 4
```

---

### Phase 2: MkDocs Integration (45 minutes)

#### Task 2.1: Update mkdocs.yml Navigation

**Enhancement:** Add image-centric documentation pages to navigation.

```yaml
# Enhanced navigation with image-integrated pages
nav:
  - Home: index.md
  - The CORTEX Story:
      - Story Home: story/CORTEX-STORY/THE-AWAKENING-OF-CORTEX.md
      # ... existing chapters ...
  - Architecture:
      - Overview: architecture/overview.md
      - Tier System: architecture/tier-system.md
      - Agent Coordination: architecture/agents.md
      - Brain Protection: architecture/brain-protection.md
  - Integration:
      - Data Flow: integration/data-flow.md
      - Conversation Tracking: integration/tracking.md
      - Plugin System: integration/plugins.md
  - Operations:
      - Pipeline: operations/pipeline.md
      - Setup Guide: operations/setup.md
      - Documentation: operations/documentation.md
  - Planning:
      - Feature Planning: planning/feature-planning.md
  - Testing:
      - Strategy: testing/strategy.md
  - Deployment:
      - Pipeline: deployment/pipeline.md
```

#### Task 2.2: Generate Documentation Pages with Images

**Template for Image-Enhanced Pages:**

**Example:** `docs/architecture/tier-system.md`

```markdown
# CORTEX Tier Architecture

![CORTEX Tier Architecture](../images/diagrams/architectural/01-tier-architecture-prompt.png)

*Figure 1: CORTEX four-tier architecture showing intelligence layers from Tier 0 (Brain Protection) to Tier 3 (Development Context)*

## Overview

CORTEX uses a four-tier intelligence architecture inspired by cognitive science:

[Narrative content from 01-tier-architecture-narrative.md extracted here]

## Tier 0: Brain Protection (SKULL Rules)

The foundational layer that ensures CORTEX maintains integrity...

## Tier 1: Working Memory (Conversation Context)

Short-term memory system that tracks recent conversations...

## Tier 2: Knowledge Graph (Pattern Learning)

Long-term memory that learns from past interactions...

## Tier 3: Development Context (Project-Specific)

Active context about current development work...

## Technical Implementation

[Technical details]

## See Also

- [Mermaid Diagram](../diagrams/mermaid/01-tier-architecture.md) - Interactive diagram
- [DALL-E Prompt](../diagrams/prompts/01-tier-architecture-prompt.md) - Image generation prompt
- [System Architecture](./overview.md) - Complete system view
```

**Script to Generate All Pages:**

```python
# scripts/generate_image_enhanced_pages.py
import yaml
from pathlib import Path

def generate_image_enhanced_pages():
    """Generate documentation pages with embedded images"""
    
    # Load image catalog
    catalog_path = Path("docs/images/diagrams/IMAGE-CATALOG.yaml")
    with open(catalog_path) as f:
        catalog = yaml.safe_load(f)
    
    # Template for each page
    template = """# {title}

![{title}](../images/diagrams/{file})

*{alt_text}*

## Overview

{narrative_content}

## Technical Details

[Generated from analysis]

## See Also

- [Mermaid Diagram]({mermaid_link}) - Interactive diagram
- [DALL-E Prompt]({prompt_link}) - Image generation prompt
- [Related Documentation]({related_links})
"""
    
    for image in catalog['images']:
        # Load narrative content
        narrative_path = Path(image['narrative_file'])
        narrative_content = narrative_path.read_text() if narrative_path.exists() else "[Narrative content]"
        
        # Generate page for each used_in_pages
        for page_path in image['used_in_pages']:
            full_path = Path(page_path)
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Fill template
            content = template.format(
                title=image['title'],
                file=image['file'],
                alt_text=image['alt_text'],
                narrative_content=narrative_content,
                mermaid_link=f"../{image['mermaid_file']}",
                prompt_link=f"../{image['prompt_file']}",
                related_links="[Related pages]"
            )
            
            full_path.write_text(content)
            print(f"✅ Generated: {page_path}")

if __name__ == "__main__":
    generate_image_enhanced_pages()
```

#### Task 2.3: Configure Material Theme for Images

**File:** `docs/themes/cortex-tales/main.css` (append)

```css
/* ========================================
   Image Display Enhancements
   ======================================== */

/* Responsive image sizing */
.md-content img {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin: 2rem 0;
    display: block;
}

/* Image captions (italicized text after image) */
.md-content img + em {
    display: block;
    text-align: center;
    color: #666;
    font-size: 0.9em;
    margin-top: -1.5rem;
    margin-bottom: 2rem;
}

/* Category-specific image borders */
img[src*="architectural/"] {
    border-left: 4px solid #4CAF50; /* Green for architectural */
}

img[src*="integration/"] {
    border-left: 4px solid #2196F3; /* Blue for integration */
}

img[src*="operational/"] {
    border-left: 4px solid #FF9800; /* Orange for operational */
}

img[src*="strategic/"] {
    border-left: 4px solid #9C27B0; /* Purple for strategic */
}

/* Image lightbox hover effect */
.md-content img:hover {
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    cursor: pointer;
    transform: scale(1.02);
    transition: all 0.3s ease;
}

/* Dark mode adjustments */
[data-md-color-scheme="slate"] .md-content img {
    box-shadow: 0 4px 6px rgba(255, 255, 255, 0.1);
    border: 1px solid #333;
}

[data-md-color-scheme="slate"] .md-content img + em {
    color: #aaa;
}
```

---

### Phase 3: Orchestrator Enhancement (30 minutes)

#### Task 3.1: Update Orchestrator - Image Reference Injection

**File:** `cortex-brain/admin/scripts/documentation/enterprise_documentation_orchestrator.py`

**Add new method:**

```python
def _integrate_images_with_docs(self, features: Dict, dry_run: bool) -> Dict:
    """
    Enhanced: Map generated images to documentation pages and validate references
    
    This method:
    1. Loads IMAGE-CATALOG.yaml
    2. Validates all images exist
    3. Injects image references into documentation pages
    4. Validates pages reference images correctly
    """
    logger.info("Phase 2G: Integrating images with documentation pages")
    
    image_catalog_path = self.docs_path / "images" / "diagrams" / "IMAGE-CATALOG.yaml"
    
    if not image_catalog_path.exists():
        logger.warning(f"Image catalog not found: {image_catalog_path}")
        return {
            "status": "skipped",
            "reason": "No image catalog found",
            "validation": {"total_images": 0}
        }
    
    # Load catalog
    with open(image_catalog_path) as f:
        catalog = yaml.safe_load(f)
    
    results = {
        "total_images": len(catalog.get("images", [])),
        "validated": 0,
        "missing_images": [],
        "missing_page_references": [],
        "injected_references": []
    }
    
    for image in catalog.get("images", []):
        image_id = image.get("id")
        image_file = self.docs_path / "images" / "diagrams" / image.get("file")
        
        # Validate image exists
        if not image_file.exists():
            logger.warning(f"Image missing: {image_file}")
            results["missing_images"].append(image_id)
            continue
        
        results["validated"] += 1
        
        # Check/inject page references
        for page_path in image.get("used_in_pages", []):
            full_page_path = self.workspace_root / page_path
            
            if not full_page_path.exists():
                logger.info(f"Page will be generated: {page_path}")
                results["missing_page_references"].append({
                    "image": image_id,
                    "page": page_path,
                    "status": "pending_generation"
                })
                continue
            
            # Check if image already referenced
            page_content = full_page_path.read_text(encoding='utf-8')
            image_ref = f"images/diagrams/{image.get('file')}"
            
            if image_ref in page_content:
                logger.debug(f"Image already referenced in {page_path}")
            else:
                logger.info(f"Image not yet referenced in {page_path}")
                if not dry_run:
                    # Inject image reference (if page has marker)
                    self._inject_image_reference(full_page_path, image, page_content)
                    results["injected_references"].append({
                        "image": image_id,
                        "page": page_path
                    })
    
    logger.info(f"✅ Image integration complete: {results['validated']}/{results['total_images']} validated")
    
    return {
        "status": "complete",
        "validation": results
    }

def _inject_image_reference(self, page_path: Path, image: Dict, page_content: str):
    """Inject image reference into documentation page if marker present"""
    
    # Look for marker comment: <!-- IMAGE: image-id -->
    marker = f"<!-- IMAGE: {image['id']} -->"
    
    if marker not in page_content:
        logger.debug(f"No marker found in {page_path} for {image['id']}")
        return
    
    # Inject image markdown after marker
    image_markdown = f"""
![{image['title']}](../images/diagrams/{image['file']})

*{image['alt_text']}*
"""
    
    updated_content = page_content.replace(marker, marker + "\n" + image_markdown)
    page_path.write_text(updated_content, encoding='utf-8')
    logger.info(f"✅ Injected image reference into {page_path}")
```

#### Task 3.2: Add Image Validation to Orchestrator

**Add validation method:**

```python
def _validate_image_integration(self) -> Dict:
    """
    Comprehensive validation of image integration
    
    Checks:
    - All catalog images exist on disk
    - All images have valid metadata
    - Referenced pages exist or will be generated
    - Image paths are correct
    """
    logger.info("Validating image integration...")
    
    image_catalog_path = self.docs_path / "images" / "diagrams" / "IMAGE-CATALOG.yaml"
    
    if not image_catalog_path.exists():
        return {"status": "no_catalog"}
    
    with open(image_catalog_path) as f:
        catalog = yaml.safe_load(f)
    
    results = {
        "total_images": 0,
        "valid_images": 0,
        "invalid_metadata": [],
        "broken_links": [],
        "orphaned_images": []
    }
    
    for image in catalog.get("images", []):
        results["total_images"] += 1
        image_id = image.get("id")
        
        # Check required metadata
        required_fields = ["id", "file", "title", "category", "prompt_file", "narrative_file"]
        missing_fields = [f for f in required_fields if f not in image]
        
        if missing_fields:
            results["invalid_metadata"].append({
                "image": image_id,
                "missing": missing_fields
            })
            continue
        
        # Check image file exists
        image_path = self.docs_path / "images" / "diagrams" / image["file"]
        if not image_path.exists():
            results["broken_links"].append(image_id)
            continue
        
        # Check prompt file exists
        prompt_path = self.workspace_root / image["prompt_file"]
        if not prompt_path.exists():
            logger.warning(f"Prompt file missing for {image_id}: {prompt_path}")
        
        # Check narrative file exists
        narrative_path = self.workspace_root / image["narrative_file"]
        if not narrative_path.exists():
            logger.warning(f"Narrative file missing for {image_id}: {narrative_path}")
        
        results["valid_images"] += 1
    
    # Check for orphaned images (images not in catalog)
    image_dir = self.docs_path / "images" / "diagrams"
    for category in ["architectural", "integration", "operational", "strategic"]:
        category_dir = image_dir / category
        if category_dir.exists():
            for image_file in category_dir.glob("*.png"):
                # Check if in catalog
                found = any(img["file"].endswith(image_file.name) for img in catalog.get("images", []))
                if not found:
                    results["orphaned_images"].append(str(image_file.relative_to(self.docs_path)))
    
    logger.info(f"✅ Validation complete: {results['valid_images']}/{results['total_images']} valid")
    
    return {
        "status": "complete",
        "results": results
    }
```

**Integrate into main execute method:**

```python
# In execute() method, add after _generate_image_guidance():
if profile in ["standard", "comprehensive"]:
    # Validate image integration
    validation_result = self._validate_image_integration()
    results["image_validation"] = validation_result
    
    # Integrate images with docs
    integration_result = self._integrate_images_with_docs(features, dry_run)
    results["image_integration"] = integration_result
```

---

### Phase 4: Documentation Generation & Validation (20 minutes)

#### Task 4.1: Generate Image-Enhanced Pages

**Command:**
```powershell
# Run orchestrator with image integration
python cortex-brain/admin/scripts/documentation/enterprise_documentation_orchestrator.py `
    --profile comprehensive `
    --component images

# Expected output:
# Phase 2G: Integrating images with documentation pages
#   ✅ Image integration complete: 14/14 validated
#   ✅ Injected 8 image references
# Phase 2H: Building MkDocs site
#   ✅ Site built successfully
```

#### Task 4.2: Validate Integration

**Validation Script:** `scripts/validate_image_integration.py`

```python
#!/usr/bin/env python3
"""
Validate CORTEX documentation image integration
Checks all images, references, and catalog consistency
"""

import yaml
from pathlib import Path

def validate_integration():
    """Run comprehensive validation"""
    
    print("🔍 CORTEX Image Integration Validation")
    print("=" * 60)
    
    results = {
        "images_found": 0,
        "images_missing": 0,
        "catalog_entries": 0,
        "page_references": 0,
        "broken_references": 0
    }
    
    # Load catalog
    catalog_path = Path("docs/images/diagrams/IMAGE-CATALOG.yaml")
    if not catalog_path.exists():
        print("❌ IMAGE-CATALOG.yaml not found")
        return False
    
    with open(catalog_path) as f:
        catalog = yaml.safe_load(f)
    
    results["catalog_entries"] = len(catalog.get("images", []))
    
    # Check each image
    for image in catalog["images"]:
        image_path = Path(f"docs/images/diagrams/{image['file']}")
        
        if image_path.exists():
            results["images_found"] += 1
            print(f"✅ {image['id']}: Image exists")
        else:
            results["images_missing"] += 1
            print(f"❌ {image['id']}: Image MISSING")
        
        # Check page references
        for page_path in image.get("used_in_pages", []):
            page_full_path = Path(page_path)
            results["page_references"] += 1
            
            if page_full_path.exists():
                content = page_full_path.read_text()
                if image['file'] in content:
                    print(f"   ✅ Referenced in {page_path}")
                else:
                    results["broken_references"] += 1
                    print(f"   ⚠️  Not referenced in {page_path}")
            else:
                print(f"   ℹ️  Page pending: {page_path}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Validation Summary:")
    print(f"   Catalog Entries: {results['catalog_entries']}")
    print(f"   Images Found: {results['images_found']}")
    print(f"   Images Missing: {results['images_missing']}")
    print(f"   Page References: {results['page_references']}")
    print(f"   Broken References: {results['broken_references']}")
    
    success = results['images_missing'] == 0 and results['broken_references'] == 0
    
    if success:
        print("\n✅ All validations passed!")
    else:
        print("\n❌ Validation failed - see issues above")
    
    return success

if __name__ == "__main__":
    import sys
    sys.exit(0 if validate_integration() else 1)
```

**Run Validation:**
```powershell
python scripts/validate_image_integration.py
```

#### Task 4.3: Build Production Site

**Commands:**
```powershell
# Clean previous build
if (Test-Path "site") {
    Remove-Item -Recurse -Force "site"
}

# Build site with MkDocs
cd docs
mkdocs build --clean

# Verify images in build
$imageCount = (Get-ChildItem -Recurse site/images/diagrams/*.png).Count
Write-Host "✅ Images in site: $imageCount (expected: 14)"

# Start local server for preview
mkdocs serve
# Visit http://localhost:8000
```

**Production Checklist:**
- [ ] All 14 images in correct category folders
- [ ] IMAGE-CATALOG.yaml created with complete metadata
- [ ] All documentation pages generated with image embeds
- [ ] Material theme CSS applied for responsive images
- [ ] Orchestrator validates and injects references
- [ ] Site builds successfully with all images
- [ ] Images display correctly in browser
- [ ] Category borders visible (architectural/integration/operational/strategic)

---

## 📊 Success Metrics

### Acceptance Criteria

| Metric | Target | Validation |
|--------|--------|------------|
| **Images Organized** | 14/14 in category folders | `ls docs/images/diagrams/{architectural,integration,operational,strategic}` |
| **Catalog Complete** | All 14 entries with metadata | `python scripts/validate_image_integration.py` |
| **Pages Generated** | All used_in_pages exist | Check navigation, verify page count |
| **Images Display** | 100% render correctly | Visual inspection in browser |
| **Orchestrator Integration** | Validates + injects references | Run orchestrator, check logs |
| **Site Build** | No errors, all images copied | `mkdocs build --clean` |

### Testing Checklist

- [ ] **Phase 1 Complete:** All images moved to category folders, no orphans in root
- [ ] **Phase 2 Complete:** MkDocs navigation updated, pages generated, CSS applied
- [ ] **Phase 3 Complete:** Orchestrator enhanced, validation methods added
- [ ] **Phase 4 Complete:** Full integration test passed, site builds successfully

### Rollback Plan

If issues occur:
1. **Restore images to root:** `Move-Item docs\images\diagrams\*\*.png docs\images\diagrams\`
2. **Revert mkdocs.yml:** Restore from git
3. **Remove catalog:** `Remove-Item docs\images\diagrams\IMAGE-CATALOG.yaml`
4. **Revert orchestrator:** Git reset changes

---

## 📝 Implementation Notes

### Platform Considerations

**Windows (PowerShell):**
- Use backslashes in paths: `docs\images\diagrams\`
- Use `-Force` flag for Move-Item to overwrite
- Test-Path for existence checks

**macOS/Linux (Bash):**
- Use forward slashes: `docs/images/diagrams/`
- Use `mv -f` for force move
- Use `test -f` for existence checks

### Git Integration

**Add to .gitignore (if needed):**
```gitignore
# Temporary generation files
docs/images/diagrams/.DS_Store
docs/images/diagrams/Thumbs.db
```

**Commit Strategy:**
```bash
# Commit in logical phases
git add docs/images/diagrams/{architectural,integration,operational,strategic}
git commit -m "Phase 1: Organize 14 ChatGPT-generated images by category"

git add docs/images/diagrams/IMAGE-CATALOG.yaml
git commit -m "Phase 1: Add image metadata catalog"

git add mkdocs.yml docs/architecture docs/integration docs/operations
git commit -m "Phase 2: MkDocs integration with image-enhanced pages"

git add cortex-brain/admin/scripts/documentation/enterprise_documentation_orchestrator.py
git commit -m "Phase 3: Orchestrator image validation and injection"
```

---

## 🎯 Next Actions

**Ready to execute?**

Choose execution approach:

1. **✅ Execute Full Integration** (~2 hours)
   - Run all 4 phases sequentially
   - Validate at each phase completion
   - Build production site at end

2. **✅ Phased Execution**
   - Phase 1: Image Organization (30 min) → validate → proceed
   - Phase 2: MkDocs Integration (45 min) → validate → proceed
   - Phases 3-4: Orchestrator + Generation (50 min) → final validation

3. **✅ Review/Adjust Plan**
   - Provide feedback on approach
   - Adjust phase breakdown
   - Clarify requirements

**Recommendation:** Phased execution for safety with validation checkpoints.

---

**Plan Status:** ✅ Ready for Execution  
**Estimated Total Time:** ~2 hours  
**Risk Level:** Low (reversible, organized)  
**Dependencies:** None (images already exist)

**Copyright © 2024-2025 Asif Hussain. All rights reserved.**
