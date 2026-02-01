# Dashboard Enhancement Implementation Guide
**CORTEX Phase 18 - Visualization Integration**
**Author:** Asif Hussain
**Status:** Implementation Ready

---

## 🎯 Executive Summary

This document provides step-by-step instructions to enhance the existing `dashboard.html` with Phase 18 enterprise-grade visualizations using D3.js and Chart.js.

**Current State:** Dashboard has tab structure but lacks interactive visualizations  
**Target State:** Enterprise dashboard with 9 working visualizations + test suite  
**Approach:** Component-based, test-driven, security-first

---

## 📋 Prerequisites Completed

✅ Test infrastructure (`conftest.py`, `test_html_lint.py`)  
✅ Component templates (`chart_directory_treemap.html.j2`, `chart_quality_radar.html.j2`)  
✅ Existing tab structure in dashboard.html  

---

## 🔧 Implementation Steps

### Step 1: Add Library Dependencies (BEFORE `</head>`)

```html
<!-- Chart.js v4.x with SRI hash -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js" 
        integrity="sha384-<HASH_HERE>"
        crossorigin="anonymous"></script>

<!-- D3.js v7.x already loaded at line 1976 -->
```

**Action Required:**
1. Generate SRI hash: `curl https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js | openssl dgst -sha384 -binary | openssl base64 -A`
2. Replace `<HASH_HERE>` with generated hash

---

### Step 2: Create Global Data Object (AFTER libraries, BEFORE closing `</body>`)

```html
<script>
// Global dashboard data (populated from JSON files)
window.dashboardData = {
  // Architecture Tab
  directoryTree: {
    name: "root",
    children: [
      {name: "App_Code", children: [], size: 125000},
      {name: "Models", children: [], size: 89000},
      {name: "Views", children: [], size: 156000}
    ]
  },
  
  dependencies: {
    nodes: [
      {id: "System.Web", group: 1},
      {id: "System.Data", group: 2}
    ],
    links: [
      {source: "System.Web", target: "System.Data", value: 1}
    ]
  },
  
  // Quality Tab
  qualityMetrics: {
    maintainability: 70,
    complexity: 65,
    testCoverage: 80,
    documentation: 60,
    security: 75,
    performance: 70
  },
  
  complexityData: {
    labels: ['0-5', '6-10', '11-15', '16-20', '21+'],
    values: [45, 32, 15, 6, 2]
  },
  
  locDistribution: {
    labels: ['<100', '100-500', '500-1000', '1000+'],
    values: [34, 28, 15, 12]
  },
  
  // Vulnerabilities Tab
  vulnerabilities: {
    codeSmells: 9,
    antiPatterns: 5,
    securityIssues: 3,
    bestPractices: 8
  },
  
  // Dependencies Tab  
  dependencyTree: {
    name: "KASHKOLE",
    children: [
      {name: "System.Web", children: []},
      {name: "System.Data", children: []}
    ]
  },
  
  // Testing Tab
  testingPyramid: {
    unit: 45,
    integration: 23,
    e2e: 8
  }
};
</script>
```

---

### Step 3: Enhance Architecture Tab (Replace line 1860-1970)

**Find:**
```html
<div id="architecture" class="tab-content">
```

**Add AFTER architecture overview section:**

```html
<!-- Directory Structure Treemap -->
<section class="section-panel">
  <h2 class="section-title">📁 Directory Structure</h2>
  <p style="color: var(--text-secondary); margin-bottom: 1rem;">Hierarchical visualization of repository files</p>
  <div class="chart-container">
    <div id="directory-treemap" class="visualization-canvas" 
         role="img" 
         aria-label="Directory structure treemap visualization"
         style="min-height: 500px;">
    </div>
  </div>
</section>

<!-- Dependency Force Graph -->
<section class="section-panel">
  <h2 class="section-title">🔗 Dependency Graph</h2>
  <p style="color: var(--text-secondary); margin-bottom: 1rem;">Interactive force-directed dependency visualization</p>
  <div class="chart-container">
    <svg id="dependency-force-graph" 
         role="img" 
         aria-label="Dependency force-directed graph"
         style="width: 100%; height: 600px; background: rgba(0,0,0,0.2); border-radius: 8px;">
    </svg>
  </div>
</section>

<!-- Layer Diagram -->
<section class="section-panel">
  <h2 class="section-title">📐 Layer Diagram</h2>
  <p style="color: var(--text-secondary); margin-bottom: 1rem;">Architecture layers flow (Presentation → Domain → Infrastructure)</p>
  <div id="layer-diagram" 
       role="img" 
       aria-label="Architecture layer diagram"
       style="min-height: 400px; background: rgba(0,0,0,0.2); border-radius: 8px; padding: 20px;">
    <!-- SVG will be rendered here -->
  </div>
</section>
```

---

### Step 4: Add Quality Tab Visualizations

**Find:** `<div id="classes" class="tab-content">` (line 1313)

**Add NEW section BEFORE it:**

```html
<!-- ============================================
     CODE QUALITY TAB
     ============================================ -->
<div id="quality" class="tab-content">
  <!-- Quality Metrics Overview -->
  <section class="section-panel">
    <h2 class="section-title">✨ Code Quality Overview</h2>
    <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));">
      <div class="metric-card">
        <div class="metric-value" style="color: var(--success);">75/100</div>
        <div class="metric-label">Overall Quality</div>
      </div>
      <div class="metric-card">
        <div class="metric-value">2,345</div>
        <div class="metric-label">Technical Debt (hrs)</div>
      </div>
      <div class="metric-card">
        <div class="metric-value" style="color: var(--warning);">12.5</div>
        <div class="metric-label">Avg Complexity</div>
      </div>
    </div>
  </section>

  <!-- Quality Radar Chart -->
  <section class="section-panel">
    <h2 class="section-title">📊 Multi-Dimensional Quality</h2>
    <div class="chart-canvas-wrapper" style="position: relative; height: 450px; padding: 20px;">
      <canvas id="quality-radar" 
              role="img" 
              aria-label="Code quality radar chart"></canvas>
    </div>
  </section>

  <!-- Complexity Histogram -->
  <section class="section-panel">
    <h2 class="section-title">📈 Complexity Distribution</h2>
    <div class="chart-canvas-wrapper" style="position: relative; height: 400px; padding: 20px;">
      <canvas id="complexity-histogram" 
              role="img" 
              aria-label="Cyclomatic complexity histogram"></canvas>
    </div>
  </section>

  <!-- LOC Distribution -->
  <section class="section-panel">
    <h2 class="section-title">📏 Lines of Code Distribution</h2>
    <div class="chart-canvas-wrapper" style="position: relative; height: 400px; padding: 20px;">
      <canvas id="loc-bar-chart" 
              role="img" 
              aria-label="Lines of code distribution bar chart"></canvas>
    </div>
  </section>
</div>
```

---

### Step 5: Add Vulnerabilities Tab

**Add AFTER Quality tab:**

```html
<!-- ============================================
     VULNERABILITIES TAB (NEW)
     ============================================ -->
<div id="vulnerabilities" class="tab-content">
  <!-- Vulnerability Summary -->
  <section class="section-panel" style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%);">
    <h2 class="section-title">⚠️ Vulnerability Summary</h2>
    <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));">
      <div class="metric-card" style="border-left: 4px solid var(--danger);">
        <div class="metric-value" style="color: var(--danger);">9</div>
        <div class="metric-label">Code Smells</div>
      </div>
      <div class="metric-card" style="border-left: 4px solid var(--warning);">
        <div class="metric-value" style="color: var(--warning);">5</div>
        <div class="metric-label">Anti-Patterns</div>
      </div>
      <div class="metric-card" style="border-left: 4px solid var(--danger);">
        <div class="metric-value" style="color: var(--danger);">3</div>
        <div class="metric-label">Security Issues</div>
      </div>
      <div class="metric-card" style="border-left: 4px solid var(--info);">
        <div class="metric-value" style="color: var(--info);">8</div>
        <div class="metric-label">Best Practice Gaps</div>
      </div>
    </div>
  </section>

  <!-- Vulnerability Distribution Pie Chart -->
  <section class="section-panel">
    <h2 class="section-title">🥧 Vulnerability Breakdown</h2>
    <div class="chart-canvas-wrapper" style="position: relative; height: 450px; padding: 20px;">
      <canvas id="vulnerability-pie-chart" 
              role="img" 
              aria-label="Vulnerability distribution pie chart"></canvas>
    </div>
  </section>

  <!-- Code Smells Detail -->
  <section class="section-panel">
    <h3 class="section-title" style="font-size: var(--font-size-lg);">🔍 Code Smells Detected</h3>
    <div style="display: grid; gap: 1rem;">
      <div class="issue-card" style="border-left: 4px solid var(--warning);">
        <div style="display: flex; justify-content: space-between; align-items: start;">
          <div>
            <h4 style="margin: 0; color: var(--warning);">God Object</h4>
            <p style="margin: 0.5rem 0; color: var(--text-secondary);">Class exceeds 1000 LOC</p>
            <code style="background: rgba(0,0,0,0.3); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.85rem;">
              Models/HealthPlan.cs:45
            </code>
          </div>
          <span style="background: var(--warning); color: #000; padding: 0.35rem 0.75rem; border-radius: var(--radius-sm); font-size: 0.85rem; font-weight: 600;">
            HIGH
          </span>
        </div>
      </div>
    </div>
  </section>
</div>
```

---

### Step 6: Add Visualization Rendering Scripts

**Add BEFORE closing `</body>` tag:**

```html
<script>
// ============================================
// VISUALIZATION RENDERING
// ============================================

// Track rendered tabs to avoid re-rendering
const renderedTabs = new Set();

function renderVisualization(tabName) {
  if (renderedTabs.has(tabName)) return;
  
  switch(tabName) {
    case 'architecture':
      renderArchitectureVisualizations();
      break;
    case 'quality':
      renderQualityVisualizations();
      break;
    case 'vulnerabilities':
      renderVulnerabilityVisualizations();
      break;
    case 'dependencies':
      renderDependencyTree();
      break;
    case 'testing':
      renderTestingPyramid();
      break;
  }
  
  renderedTabs.add(tabName);
}

// Architecture Visualizations
function renderArchitectureVisualizations() {
  renderDirectoryTreemap();
  renderDependencyForceGraph();
  renderLayerDiagram();
}

function renderDirectoryTreemap() {
  if (!window.dashboardData.directoryTree) return;
  
  const width = 800;
  const height = 500;
  
  const container = d3.select("#directory-treemap");
  container.html("");
  
  const svg = container.append("svg")
    .attr("width", "100%")
    .attr("height", height)
    .attr("viewBox", [0, 0, width, height]);
  
  const root = d3.hierarchy(window.dashboardData.directoryTree)
    .sum(d => d.size || 0)
    .sort((a, b) => b.value - a.value);
  
  d3.treemap()
    .size([width, height])
    .padding(2)
    .round(true)(root);
  
  const color = d3.scaleOrdinal(d3.schemeCategory10);
  
  const leaf = svg.selectAll("g")
    .data(root.leaves())
    .join("g")
    .attr("transform", d => `translate(${d.x0},${d.y0})`);
  
  leaf.append("rect")
    .attr("fill", d => color(d.parent.data.name))
    .attr("fill-opacity", 0.6)
    .attr("stroke", "#fff")
    .attr("stroke-width", 2)
    .attr("width", d => d.x1 - d.x0)
    .attr("height", d => d.y1 - d.y0)
    .append("title")
    .text(d => `${d.data.name}\n${d.value} bytes`);
  
  leaf.append("text")
    .attr("x", 4)
    .attr("y", 16)
    .text(d => d.data.name)
    .attr("font-size", "12px")
    .attr("fill", "#fff")
    .style("pointer-events", "none");
}

function renderDependencyForceGraph() {
  if (!window.dashboardData.dependencies) return;
  
  const width = 800;
  const height = 600;
  
  const svg = d3.select("#dependency-force-graph");
  svg.selectAll("*").remove();
  
  const simulation = d3.forceSimulation(window.dashboardData.dependencies.nodes)
    .force("link", d3.forceLink(window.dashboardData.dependencies.links).id(d => d.id))
    .force("charge", d3.forceManyBody().strength(-300))
    .force("center", d3.forceCenter(width / 2, height / 2));
  
  const link = svg.append("g")
    .selectAll("line")
    .data(window.dashboardData.dependencies.links)
    .join("line")
    .attr("stroke", "rgba(255,255,255,0.3)")
    .attr("stroke-width", 2);
  
  const node = svg.append("g")
    .selectAll("circle")
    .data(window.dashboardData.dependencies.nodes)
    .join("circle")
    .attr("r", 10)
    .attr("fill", d => d3.schemeCategory10[d.group % 10])
    .call(d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended));
  
  node.append("title")
    .text(d => d.id);
  
  simulation.on("tick", () => {
    link
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);
    
    node
      .attr("cx", d => d.x)
      .attr("cy", d => d.y);
  });
  
  function dragstarted(event) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    event.subject.fx = event.subject.x;
    event.subject.fy = event.subject.y;
  }
  
  function dragged(event) {
    event.subject.fx = event.x;
    event.subject.fy = event.y;
  }
  
  function dragended(event) {
    if (!event.active) simulation.alphaTarget(0);
    event.subject.fx = null;
    event.subject.fy = null;
  }
}

function renderLayerDiagram() {
  const container = d3.select("#layer-diagram");
  container.html("");
  
  const layers = [
    {name: "Presentation", color: "#4d8cff", y: 50},
    {name: "Domain", color: "#7fb3ff", y: 150},
    {name: "Infrastructure", color: "#a3c9ff", y: 250}
  ];
  
  const svg = container.append("svg")
    .attr("width", "100%")
    .attr("height", 350)
    .attr("viewBox", [0, 0, 800, 350]);
  
  layers.forEach(layer => {
    svg.append("rect")
      .attr("x", 100)
      .attr("y", layer.y)
      .attr("width", 600)
      .attr("height", 80)
      .attr("fill", layer.color)
      .attr("fill-opacity", 0.6)
      .attr("stroke", "#fff")
      .attr("stroke-width", 2)
      .attr("rx", 8);
    
    svg.append("text")
      .attr("x", 400)
      .attr("y", layer.y + 45)
      .attr("text-anchor", "middle")
      .attr("fill", "#fff")
      .attr("font-size", "18px")
      .attr("font-weight", "600")
      .text(layer.name + " Layer");
  });
  
  // Draw arrows between layers
  [100, 200].forEach(y => {
    svg.append("path")
      .attr("d", `M 400 ${y + 80} L 400 ${y + 100}`)
      .attr("stroke", "#fff")
      .attr("stroke-width", 3)
      .attr("marker-end", "url(#arrowhead)");
  });
  
  svg.append("defs").append("marker")
    .attr("id", "arrowhead")
    .attr("markerWidth", 10)
    .attr("markerHeight", 10)
    .attr("refX", 5)
    .attr("refY", 3)
    .attr("orient", "auto")
    .append("polygon")
    .attr("points", "0 0, 10 3, 0 6")
    .attr("fill", "#fff");
}

// Quality Visualizations
function renderQualityVisualizations() {
  renderQualityRadar();
  renderComplexityHistogram();
  renderLOCBarChart();
}

function renderQualityRadar() {
  const ctx = document.getElementById('quality-radar');
  if (!ctx) return;
  
  new Chart(ctx, {
    type: 'radar',
    data: {
      labels: ['Maintainability', 'Complexity', 'Test Coverage', 'Documentation', 'Security', 'Performance'],
      datasets: [{
        label: 'Quality Score',
        data: [
          window.dashboardData.qualityMetrics.maintainability,
          window.dashboardData.qualityMetrics.complexity,
          window.dashboardData.qualityMetrics.testCoverage,
          window.dashboardData.qualityMetrics.documentation,
          window.dashboardData.qualityMetrics.security,
          window.dashboardData.qualityMetrics.performance
        ],
        fill: true,
        backgroundColor: 'rgba(77, 140, 255, 0.2)',
        borderColor: 'rgb(77, 140, 255)',
        pointBackgroundColor: 'rgb(77, 140, 255)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgb(77, 140, 255)'
      }]
    },
    options: {
      elements: {line: {borderWidth: 3}},
      scales: {
        r: {
          angleLines: {color: 'rgba(255, 255, 255, 0.1)'},
          grid: {color: 'rgba(255, 255, 255, 0.1)'},
          pointLabels: {
            color: 'rgba(255, 255, 255, 0.8)',
            font: {size: 13}
          },
          ticks: {
            color: 'rgba(255, 255, 255, 0.6)',
            backdropColor: 'transparent',
            min: 0,
            max: 100
          }
        }
      },
      plugins: {
        legend: {labels: {color: 'rgba(255, 255, 255, 0.8)'}}
      }
    }
  });
}

function renderComplexityHistogram() {
  const ctx = document.getElementById('complexity-histogram');
  if (!ctx) return;
  
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: window.dashboardData.complexityData.labels,
      datasets: [{
        label: 'File Count',
        data: window.dashboardData.complexityData.values,
        backgroundColor: 'rgba(77, 140, 255, 0.6)',
        borderColor: 'rgb(77, 140, 255)',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {color: 'rgba(255, 255, 255, 0.8)'},
          grid: {color: 'rgba(255, 255, 255, 0.1)'}
        },
        x: {
          ticks: {color: 'rgba(255, 255, 255, 0.8)'},
          grid: {color: 'rgba(255, 255, 255, 0.1)'}
        }
      },
      plugins: {
        legend: {labels: {color: 'rgba(255, 255, 255, 0.8)'}},
        title: {
          display: true,
          text: 'Cyclomatic Complexity Distribution',
          color: 'rgba(255, 255, 255, 0.9)',
          font: {size: 16}
        }
      }
    }
  });
}

function renderLOCBarChart() {
  const ctx = document.getElementById('loc-bar-chart');
  if (!ctx) return;
  
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: window.dashboardData.locDistribution.labels,
      datasets: [{
        label: 'Files',
        data: window.dashboardData.locDistribution.values,
        backgroundColor: [
          'rgba(34, 197, 94, 0.6)',
          'rgba(77, 140, 255, 0.6)',
          'rgba(245, 158, 11, 0.6)',
          'rgba(239, 68, 68, 0.6)'
        ],
        borderColor: [
          'rgb(34, 197, 94)',
          'rgb(77, 140, 255)',
          'rgb(245, 158, 11)',
          'rgb(239, 68, 68)'
        ],
        borderWidth: 2
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          beginAtZero: true,
          ticks: {color: 'rgba(255, 255, 255, 0.8)'},
          grid: {color: 'rgba(255, 255, 255, 0.1)'}
        },
        y: {
          ticks: {color: 'rgba(255, 255, 255, 0.8)'},
          grid: {color: 'rgba(255, 255, 255, 0.1)'}
        }
      },
      plugins: {
        legend: {labels: {color: 'rgba(255, 255, 255, 0.8)'}},
        title: {
          display: true,
          text: 'File Size Distribution (Lines of Code)',
          color: 'rgba(255, 255, 255, 0.9)',
          font: {size: 16}
        }
      }
    }
  });
}

// Vulnerability Visualizations
function renderVulnerabilityVisualizations() {
  renderVulnerabilityPieChart();
}

function renderVulnerabilityPieChart() {
  const ctx = document.getElementById('vulnerability-pie-chart');
  if (!ctx) return;
  
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Code Smells', 'Anti-Patterns', 'Security Issues', 'Best Practice Gaps'],
      datasets: [{
        data: [
          window.dashboardData.vulnerabilities.codeSmells,
          window.dashboardData.vulnerabilities.antiPatterns,
          window.dashboardData.vulnerabilities.securityIssues,
          window.dashboardData.vulnerabilities.bestPractices
        ],
        backgroundColor: [
          'rgba(239, 68, 68, 0.6)',
          'rgba(245, 158, 11, 0.6)',
          'rgba(239, 68, 68, 0.8)',
          'rgba(77, 140, 255, 0.6)'
        ],
        borderColor: '#0a1428',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right',
          labels: {
            color: 'rgba(255, 255, 255, 0.8)',
            font: {size: 14},
            padding: 20
          }
        },
        title: {
          display: true,
          text: 'Vulnerability Distribution',
          color: 'rgba(255, 255, 255, 0.9)',
          font: {size: 18}
        }
      }
    }
  });
}

// Dependency Tree
function renderDependencyTree() {
  // Similar to treemap but hierarchical
  console.log("Dependency tree rendering...");
}

// Testing Pyramid
function renderTestingPyramid() {
  console.log("Testing pyramid rendering...");
}

// Auto-render on tab switch
document.addEventListener('DOMContentLoaded', function() {
  // Render first tab on load
  const firstTab = document.querySelector('.tab-button.active');
  if (firstTab) {
    const tabName = firstTab.getAttribute('onclick').match(/'([^']+)'/)[1];
    renderVisualization(tabName);
  }
});
</script>
```

---

## 🧪 Testing

Run test suite:
```bash
cd /Users/asifhussain/PROJECTS/CORTEX
pytest company/dashboards/kashkole/tests/test_html_lint.py -v
```

Expected output:
```
test_html_valid_doctype PASSED
test_html_has_lang_attribute PASSED
test_tab_exists[architecture-Architecture] PASSED
test_chart_container_exists[directory-treemap] PASSED
test_d3js_library_loaded PASSED
test_chartjs_library_loaded PASSED
```

---

## 🛡️ Security Checklist

- [ ] SRI hashes added for CDN libraries
- [ ] `window.dashboardData` escapes user input (if any)
- [ ] No `eval()` or `Function()` constructor used
- [ ] All SVG elements sanitized
- [ ] File size limit enforced (<50MB)

---

## 📊 Success Metrics

**P0 (Blocking):**
- [ ] All 9 visualizations render without errors
- [ ] HTML lint tests pass
- [ ] Dashboard opens in browser (file:// protocol)

**P1 (Required):**
- [ ] Visualizations interactive (tooltips, zoom, drag)
- [ ] WCAG 2.1 AA compliance
- [ ] Responsive (mobile/tablet/desktop)

**P2 (Nice-to-have):**
- [ ] Performance <5s load time
- [ ] Print-friendly CSS
- [ ] Export to PNG functionality

---

## 🚀 Next Steps

1. **Implement Steps 1-6** — Add library, data object, tab enhancements, and rendering scripts
2. **Run Tests** — Validate with `pytest`
3. **Manual QA** — Open in browser, test all tabs
4. **Phase 18.8** — Automate generation for all 5 simulation tiers
5. **Phase 19** — MCP exposure via `cortex_generate_dashboard_suite`

---

**End of Implementation Guide**
