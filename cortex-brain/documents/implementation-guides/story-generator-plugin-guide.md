# CORTEX Story Generator Plugin

**Plugin Type:** Documentation  
**Category:** MkDocs Integration  
**Priority:** Medium  
**Status:** ✅ Production Ready

---

## Overview

The Story Generator Plugin creates "The CORTEX Story" - an engaging, narrative-driven document that showcases CORTEX features through relatable scenarios. The story is generated as part of the `/CORTEX generate mkdocs` workflow and deployed to GitHub Pages alongside architecture diagrams.

---

## Features

### Zero-Footprint Architecture
- **No external dependencies** - Uses only CORTEX brain intelligence
- **Tier 2 Integration** - Leverages feature patterns and successful implementations
- **Tier 3 Integration** - Uses documentation context and structure
- **Template-Based** - Follows cortex-story-builder.md narrative guidelines
- **Feature-Driven** - Extracts features from 17-executive-feature-list.md

### Configurable Chapter Structure
- **7-10 chapters** (default: 10)
- **Max 5,000 words per chapter**
- **Pre-defined themes:**
  1. The Amnesia Problem
  2. Tier 1: Working Memory
  3. Tier 2: Knowledge Graph
  4. Tier 3: Context Intelligence
  5. The Dual Hemisphere Brain
  6. Intelligence & Automation
  7. Tier 0: Protection & Governance
  8. Integration & Extensibility
  9. Real-World Scenarios
  10. The Transformation

### Output Format
- **Individual chapter files** (`01-amnesia.md`, `02-tier1.md`, etc.)
- **Master story document** (`The-CORTEX-Story.md`)
- **MkDocs navigation** (auto-updated in `mkdocs.yml`)
- **GitHub Pages** hosting

---

## Usage

### Via Natural Language (Recommended)

```bash
# Generate full documentation including story
generate mkdocs

# Generate story only (if supported)
generate cortex story
```

### Via Python API

```python
from src.plugins.story_generator_plugin import StoryGeneratorPlugin

# Initialize plugin
plugin = StoryGeneratorPlugin(config={
    "root_path": "/path/to/CORTEX"
})

# Initialize resources
if plugin.initialize():
    # Execute with options
    context = {
        "dry_run": False,
        "chapters": 10,
        "max_words_per_chapter": 5000
    }
    
    result = plugin.execute(context)
    
    print(f"Chapters: {result['chapters_generated']}")
    print(f"Words: {result['total_words']:,}")
    print(f"Files: {len(result['files_created'])}")
    
    plugin.cleanup()
```

### Via Enterprise Documentation Orchestrator

The plugin integrates automatically with the enterprise documentation workflow:

```python
from src.operations.enterprise_documentation_orchestrator import EnterpriseDocumentationOrchestrator

orchestrator = EnterpriseDocumentationOrchestrator()

result = orchestrator.execute(
    profile="standard",
    dry_run=False,
    options={
        "generate_story": True,
        "story_chapters": 10,
        "story_max_words": 5000
    }
)

# Story metrics in result
story_metrics = result.data["story_generation"]
```

---

## Configuration

### Plugin Configuration

```python
config = {
    "root_path": "/path/to/CORTEX",  # Workspace root
}
```

### Execution Context

```python
context = {
    "dry_run": False,           # Preview mode (no file writes)
    "chapters": 10,             # Number of chapters (7-10)
    "max_words_per_chapter": 5000  # Word limit per chapter
}
```

---

## Architecture

### Plugin Structure

```
StoryGeneratorPlugin (inherits BasePlugin)
├── _get_metadata() → PluginMetadata
├── initialize() → Setup resources
├── execute(context) → Generate story
│   ├── Phase 1: Load story guidelines
│   ├── Phase 2: Extract features
│   ├── Phase 3: Map features to chapters
│   ├── Phase 4: Generate chapters
│   ├── Phase 5: Create directory structure
│   ├── Phase 6: Write story files
│   └── Phase 7: Update mkdocs navigation
└── cleanup() → Release resources
```

### Integration Points

```
/CORTEX generate mkdocs
        ↓
EnterpriseDocumentationOrchestrator
        ↓
DocumentationGenerator (6-stage pipeline)
        ↓
StoryGeneratorPlugin (runs after pipeline)
        ↓
Output: docs/diagrams/story/
        ↓
GitHub Pages (auto-deployed)
```

---

## Output Structure

```
docs/diagrams/story/
├── The-CORTEX-Story.md              # Master document
├── 01-the-amnesia-problem.md        # Chapter 1
├── 02-building-first-memory.md      # Chapter 2
├── 03-the-learning-system.md        # Chapter 3
├── 04-context-intelligence.md       # Chapter 4
├── 05-the-dual-hemisphere-brain.md  # Chapter 5
├── 06-intelligence-and-automation.md # Chapter 6
├── 07-protection-and-governance.md  # Chapter 7
├── 08-integration-and-extensibility.md # Chapter 8
├── 09-real-world-scenarios.md       # Chapter 9
└── 10-the-transformation.md         # Chapter 10
```

---

## Example Output

### Chapter 1: The Amnesia Problem (~4,000 words)

```markdown
# Chapter 1: The Amnesia Problem

## When Your AI Forgets Everything

Picture this: You've just hired the most brilliant intern you've ever met...

[Narrative continues with relatable scenarios]

### Understanding The Amnesia Problem

Let's explore how CORTEX solves this challenge:

**4-Tier Brain Architecture:** A key component of the Memory & Context 
system that enables intelligent behavior and context awareness.

### Real-World Example

**Scenario: The "Make It Purple" Problem**

You: "Add a button to the dashboard"
Copilot: [Creates button] ✅

[10 minutes later...]

You: "Make it purple"
Copilot: "What should I make purple?" ❌

Problem: No memory of the button from 10 minutes ago.

[... continues with CORTEX solution]
```

---

## Testing

```bash
# Run plugin tests
python tests/plugins/test_story_generator_plugin.py

# Expected output:
# ✅ Plugin initialization test passed
# ✅ Plugin metadata test passed
# ✅ Chapter configuration test passed
# ✅ Plugin execution (dry run) test passed
```

---

## GitHub Pages Deployment

The story is automatically deployed to GitHub Pages as part of the MkDocs build:

1. **Build:** `python3 -m mkdocs build`
2. **Deploy:** `python3 -m mkdocs gh-deploy`
3. **Access:** `https://<username>.github.io/CORTEX/diagrams/story/The-CORTEX-Story/`

---

## Narrative Guidelines

The plugin follows these guidelines from `cortex-story-builder.md`:

### Tone
- **95% story, 5% technical**
- Conversational, humorous, relatable
- "Asif Codeinstein" character with Wizard of Oz references

### Structure
- **5-act narrative arc**
- Before/after scenarios
- Real-world examples
- Empathy for developer pain points

### Do's
- ✅ Use conversational tone
- ✅ Add humor and personality
- ✅ Show empathy for developer pain
- ✅ Use before/after scenarios
- ✅ Weave technical details into story

### Don'ts
- ❌ Don't be overly technical
- ❌ Don't use marketing hype
- ❌ Don't list features like documentation
- ❌ Don't forget the human element

---

## Troubleshooting

### Issue: Story files not generated

**Solution:**
```bash
# Check output directory
ls -la docs/diagrams/story/

# Run with dry run first
python -c "
from src.plugins.story_generator_plugin import StoryGeneratorPlugin
plugin = StoryGeneratorPlugin(config={'root_path': '.'})
plugin.initialize()
result = plugin.execute({'dry_run': True, 'chapters': 3})
print(result)
"
```

### Issue: MkDocs navigation not updated

**Solution:**
```bash
# Verify mkdocs.yml exists
cat mkdocs.yml | grep -A 5 "nav:"

# Manually add to nav if needed:
# nav:
#   - The CORTEX Story: diagrams/story/The-CORTEX-Story.md
```

### Issue: Chapter word count exceeded

**Solution:**
```python
# Adjust max_words_per_chapter
context = {
    "dry_run": False,
    "chapters": 10,
    "max_words_per_chapter": 3000  # Reduce limit
}
```

---

## Future Enhancements

### Planned Features (CORTEX 3.1+)
- [ ] AI-assisted narrative generation (GPT-4 integration)
- [ ] Dynamic feature extraction from code comments
- [ ] Interactive HTML version with animations
- [ ] Multi-language support (i18n)
- [ ] Custom chapter templates
- [ ] Video transcript generation

### Community Contributions
- [ ] Additional character voices (not just Asif Codeinstein)
- [ ] Industry-specific scenarios (finance, healthcare, etc.)
- [ ] Alternative narrative structures
- [ ] More real-world examples

---

## Related Documentation

| Document | Purpose |
|----------|---------|
| `.github/prompts/cortex-story-builder.md` | Story guidelines and template |
| `docs/diagrams/narratives/17-executive-feature-list.md` | Feature inventory source |
| `src/epm/doc_generator.py` | Main documentation orchestrator |
| `src/operations/enterprise_documentation_orchestrator.py` | Entry point integration |
| `tests/plugins/test_story_generator_plugin.py` | Plugin tests |

---

## Copyright & License

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - Part of CORTEX 3.0  
**Repository:** https://github.com/asifhussain60/CORTEX

---

*Generated: 2025-11-17*  
*Plugin Version: 1.0.0*  
*CORTEX Version: 3.0*
