// ============================================================================
// CORTEX Registry Explorer — Pattern Renderer
// Renders typed PatternModel artifacts as detail panels
// ============================================================================

const PatternRenderer = {
    /**
     * Render a pattern artifact card with participants and anti-patterns.
     * @param {Object} artifact - PatternModel dict from registry.json
     * @returns {string} HTML string
     */
    render(artifact) {
        const { id, title, source_file, content = {} } = artifact;
        const patternName = content.pattern_name || title || id;
        const patternType = content.pattern_type || '';
        const description = content.description || '';
        const cortexUsage = content.cortex_usage || '';
        const participants = content.participants || [];
        const whenToUse = content.when_to_use || [];
        const antiPatterns = content.anti_patterns || [];
        const fileRefs = content.file_references || [];

        return `
            <div class="artifact-detail pattern-detail" data-id="${id}">
                <div class="detail-header">
                    <span class="type-badge pattern-badge">🧩 Pattern</span>
                    <h2>${this._esc(patternName)}</h2>
                    ${patternType ? `<div class="detail-meta"><span class="meta-chip">${this._esc(patternType)}</span></div>` : ''}
                </div>

                <div class="detail-body">
                    ${description ? `<p class="description">${this._esc(description)}</p>` : ''}
                    ${cortexUsage ? `<div class="cortex-usage"><h4>🧠 CORTEX Usage</h4><p>${this._esc(cortexUsage)}</p></div>` : ''}

                    ${participants.length > 0 ? this._renderList('👥 Participants', participants) : ''}
                    ${whenToUse.length > 0 ? this._renderList('✅ When to Use', whenToUse) : ''}
                    ${antiPatterns.length > 0 ? this._renderList('❌ Anti-Patterns', antiPatterns) : ''}
                    ${fileRefs.length > 0 ? this._renderFileRefs(fileRefs) : ''}
                </div>

                <div class="detail-footer">
                    <span class="source-ref">📁 ${this._esc(source_file)}</span>
                </div>
            </div>
        `;
    },

    _renderList(heading, items) {
        const lis = items.map(i => `<li>${this._esc(typeof i === 'string' ? i : JSON.stringify(i))}</li>`).join('');
        return `<div class="section"><h4>${heading}</h4><ul>${lis}</ul></div>`;
    },

    _renderFileRefs(refs) {
        const chips = refs.map(r => `<code class="file-ref">${this._esc(r)}</code>`).join(' ');
        return `<div class="section"><h4>📂 File References</h4><div>${chips}</div></div>`;
    },

    _esc(str) {
        const div = document.createElement('div');
        div.textContent = String(str);
        return div.innerHTML;
    }
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = PatternRenderer;
}
