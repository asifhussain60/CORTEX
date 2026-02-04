/**
 * CORTEX Lens Dashboard - Main Application
 */

class DashboardApp {
    constructor() {
        this.currentTab = 'executive';
        this.searchIndex = null;
        this.theme = this.loadTheme();
    }

    /**
     * Initialize the dashboard
     */
    async initialize() {
        console.log('🧠 CORTEX Lens Dashboard initializing...');

        try {
            // Load data
            await dataAdapter.load();
            console.log('✅ Data loaded');

            // Setup UI
            this.setupTabs();
            this.setupThemeToggle();
            this.setupSearch();
            this.setupChartObservers();
            
            // Populate dashboard
            this.populateDashboard();

            // Activate first tab
            this.switchTab('executive');

            console.log('✅ Dashboard initialized');
        } catch (error) {
            console.error('❌ Dashboard initialization failed:', error);
            this.showError('Failed to initialize dashboard. Please refresh the page.');
        }
    }

    /**
     * Setup tab navigation
     */
    setupTabs() {
        const tabButtons = document.querySelectorAll('.tab-button');
        
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const tabId = button.dataset.tab;
                this.switchTab(tabId);
            });
        });

        // Keyboard navigation (arrow keys)
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
                const buttons = Array.from(tabButtons);
                const currentIndex = buttons.findIndex(b => b.classList.contains('active'));
                
                if (currentIndex !== -1) {
                    const nextIndex = e.key === 'ArrowRight' 
                        ? (currentIndex + 1) % buttons.length
                        : (currentIndex - 1 + buttons.length) % buttons.length;
                    
                    const nextTabId = buttons[nextIndex].dataset.tab;
                    this.switchTab(nextTabId);
                    buttons[nextIndex].focus();
                }
            }
        });
    }

    /**
     * Switch between tabs
     */
    switchTab(tabId) {
        // Update buttons
        document.querySelectorAll('.tab-button').forEach(button => {
            const isActive = button.dataset.tab === tabId;
            button.classList.toggle('active', isActive);
            button.setAttribute('aria-selected', isActive);
        });

        // Update panels
        document.querySelectorAll('.tab-panel').forEach(panel => {
            const isActive = panel.id === `${tabId}-tab`;
            panel.classList.toggle('active', isActive);
            panel.setAttribute('aria-hidden', !isActive);
        });

        this.currentTab = tabId;
        
        // Lazy load charts for this tab
        this.loadTabCharts(tabId);
    }

    /**
     * Load charts for the active tab
     */
    loadTabCharts(tabId) {
        const tabPanel = document.getElementById(`${tabId}-tab`);
        if (!tabPanel) return;

        const chartContainers = tabPanel.querySelectorAll('[data-chart-type]');
        chartContainers.forEach(container => {
            if (!container.dataset.loaded) {
                charts.observe(container.id);
                container.dataset.loaded = 'true';
            }
        });
    }

    /**
     * Setup chart observers for lazy loading
     */
    setupChartObservers() {
        // Observe all chart containers
        const chartContainers = document.querySelectorAll('[data-chart-type]');
        chartContainers.forEach(container => {
            charts.observe(container.id);
        });
    }

    /**
     * Setup theme toggle
     */
    setupThemeToggle() {
        const themeToggle = document.getElementById('theme-toggle');
        if (!themeToggle) return;

        // Apply saved theme
        document.documentElement.setAttribute('data-theme', this.theme);
        
        themeToggle.addEventListener('click', () => {
            this.theme = this.theme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', this.theme);
            this.saveTheme(this.theme);
            
            // Update button text
            themeToggle.textContent = this.theme === 'dark' ? '☀️ Light' : '🌙 Dark';
        });

        // Set initial button text
        themeToggle.textContent = this.theme === 'dark' ? '☀️ Light' : '🌙 Dark';
    }

    /**
     * Setup search functionality
     */
    setupSearch() {
        const searchInput = document.getElementById('use-case-search');
        if (!searchInput) return;

        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            this.filterUseCases(query);
        });
    }

    /**
     * Filter use cases based on search query
     */
    filterUseCases(query) {
        const useCaseCards = document.querySelectorAll('.use-case-card');
        
        if (!query) {
            useCaseCards.forEach(card => card.style.display = '');
            return;
        }

        useCaseCards.forEach(card => {
            const title = card.querySelector('.use-case-card__title')?.textContent.toLowerCase() || '';
            const description = card.querySelector('.use-case-card__description')?.textContent.toLowerCase() || '';
            const matches = title.includes(query) || description.includes(query);
            card.style.display = matches ? '' : 'none';
        });
    }

    /**
     * Populate dashboard with data
     */
    populateDashboard() {
        this.populateHeader();
        this.populateExecutiveTab();
        this.populateOverviewTab();
        this.populateUseCasesTab();
        this.populateQualityTab();
        this.populateSecurityTab();
    }

    /**
     * Populate header
     */
    populateHeader() {
        const repoName = dataAdapter.get('repo.display_name', 'CORTEX');
        const healthScore = dataAdapter.get('metrics.health_score', 85);
        const healthStatus = this.getHealthStatus(healthScore);

        document.getElementById('repo-name').textContent = repoName;
        
        const healthBadge = document.getElementById('health-badge');
        if (healthBadge) {
            healthBadge.innerHTML = Components.renderHealthBadge(healthStatus);
        }
    }

    /**
     * Populate Executive tab
     */
    populateExecutiveTab() {
        const executive = dataAdapter.get('executive', {});
        
        // Health status
        const healthStatusEl = document.getElementById('exec-health-status');
        if (healthStatusEl && executive.health_status) {
            healthStatusEl.textContent = executive.health_status;
        }

        // Security posture
        const securityPostureEl = document.getElementById('exec-security-posture');
        if (securityPostureEl && executive.security_posture) {
            securityPostureEl.textContent = executive.security_posture;
        }

        // Tech debt
        const techDebtEl = document.getElementById('exec-tech-debt');
        if (techDebtEl && executive.tech_debt_hours) {
            techDebtEl.textContent = `${executive.tech_debt_hours}h`;
        }

        // Test pass rate
        const testPassRateEl = document.getElementById('exec-test-pass-rate');
        if (testPassRateEl && executive.test_pass_rate) {
            testPassRateEl.textContent = `${executive.test_pass_rate}%`;
        }

        // Risk summary
        const riskSummaryEl = document.getElementById('risk-summary');
        if (riskSummaryEl && executive.risk_summary) {
            riskSummaryEl.textContent = executive.risk_summary;
        }

        // Recommendations
        const recommendationsList = document.getElementById('recommendations-list');
        if (recommendationsList && executive.recommendations) {
            recommendationsList.innerHTML = executive.recommendations
                .map(rec => `<li>${Components.escapeHtml(rec)}</li>`)
                .join('');
        }
    }

    /**
     * Populate Overview tab
     */
    populateOverviewTab() {
        const overview = dataAdapter.get('overview', {});
        const metrics = dataAdapter.get('metrics', {});

        // Business summary
        const businessSummaryEl = document.getElementById('business-summary');
        if (businessSummaryEl && overview.business_summary) {
            businessSummaryEl.textContent = overview.business_summary;
        }

        // Metrics
        const metricsGrid = document.querySelector('#overview-tab .metrics-grid');
        if (metricsGrid && metrics) {
            const metricCards = [
                { icon: '📁', label: 'Total Files', value: Components.formatNumber(metrics.total_files) },
                { icon: '📝', label: 'Lines of Code', value: Components.formatNumber(metrics.lines_of_code) },
                { icon: '🎯', label: 'Test Coverage', value: `${metrics.test_coverage}%` },
                { icon: '💚', label: 'Health Score', value: metrics.health_score }
            ];

            metricsGrid.innerHTML = metricCards.map(m => Components.renderMetricCard(m)).join('');
        }
    }

    /**
     * Populate Use Cases tab
     */
    populateUseCasesTab() {
        const useCases = dataAdapter.get('use_cases', []);
        const useCasesGrid = document.getElementById('use-cases-grid');
        
        if (useCasesGrid && useCases.length > 0) {
            useCasesGrid.innerHTML = useCases
                .map(uc => Components.renderUseCaseCard(uc))
                .join('');
        }

        // Update count
        const countBadge = document.querySelector('[data-tab="use-cases"] .tab-button__count');
        if (countBadge) {
            countBadge.textContent = useCases.length;
        }
    }

    /**
     * Populate Quality tab
     */
    populateQualityTab() {
        const quality = dataAdapter.get('quality', {});

        const fields = [
            { id: 'complexity-score', value: quality.complexity_score },
            { id: 'duplication-pct', value: `${quality.duplication}%` },
            { id: 'tech-debt', value: `${quality.tech_debt_hours}h` },
            { id: 'code-smells', value: quality.code_smells }
        ];

        fields.forEach(({ id, value }) => {
            const el = document.getElementById(id);
            if (el && value !== undefined) {
                el.textContent = value;
            }
        });
    }

    /**
     * Populate Security tab
     */
    populateSecurityTab() {
        const security = dataAdapter.get('security', {});

        const totalEl = document.getElementById('security-total');
        if (totalEl && security.total_count !== undefined) {
            totalEl.textContent = security.total_count;
        }

        const vulnerabilitiesList = document.getElementById('vulnerabilities-list');
        if (vulnerabilitiesList && security.vulnerabilities) {
            vulnerabilitiesList.innerHTML = security.vulnerabilities
                .map(v => `
                    <div class="vulnerability-item">
                        ${Components.renderSeverityBadge(v.severity)}
                        <span>${v.count} ${v.severity} severity issues</span>
                    </div>
                `)
                .join('');
        }
    }

    /**
     * Get health status from score
     */
    getHealthStatus(score) {
        if (score >= 90) return 'Excellent';
        if (score >= 75) return 'Good';
        if (score >= 60) return 'Fair';
        if (score >= 40) return 'Poor';
        return 'Critical';
    }

    /**
     * Load theme from localStorage
     */
    loadTheme() {
        return localStorage.getItem('cortex-theme') || 'dark';
    }

    /**
     * Save theme to localStorage
     */
    saveTheme(theme) {
        localStorage.setItem('cortex-theme', theme);
    }

    /**
     * Show error message
     */
    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `
            <div style="background: rgba(248, 81, 73, 0.1); border: 1px solid rgba(248, 81, 73, 0.5); border-radius: 8px; padding: 16px; margin: 16px; color: #f85149;">
                <strong>❌ Error:</strong> ${Components.escapeHtml(message)}
            </div>
        `;
        document.body.insertBefore(errorDiv, document.body.firstChild);
    }
}

// Initialize dashboard when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        const app = new DashboardApp();
        app.initialize();
    });
} else {
    const app = new DashboardApp();
    app.initialize();
}
