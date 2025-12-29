# Component Composition Architecture

**Created:** December 8, 2025  
**Author:** Asif Hussain  
**Version:** 3.8.1

---

## Overview

CORTEX response templates use a **component composition architecture** where templates reference reusable components by name rather than embedding format strings directly. This enables single-point updates for format changes across all templates.

---

## Architecture Layers

### Layer 1: Base Components (Single Source of Truth)

**File:** `cortex-brain/response-templates/base-components.yaml`

**Purpose:** Define reusable format strings that templates compose from

**Structure:**
```yaml
components:
  understanding_section:
    format: "### 🎯 Understanding & Scope\n{understanding_content}"
    
  challenge_section:
    format: "### ⚡ Approach & Considerations\n{challenge_content}"
    
  response_section:
    format: "### 💬 Response\n{response_content}"
    
  request_echo_section:
    format: "### 📊 Impact & Changes\n{request_echo_content}"
    
  next_steps_section:
    format: "### 🔍 Next Steps\n{next_steps_content}"
```

### Layer 2: Templates (Component References)

**File:** `cortex-brain/response-templates.yaml`

**Purpose:** Define specific response templates that reference base components

**Structure:**
```yaml
templates:
  planning:
    name: "Planning System"
    base_structure: |
      ## 🧠 CORTEX {operation}
      **Author:** Asif Hussain
      
      {understanding_section}
      {challenge_section}
      {response_section}
      {request_echo_section}
      {next_steps_section}
    understanding_content: "..."
    challenge_content: "..."
```

**How It Works:**
1. Template references `{understanding_section}` placeholder
2. Renderer looks up `understanding_section` in base-components.yaml
3. Renderer replaces placeholder with component's format string
4. Component's format string contains its own placeholders (e.g., `{understanding_content}`)
5. Renderer fills those placeholders with template-specific content

### Layer 3: Template Renderer

**File:** `src/response_templates/response_template_manager.py`

**Rendering Process:**
```python
def render_template(template_name):
    # 1. Load template from response-templates.yaml
    template = load_template(template_name)
    
    # 2. Load base components
    components = load_base_components()
    
    # 3. Replace component placeholders with component formats
    for component_name, component_data in components.items():
        template = template.replace(
            f"{{{component_name}}}", 
            component_data['format']
        )
    
    # 4. Fill content placeholders with template-specific data
    rendered = template.format(**template_content)
    
    return rendered
```

---

## Key Discovery (v3.0 Migration)

**Problem:** Response Format v3.0 changed section names, but updates to `response-templates.yaml` and Python code didn't fully work.

**Root Cause:** Templates were composing from `base-components.yaml`, which still had old v2.0 section names.

**Solution:** Update component definitions in `base-components.yaml` - all runtime-generated templates fixed automatically.

**Lesson:** When changing response format:
1. Update `base-components.yaml` FIRST (single source of truth)
2. Update any hardcoded templates in `response-templates.yaml` (rare)
3. Update Python code with hardcoded templates (4 files)
4. Update tests to validate new format

---

## Component Types

### 1. Section Components

Define the 5-part response structure:
- `understanding_section`
- `challenge_section` 
- `response_section`
- `request_echo_section`
- `next_steps_section`

### 2. Header Components

Define response headers:
- `base_header` - Standard CORTEX header with author attribution
- `presentation_header` - Simplified header for stakeholder presentations

### 3. Footer Components

Define response footers (if needed):
- Currently unused, reserved for future

---

## Benefits

**1. Single Point of Change**
- Format updates in one file propagate to all 62 templates
- Example: v3.0 migration required 3 component edits vs 62 template edits

**2. Consistency**
- All templates use identical formatting by default
- Reduces drift and maintains brand voice

**3. Testability**
- Test component definitions once
- Template tests focus on content, not format

**4. Maintainability**
- Clear separation: components = how, templates = what
- Future developers understand architecture quickly

---

## Usage Patterns

### Creating New Template

```yaml
# In response-templates.yaml
new_template:
  name: "My New Template"
  base_structure: |
    ## 🧠 CORTEX {operation}
    **Author:** Asif Hussain
    
    {understanding_section}
    {challenge_section}
    {response_section}
    {request_echo_section}
    {next_steps_section}
  understanding_content: "Template-specific understanding text"
  challenge_content: "Template-specific challenge text"
  response_content: "Template-specific response text"
  request_echo_content: "Template-specific impact text"
  next_steps_content: "Template-specific next steps"
```

**No need to define section formats** - they're inherited from base-components.yaml

### Overriding Component Format (Rare)

If a template needs custom formatting, embed format directly:

```yaml
custom_template:
  base_structure: |
    ## 🎯 CUSTOM FORMAT
    
    ### Custom Section
    {custom_content}
  custom_content: "Custom text"
```

**Use sparingly** - defeats single-point-of-change benefit

---

## Testing Strategy

### Component Tests

**File:** `tests/response_templates/test_base_components.py`

```python
def test_component_has_required_format():
    """Validate component defines format string"""
    components = load_base_components()
    assert 'understanding_section' in components
    assert 'format' in components['understanding_section']
    
def test_component_uses_v3_names():
    """Validate v3.0 section names"""
    components = load_base_components()
    format_str = components['understanding_section']['format']
    assert "Understanding & Scope" in format_str
    assert "My Understanding Of Your Request" not in format_str
```

### Template Tests

**File:** `tests/response_templates/test_*.py`

```python
def test_template_renders_with_components():
    """Validate template composes correctly"""
    rendered = render_template('planning')
    assert "### 🎯 Understanding & Scope" in rendered
    assert "### ⚡ Approach & Considerations" in rendered
```

---

## Migration Checklist

When changing response format:

- [ ] Update component definitions in `base-components.yaml`
- [ ] Search for hardcoded templates in `response-templates.yaml` (grep "###")
- [ ] Search for hardcoded templates in Python code (grep "### 🎯")
- [ ] Update validation scripts in `scripts/`
- [ ] Update tests to check for new format
- [ ] Run full test suite to validate
- [ ] Commit with comprehensive message documenting changes

---

## Files Reference

| File | Purpose | Change Frequency |
|------|---------|------------------|
| `cortex-brain/response-templates/base-components.yaml` | Component definitions | Rare (format changes) |
| `cortex-brain/response-templates.yaml` | Template content | Frequent (new templates) |
| `src/response_templates/response_template_manager.py` | Rendering logic | Rare (new features) |
| `tests/response_templates/test_*.py` | Validation tests | Frequent (new templates) |

---

## Common Issues

### Issue: Template changes don't appear

**Cause:** Cached components or template reload needed  
**Fix:** Restart application or clear cache

### Issue: Format inconsistent across templates

**Cause:** Hardcoded format strings bypassing components  
**Fix:** Grep for "###" and replace with component references

### Issue: Tests fail after format change

**Cause:** Tests checking for old format strings  
**Fix:** Update test assertions to match new format

---

## Future Enhancements

**Potential Improvements:**
1. Component inheritance (base → specialized)
2. Conditional component rendering (if-then logic)
3. Component versioning (support multiple formats)
4. Runtime component validation (schema checks)
5. Component preview/testing tool

---

**Related Documentation:**
- Response Format v3.0: `.github/prompts/modules/response-format-v3.md`
- Template System: `cortex-brain/response-templates.yaml`
- Migration Guide: Git commit `d8be4d7f`

**Status:** ✅ COMPLETE - Component composition architecture documented for future maintainers.
