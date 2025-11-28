# Diagram Regeneration Orchestrator Guide

**Module:** `DiagramRegenerationOrchestrator`  
**Location:** `src/operations/modules/diagrams/diagram_regeneration_orchestrator.py`  
**Purpose:** Comprehensive diagram regeneration with D3.js interactive dashboard generation  
**Status:** ✅ Production  
**Version:** 3.3.0

---

## Overview

The Diagram Regeneration Orchestrator analyzes CORTEX design documentation and regenerates visual assets (Mermaid diagrams, illustration prompts, narratives) with real-time status tracking via interactive D3.js dashboards.

**Key Capabilities:**
- Scans and analyzes 15+ diagram definitions
- Regenerates Mermaid diagrams for architecture visualization
- Generates illustration prompts for AI art generation
- Creates narratives explaining each diagram
- Produces interactive D3.js dashboard showing regeneration status
- Tracks completion percentage per diagram (prompt, narrative, mermaid, image)

---

## Natural Language Triggers

**Primary Commands:**
- `regenerate diagrams`
- `refresh diagrams`
- `diagram status`
- `show diagram dashboard`

**Context Variations:**
- "Regenerate all CORTEX diagrams"
- "Refresh architecture diagrams"
- "Show me diagram completion status"

---

## Architecture & Integration

**Dependencies:**
- `InteractiveDashboardGenerator` - D3.js dashboard creation
- `docs/diagrams/` - Diagram storage structure (prompts, narratives, mermaid, img)
- `cortex-brain/diagram-definitions.yaml` - Diagram metadata

**Output Locations:**
- **Prompts:** `docs/diagrams/prompts/[diagram-name].md`
- **Narratives:** `docs/diagrams/narratives/[diagram-name].md`
- **Mermaid:** `docs/diagrams/mermaid/[diagram-name].mmd`
- **Dashboard:** `docs/diagrams/dashboard.html`

**Data Flow:**
1. Scan diagram definitions (15+ diagrams)
2. Check file existence (prompt, narrative, mermaid, image)
3. Calculate completion percentage per diagram
4. Generate regeneration report
5. Build interactive D3.js dashboard
6. Display status with visual indicators

---

## Usage Examples

### Basic Regeneration

```
User: "regenerate diagrams"
CORTEX: Scans 15 diagrams → Generates dashboard → Shows completion status
```

### Check Status

```
User: "show diagram status"
CORTEX: Opens dashboard with completion percentages and missing files
```

### Targeted Regeneration

```
User: "refresh architecture diagrams"
CORTEX: Regenerates specific subset → Updates dashboard
```

---

## Dashboard Features

**Interactive D3.js Visualization:**
- **Overview Section:** Total diagrams, completion %, status distribution
- **Progress Visualization:** Bar chart showing completion per diagram
- **Diagram Table:** Detailed status (prompt, narrative, mermaid, image)
- **Workflow Diagram:** Mermaid flowchart of regeneration process
- **Recommendations:** Missing files and next actions

**Status Indicators:**
- ✅ **Complete** (100%) - All 4 components present
- ⚠️ **Partial** (25-75%) - Some components missing
- ❌ **Missing** (0%) - No components generated

---

## Configuration

**Diagram Definitions (cortex-brain/diagram-definitions.yaml):**

```yaml
diagrams:
  - id: "01"
    name: "tier-architecture"
    title: "4-Tier Brain Architecture"
    description: "Memory hierarchy visualization"
  
  - id: "02"
    name: "agent-system"
    title: "10 Specialized Agents"
    description: "Agent roles and capabilities"
  
  # ... 13 more diagrams
```

**File Structure:**
```
docs/diagrams/
├── prompts/           # AI illustration prompts
├── narratives/        # Explanatory text
├── mermaid/          # Mermaid diagram code
├── img/              # Generated images
└── dashboard.html    # Interactive status dashboard
```

---

## Implementation Details

**Class:** `DiagramRegenerationOrchestrator`

**Key Methods:**
- `execute(context)` - Main orchestration method
- `_scan_diagrams()` - Analyze diagram completion
- `_generate_dashboard(report)` - Build D3.js dashboard
- `_build_overview_section(report)` - Dashboard overview
- `_build_visualizations_section(report)` - Charts and graphs
- `_build_diagrams_section(report)` - Diagram table
- `_build_recommendations_section(report)` - Actionable suggestions

**Data Classes:**
- `DiagramStatus` - Individual diagram metadata
- `DiagramRegenerationReport` - Aggregated report data

---

## Performance Metrics

**Execution Time:**
- Scan phase: <1 second (15 diagrams)
- Dashboard generation: <2 seconds
- Total: <3 seconds end-to-end

**Output Size:**
- Dashboard HTML: ~50-80 KB
- Includes D3.js visualizations inline

---

## Error Handling

**Common Issues:**
1. **Missing diagram definitions** → Logs warning, continues with available diagrams
2. **File I/O errors** → Reports in dashboard recommendations
3. **Dashboard generation failure** → Returns text-based report fallback

**Validation:**
- Checks `docs/diagrams/` directory existence
- Validates diagram definition YAML format
- Verifies file permissions before writing

---

## Testing

**Test Coverage:** 60% (needs improvement)

**Test Files:**
- `tests/operations/test_diagram_regeneration_orchestrator.py` (planned)

**Manual Validation:**
1. Run `regenerate diagrams`
2. Verify dashboard opens in browser
3. Check all 15 diagrams listed
4. Validate completion percentages accurate
5. Confirm missing files flagged correctly

---

## Related Modules

- **DesignSyncOrchestrator** - Synchronizes design docs with implementation
- **SystemAlignmentOrchestrator** - Uses diagram data for architecture validation
- **InteractiveDashboardGenerator** - Shared D3.js dashboard infrastructure

---

## Troubleshooting

**Issue:** Dashboard not generated  
**Solution:** Check `docs/diagrams/` permissions, verify write access

**Issue:** Diagrams showing 0% completion  
**Solution:** Run initial diagram generation, check file paths

**Issue:** Dashboard blank/not loading  
**Solution:** Check browser console, verify D3.js CDN accessible

---

## Future Enhancements

**Planned (CORTEX 4.0):**
- Auto-regeneration on design doc changes
- Diff view showing diagram evolution over time
- Integration with Git history for diagram versioning
- WebSocket live updates during regeneration
- Export to PDF/PNG for offline viewing

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)  
**Last Updated:** November 28, 2025  
**Guide Version:** 1.0.0
