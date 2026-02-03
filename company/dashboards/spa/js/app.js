/**
 * CORTEX SPA - Main Application
 * Initializes dashboard with data binding and components
 * Version: 1.0.0
 */

class CortexDashboard {
    constructor() {
        this.data = null;
        this.dataBinder = null;
        this.tabManager = null;
        this.useCasesManager = null;
        this.chartHost = window.chartHost || new ChartHost();
        this.initialized = false;
    }
    
    /**
     * Initialize the dashboard
     */
    async init() {
        try {
            console.log('🚀 [TRACE] Starting CORTEX Dashboard initialization...');
            
            // Load data from embedded JSON
            this.loadData();
            
            if (!this.data) {
                console.error('CORTEX Dashboard: No data found');
                this.showError('No dashboard data available');
                return;
            }
            
            console.log('📊 [TRACE] Data loaded successfully:', {
                hasRepo: !!this.data?.repo,
                repoName: this.data?.repo?.display_name,
                hasOverview: !!this.data?.overview,
                hasMetrics: !!this.data?.metrics,
                hasSecurity: !!this.data?.security,
                vulnerabilitiesIsArray: Array.isArray(this.data?.security?.vulnerabilities),
                vulnerabilitiesCount: this.data?.security?.vulnerabilities?.length || 0,
                hasDependencies: !!this.data?.dependencies,
                hasQuality: !!this.data?.quality,
                codeSmellsIsArray: Array.isArray(this.data?.quality?.code_smells),
                codeSmellsCount: this.data?.quality?.code_smells?.length || 0,
                hasUseCases: !!this.data?.use_cases,
                useCasesIsArray: Array.isArray(this.data?.use_cases),
                useCasesCount: this.data?.use_cases?.length || 0
            });
            
            // Initialize data binder
            this.dataBinder = new DataBinder(this.data);
            
            // Bind data to DOM
            this.dataBinder.bind();
            
            // Initialize tab manager
            this.initTabs();
            
            // Initialize use cases manager
            this.initUseCases();
            
            // Initialize charts
            this.initCharts();
            
            // Setup back to top button
            this.initBackToTop();
            
            // Hide tabs without data
            this.hideEmptyTabs();
            
            // Setup score rings
            this.initScoreRings();
            
            this.initialized = true;
            console.log('✅ CORTEX Dashboard initialized successfully');
            
        } catch (error) {
            console.error('CORTEX Dashboard: Initialization failed', error);
            this.showError('Failed to initialize dashboard');
        }
    }
    
    /**
     * Load data from embedded JSON script tag
     */
    loadData() {
        const dataScript = document.getElementById('dashboard-data');
        if (dataScript) {
            try {
                this.data = JSON.parse(dataScript.textContent);
            } catch (e) {
                console.error('Failed to parse dashboard data:', e);
            }
        }
    }
    
    /**
     * Initialize tab navigation
     */
    initTabs() {
        const tabContainer = document.querySelector('.tabs-container');
        if (!tabContainer) return;
        
        this.tabManager = new TabManager(tabContainer.parentElement);
        
        // Refresh charts when tabs change
        this.tabManager.onTabChange = (index, tab, panel) => {
            setTimeout(() => this.chartHost.refreshAll(), 150);
        };
    }
    
    /**
     * Initialize use cases manager
     */
    initUseCases() {
        const useCases = this.data?.use_cases || [];
        if (useCases.length === 0) return;
        
        this.useCasesManager = new UseCasesManager({
            containerId: 'use-cases-grid',
            searchInputId: 'use-cases-search',
            personaFilterId: 'persona-filter',
            categoryFilterId: 'category-filter'
        });
        
        this.useCasesManager.init(useCases);
    }
    
    /**
     * Initialize all charts with lazy loading
     */
    initCharts() {
        // Overview charts
        this.registerChart('health-gauge', () => {
            return ChartFactory.createGaugeChart(
                document.getElementById('health-gauge'),
                this.data.metrics?.health_score || 0,
                { title: 'Health Score' }
            );
        });
        
        this.registerChart('coverage-gauge', () => {
            return ChartFactory.createGaugeChart(
                document.getElementById('coverage-gauge'),
                this.data.metrics?.coverage_pct || 0,
                { title: 'Test Coverage' }
            );
        });
        
        // Security charts
        this.registerChart('security-severity-chart', () => {
            const vulns = this.data.security?.vulnerabilities || [];
            const severityCounts = this.countBy(vulns, 'severity');
            return ChartFactory.createPieChart(
                document.getElementById('security-severity-chart'),
                Object.entries(severityCounts).map(([name, value]) => ({ name, value })),
                { donut: true }
            );
        });
        
        // Quality charts
        this.registerChart('code-quality-chart', () => {
            const quality = this.data.quality || {};
            return ChartFactory.createRadarChart(
                document.getElementById('code-quality-chart'),
                [
                    { name: 'Maintainability', max: 100 },
                    { name: 'Readability', max: 100 },
                    { name: 'Test Coverage', max: 100 },
                    { name: 'Documentation', max: 100 },
                    { name: 'Complexity', max: 100 }
                ],
                [{
                    name: 'Quality Scores',
                    value: [
                        quality.maintainability || 0,
                        quality.readability || 0,
                        this.data.metrics?.coverage_pct || 0,
                        quality.documentation || 0,
                        100 - (quality.complexity || 50)
                    ]
                }]
            );
        });
        
        // License distribution chart
        this.registerChart('license-chart', () => {
            const licenses = this.data.dependencies?.licenses || {};
            return ChartFactory.createPieChart(
                document.getElementById('license-chart'),
                Object.entries(licenses).map(([name, value]) => ({ name, value })),
                { donut: true }
            );
        });
        
        // Language distribution chart
        this.registerChart('language-chart', () => {
            const langs = this.data.metrics?.languages || {};
            return ChartFactory.createTreemapChart(
                document.getElementById('language-chart'),
                Object.entries(langs).map(([name, value]) => ({ name, value }))
            );
        });
        
        // Render dynamic lists after charts setup
        this.renderDynamicLists();
    }
    
    /**
     * Render dynamic list content
     */
    renderDynamicLists() {
        // Key findings
        this.renderKeyFindings();
        
        // Vulnerabilities
        this.renderVulnerabilities();
        
        // Vulnerability types
        this.renderVulnTypes();
        
        // License summary
        this.renderLicenseSummary();
        
        // Dependencies table
        this.renderDependenciesTable();
        
        // Code smells
        this.renderCodeSmells();
        
        // Patterns
        this.renderPatterns();
        
        // LENS recommendations
        this.renderLensRecommendations();
        
        // Refactoring
        this.renderRefactoring();
    }
    
    /**
     * Render key findings list
     */
    renderKeyFindings() {
        const container = document.getElementById('key-findings-list');
        const findings = this.data.overview?.key_findings || [];
        
        if (!container || findings.length === 0) return;
        
        container.innerHTML = findings.map(finding => `
            <div class="flex items-center gap-2" style="padding: 0.75rem 0; border-bottom: 1px solid var(--glass-border);">
                <span style="color: var(--success); font-size: 1rem;">✓</span>
                <span>${this.escapeHtml(finding)}</span>
            </div>
        `).join('');
    }
    
    /**
     * Render vulnerabilities list
     */
    renderVulnerabilities() {
        const container = document.getElementById('vulnerabilities-list');
        const vulns = this.data.security?.vulnerabilities || [];
        
        console.log('🔒 [TRACE] renderVulnerabilities:', {
            hasContainer: !!container,
            vulnsType: Array.isArray(vulns) ? 'array' : typeof vulns,
            vulnsLength: Array.isArray(vulns) ? vulns.length : 'not an array',
            firstVuln: vulns[0] || null
        });
        
        if (!container || vulns.length === 0) {
            console.warn('⚠️ Skipping vulnerabilities render:', !container ? 'no container' : 'no data');
            return;
        }
        
        container.innerHTML = vulns.map(vuln => `
            <div class="vulnerability-item">
                <div class="vulnerability-item__severity">
                    <span class="badge badge-${this.getSeverityClass(vuln.severity)}">${vuln.severity}</span>
                </div>
                <div class="vulnerability-item__info">
                    <div class="vulnerability-item__title">${this.escapeHtml(vuln.title)}</div>
                    <div class="vulnerability-item__cwe">${this.escapeHtml(vuln.cwe_id)}</div>
                </div>
                <div class="vulnerability-item__location">${this.escapeHtml(vuln.location)}</div>
                <div class="vulnerability-item__status">
                    <span class="badge badge-${this.getStatusClass(vuln.status)}">${vuln.status}</span>
                </div>
            </div>
        `).join('');
    }
    
    /**
     * Render vulnerability types summary
     */
    renderVulnTypes() {
        const container = document.getElementById('vuln-types-list');
        const vulns = this.data.security?.vulnerabilities || [];
        
        if (!container || vulns.length === 0) return;
        
        const cweTypes = this.countBy(vulns, 'cwe_id');
        const sorted = Object.entries(cweTypes).sort((a, b) => b[1] - a[1]).slice(0, 5);
        
        container.innerHTML = sorted.map(([cwe, count]) => `
            <div class="flex justify-between items-center" style="padding: 0.5rem 0; border-bottom: 1px solid var(--glass-border);">
                <span class="text-secondary">${cwe}</span>
                <span class="badge">${count}</span>
            </div>
        `).join('');
    }
    
    /**
     * Render license summary
     */
    renderLicenseSummary() {
        const container = document.getElementById('license-summary');
        const licenses = this.data.dependencies?.licenses || {};
        
        if (!container || Object.keys(licenses).length === 0) return;
        
        const total = Object.values(licenses).reduce((a, b) => a + b, 0);
        
        container.innerHTML = Object.entries(licenses)
            .sort((a, b) => b[1] - a[1])
            .map(([name, count]) => `
                <div class="flex justify-between items-center" style="padding: 0.5rem 0; border-bottom: 1px solid var(--glass-border);">
                    <span>${this.escapeHtml(name)}</span>
                    <span class="text-muted">${count} (${Math.round(count/total*100)}%)</span>
                </div>
            `).join('');
    }
    
    /**
     * Render dependencies table
     */
    renderDependenciesTable() {
        const container = document.getElementById('dependencies-table');
        const packages = this.data.dependencies?.packages || [];
        
        if (!container || packages.length === 0 || typeof gridjs === 'undefined') return;
        
        new gridjs.Grid({
            columns: ['Package', 'Version', 'Latest', 'License', 'Type'],
            data: packages.map(p => [p.name, p.version, p.latest, p.license, p.type]),
            search: true,
            pagination: { limit: 10 },
            sort: true,
            style: {
                table: { background: 'transparent' },
                th: { 
                    background: 'var(--glass-bg-dark)', 
                    color: 'var(--text-primary)',
                    borderColor: 'var(--glass-border)'
                },
                td: { 
                    background: 'transparent', 
                    color: 'var(--text-secondary)',
                    borderColor: 'var(--glass-border)'
                }
            }
        }).render(container);
    }
    
    /**
     * Render code smells
     */
    renderCodeSmells() {
        const container = document.getElementById('code-smells-grid');
        const smells = this.data.quality?.code_smells || [];
        
        console.log('⚠️ [TRACE] renderCodeSmells:', {
            hasContainer: !!container,
            smellsType: Array.isArray(smells) ? 'array' : typeof smells,
            smellsLength: Array.isArray(smells) ? smells.length : 'not an array',
            firstSmell: smells[0] || null
        });
        
        if (!container || smells.length === 0) {
            console.warn('⚠️ Skipping code smells render:', !container ? 'no container' : 'no data');
            return;
        }
        
        container.innerHTML = smells.map(smell => `
            <div class="code-smell-card glass-card-static">
                <div class="code-smell-card__header">
                    <span class="code-smell-card__icon">⚠️</span>
                    <span class="badge badge-${this.getSeverityClass(smell.severity)}">${smell.severity}</span>
                </div>
                <div class="code-smell-card__title">${this.escapeHtml(smell.name)}</div>
                <div class="code-smell-card__description">${this.escapeHtml(smell.description)}</div>
                <div class="code-smell-card__location">📍 ${this.escapeHtml(smell.location)}</div>
            </div>
        `).join('');
    }
    
    /**
     * Render detected patterns
     */
    renderPatterns() {
        const container = document.getElementById('patterns-list');
        const patterns = this.data.lens?.patterns_detected || [];
        
        if (!container || patterns.length === 0) return;
        
        container.innerHTML = patterns.map(pattern => `
            <div class="lens-pattern-item">
                <div class="lens-pattern-item__info">
                    <span class="lens-pattern-item__name">${this.escapeHtml(pattern.name)}</span>
                    <span class="badge">${pattern.count}×</span>
                </div>
                <div class="progress-bar" style="height: 6px;">
                    <div class="progress-bar__fill" style="width: ${pattern.confidence * 100}%"></div>
                </div>
                <span class="text-xs text-muted">${Math.round(pattern.confidence * 100)}% confidence</span>
            </div>
        `).join('');
    }
    
    /**
     * Render LENS recommendations
     */
    renderLensRecommendations() {
        const container = document.getElementById('lens-recommendations');
        const recommendations = this.data.lens?.recommendations || [];
        
        if (!container || recommendations.length === 0) return;
        
        container.innerHTML = recommendations.map(rec => `
            <div class="flex items-start gap-2" style="padding: 0.75rem 0; border-bottom: 1px solid var(--glass-border);">
                <span style="color: var(--accent-primary);">💡</span>
                <span>${this.escapeHtml(rec)}</span>
            </div>
        `).join('');
    }
    
    /**
     * Render refactoring recommendations
     */
    renderRefactoring() {
        const container = document.getElementById('refactoring-list');
        const recommendations = this.data.refactoring?.recommendations || [];
        
        if (!container || recommendations.length === 0) return;
        
        container.innerHTML = recommendations.map(rec => `
            <div class="refactoring-card glass-card-static">
                <div class="refactoring-card__header">
                    <h4 class="refactoring-card__title">${this.escapeHtml(rec.title)}</h4>
                    <span class="badge badge-${this.getPriorityClass(rec.priority)}">${rec.priority}</span>
                </div>
                <p class="refactoring-card__description">${this.escapeHtml(rec.description)}</p>
                <div class="refactoring-card__meta">
                    <span><strong>Impact:</strong> ${this.escapeHtml(rec.impact)}</span>
                    <span><strong>Effort:</strong> ${this.escapeHtml(rec.effort)}</span>
                </div>
                ${rec.files && rec.files.length ? `
                <div class="refactoring-card__files">
                    <strong>Files:</strong>
                    ${rec.files.map(f => `<code class="refactoring-card__file">${this.escapeHtml(f)}</code>`).join('')}
                </div>
                ` : ''}
            </div>
        `).join('');
    }
    
    /**
     * Register a chart for lazy initialization
     */
    registerChart(containerId, initFn) {
        if (document.getElementById(containerId)) {
            this.chartHost.register(containerId, initFn);
        }
    }
    
    /**
     * Initialize score ring SVGs
     */
    initScoreRings() {
        document.querySelectorAll('.score-ring').forEach(ring => {
            const value = parseFloat(ring.dataset.value) || 0;
            const progress = ring.querySelector('.score-ring__progress');
            const valueEl = ring.querySelector('.score-ring__value');
            
            if (progress) {
                const circumference = 2 * Math.PI * 45; // r=45
                const offset = circumference - (value / 100) * circumference;
                progress.style.strokeDasharray = circumference;
                progress.style.strokeDashoffset = offset;
            }
            
            if (valueEl) {
                valueEl.textContent = Math.round(value);
            }
        });
    }
    
    /**
     * Hide tabs that don't have corresponding data
     */
    hideEmptyTabs() {
        const tabDataMap = {
            'security-tab': 'security.vulnerabilities',
            'dependencies-tab': 'dependencies.packages',
            'quality-tab': 'quality',
            'use-cases-tab': 'use_cases',
            'lens-tab': 'lens',
            'refactoring-tab': 'refactoring.recommendations'
        };
        
        Object.entries(tabDataMap).forEach(([tabId, dataPath]) => {
            if (!this.dataBinder.hasValue(dataPath)) {
                const tab = document.getElementById(tabId);
                if (tab) {
                    tab.style.display = 'none';
                }
            }
        });
    }
    
    /**
     * Initialize back to top button
     */
    initBackToTop() {
        const btn = document.getElementById('back-to-top');
        if (!btn) return;
        
        window.addEventListener('scroll', () => {
            if (window.scrollY > 400) {
                btn.classList.add('visible');
            } else {
                btn.classList.remove('visible');
            }
        });
        
        btn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
    
    /**
     * Show error message
     */
    showError(message) {
        const container = document.querySelector('.app-container');
        if (container) {
            container.innerHTML = `
                <div class="glass-card text-center" style="padding: 4rem 2rem; margin-top: 2rem;">
                    <div style="font-size: 4rem; margin-bottom: 1.5rem;">⚠️</div>
                    <h2 style="margin-bottom: 1rem;">Error</h2>
                    <p class="text-secondary">${message}</p>
                </div>
            `;
        }
    }
    
    /**
     * Helper: Count items by property
     */
    countBy(arr, prop) {
        return arr.reduce((acc, item) => {
            const key = item[prop] || 'unknown';
            acc[key] = (acc[key] || 0) + 1;
            return acc;
        }, {});
    }
    
    /**
     * Helper: Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Helper: Get severity class
     */
    getSeverityClass(severity) {
        const map = {
            critical: 'danger',
            high: 'warning',
            medium: 'info',
            low: 'success'
        };
        return map[severity?.toLowerCase()] || 'default';
    }
    
    /**
     * Helper: Get status class
     */
    getStatusClass(status) {
        const map = {
            open: 'warning',
            in_progress: 'info',
            resolved: 'success',
            accepted: 'muted',
            fixed: 'success'
        };
        return map[status?.toLowerCase()] || 'default';
    }
    
    /**
     * Helper: Get priority class
     */
    getPriorityClass(priority) {
        const map = {
            high: 'danger',
            medium: 'warning',
            low: 'info'
        };
        return map[priority?.toLowerCase()] || 'default';
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.cortexDashboard = new CortexDashboard();
    window.cortexDashboard.init();
});
