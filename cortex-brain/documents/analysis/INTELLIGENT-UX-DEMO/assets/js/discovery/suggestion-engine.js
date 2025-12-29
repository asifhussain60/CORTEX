/**
 * CORTEX Discovery System - Suggestion Engine
 * Pattern matching and context-aware suggestion generation
 * 
 * @module SuggestionEngine
 * @version 1.0.0
 * @author Asif Hussain
 */

class SuggestionEngine {
    constructor() {
        this.patterns = null;
        this.suggestionQueue = [];
        this.shownSuggestions = new Set();
        this.loadPatterns();
    }

    /**
     * Load suggestion patterns from JSON
     */
    async loadPatterns() {
        try {
            const response = await fetch('assets/data/patterns/suggestion-patterns.json');
            this.patterns = await response.json();
        } catch (error) {
            console.error('Error loading suggestion patterns:', error);
            this.patterns = this.getDefaultPatterns();
        }
    }

    /**
     * Get default patterns as fallback
     */
    getDefaultPatterns() {
        return {
            basicAuth: {
                keywords: ['username', 'password', 'basic auth', 'session'],
                triggerThreshold: 0.6,
                suggestions: [
                    {
                        id: 'mfa-suggestion',
                        title: 'Multi-Factor Authentication',
                        description: 'Add MFA for enhanced security',
                        effort: '3-5 days',
                        impact: { security: '+40%', ux: '+10%' },
                        priority: 'high'
                    },
                    {
                        id: 'oauth-suggestion',
                        title: 'OAuth 2.0 Integration',
                        description: 'Industry standard authentication',
                        effort: '5-7 days',
                        impact: { security: '+50%', compliance: 'High' },
                        priority: 'medium'
                    }
                ]
            },
            performanceBottleneck: {
                keywords: ['slow', 'bottleneck', 'latency', '>500ms', 'timeout'],
                triggerThreshold: 0.5,
                suggestions: [
                    {
                        id: 'caching-suggestion',
                        title: 'Implement Caching Strategy',
                        description: 'Redis or in-memory caching',
                        effort: '2-4 days',
                        impact: { performance: '+60%', cost: '-30%' },
                        priority: 'high'
                    },
                    {
                        id: 'async-suggestion',
                        title: 'Async Processing',
                        description: 'Background jobs for heavy operations',
                        effort: '3-5 days',
                        impact: { performance: '+40%', ux: '+25%' },
                        priority: 'medium'
                    }
                ]
            },
            securityVulnerability: {
                keywords: ['vulnerability', 'critical', 'OWASP', 'CVE', 'exploit'],
                triggerThreshold: 0.8,
                suggestions: [
                    {
                        id: 'security-audit-suggestion',
                        title: 'Security Audit',
                        description: 'Professional penetration testing',
                        effort: '1-2 weeks',
                        impact: { security: '+80%', compliance: 'Required' },
                        priority: 'critical'
                    }
                ]
            },
            complexCode: {
                keywords: ['god class', 'complexity', 'cyclomatic', 'spaghetti'],
                triggerThreshold: 0.7,
                suggestions: [
                    {
                        id: 'refactor-suggestion',
                        title: 'Refactoring Roadmap',
                        description: 'Break down complex components',
                        effort: '1-3 weeks',
                        impact: { maintainability: '+50%', bugs: '-40%' },
                        priority: 'medium'
                    }
                ]
            },
            lowTestCoverage: {
                keywords: ['test coverage', 'untested', 'no tests', 'quality'],
                triggerThreshold: 0.6,
                suggestions: [
                    {
                        id: 'tdd-suggestion',
                        title: 'TDD Implementation',
                        description: 'Test-Driven Development approach',
                        effort: '2-4 weeks',
                        impact: { quality: '+70%', confidence: '+90%' },
                        priority: 'high'
                    }
                ]
            }
        };
    }

    /**
     * Analyze current context and detect patterns
     */
    detectPatterns(context, dashboardData) {
        const detected = [];

        if (!this.patterns) {
            console.warn('Patterns not loaded yet');
            return detected;
        }

        // Check authentication patterns
        if (context.tab === 'architecture' || context.tab === 'security') {
            const authComponent = dashboardData?.architecture?.components?.find(c => c.name === 'Authentication');
            if (authComponent && authComponent.health < 70) {
                detected.push({
                    pattern: 'basicAuth',
                    confidence: 0.8,
                    context: 'Authentication component has low health score'
                });
            }
        }

        // Check performance patterns
        if (context.tab === 'journey' || context.tab === 'performance') {
            const avgLatency = dashboardData?.performance?.api_latency_avg || 0;
            if (avgLatency > 500) {
                detected.push({
                    pattern: 'performanceBottleneck',
                    confidence: 0.9,
                    context: `Average API latency is ${avgLatency}ms (target: <500ms)`
                });
            }
        }

        // Check security patterns
        if (context.tab === 'security') {
            const criticalVulns = dashboardData?.security?.vulnerabilities?.critical || 0;
            if (criticalVulns > 0) {
                detected.push({
                    pattern: 'securityVulnerability',
                    confidence: 1.0,
                    context: `${criticalVulns} critical vulnerabilities detected`
                });
            }
        }

        // Check code quality patterns
        if (context.tab === 'quality') {
            const qualityScore = dashboardData?.quality?.overall_score || 100;
            if (qualityScore < 70) {
                detected.push({
                    pattern: 'complexCode',
                    confidence: 0.75,
                    context: `Quality score is ${qualityScore}% (target: >80%)`
                });
            }

            const testCoverage = dashboardData?.quality?.test_coverage || 100;
            if (testCoverage < 60) {
                detected.push({
                    pattern: 'lowTestCoverage',
                    confidence: 0.85,
                    context: `Test coverage is ${testCoverage}% (target: >80%)`
                });
            }
        }

        return detected;
    }

    /**
     * Generate suggestions based on detected patterns
     */
    generateSuggestions(detectedPatterns) {
        const suggestions = [];

        detectedPatterns.forEach(detection => {
            const patternData = this.patterns[detection.pattern];
            if (!patternData) return;

            // Only generate if confidence meets threshold
            if (detection.confidence < patternData.triggerThreshold) return;

            patternData.suggestions.forEach(suggestion => {
                // Skip if already shown
                if (this.shownSuggestions.has(suggestion.id)) return;

                suggestions.push({
                    ...suggestion,
                    detectionContext: detection.context,
                    confidence: detection.confidence,
                    timestamp: Date.now()
                });
            });
        });

        // Sort by priority and confidence
        suggestions.sort((a, b) => {
            const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
            const priorityDiff = priorityOrder[a.priority] - priorityOrder[b.priority];
            return priorityDiff !== 0 ? priorityDiff : b.confidence - a.confidence;
        });

        return suggestions;
    }

    /**
     * Queue suggestion for display
     */
    queueSuggestion(suggestion) {
        if (this.suggestionQueue.find(s => s.id === suggestion.id)) {
            return false;
        }

        this.suggestionQueue.push(suggestion);
        this.suggestionQueue.sort((a, b) => {
            const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
            return priorityOrder[a.priority] - priorityOrder[b.priority];
        });

        return true;
    }

    /**
     * Get next suggestion from queue
     */
    getNextSuggestion() {
        return this.suggestionQueue.shift();
    }

    /**
     * Mark suggestion as shown
     */
    markShown(suggestionId) {
        this.shownSuggestions.add(suggestionId);
        localStorage.setItem(`suggestion-shown-${suggestionId}`, 'true');
    }

    /**
     * Check if suggestion was shown
     */
    wasShown(suggestionId) {
        return this.shownSuggestions.has(suggestionId) || 
               localStorage.getItem(`suggestion-shown-${suggestionId}`) === 'true';
    }

    /**
     * Clear shown suggestions (for testing)
     */
    clearShownSuggestions() {
        this.shownSuggestions.clear();
        this.suggestionQueue = [];
        
        // Clear localStorage
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith('suggestion-shown-')) {
                localStorage.removeItem(key);
            }
        }
    }

    /**
     * Get tab-specific contextual suggestions
     */
    getContextualSuggestions(tabId, dashboardData) {
        const suggestions = {
            executive: [
                {
                    id: 'executive-drill-down',
                    title: 'Drill Down Analysis',
                    description: 'Explore specific areas in detail with guided navigation',
                    priority: 'medium'
                }
            ],
            architecture: [
                {
                    id: 'architecture-refactor',
                    title: 'Refactoring Opportunities',
                    description: 'Generate automated refactoring roadmap',
                    priority: 'high'
                }
            ],
            quality: [
                {
                    id: 'quality-quick-wins',
                    title: 'Quick Quality Wins',
                    description: 'Show fixable issues < 2 hours',
                    priority: 'high'
                }
            ],
            roadmap: [
                {
                    id: 'roadmap-prioritization',
                    title: 'Smart Prioritization',
                    description: 'AI-optimized task sequence',
                    priority: 'medium'
                }
            ],
            journey: [
                {
                    id: 'performance-baseline',
                    title: 'Performance Baseline',
                    description: 'Establish benchmarks before optimization',
                    priority: 'medium'
                }
            ],
            security: [
                {
                    id: 'security-compliance',
                    title: 'Compliance Check',
                    description: 'OWASP ASVS or CWE Top 25 validation',
                    priority: 'high'
                }
            ]
        };

        return suggestions[tabId] || [];
    }
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SuggestionEngine;
}
