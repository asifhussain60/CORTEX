# Diagram Regeneration Orchestrator Guide

**Purpose:** Automated regeneration of all CORTEX architecture diagrams with D3.js interactive dashboards  
**Version:** 1.0  
**Status:** ✅ PRODUCTION

---

## 🎯 Overview

The Diagram Regeneration Orchestrator manages the complete lifecycle of CORTEX system diagrams, including:
- Architecture diagrams (system structure, component relationships)
- Workflow visualizations (TDD, planning, upgrade flows)
- Component relationship diagrams
- System flow diagrams with D3.js interactivity

---

## 🚀 Commands

**Natural Language Triggers:**
- `regenerate diagrams`
- `generate diagrams`
- `rebuild diagrams`
- `refresh diagrams`
- `update diagrams`
- `create diagrams`

**Use Cases:**
- After adding new orchestrators or agents
- After architecture changes
- Before documentation releases
- When visual documentation is outdated

---

## 📊 What Gets Generated

### 1. Architecture Diagrams
**Output Format:** Mermaid + PNG + D3.js interactive dashboard

**Diagrams Created:**
- `docs/architecture/system-overview.png` - High-level CORTEX architecture
- `docs/architecture/brain-tiers.png` - 4-tier brain architecture (Tier 0-3)
- `docs/architecture/agent-ecosystem.png` - All agents and relationships
- `docs/architecture/orchestrator-flow.png` - Orchestrator workflow patterns

### 2. Workflow Diagrams
**Output Format:** Mermaid + PNG + D3.js

**Workflows Visualized:**
- `docs/workflows/tdd-cycle.png` - RED→GREEN→REFACTOR flow
- `docs/workflows/planning-workflow.png` - Planning System 2.0 flow
- `docs/workflows/upgrade-process.png` - Upgrade orchestrator steps
- `docs/workflows/git-checkpoint.png` - Checkpoint creation and rollback

### 3. Component Relationship Diagrams
**Output Format:** D3.js force-directed graphs

**Relationships Mapped:**
- Orchestrators → Agents
- Agents → Tier APIs
- Operations → Templates
- Workflows → Checkpoints

---

## ⚙️ How It Works

### Phase 1: Discovery (10s)
```
Scan repository structure:
- .github/prompts/modules/*.md (documentation)
- src/operations/modules/**/*.py (orchestrators)
- src/cortex_agents/**/*.py (agents)
- cortex-brain/response-templates.yaml (wiring)
```

### Phase 2: Status Analysis (5s)
```
For each diagram:
- Check if prompt file exists (has_prompt)
- Check if narrative description exists (has_narrative)
- Check if mermaid source exists (has_mermaid)
- Check if PNG render exists (has_image)
- Calculate completion percentage (0-100%)
```

### Phase 3: Regeneration (30-60s)
```
For incomplete/outdated diagrams:
1. Generate Mermaid source code
2. Render to PNG using mermaid-cli
3. Create D3.js interactive version
4. Update documentation links
```

### Phase 4: Dashboard Generation (10s)
```
Create interactive dashboard:
- Diagram status grid (complete/incomplete)
- Staleness indicators (>7 days old)
- Quick navigation links
- Regeneration history
```

---

## 🔧 Configuration

**Config File:** `cortex.config.json`

```json
{
  "diagram_regeneration": {
    "output_directory": "docs/architecture/",
    "format": "png",
    "interactive_dashboard": true,
    "mermaid_theme": "default",
    "max_age_days": 30,
    "auto_regenerate": true
  }
}
```

**Options:**
- `output_directory` - Where diagrams are saved (default: `docs/architecture/`)
- `format` - Output format: `png`, `svg`, `pdf` (default: `png`)
- `interactive_dashboard` - Enable D3.js dashboards (default: `true`)
- `mermaid_theme` - Mermaid theme: `default`, `dark`, `forest` (default: `default`)
- `max_age_days` - Diagram staleness threshold (default: 30)
- `auto_regenerate` - Auto-regenerate on orchestrator changes (default: `true`)

---

## 📈 Output Examples

### Diagram Status Report
```
✅ system-overview.png (100% complete)
⚠️  brain-tiers.png (75% complete - missing interactive dashboard)
❌ agent-ecosystem.png (25% complete - outdated, last modified 45 days ago)
```

### Interactive Dashboard
- **Location:** `cortex-brain/admin/reports/diagram-dashboard.html`
- **Features:** Live diagram previews, status filters, regeneration history
- **Access:** Open in browser after regeneration

---

## 🐛 Troubleshooting

### Issue: "mermaid-cli not found"

**Solution:**
```pwsh
npm install -g @mermaid-js/mermaid-cli
```

### Issue: "Diagram generation failed"

**Check:**
1. Mermaid syntax valid: `mmdc --help`
2. Output directory writable: `Test-Path docs/architecture/`
3. Dependency installed: `npm list -g @mermaid-js/mermaid-cli`

### Issue: "Interactive dashboard not loading"

**Check:**
1. D3.js library included: `cortex-brain/admin/reports/diagram-dashboard.html` has D3.js CDN
2. Browser supports ES6: Use modern browser (Chrome, Firefox, Edge)
3. Dashboard file exists: `Test-Path cortex-brain/admin/reports/diagram-dashboard.html`

---

## 📚 Related Documentation

- **System Alignment Guide:** `.github/prompts/modules/system-alignment-guide.md`
- **Enterprise Documentation:** `.github/prompts/modules/enterprise-documentation-guide.md`
- **Design Sync:** `.github/prompts/modules/design-sync-orchestrator-guide.md`

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)
