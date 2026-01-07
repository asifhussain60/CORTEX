/**
 * Reconciliation Widget Component (Collapsible Version)
 * 
 * Displays reconciliation reports as expandable panel with violations, anomalies, and score adjustments.
 * Shows summary stats in collapsed state, full details when expanded.
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Source-Available (Use Allowed, No Contributions)
 */

/**
 * Render reconciliation widget as collapsible panel with Automated Analysis info
 * @param {Object} reconciliationData - Reconciliation report data
 * @param {string} dataSource - Data source type ('readme', 'hybrid', 'generated')
 * @param {number} accuracy - Accuracy percentage
 * @returns {string} - HTML string for reconciliation widget
 */
export function renderReconciliationWidget(reconciliationData, dataSource = 'hybrid', accuracy = 76) {
    if (!reconciliationData || !reconciliationData.reconciled_data) {
        return ''; // No reconciliation data available
    }

    const violations = reconciliationData.violations || [];
    const anomalies = reconciliationData.anomalies || [];
    const auditTrail = reconciliationData.audit_trail || {};
    const changes = auditTrail.changes || [];
    const metadata = reconciliationData.metadata || {};
    const reconciledData = reconciliationData.reconciled_data || {};
    
    // Calculate status
    const hasIssues = violations.length > 0 || anomalies.length > 0;
    const statusColor = reconciledData.overall_score >= 70 ? '#10B981' : reconciledData.overall_score >= 50 ? '#F59E0B' : '#EF4444';
    const statusIcon = hasIssues ? '⚠️' : 'ℹ️';
    
    return `
        <div class="glass-card reconciliation-panel" style="margin-bottom: 2rem; border: 2px solid ${hasIssues ? '#F59E0B' : '#FFC107'}; background: linear-gradient(135deg, rgba(10, 14, 39, 0.9), rgba(26, 31, 58, 0.8));">
            
            <!-- Collapsible Header with Automated Analysis Info -->
            <details>
                <summary style="cursor: pointer; user-select: none; list-style: none; padding: 0; transition: background 0.2s;">
                    <!-- Top Section: Automated Analysis -->
                    <div style="background: linear-gradient(135deg, rgba(255, 193, 7, 0.1) 0%, rgba(255, 152, 0, 0.1) 100%); padding: 1.25rem 1.5rem; border-bottom: 1px solid rgba(255, 193, 7, 0.2);">
                        <div style="display: flex; align-items: start; gap: 1rem;">
                            <div style="font-size: 2rem; line-height: 1;">${statusIcon}</div>
                            <div style="flex: 1;">
                                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem; flex-wrap: wrap;">
                                    <h3 style="font-size: 1.125rem; font-weight: 700; color: var(--text-primary); margin: 0;">Automated Analysis & Reconciliation</h3>
                                    <span style="background: rgba(76, 175, 80, 0.2); color: #4CAF50; padding: 0.3125rem 0.875rem; border-radius: 1rem; font-size: 0.8125rem; font-weight: 700; letter-spacing: 0.5px;">
                                        ~${accuracy}% ACCURACY
                                    </span>
                                </div>
                                <p style="color: var(--text-secondary); font-size: 0.9375rem; line-height: 1.6; margin: 0;">
                                    This executive summary has been <strong>reverse-engineered through automated code analysis</strong>. 
                                    CVSS v3.1/v4.0 and OWASP Top 10 2025 reconciliation applied.
                                    ${dataSource === 'readme' ? ' Project documentation enhanced accuracy.' : ''}
                                    ${dataSource === 'generated' ? ' Add README to improve accuracy to 90%+.' : ''}
                                </p>
                            </div>
                            <!-- Expand Indicator -->
                            <div class="expand-indicator" style="font-size: 1.5rem; color: var(--text-secondary); transition: transform 0.3s ease; margin-left: 0.5rem; align-self: center;">▼</div>
                        </div>
                    </div>
                    
                    <!-- Bottom Section: Reconciliation Stats -->
                    <div style="padding: 1.25rem 1.5rem; display: flex; align-items: center; justify-content: space-between; gap: 2rem;">
                        <div style="display: flex; align-items: center; gap: 1rem; flex: 1;">
                            <div>
                                <h2 style="font-size: 1rem; color: var(--text-primary); margin: 0 0 0.25rem 0; font-weight: 600;">
                                    Reconciliation Report
                                </h2>
                                <p style="color: var(--text-secondary); font-size: 0.8125rem; margin: 0;">
                                    ${violations.length} violations, ${anomalies.length} anomalies, ${changes.length} adjustments
                                </p>
                            </div>
                        </div>
                        
                        <!-- Summary Stats -->
                        <div style="display: flex; align-items: center; gap: 2rem; margin-right: 2rem;">
                            <div style="text-align: center;">
                                <div style="font-size: 2.25rem; font-weight: 800; color: ${violations.length > 0 ? '#F59E0B' : '#10B981'}; line-height: 1;">${violations.length}</div>
                                <div style="font-size: 0.8125rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; margin-top: 0.25rem;">Violations</div>
                            </div>
                            <div style="width: 1px; height: 50px; background: rgba(255,255,255,0.15);"></div>
                            <div style="text-align: center;">
                                <div style="font-size: 2.25rem; font-weight: 800; color: ${anomalies.length > 0 ? '#7B61FF' : '#10B981'}; line-height: 1;">${anomalies.length}</div>
                                <div style="font-size: 0.8125rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; margin-top: 0.25rem;">Anomalies</div>
                            </div>
                            <div style="width: 1px; height: 50px; background: rgba(255,255,255,0.15);"></div>
                            <div style="background: rgba(10, 14, 39, 0.95); padding: 1rem 1.5rem; border-radius: 0.625rem; border: 2px solid ${statusColor}; min-width: 120px;">
                                <div style="font-size: 0.6875rem; text-transform: uppercase; letter-spacing: 1px; color: var(--text-secondary); margin-bottom: 0.375rem; font-weight: 600; text-align: center;">
                                    Overall Score
                                </div>
                                <div style="font-size: 2rem; font-weight: 800; line-height: 1; color: ${statusColor}; text-align: center;">
                                    ${reconciledData.overall_score || 'N/A'}<span style="font-size: 1.125rem; color: var(--text-secondary); font-weight: 400;">/100</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </summary>
                
                <!-- Collapsible Content -->
                <div style="padding: 1.5rem; border-top: 1px solid rgba(245, 158, 11, 0.2); animation: fadeIn 0.3s ease;">
                    ${renderDetailedContent(violations, anomalies, changes, reconciledData)}
                </div>
            </details>
        </div>
        
        <style>
            .reconciliation-panel details summary::-webkit-details-marker {
                display: none;
            }
            .reconciliation-panel details[open] .expand-indicator {
                transform: rotate(180deg);
            }
            .reconciliation-panel details summary:hover {
                background: rgba(245, 158, 11, 0.05);
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(-10px); }
                to { opacity: 1; transform: translateY(0); }
            }
        </style>
    `;
}

/**
 * Render detailed content when panel is expanded
 */
function renderDetailedContent(violations, anomalies, changes, reconciledData) {
    if (violations.length === 0 && anomalies.length === 0) {
        return `
            <div style="text-align: center; padding: 3rem;">
                <div style="font-size: 5rem; margin-bottom: 1.5rem;">✅</div>
                <h3 style="font-size: 1.75rem; color: #10B981; margin-bottom: 0.75rem; font-weight: 700;">All Metrics Validated</h3>
                <p style="color: var(--text-secondary); margin: 0; font-size: 1.0625rem;">No violations or anomalies detected. Metrics are consistent with industry standards.</p>
            </div>
        `;
    }
    
    return `
        ${violations.length > 0 ? renderViolations(violations) : ''}
        ${anomalies.length > 0 ? renderAnomalies(anomalies) : ''}
        ${changes.length > 0 && changes.length <= 5 ? renderAuditTrail(changes) : ''}
    `;
}

/**
 * Render violations section (2-column grid)
 */
function renderViolations(violations) {
    return `
        <div style="margin-bottom: 1.5rem;">
            <h3 style="font-size: 1.125rem; color: #F59E0B; margin: 0 0 1rem 0; font-weight: 700; display: flex; align-items: center; gap: 0.625rem;">
                <span>⚠️</span>
                <span>Violations (${violations.length})</span>
            </h3>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
                ${violations.map(v => {
                    const severityColors = {
                        critical: { bg: 'rgba(239, 68, 68, 0.08)', border: '#EF4444', badge: '#EF4444' },
                        high: { bg: 'rgba(245, 158, 11, 0.08)', border: '#F59E0B', badge: '#F59E0B' },
                        medium: { bg: 'rgba(251, 191, 36, 0.08)', border: '#FBBF24', badge: '#FBBF24' },
                        low: { bg: 'rgba(16, 185, 129, 0.08)', border: '#10B981', badge: '#10B981' }
                    };
                    const color = severityColors[v.severity] || severityColors.medium;
                    
                    return `
                    <div style="background: ${color.bg}; border: 1px solid ${color.border}; border-radius: 0.625rem; padding: 1.25rem; display: flex; align-items: start; gap: 1.25rem;">
                        <!-- Left: Content -->
                        <div style="flex: 1; min-width: 0;">
                            <div style="display: flex; align-items: center; gap: 0.625rem; margin-bottom: 0.625rem;">
                                <span style="background: ${color.badge}; color: white; padding: 0.3125rem 0.75rem; border-radius: 0.3125rem; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase;">
                                    ${v.severity}
                                </span>
                                <span style="font-family: 'Courier New', monospace; font-size: 0.8125rem; color: ${color.badge}; font-weight: 600;">
                                    ${v.rule_id}
                                </span>
                            </div>
                            <h4 style="font-size: 1rem; color: var(--text-primary); margin: 0 0 0.625rem 0; font-weight: 600; line-height: 1.4;">
                                ${v.message}
                            </h4>
                            ${v.recommendation ? `
                                <p style="font-size: 0.875rem; color: var(--text-secondary); margin: 0; line-height: 1.5; display: flex; align-items: start; gap: 0.5rem;">
                                    <span style="font-size: 1.125rem;">💡</span>
                                    <span>${v.recommendation}</span>
                                </p>
                            ` : ''}
                        </div>
                        
                        <!-- Right: Score Box -->
                        <div style="min-width: 150px; background: rgba(10, 14, 39, 0.8); padding: 1rem; border-radius: 0.625rem; border: 2px solid ${color.border}; text-align: center;">
                            <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-secondary); margin-bottom: 0.625rem; font-weight: 600;">
                                Score
                            </div>
                            <div style="display: flex; align-items: center; justify-content: center; gap: 0.625rem; margin-bottom: 0.625rem;">
                                <div style="text-align: center;">
                                    <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.1875rem;">Before</div>
                                    <div style="font-size: 1.375rem; color: var(--text-secondary); text-decoration: line-through; font-weight: 700; opacity: 0.5;">
                                        ${v.original_score.toFixed(0)}
                                    </div>
                                </div>
                                <div style="font-size: 1.375rem; color: var(--text-secondary); opacity: 0.4;">→</div>
                                <div style="text-align: center;">
                                    <div style="font-size: 0.75rem; color: ${color.badge}; margin-bottom: 0.1875rem;">After</div>
                                    <div style="font-size: 1.375rem; color: ${color.badge}; font-weight: 700;">
                                        ${v.adjusted_score.toFixed(0)}
                                    </div>
                                </div>
                            </div>
                            <div style="background: ${v.adjustment < 0 ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)'}; padding: 0.4375rem 0.75rem; border-radius: 0.3125rem; font-size: 0.9375rem; color: ${v.adjustment < 0 ? '#EF4444' : '#10B981'}; font-weight: 700;">
                                ${v.adjustment >= 0 ? '+' : ''}${v.adjustment.toFixed(1)}
                            </div>
                        </div>
                    </div>
                `}).join('')}
            </div>
        </div>
    `;
}

/**
 * Render anomalies section
 */
function renderAnomalies(anomalies) {
    return `
        <div style="margin-bottom: 1.5rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.05);">
            <h3 style="font-size: 1.125rem; color: #7B61FF; margin: 0 0 1rem 0; font-weight: 700; display: flex; align-items: center; gap: 0.625rem;">
                <span>🔮</span>
                <span>Pattern Anomalies (${anomalies.length})</span>
            </h3>
            <div style="display: grid; gap: 1rem;">
                ${anomalies.map(a => {
                    const confidenceColor = a.confidence >= 0.8 ? '#10B981' : a.confidence >= 0.6 ? '#FBBF24' : '#F59E0B';
                    
                    return `
                    <div style="background: rgba(123, 97, 255, 0.08); border: 1px solid #7B61FF; border-radius: 0.625rem; padding: 1.25rem;">
                        <div style="display: flex; align-items: start; justify-content: space-between; gap: 1.25rem;">
                            <div style="flex: 1; min-width: 0;">
                                <div style="display: flex; align-items: center; gap: 0.625rem; margin-bottom: 0.625rem;">
                                    <span style="background: #7B61FF; color: white; padding: 0.3125rem 0.75rem; border-radius: 0.3125rem; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase;">
                                        ${a.type.replace(/_/g, ' ')}
                                    </span>
                                    <span style="background: ${confidenceColor}; color: white; padding: 0.3125rem 0.625rem; border-radius: 0.3125rem; font-size: 0.75rem; font-weight: 700;">
                                        ${(a.confidence * 100).toFixed(0)}% Confidence
                                    </span>
                                </div>
                                <h4 style="font-size: 1rem; color: var(--text-primary); margin: 0 0 0.625rem 0; font-weight: 600; line-height: 1.4;">
                                    ${a.message}
                                </h4>
                                ${a.recommendation ? `
                                    <p style="font-size: 0.875rem; color: var(--text-secondary); margin: 0; line-height: 1.5; display: flex; align-items: start; gap: 0.5rem;">
                                        <span style="font-size: 1.125rem;">💡</span>
                                        <span>${a.recommendation}</span>
                                    </p>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                `}).join('')}
            </div>
        </div>
    `;
}

/**
 * Render audit trail section
 */
function renderAuditTrail(changes) {
    return `
        <div style="padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.05);">
            <details style="cursor: pointer;">
                <summary style="font-size: 1.125rem; color: var(--accent-primary); font-weight: 700; display: flex; align-items: center; gap: 0.625rem; list-style: none; user-select: none;">
                    <span style="font-size: 0.875rem; transition: transform 0.2s;">▶</span>
                    <span>📝</span>
                    <span>Audit Trail (${changes.length} changes)</span>
                </summary>
                <div style="padding: 1rem 0 0 2rem;">
                    ${changes.map((c, idx) => `
                        <div style="display: flex; gap: 1rem; margin-bottom: 0.625rem; padding-bottom: 0.625rem; ${idx < changes.length - 1 ? 'border-bottom: 1px solid rgba(255,255,255,0.05);' : ''}">
                            <div style="min-width: 8px; height: 8px; border-radius: 50%; background: var(--accent-primary); margin-top: 0.625rem;"></div>
                            <div style="flex: 1;">
                                <div style="font-size: 0.875rem; color: var(--text-secondary); line-height: 1.5;">
                                    ${c.field} <strong style="color: ${c.change_type === 'adjusted' ? '#F59E0B' : '#10B981'};">${c.change_type}</strong>
                                    ${c.old_value !== undefined ? `from <code style="background: rgba(255,255,255,0.05); padding: 0.1875rem 0.4375rem; border-radius: 0.3125rem; font-size: 0.8125rem;">${c.old_value}</code>` : ''}
                                    to <code style="background: rgba(255,255,255,0.05); padding: 0.1875rem 0.4375rem; border-radius: 0.3125rem; font-size: 0.8125rem;">${c.new_value}</code>
                                </div>
                                ${c.reason ? `<div style="font-size: 0.8125rem; color: var(--text-secondary); margin-top: 0.3125rem; opacity: 0.7;">${c.reason}</div>` : ''}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </details>
        </div>
    `;
}
