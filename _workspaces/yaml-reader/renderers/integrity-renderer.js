// ============================================================================
// CORTEX Registry Explorer — Integrity Dashboard Renderer
// Renders integrity report: health overview, broken artifacts, duplicates
// ============================================================================

const IntegrityRenderer = {
    /**
     * Render the integrity dashboard from an integrity report.
     * @param {Object} report - IntegrityChecker report from registry.json
     * @returns {string} HTML string
     */
    render(report) {
        const {
            total_artifacts = 0,
            healthy_count = 0,
            broken_count = 0,
            broken_artifacts = [],
            duplicate_ids = [],
            warnings = [],
            types = {},
        } = report;

        const healthPct = total_artifacts > 0 ? Math.round((healthy_count / total_artifacts) * 100) : 100;

        return `
            <div class="integrity-dashboard">
                <h3>🏥 Registry Integrity Dashboard</h3>

                <div class="integrity-metrics">
                    <div class="metric-card health-metric">
                        <div class="metric-ring" style="--pct: ${healthPct}; --color: ${healthPct === 100 ? '#00ff88' : healthPct >= 80 ? '#f59e0b' : '#ef4444'}">
                            <span class="metric-value">${healthPct}%</span>
                        </div>
                        <div class="metric-label">Health</div>
                    </div>

                    <div class="metric-card">
                        <div class="metric-value">${total_artifacts}</div>
                        <div class="metric-label">Total</div>
                    </div>

                    <div class="metric-card">
                        <div class="metric-value" style="color: var(--success, #00ff88)">${healthy_count}</div>
                        <div class="metric-label">Healthy</div>
                    </div>

                    <div class="metric-card">
                        <div class="metric-value" style="color: ${broken_count > 0 ? 'var(--danger, #ef4444)' : 'var(--success, #00ff88)'}">${broken_count}</div>
                        <div class="metric-label">Broken</div>
                    </div>
                </div>

                ${this._renderTypeBreakdown(types)}
                ${broken_artifacts.length > 0 ? this._renderBrokenArtifacts(broken_artifacts) : ''}
                ${duplicate_ids.length > 0 ? this._renderDuplicates(duplicate_ids) : ''}
                ${warnings.length > 0 ? this._renderWarnings(warnings) : ''}

                ${broken_count === 0 && duplicate_ids.length === 0
                    ? '<div class="all-clear"><p>✅ All artifacts pass integrity checks</p></div>'
                    : ''}
            </div>
        `;
    },

    _renderTypeBreakdown(types) {
        if (Object.keys(types).length === 0) return '';
        const bars = Object.entries(types).sort((a, b) => b[1] - a[1]).map(([type, count]) => `
            <div class="type-bar">
                <span class="type-name">${this._esc(type)}</span>
                <div class="type-bar-fill" style="width: ${count}px; min-width: 20px;"></div>
                <span class="type-count">${count}</span>
            </div>
        `).join('');
        return `<div class="type-breakdown"><h4>📊 Type Breakdown</h4>${bars}</div>`;
    },

    _renderBrokenArtifacts(artifacts) {
        const rows = artifacts.map(a => `
            <tr class="broken-row">
                <td><code>${this._esc(a.id)}</code></td>
                <td>${this._esc(a.type || '')}</td>
                <td>${this._esc(a.source_file || '')}</td>
                <td>${(a.warnings || []).map(w => this._esc(w)).join('; ')}</td>
            </tr>
        `).join('');
        return `
            <div class="broken-section">
                <h4>❌ Broken Artifacts (${artifacts.length})</h4>
                <table class="integrity-table">
                    <thead><tr><th>ID</th><th>Type</th><th>Source</th><th>Issues</th></tr></thead>
                    <tbody>${rows}</tbody>
                </table>
            </div>
        `;
    },

    _renderDuplicates(duplicates) {
        const rows = duplicates.map(d => `
            <tr>
                <td><code>${this._esc(d.id)}</code></td>
                <td>${(d.source_files || []).map(f => `<code>${this._esc(f)}</code>`).join(', ')}</td>
            </tr>
        `).join('');
        return `
            <div class="duplicates-section">
                <h4>⚠️ Duplicate IDs (${duplicates.length})</h4>
                <table class="integrity-table">
                    <thead><tr><th>ID</th><th>Found In</th></tr></thead>
                    <tbody>${rows}</tbody>
                </table>
            </div>
        `;
    },

    _renderWarnings(warnings) {
        const items = warnings.slice(0, 50).map(w => `<li>${this._esc(w)}</li>`).join('');
        const more = warnings.length > 50 ? `<li class="more">... and ${warnings.length - 50} more</li>` : '';
        return `<div class="warnings-section"><h4>⚠️ Warnings (${warnings.length})</h4><ul>${items}${more}</ul></div>`;
    },

    _esc(str) {
        const div = document.createElement('div');
        div.textContent = String(str);
        return div.innerHTML;
    }
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = IntegrityRenderer;
}
