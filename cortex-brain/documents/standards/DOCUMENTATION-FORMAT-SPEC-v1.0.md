# CORTEX Documentation Format Specification v1.0

**Version:** 1.0.0  
**Status:** ✅ APPROVED  
**Effective Date:** 2025-11-28  
**Author:** Asif Hussain  
**Scope:** All Admin Entry Point Modules (EPMs)

---

## 🎯 Purpose

This specification defines the **mandatory format** for all CORTEX admin documentation outputs. All Entry Point Modules (EPMs) generating documentation MUST comply with this standard to ensure:

- **Consistent user experience** across all admin operations
- **Interactive exploration** via D3.js dashboards
- **Multi-layer context** with tabbed navigation
- **Export capabilities** for sharing and presentation
- **Deployment validation** at gate checkpoints

**Enforcement:** Deployment pipelines MUST validate compliance before allowing releases.

---

## 📐 Core Architecture

### Format Type: Interactive HTML Dashboard

All admin documentation outputs MUST be generated as **self-contained HTML files** with:

1. **Embedded D3.js library** (v7.8.5 or higher)
2. **Multi-layer tab navigation** (5 tabs minimum)
3. **Interactive visualizations** (SVG-based)
4. **Narrative intelligence** (contextual explanations)
5. **Smart annotations** (JSON-driven tooltips)
6. **Export functionality** (PDF, PNG, PPTX)

### File Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[Operation Name] - CORTEX Admin Dashboard</title>
    
    <!-- REQUIRED: D3.js Library -->
    <script src="https://d3js.org/d3.v7.min.js"></script>
    
    <!-- REQUIRED: Export Libraries -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    
    <!-- REQUIRED: Security Headers -->
    <meta http-equiv="Content-Security-Policy" content="default-src 'self' https://d3js.org https://cdnjs.cloudflare.com; script-src 'self' 'unsafe-inline' https://d3js.org https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline';">
    
    <style>
        /* Embedded CSS - NO external stylesheets */
    </style>
</head>
<body>
    <!-- Tab Navigation -->
    <!-- Content Layers -->
    <!-- Interactive Visualizations -->
    <!-- Export Controls -->
    
    <script>
        /* NO inline event handlers */
        /* All JavaScript in <script> blocks */
    </script>
</body>
</html>
```

---

## 🗂️ Tab Structure (5-Layer Minimum)

### Layer 1: Executive Summary (MANDATORY)

**Purpose:** High-level overview for quick decision-making

**Required Elements:**
- **Operation Title** (H1 heading)
- **Timestamp** (ISO 8601 format)
- **Author Attribution** ("Asif Hussain | GitHub: github.com/asifhussain60/CORTEX")
- **Status Badge** (✅ Success / ⚠️ Warning / ❌ Error)
- **Key Metrics** (3-5 primary indicators)
- **Health Score** (0-100% visualization)
- **Quick Actions** (1-3 recommended next steps)

**Visualization:** Single D3.js gauge/radial chart for health score

**Example:**
```html
<div id="layer-executive" class="tab-content active">
    <h1>System Alignment Report</h1>
    <div class="metadata">
        <span class="timestamp">2025-11-28T14:32:10Z</span>
        <span class="author">Asif Hussain | GitHub: github.com/asifhussain60/CORTEX</span>
    </div>
    <div class="status-badge success">✅ Alignment Successful</div>
    
    <div class="key-metrics">
        <div class="metric">
            <span class="label">Overall Score</span>
            <span class="value">94.2%</span>
        </div>
        <!-- 2-4 more metrics -->
    </div>
    
    <svg id="health-gauge"></svg>
    
    <div class="quick-actions">
        <button onclick="exportReport('pdf')">Export PDF</button>
        <button onclick="viewDetails()">View Details</button>
    </div>
</div>
```

### Layer 2: Detailed Analysis (MANDATORY)

**Purpose:** In-depth breakdown of operation results

**Required Elements:**
- **Component Breakdown** (table or tree visualization)
- **Issue Categorization** (grouped by severity)
- **Trend Analysis** (historical comparison if available)
- **Dependency Mapping** (relationship visualization)
- **Performance Metrics** (timing, resource usage)

**Visualization:** D3.js hierarchical tree OR force-directed graph

**Example Structure:**
```javascript
// D3.js Tree Visualization
const treeData = {
    name: "System Components",
    children: [
        {
            name: "Tier 1: Working Memory",
            status: "healthy",
            score: 98.5,
            children: [...]
        },
        {
            name: "Tier 2: Knowledge Graph",
            status: "warning",
            score: 87.3,
            issues: [...]
        }
    ]
};
```

### Layer 3: Issues & Recommendations (MANDATORY)

**Purpose:** Actionable insights and remediation steps

**Required Elements:**
- **Issue List** (filterable by severity/category)
- **Root Cause Analysis** (for each critical issue)
- **Remediation Templates** (copy-paste ready)
- **Priority Matrix** (impact vs effort visualization)
- **Dependencies** (what must be fixed first)

**Visualization:** D3.js matrix/heatmap for priority scoring

**Example:**
```html
<div id="layer-issues" class="tab-content">
    <div class="filter-controls">
        <button data-severity="critical">Critical (3)</button>
        <button data-severity="warning">Warnings (12)</button>
        <button data-severity="info">Info (8)</button>
    </div>
    
    <div class="issue-list">
        <div class="issue critical" data-id="ISS-001">
            <h3>Missing Test Coverage for Authentication Module</h3>
            <div class="root-cause">
                TDD enforcement detected 3 files without corresponding tests.
            </div>
            <div class="remediation">
                <button onclick="copyTemplate('ISS-001')">Copy Fix Template</button>
                <pre class="template">
# Test file: tests/test_authentication.py
# Add these test cases:
                </pre>
            </div>
        </div>
    </div>
    
    <svg id="priority-matrix"></svg>
</div>
```

### Layer 4: Technical Details (MANDATORY)

**Purpose:** Raw data and diagnostic information

**Required Elements:**
- **Configuration Snapshot** (relevant settings)
- **File Manifest** (files analyzed/modified)
- **Execution Trace** (operation steps with timing)
- **Database Queries** (if applicable)
- **API Calls** (if applicable)

**Visualization:** D3.js timeline for execution trace

**Example:**
```html
<div id="layer-technical" class="tab-content">
    <div class="config-snapshot">
        <h3>Active Configuration</h3>
        <pre><code>{
    "governance": {
        "tdd_enforcement": true,
        "brain_protection": true
    }
}</code></pre>
    </div>
    
    <div class="file-manifest">
        <h3>Files Analyzed (47)</h3>
        <ul>
            <li>src/tier1/working_memory.py (modified)</li>
            <li>src/tier2/knowledge_graph.py (analyzed)</li>
        </ul>
    </div>
    
    <svg id="execution-timeline"></svg>
</div>
```

### Layer 5: Export & Actions (MANDATORY)

**Purpose:** Report sharing and workflow integration

**Required Elements:**
- **Export Options** (PDF, PNG, PPTX with preview)
- **Integration Links** (ADO work items, GitHub issues)
- **Notification Settings** (email, Slack, Teams)
- **Scheduled Reports** (recurring generation)
- **API Access** (programmatic retrieval)

**Visualization:** D3.js preview thumbnail of export output

**Example:**
```html
<div id="layer-export" class="tab-content">
    <div class="export-options">
        <button onclick="exportPDF()">
            <svg id="pdf-preview"></svg>
            Export as PDF
        </button>
        <button onclick="exportPNG()">
            <svg id="png-preview"></svg>
            Export as PNG
        </button>
        <button onclick="exportPPTX()">
            <svg id="pptx-preview"></svg>
            Export as PowerPoint
        </button>
    </div>
    
    <div class="integration">
        <h3>Create Work Items</h3>
        <button onclick="createADOItems()">Create ADO Stories (3)</button>
        <button onclick="createGitHubIssues()">Create GitHub Issues (3)</button>
    </div>
</div>
```

---

## 🎨 Styling Requirements

### Color Palette (MANDATORY)

```css
:root {
    /* Primary Colors */
    --cortex-primary: #2c3e50;      /* Dark blue-grey */
    --cortex-secondary: #3498db;    /* Bright blue */
    --cortex-accent: #e74c3c;       /* Red for alerts */
    
    /* Status Colors */
    --status-success: #27ae60;      /* Green */
    --status-warning: #f39c12;      /* Orange */
    --status-error: #e74c3c;        /* Red */
    --status-info: #3498db;         /* Blue */
    
    /* Neutral Colors */
    --bg-primary: #ffffff;
    --bg-secondary: #ecf0f1;
    --text-primary: #2c3e50;
    --text-secondary: #7f8c8d;
    --border-color: #bdc3c7;
    
    /* Visualization Colors */
    --viz-color-1: #3498db;
    --viz-color-2: #2ecc71;
    --viz-color-3: #f39c12;
    --viz-color-4: #e74c3c;
    --viz-color-5: #9b59b6;
}
```

### Typography (MANDATORY)

```css
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, 
                 "Helvetica Neue", Arial, sans-serif;
    font-size: 16px;
    line-height: 1.6;
    color: var(--text-primary);
}

h1 { font-size: 2.5rem; font-weight: 700; }
h2 { font-size: 2rem; font-weight: 600; }
h3 { font-size: 1.5rem; font-weight: 600; }

code {
    font-family: "SF Mono", Monaco, "Cascadia Code", "Courier New", monospace;
    background: var(--bg-secondary);
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
}

pre code {
    display: block;
    padding: 1rem;
    overflow-x: auto;
}
```

### Layout (MANDATORY)

```css
/* Tab Navigation */
.tab-navigation {
    display: flex;
    border-bottom: 2px solid var(--border-color);
    margin-bottom: 2rem;
}

.tab-button {
    padding: 1rem 2rem;
    border: none;
    background: transparent;
    cursor: pointer;
    border-bottom: 3px solid transparent;
    transition: all 0.3s ease;
}

.tab-button.active {
    border-bottom-color: var(--cortex-secondary);
    color: var(--cortex-secondary);
    font-weight: 600;
}

/* Content Containers */
.tab-content {
    display: none;
    padding: 2rem;
    animation: fadeIn 0.3s ease;
}

.tab-content.active {
    display: block;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
```

---

## 📊 D3.js Visualization Requirements

### Mandatory Visualizations by Layer

| Layer | Visualization Type | Data Binding | Interactivity |
|-------|-------------------|--------------|---------------|
| Executive Summary | Gauge/Radial Chart | Health score (0-100%) | Hover tooltips |
| Detailed Analysis | Tree/Force Graph | Component hierarchy | Click to expand, zoom/pan |
| Issues & Recommendations | Matrix/Heatmap | Priority scoring | Filter by severity, click for details |
| Technical Details | Timeline | Execution trace | Hover for timing, click for logs |
| Export & Actions | Thumbnail Preview | Export output | Click to generate |

### D3.js Code Standards

**Data Sanitization (REQUIRED):**
```javascript
// ALWAYS sanitize user-generated content
function sanitizeText(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Example usage in D3
svg.selectAll("text")
    .data(data)
    .enter()
    .append("text")
    .text(d => sanitizeText(d.name)); // Prevents XSS
```

**SVG Structure:**
```javascript
// Standard SVG setup
const margin = {top: 20, right: 20, bottom: 30, left: 50};
const width = 960 - margin.left - margin.right;
const height = 500 - margin.top - margin.bottom;

const svg = d3.select("#chart-container")
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);
```

**Transitions (REQUIRED for all state changes):**
```javascript
// Smooth transitions (300ms standard)
elements.transition()
    .duration(300)
    .ease(d3.easeQuadInOut)
    .attr("opacity", 1);
```

**Accessibility (REQUIRED):**
```javascript
// Add ARIA labels for screen readers
svg.append("title")
    .text("System Health Gauge - 94% Healthy");

svg.append("desc")
    .text("A radial gauge showing system health at 94%, indicating healthy status");
```

---

## 🔒 Security Requirements

### Content Security Policy (CSP)

**MANDATORY CSP Header:**
```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self' https://d3js.org https://cdnjs.cloudflare.com; 
               script-src 'self' 'unsafe-inline' https://d3js.org https://cdnjs.cloudflare.com; 
               style-src 'self' 'unsafe-inline'; 
               img-src 'self' data:; 
               connect-src 'self';">
```

### XSS Prevention

**Input Sanitization (MANDATORY):**
```javascript
// Use DOMPurify or built-in sanitization
function sanitizeHTML(html) {
    const temp = document.createElement('div');
    temp.textContent = html;
    return temp.innerHTML;
}

// For JSON data
function sanitizeJSON(obj) {
    return JSON.parse(JSON.stringify(obj, (key, value) => {
        if (typeof value === 'string') {
            return sanitizeHTML(value);
        }
        return value;
    }));
}
```

**NO Inline Event Handlers:**
```html
<!-- ❌ FORBIDDEN -->
<button onclick="doSomething()">Click</button>

<!-- ✅ REQUIRED -->
<button id="action-btn">Click</button>
<script>
    document.getElementById('action-btn').addEventListener('click', doSomething);
</script>
```

### Data Validation

**Schema Validation (REQUIRED before rendering):**
```javascript
// Validate dashboard data structure
function validateDashboardData(data) {
    const required = ['title', 'timestamp', 'status', 'metrics', 'layers'];
    for (const field of required) {
        if (!(field in data)) {
            throw new Error(`Missing required field: ${field}`);
        }
    }
    
    if (data.layers.length < 5) {
        throw new Error('Dashboard must have at least 5 layers');
    }
    
    return true;
}
```

---

## 📤 Export Functionality

### PDF Export (REQUIRED)

**Implementation:**
```javascript
async function exportPDF() {
    const { jsPDF } = window.jspdf;
    const pdf = new jsPDF('p', 'mm', 'a4');
    
    // Capture each layer as image
    const layers = document.querySelectorAll('.tab-content');
    for (let i = 0; i < layers.length; i++) {
        if (i > 0) pdf.addPage();
        
        const canvas = await html2canvas(layers[i]);
        const imgData = canvas.toDataURL('image/png');
        
        const imgWidth = 190;
        const imgHeight = (canvas.height * imgWidth) / canvas.width;
        pdf.addImage(imgData, 'PNG', 10, 10, imgWidth, imgHeight);
    }
    
    pdf.save(`cortex-report-${Date.now()}.pdf`);
}
```

### PNG Export (REQUIRED)

**Implementation:**
```javascript
async function exportPNG(layerId) {
    const layer = document.getElementById(layerId);
    const canvas = await html2canvas(layer, {
        backgroundColor: '#ffffff',
        scale: 2 // High resolution
    });
    
    const link = document.createElement('a');
    link.download = `cortex-${layerId}-${Date.now()}.png`;
    link.href = canvas.toDataURL('image/png');
    link.click();
}
```

### PowerPoint Export (REQUIRED)

**Implementation:**
```javascript
async function exportPPTX() {
    // Convert layers to images
    const slides = [];
    const layers = document.querySelectorAll('.tab-content');
    
    for (const layer of layers) {
        const canvas = await html2canvas(layer);
        slides.push({
            title: layer.querySelector('h1, h2, h3').textContent,
            image: canvas.toDataURL('image/png')
        });
    }
    
    // Generate PPTX (requires PptxGenJS library)
    const pptx = new PptxGenJS();
    slides.forEach(slide => {
        const pptxSlide = pptx.addSlide();
        pptxSlide.addText(slide.title, {x: 0.5, y: 0.5, fontSize: 24});
        pptxSlide.addImage({data: slide.image, x: 0.5, y: 1.5, w: 9, h: 5});
    });
    
    pptx.writeFile({fileName: `cortex-report-${Date.now()}.pptx`});
}
```

---

## 📝 Smart Annotations (JSON Schema)

### Annotation Structure

**Format:**
```json
{
    "annotations": [
        {
            "id": "ann-001",
            "target": "#health-gauge",
            "type": "tooltip",
            "position": "top",
            "trigger": "hover",
            "content": {
                "title": "Health Score Calculation",
                "body": "Weighted average of 7 metrics: Tier 1 (20%), Tier 2 (20%), Tier 3 (15%), Agents (15%), Orchestrators (15%), Tests (10%), Documentation (5%)",
                "links": [
                    {
                        "text": "Learn More",
                        "url": "#layer-technical"
                    }
                ]
            }
        },
        {
            "id": "ann-002",
            "target": ".issue.critical",
            "type": "popover",
            "position": "right",
            "trigger": "click",
            "content": {
                "title": "Critical Issue Details",
                "body": "This issue must be resolved before deployment.",
                "actions": [
                    {
                        "label": "Copy Fix Template",
                        "action": "copyTemplate",
                        "data": "ISS-001"
                    },
                    {
                        "label": "Create ADO Task",
                        "action": "createADOTask",
                        "data": {"issueId": "ISS-001"}
                    }
                ]
            }
        }
    ]
}
```

### Implementation

**JavaScript Handler:**
```javascript
function initializeAnnotations(annotations) {
    annotations.forEach(ann => {
        const target = document.querySelector(ann.target);
        if (!target) return;
        
        const tooltip = createTooltip(ann);
        
        if (ann.trigger === 'hover') {
            target.addEventListener('mouseenter', () => showTooltip(tooltip, target, ann.position));
            target.addEventListener('mouseleave', () => hideTooltip(tooltip));
        } else if (ann.trigger === 'click') {
            target.addEventListener('click', () => togglePopover(tooltip, target, ann.position));
        }
    });
}

function createTooltip(annotation) {
    const div = document.createElement('div');
    div.className = `annotation ${annotation.type}`;
    div.innerHTML = `
        <h4>${sanitizeHTML(annotation.content.title)}</h4>
        <p>${sanitizeHTML(annotation.content.body)}</p>
        ${annotation.content.links ? renderLinks(annotation.content.links) : ''}
        ${annotation.content.actions ? renderActions(annotation.content.actions) : ''}
    `;
    return div;
}
```

---

## ✅ Validation Checklist

**Pre-Deployment Validation (MANDATORY):**

### Structure Validation
- [ ] HTML5 doctype present
- [ ] All 5 layers implemented
- [ ] Tab navigation functional
- [ ] D3.js library loaded (v7.8.5+)
- [ ] Export libraries present

### Content Validation
- [ ] Executive summary complete
- [ ] Detailed analysis has visualizations
- [ ] Issues list populated
- [ ] Technical details accessible
- [ ] Export options functional

### Security Validation
- [ ] CSP header present
- [ ] No inline event handlers
- [ ] Input sanitization implemented
- [ ] XSS prevention verified
- [ ] Data validation present

### Performance Validation
- [ ] Page load < 2 seconds
- [ ] D3.js render < 500ms per chart
- [ ] Transitions smooth (60 FPS)
- [ ] Export functions < 5 seconds
- [ ] File size < 2 MB

### Accessibility Validation
- [ ] ARIA labels on all visualizations
- [ ] Keyboard navigation works
- [ ] Screen reader compatible
- [ ] Color contrast meets WCAG AA
- [ ] Alt text on all images

### Export Validation
- [ ] PDF export generates all layers
- [ ] PNG export high resolution (2x)
- [ ] PPTX export preserves formatting
- [ ] File names include timestamp
- [ ] Export errors handled gracefully

---

## 🔧 Validation Tools

### Automated Validation Script

**Location:** `src/validators/documentation_format_validator.py`

**Usage:**
```python
from src.validators.documentation_format_validator import DocumentationFormatValidator

validator = DocumentationFormatValidator()
result = validator.validate("path/to/dashboard.html")

if result.is_valid:
    print("✅ Dashboard complies with format specification")
else:
    print("❌ Validation failed:")
    for error in result.errors:
        print(f"  - {error}")
```

### Manual Validation Process

1. **Visual Inspection:** Open dashboard in browser, verify all 5 tabs load
2. **Interaction Testing:** Click all buttons, hover tooltips, test exports
3. **Performance Testing:** Chrome DevTools > Performance tab (record page load)
4. **Security Testing:** Browser console > check for CSP violations
5. **Accessibility Testing:** Screen reader test (VoiceOver/NVDA)

---

## 📚 Reference Implementation

**Example Dashboard:** `cortex-brain/documents/examples/reference-dashboard-v1.0.html`

**Template Generator:** `src/generators/dashboard_template_generator.py`

**Migration Tool:** `src/tools/migrate_epms_to_v1.py`

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-28 | Initial specification |

---

## 📞 Support & Feedback

**Questions:** Review this specification with CORTEX Planning Orchestrator  
**Issues:** Report via `cortex feedback` command  
**Updates:** Track in `cortex-brain/documents/standards/`

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)  
**Repository:** https://github.com/asifhussain60/CORTEX
