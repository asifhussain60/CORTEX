/**
 * Package Health Dashboard Component
 * 
 * Displays package count distribution across projects with outlier detection.
 * Uses D3.js for interactive bar charts with color-coded health indicators.
 * 
 * Data Source: tech-stack.json → backend[].metadata.projects[].packages
 * 
 * Features:
 * - Horizontal bar chart showing package counts per project
 * - Average line overlay
 * - Outlier detection (>1.5x avg = warning, >2x = critical)
 * - Color-coded bars (green/yellow/orange/red)
 * - Detailed project cards for outliers
 */

class PackageHealthDashboard {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.projects = [];
        this.statistics = {};
        
        // Chart dimensions
        this.margin = { top: 20, right: 30, bottom: 40, left: 200 };
        this.width = 800 - this.margin.left - this.margin.right;
        this.height = 600 - this.margin.top - this.margin.bottom;
    }

    /**
     * Initialize dashboard with tech stack data
     * @param {Object} techStackData - Full tech-stack.json data
     */
    init(techStackData) {
        this.projects = this.extractProjects(techStackData);
        this.statistics = this.calculateStatistics(this.projects);
        this.render();
    }

    /**
     * Extract projects with package counts from tech stack data
     * @param {Object} techStackData - Tech stack JSON
     * @returns {Array} Array of project objects with package counts
     */
    extractProjects(techStackData) {
        const projects = [];
        
        if (!techStackData || !techStackData.backend) {
            return projects;
        }

        techStackData.backend.forEach(tech => {
            if (tech.metadata && tech.metadata.projects) {
                tech.metadata.projects.forEach(project => {
                    if (project.packages !== undefined) {
                        projects.push({
                            name: project.name,
                            packages: project.packages,
                            type: project.type || 'Unknown',
                            path: project.path
                        });
                    }
                });
            }
        });

        // Sort by package count descending
        return projects.sort((a, b) => b.packages - a.packages);
    }

    /**
     * Calculate statistical measures
     * @param {Array} projects - Array of project objects
     * @returns {Object} Statistics (mean, median, stdDev, outliers)
     */
    calculateStatistics(projects) {
        if (projects.length === 0) {
            return { mean: 0, median: 0, stdDev: 0, outliers: [] };
        }

        const packageCounts = projects.map(p => p.packages);
        
        // Mean
        const mean = packageCounts.reduce((sum, count) => sum + count, 0) / packageCounts.length;
        
        // Median
        const sorted = [...packageCounts].sort((a, b) => a - b);
        const mid = Math.floor(sorted.length / 2);
        const median = sorted.length % 2 === 0 
            ? (sorted[mid - 1] + sorted[mid]) / 2 
            : sorted[mid];
        
        // Standard deviation
        const variance = packageCounts.reduce((sum, count) => 
            sum + Math.pow(count - mean, 2), 0) / packageCounts.length;
        const stdDev = Math.sqrt(variance);
        
        // Outlier detection (>1.5x mean = warning, >2x mean = critical)
        const outliers = projects.filter(p => p.packages > mean * 1.5).map(p => ({
            ...p,
            severity: p.packages > mean * 2 ? 'critical' : 'warning',
            percentAboveMean: ((p.packages - mean) / mean * 100).toFixed(1)
        }));

        return { mean, median, stdDev, outliers };
    }

    /**
     * Get color class based on package count relative to average
     * @param {number} packageCount - Project package count
     * @param {number} average - Average package count
     * @returns {string} Color class name
     */
    getHealthColor(packageCount, average) {
        if (packageCount > average * 2) return 'health-critical';     // Red
        if (packageCount > average * 1.5) return 'health-warning';    // Orange
        if (packageCount > average) return 'health-caution';          // Yellow
        return 'health-good';                                          // Green
    }

    /**
     * Render the dashboard
     */
    render() {
        if (!this.container) return;

        this.container.innerHTML = `
            <div class="package-health-dashboard">
                <!-- Statistics Summary -->
                <div class="health-summary">
                    <h3>Package Distribution Analysis</h3>
                    <div class="summary-cards">
                        <div class="summary-card">
                            <div class="summary-label">Total Projects</div>
                            <div class="summary-value">${this.projects.length}</div>
                        </div>
                        <div class="summary-card">
                            <div class="summary-label">Average Packages</div>
                            <div class="summary-value">${Math.round(this.statistics.mean)}</div>
                        </div>
                        <div class="summary-card">
                            <div class="summary-label">Median</div>
                            <div class="summary-value">${Math.round(this.statistics.median)}</div>
                        </div>
                        <div class="summary-card ${this.statistics.outliers.length > 0 ? 'warning' : ''}">
                            <div class="summary-label">Outliers</div>
                            <div class="summary-value">${this.statistics.outliers.length}</div>
                        </div>
                    </div>
                </div>

                <!-- Chart Container -->
                <div class="chart-container">
                    <svg id="package-health-chart"></svg>
                </div>

                <!-- Outliers Section -->
                ${this.statistics.outliers.length > 0 ? this.renderOutliers() : ''}
            </div>
        `;

        // Render D3.js chart
        this.renderChart();
    }

    /**
     * Render D3.js bar chart
     */
    renderChart() {
        const svg = d3.select('#package-health-chart')
            .attr('width', this.width + this.margin.left + this.margin.right)
            .attr('height', this.height + this.margin.top + this.margin.bottom);

        // Clear existing content
        svg.selectAll('*').remove();

        const g = svg.append('g')
            .attr('transform', `translate(${this.margin.left},${this.margin.top})`);

        // Scales
        const x = d3.scaleLinear()
            .domain([0, d3.max(this.projects, d => d.packages) * 1.1])
            .range([0, this.width]);

        const y = d3.scaleBand()
            .domain(this.projects.map(d => d.name))
            .range([0, this.height])
            .padding(0.1);

        // Bars
        g.selectAll('.bar')
            .data(this.projects)
            .enter().append('rect')
            .attr('class', d => `bar ${this.getHealthColor(d.packages, this.statistics.mean)}`)
            .attr('x', 0)
            .attr('y', d => y(d.name))
            .attr('width', d => x(d.packages))
            .attr('height', y.bandwidth())
            .attr('rx', 3)
            .on('mouseover', (event, d) => this.showTooltip(event, d))
            .on('mouseout', () => this.hideTooltip());

        // Average line
        const avgLine = g.append('line')
            .attr('class', 'average-line')
            .attr('x1', x(this.statistics.mean))
            .attr('x2', x(this.statistics.mean))
            .attr('y1', 0)
            .attr('y2', this.height)
            .attr('stroke', '#2c3e50')
            .attr('stroke-width', 2)
            .attr('stroke-dasharray', '5,5');

        // Average label
        g.append('text')
            .attr('class', 'average-label')
            .attr('x', x(this.statistics.mean) + 5)
            .attr('y', -5)
            .text(`Avg: ${Math.round(this.statistics.mean)}`)
            .attr('font-size', '12px')
            .attr('fill', '#2c3e50');

        // X axis
        g.append('g')
            .attr('class', 'x-axis')
            .attr('transform', `translate(0,${this.height})`)
            .call(d3.axisBottom(x).ticks(10));

        // Y axis
        g.append('g')
            .attr('class', 'y-axis')
            .call(d3.axisLeft(y));

        // X axis label
        g.append('text')
            .attr('class', 'axis-label')
            .attr('x', this.width / 2)
            .attr('y', this.height + 35)
            .attr('text-anchor', 'middle')
            .text('Number of Packages');

        // Tooltip
        this.tooltip = d3.select('body').append('div')
            .attr('class', 'package-health-tooltip')
            .style('opacity', 0)
            .style('position', 'absolute')
            .style('background', 'white')
            .style('border', '1px solid #ccc')
            .style('border-radius', '4px')
            .style('padding', '8px')
            .style('pointer-events', 'none');
    }

    /**
     * Show tooltip on bar hover
     * @param {Event} event - Mouse event
     * @param {Object} data - Project data
     */
    showTooltip(event, data) {
        const percentAbove = ((data.packages - this.statistics.mean) / this.statistics.mean * 100).toFixed(1);
        const status = data.packages > this.statistics.mean 
            ? `${percentAbove}% above average` 
            : `${Math.abs(percentAbove)}% below average`;

        this.tooltip.transition().duration(200).style('opacity', 0.9);
        this.tooltip.html(`
            <strong>${data.name}</strong><br/>
            Packages: ${data.packages}<br/>
            Type: ${data.type}<br/>
            ${status}
        `)
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 28) + 'px');
    }

    /**
     * Hide tooltip
     */
    hideTooltip() {
        this.tooltip.transition().duration(500).style('opacity', 0);
    }

    /**
     * Render outliers section
     * @returns {string} HTML for outliers
     */
    renderOutliers() {
        return `
            <div class="outliers-section">
                <h4>⚠️ Projects Requiring Attention (${this.statistics.outliers.length})</h4>
                <div class="outliers-grid">
                    ${this.statistics.outliers.map(outlier => `
                        <div class="outlier-card ${outlier.severity}">
                            <div class="outlier-header">
                                <h5>${outlier.name}</h5>
                                <span class="severity-badge ${outlier.severity}">
                                    ${outlier.severity === 'critical' ? 'CRITICAL' : 'WARNING'}
                                </span>
                            </div>
                            <div class="outlier-details">
                                <div class="detail-row">
                                    <span class="label">Packages:</span>
                                    <span class="value">${outlier.packages}</span>
                                </div>
                                <div class="detail-row">
                                    <span class="label">Above Average:</span>
                                    <span class="value">+${outlier.percentAboveMean}%</span>
                                </div>
                                <div class="detail-row">
                                    <span class="label">Type:</span>
                                    <span class="value">${outlier.type}</span>
                                </div>
                            </div>
                            <div class="recommendation">
                                <strong>Recommendation:</strong> Review dependencies for unused packages, 
                                consolidate overlapping libraries, consider package bloat impact on build time.
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PackageHealthDashboard;
}
