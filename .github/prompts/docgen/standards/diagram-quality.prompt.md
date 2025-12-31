# 📊 Diagram Quality Standards

**Parent:** `cortex-docgen.prompt.md`  
**Purpose:** Define quality standards for D3.js and Mermaid diagrams

---

## D3.js Visualizations

- ✅ Interactive (hover, click, tooltips)
- ✅ Data-driven (from codebase metrics)
- ✅ Responsive (fit viewport)
- ✅ Animated (300-500ms transitions)
- ✅ Accessible (ARIA labels)

---

## Mermaid Diagrams

- ✅ Accurate (current architecture)
- ✅ Readable (clear labels)
- ✅ Styled (glassmorphism theme)
- ✅ Focused (one concept each)

### Mermaid Theme Configuration

```javascript
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#1a1f3a',
      'primaryTextColor': '#ffffff',
      'primaryBorderColor': '#00d4ff',
      'lineColor': '#00d4ff',
      'secondaryColor': '#2a2f4a',
      'tertiaryColor': '#0a0e27'
    }
  }
}%%
```

---

## Staleness Detection

**Toolkit Script:** `cortex-toolkit/documentation/diagram_staleness.py`

```bash
# Check diagram freshness
python cortex-toolkit/documentation/diagram_staleness.py --max-age 30
```

**Logic:**
- Compare diagram file mtime to related source files
- Flag diagrams >30 days old with changed source code
- Report which diagrams need update

### Staleness Thresholds by Type

| Diagram Type | Staleness Threshold | Rationale |
|--------------|---------------------|-----------|
| Architecture | 30 days | Core, changes infrequently |
| Data Flow | 14 days | Changes with features |
| API Reference | 7 days | Changes frequently |

---

## Story Generator Guidelines

### Character Voices

| Character | Voice | Color |
|-----------|-------|-------|
| **Asif Codenstein** | First-person, self-deprecating humor | `#00d4ff` (blue) |
| **Miss G** | Sassy AI, witty comebacks | `#ff00ff` (magenta) |

### Whiteboard Code Panels

Use `.whiteboard-panel` class for pseudo-code in story chapters.

**Location:** `docs/story/`

When new features discovered, update narrative:
- Opening banter (Asif + Miss G)
- Whiteboard pseudo-code session
- Solution discovery
- Victory celebration
