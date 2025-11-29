# CORTEX Interactive Dashboard Documentation Format Specification

**Version:** 1.0.0  
**Status:** Production Ready  
**Created:** 2025-11-28  
**Author:** Asif Hussain

---

## 📋 Overview

This specification defines the mandatory format for all CORTEX admin operation documentation outputs. All admin Entry Point Modules (EPMs) MUST generate interactive D3.js dashboards conforming to this specification.

**Applies To:**
- Enterprise Documentation Orchestrator
- System Alignment Orchestrator
- Diagram Regeneration Module
- Design Sync Orchestrator
- Analytics Dashboard
- Response Templates Module

**Enforcement:** Deployment pipeline validates all outputs against this specification. Non-compliant outputs block deployment.

---

## 🏗️ HTML Structure Requirements

### Root Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' https://d3js.org https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline';">
    <title>CORTEX Dashboard - [Operation Name]</title>
    
    <!-- Required Libraries -->
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    
    <!-- Dashboard Styles -->
    <style>
        /* Base styles required */
    </style>
</head>
<body>
    <!-- Tab navigation -->
    <nav class="dashboard-tabs">
        <button class="tab-button active" data-tab="overview">Overview</button>
        <button class="tab-button" data-tab="visualizations">Visualizations</button>
        <button class="tab-button" data-tab="diagrams">Diagrams</button>
        <button class="tab-button" data-tab="data">Data</button>
        <button class="tab-button" data-tab="recommendations">Recommendations</button>
    </nav>
    
    <!-- Tab content -->
    <div class="tab-content active" id="overview-tab">
        <!-- Tab 1 content -->
    </div>
    <div class="tab-content" id="visualizations-tab">
        <!-- Tab 2 content -->
    </div>
    <div class="tab-content" id="diagrams-tab">
        <!-- Tab 3 content -->
    </div>
    <div class="tab-content" id="data-tab">
        <!-- Tab 4 content -->
    </div>
    <div class="tab-content" id="recommendations-tab">
        <!-- Tab 5 content -->
    </div>
    
    <!-- Export controls -->
    <div class="export-controls">
        <button onclick="exportToPDF()">Export PDF</button>
        <button onclick="exportToPNG()">Export PNG</button>
        <button onclick="exportToPPTX()">Export PPTX</button>
    </div>
    
    <script>
        // Dashboard logic
    </script>
</body>
</html>
```

---

## 📑 Tab Structure (MANDATORY 5 Tabs)

### Tab 1: Overview (Narrative Intelligence)

**Purpose:** Executive summary with key metrics and natural language insights

**Required Sections:**
1. **Operation Summary** - 3-sentence executive summary
2. **Key Metrics** - Top 5 metrics with visual indicators
3. **Status Indicator** - Overall health (Healthy/Warning/Critical)
4. **Timestamp** - Generation time and version
5. **Quick Actions** - Links to detailed tabs

**Narrative Intelligence Requirements:**
- Natural language descriptions of trends
- Contextual explanations of metrics
- Actionable insights in plain English
- Smart annotations explaining anomalies

**Example Structure:**
```html
<div class="tab-content active" id="overview-tab">
    <section class="executive-summary">
        <h2>Executive Summary</h2>
        <p class="narrative"><!-- Auto-generated narrative --></p>
    </section>
    
    <section class="key-metrics">
        <div class="metric-card">
            <div class="metric-value">85%</div>
            <div class="metric-label">System Health</div>
            <div class="metric-trend">↗️ +5% from last week</div>
        </div>
        <!-- 4 more metric cards -->
    </section>
    
    <section class="status-indicator">
        <div class="status-badge healthy">✅ Healthy</div>
        <p class="status-explanation">All systems operational</p>
    </section>
    
    <section class="metadata">
        <p>Generated: <span id="timestamp"></span></p>
        <p>Version: CORTEX 3.4.0</p>
    </section>
    
    <section class="quick-actions">
        <button onclick="switchTab('visualizations')">View Visualizations</button>
        <button onclick="switchTab('recommendations')">See Recommendations</button>
    </section>
</div>
```

---

### Tab 2: Visualizations (D3.js + Chart.js)

**Purpose:** Interactive data visualizations with drill-down capabilities

**Required Visualizations:**
1. **Force-Directed Graph** (D3.js) - Component relationships, dependency graphs
2. **Time Series Chart** (Chart.js) - Trend analysis, historical data
3. **Bar Chart** (D3.js or Chart.js) - Comparative metrics
4. **Heatmap** (D3.js) - Intensity visualization (optional)

**D3.js Requirements (v7+):**
- Interactive zoom and pan
- Hover tooltips with detailed information
- Click handlers for drill-down
- Smooth transitions (duration: 750ms)
- Responsive sizing (adapt to viewport)

**Chart.js Requirements (v3+):**
- Responsive: true
- Interactive legend (toggle datasets)
- Tooltip callbacks for custom formatting
- Animation: { duration: 1000 }

**Example Structure:**
```html
<div class="tab-content" id="visualizations-tab">
    <section class="viz-section">
        <h3>Component Dependency Graph</h3>
        <div id="force-graph" class="d3-container"></div>
    </section>
    
    <section class="viz-section">
        <h3>Health Trend (Last 30 Days)</h3>
        <canvas id="health-trend-chart"></canvas>
    </section>
    
    <section class="viz-section">
        <h3>Feature Status Distribution</h3>
        <div id="status-bar-chart" class="d3-container"></div>
    </section>
</div>

<script>
    // Force-directed graph
    const width = 800, height = 600;
    const svg = d3.select("#force-graph")
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .call(d3.zoom().on("zoom", (event) => {
            g.attr("transform", event.transform);
        }));
    
    const g = svg.append("g");
    
    const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).id(d => d.id))
        .force("charge", d3.forceManyBody().strength(-300))
        .force("center", d3.forceCenter(width / 2, height / 2));
    
    // Chart.js time series
    const ctx = document.getElementById('health-trend-chart').getContext('2d');
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'System Health',
                data: healthScores,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'top' },
                tooltip: {
                    callbacks: {
                        label: (context) => `Health: ${context.parsed.y}%`
                    }
                }
            }
        }
    });
</script>
```

---

### Tab 3: Diagrams (Mermaid Embedding)

**Purpose:** Architecture diagrams, flowcharts, sequence diagrams with interactive controls

**Required Features:**
1. **Mermaid Rendering** - Render Mermaid diagrams inline
2. **Zoom Controls** - +/- buttons for zooming
3. **Pan Support** - Drag to pan large diagrams
4. **Fullscreen Mode** - Expand diagram to fullscreen
5. **Export Diagram** - Download diagram as PNG/SVG

**Mermaid Diagram Types:**
- **Flowchart** - Process flows, decision trees
- **Sequence Diagram** - Component interactions
- **Class Diagram** - Object relationships
- **State Diagram** - State transitions
- **ER Diagram** - Data relationships

**Example Structure:**
```html
<div class="tab-content" id="diagrams-tab">
    <section class="diagram-controls">
        <button onclick="zoomIn()">➕ Zoom In</button>
        <button onclick="zoomOut()">➖ Zoom Out</button>
        <button onclick="resetZoom()">🔄 Reset</button>
        <button onclick="fullscreen()">⛶ Fullscreen</button>
        <button onclick="exportDiagram()">💾 Export PNG</button>
    </section>
    
    <section class="diagram-container">
        <h3>System Architecture</h3>
        <div class="mermaid-wrapper" id="diagram-1">
            <pre class="mermaid">
graph TD
    A[User Request] --> B{Intent Router}
    B --> C[Planning Agent]
    B --> D[TDD Agent]
    B --> E[Admin Agent]
    C --> F[Response Template]
    D --> F
    E --> F
    F --> G[User Response]
            </pre>
        </div>
    </section>
    
    <section class="diagram-container">
        <h3>Data Flow</h3>
        <div class="mermaid-wrapper" id="diagram-2">
            <pre class="mermaid">
sequenceDiagram
    participant U as User
    participant I as Intent Router
    participant A as Agent
    participant T as Template
    U->>I: Request
    I->>A: Route to agent
    A->>T: Select template
    T->>U: Formatted response
            </pre>
        </div>
    </section>
</div>

<script>
    // Initialize Mermaid
    mermaid.initialize({
        startOnLoad: true,
        theme: 'default',
        securityLevel: 'loose',
        flowchart: {
            useMaxWidth: true,
            htmlLabels: true
        }
    });
    
    // Zoom controls
    let zoomLevel = 1.0;
    function zoomIn() {
        zoomLevel += 0.1;
        document.querySelectorAll('.mermaid-wrapper').forEach(el => {
            el.style.transform = `scale(${zoomLevel})`;
        });
    }
    
    function zoomOut() {
        zoomLevel = Math.max(0.5, zoomLevel - 0.1);
        document.querySelectorAll('.mermaid-wrapper').forEach(el => {
            el.style.transform = `scale(${zoomLevel})`;
        });
    }
</script>
```

---

### Tab 4: Data Tables (Sortable & Filterable)

**Purpose:** Raw data access with sorting, filtering, and CSV export

**Required Features:**
1. **Sortable Columns** - Click headers to sort ascending/descending
2. **Filter Controls** - Search box and column-specific filters
3. **Pagination** - Show 25/50/100 rows per page
4. **CSV Export** - Download full dataset
5. **Column Visibility** - Show/hide columns

**Example Structure:**
```html
<div class="tab-content" id="data-tab">
    <section class="table-controls">
        <input type="text" id="table-search" placeholder="Search...">
        <select id="rows-per-page">
            <option value="25">25 rows</option>
            <option value="50">50 rows</option>
            <option value="100">100 rows</option>
        </select>
        <button onclick="exportTableToCSV()">💾 Export CSV</button>
    </section>
    
    <table class="data-table">
        <thead>
            <tr>
                <th data-sort="name">Feature Name <span class="sort-icon">⬍</span></th>
                <th data-sort="type">Type <span class="sort-icon">⬍</span></th>
                <th data-sort="status">Status <span class="sort-icon">⬍</span></th>
                <th data-sort="health">Health <span class="sort-icon">⬍</span></th>
                <th data-sort="lastUpdated">Last Updated <span class="sort-icon">⬍</span></th>
            </tr>
        </thead>
        <tbody id="data-table-body">
            <!-- Rows dynamically inserted -->
        </tbody>
    </table>
    
    <div class="pagination">
        <button onclick="prevPage()">← Previous</button>
        <span id="page-info">Page 1 of 10</span>
        <button onclick="nextPage()">Next →</button>
    </div>
</div>

<script>
    let tableData = []; // Loaded from JSON
    let currentPage = 1;
    let rowsPerPage = 25;
    let sortColumn = 'name';
    let sortDirection = 'asc';
    
    function renderTable() {
        const start = (currentPage - 1) * rowsPerPage;
        const end = start + rowsPerPage;
        const sortedData = sortData(tableData, sortColumn, sortDirection);
        const pageData = sortedData.slice(start, end);
        
        const tbody = document.getElementById('data-table-body');
        tbody.innerHTML = pageData.map(row => `
            <tr>
                <td>${row.name}</td>
                <td>${row.type}</td>
                <td><span class="badge ${row.status}">${row.status}</span></td>
                <td>${row.health}%</td>
                <td>${row.lastUpdated}</td>
            </tr>
        `).join('');
    }
    
    function sortData(data, column, direction) {
        return [...data].sort((a, b) => {
            if (a[column] < b[column]) return direction === 'asc' ? -1 : 1;
            if (a[column] > b[column]) return direction === 'asc' ? 1 : -1;
            return 0;
        });
    }
    
    // Search implementation
    document.getElementById('table-search').addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        tableData = originalData.filter(row =>
            Object.values(row).some(val =>
                String(val).toLowerCase().includes(query)
            )
        );
        currentPage = 1;
        renderTable();
    });
</script>
```

---

### Tab 5: Recommendations (Actionable Insights)

**Purpose:** AI-generated recommendations with priority ranking and implementation steps

**Required Sections:**
1. **Priority Matrix** - High/Medium/Low priority recommendations
2. **Implementation Steps** - Numbered action items
3. **Expected Impact** - Quantified benefits
4. **Estimated Effort** - Time/complexity estimates
5. **Related Resources** - Links to documentation

**Smart Annotations:**
```json
{
  "recommendations": [
    {
      "priority": "high",
      "title": "Improve Testing Coverage for Warning Features",
      "rationale": "5 features at 70% coverage limiting deployment confidence",
      "steps": [
        "Generate test skeletons using System Alignment remediation",
        "Fill in test cases for critical paths",
        "Validate coverage increases to 80%+"
      ],
      "expectedImpact": "+5% overall health (70% → 75%)",
      "estimatedEffort": "4-6 hours",
      "relatedResources": [
        "/docs/tdd-mastery-guide.md",
        "/docs/test-strategy.yaml"
      ]
    }
  ]
}
```

**Example Structure:**
```html
<div class="tab-content" id="recommendations-tab">
    <section class="priority-section high-priority">
        <h3>🔴 High Priority (3)</h3>
        <div class="recommendation-card">
            <h4>Improve Testing Coverage</h4>
            <p class="rationale">5 features at 70% coverage limiting deployment confidence</p>
            <ol class="steps">
                <li>Generate test skeletons using System Alignment</li>
                <li>Fill in test cases for critical paths</li>
                <li>Validate coverage increases to 80%+</li>
            </ol>
            <div class="impact">
                <strong>Expected Impact:</strong> +5% overall health
            </div>
            <div class="effort">
                <strong>Estimated Effort:</strong> 4-6 hours
            </div>
            <div class="resources">
                <strong>Resources:</strong>
                <a href="/docs/tdd-mastery-guide.md">TDD Guide</a>
            </div>
        </div>
    </section>
    
    <section class="priority-section medium-priority">
        <h3>🟡 Medium Priority (5)</h3>
        <!-- Medium priority cards -->
    </section>
    
    <section class="priority-section low-priority">
        <h3>🟢 Low Priority (2)</h3>
        <!-- Low priority cards -->
    </section>
</div>
```

---

## 🎨 CSS Requirements

### Base Styles (MANDATORY)

```css
:root {
    --primary-color: #2196F3;
    --success-color: #4CAF50;
    --warning-color: #FF9800;
    --danger-color: #F44336;
    --bg-color: #F5F5F5;
    --card-bg: #FFFFFF;
    --text-color: #333333;
    --border-color: #DDDDDD;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    background: var(--bg-color);
    color: var(--text-color);
    line-height: 1.6;
}

/* Tab Navigation */
.dashboard-tabs {
    background: var(--card-bg);
    border-bottom: 2px solid var(--border-color);
    display: flex;
    padding: 0 20px;
}

.tab-button {
    background: none;
    border: none;
    padding: 15px 25px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    color: var(--text-color);
    border-bottom: 3px solid transparent;
    transition: all 0.3s ease;
}

.tab-button:hover {
    color: var(--primary-color);
}

.tab-button.active {
    color: var(--primary-color);
    border-bottom-color: var(--primary-color);
}

/* Tab Content */
.tab-content {
    display: none;
    padding: 20px;
    animation: fadeIn 0.3s ease;
}

.tab-content.active {
    display: block;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Cards */
.metric-card {
    background: var(--card-bg);
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    transition: transform 0.2s ease;
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

/* Status Badges */
.status-badge {
    display: inline-block;
    padding: 5px 15px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}

.status-badge.healthy {
    background: var(--success-color);
    color: white;
}

.status-badge.warning {
    background: var(--warning-color);
    color: white;
}

.status-badge.critical {
    background: var(--danger-color);
    color: white;
}

/* Data Tables */
.data-table {
    width: 100%;
    border-collapse: collapse;
    background: var(--card-bg);
}

.data-table th {
    background: var(--primary-color);
    color: white;
    padding: 12px;
    text-align: left;
    cursor: pointer;
    user-select: none;
}

.data-table th:hover {
    background: #1976D2;
}

.data-table td {
    padding: 12px;
    border-bottom: 1px solid var(--border-color);
}

.data-table tr:hover {
    background: #F5F5F5;
}

/* Export Controls */
.export-controls {
    position: fixed;
    bottom: 20px;
    right: 20px;
    display: flex;
    gap: 10px;
}

.export-controls button {
    background: var(--primary-color);
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    transition: all 0.3s ease;
}

.export-controls button:hover {
    background: #1976D2;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
}

/* Responsive Design */
@media (max-width: 768px) {
    .dashboard-tabs {
        flex-direction: column;
    }
    
    .tab-button {
        width: 100%;
        text-align: left;
    }
    
    .export-controls {
        flex-direction: column;
        bottom: 10px;
        right: 10px;
    }
}
```

---

## 📊 Data Format Requirements

### JSON Data Structure

```json
{
  "metadata": {
    "generatedAt": "2025-11-28T14:30:00Z",
    "version": "3.4.0",
    "operationType": "system_alignment",
    "author": "CORTEX"
  },
  "overview": {
    "executiveSummary": "3-sentence narrative summary",
    "keyMetrics": [
      {
        "label": "System Health",
        "value": "85%",
        "trend": "up",
        "trendValue": "+5%",
        "status": "healthy"
      }
    ],
    "statusIndicator": {
      "status": "healthy",
      "message": "All systems operational"
    }
  },
  "visualizations": {
    "forceGraph": {
      "nodes": [
        { "id": "feature1", "group": 1, "label": "Feature 1" }
      ],
      "links": [
        { "source": "feature1", "target": "feature2", "value": 1 }
      ]
    },
    "timeSeries": {
      "labels": ["2025-11-01", "2025-11-08", "2025-11-15"],
      "datasets": [
        {
          "label": "Health Score",
          "data": [78, 82, 85]
        }
      ]
    }
  },
  "diagrams": [
    {
      "title": "System Architecture",
      "mermaidCode": "graph TD\nA[Start] --> B[End]",
      "type": "flowchart"
    }
  ],
  "dataTable": [
    {
      "name": "Feature 1",
      "type": "operation",
      "status": "healthy",
      "health": 92,
      "lastUpdated": "2025-11-28"
    }
  ],
  "recommendations": [
    {
      "priority": "high",
      "title": "Recommendation title",
      "rationale": "Why this matters",
      "steps": ["Step 1", "Step 2"],
      "expectedImpact": "Quantified benefit",
      "estimatedEffort": "Time estimate",
      "relatedResources": ["link1", "link2"]
    }
  ]
}
```

---

## ⚡ Performance Requirements

### Mandatory Benchmarks

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Dashboard Generation** | <5 seconds | Time from method call to file written |
| **Initial Page Load** | <2 seconds | DOMContentLoaded event |
| **D3.js Render** | <1 second | First visualization visible |
| **Tab Switching** | <300ms | Animation completion |
| **Export PDF** | <7 seconds | File download starts |
| **Export PNG** | <3 seconds | File download starts |
| **Export PPTX** | <10 seconds | File download starts |
| **Memory Usage** | <500MB | Peak during generation |
| **File Size** | <2MB | Generated HTML file |

### Optimization Techniques

1. **Lazy Loading** - Load tab content on first view
2. **Data Pagination** - Limit initial table rows to 25
3. **Image Optimization** - Compress embedded images
4. **Minification** - Minify inline JavaScript/CSS
5. **CDN Usage** - Load D3.js/Chart.js from CDN
6. **Caching** - Cache rendered visualizations

---

## 🔒 Security Requirements

### Content Security Policy (CSP)

```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               script-src 'self' https://d3js.org https://cdn.jsdelivr.net; 
               style-src 'self' 'unsafe-inline'; 
               img-src 'self' data:;">
```

### XSS Prevention

- **Sanitize User Input** - Escape all user-generated content
- **No eval()** - Never use eval() for data processing
- **No inline event handlers** - Use addEventListener()
- **Validate JSON** - Parse and validate all JSON data

### Data Privacy

- **No External Analytics** - No Google Analytics or tracking
- **No External Fonts** - Use system fonts only
- **Local Storage Only** - No cookies or session storage
- **Admin-Only Access** - Dashboards require authentication

---

## 📤 Export Functionality Requirements

### PDF Export

**Library:** Playwright or Puppeteer  
**Requirements:**
- Preserve interactive elements as images
- Maintain layout/styling
- Include all tabs in multi-page PDF
- Add table of contents
- File size <10MB

**Implementation:**
```python
async def export_to_pdf(html_file: str, output_file: str) -> bool:
    """Export dashboard to PDF."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f'file://{html_file}')
        await page.pdf(path=output_file, format='A4', print_background=True)
        await browser.close()
    return True
```

### PNG Export

**Library:** Playwright screenshot  
**Requirements:**
- Capture current tab or full page
- Resolution: 1920x1080 minimum
- Format: PNG with transparency support
- File size <5MB

### PPTX Export

**Library:** python-pptx  
**Requirements:**
- One slide per tab
- Preserve visualizations as images
- Maintain branding/styling
- Add speaker notes with data summary
- File size <15MB

---

## ✅ Validation Checklist

### Structure Validation

- [ ] All 5 tabs present (overview, visualizations, diagrams, data, recommendations)
- [ ] Tab navigation functional
- [ ] Export controls present
- [ ] CSP headers configured
- [ ] Responsive design (mobile/tablet/desktop)

### Content Validation

- [ ] Executive summary (3 sentences)
- [ ] Key metrics (5 minimum)
- [ ] Status indicator (healthy/warning/critical)
- [ ] D3.js visualization (at least 1)
- [ ] Chart.js visualization (at least 1)
- [ ] Mermaid diagram (at least 1)
- [ ] Data table (sortable, filterable)
- [ ] Recommendations (prioritized)

### Functional Validation

- [ ] Tab switching works
- [ ] Visualizations interactive (zoom, pan, hover)
- [ ] Table sorting works
- [ ] Table filtering works
- [ ] Export PDF works
- [ ] Export PNG works
- [ ] Export PPTX works

### Performance Validation

- [ ] Generation time <5s
- [ ] Page load time <2s
- [ ] D3.js render time <1s
- [ ] Memory usage <500MB
- [ ] File size <2MB

### Security Validation

- [ ] CSP headers present
- [ ] No eval() usage
- [ ] No inline event handlers
- [ ] User input sanitized
- [ ] No external trackers

---

## 📚 Migration Guide Reference

**See:** `cortex-brain/documents/guides/EPM-MIGRATION-GUIDE.md` for step-by-step instructions on updating existing admin EPMs to conform to this specification.

---

## 🔄 Version History

**v1.0.0** (2025-11-28)
- Initial specification
- Mandatory 5-tab structure
- D3.js v7+ requirements
- Export functionality requirements
- Performance benchmarks
- Security requirements

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)
