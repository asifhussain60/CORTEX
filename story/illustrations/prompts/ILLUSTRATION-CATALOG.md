# CORTEX Story Illustration Catalog
# Generated DALL-E prompts with filenames for story reference

## Quick Reference
Total illustrations: 19 (12 Essential + 7 Valuable)
Chapters covered: 11

## Organization
- **Essential Tier:** `prompts/essential/` - 12 prompts (generate first)
- **Valuable Tier:** `prompts/valuable/` - 7 prompts (optional enhancements)
- **Image Location:** ALL images go to `docs/story/illustrations/images/` regardless of tier

## Filenames by Chapter

### PROLOGUE (Essential Tier)
- `cortex-awakening-prologue-01.png` - The Basement Laboratory (chapter_opening) 📁 `essential/`
- `cortex-awakening-prologue-02.png` - G Appears (character_intro) 📁 `essential/`

### CH01
- `cortex-awakening-ch01-01.png` - Coffee Mug Timeline (comedic_scene) 📁 `essential/`
- `cortex-awakening-ch01-02.png` - Copilot Amnesia (key_moment) 📁 `valuable/`
- `cortex-awakening-ch01-03.png` - The Goldfish Theory Whiteboard (technical_diagram) 📁 `essential/`

### CH02
- `cortex-awakening-ch02-01.png` - The Almost-Disaster (key_moment) 📁 `essential/`
- `cortex-awakening-ch02-02.png` - SKULL Rules Whiteboard (technical_diagram) 📁 `essential/`

### CH03
- `cortex-awakening-ch03-01.png` - The Laptop Crash (key_moment) 📁 `essential/`

### CH05
- `cortex-awakening-ch05-01.png` - The 2AM Knowledge Graph Epiphany (key_moment) 📁 `valuable/`

### CH06
- `cortex-awakening-ch06-01.png` - Token Mountain (key_moment) 📁 `valuable/`

### CH07 (TDD Mastery - MAJOR Feature)
- `cortex-awakening-ch07-01.png` - RED-GREEN-REFACTOR Whiteboard (technical_diagram) 📁 `essential/`
- `cortex-awakening-ch07-02.png` - Test Coverage Validation (key_moment) 📁 `valuable/`

### CH08
- `cortex-awakening-ch08-01.png` - Windows vs Mac Path Chaos (comedic_scene) 📁 `essential/`

### CH09 (System Maintenance - MAJOR Feature)
- `cortex-awakening-ch09-01.png` - The Maintenance Orchestrator (technical_diagram) 📁 `essential/`
- `cortex-awakening-ch09-02.png` - Alignment Auto-Fix Success (key_moment) 📁 `valuable/`

### CH10
- `cortex-awakening-ch10-01.png` - Personality Emergence (key_moment) 📁 `essential/`

### CH11 (Planning System 2.0 - MAJOR Feature)
- `cortex-awakening-ch11-01.png` - The Beautiful Documentation (key_moment) 📁 `valuable/`
- `cortex-awakening-ch11-02.png` - Planning System 2.0 Vision (technical_diagram) 📁 `valuable/`

### EPILOGUE (Essential Tier)
- `cortex-awakening-epilogue-01.png` - Where Are They Now (chapter_opening) 📁 `essential/`

## Usage in Story

**ALL images use the same location regardless of tier:**

```markdown
![{beat.title}](illustrations/images/{filename})
```

**Examples:**
```markdown
![Basement Laboratory](illustrations/images/cortex-awakening-prologue-01.png)
![TDD Cycle](illustrations/images/cortex-awakening-ch07-01.png)
![Knowledge Graph](illustrations/images/cortex-awakening-ch05-01.png)
```

**Image Location:** `docs/story/illustrations/images/`  
**Prompt Locations:** `prompts/essential/` and `prompts/valuable/`

---

## Generation Strategy

### Phase 1: Essential Tier (12 images)
Generate from `prompts/essential/` first - covers all MAJOR features + core narrative

### Phase 2: Valuable Tier (7 images)  
Generate from `prompts/valuable/` if budget allows - enhanced depth

### All Images Go To:
`docs/story/illustrations/images/` (single location for all tiers)