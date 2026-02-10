# YAML Response Format Guide
**Version:** 1.0 | **Updated:** 2026-02-05 | **Authority:** Response Format Standards

---

## 🎯 Purpose

This guide ensures YAML files containing response templates render correctly in GitHub Copilot Chat sessions as **formatted markdown** rather than raw text.

---

## ❌ Problem: Raw Markdown Display

When YAML files contain markdown code fences (````markdown`, ````python`, etc.) inside multi-line strings, GitHub Copilot Chat renders them as **raw markdown text** instead of formatted HTML.

### Bad Example (Renders as Raw Text)

```yaml
implementation_notes: |
  Example output:
  ```markdown
  ## 🔍 Analysis
  **Status:** Complete ✅
  ```
```

**Result in Chat:** User sees literal backticks and "markdown" keyword instead of formatted output.

---

## ✅ Solution: Use Plain Indented Text

Replace code fences with **plain indented text** or **box-drawing characters** for tables.

### Good Example (Renders as Formatted)

```yaml
implementation_notes: |
  Example output:
  
    🔍 Analysis
    Status: Complete ✅
```

**Result in Chat:** Properly formatted with icons and styling.

---

## 📐 Formatting Patterns

### 1. Simple Text Blocks

**Bad:**
```yaml
example: |
  ```markdown
  ## Header
  **Bold text**
  ```
```

**Good:**
```yaml
example: |
  
    Header
    Bold text
```

---

### 2. Tables

**Bad:**
```yaml
output: |
  ```markdown
  | Column | Value |
  |--------|-------|
  | Status | ✅    |
  ```
```

**Good (Box Drawing):**
```yaml
output: |
  
    ┌────────┬───────┐
    │ Column │ Value │
    ├────────┼───────┤
    │ Status │ ✅    │
    └────────┴───────┘
```

**Box Drawing Characters:**
- `┌` `┐` `└` `┘` (corners)
- `─` (horizontal)
- `│` (vertical)
- `├` `┤` `┬` `┴` `┼` (junctions)

---

### 3. Code Examples

**Bad:**
```yaml
usage: |
  ```python
  result = function()
  # Returns: data
  ```
```

**Good:**
```yaml
usage: |
  
    result = function()
    Returns: data
```

---

### 4. Command Examples

**Bad:**
```yaml
workflow: |
  ```bash
  git checkout -b feature
  git commit -m "Add feature"
  ```
```

**Good:**
```yaml
workflow: |
  
    git checkout -b feature
    git commit -m "Add feature"
```

---

## 🔍 Detection & Fixing

### Find All Code Fences in YAML

```bash
grep -rn '```' --include="*.yaml" docs/meta/
```

### Automated Fix Pattern

1. **Identify:** ````language` ... `` ` `` patterns inside YAML strings
2. **Remove:** Opening ```` ```language` and closing `` ` `` lines
3. **Indent:** Content by 2-4 spaces for readability
4. **Simplify:** Comments inline (e.g., `# comment` → `comment`)

---

## 📋 YAML File Categories

| File Type | Priority | Impact |
|-----------|----------|--------|
| **enhancement-history.yaml** | 🔴 Critical | Displayed in every DESIGN response |
| **Plan files** | 🟡 Medium | Viewed during implementation |
| **Config files** | 🟢 Low | Rarely read directly |

**Focus:** Fix enhancement-history.yaml first (user-facing).

---

## ✅ Verification Checklist

Before committing YAML changes:

- [ ] No ```` ``` ```` (triple backticks) in multi-line strings
- [ ] Tables use box-drawing or plain text
- [ ] Code examples use simple indentation
- [ ] Commands listed without bash/zsh keywords
- [ ] Test rendering in Copilot Chat (paste YAML content)

---

## 🎓 Related Documentation

- [response-format-standards.md](../../.github/prompts/response-format-standards.md) — Overall response formatting
- [enhancement-history.yaml](enhancement-history.yaml) — Main registry (fixed)
- ENH-028 — Semantic Response Layering (rationale)

---

**Authority:** This guide enforces ENH-028 response format standards for YAML files.  
**Enforcement:** All enhancement-history.yaml updates MUST follow this guide.  
**Review:** Check during code reviews and before CORTEX releases.
