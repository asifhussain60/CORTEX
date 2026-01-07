/**
 * CORTEX Discovery System - Behavior Tracker
 * User pattern recognition and predictive suggestions
 * 
 * @module BehaviorTracker
 * @version 1.0.0
 * @author Asif Hussain
 */

class BehaviorTracker {
    constructor() {
        this.session = {
            startTime: Date.now(),
            viewedTabs: new Set(),
            timeSpent: {},
            interactions: [],
            currentFocus: null,
            scrollDepth: {},
            clickPatterns: []
        };
        this.patterns = [];
        this.init();
    }

    /**
     * Initialize tracking
     */
    init() {
        this.trackTabViews();
        this.trackInteractions();
        this.trackScrollDepth();
        this.trackMouseMovement();
        this.startAnalysis();
    }

    /**
     * Track tab views
     */
    trackTabViews() {
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const tabId = button.dataset.tab;
                this.recordTabView(tabId);
            });
        });
    }

    /**
     * Record tab view
     */
    recordTabView(tabId) {
        this.session.viewedTabs.add(tabId);
        this.session.currentFocus = tabId;

        // Initialize time tracking for this tab
        if (!this.session.timeSpent[tabId]) {
            this.session.timeSpent[tabId] = 0;
        }

        // Clear any existing tab timer
        if (this.activeTabTimer) {
            clearInterval(this.activeTabTimer);
        }

        // Start timer for current tab
        this.activeTabTimer = setInterval(() => {
            this.session.timeSpent[tabId]++;
            
            // Analyze behavior every 5 seconds
            if (this.session.timeSpent[tabId] % 5 === 0) {
                this.analyzeCurrentBehavior();
            }
        }, 1000);
    }

    /**
     * Track user interactions
     */
    trackInteractions() {
        // Click tracking
        document.addEventListener('click', (e) => {
            this.recordInteraction('click', e.target);
        });

        // Hover tracking (throttled)
        let hoverTimeout;
        document.addEventListener('mouseover', (e) => {
            clearTimeout(hoverTimeout);
            hoverTimeout = setTimeout(() => {
                this.recordInteraction('hover', e.target);
            }, 500);
        });
    }

    /**
     * Record interaction
     */
    recordInteraction(type, element) {
        const interaction = {
            type,
            element: element.tagName,
            classes: element.className,
            id: element.id,
            text: element.textContent?.substring(0, 50),
            timestamp: Date.now()
        };

        this.session.interactions.push(interaction);

        // Keep only last 100 interactions
        if (this.session.interactions.length > 100) {
            this.session.interactions.shift();
        }

        // Update click patterns
        if (type === 'click') {
            this.updateClickPatterns(element);
        }
    }

    /**
     * Update click patterns
     */
    updateClickPatterns(element) {
        const pattern = {
            element: element.tagName,
            classes: element.className,
            timestamp: Date.now()
        };

        this.session.clickPatterns.push(pattern);

        // Keep only last 20 clicks
        if (this.session.clickPatterns.length > 20) {
            this.session.clickPatterns.shift();
        }
    }

    /**
     * Track scroll depth
     */
    trackScrollDepth() {
        let scrollTimeout;
        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                const scrollPercentage = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
                this.recordScrollDepth(scrollPercentage);
            }, 200);
        });
    }

    /**
     * Record scroll depth
     */
    recordScrollDepth(percentage) {
        const currentTab = this.session.currentFocus;
        if (!currentTab) return;

        if (!this.session.scrollDepth[currentTab]) {
            this.session.scrollDepth[currentTab] = 0;
        }

        // Track max scroll depth per tab
        if (percentage > this.session.scrollDepth[currentTab]) {
            this.session.scrollDepth[currentTab] = percentage;
        }
    }

    /**
     * Track mouse movement (heatmap data)
     */
    trackMouseMovement() {
        // Simplified - in production, use a heatmap library
        this.mouseHeatmap = [];
        
        let moveTimeout;
        document.addEventListener('mousemove', (e) => {
            clearTimeout(moveTimeout);
            moveTimeout = setTimeout(() => {
                this.mouseHeatmap.push({
                    x: e.clientX,
                    y: e.clientY,
                    timestamp: Date.now()
                });

                // Keep only last 200 points
                if (this.mouseHeatmap.length > 200) {
                    this.mouseHeatmap.shift();
                }
            }, 100);
        });
    }

    /**
     * Start periodic behavior analysis
     */
    startAnalysis() {
        // Analyze every 10 seconds
        setInterval(() => {
            this.analyzeCurrentBehavior();
        }, 10000);
    }

    /**
     * Analyze current behavior and detect patterns
     */
    analyzeCurrentBehavior() {
        this.patterns = [];

        // Pattern 1: Deep engagement
        this.detectDeepEngagement();

        // Pattern 2: Quick scanning
        this.detectQuickScanning();

        // Pattern 3: Focused investigation
        this.detectFocusedInvestigation();

        // Pattern 4: Exploration pattern
        this.detectExploration();

        // Pattern 5: Confusion indicators
        this.detectConfusion();

        return this.patterns;
    }

    /**
     * Detect deep engagement pattern
     */
    detectDeepEngagement() {
        const currentTab = this.session.currentFocus;
        if (!currentTab) return;

        const timeOnTab = this.session.timeSpent[currentTab] || 0;
        const scrollDepth = this.session.scrollDepth[currentTab] || 0;

        if (timeOnTab > 30 && scrollDepth > 50) {
            this.patterns.push({
                type: 'deep_engagement',
                confidence: 0.85,
                description: `User is deeply engaged with ${currentTab} tab`,
                suggestions: [
                    'Offer detailed export or report',
                    'Provide deep-dive analysis options',
                    'Show related content'
                ]
            });
        }
    }

    /**
     * Detect quick scanning pattern
     */
    detectQuickScanning() {
        const tabCount = this.session.viewedTabs.size;
        const totalTime = this.getTotalTimeSpent();
        const avgTimePerTab = totalTime / tabCount;

        if (tabCount >= 3 && avgTimePerTab < 15) {
            this.patterns.push({
                type: 'quick_scanning',
                confidence: 0.75,
                description: 'User is quickly scanning multiple tabs',
                suggestions: [
                    'Offer executive summary',
                    'Highlight key findings',
                    'Show quick-win opportunities'
                ]
            });
        }
    }

    /**
     * Detect focused investigation
     */
    detectFocusedInvestigation() {
        const currentTab = this.session.currentFocus;
        if (!currentTab) return;

        const timeOnTab = this.session.timeSpent[currentTab] || 0;
        const recentInteractions = this.session.interactions.slice(-10);
        const interactionCount = recentInteractions.length;

        if (timeOnTab > 20 && interactionCount > 5) {
            this.patterns.push({
                type: 'focused_investigation',
                confidence: 0.9,
                description: `User is investigating ${currentTab} in detail`,
                suggestions: [
                    'Offer drill-down analysis',
                    'Show related data points',
                    'Provide comparative analysis'
                ]
            });
        }
    }

    /**
     * Detect exploration pattern
     */
    detectExploration() {
        const tabCount = this.session.viewedTabs.size;
        const totalTime = this.getTotalTimeSpent();

        if (tabCount >= 4 && totalTime > 60) {
            this.patterns.push({
                type: 'exploration',
                confidence: 0.8,
                description: 'User is exploring multiple areas',
                suggestions: [
                    'Offer guided path',
                    'Create comprehensive report',
                    'Show connections between areas'
                ]
            });
        }
    }

    /**
     * Detect confusion indicators
     */
    detectConfusion() {
        const recentClicks = this.session.clickPatterns.slice(-10);
        
        // Check for repeated clicks on same elements
        const clickMap = {};
        recentClicks.forEach(click => {
            const key = `${click.element}-${click.classes}`;
            clickMap[key] = (clickMap[key] || 0) + 1;
        });

        const repeatedClicks = Object.values(clickMap).filter(count => count >= 3);

        if (repeatedClicks.length > 0) {
            this.patterns.push({
                type: 'confusion',
                confidence: 0.7,
                description: 'User may be confused or looking for something',
                suggestions: [
                    'Offer help or tutorial',
                    'Show contextual tooltips',
                    'Provide search functionality'
                ]
            });
        }
    }

    /**
     * Get total time spent across all tabs
     */
    getTotalTimeSpent() {
        return Object.values(this.session.timeSpent).reduce((sum, time) => sum + time, 0);
    }

    /**
     * Get most viewed tab
     */
    getMostViewedTab() {
        let maxTime = 0;
        let maxTab = null;

        for (const [tab, time] of Object.entries(this.session.timeSpent)) {
            if (time > maxTime) {
                maxTime = time;
                maxTab = tab;
            }
        }

        return { tab: maxTab, time: maxTime };
    }

    /**
     * Get session summary
     */
    getSessionSummary() {
        const duration = (Date.now() - this.session.startTime) / 1000; // seconds
        const mostViewed = this.getMostViewedTab();

        return {
            duration,
            tabsViewed: this.session.viewedTabs.size,
            totalInteractions: this.session.interactions.length,
            mostViewedTab: mostViewed.tab,
            timeOnMostViewed: mostViewed.time,
            patterns: this.patterns,
            engagement: this.calculateEngagementScore()
        };
    }

    /**
     * Calculate engagement score (0-100)
     */
    calculateEngagementScore() {
        const duration = (Date.now() - this.session.startTime) / 1000;
        const tabCount = this.session.viewedTabs.size;
        const interactionCount = this.session.interactions.length;
        const avgScrollDepth = this.getAverageScrollDepth();

        // Weighted score
        const durationScore = Math.min((duration / 300) * 30, 30); // Max 30 points for 5 min
        const tabScore = Math.min(tabCount * 10, 30); // Max 30 points for 3+ tabs
        const interactionScore = Math.min(interactionCount * 2, 20); // Max 20 points
        const scrollScore = Math.min(avgScrollDepth / 5, 20); // Max 20 points

        return Math.round(durationScore + tabScore + interactionScore + scrollScore);
    }

    /**
     * Get average scroll depth
     */
    getAverageScrollDepth() {
        const depths = Object.values(this.session.scrollDepth);
        if (depths.length === 0) return 0;

        return depths.reduce((sum, depth) => sum + depth, 0) / depths.length;
    }

    /**
     * Export session data for analysis
     */
    exportSession() {
        return {
            session: {
                ...this.session,
                viewedTabs: Array.from(this.session.viewedTabs),
                duration: (Date.now() - this.session.startTime) / 1000
            },
            summary: this.getSessionSummary(),
            patterns: this.patterns
        };
    }

    /**
     * Reset session (for testing)
     */
    resetSession() {
        clearInterval(this.activeTabTimer);
        
        this.session = {
            startTime: Date.now(),
            viewedTabs: new Set(),
            timeSpent: {},
            interactions: [],
            currentFocus: null,
            scrollDepth: {},
            clickPatterns: []
        };
        
        this.patterns = [];
        this.mouseHeatmap = [];
    }
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BehaviorTracker;
}
