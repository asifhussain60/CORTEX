/**
 * CORTEX Lens - Shared UI Components
 * 
 * Reusable components for dashboard templates:
 * - Narrative panels with collapsible sections
 * - KPI scorecards with trend indicators
 * - Reconciliation widgets for validation status
 * - Interactive tooltips and modals
 */

// ============================================================================
// Narrative Panel Component
// ============================================================================

class NarrativePanel {
    constructor(containerId, narrativeData) {
        this.container = document.getElementById(containerId);
        this.data = narrativeData;
        this.render();
    }

    render() {
        if (!this.container || !this.data) return;

        const html = `
            <div class="narrative-panel">
                <div class="narrative-header">
                    <h3 class="narrative-title">${this.data.title || 'Business Narrative'}</h3>
                    <button class="narrative-toggle" onclick="this.closest('.narrative-panel').classList.toggle('collapsed')">
                        <span class="toggle-icon">▼</span>
                    </button>
                </div>
                <div class="narrative-content">
                    ${this.renderSections()}
                </div>
            </div>
        `;

        this.container.innerHTML = html;
    }

    renderSections() {
        if (!this.data.sections) return '';

        return this.data.sections.map(section => `
            <div class="narrative-section">
                <h4 class="section-title">${section.title}</h4>
                <div class="section-content">${section.content}</div>
                ${section.insights ? this.renderInsights(section.insights) : ''}
            </div>
        `).join('');
    }

    renderInsights(insights) {
        return `
            <div class="insights-list">
                ${insights.map(insight => `
                    <div class="insight-item">
                        <span class="insight-icon">${insight.icon || '💡'}</span>
                        <span class="insight-text">${insight.text}</span>
                    </div>
                `).join('')}
            </div>
        `;
    }
}

// ============================================================================
// KPI Scorecard Component
// ============================================================================

class KPIScorecard {
    constructor(containerId, metrics) {
        this.container = document.getElementById(containerId);
        this.metrics = metrics;
        this.render();
    }

    render() {
        if (!this.container || !this.metrics) return;

        const html = `
            <div class="kpi-scorecard">
                ${this.metrics.map(metric => this.renderKPI(metric)).join('')}
            </div>
        `;

        this.container.innerHTML = html;
    }

    renderKPI(metric) {
        const trendClass = this.getTrendClass(metric.trend);
        const trendIcon = this.getTrendIcon(metric.trend);

        return `
            <div class="kpi-item">
                <div class="kpi-icon">${metric.icon}</div>
                <div class="kpi-details">
                    <div class="kpi-value">${this.formatValue(metric.value, metric.format)}</div>
                    <div class="kpi-label">${metric.label}</div>
                    ${metric.trend ? `
                        <div class="kpi-trend ${trendClass}">
                            <span class="trend-icon">${trendIcon}</span>
                            <span class="trend-value">${metric.trend}</span>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    formatValue(value, format) {
        if (!format) return value;

        switch (format) {
            case 'number':
                return value.toLocaleString();
            case 'percent':
                return `${value}%`;
            case 'currency':
                return `$${value.toLocaleString()}`;
            default:
                return value;
        }
    }

    getTrendClass(trend) {
        if (!trend) return '';
        return trend.startsWith('+') || trend.startsWith('↑') ? 'trend-up' : 'trend-down';
    }

    getTrendIcon(trend) {
        if (!trend) return '';
        return trend.startsWith('+') || trend.startsWith('↑') ? '↑' : '↓';
    }
}

// ============================================================================
// Reconciliation Widget Component
// ============================================================================

class ReconciliationWidget {
    constructor(containerId, validationData) {
        this.container = document.getElementById(containerId);
        this.data = validationData;
        this.render();
    }

    render() {
        if (!this.container || !this.data) return;

        const html = `
            <div class="reconciliation-widget">
                <div class="widget-header">
                    <h3 class="widget-title">Validation Status</h3>
                    <span class="validation-badge ${this.data.status}">
                        ${this.getStatusIcon(this.data.status)} ${this.data.status.toUpperCase()}
                    </span>
                </div>
                <div class="widget-body">
                    ${this.renderChecks()}
                </div>
                ${this.data.errors ? this.renderErrors() : ''}
            </div>
        `;

        this.container.innerHTML = html;
    }

    renderChecks() {
        if (!this.data.checks) return '';

        return `
            <div class="validation-checks">
                ${this.data.checks.map(check => `
                    <div class="check-item status-${check.status}">
                        <span class="check-icon">${this.getCheckIcon(check.status)}</span>
                        <span class="check-label">${check.label}</span>
                        ${check.message ? `<span class="check-message">${check.message}</span>` : ''}
                    </div>
                `).join('')}
            </div>
        `;
    }

    renderErrors() {
        return `
            <div class="validation-errors">
                <h4 class="errors-title">Errors (${this.data.errors.length})</h4>
                ${this.data.errors.map(error => `
                    <div class="error-item">
                        <span class="error-code">${error.code}</span>
                        <span class="error-message">${error.message}</span>
                    </div>
                `).join('')}
            </div>
        `;
    }

    getStatusIcon(status) {
        const icons = {
            'valid': '✅',
            'warning': '⚠️',
            'error': '❌',
            'pending': '⏳'
        };
        return icons[status] || '❓';
    }

    getCheckIcon(status) {
        const icons = {
            'pass': '✅',
            'fail': '❌',
            'warning': '⚠️',
            'skip': '⊘'
        };
        return icons[status] || '❓';
    }
}

// ============================================================================
// Interactive Tooltip Component
// ============================================================================

class InteractiveTooltip {
    constructor() {
        this.tooltip = null;
        this.init();
    }

    init() {
        // Create tooltip element
        this.tooltip = document.createElement('div');
        this.tooltip.className = 'cortex-tooltip';
        this.tooltip.style.display = 'none';
        document.body.appendChild(this.tooltip);

        // Attach to all elements with data-tooltip attribute
        this.attachToElements();
    }

    attachToElements() {
        document.querySelectorAll('[data-tooltip]').forEach(element => {
            element.addEventListener('mouseenter', (e) => this.show(e));
            element.addEventListener('mouseleave', () => this.hide());
            element.addEventListener('mousemove', (e) => this.position(e));
        });
    }

    show(event) {
        const content = event.target.getAttribute('data-tooltip');
        if (!content) return;

        this.tooltip.innerHTML = content;
        this.tooltip.style.display = 'block';
        this.position(event);
    }

    hide() {
        this.tooltip.style.display = 'none';
    }

    position(event) {
        const x = event.clientX + 10;
        const y = event.clientY + 10;

        this.tooltip.style.left = `${x}px`;
        this.tooltip.style.top = `${y}px`;
    }
}

// ============================================================================
// Modal Component
// ============================================================================

class Modal {
    constructor(id, options = {}) {
        this.id = id;
        this.options = {
            closeOnEscape: true,
            closeOnBackdrop: true,
            ...options
        };
        this.modal = null;
        this.create();
    }

    create() {
        const html = `
            <div id="${this.id}" class="cortex-modal" style="display: none;">
                <div class="modal-backdrop"></div>
                <div class="modal-container">
                    <div class="modal-header">
                        <h3 class="modal-title">${this.options.title || ''}</h3>
                        <button class="modal-close" onclick="document.getElementById('${this.id}').style.display='none'">×</button>
                    </div>
                    <div class="modal-body">
                        ${this.options.content || ''}
                    </div>
                    ${this.options.footer ? `
                        <div class="modal-footer">
                            ${this.options.footer}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;

        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        this.modal = tempDiv.firstElementChild;
        document.body.appendChild(this.modal);

        this.attachEventListeners();
    }

    attachEventListeners() {
        if (this.options.closeOnEscape) {
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.modal.style.display !== 'none') {
                    this.close();
                }
            });
        }

        if (this.options.closeOnBackdrop) {
            this.modal.querySelector('.modal-backdrop').addEventListener('click', () => {
                this.close();
            });
        }
    }

    open() {
        this.modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }

    close() {
        this.modal.style.display = 'none';
        document.body.style.overflow = '';
    }

    setContent(content) {
        this.modal.querySelector('.modal-body').innerHTML = content;
    }

    setTitle(title) {
        this.modal.querySelector('.modal-title').textContent = title;
    }
}

// ============================================================================
// Tab System Component
// ============================================================================

class TabSystem {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.init();
    }

    init() {
        const tabButtons = this.container.querySelectorAll('.tab-button');
        const tabContents = this.container.querySelectorAll('.tab-content');

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const targetTab = button.getAttribute('data-tab');

                // Remove active class from all buttons and contents
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabContents.forEach(content => content.classList.remove('active'));

                // Add active class to clicked button and target content
                button.classList.add('active');
                const targetContent = this.container.querySelector(`#${targetTab}`);
                if (targetContent) {
                    targetContent.classList.add('active');
                }
            });
        });
    }
}

// ============================================================================
// Export Components
// ============================================================================

// Initialize global components
window.CortexComponents = {
    NarrativePanel,
    KPIScorecard,
    ReconciliationWidget,
    InteractiveTooltip,
    Modal,
    TabSystem
};

// Auto-initialize tooltip system
document.addEventListener('DOMContentLoaded', () => {
    new InteractiveTooltip();
});
