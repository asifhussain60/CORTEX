/**
 * CORTEX Lens - Reusable UI Components
 */

class Components {
    /**
     * Render a metric card
     */
    static renderMetricCard(data) {
        return `
            <div class="metric-card">
                <div class="metric-card__icon">${data.icon || '📊'}</div>
                <div class="metric-card__content">
                    <div class="metric-card__label">${data.label}</div>
                    <div class="metric-card__value">${data.value}</div>
                    ${data.change ? `<div class="metric-card__change ${data.change > 0 ? 'positive' : 'negative'}">${data.change > 0 ? '↑' : '↓'} ${Math.abs(data.change)}%</div>` : ''}
                </div>
            </div>
        `;
    }

    /**
     * Render a use case card
     */
    static renderUseCaseCard(useCase) {
        const priorityClass = useCase.priority ? useCase.priority.toLowerCase() : 'medium';
        const categoryIcon = this.getCategoryIcon(useCase.category);
        
        return `
            <div class="use-case-card" data-id="${useCase.id}">
                <div class="use-case-card__header">
                    <span class="use-case-card__icon">${categoryIcon}</span>
                    <span class="badge badge--${priorityClass}">${useCase.priority || 'Medium'}</span>
                </div>
                <h3 class="use-case-card__title">${useCase.title}</h3>
                <p class="use-case-card__description">${useCase.description}</p>
                ${useCase.impacted_modules ? `
                    <div class="use-case-card__modules">
                        ${useCase.impacted_modules.map(m => `<span class="module-tag">${m}</span>`).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }

    /**
     * Get icon for use case category
     */
    static getCategoryIcon(category) {
        const icons = {
            'Analysis': '🔍',
            'Management': '⚙️',
            'Testing': '🧪',
            'Security': '🔒',
            'Performance': '⚡',
            'Integration': '🔗',
            'Documentation': '📚',
            'Deployment': '🚀'
        };
        return icons[category] || '💡';
    }

    /**
     * Render health badge
     */
    static renderHealthBadge(status) {
        const statusMap = {
            'Excellent': { class: 'success', icon: '✅' },
            'Good': { class: 'success', icon: '✓' },
            'Fair': { class: 'warning', icon: '⚠️' },
            'Poor': { class: 'danger', icon: '❌' },
            'Critical': { class: 'danger', icon: '🔴' }
        };
        
        const config = statusMap[status] || statusMap['Fair'];
        return `<span class="health-badge health-badge--${config.class}">${config.icon} ${status}</span>`;
    }

    /**
     * Render progress bar
     */
    static renderProgressBar(value, max = 100, label = '') {
        const percentage = Math.round((value / max) * 100);
        const colorClass = percentage >= 80 ? 'success' : percentage >= 60 ? 'warning' : 'danger';
        
        return `
            <div class="progress-bar">
                ${label ? `<div class="progress-bar__label">${label}</div>` : ''}
                <div class="progress-bar__track">
                    <div class="progress-bar__fill progress-bar__fill--${colorClass}" style="width: ${percentage}%">
                        <span class="progress-bar__value">${percentage}%</span>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Render severity badge
     */
    static renderSeverityBadge(severity) {
        const severityMap = {
            'critical': { class: 'danger', icon: '🔴', label: 'Critical' },
            'high': { class: 'danger', icon: '❗', label: 'High' },
            'medium': { class: 'warning', icon: '⚠️', label: 'Medium' },
            'low': { class: 'info', icon: 'ℹ️', label: 'Low' },
            'info': { class: 'info', icon: 'ℹ️', label: 'Info' }
        };
        
        const config = severityMap[severity.toLowerCase()] || severityMap['info'];
        return `<span class="badge badge--${config.class}">${config.icon} ${config.label}</span>`;
    }

    /**
     * Format number with commas
     */
    static formatNumber(num) {
        if (typeof num !== 'number') return num;
        return num.toLocaleString('en-US');
    }

    /**
     * Format date
     */
    static formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric' 
        });
    }

    /**
     * Format relative time
     */
    static formatRelativeTime(dateString) {
        if (!dateString) return 'N/A';
        
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);
        
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 30) return `${diffDays}d ago`;
        
        return this.formatDate(dateString);
    }

    /**
     * Escape HTML to prevent XSS
     */
    static escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Create skeleton loader
     */
    static renderSkeleton(type = 'card') {
        if (type === 'card') {
            return `
                <div class="skeleton-card">
                    <div class="skeleton-line skeleton-line--title"></div>
                    <div class="skeleton-line skeleton-line--text"></div>
                    <div class="skeleton-line skeleton-line--text"></div>
                </div>
            `;
        }
        return '<div class="skeleton-line"></div>';
    }
}
