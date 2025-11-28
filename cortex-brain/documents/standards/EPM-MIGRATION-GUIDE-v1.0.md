# EPM Migration Guidelines - Documentation Format v1.0

**Version:** 1.0.0  
**Status:** ✅ APPROVED  
**Effective Date:** 2025-11-28  
**Author:** Asif Hussain  
**Target Audience:** CORTEX Developers

---

## 🎯 Purpose

This guide provides **step-by-step instructions** for migrating existing Admin Entry Point Modules (EPMs) to the new interactive documentation format (D3.js dashboards with multi-layer visualization).

**Scope:** All admin operations that generate documentation outputs

---

## 📋 Migration Overview

### Current State

**Legacy Format:** Plain text or simple markdown outputs
- No interactive visualizations
- Limited navigation
- Static content only
- No export functionality

### Target State

**New Format:** Interactive HTML dashboards (v1.0 specification)
- D3.js visualizations (5+ per dashboard)
- Multi-layer tab navigation (5 tabs minimum)
- Smart annotations with tooltips
- Export capabilities (PDF, PNG, PPTX)
- Security-compliant (CSP, XSS prevention)

### Migration Phases

1. **Pre-Migration Assessment** (30 min per EPM)
2. **Template Integration** (2-3 hours per EPM)
3. **Data Transformation** (1-2 hours per EPM)
4. **Visualization Implementation** (3-4 hours per EPM)
5. **Testing & Validation** (2-3 hours per EPM)
6. **Deployment** (1 hour per EPM)

**Total Estimated Time per EPM:** 9-13 hours

---

## 🔍 Pre-Migration Assessment

### Step 1: Identify Target EPMs

**Location:** Search for modules generating documentation

```bash
# Find all EPMs with documentation output
cd /Users/asifhussain/PROJECTS/CORTEX
grep -r "generate.*report\|create.*dashboard\|export.*doc" src/orchestrators/ src/cortex_agents/
```

**Current Admin EPMs (Confirmed):**
1. `SystemAlignmentOrchestrator` - Alignment reports
2. `ArchitectureIntelligenceOrchestrator` - Architecture review dashboards
3. `EnterpriseDocumentationOrchestrator` - Enterprise docs generation
4. `SetupEPMOrchestrator` - Entry point module generation
5. `DeploymentValidationOrchestrator` - Deployment validation reports
6. `LintValidationOrchestrator` - Lint validation reports
7. `BrainExportOrchestrator` - Brain export reports
8. `BrainImportOrchestrator` - Brain import reports

### Step 2: Analyze Current Output Structure

For each EPM, document:
- **Current output format** (txt, md, json, html)
- **Data sources** (databases, files, APIs)
- **Key metrics** (what numbers/scores are displayed)
- **Visualizations** (if any existing charts)
- **User workflows** (how users interact with output)

**Assessment Template:**

```markdown
## EPM: [Name]

**Current Output Format:** [txt/md/json/html]
**Output Location:** [file path]
**Data Sources:**
- Source 1: [description]
- Source 2: [description]

**Key Metrics:**
1. Metric 1: [description]
2. Metric 2: [description]

**Existing Visualizations:** [Yes/No - describe if yes]

**User Workflows:**
1. User opens report
2. User reads sections
3. User takes action (what action?)

**Migration Complexity:** [Low/Medium/High]
**Estimated Hours:** [X hours]
```

### Step 3: Determine Migration Priority

**Priority Matrix:**

| EPM | User Impact | Complexity | Priority |
|-----|-------------|------------|----------|
| SystemAlignment | High | Medium | 1 (Highest) |
| ArchitectureIntelligence | High | Medium | 2 |
| EnterpriseDocumentation | Medium | High | 3 |
| DeploymentValidation | High | Low | 4 |
| LintValidation | Medium | Low | 5 |
| SetupEPM | Low | Medium | 6 |
| BrainExport | Low | Low | 7 |
| BrainImport | Low | Low | 8 |

**Migration Order:** Prioritize by (User Impact × Frequency) / Complexity

---

## 🛠️ Template Integration

### Step 1: Copy Dashboard Template

**Base Template Location:** `src/generators/dashboard_template_generator.py`

```python
from src.generators.dashboard_template_generator import DashboardTemplateGenerator

# Initialize generator
generator = DashboardTemplateGenerator()

# Generate base template
template = generator.generate_base_template(
    operation="system-alignment",
    title="System Alignment Report"
)
```

### Step 2: Configure EPM for HTML Output

**Modify EPM to use template:**

```python
# Before (legacy)
class SystemAlignmentOrchestrator:
    def generate_report(self, results):
        report_path = "cortex-brain/documents/analysis/alignment-report.md"
        with open(report_path, 'w') as f:
            f.write(f"# Alignment Report\n\n")
            f.write(f"Score: {results['score']}\n")
        return report_path

# After (new format)
class SystemAlignmentOrchestrator:
    def generate_report(self, results):
        from src.generators.dashboard_template_generator import DashboardTemplateGenerator
        
        generator = DashboardTemplateGenerator()
        dashboard = generator.generate_dashboard(
            operation="system-alignment",
            title="System Alignment Report",
            data=results,
            layers=self._build_layers(results)
        )
        
        report_path = "cortex-brain/documents/analysis/alignment-dashboard.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(dashboard)
        
        return report_path
```

### Step 3: Define Layer Structure

**Create layer configuration:**

```python
def _build_layers(self, results):
    """Build 5-layer dashboard structure"""
    return [
        {
            "id": "layer-executive",
            "name": "Executive Summary",
            "order": 1,
            "content": self._build_executive_summary(results)
        },
        {
            "id": "layer-analysis",
            "name": "Detailed Analysis",
            "order": 2,
            "content": self._build_detailed_analysis(results)
        },
        {
            "id": "layer-issues",
            "name": "Issues & Recommendations",
            "order": 3,
            "content": self._build_issues(results)
        },
        {
            "id": "layer-technical",
            "name": "Technical Details",
            "order": 4,
            "content": self._build_technical_details(results)
        },
        {
            "id": "layer-export",
            "name": "Export & Actions",
            "order": 5,
            "content": self._build_export_options(results)
        }
    ]
```

---

## 📊 Data Transformation

### Step 1: Structure Data for Visualizations

**Transform results into D3.js-compatible format:**

```python
def _transform_for_d3(self, results):
    """Transform results for D3.js visualizations"""
    return {
        "health_gauge": {
            "value": results.get('overall_score', 0),
            "max": 100,
            "thresholds": [
                {"value": 70, "color": "#e74c3c", "label": "Critical"},
                {"value": 85, "color": "#f39c12", "label": "Warning"},
                {"value": 100, "color": "#27ae60", "label": "Healthy"}
            ]
        },
        "component_tree": {
            "name": "System Components",
            "children": [
                {
                    "name": "Tier 1: Working Memory",
                    "status": "healthy",
                    "score": results['tiers']['tier1']['score'],
                    "children": [...]
                },
                # ... more tiers
            ]
        },
        "priority_matrix": {
            "issues": [
                {
                    "id": "ISS-001",
                    "severity": "critical",
                    "impact": 9,
                    "effort": 3,
                    "title": "Missing Test Coverage"
                },
                # ... more issues
            ]
        },
        "execution_timeline": {
            "events": [
                {
                    "timestamp": "2025-11-28T14:30:00Z",
                    "action": "Start Alignment",
                    "duration": 0
                },
                {
                    "timestamp": "2025-11-28T14:30:05Z",
                    "action": "Validate Tier 1",
                    "duration": 5000
                },
                # ... more events
            ]
        }
    }
```

### Step 2: Build Executive Summary Content

```python
def _build_executive_summary(self, results):
    """Build Layer 1: Executive Summary"""
    d3_data = self._transform_for_d3(results)
    
    return {
        "title": results.get('operation_name', 'System Report'),
        "timestamp": datetime.now().isoformat(),
        "author": "Asif Hussain | GitHub: github.com/asifhussain60/CORTEX",
        "status": self._determine_status(results),
        "key_metrics": [
            {
                "label": "Overall Score",
                "value": f"{results['overall_score']:.1f}%",
                "trend": "up" if results.get('trend', 0) > 0 else "down"
            },
            {
                "label": "Components Analyzed",
                "value": results.get('component_count', 0)
            },
            {
                "label": "Issues Found",
                "value": len(results.get('issues', []))
            }
        ],
        "visualization": {
            "type": "gauge",
            "data": d3_data['health_gauge'],
            "target": "#health-gauge"
        },
        "quick_actions": [
            {
                "label": "Export PDF",
                "action": "exportPDF()",
                "icon": "📄"
            },
            {
                "label": "View Issues",
                "action": "switchTab('layer-issues')",
                "icon": "⚠️"
            }
        ]
    }
```

### Step 3: Build Detailed Analysis Content

```python
def _build_detailed_analysis(self, results):
    """Build Layer 2: Detailed Analysis"""
    d3_data = self._transform_for_d3(results)
    
    return {
        "components": results.get('components', []),
        "breakdown": {
            "by_tier": results.get('tier_breakdown', {}),
            "by_status": results.get('status_breakdown', {}),
            "by_category": results.get('category_breakdown', {})
        },
        "trends": results.get('historical_trends', []),
        "dependencies": results.get('dependency_map', {}),
        "performance": {
            "total_duration": results.get('duration', 0),
            "db_queries": results.get('db_query_count', 0),
            "files_analyzed": results.get('file_count', 0)
        },
        "visualization": {
            "type": "tree",
            "data": d3_data['component_tree'],
            "target": "#component-tree"
        }
    }
```

---

## 🎨 Visualization Implementation

### Step 1: Implement Health Gauge (Layer 1)

**D3.js Gauge Implementation:**

```javascript
function renderHealthGauge(data, targetSelector) {
    const width = 400;
    const height = 300;
    const radius = Math.min(width, height) / 2;
    
    const svg = d3.select(targetSelector)
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${width/2},${height/2})`);
    
    // Arc generator
    const arc = d3.arc()
        .innerRadius(radius * 0.6)
        .outerRadius(radius * 0.9)
        .startAngle(-Math.PI / 2);
    
    // Background arc
    svg.append("path")
        .datum({endAngle: Math.PI / 2})
        .style("fill", "#ecf0f1")
        .attr("d", arc);
    
    // Value arc
    const valueArc = svg.append("path")
        .datum({endAngle: -Math.PI / 2})
        .style("fill", getColor(data.value, data.thresholds))
        .attr("d", arc);
    
    // Animate
    valueArc.transition()
        .duration(1000)
        .attrTween("d", function(d) {
            const interpolate = d3.interpolate(d.endAngle, 
                -Math.PI / 2 + (data.value / data.max) * Math.PI);
            return function(t) {
                d.endAngle = interpolate(t);
                return arc(d);
            };
        });
    
    // Center text
    svg.append("text")
        .attr("text-anchor", "middle")
        .attr("dy", "0.35em")
        .style("font-size", "48px")
        .style("font-weight", "bold")
        .style("fill", getColor(data.value, data.thresholds))
        .text(data.value + "%");
    
    // Add ARIA labels
    svg.append("title")
        .text(`Health Score: ${data.value}% - ${getStatusLabel(data.value, data.thresholds)}`);
}

function getColor(value, thresholds) {
    for (const threshold of thresholds) {
        if (value <= threshold.value) {
            return threshold.color;
        }
    }
    return thresholds[thresholds.length - 1].color;
}
```

### Step 2: Implement Component Tree (Layer 2)

**D3.js Tree Implementation:**

```javascript
function renderComponentTree(data, targetSelector) {
    const width = 960;
    const height = 600;
    
    const svg = d3.select(targetSelector)
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", "translate(50,50)");
    
    // Create hierarchy
    const root = d3.hierarchy(data);
    const treeLayout = d3.tree().size([height - 100, width - 200]);
    treeLayout(root);
    
    // Links
    svg.selectAll(".link")
        .data(root.links())
        .enter()
        .append("path")
        .attr("class", "link")
        .attr("fill", "none")
        .attr("stroke", "#bdc3c7")
        .attr("stroke-width", 2)
        .attr("d", d3.linkHorizontal()
            .x(d => d.y)
            .y(d => d.x));
    
    // Nodes
    const node = svg.selectAll(".node")
        .data(root.descendants())
        .enter()
        .append("g")
        .attr("class", "node")
        .attr("transform", d => `translate(${d.y},${d.x})`);
    
    node.append("circle")
        .attr("r", 8)
        .attr("fill", d => getStatusColor(d.data.status))
        .on("click", (event, d) => showNodeDetails(d));
    
    node.append("text")
        .attr("dx", 12)
        .attr("dy", 4)
        .text(d => d.data.name)
        .style("font-size", "14px");
    
    // Add ARIA
    svg.append("title")
        .text("Component Tree - Click nodes for details");
}
```

### Step 3: Implement Priority Matrix (Layer 3)

**D3.js Matrix Implementation:**

```javascript
function renderPriorityMatrix(data, targetSelector) {
    const width = 600;
    const height = 600;
    const margin = {top: 50, right: 50, bottom: 50, left: 50};
    
    const svg = d3.select(targetSelector)
        .append("svg")
        .attr("width", width)
        .attr("height", height);
    
    // Scales
    const xScale = d3.scaleLinear()
        .domain([0, 10])
        .range([margin.left, width - margin.right]);
    
    const yScale = d3.scaleLinear()
        .domain([0, 10])
        .range([height - margin.bottom, margin.top]);
    
    // Axes
    svg.append("g")
        .attr("transform", `translate(0,${height - margin.bottom})`)
        .call(d3.axisBottom(xScale).ticks(5))
        .append("text")
        .attr("x", width / 2)
        .attr("y", 40)
        .attr("fill", "#2c3e50")
        .text("Effort →");
    
    svg.append("g")
        .attr("transform", `translate(${margin.left},0)`)
        .call(d3.axisLeft(yScale).ticks(5))
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("x", -height / 2)
        .attr("y", -35)
        .attr("fill", "#2c3e50")
        .text("← Impact");
    
    // Quadrant backgrounds
    const quadrants = [
        {x: 0, y: 5, label: "Quick Wins", color: "#27ae60"},
        {x: 5, y: 5, label: "Major Projects", color: "#f39c12"},
        {x: 0, y: 0, label: "Low Priority", color: "#bdc3c7"},
        {x: 5, y: 0, label: "Time Wasters", color: "#e74c3c"}
    ];
    
    quadrants.forEach(q => {
        svg.append("rect")
            .attr("x", xScale(q.x))
            .attr("y", yScale(q.y + 5))
            .attr("width", xScale(5) - xScale(0))
            .attr("height", yScale(0) - yScale(5))
            .attr("fill", q.color)
            .attr("opacity", 0.1);
        
        svg.append("text")
            .attr("x", xScale(q.x + 2.5))
            .attr("y", yScale(q.y + 2.5))
            .attr("text-anchor", "middle")
            .attr("fill", q.color)
            .attr("font-weight", "bold")
            .text(q.label);
    });
    
    // Plot issues
    svg.selectAll(".issue")
        .data(data.issues)
        .enter()
        .append("circle")
        .attr("class", "issue")
        .attr("cx", d => xScale(d.effort))
        .attr("cy", d => yScale(d.impact))
        .attr("r", 8)
        .attr("fill", d => getSeverityColor(d.severity))
        .on("click", (event, d) => showIssueDetails(d))
        .append("title")
        .text(d => `${d.title}\nImpact: ${d.impact}, Effort: ${d.effort}`);
}
```

### Step 4: Implement Execution Timeline (Layer 4)

**D3.js Timeline Implementation:**

```javascript
function renderExecutionTimeline(data, targetSelector) {
    const width = 960;
    const height = 200;
    const margin = {top: 20, right: 20, bottom: 30, left: 100};
    
    const svg = d3.select(targetSelector)
        .append("svg")
        .attr("width", width)
        .attr("height", height);
    
    // Parse timestamps
    const timeExtent = d3.extent(data.events, d => new Date(d.timestamp));
    
    const xScale = d3.scaleTime()
        .domain(timeExtent)
        .range([margin.left, width - margin.right]);
    
    const yScale = d3.scaleBand()
        .domain(data.events.map(d => d.action))
        .range([margin.top, height - margin.bottom])
        .padding(0.1);
    
    // Timeline axis
    svg.append("g")
        .attr("transform", `translate(0,${height - margin.bottom})`)
        .call(d3.axisBottom(xScale).ticks(5));
    
    // Events
    svg.selectAll(".event")
        .data(data.events)
        .enter()
        .append("rect")
        .attr("class", "event")
        .attr("x", d => xScale(new Date(d.timestamp)))
        .attr("y", d => yScale(d.action))
        .attr("width", d => d.duration ? 
              xScale(new Date(new Date(d.timestamp).getTime() + d.duration)) - 
              xScale(new Date(d.timestamp)) : 2)
        .attr("height", yScale.bandwidth())
        .attr("fill", "#3498db")
        .on("mouseover", (event, d) => showEventTooltip(event, d));
    
    // Labels
    svg.selectAll(".label")
        .data(data.events)
        .enter()
        .append("text")
        .attr("x", margin.left - 10)
        .attr("y", d => yScale(d.action) + yScale.bandwidth() / 2)
        .attr("text-anchor", "end")
        .attr("dy", "0.35em")
        .text(d => d.action);
}
```

---

## ✅ Testing & Validation

### Step 1: Automated Validation

**Run format validator:**

```python
from src.validators.documentation_format_validator import DocumentationFormatValidator

validator = DocumentationFormatValidator()
result = validator.validate("cortex-brain/documents/analysis/alignment-dashboard.html")

if result.is_valid:
    print("✅ Dashboard complies with format specification")
    print(f"   Layers: {result.layer_count}")
    print(f"   Visualizations: {result.viz_count}")
    print(f"   Performance: {result.load_time:.2f}s")
else:
    print("❌ Validation failed:")
    for error in result.errors:
        print(f"  - {error}")
```

### Step 2: Manual Testing Checklist

```markdown
## Manual Test Checklist

### Structure (5 tests)
- [ ] All 5 tabs present and labeled correctly
- [ ] Tab navigation switches content
- [ ] Transitions smooth (no flickering)
- [ ] All sections have headings
- [ ] Author attribution visible

### Visualizations (5 tests)
- [ ] Health gauge renders and animates
- [ ] Component tree interactive (click/hover)
- [ ] Priority matrix shows all issues
- [ ] Timeline displays execution steps
- [ ] Export preview thumbnails visible

### Interactivity (6 tests)
- [ ] Hover tooltips appear
- [ ] Click actions work
- [ ] Zoom/pan functional (where applicable)
- [ ] Filter buttons work
- [ ] Copy buttons copy templates
- [ ] Action buttons execute functions

### Export (3 tests)
- [ ] PDF export generates all layers
- [ ] PNG export high resolution
- [ ] PPTX export preserves layout

### Performance (4 tests)
- [ ] Page load < 2 seconds
- [ ] D3.js render < 500ms per chart
- [ ] Smooth transitions (60 FPS)
- [ ] No console errors

### Security (4 tests)
- [ ] CSP header present (check DevTools)
- [ ] No inline event handlers (view source)
- [ ] Data sanitized (test with <script> tags)
- [ ] No XSS vulnerabilities

### Accessibility (5 tests)
- [ ] ARIA labels on visualizations
- [ ] Keyboard navigation works (Tab key)
- [ ] Screen reader announces content
- [ ] Color contrast meets WCAG AA
- [ ] Alt text on all images
```

### Step 3: Performance Testing

**Chrome DevTools Performance:**

1. Open dashboard in Chrome
2. Open DevTools (F12)
3. Go to Performance tab
4. Click Record
5. Refresh page
6. Stop recording after page loads

**Validate:**
- First Contentful Paint (FCP) < 1.5s
- Largest Contentful Paint (LCP) < 2.5s
- Total Blocking Time (TBT) < 200ms
- Cumulative Layout Shift (CLS) < 0.1

---

## 🚀 Deployment

### Step 1: Update EPM Code

**Commit changes:**

```bash
cd /Users/asifhussain/PROJECTS/CORTEX
git add src/orchestrators/[epm_name]_orchestrator.py
git commit -m "feat: Migrate [EPM] to documentation format v1.0

- Implement 5-layer dashboard structure
- Add D3.js visualizations (gauge, tree, matrix, timeline)
- Export functionality (PDF, PNG, PPTX)
- Security compliance (CSP, XSS prevention)
- WCAG AA accessibility

Closes #[issue-number]"
```

### Step 2: Update Documentation

**Add migration note:**

```markdown
## Migration to Format v1.0

**Date:** 2025-11-28  
**Status:** ✅ Complete  
**Validation:** Passed all 30 validation checks

**Changes:**
- Output format: markdown → interactive HTML dashboard
- Visualizations: 0 → 5 D3.js charts
- Export formats: 0 → 3 (PDF, PNG, PPTX)
- Performance: Load time 3.2s → 1.8s
```

### Step 3: Deployment Validation

**Run deployment gate:**

```python
from src.validators.deployment_gate import DeploymentGate

gate = DeploymentGate()
result = gate.validate_epm_compliance("SystemAlignmentOrchestrator")

if result.passes:
    print("✅ EPM ready for deployment")
else:
    print("❌ Deployment blocked:")
    for blocker in result.blockers:
        print(f"  - {blocker}")
```

### Step 4: Rollout Strategy

**Phased rollout:**

1. **Week 1:** Deploy to development environment
   - Test with dev team
   - Gather feedback
   - Fix critical issues

2. **Week 2:** Deploy to staging environment
   - Test with select users
   - Performance monitoring
   - Final adjustments

3. **Week 3:** Deploy to production
   - Gradual rollout (10% → 50% → 100%)
   - Monitor error rates
   - Rollback plan ready

---

## 🔄 Rollback Plan

### Emergency Rollback

**If critical issues found:**

```python
# Revert EPM to legacy format
from src.orchestrators.legacy_backup import restore_legacy_epm

restore_legacy_epm(
    epm_name="SystemAlignmentOrchestrator",
    backup_timestamp="2025-11-27T10:00:00Z"
)
```

**Rollback checklist:**
- [ ] Restore previous EPM code from git
- [ ] Restore legacy template files
- [ ] Update documentation format validator (skip new checks)
- [ ] Notify users of temporary format change
- [ ] Schedule fix and re-migration

---

## 📚 Resources

**Template Generator:** `src/generators/dashboard_template_generator.py`  
**Format Validator:** `src/validators/documentation_format_validator.py`  
**Example Dashboard:** `cortex-brain/documents/examples/reference-dashboard-v1.0.html`  
**Format Specification:** `cortex-brain/documents/standards/DOCUMENTATION-FORMAT-SPEC-v1.0.md`  
**Validation Schema:** `cortex-brain/documents/standards/format-validation-schema.json`

---

## 💬 Support

**Questions:** Ask CORTEX Planning Orchestrator  
**Issues:** Use `cortex feedback` command  
**Migration Help:** Review this guide with CORTEX

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)  
**Repository:** https://github.com/asifhussain60/CORTEX
