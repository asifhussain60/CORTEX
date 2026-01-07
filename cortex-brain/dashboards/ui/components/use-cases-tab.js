/**
 * Use Cases Tab Component
 * 
 * Renders use cases analysis with role matrix, domain sections, and business value charts.
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Source-Available (Use Allowed, No Contributions)
 */

/**
 * Render Use Cases tab
 * @param {Object} data - Use cases data
 */
export function renderUseCases(data) {
    const container = document.getElementById('use-cases-container');
    if (!container) {
        console.error('Use cases container not found');
        return;
    }

    const useCases = data.use_cases || [];
    const roles = data.roles || [];
    const domains = data.domains || [];
    const counts = data.counts || {};
    const metadata = data.metadata || {};

    if (useCases.length === 0) {
        container.innerHTML = `
            <div class="glass-card" style="text-align: center; padding: 3rem;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">🎯</div>
                <h2 style="color: var(--text-secondary);">No Use Cases Found</h2>
                <p style="color: var(--text-tertiary);">
                    Use cases will appear here once the repository is analyzed.
                </p>
            </div>
        `;
        return;
    }

    container.innerHTML = `
        <!-- Summary Stats -->
        <div class="glass-card" style="margin-bottom: 2rem;">
            <h2 style="font-size: 1.5rem; color: var(--accent-primary); margin-bottom: 1.5rem;">
                🎯 Use Cases Overview
            </h2>
            <div class="metrics-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                ${renderSummaryStats(counts, metadata)}
            </div>
        </div>

        <!-- Role Matrix -->
        <div class="glass-card" style="margin-bottom: 2rem;">
            <h2 style="font-size: 1.5rem; color: var(--accent-primary); margin-bottom: 1.5rem;">
                👥 Role Capabilities Matrix
            </h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem;">
                ${renderRoleMatrix(roles, useCases)}
            </div>
        </div>

        <!-- Use Cases by Domain -->
        <div class="glass-card" style="margin-bottom: 2rem;">
            <h2 style="font-size: 1.5rem; color: var(--accent-primary); margin-bottom: 1.5rem;">
                🏢 Use Cases by Business Domain
            </h2>
            ${renderDomainSections(domains, useCases)}
        </div>

        <!-- Business Value Distribution -->
        <div class="glass-card">
            <h2 style="font-size: 1.5rem; color: var(--accent-primary); margin-bottom: 1.5rem;">
                💎 Business Value Distribution
            </h2>
            ${renderBusinessValueChart(useCases)}
        </div>
    `;
}

/**
 * Render summary statistics
 */
function renderSummaryStats(counts, metadata) {
    const stats = [
        { icon: '📋', label: 'Total Use Cases', value: counts.total || 0, color: 'var(--accent-primary)' },
        { icon: '👥', label: 'User Roles', value: Object.keys(counts.by_role || {}).length, color: 'var(--success)' },
        { icon: '🏢', label: 'Business Domains', value: Object.keys(counts.by_domain || {}).length, color: 'var(--warning)' },
        { icon: '🔥', label: 'High Value', value: counts.by_complexity?.high || 0, color: 'var(--danger)' }
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
 * Render role matrix
 */
function renderRoleMatrix(roles, useCases) {
    const roleIcons = {
        'Admin': '👑',
        'Manager': '👔',
        'End User': '👤',
        'API Consumer': '🔌'
    };

    return roles.map(role => {
        const roleUseCases = useCases.filter(uc => uc.target_role === role);
        const icon = roleIcons[role] || '👤';

        return `
            <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(255, 255, 255, 0.1);">
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                    <span style="font-size: 2rem;">${icon}</span>
                    <h3 style="font-size: 1.25rem; color: var(--text-primary); margin: 0;">${role}</h3>
                </div>
                <div style="color: var(--text-secondary); margin-bottom: 1rem;">
                    ${roleUseCases.length} use case${roleUseCases.length !== 1 ? 's' : ''}
                </div>
                <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                    ${roleUseCases.slice(0, 5).map(uc => `
                        <div style="background: rgba(255, 255, 255, 0.03); padding: 0.75rem; border-radius: 8px; border-left: 3px solid ${getBusinessValueColor(uc.business_value)};">
                            <div style="font-size: 0.875rem; color: var(--text-primary); margin-bottom: 0.25rem;">
                                ${uc.title}
                            </div>
                            <div style="display: flex; gap: 0.5rem; align-items: center;">
                                <span style="font-size: 0.75rem; padding: 0.25rem 0.5rem; border-radius: 4px; background: ${getBusinessValueColor(uc.business_value)}20; color: ${getBusinessValueColor(uc.business_value)};">
                                    ${uc.business_value.toUpperCase()}
                                </span>
                                <span style="font-size: 0.75rem; color: var(--text-tertiary);">
                                    ${Math.round(uc.confidence * 100)}% confidence
                                </span>
                            </div>
                        </div>
                    `).join('')}
                    ${roleUseCases.length > 5 ? `
                        <div style="font-size: 0.875rem; color: var(--text-tertiary); text-align: center; padding: 0.5rem;">
                            +${roleUseCases.length - 5} more
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Render domain sections
 */
function renderDomainSections(domains, useCases) {
    const domainIcons = {
        'Security': '🔒',
        'E-Commerce': '🛒',
        'Reporting': '📊',
        'User Management': '👥'
    };

    return domains.map(domain => {
        const domainUseCases = useCases.filter(uc => uc.domain === domain);
        const icon = domainIcons[domain] || '📦';

        return `
            <div style="margin-bottom: 2rem; padding-bottom: 2rem; border-bottom: 1px solid rgba(255, 255, 255, 0.1);">
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                    <span style="font-size: 1.5rem;">${icon}</span>
                    <h3 style="font-size: 1.25rem; color: var(--text-primary); margin: 0;">${domain}</h3>
                    <span style="font-size: 0.875rem; color: var(--text-secondary); margin-left: auto;">
                        ${domainUseCases.length} use case${domainUseCases.length !== 1 ? 's' : ''}
                    </span>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem;">
                    ${domainUseCases.map(uc => renderUseCaseCard(uc)).join('')}
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Render individual use case card
 */
function renderUseCaseCard(uc) {
    return `
        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(255, 255, 255, 0.1);">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.75rem;">
                <div style="font-size: 0.75rem; color: var(--text-tertiary);">${uc.id}</div>
                <span style="font-size: 0.75rem; padding: 0.25rem 0.5rem; border-radius: 4px; background: ${getComplexityColor(uc.complexity)}20; color: ${getComplexityColor(uc.complexity)};">
                    ${uc.complexity.toUpperCase()}
                </span>
            </div>
            <h4 style="font-size: 1rem; color: var(--text-primary); margin-bottom: 0.5rem;">
                ${uc.title}
            </h4>
            <p style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 1rem; line-height: 1.5;">
                ${uc.description}
            </p>
            <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem;">
                <span style="font-size: 0.75rem; padding: 0.25rem 0.5rem; border-radius: 4px; background: ${getBusinessValueColor(uc.business_value)}20; color: ${getBusinessValueColor(uc.business_value)};">
                    💎 ${uc.business_value.toUpperCase()}
                </span>
                <span style="font-size: 0.75rem; padding: 0.25rem 0.5rem; border-radius: 4px; background: rgba(255, 255, 255, 0.1); color: var(--text-secondary);">
                    ${uc.target_role}
                </span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="flex: 1; height: 4px; background: rgba(255, 255, 255, 0.1); border-radius: 2px; overflow: hidden;">
                    <div style="height: 100%; width: ${uc.confidence * 100}%; background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary)); border-radius: 2px;"></div>
                </div>
                <span style="font-size: 0.75rem; color: var(--text-tertiary);">
                    ${Math.round(uc.confidence * 100)}%
                </span>
            </div>
        </div>
    `;
}

/**
 * Render business value distribution chart
 */
function renderBusinessValueChart(useCases) {
    const distribution = useCases.reduce((acc, uc) => {
        acc[uc.business_value] = (acc[uc.business_value] || 0) + 1;
        return acc;
    }, {});

    const total = useCases.length;
    const values = ['critical', 'high', 'medium', 'low'];
    
    return `
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1.5rem;">
            ${values.map(value => {
                const count = distribution[value] || 0;
                const percentage = total > 0 ? Math.round((count / total) * 100) : 0;
                const color = getBusinessValueColor(value);
                
                return `
                    <div style="text-align: center;">
                        <div style="width: 120px; height: 120px; margin: 0 auto 1rem; position: relative;">
                            <svg viewBox="0 0 36 36" style="transform: rotate(-90deg);">
                                <circle cx="18" cy="18" r="16" fill="none" stroke="rgba(255, 255, 255, 0.1)" stroke-width="3"></circle>
                                <circle cx="18" cy="18" r="16" fill="none" stroke="${color}" stroke-width="3" 
                                    stroke-dasharray="${percentage}, 100" stroke-linecap="round"></circle>
                            </svg>
                            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 1.5rem; font-weight: 600; color: ${color};">
                                ${percentage}%
                            </div>
                        </div>
                        <div style="font-size: 1rem; color: var(--text-primary); margin-bottom: 0.25rem; text-transform: capitalize;">
                            ${value}
                        </div>
                        <div style="font-size: 0.875rem; color: var(--text-secondary);">
                            ${count} use case${count !== 1 ? 's' : ''}
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
}

/**
 * Get color for business value
 */
function getBusinessValueColor(value) {
    const colors = {
        'critical': '#ef4444',
        'high': '#f59e0b',
        'medium': '#3b82f6',
        'low': '#6b7280'
    };
    return colors[value.toLowerCase()] || colors.low;
}

/**
 * Get color for complexity
 */
function getComplexityColor(complexity) {
    const colors = {
        'high': '#ef4444',
        'medium': '#f59e0b',
        'low': '#10b981'
    };
    return colors[complexity.toLowerCase()] || colors.medium;
}
