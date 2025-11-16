# Refresh CORTEX Story

**Operation:** `refresh_cortex_story`  
**Category:** Documentation  
**Status:** ✅ Ready

## Overview

Update CORTEX story documentation with active narrator voice transformation. Converts third-person passive documentation into engaging first-person narrative with dialogue-heavy style.

## Natural Language Triggers

- "refresh story"
- "refresh cortex story"
- "update story"
- "regenerate story"
- "update cortex story"
- "transform story"

## Story Modules

The story refresh operation consists of 6 modules:

1. **load_story_template** - Load existing story structure
2. **apply_narrator_voice** - Transform to active narrator voice
3. **validate_story_structure** - Check parts, interludes, flow
4. **save_story_markdown** - Write updated story file
5. **update_mkdocs_index** - Update mkdocs.yml navigation
6. **build_story_preview** - Generate HTML preview (optional)

## Profiles

### Quick Profile ⚡
Narrator voice transformation only.

**Duration:** ~30 seconds  
**Modules:** load_story_template, apply_narrator_voice, save_story_markdown

```bash
# Use when
"quick story refresh"
"just update narrator voice"
```

### Standard Profile ⭐ Recommended
Narrator voice + validation.

**Duration:** ~45 seconds  
**Modules:** load, apply, validate, save, update_mkdocs

```bash
# Use when  
"refresh story"
"update cortex story"
```

### Full Profile 🚀
Everything including HTML preview.

**Duration:** ~60 seconds  
**Modules:** All 6 modules

```bash
# Use when
"full story refresh"
"regenerate story with preview"
```

## Narrator Voice Transformation

### Before (Passive Documentation Style)
```markdown
The CORTEX system was designed to provide memory capabilities.
Brain protection rules were implemented to ensure safety.
The system architecture consists of four tiers.
```

### After (Active Narrator Voice)
```markdown
"Wait, what if we just... store the conversations?" I said, 
staring at the whiteboard covered in architectural diagrams.

The brain protection rules? Those came from a 3am panic attack 
about accidentally deleting production databases. Never again.

Here's the thing about the four-tier architecture - it's not 
elegant design. It's three weeks of "this won't work" followed 
by "holy shit it worked."
```

## Story Structure

The CORTEX story is organized into:

### Parts
- **Part 1:** The Genesis (Problem identification)
- **Part 2:** The Evolution to 2.0 (Architecture design)
- **Part 3:** The Extension Era (Implementation)

### Interludes  
Transitional sections between technical chapters:
- The Whiteboard Archaeology
- The Invoice That Haunts Him
- The Lab Notebook Retrospective
- The Coffee Shop Epiphany
- The Git Log Detective Work
- The 3am Debugging Session

### Progressive Recaps
Each Part starts with a funny recap of previous parts:
- Part 2 recaps Part 1 (medium compression)
- Part 3 recaps Part 2 + Part 1 (progressive compression)

## Examples

### Basic Story Refresh

```bash
# Via entry point
/CORTEX refresh story

# Natural language
"update the cortex story"
"refresh story documentation"
```

### Quick Voice Update

```bash
# Via entry point with profile
/CORTEX refresh story quick

# Natural language
"quick story update"
"just fix narrator voice"
```

### Full Regeneration with Preview

```bash
# Via entry point
/CORTEX refresh story full

# Natural language  
"full story refresh with preview"
"regenerate entire story"
```

## Expected Output

```
🧠 CORTEX Story Refresh
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Module 1/6: Load Story Template
   └─ Loaded: awakening-of-cortex.md (3 parts, 8 chapters)

✅ Module 2/6: Apply Narrator Voice
   └─ Transformed: 147 paragraphs (passive → active)
   └─ Style: dialogue_heavy, casual, first-person
   └─ Comedy level: HIGH

✅ Module 3/6: Validate Story Structure
   └─ Parts: 3/3 ✓
   └─ Interludes: 6/6 ✓
   └─ Progressive recaps: 2/2 ✓
   └─ Narrative flow: EXCELLENT

✅ Module 4/6: Save Story Markdown
   └─ Written: docs/awakening-of-cortex.md
   └─ Backup: docs/awakening-of-cortex.backup.20251110_120534.md

✅ Module 5/6: Update MkDocs Index
   └─ Updated: mkdocs.yml (navigation added)

✅ Module 6/6: Build Story Preview
   └─ Preview: site/awakening-of-cortex/index.html
   └─ URL: http://localhost:8000/awakening-of-cortex/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Story refresh complete in 58s
Read time: 60-75 minutes (epic full story)
```

## Voice Transformation Modes

### dialogue_heavy (Default)
Converts exposition into conversations:
- Direct speech with character voices
- Technical discussions as dialogue
- Maintains technical accuracy
- High comedy factor

### internal_monologue  
First-person stream of consciousness:
- Developer's inner thoughts
- Technical epiphanies
- Debugging thought process
- Medium comedy factor

### mixed
Combination of dialogue and narration:
- Narrator introduces context
- Characters discuss technical details
- Balanced technical/comedy ratio
- Most versatile

## Read Time Management

**Target:** 60-75 minutes (epic full story)

If story exceeds target:
1. Plugin **trims content** (never creates "Quick Read" variants)
2. Compresses older sections progressively
3. Maintains key technical milestones
4. Preserves comedy and narrative arc

**Configuration:**
```json
{
  "story_refresh": {
    "target_read_minutes": 60,
    "trim_on_exceed": true,
    "progressive_compression": 0.5
  }
}
```

## Success Criteria

✅ All parts present and properly structured  
✅ Interludes positioned correctly  
✅ Progressive recaps at start of Parts 2-3  
✅ Narrator voice active (not passive documentation)  
✅ Technical accuracy maintained  
✅ Comedy tone preserved  
✅ Read time within 60-75 minute target  
✅ MkDocs navigation updated  
✅ Backup created before modification

## Configuration

Story refresh can be customized via `cortex.config.json`:

```json
{
  "story_refresh": {
    "narrator_voice": {
      "enabled": true,
      "mode": "dialogue_heavy",
      "comedy_level": "high",
      "enforce_active_voice": true
    },
    "progressive_recaps": {
      "enabled": true,
      "compression_factor": 0.5,
      "style": "lab_notebook"
    },
    "validation": {
      "check_structure": true,
      "check_narrative_flow": true,
      "check_technical_accuracy": true
    },
    "backup": {
      "enabled": true,
      "keep_n_backups": 5
    },
    "read_time": {
      "target_minutes": 60,
      "max_minutes": 75,
      "trim_on_exceed": true
    }
  }
}
```

## Technical Details

### Transformation Algorithm

1. **Parse Structure:** Identify parts, chapters, interludes
2. **Analyze Voice:** Detect passive constructions
3. **Transform Paragraphs:** Convert passive → active
4. **Inject Dialogue:** Replace exposition with conversations
5. **Add Recaps:** Generate progressive recaps for Parts 2-3
6. **Validate Flow:** Check narrative transitions
7. **Compress if Needed:** Trim to target read time

### Voice Patterns

**Passive → Active Transformations:**
- "The system was designed" → "I designed the system"
- "It was discovered that" → "Holy shit, we discovered"
- "The architecture consists of" → "Here's the thing about the architecture"
- "Rules were implemented" → "After that 3am panic attack, I implemented rules"

**Comedy Injection:**
- Technical terms → casual explanations with humor
- Design decisions → honest admission of iteration
- Bug fixes → war stories with comedic timing
- Success metrics → surprise at actually working

## Troubleshooting

### Story Structure Errors
```bash
# Validate structure manually
python -c "from src.plugins.doc_refresh_plugin import Plugin; \
  Plugin()._validate_story_structure({'story': open('docs/awakening-of-cortex.md').read()})"
```

### Narrator Voice Not Applied
Check configuration:
```bash
# Verify narrator voice enabled
grep -A5 "narrator_voice" cortex.config.json

# Check story file has passive constructions
grep -E "was|were|is|are" docs/awakening-of-cortex.md | head -20
```

### Read Time Exceeds Target
```bash
# Check current read time
python -c "from src.plugins.doc_refresh_plugin import Plugin; \
  p = Plugin(); \
  content = open('docs/awakening-of-cortex.md').read(); \
  print(p._validate_read_time(content, 60))"

# Enable trimming
# Edit cortex.config.json: "trim_on_exceed": true
```

### MkDocs Preview Broken
```bash
# Rebuild mkdocs site
mkdocs build --clean

# Test locally  
mkdocs serve

# Check for broken links
mkdocs build 2>&1 | grep -i "warning\|error"
```

## Related Documentation

- [Doc Refresh Plugin](../plugins/doc-refresh.md)
- [Story Writing Guide](../guides/story-writing-guide.md)
- [Narrator Voice Transformation](../guides/narrator-voice-transformation.md)
- [Progressive Recaps System](../guides/progressive-recaps.md)

## Testing

Tested on:
- ✅ macOS Sonoma (Mac Track B)
- ✅ Windows 11 (Track A)
- ✅ All three profiles (quick, standard, full)
- ✅ Voice transformation accuracy (147 paragraphs)
- ✅ Read time validation (60-75 minute target)
- ✅ MkDocs integration
- ✅ Backup creation and restoration

## Performance

**Benchmarks** (MacBook Air M2):
- Quick Profile: 28s
- Standard Profile: 42s
- Full Profile: 58s

**Voice Transformation Rate:**
- ~5-6 paragraphs per second
- 147 paragraphs in ~25 seconds
- Real-time streaming during transformation

## Notes

**Story refresh is careful:**
- Always creates backup before modification
- Validates structure before and after transformation
- Maintains technical accuracy (no hallucinations)
- Preserves existing interludes and recaps
- Never creates alternate versions (trims existing file if needed)

**Best practices:**
- Run story refresh after major architectural changes
- Review transformed sections for technical accuracy  
- Keep backups (plugin keeps last 5 automatically)
- Test mkdocs preview after refresh
- Verify read time meets target (60-75 minutes)
