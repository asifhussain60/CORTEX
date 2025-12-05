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
    
    // Handle owasp_top_10 structure - new format with metadata
    let owaspTop10 = [];
    let owaspVersion = '2025';
    let owaspCompliance = 0;
    
    if (security.owasp_top_10) {
        if (Array.isArray(security.owasp_top_10)) {
            // Legacy format: direct array
            owaspTop10 = security.owasp_top_10;
        } else if (security.owasp_top_10.categories && Array.isArray(security.owasp_top_10.categories)) {
            // New format: object with categories array
            owaspTop10 = security.owasp_top_10.categories;
            owaspVersion = security.owasp_top_10.version || '2025';
            owaspCompliance = security.owasp_top_10.overall_compliance || 0;
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
                    <div class="vuln-card" data-severity="critical" onclick="showVulnerabilityDetails('critical', ${vulnerabilities.critical || 0})" 
                        style="text-align: center; padding: 1rem; border-radius: 8px; background: rgba(239, 68, 68, 0.1); cursor: pointer; transition: transform 0.2s, box-shadow 0.2s;">
                        <div style="font-size: 2rem; font-weight: bold; color: #ef4444;">
                            ${vulnerabilities.critical || 0}
                        </div>
                        <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Critical</div>
                        ${vulnerabilities.critical > 0 ? '<div style="font-size: 0.75rem; color: #ef4444; margin-top: 0.25rem;">Click to view</div>' : ''}
                    </div>
                    <div class="vuln-card" data-severity="high" onclick="showVulnerabilityDetails('high', ${vulnerabilities.high || 0})" 
                        style="text-align: center; padding: 1rem; border-radius: 8px; background: rgba(245, 158, 11, 0.1); cursor: pointer; transition: transform 0.2s, box-shadow 0.2s;">
                        <div style="font-size: 2rem; font-weight: bold; color: #f59e0b;">
                            ${vulnerabilities.high || 0}
                        </div>
                        <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">High</div>
                        ${vulnerabilities.high > 0 ? '<div style="font-size: 0.75rem; color: #f59e0b; margin-top: 0.25rem;">Click to view</div>' : ''}
                    </div>
                    <div class="vuln-card" data-severity="medium" onclick="showVulnerabilityDetails('medium', ${vulnerabilities.medium || 0})" 
                        style="text-align: center; padding: 1rem; border-radius: 8px; background: rgba(251, 191, 36, 0.1); cursor: pointer; transition: transform 0.2s, box-shadow 0.2s;">
                        <div style="font-size: 2rem; font-weight: bold; color: #fbbf24;">
                            ${vulnerabilities.medium || 0}
                        </div>
                        <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Medium</div>
                        ${vulnerabilities.medium > 0 ? '<div style="font-size: 0.75rem; color: #fbbf24; margin-top: 0.25rem;">Click to view</div>' : ''}
                    </div>
                    <div class="vuln-card" data-severity="low" onclick="showVulnerabilityDetails('low', ${vulnerabilities.low || 0})" 
                        style="text-align: center; padding: 1rem; border-radius: 8px; background: rgba(16, 185, 129, 0.1); cursor: pointer; transition: transform 0.2s, box-shadow 0.2s;">
                        <div style="font-size: 2rem; font-weight: bold; color: #10b981;">
                            ${vulnerabilities.low || 0}
                        </div>
                        <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Low</div>
                        ${vulnerabilities.low > 0 ? '<div style="font-size: 0.75rem; color: #10b981; margin-top: 0.25rem;">Click to view</div>' : ''}
                    </div>
                </div>
                
                <!-- Vulnerability Details Modal Container -->
                <div id="vuln-details-container" style="margin-top: 1.5rem; display: none;">
                    <div style="border-top: 1px solid rgba(255, 255, 255, 0.1); padding-top: 1.5rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                            <h4 id="vuln-details-title" style="margin: 0;"></h4>
                            <button onclick="hideVulnerabilityDetails()" style="background: rgba(239, 68, 68, 0.2); color: #ef4444; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; font-size: 0.875rem;">
                                ✕ Close
                            </button>
                        </div>
                        <div id="vuln-details-list" style="max-height: 400px; overflow-y: auto;"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- OWASP Top 10 Compliance -->
        <div class="glass-card" style="margin-bottom: 2rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <div>
                    <h3 style="margin: 0 0 0.25rem 0;">🛡️ OWASP Top 10 Compliance</h3>
                    <div style="font-size: 0.875rem; color: var(--text-secondary);">
                        Overall Compliance: <span style="color: ${getScoreColor(owaspCompliance)}; font-weight: 600;">${Math.round(owaspCompliance)}%</span>
                    </div>
                </div>
                <span style="
                    background: var(--accent-primary)22;
                    color: var(--accent-primary);
                    padding: 0.5rem 1rem;
                    border-radius: 8px;
                    font-size: 0.875rem;
                    font-weight: 600;
                ">
                    ${owaspVersion} Standard
                </span>
            </div>
            <div style="
                background: rgba(0, 212, 255, 0.1);
                border-left: 3px solid var(--accent-primary);
                padding: 0.75rem 1rem;
                border-radius: 6px;
                font-size: 0.875rem;
                color: var(--text-secondary);
                margin-bottom: 1.5rem;
            ">
                Each card shows a security risk category with evidence-based scoring. 
                ✅ <strong>Pass (80-100)</strong>: No issues found. 
                ⚠️ <strong>Warning (60-79)</strong>: Minor issues detected. 
                ❌ <strong>Fail (<60)</strong>: Critical vulnerabilities require immediate attention. Findings count shows actual issues discovered.
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem;">
                ${owaspTop10.map(item => renderOwaspItem(item)).join('')}
            </div>
        </div>

        <!-- Compliance Status -->
        <div class="glass-card">
            <h3 style="margin-bottom: 1rem;">📋 Compliance Status</h3>
            <div style="
                background: rgba(16, 185, 129, 0.1);
                border-left: 3px solid #10b981;
                padding: 0.75rem 1rem;
                border-radius: 6px;
                font-size: 0.875rem;
                color: var(--text-secondary);
                margin-bottom: 1.5rem;
            ">
                Shows readiness for major compliance frameworks. 
                ✅ <strong>Ready</strong>: Security posture meets framework requirements. 
                ⚠️ <strong>Not Ready</strong>: Specific issues listed below prevent certification. Address blockers to achieve compliance.
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem;">
                ${renderComplianceCard('GDPR', compliance.gdpr_ready, compliance.gdpr_issues)}
                ${renderComplianceCard('SOC 2', compliance.soc2_ready, compliance.soc2_issues)}
                ${renderComplianceCard('HIPAA', compliance.hipaa_ready, compliance.hipaa_issues)}
                ${renderComplianceCard('PCI DSS', compliance.pci_dss_ready, compliance.pci_dss_issues)}
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
        pass: { icon: '✅', color: '#10b981', label: 'Pass' },
        warn: { icon: '⚠️', color: '#f59e0b', label: 'Warning' },
        fail: { icon: '❌', color: '#ef4444', label: 'Fail' }
    };
    
    const status = statusConfig[item.status] || statusConfig.pass;
    const itemScore = item.score || 0;
    const findingsCount = item.findings_count || 0;
    
    return `
        <div style="
            padding: 1.25rem;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.05);
            border-left: 4px solid ${status.color};
            transition: transform 0.2s, box-shadow 0.2s;
        " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.2)'" 
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.75rem;">
                <div style="flex: 1;">
                    <div style="font-size: 1.1rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.25rem;">
                        ${item.name || 'Unknown Risk'}
                    </div>
                    <div style="font-size: 0.75rem; color: var(--text-secondary);">
                        ${item.risk || 'A01'}
                    </div>
                </div>
                <span style="font-size: 1.5rem; margin-left: 0.5rem;">${status.icon}</span>
            </div>
            
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                <div style="font-size: 0.875rem; color: var(--text-secondary);">
                    Score: <span style="color: ${status.color}; font-weight: 600;">${itemScore}/100</span>
                </div>
                <div style="
                    background: ${status.color}22;
                    color: ${status.color};
                    padding: 0.25rem 0.5rem;
                    border-radius: 4px;
                    font-size: 0.75rem;
                    font-weight: 600;
                ">
                    ${status.label.toUpperCase()}
                </div>
            </div>
            
            <div style="height: 6px; background: rgba(255, 255, 255, 0.1); border-radius: 3px; overflow: hidden; margin-bottom: 0.75rem;">
                <div style="
                    height: 100%;
                    width: ${itemScore}%;
                    background: ${status.color};
                    transition: width 0.3s ease;
                "></div>
            </div>
            
            ${findingsCount > 0 ? `
                <div style="
                    font-size: 0.75rem;
                    color: ${status.color};
                    background: ${status.color}11;
                    padding: 0.5rem;
                    border-radius: 4px;
                    text-align: center;
                ">
                    ${findingsCount} issue${findingsCount !== 1 ? 's' : ''} found
                </div>
            ` : `
                <div style="
                    font-size: 0.75rem;
                    color: #10b981;
                    background: rgba(16, 185, 129, 0.1);
                    padding: 0.5rem;
                    border-radius: 4px;
                    text-align: center;
                ">
                    No issues detected
                </div>
            `}
        </div>
    `;
}

/**
 * Render compliance card
 * @param {string} name - Compliance name
 * @param {boolean} ready - Compliance ready status
 * @param {Array} issues - List of compliance issues
 * @returns {string} HTML string
 */
function renderComplianceCard(name, ready, issues = []) {
    const icon = ready ? '✅' : '⚠️';
    const status = ready ? 'Ready' : 'Not Ready';
    const borderColor = ready ? '#10b981' : '#f59e0b';
    const issuesHtml = issues && issues.length > 0 
        ? `<div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.75rem; text-align: left; padding: 0.5rem; background: rgba(0, 0, 0, 0.2); border-radius: 6px;">
            <strong>Issues:</strong>
            <ul style="margin: 0.5rem 0 0 0; padding-left: 1.25rem;">
                ${issues.slice(0, 3).map(issue => `<li style="margin: 0.25rem 0;">${issue}</li>`).join('')}
                ${issues.length > 3 ? `<li style="margin: 0.25rem 0; color: var(--accent-primary);">+${issues.length - 3} more...</li>` : ''}
            </ul>
        </div>` 
        : '';
    
    return `
        <div style="
            padding: 1.5rem;
            border: 2px solid ${borderColor};
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.02);
        ">
            <div style="text-align: center;">
                <div style="font-size: 3rem; margin-bottom: 0.5rem;">${icon}</div>
                <div style="font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">
                    ${name}
                </div>
                <div style="font-size: 0.875rem; color: ${ready ? '#10b981' : '#f59e0b'}; font-weight: 600;">
                    ${status}
                </div>
            </div>
            ${issuesHtml}
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
 * Show vulnerability details for a specific severity level
 * @param {string} severity - Vulnerability severity (critical, high, medium, low)
 * @param {number} count - Number of vulnerabilities
 */
window.showVulnerabilityDetails = function(severity, count) {
    if (count === 0) return;
    
    const container = document.getElementById('vuln-details-container');
    const titleEl = document.getElementById('vuln-details-title');
    const listEl = document.getElementById('vuln-details-list');
    
    if (!container || !titleEl || !listEl) return;
    
    // Get current dashboard data from global state
    const dashboardData = window.currentDashboardData || {};
    const findings = dashboardData.security?.findings?.vulnerabilities || [];
    
    // Filter by severity
    const filteredFindings = findings.filter(f => f.severity === severity);
    
    // Severity configuration
    const severityConfig = {
        critical: { color: '#ef4444', icon: '🔴', label: 'Critical' },
        high: { color: '#f59e0b', icon: '🟠', label: 'High' },
        medium: { color: '#fbbf24', icon: '🟡', label: 'Medium' },
        low: { color: '#10b981', icon: '🟢', label: 'Low' }
    };
    
    const config = severityConfig[severity] || severityConfig.medium;
    
    // Update title
    titleEl.innerHTML = `${config.icon} ${config.label} Severity Vulnerabilities (${filteredFindings.length})`;
    titleEl.style.color = config.color;
    
    // Build list
    if (filteredFindings.length === 0) {
        listEl.innerHTML = `<p style="color: var(--text-secondary); text-align: center; padding: 2rem;">No ${severity} severity vulnerabilities found.</p>`;
    } else {
        listEl.innerHTML = filteredFindings.map((finding, idx) => `
            <div style="
                margin-bottom: 1rem;
                padding: 1rem;
                background: rgba(255, 255, 255, 0.03);
                border-left: 4px solid ${config.color};
                border-radius: 6px;
            ">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                    <div style="flex: 1;">
                        <div style="font-weight: 600; color: var(--accent-primary); margin-bottom: 0.25rem;">
                            ${idx + 1}. ${finding.type || 'Unknown Vulnerability'}
                        </div>
                        <div style="font-size: 0.875rem; color: var(--text-secondary);">
                            📁 ${finding.file || 'Unknown file'} ${finding.line ? `(Line ${finding.line})` : ''}
                        </div>
                    </div>
                    <div style="
                        background: ${config.color}22;
                        color: ${config.color};
                        padding: 0.25rem 0.75rem;
                        border-radius: 12px;
                        font-size: 0.75rem;
                        font-weight: 600;
                        white-space: nowrap;
                    ">
                        ${config.label.toUpperCase()}
                    </div>
                </div>
                
                ${finding.description ? `
                    <div style="font-size: 0.875rem; color: var(--text-primary); margin-bottom: 0.5rem;">
                        ${finding.description}
                    </div>
                ` : ''}
                
                ${finding.code_snippet ? `
                    <div style="
                        font-family: 'Consolas', 'Monaco', monospace;
                        font-size: 0.8rem;
                        background: rgba(0, 0, 0, 0.3);
                        padding: 0.75rem;
                        border-radius: 4px;
                        overflow-x: auto;
                        margin-bottom: 0.5rem;
                        color: #d4d4d4;
                    ">
                        ${escapeHtml(finding.code_snippet)}
                    </div>
                ` : ''}
                
                ${finding.recommendation ? `
                    <div style="
                        font-size: 0.8rem;
                        color: #10b981;
                        background: rgba(16, 185, 129, 0.1);
                        padding: 0.5rem 0.75rem;
                        border-radius: 4px;
                        border-left: 3px solid #10b981;
                    ">
                        <strong>💡 Recommendation:</strong> ${finding.recommendation}
                    </div>
                ` : ''}
            </div>
        `).join('');
    }
    
    // Show container with animation
    container.style.display = 'block';
    container.style.animation = 'slideDown 0.3s ease-out';
    
    // Scroll to details
    container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
};

/**
 * Hide vulnerability details
 */
window.hideVulnerabilityDetails = function() {
    const container = document.getElementById('vuln-details-container');
    if (container) {
        container.style.display = 'none';
    }
};

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped HTML
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

/**
 * Refresh security scan (placeholder)
 */
window.refreshSecurityScan = function() {
    console.log('Refresh security scan');
    alert('Security scan refresh functionality coming soon!');
};
