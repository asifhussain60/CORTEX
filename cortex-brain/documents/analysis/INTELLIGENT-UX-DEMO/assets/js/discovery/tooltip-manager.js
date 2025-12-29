/**
 * CORTEX Discovery System - Tooltip Manager
 * Contextual tooltips with frosted glass effect for inline learning
 * 
 * @module TooltipManager
 * @version 1.0.0
 * @author Asif Hussain
 */

class TooltipManager {
    constructor() {
        this.tooltips = {};
        this.activeTooltip = null;
        this.options = {
            delay: 500,
            animationDuration: 200,
            maxWidth: 300,
            offset: 10
        };
        this.init();
    }

    /**
     * Initialize tooltip system
     */
    init() {
        this.loadTooltipDefinitions();
        this.attachTooltips();
        this.createTooltipContainer();
    }

    /**
     * Load tooltip definitions
     */
    loadTooltipDefinitions() {
        this.tooltips = {
            // Quality metrics
            'quality-score': {
                title: 'Quality Score',
                content: 'Overall code quality based on code smells, test coverage, complexity, and maintainability metrics.',
                learnMore: 'https://docs.cortex.dev/quality-metrics'
            },
            'technical-debt': {
                title: 'Technical Debt',
                content: 'Estimated time and cost to fix all quality issues. Based on industry standards (SQALE methodology).',
                learnMore: 'https://docs.cortex.dev/technical-debt'
            },
            'code-smells': {
                title: 'Code Smells',
                content: 'Patterns in code that indicate potential problems: God classes, tight coupling, long methods, etc.',
                learnMore: 'https://docs.cortex.dev/code-smells'
            },
            'test-coverage': {
                title: 'Test Coverage',
                content: 'Percentage of code covered by automated tests. Target: 80%+ for production code.',
                learnMore: 'https://docs.cortex.dev/test-coverage'
            },
            'cyclomatic-complexity': {
                title: 'Cyclomatic Complexity',
                content: 'Measure of code complexity. Higher values = harder to test and maintain. Target: <10 per method.',
                learnMore: 'https://docs.cortex.dev/complexity'
            },

            // Security metrics
            'owasp-top-10': {
                title: 'OWASP Top 10',
                content: 'Most critical web application security risks as defined by Open Web Application Security Project.',
                learnMore: 'https://owasp.org/www-project-top-ten/'
            },
            'cve': {
                title: 'CVE (Common Vulnerabilities and Exposures)',
                content: 'Publicly disclosed security vulnerabilities identified by unique ID numbers.',
                learnMore: 'https://cve.mitre.org/'
            },
            'compliance': {
                title: 'Compliance Score',
                content: 'Adherence to regulatory standards (GDPR, SOC 2, PCI-DSS, HIPAA). Critical for regulated industries.',
                learnMore: 'https://docs.cortex.dev/compliance'
            },

            // Performance metrics
            'api-latency': {
                title: 'API Latency',
                content: 'Time taken for API to respond. P95 = 95th percentile (95% of requests faster than this).',
                learnMore: 'https://docs.cortex.dev/performance'
            },
            'throughput': {
                title: 'Throughput',
                content: 'Number of requests handled per second. Indicates system capacity and scalability.',
                learnMore: 'https://docs.cortex.dev/throughput'
            },
            'error-rate': {
                title: 'Error Rate',
                content: 'Percentage of failed requests. Target: <1% for production systems.',
                learnMore: 'https://docs.cortex.dev/error-tracking'
            },

            // Architecture concepts
            'god-class': {
                title: 'God Class',
                content: 'Class that knows too much or does too much. Violates Single Responsibility Principle (SOLID).',
                learnMore: 'https://docs.cortex.dev/god-class'
            },
            'tight-coupling': {
                title: 'Tight Coupling',
                content: 'Components are too dependent on each other. Makes changes risky and testing difficult.',
                learnMore: 'https://docs.cortex.dev/coupling'
            },
            'circular-dependency': {
                title: 'Circular Dependency',
                content: 'Components depend on each other in a circular way. Creates initialization issues and fragility.',
                learnMore: 'https://docs.cortex.dev/circular-deps'
            },

            // TDD concepts
            'tdd': {
                title: 'Test-Driven Development (TDD)',
                content: 'Development process: Write failing test (RED) → Make it pass (GREEN) → Improve code (REFACTOR).',
                learnMore: 'https://docs.cortex.dev/tdd'
            },
            'red-green-refactor': {
                title: 'RED-GREEN-REFACTOR',
                content: 'TDD cycle: 1) Write failing test, 2) Write minimal code to pass, 3) Improve without breaking tests.',
                learnMore: 'https://docs.cortex.dev/tdd-cycle'
            }
        };
    }

    /**
     * Attach tooltips to elements
     */
    attachTooltips() {
        // Automatically attach to elements with data-tooltip attribute
        document.addEventListener('DOMContentLoaded', () => {
            const elements = document.querySelectorAll('[data-tooltip]');
            elements.forEach(element => {
                this.attachTooltip(element);
            });
        });

        // Re-attach on dynamic content changes
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1 && node.hasAttribute('data-tooltip')) {
                        this.attachTooltip(node);
                    }
                    if (node.querySelectorAll) {
                        node.querySelectorAll('[data-tooltip]').forEach(el => {
                            this.attachTooltip(el);
                        });
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    /**
     * Attach tooltip to specific element
     */
    attachTooltip(element) {
        const tooltipId = element.dataset.tooltip;
        if (!this.tooltips[tooltipId]) return;

        let showTimeout;

        element.addEventListener('mouseenter', (e) => {
            showTimeout = setTimeout(() => {
                this.showTooltip(tooltipId, element);
            }, this.options.delay);
        });

        element.addEventListener('mouseleave', () => {
            clearTimeout(showTimeout);
            this.hideTooltip();
        });

        // Touch support for mobile
        element.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.showTooltip(tooltipId, element);
            setTimeout(() => this.hideTooltip(), 3000);
        });
    }

    /**
     * Create tooltip container
     */
    createTooltipContainer() {
        if (document.getElementById('cortex-tooltip')) return;

        const container = document.createElement('div');
        container.id = 'cortex-tooltip';
        container.className = 'cortex-tooltip';
        container.style.cssText = `
            position: fixed;
            display: none;
            z-index: 10000;
            max-width: ${this.options.maxWidth}px;
            padding: 12px 16px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            border: 1px solid rgba(0, 0, 0, 0.1);
            pointer-events: none;
            transition: opacity ${this.options.animationDuration}ms ease, transform ${this.options.animationDuration}ms ease;
            opacity: 0;
            transform: translateY(10px);
        `;

        document.body.appendChild(container);
    }

    /**
     * Show tooltip
     */
    showTooltip(tooltipId, targetElement) {
        const tooltipData = this.tooltips[tooltipId];
        if (!tooltipData) return;

        const container = document.getElementById('cortex-tooltip');
        if (!container) return;

        // Build tooltip content
        container.innerHTML = `
            <div class="tooltip-content">
                <div class="tooltip-title" style="font-weight: 600; margin-bottom: 4px; font-size: 14px; color: #111827;">
                    ${tooltipData.title}
                </div>
                <div class="tooltip-body" style="font-size: 13px; line-height: 1.5; color: #4b5563;">
                    ${tooltipData.content}
                </div>
                ${tooltipData.learnMore ? `
                    <div class="tooltip-link" style="margin-top: 8px; font-size: 12px;">
                        <a href="${tooltipData.learnMore}" target="_blank" style="color: #3b82f6; text-decoration: none;">
                            Learn more →
                        </a>
                    </div>
                ` : ''}
            </div>
        `;

        // Position tooltip
        this.positionTooltip(container, targetElement);

        // Show with animation
        container.style.display = 'block';
        requestAnimationFrame(() => {
            container.style.opacity = '1';
            container.style.transform = 'translateY(0)';
        });

        this.activeTooltip = tooltipId;
    }

    /**
     * Position tooltip relative to target
     */
    positionTooltip(container, targetElement) {
        const rect = targetElement.getBoundingClientRect();
        const tooltipRect = container.getBoundingClientRect();

        let top = rect.bottom + this.options.offset;
        let left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);

        // Check if tooltip goes off screen
        if (left < 10) left = 10;
        if (left + tooltipRect.width > window.innerWidth - 10) {
            left = window.innerWidth - tooltipRect.width - 10;
        }

        // If tooltip goes below viewport, show above element
        if (top + tooltipRect.height > window.innerHeight - 10) {
            top = rect.top - tooltipRect.height - this.options.offset;
        }

        container.style.top = `${top}px`;
        container.style.left = `${left}px`;
    }

    /**
     * Hide tooltip
     */
    hideTooltip() {
        const container = document.getElementById('cortex-tooltip');
        if (!container) return;

        container.style.opacity = '0';
        container.style.transform = 'translateY(10px)';

        setTimeout(() => {
            container.style.display = 'none';
        }, this.options.animationDuration);

        this.activeTooltip = null;
    }

    /**
     * Register custom tooltip
     */
    registerTooltip(id, data) {
        this.tooltips[id] = {
            title: data.title,
            content: data.content,
            learnMore: data.learnMore || null
        };
    }

    /**
     * Add tooltip to element programmatically
     */
    addTooltip(element, tooltipId) {
        if (!this.tooltips[tooltipId]) {
            console.error(`Tooltip '${tooltipId}' not found`);
            return;
        }

        element.setAttribute('data-tooltip', tooltipId);
        this.attachTooltip(element);
    }

    /**
     * Update tooltip options
     */
    setOptions(options) {
        this.options = { ...this.options, ...options };
    }

    /**
     * Destroy tooltip system (cleanup)
     */
    destroy() {
        const container = document.getElementById('cortex-tooltip');
        if (container) {
            container.remove();
        }

        // Remove all tooltip attributes
        document.querySelectorAll('[data-tooltip]').forEach(element => {
            element.removeAttribute('data-tooltip');
        });
    }
}

// Auto-initialize on page load
window.addEventListener('DOMContentLoaded', () => {
    window.tooltipManager = new TooltipManager();
});

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TooltipManager;
}
