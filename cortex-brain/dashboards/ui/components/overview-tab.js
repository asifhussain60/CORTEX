/**
 * Overview Tab Component
 * 
 * Renders the main dashboard overview with health score gauge,
 * key metrics, and status indicators.
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Source-Available (Use Allowed, No Contributions)
 */

import { showPanelSpinner } from '../shared-utils.js';

/**
 * Render overview tab
 * @param {Object} data - Dashboard data
 */
export function renderOverview(data) {
    const container = document.getElementById('overview-container');
    if (!container) {
        console.error('Overview container not found');
        return;
    }
    
    const healthData = data.healthData || {};
    const techStack = data.techStack || {};
    const security = data.security || {};
    const codeOrg = data.codeOrganization || {};
    const teamMetrics = data.teamMetrics || {};
    
    // Build HTML
    container.innerHTML = `
        <!-- How to Read Description -->
        <div class="glass-card" style="margin-bottom: 2rem; background: linear-gradient(135deg, var(--glass-light) 0%, var(--background-secondary) 100%);">
            <h3 style="margin-bottom: 1rem;">📊 Dashboard Overview</h3>
            <p style="color: var(--text-secondary); line-height: 1.6; margin-bottom: 1rem;">
                This overview provides a comprehensive health assessment of your project. The 
                <strong style="color: var(--success);">health score (🟢 >75)</strong>, 
                <strong style="color: var(--warning);">needs attention (🟡 50-75)</strong>, or 
                <strong style="color: var(--danger);">requires immediate action (🔴 <50)</strong>.
                <strong>Hover over each metric card</strong> to see detailed explanations, scoring methodology, and actionable recommendations for improvement.
            </p>
        </div>

        <!-- Health Score Section -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin-bottom: 2rem;">
            <!-- Health Score Gauge -->
            <div class="glass-card" style="grid-column: span 2;">
                <h3 style="margin-bottom: 1.5rem;">📊 Overall Health Score</h3>
                <div id="health-gauge" style="width: 100%; height: 400px;"></div>
                <div style="text-align: center; margin-top: 1rem;">
                    <p style="font-size: 0.875rem; color: var(--text-secondary);">
                        Status: <span class="status-badge status-${healthData.status || 'unknown'}" style="
                            padding: 0.25rem 0.75rem;
                            border-radius: 12px;
                            font-weight: 600;
                            background: ${getStatusColor(healthData.status)};
                        ">${(healthData.status || 'Unknown').toUpperCase()}</span>
                    </p>
                    <p style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.5rem;">
                        Last scan: ${formatTimestamp(healthData.last_scan)}
                    </p>
                </div>
            </div>
        </div>
        
        <!-- Key Metrics Grid -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
            <!-- Code Quality -->
            <div 
                class="overview-metric-card glass-card"
                style="cursor: pointer; transition: all 0.3s ease;"
                onmouseover="showOverviewTooltip(event, 'Code Quality', ${healthData.metrics?.code_quality_score || 0}, 'code_quality', this)"
                onmouseout="hideOverviewTooltip(this)"
            >
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <span style="font-size: 2rem; margin-right: 1rem;">📝</span>
                    <div>
                        <h4 style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Code Quality</h4>
                        <h2 style="font-size: 2rem; color: var(--accent-primary);">${healthData.metrics?.code_quality_score || 0}/100</h2>
                    </div>
                </div>
                <div style="height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; overflow: hidden;">
                    <div style="width: ${healthData.metrics?.code_quality_score || 0}%; height: 100%; background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary)); transition: width 0.5s;"></div>
                </div>
            </div>
            
            <!-- Security Score -->
            <div 
                class="overview-metric-card glass-card"
                style="cursor: pointer; transition: all 0.3s ease;"
                onmouseover="showOverviewTooltip(event, 'Security Score', ${security.overall_score || 0}, 'security', this)"
                onmouseout="hideOverviewTooltip(this)"
            >
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <span style="font-size: 2rem; margin-right: 1rem;">🔒</span>
                    <div>
                        <h4 style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Security Score</h4>
                        <h2 style="font-size: 2rem; color: ${security.overall_score >= 90 ? 'var(--success)' : security.overall_score >= 70 ? 'var(--warning)' : 'var(--danger)'};">${security.overall_score || 0}/100</h2>
                    </div>
                </div>
                <div style="height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; overflow: hidden;">
                    <div style="width: ${security.overall_score || 0}%; height: 100%; background: ${security.overall_score >= 90 ? 'var(--success)' : security.overall_score >= 70 ? 'var(--warning)' : 'var(--danger)'}; transition: width 0.5s;"></div>
                </div>
            </div>
            
            <!-- Test Coverage -->
            <div 
                class="overview-metric-card glass-card"
                style="cursor: pointer; transition: all 0.3s ease;"
                onmouseover="showOverviewTooltip(event, 'Test Coverage', ${healthData.summary?.test_coverage || 0}, 'test_coverage', this)"
                onmouseout="hideOverviewTooltip(this)"
            >
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <span style="font-size: 2rem; margin-right: 1rem;">🧪</span>
                    <div>
                        <h4 style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Test Coverage</h4>
                        <h2 style="font-size: 2rem; color: var(--accent-primary);">${healthData.summary?.test_coverage || 0}%</h2>
                    </div>
                </div>
                <div style="height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; overflow: hidden;">
                    <div style="width: ${healthData.summary?.test_coverage || 0}%; height: 100%; background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary)); transition: width 0.5s;"></div>
                </div>
            </div>
            
            <!-- Documentation -->
            <div 
                class="overview-metric-card glass-card"
                style="cursor: pointer; transition: all 0.3s ease;"
                onmouseover="showOverviewTooltip(event, 'Documentation', ${healthData.metrics?.documentation_score || 0}, 'documentation', this)"
                onmouseout="hideOverviewTooltip(this)"
            >
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <span style="font-size: 2rem; margin-right: 1rem;">📚</span>
                    <div>
                        <h4 style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Documentation</h4>
                        <h2 style="font-size: 2rem; color: var(--accent-primary);">${healthData.metrics?.documentation_score || 0}/100</h2>
                    </div>
                </div>
                <div style="height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; overflow: hidden;">
                    <div style="width: ${healthData.metrics?.documentation_score || 0}%; height: 100%; background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary)); transition: width 0.5s;"></div>
                </div>
            </div>
        </div>
        
        <!-- Summary Stats -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
            <div class="glass-card" style="text-align: center;">
                <h3 style="font-size: 2.5rem; color: var(--accent-primary); margin-bottom: 0.5rem;">${healthData.summary?.total_files || 0}</h3>
                <p style="color: var(--text-secondary);">Total Files</p>
            </div>
            <div class="glass-card" style="text-align: center;">
                <h3 style="font-size: 2.5rem; color: var(--accent-primary); margin-bottom: 0.5rem;">${formatNumber(healthData.summary?.total_loc || 0)}</h3>
                <p style="color: var(--text-secondary);">Lines of Code</p>
            </div>
            <div class="glass-card" style="text-align: center;">
                <h3 style="font-size: 2.5rem; color: var(--accent-primary); margin-bottom: 0.5rem;">${techStack.summary?.total_technologies || 0}</h3>
                <p style="color: var(--text-secondary);">Technologies</p>
            </div>
            <div class="glass-card" style="text-align: center;">
                <h3 style="font-size: 2.5rem; color: var(--accent-primary); margin-bottom: 0.5rem;">${teamMetrics.summary?.total_contributors || 0}</h3>
                <p style="color: var(--text-secondary);">Contributors</p>
            </div>
            <div class="glass-card" style="text-align: center;">
                <h3 style="font-size: 2.5rem; color: ${healthData.summary?.critical_issues > 0 ? 'var(--danger)' : 'var(--success)'}; margin-bottom: 0.5rem;">${healthData.summary?.critical_issues || 0}</h3>
                <p style="color: var(--text-secondary);">Critical Issues</p>
            </div>
            <div class="glass-card" style="text-align: center;">
                <h3 style="font-size: 2.5rem; color: ${healthData.summary?.warnings > 5 ? 'var(--warning)' : 'var(--success)'}; margin-bottom: 0.5rem;">${healthData.summary?.warnings || 0}</h3>
                <p style="color: var(--text-secondary);">Warnings</p>
            </div>
        </div>
        
        <!-- Quick Links -->
        <div class="glass-card">
            <h3 style="margin-bottom: 1.5rem;">🔗 Quick Access</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">
                <button class="btn" onclick="switchTab('tech-stack')" style="padding: 1rem;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🛠️</div>
                    <div style="font-size: 0.875rem;">Tech Stack</div>
                </button>
                <button class="btn" onclick="switchTab('security')" style="padding: 1rem;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔒</div>
                    <div style="font-size: 0.875rem;">Security</div>
                </button>
                <button class="btn" onclick="switchTab('architecture')" style="padding: 1rem;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🏗️</div>
                    <div style="font-size: 0.875rem;">Architecture</div>
                </button>
                <button class="btn" onclick="switchTab('code-org')" style="padding: 1rem;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📁</div>
                    <div style="font-size: 0.875rem;">Code Org</div>
                </button>
                <button class="btn" onclick="switchTab('vendors')" style="padding: 1rem;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔌</div>
                    <div style="font-size: 0.875rem;">Dependencies</div>
                </button>
            </div>
        </div>
        
        <!-- Trends -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin-top: 2rem;">
            <div class="glass-card">
                <h4 style="margin-bottom: 1rem;">📈 Health Trend</h4>
                <p style="font-size: 1.25rem; color: ${healthData.trends?.health_trend === 'improving' ? 'var(--success)' : healthData.trends?.health_trend === 'declining' ? 'var(--danger)' : 'var(--warning)'};">
                    ${getTrendIcon(healthData.trends?.health_trend)} ${capitalizeFirst(healthData.trends?.health_trend || 'stable')}
                </p>
            </div>
            <div class="glass-card">
                <h4 style="margin-bottom: 1rem;">📈 Velocity Trend</h4>
                <p style="font-size: 1.25rem; color: ${healthData.trends?.velocity_trend === 'improving' ? 'var(--success)' : healthData.trends?.velocity_trend === 'declining' ? 'var(--danger)' : 'var(--warning)'};">
                    ${getTrendIcon(healthData.trends?.velocity_trend)} ${capitalizeFirst(healthData.trends?.velocity_trend || 'stable')}
                </p>
            </div>
            <div class="glass-card">
                <h4 style="margin-bottom: 1rem;">📈 Quality Trend</h4>
                <p style="font-size: 1.25rem; color: ${healthData.trends?.quality_trend === 'improving' ? 'var(--success)' : healthData.trends?.quality_trend === 'declining' ? 'var(--danger)' : 'var(--warning)'};">
                    ${getTrendIcon(healthData.trends?.quality_trend)} ${capitalizeFirst(healthData.trends?.quality_trend || 'stable')}
                </p>
            </div>
        </div>
    `;
    
    // Show spinner then render health gauge
    const gaugeContainer = document.getElementById('health-gauge');
    if (gaugeContainer) {
        showPanelSpinner(gaugeContainer, 'Loading health score...');
    }
    
    // Render health gauge after brief delay to show spinner
    setTimeout(() => {
        renderHealthGauge(healthData.overall_health_score || 0);
    }, 300);
}

/**
 * Render health score gauge using D3.js
 * @param {number} score - Health score (0-100)
 */
function renderHealthGauge(score) {
    const container = document.getElementById('health-gauge');
    if (!container) return;
    
    // Clear previous content (including spinner)
    container.innerHTML = '';
    
    const width = container.clientWidth;
    const height = 400;
    const radius = Math.min(width, height) / 2 - 30;
    
    const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .append('g')
        .attr('transform', `translate(${width / 2}, ${height / 2})`);
    
    // Background arc
    const backgroundArc = d3.arc()
        .innerRadius(radius - 30)
        .outerRadius(radius)
        .startAngle(-Math.PI / 2)
        .endAngle(Math.PI / 2);
    
    svg.append('path')
        .attr('d', backgroundArc)
        .attr('fill', 'rgba(255, 255, 255, 0.1)');
    
    // Score arc
    const scoreAngle = -Math.PI / 2 + (score / 100) * Math.PI;
    const scoreArc = d3.arc()
        .innerRadius(radius - 30)
        .outerRadius(radius)
        .startAngle(-Math.PI / 2)
        .endAngle(scoreAngle);
    
    // Color based on score
    let color = '#00ff88'; // Green
    if (score < 50) color = '#ff4444'; // Red
    else if (score < 75) color = '#ffa500'; // Orange
    
    svg.append('path')
        .attr('d', scoreArc)
        .attr('fill', color)
        .attr('opacity', 0.8);
    
    // Score text - larger and more prominent
    svg.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', '0.1em')
        .style('font-size', '5rem')
        .style('font-weight', '800')
        .style('fill', color)
        .style('text-shadow', `0 0 20px ${color}40`)
        .text(score);
    
    svg.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', '3.2em')
        .style('font-size', '1.125rem')
        .style('font-weight', '500')
        .style('fill', 'var(--text-secondary)')
        .text('Health Score');
}

/**
 * Helper: Get status color
 */
function getStatusColor(status) {
    const colors = {
        healthy: 'rgba(0, 255, 136, 0.2)',
        warning: 'rgba(255, 165, 0, 0.2)',
        critical: 'rgba(255, 68, 68, 0.2)',
        unknown: 'rgba(255, 255, 255, 0.1)'
    };
    return colors[status] || colors.unknown;
}

/**
 * Helper: Format timestamp
 */
function formatTimestamp(timestamp) {
    if (!timestamp) return 'Never';
    const date = new Date(timestamp);
    return date.toLocaleString();
}

/**
 * Helper: Format number with commas
 */
function formatNumber(num) {
    return num.toLocaleString();
}

/**
 * Helper: Get trend icon
 */
function getTrendIcon(trend) {
    const icons = {
        improving: '📈',
        declining: '📉',
        stable: '➡️'
    };
    return icons[trend] || '➡️';
}

/**
 * Helper: Capitalize first letter
 */
function capitalizeFirst(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Show overview metric tooltip with explanation and recommendations
 * @param {Event} event - Mouse event
 * @param {string} metricName - Name of the metric
 * @param {number} score - Metric score
 * @param {string} metricType - Type of metric for contextual info
 * @param {HTMLElement} card - Card element
 */
window.showOverviewTooltip = function(event, metricName, score, metricType, card) {
    hideOverviewTooltip();
    
    let scoreColor = 'var(--success)';
    let scoreLabel = 'Excellent';
    let scoreIcon = '🟢';
    
    if (score < 50) {
        scoreColor = 'var(--danger)';
        scoreLabel = 'Critical';
        scoreIcon = '🔴';
    } else if (score < 75) {
        scoreColor = 'var(--warning)';
        scoreLabel = 'Needs Improvement';
        scoreIcon = '🟡';
    } else if (score < 90) {
        scoreColor = 'var(--info)';
        scoreLabel = 'Good';
        scoreIcon = '🟢';
    }
    
    // Generate metric-specific explanations
    const metricInfo = {
        code_quality: {
            description: 'Measures cyclomatic complexity, code duplication, maintainability index, and adherence to coding standards.',
            factors: ['Cyclomatic Complexity', 'Code Duplication %', 'Maintainability Index', 'Coding Standards Compliance'],
            recommendations: score < 75 
                ? 'Refactor complex methods, eliminate code duplication, improve naming conventions, add documentation.'
                : 'Continue following best practices, perform regular code reviews, maintain consistent style guide adherence.'
        },
        security: {
            description: 'Evaluates OWASP compliance, vulnerability count, authentication/authorization patterns, and dependency security.',
            factors: ['OWASP Top 10 Compliance', 'Known CVEs', 'Authentication Strength', 'Dependency Security'],
            recommendations: score < 75
                ? '⚠️ Address identified vulnerabilities immediately. Update insecure dependencies. Review authentication mechanisms.'
                : 'Monitor for new CVEs, schedule regular security audits, keep dependencies updated.'
        },
        test_coverage: {
            description: 'Percentage of code covered by automated tests (unit, integration, end-to-end).',
            factors: ['Unit Test Coverage', 'Integration Test Coverage', 'Critical Path Coverage', 'Edge Case Coverage'],
            recommendations: score < 75
                ? 'Prioritize testing critical business logic. Add tests for edge cases. Aim for 80%+ coverage on core modules.'
                : 'Maintain coverage levels, focus on testing new features, consider mutation testing.'
        },
        documentation: {
            description: 'Assesses code comments, README quality, API documentation, and architectural decision records.',
            factors: ['Inline Comments', 'API Documentation', 'README Completeness', 'Architecture Docs'],
            recommendations: score < 75
                ? 'Add XML comments to public APIs. Create/update README with setup instructions. Document architectural decisions.'
                : 'Keep documentation in sync with code changes, maintain changelog, document design patterns used.'
        }
    };
    
    const info = metricInfo[metricType] || {
        description: `${metricName} measures overall project health across multiple dimensions.`,
        factors: ['Multiple factors contribute to this score'],
        recommendations: score < 75 
            ? 'Review individual metric tabs for detailed recommendations.'
            : 'Continue maintaining high standards across all metrics.'
    };
    
    const tooltip = document.createElement('div');
    tooltip.id = 'overview-tooltip';
    tooltip.innerHTML = `
        <div style="
            position: fixed;
            background: linear-gradient(135deg, var(--glass-dark) 0%, var(--background-primary) 100%);
            border: 2px solid ${scoreColor};
            border-radius: 12px;
            padding: 1.25rem;
            max-width: 500px;
            box-shadow: 0 12px 40px rgba(0,0,0,0.4);
            z-index: 10000;
            animation: tooltipFadeIn 0.2s ease-out;
        ">
            <!-- Header -->
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem; padding-bottom: 0.75rem; border-bottom: 1px solid var(--glass-border);">
                <div style="font-size: 1.5rem;">${scoreIcon}</div>
                <div style="flex: 1;">
                    <div style="font-weight: 600; font-size: 1.125rem; margin-bottom: 0.25rem;">${metricName}</div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary);">Score: ${score}/100</div>
                </div>
                <div style="
                    padding: 0.375rem 0.75rem;
                    border-radius: 8px;
                    background: ${scoreColor}22;
                    color: ${scoreColor};
                    font-size: 0.75rem;
                    font-weight: 600;
                    white-space: nowrap;
                ">
                    ${scoreLabel}
                </div>
            </div>
            
            <!-- Description -->
            <div style="margin-bottom: 1rem;">
                <div style="font-weight: 600; font-size: 0.875rem; margin-bottom: 0.5rem; color: var(--text-primary);">
                    📊 What This Measures
                </div>
                <div style="font-size: 0.875rem; color: var(--text-secondary); line-height: 1.5;">
                    ${info.description}
                </div>
            </div>
            
            <!-- Contributing Factors -->
            <div style="background: var(--glass-light); border-radius: 8px; padding: 0.75rem; margin-bottom: 0.75rem;">
                <div style="font-weight: 600; font-size: 0.875rem; margin-bottom: 0.5rem; color: var(--text-primary);">
                    🎯 Contributing Factors
                </div>
                <ul style="margin: 0; padding-left: 1.25rem; font-size: 0.875rem; color: var(--text-secondary); line-height: 1.6;">
                    ${info.factors.map(factor => `<li>${factor}</li>`).join('')}
                </ul>
            </div>
            
            <!-- Score Interpretation -->
            <div style="background: var(--glass-light); border-radius: 8px; padding: 0.75rem; margin-bottom: 0.75rem;">
                <div style="font-weight: 600; font-size: 0.875rem; margin-bottom: 0.5rem; color: var(--text-primary);">
                    📈 Score Interpretation
                </div>
                <div style="display: grid; gap: 0.25rem; font-size: 0.75rem;">
                    <div style="color: var(--success);">🟢 90-100: Excellent - Industry best practices</div>
                    <div style="color: var(--info);">🟢 75-89: Good - Minor improvements possible</div>
                    <div style="color: var(--warning);">🟡 50-74: Needs Work - Significant issues present</div>
                    <div style="color: var(--danger);">🔴 0-49: Critical - Immediate action required</div>
                </div>
            </div>
            
            <!-- Recommendations -->
            <div style="
                background: ${scoreColor}11;
                border: 1px solid ${scoreColor};
                border-radius: 8px;
                padding: 0.75rem;
            ">
                <div style="font-weight: 600; font-size: 0.875rem; margin-bottom: 0.5rem; color: ${scoreColor};">
                    💡 Recommendations
                </div>
                <div style="font-size: 0.875rem; color: var(--text-secondary); line-height: 1.5;">
                    ${info.recommendations}
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(tooltip);
    
    // Position tooltip
    const tooltipRect = tooltip.firstElementChild.getBoundingClientRect();
    const cardRect = card.getBoundingClientRect();
    
    let left = cardRect.right + 10;
    let top = cardRect.top;
    
    if (left + tooltipRect.width > window.innerWidth) {
        left = cardRect.left - tooltipRect.width - 10;
    }
    
    if (top + tooltipRect.height > window.innerHeight) {
        top = window.innerHeight - tooltipRect.height - 10;
    }
    
    if (top < 10) top = 10;
    
    tooltip.firstElementChild.style.left = `${left}px`;
    tooltip.firstElementChild.style.top = `${top}px`;
    
    // Add hover effect to card
    card.style.transform = 'translateY(-4px)';
    card.style.boxShadow = `0 8px 24px ${scoreColor}33`;
};

/**
 * Hide overview tooltip
 * @param {HTMLElement} card - Card element
 */
window.hideOverviewTooltip = function(card) {
    const tooltip = document.getElementById('overview-tooltip');
    if (tooltip) tooltip.remove();
    
    if (card) {
        card.style.transform = 'translateY(0)';
        card.style.boxShadow = 'none';
    }
};

/**
 * Show overview metric tooltip
 * @param {Event} event - Mouse event
 * @param {string} metricName - Metric name
 * @param {number} score - Metric score
 * @param {string} metricType - Type of metric
 * @param {HTMLElement} element - Hovered element
 */
window.showOverviewTooltip = function(event, metricName, score, metricType, element) {
    // Add hover effect
    element.style.transform = 'translateY(-4px)';
    element.style.boxShadow = '0 8px 24px rgba(0, 0, 0, 0.3)';
    
    // Remove existing tooltip
    const existing = document.getElementById('overview-tooltip');
    if (existing) {
        existing.remove();
    }
    
    // Determine status
    let statusIcon = '🟢';
    let statusLabel = 'Excellent';
    let statusColor = 'var(--success)';
    
    if (score < 50) {
        statusIcon = '🔴';
        statusLabel = 'Critical';
        statusColor = 'var(--danger)';
    } else if (score < 75) {
        statusIcon = '🟡';
        statusLabel = 'Needs Improvement';
        statusColor = 'var(--warning)';
    } else if (score < 90) {
        statusIcon = '🟢';
        statusLabel = 'Good';
        statusColor = 'var(--success)';
    }
    
    // Build explanation based on metric type
    let explanation = '';
    let methodology = '';
    let recommendation = '';
    
    switch (metricType) {
        case 'code_quality':
            explanation = `Measures code maintainability, complexity, and adherence to best practices. `;
            explanation += `Your score of ${score}/100 indicates ${score >= 75 ? 'well-structured, maintainable code' : score >= 50 ? 'code that could benefit from refactoring' : 'significant technical debt requiring immediate attention'}.`;
            methodology = 'Calculated from cyclomatic complexity, code duplication, method length, and SOLID principles compliance.';
            recommendation = score < 75 
                ? 'Focus on reducing complexity in hotspots, extracting large methods, and eliminating code duplication.'
                : 'Maintain current standards. Continue code reviews and refactoring practices.';
            break;
            
        case 'security':
            explanation = `Evaluates vulnerability exposure across OWASP Top 10 2025 categories. `;
            explanation += `A score of ${score}/100 ${score >= 90 ? 'indicates strong security posture' : score >= 70 ? 'suggests some security gaps need attention' : 'reveals critical vulnerabilities requiring immediate remediation'}.`;
            methodology = 'Based on OWASP compliance scores, CVE counts, exposed secrets, weak cryptography, and input validation gaps.';
            recommendation = score < 90 
                ? 'Review Security tab for specific vulnerabilities. Address critical findings first, then implement preventive controls.'
                : 'Excellent security posture. Maintain regular audits and dependency updates.';
            break;
            
        case 'test_coverage':
            explanation = `Indicates percentage of code exercised by automated tests. `;
            explanation += `${score}% coverage ${score >= 80 ? 'provides strong confidence in code reliability' : score >= 60 ? 'offers moderate protection but has gaps' : 'leaves significant portions untested and vulnerable to regressions'}.`;
            methodology = 'Calculated from unit test line/branch coverage, integration test coverage, and critical path coverage.';
            recommendation = score < 80 
                ? 'Prioritize testing for critical business logic, hotspots, and frequently changed files. Target 80%+ coverage.'
                : 'Strong test coverage. Focus on edge cases and integration scenarios.';
            break;
            
        case 'documentation':
            explanation = `Assesses completeness and quality of code documentation. `;
            explanation += `${score}/100 means ${score >= 75 ? 'most code is well-documented' : score >= 50 ? 'documentation exists but has gaps' : 'significant documentation deficiencies exist'}.`;
            methodology = 'Evaluated from XML doc comments, README files, API documentation, and inline comment density.';
            recommendation = score < 75 
                ? 'Add XML comments to public APIs, document complex algorithms, and maintain README with architecture overview.'
                : 'Good documentation practices. Ensure new code maintains these standards.';
            break;
    }
    
    // Create tooltip
    const tooltip = document.createElement('div');
    tooltip.id = 'overview-tooltip';
    tooltip.style.cssText = `
        position: fixed;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.98) 0%, rgba(30, 41, 59, 0.98) 100%);
        border: 1px solid ${statusColor};
        border-radius: 12px;
        padding: 1.25rem;
        max-width: 500px;
        z-index: 10000;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        pointer-events: none;
        animation: tooltipFadeIn 0.2s ease-out;
        backdrop-filter: blur(10px);
    `;
    
    tooltip.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem; padding-bottom: 1rem; border-top: 1px solid var(--glass-border);">
            <div style="font-size: 2rem;">${statusIcon}</div>
            <div style="flex: 1;">
                <div style="font-weight: 700; font-size: 1.1rem; color: var(--text-primary); margin-bottom: 0.25rem;">
                    ${metricName}
                </div>
                <div style="font-size: 0.875rem; color: var(--text-secondary);">
                    Score: <strong style="color: ${statusColor};">${score}/100</strong>
                </div>
            </div>
        </div>
        
        <div style="margin-bottom: 1rem;">
            <div style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; background: ${statusColor}22; border-radius: 8px;">
                <span style="font-size: 1.25rem;">${statusIcon}</span>
                <span style="color: ${statusColor}; font-weight: 600; font-size: 0.875rem;">
                    ${statusLabel}
                </span>
            </div>
        </div>
        
        <div style="margin-bottom: 1rem;">
            <div style="color: var(--accent-primary); font-size: 0.875rem; font-weight: 600; margin-bottom: 0.5rem;">
                📊 What This Means
            </div>
            <div style="color: var(--text-secondary); line-height: 1.6; font-size: 0.875rem;">
                ${explanation}
            </div>
        </div>
        
        <div style="margin-bottom: 1rem; padding: 1rem; background: rgba(0,0,0,0.2); border-radius: 8px;">
            <div style="color: var(--accent-primary); font-size: 0.875rem; font-weight: 600; margin-bottom: 0.5rem;">
                🔍 Scoring Methodology
            </div>
            <div style="color: var(--text-secondary); line-height: 1.6; font-size: 0.875rem;">
                ${methodology}
            </div>
        </div>
        
        <div style="padding-top: 1rem; border-top: 1px solid var(--glass-border);">
            <div style="color: var(--accent-primary); font-size: 0.875rem; font-weight: 600; margin-bottom: 0.5rem;">
                💡 Recommended Action
            </div>
            <div style="color: var(--text-secondary); line-height: 1.6; font-size: 0.875rem;">
                ${recommendation}
            </div>
        </div>
    `;
    
    document.body.appendChild(tooltip);
    
    // Position tooltip
    const rect = element.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();
    
    let left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
    let top = rect.top - tooltipRect.height - 12;
    
    // Keep tooltip on screen
    if (left < 10) left = 10;
    if (left + tooltipRect.width > window.innerWidth - 10) {
        left = window.innerWidth - tooltipRect.width - 10;
    }
    
    if (top < 10) {
        top = rect.bottom + 12;
    }
    
    tooltip.style.left = left + 'px';
    tooltip.style.top = top + 'px';
};

/**
 * Hide overview metric tooltip
 * @param {HTMLElement} element - Hovered element
 */
window.hideOverviewTooltip = function(element) {
    // Remove hover effect
    element.style.transform = '';
    element.style.boxShadow = '';
    
    // Remove tooltip
    const tooltip = document.getElementById('overview-tooltip');
    if (tooltip) {
        tooltip.remove();
    }
};
