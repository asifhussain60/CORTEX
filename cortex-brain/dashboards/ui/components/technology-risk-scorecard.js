/**
 * Technology Risk Scorecard Component
 * D3.js scatter plot + sortable table for technology risk assessment
 * Features: Risk matrix, priority queue, filtering, sorting
 */

class TechnologyRiskScorecard {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        
        // Configuration
        this.width = options.width || 800;
        this.height = options.height || 500;
        this.margin = options.margin || {top: 40, right: 40, bottom: 60, left: 60};
        
        // State
        this.data = [];
        this.filteredData = [];
        this.sortColumn = 'risk_score';
        this.sortDirection = 'desc';
        this.filterLevel = 'all'; // 'all', 'critical', 'high', 'medium'
        
        // Risk thresholds
        this.thresholds = {
            low: 30,
            medium: 60,
            high: 100
        };
        
        this.initialize();
    }
    
    initialize() {
        // Create container structure
        this.container.innerHTML = `
            <div class="risk-scorecard">
                <div class="scorecard-header">
                    <h3>Technology Risk Assessment</h3>
                    <div class="filter-controls">
                        <button class="filter-btn active" data-filter="all">All</button>
                        <button class="filter-btn" data-filter="critical">Critical (>60)</button>
                        <button class="filter-btn" data-filter="high">High (40-60)</button>
                        <button class="filter-btn" data-filter="low">Low (<40)</button>
                    </div>
                </div>
                
                <div class="risk-matrix-container">
                    <h4>Risk Matrix</h4>
                    <svg id="risk-matrix-svg"></svg>
                </div>
                
                <div class="priority-queue">
                    <h4>Top 5 Technologies Needing Attention</h4>
                    <div id="priority-list"></div>
                </div>
                
                <div class="scorecard-table-container">
                    <h4>Detailed Scorecard</h4>
                    <table class="scorecard-table">
                        <thead>
                            <tr>
                                <th data-sort="product">Product</th>
                                <th data-sort="version">Version</th>
                                <th data-sort="risk_score">Risk Score ▼</th>
                                <th data-sort="eol_date">EOL Date</th>
                                <th data-sort="months_to_eol">Months to EOL</th>
                                <th data-sort="cve_count">CVEs</th>
                                <th>Recommendation</th>
                            </tr>
                        </thead>
                        <tbody id="scorecard-tbody"></tbody>
                    </table>
                </div>
            </div>
        `;
        
        // Attach event listeners
        this.attachEventListeners();
    }
    
    attachEventListeners() {
        // Filter buttons
        const filterButtons = this.container.querySelectorAll('.filter-btn');
        filterButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                filterButtons.forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.filterLevel = e.target.dataset.filter;
                this.applyFilter();
            });
        });
        
        // Table headers (sorting)
        const tableHeaders = this.container.querySelectorAll('th[data-sort]');
        tableHeaders.forEach(th => {
            th.addEventListener('click', (e) => {
                const column = e.target.dataset.sort;
                this.sortBy(column);
            });
        });
    }
    
    async loadData(riskDataPath) {
        try {
            const response = await fetch(riskDataPath);
            this.data = await response.json();
            this.filteredData = [...this.data];
            this.render();
        } catch (error) {
            console.error('Error loading risk data:', error);
            this.showError('Failed to load risk assessment data');
        }
    }
    
    applyFilter() {
        if (this.filterLevel === 'all') {
            this.filteredData = [...this.data];
        } else if (this.filterLevel === 'critical') {
            this.filteredData = this.data.filter(d => d.risk_score > 60);
        } else if (this.filterLevel === 'high') {
            this.filteredData = this.data.filter(d => d.risk_score >= 40 && d.risk_score <= 60);
        } else if (this.filterLevel === 'low') {
            this.filteredData = this.data.filter(d => d.risk_score < 40);
        }
        
        this.render();
    }
    
    sortBy(column) {
        // Toggle direction if same column
        if (this.sortColumn === column) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortColumn = column;
            this.sortDirection = 'desc';
        }
        
        // Sort data
        this.filteredData.sort((a, b) => {
            let aVal = a[column];
            let bVal = b[column];
            
            // Handle null/undefined
            if (aVal === null || aVal === undefined) aVal = -Infinity;
            if (bVal === null || bVal === undefined) bVal = -Infinity;
            
            // String comparison
            if (typeof aVal === 'string') {
                aVal = aVal.toLowerCase();
                bVal = bVal.toLowerCase();
            }
            
            const comparison = aVal > bVal ? 1 : (aVal < bVal ? -1 : 0);
            return this.sortDirection === 'asc' ? comparison : -comparison;
        });
        
        this.updateTableHeaders();
        this.renderTable();
    }
    
    updateTableHeaders() {
        const headers = this.container.querySelectorAll('th[data-sort]');
        headers.forEach(th => {
            const column = th.dataset.sort;
            if (column === this.sortColumn) {
                th.textContent = th.textContent.replace(/[▲▼]/, '') + 
                                (this.sortDirection === 'asc' ? ' ▲' : ' ▼');
            } else {
                th.textContent = th.textContent.replace(/[▲▼]/, '');
            }
        });
    }
    
    render() {
        this.renderMatrix();
        this.renderPriorityQueue();
        this.renderTable();
    }
    
    renderMatrix() {
        const svg = d3.select('#risk-matrix-svg')
            .attr('width', this.width)
            .attr('height', this.height);
        
        svg.selectAll('*').remove();
        
        const g = svg.append('g')
            .attr('transform', `translate(${this.margin.left}, ${this.margin.top})`);
        
        const innerWidth = this.width - this.margin.left - this.margin.right;
        const innerHeight = this.height - this.margin.top - this.margin.bottom;
        
        // Scales
        const xScale = d3.scaleLinear()
            .domain([0, 100])
            .range([0, innerWidth]);
        
        const yScale = d3.scaleLinear()
            .domain([0, d3.max(this.filteredData, d => d.project_count || 1) * 1.1])
            .range([innerHeight, 0]);
        
        const radiusScale = d3.scaleSqrt()
            .domain([0, d3.max(this.filteredData, d => d.project_count || 1)])
            .range([5, 20]);
        
        // Axes
        const xAxis = d3.axisBottom(xScale).ticks(10);
        const yAxis = d3.axisLeft(yScale).ticks(5);
        
        g.append('g')
            .attr('transform', `translate(0, ${innerHeight})`)
            .call(xAxis)
            .append('text')
            .attr('x', innerWidth / 2)
            .attr('y', 40)
            .attr('fill', '#2c3e50')
            .attr('text-anchor', 'middle')
            .text('Risk Score');
        
        g.append('g')
            .call(yAxis)
            .append('text')
            .attr('transform', 'rotate(-90)')
            .attr('x', -innerHeight / 2)
            .attr('y', -45)
            .attr('fill', '#2c3e50')
            .attr('text-anchor', 'middle')
            .text('Impact (Project Count)');
        
        // Risk zones (background)
        const zones = [
            {x: 0, width: this.thresholds.low, color: '#d4edda', label: 'LOW'},
            {x: this.thresholds.low, width: this.thresholds.medium - this.thresholds.low, color: '#fff3cd', label: 'MEDIUM'},
            {x: this.thresholds.medium, width: 100 - this.thresholds.medium, color: '#f8d7da', label: 'HIGH'}
        ];
        
        zones.forEach(zone => {
            g.append('rect')
                .attr('x', xScale(zone.x))
                .attr('y', 0)
                .attr('width', xScale(zone.width))
                .attr('height', innerHeight)
                .attr('fill', zone.color)
                .attr('opacity', 0.3);
            
            g.append('text')
                .attr('x', xScale(zone.x + zone.width / 2))
                .attr('y', -10)
                .attr('text-anchor', 'middle')
                .attr('fill', '#6c757d')
                .attr('font-size', '12px')
                .attr('font-weight', 'bold')
                .text(zone.label);
        });
        
        // Bubbles
        const bubbles = g.selectAll('.bubble')
            .data(this.filteredData)
            .enter()
            .append('g')
            .attr('class', 'bubble');
        
        bubbles.append('circle')
            .attr('cx', d => xScale(d.risk_score))
            .attr('cy', d => yScale(d.project_count || 1))
            .attr('r', d => radiusScale(d.project_count || 1))
            .attr('fill', d => this.getRiskColor(d.risk_score))
            .attr('stroke', '#2c3e50')
            .attr('stroke-width', 2)
            .attr('opacity', 0.7)
            .on('mouseover', (event, d) => this.showTooltip(event, d))
            .on('mouseout', () => this.hideTooltip());
        
        // Labels for high-risk technologies
        bubbles.filter(d => d.risk_score > 60)
            .append('text')
            .attr('x', d => xScale(d.risk_score))
            .attr('y', d => yScale(d.project_count || 1) - radiusScale(d.project_count || 1) - 5)
            .attr('text-anchor', 'middle')
            .attr('font-size', '10px')
            .attr('fill', '#2c3e50')
            .text(d => d.product);
    }
    
    renderPriorityQueue() {
        const topTechnologies = [...this.data]
            .sort((a, b) => b.risk_score - a.risk_score)
            .slice(0, 5);
        
        const priorityList = document.getElementById('priority-list');
        
        if (topTechnologies.length === 0) {
            priorityList.innerHTML = '<p class="empty-message">No risk data available</p>';
            return;
        }
        
        priorityList.innerHTML = topTechnologies.map((tech, index) => `
            <div class="priority-item" data-rank="${index + 1}">
                <div class="priority-rank">#${index + 1}</div>
                <div class="priority-details">
                    <div class="priority-header">
                        <span class="tech-name">${tech.product} ${tech.version}</span>
                        <span class="risk-badge ${this.getRiskClass(tech.risk_score)}">
                            ${tech.risk_score.toFixed(1)}
                        </span>
                    </div>
                    <div class="priority-info">
                        <span>EOL: ${tech.eol_date || 'Unknown'}</span>
                        <span>CVEs: ${tech.cve_count || 0}</span>
                        <span>Impact: ${tech.project_count || 1} projects</span>
                    </div>
                    <div class="priority-recommendation">
                        ${tech.recommendation}
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    renderTable() {
        const tbody = document.getElementById('scorecard-tbody');
        
        if (this.filteredData.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="empty-message">No technologies match filter</td></tr>';
            return;
        }
        
        tbody.innerHTML = this.filteredData.map(tech => `
            <tr class="${this.getRiskClass(tech.risk_score)}">
                <td class="tech-name">${tech.product}</td>
                <td>${tech.version}</td>
                <td class="risk-score">
                    <span class="risk-badge ${this.getRiskClass(tech.risk_score)}">
                        ${tech.risk_score.toFixed(1)}
                    </span>
                </td>
                <td>${tech.eol_date || 'Unknown'}</td>
                <td>${tech.months_to_eol >= 0 ? tech.months_to_eol : 'N/A'}</td>
                <td>${tech.cve_count || 0}</td>
                <td class="recommendation">${tech.recommendation}</td>
            </tr>
        `).join('');
    }
    
    getRiskColor(score) {
        if (score < this.thresholds.low) return '#28a745'; // Green
        if (score < this.thresholds.medium) return '#ffc107'; // Yellow
        return '#dc3545'; // Red
    }
    
    getRiskClass(score) {
        if (score < this.thresholds.low) return 'risk-low';
        if (score < this.thresholds.medium) return 'risk-medium';
        return 'risk-high';
    }
    
    showTooltip(event, d) {
        const tooltip = d3.select('body').append('div')
            .attr('class', 'risk-tooltip')
            .style('position', 'absolute')
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 10) + 'px')
            .html(`
                <strong>${d.product} ${d.version}</strong><br>
                Risk Score: ${d.risk_score.toFixed(1)}<br>
                Age Score: ${d.age_score.toFixed(1)}<br>
                EOL Score: ${d.eol_score.toFixed(1)}<br>
                CVE Score: ${d.cve_score.toFixed(1)}<br>
                Projects: ${d.project_count || 1}<br>
                ${d.eol_date ? `EOL: ${d.eol_date}` : ''}
            `);
        
        this.currentTooltip = tooltip;
    }
    
    hideTooltip() {
        if (this.currentTooltip) {
            this.currentTooltip.remove();
            this.currentTooltip = null;
        }
    }
    
    showError(message) {
        this.container.innerHTML = `
            <div class="error-message">
                <p>⚠️ ${message}</p>
            </div>
        `;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TechnologyRiskScorecard;
}
