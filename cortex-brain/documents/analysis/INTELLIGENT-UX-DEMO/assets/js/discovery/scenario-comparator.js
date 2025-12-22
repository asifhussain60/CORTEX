/**
 * CORTEX Discovery System - Scenario Comparator
 * Visual "what if" scenario comparisons with smooth transitions
 * 
 * @module ScenarioComparator
 * @version 1.0.0
 * @author Asif Hussain
 */

class ScenarioComparator {
    constructor() {
        this.scenarios = {
            auth: null,
            performance: null,
            security: null
        };
        this.currentComparison = null;
        this.loadScenarios();
    }

    /**
     * Load all scenario data
     */
    async loadScenarios() {
        const scenarioTypes = ['auth', 'performance', 'security'];
        
        for (const type of scenarioTypes) {
            try {
                const response = await fetch(`assets/data/scenarios/${type}-scenarios.json`);
                this.scenarios[type] = await response.json();
            } catch (error) {
                console.warn(`Could not load ${type} scenarios:`, error);
                this.scenarios[type] = this.getDefaultScenario(type);
            }
        }
    }

    /**
     * Get default scenarios as fallback
     */
    getDefaultScenario(type) {
        const defaults = {
            auth: {
                current: {
                    name: 'Basic Username/Password',
                    description: 'Simple authentication',
                    effort: '0 days (current)',
                    security: 40,
                    ux: 60,
                    cost: 0,
                    pros: ['Simple', 'Familiar to users'],
                    cons: ['Vulnerable to attacks', 'No recovery options']
                },
                options: [
                    {
                        name: 'Multi-Factor Authentication',
                        description: 'Add SMS/Email verification',
                        effort: '3-5 days',
                        security: 80,
                        ux: 55,
                        cost: 500,
                        pros: ['Much more secure', 'Industry standard'],
                        cons: ['Slight UX friction', 'Ongoing SMS costs']
                    },
                    {
                        name: 'OAuth 2.0',
                        description: 'Social login integration',
                        effort: '5-7 days',
                        security: 85,
                        ux: 75,
                        cost: 0,
                        pros: ['Very secure', 'Great UX', 'No password management'],
                        cons: ['Dependent on providers', 'More complex implementation']
                    }
                ]
            },
            performance: {
                current: {
                    name: 'No Optimization',
                    description: 'Current state',
                    effort: '0 days',
                    latency: 2847,
                    throughput: 50,
                    cost: 1000,
                    pros: ['Works as-is'],
                    cons: ['Slow response times', 'High server costs']
                },
                options: [
                    {
                        name: 'Basic Caching',
                        description: 'In-memory caching for common queries',
                        effort: '2-4 days',
                        latency: 856,
                        throughput: 200,
                        cost: 950,
                        pros: ['Easy to implement', 'Immediate improvements'],
                        cons: ['Cache invalidation complexity']
                    },
                    {
                        name: 'Full Optimization',
                        description: 'Caching + CDN + async processing',
                        effort: '2-3 weeks',
                        latency: 127,
                        throughput: 1000,
                        cost: 800,
                        pros: ['Dramatic performance gains', 'Better scalability'],
                        cons: ['Significant development effort', 'More infrastructure']
                    }
                ]
            },
            security: {
                current: {
                    name: 'Basic Security',
                    description: 'Minimal security measures',
                    effort: '0 days',
                    vulnerabilities: 173,
                    compliance: 41,
                    cost: 0,
                    pros: ['Simple to maintain'],
                    cons: ['High risk', 'Non-compliant']
                },
                options: [
                    {
                        name: 'Standard Security',
                        description: 'OWASP Top 10 compliance',
                        effort: '1-2 weeks',
                        vulnerabilities: 22,
                        compliance: 69,
                        cost: 5000,
                        pros: ['Industry standard', 'Reduced risk'],
                        cons: ['Moderate investment required']
                    },
                    {
                        name: 'Enterprise Security',
                        description: 'Full security audit + penetration testing',
                        effort: '4-6 weeks',
                        vulnerabilities: 3,
                        compliance: 89,
                        cost: 25000,
                        pros: ['Enterprise-grade', 'Full compliance'],
                        cons: ['Expensive', 'Long implementation']
                    }
                ]
            }
        };

        return defaults[type] || null;
    }

    /**
     * Compare scenarios side-by-side
     */
    compareScenarios(type, optionIndices = [0, 1]) {
        const scenarioData = this.scenarios[type];
        if (!scenarioData) {
            console.error(`No scenarios loaded for type: ${type}`);
            return null;
        }

        const current = scenarioData.current;
        const options = optionIndices.map(i => scenarioData.options[i]).filter(Boolean);

        this.currentComparison = {
            type,
            current,
            options,
            comparison: this.buildComparisonMatrix(current, options)
        };

        return this.currentComparison;
    }

    /**
     * Build comparison matrix
     */
    buildComparisonMatrix(current, options) {
        const matrix = {
            headers: ['Metric', 'Current', ...options.map(opt => opt.name)],
            rows: []
        };

        // Determine metrics based on available data
        const metrics = this.extractMetrics(current, options);

        metrics.forEach(metric => {
            const row = {
                metric: metric.label,
                values: [
                    this.formatMetricValue(current[metric.key], metric.format),
                    ...options.map(opt => this.formatMetricValue(opt[metric.key], metric.format))
                ],
                improvements: this.calculateImprovements(current[metric.key], options.map(opt => opt[metric.key]), metric.higherIsBetter)
            };

            matrix.rows.push(row);
        });

        return matrix;
    }

    /**
     * Extract metrics from scenarios
     */
    extractMetrics(current, options) {
        const allKeys = new Set([
            ...Object.keys(current),
            ...options.flatMap(opt => Object.keys(opt))
        ]);

        const metrics = [];
        const metricConfig = {
            effort: { label: 'Implementation Time', format: 'text', higherIsBetter: false },
            security: { label: 'Security Score', format: 'percent', higherIsBetter: true },
            ux: { label: 'User Experience', format: 'percent', higherIsBetter: true },
            cost: { label: 'Monthly Cost', format: 'currency', higherIsBetter: false },
            latency: { label: 'API Latency (ms)', format: 'number', higherIsBetter: false },
            throughput: { label: 'Requests/sec', format: 'number', higherIsBetter: true },
            vulnerabilities: { label: 'Vulnerabilities', format: 'number', higherIsBetter: false },
            compliance: { label: 'Compliance %', format: 'percent', higherIsBetter: true }
        };

        for (const key of allKeys) {
            if (metricConfig[key] && typeof current[key] !== 'undefined') {
                metrics.push({ key, ...metricConfig[key] });
            }
        }

        return metrics;
    }

    /**
     * Format metric value for display
     */
    formatMetricValue(value, format) {
        if (value === undefined || value === null) return 'N/A';

        switch (format) {
            case 'percent':
                return `${value}%`;
            case 'currency':
                return `$${value.toLocaleString()}`;
            case 'number':
                return value.toLocaleString();
            case 'text':
            default:
                return value;
        }
    }

    /**
     * Calculate improvement percentages
     */
    calculateImprovements(currentValue, optionValues, higherIsBetter) {
        return optionValues.map(optValue => {
            if (typeof currentValue !== 'number' || typeof optValue !== 'number') {
                return null;
            }

            const diff = optValue - currentValue;
            const percent = (diff / currentValue) * 100;

            const isImprovement = higherIsBetter ? diff > 0 : diff < 0;

            return {
                percent: Math.abs(percent).toFixed(1),
                direction: diff > 0 ? 'up' : 'down',
                isImprovement,
                icon: isImprovement ? '✅' : '⚠️'
            };
        });
    }

    /**
     * Render comparison as HTML
     */
    renderComparison(containerId) {
        if (!this.currentComparison) {
            console.error('No comparison to render');
            return;
        }

        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container '${containerId}' not found`);
            return;
        }

        const { current, options, comparison } = this.currentComparison;

        const html = `
            <div class="scenario-comparison">
                <div class="comparison-header mb-6">
                    <h3 class="text-2xl font-bold mb-2">Scenario Comparison</h3>
                    <p class="text-gray-600 dark:text-gray-400">Compare different enhancement options</p>
                </div>

                <!-- Comparison Table -->
                <div class="overflow-x-auto">
                    <table class="w-full border-collapse">
                        <thead>
                            <tr class="bg-gray-100 dark:bg-gray-800">
                                ${comparison.headers.map(header => `
                                    <th class="p-3 text-left font-semibold border-b-2 border-gray-300 dark:border-gray-600">
                                        ${header}
                                    </th>
                                `).join('')}
                            </tr>
                        </thead>
                        <tbody>
                            ${comparison.rows.map(row => `
                                <tr class="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 transition">
                                    <td class="p-3 font-medium">${row.metric}</td>
                                    ${row.values.map((value, i) => {
                                        const improvement = row.improvements[i - 1]; // Skip current (index 0)
                                        return `
                                            <td class="p-3">
                                                <div class="flex items-center gap-2">
                                                    <span>${value}</span>
                                                    ${improvement ? `
                                                        <span class="text-sm ${improvement.isImprovement ? 'text-green-600' : 'text-orange-500'}">
                                                            ${improvement.icon} ${improvement.direction === 'up' ? '+' : '-'}${improvement.percent}%
                                                        </span>
                                                    ` : ''}
                                                </div>
                                            </td>
                                        `;
                                    }).join('')}
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>

                <!-- Pros/Cons Cards -->
                <div class="grid grid-cols-1 md:grid-cols-${options.length + 1} gap-4 mt-8">
                    ${this.renderProConCard(current, 'Current State')}
                    ${options.map(opt => this.renderProConCard(opt, opt.name)).join('')}
                </div>
            </div>
        `;

        container.innerHTML = html;

        // Add smooth entrance animation
        container.style.opacity = '0';
        container.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            container.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            container.style.opacity = '1';
            container.style.transform = 'translateY(0)';
        }, 10);
    }

    /**
     * Render pros/cons card
     */
    renderProConCard(scenario, title) {
        return `
            <div class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-white dark:bg-gray-800">
                <h4 class="font-bold text-lg mb-2">${title}</h4>
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">${scenario.description}</p>
                
                ${scenario.pros ? `
                    <div class="mb-3">
                        <div class="font-semibold text-green-600 mb-1">✅ Pros:</div>
                        <ul class="text-sm space-y-1">
                            ${scenario.pros.map(pro => `<li class="text-gray-700 dark:text-gray-300">• ${pro}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}

                ${scenario.cons ? `
                    <div>
                        <div class="font-semibold text-orange-600 mb-1">⚠️ Cons:</div>
                        <ul class="text-sm space-y-1">
                            ${scenario.cons.map(con => `<li class="text-gray-700 dark:text-gray-300">• ${con}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
    }

    /**
     * Get available scenario types
     */
    getAvailableTypes() {
        return Object.keys(this.scenarios).filter(type => this.scenarios[type] !== null);
    }

    /**
     * Get scenario options for a type
     */
    getScenarioOptions(type) {
        const scenarioData = this.scenarios[type];
        return scenarioData ? scenarioData.options : [];
    }
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ScenarioComparator;
}
