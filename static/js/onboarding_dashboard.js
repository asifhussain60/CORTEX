/**
 * CORTEX Onboarding Dashboard - Main JavaScript Controller
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025
 * Repository: https://github.com/asifhussain60/CORTEX
 */

// ========== Global State ==========
let dashboardState = {
    currentTab: 'overview',
    dashboardData: null,
    filters: {
        language: 'all',
        minHealth: 0,
        severity: 'all'
    },
    charts: {}
};

// ========== Initialization ==========
function initializeDashboard(data) {
    console.log('Initializing CORTEX Dashboard...');
    dashboardState.dashboardData = data;
    
    // Setup tab navigation
    setupTabNavigation();
    
    // Initialize all tabs
    initializeOverviewTab(data);
    initializeArchitectureTab(data);
    initializeQualityTab(data);
    initializeSecurityTab(data);
    initializeRecommendationsTab(data);
    
    // Setup export handlers
    setupExportHandlers();
    
    console.log('Dashboard initialized successfully');
}

// ========== Tab Navigation ==========
function setupTabNavigation() {
    const tabButtons = document.querySelectorAll('.tab-button');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.getAttribute('data-tab');
            switchTab(tabId);
        });
    });
}

function switchTab(tabId) {
    // Update button states
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
    
    // Update content visibility
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabId}-tab`).classList.add('active');
    
    // Update state
    dashboardState.currentTab = tabId;
    
    // Trigger tab-specific initialization if needed
    switch(tabId) {
        case 'architecture':
            renderArchitectureGraph();
            break;
        case 'quality':
            updateQualityCharts();
            break;
        case 'security':
            updateSecurityView();
            break;
    }
}

// ========== Overview Tab ==========
function initializeOverviewTab(data) {
    // Initialize language chart
    if (data.languages && data.languages.length > 0) {
        createLanguageChart(data.languages);
    }
}

function createLanguageChart(languages) {
    const ctx = document.getElementById('language-chart');
    if (!ctx) return;
    
    dashboardState.charts.languageChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: languages.map(l => l.name),
            datasets: [{
                data: languages.map(l => l.percentage),
                backgroundColor: languages.map(l => l.color || generateColor()),
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: { size: 12 }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            return `${label}: ${value.toFixed(1)}%`;
                        }
                    }
                }
            }
        }
    });
}

// ========== Architecture Tab ==========
function initializeArchitectureTab(data) {
    if (data.architecture_nodes && data.architecture_edges) {
        renderArchitectureGraph();
    }
}

function renderArchitectureGraph() {
    const svg = d3.select('#dependency-svg');
    const width = svg.node().getBoundingClientRect().width;
    const height = 600;
    
    // Clear existing content
    svg.selectAll('*').remove();
    
    const data = dashboardState.dashboardData;
    if (!data.architecture_nodes || data.architecture_nodes.length === 0) {
        svg.append('text')
            .attr('x', width / 2)
            .attr('y', height / 2)
            .attr('text-anchor', 'middle')
            .attr('fill', '#9ca3af')
            .text('No architecture data available');
        return;
    }
    
    // Create force simulation
    const simulation = d3.forceSimulation(data.architecture_nodes)
        .force('link', d3.forceLink(data.architecture_edges).id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(30));
    
    // Create zoom behavior
    const zoom = d3.zoom()
        .scaleExtent([0.1, 4])
        .on('zoom', (event) => {
            g.attr('transform', event.transform);
        });
    
    svg.call(zoom);
    
    const g = svg.append('g');
    
    // Draw edges
    const link = g.append('g')
        .selectAll('line')
        .data(data.architecture_edges)
        .join('line')
        .attr('stroke', '#d1d5db')
        .attr('stroke-width', 2)
        .attr('stroke-opacity', 0.6);
    
    // Draw nodes
    const node = g.append('g')
        .selectAll('circle')
        .data(data.architecture_nodes)
        .join('circle')
        .attr('r', 8)
        .attr('fill', d => getHealthColor(d.health_score))
        .attr('stroke', '#ffffff')
        .attr('stroke-width', 2)
        .style('cursor', 'pointer')
        .call(drag(simulation))
        .on('click', (event, d) => showComponentDetails(d))
        .on('mouseover', (event, d) => showTooltip(event, d))
        .on('mouseout', hideTooltip);
    
    // Add labels
    const label = g.append('g')
        .selectAll('text')
        .data(data.architecture_nodes)
        .join('text')
        .text(d => d.name)
        .attr('font-size', 10)
        .attr('dx', 12)
        .attr('dy', 4)
        .style('pointer-events', 'none');
    
    // Update positions on each tick
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
        
        label
            .attr('x', d => d.x)
            .attr('y', d => d.y);
    });
}

function drag(simulation) {
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
    
    return d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended);
}

function showComponentDetails(component) {
    const panel = document.getElementById('component-details');
    const nameEl = document.getElementById('component-name');
    const metricsEl = document.getElementById('component-metrics');
    const depsEl = document.getElementById('component-dependencies');
    const issuesEl = document.getElementById('component-issues');
    
    nameEl.textContent = component.name;
    metricsEl.innerHTML = `
        <p>Health Score: <strong>${component.health_score}%</strong></p>
        <p>LOC: <strong>${component.loc || 'N/A'}</strong></p>
        <p>Complexity: <strong>${component.complexity || 'N/A'}</strong></p>
    `;
    
    depsEl.innerHTML = component.dependencies 
        ? `<ul>${component.dependencies.map(d => `<li>${d}</li>`).join('')}</ul>`
        : '<p>No dependencies</p>';
    
    issuesEl.innerHTML = component.issues 
        ? `<ul>${component.issues.map(i => `<li>${i}</li>`).join('')}</ul>`
        : '<p>No issues</p>';
    
    panel.style.display = 'block';
}

function closeComponentDetails() {
    document.getElementById('component-details').style.display = 'none';
}

function updateArchitectureGraph() {
    // Reapply filters and re-render
    const language = document.getElementById('filter-language').value;
    const minHealth = parseInt(document.getElementById('min-health').value);
    
    dashboardState.filters.language = language;
    dashboardState.filters.minHealth = minHealth;
    
    renderArchitectureGraph();
}

function resetArchitectureView() {
    document.getElementById('filter-language').value = 'all';
    document.getElementById('min-health').value = 0;
    document.getElementById('health-value').textContent = '0%';
    updateArchitectureGraph();
}

// ========== Quality Tab ==========
function initializeQualityTab(data) {
    if (document.getElementById('quality-gauge')) {
        createQualityGauge(data.quality_score || 0);
    }
    
    if (document.getElementById('complexity-chart')) {
        createComplexityChart(data.complexity_data || []);
    }
    
    if (document.getElementById('coverage-chart')) {
        createCoverageChart(data);
    }
}

function createQualityGauge(score) {
    const ctx = document.getElementById('quality-gauge');
    if (!ctx) return;
    
    dashboardState.charts.qualityGauge = new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [score, 100 - score],
                backgroundColor: [getHealthColor(score), '#e5e7eb'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '75%',
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false }
            }
        }
    });
}

function updateQualityCharts() {
    // Refresh charts if needed
    Object.values(dashboardState.charts).forEach(chart => {
        if (chart && chart.update) chart.update();
    });
}

// ========== Security Tab ==========
function initializeSecurityTab(data) {
    setupSecurityFilters();
}

function setupSecurityFilters() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    
    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            filterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            const filter = btn.getAttribute('data-filter');
            filterVulnerabilities(filter);
        });
    });
}

function filterVulnerabilities(severity) {
    const vulnItems = document.querySelectorAll('.vuln-item');
    
    vulnItems.forEach(item => {
        if (severity === 'all' || item.getAttribute('data-severity') === severity) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

function updateSecurityView() {
    // Update security tab view if needed
}

// ========== Recommendations Tab ==========
function initializeRecommendationsTab(data) {
    // Recommendations are rendered server-side
}

// ========== Export Functions ==========
function setupExportHandlers() {
    // Export handlers will be connected to buttons
}

function exportDashboard(format) {
    showLoading('Exporting dashboard...');
    
    setTimeout(() => {
        switch(format) {
            case 'pdf':
                exportToPDF();
                break;
            case 'png':
                exportToPNG();
                break;
            default:
                console.warn('Unknown export format:', format);
        }
        hideLoading();
    }, 500);
}

function exportToPDF() {
    window.print();
}

function exportToPNG() {
    html2canvas(document.querySelector('.dashboard-container')).then(canvas => {
        const link = document.createElement('a');
        link.download = 'cortex-dashboard.png';
        link.href = canvas.toDataURL();
        link.click();
    });
}

function refreshDashboard() {
    showLoading('Refreshing dashboard...');
    location.reload();
}

// ========== Utility Functions ==========
function getHealthColor(score) {
    if (score >= 80) return '#10b981'; // green
    if (score >= 60) return '#84cc16'; // lime
    if (score >= 40) return '#f59e0b'; // amber
    if (score >= 20) return '#f97316'; // orange
    return '#ef4444'; // red
}

function generateColor() {
    const colors = ['#3b82f6', '#6366f1', '#8b5cf6', '#d946ef', '#ec4899', '#f43f5e'];
    return colors[Math.floor(Math.random() * colors.length)];
}

function formatNumber(num) {
    return num.toLocaleString();
}

function showLoading(message) {
    const overlay = document.getElementById('loading-overlay');
    const messageEl = overlay.querySelector('.loading-message');
    messageEl.textContent = message;
    overlay.style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading-overlay').style.display = 'none';
}

function showTooltip(event, data) {
    // Implement tooltip display
}

function hideTooltip() {
    // Implement tooltip hide
}

// ========== Event Listeners ==========
document.addEventListener('DOMContentLoaded', () => {
    console.log('CORTEX Dashboard script loaded');
});

// ========== Keyboard Shortcuts ==========
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Number: Switch tabs
    if ((e.ctrlKey || e.metaKey) && e.key >= '1' && e.key <= '5') {
        e.preventDefault();
        const tabs = ['overview', 'architecture', 'quality', 'security', 'recommendations'];
        const tabIndex = parseInt(e.key) - 1;
        if (tabs[tabIndex]) {
            switchTab(tabs[tabIndex]);
        }
    }
});
