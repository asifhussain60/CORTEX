/**
 * Use Cases Tab Component
 * 
 * GPT Spec Section 6: Use Cases tab with scalable organization (100+)
 * 
 * Features:
 * - Fuse.js fuzzy search (title + summary + tags)
 * - Filter by Persona, Category, Severity
 * - Grouping by Persona or Category
 * - Saved views (Leadership, Security, Release Readiness)
 * - Grid.js virtualization for large lists
 * - Side drawer for use case details
 * 
 * Dependencies:
 * - Fuse.js (vendored locally)
 * - Grid.js (vendored locally)
 * 
 * @version 1.0.0
 * @license MIT
 */

(function(global) {
    'use strict';
    
    /**
     * Use Cases Tab Configuration
     */
    const CONFIG = {
        searchThreshold: 0.4,
        searchKeys: ['title', 'summary', 'tags'],
        pageSize: 25,
        groupings: {
            persona: 'Persona',
            category: 'Category'
        },
        savedViews: {
            leadership: {
                name: 'Leadership View',
                filters: { persona: 'leadership' }
            },
            security: {
                name: 'Security View',
                filters: { persona: 'security', category: 'risk' }
            },
            release: {
                name: 'Release Readiness',
                filters: { category: ['delivery', 'reliability'] }
            }
        }
    };
    
    /**
     * Persona labels and icons
     */
    const PERSONAS = {
        leadership: { label: 'Leadership', icon: '👔', color: '#9333ea' },
        production_owner: { label: 'Production Owner', icon: '🏭', color: '#2563eb' },
        engineer: { label: 'Engineer', icon: '🛠️', color: '#16a34a' },
        security: { label: 'Security', icon: '🛡️', color: '#dc2626' },
        qa: { label: 'QA', icon: '🧪', color: '#ca8a04' }
    };
    
    /**
     * Category labels and icons
     */
    const CATEGORIES = {
        delivery: { label: 'Delivery', icon: '🚀', color: '#2563eb' },
        risk: { label: 'Risk', icon: '⚠️', color: '#dc2626' },
        compliance: { label: 'Compliance', icon: '📋', color: '#9333ea' },
        reliability: { label: 'Reliability', icon: '🔧', color: '#16a34a' },
        cost: { label: 'Cost', icon: '💰', color: '#ca8a04' },
        maintainability: { label: 'Maintainability', icon: '🔨', color: '#0891b2' },
        observability: { label: 'Observability', icon: '👁️', color: '#7c3aed' }
    };
    
    /**
     * Severity levels
     */
    const SEVERITIES = {
        info: { label: 'Info', color: '#6b7280' },
        low: { label: 'Low', color: '#16a34a' },
        medium: { label: 'Medium', color: '#ca8a04' },
        high: { label: 'High', color: '#f97316' },
        critical: { label: 'Critical', color: '#dc2626' }
    };
    
    /**
     * UseCasesManager - Main controller for Use Cases tab
     */
    class UseCasesManager {
        /**
         * Create UseCasesManager
         * @param {HTMLElement} container - Container element
         * @param {Array} useCases - Use case data array
         * @param {Object} options - Configuration options
         */
        constructor(container, useCases, options = {}) {
            this.container = container;
            this.useCases = useCases || [];
            this.options = { ...CONFIG, ...options };
            
            // State
            this.filteredUseCases = [...this.useCases];
            this.currentFilters = {};
            this.currentGrouping = 'persona';
            this.searchQuery = '';
            
            // Initialize Fuse.js for search
            this.fuse = null;
            this._initSearch();
            
            // Grid.js instance
            this.grid = null;
            
            // Drawer element
            this.drawer = null;
            
            this._render();
        }
        
        /**
         * Initialize Fuse.js search
         * @private
         */
        _initSearch() {
            if (typeof Fuse !== 'undefined') {
                this.fuse = new Fuse(this.useCases, {
                    keys: this.options.searchKeys,
                    threshold: this.options.searchThreshold,
                    includeScore: true
                });
            } else {
                console.warn('UseCases: Fuse.js not loaded, falling back to simple search');
            }
        }
        
        /**
         * Render the use cases tab
         * @private
         */
        _render() {
            this.container.innerHTML = `
                <div class="use-cases-container">
                    <!-- Controls Bar -->
                    <div class="use-cases-controls">
                        <div class="search-wrapper">
                            <input 
                                type="text" 
                                class="use-cases-search" 
                                placeholder="Search use cases..."
                                aria-label="Search use cases"
                            >
                            <span class="search-icon">🔍</span>
                        </div>
                        
                        <div class="filter-group">
                            <label>Persona:</label>
                            <select class="filter-select" data-filter="persona">
                                <option value="">All</option>
                                ${Object.entries(PERSONAS).map(([key, p]) => 
                                    `<option value="${key}">${p.icon} ${p.label}</option>`
                                ).join('')}
                            </select>
                        </div>
                        
                        <div class="filter-group">
                            <label>Category:</label>
                            <select class="filter-select" data-filter="category">
                                <option value="">All</option>
                                ${Object.entries(CATEGORIES).map(([key, c]) => 
                                    `<option value="${key}">${c.icon} ${c.label}</option>`
                                ).join('')}
                            </select>
                        </div>
                        
                        <div class="filter-group">
                            <label>Severity:</label>
                            <select class="filter-select" data-filter="severity">
                                <option value="">All</option>
                                ${Object.entries(SEVERITIES).map(([key, s]) => 
                                    `<option value="${key}">${s.label}</option>`
                                ).join('')}
                            </select>
                        </div>
                        
                        <div class="filter-group">
                            <label>Group by:</label>
                            <select class="grouping-select">
                                <option value="persona">Persona</option>
                                <option value="category">Category</option>
                            </select>
                        </div>
                    </div>
                    
                    <!-- Saved Views -->
                    <div class="saved-views">
                        ${Object.entries(this.options.savedViews).map(([key, view]) => 
                            `<button class="saved-view-btn" data-view="${key}">${view.name}</button>`
                        ).join('')}
                        <button class="saved-view-btn clear-btn" data-view="clear">Clear Filters</button>
                    </div>
                    
                    <!-- Results Summary -->
                    <div class="results-summary">
                        Showing <span class="results-count">${this.useCases.length}</span> use cases
                    </div>
                    
                    <!-- Use Cases Grid -->
                    <div class="use-cases-grid" id="use-cases-grid"></div>
                </div>
                
                <!-- Detail Drawer -->
                <div class="use-case-drawer" aria-hidden="true">
                    <div class="drawer-content">
                        <button class="drawer-close" aria-label="Close">&times;</button>
                        <div class="drawer-body"></div>
                    </div>
                </div>
            `;
            
            this._attachEventListeners();
            this._renderGrid();
        }
        
        /**
         * Render the use cases grid (with or without Grid.js)
         * @private
         */
        _renderGrid() {
            const gridContainer = this.container.querySelector('#use-cases-grid');
            
            if (typeof gridjs !== 'undefined' && gridjs.Grid) {
                // Use Grid.js for virtualization
                this._renderWithGridJS(gridContainer);
            } else {
                // Fallback to grouped card view
                this._renderGroupedCards(gridContainer);
            }
        }
        
        /**
         * Render with Grid.js
         * @private
         */
        _renderWithGridJS(container) {
            const data = this._prepareGridData();
            
            this.grid = new gridjs.Grid({
                columns: [
                    {
                        name: 'Title',
                        formatter: (cell, row) => gridjs.html(`
                            <strong style="color: #4d8cff">${cell}</strong>
                        `)
                    },
                    {
                        name: 'Persona',
                        formatter: (cell) => {
                            const persona = PERSONAS[cell] || { icon: '👤', label: cell };
                            return gridjs.html(`
                                <span class="persona-badge" style="background: ${persona.color}20; color: ${persona.color}">
                                    ${persona.icon} ${persona.label}
                                </span>
                            `);
                        }
                    },
                    {
                        name: 'Category',
                        formatter: (cell) => {
                            const category = CATEGORIES[cell] || { icon: '📁', label: cell };
                            return gridjs.html(`
                                <span class="category-badge">
                                    ${category.icon} ${category.label}
                                </span>
                            `);
                        }
                    },
                    {
                        name: 'Severity',
                        formatter: (cell) => {
                            const severity = SEVERITIES[cell] || { color: '#6b7280', label: cell };
                            return gridjs.html(`
                                <span class="severity-badge" style="background: ${severity.color}20; color: ${severity.color}">
                                    ${severity.label}
                                </span>
                            `);
                        }
                    },
                    {
                        name: 'Actions',
                        formatter: (_, row) => gridjs.html(`
                            <button class="view-details-btn" data-id="${row.cells[4].data}">
                                View Details
                            </button>
                        `)
                    }
                ],
                data: data,
                pagination: {
                    limit: this.options.pageSize
                },
                search: false, // We handle search ourselves
                sort: true,
                className: {
                    container: 'gridjs-use-cases',
                    table: 'gridjs-table',
                    th: 'gridjs-th',
                    td: 'gridjs-td'
                },
                style: {
                    table: {
                        'background': 'transparent'
                    }
                }
            }).render(container);
            
            // Attach click handlers for view details
            container.addEventListener('click', (e) => {
                const btn = e.target.closest('.view-details-btn');
                if (btn) {
                    const id = btn.dataset.id;
                    const useCase = this.useCases.find(uc => uc.id === id);
                    if (useCase) {
                        this._openDrawer(useCase);
                    }
                }
            });
        }
        
        /**
         * Prepare data for Grid.js
         * @private
         */
        _prepareGridData() {
            return this.filteredUseCases.map(uc => [
                uc.title,
                uc.persona,
                uc.category,
                uc.severity,
                uc.id
            ]);
        }
        
        /**
         * Render grouped cards (fallback without Grid.js)
         * @private
         */
        _renderGroupedCards(container) {
            const grouped = this._groupUseCases();
            
            let html = '';
            
            for (const [groupKey, items] of Object.entries(grouped)) {
                const groupInfo = this.currentGrouping === 'persona' 
                    ? PERSONAS[groupKey] 
                    : CATEGORIES[groupKey];
                const label = groupInfo?.label || groupKey;
                const icon = groupInfo?.icon || '📁';
                
                html += `
                    <div class="use-case-group">
                        <h3 class="group-header">
                            <span class="group-icon">${icon}</span>
                            ${label}
                            <span class="group-count">${items.length}</span>
                        </h3>
                        <div class="group-items">
                            ${items.map(uc => this._renderUseCaseCard(uc)).join('')}
                        </div>
                    </div>
                `;
            }
            
            container.innerHTML = html || '<p class="no-results">No use cases match your filters.</p>';
            
            // Attach click handlers
            container.querySelectorAll('.use-case-card').forEach(card => {
                card.addEventListener('click', () => {
                    const id = card.dataset.id;
                    const useCase = this.useCases.find(uc => uc.id === id);
                    if (useCase) {
                        this._openDrawer(useCase);
                    }
                });
            });
        }
        
        /**
         * Render a single use case card
         * @private
         */
        _renderUseCaseCard(uc) {
            const severity = SEVERITIES[uc.severity] || SEVERITIES.info;
            
            return `
                <div class="use-case-card" data-id="${uc.id}" tabindex="0">
                    <div class="card-header">
                        <h4 class="card-title">${uc.title}</h4>
                        <span class="severity-badge" style="background: ${severity.color}20; color: ${severity.color}">
                            ${severity.label}
                        </span>
                    </div>
                    <p class="card-summary">${uc.summary}</p>
                    <div class="card-tags">
                        ${(uc.tags || []).slice(0, 3).map(tag => 
                            `<span class="tag">${tag}</span>`
                        ).join('')}
                    </div>
                </div>
            `;
        }
        
        /**
         * Group use cases by current grouping
         * @private
         */
        _groupUseCases() {
            const grouped = {};
            
            for (const uc of this.filteredUseCases) {
                const key = uc[this.currentGrouping] || 'other';
                if (!grouped[key]) {
                    grouped[key] = [];
                }
                grouped[key].push(uc);
            }
            
            return grouped;
        }
        
        /**
         * Attach event listeners
         * @private
         */
        _attachEventListeners() {
            // Search
            const searchInput = this.container.querySelector('.use-cases-search');
            searchInput.addEventListener('input', this._debounce((e) => {
                this.searchQuery = e.target.value;
                this._applyFilters();
            }, 300));
            
            // Filters
            this.container.querySelectorAll('.filter-select').forEach(select => {
                select.addEventListener('change', (e) => {
                    const filterType = e.target.dataset.filter;
                    this.currentFilters[filterType] = e.target.value || null;
                    this._applyFilters();
                });
            });
            
            // Grouping
            const groupingSelect = this.container.querySelector('.grouping-select');
            groupingSelect.addEventListener('change', (e) => {
                this.currentGrouping = e.target.value;
                this._renderGrid();
            });
            
            // Saved views
            this.container.querySelectorAll('.saved-view-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const viewKey = e.target.dataset.view;
                    if (viewKey === 'clear') {
                        this._clearFilters();
                    } else {
                        this._applySavedView(viewKey);
                    }
                });
            });
            
            // Drawer close
            const drawer = this.container.querySelector('.use-case-drawer');
            const closeBtn = drawer.querySelector('.drawer-close');
            
            closeBtn.addEventListener('click', () => this._closeDrawer());
            drawer.addEventListener('click', (e) => {
                if (e.target === drawer) {
                    this._closeDrawer();
                }
            });
            
            // Keyboard navigation
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    this._closeDrawer();
                }
            });
        }
        
        /**
         * Apply current filters and search
         * @private
         */
        _applyFilters() {
            let results = this.useCases;
            
            // Apply search
            if (this.searchQuery && this.fuse) {
                results = this.fuse.search(this.searchQuery).map(r => r.item);
            } else if (this.searchQuery) {
                // Simple search fallback
                const query = this.searchQuery.toLowerCase();
                results = results.filter(uc => 
                    uc.title.toLowerCase().includes(query) ||
                    uc.summary.toLowerCase().includes(query) ||
                    (uc.tags || []).some(t => t.toLowerCase().includes(query))
                );
            }
            
            // Apply filters
            for (const [filterType, value] of Object.entries(this.currentFilters)) {
                if (!value) continue;
                
                if (Array.isArray(value)) {
                    results = results.filter(uc => value.includes(uc[filterType]));
                } else {
                    results = results.filter(uc => uc[filterType] === value);
                }
            }
            
            this.filteredUseCases = results;
            
            // Update count
            const countEl = this.container.querySelector('.results-count');
            if (countEl) {
                countEl.textContent = this.filteredUseCases.length;
            }
            
            this._renderGrid();
        }
        
        /**
         * Apply a saved view
         * @private
         */
        _applySavedView(viewKey) {
            const view = this.options.savedViews[viewKey];
            if (!view) return;
            
            this.currentFilters = { ...view.filters };
            
            // Update select elements
            for (const [filterType, value] of Object.entries(this.currentFilters)) {
                const select = this.container.querySelector(`[data-filter="${filterType}"]`);
                if (select) {
                    select.value = Array.isArray(value) ? value[0] : (value || '');
                }
            }
            
            // Highlight active view button
            this.container.querySelectorAll('.saved-view-btn').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.view === viewKey);
            });
            
            this._applyFilters();
        }
        
        /**
         * Clear all filters
         * @private
         */
        _clearFilters() {
            this.currentFilters = {};
            this.searchQuery = '';
            
            // Reset UI
            this.container.querySelector('.use-cases-search').value = '';
            this.container.querySelectorAll('.filter-select').forEach(s => s.value = '');
            this.container.querySelectorAll('.saved-view-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            this._applyFilters();
        }
        
        /**
         * Open use case detail drawer
         * @private
         */
        _openDrawer(useCase) {
            const drawer = this.container.querySelector('.use-case-drawer');
            const body = drawer.querySelector('.drawer-body');
            
            const persona = PERSONAS[useCase.persona] || { icon: '👤', label: useCase.persona };
            const category = CATEGORIES[useCase.category] || { icon: '📁', label: useCase.category };
            const severity = SEVERITIES[useCase.severity] || SEVERITIES.info;
            
            body.innerHTML = `
                <h2 class="drawer-title">${useCase.title}</h2>
                
                <div class="drawer-meta">
                    <span class="meta-badge" style="background: ${persona.color}20; color: ${persona.color}">
                        ${persona.icon} ${persona.label}
                    </span>
                    <span class="meta-badge">
                        ${category.icon} ${category.label}
                    </span>
                    <span class="meta-badge" style="background: ${severity.color}20; color: ${severity.color}">
                        ${severity.label}
                    </span>
                </div>
                
                <div class="drawer-section">
                    <h3>Summary</h3>
                    <p>${useCase.summary}</p>
                </div>
                
                ${useCase.signals && useCase.signals.length ? `
                <div class="drawer-section">
                    <h3>Signals</h3>
                    <ul class="signals-list">
                        ${useCase.signals.map(s => `<li>${s}</li>`).join('')}
                    </ul>
                </div>
                ` : ''}
                
                ${useCase.actions && useCase.actions.length ? `
                <div class="drawer-section">
                    <h3>Recommended Actions</h3>
                    <ul class="actions-list">
                        ${useCase.actions.map(a => `<li>${a}</li>`).join('')}
                    </ul>
                </div>
                ` : ''}
                
                ${useCase.related_tabs && useCase.related_tabs.length ? `
                <div class="drawer-section">
                    <h3>Related Tabs</h3>
                    <div class="related-tabs">
                        ${useCase.related_tabs.map(tab => `
                            <button class="related-tab-btn" data-tab="${tab}">
                                Jump to ${tab}
                            </button>
                        `).join('')}
                    </div>
                </div>
                ` : ''}
                
                ${useCase.tags && useCase.tags.length ? `
                <div class="drawer-section">
                    <h3>Tags</h3>
                    <div class="drawer-tags">
                        ${useCase.tags.map(t => `<span class="tag">${t}</span>`).join('')}
                    </div>
                </div>
                ` : ''}
            `;
            
            drawer.setAttribute('aria-hidden', 'false');
            drawer.classList.add('open');
            
            // Focus close button
            drawer.querySelector('.drawer-close').focus();
            
            // Handle related tab jumps
            body.querySelectorAll('.related-tab-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const tabId = btn.dataset.tab;
                    // Dispatch custom event for tab switching
                    document.dispatchEvent(new CustomEvent('jumpToTab', { 
                        detail: { tabId } 
                    }));
                    this._closeDrawer();
                });
            });
        }
        
        /**
         * Close detail drawer
         * @private
         */
        _closeDrawer() {
            const drawer = this.container.querySelector('.use-case-drawer');
            drawer.setAttribute('aria-hidden', 'true');
            drawer.classList.remove('open');
        }
        
        /**
         * Debounce helper
         * @private
         */
        _debounce(fn, delay) {
            let timeoutId;
            return (...args) => {
                clearTimeout(timeoutId);
                timeoutId = setTimeout(() => fn.apply(this, args), delay);
            };
        }
        
        /**
         * Update use cases data
         * @param {Array} useCases - New use cases array
         */
        updateData(useCases) {
            this.useCases = useCases || [];
            this._initSearch();
            this._applyFilters();
        }
    }
    
    /**
     * Factory function to create UseCasesManager
     * @param {string|HTMLElement} container - Container element or selector
     * @param {Array} useCases - Use case data
     * @param {Object} options - Configuration options
     * @returns {UseCasesManager}
     */
    function createUseCasesTab(container, useCases, options = {}) {
        const element = typeof container === 'string'
            ? document.querySelector(container)
            : container;
            
        if (!element) {
            throw new Error(`UseCases: Container not found: ${container}`);
        }
        
        return new UseCasesManager(element, useCases, options);
    }
    
    // Export to global
    global.UseCasesManager = UseCasesManager;
    global.createUseCasesTab = createUseCasesTab;
    
})(typeof window !== 'undefined' ? window : this);
