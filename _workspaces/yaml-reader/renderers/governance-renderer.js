// ============================================================================
// CORTEX Registry Explorer — Governance Rule Renderer
// Renders typed GovernanceRuleModel artifacts as detail panels
// ============================================================================

const GovernanceRenderer = {
    /**
     * Render a governance-rule artifact card with full detail.
     * @param {Object} artifact - GovernanceRuleModel dict from registry.json
     * @returns {string} HTML string
     */
    render(artifact) {
        const { id, title, source_file, content = {}, integrity = {} } = artifact;
        const domain = content.domain || 'unknown';
        const category = content.category || '';
        const severity = content.severity || 'P2';
        const enforcement = content.enforcement_mode || 'advisory';
        const rules = content.rules || [];

        return `
            <div class="artifact-detail governance-detail" data-id="${id}">
                <div class="detail-header">
                    <span class="type-badge governance-badge">⚖️ Governance Rule</span>
                    <h2>${this._esc(title || id)}</h2>
                    <div class="detail-meta">
                        <span class="meta-chip severity-${severity.toLowerCase()}">${severity}</span>
                        <span class="meta-chip">${this._esc(domain)}</span>
                        ${category ? `<span class="meta-chip">${this._esc(category)}</span>` : ''}
                        <span class="meta-chip enforcement-${enforcement}">${enforcement}</span>
                    </div>
                </div>

                <div class="detail-body">
                    <h3>📜 Rules (${rules.length})</h3>
                    ${rules.length > 0 ? this._renderRulesTable(rules) : '<p class="empty">No rules defined</p>'}
                </div>

                ${this._renderIntegrity(integrity)}
                <div class="detail-footer">
                    <span class="source-ref">📁 ${this._esc(source_file)}</span>
                </div>
            </div>
        `;
    },

    _renderRulesTable(rules) {
        const rows = rules.map(r => `
            <tr>
                <td class="rule-id"><code>${this._esc(r.id || '')}</code></td>
                <td>${this._esc(r.description || r.title || '')}</td>
                <td>${this._esc(r.enforcement || '')}</td>
            </tr>
        `).join('');

        return `
            <table class="rules-table">
                <thead><tr><th>ID</th><th>Description</th><th>Enforcement</th></tr></thead>
                <tbody>${rows}</tbody>
            </table>
        `;
    },

    _renderIntegrity(integrity) {
        if (!integrity || Object.keys(integrity).length === 0) return '';
        const resolved = integrity.all_refs_resolved;
        const icon = resolved ? '✅' : '⚠️';
        const warnings = integrity.warnings || [];
        return `
            <div class="integrity-block">
                <h4>${icon} Integrity</h4>
                ${warnings.length > 0
                    ? `<ul class="warning-list">${warnings.map(w => `<li>${this._esc(w)}</li>`).join('')}</ul>`
                    : '<p class="ok">All references resolved</p>'}
            </div>
        `;
    },

    _esc(str) {
        const div = document.createElement('div');
        div.textContent = String(str);
        return div.innerHTML;
    }
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = GovernanceRenderer;
}
