/**
 * CORTEX SPA - Use Cases Manager Component
 * Handles search, filter, and display of use cases with Fuse.js
 * Version: 1.0.0
 */

class UseCasesManager {
    constructor(options = {}) {
        this.options = {
            containerId: 'use-cases-grid',
            searchInputId: 'use-cases-search',
            personaFilterId: 'persona-filter',
            categoryFilterId: 'category-filter',
            drawerEnabled: true,
            fuseOptions: {
                keys: ['title', 'description', 'category', 'persona', 'tags'],
                threshold: 0.3,
                includeScore: true
            },
            ...options
        };
        
        this.useCases = [];
        this.filteredCases = [];
        this.fuse = null;
        this.drawer = null;
        this.backdrop = null;
        
        this.currentFilters = {
            search: '',
            persona: 'all',
            category: 'all'
        };
    }
    
    /**
     * Initialize with use case data
     */
    init(useCases = []) {
        this.useCases = useCases;
        this.filteredCases = [...useCases];
        
        // Initialize Fuse.js for fuzzy search
        if (typeof Fuse !== 'undefined') {
            this.fuse = new Fuse(useCases, this.options.fuseOptions);
        }
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Setup drawer if enabled
        if (this.options.drawerEnabled) {
            this.setupDrawer();
        }
        
        // Populate filter dropdowns
        this.populateFilters();
        
        // Initial render
        this.render();
    }
    
    setupEventListeners() {
        // Search input
        const searchInput = document.getElementById(this.options.searchInputId);
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce((e) => {
                this.currentFilters.search = e.target.value;
                this.applyFilters();
            }, 200));
        }
        
        // Persona filter
        const personaFilter = document.getElementById(this.options.personaFilterId);
        if (personaFilter) {
            personaFilter.addEventListener('change', (e) => {
                this.currentFilters.persona = e.target.value;
                this.applyFilters();
            });
        }
        
        // Category filter
        const categoryFilter = document.getElementById(this.options.categoryFilterId);
        if (categoryFilter) {
            categoryFilter.addEventListener('change', (e) => {
                this.currentFilters.category = e.target.value;
                this.applyFilters();
            });
        }
    }
    
    setupDrawer() {
        // Create drawer elements if they don't exist
        if (!document.getElementById('use-case-drawer')) {
            const drawerHtml = `
                <div id="use-case-drawer-backdrop" class="use-case-drawer__backdrop"></div>
                <aside id="use-case-drawer" class="use-case-drawer" aria-hidden="true">
                    <header class="use-case-drawer__header">
                        <h3 id="drawer-title" class="text-lg font-semibold"></h3>
                        <button id="drawer-close" class="btn btn-icon" aria-label="Close">
                            <span>✕</span>
                        </button>
                    </header>
                    <div id="drawer-content" class="use-case-drawer__content"></div>
                </aside>
            `;
            document.body.insertAdjacentHTML('beforeend', drawerHtml);
        }
        
        this.drawer = document.getElementById('use-case-drawer');
        this.backdrop = document.getElementById('use-case-drawer-backdrop');
        
        // Close handlers
        document.getElementById('drawer-close')?.addEventListener('click', () => this.closeDrawer());
        this.backdrop?.addEventListener('click', () => this.closeDrawer());
        
        // Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.drawer?.classList.contains('open')) {
                this.closeDrawer();
            }
        });
    }
    
    populateFilters() {
        // Get unique personas
        const personas = [...new Set(this.useCases.map(uc => uc.persona).filter(Boolean))];
        const personaFilter = document.getElementById(this.options.personaFilterId);
        if (personaFilter) {
            personaFilter.innerHTML = '<option value="all">All Personas</option>';
            personas.forEach(p => {
                personaFilter.innerHTML += `<option value="${p}">${p}</option>`;
            });
        }
        
        // Get unique categories
        const categories = [...new Set(this.useCases.map(uc => uc.category).filter(Boolean))];
        const categoryFilter = document.getElementById(this.options.categoryFilterId);
        if (categoryFilter) {
            categoryFilter.innerHTML = '<option value="all">All Categories</option>';
            categories.forEach(c => {
                categoryFilter.innerHTML += `<option value="${c}">${c}</option>`;
            });
        }
    }
    
    applyFilters() {
        let results = [...this.useCases];
        
        // Apply search
        if (this.currentFilters.search && this.fuse) {
            results = this.fuse.search(this.currentFilters.search).map(r => r.item);
        }
        
        // Apply persona filter
        if (this.currentFilters.persona !== 'all') {
            results = results.filter(uc => uc.persona === this.currentFilters.persona);
        }
        
        // Apply category filter
        if (this.currentFilters.category !== 'all') {
            results = results.filter(uc => uc.category === this.currentFilters.category);
        }
        
        this.filteredCases = results;
        this.render();
    }
    
    render() {
        const container = document.getElementById(this.options.containerId);
        if (!container) return;
        
        if (this.filteredCases.length === 0) {
            container.innerHTML = `
                <div class="no-data">
                    <div class="no-data__icon">🔍</div>
                    <div class="no-data__title">No use cases found</div>
                    <div class="no-data__description">Try adjusting your search or filters</div>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.filteredCases.map((uc, index) => this.renderCard(uc, index)).join('');
        
        // Add click handlers for cards
        container.querySelectorAll('.use-case-card').forEach((card, index) => {
            card.addEventListener('click', () => this.openDrawer(this.filteredCases[index]));
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.openDrawer(this.filteredCases[index]);
                }
            });
        });
        
        // Update count
        const countEl = document.getElementById('use-cases-count');
        if (countEl) {
            countEl.textContent = `${this.filteredCases.length} of ${this.useCases.length}`;
        }
    }
    
    renderCard(useCase, index) {
        const personaBadgeClass = this.getPersonaBadgeClass(useCase.persona);
        const tags = useCase.tags?.slice(0, 3) || [];
        
        return `
            <article class="use-case-card" tabindex="0" role="button" aria-label="View details for ${useCase.title}" data-index="${index}">
                <div class="use-case-card__header">
                    <h4 class="use-case-card__title">${this.escapeHtml(useCase.title)}</h4>
                    <span class="badge ${personaBadgeClass} use-case-card__persona">${this.escapeHtml(useCase.persona || 'General')}</span>
                </div>
                <p class="use-case-card__description">${this.escapeHtml(this.truncate(useCase.description, 120))}</p>
                <div class="use-case-card__meta">
                    ${useCase.category ? `<span class="use-case-card__tag">${this.escapeHtml(useCase.category)}</span>` : ''}
                    ${tags.map(t => `<span class="use-case-card__tag">${this.escapeHtml(t)}</span>`).join('')}
                </div>
            </article>
        `;
    }
    
    openDrawer(useCase) {
        if (!this.drawer) return;
        
        const title = document.getElementById('drawer-title');
        const content = document.getElementById('drawer-content');
        
        if (title) title.textContent = useCase.title;
        if (content) {
            content.innerHTML = this.renderDrawerContent(useCase);
        }
        
        this.drawer.classList.add('open');
        this.drawer.setAttribute('aria-hidden', 'false');
        this.backdrop?.classList.add('open');
        document.body.style.overflow = 'hidden';
        
        // Focus management
        this.drawer.querySelector('button')?.focus();
    }
    
    closeDrawer() {
        if (!this.drawer) return;
        
        this.drawer.classList.remove('open');
        this.drawer.setAttribute('aria-hidden', 'true');
        this.backdrop?.classList.remove('open');
        document.body.style.overflow = '';
    }
    
    renderDrawerContent(useCase) {
        return `
            <div class="use-case-drawer__section">
                <div class="flex gap-2 mb-4">
                    <span class="badge ${this.getPersonaBadgeClass(useCase.persona)}">${this.escapeHtml(useCase.persona || 'General')}</span>
                    ${useCase.category ? `<span class="badge">${this.escapeHtml(useCase.category)}</span>` : ''}
                </div>
            </div>
            
            <div class="use-case-drawer__section">
                <h4 class="use-case-drawer__section-title">Description</h4>
                <p class="text-secondary">${this.escapeHtml(useCase.description)}</p>
            </div>
            
            ${useCase.business_value ? `
            <div class="use-case-drawer__section">
                <h4 class="use-case-drawer__section-title">Business Value</h4>
                <p class="text-secondary">${this.escapeHtml(useCase.business_value)}</p>
            </div>
            ` : ''}
            
            ${useCase.implementation_notes ? `
            <div class="use-case-drawer__section">
                <h4 class="use-case-drawer__section-title">Implementation Notes</h4>
                <p class="text-secondary">${this.escapeHtml(useCase.implementation_notes)}</p>
            </div>
            ` : ''}
            
            ${useCase.related_files?.length ? `
            <div class="use-case-drawer__section">
                <h4 class="use-case-drawer__section-title">Related Files</h4>
                <ul class="text-sm text-muted" style="list-style: none; padding: 0;">
                    ${useCase.related_files.map(f => `<li style="padding: 0.25rem 0; font-family: var(--font-family-mono);">📄 ${this.escapeHtml(f)}</li>`).join('')}
                </ul>
            </div>
            ` : ''}
            
            ${useCase.tags?.length ? `
            <div class="use-case-drawer__section">
                <h4 class="use-case-drawer__section-title">Tags</h4>
                <div class="flex gap-2" style="flex-wrap: wrap;">
                    ${useCase.tags.map(t => `<span class="badge">${this.escapeHtml(t)}</span>`).join('')}
                </div>
            </div>
            ` : ''}
        `;
    }
    
    getPersonaBadgeClass(persona) {
        const map = {
            'Developer': 'badge-info',
            'DevOps': 'badge-warning',
            'Security': 'badge-danger',
            'Manager': 'badge-success',
            'Architect': 'badge-info',
            'QA': 'badge-warning'
        };
        return map[persona] || 'badge';
    }
    
    // Utility functions
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    truncate(text, length) {
        if (!text || text.length <= length) return text || '';
        return text.substring(0, length) + '...';
    }
    
    debounce(fn, delay) {
        let timeoutId;
        return (...args) => {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => fn.apply(this, args), delay);
        };
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UseCasesManager;
}
