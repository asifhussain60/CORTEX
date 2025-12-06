/**
 * Executive Summary Tab Component
 * 
 * Renders high-level executive overview with purpose, history, and composition.
 * Designed for both technical and non-technical stakeholders.
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Source-Available (Use Allowed, No Contributions)
 */

/**
 * Render executive summary tab
 * @param {Object} data - Dashboard data
 */
export function renderExecutiveSummary(data) {
    const container = document.getElementById('executive-summary-container');
    if (!container) {
        console.error('Executive summary container not found');
        return;
    }
    
    const summary = data.executiveSummary || {};
    const purpose = summary.purpose || {};
    const history = summary.history || {};
    const composition = summary.composition || {};
    
    // Build HTML
    container.innerHTML = `
        <!-- Hero Section: Purpose -->
        <div class="glass-card executive-hero">
            <div class="executive-title-section">
                <h1 class="executive-main-title">
                    ${purpose.title || 'CORTEX'}
                </h1>
                <p class="executive-tagline">
                    ${purpose.tagline || 'AI Assistant Enhancement System'}
                </p>
            </div>
            
            <div class="executive-description">
                <p>${purpose.description || ''}</p>
            </div>
            
            <div class="value-proposition-grid">
                ${renderValueProposition(purpose.value_proposition || [])}
            </div>
            
            ${purpose.target_users ? `
            <div class="target-users-section">
                <h3 style="font-size: 1rem; color: var(--text-secondary); margin-bottom: 1rem;">👥 Target Users</h3>
                <div class="target-users-grid">
                    ${purpose.target_users.map(user => `
                        <div class="target-user-badge">${user}</div>
                    `).join('')}
                </div>
            </div>
            ` : ''}
        </div>
        
        <!-- History Timeline -->
        <div class="glass-card executive-history">
            <h2 class="section-title">
                <span class="section-icon">📅</span>
                Project Timeline & Evolution
            </h2>
            
            <div class="history-stats-grid">
                ${renderHistoryStats(history)}
            </div>
            
            <div class="milestone-timeline">
                <h3 class="subsection-title">Major Milestones</h3>
                ${renderMilestones(history.major_milestones || [])}
            </div>
            
            ${history.evolution ? `
            <div class="evolution-indicators">
                <div class="evolution-badge">
                    <span class="evolution-label">Phase:</span>
                    <span class="evolution-value">${history.evolution.development_phase}</span>
                </div>
                <div class="evolution-badge">
                    <span class="evolution-label">Velocity:</span>
                    <span class="evolution-value">${history.evolution.velocity_trend}</span>
                </div>
                <div class="evolution-badge">
                    <span class="evolution-label">Activity:</span>
                    <span class="evolution-value">${history.evolution.activity_level}</span>
                </div>
            </div>
            ` : ''}
        </div>
        
        <!-- Composition Overview -->
        <div class="glass-card executive-composition">
            <h2 class="section-title">
                <span class="section-icon">🏗️</span>
                System Architecture & Composition
            </h2>
            
            <div class="composition-intro">
                <p>CORTEX is built on a sophisticated multi-tier architecture combining cognitive storage, intelligent agents, and modern web technologies to deliver an unparalleled AI enhancement experience.</p>
            </div>
            
            <!-- Brain Tiers -->
            <div class="architecture-section">
                <h3 class="subsection-title">
                    <span class="subsection-icon">🧠</span>
                    Brain Architecture (4 Tiers)
                </h3>
                <div class="tier-grid">
                    ${renderArchitectureTiers(composition.architecture_layers || [])}
                </div>
            </div>
            
            <!-- Agent System -->
            <div class="architecture-section">
                <h3 class="subsection-title">
                    <span class="subsection-icon">🤖</span>
                    Agent System (Dual Hemisphere)
                </h3>
                <div class="hemisphere-layout">
                    ${renderAgentSystem(composition.agent_system || {})}
                </div>
            </div>
            
            <!-- Technology Stack -->
            <div class="architecture-section">
                <h3 class="subsection-title">
                    <span class="subsection-icon">🛠️</span>
                    Technology Stack
                </h3>
                <div class="tech-stack-layout">
                    ${renderTechStack(composition.technology_stack || {})}
                </div>
            </div>
            
            <!-- Key Features -->
            <div class="architecture-section">
                <h3 class="subsection-title">
                    <span class="subsection-icon">⚡</span>
                    Key Features
                </h3>
                <div class="features-grid">
                    ${renderKeyFeatures(composition.key_features || [])}
                </div>
            </div>
        </div>
        
        <!-- Statistics Footer -->
        <div class="glass-card executive-stats-footer">
            ${renderStatisticsFooter(composition.file_statistics || {}, history)}
        </div>
    `;
    
    // Initialize any interactive elements
    initializeExecutiveInteractions();
}

/**
 * Render value proposition items
 */
function renderValueProposition(items) {
    if (!items || items.length === 0) return '';
    
    return items.map(item => `
        <div class="value-prop-item">
            <span class="value-prop-icon">✓</span>
            <span class="value-prop-text">${item}</span>
        </div>
    `).join('');
}

/**
 * Render history statistics cards
 */
function renderHistoryStats(history) {
    const stats = [
        {
            icon: '📆',
            label: 'Project Started',
            value: formatDate(history.project_inception),
            color: 'var(--accent-primary)'
        },
        {
            icon: '📊',
            label: 'Total Commits',
            value: (history.total_commits || 0).toLocaleString(),
            color: 'var(--accent-secondary)'
        },
        {
            icon: '⚡',
            label: 'Commits/Day',
            value: history.commits_per_day || '0',
            color: 'var(--success)'
        },
        {
            icon: '👥',
            label: 'Contributors',
            value: history.total_contributors || '0',
            color: 'var(--warning)'
        },
        {
            icon: '🕒',
            label: 'Days Active',
            value: (history.days_active || 0).toLocaleString(),
            color: 'var(--accent-primary)'
        },
        {
            icon: '🔥',
            label: 'Last 7 Days',
            value: `${history.commits_last_7_days || 0} commits`,
            color: 'var(--danger)'
        }
    ];
    
    return stats.map(stat => `
        <div class="history-stat-card">
            <div class="stat-icon" style="color: ${stat.color};">${stat.icon}</div>
            <div class="stat-content">
                <div class="stat-label">${stat.label}</div>
                <div class="stat-value" style="color: ${stat.color};">${stat.value}</div>
            </div>
        </div>
    `).join('');
}

/**
 * Render milestone timeline
 */
function renderMilestones(milestones) {
    if (!milestones || milestones.length === 0) {
        return '<p style="color: var(--text-secondary);">No milestones available</p>';
    }
    
    return milestones.map((milestone, index) => `
        <div class="milestone-item">
            <div class="milestone-dot" style="animation-delay: ${index * 0.1}s;"></div>
            <div class="milestone-content">
                <div class="milestone-header">
                    <span class="milestone-date">${formatDate(milestone.date)}</span>
                    <span class="milestone-type milestone-type-${milestone.type}">${milestone.type}</span>
                </div>
                <div class="milestone-version">${milestone.version}</div>
                <div class="milestone-description">${milestone.description}</div>
            </div>
        </div>
    `).join('');
}

/**
 * Render architecture tier cards
 */
function renderArchitectureTiers(layers) {
    if (!layers || layers.length === 0) return '';
    
    return layers.map(layer => `
        <div class="tier-card">
            <div class="tier-header">
                <span class="tier-icon">${layer.icon || '📦'}</span>
                <h4 class="tier-name">${layer.name}</h4>
            </div>
            <p class="tier-purpose">${layer.purpose}</p>
            <div class="tier-components">
                ${layer.components.map(comp => `
                    <span class="component-badge">${comp}</span>
                `).join('')}
            </div>
        </div>
    `).join('');
}

/**
 * Render agent system (dual hemisphere)
 */
function renderAgentSystem(agentSystem) {
    if (!agentSystem || !agentSystem.left_brain) return '';
    
    const leftBrain = agentSystem.left_brain || {};
    const rightBrain = agentSystem.right_brain || {};
    
    return `
        <div class="hemisphere-card left-brain">
            <div class="hemisphere-header">
                <span class="hemisphere-icon">🧠</span>
                <h4 class="hemisphere-title">LEFT BRAIN</h4>
                <span class="hemisphere-subtitle">${leftBrain.role}</span>
            </div>
            <div class="hemisphere-capabilities">
                ${(leftBrain.capabilities || []).map(cap => `
                    <div class="capability-item">
                        <span class="capability-dot"></span>
                        <span class="capability-text">${cap}</span>
                    </div>
                `).join('')}
            </div>
            <div class="hemisphere-footer">
                <span class="agent-count">${leftBrain.agent_count || 0} Agents</span>
            </div>
        </div>
        
        <div class="hemisphere-card right-brain">
            <div class="hemisphere-header">
                <span class="hemisphere-icon">🎨</span>
                <h4 class="hemisphere-title">RIGHT BRAIN</h4>
                <span class="hemisphere-subtitle">${rightBrain.role}</span>
            </div>
            <div class="hemisphere-capabilities">
                ${(rightBrain.capabilities || []).map(cap => `
                    <div class="capability-item">
                        <span class="capability-dot"></span>
                        <span class="capability-text">${cap}</span>
                    </div>
                `).join('')}
            </div>
            <div class="hemisphere-footer">
                <span class="agent-count">${rightBrain.agent_count || 0} Agents</span>
            </div>
        </div>
        
        ${agentSystem.specialized_agents ? `
        <div class="specialized-agents-section">
            <h4 style="font-size: 1rem; color: var(--text-secondary); margin-bottom: 1rem;">
                🎯 ${agentSystem.total_agents} Specialized Agents
            </h4>
            <div class="agent-tags">
                ${agentSystem.specialized_agents.map(agent => `
                    <span class="agent-tag">${agent}</span>
                `).join('')}
            </div>
        </div>
        ` : ''}
    `;
}

/**
 * Render technology stack
 */
function renderTechStack(techStack) {
    if (!techStack) return '';
    
    const categories = [
        { key: 'backend', title: 'Backend', icon: '⚙️', color: 'var(--accent-primary)' },
        { key: 'frontend', title: 'Frontend', icon: '🎨', color: 'var(--accent-secondary)' },
        { key: 'dashboard', title: 'Dashboard', icon: '📊', color: 'var(--success)' },
        { key: 'integration', title: 'Integration', icon: '🔌', color: 'var(--warning)' }
    ];
    
    return categories.map(category => {
        const items = techStack[category.key] || [];
        if (items.length === 0) return '';
        
        return `
            <div class="tech-category">
                <h4 class="tech-category-title">
                    <span style="color: ${category.color};">${category.icon}</span>
                    ${category.title}
                </h4>
                <div class="tech-badges">
                    ${items.map(tech => `
                        <div class="tech-badge" title="${tech.purpose || ''}">
                            <span class="tech-name">${tech.name}</span>
                            <span class="tech-version">${tech.version}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Render key features grid
 */
function renderKeyFeatures(features) {
    if (!features || features.length === 0) return '';
    
    return features.map(feature => `
        <div class="feature-card">
            <span class="feature-icon">✨</span>
            <span class="feature-text">${feature}</span>
        </div>
    `).join('');
}

/**
 * Render statistics footer
 */
function renderStatisticsFooter(stats, history) {
    const fileStats = [
        { label: 'Total Files', value: (stats.total || 0).toLocaleString(), icon: '📁' },
        { label: 'Python Files', value: (stats.python || 0).toLocaleString(), icon: '🐍' },
        { label: 'JavaScript Files', value: (stats.javascript || 0).toLocaleString(), icon: '📜' },
        { label: 'Documentation', value: (stats.markdown || 0).toLocaleString(), icon: '📝' },
        { label: 'Configuration', value: ((stats.yaml || 0) + (stats.json || 0)).toLocaleString(), icon: '⚙️' }
    ];
    
    return `
        <div class="stats-footer-header">
            <h3>📊 Project Statistics</h3>
            <p style="color: var(--text-secondary); font-size: 0.875rem;">
                Last updated: ${formatDate(history?.last_update)} | 
                Primary author: ${history?.primary_author || 'Unknown'}
            </p>
        </div>
        <div class="stats-footer-grid">
            ${fileStats.map(stat => `
                <div class="footer-stat">
                    <span class="footer-stat-icon">${stat.icon}</span>
                    <div class="footer-stat-content">
                        <div class="footer-stat-value">${stat.value}</div>
                        <div class="footer-stat-label">${stat.label}</div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

/**
 * Format date for display
 */
function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    try {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric' 
        });
    } catch (e) {
        return dateStr;
    }
}

/**
 * Initialize interactive elements
 */
function initializeExecutiveInteractions() {
    // Add smooth scroll animations
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.glass-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(card);
    });
    
    // Add hover effects to tech badges
    document.querySelectorAll('.tech-badge').forEach(badge => {
        badge.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05)';
        });
        badge.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
}
