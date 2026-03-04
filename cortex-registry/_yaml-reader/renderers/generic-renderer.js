// ============================================================================
// CORTEX Registry Explorer — Generic Renderer
// Renders GenericModel artifacts (fallback for unrecognized schema types)
// ============================================================================

const GenericRenderer = {
    /**
     * Render a generic artifact card with raw key-value display.
     * @param {Object} artifact - GenericModel dict from registry.json
     * @returns {string} HTML string
     */
    render(artifact) {
        const { id, title, source_file, content = {}, type } = artifact;
        const schemaWarning = artifact.schema_warning === true;

        return `
            <div class="artifact-detail generic-detail" data-id="${id}">
                <div class="detail-header">
                    <span class="type-badge generic-badge">📄 ${this._esc(type || 'Generic')}</span>
                    <h2>${this._esc(title || id)}</h2>
                </div>

                ${schemaWarning ? `
                    <div class="schema-warning">
                        ⚠️ No typed parser registered for schema type <code>${this._esc(type)}</code>.
                        Displaying raw content.
                    </div>
                ` : ''}

                <div class="detail-body">
                    ${this._renderContent(content)}
                </div>

                <div class="detail-footer">
                    <span class="source-ref">📁 ${this._esc(source_file)}</span>
                </div>
            </div>
        `;
    },

    _renderContent(content) {
        if (!content || Object.keys(content).length === 0) {
            return '<p class="empty">No content</p>';
        }

        const rows = Object.entries(content).map(([key, value]) => {
            let rendered;
            if (typeof value === 'object' && value !== null) {
                rendered = `<pre><code>${this._esc(JSON.stringify(value, null, 2))}</code></pre>`;
            } else {
                rendered = `<span>${this._esc(String(value))}</span>`;
            }
            return `
                <div class="kv-row">
                    <span class="kv-key">${this._esc(key)}</span>
                    <div class="kv-value">${rendered}</div>
                </div>
            `;
        }).join('');

        return `<div class="kv-grid">${rows}</div>`;
    },

    _esc(str) {
        const div = document.createElement('div');
        div.textContent = String(str);
        return div.innerHTML;
    }
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = GenericRenderer;
}
