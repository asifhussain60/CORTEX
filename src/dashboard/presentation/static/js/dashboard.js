/**
 * CORTEX Dashboard Master JavaScript
 * Handles tab navigation and common dashboard functionality
 */

class DashboardController {
    constructor() {
        this.currentTab = 'overview';
        this.tabs = ['overview', 'architecture', 'health', 'metrics', 'reports'];
        this.data = null;
        
        this.init();
    }
    
    init() {
        console.log('🧠 CORTEX Dashboard initialized');
        this.setupTabNavigation();
        this.setupHeaderActions();
        this.loadData();
        this.handleURLHash();
    }
    
    /**
     * Setup tab navigation with active state management
     */
    setupTabNavigation() {
        const tabLinks = document.querySelectorAll('.tab-link');
        
        tabLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const tabName = link.getAttribute('data-tab');
                this.switchTab(tabName);
            });
        });
    }
    
    /**
     * Switch to specified tab
     */
    switchTab(tabName) {
        if (!this.tabs.includes(tabName)) {
            console.error(`Invalid tab: ${tabName}`);
            return;
        }
        
        // Update active tab link
        document.querySelectorAll('.tab-link').forEach(link => {
            if (link.getAttribute('data-tab') === tabName) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
        
        // Update active tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            if (content.getAttribute('data-tab-content') === tabName) {
                content.classList.add('active');
            } else {
                content.classList.remove('active');
            }
        });
        
        // Update URL hash
        window.location.hash = tabName;
        this.currentTab = tabName;
        
        // Trigger tab-specific initialization
        this.onTabActivated(tabName);
    }
    
    /**
     * Handle URL hash for direct tab access
     */
    handleURLHash() {
        const hash = window.location.hash.substring(1);
        if (hash && this.tabs.includes(hash)) {
            this.switchTab(hash);
        }
        
        // Listen for hash changes
        window.addEventListener('hashchange', () => {
            const newHash = window.location.hash.substring(1);
            if (newHash && this.tabs.includes(newHash)) {
                this.switchTab(newHash);
            }
        });
    }
    
    /**
     * Setup header action buttons
     */
    setupHeaderActions() {
        const refreshBtn = document.getElementById('refresh-data');
        const settingsBtn = document.getElementById('settings-btn');
        
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshData();
            });
        }
        
        if (settingsBtn) {
            settingsBtn.addEventListener('click', () => {
                this.openSettings();
            });
        }
    }
    
    /**
     * Load dashboard data
     */
    async loadData() {
        try {
            // Load architecture data
            const architectureResponse = await fetch('../static/data/architecture.json');
            if (architectureResponse.ok) {
                const architectureData = await architectureResponse.json();
                this.data = { architecture: architectureData };
                console.log('✅ Data loaded successfully');
                this.populateOverview();
            } else {
                console.warn('⚠️ No data file found, using sample data');
                this.data = this.getSampleData();
                this.populateOverview();
            }
        } catch (error) {
            console.error('❌ Error loading data:', error);
            this.data = this.getSampleData();
            this.populateOverview();
        }
    }
    
    /**
     * Refresh dashboard data
     */
    async refreshData() {
        console.log('🔄 Refreshing data...');
        const refreshBtn = document.getElementById('refresh-data');
        if (refreshBtn) {
            refreshBtn.disabled = true;
            refreshBtn.innerHTML = '<span class="icon">⏳</span><span class="text">Loading...</span>';
        }
        
        await this.loadData();
        
        // Refresh current tab
        this.onTabActivated(this.currentTab);
        
        if (refreshBtn) {
            refreshBtn.disabled = false;
            refreshBtn.innerHTML = '<span class="icon">🔄</span><span class="text">Refresh</span>';
        }
        
        console.log('✅ Data refreshed');
    }
    
    /**
     * Open settings dialog
     */
    openSettings() {
        alert('Settings functionality coming soon!');
    }
    
    /**
     * Populate overview tab with data
     */
    populateOverview() {
        if (!this.data || !this.data.architecture) return;
        
        const arch = this.data.architecture;
        
        // Update stats
        document.getElementById('total-files').textContent = arch.nodes?.length || 0;
        document.getElementById('total-components').textContent = arch.nodes?.length || 0;
        document.getElementById('overall-health').textContent = this.calculateOverallHealth(arch);
        document.getElementById('total-issues').textContent = this.countIssues(arch);
        
        // Populate top issues
        this.populateTopIssues();
    }
    
    /**
     * Calculate overall health score
     */
    calculateOverallHealth(arch) {
        if (!arch.nodes || arch.nodes.length === 0) return '0%';
        
        const healthyNodes = arch.nodes.filter(node => 
            node.health === 'healthy' || node.health === 'excellent'
        ).length;
        
        const percentage = Math.round((healthyNodes / arch.nodes.length) * 100);
        return `${percentage}%`;
    }
    
    /**
     * Count total issues
     */
    countIssues(arch) {
        if (!arch.nodes) return 0;
        
        return arch.nodes.filter(node => 
            node.health === 'critical' || node.health === 'poor'
        ).length;
    }
    
    /**
     * Populate top issues list
     */
    populateTopIssues() {
        const issuesList = document.getElementById('top-issues-list');
        if (!issuesList) return;
        
        // Sample issues (would be populated from real data)
        const issues = [
            { severity: 'high', message: 'High cyclomatic complexity in module X', file: 'src/module_x.py' },
            { severity: 'medium', message: 'Low test coverage in component Y', file: 'src/component_y.py' },
            { severity: 'low', message: 'Missing documentation in class Z', file: 'src/class_z.py' }
        ];
        
        issuesList.innerHTML = issues.map(issue => `
            <div class="issue-item">
                <span class="issue-severity ${issue.severity}">${issue.severity.toUpperCase()}</span>
                <div class="issue-details">
                    <p class="issue-message">${issue.message}</p>
                    <p class="issue-file">${issue.file}</p>
                </div>
            </div>
        `).join('');
    }
    
    /**
     * Called when a tab is activated
     */
    onTabActivated(tabName) {
        console.log(`📋 Tab activated: ${tabName}`);
        
        switch (tabName) {
            case 'architecture':
                this.initializeArchitectureTab();
                break;
            case 'health':
                this.initializeHealthTab();
                break;
            case 'metrics':
                this.initializeMetricsTab();
                break;
            case 'reports':
                this.initializeReportsTab();
                break;
        }
    }
    
    /**
     * Initialize Architecture tab
     */
    initializeArchitectureTab() {
        // Architecture tab initialization is handled by architecture_tab.js
        if (window.ArchitectureGraph && this.data && this.data.architecture) {
            console.log('🏛️ Architecture tab ready with data');
        }
    }
    
    /**
     * Initialize Health tab
     */
    initializeHealthTab() {
        console.log('❤️ Initializing Health tab...');
        // Health tab initialization would go here
    }
    
    /**
     * Initialize Metrics tab
     */
    initializeMetricsTab() {
        console.log('📈 Initializing Metrics tab...');
        // Metrics tab initialization would go here
    }
    
    /**
     * Initialize Reports tab
     */
    initializeReportsTab() {
        console.log('📄 Initializing Reports tab...');
        // Reports tab initialization would go here
    }
    
    /**
     * Get sample data for testing
     */
    getSampleData() {
        return {
            architecture: {
                nodes: [
                    { id: 'node1', name: 'Component A', type: 'python', health: 'healthy' },
                    { id: 'node2', name: 'Component B', type: 'python', health: 'healthy' },
                    { id: 'node3', name: 'Component C', type: 'javascript', health: 'poor' }
                ],
                edges: [
                    { source: 'node1', target: 'node2', weight: 5 },
                    { source: 'node2', target: 'node3', weight: 3 }
                ]
            }
        };
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardController = new DashboardController();
});
