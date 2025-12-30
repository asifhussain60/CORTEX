# CORTEX Documentation Hierarchy Guide

**Version:** 4.0.0  
**Author:** Asif Hussain  
**Date:** 2025-12-28  
**Purpose:** Define the three-tier documentation model to prevent duplication and ensure consistency

---

## 🎯 Overview

CORTEX documentation follows a **three-tier model** where each tier serves a distinct audience and purpose. This hierarchy prevents duplication, maintains clarity, and ensures users can find the right level of detail for their needs.

---

## 📊 The Three-Tier Model

### Tier 1: Features (Overview & Marketing)

**Location:** `docs/features/`  
**Target Audience:** Decision makers, new users, evaluators  
**Purpose:** High-level benefits, use cases, value proposition  
**Word Count:** 500-800 words per page

#### Content Guidelines:

✅ **Include:**
- **Problem statement** (What pain does this solve?)
- **Key benefits** (3-5 bullet points)
- **Simple command example** (1-2 commands)
- **Metrics summary** (from `orchestrator-metrics.json`)
- **Call-to-action** link to Tier 2 (complete docs)

❌ **Exclude:**
- Detailed workflow steps
- Technical implementation details
- Troubleshooting guides
- API references
- Code examples beyond basic commands

#### Example Structure:

```html
<section class="feature-benefit-panel">
    <h2>What Is [Feature Name]?</h2>
    <p>[1-2 sentence value proposition]</p>
</section>

<section>
    <h2>Key Benefits</h2>
    <ul>
        <li>Benefit 1</li>
        <li>Benefit 2</li>
        <li>Benefit 3</li>
    </ul>
</section>

<section>
    <h2>Quick Example</h2>
    <code>plan user authentication</code>
</section>

<a href="../orchestrators/[feature].html" class="cta-button">
    View Complete Documentation →
</a>
```

---

### Tier 2: Orchestrators (Complete User Documentation)

**Location:** `docs/orchestrators/`  
**Target Audience:** All users (technical and non-technical)  
**Purpose:** Complete workflow documentation, command reference, troubleshooting  
**Word Count:** 1500-3000 words per page

**⭐ This is the SOURCE OF TRUTH for user-facing documentation.**

#### Content Guidelines:

✅ **Include:**
- **Full workflow description** (all phases)
- **Phase-by-phase breakdown** with visual workflow
- **Command syntax** with all options
- **Output examples** (terminal output, file structure)
- **Troubleshooting section** (common issues + fixes)
- **Integration points** (how it works with other orchestrators)
- **Metrics** (from `orchestrator-metrics.json`)
- **Technical sections** for advanced users (merged from Tier 3 where needed)
- **Link to Tier 3** (technical implementation) if it exists

❌ **Exclude:**
- Marketing fluff (leave that for Tier 1)
- Deep implementation details (code structure, algorithms) unless merged for comprehensive docs

#### Example Structure:

```html
<h1>[Orchestrator Name]</h1>
<p>[1-2 paragraph explanation of what it does]</p>

<!-- Metrics -->
<div class="metrics-grid">
    <div class="metric-card">
        <div class="metric-value">[Value from JSON]</div>
        <div class="metric-label">[Label]</div>
    </div>
</div>

<!-- Command Syntax -->
<div class="command-card">
    <code>[command] [options]</code>
</div>

<!-- Workflow -->
<section>
    <h2>The [N]-Phase Workflow</h2>
    <div class="workflow-phases">
        <div class="phase-card">
            <span class="phase-number">1</span>
            <div class="phase-title">[Phase Name]</div>
            <p>[Phase description]</p>
        </div>
        <!-- Repeat for each phase -->
    </div>
</section>

<!-- Examples -->
<section>
    <h2>Usage Examples</h2>
    <pre>[Terminal output]</pre>
</section>

<!-- Troubleshooting -->
<section>
    <h2>Troubleshooting</h2>
    <ul>
        <li><strong>Issue:</strong> [Problem] → <strong>Fix:</strong> [Solution]</li>
    </ul>
</section>

<!-- Technical Details (if merged from Tier 3) -->
<section>
    <h2>Technical Implementation</h2>
    <p>[Architecture, code structure, APIs for advanced users]</p>
</section>
```

---

### Tier 3: Technical (Implementation Details)

**Location:** `docs/technical/orchestrators/`  
**Target Audience:** Contributors, developers extending CORTEX  
**Purpose:** Architecture, code structure, APIs, contribution guidelines  
**Word Count:** 2000-5000 words per page

#### Content Guidelines:

✅ **Include:**
- **System architecture** diagrams
- **Code structure** (file organization, key classes)
- **API references** (function signatures, parameters)
- **Algorithm descriptions** (how it works internally)
- **Extension points** (how to add new features)
- **Contribution guidelines** (how to modify this orchestrator)
- **Performance considerations**

❌ **Exclude:**
- User-facing workflows (that's Tier 2)
- Marketing content (that's Tier 1)

#### Example Structure:

```html
<h1>[Orchestrator Name] - Technical Reference</h1>

<section>
    <h2>Architecture</h2>
    <pre class="mermaid">[Architecture diagram]</pre>
</section>

<section>
    <h2>Code Structure</h2>
    <pre>
src/orchestrators/[name]/
├── __init__.py
├── phases/
└── validators/
    </pre>
</section>

<section>
    <h2>API Reference</h2>
    <h3>execute_phase_1(context: PlanContext)</h3>
    <p>[Description]</p>
    <ul>
        <li><strong>Parameters:</strong> [List]</li>
        <li><strong>Returns:</strong> [Type]</li>
    </ul>
</section>

<section>
    <h2>Extension Points</h2>
    <p>To add a new complexity tier:</p>
    <ol>
        <li>[Step 1]</li>
        <li>[Step 2]</li>
    </ol>
</section>
```

---

## 🔀 Decision Matrix: Which Tier?

| Question | Tier 1 | Tier 2 | Tier 3 |
|----------|--------|--------|--------|
| Is this a high-level benefit? | ✅ | ❌ | ❌ |
| Is this a complete workflow? | ❌ | ✅ | ❌ |
| Is this an API reference? | ❌ | ❌ | ✅ |
| Will users run this command? | ✅ (basic) | ✅ (complete) | ❌ |
| Does this explain "why"? | ✅ | ✅ | ❌ |
| Does this explain "how"? | ❌ | ✅ | ✅ (deep) |
| Will contributors modify this code? | ❌ | ❌ | ✅ |

---

## 📏 Word Count Targets

| Tier | Min | Target | Max | Purpose |
|------|-----|--------|-----|---------|
| Tier 1 | 500 | 650 | 800 | Quick overview |
| Tier 2 | 1500 | 2000 | 3000 | Complete docs |
| Tier 3 | 2000 | 3000 | 5000 | Deep technical |

---

## 🔗 Cross-Referencing Rules

### From Tier 1 → Tier 2
✅ **Always include prominent CTA:**
```html
<a href="../orchestrators/[name].html" class="cta-button">
    View Complete Documentation →
</a>
```

### From Tier 2 → Tier 3
✅ **Include link at end of page:**
```html
<section>
    <h2>Technical Reference</h2>
    <p>For implementation details, architecture, and contribution guidelines:</p>
    <a href="../technical/orchestrators/[name].html">Technical Documentation →</a>
</section>
```

### From Tier 3 → Tier 2
✅ **Include breadcrumb navigation:**
```html
<nav class="breadcrumb">
    <a href="../../orchestrators/[name].html">User Documentation</a>
    <span>→</span>
    <span>Technical Reference</span>
</nav>
```

---

## 🚫 Anti-Patterns (What NOT to Do)

❌ **Don't duplicate content across tiers**
- Each tier should have distinct content
- Use links, not copy-paste

❌ **Don't mix audiences in the same page**
- Exception: Tier 2 can include technical sections for comprehensive coverage

❌ **Don't put technical details in Tier 1**
- Keep it high-level and benefits-focused

❌ **Don't put marketing in Tier 3**
- Stay technical and implementation-focused

❌ **Don't hardcode metrics**
- Always reference `assets/data/orchestrator-metrics.json`

---

## 📊 Metrics Management

### Single Source of Truth

**File:** `docs/assets/data/orchestrator-metrics.json`

All phase counts, success rates, and metrics MUST come from this file.

### How to Use Metrics

#### Option 1: JavaScript Injection (Recommended)
```javascript
fetch('/assets/data/orchestrator-metrics.json')
    .then(r => r.json())
    .then(data => {
        document.getElementById('phase-count').textContent = 
            data.orchestrators.planning_system.metrics.core_phases;
    });
```

#### Option 2: Manual Update (Current)
1. Edit `orchestrator-metrics.json`
2. Update all affected HTML files manually
3. Verify consistency with grep search

---

## ✅ Quality Checklist

Before publishing any documentation page:

### Tier 1 (Features)
- [ ] 500-800 words
- [ ] Clear problem statement
- [ ] 3-5 bullet point benefits
- [ ] Simple command example
- [ ] CTA link to Tier 2
- [ ] No technical implementation details

### Tier 2 (Orchestrators)
- [ ] 1500-3000 words
- [ ] All phases documented
- [ ] Command syntax with examples
- [ ] Output examples included
- [ ] Troubleshooting section
- [ ] Metrics from JSON file
- [ ] Link to Tier 3 (if exists)

### Tier 3 (Technical)
- [ ] 2000-5000 words
- [ ] Architecture diagram
- [ ] Code structure documented
- [ ] API references complete
- [ ] Extension points documented
- [ ] No user-facing workflow duplication

---

## 📝 Examples

### Good: Three-Tier Implementation

**Tier 1 (features/planning-system.html):**
- 650 words
- Explains how it saves time
- Shows `plan [feature]` command
- Links to orchestrators/planning-system.html

**Tier 2 (orchestrators/planning-system.html):**
- 2200 words
- Documents all 4 phases
- Shows command examples with output
- Includes troubleshooting
- Links to technical/orchestrators/planning-system.html

**Tier 3 (technical/orchestrators/planning-system.html):**
- 3500 words
- Architecture diagrams
- Code structure
- API references
- Contribution guidelines

### Bad: Duplication

❌ All three tiers explain the 4-phase workflow in detail  
❌ Tier 1 has 2000 words of technical content  
❌ Metrics hardcoded differently in each file  
❌ No clear links between tiers

---

## 🔄 Maintenance

### When Metrics Change
1. Update `orchestrator-metrics.json`
2. Propagate to all affected pages
3. Verify with: `grep -r "[old-value]" docs/`

### When Adding New Orchestrator
1. Create Tier 1 page (features/)
2. Create Tier 2 page (orchestrators/) - **SOURCE OF TRUTH**
3. Create Tier 3 page (technical/) if needed
4. Add entry to `orchestrator-metrics.json`
5. Update navigation (index.html, features/index.html, orchestrators/index.html)

### When Refactoring
1. Check all three tiers
2. Ensure no duplication introduced
3. Verify cross-references still valid
4. Update metrics JSON if needed

---

## 📚 See Also

- `docs/README.md` - Documentation structure overview
- `assets/data/orchestrator-metrics.json` - Metrics source of truth
- `cortex-brain/brain-protection-rules.yaml` - SKULL rules preventing duplication

---

**Author:** Asif Hussain  
**Last Updated:** 2025-12-28  
**Version:** 4.0.0
