/**
 * Overview Tab Component v3.0
 * 
 * Renders comprehensive dashboard overview with:
 * - Compact health score gauge (280px, reduced padding)
 * - Key metrics cards with trend indicators
 * - Health categories breakdown
 * - Composition pie chart
 * - Critical issues alerts
 * 
 * Data Source: /data/mock/overview.json (OverviewCollector output)
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Source-Available (Use Allowed, No Contributions)
 */

import { BaseTabComponent } from '../core/BaseTabComponent.js';

/**
 * Overview Tab Component (extends BaseTabComponent)
 */
class OverviewTab extends BaseTabComponent {
    constructor() {
        super('overview-container');
    }
    
    render() {
        renderOverview(this.data, this.container);
    }
}

/**
 * Render overview tab with compact health hero design
 * @param {Object} data - Overview data from OverviewCollector
 * @param {HTMLElement} container - Container element (optional, for backward compatibility)
 */
export function renderOverview(data, container = null) {
    container = container || document.getElementById('overview-container');
    if (!container) {
        console.error('Overview container not found');
        return;
    }
    
    // Extract data sections
    const overallHealth = data.overall_health || {};
    const metrics = data.key_metrics || {};
    const categories = data.health_categories || [];
    const compositionData = data.composition || {};
    const compositionLanguages = compositionData.languages || [];
    const issues = data.critical_issues || [];
    
    // Build HTML
    container.innerHTML = `
        <!-- Compact Health Score Hero -->
        <div class="health-score-hero glass-card" style="
            padding: 1rem 1.5rem;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 2rem;
        ">
            <!-- Gauge Container -->
            <div style="flex-shrink: 0;">
                <div id="health-gauge" style="width: 280px; height: 280px;"></div>
            </div>
            
            <!-- Health Status Info -->
            <div style="flex: 1;">
                <h2 style="font-size: 1.75rem; margin-bottom: 0.5rem; color: var(--text-primary);">
                    Overall Health: ${overallHealth.score || 0}/100
                </h2>
                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                    <span class="status-badge status-${overallHealth.status}" style="
                        padding: 0.375rem 0.875rem;
                        border-radius: 16px;
                        font-weight: 600;
                        font-size: 0.875rem;
                        background: ${getStatusGradient(overallHealth.status)};
                        text-transform: uppercase;
                    ">${overallHealth.status || 'unknown'}</span>
                    <span class="trend-badge trend-${overallHealth.trend}" style="
                        padding: 0.375rem 0.875rem;
                        border-radius: 16px;
                        font-weight: 500;
                        font-size: 0.875rem;
                        background: ${getTrendGradient(overallHealth.trend)};
                    ">
                        ${getTrendIcon(overallHealth.trend)} ${overallHealth.trend || 'stable'}
                    </span>
                </div>
                <p style="color: var(--text-secondary); font-size: 0.875rem; line-height: 1.6;">
                    System health is ${overallHealth.status || 'unknown'}. 
                    ${getHealthDescription(overallHealth.status, overallHealth.score)}
                </p>
                <p style="color: var(--text-muted); font-size: 0.75rem; margin-top: 0.75rem;">
                    Last scan: ${formatTimestamp(overallHealth.last_scan)}
                </p>
            </div>
        </div>

        <!-- Key Metrics Grid -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.25rem; margin-bottom: 2rem;">
            ${renderMetricCard('📊', 'Total Files', metrics.total_files || 0, '')}
            ${renderMetricCard('📝', 'Lines of Code', formatNumber(metrics.total_loc || 0), '')}
            ${renderMetricCard('🧪', 'Test Coverage', metrics.test_coverage || 0, '%', metrics.test_coverage >= 80 ? 'success' : metrics.test_coverage >= 60 ? 'warning' : 'danger')}
            ${renderMetricCard('🎯', 'Maintainability', metrics.maintainability_index || 0, '/100', metrics.maintainability_index >= 80 ? 'success' : metrics.maintainability_index >= 60 ? 'warning' : 'danger')}
            ${renderMetricCard('⏱️', 'Tech Debt', metrics.technical_debt_hours || 0, 'hrs', metrics.technical_debt_hours <= 20 ? 'success' : metrics.technical_debt_hours <= 50 ? 'warning' : 'danger')}
        </div>

        <!-- Health Categories & Composition Row -->
        <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 1.5rem; margin-bottom: 2rem;">
            <!-- Health Categories Breakdown -->
            <div class="glass-card">
                <h3 style="margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.5rem;">
                    <span>📈</span> Health Categories
                </h3>
                <div style="display: grid; gap: 1rem;">
                    ${categories.map(cat => renderCategoryBar(cat)).join('')}
                </div>
            </div>

            <!-- Project Composition -->
            <div class="glass-card">
                <h3 style="margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.5rem;">
                    <span>🥧</span> Composition
                </h3>
                <div id="composition-chart" style="width: 100%; height: 240px;"></div>
                <div style="margin-top: 1rem; font-size: 0.75rem; color: var(--text-secondary);">
                    ${compositionLanguages.map(lang => 
                        `<div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                            <span>${lang.name}</span>
                            <span style="font-weight: 600;">${lang.percentage.toFixed(1)}%</span>
                        </div>`
                    ).join('')}
                </div>
            </div>
        </div>

        <!-- Critical Issues Alert -->
        ${issues.length > 0 ? `
            <div class="glass-card" style="
                border-left: 4px solid var(--danger);
                background: linear-gradient(135deg, rgba(255, 59, 48, 0.1), transparent);
                margin-bottom: 2rem;
            ">
                <h3 style="margin-bottom: 1rem; color: var(--danger); display: flex; align-items: center; gap: 0.5rem;">
                    <span>⚠️</span> Critical Issues (${issues.length})
                </h3>
                <div style="display: grid; gap: 0.75rem;">
                    ${issues.map(issue => `
                        <div style="
                            padding: 0.75rem;
                            background: rgba(255, 255, 255, 0.05);
                            border-radius: 8px;
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                        ">
                            <div>
                                <div style="font-weight: 600; margin-bottom: 0.25rem;">
                                    ${issue.severity ? `[${issue.severity.toUpperCase()}]` : ''} 
                                    ${issue.category || 'Unknown Category'}
                                </div>
                                <div style="font-size: 0.875rem; color: var(--text-secondary);">
                                    ${issue.message || 'No description'} 
                                    ${issue.count ? `(${issue.count} issue${issue.count > 1 ? 's' : ''})` : ''}
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        ` : `
            <div class="glass-card" style="
                border-left: 4px solid var(--success);
                background: linear-gradient(135deg, rgba(52, 199, 89, 0.1), transparent);
                margin-bottom: 2rem;
                text-align: center;
                padding: 2rem;
            ">
                <h3 style="color: var(--success); margin-bottom: 0.5rem; font-size: 1.5rem;">✅ All Clear</h3>
                <p style="color: var(--text-secondary); font-size: 0.875rem;">No critical issues detected</p>
            </div>
        `}

        <!-- Quick Links -->
        <div class="glass-card">
            <h3 style="margin-bottom: 1.5rem;">🔗 Explore Details</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 1rem;">
                ${renderQuickLink('🛠️', 'Tech Stack', 'tech-stack')}
                ${renderQuickLink('🔒', 'Security', 'security')}
                ${renderQuickLink('🏗️', 'Architecture', 'architecture')}
                ${renderQuickLink('📁', 'Code Org', 'code-org')}
                ${renderQuickLink('📈', 'Executive', 'executive')}
            </div>
        </div>
    `;
    
    // Render charts after DOM is ready
    setTimeout(() => {
        renderHealthGauge(overallHealth.score, overallHealth.status);
        renderCompositionChart(compositionLanguages);
    }, 0);
}

/**
 * Render metric card
 */
function renderMetricCard(icon, label, value, unit, statusClass = '') {
    const colorClass = statusClass ? `color: var(--${statusClass});` : 'color: var(--accent-primary);';
    return `
        <div class="glass-card" style="text-align: center; padding: 1.25rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">${icon}</div>
            <h3 style="font-size: 1.75rem; ${colorClass} margin-bottom: 0.25rem; font-weight: 700;">
                ${value}${unit}
            </h3>
            <p style="color: var(--text-secondary); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px;">
                ${label}
            </p>
        </div>
    `;
}

/**
 * Render category bar
 */
function renderCategoryBar(category) {
    const score = category.score || 0;
    const status = category.status || 'unknown';
    const trend = category.trend || 'stable';
    const barColor = score >= 80 ? 'var(--success)' : score >= 60 ? 'var(--warning)' : 'var(--danger)';
    
    return `
        <div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <span style="font-weight: 600; text-transform: capitalize;">
                        ${category.name.replace(/_/g, ' ')}
                    </span>
                    <span style="font-size: 0.75rem; color: var(--text-secondary);">
                        ${getTrendIcon(trend)}
                    </span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <span style="font-weight: 700; color: ${barColor};">${score}/100</span>
                    ${category.issues_count > 0 ? 
                        `<span style="font-size: 0.75rem; color: var(--warning);">${category.issues_count} issues</span>` 
                        : ''
                    }
                </div>
            </div>
            <div style="height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden;">
                <div style="
                    width: ${score}%;
                    height: 100%;
                    background: ${barColor};
                    border-radius: 4px;
                    transition: width 0.5s ease;
                "></div>
            </div>
            <p style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.25rem;">
                ${category.details || ''}
            </p>
        </div>
    `;
}

/**
 * Render quick link button
 */
function renderQuickLink(icon, label, tabId) {
    return `
        <button class="btn" onclick="switchTab('${tabId}')" style="
            padding: 1rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.5rem;
            border: 1px solid rgba(255,255,255,0.1);
            transition: all 0.3s ease;
        " onmouseover="this.style.borderColor='var(--accent-primary)'" onmouseout="this.style.borderColor='rgba(255,255,255,0.1)'">
            <div style="font-size: 2rem;">${icon}</div>
            <div style="font-size: 0.875rem; font-weight: 500;">${label}</div>
        </button>
    `;
}

/**
 * Render health gauge with D3.js
 */
function renderHealthGauge(score, status) {
    const container = document.getElementById('health-gauge');
    if (!container) return;
    
    // Clear existing
    container.innerHTML = '';
    
    const width = 280;
    const height = 280;
    const radius = Math.min(width, height) / 2 - 20;
    
    // Create SVG
    const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .append('g')
        .attr('transform', `translate(${width/2}, ${height/2})`);
    
    // Background arc
    const backgroundArc = d3.arc()
        .innerRadius(radius * 0.7)
        .outerRadius(radius)
        .startAngle(-Math.PI / 2)
        .endAngle(Math.PI / 2);
    
    svg.append('path')
        .attr('d', backgroundArc)
        .attr('fill', 'rgba(255,255,255,0.1)');
    
    // Score arc
    const scoreArc = d3.arc()
        .innerRadius(radius * 0.7)
        .outerRadius(radius)
        .startAngle(-Math.PI / 2)
        .endAngle(-Math.PI / 2 + (score / 100) * Math.PI);
    
    const gradient = svg.append('defs')
        .append('linearGradient')
        .attr('id', 'gauge-gradient')
        .attr('x1', '0%')
        .attr('y1', '0%')
        .attr('x2', '100%')
        .attr('y2', '100%');
    
    gradient.append('stop')
        .attr('offset', '0%')
        .attr('stop-color', getScoreColor(score, 0));
    
    gradient.append('stop')
        .attr('offset', '100%')
        .attr('stop-color', getScoreColor(score, 1));
    
    svg.append('path')
        .attr('d', scoreArc)
        .attr('fill', 'url(#gauge-gradient)')
        .style('filter', 'drop-shadow(0 0 10px rgba(94, 92, 230, 0.5))');
    
    // Center text
    svg.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', '0.1em')
        .style('font-size', '3.5rem')
        .style('font-weight', '700')
        .style('fill', 'var(--text-primary)')
        .text(score);
    
    svg.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', '3em')
        .style('font-size', '0.875rem')
        .style('fill', 'var(--text-secondary)')
        .style('text-transform', 'uppercase')
        .style('letter-spacing', '1px')
        .text('Health Score');
}

/**
 * Render composition pie chart with D3.js
 */
function renderCompositionChart(languages) {
    const container = document.getElementById('composition-chart');
    if (!container) return;
    
    container.innerHTML = '';
    
    const width = 240;
    const height = 240;
    const radius = Math.min(width, height) / 2 - 10;
    
    const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .append('g')
        .attr('transform', `translate(${width/2}, ${height/2})`);
    
    // Prepare data from languages array
    const data = languages.map(lang => ({
        name: lang.name,
        value: lang.percentage
    }));
    
    const pie = d3.pie()
        .value(d => d.value)
        .sort(null);
    
    const arc = d3.arc()
        .innerRadius(radius * 0.6)
        .outerRadius(radius);
    
    const color = d3.scaleOrdinal()
        .domain(data.map(d => d.name))
        .range(['#5E5CE6', '#AF52DE', '#FF2D55', '#FF9500', '#FFCC00', '#34C759']);
    
    svg.selectAll('path')
        .data(pie(data))
        .enter()
        .append('path')
        .attr('d', arc)
        .attr('fill', d => color(d.data.name))
        .attr('stroke', 'var(--background-primary)')
        .attr('stroke-width', 2)
        .style('filter', 'drop-shadow(0 2px 4px rgba(0,0,0,0.3))')
        .on('mouseover', function(event, d) {
            d3.select(this)
                .transition()
                .duration(200)
                .attr('d', d3.arc()
                    .innerRadius(radius * 0.6)
                    .outerRadius(radius * 1.1)
                );
        })
        .on('mouseout', function(event, d) {
            d3.select(this)
                .transition()
                .duration(200)
                .attr('d', arc);
        });
}

/**
 * Helper functions
 */

function getStatusGradient(status) {
    switch(status) {
        case 'healthy': return 'linear-gradient(135deg, #34C759, #30D158)';
        case 'warning': return 'linear-gradient(135deg, #FF9500, #FF9F0A)';
        case 'critical': return 'linear-gradient(135deg, #FF3B30, #FF453A)';
        default: return 'linear-gradient(135deg, #8E8E93, #98989D)';
    }
}

function getTrendGradient(trend) {
    switch(trend) {
        case 'improving': return 'rgba(52, 199, 89, 0.2)';
        case 'declining': return 'rgba(255, 59, 48, 0.2)';
        case 'stable': return 'rgba(142, 142, 147, 0.2)';
        default: return 'rgba(142, 142, 147, 0.2)';
    }
}

function getTrendIcon(trend) {
    switch(trend) {
        case 'improving': return '📈';
        case 'declining': return '📉';
        case 'stable': return '➡️';
        default: return '➡️';
    }
}

function getScoreColor(score, offset) {
    if (score >= 80) return offset === 0 ? '#34C759' : '#30D158';
    if (score >= 60) return offset === 0 ? '#FF9500' : '#FF9F0A';
    return offset === 0 ? '#FF3B30' : '#FF453A';
}

function getHealthDescription(status, score) {
    if (score >= 90) return 'Excellent health with no major concerns.';
    if (score >= 75) return 'Good health with minor improvements needed.';
    if (score >= 60) return 'Fair health - some attention required.';
    return 'Action needed to improve system health.';
}

function formatNumber(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
}

function formatTimestamp(timestamp) {
    if (!timestamp) return 'Never';
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minutes ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours} hours ago`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays} days ago`;
}

function viewIssueDetails(issueId) {
    console.log('View issue:', issueId);
    // TODO: Implement issue detail modal
    alert(`Issue details for ${issueId} - coming soon!`);
}

// Export for use in dashboard
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { renderOverview };
}

// Export class for BaseTabComponent pattern
export { OverviewTab };
