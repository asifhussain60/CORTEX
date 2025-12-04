/**
 * Security Tab Component
 * 
 * Renders security dashboard with D3.js gauge, vulnerability breakdown, and OWASP compliance.
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Source-Available (Use Allowed, No Contributions)
 */

import { showPanelSpinner } from '../shared-utils.js';

/**
 * Render security tab
 * @param {Object} data - Dashboard data containing security information
 */
export function renderSecurity(data) {
    const container = document.getElementById('security-container');
    if (!container) {
        console.error('Security container not found');
        return;
    }
    
    // Show loading spinner
    showPanelSpinner(container, 'Loading security analysis...');
    
    // Render after brief delay to show spinner
    setTimeout(() => {
        const security = data.security || {};
    const score = security.overall_score || 0;
    const vulnerabilities = security.vulnerabilities || {};
    
    // Handle owasp_top_10 structure - can be object with categories or direct array (legacy)
    let owaspTop10 = [];
    if (security.owasp_top_10) {
        if (Array.isArray(security.owasp_top_10)) {
            // Legacy format: direct array
            owaspTop10 = security.owasp_top_10;
        } else if (security.owasp_top_10.categories && Array.isArray(security.owasp_top_10.categories)) {
            // New format: object with categories array
            owaspTop10 = security.owasp_top_10.categories;
        }
    }
    
    const compliance = security.compliance || {};
    
    // Build HTML
    container.innerHTML = `
        <div class="view-header">
            <h2>🔒 Security Dashboard</h2>
            <div class="header-actions">
                <button class="btn-secondary" onclick="refreshSecurityScan()">🔄 Refresh Scan</button>
            </div>
        </div>

        <!-- Security Score and Vulnerabilities -->
        <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 2rem; margin-bottom: 2rem;">
            <!-- Score Gauge -->
            <div class="glass-card" style="text-align: center; padding: 2rem;">
                <h3 style="margin-bottom: 1.5rem;">Overall Security Score</h3>
                <div id="security-gauge-container" style="width: 100%; height: 200px; position: relative;">
                    <svg id="security-gauge" width="300" height="200" style="margin: 0 auto;"></svg>
                </div>
                <div style="font-size: 2rem; font-weight: bold; margin-top: 1rem; color: ${getScoreColor(score)};">
                    ${score}/100
                </div>
                <p style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">
                    Last scan: ${security.last_scan || 'N/A'}
                </p>
            </div>

            <!-- Vulnerability Summary -->
            <div class="glass-card" style="padding: 2rem;">
                <h3 style="margin-bottom: 1.5rem;">Vulnerability Breakdown</h3>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem;">
                    <div style="text-align: center; padding: 1rem; border-radius: 8px; background: rgba(239, 68, 68, 0.1);">
                        <div style="font-size: 2rem; font-weight: bold; color: #ef4444;">
                            ${vulnerabilities.critical || 0}
                        </div>
                        <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Critical</div>
                    </div>
                    <div style="text-align: center; padding: 1rem; border-radius: 8px; background: rgba(245, 158, 11, 0.1);">
                        <div style="font-size: 2rem; font-weight: bold; color: #f59e0b;">
                            ${vulnerabilities.high || 0}
                        </div>
                        <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">High</div>
                    </div>
                    <div style="text-align: center; padding: 1rem; border-radius: 8px; background: rgba(251, 191, 36, 0.1);">
                        <div style="font-size: 2rem; font-weight: bold; color: #fbbf24;">
                            ${vulnerabilities.medium || 0}
                        </div>
                        <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Medium</div>
                    </div>
                    <div style="text-align: center; padding: 1rem; border-radius: 8px; background: rgba(16, 185, 129, 0.1);">
                        <div style="font-size: 2rem; font-weight: bold; color: #10b981;">
                            ${vulnerabilities.low || 0}
                        </div>
                        <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Low</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- OWASP Top 10 Compliance -->
        <div class="glass-card" style="margin-bottom: 2rem;">
            <h3 style="margin-bottom: 1.5rem;">🛡️ OWASP Top 10 (2021) Compliance</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 1rem;">
                ${owaspTop10.map(item => renderOwaspItem(item)).join('')}
            </div>
        </div>

        <!-- Compliance Status -->
        <div class="glass-card">
            <h3 style="margin-bottom: 1.5rem;">📋 Compliance Status</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem;">
                ${renderComplianceCard('GDPR', compliance.gdpr_ready)}
                ${renderComplianceCard('SOC 2', compliance.soc2_ready)}
                ${renderComplianceCard('HIPAA', compliance.hipaa_ready)}
                ${renderComplianceCard('PCI DSS', compliance.pci_dss_ready)}
            </div>
        </div>
    `;
        
        // Draw the gauge after DOM is updated
        setTimeout(() => drawSecurityGauge(score), 100);
    }, 250);
}

/**
 * Render OWASP Top 10 item
 * @param {Object} item - OWASP item object
 * @returns {string} HTML string
 */
function renderOwaspItem(item) {
    const statusConfig = {
        pass: { icon: '✅', color: '#10b981' },
        warn: { icon: '⚠️', color: '#f59e0b' },
        fail: { icon: '❌', color: '#ef4444' }
    };
    
    const status = statusConfig[item.status] || statusConfig.pass;
    const itemScore = item.score || 0;
    
    return `
        <div style="
            padding: 1rem;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.05);
            border-left: 4px solid ${status.color};
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-weight: bold; color: var(--accent-primary);">
                    ${item.risk?.split('_')[0] || 'A01'}
                </span>
                <span style="font-size: 1.25rem;">${status.icon}</span>
            </div>
            <div style="font-size: 0.9rem; color: var(--text-primary); margin-bottom: 0.5rem;">
                ${item.name || 'Unknown Risk'}
            </div>
            <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                Score: ${itemScore}/100
            </div>
            <div style="height: 4px; background: rgba(255, 255, 255, 0.1); border-radius: 2px; overflow: hidden;">
                <div style="
                    height: 100%;
                    width: ${itemScore}%;
                    background: ${status.color};
                    transition: width 0.3s ease;
                "></div>
            </div>
        </div>
    `;
}

/**
 * Render compliance card
 * @param {string} name - Compliance name
 * @param {boolean} ready - Compliance ready status
 * @returns {string} HTML string
 */
function renderComplianceCard(name, ready) {
    const icon = ready ? '✅' : '⚠️';
    const status = ready ? 'Ready' : 'Not Ready';
    const borderColor = ready ? '#10b981' : '#f59e0b';
    
    return `
        <div style="
            text-align: center;
            padding: 2rem;
            border: 2px solid ${borderColor};
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.02);
        ">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">${icon}</div>
            <div style="font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">
                ${name}
            </div>
            <div style="font-size: 0.875rem; color: var(--text-secondary);">
                ${status}
            </div>
        </div>
    `;
}

/**
 * Get color based on score
 * @param {number} score - Security score (0-100)
 * @returns {string} Color value
 */
function getScoreColor(score) {
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#f59e0b';
    return '#ef4444';
}

/**
 * Draw security gauge with D3.js
 * @param {number} score - Security score (0-100)
 */
function drawSecurityGauge(score) {
    // Check if D3 is available
    if (typeof d3 === 'undefined') {
        console.warn('D3.js not loaded, skipping gauge rendering');
        return;
    }
    
    const svg = d3.select("#security-gauge");
    svg.selectAll("*").remove(); // Clear previous content
    
    const width = 300;
    const height = 200;
    const radius = Math.min(width, height) / 2 - 20;

    const arc = d3.arc()
        .innerRadius(radius - 30)
        .outerRadius(radius)
        .startAngle(-Math.PI / 2)
        .endAngle((score / 100) * Math.PI - Math.PI / 2);

    const background = d3.arc()
        .innerRadius(radius - 30)
        .outerRadius(radius)
        .startAngle(-Math.PI / 2)
        .endAngle(Math.PI / 2);

    const g = svg.append("g")
        .attr("transform", `translate(${width / 2}, ${height / 2})`);

    // Background arc
    g.append("path")
        .attr("d", background)
        .style("fill", "rgba(255, 255, 255, 0.1)");

    // Score arc with animation
    g.append("path")
        .attr("d", arc)
        .style("fill", getScoreColor(score))
        .style("opacity", 0)
        .transition()
        .duration(1000)
        .style("opacity", 1);
}

/**
 * Refresh security scan (placeholder)
 */
window.refreshSecurityScan = function() {
    console.log('Refresh security scan');
    alert('Security scan refresh functionality coming soon!');
};
