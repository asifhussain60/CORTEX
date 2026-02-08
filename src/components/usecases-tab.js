/**
 * Phase S6: Use Cases Tab (📋) - Business Capabilities Dashboard
 * Renders detected business capabilities, flows, integrations, and stakeholder mapping
 */

class UseCasesTab {
    constructor(data = {}) {
        this.data = {
            detected_capabilities: data.detected_capabilities || [],
            business_flows: data.business_flows || [],
            integrations: data.integrations || [],
            stakeholder_mapping: data.stakeholder_mapping || {}
        };
    }

    init() {
        this.update(this.data);
    }

    /**
     * Render the complete use cases dashboard
     */
    render() {
        return `
            <div class="usecases-dashboard">
                <style>${this.styles()}</style>
                
                <div class="usecases-header">
                    <h2>Business Capabilities 📋</h2>
                    <p class="usecases-subtitle">
                        ${this.data.detected_capabilities.length} capabilities detected
                    </p>
                </div>

                <div class="usecases-grid">
                    <!-- Capabilities Section -->
                    <section class="usecases-section">
                        <h3 class="section-title">🎯 Detected Capabilities</h3>
                        <div class="capabilities-container">
                            ${this.renderCapabilities()}
                        </div>
                    </section>

                    <!-- Business Flows Section -->
                    <section class="usecases-section">
                        <h3 class="section-title">🔄 Business Flows</h3>
                        <div class="flows-container">
                            ${this.renderFlows()}
                        </div>
                    </section>

                    <!-- Integrations Section -->
                    <section class="usecases-section">
                        <h3 class="section-title">🔗 Integrations</h3>
                        <div class="integrations-container">
                            ${this.renderIntegrations()}
                        </div>
                    </section>

                    <!-- Stakeholder Mapping Section -->
                    <section class="usecases-section">
                        <h3 class="section-title">👥 Stakeholder Mapping</h3>
                        <div class="stakeholders-container">
                            ${this.renderStakeholders()}
                        </div>
                    </section>
                </div>
            </div>
        `;
    }

    /**
     * Render business capabilities with complexity and maturity
     */
    renderCapabilities() {
        if (this.data.detected_capabilities.length === 0) {
            return `
                <div class="empty-state">
                    <p>No business capabilities detected yet</p>
                </div>
            `;
        }

        return this.data.detected_capabilities
            .map((cap, idx) => this.renderCapabilityCard(cap, idx))
            .join('');
    }

    renderCapabilityCard(cap, idx) {
        const complexityColor = {
            'low': '#4CAF50',
            'medium': '#FF9800',
            'high': '#F44336'
        };
        const maturityIcon = {
            'emerging': '🌱',
            'stable': '✅',
            'mature': '⭐'
        };

        return `
            <div class="capability-card" key="${cap.id}">
                <div class="capability-header">
                    <div class="capability-title">
                        <h4>${cap.business_capability}</h4>
                        <span class="technical-name">${cap.technical_name}</span>
                    </div>
                    <div class="capability-badges">
                        <span class="maturity-badge" title="Maturity">
                            ${maturityIcon[cap.maturity] || '❓'} ${cap.maturity}
                        </span>
                    </div>
                </div>

                <p class="capability-description">${cap.description}</p>
                <p class="business-value"><strong>Business Value:</strong> ${cap.business_value}</p>

                <div class="capability-metrics">
                    <div class="metric">
                        <label>Complexity</label>
                        <div class="complexity-bar">
                            <div class="complexity-fill" 
                                style="width: ${cap.complexity === 'low' ? '33%' : cap.complexity === 'medium' ? '66%' : '100%'};
                                        background-color: ${complexityColor[cap.complexity]};">
                            </div>
                        </div>
                        <span>${cap.complexity}</span>
                    </div>
                    <div class="metric">
                        <label>Modernization</label>
                        <div class="score-circle" style="--score: ${cap.modernization_score}%">
                            <div class="score-number">${cap.modernization_score.toFixed(0)}%</div>
                        </div>
                    </div>
                </div>

                <div class="capability-stakeholders">
                    <div class="actors">
                        <strong>Actors:</strong>
                        <div class="actor-list">
                            ${cap.actors.map(a => `<span class="actor-badge">${a}</span>`).join('')}
                        </div>
                    </div>
                    <div class="systems">
                        <strong>Systems:</strong>
                        <div class="system-list">
                            ${cap.systems.map(s => `<span class="system-badge">${s}</span>`).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Render business flows with steps and success criteria
     */
    renderFlows() {
        if (this.data.business_flows.length === 0) {
            return `
                <div class="empty-state">
                    <p>No business flows defined</p>
                </div>
            `;
        }

        return this.data.business_flows
            .map((flow, idx) => this.renderFlowCard(flow, idx))
            .join('');
    }

    renderFlowCard(flow, idx) {
        return `
            <div class="flow-card" key="flow-${idx}">
                <div class="flow-header">
                    <h4>${flow.name}</h4>
                    <span class="primary-actor">${flow.primary_actor}</span>
                </div>

                <p class="flow-description">${flow.description}</p>

                <div class="flow-details">
                    <div class="flow-section">
                        <strong>Steps (${flow.steps.length})</strong>
                        <ol class="steps-list">
                            ${flow.steps.map(step => `<li>${step}</li>`).join('')}
                        </ol>
                    </div>

                    ${flow.preconditions.length > 0 ? `
                        <div class="flow-section">
                            <strong>Preconditions</strong>
                            <ul class="preconditions-list">
                                ${flow.preconditions.map(pre => `<li>✓ ${pre}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}

                    ${flow.success_criteria.length > 0 ? `
                        <div class="flow-section">
                            <strong>Success Criteria</strong>
                            <ul class="criteria-list">
                                ${flow.success_criteria.map(crit => `<li>✓ ${crit}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    /**
     * Render external system integrations
     */
    renderIntegrations() {
        if (this.data.integrations.length === 0) {
            return `
                <div class="empty-state">
                    <p>No integrations configured</p>
                </div>
            `;
        }

        const grouped = this.groupIntegrationsByType();
        
        return Object.entries(grouped)
            .map(([type, integrations]) => `
                <div class="integration-group">
                    <h5 class="integration-type">${type}</h5>
                    <div class="integration-items">
                        ${integrations.map(integ => `
                            <div class="integration-item">
                                <div class="integration-icon">🔗</div>
                                <div class="integration-info">
                                    <strong>${integ.system}</strong>
                                    <p>${integ.description}</p>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `)
            .join('');
    }

    groupIntegrationsByType() {
        const grouped = {};
        this.data.integrations.forEach(integ => {
            if (!grouped[integ.type]) {
                grouped[integ.type] = [];
            }
            grouped[integ.type].push(integ);
        });
        return grouped;
    }

    /**
     * Render stakeholder capability mapping
     */
    renderStakeholders() {
        if (Object.keys(this.data.stakeholder_mapping).length === 0) {
            return `
                <div class="empty-state">
                    <p>No stakeholder mapping defined</p>
                </div>
            `;
        }

        return Object.entries(this.data.stakeholder_mapping)
            .map(([role, capabilities]) => `
                <div class="stakeholder-card">
                    <div class="stakeholder-role">
                        <h5>${this.getRoleEmoji(role)} ${role}</h5>
                    </div>
                    <div class="capabilities-grid">
                        ${capabilities.map(cap => `
                            <div class="capability-tag">${cap}</div>
                        `).join('')}
                    </div>
                </div>
            `)
            .join('');
    }

    getRoleEmoji(role) {
        const roleEmojis = {
            'Executive': '👔',
            'Product Owner': '🎯',
            'Dev Manager': '📊',
            'Engineer': '💻',
            'Analyst': '📈',
            'Manager': '👨‍💼',
            'Support': '🆘',
            'Admin': '🔑'
        };
        return roleEmojis[role] || '👤';
    }

    /**
     * Update the dashboard with new data
     */
    update(newData) {
        this.data = {
            detected_capabilities: newData.detected_capabilities || this.data.detected_capabilities,
            business_flows: newData.business_flows || this.data.business_flows,
            integrations: newData.integrations || this.data.integrations,
            stakeholder_mapping: newData.stakeholder_mapping || this.data.stakeholder_mapping
        };
    }

    /**
     * CSS Styles for use cases dashboard
     */
    styles() {
        return `
            .usecases-dashboard {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                padding: 24px;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                min-height: 100vh;
            }

            .usecases-header {
                margin-bottom: 32px;
                text-align: center;
            }

            .usecases-header h2 {
                font-size: 32px;
                font-weight: 700;
                color: #1a1a1a;
                margin: 0 0 8px 0;
            }

            .usecases-subtitle {
                font-size: 14px;
                color: #666;
                margin: 0;
            }

            .usecases-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 24px;
            }

            .usecases-section {
                background: white;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                display: flex;
                flex-direction: column;
                gap: 16px;
            }

            .section-title {
                font-size: 18px;
                font-weight: 600;
                color: #1a1a1a;
                margin: 0;
                padding-bottom: 12px;
                border-bottom: 2px solid #e0e0e0;
            }

            /* Capabilities Styles */
            .capabilities-container {
                display: flex;
                flex-direction: column;
                gap: 12px;
                max-height: 600px;
                overflow-y: auto;
            }

            .capability-card {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px;
                background: #fafafa;
            }

            .capability-header {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 8px;
            }

            .capability-title h4 {
                margin: 0 0 4px 0;
                font-size: 14px;
                color: #1a1a1a;
            }

            .technical-name {
                font-size: 12px;
                color: #999;
                font-family: 'Courier New', monospace;
                background: #f0f0f0;
                padding: 2px 6px;
                border-radius: 3px;
            }

            .maturity-badge {
                display: inline-block;
                font-size: 12px;
                padding: 4px 8px;
                border-radius: 4px;
                background: #e3f2fd;
                color: #1976d2;
            }

            .capability-description {
                font-size: 12px;
                color: #666;
                margin: 8px 0;
            }

            .business-value {
                font-size: 12px;
                color: #2e7d32;
                margin: 4px 0 8px 0;
            }

            .capability-metrics {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 12px;
                margin-bottom: 8px;
            }

            .metric {
                display: flex;
                flex-direction: column;
                gap: 4px;
            }

            .metric label {
                font-size: 11px;
                font-weight: 600;
                color: #666;
                text-transform: uppercase;
            }

            .complexity-bar {
                height: 6px;
                background: #e0e0e0;
                border-radius: 3px;
                overflow: hidden;
            }

            .complexity-fill {
                height: 100%;
                transition: width 0.3s ease;
            }

            .score-circle {
                width: 50px;
                height: 50px;
                border-radius: 50%;
                background: conic-gradient(#4CAF50 0deg, #4CAF50 calc(var(--score) * 3.6deg), #e0e0e0 0deg);
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: inset 0 0 0 3px white;
            }

            .score-number {
                font-size: 12px;
                font-weight: 700;
                color: #1a1a1a;
            }

            .capability-stakeholders {
                font-size: 11px;
                display: flex;
                flex-direction: column;
                gap: 6px;
            }

            .actor-list, .system-list {
                display: flex;
                flex-wrap: wrap;
                gap: 4px;
            }

            .actor-badge, .system-badge {
                display: inline-block;
                padding: 2px 6px;
                background: #e8f5e9;
                color: #2e7d32;
                border-radius: 3px;
                font-size: 11px;
            }

            .system-badge {
                background: #e3f2fd;
                color: #1976d2;
            }

            /* Flows Styles */
            .flows-container {
                display: flex;
                flex-direction: column;
                gap: 12px;
            }

            .flow-card {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px;
                background: #fafafa;
            }

            .flow-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 8px;
            }

            .flow-header h4 {
                margin: 0;
                font-size: 14px;
                color: #1a1a1a;
            }

            .primary-actor {
                font-size: 11px;
                background: #fce4ec;
                color: #c2185b;
                padding: 3px 8px;
                border-radius: 3px;
            }

            .flow-description {
                font-size: 12px;
                color: #666;
                margin: 4px 0 8px 0;
            }

            .flow-details {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }

            .flow-section {
                font-size: 12px;
            }

            .flow-section strong {
                display: block;
                color: #1a1a1a;
                margin-bottom: 4px;
            }

            .steps-list, .preconditions-list, .criteria-list {
                margin: 4px 0;
                padding-left: 20px;
                color: #666;
            }

            .steps-list li, .preconditions-list li, .criteria-list li {
                margin: 2px 0;
                font-size: 11px;
            }

            /* Integrations Styles */
            .integrations-container {
                display: flex;
                flex-direction: column;
                gap: 12px;
            }

            .integration-group {
                margin-bottom: 8px;
            }

            .integration-type {
                font-size: 12px;
                font-weight: 600;
                color: #1a1a1a;
                margin: 0 0 8px 0;
                padding-bottom: 4px;
                border-bottom: 1px solid #e0e0e0;
            }

            .integration-items {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }

            .integration-item {
                display: flex;
                gap: 8px;
                align-items: flex-start;
                padding: 8px;
                border-radius: 4px;
                background: #f5f5f5;
            }

            .integration-icon {
                font-size: 16px;
                min-width: 24px;
            }

            .integration-info {
                flex: 1;
            }

            .integration-info strong {
                display: block;
                font-size: 12px;
                color: #1a1a1a;
                margin-bottom: 2px;
            }

            .integration-info p {
                margin: 0;
                font-size: 11px;
                color: #666;
            }

            /* Stakeholders Styles */
            .stakeholders-container {
                display: flex;
                flex-direction: column;
                gap: 12px;
            }

            .stakeholder-card {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px;
                background: #fafafa;
            }

            .stakeholder-role {
                margin-bottom: 8px;
            }

            .stakeholder-role h5 {
                margin: 0;
                font-size: 13px;
                color: #1a1a1a;
            }

            .capabilities-grid {
                display: flex;
                flex-wrap: wrap;
                gap: 6px;
            }

            .capability-tag {
                display: inline-block;
                padding: 4px 8px;
                background: #fff9c4;
                color: #f57f17;
                border-radius: 4px;
                font-size: 11px;
            }

            /* Empty State */
            .empty-state {
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 40px 20px;
                color: #999;
                text-align: center;
            }

            .empty-state p {
                margin: 0;
                font-size: 14px;
            }

            /* Scrollbar styling */
            .capabilities-container::-webkit-scrollbar {
                width: 6px;
            }

            .capabilities-container::-webkit-scrollbar-track {
                background: #f1f1f1;
                border-radius: 3px;
            }

            .capabilities-container::-webkit-scrollbar-thumb {
                background: #888;
                border-radius: 3px;
            }

            .capabilities-container::-webkit-scrollbar-thumb:hover {
                background: #555;
            }

            /* Responsive Design */
            @media (max-width: 768px) {
                .usecases-grid {
                    grid-template-columns: 1fr;
                }

                .capability-metrics {
                    grid-template-columns: 1fr;
                }

                .flow-header {
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 4px;
                }
            }
        `;
    }
}

// Export for CommonJS / Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UseCasesTab;
}
