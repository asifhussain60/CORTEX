/**
 * Tech Stack Tab Component
 * 
 * Renders technology stack view with categorized tables and status indicators.
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Source-Available (Use Allowed, No Contributions)
 */

/**
 * Render tech stack tab
 * @param {Object} data - Dashboard data containing tech stack information
 */
export function renderTechStack(data) {
    const container = document.getElementById('tech-stack-container');
    if (!container) {
        console.error('Tech stack container not found');
        return;
    }
    
    const techStack = data.techStack || {};
    const summary = techStack.summary || {};
    
    // Build HTML
    container.innerHTML = `
        <div class="view-header">
            <h2>🛠️ Technology Stack</h2>
            <div class="header-actions">
                <button class="btn-secondary" onclick="exportTechStack()">Export CSV</button>
            </div>
        </div>

        <!-- Summary Cards -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
            <div class="glass-card" style="text-align: center; padding: 1.5rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📦</div>
                <h3 style="font-size: 2rem; margin-bottom: 0.5rem; color: var(--accent-primary);">
                    ${summary.total_technologies || 0}
                </h3>
                <p style="color: var(--text-secondary);">Total Technologies</p>
            </div>
            
            <div class="glass-card" style="text-align: center; padding: 1.5rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">✅</div>
                <h3 style="font-size: 2rem; margin-bottom: 0.5rem; color: var(--success);">
                    ${summary.current_count || 0}
                </h3>
                <p style="color: var(--text-secondary);">Up to Date</p>
            </div>
            
            <div class="glass-card" style="text-align: center; padding: 1.5rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚠️</div>
                <h3 style="font-size: 2rem; margin-bottom: 0.5rem; color: var(--warning);">
                    ${summary.outdated_count || 0}
                </h3>
                <p style="color: var(--text-secondary);">Needs Update</p>
            </div>
            
            <div class="glass-card" style="text-align: center; padding: 1.5rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">❌</div>
                <h3 style="font-size: 2rem; margin-bottom: 0.5rem; color: var(--danger);">
                    ${summary.deprecated_count || 0}
                </h3>
                <p style="color: var(--text-secondary);">Deprecated</p>
            </div>
        </div>

        <!-- Technology Categories -->
        <div style="display: grid; gap: 2rem;">
            ${renderTechCategory('Frontend', '🎨', techStack.frontend || [])}
            ${renderTechCategory('Backend', '⚙️', techStack.backend || [])}
            ${renderTechCategory('Database', '💾', techStack.database || [])}
            ${renderTechCategory('DevOps', '🚀', techStack.devops || [])}
        </div>
    `;
}

/**
 * Render a technology category table
 * @param {string} categoryName - Category display name
 * @param {string} icon - Category icon
 * @param {Array} technologies - Array of technology objects
 * @returns {string} HTML string
 */
function renderTechCategory(categoryName, icon, technologies) {
    if (!technologies || technologies.length === 0) {
        return '';
    }
    
    return `
        <div class="glass-card">
            <h3 style="margin-bottom: 1.5rem;">${icon} ${categoryName}</h3>
            <div style="overflow-x: auto;">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="border-bottom: 1px solid var(--glass-border);">
                            <th style="padding: 1rem; text-align: left; color: var(--text-secondary); font-weight: 600;">Technology</th>
                            <th style="padding: 1rem; text-align: left; color: var(--text-secondary); font-weight: 600;">Current Version</th>
                            <th style="padding: 1rem; text-align: left; color: var(--text-secondary); font-weight: 600;">Latest Version</th>
                            <th style="padding: 1rem; text-align: left; color: var(--text-secondary); font-weight: 600;">Status</th>
                            <th style="padding: 1rem; text-align: left; color: var(--text-secondary); font-weight: 600;">CVEs</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${technologies.map(tech => renderTechRow(tech)).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

/**
 * Render a single technology row
 * @param {Object} tech - Technology object
 * @returns {string} HTML string
 */
function renderTechRow(tech) {
    const statusConfig = {
        current: { icon: '✅', label: 'Current', color: 'var(--success)' },
        outdated: { icon: '⚠️', label: 'Outdated', color: 'var(--warning)' },
        deprecated: { icon: '❌', label: 'Deprecated', color: 'var(--danger)' }
    };
    
    const status = statusConfig[tech.status] || statusConfig.current;
    const cveCount = tech.cve_count || 0;
    
    return `
        <tr style="border-bottom: 1px solid var(--glass-border);">
            <td style="padding: 1rem;">
                <strong>${tech.name || 'Unknown'}</strong>
            </td>
            <td style="padding: 1rem; color: var(--text-secondary);">
                ${tech.version || 'N/A'}
            </td>
            <td style="padding: 1rem; color: var(--text-secondary);">
                ${tech.latest || 'N/A'}
            </td>
            <td style="padding: 1rem;">
                <span style="
                    padding: 0.25rem 0.75rem;
                    border-radius: 12px;
                    font-size: 0.875rem;
                    font-weight: 600;
                    background: ${status.color}22;
                    color: ${status.color};
                ">
                    ${status.icon} ${status.label}
                </span>
            </td>
            <td style="padding: 1rem;">
                ${cveCount > 0 
                    ? `<span style="
                        padding: 0.25rem 0.75rem;
                        border-radius: 12px;
                        font-size: 0.875rem;
                        font-weight: 600;
                        background: var(--danger)22;
                        color: var(--danger);
                    ">${cveCount} CVEs</span>`
                    : `<span style="
                        padding: 0.25rem 0.75rem;
                        border-radius: 12px;
                        font-size: 0.875rem;
                        font-weight: 600;
                        background: var(--success)22;
                        color: var(--success);
                    ">None</span>`
                }
            </td>
        </tr>
    `;
}

/**
 * Export tech stack to CSV (placeholder)
 */
window.exportTechStack = function() {
    console.log('Export tech stack to CSV');
    // TODO: Implement CSV export
    alert('CSV export functionality coming soon!');
};
