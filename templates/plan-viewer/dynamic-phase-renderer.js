/**
 * CORTEX 6.0 Dynamic Phase Detail Renderer
 * Loads phase data from YAML sources and renders with real-time updates
 */

class PhaseDetailRenderer {
    constructor() {
        this.phaseData = null;
        this.progressData = null;
        this.acIndexData = null;
        this.useCaseScenarios = this.initializeUseCases();
    }
    
    /**
     * Load phase data from YAML + JSON sources
     */
    async loadPhaseData(phaseNumber) {
        try {
            // Load holistic plan
            const planResponse = await fetch('../../cortex-brain/documents/cx6-holistic-analysis/holistic-snowball-plan.yaml');
            const planText = await planResponse.text();
            const plan = jsyaml.load(planText);
            
            // Load progress tracker
            const progressResponse = await fetch('../../cortex-brain/tier1/tracking/progress-tracker.json');
            this.progressData = await progressResponse.json();
            
            // Load AC-INDEX
            const acResponse = await fetch('../../cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml');
            const acText = await acResponse.text();
            this.acIndexData = jsyaml.load(acText);
            
            // Extract phase data
            const phaseKey = `phase_${phaseNumber}_${this.getPhaseKeyName(phaseNumber)}`;
            this.phaseData = plan[phaseKey];
            
            if (!this.phaseData) {
                throw new Error(`Phase ${phaseNumber} not found in plan`);
            }
            
            this.render(phaseNumber);
        } catch (error) {
            console.error('Error loading phase data:', error);
            this.renderError(error.message);
        }
    }
    
    /**
     * Get phase key name from number
     */
    getPhaseKeyName(phaseNumber) {
        const names = {
            '1': 'foundation',
            '2': 'orchestration_core',
            '3': 'feature_orchestrators',
            '4': 'intelligence'
        };
        return names[phaseNumber] || 'foundation';
    }
    
    /**
     * Render all phase sections
     */
    render(phaseNumber) {
        this.renderHeader();
        this.renderProgress();
        this.renderArchitecture();
        this.renderComponents();
        this.renderUseCases(phaseNumber);
    }
    
    /**
     * Render phase header
     */
    renderHeader() {
        const titleEl = document.getElementById('phaseTitle');
        const metaEl = document.getElementById('phaseMeta');
        
        titleEl.textContent = this.phaseData.name;
        
        const duration = `${this.phaseData.duration} | ${this.phaseData.start_date} to ${this.phaseData.end_date}`;
        const status = this.phaseData.status.replace(/_/g, ' ').toUpperCase();
        
        metaEl.innerHTML = `
            <div>${duration}</div>
            <div style="margin-top: 8px;">Status: <span style="color: var(--${this.getStatusColor(this.phaseData.status)});">${status}</span></div>
            <div style="margin-top: 8px; color: var(--text-secondary); font-size: 0.9em;">${this.phaseData.description}</div>
        `;
    }
    
    /**
     * Render progress bar and stats
     */
    renderProgress() {
        // Calculate progress based on completed AC-IDs
        const totalACs = this.countPhaseACs();
        const completedACs = this.countCompletedACs();
        const progressPercent = totalACs > 0 ? Math.round((completedACs / totalACs) * 100) : 0;
        
        const progressBar = document.getElementById('progressBar');
        progressBar.style.width = `${progressPercent}%`;
        progressBar.textContent = `${progressPercent}%`;
        
        // Render stats
        const statsEl = document.getElementById('progressStats');
        statsEl.innerHTML = `
            <div class="progress-stat">
                <div class="progress-stat-label">AC-IDs Completed</div>
                <div class="progress-stat-value">${completedACs}<span style="font-size: 0.5em; color: var(--text-secondary);">/${totalACs}</span></div>
            </div>
            <div class="progress-stat">
                <div class="progress-stat-label">Components</div>
                <div class="progress-stat-value">${Object.keys(this.phaseData.components).length}</div>
            </div>
            <div class="progress-stat">
                <div class="progress-stat-label">Priority</div>
                <div class="progress-stat-value" style="color: var(--accent-color);">${this.phaseData.priority}</div>
            </div>
            <div class="progress-stat">
                <div class="progress-stat-label">Duration</div>
                <div class="progress-stat-value">${this.phaseData.duration}</div>
            </div>
        `;
    }
    
    /**
     * Render architecture diagram
     */
    renderArchitecture() {
        const components = this.phaseData.components;
        let mermaidCode = 'graph TD\n';
        
        // Add nodes for each component
        Object.entries(components).forEach(([key, component]) => {
            const componentId = key.replace(/_/g, '');
            mermaidCode += `  ${componentId}["${component.name}"]\n`;
            
            // Add dependency edges
            if (component.dependencies && component.dependencies.length > 0) {
                component.dependencies.forEach(dep => {
                    const depId = this.findComponentId(dep);
                    if (depId) {
                        mermaidCode += `  ${depId} --> ${componentId}\n`;
                    }
                });
            }
            
            // Style by priority
            if (component.priority === 'CRITICAL') {
                mermaidCode += `  style ${componentId} fill:#ff006e,stroke:#fff,stroke-width:2px\n`;
            } else if (component.priority === 'HIGH') {
                mermaidCode += `  style ${componentId} fill:#00d4ff,stroke:#fff,stroke-width:2px\n`;
            } else {
                mermaidCode += `  style ${componentId} fill:#7b2cbf,stroke:#fff,stroke-width:2px\n`;
            }
        });
        
        const diagramEl = document.getElementById('architectureDiagram');
        diagramEl.textContent = mermaidCode;
        diagramEl.removeAttribute('data-processed');
        
        // Re-initialize mermaid for this element
        mermaid.init(undefined, diagramEl);
    }
    
    /**
     * Find component ID from AC-ID
     */
    findComponentId(acId) {
        const components = this.phaseData.components;
        
        for (const [key, component] of Object.entries(components)) {
            if (component.ac_ids && component.ac_ids.includes(acId)) {
                return key.replace(/_/g, '');
            }
        }
        
        return null;
    }
    
    /**
     * Render components grid
     */
    renderComponents() {
        const gridEl = document.getElementById('componentsGrid');
        const components = this.phaseData.components;
        
        gridEl.innerHTML = '';
        
        Object.entries(components).forEach(([key, component]) => {
            const card = document.createElement('div');
            card.className = 'component-card';
            
            const status = this.getComponentStatus(component);
            const capabilities = component.capabilities || [];
            const evidence = component.evidence_bundle || {};
            
            card.innerHTML = `
                <div class="component-header">
                    <div class="component-name">${component.name}</div>
                    <div class="component-status status-${status.toLowerCase()}">${status}</div>
                </div>
                
                <div class="component-description">
                    ${this.getComponentDescription(component)}
                </div>
                
                <div class="ac-badges">
                    ${component.ac_ids.map(acId => 
                        `<span class="ac-badge" onclick="window.showACDetail('${acId}')">${acId}</span>`
                    ).join('')}
                </div>
                
                <div class="component-details">
                    <div class="detail-item">
                        <div class="detail-label">Priority</div>
                        <div class="detail-value">${component.priority}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Duration</div>
                        <div class="detail-value">${component.duration}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Owner</div>
                        <div class="detail-value">${component.owner}</div>
                    </div>
                    ${capabilities.length > 0 ? `
                    <div class="detail-item" style="grid-column: 1 / -1;">
                        <div class="detail-label">Key Capabilities</div>
                        <ul style="margin-top: 8px; padding-left: 20px; color: var(--text-secondary);">
                            ${capabilities.slice(0, 3).map(cap => `<li>${cap}</li>`).join('')}
                        </ul>
                    </div>
                    ` : ''}
                </div>
            `;
            
            gridEl.appendChild(card);
        });
    }
    
    /**
     * Get component description
     */
    getComponentDescription(component) {
        if (this.phaseData.why_first && component === Object.values(this.phaseData.components)[0]) {
            return this.phaseData.why_first;
        }
        
        if (component.capabilities && component.capabilities.length > 0) {
            return component.capabilities.slice(0, 2).join('. ') + '.';
        }
        
        return 'Core infrastructure component for CORTEX 6.0 implementation.';
    }
    
    /**
     * Render use cases
     */
    renderUseCases(phaseNumber) {
        const containerEl = document.getElementById('useCasesContainer');
        const useCases = this.useCaseScenarios[`phase${phaseNumber}`] || [];
        
        if (useCases.length === 0) {
            containerEl.innerHTML = '<div class="loading">No use cases defined for this phase yet.</div>';
            return;
        }
        
        containerEl.innerHTML = useCases.map(useCase => `
            <div class="use-case-card">
                <div class="use-case-title">${useCase.title}</div>
                <div class="use-case-description">${useCase.description}</div>
                ${useCase.example ? `
                <div class="use-case-example">${useCase.example}</div>
                ` : ''}
            </div>
        `).join('');
    }
    
    /**
     * Count total AC-IDs in phase
     */
    countPhaseACs() {
        let count = 0;
        Object.values(this.phaseData.components).forEach(component => {
            count += (component.ac_ids || []).length;
        });
        return count;
    }
    
    /**
     * Count completed AC-IDs
     */
    countCompletedACs() {
        // This would check actual completion from progress-tracker.json
        // For now, return 0 as implementation hasn't started
        return 0;
    }
    
    /**
     * Get component status
     */
    getComponentStatus(component) {
        // Check if component is in progress or completed
        if (this.phaseData.status === 'ready_to_implement') {
            return 'PENDING';
        } else if (this.phaseData.status === 'in_progress') {
            return 'IN_PROGRESS';
        }
        return 'PENDING';
    }
    
    /**
     * Get status color
     */
    getStatusColor(status) {
        const colors = {
            'ready_to_implement': 'success-color',
            'in_progress': 'primary-color',
            'blocked_by_phase_1': 'warning-color',
            'blocked_by_phase_2': 'warning-color',
            'blocked_by_phase_3': 'warning-color',
            'completed': 'success-color'
        };
        return colors[status] || 'text-secondary';
    }
    
    /**
     * Initialize use case scenarios
     */
    initializeUseCases() {
        return {
            phase1: [
                {
                    title: '🔍 Audit Trail for Compliance',
                    description: 'Enterprise organizations need complete audit trails for compliance (SOX, GDPR, HIPAA). The Enhanced Audit Logger provides tamper-evident logging with hash chain integrity.',
                    example: 'Scenario: Financial services company needs to prove no unauthorized changes to trading algorithms.\n\nSolution: AC-AUDIT-007 hash chain validates every code change with cryptographic proof.\n\nResult: Pass SOX audit with complete change history and integrity verification.'
                },
                {
                    title: '🛡️ Governance Enforcement',
                    description: 'Large teams need consistent code quality without manual reviews. 4-Tier Governance automatically enforces SKULL rules, company practices, and learned patterns.',
                    example: 'Scenario: 50-person engineering team with varying skill levels.\n\nSolution: AC-GOV-001 to AC-GOV-005 merge rules with Tier 0 precedence, blocking violations before commit.\n\nResult: Zero hardcoded secrets, 100% TDD compliance, consistent file organization.'
                },
                {
                    title: '💾 State Recovery After Failures',
                    description: 'Long-running AI operations can fail mid-execution. State Manager enables checkpoint recovery without losing work.',
                    example: 'Scenario: 3-hour code refactoring interrupted by power outage.\n\nSolution: AC-STATE-002 atomic state transitions with rollback capability.\n\nResult: Resume from last checkpoint, no work lost, no corrupted state.'
                },
                {
                    title: '🔒 Security Gate for Destructive Operations',
                    description: 'Production systems need approval workflows for high-risk operations like database migrations or file deletions.',
                    example: 'Scenario: Junior dev requests bulk file deletion.\n\nSolution: AC-SECURITY-005 approval state machine blocks operation pending senior review.\n\nResult: Prevents accidental data loss, audit trail of approval process.'
                }
            ],
            
            phase2: [
                {
                    title: '🎯 Automated Development Workflow',
                    description: 'MasterOrchestrator orchestrates the entire development lifecycle from request to deployment, eliminating manual coordination.',
                    example: 'Scenario: "Implement user authentication with OAuth2 and JWT".\n\nSolution: MasterOrchestrator (AC-ORCH-006) → TodoManager creates tasks → TDD-Master generates tests → Implementation → Validation.\n\nResult: Fully tested auth system with evidence bundle, zero manual steps.'
                },
                {
                    title: '🧪 TDD Enforcement for Quality',
                    description: 'Ensure 100% of production code has tests by blocking direct coding, requiring TDD-Master gateway for all development.',
                    example: 'Scenario: Developer tries to commit code without tests.\n\nSolution: CORE-019 + AC-TDD-001 enforce RED→GREEN→REFACTOR workflow.\n\nResult: All code has tests before merge, test coverage never drops below 80%.'
                },
                {
                    title: '📋 Intelligent Planning from Git History',
                    description: 'Planning v5 searches git history before creating new code, reusing existing implementations instead of rebuilding.',
                    example: 'Scenario: "Implement file upload with S3".\n\nSolution: AC-PLAN-003 searches CORTEX-4.0, finds existing S3Uploader class.\n\nResult: Reuse + adapt in 30 minutes vs rebuild in 3 hours.'
                },
                {
                    title: '🔀 Deterministic Routing with Conflict Detection',
                    description: 'Multiple orchestrators handle overlapping patterns. Routing engine detects conflicts and ensures correct orchestrator selection.',
                    example: 'Scenario: "implement new feature" could match TDD-Master or Planning orchestrator.\n\nSolution: AC-ROUTE-004 unicode normalization + priority-based tie-breaking.\n\nResult: Consistent routing, no ambiguity, audit trail of routing decisions.'
                }
            ],
            
            phase3: [
                {
                    title: '🔄 Azure DevOps Work Item Synchronization',
                    description: 'Keep CORTEX tasks synchronized with ADO work items, automatically updating status, linking commits, and tracking progress.',
                    example: 'Scenario: Product manager creates user story in ADO.\n\nSolution: AC-ADO-002 creates corresponding TodoManager tasks, syncs status bidirectionally.\n\nResult: Developers work in CORTEX, managers see real-time progress in ADO.'
                },
                {
                    title: '🧹 Safe Automated Cleanup',
                    description: 'Vacuum orchestrator uses knowledge graph to safely identify unused files, preventing accidental deletion of dynamically loaded code.',
                    example: 'Scenario: Repository has 2000+ files after 2 years of development.\n\nSolution: AC-VAC-003 + AC-CRAWLER-002 build dependency graph → AC-VAC-004 identifies 300 unused files.\n\nResult: Repository size reduced 40%, zero broken imports.'
                },
                {
                    title: '🔍 Root Cause Investigation',
                    description: 'Investigation orchestrator analyzes test failures, git history, and code changes to identify root causes automatically.',
                    example: 'Scenario: Production bug - authentication fails intermittently.\n\nSolution: AC-INV-002 analyzes recent commits, identifies race condition in token refresh.\n\nResult: Root cause found in 10 minutes vs 3 hours of manual debugging.'
                },
                {
                    title: '📊 Progressive Rollout with DRY_RUN',
                    description: 'Test new orchestrators safely with DRY_RUN mode before activating, preventing production incidents from untested code.',
                    example: 'Scenario: New database migration orchestrator ready for production.\n\nSolution: AC-ROLLOUT-SIMPLE-001 runs in DRY_RUN for 1 week, logs intended operations.\n\nResult: Discover edge case in rollback logic before production deployment.'
                }
            ],
            
            phase4: [
                {
                    title: '🤖 Fuzzy Intent Classification',
                    description: 'LLM Intent Classifier handles ambiguous requests by understanding context and user intent beyond pattern matching.',
                    example: 'Scenario: User says "make it better" without specifying what.\n\nSolution: AC-ROUTE-003 analyzes conversation history + current file context → routes to Refinement orchestrator.\n\nResult: Accurate routing even with vague requests.'
                },
                {
                    title: '📚 Learned Patterns from Production',
                    description: 'Tier 3 Knowledge Practices automatically extract successful patterns from audit logs, suggesting optimizations to future work.',
                    example: 'Scenario: Team repeatedly implements pagination the same way.\n\nSolution: AC-KNOW-002 detects pattern, creates tier3/pagination-pattern.yaml.\n\nResult: Future implementations get pagination scaffolding automatically.'
                },
                {
                    title: '👁️ Visual Debugging with Vision API',
                    description: 'Analyze screenshots of UI bugs, compare expected vs actual states, and identify visual regressions automatically.',
                    example: 'Scenario: User reports "button looks wrong" with screenshot.\n\nSolution: AC-VISION-001 compares screenshot to design mockup, identifies 2px alignment issue.\n\nResult: Precise bug identification without developer reproducing manually.'
                }
            ]
        };
    }
    
    /**
     * Render error state
     */
    renderError(message) {
        document.getElementById('phaseTitle').textContent = 'Error Loading Phase';
        document.getElementById('phaseMeta').innerHTML = `
            <div style="color: var(--danger-color); margin-top: 10px;">
                ${message}
            </div>
            <div style="margin-top: 10px;">
                <a href="cortex-plan-viewer.html" style="color: var(--primary-color);">← Back to Dashboard</a>
            </div>
        `;
        
        document.getElementById('componentsGrid').innerHTML = '';
        document.getElementById('useCasesContainer').innerHTML = '';
    }
}

/**
 * Show AC-ID detail modal (global function)
 */
window.showACDetail = function(acId) {
    const modal = document.getElementById('acModal');
    const modalContent = document.getElementById('modalContent');
    
    // Load AC-ID details from AC-INDEX (would need to fetch in real implementation)
    modalContent.innerHTML = `
        <h2 style="margin-bottom: 20px; color: var(--primary-color);">${acId}</h2>
        
        <div style="margin-bottom: 20px;">
            <h3 style="color: var(--text-secondary); font-size: 1em; margin-bottom: 10px;">Description</h3>
            <p style="color: var(--text-primary); line-height: 1.6;">
                Detailed acceptance criteria and implementation requirements for this AC-ID.
            </p>
        </div>
        
        <div style="margin-bottom: 20px;">
            <h3 style="color: var(--text-secondary); font-size: 1em; margin-bottom: 10px;">Status</h3>
            <div class="component-status status-pending">NOT STARTED</div>
        </div>
        
        <div style="margin-bottom: 20px;">
            <h3 style="color: var(--text-secondary); font-size: 1em; margin-bottom: 10px;">Dependencies</h3>
            <p style="color: var(--text-secondary);">Loading dependencies...</p>
        </div>
        
        <div style="margin-bottom: 20px;">
            <h3 style="color: var(--text-secondary); font-size: 1em; margin-bottom: 10px;">Test Results</h3>
            <p style="color: var(--text-secondary);">No tests run yet</p>
        </div>
        
        <div>
            <h3 style="color: var(--text-secondary); font-size: 1em; margin-bottom: 10px;">Audit Trail</h3>
            <p style="color: var(--text-secondary);">No audit entries yet</p>
        </div>
    `;
    
    modal.classList.add('active');
};

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { PhaseDetailRenderer };
}
