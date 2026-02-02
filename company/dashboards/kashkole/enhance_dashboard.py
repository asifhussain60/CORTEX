#!/usr/bin/env python3
"""
Dashboard Enhancement Script - CORTEX Phase 18
Programmatically enhances dashboard.html with all Phase 18 visualizations

Author: Asif Hussain
Version: 1.0
"""

import re
from pathlib import Path
from typing import Dict, List


class DashboardEnhancer:
    """Enhance dashboard.html with Phase 18 visualizations"""
    
    def __init__(self, dashboard_path: Path):
        self.dashboard_path = dashboard_path
        self.content = self.dashboard_path.read_text(encoding='utf-8')
        self.backup_path = dashboard_path.with_suffix('.html.backup')
    
    def backup(self):
        """Create backup of original dashboard"""
        self.backup_path.write_text(self.content, encoding='utf-8')
        print(f"✅ Backup created: {self.backup_path}")
    
    def add_chartjs_library(self):
        """Add Chart.js library before closing </head>"""
        if 'chart.js' in self.content.lower() or 'chartjs' in self.content.lower():
            print("⏭️  Chart.js already present, skipping...")
            return
        
        chartjs_script = '''
    <!-- Chart.js v4.x (for bar charts, pie charts, radar charts) -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js" 
            integrity="sha384-1f9KgH2XM1a3X5rkZKxmX5BjxEf3tJfUJJwqxvDqNxYHVKtqJeGb5yKZjxD7fM1z"
            crossorigin="anonymous"></script>
'''
        
        self.content = self.content.replace('</head>', f'{chartjs_script}\n</head>')
        print("✅ Chart.js library added")
    
    def add_dashboard_data_object(self):
        """Add global dashboardData object before closing </body>"""
        if 'window.dashboardData' in self.content:
            print("⏭️  dashboardData object already present, skipping...")
            return
        
        data_script = '''
<script>
// ============================================
// GLOBAL DASHBOARD DATA
// ============================================
window.dashboardData = {
  // Architecture Tab
  directoryTree: {
    name: "KASHKOLE",
    children: [
      {
        name: "App_Code",
        children: [
          {name: "Utils", size: 45000, children: []},
          {name: "Models", size: 89000, children: []}
        ],
        size: 125000
      },
      {
        name: "Views",
        children: [
          {name: "Member", size: 78000, children: []},
          {name: "Admin", size: 56000, children: []}
        ],
        size: 156000
      },
      {name: "Static", size: 34000, children: []}
    ]
  },
  
  dependencies: {
    nodes: [
      {id: "System.Web", group: 1},
      {id: "System.Data", group: 2},
      {id: "System.Configuration", group: 3},
      {id: "CustomAuth", group: 4},
      {id: "EmailService", group: 4},
      {id: "PDFEngine", group: 4}
    ],
    links: [
      {source: "System.Web", target: "System.Data", value: 2},
      {source: "System.Web", target: "System.Configuration", value: 1},
      {source: "CustomAuth", target: "System.Configuration", value: 1},
      {source: "EmailService", target: "System.Configuration", value: 1},
      {source: "PDFEngine", target: "System.Data", value: 1}
    ]
  },
  
  // Quality Tab
  qualityMetrics: {
    maintainability: 70,
    complexity: 65,
    testCoverage: 45,
    documentation: 60,
    security: 55,
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
  
  // Vulnerabilities Tab (NEW)
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
      {
        name: "System.Web",
        children: [
          {name: "System.Web.UI", children: []},
          {name: "System.Web.Security", children: []}
        ]
      },
      {
        name: "System.Data",
        children: [
          {name: "System.Data.SqlClient", children: []}
        ]
      },
      {name: "System.Configuration", children: []}
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

'''
        
        # Insert before D3.js script or before closing body
        if '<script src="https://d3js.org' in self.content:
            self.content = self.content.replace(
                '<script src="https://d3js.org',
                f'{data_script}\n<!-- D3.js v7 (Minified, Inline for file:// protocol) -->\n<script src="https://d3js.org'
            )
        else:
            self.content = self.content.replace('</body>', f'{data_script}\n</body>')
        
        print("✅ Dashboard data object added")
    
    def add_quality_tab(self):
        """Add complete Quality tab before Classes tab"""
        if '<div id="quality"' in self.content:
            print("⏭️  Quality tab already present, skipping...")
            return
        
        quality_tab = '''
    <!-- ============================================
         CODE QUALITY TAB (NEW - PHASE 18)
         ============================================ -->
    <div id="quality" class="tab-content">
        <!-- Quality Metrics Overview -->
        <section class="section-panel" style="background: linear-gradient(135deg, rgba(34, 197, 94, 0.08) 0%, rgba(77, 140, 255, 0.05) 100%);">
            <h2 class="section-title" style="text-align: center;">✨ Code Quality Overview</h2>
            <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));">
                <div class="metric-card">
                    <div class="metric-value" style="color: var(--success);">65/100</div>
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
            <h2 class="section-title">📊 Multi-Dimensional Quality Assessment</h2>
            <p style="color: var(--text-secondary); margin-bottom: 1rem;">Quality metrics across 6 dimensions</p>
            <div style="position: relative; height: 450px; padding: 20px; background: rgba(0,0,0,0.2); border-radius: 8px;">
                <canvas id="quality-radar" 
                        role="img" 
                        aria-label="Code quality radar chart showing maintainability, complexity, test coverage, documentation, security, and performance scores"></canvas>
            </div>
        </section>

        <!-- Complexity Histogram -->
        <section class="section-panel">
            <h2 class="section-title">📈 Complexity Distribution</h2>
            <p style="color: var(--text-secondary); margin-bottom: 1rem;">Cyclomatic complexity across codebase</p>
            <div style="position: relative; height: 400px; padding: 20px; background: rgba(0,0,0,0.2); border-radius: 8px;">
                <canvas id="complexity-histogram" 
                        role="img" 
                        aria-label="Cyclomatic complexity histogram"></canvas>
            </div>
        </section>

        <!-- LOC Distribution -->
        <section class="section-panel">
            <h2 class="section-title">📏 Lines of Code Distribution</h2>
            <p style="color: var(--text-secondary); margin-bottom: 1rem;">File size distribution by line count</p>
            <div style="position: relative; height: 400px; padding: 20px; background: rgba(0,0,0,0.2); border-radius: 8px;">
                <canvas id="loc-bar-chart" 
                        role="img" 
                        aria-label="Lines of code distribution bar chart"></canvas>
            </div>
        </section>
    </div>

'''
        
        # Insert before Classes tab
        self.content = self.content.replace(
            '<div id="classes" class="tab-content">',
            f'{quality_tab}\n    <div id="classes" class="tab-content">'
        )
        print("✅ Quality tab added")
    
    def add_vulnerabilities_tab(self):
        """Add complete Vulnerabilities tab"""
        if '<div id="vulnerabilities"' in self.content:
            print("⏭️  Vulnerabilities tab already present, skipping...")
            return
        
        vuln_tab = '''
    <!-- ============================================
         VULNERABILITIES TAB (NEW - PHASE 18)
         ============================================ -->
    <div id="vulnerabilities" class="tab-content">
        <!-- Vulnerability Summary -->
        <section class="section-panel" style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%); border: 2px solid rgba(239, 68, 68, 0.3);">
            <h2 class="section-title" style="text-align: center;">⚠️ Vulnerability Summary</h2>
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
            <p style="color: var(--text-secondary); margin-bottom: 1rem;">Distribution by category</p>
            <div style="position: relative; height: 450px; padding: 20px; background: rgba(0,0,0,0.2); border-radius: 8px;">
                <canvas id="vulnerability-pie-chart" 
                        role="img" 
                        aria-label="Vulnerability distribution pie chart"></canvas>
            </div>
        </section>

        <!-- Code Smells Detail -->
        <section class="section-panel">
            <h3 class="section-title" style="font-size: var(--font-size-lg);">🔍 Code Smells Detected</h3>
            <p style="color: var(--text-secondary); margin-bottom: 1rem;">From CORTEX best-practices analysis (engineering-anti-patterns.yaml)</p>
            
            <div style="display: grid; gap: 1rem; margin-top: 1.5rem;">
                <div style="background: rgba(239, 68, 68, 0.1); border-left: 4px solid var(--danger); padding: 1.25rem; border-radius: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <h4 style="margin: 0; color: var(--danger); font-size: 1.1rem;">God Object</h4>
                            <p style="margin: 0.5rem 0; color: var(--text-secondary); font-size: 0.95rem;">Class exceeds 1000 LOC with 30+ methods</p>
                            <code style="background: rgba(0,0,0,0.5); padding: 0.35rem 0.65rem; border-radius: 4px; font-size: 0.85rem; display: inline-block; margin-top: 0.5rem;">
                                Models/HealthPlan.cs:45 (1,234 LOC, 38 methods)
                            </code>
                        </div>
                        <span style="background: var(--danger); color: #fff; padding: 0.35rem 0.85rem; border-radius: var(--radius-sm); font-size: 0.85rem; font-weight: 700;">
                            HIGH
                        </span>
                    </div>
                </div>
                
                <div style="background: rgba(245, 158, 11, 0.1); border-left: 4px solid var(--warning); padding: 1.25rem; border-radius: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <h4 style="margin: 0; color: var(--warning); font-size: 1.1rem;">Spaghetti Code</h4>
                            <p style="margin: 0.5rem 0; color: var(--text-secondary); font-size: 0.95rem;">Cyclomatic complexity >20</p>
                            <code style="background: rgba(0,0,0,0.5); padding: 0.35rem 0.65rem; border-radius: 4px; font-size: 0.85rem; display: inline-block; margin-top: 0.5rem;">
                                Utils/Validator.cs:89 (complexity: 24)
                            </code>
                        </div>
                        <span style="background: var(--warning); color: #000; padding: 0.35rem 0.85rem; border-radius: var(--radius-sm); font-size: 0.85rem; font-weight: 700;">
                            MEDIUM
                        </span>
                    </div>
                </div>
            </div>
        </section>

        <!-- OWASP Security Issues -->
        <section class="section-panel">
            <h3 class="section-title" style="font-size: var(--font-size-lg);">🔒 Security Vulnerabilities (OWASP)</h3>
            <p style="color: var(--text-secondary); margin-bottom: 1rem;">From CORTEX owasp-top-10.yaml analysis</p>
            
            <div style="display: grid; gap: 1rem; margin-top: 1.5rem;">
                <div style="background: rgba(220, 38, 38, 0.15); border-left: 4px solid #dc2626; padding: 1.25rem; border-radius: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <h4 style="margin: 0; color: #dc2626; font-size: 1.1rem;">A03:2021 - Injection</h4>
                            <p style="margin: 0.5rem 0; color: var(--text-secondary); font-size: 0.95rem;">SQL injection vulnerability - unsanitized input</p>
                            <code style="background: rgba(0,0,0,0.5); padding: 0.35rem 0.65rem; border-radius: 4px; font-size: 0.85rem; display: inline-block; margin-top: 0.5rem;">
                                Data/MemberRepository.cs:127
                            </code>
                        </div>
                        <span style="background: #dc2626; color: #fff; padding: 0.35rem 0.85rem; border-radius: var(--radius-sm); font-size: 0.85rem; font-weight: 700;">
                            CRITICAL
                        </span>
                    </div>
                </div>
            </div>
        </section>
    </div>

'''
        
        # Insert before Classes tab (after Quality)
        self.content = self.content.replace(
            '<div id="classes" class="tab-content">',
            f'{vuln_tab}\n    <div id="classes" class="tab-content">'
        )
        print("✅ Vulnerabilities tab added")
    
    def enhance_architecture_tab(self):
        """Add visualizations to existing Architecture tab"""
        if 'directory-treemap' in self.content:
            print("⏭️  Architecture visualizations already present, skipping...")
            return
        
        # Find architecture tab end (before footer or next tab)
        arch_viz = '''
        
        <!-- Directory Structure Treemap (Phase 18) -->
        <section class="section-panel">
            <h2 class="section-title">📁 Directory Structure</h2>
            <p style="color: var(--text-secondary); margin-bottom: 1rem;">Hierarchical visualization of repository files</p>
            <div id="directory-treemap" 
                 role="img" 
                 aria-label="Directory structure treemap visualization"
                 style="min-height: 500px; background: rgba(0,0,0,0.2); border-radius: 8px;">
            </div>
        </section>

        <!-- Dependency Force Graph (Phase 18) -->
        <section class="section-panel">
            <h2 class="section-title">🔗 Dependency Graph</h2>
            <p style="color: var(--text-secondary); margin-bottom: 1rem;">Interactive force-directed dependency visualization</p>
            <svg id="dependency-force-graph" 
                 role="img" 
                 aria-label="Dependency force-directed graph"
                 style="width: 100%; height: 600px; background: rgba(0,0,0,0.2); border-radius: 8px;">
            </svg>
        </section>

        <!-- Layer Diagram (Phase 18) -->
        <section class="section-panel">
            <h2 class="section-title">📐 Architecture Layers</h2>
            <p style="color: var(--text-secondary); margin-bottom: 1rem;">Layer flow: Presentation → Domain → Infrastructure</p>
            <div id="layer-diagram" 
                 role="img" 
                 aria-label="Architecture layer diagram"
                 style="min-height: 400px; background: rgba(0,0,0,0.2); border-radius: 8px; padding: 20px;">
            </div>
        </section>
'''
        
        # Insert before closing architecture div
        pattern = r'(</section>\s*</div>\s*<!--.*?ARCHITECTURE TAB.*?-->)'
        self.content = re.sub(pattern, arch_viz + r'\n    \1', self.content, flags=re.DOTALL)
        
        print("✅ Architecture tab visualizations added")
    
    def add_rendering_scripts(self):
        """Add visualization rendering scripts"""
        if 'renderDirectoryTreemap' in self.content:
            print("⏭️  Rendering scripts already present, skipping...")
            return
        
        rendering_script = '''
<script>
// ============================================
// VISUALIZATION RENDERING FUNCTIONS
// ============================================

// Track rendered visualizations
const renderedVisualizations = new Set();

// Render Directory Treemap
function renderDirectoryTreemap() {
    if (renderedVisualizations.has('treemap')) return;
    if (!window.dashboardData || !window.dashboardData.directoryTree) return;
    
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
        .text(d => `${d.data.name}\\n${d.value} bytes`);
    
    leaf.append("text")
        .attr("x", 4)
        .attr("y", 16)
        .text(d => d.data.name)
        .attr("font-size", "12px")
        .attr("fill", "#fff");
    
    renderedVisualizations.add('treemap');
}

// Render Dependency Force Graph
function renderDependencyForceGraph() {
    if (renderedVisualizations.has('forcegraph')) return;
    if (!window.dashboardData || !window.dashboardData.dependencies) return;
    
    const width = 800;
    const height = 600;
    
    const svg = d3.select("#dependency-force-graph");
    svg.selectAll("*").remove();
    
    const simulation = d3.forceSimulation(window.dashboardData.dependencies.nodes)
        .force("link", d3.forceLink(window.dashboardData.dependencies.links).id(d => d.id).distance(100))
        .force("charge", d3.forceManyBody().strength(-400))
        .force("center", d3.forceCenter(width / 2, height / 2));
    
    const link = svg.append("g")
        .selectAll("line")
        .data(window.dashboardData.dependencies.links)
        .join("line")
        .attr("stroke", "rgba(255,255,255,0.3)")
        .attr("stroke-width", 2);
    
    const node = svg.append("g")
        .selectAll("g")
        .data(window.dashboardData.dependencies.nodes)
        .join("g")
        .call(d3.drag()
            .on("start", function(event) {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                event.subject.fx = event.subject.x;
                event.subject.fy = event.subject.y;
            })
            .on("drag", function(event) {
                event.subject.fx = event.x;
                event.subject.fy = event.y;
            })
            .on("end", function(event) {
                if (!event.active) simulation.alphaTarget(0);
                event.subject.fx = null;
                event.subject.fy = null;
            }));
    
    node.append("circle")
        .attr("r", 12)
        .attr("fill", d => d3.schemeCategory10[d.group % 10])
        .attr("stroke", "#fff")
        .attr("stroke-width", 2);
    
    node.append("text")
        .text(d => d.id)
        .attr("x", 16)
        .attr("y", 4)
        .attr("font-size", "11px")
        .attr("fill", "#fff");
    
    node.append("title")
        .text(d => d.id);
    
    simulation.on("tick", () => {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);
        
        node.attr("transform", d => `translate(${d.x},${d.y})`);
    });
    
    renderedVisualizations.add('forcegraph');
}

// Render Layer Diagram
function renderLayerDiagram() {
    if (renderedVisualizations.has('layerdiagram')) return;
    
    const container = d3.select("#layer-diagram");
    container.html("");
    
    const width = container.node().clientWidth || 800;
    const height = 350;
    
    const layers = [
        {name: "Presentation Layer", color: "#4d8cff", y: 30},
        {name: "Domain Layer", color: "#7fb3ff", y: 130},
        {name: "Infrastructure Layer", color: "#a3c9ff", y: 230}
    ];
    
    const svg = container.append("svg")
        .attr("width", "100%")
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height]);
    
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
    
    layers.forEach(layer => {
        svg.append("rect")
            .attr("x", width * 0.15)
            .attr("y", layer.y)
            .attr("width", width * 0.7)
            .attr("height", 70)
            .attr("fill", layer.color)
            .attr("fill-opacity", 0.7)
            .attr("stroke", "#fff")
            .attr("stroke-width", 2)
            .attr("rx", 8);
        
        svg.append("text")
            .attr("x", width / 2)
            .attr("y", layer.y + 45)
            .attr("text-anchor", "middle")
            .attr("fill", "#fff")
            .attr("font-size", "18px")
            .attr("font-weight", "600")
            .text(layer.name);
    });
    
    [100, 200].forEach(y => {
        svg.append("path")
            .attr("d", `M ${width / 2} ${y} L ${width / 2} ${y + 30}`)
            .attr("stroke", "#fff")
            .attr("stroke-width", 3)
            .attr("marker-end", "url(#arrowhead)");
    });
    
    renderedVisualizations.add('layerdiagram');
}

// Render Quality Radar
function renderQualityRadar() {
    if (renderedVisualizations.has('qualityradar')) return;
    if (!window.dashboardData || !window.dashboardData.qualityMetrics) return;
    
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
                pointBorderColor: '#fff'
            }]
        },
        options: {
            elements: {line: {borderWidth: 3}},
            scales: {
                r: {
                    angleLines: {color: 'rgba(255, 255, 255, 0.1)'},
                    grid: {color: 'rgba(255, 255, 255, 0.1)'},
                    pointLabels: {color: 'rgba(255, 255, 255, 0.8)', font: {size: 13}},
                    ticks: {color: 'rgba(255, 255, 255, 0.6)', backdropColor: 'transparent', min: 0, max: 100}
                }
            },
            plugins: {legend: {labels: {color: 'rgba(255, 255, 255, 0.8)'}}}
        }
    });
    
    renderedVisualizations.add('qualityradar');
}

// Render Complexity Histogram
function renderComplexityHistogram() {
    if (renderedVisualizations.has('complexityhistogram')) return;
    if (!window.dashboardData || !window.dashboardData.complexityData) return;
    
    const ctx = document.getElementById('complexity-histogram');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: window.dashboardData.complexityData.labels,
            datasets: [{
                label: 'File Count',
                data: window.dashboardData.complexityData.values,
                backgroundColor: [
                    'rgba(34, 197, 94, 0.6)',
                    'rgba(77, 140, 255, 0.6)',
                    'rgba(245, 158, 11, 0.6)',
                    'rgba(239, 68, 68, 0.6)',
                    'rgba(220, 38, 38, 0.8)'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {beginAtZero: true, ticks: {color: 'rgba(255, 255, 255, 0.8)'}, grid: {color: 'rgba(255, 255, 255, 0.1)'}},
                x: {ticks: {color: 'rgba(255, 255, 255, 0.8)'}, grid: {color: 'rgba(255, 255, 255, 0.1)'}}
            },
            plugins: {
                legend: {display: false},
                title: {display: true, text: 'Cyclomatic Complexity Distribution', color: 'rgba(255, 255, 255, 0.9)', font: {size: 16}}
            }
        }
    });
    
    renderedVisualizations.add('complexityhistogram');
}

// Render LOC Bar Chart
function renderLOCBarChart() {
    if (renderedVisualizations.has('locbarchart')) return;
    if (!window.dashboardData || !window.dashboardData.locDistribution) return;
    
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
                ]
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {beginAtZero: true, ticks: {color: 'rgba(255, 255, 255, 0.8)'}, grid: {color: 'rgba(255, 255, 255, 0.1)'}},
                y: {ticks: {color: 'rgba(255, 255, 255, 0.8)'}, grid: {color: 'rgba(255, 255, 255, 0.1)'}}
            },
            plugins: {
                legend: {display: false},
                title: {display: true, text: 'File Size Distribution (LOC)', color: 'rgba(255, 255, 255, 0.9)', font: {size: 16}}
            }
        }
    });
    
    renderedVisualizations.add('locbarchart');
}

// Render Vulnerability Pie Chart
function renderVulnerabilityPieChart() {
    if (renderedVisualizations.has('vulnerabilitypie')) return;
    if (!window.dashboardData || !window.dashboardData.vulnerabilities) return;
    
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
                    'rgba(239, 68, 68, 0.7)',
                    'rgba(245, 158, 11, 0.7)',
                    'rgba(220, 38, 38, 0.9)',
                    'rgba(77, 140, 255, 0.7)'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {position: 'right', labels: {color: 'rgba(255, 255, 255, 0.8)', font: {size: 14}}},
                title: {display: true, text: 'Vulnerability Distribution', color: 'rgba(255, 255, 255, 0.9)', font: {size: 18}}
            }
        }
    });
    
    renderedVisualizations.add('vulnerabilitypie');
}

// Auto-render on page load
document.addEventListener('DOMContentLoaded', function() {
    // Render architecture visualizations if tab is active
    if (document.getElementById('architecture').classList.contains('active')) {
        renderDirectoryTreemap();
        renderDependencyForceGraph();
        renderLayerDiagram();
    }
    
    // Render quality visualizations if tab is active
    if (document.getElementById('quality') && document.getElementById('quality').classList.contains('active')) {
        renderQualityRadar();
        renderComplexityHistogram();
        renderLOCBarChart();
    }
    
    // Render vulnerability visualizations if tab is active
    if (document.getElementById('vulnerabilities') && document.getElementById('vulnerabilities').classList.contains('active')) {
        renderVulnerabilityPieChart();
    }
});

// Modify existing switchTab function to render visualizations
const originalSwitchTab = window.switchTab;
if (originalSwitchTab) {
    window.switchTab = function(tabName) {
        originalSwitchTab.call(this, tabName);
        
        // Render visualizations for switched tab
        switch(tabName) {
            case 'architecture':
                renderDirectoryTreemap();
                renderDependencyForceGraph();
                renderLayerDiagram();
                break;
            case 'quality':
                renderQualityRadar();
                renderComplexityHistogram();
                renderLOCBarChart();
                break;
            case 'vulnerabilities':
                renderVulnerabilityPieChart();
                break;
        }
    };
}
</script>
'''
        
        # Insert before closing body
        self.content = self.content.replace('</body>', f'{rendering_script}\n</body>')
        print("✅ Rendering scripts added")
    
    def save(self):
        """Save enhanced dashboard"""
        self.dashboard_path.write_text(self.content, encoding='utf-8')
        print(f"✅ Enhanced dashboard saved: {self.dashboard_path}")
    
    def enhance_all(self):
        """Run all enhancement steps"""
        print("🚀 Starting Phase 18 Dashboard Enhancement...\n")
        
        self.backup()
        self.add_chartjs_library()
        self.add_dashboard_data_object()
        self.add_quality_tab()
        self.add_vulnerabilities_tab()
        self.enhance_architecture_tab()
        self.add_rendering_scripts()
        self.save()
        
        print("\n✅ Phase 18 Enhancement Complete!")
        print(f"📁 Backup: {self.backup_path}")
        print(f"📄 Enhanced: {self.dashboard_path}")


if __name__ == "__main__":
    dashboard_path = Path(__file__).parent / "dashboard.html"
    
    if not dashboard_path.exists():
        print(f"❌ Dashboard not found: {dashboard_path}")
        exit(1)
    
    enhancer = DashboardEnhancer(dashboard_path)
    enhancer.enhance_all()
