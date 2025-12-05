/**
 * Tech Stack Tab Component
 * 
 * Renders technology stack view with categorized tables and status indicators.
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Source-Available (Use Allowed, No Contributions)
 */

import { showPanelSpinner } from '../shared-utils.js';

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
    
    // Show loading spinner
    showPanelSpinner(container, 'Loading technology stack...');
    
    // Render after brief delay to show spinner
    setTimeout(() => {
        const techStack = data.techStack || {};
        const summary = techStack.summary || {};
        
        // Calculate actual status counts from data
        const statusCounts = calculateStatusCounts(techStack);
        
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
                    ${statusCounts.total || 0}
                </h3>
                <p style="color: var(--text-secondary);">Total Technologies</p>
            </div>
            
            <div class="glass-card" style="text-align: center; padding: 1.5rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">✅</div>
                <h3 style="font-size: 2rem; margin-bottom: 0.5rem; color: var(--success);">
                    ${statusCounts.current || 0}
                </h3>
                <p style="color: var(--text-secondary);">Up to Date</p>
            </div>
            
            <div class="glass-card" style="text-align: center; padding: 1.5rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚠️</div>
                <h3 style="font-size: 2rem; margin-bottom: 0.5rem; color: var(--warning);">
                    ${statusCounts.outdated || 0}
                </h3>
                <p style="color: var(--text-secondary);">Needs Update</p>
            </div>
            
            <div class="glass-card" style="text-align: center; padding: 1.5rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">❌</div>
                <h3 style="font-size: 2rem; margin-bottom: 0.5rem; color: var(--danger);">
                    ${statusCounts.deprecated || 0}
                </h3>
                <p style="color: var(--text-secondary);">Deprecated</p>
            </div>
        </div>

        <!-- How to Read Description -->
        <div class="glass-card" style="margin-bottom: 2rem; background: linear-gradient(135deg, var(--glass-light) 0%, var(--background-secondary) 100%);">
            <h3 style="margin-bottom: 1rem;">📋 Technology Stack Status</h3>
            <p style="color: var(--text-secondary); line-height: 1.6; margin-bottom: 1rem;">
                This view shows all technologies detected in your project. Each technology is color-coded by status: 
                <strong style="color: var(--success);">✅ Current</strong> versions are up-to-date, 
                <strong style="color: var(--warning);">⚠️ Outdated</strong> versions should be upgraded, and 
                <strong style="color: var(--danger);">❌ Deprecated</strong> technologies require immediate attention.
                <strong>Hover over each technology card</strong> to see detailed version information, security vulnerabilities, and upgrade recommendations.
            </p>
        </div>

        <!-- Description Panel -->
        <div style="
            background: var(--glass-light);
            border: 1px solid var(--glass-border);
            border-left: 4px solid var(--accent-primary);
            border-radius: 12px;
            padding: 1.5rem;
            margin-top: 2rem;
        ">
            <div style="display: flex; align-items: start; gap: 1rem;">
                <div style="
                    font-size: 2rem;
                    line-height: 1;
                    opacity: 0.8;
                ">💡</div>
                <div style="flex: 1;">
                    <div style="font-size: 0.95rem; color: var(--text-secondary); line-height: 1.6;">
                        Technology status indicators show maintenance state and security posture.
                        <span style="color: var(--success); font-weight: 600;">✅ Current</span> means running the latest stable release (no action needed).
                        <span style="color: var(--warning); font-weight: 600;">⚠️ Outdated</span> indicates a newer version is available (update recommended for features and fixes).
                        <span style="color: var(--danger); font-weight: 600;">❌ Deprecated</span> means end-of-life reached (migration required due to security risks).
                        <strong>Hover over any technology card</strong> for detailed version information, CVE counts, and specific update recommendations.
                    </div>
                </div>
            </div>
        </div>

        <!-- Technology Categories -->
        <div style="display: grid; gap: 2rem; margin-top: 2rem;">
            ${renderTechCategory('Frontend', '🎨', techStack.frontend || [])}
            ${renderTechCategory('Backend', '⚙️', techStack.backend || [])}
            ${renderTechCategory('Database', '💾', techStack.database || [])}
            ${renderTechCategory('DevOps', '🚀', techStack.devops || [])}
        </div>
    `;
    }, 250);
}

/**
 * Calculate status counts from tech stack data
 * @param {Object} techStack - Tech stack data
 * @returns {Object} Status counts
 */
function calculateStatusCounts(techStack) {
    const counts = { total: 0, current: 0, outdated: 0, deprecated: 0 };
    
    ['frontend', 'backend', 'database', 'devops'].forEach(category => {
        const techs = techStack[category] || [];
        techs.forEach(tech => {
            counts.total++;
            const status = tech.status || 'current';
            if (counts[status] !== undefined) {
                counts[status]++;
            }
        });
    });
    
    return counts;
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
            <div style="display: grid; gap: 1.5rem;">
                ${technologies.map(tech => renderTechCard(tech)).join('')}
            </div>
        </div>
    `;
}

/**
 * Build technology tooltip explanation based on status
 * @param {Object} tech - Technology object
 * @returns {string} Explanation text
 */
function buildTechTooltipExplanation(tech) {
    const status = tech.status || 'current';
    const version = tech.version || 'N/A';
    const latest = tech.latest || 'unknown';
    
    if (status === 'current') {
        return `${tech.name} ${version} is the latest stable release. No updates required at this time.`;
    } else if (status === 'outdated') {
        if (latest !== 'unknown' && latest !== version) {
            return `${tech.name} ${version} has a newer version available (${latest}). Consider updating to access latest features and security patches.`;
        }
        return `${tech.name} ${version} is outdated. A newer version is available with improvements and bug fixes.`;
    } else if (status === 'deprecated') {
        return `${tech.name} ${version} has reached end-of-life and is no longer supported. Plan migration to a supported alternative to avoid security vulnerabilities.`;
    }
    
    return `${tech.name} ${version} - Status information unavailable.`;
}

/**
 * Render a technology card with hierarchical details
 * @param {Object} tech - Technology object
 * @returns {string} HTML string
 */
function renderTechCard(tech) {
    const statusConfig = {
        current: { icon: '✅', label: 'Current', color: 'var(--success)' },
        outdated: { icon: '⚠️', label: 'Outdated', color: 'var(--warning)' },
        deprecated: { icon: '❌', label: 'Deprecated', color: 'var(--danger)' }
    };
    
    const status = statusConfig[tech.status] || statusConfig.current;
    const cveCount = tech.cve_count || 0;
    const metadata = tech.metadata || {};
    const hasMetadata = metadata.solutions || metadata.projects || metadata.frameworks;
    
    // Generate unique ID for collapse functionality
    const cardId = `tech-${tech.name.replace(/[^a-zA-Z0-9]/g, '-').toLowerCase()}`;
    
    // Build tooltip explanation
    const explanation = buildTechTooltipExplanation(tech);
    
    return `
        <div 
            class="tech-card-hoverable"
            style="
                background: var(--glass-light);
                border: 1px solid var(--glass-border);
                border-radius: 12px;
                padding: 1.5rem;
                transition: all 0.3s ease;
                cursor: pointer;
            "
            onmouseover="showTechTooltip(event, ${JSON.stringify(tech.name).replace(/"/g, '&quot;')}, ${JSON.stringify(tech.version || 'N/A').replace(/"/g, '&quot;')}, ${JSON.stringify(tech.status).replace(/"/g, '&quot;')}, ${tech.cve_count || 0}, ${JSON.stringify(explanation).replace(/"/g, '&quot;')}, this)"
            onmouseout="hideTechTooltip(this)"
        >
            <!-- Header -->
            <div style="display: flex; align-items: start; justify-content: space-between; margin-bottom: 1rem;">
                <div style="flex: 1;">
                    <h4 style="margin: 0 0 0.5rem 0; font-size: 1.25rem;">${tech.name || 'Unknown'}</h4>
                    <div style="display: flex; gap: 1rem; flex-wrap: wrap; align-items: center;">
                        <span style="color: var(--text-secondary); font-size: 0.875rem;">
                            Version: <strong style="color: var(--text-primary);">${tech.version || 'N/A'}</strong>
                        </span>
                        ${tech.latest && tech.latest !== 'unknown' ? `
                            <span style="color: var(--text-secondary); font-size: 0.875rem;">
                                Latest: <strong style="color: var(--accent-primary);">${tech.latest}</strong>
                            </span>
                        ` : ''}
                    </div>
                </div>
                <div style="display: flex; gap: 0.75rem; align-items: center;">
                    <span style="
                        padding: 0.375rem 0.875rem;
                        border-radius: 12px;
                        font-size: 0.875rem;
                        font-weight: 600;
                        background: ${status.color}22;
                        color: ${status.color};
                        white-space: nowrap;
                    ">
                        ${status.icon} ${status.label}
                    </span>
                    ${cveCount > 0 ? `
                        <span style="
                            padding: 0.375rem 0.875rem;
                            border-radius: 12px;
                            font-size: 0.875rem;
                            font-weight: 600;
                            background: var(--danger)22;
                            color: var(--danger);
                            white-space: nowrap;
                        ">
                            🛡️ ${cveCount} CVEs
                        </span>
                    ` : ''}
                </div>
            </div>
            
            ${hasMetadata ? renderTechMetadata(tech, cardId) : ''}
        </div>
    `;
}

/**
 * Render technology metadata (solutions, projects, packages)
 * @param {Object} tech - Technology object
 * @param {string} cardId - Unique card ID
 * @returns {string} HTML string
 */
function renderTechMetadata(tech, cardId) {
    const metadata = tech.metadata || {};
    const solutions = metadata.solutions || [];
    const projects = metadata.projects || [];
    const frameworks = metadata.frameworks || [];
    
    let html = '<div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--glass-border);">';
    
    // Database-specific metadata (server, database, user, evidence)
    if (metadata.server || metadata.database || metadata.user || metadata.evidence) {
        html += '<div style="background: var(--background-secondary); border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">';
        html += '<h5 style="margin: 0 0 0.75rem 0; font-size: 0.875rem; color: var(--text-secondary);">🔗 Connection Details</h5>';
        html += '<div style="display: grid; gap: 0.5rem; font-size: 0.875rem;">';
        
        if (metadata.server) {
            html += `
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="color: var(--text-secondary); min-width: 100px;">Server:</span>
                    <strong style="color: var(--accent-primary); font-family: monospace;">${metadata.server}</strong>
                </div>
            `;
        }
        
        if (metadata.database && metadata.database !== metadata.server) {
            html += `
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="color: var(--text-secondary); min-width: 100px;">Database:</span>
                    <strong style="color: var(--text-primary); font-family: monospace;">${metadata.database}</strong>
                </div>
            `;
        }
        
        if (metadata.user) {
            html += `
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="color: var(--text-secondary); min-width: 100px;">User:</span>
                    <strong style="color: var(--text-primary); font-family: monospace;">${metadata.user}</strong>
                </div>
            `;
        }
        
        if (metadata.source) {
            html += `
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="color: var(--text-secondary); min-width: 100px;">Source:</span>
                    <code style="background: var(--glass-border); padding: 0.125rem 0.5rem; border-radius: 4px; font-size: 0.75rem;">${metadata.source}</code>
                </div>
            `;
        }
        
        if (metadata.evidence) {
            html += `
                <div style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid var(--glass-border);">
                    <span style="color: var(--text-secondary); font-size: 0.75rem;">✓ ${metadata.evidence}</span>
                </div>
            `;
        }
        
        html += '</div></div>';
    }
    
    // Quick stats row (for non-database technologies)
    const stats = [];
    if (metadata.solution_count) stats.push(`📁 ${metadata.solution_count} Solution${metadata.solution_count > 1 ? 's' : ''}`);
    if (metadata.project_count) stats.push(`📦 ${metadata.project_count} Project${metadata.project_count > 1 ? 's' : ''}`);
    if (metadata.file_count) stats.push(`📄 ${metadata.file_count} Files`);
    if (metadata.lines_of_code) stats.push(`📊 ${metadata.lines_of_code.toLocaleString()} LOC`);
    if (metadata.package_count) stats.push(`📚 ${metadata.package_count} Packages`);
    
    if (stats.length > 0) {
        html += `
            <div style="display: flex; gap: 1.5rem; flex-wrap: wrap; margin-bottom: 1rem; font-size: 0.875rem; color: var(--text-secondary);">
                ${stats.join('<span style="color: var(--glass-border);">•</span>')}
            </div>
        `;
    }
    
    // Expandable sections
    const hasExpandableContent = solutions.length > 0 || projects.length > 0 || frameworks.length > 5;
    
    if (hasExpandableContent) {
        html += `
            <button 
                onclick="toggleTechDetails('${cardId}')"
                style="
                    background: var(--glass-light);
                    border: 1px solid var(--glass-border);
                    border-radius: 8px;
                    padding: 0.5rem 1rem;
                    color: var(--accent-primary);
                    font-size: 0.875rem;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.2s;
                "
                onmouseover="this.style.background='var(--glass-border)'"
                onmouseout="this.style.background='var(--glass-light)'"
            >
                <span id="${cardId}-toggle-icon">▶</span> Show Details
            </button>
            
            <div id="${cardId}-details" style="display: none; margin-top: 1rem;">
                ${solutions.length > 0 ? renderSolutions(solutions) : ''}
                ${projects.length > 0 ? renderProjects(projects) : ''}
                ${frameworks.length > 0 ? renderFrameworks(frameworks) : ''}
            </div>
        `;
    }
    
    html += '</div>';
    return html;
}

/**
 * Render solution details
 * @param {Array} solutions - Array of solution objects
 * @returns {string} HTML string
 */
function renderSolutions(solutions) {
    return `
        <div style="margin-top: 1rem;">
            <h5 style="margin: 0 0 0.75rem 0; font-size: 0.875rem; text-transform: uppercase; color: var(--text-secondary); letter-spacing: 0.5px;">
                Solutions
            </h5>
            ${solutions.map(sol => `
                <div style="
                    background: var(--background-secondary);
                    border-radius: 8px;
                    padding: 1rem;
                    margin-bottom: 0.75rem;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                        <strong style="color: var(--text-primary);">${sol.name}</strong>
                        <div style="display: flex; gap: 0.5rem; font-size: 0.75rem;">
                            ${sol.vs_version ? `<span style="background: var(--glass-border); padding: 0.25rem 0.5rem; border-radius: 6px;">VS ${sol.vs_version}</span>` : ''}
                            ${sol.format_version ? `<span style="background: var(--glass-border); padding: 0.25rem 0.5rem; border-radius: 6px;">Format ${sol.format_version}</span>` : ''}
                        </div>
                    </div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary);">
                        ${sol.project_count || 0} project${(sol.project_count || 0) !== 1 ? 's' : ''}
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

/**
 * Render project details
 * @param {Array} projects - Array of project objects
 * @returns {string} HTML string
 */
function renderProjects(projects) {
    return `
        <div style="margin-top: 1rem;">
            <h5 style="margin: 0 0 0.75rem 0; font-size: 0.875rem; text-transform: uppercase; color: var(--text-secondary); letter-spacing: 0.5px;">
                Projects
            </h5>
            <div style="display: grid; gap: 0.5rem;">
                ${projects.map(proj => `
                    <div style="
                        background: var(--background-secondary);
                        border-radius: 8px;
                        padding: 0.75rem 1rem;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    ">
                        <div>
                            <strong style="color: var(--text-primary); font-size: 0.875rem;">${proj.name}</strong>
                            <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.25rem;">
                                ${proj.framework || 'Unknown framework'}
                            </div>
                        </div>
                        ${proj.packages ? `
                            <span style="
                                background: var(--accent-primary)22;
                                color: var(--accent-primary);
                                padding: 0.25rem 0.625rem;
                                border-radius: 6px;
                                font-size: 0.75rem;
                                font-weight: 600;
                            ">
                                ${proj.packages} pkg${proj.packages !== 1 ? 's' : ''}
                            </span>
                        ` : ''}
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

/**
 * Render framework/package list
 * @param {Array} frameworks - Array of framework strings
 * @returns {string} HTML string
 */
function renderFrameworks(frameworks) {
    // Group by category if available (look for category in parentheses)
    const categorized = {};
    const uncategorized = [];
    
    frameworks.forEach(fw => {
        const match = fw.match(/^(.+?)\s*\((.+?)\)$/);
        if (match) {
            const [, name, category] = match;
            if (!categorized[category]) categorized[category] = [];
            categorized[category].push(name.trim());
        } else {
            uncategorized.push(fw);
        }
    });
    
    let html = `
        <div style="margin-top: 1rem;">
            <h5 style="margin: 0 0 0.75rem 0; font-size: 0.875rem; text-transform: uppercase; color: var(--text-secondary); letter-spacing: 0.5px;">
                Key Packages (${frameworks.length})
            </h5>
    `;
    
    // Render categorized packages
    Object.entries(categorized).forEach(([category, items]) => {
        html += `
            <div style="margin-bottom: 1rem;">
                <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.5rem; font-weight: 600;">
                    ${category}
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                    ${items.map(item => `
                        <span style="
                            background: var(--glass-light);
                            border: 1px solid var(--glass-border);
                            padding: 0.375rem 0.75rem;
                            border-radius: 8px;
                            font-size: 0.75rem;
                            color: var(--text-primary);
                        ">${item}</span>
                    `).join('')}
                </div>
            </div>
        `;
    });
    
    // Render uncategorized (show first 10)
    if (uncategorized.length > 0) {
        const displayItems = uncategorized.slice(0, 10);
        const remaining = uncategorized.length - 10;
        
        html += `
            <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                ${displayItems.map(item => `
                    <span style="
                        background: var(--glass-light);
                        border: 1px solid var(--glass-border);
                        padding: 0.375rem 0.75rem;
                        border-radius: 8px;
                        font-size: 0.75rem;
                        color: var(--text-primary);
                    ">${item}</span>
                `).join('')}
                ${remaining > 0 ? `
                    <span style="
                        background: var(--accent-primary)22;
                        color: var(--accent-primary);
                        padding: 0.375rem 0.75rem;
                        border-radius: 8px;
                        font-size: 0.75rem;
                        font-weight: 600;
                    ">+${remaining} more</span>
                ` : ''}
            </div>
        `;
    }
    
    html += '</div>';
    return html;
}

/**
 * Build tooltip explanation for a technology
 * @param {Object} tech - Technology object
 * @returns {string} Explanation text
 */
function buildTechTooltipExplanation(tech) {
    const status = tech.status || 'current';
    const currentVersion = tech.version || 'N/A';
    const latestVersion = tech.latest || 'unknown';
    const cveCount = tech.cve_count || 0;
    
    let explanation = '';
    
    if (status === 'current') {
        explanation = `This technology is running the latest version (${currentVersion}). No immediate action required.`;
        if (cveCount > 0) {
            explanation += ` However, ${cveCount} CVE${cveCount > 1 ? 's' : ''} detected - review security findings.`;
        }
    } else if (status === 'outdated') {
        explanation = `Currently running version ${currentVersion}, but version ${latestVersion} is available. `;
        explanation += `Consider upgrading to access new features, performance improvements, and security patches.`;
        if (cveCount > 0) {
            explanation += ` ${cveCount} known CVE${cveCount > 1 ? 's' : ''} affect this version - upgrade recommended.`;
        }
    } else if (status === 'deprecated') {
        explanation = `This technology is deprecated and no longer supported. Version ${currentVersion} is running. `;
        explanation += `Immediate migration to a supported alternative is strongly recommended to maintain security and compatibility.`;
        if (cveCount > 0) {
            explanation += ` ${cveCount} critical CVE${cveCount > 1 ? 's' : ''} detected - high security risk.`;
        }
    }
    
    return explanation;
}

/**
 * Show technology tooltip on hover
 * @param {Event} event - Mouse event
 * @param {string} name - Technology name
 * @param {string} version - Current version
 * @param {string} status - Technology status
 * @param {number} cveCount - CVE count
 * @param {string} explanation - Tooltip explanation
 * @param {HTMLElement} element - Hovered element
 */
window.showTechTooltip = function(event, name, version, status, cveCount, explanation, element) {
    // Add hover effect to card
    element.style.transform = 'translateY(-4px)';
    element.style.boxShadow = '0 8px 24px rgba(0, 0, 0, 0.2)';
    
    // Status configuration
    const statusConfig = {
        current: { icon: '✅', label: 'Current', color: 'var(--success)' },
        outdated: { icon: '⚠️', label: 'Outdated', color: 'var(--warning)' },
        deprecated: { icon: '❌', label: 'Deprecated', color: 'var(--danger)' }
    };
    
    const statusInfo = statusConfig[status] || statusConfig.current;
    
    // Remove existing tooltip
    const existing = document.getElementById('tech-tooltip');
    if (existing) {
        existing.remove();
    }
    
    // Create tooltip
    const tooltip = document.createElement('div');
    tooltip.id = 'tech-tooltip';
    tooltip.style.cssText = `
        position: fixed;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.98) 0%, rgba(30, 41, 59, 0.98) 100%);
        border: 1px solid ${statusInfo.color};
        border-radius: 12px;
        padding: 1.25rem;
        max-width: 400px;
        z-index: 10000;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        pointer-events: none;
        animation: tooltipFadeIn 0.2s ease-out;
        backdrop-filter: blur(10px);
    `;
    
    tooltip.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid var(--glass-border);">
            <div style="font-size: 2rem;">${statusInfo.icon}</div>
            <div style="flex: 1;">
                <div style="font-weight: 700; font-size: 1.1rem; color: var(--text-primary); margin-bottom: 0.25rem;">
                    ${name}
                </div>
                <div style="font-size: 0.875rem; color: var(--text-secondary);">
                    Version: <strong style="color: ${statusInfo.color};">${version}</strong>
                </div>
            </div>
        </div>
        
        <div style="margin-bottom: 1rem;">
            <div style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; background: ${statusInfo.color}22; border-radius: 8px; margin-bottom: 0.75rem;">
                <span style="font-size: 1.25rem;">${statusInfo.icon}</span>
                <span style="color: ${statusInfo.color}; font-weight: 600; font-size: 0.875rem;">
                    ${statusInfo.label}
                </span>
            </div>
            ${cveCount > 0 ? `
                <div style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; background: var(--danger)22; border-radius: 8px; margin-left: 0.5rem;">
                    <span style="font-size: 1.25rem;">🛡️</span>
                    <span style="color: var(--danger); font-weight: 600; font-size: 0.875rem;">
                        ${cveCount} CVE${cveCount > 1 ? 's' : ''}
                    </span>
                </div>
            ` : ''}
        </div>
        
        <div style="color: var(--text-secondary); line-height: 1.6; font-size: 0.875rem;">
            ${explanation}
        </div>
        
        ${status !== 'current' ? `
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--glass-border);">
                <div style="color: var(--accent-primary); font-size: 0.875rem; font-weight: 600;">
                    💡 Recommended Action
                </div>
                <div style="color: var(--text-secondary); font-size: 0.875rem; margin-top: 0.5rem;">
                    ${status === 'deprecated' 
                        ? 'Plan immediate migration to a supported alternative technology.' 
                        : 'Schedule upgrade in next sprint to maintain security and performance.'}
                </div>
            </div>
        ` : ''}
    `;
    
    document.body.appendChild(tooltip);
    
    // Position tooltip
    const rect = element.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();
    
    let left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
    let top = rect.top - tooltipRect.height - 12;
    
    // Keep tooltip on screen
    if (left < 10) left = 10;
    if (left + tooltipRect.width > window.innerWidth - 10) {
        left = window.innerWidth - tooltipRect.width - 10;
    }
    
    if (top < 10) {
        top = rect.bottom + 12;
    }
    
    tooltip.style.left = left + 'px';
    tooltip.style.top = top + 'px';
};

/**
 * Hide technology tooltip
 * @param {HTMLElement} element - Hovered element
 */
window.hideTechTooltip = function(element) {
    // Remove hover effect
    element.style.transform = '';
    element.style.boxShadow = '';
    
    // Remove tooltip
    const tooltip = document.getElementById('tech-tooltip');
    if (tooltip) {
        tooltip.remove();
    }
};

/**
 * Toggle tech details visibility
 * @param {string} cardId - Card ID
 */
window.toggleTechDetails = function(cardId) {
    const details = document.getElementById(`${cardId}-details`);
    const icon = document.getElementById(`${cardId}-toggle-icon`);
    
    if (details && icon) {
        const isHidden = details.style.display === 'none';
        details.style.display = isHidden ? 'block' : 'none';
        icon.textContent = isHidden ? '▼' : '▶';
        
        // Update button text
        const button = icon.parentElement;
        if (button) {
            const text = button.childNodes[1];
            if (text) {
                text.textContent = isHidden ? ' Hide Details' : ' Show Details';
            }
        }
    }
};

/**
 * Export tech stack to CSV (placeholder)
 */
window.exportTechStack = function() {
    console.log('Export tech stack to CSV');
    // TODO: Implement CSV export
    alert('CSV export functionality coming soon!');
};

/**
 * Show technology tooltip with detailed information
 * @param {Event} event - Mouse event
 * @param {string} name - Technology name
 * @param {string} version - Current version
 * @param {string} status - Technology status
 * @param {number} cveCount - CVE count
 * @param {string} explanation - Status explanation
 * @param {HTMLElement} card - Card element
 */
window.showTechTooltip = function(event, name, version, status, cveCount, explanation, card) {
    // Remove any existing tooltip
    hideTechTooltip();
    
    // Status configurations
    const statusConfig = {
        'current': { color: 'var(--success)', icon: '✅', label: 'Current' },
        'outdated': { color: 'var(--warning)', icon: '⚠️', label: 'Outdated' },
        'deprecated': { color: 'var(--danger)', icon: '❌', label: 'Deprecated' }
    };
    
    const statusInfo = statusConfig[status] || statusConfig['current'];
    
    // Generate recommendation based on status
    let recommendation = '';
    if (status === 'current') {
        recommendation = 'No action needed - you\'re running the recommended version.';
    } else if (status === 'outdated') {
        recommendation = 'Update recommended to get latest features, performance improvements, and bug fixes.';
    } else if (status === 'deprecated') {
        recommendation = '⚠️ <strong>Action Required:</strong> Plan migration as this technology is no longer supported and may have security vulnerabilities.';
    }
    
    // CVE warning
    let cveWarning = '';
    if (cveCount > 0) {
        cveWarning = `
            <div style="
                background: var(--danger)22;
                border: 1px solid var(--danger);
                border-radius: 8px;
                padding: 0.75rem;
                margin-top: 0.75rem;
            ">
                <div style="display: flex; align-items: center; gap: 0.5rem; color: var(--danger); font-weight: 600; margin-bottom: 0.25rem;">
                    🛡️ Security Alert
                </div>
                <div style="font-size: 0.875rem; color: var(--text-secondary);">
                    ${cveCount} known CVE${cveCount > 1 ? 's' : ''} detected. Review and update immediately to mitigate security risks.
                </div>
            </div>
        `;
    }
    
    // Create tooltip
    const tooltip = document.createElement('div');
    tooltip.id = 'tech-tooltip';
    tooltip.innerHTML = `
        <div style="
            position: fixed;
            background: linear-gradient(135deg, var(--glass-dark) 0%, var(--background-primary) 100%);
            border: 2px solid ${statusInfo.color};
            border-radius: 12px;
            padding: 1.25rem;
            max-width: 400px;
            box-shadow: 0 12px 40px rgba(0,0,0,0.4);
            z-index: 10000;
            animation: tooltipFadeIn 0.2s ease-out;
        ">
            <!-- Header -->
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem; padding-bottom: 0.75rem; border-bottom: 1px solid var(--glass-border);">
                <div style="font-size: 1.5rem;">${statusInfo.icon}</div>
                <div style="flex: 1;">
                    <div style="font-weight: 600; font-size: 1.125rem; margin-bottom: 0.25rem;">${name}</div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary);">Version ${version}</div>
                </div>
                <div style="
                    padding: 0.375rem 0.75rem;
                    border-radius: 8px;
                    background: ${statusInfo.color}22;
                    color: ${statusInfo.color};
                    font-size: 0.75rem;
                    font-weight: 600;
                    white-space: nowrap;
                ">
                    ${statusInfo.label}
                </div>
            </div>
            
            <!-- Status Explanation -->
            <div style="margin-bottom: 1rem;">
                <div style="font-weight: 600; font-size: 0.875rem; margin-bottom: 0.5rem; color: var(--text-primary);">
                    Status Details
                </div>
                <div style="font-size: 0.875rem; color: var(--text-secondary); line-height: 1.5;">
                    ${explanation}
                </div>
            </div>
            
            <!-- Recommendation -->
            <div style="
                background: var(--glass-light);
                border-radius: 8px;
                padding: 0.75rem;
            ">
                <div style="font-weight: 600; font-size: 0.875rem; margin-bottom: 0.25rem; color: var(--accent-primary);">
                    💡 Recommendation
                </div>
                <div style="font-size: 0.875rem; color: var(--text-secondary); line-height: 1.5;">
                    ${recommendation}
                </div>
            </div>
            
            ${cveWarning}
        </div>
    `;
    
    document.body.appendChild(tooltip);
    
    // Position tooltip
    const tooltipRect = tooltip.firstElementChild.getBoundingClientRect();
    const cardRect = card.getBoundingClientRect();
    
    let left = cardRect.right + 10;
    let top = cardRect.top;
    
    // Adjust if tooltip goes off screen
    if (left + tooltipRect.width > window.innerWidth) {
        left = cardRect.left - tooltipRect.width - 10;
    }
    
    if (top + tooltipRect.height > window.innerHeight) {
        top = window.innerHeight - tooltipRect.height - 10;
    }
    
    if (top < 10) {
        top = 10;
    }
    
    tooltip.firstElementChild.style.left = `${left}px`;
    tooltip.firstElementChild.style.top = `${top}px`;
    
    // Add hover effect to card
    card.style.borderColor = statusInfo.color;
    card.style.transform = 'translateY(-4px)';
    card.style.boxShadow = `0 8px 24px ${statusInfo.color}33`;
};

/**
 * Hide technology tooltip
 * @param {HTMLElement} card - Card element
 */
window.hideTechTooltip = function(card) {
    const tooltip = document.getElementById('tech-tooltip');
    if (tooltip) {
        tooltip.remove();
    }
    
    // Reset card styling
    if (card) {
        card.style.borderColor = 'var(--glass-border)';
        card.style.transform = 'translateY(0)';
        card.style.boxShadow = 'none';
    }
};
