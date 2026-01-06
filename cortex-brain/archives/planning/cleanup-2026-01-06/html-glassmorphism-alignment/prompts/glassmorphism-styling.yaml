# 🎨 Glassmorphism Styling Prompt Template

**Version:** 1.0.0 | **Created:** 2026-01-05  
**Purpose:** Reusable prompt for applying glassmorphism colors to HTML elements  
**Context:** HTML View Standardization Plan (Phase 16b)

---

## 📋 Prompt Template

```
Apply glassmorphism color styling to {TARGET_ELEMENT} on {TARGET_FILE}.

CONTEXT FILES (auto-reference):
- Design Standard: cortex-brain/documents/standards/glassmorphism-design-standard.md
- Reference Implementation: docs/panel-viewer.html
- Reference CSS: docs/assets/css/panel-viewer.css
- Main CSS: docs/assets/css/main.css

REQUIREMENTS:
1. Identify {TARGET_ELEMENT} in {TARGET_FILE}
2. Search glassmorphism-design-standard.md for color class patterns
3. Search panel-viewer.html and panel-viewer.css for approved template examples
4. Apply color variant classes following pattern:
   - .card-icon-primary (purple gradient)
   - .card-icon-success (green gradient)
   - .card-icon-info (blue gradient)
   - .card-icon-warning (amber gradient)
5. Add CSS definitions if missing (check main.css first)
6. Match existing .metric-icon-* pattern for consistency

WORKFLOW:
1. Read target file to locate elements
2. Search design standard for color guidelines
3. Search reference files for approved patterns
4. Identify existing CSS color classes
5. Apply HTML class changes
6. Add CSS definitions if needed
7. Validate against glassmorphism standard

OUTPUT:
- Modified HTML with color classes applied
- New CSS classes added to main.css (if needed)
- Summary of color assignments
```

---

## 🎯 Usage Examples

### Example 1: Token Optimization Cards

**Prompt:**
```
Apply glassmorphism color styling to Optimization Strategy cards on docs/token-optimization/index.html.

CONTEXT FILES (auto-reference):
- Design Standard: cortex-brain/documents/standards/glassmorphism-design-standard.md
- Reference Implementation: docs/panel-viewer.html
- Reference CSS: docs/assets/css/panel-viewer.css
- Main CSS: docs/assets/css/main.css
```

**Expected Actions:**
1. ✅ Read `docs/token-optimization/index.html` (lines 214-285)
2. ✅ Search `glassmorphism-design-standard.md` for color patterns
3. ✅ Search `panel-viewer.html` for approved card templates
4. ✅ Search `main.css` for existing `.metric-icon-*` classes
5. ✅ Apply `.card-icon-primary/success/info/warning` to HTML
6. ✅ Add CSS definitions to `main.css` (after `.card-icon` base class)
7. ✅ Validate color scheme matches standard

### Example 2: Architecture Tier Cards

**Prompt:**
```
Apply glassmorphism color styling to Tier cards on docs/architecture/index.html.

CONTEXT FILES (auto-reference):
- Design Standard: cortex-brain/documents/standards/glassmorphism-design-standard.md
- Reference Implementation: docs/panel-viewer.html
- Reference CSS: docs/assets/css/panel-viewer.css
- Main CSS: docs/assets/css/main.css
```

### Example 3: Security Feature Cards

**Prompt:**
```
Apply glassmorphism color styling to Security feature cards on docs/security/index.html.

CONTEXT FILES (auto-reference):
- Design Standard: cortex-brain/documents/standards/glassmorphism-design-standard.md
- Reference Implementation: docs/panel-viewer.html
- Reference CSS: docs/assets/css/panel-viewer.css
- Main CSS: docs/assets/css/main.css
```

---

## 🔍 Context Discovery Pattern

**Copilot should automatically:**

1. **Read Target File** → Locate elements needing color
2. **Search Design Standard** → Find color class patterns and guidelines
3. **Search Reference Files** → Identify approved template implementations
4. **Search Existing CSS** → Check for existing color variant classes
5. **Apply Changes** → HTML classes + CSS definitions
6. **Validate** → Ensure compliance with glassmorphism standard

**NO manual reminders needed for:**
- File references
- Context gathering sequence
- CSS pattern matching
- Color scheme validation

---

## 📊 Color Class Reference

**Pattern:** `.card-icon-{variant}` or `.metric-icon-{variant}`

| Variant | Gradient | Shadow | Use Case |
|---------|----------|--------|----------|
| `primary` | #7b61ff → #9f87ff | rgba(123,97,255,0.3) | Primary actions, core features |
| `success` | #10b981 → #34d399 | rgba(16,185,129,0.3) | Positive outcomes, active states |
| `info` | #3b82f6 → #60a5fa | rgba(59,130,246,0.3) | Informational, neutral features |
| `warning` | #f59e0b → #fbbf24 | rgba(245,158,11,0.3) | Important notices, caution |

**CSS Structure:**
```css
.card-icon-{variant} {
    width: 4rem;
    height: 4rem;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 1rem;
    border-radius: var(--radius-md);
    background: linear-gradient(135deg, {color1}, {color2});
    box-shadow: 0 8px 24px {shadow-color};
    font-size: 2rem;
    color: var(--text-primary);
}

.glass-card-clickable:hover .card-icon-{variant} {
    box-shadow: 0 12px 32px {enhanced-shadow};
    transform: scale(1.05);
    transition: all var(--transition-base);
}
```

---

## ✅ Success Criteria

- [ ] Target elements identified in HTML
- [ ] Color variant classes applied
- [ ] CSS definitions added (if missing)
- [ ] Color scheme matches glassmorphism standard
- [ ] Hover effects implemented
- [ ] No inline styles used
- [ ] Consistent with existing `.metric-icon-*` pattern

---

## 🚀 Invocation

**Simple Form:**
```
Apply glassmorphism color styling to {element_description} on {file_path}.
```

**Expanded Form (optional):**
```
Apply glassmorphism color styling to {element_description} on {file_path}.

CONTEXT FILES (auto-reference):
- Design Standard: cortex-brain/documents/standards/glassmorphism-design-standard.md
- Reference Implementation: docs/panel-viewer.html
- Reference CSS: docs/assets/css/panel-viewer.css
- Main CSS: docs/assets/css/main.css

ADDITIONAL CONTEXT (optional):
- {any specific requirements}
- {any constraints}
```

---

## 📚 Related Documents

- **Design Standard:** `cortex-brain/documents/standards/glassmorphism-design-standard.md`
- **HTML Plan:** `cortex-brain/documents/planning/active/html-glassmorphism-alignment/00-html-view-standardization.md`
- **Reference Panel Viewer:** `docs/panel-viewer.html`
- **Reference CSS:** `docs/assets/css/panel-viewer.css`
- **Main Stylesheet:** `docs/assets/css/main.css`

---

**Last Updated:** 2026-01-05  
**Maintained By:** HTML View Standardization Plan  
**Version:** 1.0.0
