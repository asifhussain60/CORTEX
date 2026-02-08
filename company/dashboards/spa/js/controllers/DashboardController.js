/**
 * DashboardController - Refactored Main Application Controller
 * 
 * Architecture:
 * - Dependency Injection (all services injected)
 * - Single Responsibility (only coordinates, no business logic)
 * - Open/Closed (extensible via services)
 * - Dependency Inversion (depends on abstractions)
 * 
 * Authority: violations.md § SOLID Violations & Modular Architecture
 * Audit: AC_START: AC-SPA-001-05
 */

class DashboardController {
    constructor() {
        // Services (injected dependencies)
        this.stateManager = null;
        this.errorBoundary = null;
        this.repositoryService = null;
        this.validationService = null;
        
        // DOM references
        this.dom = {};
        
        // Render cancellation tokens
        this.renderTokens = new Map();
        
        // Configuration
        this.config = {
            repositories: ['cortex', 'ksessions', 'kashkole', 'alist', 'noor-canvas'],
            dataDir: './data',
            defaultRepo: 'ksessions',
            tabs: [
                { id: 'overview', icon: 'fas fa-chart-line', label: 'Overview' },
                { id: 'architecture', icon: 'fas fa-sitemap', label: 'Architecture' },
                { id: 'quality', icon: 'fas fa-medal', label: 'Quality' },
                { id: 'security', icon: 'fas fa-shield-alt', label: 'Security' },
                { id: 'dependencies', icon: 'fas fa-cubes', label: 'Dependencies' },
                { id: 'usecases', icon: 'fas fa-lightbulb', label: 'Use Cases' }
            ]
        };
    }
    
    /**
     * Initialize dashboard with dependency injection
     */
    async initialize(services) {
        console.log('[Controller] Initializing dashboard...');
        
        // Inject dependencies
        console.log('[Controller] → Injecting dependencies...');
        this.errorBoundary = services.errorBoundary;
        this.stateManager = services.stateManager;
        this.repositoryService = services.repositoryService;
        this.validationService = services.validationService;
        console.log('[Controller] ✓ Dependencies injected');
        
        // Initialize DOM references
        console.log('[Controller] → Initializing DOM references...');
        this._initDOMReferences();
        console.log('[Controller] ✓ DOM references initialized');
        
        // Subscribe to state changes
        console.log('[Controller] → Subscribing to state changes...');
        this.stateManager.subscribe('controller', this._onStateChange.bind(this));
        console.log('[Controller] ✓ State subscription active');
        
        // Setup event listeners
        console.log('[Controller] → Setting up event listeners...');
        this._setupEventListeners();
        console.log('[Controller] ✓ Event listeners attached');
        
        // Load initial repository from URL or default
        const params = this._parseUrlParams();
        const initialRepo = params.repo || this.config.defaultRepo;
        console.log('[Controller] → Loading initial repository:', initialRepo);
        console.log('[Controller]   URL params:', params);
        console.log('[Controller]   Default repo:', this.config.defaultRepo);
        
        await this.loadRepository(initialRepo);
        
        console.log('[Controller] ✅ Initialization complete');
    }
    
    /**
     * Load repository data
     */
    async loadRepository(repoName) {
        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        console.log(`[Controller] loadRepository: Starting load for "${repoName}"`);
        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        
        console.log('[Controller] loadRepository: Generation BEFORE state update:', this.stateManager.getGeneration());
        
        // Update state: loading started
        console.log('[Controller] loadRepository: → Updating state (loading started)...');
        this.stateManager.setState(draft => {
            draft.currentRepo = repoName;
            draft.isLoading = true;
            draft.data = null;
        });
        console.log('[Controller] loadRepository: ✓ State updated');
        
        // CRITICAL: Capture generation AFTER state update
        const generation = this.stateManager.getGeneration();
        console.log('[Controller] loadRepository: Generation AFTER state update (CAPTURED):', generation);
        
        // Show loading UI
        console.log('[Controller] loadRepository: → Showing loading overlay...');
        this._showLoading(true);
        console.log('[Controller] loadRepository: ✓ Loading overlay visible');
        
        try {
            // Check cache
            console.log('[Controller] loadRepository: → Checking cache...');
            const cached = this.stateManager.getCacheEntry(repoName);
            let data;
            
            if (cached && (Date.now() - cached.timestamp < 300000)) { // 5 min TTL
                console.log('[Controller] loadRepository: ✓ Cache HIT');
                console.log('[Controller] loadRepository:   Cache age:', Math.round((Date.now() - cached.timestamp) / 1000), 'seconds');
                console.log('[Controller] loadRepository:   Cache hits:', cached.hits);
                data = cached.data;
                cached.hits++;
            } else {
                if (cached) {
                    console.log('[Controller] loadRepository: ✗ Cache EXPIRED');
                } else {
                    console.log('[Controller] loadRepository: ✗ Cache MISS');
                }
                
                // Load from service
                console.log('[Controller] loadRepository: → Loading from RepositoryService...');
                data = await this.repositoryService.loadRepository(repoName);
                console.log('[Controller] loadRepository: ✓ Data loaded from service');
                
                if (data) {
                    console.log('[Controller] loadRepository: → Data structure:');
                    console.log('[Controller] loadRepository:   Keys:', Object.keys(data));
                    console.log('[Controller] loadRepository:   Repo:', data.repo?.display_name || data.metadata?.name || 'N/A');
                    console.log('[Controller] loadRepository:   Overview:', data.overview ? '✓' : '✗');
                    console.log('[Controller] loadRepository:   Metrics:', data.metrics ? '✓' : '✗');
                    console.log('[Controller] loadRepository:   Metadata:', data.metadata ? '✓' : '✗');
                }
                
                // Validate integrity BEFORE rendering (only if data loaded)
                if (data) {
                    console.log('[Controller] loadRepository: → Validating data integrity...');
                    const validation = this.validationService.validateDataIntegrity(data);
                    
                    if (!validation.valid) {
                        console.error('[Controller] loadRepository: ✗ Validation FAILED');
                        console.error('[Controller] loadRepository:   Issues:', validation.issues);
                    } else {
                        console.log('[Controller] loadRepository: ✓ Validation PASSED');
                    }
                    
                    if (validation.warnings.length > 0) {
                        console.warn('[Controller] loadRepository: ⚠ Validation warnings:', validation.warnings);
                    }
                } else {
                    console.warn('[Controller] loadRepository: ⚠ No data loaded - skipping validation');
                }
                
                // Cache validated data
                console.log('[Controller] loadRepository: → Caching data...');
                this.stateManager.setCacheEntry(repoName, data);
                console.log('[Controller] loadRepository: ✓ Data cached');
            }
            
            // NOTE: No generation check here - _renderCurrentTab() does its own generation tracking
            // This prevents false positives from intermediate setState calls
            console.log('[Controller] loadRepository: → Proceeding to render (generation tracking handled by _renderCurrentTab)');
            
            // Update state: loading complete
            console.log('[Controller] loadRepository: → Updating state (loading complete)...');
            this.stateManager.setState(draft => {
                draft.data = data;
                draft.isLoading = false;
                draft.errors = {};
            });
            console.log('[Controller] loadRepository: ✓ State updated with data');
            console.log('[Controller] loadRepository:   New generation:', this.stateManager.getGeneration());
            
            // Update URL
            console.log('[Controller] loadRepository: → Updating URL...');
            this._updateUrl(repoName);
            console.log('[Controller] loadRepository: ✓ URL updated');
            
            // Render dashboard (lazy per tab)
            console.log('[Controller] loadRepository: → Rendering current tab...');
            await this._renderCurrentTab();
            console.log('[Controller] loadRepository: ✓ Tab rendered');
            
            console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
            console.log(`[Controller] loadRepository: ✅ SUCCESS - "${repoName}" loaded`);
            console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
            
        } catch (error) {
            console.error('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
            console.error('[Controller] loadRepository: ✗ FAILED');
            console.error('[Controller] loadRepository: Error:', error);
            console.error('[Controller] loadRepository: Stack:', error.stack);
            console.error('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
            
            this.stateManager.setState(draft => {
                draft.isLoading = false;
                draft.errors.load = error.message;
            });
        } finally {
            this._showLoading(false);
        }
    }
    
    /**
     * Switch tab with lazy loading
     */
    async switchTab(tabId) {
        const state = this.stateManager.getState();
        
        if (state.currentTab === tabId) return;
        
        // Update state
        this.stateManager.setState(draft => {
            draft.currentTab = tabId;
        });
        
        // Render tab
        await this._renderCurrentTab();
        
        // Update URL hash
        window.location.hash = tabId;
    }
    
    /**
     * Render current tab only (lazy loading)
     */
    async _renderCurrentTab() {
        const state = this.stateManager.getState();
        
        if (!state.data) return;
        
        // Cancel old renders
        this._cancelOldRenders(state.currentTab);
        
        // Mark tab as loading
        this.stateManager.setState(draft => {
            draft.loadingTabs.add(state.currentTab);
        });
        
        // CRITICAL: Capture generation AFTER setState above
        // Otherwise we check against stale generation
        const generation = this.stateManager.getGeneration();
        console.log('[Controller] _renderCurrentTab: Generation captured for staleness check:', generation);
        
        try {
            // Render tab content with error boundary
            await this.errorBoundary.wrap(
                `tab_${state.currentTab}`,
                async () => {
                    // Check generation before render
                    const currentGen = this.stateManager.getGeneration();
                    console.log('[Controller] _renderCurrentTab: Pre-render generation check:', generation, 'vs', currentGen);
                    
                    if (!this.stateManager.isGenerationCurrent(generation)) {
                        console.warn('[Controller] _renderCurrentTab: Stale render detected - aborting');
                        throw new Error('Stale render cancelled');
                    }
                    
                    console.log('[Controller] _renderCurrentTab: Generation valid - proceeding with render');
                    
                    switch (state.currentTab) {
                        case 'overview':
                            await this._renderOverview(state.data);
                            break;
                        case 'architecture':
                            await this._renderArchitecture(state.data);
                            break;
                        case 'quality':
                            await this._renderQuality(state.data);
                            break;
                        case 'security':
                            await this._renderSecurity(state.data);
                            break;
                        case 'dependencies':
                            await this._renderDependencies(state.data);
                            break;
                        case 'usecases':
                            await this._renderUseCases(state.data);
                            break;
                    }
                },
                { tabId: state.currentTab, repoName: state.currentRepo }
            );
            
        } finally {
            // Mark tab as loaded
            this.stateManager.setState(draft => {
                draft.loadingTabs.delete(state.currentTab);
            });
        }
    }
    
    /**
     * Render overview tab
     */
    async _renderOverview(data) {
        // Update header
        this._updateHeader(data);
        
        // Update metrics
        this._updateMetrics(data);
        
        // Update overview content with sanitized HTML
        const overview = data.overview || {};
        
        if (this.dom.overviewSummary) {
            // Sanitize to prevent XSS
            const sanitized = this.validationService.sanitizeHTML(
                overview.business_summary || overview.summary || 'No summary available.'
            );
            this.dom.overviewSummary.innerHTML = sanitized;
        }
        
        // Render key findings
        const keyFindingsList = document.getElementById('key-findings');
        if (keyFindingsList && overview.key_findings) {
            keyFindingsList.innerHTML = overview.key_findings.map(finding => `
                <li style="display: flex; align-items: start; gap: 0.75rem; margin-bottom: 0.75rem;">
                    <i class="fas fa-check-circle" style="color: var(--accent-primary); margin-top: 0.25rem;"></i>
                    <span>${this.validationService.sanitizeHTML(finding)}</span>
                </li>
            `).join('');
        }
        
        // Show data integrity warnings
        this._showDataIntegrityWarnings(data);
        
        // Render visualizations
        if (window.CortexViz) {
            await this._renderOverviewVisualizations(data);
        }
    }
    
    /**
     * Show data integrity warnings
     */
    _showDataIntegrityWarnings(data) {
        const validation = this.validationService.validateDataIntegrity(data);
        
        if (validation.issues.length === 0 && validation.warnings.length === 0) {
            return;
        }
        
        // Find or create banner
        let banner = document.getElementById('data-integrity-banner');
        if (!banner) {
            banner = document.createElement('div');
            banner.id = 'data-integrity-banner';
            banner.className = 'integrity-banner';
            
            const container = document.querySelector('.dashboard-container');
            if (container) {
                container.insertBefore(banner, container.firstChild);
            }
        }
        
        // Build warning HTML
        const items = [...validation.issues, ...validation.warnings].map(issue => {
            const icon = issue.severity === 'error' ? 'exclamation-circle' : 'exclamation-triangle';
            const color = issue.severity === 'error' ? 'var(--status-danger)' : 'var(--status-warning)';
            
            return `
                <div class="integrity-item" style="border-left: 3px solid ${color};">
                    <i class="fas fa-${icon}" style="color: ${color};"></i>
                    <div>
                        <strong>${issue.type.toUpperCase()}</strong>
                        <p>${this.validationService.sanitizeHTML(issue.message)}</p>
                        <span class="confidence">Confidence: ${Math.round(issue.confidence * 100)}%</span>
                    </div>
                </div>
            `;
        }).join('');
        
        banner.innerHTML = `
            <div class="integrity-header">
                <i class="fas fa-shield-alt"></i>
                <h3>Data Integrity Issues Detected</h3>
                <button onclick="this.parentElement.parentElement.remove()" class="btn-close">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="integrity-items">${items}</div>
        `;
    }
    
    /**
     * Render use cases tab
     */
    async _renderUseCases(data) {
        const useCases = data.use_cases || [];
        const container = document.getElementById('usecase-grid');
        
        if (!container) return;
        
        if (useCases.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 3rem; color: var(--text-secondary);">
                    <i class="fas fa-lightbulb" style="font-size: 3rem; opacity: 0.3; margin-bottom: 1rem;"></i>
                    <p>No use cases available for this repository.</p>
                </div>
            `;
            return;
        }
        
        // Render use case cards
        const cards = useCases.map((uc, index) => {
            const icon = this._getUseCaseIcon(uc.persona || uc.category);
            const severityColor = this._getSeverityColor(uc.severity || 'info');
            
            return `
                <div class="use-case-card" data-persona="${(uc.persona || 'Engineer').toLowerCase()}" style="border-left: 4px solid ${severityColor};">
                    <div class="use-case-header">
                        <div class="use-case-icon" style="background: ${severityColor}22;">
                            <i class="${icon}" style="color: ${severityColor};"></i>
                        </div>
                        <div class="use-case-meta">
                            <h4 class="use-case-title">${this.validationService.sanitizeHTML(uc.title)}</h4>
                            <div class="use-case-badges">
                                <span class="badge badge-persona">${uc.persona || 'Engineer'}</span>
                                <span class="badge badge-category">${uc.category || 'General'}</span>
                            </div>
                        </div>
                    </div>
                    <div class="use-case-body">
                        <p class="use-case-summary">${this.validationService.sanitizeHTML(uc.summary || uc.description || '')}</p>
                        ${uc.recommended_actions && uc.recommended_actions.length > 0 ? `
                            <div class="use-case-actions">
                                <strong><i class="fas fa-tasks"></i> Actions:</strong>
                                <ul>
                                    ${uc.recommended_actions.slice(0, 3).map(action => `
                                        <li>${this.validationService.sanitizeHTML(action)}</li>
                                    `).join('')}
                                </ul>
                            </div>
                        ` : ''}
                        ${uc.tags && uc.tags.length > 0 ? `
                            <div class="use-case-tags">
                                ${uc.tags.map(tag => `<span class="tag">${this.validationService.sanitizeHTML(tag)}</span>`).join('')}
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
        }).join('');
        
        container.innerHTML = `
            <div style="margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center;">
                <h3 style="margin: 0;"><i class="fas fa-list"></i> ${useCases.length} Use Cases</h3>
            </div>
            <div class="use-cases-grid">
                ${cards}
            </div>
        `;
    }
    
    _getUseCaseIcon(persona) {
        const icons = {
            'engineer': 'fas fa-code',
            'manager': 'fas fa-user-tie',
            'po': 'fas fa-clipboard-list',
            'tech': 'fas fa-project-diagram',
            'security': 'fas fa-shield-alt',
            'qa': 'fas fa-vial',
            'developer': 'fas fa-laptop-code',
            'api': 'fas fa-plug',
            'user interface': 'fas fa-desktop',
            'media management': 'fas fa-photo-video',
            'delivery': 'fas fa-truck',
            'processing': 'fas fa-cogs'
        };
        return icons[(persona || '').toLowerCase()] || 'fas fa-lightbulb';
    }
    
    _getSeverityColor(severity) {
        const colors = {
            'critical': '#ef4444',
            'high': '#f59e0b',
            'medium': '#3b82f6',
            'low': '#10b981',
            'info': '#7b61ff'
        };
        return colors[severity] || colors.info;
    }
    
    /**
     * Render architecture tab
     */
    async _renderArchitecture(data) {
        // Delegate to visualization module
        if (window.CortexViz) {
            await window.CortexViz.renderArchitectureTab(data);
        }
    }
    
    /**
     * Render quality tab
     */
    async _renderQuality(data) {
        if (window.CortexViz) {
            await window.CortexViz.renderQualityTab(data);
        }
    }
    
    /**
     * Render security tab
     */
    async _renderSecurity(data) {
        const security = data.security || {};
        const vulns = security.vulnerabilities || [];
        
        if (this.dom.secVulnList) {
            if (vulns.length === 0) {
                this.dom.secVulnList.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-shield-alt"></i>
                        <h3 style="color: var(--status-success);">All Clear!</h3>
                        <p>No security vulnerabilities detected.</p>
                    </div>
                `;
            } else {
                // Render vulnerability list with sanitization
                const items = vulns.slice(0, 50).map(vuln => {
                    const severity = vuln.severity || 'unknown';
                    const color = this._getSeverityColor(severity);
                    
                    return `
                        <div class="vuln-item" style="border-left: 3px solid ${color};">
                            <div class="vuln-header">
                                <span class="vuln-severity" style="background: ${color};">${severity}</span>
                                <strong>${this.validationService.sanitizeHTML(vuln.title || vuln.package)}</strong>
                            </div>
                            <p>${this.validationService.sanitizeHTML(vuln.description || 'No description')}</p>
                        </div>
                    `;
                }).join('');
                
                this.dom.secVulnList.innerHTML = items;
            }
        }
        
        // Render security visualizations
        if (window.CortexViz) {
            await window.CortexViz.renderSecurityVisualizations(data);
        }
    }
    
    /**
     * Render dependencies tab
     */
    async _renderDependencies(data) {
        const deps = data.dependencies || {};
        const packages = deps.packages || [];
        
        if (this.dom.depTable) {
            // Virtualize if > 100 items
            const maxRows = packages.length > 100 ? 100 : packages.length;
            
            const rows = packages.slice(0, maxRows).map(pkg => {
                const name = this.validationService.sanitizeHTML(pkg.name);
                const version = this.validationService.sanitizeHTML(pkg.version || 'N/A');
                const license = this.validationService.sanitizeHTML(pkg.license || '—');
                
                return `
                    <tr>
                        <td style="font-family: var(--font-mono);">${name}</td>
                        <td style="font-family: var(--font-mono);">${version}</td>
                        <td>
                            <span class="badge ${pkg.is_direct ? 'badge-info' : 'badge-success'}">
                                ${pkg.is_direct ? 'Direct' : 'Transitive'}
                            </span>
                        </td>
                        <td>${license}</td>
                    </tr>
                `;
            }).join('');
            
            this.dom.depTable.innerHTML = `
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Package</th>
                            <th>Version</th>
                            <th>Type</th>
                            <th>License</th>
                        </tr>
                    </thead>
                    <tbody>${rows}</tbody>
                </table>
                <p class="text-muted mt-md">
                    Showing ${maxRows} of ${packages.length} packages
                    ${packages.length > 100 ? ' (virtualized for performance)' : ''}
                </p>
            `;
        }
        
        // Render dependency graph (with limit)
        if (window.CortexViz) {
            await window.CortexViz.renderDependencyGraph(data, { maxNodes: 50 });
        }
    }
    
    /**
     * Render use cases tab
     */
    async _renderUseCases(data) {
        if (window.CortexViz) {
            await window.CortexViz.renderUseCasesTab(data);
        }
    }
    
    /**
     * Render overview visualizations
     */
    async _renderOverviewVisualizations(data) {
        // Delegate to visualization module
        const viz = window.CortexViz;
        
        await Promise.allSettled([
            viz.createLanguagePieChart(data, 'viz-languages'),
            viz.createHealthGauge(data, 'viz-health')
        ]);
    }
    
    // ... (Continued in next part)
    
    /**
     * Initialize DOM references
     */
    _initDOMReferences() {
        this.dom = {
            loadingOverlay: document.getElementById('loading-overlay'),
            repoTitle: document.getElementById('repo-title'),
            repoSubtitle: document.getElementById('repo-subtitle'),
            statusTdd: document.getElementById('status-tdd'),
            statusGit: document.getElementById('status-git'),
            statusErrors: document.getElementById('status-errors'),
            healthScore: document.getElementById('health-score'),
            primaryLang: document.getElementById('primary-lang'),
            totalFiles: document.getElementById('total-files'),
            lastUpdated: document.getElementById('last-updated'),
            overviewSummary: document.getElementById('overview-summary'),
            depTable: document.getElementById('dep-table'),
            secVulnList: document.getElementById('sec-vuln-list'),
            tabNav: document.getElementById('tab-nav'),
            tabContents: document.querySelectorAll('.tab-content')
        };
        
        // Initialize tabs UI
        this._initTabs();
    }
    
    /**
     * Initialize tab navigation
     */
    _initTabs() {
        console.log('[Controller] _initTabs: Initializing tab navigation...');
        console.log('[Controller] _initTabs: tabNav element:', this.dom.tabNav ? '✓ Found' : '✗ Not found');
        
        if (!this.dom.tabNav) {
            console.warn('[Controller] _initTabs: ✗ Tab navigation element not found!');
            return;
        }
        
        console.log('[Controller] _initTabs: Creating', this.config.tabs.length, 'tab buttons');
        this.config.tabs.forEach((tab, index) => {
            console.log(`[Controller] _initTabs:   ${index + 1}. ${tab.label} (${tab.id})`);
        });
        
        // Create tab buttons
        this.dom.tabNav.innerHTML = this.config.tabs.map(tab => `
            <button class="tab-btn ${tab.id === 'overview' ? 'active' : ''}" 
                    data-tab="${tab.id}">
                <i class="${tab.icon}"></i>
                ${tab.label}
            </button>
        `).join('');
        
        console.log('[Controller] _initTabs: ✓ Tab HTML generated');
        console.log('[Controller] _initTabs: ✓ Tab navigation initialized');
    }
    
    /**
     * Setup event listeners
     */
    _setupEventListeners() {
        // Tab navigation
        if (this.dom.tabNav) {
            this.dom.tabNav.addEventListener('click', (e) => {
                const tab = e.target.closest('[data-tab]');
                if (tab) {
                    this.switchTab(tab.dataset.tab);
                }
            });
        }
        
        // Repository selector
        const repoSelector = document.getElementById('repo-selector-btn');
        if (repoSelector) {
            repoSelector.addEventListener('click', () => {
                this._showRepositoryModal();
            });
        }
        
        // Back button
        window.addEventListener('popstate', (e) => {
            if (e.state && e.state.repo) {
                this.loadRepository(e.state.repo);
            }
        });
    }
    
    /**
     * Show repository modal
     */
    _showRepositoryModal() {
        const modal = document.getElementById('modal-overlay');
        if (modal) {
            modal.classList.remove('hidden');
            
            // Populate repository grid
            const grid = document.getElementById('repo-grid');
            if (grid) {
                grid.innerHTML = this.config.repositories.map(repo => `
                    <button class="repo-card" onclick="window.dashboardController.loadRepository('${repo}')">
                        <i class="fas fa-folder-open"></i>
                        <span>${repo}</span>
                    </button>
                `).join('');
            }
        }
    }
    
    /**
     * Update header
     */
    _updateHeader(data) {
        // Handle both old and new data formats
        const repo = data.repo || {};
        const metadata = data.metadata || {};
        
        if (this.dom.repoTitle) {
            const name = repo.display_name || metadata.name || 'Dashboard';
            this.dom.repoTitle.textContent = this.validationService.sanitizeHTML(name);
        }
        
        if (this.dom.repoSubtitle) {
            const desc = repo.description || metadata.description || 'Repository analytics';
            this.dom.repoSubtitle.textContent = this.validationService.sanitizeHTML(desc);
        }
        
        this._updateStatusBadges(data);
    }
    
    /**
     * Update status badges
     */
    _updateStatusBadges(data) {
        const security = data.security || {};
        const hasVulns = (security.critical_count || 0) + (security.high_count || 0) > 0;
        
        if (this.dom.statusErrors) {
            if (hasVulns) {
                this.dom.statusErrors.className = 'status-badge warning';
                this.dom.statusErrors.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${security.total_count || 0} Issues`;
            } else {
                this.dom.statusErrors.className = 'status-badge success';
                this.dom.statusErrors.innerHTML = '<i class="fas fa-check-circle"></i> 0 Errors';
            }
        }
    }
    
    /**
     * Update metrics
     */
    _updateMetrics(data) {
        // Handle both old and new data formats
        const repo = data.repo || {};
        const metadata = data.metadata || {};
        const metrics = data.metrics || {};
        const overview = data.overview || {};
        const architecture = data.architecture || {};
        
        if (this.dom.healthScore) {
            // Support multiple data formats: metrics.health_score, metadata.health_score, or overview.health_score
            const score = metrics.health_score ?? metadata.health_score ?? overview.health_score ?? 0;
            this.dom.healthScore.textContent = score;
        }
        
        if (this.dom.primaryLang) {
            const languages = metrics.languages || architecture.languages || {};
            if (Object.keys(languages).length > 0) {
                const langs = Object.entries(languages).sort((a, b) => b[1] - a[1]);
                this.dom.primaryLang.textContent = langs[0]?.[0] || 'N/A';
            } else if (repo.primary_language) {
                this.dom.primaryLang.textContent = repo.primary_language;
            } else {
                this.dom.primaryLang.textContent = 'N/A';
            }
        }
        
        if (this.dom.totalFiles) {
            const files = metrics.files || overview.total_files || 0;
            this.dom.totalFiles.textContent = files;
        }
        
        if (this.dom.lastUpdated) {
            const dateStr = repo.last_analyzed_at || metadata.last_analyzed_at;
            const date = dateStr ? new Date(dateStr) : new Date();
            this.dom.lastUpdated.textContent = date.toISOString().split('T')[0];
        }
    }
    
    /**
     * Show/hide loading overlay
     */
    _showLoading(show) {
        if (this.dom.loadingOverlay) {
            this.dom.loadingOverlay.classList.toggle('hidden', !show);
        }
    }
    
    /**
     * Parse URL parameters
     */
    _parseUrlParams() {
        const params = new URLSearchParams(window.location.search);
        return {
            repo: params.get('repo')
        };
    }
    
    /**
     * Update URL
     */
    _updateUrl(repo) {
        const url = new URL(window.location);
        url.searchParams.set('repo', repo);
        window.history.pushState({ repo }, '', url);
    }
    
    /**
     * Cancel old render operations
     */
    _cancelOldRenders(exceptTabId = null) {
        for (const [tabId, token] of this.renderTokens.entries()) {
            if (tabId !== exceptTabId) {
                token.cancelled = true;
                this.renderTokens.delete(tabId);
            }
        }
    }
    
    /**
     * Get severity color
     */
    _getSeverityColor(severity) {
        const colors = {
            critical: 'var(--status-danger)',
            high: 'var(--status-warning)',
            medium: 'var(--status-warning)',
            low: 'var(--status-info)',
            unknown: 'var(--text-tertiary)'
        };
        return colors[severity.toLowerCase()] || colors.unknown;
    }
    
    /**
     * State change callback
     */
    _onStateChange(oldState, newState) {
        console.log('[Controller] _onStateChange: State change detected');
        console.log('[Controller] _onStateChange: Old generation:', oldState.generation);
        console.log('[Controller] _onStateChange: New generation:', newState.generation);
        console.log('[Controller] _onStateChange: Generation delta:', newState.generation - oldState.generation);
        
        // React to state changes if needed
        if (oldState.currentRepo !== newState.currentRepo) {
            console.log(`[Controller] _onStateChange: Repo changed: ${oldState.currentRepo} → ${newState.currentRepo}`);
        }
        
        if (oldState.currentTab !== newState.currentTab) {
            console.log(`[Controller] _onStateChange: Tab changed: ${oldState.currentTab} → ${newState.currentTab}`);
            // CRITICAL: _updateActiveTab should NOT call setState
            this._updateActiveTab(newState.currentTab);
        }
        
        console.log('[Controller] _onStateChange: Handler complete (no state mutations)');
    }
    
    /**
     * Update active tab visual state
     */
    _updateActiveTab(tabId) {
        // Update tab nav
        document.querySelectorAll('[data-tab]').forEach(el => {
            el.classList.toggle('active', el.dataset.tab === tabId);
        });
        
        // Show tab content
        document.querySelectorAll('.tab-content').forEach(el => {
            el.classList.toggle('active', el.id === `tab-${tabId}`);
        });
    }
    
    /**
     * Export diagnostics
     */
    exportDiagnostics() {
        return {
            controller: {
                config: this.config,
                renderTokens: this.renderTokens.size
            },
            state: this.stateManager.exportDiagnostics(),
            errors: this.errorBoundary.exportDiagnostics(),
            repository: this.repositoryService.exportDiagnostics()
        };
    }
}

// AC_COMPLETE: AC-SPA-001-05 ✅ DashboardController with SOLID architecture
