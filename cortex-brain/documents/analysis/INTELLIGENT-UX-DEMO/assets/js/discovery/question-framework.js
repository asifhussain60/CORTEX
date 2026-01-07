/**
 * CORTEX Discovery System - Question Framework
 * Progressive questioning for clarification, exploration, and learning
 * 
 * @module QuestionFramework
 * @version 1.0.0
 * @author Asif Hussain
 */

class QuestionFramework {
    constructor() {
        this.questionTrees = null;
        this.currentQuestion = null;
        this.questionHistory = [];
        this.userResponses = {};
        this.loadQuestionTrees();
    }

    /**
     * Load question trees from JSON
     */
    async loadQuestionTrees() {
        try {
            const response = await fetch('assets/data/patterns/question-trees.json');
            this.questionTrees = await response.json();
        } catch (error) {
            console.error('Error loading question trees:', error);
            this.questionTrees = this.getDefaultQuestions();
        }
    }

    /**
     * Get default questions as fallback
     */
    getDefaultQuestions() {
        return {
            clarification: {
                enhancement_priorities: {
                    id: 'enhancement_priorities',
                    type: 'multi-select',
                    question: 'What matters most to you?',
                    description: 'Select all that apply to help me understand your priorities',
                    options: [
                        { id: 'speed', label: 'Speed up processing time', nextQuestion: 'performance_goals' },
                        { id: 'security', label: 'Improve security and fraud detection', nextQuestion: 'security_goals' },
                        { id: 'features', label: 'Add new features/capabilities', nextQuestion: 'feature_goals' },
                        { id: 'quality', label: 'Improve code quality', nextQuestion: 'quality_goals' },
                        { id: 'cost', label: 'Reduce operational costs', nextQuestion: 'cost_goals' }
                    ]
                },
                performance_goals: {
                    id: 'performance_goals',
                    type: 'single-select',
                    question: 'What level of performance improvement are you targeting?',
                    options: [
                        { id: 'incremental', label: '20-30% improvement (quick wins)', impact: 'low' },
                        { id: 'significant', label: '50-70% improvement (moderate refactoring)', impact: 'medium' },
                        { id: 'dramatic', label: '80%+ improvement (architectural changes)', impact: 'high' }
                    ]
                },
                security_goals: {
                    id: 'security_goals',
                    type: 'multi-select',
                    question: 'Which security areas concern you most?',
                    options: [
                        { id: 'auth', label: 'Authentication/Authorization', severity: 'high' },
                        { id: 'data', label: 'Data encryption and privacy', severity: 'high' },
                        { id: 'vulns', label: 'Known vulnerabilities (CVEs)', severity: 'critical' },
                        { id: 'compliance', label: 'Regulatory compliance (GDPR, SOC 2)', severity: 'medium' }
                    ]
                }
            },
            exploration: {
                alternative_approaches: {
                    id: 'alternative_approaches',
                    type: 'scenario-comparison',
                    question: 'I see several ways to approach this. Would you like to compare options?',
                    scenarios: ['conservative', 'balanced', 'aggressive']
                },
                technical_depth: {
                    id: 'technical_depth',
                    type: 'single-select',
                    question: 'How deep should we go technically?',
                    options: [
                        { id: 'executive', label: 'Executive summary only (high-level)', audience: 'leadership' },
                        { id: 'balanced', label: 'Balanced (some technical details)', audience: 'product' },
                        { id: 'detailed', label: 'Full technical deep-dive', audience: 'engineering' }
                    ]
                }
            },
            learning: {
                pattern_explanation: {
                    id: 'pattern_explanation',
                    type: 'info',
                    question: 'Would you like to understand why I\'m suggesting this?',
                    explanation: 'I detected a pattern indicating {{pattern_name}}. This typically means {{reason}} and can be addressed by {{solution}}.'
                },
                best_practices: {
                    id: 'best_practices',
                    type: 'expandable',
                    question: 'Want to learn the industry best practices for this?',
                    content: 'Show relevant patterns, case studies, benchmarks'
                }
            }
        };
    }

    /**
     * Start a question flow
     */
    startFlow(flowType, context) {
        if (!this.questionTrees || !this.questionTrees[flowType]) {
            console.error(`Question flow '${flowType}' not found`);
            return null;
        }

        // Get first question in flow
        const firstQuestionId = Object.keys(this.questionTrees[flowType])[0];
        this.currentQuestion = this.questionTrees[flowType][firstQuestionId];
        this.questionHistory = [this.currentQuestion];

        return this.formatQuestion(this.currentQuestion, context);
    }

    /**
     * Handle user response and get next question
     */
    async handleResponse(questionId, response, context) {
        // Store response
        this.userResponses[questionId] = response;

        // Find current question
        const question = this.findQuestion(questionId);
        if (!question) {
            console.error(`Question '${questionId}' not found`);
            return null;
        }

        // Determine next question based on response
        const nextQuestionId = this.determineNextQuestion(question, response);
        
        if (!nextQuestionId) {
            // End of flow
            return {
                type: 'complete',
                summary: this.generateSummary(),
                recommendations: this.generateRecommendations(context)
            };
        }

        // Get next question
        const nextQuestion = this.findQuestion(nextQuestionId);
        if (!nextQuestion) {
            return this.handleResponse(questionId, response, context); // Try to complete
        }

        this.currentQuestion = nextQuestion;
        this.questionHistory.push(nextQuestion);

        return this.formatQuestion(nextQuestion, context);
    }

    /**
     * Find question by ID across all trees
     */
    findQuestion(questionId) {
        if (!this.questionTrees) return null;

        for (const flowType in this.questionTrees) {
            if (this.questionTrees[flowType][questionId]) {
                return this.questionTrees[flowType][questionId];
            }
        }
        return null;
    }

    /**
     * Determine next question based on response
     */
    determineNextQuestion(question, response) {
        if (!question.options) return null;

        // For single-select, find matching option's nextQuestion
        if (question.type === 'single-select') {
            const selected = question.options.find(opt => opt.id === response);
            return selected?.nextQuestion || null;
        }

        // For multi-select, use highest priority nextQuestion
        if (question.type === 'multi-select' && Array.isArray(response)) {
            const nextQuestions = response
                .map(respId => question.options.find(opt => opt.id === respId))
                .filter(opt => opt && opt.nextQuestion)
                .map(opt => opt.nextQuestion);
            
            return nextQuestions.length > 0 ? nextQuestions[0] : null;
        }

        return null;
    }

    /**
     * Format question for display
     */
    formatQuestion(question, context) {
        if (!question) return null;

        const formatted = {
            id: question.id,
            type: question.type,
            question: question.question,
            description: question.description,
            options: question.options || [],
            metadata: {
                progress: `${this.questionHistory.length} of ~${this.estimateTotalQuestions()}`,
                canGoBack: this.questionHistory.length > 1
            }
        };

        // Replace template variables
        if (context) {
            formatted.question = this.replaceTemplateVars(formatted.question, context);
            if (formatted.description) {
                formatted.description = this.replaceTemplateVars(formatted.description, context);
            }
        }

        return formatted;
    }

    /**
     * Replace template variables in strings
     */
    replaceTemplateVars(text, context) {
        return text.replace(/\{\{(\w+)\}\}/g, (match, key) => {
            return context[key] || match;
        });
    }

    /**
     * Estimate total questions in flow
     */
    estimateTotalQuestions() {
        // Simple heuristic: 3-5 questions per flow
        return 5;
    }

    /**
     * Go back to previous question
     */
    goBack() {
        if (this.questionHistory.length <= 1) {
            return null; // Can't go back from first question
        }

        // Remove current question
        this.questionHistory.pop();
        
        // Get previous question
        this.currentQuestion = this.questionHistory[this.questionHistory.length - 1];
        
        // Remove stored response for current question
        delete this.userResponses[this.currentQuestion.id];

        return this.formatQuestion(this.currentQuestion, {});
    }

    /**
     * Generate summary of user responses
     */
    generateSummary() {
        const summary = {
            totalQuestions: this.questionHistory.length,
            responses: this.userResponses,
            priorities: [],
            insights: []
        };

        // Extract priorities from responses
        for (const [questionId, response] of Object.entries(this.userResponses)) {
            const question = this.findQuestion(questionId);
            if (!question) continue;

            if (questionId === 'enhancement_priorities' && Array.isArray(response)) {
                summary.priorities = response.map(respId => {
                    const option = question.options.find(opt => opt.id === respId);
                    return option?.label || respId;
                });
            }
        }

        return summary;
    }

    /**
     * Generate recommendations based on responses
     */
    generateRecommendations(context) {
        const recommendations = [];
        const responses = this.userResponses;

        // Security-focused recommendations
        if (responses.enhancement_priorities?.includes('security')) {
            recommendations.push({
                category: 'Security',
                priority: 'high',
                items: [
                    'Implement multi-factor authentication',
                    'Conduct security audit',
                    'Address critical vulnerabilities first'
                ]
            });
        }

        // Performance-focused recommendations
        if (responses.enhancement_priorities?.includes('speed')) {
            const perfLevel = responses.performance_goals;
            if (perfLevel === 'dramatic') {
                recommendations.push({
                    category: 'Performance',
                    priority: 'high',
                    items: [
                        'Consider architectural refactoring',
                        'Implement caching layer',
                        'Optimize database queries',
                        'Use CDN for static assets'
                    ]
                });
            } else {
                recommendations.push({
                    category: 'Performance',
                    priority: 'medium',
                    items: [
                        'Add query optimization',
                        'Implement basic caching',
                        'Review slow endpoints'
                    ]
                });
            }
        }

        // Quality-focused recommendations
        if (responses.enhancement_priorities?.includes('quality')) {
            recommendations.push({
                category: 'Code Quality',
                priority: 'medium',
                items: [
                    'Increase test coverage to 80%+',
                    'Implement TDD practices',
                    'Address code smells',
                    'Setup automated code review'
                ]
            });
        }

        return recommendations;
    }

    /**
     * Reset framework for new session
     */
    reset() {
        this.currentQuestion = null;
        this.questionHistory = [];
        this.userResponses = {};
    }
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = QuestionFramework;
}
