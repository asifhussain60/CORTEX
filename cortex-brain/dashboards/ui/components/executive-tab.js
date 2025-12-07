/**
 * Executive Summary Tab Component
 * 
 * Renders high-level project summary with key insights and recommendations.
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Source-Available (Use Allowed, No Contributions)
 */

import { renderReconciliationWidget } from './reconciliation-widget-collapsible.js';
import { BaseTabComponent } from '../core/BaseTabComponent.js';

/**
 * Render executive summary tab
 * @param {Object} data - Dashboard data
 */
export function renderExecutiveSummary(data) {
    const container = document.getElementById('executive-container');
    if (!container) {
        console.error('Executive summary container not found');
        return;
    }
    
    // Check if we have new executive summary format
    const execSummary = data.executiveSummary || {};
    
    if (execSummary.project_name) {
        // Render new narrative format
        renderNarrativeExecutiveSummary(container, execSummary, data.reconciliation);
    } else {
        // Fallback to old format
        renderLegacyExecutiveSummary(container, data);
    }
}

/**
 * Render new narrative executive summary format
 * @param {HTMLElement} container - Container element
 * @param {Object} execSummary - Executive summary data
 * @param {Object} reconciliation - Reconciliation report data
 */
function renderNarrativeExecutiveSummary(container, execSummary, reconciliation) {
    const whatItDoes = execSummary.what_it_does || {};
    const composition = execSummary.composition || {};
    const capabilities = execSummary.capabilities || [];
    const techFoundation = execSummary.technical_foundation || {};
    const quickInsights = execSummary.quick_insights || [];
    const recommendedSteps = execSummary.recommended_next_steps || [];
    
    // Calculate accuracy percentage based on data source
    const dataSource = whatItDoes.source || 'generated';
    const accuracyMap = {
        'readme': 90,
        'hybrid': 76,
        'generated': 65
    };
    const accuracy = accuracyMap[dataSource] || 76;
    
    container.innerHTML = `
        <!-- Combined Automated Analysis & Reconciliation Panel -->
        ${renderReconciliationWidget(reconciliation, dataSource, accuracy)}
        
        <!-- Project Header -->
        <div class="glass-card" style="margin-bottom: 2rem; padding: 2rem;">
            <h1 style="font-size: 2.5rem; color: var(--accent-primary); margin-bottom: 0.5rem;">
                ${execSummary.project_name || 'Project'}
            </h1>
            <p style="font-size: 1.25rem; color: var(--text-secondary); font-style: italic;">
                ${execSummary.tagline || ''}
            </p>
        </div>
        
        <!-- What It Does Section -->
        <div class="glass-card" style="margin-bottom: 2rem;">
            <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
                <span style="font-size: 2rem; margin-right: 1rem;">📋</span>
                <h2 style="font-size: 1.75rem; color: var(--accent-primary);">What It Does</h2>
            </div>
            <div style="font-size: 1.125rem; line-height: 1.8; color: var(--text-primary); white-space: pre-line; margin-bottom: 1.5rem;">
                ${whatItDoes.summary || ''}
            </div>
            ${whatItDoes.key_points && whatItDoes.key_points.length > 0 ? `
                <div style="background: var(--bg-secondary); padding: 1.5rem; border-radius: 0.5rem; border-left: 4px solid var(--accent-primary);">
                    <h3 style="font-size: 1.125rem; color: var(--accent-primary); margin-bottom: 1rem;">Key Highlights</h3>
                    <ul style="list-style: none; padding: 0; margin: 0;">
                        ${whatItDoes.key_points.map(point => `
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--border-color); display: flex; align-items: start;">
                                <span style="color: var(--accent-primary); margin-right: 0.75rem; font-size: 1.25rem;">✓</span>
                                <span style="color: var(--text-primary);">${point}</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            ` : ''}
        </div>
        
        <!-- Composition & Architecture -->
        ${composition.components && composition.components.length > 0 ? `
            <div class="glass-card" style="margin-bottom: 2rem;">
                <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
                    <span style="font-size: 2rem; margin-right: 1rem;">🏗️</span>
                    <h2 style="font-size: 1.75rem; color: var(--accent-primary);">Composition & Architecture</h2>
                </div>
                <p style="font-size: 1.125rem; color: var(--text-primary); margin-bottom: 1.5rem;">
                    This application is built using <strong>${composition.architecture_style || 'modern architecture'}</strong> 
                    and consists of the following components:
                </p>
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="border-bottom: 2px solid var(--border-color);">
                                <th style="text-align: left; padding: 1rem; color: var(--accent-primary);">Component</th>
                                <th style="text-align: left; padding: 1rem; color: var(--accent-primary);">Technology</th>
                                <th style="text-align: left; padding: 1rem; color: var(--accent-primary);">Purpose</th>
                                <th style="text-align: center; padding: 1rem; color: var(--accent-primary);">Files</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${composition.components.map(comp => `
                                <tr style="border-bottom: 1px solid var(--border-color);">
                                    <td style="padding: 1rem; color: var(--text-primary); font-weight: 600;">${comp.name}</td>
                                    <td style="padding: 1rem; color: var(--text-secondary);">${comp.technology}</td>
                                    <td style="padding: 1rem; color: var(--text-secondary);">${comp.purpose}</td>
                                    <td style="padding: 1rem; text-align: center; color: var(--accent-primary);">${comp.files_count || 'N/A'}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        ` : ''}
        
        <!-- Key Capabilities -->
        ${capabilities.length > 0 ? `
            <div class="glass-card" style="margin-bottom: 2rem;">
                <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
                    <span style="font-size: 2rem; margin-right: 1rem;">⚡</span>
                    <h2 style="font-size: 1.75rem; color: var(--accent-primary);">Key Capabilities</h2>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem;">
                    ${capabilities.map(cap => `
                        <div style="background: var(--bg-secondary); padding: 1.25rem; border-radius: 0.5rem; border-left: 3px solid var(--accent-primary);">
                            <h3 style="font-size: 1.125rem; color: var(--accent-primary); margin-bottom: 0.5rem;">${cap.name}</h3>
                            <p style="color: var(--text-secondary); font-size: 0.9375rem; line-height: 1.6;">${cap.description}</p>
                            ${cap.confidence ? `
                                <div style="margin-top: 0.75rem;">
                                    <div style="background: var(--bg-primary); height: 4px; border-radius: 2px; overflow: hidden;">
                                        <div style="background: var(--accent-primary); height: 100%; width: ${(cap.confidence * 100).toFixed(0)}%;"></div>
                                    </div>
                                    <p style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.25rem;">
                                        Confidence: ${(cap.confidence * 100).toFixed(0)}%
                                    </p>
                                </div>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        ` : ''}
        
        <!-- Technical Foundation -->
        ${techFoundation.languages ? `
            <div class="glass-card" style="margin-bottom: 2rem;">
                <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
                    <span style="font-size: 2rem; margin-right: 1rem;">🛠️</span>
                    <h2 style="font-size: 1.75rem; color: var(--accent-primary);">Technical Foundation</h2>
                </div>
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="border-bottom: 2px solid var(--border-color);">
                                <th style="text-align: left; padding: 1rem; color: var(--accent-primary);">Category</th>
                                <th style="text-align: left; padding: 1rem; color: var(--accent-primary);">Details</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr style="border-bottom: 1px solid var(--border-color);">
                                <td style="padding: 1rem; color: var(--text-primary); font-weight: 600;">Languages</td>
                                <td style="padding: 1rem; color: var(--text-secondary);">
                                    ${Object.entries(techFoundation.languages).map(([lang, pct]) => `${lang} (${pct})`).join(', ')}
                                </td>
                            </tr>
                            ${techFoundation.frameworks && techFoundation.frameworks.length > 0 ? `
                                <tr style="border-bottom: 1px solid var(--border-color);">
                                    <td style="padding: 1rem; color: var(--text-primary); font-weight: 600;">Frameworks</td>
                                    <td style="padding: 1rem; color: var(--text-secondary);">${techFoundation.frameworks.join(', ')}</td>
                                </tr>
                            ` : ''}
                            ${techFoundation.architecture_type ? `
                                <tr style="border-bottom: 1px solid var(--border-color);">
                                    <td style="padding: 1rem; color: var(--text-primary); font-weight: 600;">Architecture</td>
                                    <td style="padding: 1rem; color: var(--text-secondary);">${techFoundation.architecture_type}</td>
                                </tr>
                            ` : ''}
                            ${techFoundation.dependencies ? `
                                <tr style="border-bottom: 1px solid var(--border-color);">
                                    <td style="padding: 1rem; color: var(--text-primary); font-weight: 600;">Dependencies</td>
                                    <td style="padding: 1rem; color: var(--text-secondary);">
                                        ${techFoundation.dependencies.total || 0} total 
                                        (${techFoundation.dependencies.production || 0} production, 
                                        ${techFoundation.dependencies.development || 0} development)
                                    </td>
                                </tr>
                            ` : ''}
                        </tbody>
                    </table>
                </div>
            </div>
        ` : ''}
        
        <!-- Quick Insights -->
        ${quickInsights.length > 0 ? `
            <div class="glass-card" style="margin-bottom: 2rem;">
                <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
                    <span style="font-size: 2rem; margin-right: 1rem;">💡</span>
                    <h2 style="font-size: 1.75rem; color: var(--accent-primary);">Quick Insights</h2>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem;">
                    ${quickInsights.map(insight => `
                        <div style="display: flex; flex-direction: column; padding: 1.25rem; background: var(--bg-secondary); border-radius: 0.5rem; border-top: 3px solid ${getSeverityColor(insight.severity)};">
                            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
                                <span style="font-size: 1.5rem;">${getSeverityIcon(insight.severity)}</span>
                                <span style="font-weight: 600; color: var(--text-primary); font-size: 0.875rem;">${insight.category}</span>
                            </div>
                            <p style="color: var(--text-secondary); font-size: 0.9375rem; line-height: 1.5;">${insight.insight}</p>
                        </div>
                    `).join('')}
                </div>
            </div>
        ` : ''}
        
        <!-- Recommended Next Steps -->
        ${recommendedSteps.length > 0 ? `
            <div class="glass-card">
                <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
                    <span style="font-size: 2rem; margin-right: 1rem;">🎯</span>
                    <h2 style="font-size: 1.75rem; color: var(--accent-primary);">Recommended Next Steps</h2>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1rem;">
                    ${recommendedSteps.map((step, index) => `
                        <div style="display: flex; flex-direction: column; padding: 1.25rem; background: var(--bg-secondary); border-radius: 0.5rem; border-top: 4px solid ${getPriorityColor(step.priority)}; position: relative;">
                            <div style="position: absolute; top: 0.75rem; right: 0.75rem; width: 2rem; height: 2rem; background: var(--accent-primary); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.875rem;">
                                ${index + 1}
                            </div>
                            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
                                <span style="background: ${getPriorityColor(step.priority)}; color: white; padding: 0.25rem 0.625rem; border-radius: 0.25rem; font-size: 0.6875rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                                    ${step.priority}
                                </span>
                                <span style="color: var(--text-secondary); font-size: 0.75rem;">⏱️ ${step.estimated_effort}</span>
                            </div>
                            <p style="font-weight: 600; color: var(--text-primary); margin-bottom: 0.625rem; font-size: 1rem; line-height: 1.4; padding-right: 2.5rem;">${step.action}</p>
                            <p style="color: var(--text-secondary); font-size: 0.8125rem;">📁 ${step.category}</p>
                        </div>
                    `).join('')}
                </div>
            </div>
        ` : ''}
    `;
}

/**
 * Render legacy executive summary format (fallback)
 * @param {HTMLElement} container - Container element
 * @param {Object} data - Dashboard data
 */
function renderLegacyExecutiveSummary(container, data) {
    const healthData = data.healthData || {};
    const techStack = data.techStack || {};
    const security = data.security || {};
    const codeOrg = data.codeOrganization || {};
    
    const overallScore = healthData.overall_score || 0;
    const projectType = data.projectType || 'Unknown';
    const linesOfCode = codeOrg.linesOfCode || 0;
    const fileCount = codeOrg.fileCount || 0;
    
    // Generate executive summary text
    const summaryText = generateExecutiveSummary(data);
    
    // Build HTML
    container.innerHTML = `
        <!-- Executive Summary Section -->
        <div class="glass-card" style="margin-bottom: 2rem;">
            <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
                <span style="font-size: 2.5rem; margin-right: 1rem;">📋</span>
                <h2 style="font-size: 1.75rem; color: var(--accent-primary);">Executive Summary</h2>
            </div>
            <p style="font-size: 1.125rem; line-height: 1.8; color: var(--text-primary); white-space: pre-line;">
                ${summaryText}
            </p>
        </div>
        
        <!-- Quick Stats Grid -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
            <!-- Overall Health -->
            <div class="glass-card" style="text-align: center; padding: 2rem;">
                <div style="font-size: 3rem; margin-bottom: 0.5rem;">${getHealthEmoji(overallScore)}</div>
                <h3 style="font-size: 2.5rem; color: var(--accent-primary); margin-bottom: 0.5rem;">${overallScore}</h3>
                <p style="color: var(--text-secondary); font-weight: 600;">Overall Health Score</p>
                <p style="color: var(--text-secondary); font-size: 0.875rem; margin-top: 0.5rem;">
                    ${getHealthStatus(overallScore)}
                </p>
            </div>
            
            <!-- Project Type -->
            <div class="glass-card" style="text-align: center; padding: 2rem;">
                <div style="font-size: 3rem; margin-bottom: 0.5rem;">${getProjectTypeEmoji(projectType)}</div>
                <h3 style="font-size: 1.5rem; color: var(--accent-primary); margin-bottom: 0.5rem;">${projectType}</h3>
                <p style="color: var(--text-secondary); font-weight: 600;">Project Type</p>
                <p style="color: var(--text-secondary); font-size: 0.875rem; margin-top: 0.5rem;">
                    ${linesOfCode.toLocaleString()} lines • ${fileCount} files
                </p>
            </div>
            
            <!-- Security Status -->
            <div class="glass-card" style="text-align: center; padding: 2rem;">
                <div style="font-size: 3rem; margin-bottom: 0.5rem;">${getSecurityEmoji(security)}</div>
                <h3 style="font-size: 2.5rem; color: var(--accent-primary); margin-bottom: 0.5rem;">
                    ${security.vulnerabilities?.total || 0}
                </h3>
                <p style="color: var(--text-secondary); font-weight: 600;">Security Issues</p>
                <p style="color: var(--text-secondary); font-size: 0.875rem; margin-top: 0.5rem;">
                    ${(security.vulnerabilities?.critical || 0)} critical • ${(security.vulnerabilities?.high || 0)} high
                </p>
            </div>
        </div>
        
        <!-- Key Strengths & Concerns -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2rem;">
            <!-- Strengths -->
            <div class="glass-card">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <span style="font-size: 2rem; margin-right: 1rem;">✅</span>
                    <h3 style="color: var(--success);">Key Strengths</h3>
                </div>
                <ul id="strengths-list" style="list-style: none; padding: 0;">
                    ${generateStrengths(data).map(strength => `
                        <li style="padding: 0.75rem; margin-bottom: 0.5rem; background: rgba(0, 255, 136, 0.1); border-left: 3px solid var(--success); border-radius: 4px;">
                            ${strength}
                        </li>
                    `).join('')}
                </ul>
            </div>
            
            <!-- Concerns -->
            <div class="glass-card">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <span style="font-size: 2rem; margin-right: 1rem;">⚠️</span>
                    <h3 style="color: var(--warning);">Areas of Concern</h3>
                </div>
                <ul id="concerns-list" style="list-style: none; padding: 0;">
                    ${generateConcerns(data).map(concern => `
                        <li style="padding: 0.75rem; margin-bottom: 0.5rem; background: rgba(255, 165, 0, 0.1); border-left: 3px solid var(--warning); border-radius: 4px;">
                            ${concern}
                        </li>
                    `).join('')}
                </ul>
            </div>
        </div>
        
        <!-- Top Recommendations -->
        <div class="glass-card">
            <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
                <span style="font-size: 2rem; margin-right: 1rem;">💡</span>
                <h3 style="color: var(--accent-primary);">Top Priority Recommendations</h3>
            </div>
            <div id="top-recommendations">
                ${generateTopRecommendations(data).map((rec, idx) => `
                    <div style="padding: 1rem; margin-bottom: 1rem; background: var(--glass-bg); border-left: 4px solid ${rec.color}; border-radius: 4px;">
                        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                            <span style="background: ${rec.color}; color: white; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600; margin-right: 1rem;">
                                ${rec.priority}
                            </span>
                            <h4 style="color: var(--text-primary);">${rec.title}</h4>
                        </div>
                        <p style="color: var(--text-secondary); margin-left: 0;">
                            ${rec.description}
                        </p>
                    </div>
                `).join('')}
            </div>
        </div>
        
        <!-- Action Items -->
        <div class="glass-card" style="margin-top: 2rem;">
            <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
                <span style="font-size: 2rem; margin-right: 1rem;">🎯</span>
                <h3 style="color: var(--accent-primary);">Recommended Next Steps</h3>
            </div>
            <ol style="padding-left: 1.5rem; color: var(--text-secondary); line-height: 2;">
                ${generateActionItems(data).map(action => `<li>${action}</li>`).join('')}
            </ol>
        </div>
    `;
}

/**
 * Generate executive summary text based on project data
 */
function generateExecutiveSummary(data) {
    const healthData = data.healthData || {};
    const overallScore = healthData.overall_score || 0;
    const projectType = data.projectType || 'software project';
    const codeOrg = data.codeOrganization || {};
    const security = data.security || {};
    const techStack = data.techStack || {};
    
    const healthStatus = getHealthStatus(overallScore);
    const linesOfCode = (codeOrg.linesOfCode || 0).toLocaleString();
    const fileCount = codeOrg.fileCount || 0;
    const criticalIssues = security.vulnerabilities?.critical || 0;
    const languageCount = Object.keys(techStack.languages || {}).length;
    
    const primaryLanguage = Object.entries(techStack.languages || {})
        .sort((a, b) => (b[1].percentage || 0) - (a[1].percentage || 0))[0]?.[0] || 'unknown';
    
    let summary = `This ${projectType} consists of ${linesOfCode} lines of code across ${fileCount} files, primarily written in ${primaryLanguage}. `;
    
    if (overallScore >= 75) {
        summary += `The project demonstrates strong health with an overall score of ${overallScore}, indicating ${healthStatus}. `;
    } else if (overallScore >= 50) {
        summary += `The project shows moderate health with an overall score of ${overallScore}, ${healthStatus}. `;
    } else {
        summary += `The project health score of ${overallScore} ${healthStatus}. `;
    }
    
    if (criticalIssues > 0) {
        summary += `There are ${criticalIssues} critical security issues that require immediate attention. `;
    } else if (security.vulnerabilities?.total > 0) {
        summary += `Security analysis identified ${security.vulnerabilities.total} issues of varying severity. `;
    } else {
        summary += `No critical security vulnerabilities were detected. `;
    }
    
    summary += `\n\nThe technology stack includes ${languageCount} programming language${languageCount !== 1 ? 's' : ''} with ${Object.keys(techStack.frameworks || {}).length} frameworks and ${techStack.dependencies?.total || 0} external dependencies.`;
    
    return summary;
}

/**
 * Generate list of project strengths
 */
function generateStrengths(data) {
    const strengths = [];
    const healthData = data.healthData || {};
    const metrics = healthData.metrics || {};
    const security = data.security || {};
    
    if (metrics.code_quality_score >= 75) {
        strengths.push(`High code quality score (${metrics.code_quality_score}/100)`);
    }
    if (metrics.test_coverage >= 70) {
        strengths.push(`Good test coverage (${metrics.test_coverage}%)`);
    }
    if (metrics.documentation_score >= 75) {
        strengths.push(`Well-documented codebase (${metrics.documentation_score}/100)`);
    }
    if ((security.vulnerabilities?.critical || 0) === 0) {
        strengths.push('No critical security vulnerabilities detected');
    }
    if (metrics.maintainability_index >= 75) {
        strengths.push(`High maintainability index (${metrics.maintainability_index}/100)`);
    }
    
    if (strengths.length === 0) {
        strengths.push('Project structure is present and analyzable');
        strengths.push('Codebase is accessible for analysis');
    }
    
    return strengths;
}

/**
 * Generate list of concerns
 */
function generateConcerns(data) {
    const concerns = [];
    const healthData = data.healthData || {};
    const metrics = healthData.metrics || {};
    const security = data.security || {};
    
    if (metrics.code_quality_score < 50) {
        concerns.push(`Low code quality score (${metrics.code_quality_score}/100)`);
    }
    if (metrics.test_coverage < 50) {
        concerns.push(`Insufficient test coverage (${metrics.test_coverage}%)`);
    }
    if ((security.vulnerabilities?.critical || 0) > 0) {
        concerns.push(`${security.vulnerabilities.critical} critical security vulnerabilities`);
    }
    if ((security.vulnerabilities?.high || 0) > 5) {
        concerns.push(`${security.vulnerabilities.high} high-severity security issues`);
    }
    if (metrics.technical_debt_ratio > 30) {
        concerns.push(`High technical debt ratio (${metrics.technical_debt_ratio}%)`);
    }
    if (metrics.documentation_score < 50) {
        concerns.push(`Limited documentation (${metrics.documentation_score}/100)`);
    }
    
    if (concerns.length === 0) {
        concerns.push('Continue monitoring code quality metrics');
        concerns.push('Ensure security scanning remains active');
    }
    
    return concerns;
}

/**
 * Generate top priority recommendations
 */
function generateTopRecommendations(data) {
    const recommendations = [];
    const healthData = data.healthData || {};
    const metrics = healthData.metrics || {};
    const security = data.security || {};
    
    if ((security.vulnerabilities?.critical || 0) > 0) {
        recommendations.push({
            priority: 'CRITICAL',
            color: 'var(--danger)',
            title: 'Address Critical Security Vulnerabilities',
            description: `${security.vulnerabilities.critical} critical vulnerabilities require immediate remediation to prevent potential security breaches.`
        });
    }
    
    if (metrics.test_coverage < 50) {
        recommendations.push({
            priority: 'HIGH',
            color: 'var(--warning)',
            title: 'Improve Test Coverage',
            description: `Current test coverage is ${metrics.test_coverage}%. Aim for at least 70% coverage to ensure code reliability.`
        });
    }
    
    if (metrics.code_quality_score < 60) {
        recommendations.push({
            priority: 'HIGH',
            color: 'var(--warning)',
            title: 'Enhance Code Quality',
            description: `Code quality score of ${metrics.code_quality_score}/100 indicates room for improvement. Focus on reducing complexity and improving consistency.`
        });
    }
    
    if (metrics.documentation_score < 60) {
        recommendations.push({
            priority: 'MEDIUM',
            color: '#ffa500',
            title: 'Expand Documentation',
            description: `Documentation score is ${metrics.documentation_score}/100. Add comprehensive docs to improve maintainability and onboarding.`
        });
    }
    
    if (recommendations.length === 0) {
        recommendations.push({
            priority: 'LOW',
            color: 'var(--success)',
            title: 'Maintain Current Standards',
            description: 'Project health is good. Continue following current development practices and monitor metrics regularly.'
        });
    }
    
    return recommendations.slice(0, 4); // Top 4 recommendations
}

/**
 * Generate action items
 */
function generateActionItems(data) {
    const actions = [];
    const healthData = data.healthData || {};
    const metrics = healthData.metrics || {};
    const security = data.security || {};
    
    if ((security.vulnerabilities?.critical || 0) > 0) {
        actions.push('Review and remediate all critical security vulnerabilities immediately');
    }
    if (metrics.test_coverage < 70) {
        actions.push('Increase test coverage with unit and integration tests');
    }
    if (metrics.code_quality_score < 70) {
        actions.push('Refactor complex modules to improve code quality metrics');
    }
    if (metrics.documentation_score < 70) {
        actions.push('Add comprehensive documentation for key modules and APIs');
    }
    
    actions.push('Schedule regular security scans and dependency updates');
    actions.push('Establish code review processes and quality gates');
    actions.push('Monitor performance metrics and optimize bottlenecks');
    
    return actions.slice(0, 6); // Top 6 action items
}

/**
 * Get health emoji based on score
 */
function getHealthEmoji(score) {
    if (score >= 75) return '🟢';
    if (score >= 50) return '🟡';
    return '🔴';
}

/**
 * Get health status text
 */
function getHealthStatus(score) {
    if (score >= 75) return 'Healthy';
    if (score >= 50) return 'Needs Attention';
    return 'Requires Action';
}

/**
 * Get project type emoji
 */
function getProjectTypeEmoji(type) {
    const typeMap = {
        'Web Application': '🌐',
        'API Service': '🔌',
        'Desktop Application': '💻',
        'Mobile Application': '📱',
        'Library/Framework': '📚',
        'CLI Tool': '⌨️',
        'Microservice': '🔧'
    };
    return typeMap[type] || '📦';
}

/**
 * Get security emoji
 */
function getSecurityEmoji(security) {
    const critical = security.vulnerabilities?.critical || 0;
    const high = security.vulnerabilities?.high || 0;
    
    if (critical > 0) return '🔴';
    if (high > 5) return '🟡';
    return '🟢';
}

/**
 * Get severity color
 */
function getSeverityColor(severity) {
    const colorMap = {
        'info': '#3b82f6',
        'warning': '#f59e0b',
        'error': '#ef4444',
        'critical': '#dc2626'
    };
    return colorMap[severity] || '#3b82f6';
}

/**
 * Get severity icon
 */
function getSeverityIcon(severity) {
    const iconMap = {
        'info': 'ℹ️',
        'warning': '⚠️',
        'error': '❌',
        'critical': '🚨'
    };
    return iconMap[severity] || 'ℹ️';
}

/**
 * Get priority color
 */
function getPriorityColor(priority) {
    const colorMap = {
        'high': '#ef4444',
        'medium': '#f59e0b',
        'low': '#10b981'
    };
    return colorMap[priority] || '#6b7280';
}

// BaseTabComponent wrapper
class ExecutiveTab extends BaseTabComponent {
    constructor() {
        super('executive-container');
    }
    
    render() {
        renderExecutiveSummary(this.data);
    }
}

export { ExecutiveTab };
