/**
 * CORTEX Lens - Chart Renderers
 * Initializes and manages Chart.js, D3.js, and ECharts visualizations
 */

class Charts {
    constructor() {
        this.charts = new Map();
        this.observedElements = new Set();
        this.setupIntersectionObserver();
    }

    /**
     * Setup lazy loading for charts using IntersectionObserver
     */
    setupIntersectionObserver() {
        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !this.observedElements.has(entry.target.id)) {
                    this.observedElements.add(entry.target.id);
                    const chartType = entry.target.dataset.chartType;
                    const chartId = entry.target.id;
                    
                    console.log(`📊 Lazy loading chart: ${chartId}`);
                    this.renderChart(chartId, chartType);
                }
            });
        }, { threshold: 0.1 });
    }

    /**
     * Observe chart container for lazy loading
     */
    observe(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            this.observer.observe(element);
        }
    }

    /**
     * Render chart based on type
     */
    async renderChart(elementId, chartType) {
        try {
            switch (chartType) {
                case 'health-radar':
                    await this.renderHealthRadar(elementId);
                    break;
                case 'layer-bar':
                    await this.renderLayerChart(elementId);
                    break;
                case 'complexity-line':
                    await this.renderComplexityChart(elementId);
                    break;
                case 'testing-pyramid':
                    await this.renderTestingPyramid(elementId);
                    break;
                case 'sankey':
                    await this.renderSankey(elementId);
                    break;
                case 'dependency-network':
                    await this.renderDependencyNetwork(elementId);
                    break;
                default:
                    console.warn(`Unknown chart type: ${chartType}`);
            }
        } catch (error) {
            console.error(`Error rendering chart ${elementId}:`, error);
            this.showChartError(elementId);
        }
    }

    /**
     * Render health radar chart (Chart.js)
     */
    async renderHealthRadar(elementId) {
        const canvas = document.getElementById(elementId);
        if (!canvas || !window.Chart) return;

        const data = dataAdapter.get('overview.health_metrics', {
            maintainability: 85,
            reliability: 90,
            security: 80,
            performance: 75,
            testability: 78
        });

        const ctx = canvas.getContext('2d');
        const chart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Maintainability', 'Reliability', 'Security', 'Performance', 'Testability'],
                datasets: [{
                    label: 'Health Metrics',
                    data: Object.values(data),
                    backgroundColor: 'rgba(88, 166, 255, 0.2)',
                    borderColor: 'rgba(88, 166, 255, 1)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgba(88, 166, 255, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(88, 166, 255, 1)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        pointLabels: { color: '#c9d1d9', font: { size: 12 } },
                        ticks: { 
                            backdropColor: 'transparent',
                            color: '#8b949e',
                            stepSize: 20
                        },
                        min: 0,
                        max: 100
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });

        this.charts.set(elementId, chart);
    }

    /**
     * Render layer architecture chart (Chart.js)
     */
    async renderLayerChart(elementId) {
        const canvas = document.getElementById(elementId);
        if (!canvas || !window.Chart) return;

        const ctx = canvas.getContext('2d');
        const chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Orchestration', 'Brain', 'Infrastructure', 'Tools', 'API'],
                datasets: [{
                    label: 'Files',
                    data: [45, 82, 38, 27, 15],
                    backgroundColor: 'rgba(88, 166, 255, 0.8)',
                    borderColor: 'rgba(88, 166, 255, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { 
                        beginAtZero: true,
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: '#8b949e' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#c9d1d9' }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });

        this.charts.set(elementId, chart);
    }

    /**
     * Render complexity trend chart (Chart.js)
     */
    async renderComplexityChart(elementId) {
        const canvas = document.getElementById(elementId);
        if (!canvas || !window.Chart) return;

        const ctx = canvas.getContext('2d');
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Complexity Score',
                    data: [7.8, 7.6, 7.4, 7.5, 7.3, 7.2],
                    borderColor: 'rgba(88, 166, 255, 1)',
                    backgroundColor: 'rgba(88, 166, 255, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { 
                        beginAtZero: false,
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: '#8b949e' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#c9d1d9' }
                    }
                },
                plugins: {
                    legend: { 
                        labels: { color: '#c9d1d9' }
                    }
                }
            }
        });

        this.charts.set(elementId, chart);
    }

    /**
     * Render testing pyramid (D3.js)
     */
    async renderTestingPyramid(elementId) {
        const container = document.getElementById(elementId);
        if (!container || !window.d3) return;

        const width = container.offsetWidth;
        const height = 400;

        const data = [
            { level: 'E2E Tests', count: 45, color: '#58a6ff' },
            { level: 'Integration', count: 120, color: '#79c0ff' },
            { level: 'Unit Tests', count: 340, color: '#a5d6ff' }
        ];

        const svg = d3.select(container)
            .append('svg')
            .attr('width', width)
            .attr('height', height);

        const pyramidWidth = Math.min(width * 0.8, 400);
        const levelHeight = height / data.length;

        data.forEach((d, i) => {
            const levelWidth = pyramidWidth * ((i + 1) / data.length);
            const x = (width - levelWidth) / 2;
            const y = i * levelHeight;

            svg.append('rect')
                .attr('x', x)
                .attr('y', y)
                .attr('width', levelWidth)
                .attr('height', levelHeight - 10)
                .attr('fill', d.color)
                .attr('rx', 4);

            svg.append('text')
                .attr('x', width / 2)
                .attr('y', y + levelHeight / 2 - 5)
                .attr('text-anchor', 'middle')
                .attr('fill', '#0d1117')
                .style('font-size', '14px')
                .style('font-weight', '600')
                .text(d.level);

            svg.append('text')
                .attr('x', width / 2)
                .attr('y', y + levelHeight / 2 + 15)
                .attr('text-anchor', 'middle')
                .attr('fill', '#0d1117')
                .style('font-size', '18px')
                .style('font-weight', 'bold')
                .text(d.count);
        });
    }

    /**
     * Render Sankey diagram (ECharts)
     */
    async renderSankey(elementId) {
        const container = document.getElementById(elementId);
        if (!container || !window.echarts) return;

        const chart = echarts.init(container, 'dark');
        
        const option = {
            series: {
                type: 'sankey',
                layout: 'none',
                emphasis: { focus: 'adjacency' },
                data: [
                    { name: 'User Request' },
                    { name: 'Orchestrator' },
                    { name: 'Brain' },
                    { name: 'Tools' },
                    { name: 'Response' }
                ],
                links: [
                    { source: 'User Request', target: 'Orchestrator', value: 100 },
                    { source: 'Orchestrator', target: 'Brain', value: 80 },
                    { source: 'Orchestrator', target: 'Tools', value: 20 },
                    { source: 'Brain', target: 'Response', value: 80 },
                    { source: 'Tools', target: 'Response', value: 20 }
                ]
            }
        };

        chart.setOption(option);
        this.charts.set(elementId, chart);
    }

    /**
     * Render dependency network (D3.js force simulation)
     */
    async renderDependencyNetwork(elementId) {
        const container = document.getElementById(elementId);
        if (!container || !window.d3) return;

        const width = container.offsetWidth;
        const height = 400;

        const nodes = [
            { id: 'cortex.orchestrators', group: 1 },
            { id: 'cortex.brain', group: 2 },
            { id: 'cortex.tools', group: 3 },
            { id: 'cortex.mcp', group: 1 }
        ];

        const links = [
            { source: 'cortex.orchestrators', target: 'cortex.brain' },
            { source: 'cortex.orchestrators', target: 'cortex.mcp' },
            { source: 'cortex.brain', target: 'cortex.tools' }
        ];

        const svg = d3.select(container)
            .append('svg')
            .attr('width', width)
            .attr('height', height);

        const color = d3.scaleOrdinal(d3.schemeCategory10);

        const simulation = d3.forceSimulation(nodes)
            .force('link', d3.forceLink(links).id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2));

        const link = svg.append('g')
            .selectAll('line')
            .data(links)
            .join('line')
            .attr('stroke', '#8b949e')
            .attr('stroke-width', 2);

        const node = svg.append('g')
            .selectAll('circle')
            .data(nodes)
            .join('circle')
            .attr('r', 10)
            .attr('fill', d => color(d.group));

        simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);

            node
                .attr('cx', d => d.x)
                .attr('cy', d => d.y);
        });
    }

    /**
     * Show error message in chart container
     */
    showChartError(elementId) {
        const container = document.getElementById(elementId);
        if (container) {
            container.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #8b949e;">
                    <p>❌ Failed to load chart</p>
                </div>
            `;
        }
    }

    /**
     * Destroy all charts
     */
    destroy() {
        this.charts.forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        this.charts.clear();
        this.observer.disconnect();
    }
}

// Global instance
const charts = new Charts();
