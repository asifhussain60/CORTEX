# Story Formatting Guidelines

## Overview

The CORTEX Story Generator now includes visual formatting enhancements to make the narrative more engaging and easier to read. This document describes the formatting system, its features, and how to use it.

## Formatting Features

### 1. Bold Emphasis (`**text**`)

**When to Use:**
- Key concepts and important terms
- Feature names (Tier 1, Tier 2, CORTEX, etc.)
- Emphasis for dramatic effect
- Section labels (Before/After, Key Takeaway, etc.)

**Examples:**
```markdown
**CORTEX** has a brain.
The **highly sophisticated amnesiac** needed help.
**Tier 1:** Working Memory System
```

### 2. Italic Emphasis (`*text*`)

**When to Use:**
- Inner voice or thoughts
- Dramatic asides
- Subtle emphasis
- Character descriptors

**Examples:**
```markdown
Then it *forgot who I was*.
It was *learning too*. Possibly *plotting*.
Like a *completely reasonable scientist* with *no questionable decisions*.
```

### 3. Code Formatting (`` `code` ``)

**When to Use:**
- Technical terms and identifiers
- File names, class names, method names
- Technology stack keywords
- Command snippets

**Examples:**
```markdown
A brilliant coder with `ZERO RAM`.
Using `JWT` tokens and `bcrypt` hashing.
The `SQLite` database with `FTS5` search.
```

### 4. Badge Formatting

**Feature Badges (`**✨ text**`):**
```markdown
**✨ Tier 1** - Working Memory System
**✨ TDD Enforcement**
```

**Warning Badges (`**⚠️ text**`):**
```markdown
**⚠️ HOTSPOT DETECTED**
**⚠️ This file is high-risk**
```

**Success Badges (`**✅ text**`):**
```markdown
**✅ Tests passed**
**✅ Story generation complete**
```

### 5. Dialogue Formatting

**Format:** `**Speaker:** text`

**Examples:**
```markdown
**Copilot:** "What should I make purple?"
**ME:** "THE BUTTON!"
**CORTEX:** "Applying purple to the dashboard button"
```

### 6. Lists and Structure

**Bullet Lists:**
```markdown
- Working memory (Tier 1)
- Knowledge graph (Tier 2)
- Context intelligence (Tier 3)
```

**Numbered Lists:**
```markdown
1. Write tests first
2. Implement feature
3. Refactor code
```

### 7. Code Blocks

**Format:**
````markdown
```language
code here
```
````

**Examples:**
````markdown
```python
def remember_context():
    return tier1_memory.last_20()
```

```bash
cortex generate story
```
````

## Formatting Utility API

### StoryFormatter Class

Located in: `src/plugins/story_formatting.py`

**Basic Methods:**
```python
fmt = StoryFormatter()

# Text emphasis
fmt.emphasize("important")  # Returns: **important**
fmt.italicize("dramatic")   # Returns: *dramatic*
fmt.code("variable")        # Returns: `variable`
fmt.quote("dialogue")       # Returns: "dialogue"

# Badges
fmt.feature_badge("Tier 1")  # Returns: **✨ Tier 1**
fmt.warning_badge("Hotspot") # Returns: **⚠️ Hotspot**
fmt.success_badge("Done")    # Returns: **✅ Done**

# Dialogue
fmt.dialogue("Speaker", "text")  # Returns: **Speaker:** text

# Lists
fmt.bullet_list(["Item 1", "Item 2"])
fmt.numbered_list(["Step 1", "Step 2"])

# Comparisons
fmt.before_after("Old way", "New way")

# Code blocks
fmt.code_block("code", "python")
```

### Smart Formatting Function

`apply_narrative_formatting(text: str) -> str`

Automatically detects and formats:
- All-caps words → bold emphasis
- Common technical terms → code formatting
- Maintains existing formatting

**Example:**
```python
text = "I used JWT tokens with SQLite and THE BUTTON was purple"
formatted = apply_narrative_formatting(text)
# Result: "I used `JWT` tokens with `SQLite` and **THE** **BUTTON** was purple"
```

## Testing

### Test Files

1. **`tests/plugins/test_story_formatting.py`**
   - Tests formatter utilities
   - Validates visual formatting in generated story
   - Checks first-person narrative
   - Verifies 50+ features covered
   - Ensures formatting consistency across chapters

2. **`tests/plugins/test_story_narrator_style.py`**
   - Tests narrator voice (Asif Codenstein)
   - Validates story.txt integration
   - Checks chapter structure
   - Verifies feature coverage (88 features)

### Running Tests

```bash
# Run formatting tests
python3 tests/plugins/test_story_formatting.py

# Run narrator style tests
python3 tests/plugins/test_story_narrator_style.py

# Run both
python3 tests/plugins/test_story_narrator_style.py && \
python3 tests/plugins/test_story_formatting.py
```

### Test Requirements

**Visual Formatting:**
- Bold emphasis: ≥20 occurrences
- Italic emphasis: ≥10 occurrences
- Inline code: ≥5 occurrences
- Badges: ≥3 occurrences
- Code blocks: Present
- Dialogue formatting: Present

**Narrative Quality:**
- First-person markers: ≥50 occurrences
- Codenstein character: Present
- Basement setting: Referenced
- Roomba character: Present

**Feature Coverage:**
- Features mentioned: ≥50
- All tiers covered (0-3)
- Agents described
- Use cases demonstrated

**Consistency:**
- ≥70% of chapters have formatting
- Formatting applied throughout story

## Current Metrics (as of 2025-11-17)

**Story Statistics:**
- Bold emphasis: 22 occurrences
- Italic emphasis: 59 occurrences
- Inline code: 5 occurrences
- Code blocks: 72 occurrences
- Badges: 90 occurrences
- Dialogue: 21 occurrences
- First-person markers: 61 occurrences
- Features covered: 54
- Chapters with formatting: 8/10 (80%)

**Test Results:**
- All formatter utilities: ✅ PASS
- Visual formatting: ✅ PASS
- First-person narrative: ✅ PASS
- Feature coverage: ✅ PASS
- Formatting consistency: ✅ PASS

## Best Practices

### Do:
✅ Use bold for key concepts and feature names
✅ Use italics for dramatic effect and inner voice
✅ Use code formatting for technical terms
✅ Use badges for warnings, features, and success indicators
✅ Maintain first-person narrative voice
✅ Balance formatting (not too much, not too little)
✅ Apply formatting consistently across chapters

### Don't:
❌ Over-format (makes text hard to read)
❌ Use formatting for decoration only
❌ Break first-person narrative voice
❌ Format entire paragraphs in bold/italic
❌ Use technical jargon without code formatting
❌ Skip formatting for key technical terms

## Integration

### Story Generator Plugin

The `StoryGeneratorPlugin` now includes:

1. **Formatter Initialization:**
   ```python
   self.formatter = StoryFormatter()
   ```

2. **Format Usage in Templates:**
   ```python
   fmt = self.formatter
   intro = f"So I built {fmt.emphasize('CORTEX')} with {fmt.code('SQLite')}."
   ```

3. **Post-Processing Enhancement:**
   - Automatic technical term formatting
   - Tier badge formatting
   - Smart emphasis application

### Adding New Formatting

To add new formatting patterns:

1. Add method to `StoryFormatter` class
2. Add test to `test_story_formatting.py`
3. Update this documentation
4. Apply in story templates or post-processing

**Example:**
```python
@staticmethod
def highlight(text: str, color: str = "yellow") -> str:
    """Highlight text with color (for HTML output)"""
    return f'<mark style="background-color:{color}">{text}</mark>'
```

## Maintenance

### Regenerating Story

```bash
# Regenerate documentation (includes story)
python3 -m mkdocs build --clean

# Story output location
docs/diagrams/story/The-CORTEX-Story.md
```

### Updating Tests

If you change formatting requirements:

1. Update thresholds in `test_story_formatting.py`
2. Regenerate story
3. Run tests to verify
4. Update this documentation

### Version History

- **v1.0** (2025-11-17): Initial formatting system
  - StoryFormatter utility class
  - Comprehensive test suite
  - Documentation and guidelines
  - Integration with story generator

## Resources

- **Formatter Source:** `src/plugins/story_formatting.py`
- **Story Generator:** `src/plugins/story_generator_plugin.py`
- **Tests:** `tests/plugins/test_story_formatting.py`
- **Generated Story:** `docs/diagrams/story/The-CORTEX-Story.md`
- **Narrator Source:** `.github/CopilotChats/story.txt`

## Support

For questions or issues with story formatting:

1. Check test output for specific failures
2. Review this documentation
3. Examine `StoryFormatter` source code
4. Check generated story for examples

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - Part of CORTEX 3.0  
**Last Updated:** 2025-11-17
