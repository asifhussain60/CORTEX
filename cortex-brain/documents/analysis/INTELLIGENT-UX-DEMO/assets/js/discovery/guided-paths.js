/**
 * CORTEX Discovery System - Guided Paths
 * Discovery journey builder with breadcrumb navigation and progress tracking
 * 
 * @module GuidedPaths
 * @version 1.0.0
 * @author Asif Hussain
 */

class GuidedPaths {
    constructor() {
        this.paths = null;
        this.currentPath = null;
        this.currentStep = 0;
        this.pathHistory = [];
        this.loadPaths();
    }

    /**
     * Load discovery paths from JSON
     */
    async loadPaths() {
        try {
            const response = await fetch('assets/data/patterns/discovery-paths.json');
            this.paths = await response.json();
        } catch (error) {
            console.error('Error loading discovery paths:', error);
            this.paths = this.getDefaultPaths();
        }
    }

    /**
     * Get default paths as fallback
     */
    getDefaultPaths() {
        return {
            technical: {
                id: 'technical',
                name: 'Technical Deep Dive',
                description: 'For engineers wanting detailed analysis',
                audience: 'Engineering Team',
                duration: '15-20 minutes',
                steps: [
                    {
                        id: 'tech-1',
                        tab: 'architecture',
                        title: 'Architecture Overview',
                        description: 'Understand system structure and dependencies',
                        focusAreas: ['components', 'relationships', 'complexity'],
                        questions: ['Are there any circular dependencies?', 'Which components need refactoring?'],
                        nextStep: 'tech-2'
                    },
                    {
                        id: 'tech-2',
                        tab: 'quality',
                        title: 'Code Quality Analysis',
                        description: 'Review code smells and technical debt',
                        focusAreas: ['code_smells', 'complexity', 'duplication'],
                        questions: ['What are the quick wins?', 'Which refactorings have highest ROI?'],
                        nextStep: 'tech-3'
                    },
                    {
                        id: 'tech-3',
                        tab: 'journey',
                        title: 'Performance Bottlenecks',
                        description: 'Identify and prioritize performance issues',
                        focusAreas: ['latency', 'throughput', 'errors'],
                        questions: ['Where are the slowest endpoints?', 'Can we cache anything?'],
                        nextStep: 'tech-4'
                    },
                    {
                        id: 'tech-4',
                        tab: 'security',
                        title: 'Security Assessment',
                        description: 'Review vulnerabilities and compliance',
                        focusAreas: ['vulnerabilities', 'compliance', 'best_practices'],
                        questions: ['What are critical security risks?', 'Compliance gaps?'],
                        nextStep: 'tech-5'
                    },
                    {
                        id: 'tech-5',
                        tab: 'roadmap',
                        title: 'Implementation Roadmap',
                        description: 'Create prioritized action plan',
                        focusAreas: ['priorities', 'dependencies', 'timeline'],
                        questions: ['What should we do first?', 'What are dependencies?'],
                        nextStep: null
                    }
                ]
            },
            executive: {
                id: 'executive',
                name: 'Executive Overview',
                description: 'For leadership wanting strategic insights',
                audience: 'Executive Leadership',
                duration: '5-10 minutes',
                steps: [
                    {
                        id: 'exec-1',
                        tab: 'executive',
                        title: 'Executive Summary',
                        description: 'High-level metrics and business impact',
                        focusAreas: ['quality_score', 'technical_debt', 'risk_assessment'],
                        questions: ['What is our overall health?', 'Where should we invest?'],
                        nextStep: 'exec-2'
                    },
                    {
                        id: 'exec-2',
                        tab: 'security',
                        title: 'Security & Compliance',
                        description: 'Risk assessment and regulatory status',
                        focusAreas: ['critical_vulnerabilities', 'compliance_gaps', 'recommendations'],
                        questions: ['Are we at risk?', 'What does compliance require?'],
                        nextStep: 'exec-3'
                    },
                    {
                        id: 'exec-3',
                        tab: 'roadmap',
                        title: 'Strategic Roadmap',
                        description: 'Investment priorities and timeline',
                        focusAreas: ['high_impact_items', 'timeline', 'resource_needs'],
                        questions: ['What will this cost?', 'When can we complete it?'],
                        nextStep: null
                    }
                ]
            },
            developer: {
                id: 'developer',
                name: 'Developer Journey',
                description: 'For developers working on improvements',
                audience: 'Development Team',
                duration: '10-15 minutes',
                steps: [
                    {
                        id: 'dev-1',
                        tab: 'quality',
                        title: 'Quick Wins',
                        description: 'Easy fixes with high impact',
                        focusAreas: ['low_hanging_fruit', 'test_coverage', 'linting'],
                        questions: ['What can I fix today?', 'Where should I add tests?'],
                        nextStep: 'dev-2'
                    },
                    {
                        id: 'dev-2',
                        tab: 'architecture',
                        title: 'Refactoring Targets',
                        description: 'Components needing restructure',
                        focusAreas: ['god_classes', 'tight_coupling', 'violations'],
                        questions: ['Which classes need refactoring?', 'How can I improve coupling?'],
                        nextStep: 'dev-3'
                    },
                    {
                        id: 'dev-3',
                        tab: 'journey',
                        title: 'Performance Optimization',
                        description: 'Code-level performance improvements',
                        focusAreas: ['slow_queries', 'n+1_queries', 'caching_opportunities'],
                        questions: ['Which queries are slow?', 'Where should I cache?'],
                        nextStep: 'dev-4'
                    },
                    {
                        id: 'dev-4',
                        tab: 'roadmap',
                        title: 'My Action Items',
                        description: 'Personalized task list',
                        focusAreas: ['assigned_tasks', 'priorities', 'blockers'],
                        questions: ['What are my tasks?', 'Any blockers?'],
                        nextStep: null
                    }
                ]
            }
        };
    }

    /**
     * Start a guided path
     */
    startPath(pathId) {
        const path = this.paths[pathId];
        if (!path) {
            console.error(`Path '${pathId}' not found`);
            return null;
        }

        this.currentPath = path;
        this.currentStep = 0;
        this.pathHistory = [{ pathId, stepIndex: 0, timestamp: Date.now() }];

        return this.getCurrentStepData();
    }

    /**
     * Get current step data
     */
    getCurrentStepData() {
        if (!this.currentPath) return null;

        const step = this.currentPath.steps[this.currentStep];
        if (!step) return null;

        return {
            path: {
                id: this.currentPath.id,
                name: this.currentPath.name,
                audience: this.currentPath.audience,
                duration: this.currentPath.duration
            },
            step: {
                ...step,
                index: this.currentStep,
                total: this.currentPath.steps.length,
                progress: ((this.currentStep + 1) / this.currentPath.steps.length) * 100,
                isFirst: this.currentStep === 0,
                isLast: this.currentStep === this.currentPath.steps.length - 1
            },
            navigation: {
                canGoBack: this.currentStep > 0,
                canGoNext: this.currentStep < this.currentPath.steps.length - 1,
                canComplete: this.currentStep === this.currentPath.steps.length - 1
            }
        };
    }

    /**
     * Navigate to next step
     */
    nextStep() {
        if (!this.currentPath) return null;

        if (this.currentStep >= this.currentPath.steps.length - 1) {
            // Path complete
            return this.completePath();
        }

        this.currentStep++;
        this.pathHistory.push({
            pathId: this.currentPath.id,
            stepIndex: this.currentStep,
            timestamp: Date.now()
        });

        // Switch to appropriate tab
        const stepData = this.getCurrentStepData();
        if (stepData && stepData.step.tab) {
            this.switchTab(stepData.step.tab);
        }

        return stepData;
    }

    /**
     * Navigate to previous step
     */
    previousStep() {
        if (!this.currentPath || this.currentStep <= 0) return null;

        this.currentStep--;
        this.pathHistory.push({
            pathId: this.currentPath.id,
            stepIndex: this.currentStep,
            timestamp: Date.now()
        });

        const stepData = this.getCurrentStepData();
        if (stepData && stepData.step.tab) {
            this.switchTab(stepData.step.tab);
        }

        return stepData;
    }

    /**
     * Jump to specific step
     */
    goToStep(stepIndex) {
        if (!this.currentPath) return null;
        if (stepIndex < 0 || stepIndex >= this.currentPath.steps.length) return null;

        this.currentStep = stepIndex;
        this.pathHistory.push({
            pathId: this.currentPath.id,
            stepIndex: this.currentStep,
            timestamp: Date.now()
        });

        const stepData = this.getCurrentStepData();
        if (stepData && stepData.step.tab) {
            this.switchTab(stepData.step.tab);
        }

        return stepData;
    }

    /**
     * Complete current path
     */
    completePath() {
        const completion = {
            pathId: this.currentPath.id,
            pathName: this.currentPath.name,
            completedAt: Date.now(),
            duration: this.calculateDuration(),
            stepsCompleted: this.currentStep + 1,
            totalSteps: this.currentPath.steps.length,
            history: this.pathHistory
        };

        // Store completion in localStorage
        this.saveCompletion(completion);

        return {
            type: 'complete',
            completion,
            suggestions: this.generateNextSteps()
        };
    }

    /**
     * Calculate path duration
     */
    calculateDuration() {
        if (this.pathHistory.length < 2) return 0;

        const start = this.pathHistory[0].timestamp;
        const end = this.pathHistory[this.pathHistory.length - 1].timestamp;
        
        return Math.round((end - start) / 1000); // seconds
    }

    /**
     * Save completion to localStorage
     */
    saveCompletion(completion) {
        try {
            const key = 'cortex-path-completions';
            const existing = JSON.parse(localStorage.getItem(key) || '[]');
            existing.push(completion);
            
            // Keep only last 10 completions
            const recent = existing.slice(-10);
            localStorage.setItem(key, JSON.stringify(recent));
        } catch (error) {
            console.error('Error saving completion:', error);
        }
    }

    /**
     * Generate next step suggestions
     */
    generateNextSteps() {
        const suggestions = [];

        // Suggest different paths
        const completedPathId = this.currentPath.id;
        for (const [pathId, path] of Object.entries(this.paths)) {
            if (pathId !== completedPathId) {
                suggestions.push({
                    type: 'path',
                    id: pathId,
                    title: `Try ${path.name}`,
                    description: path.description,
                    action: () => this.startPath(pathId)
                });
            }
        }

        // Suggest deep dive
        suggestions.push({
            type: 'explore',
            title: 'Explore on Your Own',
            description: 'Free navigation through all tabs',
            action: () => this.exitGuidedMode()
        });

        return suggestions;
    }

    /**
     * Switch to tab
     */
    switchTab(tabId) {
        const tabButton = document.querySelector(`[data-tab="${tabId}"]`);
        if (tabButton) {
            tabButton.click();
        }
    }

    /**
     * Exit guided mode
     */
    exitGuidedMode() {
        this.currentPath = null;
        this.currentStep = 0;
        
        // Hide breadcrumb navigation
        const breadcrumb = document.getElementById('guided-path-breadcrumb');
        if (breadcrumb) {
            breadcrumb.style.display = 'none';
        }
    }

    /**
     * Render breadcrumb navigation
     */
    renderBreadcrumb(containerId) {
        const stepData = this.getCurrentStepData();
        if (!stepData) return;

        const container = document.getElementById(containerId);
        if (!container) return;

        const { path, step, navigation } = stepData;

        const html = `
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 border-l-4 border-blue-500">
                <div class="flex items-center justify-between mb-2">
                    <div class="flex items-center gap-2">
                        <span class="text-blue-600 font-semibold">🗺️ ${path.name}</span>
                        <span class="text-gray-500 text-sm">•</span>
                        <span class="text-gray-600 dark:text-gray-400 text-sm">${path.audience}</span>
                    </div>
                    <button onclick="window.guidedPaths.exitGuidedMode()" class="text-gray-500 hover:text-gray-700 text-sm">
                        Exit Guide
                    </button>
                </div>

                <!-- Progress Bar -->
                <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-3">
                    <div class="bg-blue-600 h-2 rounded-full transition-all duration-500" style="width: ${step.progress}%"></div>
                </div>

                <!-- Step Info -->
                <div class="mb-3">
                    <div class="flex items-center gap-2 mb-1">
                        <span class="font-semibold">Step ${step.index + 1} of ${step.total}:</span>
                        <span>${step.title}</span>
                    </div>
                    <p class="text-sm text-gray-600 dark:text-gray-400">${step.description}</p>
                </div>

                <!-- Navigation Buttons -->
                <div class="flex gap-2">
                    ${navigation.canGoBack ? `
                        <button onclick="window.guidedPaths.previousStep()" 
                                class="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded hover:bg-gray-300 dark:hover:bg-gray-600 transition">
                            ← Previous
                        </button>
                    ` : ''}
                    
                    ${navigation.canGoNext ? `
                        <button onclick="window.guidedPaths.nextStep()" 
                                class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition">
                            Next →
                        </button>
                    ` : ''}

                    ${navigation.canComplete ? `
                        <button onclick="window.guidedPaths.completePath()" 
                                class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition">
                            ✓ Complete
                        </button>
                    ` : ''}
                </div>
            </div>
        `;

        container.innerHTML = html;
        container.style.display = 'block';
    }

    /**
     * Get all available paths
     */
    getAvailablePaths() {
        return Object.values(this.paths);
    }
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GuidedPaths;
}
