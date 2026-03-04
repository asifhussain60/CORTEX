// ============================================================================
// CORTEX Registry Explorer — Plan Renderer
// Renders typed PlanModel artifacts as detail panels
// ============================================================================

const PlanRenderer = {
    /**
     * Render a plan artifact card with phases and acceptance criteria.
     * @param {Object} artifact - PlanModel dict from registry.json
     * @returns {string} HTML string
     */
    render(artifact) {
        const { id, title, source_file, content = {} } = artifact;
        const status = content.status || 'PLANNED';
        const priority = content.priority || '';
        const version = content.version || '';
        const phases = content.phases || [];
        const sweepCatalogue = content.sweep_catalogue || [];
        const acceptanceCriteria = content.acceptance_criteria || [];
        const dependsOn = content.depends_on || [];

        return `
            <div class="artifact-detail plan-detail" data-id="${id}">
                <div class="detail-header">
                    <span class="type-badge plan-badge">📋 Plan</span>
                    <h2>${this._esc(title || id)}</h2>
                    <div class="detail-meta">
                        <span class="meta-chip status-${status.toLowerCase()}">${this._esc(status)}</span>
                        ${priority ? `<span class="meta-chip severity-${priority.toLowerCase()}">${this._esc(priority)}</span>` : ''}
                        ${version ? `<span class="meta-chip">v${this._esc(version)}</span>` : ''}
                    </div>
                </div>

                <div class="detail-body">
                    ${dependsOn.length > 0 ? this._renderDependencies(dependsOn) : ''}
                    ${phases.length > 0 ? this._renderPhases(phases) : ''}
                    ${sweepCatalogue.length > 0 ? this._renderSweep(sweepCatalogue) : ''}
                    ${acceptanceCriteria.length > 0 ? this._renderAC(acceptanceCriteria) : ''}
                </div>

                <div class="detail-footer">
                    <span class="source-ref">📁 ${this._esc(source_file)}</span>
                </div>
            </div>
        `;
    },

    _renderPhases(phases) {
        const rows = phases.map(p => {
            const pid = typeof p === 'string' ? p : (p.id || '');
            const ptitle = typeof p === 'string' ? '' : (p.title || '');
            const pstatus = typeof p === 'string' ? '' : (p.status || '');
            return `<tr><td><code>${this._esc(pid)}</code></td><td>${this._esc(ptitle)}</td><td>${this._esc(pstatus)}</td></tr>`;
        }).join('');
        return `
            <h3>🔢 Phases (${phases.length})</h3>
            <table class="phases-table">
                <thead><tr><th>ID</th><th>Title</th><th>Status</th></tr></thead>
                <tbody>${rows}</tbody>
            </table>
        `;
    },

    _renderSweep(catalogue) {
        const items = catalogue.map(g => `<li><code>${this._esc(g.id || '')}</code> ${this._esc(g.title || '')} <span class="meta-chip">${this._esc(g.status || '')}</span></li>`).join('');
        return `<h3>🧹 Sweep Catalogue (${catalogue.length})</h3><ul>${items}</ul>`;
    },

    _renderAC(criteria) {
        const items = criteria.map(c => `<li>${this._esc(typeof c === 'string' ? c : JSON.stringify(c))}</li>`).join('');
        return `<h3>✅ Acceptance Criteria</h3><ul>${items}</ul>`;
    },

    _renderDependencies(deps) {
        const chips = deps.map(d => `<code class="dep-chip">${this._esc(d)}</code>`).join(' → ');
        return `<div class="dependencies"><h4>🔗 Dependencies</h4><div>${chips}</div></div>`;
    },

    _esc(str) {
        const div = document.createElement('div');
        div.textContent = String(str);
        return div.innerHTML;
    }
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = PlanRenderer;
}
