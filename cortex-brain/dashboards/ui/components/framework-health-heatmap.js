/**
 * Framework Health Heatmap
 * 
 * Purpose: 2D heatmap visualization showing framework health across multiple factors:
 * - Version Currency (25%): How up-to-date the framework version is
 * - CVE Score (30%): Security vulnerabilities
 * - EOL Status (25%): End-of-life proximity
 * - Community Activity (20%): GitHub stars, recent commits, maintenance
 * 
 * Features:
 * - Color gradient: green >70, yellow 50-70, red <50
 * - Cell drill-down: Click to show detailed scores and recommendations
 * - Filter controls: Show only critical (<50), filter by category
 * - Migration path suggestions for critical frameworks
 * 
 * Author: CORTEX Dashboard System
 * Version: 1.0.0
 * Created: December 6, 2025
 */

class FrameworkHealthHeatmap {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.techStackData = null;
        this.healthData = [];
        this.selectedCell = null;
        this.filters = {
            showOnlyCritical: false,
            category: 'all'
        };
        
        // Health factor weights
        this.weights = {
            versionCurrency: 0.25,
            cveScore: 0.30,
            eolStatus: 0.25,
            communityActivity: 0.20
        };
        
        this.init();
    }
    
    init() {
        this.createLayout();
        this.loadData();
    }
    
    createLayout() {
        this.container.innerHTML = `
            <div class="heatmap-header">
                <h2>Framework Health Heatmap</h2>
                <div class="heatmap-controls">
                    <button id="showCriticalOnly" class="btn-filter" data-active="false">
                        Show Critical Only
                    </button>
                    <select id="categoryFilter" class="select-filter">
                        <option value="all">All Categories</option>
                        <option value="dependency-injection">Dependency Injection</option>
                        <option value="logging">Logging</option>
                        <option value="orm">ORM/Data Access</option>
                        <option value="serialization">Serialization</option>
                        <option value="testing">Testing</option>
                        <option value="web">Web Framework</option>
                    </select>
                </div>
            </div>
            
            <div class="heatmap-legend">
                <div class="legend-title">Health Score</div>
                <div class="legend-gradient">
                    <div class="legend-marker" style="left: 0%">0</div>
                    <div class="legend-marker" style="left: 50%">50</div>
                    <div class="legend-marker" style="left: 70%">70</div>
                    <div class="legend-marker" style="left: 100%">100</div>
                </div>
                <div class="legend-labels">
                    <span class="legend-label critical">Critical (&lt;50)</span>
                    <span class="legend-label warning">Warning (50-70)</span>
                    <span class="legend-label healthy">Healthy (&gt;70)</span>
                </div>
            </div>
            
            <div class="heatmap-container" id="heatmapViz">
                <!-- Heatmap populated by renderHeatmap() -->
            </div>
            
            <div class="drill-down-panel" id="drillDownPanel" style="display: none;">
                <!-- Drill-down details populated by showDrillDown() -->
            </div>
        `;
        
        // Attach event listeners
        document.getElementById('showCriticalOnly').addEventListener('click', (e) => {
            this.filters.showOnlyCritical = !this.filters.showOnlyCritical;
            e.target.dataset.active = this.filters.showOnlyCritical;
            this.renderHeatmap();
        });
        
        document.getElementById('categoryFilter').addEventListener('change', (e) => {
            this.filters.category = e.target.value;
            this.renderHeatmap();
        });
    }
    
    async loadData() {
        try {
            const response = await fetch('/api/tech-stack');
            this.techStackData = await response.json();
            
            this.calculateHealthScores();
            this.renderHeatmap();
        } catch (error) {
            console.error('Error loading tech stack data:', error);
            this.showError('Failed to load framework health data');
        }
    }
    
    calculateHealthScores() {
        if (!this.techStackData || !this.techStackData.frameworks) {
            return;
        }
        
        this.healthData = this.techStackData.frameworks.map(framework => {
            const versionCurrency = this.calculateVersionCurrency(framework);
            const cveScore = this.calculateCVEScore(framework);
            const eolStatus = this.calculateEOLStatus(framework);
            const communityActivity = this.calculateCommunityActivity(framework);
            
            const healthScore = (
                versionCurrency * this.weights.versionCurrency +
                cveScore * this.weights.cveScore +
                eolStatus * this.weights.eolStatus +
                communityActivity * this.weights.communityActivity
            );
            
            return {
                name: framework.name,
                version: framework.version,
                category: framework.category || 'other',
                project_count: framework.project_count || 0,
                healthScore: Math.round(healthScore),
                factors: {
                    versionCurrency: Math.round(versionCurrency),
                    cveScore: Math.round(cveScore),
                    eolStatus: Math.round(eolStatus),
                    communityActivity: Math.round(communityActivity)
                },
                raw: {
                    risk_score: framework.risk_score,
                    eol_date: framework.eol_date,
                    months_to_eol: framework.months_to_eol,
                    cve_count: framework.cve_count || 0
                }
            };
        });
        
        // Sort by health score (worst first for visibility)
        this.healthData.sort((a, b) => a.healthScore - b.healthScore);
    }
    
    calculateVersionCurrency(framework) {
        // Version currency based on risk score (inverse relationship)
        // Lower risk = more current version
        const riskScore = framework.risk_score || 50;
        
        // Convert risk score (0-100, higher = worse) to currency (0-100, higher = better)
        return 100 - riskScore;
    }
    
    calculateCVEScore(framework) {
        // CVE score: 0 CVEs = 100, decreases with more CVEs
        const cveCount = framework.cve_count || 0;
        
        if (cveCount === 0) return 100;
        if (cveCount === 1) return 85;
        if (cveCount <= 3) return 70;
        if (cveCount <= 5) return 50;
        if (cveCount <= 10) return 30;
        return 10;
    }
    
    calculateEOLStatus(framework) {
        // EOL status based on months to EOL
        const monthsToEOL = framework.months_to_eol;
        
        if (monthsToEOL === null || monthsToEOL === undefined) {
            return 80; // No EOL date = assume maintained
        }
        
        if (monthsToEOL <= 0) return 0;   // Already EOL
        if (monthsToEOL <= 6) return 20;  // < 6 months
        if (monthsToEOL <= 12) return 50; // < 1 year
        if (monthsToEOL <= 24) return 75; // < 2 years
        return 100; // > 2 years or no EOL
    }
    
    calculateCommunityActivity(framework) {
        // Community activity score (simplified - would need GitHub API in production)
        // For now, use heuristics based on framework popularity and age
        
        const popularFrameworks = {
            'serilog': 95,
            'autofac': 90,
            'entityframework': 95,
            'system.text.json': 100,
            'xunit': 95,
            'moq': 90,
            'newtonsoft.json': 80, // Still popular but declining
            'log4net': 40, // Low maintenance
            'unity': 35, // Low maintenance
            'nlog': 85
        };
        
        const frameworkNameLower = framework.name.toLowerCase();
        
        // Check if framework name contains known framework
        for (const [name, score] of Object.entries(popularFrameworks)) {
            if (frameworkNameLower.includes(name)) {
                return score;
            }
        }
        
        // Default: assume moderate activity
        return 60;
    }
    
    renderHeatmap() {
        const container = document.getElementById('heatmapViz');
        container.innerHTML = '';
        
        // Apply filters
        let filteredData = [...this.healthData];
        
        if (this.filters.showOnlyCritical) {
            filteredData = filteredData.filter(d => d.healthScore < 50);
        }
        
        if (this.filters.category !== 'all') {
            filteredData = filteredData.filter(d => d.category === this.filters.category);
        }
        
        if (filteredData.length === 0) {
            container.innerHTML = '<div class="no-data">No frameworks match the current filters</div>';
            return;
        }
        
        // Create D3 heatmap
        const margin = { top: 100, right: 40, bottom: 40, left: 200 };
        const width = container.clientWidth - margin.left - margin.right;
        const cellHeight = 40;
        const height = filteredData.length * cellHeight;
        
        const svg = d3.select(container)
            .append('svg')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom);
        
        const g = svg.append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);
        
        // Health factors (columns)
        const factors = [
            { key: 'versionCurrency', label: 'Version Currency (25%)' },
            { key: 'cveScore', label: 'CVE Score (30%)' },
            { key: 'eolStatus', label: 'EOL Status (25%)' },
            { key: 'communityActivity', label: 'Community (20%)' },
            { key: 'healthScore', label: 'Overall Health' }
        ];
        
        const cellWidth = width / factors.length;
        
        // Color scale
        const colorScale = d3.scaleLinear()
            .domain([0, 50, 70, 100])
            .range(['#dc3545', '#ffc107', '#90ee90', '#28a745'])
            .clamp(true);
        
        // Y scale (frameworks)
        const yScale = d3.scaleBand()
            .domain(filteredData.map(d => d.name))
            .range([0, height])
            .padding(0.05);
        
        // X scale (factors)
        const xScale = d3.scaleBand()
            .domain(factors.map(f => f.key))
            .range([0, width])
            .padding(0.05);
        
        // Column headers
        g.selectAll('.col-header')
            .data(factors)
            .enter()
            .append('text')
            .attr('class', 'col-header')
            .attr('x', d => xScale(d.key) + xScale.bandwidth() / 2)
            .attr('y', -10)
            .attr('text-anchor', 'middle')
            .text(d => d.label)
            .style('font-size', '12px')
            .style('font-weight', 'bold');
        
        // Row labels (framework names)
        g.selectAll('.row-label')
            .data(filteredData)
            .enter()
            .append('text')
            .attr('class', 'row-label')
            .attr('x', -10)
            .attr('y', d => yScale(d.name) + yScale.bandwidth() / 2)
            .attr('text-anchor', 'end')
            .attr('dominant-baseline', 'middle')
            .text(d => `${d.name} ${d.version}`)
            .style('font-size', '11px')
            .style('cursor', 'pointer')
            .on('click', (event, d) => this.showDrillDown(d));
        
        // Heatmap cells
        filteredData.forEach(framework => {
            factors.forEach(factor => {
                const value = factor.key === 'healthScore' 
                    ? framework.healthScore 
                    : framework.factors[factor.key];
                
                g.append('rect')
                    .attr('x', xScale(factor.key))
                    .attr('y', yScale(framework.name))
                    .attr('width', xScale.bandwidth())
                    .attr('height', yScale.bandwidth())
                    .attr('fill', colorScale(value))
                    .attr('stroke', '#fff')
                    .attr('stroke-width', 2)
                    .style('cursor', 'pointer')
                    .on('click', () => this.showDrillDown(framework, factor.key))
                    .on('mouseenter', function() {
                        d3.select(this).attr('stroke', '#000').attr('stroke-width', 3);
                    })
                    .on('mouseleave', function() {
                        d3.select(this).attr('stroke', '#fff').attr('stroke-width', 2);
                    })
                    .append('title')
                    .text(`${framework.name}\n${factor.label}: ${value}`);
                
                // Cell value text
                g.append('text')
                    .attr('x', xScale(factor.key) + xScale.bandwidth() / 2)
                    .attr('y', yScale(framework.name) + yScale.bandwidth() / 2)
                    .attr('text-anchor', 'middle')
                    .attr('dominant-baseline', 'middle')
                    .text(value)
                    .style('font-size', '12px')
                    .style('font-weight', 'bold')
                    .style('fill', value < 60 ? '#fff' : '#000')
                    .style('pointer-events', 'none');
            });
        });
    }
    
    showDrillDown(framework, focusFactor = null) {
        this.selectedCell = framework;
        const panel = document.getElementById('drillDownPanel');
        panel.style.display = 'block';
        
        const healthClass = this.getHealthClass(framework.healthScore);
        
        let html = `
            <div class="drill-down-header">
                <h3>${framework.name} ${framework.version}</h3>
                <button class="close-btn" onclick="document.getElementById('drillDownPanel').style.display='none'">×</button>
            </div>
            
            <div class="drill-down-content">
                <div class="overall-health">
                    <div class="health-score ${healthClass}">
                        ${framework.healthScore}
                    </div>
                    <div class="health-label">Overall Health Score</div>
                </div>
                
                <div class="factor-breakdown">
                    <h4>Health Factor Breakdown</h4>
                    <div class="factor-grid">
        `;
        
        const factorDetails = [
            { key: 'versionCurrency', label: 'Version Currency', weight: '25%' },
            { key: 'cveScore', label: 'CVE Score', weight: '30%' },
            { key: 'eolStatus', label: 'EOL Status', weight: '25%' },
            { key: 'communityActivity', label: 'Community Activity', weight: '20%' }
        ];
        
        factorDetails.forEach(factor => {
            const value = framework.factors[factor.key];
            const factorClass = this.getHealthClass(value);
            const isFocus = focusFactor === factor.key;
            
            html += `
                <div class="factor-card ${isFocus ? 'focus' : ''}">
                    <div class="factor-name">${factor.label} (${factor.weight})</div>
                    <div class="factor-value ${factorClass}">${value}</div>
                </div>
            `;
        });
        
        html += `
                    </div>
                </div>
                
                <div class="recommendations">
                    <h4>Recommendations</h4>
                    ${this.generateRecommendations(framework)}
                </div>
                
                <div class="migration-paths">
                    <h4>Available Migration Paths</h4>
                    ${this.getMigrationPaths(framework)}
                </div>
                
                <div class="raw-data">
                    <h4>Raw Data</h4>
                    <ul>
                        <li><strong>Projects:</strong> ${framework.project_count}</li>
                        <li><strong>Risk Score:</strong> ${framework.raw.risk_score || 'N/A'}</li>
                        <li><strong>CVE Count:</strong> ${framework.raw.cve_count}</li>
                        <li><strong>EOL Date:</strong> ${framework.raw.eol_date || 'No EOL date'}</li>
                        <li><strong>Months to EOL:</strong> ${framework.raw.months_to_eol !== null ? framework.raw.months_to_eol : 'N/A'}</li>
                    </ul>
                </div>
            </div>
        `;
        
        panel.innerHTML = html;
        panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    generateRecommendations(framework) {
        const recommendations = [];
        
        if (framework.factors.versionCurrency < 50) {
            recommendations.push('⚠️ <strong>Update to latest version</strong> to improve security and performance');
        }
        
        if (framework.factors.cveScore < 50) {
            recommendations.push('🔒 <strong>Critical security vulnerabilities detected</strong> - immediate update recommended');
        }
        
        if (framework.factors.eolStatus < 30) {
            recommendations.push('⏰ <strong>Framework approaching or past EOL</strong> - plan migration to maintained alternative');
        }
        
        if (framework.factors.communityActivity < 50) {
            recommendations.push('📉 <strong>Low community activity</strong> - consider migration to more actively maintained framework');
        }
        
        if (framework.healthScore >= 70) {
            recommendations.push('✅ <strong>Framework is healthy</strong> - continue monitoring for updates');
        }
        
        if (recommendations.length === 0) {
            recommendations.push('ℹ️ No specific recommendations at this time');
        }
        
        return '<ul class="recommendation-list">' + 
               recommendations.map(r => `<li>${r}</li>`).join('') + 
               '</ul>';
    }
    
    getMigrationPaths(framework) {
        const migrationMap = {
            'log4net': 'Serilog (8h/project, MEDIUM complexity)',
            'unity': 'Autofac (6h/project, MEDIUM complexity)',
            'newtonsoft.json': 'System.Text.Json (10h/project, MEDIUM complexity)',
            '.net framework': '.NET 8 (40h/project, HIGH complexity)'
        };
        
        const frameworkNameLower = framework.name.toLowerCase();
        
        for (const [key, path] of Object.entries(migrationMap)) {
            if (frameworkNameLower.includes(key)) {
                return `<div class="migration-path">
                    <strong>Recommended:</strong> ${path}
                    <br>
                    <a href="#migration-roadmap">View Migration Roadmap</a>
                </div>`;
            }
        }
        
        return '<div class="no-migration">No migration paths defined for this framework</div>';
    }
    
    getHealthClass(score) {
        if (score >= 70) return 'healthy';
        if (score >= 50) return 'warning';
        return 'critical';
    }
    
    showError(message) {
        this.container.innerHTML = `
            <div class="error-message">
                <h3>Error</h3>
                <p>${message}</p>
            </div>
        `;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    new FrameworkHealthHeatmap('frameworkHealthHeatmapContainer');
});
