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
            <div class="glass-card">
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
            <div class="glass-card">
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
            <div class="glass-card">
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
            <div class="glass-card">
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
                <button class="btn" onclick="switchTab('team')" style="padding: 1rem;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">👥</div>
                    <div style="font-size: 0.875rem;">Team</div>
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
