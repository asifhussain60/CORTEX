/**
 * Executive Intelligence Panel Component
 * 
 * Displays enriched executive summaries with Phase 2 intelligence:
 * - Git commit patterns and development trends
 * - README insights and purpose statements
 * - Business domain inference
 * - Quality scoring and data source indicators
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 */

/**
 * Render enhanced executive intelligence panel
 * @param {HTMLElement} container - Container element
 * @param {Object} intelligenceSummary - Executive summary from Phase 2 orchestrator
 */
export function renderExecutiveIntelligencePanel(container, intelligenceSummary) {
    if (!container) {
        console.error('Executive intelligence container not found');
        return;
    }
    
    if (!intelligenceSummary || !intelligenceSummary.repo_name) {
        container.innerHTML = renderNoDataState();
        return;
    }
    
    container.innerHTML = `
        ${renderProjectHeader(intelligenceSummary)}
        ${renderQualityIndicator(intelligenceSummary)}
        ${renderPurposeSection(intelligenceSummary)}
        ${renderBusinessContext(intelligenceSummary)}
        ${renderTechnicalDetails(intelligenceSummary)}
        ${renderDevelopmentInsights(intelligenceSummary)}
        ${renderDataSources(intelligenceSummary)}
    `;
}

/**
 * Render project header with title and description
 */
function renderProjectHeader(summary) {
    return `
        <div class="glass-card" style="margin-bottom: 2rem; padding: 2rem; background: linear-gradient(135deg, rgba(94, 114, 228, 0.1) 0%, rgba(168, 85, 247, 0.1) 100%);">
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                <span style="font-size: 3rem;">🧠</span>
                <div>
                    <h1 style="font-size: 2.5rem; color: var(--accent-primary); margin: 0;">
                        ${escapeHtml(summary.title || summary.repo_name)}
                    </h1>
                    <p style="font-size: 0.875rem; color: var(--text-secondary); margin: 0.25rem 0 0 0;">
                        ${escapeHtml(summary.repo_path || '')}
                    </p>
                </div>
            </div>
            ${summary.description ? `
                <p style="font-size: 1.25rem; color: var(--text-primary); line-height: 1.6; margin: 1rem 0 0 0;">
                    ${escapeHtml(summary.description)}
                </p>
            ` : ''}
        </div>
    `;
}

/**
 * Render quality indicator badge
 */
function renderQualityIndicator(summary) {
    const score = summary.summary_quality_score || 0;
    const percentage = Math.round((score / 10) * 100);
    
    let qualityLevel = 'Low';
    let qualityColor = '#ef4444';
    
    if (score >= 8) {
        qualityLevel = 'Excellent';
        qualityColor = '#10b981';
    } else if (score >= 6) {
        qualityLevel = 'Good';
        qualityColor = '#f59e0b';
    } else if (score >= 4) {
        qualityLevel = 'Fair';
        qualityColor = '#f59e0b';
    }
    
    return `
        <div class="glass-card" style="margin-bottom: 2rem; padding: 1.5rem;">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <h3 style="font-size: 1rem; color: var(--text-secondary); margin: 0 0 0.25rem 0;">Intelligence Quality</h3>
                    <p style="font-size: 2rem; color: ${qualityColor}; margin: 0; font-weight: bold;">
                        ${qualityLevel}
                    </p>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 3rem; color: ${qualityColor}; line-height: 1;">
                        ${score.toFixed(1)}
                    </div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary);">
                        out of 10
                    </div>
                </div>
            </div>
            <div style="margin-top: 1rem; background: var(--bg-secondary); height: 8px; border-radius: 4px; overflow: hidden;">
                <div style="width: ${percentage}%; height: 100%; background: ${qualityColor}; transition: width 0.3s ease;"></div>
            </div>
        </div>
    `;
}

/**
 * Render purpose section
 */
function renderPurposeSection(summary) {
    if (!summary.purpose) return '';
    
    return `
        <div class="glass-card" style="margin-bottom: 2rem;">
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                <span style="font-size: 1.5rem;">🎯</span>
                <h2 style="font-size: 1.5rem; color: var(--accent-primary); margin: 0;">Purpose</h2>
            </div>
            <p style="font-size: 1.125rem; line-height: 1.8; color: var(--text-primary); white-space: pre-line;">
                ${escapeHtml(summary.purpose)}
            </p>
        </div>
    `;
}

/**
 * Render business context section
 */
function renderBusinessContext(summary) {
    const hasDomains = summary.primary_domains && summary.primary_domains.length > 0;
    const hasCapabilities = summary.capabilities && summary.capabilities.length > 0;
    
    if (!hasDomains && !hasCapabilities) return '';
    
    return `
        <div class="glass-card" style="margin-bottom: 2rem;">
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem;">
                <span style="font-size: 1.5rem;">🏢</span>
                <h2 style="font-size: 1.5rem; color: var(--accent-primary); margin: 0;">Business Context</h2>
            </div>
            
            ${hasDomains ? `
                <div style="margin-bottom: 1.5rem;">
                    <h3 style="font-size: 1.125rem; color: var(--text-secondary); margin-bottom: 0.75rem;">Primary Domains</h3>
                    <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                        ${summary.primary_domains.map(domain => `
                            <span style="padding: 0.5rem 1rem; background: var(--accent-primary); color: white; border-radius: 1rem; font-size: 0.875rem; font-weight: 500;">
                                ${escapeHtml(domain)}
                            </span>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
            
            ${hasCapabilities ? `
                <div>
                    <h3 style="font-size: 1.125rem; color: var(--text-secondary); margin-bottom: 0.75rem;">Key Capabilities</h3>
                    <ul style="list-style: none; padding: 0; margin: 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 0.75rem;">
                        ${summary.capabilities.map(capability => `
                            <li style="display: flex; align-items: start; padding: 0.75rem; background: var(--bg-secondary); border-radius: 0.5rem; border-left: 3px solid var(--accent-primary);">
                                <span style="color: var(--accent-primary); margin-right: 0.5rem;">✓</span>
                                <span style="color: var(--text-primary);">${escapeHtml(capability)}</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            ` : ''}
        </div>
    `;
}

/**
 * Render technical details section
 */
function renderTechnicalDetails(summary) {
    const hasFeatures = summary.features && summary.features.length > 0;
    const hasTech = summary.technologies && summary.technologies.length > 0;
    
    if (!hasFeatures && !hasTech) return '';
    
    return `
        <div class="glass-card" style="margin-bottom: 2rem;">
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem;">
                <span style="font-size: 1.5rem;">⚙️</span>
                <h2 style="font-size: 1.5rem; color: var(--accent-primary); margin: 0;">Technical Details</h2>
            </div>
            
            ${hasFeatures ? `
                <div style="margin-bottom: 1.5rem;">
                    <h3 style="font-size: 1.125rem; color: var(--text-secondary); margin-bottom: 0.75rem;">Features</h3>
                    <ul style="list-style: none; padding: 0; margin: 0;">
                        ${summary.features.map(feature => `
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--border-color); display: flex; align-items: start;">
                                <span style="color: var(--accent-secondary); margin-right: 0.75rem;">▸</span>
                                <span style="color: var(--text-primary);">${escapeHtml(feature)}</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            ` : ''}
            
            ${hasTech ? `
                <div>
                    <h3 style="font-size: 1.125rem; color: var(--text-secondary); margin-bottom: 0.75rem;">Technology Stack</h3>
                    <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                        ${summary.technologies.map(tech => `
                            <span style="padding: 0.375rem 0.75rem; background: var(--bg-secondary); color: var(--text-primary); border-radius: 0.25rem; font-size: 0.875rem; border: 1px solid var(--border-color);">
                                ${escapeHtml(tech)}
                            </span>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
        </div>
    `;
}

/**
 * Render development insights section
 */
function renderDevelopmentInsights(summary) {
    const hasDevelopment = summary.development_focus || 
                          (summary.active_areas && summary.active_areas.length > 0) ||
                          summary.recent_velocity;
    
    if (!hasDevelopment) return '';
    
    const velocity = summary.recent_velocity || {};
    
    return `
        <div class="glass-card" style="margin-bottom: 2rem;">
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem;">
                <span style="font-size: 1.5rem;">📊</span>
                <h2 style="font-size: 1.5rem; color: var(--accent-primary); margin: 0;">Development Activity</h2>
            </div>
            
            ${summary.development_focus ? `
                <div style="margin-bottom: 1.5rem; padding: 1rem; background: var(--bg-secondary); border-radius: 0.5rem;">
                    <h3 style="font-size: 1rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Current Focus</h3>
                    <p style="font-size: 1rem; color: var(--text-primary); margin: 0;">
                        ${escapeHtml(summary.development_focus)}
                    </p>
                </div>
            ` : ''}
            
            ${summary.active_areas && summary.active_areas.length > 0 ? `
                <div style="margin-bottom: 1.5rem;">
                    <h3 style="font-size: 1rem; color: var(--text-secondary); margin-bottom: 0.75rem;">Active Areas</h3>
                    <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                        ${summary.active_areas.map(area => `
                            <span style="padding: 0.375rem 0.75rem; background: rgba(94, 114, 228, 0.1); color: var(--accent-primary); border-radius: 0.25rem; font-size: 0.875rem; font-family: monospace;">
                                ${escapeHtml(area)}
                            </span>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
            
            ${velocity.total_commits ? `
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">
                    <div style="padding: 1rem; background: var(--bg-secondary); border-radius: 0.5rem; text-align: center;">
                        <div style="font-size: 2rem; color: var(--accent-primary); font-weight: bold;">
                            ${velocity.total_commits}
                        </div>
                        <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.25rem;">
                            Total Commits
                        </div>
                    </div>
                    ${velocity.features_completed !== undefined ? `
                        <div style="padding: 1rem; background: var(--bg-secondary); border-radius: 0.5rem; text-align: center;">
                            <div style="font-size: 2rem; color: #10b981; font-weight: bold;">
                                ${velocity.features_completed}
                            </div>
                            <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.25rem;">
                                Features
                            </div>
                        </div>
                    ` : ''}
                    ${velocity.bugs_fixed !== undefined ? `
                        <div style="padding: 1rem; background: var(--bg-secondary); border-radius: 0.5rem; text-align: center;">
                            <div style="font-size: 2rem; color: #f59e0b; font-weight: bold;">
                                ${velocity.bugs_fixed}
                            </div>
                            <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.25rem;">
                                Bugs Fixed
                            </div>
                        </div>
                    ` : ''}
                    ${velocity.commits_per_day !== undefined ? `
                        <div style="padding: 1rem; background: var(--bg-secondary); border-radius: 0.5rem; text-align: center;">
                            <div style="font-size: 2rem; color: var(--accent-secondary); font-weight: bold;">
                                ${velocity.commits_per_day.toFixed(1)}
                            </div>
                            <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.25rem;">
                                Commits/Day
                            </div>
                        </div>
                    ` : ''}
                </div>
            ` : ''}
        </div>
    `;
}

/**
 * Render data sources section
 */
function renderDataSources(summary) {
    return `
        <div class="glass-card" style="padding: 1rem;">
            <h3 style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em;">
                Intelligence Sources
            </h3>
            <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                ${renderSourceBadge('README', summary.has_readme)}
                ${renderSourceBadge('Git History', summary.has_git_history)}
                ${renderSourceBadge('Domain Inference', summary.primary_domains && summary.primary_domains.length > 0)}
            </div>
        </div>
    `;
}

/**
 * Render source availability badge
 */
function renderSourceBadge(name, available) {
    const color = available ? '#10b981' : '#6b7280';
    const icon = available ? '✓' : '✗';
    
    return `
        <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; background: var(--bg-secondary); border-radius: 0.25rem; border-left: 3px solid ${color};">
            <span style="color: ${color}; font-weight: bold;">${icon}</span>
            <span style="font-size: 0.875rem; color: var(--text-primary);">${name}</span>
        </div>
    `;
}

/**
 * Render no data state
 */
function renderNoDataState() {
    return `
        <div class="glass-card" style="padding: 3rem; text-align: center;">
            <span style="font-size: 4rem; display: block; margin-bottom: 1rem;">📊</span>
            <h2 style="font-size: 1.5rem; color: var(--text-secondary); margin-bottom: 0.5rem;">No Intelligence Data Available</h2>
            <p style="color: var(--text-secondary);">
                Executive summary has not been generated yet.
            </p>
        </div>
    `;
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
