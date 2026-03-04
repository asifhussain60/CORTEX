// ============================================================================
// CORTEX Registry Explorer — Workflow Template Renderer
// Renders typed WorkflowTemplateModel artifacts as detail panels
// ============================================================================

const WorkflowRenderer = {
    /**
     * Render a workflow-template artifact card with step pipeline.
     * @param {Object} artifact - WorkflowTemplateModel dict from registry.json
     * @returns {string} HTML string
     */
    render(artifact) {
        const { id, title, source_file, content = {}, integrity = {} } = artifact;
        const version = content.version || '';
        const category = content.category || '';
        const status = content.status || '';
        const steps = content.steps || [];
        const triggerKeywords = content.trigger_keywords || [];
        const convergenceGate = content.convergence_gate || null;

        return `
            <div class="artifact-detail workflow-detail" data-id="${id}">
                <div class="detail-header">
                    <span class="type-badge workflow-badge">⚙️ Workflow Template</span>
                    <h2>${this._esc(title || id)}</h2>
                    <div class="detail-meta">
                        ${version ? `<span class="meta-chip">v${this._esc(version)}</span>` : ''}
                        ${category ? `<span class="meta-chip">${this._esc(category)}</span>` : ''}
                        ${status ? `<span class="meta-chip status-${status.toLowerCase()}">${this._esc(status)}</span>` : ''}
                    </div>
                </div>

                <div class="detail-body">
                    ${triggerKeywords.length > 0 ? this._renderTriggers(triggerKeywords) : ''}

                    <h3>🔄 Steps (${steps.length})</h3>
                    ${steps.length > 0 ? this._renderStepsPipeline(steps) : '<p class="empty">No steps defined</p>'}

                    ${convergenceGate ? this._renderConvergenceGate(convergenceGate) : ''}
                </div>

                <div class="detail-footer">
                    <span class="source-ref">📁 ${this._esc(source_file)}</span>
                </div>
            </div>
        `;
    },

    _renderTriggers(keywords) {
        const chips = keywords.map(k => `<span class="trigger-chip">${this._esc(k)}</span>`).join('');
        return `<div class="trigger-bar"><h4>🎯 Triggers</h4><div class="trigger-chips">${chips}</div></div>`;
    },

    _renderStepsPipeline(steps) {
        const items = steps.map((s, i) => {
            const name = s.name || s.id || `Step ${i + 1}`;
            const action = s.action || s.description || '';
            return `
                <div class="pipeline-step">
                    <div class="step-number">${i + 1}</div>
                    <div class="step-content">
                        <strong>${this._esc(name)}</strong>
                        ${action ? `<span class="step-action">${this._esc(action)}</span>` : ''}
                    </div>
                </div>
            `;
        }).join('<div class="pipeline-arrow">→</div>');

        return `<div class="pipeline-container">${items}</div>`;
    },

    _renderConvergenceGate(gate) {
        return `
            <div class="convergence-gate">
                <h4>🔁 Convergence Gate</h4>
                <pre><code>${this._esc(typeof gate === 'string' ? gate : JSON.stringify(gate, null, 2))}</code></pre>
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
    module.exports = WorkflowRenderer;
}
