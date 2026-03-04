// ============================================================================
// CORTEX Registry Explorer — Diff Renderer
// Shows added/removed/changed artifacts between snapshots
// ============================================================================

const DiffRenderer = {
    /**
     * Render a diff report into HTML.
     * @param {Object} diff - { added: [...], removed: [...], changed: [...] }
     * @returns {string} HTML string
     */
    render(diff) {
        const { added = [], removed = [], changed = [] } = diff;
        const total = added.length + removed.length + changed.length;

        if (total === 0) {
            return `
                <div class="diff-report empty-diff">
                    <h3>📊 Diff Report</h3>
                    <p class="ok">✅ No changes detected between snapshots</p>
                </div>
            `;
        }

        return `
            <div class="diff-report">
                <h3>📊 Diff Report</h3>
                <div class="diff-summary">
                    ${added.length > 0 ? `<span class="diff-chip added">+${added.length} added</span>` : ''}
                    ${removed.length > 0 ? `<span class="diff-chip removed">-${removed.length} removed</span>` : ''}
                    ${changed.length > 0 ? `<span class="diff-chip changed">~${changed.length} changed</span>` : ''}
                </div>

                ${added.length > 0 ? this._renderSection('➕ Added', added, 'added') : ''}
                ${removed.length > 0 ? this._renderSection('➖ Removed', removed, 'removed') : ''}
                ${changed.length > 0 ? this._renderChangedSection(changed) : ''}
            </div>
        `;
    },

    _renderSection(heading, items, className) {
        const rows = items.map(item => `
            <tr class="diff-row ${className}">
                <td><code>${this._esc(item.id)}</code></td>
                <td>${this._esc(item.type || '')}</td>
                <td>${this._esc(item.title || '')}</td>
            </tr>
        `).join('');

        return `
            <div class="diff-section ${className}-section">
                <h4>${heading}</h4>
                <table class="diff-table">
                    <thead><tr><th>ID</th><th>Type</th><th>Title</th></tr></thead>
                    <tbody>${rows}</tbody>
                </table>
            </div>
        `;
    },

    _renderChangedSection(items) {
        const rows = items.map(item => `
            <tr class="diff-row changed">
                <td><code>${this._esc(item.id)}</code></td>
                <td class="hash-cell"><code>${this._esc((item.old_hash || '').slice(0, 12))}</code></td>
                <td class="hash-cell"><code>${this._esc((item.new_hash || '').slice(0, 12))}</code></td>
            </tr>
        `).join('');

        return `
            <div class="diff-section changed-section">
                <h4>🔄 Changed</h4>
                <table class="diff-table">
                    <thead><tr><th>ID</th><th>Old Hash</th><th>New Hash</th></tr></thead>
                    <tbody>${rows}</tbody>
                </table>
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
    module.exports = DiffRenderer;
}
