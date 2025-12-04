/**
 * Team Metrics Tab Component
 * 
 * Renders team productivity metrics with Chart.js graphs.
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Source-Available (Use Allowed, No Contributions)
 */

import { showPanelSpinner } from '../shared-utils.js';

/**
 * Render team metrics tab
 * @param {Object} data - Dashboard data containing team metrics information
 */
export function renderTeamMetrics(data) {
    const container = document.getElementById('team-container');
    if (!container) {
        console.error('Team container not found');
        return;
    }
    
    showPanelSpinner(container, 'Loading team metrics...');
    
    setTimeout(() => {
        const teamMetrics = data.teamMetrics || {};
    const summary = teamMetrics.summary || {};
    const contributors = teamMetrics.contributors || [];
    const velocity = teamMetrics.velocity || {};
    const busFactor = teamMetrics.bus_factor || {};
    
    // Build HTML
    container.innerHTML = `
        <div class="view-header">
            <h2>👥 Team Productivity</h2>
            <div class="header-actions">
                <button class="btn-secondary" onclick="exportTeamMetrics()">Export Report</button>
            </div>
        </div>

        <!-- Summary Cards -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
            <div class="glass-card" style="display: flex; align-items: center; gap: 1rem; padding: 1.5rem;">
                <div style="font-size: 2.5rem;">👥</div>
                <div>
                    <h3 style="font-size: 2rem; margin: 0; color: var(--accent-primary);">
                        ${summary.total_contributors || 0}
                    </h3>
                    <p style="margin: 0.25rem 0 0 0; color: var(--text-secondary);">Total Contributors</p>
                </div>
            </div>
            
            <div class="glass-card" style="display: flex; align-items: center; gap: 1rem; padding: 1.5rem;">
                <div style="font-size: 2.5rem;">✅</div>
                <div>
                    <h3 style="font-size: 2rem; margin: 0; color: var(--success);">
                        ${summary.active_contributors || 0}
                    </h3>
                    <p style="margin: 0.25rem 0 0 0; color: var(--text-secondary);">Active Contributors</p>
                </div>
            </div>
            
            <div class="glass-card" style="display: flex; align-items: center; gap: 1rem; padding: 1.5rem;">
                <div style="font-size: 2.5rem;">📝</div>
                <div>
                    <h3 style="font-size: 2rem; margin: 0; color: var(--accent-primary);">
                        ${summary.total_commits || 0}
                    </h3>
                    <p style="margin: 0.25rem 0 0 0; color: var(--text-secondary);">Total Commits</p>
                </div>
            </div>
            
            <div class="glass-card" style="display: flex; align-items: center; gap: 1rem; padding: 1.5rem;">
                <div style="font-size: 2.5rem;">📊</div>
                <div>
                    <h3 style="font-size: 2rem; margin: 0; color: var(--accent-primary);">
                        ${(summary.avg_commits_per_contributor || 0).toFixed(1)}
                    </h3>
                    <p style="margin: 0.25rem 0 0 0; color: var(--text-secondary);">Avg Commits/Person</p>
                </div>
            </div>
        </div>

        <!-- Velocity and Bus Factor Row -->
        <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 2rem; margin-bottom: 2rem;">
            <!-- Velocity Trends -->
            <div class="glass-card">
                <h3 style="margin-bottom: 1rem;">📈 Velocity Trends</h3>
                <div style="display: flex; gap: 2rem; margin-bottom: 1.5rem;">
                    <div>
                        <span style="color: var(--text-secondary); font-size: 0.875rem;">Commits/Week:</span>
                        <span style="font-size: 1.5rem; font-weight: 600; margin-left: 0.5rem;">
                            ${(velocity.commits_per_week || 0).toFixed(1)}
                        </span>
                    </div>
                    <div>
                        <span style="color: var(--text-secondary); font-size: 0.875rem;">Trend:</span>
                        <span style="font-size: 1.25rem; font-weight: 600; margin-left: 0.5rem; color: ${getTrendColor(velocity.trend)};">
                            ${getTrendIcon(velocity.trend)} ${(velocity.trend || 'stable').charAt(0).toUpperCase() + (velocity.trend || 'stable').slice(1)}
                        </span>
                    </div>
                </div>
                <canvas id="velocity-chart" style="max-height: 200px;"></canvas>
            </div>

            <!-- Bus Factor -->
            <div class="glass-card">
                <h3 style="margin-bottom: 1rem;">🚍 Bus Factor</h3>
                <p style="color: var(--text-secondary); font-size: 0.875rem; margin-bottom: 1.5rem;">
                    Team members whose absence would cripple the project
                </p>
                <div style="text-align: center; margin: 2rem 0;">
                    <div style="font-size: 4rem; font-weight: bold; color: ${getBusFactorColor(busFactor.risk)};">
                        ${busFactor.factor || 1}
                    </div>
                    <div style="
                        display: inline-block;
                        padding: 0.5rem 1rem;
                        border-radius: 12px;
                        font-weight: 600;
                        background: ${getBusFactorColor(busFactor.risk)}22;
                        color: ${getBusFactorColor(busFactor.risk)};
                        margin-top: 0.5rem;
                    ">
                        ${(busFactor.risk || 'medium').toUpperCase()} RISK
                    </div>
                </div>
            </div>
        </div>

        <!-- Contributors Table -->
        <div class="glass-card">
            <h3 style="margin-bottom: 1.5rem;">👤 Contributor Breakdown</h3>
            <div style="overflow-x: auto;">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="border-bottom: 1px solid var(--glass-border);">
                            <th style="padding: 1rem; text-align: left; color: var(--text-secondary); font-weight: 600;">Contributor</th>
                            <th style="padding: 1rem; text-align: left; color: var(--text-secondary); font-weight: 600;">Commits</th>
                            <th style="padding: 1rem; text-align: left; color: var(--text-secondary); font-weight: 600;">Lines Added</th>
                            <th style="padding: 1rem; text-align: left; color: var(--text-secondary); font-weight: 600;">Lines Removed</th>
                            <th style="padding: 1rem; text-align: left; color: var(--text-secondary); font-weight: 600;">Files Changed</th>
                            <th style="padding: 1rem; text-align: left; color: var(--text-secondary); font-weight: 600;">Active Period</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${contributors.slice(0, 15).map(contributor => renderContributorRow(contributor)).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;
        
        // Initialize charts after DOM is updated
        setTimeout(() => {
            initVelocityChart(velocity);
        }, 100);
    }, 250);
}

/**
 * Render contributor row
 * @param {Object} contributor - Contributor object
 * @returns {string} HTML string
 */
function renderContributorRow(contributor) {
    return `
        <tr style="border-bottom: 1px solid var(--glass-border);">
            <td style="padding: 1rem; font-weight: 600;">
                ${contributor.name || 'Unknown'}
            </td>
            <td style="padding: 1rem;">
                <span style="
                    padding: 0.25rem 0.75rem;
                    border-radius: 12px;
                    background: var(--accent-primary)22;
                    color: var(--accent-primary);
                    font-weight: 600;
                ">${contributor.commits || 0}</span>
            </td>
            <td style="padding: 1rem; color: var(--success);">
                +${(contributor.lines_added || 0).toLocaleString()}
            </td>
            <td style="padding: 1rem; color: var(--danger);">
                -${(contributor.lines_removed || 0).toLocaleString()}
            </td>
            <td style="padding: 1rem; color: var(--text-secondary);">
                ${contributor.files_changed || 0}
            </td>
            <td style="padding: 1rem; font-size: 0.875rem; color: var(--text-secondary);">
                ${contributor.first_commit || 'N/A'} to ${contributor.last_commit || 'N/A'}
            </td>
        </tr>
    `;
}

/**
 * Get trend icon
 * @param {string} trend - Trend value
 * @returns {string} Icon
 */
function getTrendIcon(trend) {
    if (trend === 'increasing') return '↑';
    if (trend === 'decreasing') return '↓';
    return '→';
}

/**
 * Get trend color
 * @param {string} trend - Trend value
 * @returns {string} Color
 */
function getTrendColor(trend) {
    if (trend === 'increasing') return 'var(--success)';
    if (trend === 'decreasing') return 'var(--danger)';
    return 'var(--warning)';
}

/**
 * Get bus factor color
 * @param {string} risk - Risk level
 * @returns {string} Color
 */
function getBusFactorColor(risk) {
    if (risk === 'critical') return 'var(--danger)';
    if (risk === 'high') return 'var(--warning)';
    if (risk === 'medium') return '#fbbf24';
    return 'var(--success)';
}

/**
 * Initialize velocity chart with Chart.js
 * @param {Object} velocity - Velocity data
 */
function initVelocityChart(velocity) {
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js not loaded, skipping velocity chart');
        return;
    }
    
    const canvas = document.getElementById('velocity-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Sample data - in real implementation, this would come from velocity object
    const labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6'];
    const dataPoints = velocity.weekly_commits || [45, 52, 38, 61, 55, 48];
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Commits per Week',
                data: dataPoints,
                borderColor: '#00d4ff',
                backgroundColor: 'rgba(0, 212, 255, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#94a3b8'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: '#94a3b8'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });
}

/**
 * Export team metrics (placeholder)
 */
window.exportTeamMetrics = function() {
    console.log('Export team metrics');
    alert('Team metrics export functionality coming soon!');
};
