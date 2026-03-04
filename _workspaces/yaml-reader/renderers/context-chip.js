// ============================================================================
// CORTEX Registry Explorer — Context Chip
// Always-visible intelligence bar: registry health, type counts, integrity
// ============================================================================

const ContextChip = {
    /**
     * Render the context chip bar from registry output data.
     * @param {Object} registryOutput - Full output from RegistryIndexer.emit()
     * @returns {string} HTML string for the context chip bar
     */
    render(registryOutput) {
        const { artifacts = [], integrity = {}, stats = {} } = registryOutput;
        const total = integrity.total_artifacts || artifacts.length || 0;
        const healthy = integrity.healthy_count || 0;
        const broken = integrity.broken_count || 0;
        const types = integrity.types || stats.types || {};
        const nodeCount = stats.node_count || 0;
        const edgeCount = stats.edge_count || 0;
        const duplicates = (integrity.duplicate_ids || []).length;

        const healthPct = total > 0 ? Math.round((healthy / total) * 100) : 100;
        const healthColor = healthPct === 100 ? 'var(--success, #00ff88)' : healthPct >= 80 ? 'var(--warning, #f59e0b)' : 'var(--danger, #ef4444)';

        return `
            <div class="context-chip-bar">
                <div class="chip health-chip" style="border-color: ${healthColor}">
                    <span class="chip-icon">${healthPct === 100 ? '✅' : '⚠️'}</span>
                    <span class="chip-label">Health</span>
                    <span class="chip-value" style="color: ${healthColor}">${healthPct}%</span>
                </div>

                <div class="chip">
                    <span class="chip-icon">📦</span>
                    <span class="chip-label">Artifacts</span>
                    <span class="chip-value">${total}</span>
                </div>

                <div class="chip">
                    <span class="chip-icon">🔗</span>
                    <span class="chip-label">Graph</span>
                    <span class="chip-value">${nodeCount}N / ${edgeCount}E</span>
                </div>

                ${broken > 0 ? `
                    <div class="chip danger-chip">
                        <span class="chip-icon">❌</span>
                        <span class="chip-label">Broken</span>
                        <span class="chip-value">${broken}</span>
                    </div>
                ` : ''}

                ${duplicates > 0 ? `
                    <div class="chip warning-chip">
                        <span class="chip-icon">⚠️</span>
                        <span class="chip-label">Duplicates</span>
                        <span class="chip-value">${duplicates}</span>
                    </div>
                ` : ''}

                ${this._renderTypeChips(types)}
            </div>
        `;
    },

    _renderTypeChips(types) {
        const typeIcons = {
            'governance-rule': '⚖️',
            'workflow-template': '⚙️',
            'pattern': '🧩',
            'plan': '📋',
            'config': '🔧',
            'knowledge': '📚',
            'response-template': '📝',
            'generic': '📄',
        };

        return Object.entries(types).map(([type, count]) => {
            const icon = typeIcons[type] || '📄';
            const shortName = type.split('-').pop();
            return `
                <div class="chip type-chip">
                    <span class="chip-icon">${icon}</span>
                    <span class="chip-label">${this._esc(shortName)}</span>
                    <span class="chip-value">${count}</span>
                </div>
            `;
        }).join('');
    },

    _esc(str) {
        const div = document.createElement('div');
        div.textContent = String(str);
        return div.innerHTML;
    }
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = ContextChip;
}
