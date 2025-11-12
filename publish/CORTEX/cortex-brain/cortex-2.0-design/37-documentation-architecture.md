# CORTEX 2.0: Documentation Architecture - Single Source of Truth

**Document:** 37-documentation-architecture.md  
**Version:** 1.0  
**Created:** 2025-11-09  
**Status:** Design Complete  
**Priority:** HIGH  

**Related Documents:**
- 31-human-readable-documentation-system.md (Human-readable docs)
- 23-modular-entry-point.md (AI context prompts)
- 06-documentation-system.md (Git Pages / MkDocs)
- 35-unified-architecture-analysis.md (Issue #3 resolution)

---

## 🎯 Purpose

Eliminate documentation duplication and sync issues by establishing a **single source of truth** architecture with automated generation of all derived documentation layers.

**Problem Solved:** Information scattered across 4 documentation systems, requiring manual updates in 3-4 places, leading to out-of-sync documentation and maintenance burden.

---

## 🏗️ Documentation Pyramid

### Principle: Write Once, Generate Many

```
                    ┌─────────────────────┐
                    │  Layer 1: Design    │
                    │     Documents       │
                    │  (Source of Truth)  │
                    │ cortex-2.0-design/  │
                    └──────────┬──────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
    ┌────▼─────┐         ┌────▼─────┐         ┌────▼─────┐
    │ Layer 2  │         │ Layer 3  │         │ Layer 4  │
    │  Human   │         │    AI    │         │  Public  │
    │ Readable │         │ Context  │         │   Git    │
    │   docs/  │         │ prompts/ │         │  Pages   │
    └──────────┘         └──────────┘         └──────────┘
    Generated            Generated             Generated
    (story-driven)       (AI-optimized)        (MkDocs)
```

---

## 📚 Layer Definitions

### Layer 1: Design Documents (SSOT - Source of Truth)

**Location:** `cortex-brain/cortex-2.0-design/`

**Purpose:** Authoritative specifications for all CORTEX 2.0 functionality

**Audience:** Developers, architects

**Format:** Markdown (narrative) + YAML (structured data)

**Content:**
- Architecture specifications
- Implementation guides
- API references
- System designs
- Database schemas
- Plugin specifications
- Workflow definitions

**Maintenance:**
- ✅ Developers edit ONLY this layer
- ✅ All changes start here
- ✅ Version controlled (Git)
- ✅ Peer reviewed (PR process)

**Files:**
- 01-core-architecture.md
- 02-plugin-system.md
- ... (34 design documents)
- status-data.yaml
- implementation-roadmap.yaml (future)
- plugin-specifications.yaml (future)

---

### Layer 2: Human-Readable Documentation (Generated)

**Location:** `docs/human-readable/`

**Purpose:** User-facing narrative documentation

**Audience:** End users, stakeholders, non-technical readers

**Format:** Markdown with 95% story / 5% technical ratio

**Content:**
- THE-AWAKENING-OF-CORTEX.md (consolidated story)
- CORTEX-RULEBOOK.md (plain English rules)
- CORTEX-FEATURES.md (feature list)
- Image-Prompts.md (diagram generation specs)

**Generation Source:**
- Narrative: Extracted from Layer 1 design docs
- Technical details: Summarized from Layer 1
- Rules: Generated from governance.yaml
- Features: Extracted from design docs + implementation

**Update Trigger:**
- Automatic: After design doc changes (git hook)
- Manual: `cortex docs:refresh --human-readable`

**Generator:** `doc_refresh_plugin.py` extended

**Maintenance:**
- ❌ Never manually edited
- ✅ Always generated from Layer 1
- ✅ Automated consistency

---

### Layer 3: AI Context Prompts (Generated)

**Location:** `prompts/shared/`

**Purpose:** Optimized context for GitHub Copilot

**Audience:** GitHub Copilot AI

**Format:** Markdown modules (slim, focused)

**Content:**
- cortex.md (slim entry point - manual)
- story.md (generated from Layer 1 + Layer 2)
- setup-guide.md (generated from Doc 23)
- technical-reference.md (generated from Layer 1 API docs)
- agents-guide.md (generated from Doc 10 + agent code)
- brain-architecture.md (generated from Doc 01)
- examples.md (extracted from design docs)

**Generation Source:**
- Agent specifications: Doc 10 + agent implementations
- Setup instructions: Doc 23 + scripts/cortex_setup.py
- Architecture: Doc 01 + diagrams
- API reference: Docstrings from code

**Update Trigger:**
- Automatic: After design doc changes (git hook)
- Manual: `cortex docs:refresh --ai-context`

**Generator:** `doc_refresh_plugin.py` extended

**Optimization:**
- Token-efficient format
- AI-friendly structure
- Module-based (load on-demand)
- <200 lines per module

**Maintenance:**
- ❌ Module content never manually edited
- ✅ cortex.md (entry point) manually maintained
- ✅ Generated from authoritative sources

---

### Layer 4: Public Git Pages (Generated)

**Location:** `docs/` (MkDocs structure)

**Purpose:** Public-facing documentation site

**Audience:** Community, potential users, contributors

**Format:** MkDocs (static site generator)

**Content:**
- Getting Started guides
- Architecture documentation
- API reference
- Plugin development guide
- Tutorials and examples
- Contributing guidelines

**Generation Source:**
- Getting Started: Layer 2 (human-readable)
- Architecture: Layer 1 (design docs) + diagrams
- API Reference: Code docstrings (autodoc)
- Tutorials: Layer 1 examples sections

**Update Trigger:**
- Automatic: CI/CD after PR merge
- Manual: `mkdocs build`

**Generator:** MkDocs + custom build script

**Deployment:** GitHub Pages (automatic)

**Maintenance:**
- ❌ Never manually edited
- ✅ Generated from Layer 1 + Layer 2
- ✅ CI/CD enforced freshness

---

## 🔄 Update Triggers

### Automatic Triggers

```yaml
triggers:
  design_doc_changed:
    condition: "*.md or *.yaml in cortex-2.0-design/ modified"
    actions:
      - regenerate_human_readable_docs
      - regenerate_ai_context_modules
      - trigger_git_pages_rebuild
  
  governance_changed:
    condition: "brain-protection-rules.yaml or governance.yaml modified"
    actions:
      - regenerate_rulebook
      - update_governance_sections
  
  code_changed:
    condition: "src/**/*.py docstrings modified"
    actions:
      - regenerate_api_reference
      - update_code_examples
  
  implementation_status_changed:
    condition: "status-data.yaml modified"
    actions:
      - regenerate_status_md
      - update_progress_tracking
```

### Manual Triggers

```bash
# Refresh all documentation layers
cortex docs:refresh --all

# Refresh specific layer
cortex docs:refresh --human-readable
cortex docs:refresh --ai-context
cortex docs:refresh --git-pages

# Force refresh (ignore cache)
cortex docs:refresh --all --force
```

---

## 🛠️ Implementation: Documentation Orchestrator

### Extended doc_refresh_plugin.py

```python
# src/plugins/doc_refresh_plugin.py

from pathlib import Path
import yaml
from typing import Dict, List

class DocumentationOrchestrator:
    """Orchestrates all documentation generation from SSOT"""
    
    def __init__(self):
        self.design_docs_path = Path('cortex-brain/cortex-2.0-design')
        self.human_readable_path = Path('docs/human-readable')
        self.ai_context_path = Path('prompts/shared')
        self.git_pages_path = Path('docs')
    
    def refresh_all(self, trigger_event: str = 'manual'):
        """Regenerate all derived documentation"""
        
        print("🔄 Refreshing all documentation layers...")
        
        # Layer 1: Design docs (manual, no action needed)
        design_docs = self._load_design_docs()
        
        # Layer 2: Human-Readable
        print("  📖 Generating human-readable documentation...")
        self._generate_human_readable(design_docs)
        
        # Layer 3: AI Context Prompts
        print("  🤖 Generating AI context modules...")
        self._generate_ai_context_modules(design_docs)
        
        # Layer 4: Git Pages
        print("  🌐 Triggering Git Pages rebuild...")
        self._trigger_git_pages_rebuild()
        
        print("✅ Documentation refresh complete!")
    
    def _load_design_docs(self) -> Dict:
        """Load all design documents (Layer 1)"""
        docs = {}
        
        for doc_file in self.design_docs_path.glob('*.md'):
            doc_id = doc_file.stem
            with open(doc_file, 'r', encoding='utf-8') as f:
                docs[doc_id] = f.read()
        
        # Load YAML docs
        for yaml_file in self.design_docs_path.glob('*.yaml'):
            with open(yaml_file, 'r', encoding='utf-8') as f:
                docs[yaml_file.stem] = yaml.safe_load(f)
        
        return docs
    
    def _generate_human_readable(self, design_docs: Dict):
        """Generate Layer 2: Human-readable docs"""
        
        # 1. Generate THE-AWAKENING-OF-CORTEX.md
        self._generate_consolidated_story(design_docs)
        
        # 2. Update CORTEX-RULEBOOK.md (from governance YAMLs)
        self._generate_rulebook()
        
        # 3. Generate CORTEX-FEATURES.md
        self._generate_features_list(design_docs)
        
        # 4. Update Image-Prompts.md
        self._generate_image_prompts(design_docs)
    
    def _generate_ai_context_modules(self, design_docs: Dict):
        """Generate Layer 3: AI context modules"""
        
        # 1. Generate agents-guide.md from Doc 10
        agents_data = self._extract_agent_specs(design_docs['10-agent-workflows'])
        self._write_module('agents-guide.md', self._format_for_ai(agents_data))
        
        # 2. Generate setup-guide.md from Doc 23
        setup_data = self._extract_setup_steps(design_docs['23-modular-entry-point'])
        self._write_module('setup-guide.md', self._format_for_ai(setup_data))
        
        # 3. Generate technical-reference.md from API docs
        api_data = self._extract_api_reference(design_docs)
        self._write_module('technical-reference.md', self._format_for_ai(api_data))
        
        # 4. Generate brain-architecture.md from Doc 01
        arch_data = self._extract_architecture(design_docs['01-core-architecture'])
        self._write_module('brain-architecture.md', self._format_for_ai(arch_data))
    
    def _generate_consolidated_story(self, design_docs: Dict):
        """Generate THE-AWAKENING-OF-CORTEX.md with 95/5 ratio"""
        
        # Load story sections
        story_sections = self._extract_story_sections(design_docs)
        
        # Load technical sections
        technical_sections = self._extract_technical_sections(design_docs)
        
        # Load images
        image_prompts = self._load_image_prompts()
        
        # Weave together maintaining 95/5 ratio
        consolidated = self._weave_narrative(
            story_sections, 
            technical_sections, 
            image_prompts,
            ratio={'story': 0.95, 'technical': 0.05}
        )
        
        # Write to file
        output_path = self.human_readable_path / 'THE-AWAKENING-OF-CORTEX.md'
        output_path.write_text(consolidated, encoding='utf-8')
    
    def _generate_rulebook(self):
        """Generate CORTEX-RULEBOOK.md from governance YAMLs"""
        
        # Load governance files
        governance = self._load_yaml('cortex-brain/brain-protection-rules.yaml')
        
        # Convert to plain English
        rulebook_content = self._yaml_to_plain_english(governance)
        
        # Write to file
        output_path = self.human_readable_path / 'CORTEX-RULEBOOK.md'
        output_path.write_text(rulebook_content, encoding='utf-8')
    
    def _generate_features_list(self, design_docs: Dict):
        """Generate CORTEX-FEATURES.md from design docs"""
        
        features = []
        
        # Extract features from each design doc
        for doc_id, content in design_docs.items():
            if isinstance(content, str) and '## ' in content:
                doc_features = self._extract_features(content)
                features.extend(doc_features)
        
        # Format as plain English list
        features_content = self._format_features_plain_english(features)
        
        # Write to file
        output_path = self.human_readable_path / 'CORTEX-FEATURES.md'
        output_path.write_text(features_content, encoding='utf-8')
    
    def _weave_narrative(self, story, technical, images, ratio):
        """Weave story + technical + images maintaining ratio"""
        
        sections = []
        story_words = 0
        technical_words = 0
        target_ratio = ratio['story'] / ratio['technical']
        
        # Algorithm: alternate story and technical sections
        # maintaining 95/5 word count ratio
        story_idx = 0
        tech_idx = 0
        
        while story_idx < len(story) or tech_idx < len(technical):
            current_ratio = story_words / (technical_words + 1)
            
            if current_ratio < target_ratio and story_idx < len(story):
                # Add story section
                section = story[story_idx]
                sections.append(section)
                story_words += len(section.split())
                story_idx += 1
                
                # Insert image if relevant
                if image := self._find_relevant_image(section, images):
                    sections.append(image)
            
            elif tech_idx < len(technical):
                # Add technical section (brief)
                section = technical[tech_idx]
                sections.append(section)
                technical_words += len(section.split())
                tech_idx += 1
        
        return '\n\n'.join(sections)
    
    def _write_module(self, module_name: str, content: str):
        """Write AI context module"""
        output_path = self.ai_context_path / module_name
        output_path.write_text(content, encoding='utf-8')
    
    def _trigger_git_pages_rebuild(self):
        """Trigger MkDocs rebuild for Git Pages"""
        # This would typically trigger CI/CD
        # For now, just update a timestamp file
        trigger_file = self.git_pages_path / '.rebuild_trigger'
        trigger_file.write_text(str(time.time()))
    
    # ... additional helper methods
```

---

## 🔗 Git Hooks Integration

### Post-Commit Hook

```bash
#!/bin/bash
# .git/hooks/post-commit

# Check which files changed
CHANGED_FILES=$(git diff-tree --no-commit-id --name-only -r HEAD)

# Design docs changed?
if echo "$CHANGED_FILES" | grep -q "cortex-brain/cortex-2.0-design"; then
    echo "🔄 Design docs changed - refreshing documentation..."
    python -m src.plugins.doc_refresh_plugin refresh-all
    
    # Auto-commit generated docs
    git add docs/human-readable/
    git add prompts/shared/
    git commit -m "docs: auto-refresh from design doc changes" --no-verify || true
fi

# Governance changed?
if echo "$CHANGED_FILES" | grep -q "brain-protection-rules.yaml\|governance.yaml"; then
    echo "🔄 Governance changed - refreshing rulebook..."
    python -m src.plugins.doc_refresh_plugin refresh-rulebook
    
    git add docs/human-readable/CORTEX-RULEBOOK.md
    git commit -m "docs: auto-refresh rulebook" --no-verify || true
fi
```

---

## 🤖 CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/refresh-docs.yml
name: Refresh Documentation

on:
  push:
    paths:
      - 'cortex-brain/cortex-2.0-design/**'
      - 'cortex-brain/*.yaml'
      - 'src/**/*.py'  # For docstring changes

jobs:
  refresh-docs:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Refresh All Documentation
        run: |
          python -m src.plugins.doc_refresh_plugin refresh-all
      
      - name: Commit Updated Docs
        run: |
          git config user.name "CORTEX Bot"
          git config user.email "bot@cortex.ai"
          git add docs/human-readable/
          git add prompts/shared/
          git commit -m "docs: auto-refresh from ${GITHUB_SHA:0:7}" || echo "No changes"
          git push
      
      - name: Build Git Pages
        run: |
          mkdocs build
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./site
```

---

## 📊 Benefits Analysis

### Before (4 Separate Systems)

**Update Process:**
1. Edit design doc (cortex-2.0-design/)
2. Manually update human-readable doc (docs/human-readable/)
3. Manually update AI context module (prompts/shared/)
4. Manually update Git Pages (docs/)
5. Hope all are consistent 🤞

**Problems:**
- ❌ 4 places to edit (error-prone)
- ❌ Easy to miss updates
- ❌ Information gets out of sync
- ❌ 30-60 minutes per update
- ❌ No consistency guarantee

---

### After (Single Source of Truth)

**Update Process:**
1. Edit design doc (cortex-2.0-design/) ✅
2. Git commit
3. **Everything else automatic** ✅

**Benefits:**
- ✅ 1 place to edit (error-proof)
- ✅ Can't miss updates (automated)
- ✅ Always in sync (generated)
- ✅ 5 minutes per update (95% reduction)
- ✅ Consistency guaranteed

---

## 🎯 Migration Plan

### Phase 1: Setup Infrastructure (Week 1)

**Tasks:**
- [ ] Extend `doc_refresh_plugin.py` with orchestrator
- [ ] Create generation methods for each layer
- [ ] Add git hooks (post-commit)
- [ ] Add CI/CD workflow
- [ ] Test generation pipeline

**Deliverables:**
- DocumentationOrchestrator class complete
- Git hooks installed
- CI/CD workflow committed
- Generation tested end-to-end

---

### Phase 2: Initial Generation (Week 1-2)

**Tasks:**
- [ ] Run initial full generation
- [ ] Verify all 4 layers generated correctly
- [ ] Compare with existing docs (quality check)
- [ ] Fix any generation issues
- [ ] Archive old manually-maintained docs

**Deliverables:**
- All Layer 2 docs generated from Layer 1
- All Layer 3 modules generated from Layer 1
- Git Pages builds successfully
- Quality verified (no information loss)

---

### Phase 3: Enforcement (Week 2)

**Tasks:**
- [ ] Add pre-commit hook (prevent manual Layer 2/3 edits)
- [ ] Update developer documentation
- [ ] Add README to each layer explaining SSOT
- [ ] Train team on new process

**Deliverables:**
- Pre-commit hook prevents manual edits
- README.md in each docs folder
- Team trained on SSOT workflow
- Old docs archived

---

## ✅ Success Criteria

**Architecture is successful when:**

1. ✅ All Layer 2 docs auto-generated from Layer 1
2. ✅ All Layer 3 modules auto-generated from Layer 1
3. ✅ Git Pages auto-builds from Layer 1 + Layer 2
4. ✅ Git hooks trigger regeneration automatically
5. ✅ CI/CD enforces freshness
6. ✅ Developers edit ONLY Layer 1
7. ✅ Documentation never out of sync
8. ✅ Update time: 5 minutes (down from 30-60 minutes)

**Measurement:**
- Layer 2/3/4 freshness: 100% (always in sync)
- Manual edits to Layer 2/3/4: 0 (prevented)
- Documentation update time: <5 minutes
- Team satisfaction: >90%

---

## 📚 Related Documents

- **31-human-readable-documentation-system.md** - Layer 2 specifications
- **23-modular-entry-point.md** - Layer 3 specifications
- **06-documentation-system.md** - Layer 4 specifications
- **35-unified-architecture-analysis.md** - Issue #3 (this document resolves)
- **00-INDEX.md** - Update with this document

---

**Document Status:** ✅ Complete  
**Next Action:** Implement DocumentationOrchestrator  
**Implementation:** Phase 3 (or earlier if docs out of sync)  

**© 2024-2025 Asif Hussain. All rights reserved.**
