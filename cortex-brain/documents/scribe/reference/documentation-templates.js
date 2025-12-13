/**
 * CORTEX Documentation Templates Library
 * Reusable HTML/CSS/JS patterns for Phase 1 documentation generation
 * 
 * Author: Asif Hussain
 * Created: December 13, 2025
 * Purpose: Standardize documentation generation for cortex_scribe orchestrator
 */

/* ============================================
   HTML TEMPLATE: Feature Page Structure
   ============================================ */

// Base HTML Structure
const FEATURE_PAGE_TEMPLATE = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{FEATURE_NAME}} - CORTEX 3.0</title>
    <link rel="stylesheet" href="../assets/css/main.css">
    <link rel="icon" href="../assets/images/CORTEX-logo.png" type="image/png">
    <script src="https://d3js.org/d3.v7.min.js"></script>
</head>
<body>
    {{BREADCRUMB}}
    
    {{HERO_SECTION}}
    
    {{OVERVIEW_SECTION}}
    
    {{FEATURES_SECTION}}
    
    {{VISUALIZATION_SECTION}}
    
    {{USAGE_SECTION}}
    
    {{INTEGRATION_SECTION}}
    
    {{FAQ_SECTION}}
    
    {{FOOTER}}
    
    <script src="../assets/js/main.js"></script>
    <script src="../assets/js/{{FEATURE_JS}}"></script>
</body>
</html>
`;

/* ============================================
   COMPONENT: Breadcrumb Navigation
   ============================================ */

const BREADCRUMB_TEMPLATE = `
<nav class="breadcrumb">
    <a href="../index.html">Home</a>
    <span class="breadcrumb-separator">›</span>
    <a href="index.html">{{CATEGORY}}</a>
    <span class="breadcrumb-separator">›</span>
    <span class="breadcrumb-current">{{FEATURE_NAME}}</span>
</nav>
`;

/* ============================================
   COMPONENT: Hero Section with Metrics
   ============================================ */

const HERO_SECTION_TEMPLATE = `
<section class="section">
    <div class="container">
        <div class="glass-card">
            <div style="display: flex; align-items: center; gap: 2rem; margin-bottom: 2rem;">
                <div class="icon" style="font-size: 4rem;">{{ICON}}</div>
                <div>
                    <h1 style="margin-bottom: 0.5rem;">{{FEATURE_NAME}}</h1>
                    <p style="color: var(--text-secondary); font-size: 1.25rem; margin: 0;">
                        {{TAGLINE}}
                    </p>
                </div>
            </div>

            <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); margin-top: 2rem;">
                {{METRICS_CARDS}}
            </div>
        </div>
    </div>
</section>
`;

const METRIC_CARD_TEMPLATE = `
<div class="metric-card">
    <div class="metric-value">{{VALUE}}</div>
    <div class="metric-label">{{LABEL}}</div>
    <div class="metric-sublabel">{{SUBLABEL}}</div>
</div>
`;

/* ============================================
   COMPONENT: Overview Section
   ============================================ */

const OVERVIEW_SECTION_TEMPLATE = `
<section class="section" style="padding-top: 0;">
    <div class="container">
        <h2>Overview</h2>
        <div class="glass-card">
            <p style="font-size: 1.125rem; line-height: 1.8; color: var(--text-secondary);">
                {{OVERVIEW_TEXT}}
            </p>
        </div>
    </div>
</section>
`;

/* ============================================
   COMPONENT: Collapsible Section
   ============================================ */

const COLLAPSIBLE_TEMPLATE = `
<div class="collapsible">
    <button class="collapsible-header">
        <span>{{TITLE}}</span>
        <span class="collapsible-icon">▼</span>
    </button>
    <div class="collapsible-content">
        {{CONTENT}}
    </div>
</div>
`;

/* ============================================
   COMPONENT: D3.js Visualization Container
   ============================================ */

const D3_CONTAINER_TEMPLATE = `
<section class="section">
    <div class="container">
        <h2>{{VISUALIZATION_TITLE}}</h2>
        <div class="glass-card">
            <div id="{{VISUALIZATION_ID}}" style="min-height: 400px; position: relative;">
                <!-- D3.js visualization will be injected here -->
            </div>
        </div>
    </div>
</section>
`;

/* ============================================
   D3.js: Phase Flow Visualization
   ============================================ */

const D3_PHASE_FLOW = `
function renderPhaseFlow(containerId, phases) {
    const container = d3.select('#' + containerId);
    const width = container.node().getBoundingClientRect().width;
    const height = 400;
    
    const svg = container.append('svg')
        .attr('width', width)
        .attr('height', height);
    
    const phaseWidth = (width - 100) / phases.length;
    const phaseHeight = 120;
    
    // Draw phases
    phases.forEach((phase, i) => {
        const x = 50 + (i * phaseWidth);
        const y = height / 2 - phaseHeight / 2;
        
        // Phase box with glassmorphism
        const phaseGroup = svg.append('g')
            .attr('class', 'phase-box')
            .attr('transform', \`translate(\${x}, \${y})\`);
        
        phaseGroup.append('rect')
            .attr('width', phaseWidth - 20)
            .attr('height', phaseHeight)
            .attr('rx', 12)
            .attr('fill', 'rgba(26, 31, 58, 0.7)')
            .attr('stroke', phase.status === 'complete' ? '#00ff88' : '#00d4ff')
            .attr('stroke-width', 2)
            .style('backdrop-filter', 'blur(10px)');
        
        // Phase number
        phaseGroup.append('text')
            .attr('x', (phaseWidth - 20) / 2)
            .attr('y', 30)
            .attr('text-anchor', 'middle')
            .attr('fill', '#00d4ff')
            .attr('font-size', '24px')
            .attr('font-weight', 'bold')
            .text(\`Phase \${i + 1}\`);
        
        // Phase title
        phaseGroup.append('text')
            .attr('x', (phaseWidth - 20) / 2)
            .attr('y', 60)
            .attr('text-anchor', 'middle')
            .attr('fill', '#ffffff')
            .attr('font-size', '14px')
            .text(phase.title);
        
        // Status indicator
        phaseGroup.append('circle')
            .attr('cx', (phaseWidth - 20) / 2)
            .attr('cy', 90)
            .attr('r', 8)
            .attr('fill', phase.status === 'complete' ? '#00ff88' : 
                         phase.status === 'in-progress' ? '#ffa500' : '#6b7280');
        
        // Arrow to next phase
        if (i < phases.length - 1) {
            svg.append('path')
                .attr('d', \`M \${x + phaseWidth - 20} \${y + phaseHeight / 2} 
                           L \${x + phaseWidth} \${y + phaseHeight / 2}\`)
                .attr('stroke', '#00d4ff')
                .attr('stroke-width', 2)
                .attr('marker-end', 'url(#arrowhead)');
        }
    });
    
    // Arrow marker definition
    svg.append('defs').append('marker')
        .attr('id', 'arrowhead')
        .attr('markerWidth', 10)
        .attr('markerHeight', 10)
        .attr('refX', 5)
        .attr('refY', 3)
        .attr('orient', 'auto')
        .append('polygon')
        .attr('points', '0 0, 10 3, 0 6')
        .attr('fill', '#00d4ff');
}
`;

/* ============================================
   D3.js: Metrics Dashboard
   ============================================ */

const D3_METRICS_DASHBOARD = `
function renderMetricsDashboard(containerId, metrics) {
    const container = d3.select('#' + containerId);
    const width = container.node().getBoundingClientRect().width;
    const height = 300;
    
    const svg = container.append('svg')
        .attr('width', width)
        .attr('height', height);
    
    const gridSize = Math.floor(width / metrics.length);
    
    metrics.forEach((metric, i) => {
        const x = i * gridSize + gridSize / 2;
        const y = height / 2;
        const radius = Math.min(gridSize / 3, 60);
        
        // Outer ring (progress)
        const arc = d3.arc()
            .innerRadius(radius - 10)
            .outerRadius(radius)
            .startAngle(0)
            .endAngle((metric.value / metric.max) * 2 * Math.PI);
        
        svg.append('path')
            .attr('d', arc)
            .attr('transform', \`translate(\${x}, \${y})\`)
            .attr('fill', metric.color || '#00d4ff')
            .attr('opacity', 0.7);
        
        // Value text
        svg.append('text')
            .attr('x', x)
            .attr('y', y)
            .attr('text-anchor', 'middle')
            .attr('fill', '#ffffff')
            .attr('font-size', '24px')
            .attr('font-weight', 'bold')
            .text(metric.value + (metric.unit || ''));
        
        // Label
        svg.append('text')
            .attr('x', x)
            .attr('y', y + radius + 30)
            .attr('text-anchor', 'middle')
            .attr('fill', '#a0a6c0')
            .attr('font-size', '12px')
            .text(metric.label);
    });
}
`;

/* ============================================
   D3.js: Architecture Diagram
   ============================================ */

const D3_ARCHITECTURE_DIAGRAM = `
function renderArchitecture(containerId, components) {
    const container = d3.select('#' + containerId);
    const width = container.node().getBoundingClientRect().width;
    const height = 500;
    
    const svg = container.append('svg')
        .attr('width', width)
        .attr('height', height);
    
    const layers = d3.group(components, d => d.layer);
    const layerHeight = height / layers.size;
    
    let layerIndex = 0;
    layers.forEach((comps, layerName) => {
        const y = layerIndex * layerHeight;
        const compWidth = (width - 100) / comps.length;
        
        // Layer background
        svg.append('rect')
            .attr('x', 25)
            .attr('y', y + 10)
            .attr('width', width - 50)
            .attr('height', layerHeight - 20)
            .attr('fill', 'rgba(26, 31, 58, 0.3)')
            .attr('stroke', '#00d4ff')
            .attr('stroke-width', 1)
            .attr('rx', 8);
        
        // Layer label
        svg.append('text')
            .attr('x', 40)
            .attr('y', y + 35)
            .attr('fill', '#00d4ff')
            .attr('font-size', '14px')
            .attr('font-weight', 'bold')
            .text(layerName);
        
        // Components
        comps.forEach((comp, i) => {
            const x = 50 + (i * compWidth) + compWidth / 2;
            const cy = y + layerHeight / 2;
            
            // Component box
            svg.append('rect')
                .attr('x', x - 60)
                .attr('y', cy - 30)
                .attr('width', 120)
                .attr('height', 60)
                .attr('fill', 'rgba(123, 97, 255, 0.2)')
                .attr('stroke', comp.status === 'active' ? '#7b61ff' : '#6b7280')
                .attr('stroke-width', 2)
                .attr('rx', 8);
            
            // Component name
            svg.append('text')
                .attr('x', x)
                .attr('y', cy + 5)
                .attr('text-anchor', 'middle')
                .attr('fill', '#ffffff')
                .attr('font-size', '12px')
                .text(comp.name);
        });
        
        layerIndex++;
    });
}
`;

/* ============================================
   COMPONENT: Code Example with Syntax Highlighting
   ============================================ */

const CODE_EXAMPLE_TEMPLATE = `
<div class="glass-card" style="margin-top: 2rem;">
    <h3 style="margin-bottom: 1rem;">{{EXAMPLE_TITLE}}</h3>
    <pre style="background: rgba(0, 0, 0, 0.5); padding: 1.5rem; border-radius: 8px; overflow-x: auto;"><code class="language-{{LANGUAGE}}">{{CODE}}</code></pre>
    <p style="margin-top: 1rem; color: var(--text-secondary);">{{EXPLANATION}}</p>
</div>
`;

/* ============================================
   COMPONENT: Feature Grid
   ============================================ */

const FEATURE_GRID_TEMPLATE = `
<div class="feature-grid" style="grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin-top: 2rem;">
    {{FEATURE_CARDS}}
</div>
`;

const FEATURE_CARD_TEMPLATE = `
<div class="glass-card feature-card">
    <div class="icon">{{ICON}}</div>
    <h3>{{TITLE}}</h3>
    <p>{{DESCRIPTION}}</p>
    {{CTA_BUTTON}}
</div>
`;

/* ============================================
   COMPONENT: Status Badge
   ============================================ */

const STATUS_BADGE_TEMPLATES = {
    complete: '<span class="badge badge-success">✅ Production Ready</span>',
    in_progress: '<span class="badge badge-warning">🔧 In Development</span>',
    planned: '<span class="badge badge-info">📋 Planned</span>',
    experimental: '<span class="badge" style="background: rgba(255, 165, 0, 0.2); color: #ffa500;">🧪 Experimental</span>'
};

/* ============================================
   COMPONENT: Quick Stats Bar
   ============================================ */

const QUICK_STATS_TEMPLATE = `
<div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 1rem; padding: 1.5rem; background: rgba(0, 212, 255, 0.05); border-radius: 12px; margin-top: 2rem;">
    {{STATS}}
</div>
`;

const STAT_ITEM_TEMPLATE = `
<div style="text-align: center;">
    <div style="font-size: 2rem; font-weight: bold; color: var(--accent-primary);">{{VALUE}}</div>
    <div style="color: var(--text-secondary); font-size: 0.9rem;">{{LABEL}}</div>
</div>
`;

/* ============================================
   DOCUMENTATION GENERATION PATTERNS
   ============================================ */

const DOC_PATTERNS = {
    // Feature documentation structure
    feature: {
        sections: [
            'hero',
            'overview',
            'key-features',
            'visualization',
            'usage-examples',
            'integration',
            'configuration',
            'best-practices',
            'troubleshooting',
            'faq',
            'related-features'
        ],
        required_visualizations: 1,
        required_examples: 2
    },
    
    // Orchestrator documentation structure
    orchestrator: {
        sections: [
            'hero',
            'overview',
            'architecture',
            'workflow-visualization',
            'phases',
            'integration-points',
            'configuration',
            'usage-examples',
            'monitoring',
            'troubleshooting'
        ],
        required_visualizations: 2,
        required_examples: 3
    },
    
    // Capability documentation structure
    capability: {
        sections: [
            'hero',
            'overview',
            'supported-languages',
            'usage-examples',
            'configuration',
            'integration',
            'best-practices',
            'limitations'
        ],
        required_visualizations: 1,
        required_examples: 4
    }
};

/* ============================================
   FOLDER STRUCTURE CONVENTIONS
   ============================================ */

const FOLDER_STRUCTURE = {
    features: 'docs/features/',
    orchestration: 'docs/orchestration/',
    architecture: 'docs/architecture/',
    future: 'docs/future/',
    assets: {
        css: 'docs/assets/css/',
        js: 'docs/assets/js/',
        images: 'docs/assets/images/'
    }
};

/* ============================================
   NAVIGATION STRUCTURE
   ============================================ */

const NAV_CATEGORIES = {
    'Features': 'features',
    'Orchestrators': 'orchestration',
    'Architecture': 'architecture',
    'Future Vision': 'future'
};

/* ============================================
   EXPORT FOR CORTEX_SCRIBE ORCHESTRATOR
   ============================================ */

module.exports = {
    templates: {
        FEATURE_PAGE_TEMPLATE,
        BREADCRUMB_TEMPLATE,
        HERO_SECTION_TEMPLATE,
        METRIC_CARD_TEMPLATE,
        OVERVIEW_SECTION_TEMPLATE,
        COLLAPSIBLE_TEMPLATE,
        D3_CONTAINER_TEMPLATE,
        CODE_EXAMPLE_TEMPLATE,
        FEATURE_GRID_TEMPLATE,
        FEATURE_CARD_TEMPLATE,
        QUICK_STATS_TEMPLATE,
        STAT_ITEM_TEMPLATE
    },
    d3: {
        D3_PHASE_FLOW,
        D3_METRICS_DASHBOARD,
        D3_ARCHITECTURE_DIAGRAM
    },
    patterns: DOC_PATTERNS,
    structure: FOLDER_STRUCTURE,
    navigation: NAV_CATEGORIES,
    badges: STATUS_BADGE_TEMPLATES
};
