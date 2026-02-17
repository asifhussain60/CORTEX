// ============================================================================
// CORTEX Registry Explorer - View Renderers
// Generates HTML for semantic views (Overview, Cards, Raw)
// ============================================================================

/**
 * View Renderer Manager
 * Orchestrates different view types based on schema
 */
class ViewRenderers {
    /**
     * Render Overview view
     */
    static renderOverview(schemaResult, fileName) {
        const { type, entities, metadata, graph } = schemaResult;
        
        const html = `
            <div class="overview-container">
                <div class="overview-header">
                    <div class="file-badge">
                        <span class="file-icon">📊</span>
                        <span class="file-name">${fileName}</span>
                    </div>
                    <div class="schema-badge schema-${type}">
                        <span class="schema-icon">${this.getSchemaIcon(type)}</span>
                        <span>${type.toUpperCase()}</span>
                    </div>
                </div>

                <div class="executive-summary">
                    <h3>📋 Executive Summary</h3>
                    <p class="summary-text">${NarrativeGenerator.generateExecutiveSummary(schemaResult)}</p>
                </div>

                ${this.renderMetrics(entities, metadata, graph)}
                ${this.renderTopRelationships(graph, entities)}
            </div>
        `;

        return html;
    }

    /**
     * Render key metrics section
     */
    static renderMetrics(entities, metadata, graph) {
        const statusCounts = NarrativeGenerator.countByStatus(entities);
        const typeCounts = NarrativeGenerator.countByType(entities);
        const topTags = NarrativeGenerator.getTopTags(entities, 8);

        return `
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-icon">📦</div>
                    <div class="metric-value">${entities.length}</div>
                    <div class="metric-label">Total Entities</div>
                </div>

                ${graph ? `
                <div class="metric-card">
                    <div class="metric-icon">🔗</div>
                    <div class="metric-value">${graph.links.length}</div>
                    <div class="metric-label">Relationships</div>
                </div>
                ` : ''}

                <div class="metric-card">
                    <div class="metric-icon">📊</div>
                    <div class="metric-value">${Object.keys(typeCounts).length}</div>
                    <div class="metric-label">Types</div>
                </div>

                <div class="metric-card">
                    <div class="metric-icon">🏷️</div>
                    <div class="metric-value">${topTags.length}</div>
                    <div class="metric-label">Tags</div>
                </div>
            </div>

            <div class="breakdown-section">
                <div class="breakdown-group">
                    <h4>📍 By Status</h4>
                    <div class="breakdown-list">
                        ${Object.entries(statusCounts).map(([status, count]) => `
                            <div class="breakdown-item">
                                <span class="status-pill status-${status.toLowerCase()}">${status}</span>
                                <span class="breakdown-count">${count}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <div class="breakdown-group">
                    <h4>🔖 By Type</h4>
                    <div class="breakdown-list">
                        ${Object.entries(typeCounts).map(([type, count]) => `
                            <div class="breakdown-item">
                                <span class="type-badge">${type}</span>
                                <span class="breakdown-count">${count}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>

                ${topTags.length > 0 ? `
                <div class="breakdown-group">
                    <h4>🏷️ Top Tags</h4>
                    <div class="tag-cloud">
                        ${topTags.map(({ tag, count }) => `
                            <span class="tag-item" data-count="${count}">
                                ${tag} <span class="tag-count">${count}</span>
                            </span>
                        `).join('')}
                    </div>
                </div>
                ` : ''}
            </div>
        `;
    }

    /**
     * Render top relationships
     */
    static renderTopRelationships(graph, entities) {
        if (!graph || graph.links.length === 0) {
            return '<div class="empty-state">No relationships detected</div>';
        }

        // Calculate node degrees (most connected)
        const degrees = {};
        graph.links.forEach(link => {
            degrees[link.source] = (degrees[link.source] || 0) + 1;
            degrees[link.target] = (degrees[link.target] || 0) + 1;
        });

        const topNodes = Object.entries(degrees)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5);

        return `
            <div class="relationships-section">
                <h3>🔗 Most Connected Entities</h3>
                <div class="relationship-list">
                    ${topNodes.map(([nodeId, degree]) => {
                        const entity = entities.find(e => e.id === nodeId);
                        const label = entity ? entity.label : nodeId;
                        return `
                            <div class="relationship-item">
                                <span class="relationship-icon">🔷</span>
                                <span class="relationship-label">${label}</span>
                                <span class="relationship-degree">${degree} connections</span>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    }

    /**
     * Render Cards view
     */
    static renderCards(entities, filters = {}) {
        const filteredEntities = this.applyFilters(entities, filters);

        if (filteredEntities.length === 0) {
            return `
                <div class="empty-state">
                    <div class="empty-icon">📭</div>
                    <div class="empty-message">No entities match your filters</div>
                    <button class="btn-clear-filters" onclick="clearFilters()">Clear Filters</button>
                </div>
            `;
        }

        return `
            <div class="cards-container">
                <div class="cards-header">
                    <div class="cards-count">${filteredEntities.length} entities</div>
                    ${this.renderFilterBar(entities, filters)}
                </div>
                <div class="cards-grid">
                    ${filteredEntities.map(entity => this.renderEntityCard(entity)).join('')}
                </div>
            </div>
        `;
    }

    /**
     * Render single entity card
     */
    static renderEntityCard(entity) {
        const narrative = NarrativeGenerator.generateEntityNarrative(entity);

        return `
            <div class="entity-card" data-id="${entity.id}">
                <div class="card-header">
                    <div class="card-icon">${this.getEntityIcon(entity.kind)}</div>
                    <div class="card-title-group">
                        <div class="card-title">${entity.label}</div>
                        <div class="card-id">${entity.id}</div>
                    </div>
                    <span class="status-pill status-${entity.status.toLowerCase()}">${entity.status}</span>
                </div>

                <div class="card-body">
                    <div class="card-narrative">${narrative}</div>
                    
                    ${entity.description ? `
                        <div class="card-description">${entity.description}</div>
                    ` : ''}

                    ${entity.owner ? `
                        <div class="card-owner">
                            <span class="owner-icon">👤</span>
                            <span class="owner-name">${entity.owner}</span>
                        </div>
                    ` : ''}

                    ${entity.tags.length > 0 ? `
                        <div class="card-tags">
                            ${entity.tags.map(tag => `
                                <span class="tag-badge">${tag}</span>
                            `).join('')}
                        </div>
                    ` : ''}

                    ${Object.keys(entity.metrics).length > 0 ? `
                        <div class="card-metrics">
                            ${Object.entries(entity.metrics).slice(0, 4).map(([key, value]) => `
                                <div class="metric-chip">
                                    <span class="metric-key">${key}:</span>
                                    <span class="metric-value">${value}</span>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}

                    ${entity.dependencies.length > 0 ? `
                        <div class="card-dependencies">
                            <div class="dependencies-label">🔗 Depends on:</div>
                            <div class="dependencies-list">
                                ${entity.dependencies.slice(0, 3).map(dep => `
                                    <span class="dependency-badge">${dep}</span>
                                `).join('')}
                                ${entity.dependencies.length > 3 ? `
                                    <span class="dependency-more">+${entity.dependencies.length - 3} more</span>
                                ` : ''}
                            </div>
                        </div>
                    ` : ''}
                </div>

                <div class="card-footer">
                    <button class="card-action" onclick="viewEntityDetails('${entity.id}')">
                        <span>View Details</span>
                        <span>→</span>
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Render filter bar
     */
    static renderFilterBar(entities, filters) {
        const allStatuses = [...new Set(entities.map(e => e.status))];
        const allTypes = [...new Set(entities.map(e => e.kind))];
        const allTags = [...new Set(entities.flatMap(e => e.tags))];

        return `
            <div class="filter-bar">
                <div class="filter-group">
                    <label class="filter-label">Status:</label>
                    <select class="filter-select" id="filterStatus">
                        <option value="all">All</option>
                        ${allStatuses.map(status => `
                            <option value="${status}" ${filters.status === status ? 'selected' : ''}>
                                ${status}
                            </option>
                        `).join('')}
                    </select>
                </div>

                <div class="filter-group">
                    <label class="filter-label">Type:</label>
                    <select class="filter-select" id="filterType">
                        <option value="all">All</option>
                        ${allTypes.map(type => `
                            <option value="${type}" ${filters.type === type ? 'selected' : ''}>
                                ${type}
                            </option>
                        `).join('')}
                    </select>
                </div>

                ${allTags.length > 0 ? `
                <div class="filter-group">
                    <label class="filter-label">Tag:</label>
                    <select class="filter-select" id="filterTag">
                        <option value="all">All</option>
                        ${allTags.slice(0, 20).map(tag => `
                            <option value="${tag}" ${filters.tag === tag ? 'selected' : ''}>
                                ${tag}
                            </option>
                        `).join('')}
                    </select>
                </div>
                ` : ''}

                <button class="btn-reset-filters" id="resetFilters">
                    <span>🔄</span>
                    <span>Reset</span>
                </button>
            </div>
        `;
    }

    /**
     * Apply filters to entities
     */
    static applyFilters(entities, filters) {
        return entities.filter(entity => {
            if (filters.status && filters.status !== 'all' && entity.status !== filters.status) return false;
            if (filters.type && filters.type !== 'all' && entity.kind !== filters.type) return false;
            if (filters.tag && filters.tag !== 'all' && !entity.tags.includes(filters.tag)) return false;
            if (filters.search) {
                const searchLower = filters.search.toLowerCase();
                const matches = 
                    entity.label.toLowerCase().includes(searchLower) ||
                    entity.id.toLowerCase().includes(searchLower) ||
                    entity.summary.toLowerCase().includes(searchLower);
                if (!matches) return false;
            }
            return true;
        });
    }

    /**
     * Render Raw view (pretty printed with syntax highlighting)
     */
    static renderRaw(content, format = 'yaml') {
        const escaped = content
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');

        return `
            <div class="raw-container">
                <div class="raw-header">
                    <div class="raw-format-badge">${format.toUpperCase()}</div>
                    <div class="raw-actions">
                        <button class="btn-raw-action" onclick="copyRawContent()">
                            <span>📋</span>
                            <span>Copy</span>
                        </button>
                        <button class="btn-raw-action" onclick="downloadRawContent()">
                            <span>💾</span>
                            <span>Download</span>
                        </button>
                    </div>
                </div>
                <div class="raw-search">
                    <input type="text" 
                           class="raw-search-input" 
                           placeholder="Search in content (Ctrl+F)..."
                           onkeyup="searchRawContent(event)">
                    <div class="raw-search-results" id="rawSearchResults"></div>
                </div>
                <pre class="raw-content" id="rawContent"><code>${escaped}</code></pre>
            </div>
        `;
    }

    /**
     * Get schema icon
     */
    static getSchemaIcon(type) {
        const icons = {
            'registry': '📚',
            'workflow': '🔄',
            'collection': '📦',
            'graph': '🕸️',
            'generic': '📄'
        };
        return icons[type] || '📄';
    }

    /**
     * Get entity icon based on kind
     */
    static getEntityIcon(kind) {
        const icons = {
            'phase': '📋',
            'workflow-step': '➡️',
            'component': '🧩',
            'item': '📌',
            'tool': '🔧',
            'service': '⚙️',
            'api': '🔌',
            'database': '💾',
            'config': '⚙️'
        };
        return icons[kind] || '📄';
    }

    /**
     * Render error state
     */
    static renderError(error, fileName) {
        let errorDetails = '';
        
        if (error.mark) {
            errorDetails = `
                <div class="error-location">
                    Line ${error.mark.line + 1}, Column ${error.mark.column + 1}
                </div>
            `;
        }

        return `
            <div class="error-container">
                <div class="error-icon">⚠️</div>
                <div class="error-title">YAML Parse Error</div>
                <div class="error-file">${fileName}</div>
                ${errorDetails}
                <div class="error-message">${error.message || error.toString()}</div>
                <div class="error-actions">
                    <button class="btn-error-action" onclick="viewRawContent()">
                        View Raw Content
                    </button>
                    <button class="btn-error-action" onclick="closeErrorFile()">
                        Close File
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Render loading skeleton
     */
    static renderSkeleton() {
        return `
            <div class="skeleton-container">
                <div class="skeleton-header"></div>
                <div class="skeleton-metrics">
                    <div class="skeleton-card"></div>
                    <div class="skeleton-card"></div>
                    <div class="skeleton-card"></div>
                    <div class="skeleton-card"></div>
                </div>
                <div class="skeleton-content"></div>
            </div>
        `;
    }
}

// Export for use in app.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ViewRenderers };
}
