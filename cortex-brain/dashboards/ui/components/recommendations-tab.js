/**
 * Recommendations Tab Component
 * 
 * Renders actionable recommendations with priority matrix, ROI scoring, and filtering.
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Source-Available (Use Allowed, No Contributions)
 */

/**
 * Render Recommendations tab
 * @param {Object} data - Recommendations data
 */
export function renderRecommendations(data) {
    const container = document.getElementById('recommendations-container');
    if (!container) {
        console.error('Recommendations container not found');
        return;
    }

    const recommendations = data.recommendations || [];
    const topRecommendations = data.top_recommendations || [];
    const counts = data.counts || {};

    if (recommendations.length === 0) {
        container.innerHTML = `
            <div class="glass-card" style="text-align: center; padding: 3rem;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">💡</div>
                <h2 style="color: var(--text-secondary);">No Recommendations Available</h2>
                <p style="color: var(--text-tertiary);">
                    Recommendations will appear here once the repository is analyzed.
                </p>
            </div>
        `;
        return;
    }

    container.innerHTML = `
        <!-- Summary Stats -->
        <div class="glass-card" style="margin-bottom: 2rem;">
            <h2 style="font-size: 1.5rem; color: var(--accent-primary); margin-bottom: 1.5rem;">
                💡 Recommendations Overview
            </h2>
            <div class="metrics-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                ${renderSummaryStats(counts)}
            </div>
        </div>

        <!-- Priority Matrix -->
        <div class="glass-card" style="margin-bottom: 2rem;">
            <h2 style="font-size: 1.5rem; color: var(--accent-primary); margin-bottom: 1.5rem;">
                🎯 Priority Matrix
            </h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
                ${renderPriorityMatrix(recommendations, counts.by_priority)}
            </div>
        </div>

        <!-- Top 10 Recommendations by ROI -->
        <div class="glass-card" style="margin-bottom: 2rem;">
            <h2 style="font-size: 1.5rem; color: var(--accent-primary); margin-bottom: 1.5rem;">
                🏆 Top 10 Recommendations by ROI
            </h2>
            <div style="display: flex; flex-direction: column; gap: 1rem;">
                ${renderTopRecommendations(topRecommendations)}
            </div>
        </div>

        <!-- Category Breakdown -->
        <div class="glass-card">
            <h2 style="font-size: 1.5rem; color: var(--accent-primary); margin-bottom: 1.5rem;">
                📊 Category Breakdown
            </h2>
            ${renderCategoryBreakdown(recommendations, counts.by_category)}
        </div>
    `;
}

/**
 * Render summary statistics
 */
function renderSummaryStats(counts) {
    const stats = [
        { icon: '📋', label: 'Total Recommendations', value: counts.total || 0, color: 'var(--accent-primary)' },
        { icon: '🔥', label: 'Critical (P0)', value: counts.by_priority?.p0 || 0, color: '#ef4444' },
        { icon: '⚠️', label: 'Important (P1)', value: counts.by_priority?.p1 || 0, color: '#f59e0b' },
        { icon: '📌', label: 'Optional (P2+)', value: (counts.by_priority?.p2 || 0) + (counts.by_priority?.p3 || 0), color: '#6b7280' }
    ];

    return stats.map(stat => `
        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(255, 255, 255, 0.1);">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">${stat.icon}</div>
            <div style="font-size: 2rem; font-weight: 600; color: ${stat.color}; margin-bottom: 0.25rem;">
                ${stat.value}
            </div>
            <div style="font-size: 0.875rem; color: var(--text-secondary);">
                ${stat.label}
            </div>
        </div>
    `).join('');
}

/**
 * Render priority matrix
 */
function renderPriorityMatrix(recommendations, byPriority) {
    const priorities = [
        { level: 'p0', label: 'Critical', icon: '🔥', color: '#ef4444', description: 'Immediate action required' },
        { level: 'p1', label: 'Important', icon: '⚠️', color: '#f59e0b', description: 'High priority' },
        { level: 'p2', label: 'Optional', icon: '📌', color: '#3b82f6', description: 'Medium priority' },
        { level: 'p3', label: 'Deferred', icon: '⏳', color: '#6b7280', description: 'Low priority' }
    ];

    return priorities.map(priority => {
        const count = byPriority?.[priority.level] || 0;
        const items = recommendations.filter(r => r.priority === priority.level);

        return `
            <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(255, 255, 255, 0.1); border-left: 4px solid ${priority.color};">
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
                    <span style="font-size: 1.5rem;">${priority.icon}</span>
                    <div>
                        <h3 style="font-size: 1.125rem; color: ${priority.color}; margin: 0;">${priority.label}</h3>
                        <p style="font-size: 0.75rem; color: var(--text-tertiary); margin: 0;">${priority.description}</p>
                    </div>
                </div>
                <div style="font-size: 2rem; font-weight: 600; color: ${priority.color}; margin-bottom: 1rem;">
                    ${count}
                </div>
                ${items.slice(0, 3).map(item => `
                    <div style="background: rgba(255, 255, 255, 0.03); padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem;">
                        <div style="font-size: 0.875rem; color: var(--text-primary); margin-bottom: 0.25rem;">
                            ${item.title}
                        </div>
                        <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                            <span style="font-size: 0.75rem; padding: 0.25rem 0.5rem; border-radius: 4px; background: ${getCategoryColor(item.category)}20; color: ${getCategoryColor(item.category)};">
                                ${formatCategory(item.category)}
                            </span>
                            <span style="font-size: 0.75rem; color: var(--text-tertiary);">
                                ROI: ${item.roi_score.toFixed(1)}
                            </span>
                        </div>
                    </div>
                `).join('')}
                ${items.length > 3 ? `
                    <div style="font-size: 0.875rem; color: var(--text-tertiary); text-align: center; padding: 0.5rem;">
                        +${items.length - 3} more
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');
}

/**
 * Render top recommendations by ROI
 */
function renderTopRecommendations(topRecommendations) {
    return topRecommendations.map((rec, index) => `
        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(255, 255, 255, 0.1); border-left: 4px solid ${getPriorityColor(rec.priority)};">
            <div style="display: flex; align-items: start; gap: 1rem; margin-bottom: 1rem;">
                <div style="font-size: 1.5rem; font-weight: 600; color: var(--accent-primary); min-width: 2rem;">
                    #${index + 1}
                </div>
                <div style="flex: 1;">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                        <h3 style="font-size: 1.125rem; color: var(--text-primary); margin: 0;">
                            ${rec.title}
                        </h3>
                        <div style="font-size: 1.25rem; font-weight: 600; color: var(--accent-primary); margin-left: 1rem;">
                            ${rec.roi_score.toFixed(1)}
                        </div>
                    </div>
                    <p style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 1rem; line-height: 1.5;">
                        ${rec.description}
                    </p>
                    <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                        <span style="font-size: 0.75rem; padding: 0.25rem 0.5rem; border-radius: 4px; background: ${getPriorityColor(rec.priority)}20; color: ${getPriorityColor(rec.priority)};">
                            ${(rec.priority || 'P2').toUpperCase()}
                        </span>
                        <span style="font-size: 0.75rem; padding: 0.25rem 0.5rem; border-radius: 4px; background: ${getCategoryColor(rec.category)}20; color: ${getCategoryColor(rec.category)};">
                            ${formatCategory(rec.category)}
                        </span>
                        <span style="font-size: 0.75rem; padding: 0.25rem 0.5rem; border-radius: 4px; background: rgba(255, 255, 255, 0.1); color: var(--text-secondary);">
                            Impact: ${rec.impact}
                        </span>
                        <span style="font-size: 0.75rem; padding: 0.25rem 0.5rem; border-radius: 4px; background: rgba(255, 255, 255, 0.1); color: var(--text-secondary);">
                            Effort: ${rec.effort}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

/**
 * Render category breakdown
 */
function renderCategoryBreakdown(recommendations, byCategory) {
    const categories = [
        { id: 'health', label: 'Health Improvements', icon: '🏥', color: '#10b981' },
        { id: 'performance', label: 'Performance', icon: '⚡', color: '#f59e0b' },
        { id: 'security', label: 'Security', icon: '🔒', color: '#ef4444' },
        { id: 'technical_debt', label: 'Technical Debt', icon: '🔧', color: '#8b5cf6' },
        { id: 'e2e_testing', label: 'E2E Testing', icon: '🧪', color: '#3b82f6' }
    ];

    const total = recommendations.length;

    return `
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem;">
            ${categories.map(category => {
                const count = byCategory?.[category.id] || 0;
                const percentage = total > 0 ? Math.round((count / total) * 100) : 0;
                const items = recommendations.filter(r => r.category === category.id);

                return `
                    <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(255, 255, 255, 0.1);">
                        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                            <span style="font-size: 1.5rem;">${category.icon}</span>
                            <div>
                                <h3 style="font-size: 1rem; color: ${category.color}; margin: 0;">${category.label}</h3>
                                <p style="font-size: 0.75rem; color: var(--text-tertiary); margin: 0;">${count} recommendations</p>
                            </div>
                        </div>
                        <div style="position: relative; height: 8px; background: rgba(255, 255, 255, 0.1); border-radius: 4px; overflow: hidden; margin-bottom: 0.5rem;">
                            <div style="position: absolute; top: 0; left: 0; height: 100%; width: ${percentage}%; background: ${category.color}; border-radius: 4px;"></div>
                        </div>
                        <div style="font-size: 0.875rem; color: var(--text-secondary); text-align: right;">
                            ${percentage}% of total
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
}

/**
 * Get color for priority level
 */
function getPriorityColor(priority) {
    const colors = {
        'p0': '#ef4444',
        'p1': '#f59e0b',
        'p2': '#3b82f6',
        'p3': '#6b7280'
    };
    // Handle undefined/null priority
    if (!priority || typeof priority !== 'string') {
        return colors.p2; // Default to P2 color
    }
    return colors[priority.toLowerCase()] || colors.p2;
}

/**
 * Get color for category
 */
function getCategoryColor(category) {
    const colors = {
        'health': '#10b981',
        'performance': '#f59e0b',
        'security': '#ef4444',
        'technical_debt': '#8b5cf6',
        'e2e_testing': '#3b82f6'
    };
    return colors[category] || '#6b7280';
}

/**
 * Format category name
 */
function formatCategory(category) {
    return category
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}
