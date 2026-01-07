/**
 * Reconciliation Widget Component
 * 
 * Displays reconciliation reports with violations, anomalies, and score adjustments.
 * Shows before/after metrics with industry standards validation (CVSS, OWASP).
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Source-Available (Use Allowed, No Contributions)
 */

/**
 * Render reconciliation widget
 * @param {HTMLElement} container - Container element
 * @param {Object} reconciliationData - Reconciliation report data
 * @returns {string} - HTML string for reconciliation widget
 */
export function renderReconciliationWidget(reconciliationData) {
    if (!reconciliationData || !reconciliationData.reconciled_data) {
        return ''; // No reconciliation data available
    }

    const violations = reconciliationData.violations || [];
    const anomalies = reconciliationData.anomalies || [];
    const auditTrail = reconciliationData.audit_trail || {};
    const changes = auditTrail.changes || [];
    const metadata = reconciliationData.metadata || {};
    const reconciledData = reconciliationData.reconciled_data || {};
    
    // Only show widget if there are findings or changes
    if (violations.length === 0 && anomalies.length === 0 && changes.length === 0) {
        return `
            <div class="glass-card" style="margin-bottom: 2rem; border-left: 4px solid var(--success); background: linear-gradient(135deg, rgba(16, 185, 129, 0.05), rgba(5, 150, 105, 0.02));">
                <div style="display: flex; align-items: center; gap: 1.5rem; padding: 0.5rem;">
                    <div style="background: rgba(16, 185, 129, 0.15); border-radius: 50%; padding: 1.25rem; display: flex; align-items: center; justify-content: center;">
                        <span style="font-size: 2.5rem; line-height: 1;">✅</span>
                    </div>
                    <div style="flex: 1;">
                        <h3 style="font-size: 1.375rem; color: var(--success); margin-bottom: 0.5rem; font-weight: 700;">
                            All Metrics Validated
                        </h3>
                        <p style="color: var(--text-secondary); margin: 0 0 0.5rem 0; font-size: 0.9375rem; line-height: 1.6;">
                            No violations or anomalies detected. Metrics are consistent with CVSS v3.1/v4.0 and OWASP Top 10 2025 standards.
                        </p>
                        <div style="background: rgba(16, 185, 129, 0.1); padding: 0.75rem 1rem; border-radius: 0.5rem; display: inline-block;">
                            <span style="color: var(--text-secondary); font-size: 0.875rem; margin-right: 0.5rem;">Overall Score:</span>
                            <strong style="color: var(--success); font-size: 1.5rem;">${reconciledData.overall_score || 'N/A'}<span style="font-size: 1rem; opacity: 0.7;">/100</span></strong>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Build severity badge helper
    const getSeverityBadge = (severity) => {
        const styles = {
            critical: 'background: rgba(239, 68, 68, 0.2); color: #EF4444; border: 1px solid #EF4444;',
            high: 'background: rgba(245, 158, 11, 0.2); color: #F59E0B; border: 1px solid #F59E0B;',
            medium: 'background: rgba(251, 191, 36, 0.2); color: #FBBF24; border: 1px solid #FBBF24;',
            low: 'background: rgba(16, 185, 129, 0.2); color: #10B981; border: 1px solid #10B981;'
        };
        const style = styles[severity] || styles.medium;
        return `<span style="${style} padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase;">${severity}</span>`;
    };

    // Build confidence badge helper
    const getConfidenceBadge = (confidence) => {
        const percentage = Math.round(confidence * 100);
        const color = confidence >= 0.8 ? '#10B981' : confidence >= 0.6 ? '#FBBF24' : '#F59E0B';
        return `<span style="background: rgba(16, 185, 129, 0.2); color: ${color}; padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.75rem; font-weight: 700;">${percentage}% Confidence</span>`;
    };

    return `
        <div class="glass-card" style="margin-bottom: 2rem; border: 2px solid ${violations.length > 0 || anomalies.length > 0 ? '#F59E0B' : 'var(--accent-primary)'}; background: linear-gradient(135deg, rgba(10, 14, 39, 0.9), rgba(26, 31, 58, 0.8));">
            
            <!-- Compact Header -->
            <div style="display: flex; align-items: center; justify-content: space-between; padding-bottom: 1rem; border-bottom: 1px solid rgba(245, 158, 11, 0.2);">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <span style="font-size: 1.75rem; line-height: 1;">🔍</span>
                    <div>
                        <h2 style="font-size: 1.375rem; color: var(--text-primary); margin: 0; font-weight: 700;">
                            Reconciliation Report
                        </h2>
                        <p style="color: var(--text-secondary); font-size: 0.8125rem; margin: 0.25rem 0 0 0;">
                            CVSS v3.1/v4.0 • OWASP Top 10 2025 • ${metadata.execution_time_ms ? metadata.execution_time_ms.toFixed(2) : 'N/A'}ms
                        </p>
                    </div>
                </div>
                
                <!-- Hero Score Box -->
                <div style="background: rgba(10, 14, 39, 0.95); padding: 1rem 1.5rem; border-radius: 0.5rem; border: 2px solid ${reconciledData.overall_score >= 70 ? '#10B981' : reconciledData.overall_score >= 50 ? '#F59E0B' : '#EF4444'};">
                    <div style="font-size: 0.6875rem; text-transform: uppercase; letter-spacing: 1px; color: var(--text-secondary); margin-bottom: 0.25rem; font-weight: 600; text-align: center;">
                        Overall Score
                    </div>
                    <div style="font-size: 2.25rem; font-weight: 800; line-height: 1; color: ${reconciledData.overall_score >= 70 ? '#10B981' : reconciledData.overall_score >= 50 ? '#F59E0B' : '#EF4444'}; text-align: center;">
                        ${reconciledData.overall_score || 'N/A'}<span style="font-size: 1.25rem; color: var(--text-secondary); font-weight: 400;">/100</span>
                    </div>
                    ${reconciledData.overall_score < 70 ? `
                        <div style="font-size: 0.6875rem; color: ${reconciledData.overall_score >= 50 ? '#F59E0B' : '#EF4444'}; margin-top: 0.375rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; text-align: center;">
                            ${reconciledData.overall_score >= 50 ? '⚠️ Needs Attention' : '🚨 Critical'}
                        </div>
                    ` : ''}
                </div>
            </div>

            <!-- Inline Stats -->
            <div style="display: flex; gap: 1.5rem; padding: 1rem 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-size: 1.5rem; font-weight: 800; color: ${violations.length > 0 ? '#F59E0B' : '#10B981'};">${violations.length}</span>
                    <span style="font-size: 0.8125rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px;">Violations</span>
                </div>
                <div style="width: 1px; background: rgba(255,255,255,0.1);"></div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-size: 1.5rem; font-weight: 800; color: ${anomalies.length > 0 ? '#7B61FF' : '#10B981'};">${anomalies.length}</span>
                    <span style="font-size: 0.8125rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px;">Anomalies</span>
                </div>
                <div style="width: 1px; background: rgba(255,255,255,0.1);"></div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-size: 1.5rem; font-weight: 800; color: var(--accent-primary);">${changes.length}</span>
                    <span style="font-size: 0.8125rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px;">Adjustments</span>
                </div>
            </div>

            <!-- Compact Violations (2-Column Layout) -->
            ${violations.length > 0 ? `
                <div style="padding-top: 1rem;">
                    <h3 style="font-size: 1rem; color: #F59E0B; margin: 0 0 0.75rem 0; font-weight: 700; display: flex; align-items: center; gap: 0.5rem;">
                        <span>⚠️</span>
                        <span>Violations (${violations.length})</span>
                    </h3>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem;">
                        ${violations.map((v, index) => {
                            const severityColors = {
                                critical: { bg: 'rgba(239, 68, 68, 0.08)', border: '#EF4444', badge: '#EF4444' },
                                high: { bg: 'rgba(245, 158, 11, 0.08)', border: '#F59E0B', badge: '#F59E0B' },
                                medium: { bg: 'rgba(251, 191, 36, 0.08)', border: '#FBBF24', badge: '#FBBF24' },
                                low: { bg: 'rgba(16, 185, 129, 0.08)', border: '#10B981', badge: '#10B981' }
                            };
                            const color = severityColors[v.severity] || severityColors.medium;
                            
                            return `
                            <div style="background: ${color.bg}; border: 1px solid ${color.border}; border-radius: 0.5rem; padding: 1rem; display: flex; align-items: start; gap: 1rem;">
                                <!-- Left: Content -->
                                <div style="flex: 1; min-width: 0;">
                                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                                        <span style="background: ${color.badge}; color: white; padding: 0.25rem 0.625rem; border-radius: 0.25rem; font-size: 0.6875rem; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase;">
                                            ${v.severity}
                                        </span>
                                        <span style="font-family: 'Courier New', monospace; font-size: 0.75rem; color: ${color.badge}; font-weight: 600;">
                                            ${v.rule_id}
                                        </span>
                                    </div>
                                    <h4 style="font-size: 0.9375rem; color: var(--text-primary); margin: 0 0 0.5rem 0; font-weight: 600; line-height: 1.4;">
                                        ${v.message}
                                    </h4>
                                    ${v.recommendation ? `
                                        <p style="font-size: 0.8125rem; color: var(--text-secondary); margin: 0; line-height: 1.5; display: flex; align-items: start; gap: 0.5rem;">
                                            <span style="font-size: 1rem;">💡</span>
                                            <span>${v.recommendation}</span>
                                        </p>
                                    ` : ''}
                                </div>
                                
                                <!-- Right: Score Box (Your Favorite!) -->
                                <div style="min-width: 140px; background: rgba(10, 14, 39, 0.8); padding: 0.875rem; border-radius: 0.5rem; border: 2px solid ${color.border}; text-align: center;">
                                    <div style="font-size: 0.6875rem; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-secondary); margin-bottom: 0.5rem; font-weight: 600;">
                                        Score
                                    </div>
                                    <div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                                        <div style="text-align: center;">
                                            <div style="font-size: 0.6875rem; color: var(--text-secondary); margin-bottom: 0.125rem;">Before</div>
                                            <div style="font-size: 1.25rem; color: var(--text-secondary); text-decoration: line-through; font-weight: 700; opacity: 0.5;">
                                                ${v.original_score.toFixed(0)}
                                            </div>
                                        </div>
                                        <div style="font-size: 1.25rem; color: var(--text-secondary); opacity: 0.4;">→</div>
                                        <div style="text-align: center;">
                                            <div style="font-size: 0.6875rem; color: ${color.badge}; margin-bottom: 0.125rem;">After</div>
                                            <div style="font-size: 1.25rem; color: ${color.badge}; font-weight: 700;">
                                                ${v.adjusted_score.toFixed(0)}
                                            </div>
                                        </div>
                                    </div>
                                    <div style="background: ${v.adjustment < 0 ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)'}; padding: 0.375rem 0.625rem; border-radius: 0.25rem; font-size: 0.875rem; color: ${v.adjustment < 0 ? '#EF4444' : '#10B981'}; font-weight: 700;">
                                        ${v.adjustment >= 0 ? '+' : ''}${v.adjustment.toFixed(1)}
                                    </div>
                                </div>
                            </div>
                        `}).join('')}
                    </div>
                </div>
            ` : ''}

            <!-- Compact Anomalies -->
            ${anomalies.length > 0 ? `
                <div style="padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.05);">
                    <h3 style="font-size: 1rem; color: #7B61FF; margin: 0 0 0.75rem 0; font-weight: 700; display: flex; align-items: center; gap: 0.5rem;">
                        <span>�</span>
                        <span>Pattern Anomalies (${anomalies.length})</span>
                    </h3>
                    <div style="display: grid; gap: 0.75rem;">
                        ${anomalies.map((a, index) => {
                            const confidenceColor = a.confidence >= 0.8 ? '#10B981' : a.confidence >= 0.6 ? '#FBBF24' : '#F59E0B';
                            const confidenceLabel = a.confidence >= 0.8 ? 'High' : a.confidence >= 0.6 ? 'Medium' : 'Low';
                            
                            return `
                            <div style="background: rgba(123, 97, 255, 0.08); border: 1px solid #7B61FF; border-radius: 0.5rem; padding: 1rem;">
                                <div style="display: flex; align-items: start; justify-content: space-between; gap: 1rem;">
                                    <div style="flex: 1; min-width: 0;">
                                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                                            <span style="background: #7B61FF; color: white; padding: 0.25rem 0.625rem; border-radius: 0.25rem; font-size: 0.6875rem; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase;">
                                                ${a.type.replace(/_/g, ' ')}
                                            </span>
                                            <span style="background: ${confidenceColor}; color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.6875rem; font-weight: 700;">
                                                ${(a.confidence * 100).toFixed(0)}%
                                            </span>
                                        </div>
                                        <h4 style="font-size: 0.9375rem; color: var(--text-primary); margin: 0 0 0.5rem 0; font-weight: 600; line-height: 1.4;">
                                            ${a.message}
                                        </h4>
                                        ${a.recommendation ? `
                                            <p style="font-size: 0.8125rem; color: var(--text-secondary); margin: 0; line-height: 1.5; display: flex; align-items: start; gap: 0.5rem;">
                                                <span style="font-size: 1rem;">💡</span>
                                                <span>${a.recommendation}</span>
                                            </p>
                                        ` : ''}
                                    </div>
                                </div>
                            </div>
                        `}).join('')}
                    </div>
                </div>
            ` : ''}

            <!-- Compact Audit Trail -->
            ${changes.length > 0 && changes.length <= 5 ? `
                <div style="padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.05);">
                    <details style="cursor: pointer;">
                        <summary style="font-size: 1rem; color: var(--accent-primary); font-weight: 700; display: flex; align-items: center; gap: 0.5rem; list-style: none; user-select: none;">
                            <span style="font-size: 0.75rem;">▶</span>
                            <span>📝</span>
                            <span>Audit Trail (${changes.length} changes)</span>
                        </summary>
                        <div style="padding: 0.75rem 0 0 1.5rem;">
                            ${changes.map((c, idx) => `
                                <div style="display: flex; gap: 0.75rem; margin-bottom: 0.5rem; padding-bottom: 0.5rem; ${idx < changes.length - 1 ? 'border-bottom: 1px solid rgba(255,255,255,0.05);' : ''}">
                                    <div style="min-width: 6px; height: 6px; border-radius: 50%; background: var(--accent-primary); margin-top: 0.5rem;"></div>
                                    <div style="flex: 1;">
                                        <div style="font-size: 0.8125rem; color: var(--text-secondary); line-height: 1.5;">
                                            ${c.field} <strong style="color: ${c.change_type === 'adjusted' ? '#F59E0B' : '#10B981'};">${c.change_type}</strong>
                                            ${c.old_value !== undefined ? `from <code style="background: rgba(255,255,255,0.05); padding: 0.125rem 0.375rem; border-radius: 0.25rem; font-size: 0.75rem;">${c.old_value}</code>` : ''}
                                            to <code style="background: rgba(255,255,255,0.05); padding: 0.125rem 0.375rem; border-radius: 0.25rem; font-size: 0.75rem;">${c.new_value}</code>
                                        </div>
                                        ${c.reason ? `<div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.25rem; opacity: 0.7;">${c.reason}</div>` : ''}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </details>
                </div>
            ` : ''}
        </div>
    `;
}
