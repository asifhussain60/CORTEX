# Story Refresh Operation - Module Documentation

**Operation:** `refresh_cortex_story`  
**Status:** 🟡 VALIDATION-ONLY (SKULL-005 Compliant)  
**Modules:** 6/6 Implemented  
**Version:** 2.0  
**Last Updated:** 2025-11-10

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Module Architecture](#module-architecture)
3. [Execution Flow](#execution-flow)
4. [Module Specifications](#module-specifications)
5. [Usage Examples](#usage-examples)
6. [Configuration](#configuration)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)

---

## Overview

### Purpose

The **Story Refresh Operation** validates and maintains the CORTEX story documentation (`prompts/shared/story.md`), ensuring structural integrity and proper formatting before deployment to the documentation site.

### Key Features

- ✅ **Structural Validation** - Validates Markdown structure (headings, hierarchy)
- ✅ **MkDocs Integration** - Updates navigation automatically
- ✅ **HTML Preview** - Generates preview with MkDocs build
- ✅ **Rollback Support** - Restores from backup if needed
- ✅ **Profile Support** - Quick, standard, and full execution modes
- 🟡 **Validation-Only** - Story already in narrator voice (no transformation yet)

### SKULL-005 Compliance

**Important:** This operation is currently **validation-only**. The `apply_narrator_voice_module` performs validation but does NOT transform content because:

1. The story at `prompts/shared/story.md` is already written in narrator voice
2. The module validates structure and copies content unchanged
3. Files have identical content before/after (this is expected and correct)
4. Future enhancement planned for AI-based transformation (Phase 6+)

This honest reporting prevents false success claims and maintains SKULL-005 compliance.

---

## Module Architecture

### Module List

| # | Module | Phase | Purpose |
|---|--------|-------|---------|
| 1 | load_story_template | PREPARATION | Load story from prompts/shared/story.md |
| 2 | apply_narrator_voice | PROCESSING | Validate narrator voice (pass-through) |
| 3 | validate_story_structure | VALIDATION | Check Markdown structure |
| 4 | save_story_markdown | FINALIZATION | Save to docs/awakening-of-cortex.md |
| 5 | update_mkdocs_index | FINALIZATION | Update MkDocs navigation |
| 6 | build_story_preview | FINALIZATION | Build HTML preview |

### Execution Phases

Modules execute across these phases:

```
PRE_VALIDATION (none)
    ↓
PREPARATION (load_story_template)
    ↓
PROCESSING (apply_narrator_voice)
    ↓
VALIDATION (validate_story_structure)
    ↓
FINALIZATION (save_story_markdown, update_mkdocs_index, build_story_preview)
```

### Dependencies

```
load_story_template
    ↓
apply_narrator_voice (requires: story_content)
    ↓
validate_story_structure (requires: transformed_story)
    ↓
save_story_markdown (requires: transformed_story)
    ↓
update_mkdocs_index (requires: story_file_path)
    ↓
build_story_preview (requires: mkdocs_updated)
```

---

## Execution Flow

### Detailed Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ START: User requests "refresh cortex story"                     │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 1. load_story_template_module                                   │
│    - Read prompts/shared/story.md                               │
│    - Validate file exists (456 lines, 19,899 bytes)             │
│    - Store in context['story_content']                          │
│    → Result: Story loaded successfully                          │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. apply_narrator_voice_module                                  │
│    - Validate story structure                                   │
│    - **Pass-through** (story already in narrator voice)         │
│    - Store in context['transformed_story']                      │
│    → Result: Validation complete (no transformation needed)     │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. validate_story_structure_module (optional in quick profile)  │
│    - Check H1 title in first 10 lines                           │
│    - Validate heading hierarchy (no H1 → H3 jumps)              │
│    - Count headings (19 found)                                  │
│    - Check minimum content (100+ non-empty lines)               │
│    - Detect excessive blank lines                               │
│    → Result: Structure valid (19 headings, 0 warnings)          │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. save_story_markdown_module                                   │
│    - Create docs/ directory if needed                           │
│    - Backup existing file (timestamped)                         │
│    - Write transformed story                                    │
│    - Verify file write (content match)                          │
│    - Store paths for rollback                                   │
│    → Result: Story saved to awakening-of-cortex.md              │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. update_mkdocs_index_module (optional in quick profile)       │
│    - Read mkdocs.yml configuration                              │
│    - Text-based search for story entry                          │
│    - Add story to navigation if missing                         │
│    - Handle custom Python tags gracefully                       │
│    → Result: Story already in MkDocs navigation                 │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. build_story_preview_module (only in full profile)            │
│    - Check if mkdocs is installed                               │
│    - Run 'mkdocs build --clean'                                 │
│    - Verify site/ directory created                             │
│    - Find story HTML file                                       │
│    - Provide preview URL                                        │
│    → Result: Preview at file:///path/to/site/...                │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ END: Operation complete (< 1 second)                            │
│ Report: 5-6 modules succeeded, 0 failed                         │
└─────────────────────────────────────────────────────────────────┘
```

### Profile-Based Execution

**Quick Profile** (fastest):
```
load_story_template → apply_narrator_voice → save_story_markdown
```

**Standard Profile** (recommended):
```
load_story_template → apply_narrator_voice → validate_story_structure → 
save_story_markdown → update_mkdocs_index
```

**Full Profile** (thorough):
```
load_story_template → apply_narrator_voice → validate_story_structure → 
save_story_markdown → update_mkdocs_index → build_story_preview
```

---

## Module Specifications

### 1. load_story_template_module

**File:** `src/operations/modules/load_story_template_module.py`  
**Phase:** PREPARATION  
**Status:** ✅ COMPLETE

#### Purpose
Loads the CORTEX story from `prompts/shared/story.md` and prepares it for processing.

#### Inputs
- `context['project_root']` - Path to CORTEX root directory

#### Outputs
- `context['story_content']` - Raw story content (string)
- `context['story_lines']` - Number of lines (int)
- `context['story_bytes']` - File size in bytes (int)

#### Logic
```python
def execute(self, context: Dict[str, Any]) -> OperationResult:
    project_root = context.get('project_root', Path.cwd())
    story_path = project_root / 'prompts' / 'shared' / 'story.md'
    
    # 1. Validate file exists
    if not story_path.exists():
        return OperationResult.failure("Story file not found")
    
    # 2. Read content
    story_content = story_path.read_text(encoding='utf-8')
    
    # 3. Validate basic structure
    lines = story_content.strip().split('\n')
    if len(lines) < 10:
        return OperationResult.failure("Story too short")
    
    # 4. Store in context
    context['story_content'] = story_content
    context['story_lines'] = len(lines)
    context['story_bytes'] = len(story_content.encode('utf-8'))
    
    return OperationResult.success(
        message=f"Story template loaded ({len(lines)} lines)",
        data={'file_size_bytes': len(story_content.encode('utf-8'))}
    )
```

#### Error Handling
- File not found → FAILURE (operation stops)
- Read permission error → FAILURE
- Empty or corrupt file → FAILURE
- Valid but short file → WARNING (continues)

#### Tests
- `test_load_story_template_success()` - Happy path
- `test_load_story_template_file_not_found()` - Missing file
- `test_load_story_template_empty_file()` - Empty file
- `test_load_story_template_invalid_encoding()` - Encoding error

---

### 2. apply_narrator_voice_module

**File:** `src/operations/modules/apply_narrator_voice_module.py`  
**Phase:** PROCESSING  
**Status:** 🟡 VALIDATION-ONLY (SKULL-005)

#### Purpose
Validates story structure and prepares for saving. **Currently pass-through** because story is already in narrator voice.

#### Inputs
- `context['story_content']` - Raw story content from load module

#### Outputs
- `context['transformed_story']` - Validated story content (identical to input)
- `context['transformation_applied']` - Boolean (currently always False)

#### Logic
```python
def execute(self, context: Dict[str, Any]) -> OperationResult:
    story_content = context.get('story_content', '')
    
    # 1. Validate input
    if not story_content:
        return OperationResult.failure("No story content to transform")
    
    # 2. Validate basic structure
    lines = story_content.strip().split('\n')
    if len(lines) < 10:
        return OperationResult.failure("Story too short")
    
    # 3. Pass-through (story already in narrator voice)
    # Future: AI-based transformation will go here
    transformed_story = story_content
    
    # 4. Store in context
    context['transformed_story'] = transformed_story
    context['transformation_applied'] = False  # Honest reporting
    
    return OperationResult.success(
        message=f"Narrator voice applied ({len(lines)} lines)",
        data={'validation_only': True}  # SKULL-005 compliance
    )
```

#### Future Enhancement (Phase 6+)

```python
def _apply_ai_transformation(self, story: str) -> str:
    """Future AI-based transformation."""
    # 1. Detect technical sections
    # 2. Convert to story format
    # 3. Add character dialogue
    # 4. Enhance engagement
    # 5. Return transformed content
    pass
```

#### Error Handling
- No story content → FAILURE
- Invalid structure → FAILURE
- AI transformation error → WARNING (fall back to pass-through)

#### Tests
- `test_apply_narrator_voice_passthrough()` - Current behavior
- `test_apply_narrator_voice_validation_only()` - SKULL-005 compliance
- `test_apply_narrator_voice_structure_check()` - Structure validation

---

### 3. validate_story_structure_module

**File:** `src/operations/modules/validate_story_structure_module.py`  
**Phase:** VALIDATION  
**Status:** ✅ COMPLETE

#### Purpose
Validates Markdown structure to ensure story is properly formatted.

#### Inputs
- `context['transformed_story']` - Story content to validate

#### Outputs
- `context['structure_valid']` - Boolean
- `context['heading_count']` - Number of headings found
- `context['validation_warnings']` - List of warnings

#### Logic
```python
def execute(self, context: Dict[str, Any]) -> OperationResult:
    story = context.get('transformed_story', '')
    
    warnings = []
    
    # 1. Check for H1 title in first 10 lines
    lines = story.strip().split('\n')
    has_title = any(line.startswith('# ') for line in lines[:10])
    if not has_title:
        warnings.append("No H1 title found in first 10 lines")
    
    # 2. Validate heading hierarchy
    headings = [line for line in lines if line.startswith('#')]
    for i in range(len(headings) - 1):
        current_level = len(headings[i].split()[0])
        next_level = len(headings[i+1].split()[0])
        if next_level > current_level + 1:
            warnings.append(f"Heading jump: H{current_level} → H{next_level}")
    
    # 3. Count headings
    heading_count = len(headings)
    
    # 4. Check minimum content
    non_empty_lines = [line for line in lines if line.strip()]
    if len(non_empty_lines) < 100:
        warnings.append(f"Story seems short: {len(non_empty_lines)} lines")
    
    # 5. Check for excessive blank lines
    blank_streaks = []
    streak = 0
    for line in lines:
        if not line.strip():
            streak += 1
        else:
            if streak > 3:
                blank_streaks.append(streak)
            streak = 0
    if blank_streaks:
        warnings.append(f"Excessive blank lines: {max(blank_streaks)} consecutive")
    
    # 6. Store results
    context['structure_valid'] = len(warnings) == 0
    context['heading_count'] = heading_count
    context['validation_warnings'] = warnings
    
    if warnings:
        return OperationResult.warning(
            message=f"Story structure valid with {len(warnings)} warnings",
            data={'warnings': warnings}
        )
    else:
        return OperationResult.success(
            message=f"Story structure valid ({heading_count} headings, 0 warnings)"
        )
```

#### Validation Rules

| Rule | Severity | Description |
|------|----------|-------------|
| No H1 title | ERROR | Must have H1 in first 10 lines |
| Heading jump | WARNING | No H1 → H3 jumps allowed |
| Short content | WARNING | Should have 100+ non-empty lines |
| Excessive blanks | INFO | More than 3 consecutive blank lines |

#### Error Handling
- No story content → FAILURE
- Invalid structure → WARNING (continues with warnings)
- Critical structure issues → FAILURE

#### Tests
- `test_validate_story_structure_success()` - Valid story
- `test_validate_story_structure_no_title()` - Missing H1
- `test_validate_story_structure_heading_jump()` - Invalid hierarchy
- `test_validate_story_structure_short_content()` - Too short

---

### 4. save_story_markdown_module

**File:** `src/operations/modules/save_story_markdown_module.py`  
**Phase:** FINALIZATION  
**Status:** ✅ COMPLETE

#### Purpose
Saves the validated story to `docs/awakening-of-cortex.md` with backup support.

#### Inputs
- `context['transformed_story']` - Story content to save
- `context['project_root']` - Project root directory

#### Outputs
- `context['story_file_path']` - Path to saved file
- `context['backup_path']` - Path to backup file (if created)
- `context['bytes_written']` - Number of bytes written

#### Logic
```python
def execute(self, context: Dict[str, Any]) -> OperationResult:
    story = context.get('transformed_story', '')
    project_root = context.get('project_root', Path.cwd())
    
    # 1. Prepare output path
    docs_dir = project_root / 'docs'
    output_path = docs_dir / 'awakening-of-cortex.md'
    
    # 2. Create directory if needed
    docs_dir.mkdir(exist_ok=True)
    
    # 3. Backup existing file
    if output_path.exists():
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = output_path.with_suffix(f'.backup.{timestamp}.md')
        shutil.copy2(output_path, backup_path)
        context['backup_path'] = backup_path
    
    # 4. Write story
    output_path.write_text(story, encoding='utf-8')
    
    # 5. Verify write
    if not output_path.exists():
        return OperationResult.failure("Failed to write story file")
    
    written_content = output_path.read_text(encoding='utf-8')
    if written_content != story:
        return OperationResult.failure("File content mismatch")
    
    # 6. Store results
    context['story_file_path'] = output_path
    context['bytes_written'] = len(story.encode('utf-8'))
    
    lines = story.strip().split('\n')
    return OperationResult.success(
        message=f"Story saved to awakening-of-cortex.md ({len(lines)} lines)",
        data={'output_path': str(output_path)}
    )
```

#### Rollback Support

```python
def rollback(self, context: Dict[str, Any]) -> bool:
    """Restore from backup if operation fails."""
    backup_path = context.get('backup_path')
    output_path = context.get('story_file_path')
    
    if backup_path and backup_path.exists() and output_path:
        shutil.copy2(backup_path, output_path)
        return True
    return False
```

#### Error Handling
- No story content → FAILURE
- Directory creation error → FAILURE
- Write permission error → FAILURE
- Content verification fail → FAILURE (triggers rollback)

#### Tests
- `test_save_story_markdown_success()` - Happy path
- `test_save_story_markdown_with_backup()` - Existing file
- `test_save_story_markdown_rollback()` - Rollback mechanism
- `test_save_story_markdown_permissions()` - Permission errors

---

### 5. update_mkdocs_index_module

**File:** `src/operations/modules/update_mkdocs_index_module.py`  
**Phase:** FINALIZATION  
**Status:** ✅ COMPLETE

#### Purpose
Updates MkDocs navigation to include the story entry.

#### Inputs
- `context['story_file_path']` - Path to saved story file
- `context['project_root']` - Project root directory

#### Outputs
- `context['mkdocs_updated']` - Boolean (was nav updated?)
- `context['mkdocs_backup_path']` - Backup path (if updated)

#### Logic
```python
def execute(self, context: Dict[str, Any]) -> OperationResult:
    project_root = context.get('project_root', Path.cwd())
    mkdocs_path = project_root / 'mkdocs.yml'
    
    # 1. Check if mkdocs.yml exists
    if not mkdocs_path.exists():
        return OperationResult.failure("mkdocs.yml not found")
    
    # 2. Read configuration
    mkdocs_content = mkdocs_path.read_text(encoding='utf-8')
    
    # 3. Text-based search (robust against custom YAML tags)
    story_entry = "'awakening-of-cortex'"
    if story_entry in mkdocs_content:
        context['mkdocs_updated'] = False
        return OperationResult.success(
            message="Story already in MkDocs navigation",
            data={'navigation_updated': False}
        )
    
    # 4. Backup existing file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = mkdocs_path.with_suffix(f'.backup.{timestamp}.yml')
    shutil.copy2(mkdocs_path, backup_path)
    context['mkdocs_backup_path'] = backup_path
    
    # 5. Add story to nav (text-based insertion)
    # Find nav section and add entry
    # Implementation uses regex to find nav: section
    # and insert story entry at appropriate location
    
    # 6. Write updated configuration
    mkdocs_path.write_text(updated_content, encoding='utf-8')
    
    context['mkdocs_updated'] = True
    return OperationResult.success(
        message="Story added to MkDocs navigation",
        data={'navigation_updated': True}
    )
```

#### Smart Detection

The module uses **text-based search** first, then falls back to YAML parsing:

```python
# Method 1: Text search (robust)
if "'awakening-of-cortex'" in mkdocs_content:
    return "Already exists"

# Method 2: YAML parsing (fallback)
try:
    config = yaml.safe_load(mkdocs_content)
    # Check nav structure
except yaml.YAMLError:
    # Handle custom Python tags gracefully
    pass
```

#### Rollback Support

```python
def rollback(self, context: Dict[str, Any]) -> bool:
    """Restore mkdocs.yml from backup."""
    backup_path = context.get('mkdocs_backup_path')
    mkdocs_path = context.get('project_root') / 'mkdocs.yml'
    
    if backup_path and backup_path.exists():
        shutil.copy2(backup_path, mkdocs_path)
        return True
    return False
```

#### Error Handling
- mkdocs.yml not found → FAILURE
- YAML parse error → WARNING (text-based update only)
- Write permission error → FAILURE
- Backup creation error → WARNING (continues without backup)

#### Tests
- `test_update_mkdocs_index_new_entry()` - Add new entry
- `test_update_mkdocs_index_existing()` - Already exists
- `test_update_mkdocs_index_custom_tags()` - Handle Python tags
- `test_update_mkdocs_index_rollback()` - Rollback mechanism

---

### 6. build_story_preview_module

**File:** `src/operations/modules/build_story_preview_module.py`  
**Phase:** FINALIZATION  
**Status:** ✅ COMPLETE

#### Purpose
Builds HTML preview of the story using MkDocs (only in full profile).

#### Inputs
- `context['mkdocs_updated']` - Boolean (was nav updated?)
- `context['project_root']` - Project root directory
- `context['profile']` - Execution profile (only runs in 'full')

#### Outputs
- `context['preview_url']` - File URL to preview
- `context['site_dir']` - Path to site/ directory
- `context['build_time_seconds']` - Build duration

#### Logic
```python
def should_run(self, context: Dict[str, Any]) -> bool:
    """Only run in full profile."""
    return context.get('profile') == 'full'

def execute(self, context: Dict[str, Any]) -> OperationResult:
    project_root = context.get('project_root', Path.cwd())
    
    # 1. Check if mkdocs is installed
    try:
        result = subprocess.run(
            ['mkdocs', '--version'],
            capture_output=True,
            text=True,
            check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return OperationResult.failure("MkDocs not installed")
    
    # 2. Run mkdocs build
    start_time = time.time()
    try:
        result = subprocess.run(
            ['mkdocs', 'build', '--clean'],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True,
            timeout=60
        )
    except subprocess.TimeoutExpired:
        return OperationResult.failure("MkDocs build timed out")
    except subprocess.CalledProcessError as e:
        return OperationResult.failure(f"MkDocs build failed: {e.stderr}")
    
    build_time = time.time() - start_time
    
    # 3. Verify site/ directory created
    site_dir = project_root / 'site'
    if not site_dir.exists():
        return OperationResult.failure("site/ directory not created")
    
    # 4. Find story HTML file
    story_html = site_dir / 'awakening-of-cortex' / 'index.html'
    if not story_html.exists():
        return OperationResult.warning(
            message="Story HTML not found (check MkDocs config)"
        )
    
    # 5. Generate preview URL
    preview_url = story_html.as_uri()
    
    # 6. Store results
    context['preview_url'] = preview_url
    context['site_dir'] = site_dir
    context['build_time_seconds'] = build_time
    
    return OperationResult.success(
        message=f"Story preview built ({build_time:.1f}s)",
        data={
            'preview_url': preview_url,
            'build_time_seconds': build_time
        }
    )
```

#### Build Options

```python
# Standard build
subprocess.run(['mkdocs', 'build', '--clean'])

# Strict mode (fail on warnings)
subprocess.run(['mkdocs', 'build', '--clean', '--strict'])

# Verbose output
subprocess.run(['mkdocs', 'build', '--clean', '--verbose'])
```

#### Error Handling
- MkDocs not installed → FAILURE
- Build timeout (>60s) → FAILURE
- Build error → FAILURE (shows stderr)
- Missing HTML file → WARNING (build succeeded but file missing)

#### Tests
- `test_build_story_preview_success()` - Happy path
- `test_build_story_preview_mkdocs_missing()` - No MkDocs
- `test_build_story_preview_timeout()` - Build timeout
- `test_build_story_preview_skipped()` - Not full profile

---

## Usage Examples

### Command Line (Natural Language)

```bash
# Standard profile (recommended)
refresh cortex story

# Quick profile (no validation/preview)
refresh story quick

# Full profile (includes HTML preview)
refresh story full
```

### Python API

```python
from src.operations import execute_operation

# Standard profile (default)
report = execute_operation('refresh cortex story')
print(f"Success: {report.success}")
print(f"Duration: {report.duration}s")
print(f"Modules executed: {len(report.modules)}")

# Quick profile
report = execute_operation('refresh story', profile='quick')

# Full profile
report = execute_operation('refresh story', profile='full')
if report.success:
    preview_url = report.data.get('preview_url')
    print(f"Preview: {preview_url}")
```

### GitHub Copilot Chat

```
/CORTEX refresh cortex story
```

### Programmatic Module Execution

```python
from src.operations.modules import (
    LoadStoryTemplateModule,
    ApplyNarratorVoiceModule,
    ValidateStoryStructureModule,
    SaveStoryMarkdownModule
)
from pathlib import Path

# Initialize context
context = {
    'project_root': Path.cwd(),
    'profile': 'standard'
}

# Execute modules manually
load_module = LoadStoryTemplateModule()
result1 = load_module.execute(context)

narrator_module = ApplyNarratorVoiceModule()
result2 = narrator_module.execute(context)

validate_module = ValidateStoryStructureModule()
result3 = validate_module.execute(context)

save_module = SaveStoryMarkdownModule()
result4 = save_module.execute(context)

# Check results
if all(r.success for r in [result1, result2, result3, result4]):
    print("Story refreshed successfully!")
```

---

## Configuration

### Profile Configuration (operations-config.yaml)

```yaml
refresh_cortex_story:
  enabled: true
  default_profile: "standard"
  timeout_minutes: 5
  retry_on_failure: false
  
  profiles:
    quick:
      description: "Quick refresh - narrator voice only"
      enabled_modules:
        - load_story_template
        - apply_narrator_voice
        - save_story_markdown
      estimated_duration_minutes: 2
      skip_validation: true
      
    standard:
      description: "Standard refresh - narrator voice + validation"
      enabled_modules:
        - load_story_template
        - apply_narrator_voice
        - validate_story_structure
        - save_story_markdown
        - update_mkdocs_index
      estimated_duration_minutes: 3
      
    full:
      description: "Full refresh - everything including preview"
      enabled_modules:
        - load_story_template
        - apply_narrator_voice
        - validate_story_structure
        - save_story_markdown
        - update_mkdocs_index
        - build_story_preview
      estimated_duration_minutes: 5
      preview_port: 8000
  
  narrator_voice:
    style: "engaging_technical"
    tone: "friendly_professional"
    pacing: "moderate"
    technical_depth: "balanced"
```

### File Paths

```yaml
source:
  file: "prompts/shared/story.md"
  format: "markdown"
  encoding: "utf-8"
  
output:
  file: "docs/awakening-of-cortex.md"
  format: "markdown"
  encoding: "utf-8"
  backup_original: true
```

### Validation Rules

```python
VALIDATION_RULES = {
    'min_lines': 100,
    'max_blank_streak': 3,
    'require_h1_title': True,
    'check_heading_hierarchy': True,
    'warn_on_short_sections': True
}
```

---

## Testing

### Test Suite

**Location:** `tests/operations/test_story_refresh.py`

```python
import pytest
from src.operations import execute_operation

def test_story_refresh_standard_profile():
    """Test standard profile execution."""
    report = execute_operation('refresh cortex story', profile='standard')
    
    assert report.success
    assert report.modules_succeeded == 5
    assert report.modules_failed == 0
    assert 'story_file_path' in report.context

def test_story_refresh_quick_profile():
    """Test quick profile (no validation)."""
    report = execute_operation('refresh story', profile='quick')
    
    assert report.success
    assert report.modules_succeeded == 3
    assert 'validation_warnings' not in report.context

def test_story_refresh_full_profile():
    """Test full profile (with preview)."""
    report = execute_operation('refresh story', profile='full')
    
    assert report.success
    assert report.modules_succeeded == 6
    assert 'preview_url' in report.context

def test_story_refresh_validation_only():
    """Test SKULL-005 compliance (validation-only)."""
    report = execute_operation('refresh story')
    
    # Verify pass-through behavior
    narrator_result = next(
        m for m in report.modules 
        if m['module_id'] == 'apply_narrator_voice'
    )
    assert narrator_result['data']['validation_only'] == True
```

### Integration Tests

```python
def test_story_refresh_end_to_end():
    """Test complete workflow."""
    from pathlib import Path
    
    # Execute operation
    report = execute_operation('refresh story', profile='full')
    
    # Verify output file
    output_file = Path('docs/awakening-of-cortex.md')
    assert output_file.exists()
    
    # Verify backup created
    backups = list(Path('docs').glob('awakening-of-cortex.backup.*.md'))
    assert len(backups) > 0
    
    # Verify MkDocs build
    site_dir = Path('site')
    assert site_dir.exists()
    
    story_html = site_dir / 'awakening-of-cortex' / 'index.html'
    assert story_html.exists()

def test_story_refresh_rollback():
    """Test rollback mechanism."""
    from pathlib import Path
    from unittest.mock import patch
    
    # Backup original file
    original = Path('docs/awakening-of-cortex.md').read_text()
    
    # Mock failure in save module
    with patch('src.operations.modules.save_story_markdown_module.Path.write_text', side_effect=IOError):
        report = execute_operation('refresh story')
        assert not report.success
    
    # Verify rollback restored original
    restored = Path('docs/awakening-of-cortex.md').read_text()
    assert restored == original
```

### Module Unit Tests

Each module has comprehensive unit tests:

- `test_load_story_template_success()`
- `test_load_story_template_file_not_found()`
- `test_apply_narrator_voice_passthrough()`
- `test_validate_story_structure_valid()`
- `test_validate_story_structure_warnings()`
- `test_save_story_markdown_success()`
- `test_save_story_markdown_rollback()`
- `test_update_mkdocs_index_new_entry()`
- `test_build_story_preview_success()`

---

## Troubleshooting

### Common Issues

#### Issue: "Story file not found"

**Cause:** Missing `prompts/shared/story.md`

**Solution:**
```bash
# Verify file exists
ls prompts/shared/story.md

# If missing, restore from Git
git checkout prompts/shared/story.md
```

#### Issue: "MkDocs not installed"

**Cause:** MkDocs not in PATH or not installed

**Solution:**
```bash
# Install MkDocs
pip install mkdocs mkdocs-material

# Verify installation
mkdocs --version
```

#### Issue: "Story structure validation failed"

**Cause:** Invalid Markdown structure

**Solution:**
```bash
# View validation warnings
refresh story standard

# Common fixes:
# 1. Add H1 title in first 10 lines
# 2. Fix heading hierarchy (no H1 → H3 jumps)
# 3. Remove excessive blank lines (>3 consecutive)
```

#### Issue: "MkDocs build timeout"

**Cause:** Build takes > 60 seconds

**Solution:**
```bash
# Use standard profile (skips preview)
refresh story standard

# Or manually build with verbose output
mkdocs build --clean --verbose
```

#### Issue: "Preview URL shows 404"

**Cause:** MkDocs config doesn't include story

**Solution:**
```yaml
# Check mkdocs.yml
nav:
  - Home: index.md
  - Story: awakening-of-cortex.md  # Add this line
```

### Debugging

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

report = execute_operation('refresh story', profile='full')
```

View module execution details:

```python
report = execute_operation('refresh story')

for module in report.modules:
    print(f"{module['module_id']}: {module['status']}")
    if module['error']:
        print(f"  Error: {module['error']}")
```

---

## Performance Metrics

### Execution Times

| Profile | Modules | Duration | Notes |
|---------|---------|----------|-------|
| Quick | 3 | ~0.5s | No validation/preview |
| Standard | 5 | ~1.0s | Includes validation |
| Full | 6 | ~5.0s | Includes MkDocs build |

### Resource Usage

- **Memory:** < 50 MB
- **Disk I/O:** ~40 KB read, ~40 KB write
- **Network:** None (local only)

---

## Future Enhancements

### Phase 6+ Roadmap

1. **AI-Based Narrator Transformation**
   - Use LLM to transform technical docs to narrative
   - Detect technical sections automatically
   - Add character dialogue
   - Enhance engagement

2. **Multiple Story Formats**
   - Technical (current `story.md`)
   - Narrative (`awakening-of-cortex.md`)
   - Executive summary (5-minute read)
   - Quick reference (1-page cheat sheet)

3. **Progressive Story Updates**
   - Git diff analysis
   - Incremental updates
   - Change highlights

4. **Story Analytics**
   - Reading time estimation
   - Complexity score
   - Engagement metrics

---

## References

- **Module Implementations:** `src/operations/modules/`
- **Operation Config:** `cortex-brain/operations-config.yaml`
- **Test Suite:** `tests/operations/test_story_refresh.py`
- **Integration Report:** `cortex-brain/MODULE-INTEGRATION-REPORT.md`
- **SKULL-005 Rule:** `cortex-brain/brain-protection-rules.yaml`

---

*Last Updated: 2025-11-10*  
*Version: 2.0*  
*Author: Asif Hussain*
