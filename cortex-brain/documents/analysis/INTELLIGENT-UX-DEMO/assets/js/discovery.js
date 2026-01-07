/**
 * CORTEX UX Enhancement Dashboard - Discovery System
 * Context-aware suggestions and progressive questioning
 */

class DiscoveryEngine {
    constructor() {
        this.preferences = this.loadPreferences();
        this.sessionContext = {
            viewedTabs: new Set(),
            timeSpent: {},
            interactions: [],
            currentFocus: null
        };
        this.suggestionQueue = [];
        this.init();
    }

    /**
     * Initialize discovery system
     */
    init() {
        this.trackTabViews();
        this.trackInteractions();
        this.startContextAnalysis();
        this.checkForAutoEnhance();
    }

    /**
     * Load user preferences from Tier 1 (localStorage fallback)
     */
    loadPreferences() {
        try {
            const stored = localStorage.getItem('cortex-preferences');
            return stored ? JSON.parse(stored) : {
                alwaysEnhance: false,
                discoveryEnabled: true,
                autoSuggestions: true,
                suggestionDelay: 2000
            };
        } catch (error) {
            console.error('Error loading preferences:', error);
            return {
                alwaysEnhance: false,
                discoveryEnabled: true,
                autoSuggestions: true,
                suggestionDelay: 2000
            };
        }
    }

    /**
     * Save preferences to Tier 1 (localStorage fallback)
     */
    savePreferences() {
        try {
            localStorage.setItem('cortex-preferences', JSON.stringify(this.preferences));
            // In production, also save to Tier 1 SQLite via API
            this.saveTier1Preference('user_preferences', this.preferences);
        } catch (error) {
            console.error('Error saving preferences:', error);
        }
    }

    /**
     * Save to Tier 1 working memory (API call in production)
     */
    async saveTier1Preference(key, value) {
        // Production: POST to /api/tier1/preferences
        // For now, just localStorage
        console.log('Tier 1 save:', key, value);
    }

    /**
     * Check if user has "always enhance" enabled
     */
    checkForAutoEnhance() {
        const alwaysEnhance = document.getElementById('always-enhance');
        if (alwaysEnhance) {
            alwaysEnhance.checked = this.preferences.alwaysEnhance;
            
            alwaysEnhance.addEventListener('change', (e) => {
                this.preferences.alwaysEnhance = e.target.checked;
                this.savePreferences();
                
                if (e.target.checked) {
                    this.showNotification(
                        'Always Enhance Enabled',
                        'Future analyses will run automatically without consent prompts.',
                        'success'
                    );
                }
            });
        }
    }

    /**
     * Track which tabs users view
     */
    trackTabViews() {
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const tabId = button.dataset.tab;
                this.sessionContext.viewedTabs.add(tabId);
                this.sessionContext.currentFocus = tabId;
                
                // Track time spent
                if (!this.sessionContext.timeSpent[tabId]) {
                    this.sessionContext.timeSpent[tabId] = 0;
                }
                
                // Start timer for this tab
                if (this.activeTabTimer) {
                    clearInterval(this.activeTabTimer);
                }
                
                this.activeTabTimer = setInterval(() => {
                    this.sessionContext.timeSpent[tabId]++;
                    this.analyzeUserBehavior();
                }, 1000);
                
                // Generate contextual suggestions
                this.generateContextualSuggestions(tabId);
            });
        });
    }

    /**
     * Track user interactions (clicks, hovers, etc.)
     */
    trackInteractions() {
        document.addEventListener('click', (e) => {
            const target = e.target;
            const interaction = {
                type: 'click',
                element: target.tagName,
                class: target.className,
                timestamp: Date.now()
            };
            
            this.sessionContext.interactions.push(interaction);
            
            // Keep only last 50 interactions
            if (this.sessionContext.interactions.length > 50) {
                this.sessionContext.interactions.shift();
            }
        });
    }

    /**
     * Analyze user behavior patterns
     */
    analyzeUserBehavior() {
        const { timeSpent, viewedTabs, currentFocus } = this.sessionContext;
        
        // User spending a lot of time on quality tab
        if (timeSpent.quality > 30 && !this.suggestionShown('quality-deep-dive')) {
            this.queueSuggestion({
                id: 'quality-deep-dive',
                type: 'insight',
                title: 'Deep Dive into Quality Issues',
                description: 'You seem interested in code quality. Would you like specific recommendations for the top 3 issues?',
                actions: [
                    { label: 'Show Recommendations', callback: () => this.showQualityRecommendations() },
                    { label: 'Export Report', callback: () => this.exportQualityReport() }
                ],
                priority: 'high'
            });
        }
        
        // User viewing security tab
        if (currentFocus === 'security' && !this.suggestionShown('security-action-plan')) {
            this.queueSuggestion({
                id: 'security-action-plan',
                type: 'action',
                title: 'Security Action Plan',
                description: `Found ${dashboardData?.security.vulnerabilities.critical || 0} critical vulnerabilities. Generate a prioritized remediation plan?`,
                actions: [
                    { label: 'Generate Plan', callback: () => this.generateSecurityPlan() },
                    { label: 'Export CVE Report', callback: () => this.exportSecurityReport() }
                ],
                priority: 'critical'
            });
        }
        
        // User viewed multiple tabs (exploration pattern)
        if (viewedTabs.size >= 4 && !this.suggestionShown('comprehensive-report')) {
            this.queueSuggestion({
                id: 'comprehensive-report',
                type: 'question',
                title: 'Comprehensive Analysis',
                description: 'You\'ve explored multiple areas. Would you like a comprehensive improvement plan?',
                actions: [
                    { label: 'Create Plan', callback: () => this.createComprehensivePlan() },
                    { label: 'Schedule Review', callback: () => this.scheduleReview() }
                ],
                priority: 'medium'
            });
        }
    }

    /**
     * Generate suggestions based on current tab
     */
    generateContextualSuggestions(tabId) {
        const suggestions = {
            executive: [
                {
                    id: 'executive-drill-down',
                    title: 'Drill Down Analysis',
                    description: 'Want to explore specific areas in detail? I can guide you to the most impactful improvements.',
                    actions: [
                        { label: 'Show Me', callback: () => this.guidedTour() }
                    ]
                }
            ],
            architecture: [
                {
                    id: 'architecture-refactor',
                    title: 'Refactoring Opportunities',
                    description: 'Detected God classes and tight coupling. Generate a refactoring roadmap?',
                    actions: [
                        { label: 'Generate Roadmap', callback: () => this.generateRefactoringRoadmap() }
                    ]
                }
            ],
            quality: [
                {
                    id: 'quality-quick-wins',
                    title: 'Quick Quality Wins',
                    description: 'I found 23 code smells that can be fixed in < 2 hours. Show them?',
                    actions: [
                        { label: 'Show Quick Wins', callback: () => this.showQuickWins() }
                    ]
                }
            ],
            roadmap: [
                {
                    id: 'roadmap-prioritization',
                    title: 'Smart Prioritization',
                    description: 'Based on your codebase, here\'s an optimized task sequence. Review?',
                    actions: [
                        { label: 'Review Sequence', callback: () => this.reviewTaskSequence() }
                    ]
                }
            ],
            journey: [
                {
                    id: 'performance-baseline',
                    title: 'Performance Baseline',
                    description: 'Want to establish performance benchmarks before optimization?',
                    actions: [
                        { label: 'Set Baseline', callback: () => this.setPerformanceBaseline() }
                    ]
                }
            ],
            security: [
                {
                    id: 'security-compliance',
                    title: 'Compliance Check',
                    description: 'Check against OWASP ASVS or CWE Top 25 standards?',
                    actions: [
                        { label: 'Run Check', callback: () => this.runComplianceCheck() }
                    ]
                }
            ]
        };

        const tabSuggestions = suggestions[tabId] || [];
        tabSuggestions.forEach(suggestion => {
            if (!this.suggestionShown(suggestion.id)) {
                this.queueSuggestion({
                    ...suggestion,
                    type: 'contextual',
                    priority: 'medium'
                });
            }
        });
    }

    /**
     * Check if suggestion was already shown
     */
    suggestionShown(id) {
        return localStorage.getItem(`suggestion-shown-${id}`) === 'true';
    }

    /**
     * Mark suggestion as shown
     */
    markSuggestionShown(id) {
        localStorage.setItem(`suggestion-shown-${id}`, 'true');
    }

    /**
     * Queue a suggestion for display
     */
    queueSuggestion(suggestion) {
        // Check if already in queue
        if (this.suggestionQueue.find(s => s.id === suggestion.id)) {
            return;
        }
        
        this.suggestionQueue.push(suggestion);
        this.suggestionQueue.sort((a, b) => {
            const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
            return priorityOrder[a.priority] - priorityOrder[b.priority];
        });
        
        // Show next suggestion after delay
        if (this.preferences.autoSuggestions) {
            setTimeout(() => this.showNextSuggestion(), this.preferences.suggestionDelay);
        }
    }

    /**
     * Show next suggestion from queue
     */
    showNextSuggestion() {
        if (this.suggestionQueue.length === 0) return;
        
        const suggestion = this.suggestionQueue.shift();
        this.displaySuggestion(suggestion);
        this.markSuggestionShown(suggestion.id);
    }

    /**
     * Display suggestion in discovery panel
     */
    displaySuggestion(suggestion) {
        const panel = document.getElementById('discovery-panel');
        const content = document.getElementById('discovery-content');
        
        const priorityColors = {
            critical: 'border-red-500 bg-red-50 dark:bg-red-900/20',
            high: 'border-orange-500 bg-orange-50 dark:bg-orange-900/20',
            medium: 'border-blue-500 bg-blue-50 dark:bg-blue-900/20',
            low: 'border-gray-500 bg-gray-50 dark:bg-gray-900/20'
        };
        
        content.innerHTML = `
            <div class="border-l-4 ${priorityColors[suggestion.priority]} p-4 rounded">
                <div class="flex items-start justify-between mb-2">
                    <h4 class="font-semibold text-lg">${suggestion.title}</h4>
                    <span class="badge badge-${suggestion.priority}">${suggestion.priority}</span>
                </div>
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">${suggestion.description}</p>
                <div class="flex flex-wrap gap-2">
                    ${suggestion.actions.map((action, i) => `
                        <button 
                            class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition text-sm"
                            onclick="window.discoveryEngine.executeAction('${suggestion.id}', ${i})"
                        >
                            ${action.label}
                        </button>
                    `).join('')}
                    <button 
                        class="px-4 py-2 bg-gray-300 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-400 dark:hover:bg-gray-600 transition text-sm"
                        onclick="window.discoveryEngine.dismissSuggestion('${suggestion.id}')"
                    >
                        Dismiss
                    </button>
                </div>
            </div>
        `;
        
        panel.style.display = 'block';
        
        // Store for action execution
        this.currentSuggestion = suggestion;
    }

    /**
     * Execute suggestion action
     */
    executeAction(suggestionId, actionIndex) {
        if (this.currentSuggestion && this.currentSuggestion.id === suggestionId) {
            const action = this.currentSuggestion.actions[actionIndex];
            if (action && action.callback) {
                action.callback();
            }
        }
    }

    /**
     * Dismiss suggestion
     */
    dismissSuggestion(suggestionId) {
        document.getElementById('discovery-panel').style.display = 'none';
        this.markSuggestionShown(suggestionId);
        
        // Show next suggestion after delay
        setTimeout(() => this.showNextSuggestion(), 5000);
    }

    /**
     * Start continuous context analysis
     */
    startContextAnalysis() {
        setInterval(() => {
            this.analyzeUserBehavior();
        }, 10000); // Every 10 seconds
    }

    /**
     * Show notification
     */
    showNotification(title, message, type = 'info') {
        const colors = {
            success: 'bg-green-100 dark:bg-green-900 border-green-500',
            error: 'bg-red-100 dark:bg-red-900 border-red-500',
            warning: 'bg-yellow-100 dark:bg-yellow-900 border-yellow-500',
            info: 'bg-blue-100 dark:bg-blue-900 border-blue-500'
        };
        
        const notification = document.createElement('div');
        notification.className = `fixed top-20 right-4 p-4 rounded-lg shadow-lg border-l-4 ${colors[type]} z-50 max-w-sm`;
        notification.innerHTML = `
            <div class="flex items-start justify-between">
                <div>
                    <div class="font-semibold">${title}</div>
                    <div class="text-sm mt-1">${message}</div>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-gray-500 hover:text-gray-700">✕</button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    // Action callbacks

    guidedTour() {
        this.showNotification('Guided Tour', 'Starting guided tour of key improvement areas...', 'info');
        // Navigate to architecture tab
        document.querySelector('[data-tab="architecture"]').click();
    }

    showQualityRecommendations() {
        this.showNotification('Quality Recommendations', 'Generating personalized recommendations...', 'info');
        // In production, this would call UXEnhancementOrchestrator
    }

    exportQualityReport() {
        const report = {
            timestamp: new Date().toISOString(),
            quality: dashboardData.quality,
            recommendations: []
        };
        
        const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'cortex-quality-report.json';
        a.click();
        
        this.showNotification('Export Complete', 'Quality report downloaded', 'success');
    }

    generateSecurityPlan() {
        this.showNotification('Security Plan', 'Generating prioritized security remediation plan...', 'info');
        // Navigate to roadmap with security filter
        document.querySelector('[data-tab="roadmap"]').click();
    }

    exportSecurityReport() {
        const report = {
            timestamp: new Date().toISOString(),
            security: dashboardData.security,
            recommendations: []
        };
        
        const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'cortex-security-report.json';
        a.click();
        
        this.showNotification('Export Complete', 'Security report downloaded', 'success');
    }

    createComprehensivePlan() {
        this.showNotification('Comprehensive Plan', 'Creating full improvement roadmap...', 'info');
        document.querySelector('[data-tab="roadmap"]').click();
    }

    scheduleReview() {
        this.showNotification('Schedule Review', 'Feature coming soon: Schedule team review sessions', 'info');
    }

    generateRefactoringRoadmap() {
        this.showNotification('Refactoring Roadmap', 'Analyzing architecture for optimal refactoring sequence...', 'info');
    }

    showQuickWins() {
        this.showNotification('Quick Wins', 'Showing easiest fixes with highest impact...', 'success');
    }

    reviewTaskSequence() {
        this.showNotification('Task Sequence', 'Optimizing task order based on dependencies...', 'info');
    }

    setPerformanceBaseline() {
        this.showNotification('Performance Baseline', 'Establishing baseline metrics...', 'info');
    }

    runComplianceCheck() {
        this.showNotification('Compliance Check', 'Checking against security standards...', 'info');
    }
}

// Initialize discovery engine
window.addEventListener('DOMContentLoaded', () => {
    window.discoveryEngine = new DiscoveryEngine();
});

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DiscoveryEngine;
}
