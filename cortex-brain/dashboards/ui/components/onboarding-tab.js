/**
 * Onboarding Tab Component
 * 
 * Progressive learning path with 6 stages for new engineers.
 * Features: Stage navigation, completion tracking, interactive content,
 * responsive design, accessibility support.
 * 
 * @version 1.2.0
 * @date 2025-12-07
 * @extends BaseTabComponent
 */

import { BaseTabComponent } from '../core/BaseTabComponent.js';

class OnboardingTab extends BaseTabComponent {
    constructor() {
        super('engineering-onboarding-content');
        this.currentStage = 1;
        this.completedStages = this.loadProgress();
    }

    /**
     * Initialize tab with data (override BaseTabComponent)
     */
    async init(data) {
        await super.init(data); // Handles container setup, loading state, error handling
        this.initializeMermaid();
        this.attachEventListeners();
        this.restoreScrollPosition();
        this.renderAllDiagrams();
    }

    /**
     * Initialize Mermaid with custom theme
     */
    initializeMermaid() {
        if (typeof mermaid !== 'undefined') {
            mermaid.initialize({
                startOnLoad: false,
                theme: 'dark',
                themeVariables: {
                    primaryColor: '#00d4ff',
                    primaryTextColor: '#fff',
                    primaryBorderColor: '#00d4ff',
                    lineColor: '#00d4ff',
                    secondaryColor: '#7b61ff',
                    tertiaryColor: '#ffa500',
                    background: '#1a1a2e',
                    mainBkg: '#1a1a2e',
                    secondBkg: '#16213e',
                    border1: '#00d4ff',
                    border2: '#7b61ff'
                },
                flowchart: {
                    curve: 'basis',
                    padding: 20
                },
                sequence: {
                    diagramMarginX: 20,
                    diagramMarginY: 20,
                    actorMargin: 100,
                    width: 200,
                    height: 65,
                    boxMargin: 10,
                    boxTextMargin: 5,
                    noteMargin: 10,
                    messageMargin: 35
                }
            });
        }
    }

    /**
     * Render all diagrams after DOM update
     */
    async renderAllDiagrams() {
        if (typeof mermaid !== 'undefined') {
            // Use setTimeout to ensure DOM is ready
            setTimeout(() => {
                mermaid.run({
                    querySelector: '.mermaid'
                });
            }, 100);
        }
    }

    /**
     * Load progress from localStorage
     */
    loadProgress() {
        try {
            const progress = localStorage.getItem('cortex_onboarding_progress');
            if (progress) {
                const data = JSON.parse(progress);
                this.currentStage = data.current_stage || 1;
                return new Set(data.completed_stages || []);
            }
        } catch (e) {
            console.warn('Failed to load onboarding progress:', e);
        }
        return new Set();
    }

    /**
     * Save progress to localStorage
     */
    saveProgress() {
        try {
            const progress = {
                current_stage: this.currentStage,
                completed_stages: Array.from(this.completedStages),
                last_accessed: new Date().toISOString(),
                completion_percentage: this.getCompletionPercentage()
            };
            localStorage.setItem('cortex_onboarding_progress', JSON.stringify(progress));
        } catch (e) {
            console.warn('Failed to save onboarding progress:', e);
        }
    }

    /**
     * Calculate completion percentage
     */
    getCompletionPercentage() {
        if (!this.data || !this.data.stages) return 0;
        return Math.round((this.completedStages.size / this.data.stages.length) * 100);
    }

    /**
     * Render the tab with wizard layout (override BaseTabComponent)
     */
    render() {
        // BaseTabComponent.init() already set this.container
        if (!this.container || !this.data) return;

        const stage = this.data.stages.find(s => s.id === this.currentStage);
        if (!stage) return;

        this.container.innerHTML = `
            <div style="margin-bottom: 1rem;">
                ${this.renderHeader()}
                ${this.renderProgressBar()}
            </div>
            <div class="onboarding-container">
                ${this.renderWizardStepper()}
                <div class="wizard-content-area">
                    ${this.renderStageContent(stage)}
                </div>
            </div>
        `;
    }

    /**
     * Render header with progress stats (no duplicate title)
     */
    renderHeader() {
        const completionPct = this.getCompletionPercentage();
        return `
            <div class="onboarding-header">
                <p class="onboarding-subtitle">
                    Progressive learning path for ${this.data.metadata.repository} repository
                </p>
                <div class="onboarding-stats">
                    <div class="stat-card">
                        <div class="stat-value">${completionPct}%</div>
                        <div class="stat-label">Complete</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${this.completedStages.size}/${this.data.stages.length}</div>
                        <div class="stat-label">Stages</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${this.getTotalDuration()} min</div>
                        <div class="stat-label">Total Time</div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Get total duration of all stages
     */
    getTotalDuration() {
        return this.data.stages.reduce((sum, stage) => sum + stage.duration_minutes, 0);
    }

    /**
     * Render progress bar
     */
    renderProgressBar() {
        const completionPct = this.getCompletionPercentage();
        return `
            <div class="onboarding-progress-bar">
                <div class="progress-fill" style="width: ${completionPct}%"></div>
            </div>
        `;
    }

    /**
     * Render wizard stepper navigation (left sidebar)
     */
    renderWizardStepper() {
        return `
            <div class="wizard-stepper">
                ${this.data.stages.map(stage => this.renderWizardStep(stage)).join('')}
            </div>
        `;
    }

    /**
     * Render individual wizard step
     */
    renderWizardStep(stage) {
        const isActive = stage.id === this.currentStage;
        const isCompleted = this.completedStages.has(stage.id);
        const statusClass = isCompleted ? 'completed' : '';
        const activeClass = isActive ? 'active' : '';
        const statusIcon = isCompleted ? '✅' : (isActive ? '⏳' : '◻️');

        return `
            <div class="wizard-step ${statusClass} ${activeClass}" data-stage-id="${stage.id}">
                <div class="wizard-step-header">
                    <div class="wizard-step-icon">${stage.icon}</div>
                    <div class="wizard-step-info">
                        <div class="wizard-step-title">${stage.title}</div>
                        <div class="wizard-step-duration">⏱️ ${stage.duration_minutes} min</div>
                    </div>
                    <div class="wizard-step-status">${statusIcon}</div>
                </div>
            </div>
        `;
    }

    /**
     * Render wizard stepper navigation (left sidebar)
     */
    renderWizardStepper() {
        return `
            <div class="wizard-stepper">
                ${this.data.stages.map(stage => this.renderWizardStep(stage)).join('')}
            </div>
        `;
    }

    /**
     * Render individual wizard step
     */
    renderWizardStep(stage) {
        const isActive = stage.id === this.currentStage;
        const isCompleted = this.completedStages.has(stage.id);
        const statusClass = isCompleted ? 'completed' : '';
        const activeClass = isActive ? 'active' : '';
        const statusIcon = isCompleted ? '✅' : (isActive ? '⏳' : '◻️');

        return `
            <div class="wizard-step ${statusClass} ${activeClass}" data-stage-id="${stage.id}">
                <div class="wizard-step-header">
                    <div class="wizard-step-icon">${stage.icon}</div>
                    <div class="wizard-step-info">
                        <div class="wizard-step-title">${stage.title}</div>
                        <div class="wizard-step-duration">⏱️ ${stage.duration_minutes} min</div>
                    </div>
                    <div class="wizard-step-status">${statusIcon}</div>
                </div>
            </div>
        `;
    }

    /**
     * Render diagram container
     */
    renderDiagram(diagram) {
        if (!diagram || !diagram.mermaid_code) return '';
        
        // Generate unique ID for this diagram
        const diagramId = `diagram-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        
        return `
            <div class="diagram-container">
                <h3 class="diagram-title">📊 ${diagram.title}</h3>
                <div class="mermaid" id="${diagramId}">
${diagram.mermaid_code}
                </div>
            </div>
        `;
    }

    /**
     * Render stage navigation pills (DEPRECATED - replaced by wizard stepper)
     */
    renderStageNavigation() {
        return ''; // Removed in wizard design
    }

    /**
     * Render individual stage card (DEPRECATED)
     */
    renderStageCard(stage) {
        return ''; // Removed in wizard design
    }

    /**
     * Render stage content based on stage ID
     */
    renderStageContent(stage) {
        const contentMethod = `renderStage${stage.id}Content`;
        if (typeof this[contentMethod] === 'function') {
            return `
                <div class="stage-content" id="stage-content-${stage.id}" role="tabpanel">
                    ${this.renderStageHeader(stage)}
                    ${this[contentMethod](stage.content, stage)}
                    ${this.renderCompletionFooter(stage)}
                </div>
            `;
        }
        return '<div class="stage-content"><p>Content not available</p></div>';
    }

    /**
     * Render stage header with centered icon and yellow badge
     */
    renderStageHeader(stage) {
        return `
            <div class="step-badge">
                <div class="step-badge-label">STEP</div>
                <div>${stage.id}</div>
            </div>
            <div class="stage-header">
                <span class="stage-icon-large">${stage.icon}</span>
                <h2 class="stage-content-title">${stage.title}</h2>
                <p class="stage-description">${stage.description}</p>
                <div class="stage-actions">
                    <span class="stage-duration-badge">⏱️ ${stage.duration_minutes} minutes</span>
                </div>
            </div>
        `;
    }

    /**
     * Render completion footer with Mark as Complete button
     */
    renderCompletionFooter(stage) {
        const isCompleted = this.completedStages.has(stage.id);
        const nextStage = this.data.stages.find(s => s.order === stage.order + 1);
        
        return `
            <div class="stage-completion-footer">
                <button class="btn-mark-complete ${isCompleted ? 'completed' : ''}" 
                        data-stage-id="${stage.id}"
                        data-has-next="${nextStage ? 'true' : 'false'}"
                        data-next-stage-id="${nextStage ? nextStage.id : ''}">
                    ${isCompleted ? '✅ Completed' : '☐ Mark as Complete'}
                </button>
            </div>
        `;
    }

    /**
     * Stage 1: Project Overview
     */
    renderStage1Content(content, stage) {
        return `
            <div class="stage-content-body">
                ${stage.diagram ? this.renderDiagram(stage.diagram) : ''}
                ${this.renderProjectInfo(content.project_info)}
                ${this.renderProjectScale(content.scale)}
                ${this.renderTechStack(content.tech_stack)}
                ${this.renderHealthMetrics(content.health_metrics)}
                ${this.renderTeamInfo(content.team_info)}
                ${this.renderLearningPoints(content.learning_points)}
            </div>
        `;
    }

    renderProjectInfo(info) {
        return `
            <div class="content-section">
                <h3 class="section-title">📋 Project Information</h3>
                <div class="info-grid">
                    <div class="info-card">
                        <div class="info-label">Project Name</div>
                        <div class="info-value">${info.name}</div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">Type</div>
                        <div class="info-value">${info.type}</div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">Architecture</div>
                        <div class="info-value">${info.architecture}</div>
                    </div>
                </div>
                <div class="info-description">
                    <p>${info.description}</p>
                </div>
            </div>
        `;
    }

    renderProjectScale(scale) {
        return `
            <div class="content-section">
                <h3 class="section-title">📊 Project Scale</h3>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-icon">📦</div>
                        <div class="metric-value">${scale.solutions}</div>
                        <div class="metric-label">Solutions</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon">🔨</div>
                        <div class="metric-value">${scale.projects}</div>
                        <div class="metric-label">Projects</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon">📄</div>
                        <div class="metric-value">${this.formatNumber(scale.total_files)}</div>
                        <div class="metric-label">Total Files</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon">💻</div>
                        <div class="metric-value">${this.formatNumber(scale.csharp_files)}</div>
                        <div class="metric-label">C# Files</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon">📏</div>
                        <div class="metric-value">${this.formatNumber(scale.total_loc)}</div>
                        <div class="metric-label">Lines of Code</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon">🧪</div>
                        <div class="metric-value">${scale.test_files}</div>
                        <div class="metric-label">Test Files</div>
                    </div>
                </div>
            </div>
        `;
    }

    renderTechStack(stack) {
        return `
            <div class="content-section">
                <h3 class="section-title">🛠️ Technology Stack</h3>
                <div class="tech-stack-grid">
                    <div class="tech-category">
                        <h4 class="tech-category-title">Primary Framework</h4>
                        <div class="tech-badge primary">${stack.primary.framework}</div>
                        <div class="tech-badge primary">${stack.primary.language}</div>
                        <span class="tech-status-badge success">${stack.primary.status}</span>
                    </div>
                    <div class="tech-category">
                        <h4 class="tech-category-title">Frontend</h4>
                        ${stack.frontend.map(tech => `<div class="tech-badge">${tech}</div>`).join('')}
                    </div>
                    <div class="tech-category">
                        <h4 class="tech-category-title">Backend</h4>
                        ${stack.backend.map(tech => `<div class="tech-badge">${tech}</div>`).join('')}
                    </div>
                    <div class="tech-category">
                        <h4 class="tech-category-title">Database & Caching</h4>
                        <div class="tech-badge">${stack.database.primary}</div>
                        <div class="tech-badge">${stack.database.cache}</div>
                        <div class="tech-badge">${stack.database.search}</div>
                    </div>
                    <div class="tech-category">
                        <h4 class="tech-category-title">Testing</h4>
                        ${stack.testing.map(tech => `<div class="tech-badge">${tech}</div>`).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    renderHealthMetrics(metrics) {
        return `
            <div class="content-section">
                <h3 class="section-title">🏥 Project Health</h3>
                <div class="health-metrics">
                    <div class="health-metric">
                        <div class="health-metric-label">Maintainability</div>
                        <div class="health-metric-bar">
                            <div class="health-metric-fill ${this.getHealthClass(metrics.maintainability_score)}" 
                                 style="width: ${metrics.maintainability_score}%">
                                ${metrics.maintainability_score}/100
                            </div>
                        </div>
                    </div>
                    <div class="health-metric">
                        <div class="health-metric-label">Test Coverage</div>
                        <div class="health-metric-bar">
                            <div class="health-metric-fill ${this.getHealthClass(metrics.test_coverage)}" 
                                 style="width: ${metrics.test_coverage}%">
                                ${metrics.test_coverage}%
                            </div>
                        </div>
                    </div>
                    <div class="health-metric">
                        <div class="health-metric-label">Code Duplication</div>
                        <div class="health-metric-value ${metrics.code_duplication < 5 ? 'success' : 'warning'}">
                            ${metrics.code_duplication}%
                        </div>
                    </div>
                    <div class="health-metric">
                        <div class="health-metric-label">Technical Debt</div>
                        <div class="health-metric-value warning">
                            ${this.formatNumber(metrics.technical_debt_hours)} hours
                        </div>
                    </div>
                </div>
                ${this.renderSecurityVulnerabilities(metrics.security_vulnerabilities)}
            </div>
        `;
    }

    renderSecurityVulnerabilities(vulns) {
        return `
            <div class="security-summary">
                <h4>Security Vulnerabilities</h4>
                <div class="vulnerability-badges">
                    <span class="vuln-badge critical">Critical: ${vulns.critical}</span>
                    <span class="vuln-badge high">High: ${vulns.high}</span>
                    <span class="vuln-badge medium">Medium: ${vulns.medium}</span>
                    <span class="vuln-badge low">Low: ${vulns.low}</span>
                </div>
            </div>
        `;
    }

    renderTeamInfo(team) {
        return `
            <div class="content-section">
                <h3 class="section-title">👥 Team & Activity</h3>
                <div class="team-stats">
                    <div class="team-stat">
                        <span class="team-stat-icon">👨‍💻</span>
                        <span class="team-stat-value">${team.total_engineers}</span>
                        <span class="team-stat-label">Engineers</span>
                    </div>
                    <div class="team-stat">
                        <span class="team-stat-icon">🌿</span>
                        <span class="team-stat-value">${team.active_branches}</span>
                        <span class="team-stat-label">Active Branches</span>
                    </div>
                    <div class="team-stat">
                        <span class="team-stat-icon">📝</span>
                        <span class="team-stat-value">${team.avg_commits_per_week}</span>
                        <span class="team-stat-label">Commits/Week</span>
                    </div>
                    <div class="team-stat">
                        <span class="team-stat-icon">🚀</span>
                        <span class="team-stat-value">${team.deployment_frequency}</span>
                        <span class="team-stat-label">Deployments</span>
                    </div>
                </div>
            </div>
        `;
    }

    renderLearningPoints(points) {
        return `
            <div class="content-section learning-points">
                <h3 class="section-title">💡 Key Learning Points</h3>
                <ul class="learning-points-list">
                    ${points.map(point => `<li>${point}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    /**
     * Stage 2: Solution Structure
     */
    renderStage2Content(content, stage) {
        return `
            <div class="stage-content-body">
                ${stage.diagram ? this.renderDiagram(stage.diagram) : ''}
                ${this.renderSolutions(content.solutions)}
                ${this.renderArchitecturePatterns(content.architecture_patterns)}
                ${this.renderNavigationTips(content.navigation_tips)}
            </div>
        `;
    }

    renderSolutions(solutions) {
        return `
            <div class="content-section">
                <h3 class="section-title">📁 Solutions Overview</h3>
                <div class="solutions-list">
                    ${solutions.map((solution, idx) => this.renderSolution(solution, idx)).join('')}
                </div>
            </div>
        `;
    }

    renderSolution(solution, idx) {
        return `
            <details class="solution-panel">
                <summary class="solution-summary">
                    <div class="solution-info">
                        <h4 class="solution-name">${solution.name}</h4>
                        <p class="solution-description">${solution.description}</p>
                    </div>
                    <div class="solution-meta">
                        <span class="solution-project-count">${solution.project_count} projects</span>
                        <svg class="chevron-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
                            <path d="M5 7.5L10 12.5L15 7.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </div>
                </summary>
                <div class="solution-content">
                    ${solution.projects ? solution.projects.map(proj => this.renderProject(proj)).join('') : ''}
                </div>
            </details>
        `;
    }

    renderProject(project) {
        return `
            <div class="project-card">
                <div class="project-header">
                    <h5 class="project-name">${project.name}</h5>
                    <span class="project-type-badge">${project.type}</span>
                </div>
                <p class="project-path">${project.path}</p>
                ${project.responsibilities ? `
                    <div class="project-responsibilities">
                        <strong>Responsibilities:</strong>
                        <ul>
                            ${project.responsibilities.map(resp => `<li>${resp}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                <div class="project-stats">
                    ${project.file_count ? `<span>📄 ${project.file_count} files</span>` : ''}
                    ${project.loc ? `<span>📏 ${this.formatNumber(project.loc)} LOC</span>` : ''}
                    ${project.test_count ? `<span>🧪 ${project.test_count} tests</span>` : ''}
                </div>
                ${project.dependencies && project.dependencies.length > 0 ? `
                    <div class="project-dependencies">
                        <strong>Dependencies:</strong> ${project.dependencies.join(', ')}
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderArchitecturePatterns(patterns) {
        return `
            <div class="content-section">
                <h3 class="section-title">🏛️ Architecture Patterns</h3>
                <ul class="patterns-list">
                    ${patterns.map(pattern => `<li class="pattern-item">${pattern}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    renderNavigationTips(tips) {
        return `
            <div class="content-section tips-section">
                <h3 class="section-title">🧭 Navigation Tips</h3>
                <ul class="tips-list">
                    ${tips.map(tip => `<li class="tip-item">${tip}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    /**
     * Stage 3: Entry Points & Controllers
     */
    renderStage3Content(content, stage) {
        return `
            <div class="stage-content-body">
                ${stage.diagram ? this.renderDiagram(stage.diagram) : ''}
                ${this.renderEntryPoints(content.entry_points)}
                ${this.renderControllers(content.controllers)}
                ${this.renderRequestFlow(content.request_flow)}
                ${this.renderLearningPoints(content.learning_points)}
            </div>
        `;
    }

    renderEntryPoints(entryPoints) {
        return `
            <div class="content-section">
                <h3 class="section-title">🚪 Application Entry Points</h3>
                <div class="entry-points-grid">
                    ${this.renderEntryPoint('Web Application', entryPoints.web_app)}
                    ${this.renderEntryPoint('API', entryPoints.api)}
                </div>
            </div>
        `;
    }

    renderEntryPoint(title, entryPoint) {
        return `
            <div class="entry-point-card">
                <h4 class="entry-point-title">${title}</h4>
                <div class="entry-point-file">${entryPoint.file}</div>
                <div class="entry-point-meta">${entryPoint.loc} LOC</div>
                <div class="entry-point-responsibilities">
                    <strong>Responsibilities:</strong>
                    <ul>
                        ${entryPoint.responsibilities.map(resp => `<li>${resp}</li>`).join('')}
                    </ul>
                </div>
                ${entryPoint.key_configurations ? `
                    <div class="entry-point-config">
                        <strong>Key Configurations:</strong>
                        <ul>
                            ${entryPoint.key_configurations.map(config => `<li>${config}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderControllers(controllers) {
        return `
            <div class="content-section">
                <h3 class="section-title">🎮 API Controllers</h3>
                <div class="controllers-list">
                    ${controllers.map((controller, idx) => this.renderController(controller, idx)).join('')}
                </div>
            </div>
        `;
    }

    renderController(controller, idx) {
        const riskClass = this.getRiskClass(controller.risk_level);
        const riskIcon = this.getRiskIcon(controller.risk_level);
        
        return `
            <details class="controller-panel ${riskClass}">
                <summary class="controller-summary">
                    <div class="controller-info">
                        <h4 class="controller-name">${controller.name}</h4>
                        ${controller.alert ? `<div class="controller-alert">${controller.alert}</div>` : ''}
                        <div class="controller-meta-aligned">
                            <span class="complexity-badge ${this.getComplexityClass(controller.complexity)}">
                                Complexity: ${controller.complexity}
                            </span>
                            <span class="risk-badge ${riskClass}" title="${controller.risk_level}">${riskIcon}</span>
                        </div>
                    </div>
                    <svg class="chevron-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
                        <path d="M5 7.5L10 12.5L15 7.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </summary>
                <div class="controller-content">
                    <div class="controller-stats">
                        <span>📄 ${controller.loc} LOC</span>
                        <span>🔌 ${controller.endpoints} endpoints</span>
                    </div>
                    <div class="controller-responsibilities">
                        <strong>Responsibilities:</strong>
                        <ul>
                            ${controller.responsibilities.map(resp => `<li>${resp}</li>`).join('')}
                        </ul>
                    </div>
                    ${controller.key_methods ? `
                        <div class="controller-methods">
                            <strong>Key Methods:</strong>
                            <ul>
                                ${controller.key_methods.map(method => `<li>${method}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                    ${controller.dependencies ? `
                        <div class="controller-dependencies">
                            <strong>Dependencies:</strong>
                            <ul>
                                ${controller.dependencies.map(dep => `<li>${dep}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                    ${controller.refactoring_suggestions ? `
                        <div class="refactoring-suggestions">
                            <strong>🔧 Refactoring Suggestions:</strong>
                            <ul>
                                ${controller.refactoring_suggestions.map(sug => `<li>${sug}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            </details>
        `;
    }

    renderRequestFlow(requestFlow) {
        return `
            <div class="content-section">
                <h3 class="section-title">🔄 Request Flow</h3>
                <div class="request-flow-diagram">
                    <h4>Typical Request Flow:</h4>
                    <ol class="flow-steps">
                        ${requestFlow.typical_flow.map(step => `<li>${step}</li>`).join('')}
                    </ol>
                </div>
                ${requestFlow.example ? `
                    <div class="flow-example">
                        <h4>Example: ${requestFlow.example.scenario}</h4>
                        <ol class="flow-steps example">
                            ${requestFlow.example.steps.map(step => `<li>${step}</li>`).join('')}
                        </ol>
                    </div>
                ` : ''}
            </div>
        `;
    }

    /**
     * Stage 4: Core Business Logic
     */
    renderStage4Content(content, stage) {
        return `
            <div class="stage-content-body">
                ${stage.diagram ? this.renderDiagram(stage.diagram) : ''}
                ${this.renderServiceLayer(content.service_layer)}
                ${this.renderKeyServices(content.key_services)}
                ${this.renderDesignPatterns(content.design_patterns)}
                ${this.renderBusinessRules(content.business_rules)}
                ${this.renderLearningPoints(content.learning_points)}
            </div>
        `;
    }

    renderServiceLayer(serviceLayer) {
        return `
            <div class="content-section">
                <h3 class="section-title">🧩 Service Layer Overview</h3>
                <div class="service-layer-info">
                    <p><strong>Location:</strong> ${serviceLayer.location}</p>
                    <div class="service-layer-stats">
                        <span>📄 ${serviceLayer.file_count} files</span>
                        <span>📏 ${this.formatNumber(serviceLayer.total_loc)} LOC</span>
                    </div>
                    <p class="service-layer-description">${serviceLayer.description}</p>
                </div>
            </div>
        `;
    }

    renderKeyServices(services) {
        return `
            <div class="content-section">
                <h3 class="section-title">🔑 Key Services</h3>
                <div class="services-list">
                    ${services.map((service, idx) => this.renderService(service, idx)).join('')}
                </div>
            </div>
        `;
    }

    renderService(service, idx) {
        const riskClass = this.getRiskClass(service.risk_level);
        const riskIcon = this.getRiskIcon(service.risk_level);
        
        return `
            <details class="service-panel ${riskClass}">
                <summary class="service-summary">
                    <div class="service-info">
                        <h4 class="service-name">${service.name}</h4>
                        ${service.alert ? `<div class="service-alert">${service.alert}</div>` : ''}
                        <div class="service-file">${service.file}</div>
                        <div class="service-meta-aligned">
                            <span class="complexity-badge ${this.getComplexityClass(service.complexity)}">
                                Complexity: ${service.complexity}
                            </span>
                            <span class="risk-badge ${riskClass}" title="${service.risk_level}">${riskIcon}</span>
                        </div>
                    </div>
                    <svg class="chevron-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
                        <path d="M5 7.5L10 12.5L15 7.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </summary>
                <div class="service-content">
                    <div class="service-stats">
                        <span>📄 ${this.formatNumber(service.loc)} LOC</span>
                    </div>
                    <div class="service-responsibilities">
                        <strong>Responsibilities:</strong>
                        <ul>
                            ${service.responsibilities.map(resp => `<li>${resp}</li>`).join('')}
                        </ul>
                    </div>
                    ${service.key_methods ? `
                        <div class="service-methods">
                            <strong>Key Methods:</strong>
                            ${service.key_methods.map(method => this.renderServiceMethod(method)).join('')}
                        </div>
                    ` : ''}
                    ${service.dependencies ? `
                        <div class="service-dependencies">
                            <strong>Dependencies:</strong>
                            <ul>
                                ${service.dependencies.map(dep => `<li>${dep}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                    ${service.refactoring_priority ? `
                        <div class="refactoring-info">
                            <div class="refactoring-header">
                                <strong>🔧 Refactoring Recommended</strong>
                                <span class="priority-badge ${service.refactoring_priority}">${service.refactoring_priority} priority</span>
                            </div>
                            ${service.suggested_refactorings ? `
                                <ul class="refactoring-list">
                                    ${service.suggested_refactorings.map(ref => `<li>${ref}</li>`).join('')}
                                </ul>
                            ` : ''}
                            ${service.estimated_refactoring_time ? `
                                <p class="refactoring-estimate">Estimated time: ${service.estimated_refactoring_time}</p>
                            ` : ''}
                        </div>
                    ` : ''}
                </div>
            </details>
        `;
    }

    renderServiceMethod(method) {
        if (typeof method === 'string') {
            return `<div class="service-method-simple">${method}</div>`;
        }
        
        return `
            <div class="service-method">
                <div class="method-header">
                    <span class="method-name">${method.name}</span>
                    <span class="method-complexity ${this.getComplexityClass(method.complexity)}">
                        C: ${method.complexity}
                    </span>
                    <span class="method-loc">${method.loc} LOC</span>
                </div>
                <p class="method-description">${method.description}</p>
            </div>
        `;
    }

    renderDesignPatterns(patterns) {
        return `
            <div class="content-section">
                <h3 class="section-title">🎨 Design Patterns</h3>
                <div class="patterns-list">
                    ${patterns.map((pattern, idx) => this.renderPattern(pattern, idx)).join('')}
                </div>
            </div>
        `;
    }

    renderPattern(pattern, idx) {
        return `
            <details class="pattern-panel">
                <summary class="pattern-summary">
                    <div class="pattern-info">
                        <h4 class="pattern-name">${pattern.pattern}</h4>
                        <p class="pattern-usage-brief">${pattern.usage}</p>
                    </div>
                    <svg class="chevron-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
                        <path d="M5 7.5L10 12.5L15 7.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </summary>
                <div class="pattern-content">
                    <div class="pattern-usage-full">
                        <strong>Usage:</strong>
                        <p>${pattern.usage}</p>
                    </div>
                    <div class="pattern-example">
                        <strong>Example:</strong>
                        <p>${pattern.example}</p>
                    </div>
                </div>
            </details>
        `;
    }

    renderBusinessRules(rules) {
        return `
            <div class="content-section">
                <h3 class="section-title">📜 Business Rules</h3>
                <ul class="business-rules-list">
                    ${rules.map(rule => `<li class="business-rule">${rule}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    /**
     * Stage 5: Data Layer & Persistence
     */
    renderStage5Content(content, stage) {
        return `
            <div class="stage-content-body">
                ${stage.diagram ? this.renderDiagram(stage.diagram) : ''}
                ${this.renderDataAccessOverview(content)}
                ${this.renderDbContext(content.db_context)}
                ${this.renderKeyEntities(content.key_entities)}
                ${this.renderRepositories(content.repositories)}
                ${this.renderQueryOptimization(content.query_optimization)}
                ${this.renderCachingStrategy(content.caching_strategy)}
                ${this.renderLearningPoints(content.learning_points)}
            </div>
        `;
    }

    renderDataAccessOverview(content) {
        return `
            <div class="content-section">
                <h3 class="section-title">💾 Data Access Overview</h3>
                <div class="data-access-info">
                    <div class="info-row">
                        <strong>Pattern:</strong> ${content.data_access_pattern}
                    </div>
                    <div class="info-row">
                        <strong>ORM:</strong> ${content.orm}
                    </div>
                    <div class="info-row">
                        <strong>Database:</strong> ${content.database.type}
                    </div>
                    <div class="info-row">
                        <strong>Location:</strong> ${content.location}
                    </div>
                </div>
            </div>
        `;
    }

    renderDbContext(dbContext) {
        return `
            <div class="content-section">
                <h3 class="section-title">🗄️ Database Context</h3>
                <div class="dbcontext-card">
                    <h4>${dbContext.name}</h4>
                    <p class="dbcontext-file">${dbContext.file}</p>
                    <div class="dbcontext-stats">
                        <span>📄 ${dbContext.loc} LOC</span>
                        <span>📊 ${dbContext.entity_count} entities</span>
                    </div>
                    <div class="dbcontext-responsibilities">
                        <strong>Responsibilities:</strong>
                        <ul>
                            ${dbContext.responsibilities.map(resp => `<li>${resp}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            </div>
        `;
    }

    renderKeyEntities(entities) {
        return `
            <div class="content-section">
                <h3 class="section-title">📊 Key Entities</h3>
                <div class="entities-list">
                    ${entities.map((entity, idx) => this.renderEntity(entity, idx)).join('')}
                </div>
            </div>
        `;
    }

    renderEntity(entity, idx) {
        return `
            <details class="entity-panel">
                <summary class="entity-summary">
                    <div class="entity-info">
                        <h4 class="entity-name">${entity.name}</h4>
                        <span class="entity-table">Table: ${entity.table}</span>
                    </div>
                    <svg class="chevron-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
                        <path d="M5 7.5L10 12.5L15 7.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </summary>
                <div class="entity-content">
                    ${entity.properties ? `
                        <div class="entity-properties">
                            <strong>Properties:</strong>
                            <ul class="properties-list">
                                ${entity.properties.map(prop => `<li><code>${prop}</code></li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                    ${entity.relationships ? `
                        <div class="entity-relationships">
                            <strong>Relationships:</strong>
                            <ul>
                                ${entity.relationships.map(rel => `<li>${rel}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                    ${entity.indexes ? `
                        <div class="entity-indexes">
                            <strong>Indexes:</strong>
                            <ul>
                                ${entity.indexes.map(idx => `<li><code>${idx}</code></li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            </details>
        `;
    }

    renderRepositories(repositories) {
        return `
            <div class="content-section">
                <h3 class="section-title">📚 Repositories</h3>
                <div class="repositories-list">
                    ${repositories.map(repo => this.renderRepository(repo)).join('')}
                </div>
            </div>
        `;
    }

    renderRepository(repo) {
        return `
            <div class="repository-card">
                <h4 class="repository-name">${repo.name}</h4>
                <p class="repository-file">${repo.file}</p>
                <p class="repository-implements">Implements: <code>${repo.implements}</code></p>
                ${repo.key_methods ? `
                    <div class="repository-methods">
                        <strong>Key Methods:</strong>
                        <ul>
                            ${repo.key_methods.map(method => `<li>${method}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderQueryOptimization(optimizations) {
        return `
            <div class="content-section">
                <h3 class="section-title">⚡ Query Optimization</h3>
                <div class="optimizations-list">
                    ${optimizations.map(opt => this.renderOptimization(opt)).join('')}
                </div>
            </div>
        `;
    }

    renderOptimization(opt) {
        return `
            <div class="optimization-card">
                <h4 class="optimization-technique">${opt.technique}</h4>
                <p class="optimization-usage">${opt.usage}</p>
                <div class="optimization-example">
                    <strong>Example:</strong>
                    <code>${opt.example}</code>
                </div>
            </div>
        `;
    }

    renderCachingStrategy(caching) {
        return `
            <div class="content-section">
                <h3 class="section-title">🚀 Caching Strategy</h3>
                <div class="caching-info">
                    <div class="cache-level">
                        <strong>L1 Cache:</strong> ${caching.l1_cache}
                    </div>
                    <div class="cache-level">
                        <strong>L2 Cache:</strong> ${caching.l2_cache}
                    </div>
                    ${caching.cached_entities ? `
                        <div class="cached-entities">
                            <strong>Cached Entities:</strong>
                            <ul>
                                ${caching.cached_entities.map(entity => `<li>${entity}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                    <div class="cache-invalidation">
                        <strong>Invalidation:</strong> ${caching.cache_invalidation}
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Stage 6: Advanced Topics & Best Practices
     */
    renderStage6Content(content, stage) {
        return `
            <div class="stage-content-body">
                ${stage.diagram ? this.renderDiagram(stage.diagram) : ''}
                ${this.renderComplexityHotspots(content.complexity_hotspots)}
                ${this.renderCodeSmells(content.code_smells)}
                ${this.renderTechnicalDebt(content.technical_debt)}
                ${this.renderTestingStrategy(content.testing_strategy)}
                ${this.renderSecurityConsiderations(content.security_considerations)}
                ${this.renderPerformanceOptimization(content.performance_optimization)}
                ${this.renderBestPractices(content.best_practices)}
                ${this.renderImprovementRoadmap(content.improvement_roadmap)}
                ${this.renderLearningPoints(content.learning_points)}
            </div>
        `;
    }

    renderComplexityHotspots(hotspots) {
        return `
            <div class="content-section">
                <h3 class="section-title">🔥 Complexity Hotspots</h3>
                <div class="hotspots-list">
                    ${hotspots.slice(0, 5).map((hotspot, idx) => this.renderHotspot(hotspot, idx)).join('')}
                </div>
            </div>
        `;
    }

    renderHotspot(hotspot, idx) {
        return `
            <details class="hotspot-panel rank-${hotspot.rank}">
                <summary class="hotspot-summary">
                    <div class="hotspot-info">
                        <span class="hotspot-rank">#${hotspot.rank}</span>
                        <h4 class="hotspot-file">${hotspot.file}</h4>
                        <span class="hotspot-category">${hotspot.category}</span>
                    </div>
                    <div class="hotspot-metrics">
                        <span class="complexity-badge very-high">${hotspot.complexity}</span>
                        <span class="loc-badge">${this.formatNumber(hotspot.loc)} LOC</span>
                        <svg class="chevron-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
                            <path d="M5 7.5L10 12.5L15 7.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </div>
                </summary>
                <div class="hotspot-content">
                    ${hotspot.issues ? `
                        <div class="hotspot-issues">
                            <strong>⚠️ Issues:</strong>
                            <ul>
                                ${hotspot.issues.map(issue => `<li>${issue}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                    <div class="hotspot-impact">
                        <strong>Impact:</strong> ${hotspot.impact}
                    </div>
                    ${hotspot.refactoring_plan ? `
                        <div class="refactoring-plan">
                            <div class="plan-header">
                                <strong>🔧 Refactoring Plan</strong>
                                <span class="priority-badge ${hotspot.refactoring_plan.priority}">${hotspot.refactoring_plan.priority}</span>
                                <span class="time-badge">${hotspot.refactoring_plan.estimated_hours}h</span>
                            </div>
                            ${hotspot.refactoring_plan.approach ? `
                                <div class="plan-approach">
                                    <strong>Approach:</strong>
                                    <ol>
                                        ${hotspot.refactoring_plan.approach.map(step => `<li>${step}</li>`).join('')}
                                    </ol>
                                </div>
                            ` : ''}
                            ${hotspot.refactoring_plan.benefits ? `
                                <div class="plan-benefits">
                                    <strong>Benefits:</strong>
                                    <ul>
                                        ${hotspot.refactoring_plan.benefits.map(benefit => `<li>${benefit}</li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                        </div>
                    ` : ''}
                </div>
            </details>
        `;
    }

    renderCodeSmells(smells) {
        return `
            <div class="content-section">
                <h3 class="section-title">👃 Code Smells</h3>
                <div class="code-smells-list">
                    ${smells.map(smell => this.renderCodeSmell(smell)).join('')}
                </div>
            </div>
        `;
    }

    renderCodeSmell(smell) {
        return `
            <div class="code-smell-card">
                <div class="smell-header">
                    <h4 class="smell-name">${smell.smell}</h4>
                    <span class="smell-count">${smell.count} occurrences</span>
                </div>
                ${smell.examples ? `
                    <div class="smell-examples">
                        <strong>Examples:</strong>
                        <ul>
                            ${smell.examples.map(ex => `<li>${ex}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                <div class="smell-fix">
                    <strong>Fix:</strong> ${smell.fix}
                </div>
            </div>
        `;
    }

    renderTechnicalDebt(debt) {
        return `
            <div class="content-section">
                <h3 class="section-title">⏱️ Technical Debt</h3>
                <div class="tech-debt-summary">
                    <div class="debt-total">
                        <span class="debt-value">${this.formatNumber(debt.total_hours)}</span>
                        <span class="debt-label">Total Hours</span>
                    </div>
                </div>
                <div class="debt-breakdown">
                    ${debt.breakdown.map(item => this.renderDebtCategory(item)).join('')}
                </div>
                ${debt.priority_areas ? `
                    <div class="debt-priorities">
                        <strong>Priority Areas:</strong>
                        <ol>
                            ${debt.priority_areas.map(area => `<li>${area}</li>`).join('')}
                        </ol>
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderDebtCategory(category) {
        return `
            <div class="debt-category">
                <div class="debt-category-header">
                    <span class="debt-category-name">${category.category}</span>
                    <span class="debt-category-hours">${category.hours}h (${category.percentage}%)</span>
                </div>
                <div class="debt-category-bar">
                    <div class="debt-category-fill" style="width: ${category.percentage}%"></div>
                </div>
                ${category.items ? `
                    <ul class="debt-items">
                        ${category.items.map(item => `<li>${item}</li>`).join('')}
                    </ul>
                ` : ''}
            </div>
        `;
    }

    renderTestingStrategy(testing) {
        return `
            <div class="content-section">
                <h3 class="section-title">🧪 Testing Strategy</h3>
                <div class="testing-coverage">
                    <div class="coverage-current">
                        <span class="coverage-label">Current:</span>
                        <span class="coverage-value">${testing.current_coverage}%</span>
                    </div>
                    <div class="coverage-target">
                        <span class="coverage-label">Target:</span>
                        <span class="coverage-value">${testing.target_coverage}%</span>
                    </div>
                </div>
                <div class="test-types">
                    ${testing.test_types.map(type => this.renderTestType(type)).join('')}
                </div>
                ${testing.gaps ? `
                    <div class="testing-gaps">
                        <strong>Coverage Gaps:</strong>
                        <ul>
                            ${testing.gaps.map(gap => `<li>${gap}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderTestType(type) {
        return `
            <div class="test-type-card">
                <div class="test-type-header">
                    <h4>${type.type}</h4>
                    <span class="test-count">${type.count} tests</span>
                </div>
                <div class="test-type-coverage">
                    <span class="coverage-label">Coverage:</span>
                    <div class="coverage-bar">
                        <div class="coverage-fill ${this.getHealthClass(type.coverage)}" 
                             style="width: ${type.coverage}%">
                            ${type.coverage}%
                        </div>
                    </div>
                </div>
                <div class="test-type-info">
                    <p><strong>Framework:</strong> ${type.framework}</p>
                    <p><strong>Location:</strong> ${type.location}</p>
                </div>
            </div>
        `;
    }

    renderSecurityConsiderations(security) {
        return `
            <div class="content-section">
                <h3 class="section-title">🔒 Security Considerations</h3>
                <div class="security-areas">
                    ${security.map(area => this.renderSecurityArea(area)).join('')}
                </div>
            </div>
        `;
    }

    renderSecurityArea(area) {
        const statusClass = area.status.toLowerCase().replace(' ', '-');
        return `
            <div class="security-area-card">
                <div class="security-area-header">
                    <h4>${area.area}</h4>
                    <span class="security-status ${statusClass}">${area.status}</span>
                </div>
                <ul class="security-details">
                    ${area.details.map(detail => `<li>${detail}</li>`).join('')}
                </ul>
                ${area.action ? `
                    <div class="security-action">
                        <strong>Action:</strong> ${area.action}
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderPerformanceOptimization(performance) {
        return `
            <div class="content-section">
                <h3 class="section-title">⚡ Performance Optimization</h3>
                <div class="performance-areas">
                    ${performance.map(area => this.renderPerformanceArea(area)).join('')}
                </div>
            </div>
        `;
    }

    renderPerformanceArea(area) {
        return `
            <div class="performance-area-card">
                <h4>${area.area}</h4>
                ${area.current ? `<p><strong>Current:</strong> ${area.current}</p>` : ''}
                ${area.target ? `<p><strong>Target:</strong> ${area.target}</p>` : ''}
                ${area.recommendations ? `
                    <div class="performance-recommendations">
                        <strong>Recommendations:</strong>
                        <ul>
                            ${area.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderBestPractices(practices) {
        return `
            <div class="content-section">
                <h3 class="section-title">✨ Best Practices</h3>
                <div class="best-practices-list">
                    ${practices.map(practice => this.renderBestPractice(practice)).join('')}
                </div>
            </div>
        `;
    }

    renderBestPractice(practice) {
        return `
            <div class="best-practice-card">
                <h4 class="practice-category">${practice.category}</h4>
                <ul class="practice-list">
                    ${practice.practices.map(p => `<li>${p}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    renderImprovementRoadmap(roadmap) {
        return `
            <div class="content-section">
                <h3 class="section-title">🗺️ Improvement Roadmap</h3>
                <div class="roadmap-timeline">
                    ${roadmap.map(quarter => this.renderRoadmapQuarter(quarter)).join('')}
                </div>
            </div>
        `;
    }

    renderRoadmapQuarter(quarter) {
        return `
            <div class="roadmap-quarter">
                <h4 class="quarter-label">${quarter.quarter}</h4>
                <ul class="quarter-goals">
                    ${quarter.goals.map(goal => `<li>${goal}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    /**
     * Render footer navigation
     */
    renderFooterNavigation(stage) {
        const prevStage = this.data.stages.find(s => s.order === stage.order - 1);
        const nextStage = this.data.stages.find(s => s.order === stage.order + 1);
        
        return `
            <div class="wizard-navigation">
                ${prevStage ? `
                    <button class="btn-nav btn-prev" data-stage-id="${prevStage.id}">
                        Previous
                    </button>
                ` : '<button class="btn-nav btn-prev" disabled>Previous</button>'}
                ${nextStage ? `
                    <button class="btn-nav btn-next" data-stage-id="${nextStage.id}">
                        Next
                    </button>
                ` : '<button class="btn-nav btn-next" disabled>Next</button>'}
            </div>
        `;
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Wizard step navigation
        document.querySelectorAll('.wizard-step').forEach(step => {
            step.addEventListener('click', (e) => {
                const stageId = parseInt(e.currentTarget.dataset.stageId);
                this.navigateToStage(stageId);
            });
        });

        // Navigation buttons
        document.querySelectorAll('.btn-nav:not([disabled])').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const stageId = parseInt(e.currentTarget.dataset.stageId);
                this.navigateToStage(stageId);
            });
        });

        // Mark complete button with auto-navigation
        document.querySelectorAll('.btn-mark-complete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const stageId = parseInt(e.currentTarget.dataset.stageId);
                const hasNext = e.currentTarget.dataset.hasNext === 'true';
                const nextStageId = parseInt(e.currentTarget.dataset.nextStageId);
                
                // Toggle completion
                this.toggleStageCompletion(stageId);
                
                // Auto-navigate to next step if exists and current step is now complete
                if (hasNext && this.completedStages.has(stageId)) {
                    setTimeout(() => {
                        this.navigateToStage(nextStageId);
                    }, 300); // Brief delay for completion animation
                }
            });
        });

        // Accordion behavior: close other panels when one opens
        document.addEventListener('toggle', (e) => {
            if (e.target.matches('details.service-panel, details.controller-panel, details.entity-panel, details.solution-panel, details.pattern-panel, details.hotspot-panel')) {
                if (e.target.open) {
                    // Close all sibling details elements in the same container
                    const container = e.target.parentElement;
                    container.querySelectorAll('details').forEach(detail => {
                        if (detail !== e.target && detail.open) {
                            detail.open = false;
                        }
                    });
                    
                    // Scroll panel into view smoothly
                    setTimeout(() => {
                        e.target.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }, 100);
                }
            }
        }, true);
    }

    /**
     * Navigate to a specific stage
     */
    navigateToStage(stageId) {
        this.currentStage = stageId;
        this.saveProgress();
        this.render();
        this.attachEventListeners();
        this.renderAllDiagrams(); // Re-render diagrams after navigation
        
        // Scroll to top after DOM updates
        setTimeout(() => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }, 50);
    }

    /**
     * Toggle stage completion
     */
    toggleStageCompletion(stageId) {
        if (this.completedStages.has(stageId)) {
            this.completedStages.delete(stageId);
        } else {
            this.completedStages.add(stageId);
        }
        this.saveProgress();
        this.render();
        this.attachEventListeners();
        this.renderAllDiagrams(); // Re-render diagrams after completion toggle
    }

    /**
     * Restore scroll position
     */
    restoreScrollPosition() {
        const scrollPos = sessionStorage.getItem('onboarding_scroll_position');
        if (scrollPos) {
            setTimeout(() => {
                window.scrollTo(0, parseInt(scrollPos));
            }, 100);
        }
    }

    /**
     * Utility: Format number with commas
     */
    formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }

    /**
     * Utility: Get health class based on score
     */
    getHealthClass(score) {
        if (score >= 80) return 'excellent';
        if (score >= 60) return 'good';
        if (score >= 40) return 'fair';
        return 'poor';
    }

    /**
     * Utility: Get complexity class
     */
    getComplexityClass(complexity) {
        if (complexity > 500) return 'very-high';
        if (complexity > 300) return 'high';
        if (complexity > 150) return 'medium';
        return 'low';
    }

    /**
     * Utility: Get risk class
     */
    getRiskClass(riskLevel) {
        if (!riskLevel) return '';
        return riskLevel.replace(' ', '-').toLowerCase();
    }

    /**
     * Utility: Get risk icon
     */
    getRiskIcon(riskLevel) {
        if (!riskLevel) return '🔵';
        const level = riskLevel.toLowerCase();
        if (level.includes('very high')) return '🔴';
        if (level.includes('high')) return '🟠';
        if (level.includes('medium')) return '🟡';
        return '🟢';
    }
}

// ES6 default export for browser modules
export default OnboardingTab;
