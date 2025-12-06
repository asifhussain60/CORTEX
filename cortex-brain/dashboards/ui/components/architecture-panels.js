/**
 * Architecture Panels - Dynamic sections for Frontend, Backend, and Database
 * 
 * Renders specialized panels based on collected architecture data from
 * universal language analyzers (C#, TypeScript, SQL, ColdFusion, Python).
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Source-Available (Use Allowed, No Contributions)
 */

/**
 * Render Frontend Architecture Panel
 * @param {Object} frontendData - Frontend information from analyzers
 * @returns {HTMLElement} - Frontend panel element
 */
export function renderFrontendPanel(frontendData) {
    if (!frontendData || Object.keys(frontendData).length === 0) {
        return null;
    }
    
    const panel = document.createElement('div');
    panel.className = 'glass-panel architecture-panel';
    panel.setAttribute('data-section', 'frontend');
    
    panel.innerHTML = `
        <div class="panel-header">
            <h2>🎨 Frontend Architecture</h2>
            <span class="panel-badge">${frontendData.framework || 'Web UI'}</span>
        </div>
        
        <div class="panel-content">
            <!-- Framework Info -->
            ${renderFrameworkInfo(frontendData)}
            
            <!-- Components -->
            ${renderComponentsSection(frontendData)}
            
            <!-- Routing -->
            ${renderRoutingSection(frontendData)}
            
            <!-- State Management -->
            ${renderStateManagementSection(frontendData)}
        </div>
    `;
    
    return panel;
}

function renderFrameworkInfo(data) {
    if (!data.framework) return '';
    
    return `
        <div class="info-section">
            <h3>Framework</h3>
            <div class="info-grid">
                <div class="info-item">
                    <span class="label">Framework:</span>
                    <span class="value">${data.framework}</span>
                </div>
                ${data.version ? `
                <div class="info-item">
                    <span class="label">Version:</span>
                    <span class="value">${data.version}</span>
                </div>
                ` : ''}
                ${data.componentCount ? `
                <div class="info-item">
                    <span class="label">Components:</span>
                    <span class="value">${data.componentCount}</span>
                </div>
                ` : ''}
                ${data.routes && data.routes.length ? `
                <div class="info-item">
                    <span class="label">Routes:</span>
                    <span class="value">${data.routes.length}</span>
                </div>
                ` : ''}
            </div>
        </div>
    `;
}

function renderComponentsSection(data) {
    if (!data.components || data.components.length === 0) return '';
    
    const componentList = data.components.slice(0, 10).map(comp => `
        <div class="list-item">
            <span class="item-icon">📦</span>
            <span class="item-name">${comp.name || comp}</span>
            ${comp.type ? `<span class="item-badge">${comp.type}</span>` : ''}
        </div>
    `).join('');
    
    return `
        <div class="info-section">
            <h3>Components (${data.components.length})</h3>
            <div class="scrollable-list">
                ${componentList}
            </div>
            ${data.components.length > 10 ? `
                <div class="show-more">+ ${data.components.length - 10} more</div>
            ` : ''}
        </div>
    `;
}

function renderRoutingSection(data) {
    if (!data.routes || data.routes.length === 0) return '';
    
    const routeList = data.routes.slice(0, 10).map(route => `
        <div class="list-item">
            <span class="item-icon">🔗</span>
            <span class="item-name">${route.path || route}</span>
            ${route.component ? `<span class="item-badge">${route.component}</span>` : ''}
        </div>
    `).join('');
    
    return `
        <div class="info-section">
            <h3>Routes (${data.routes.length})</h3>
            <div class="scrollable-list">
                ${routeList}
            </div>
        </div>
    `;
}

function renderStateManagementSection(data) {
    if (!data.stateManagement) return '';
    
    return `
        <div class="info-section">
            <h3>State Management</h3>
            <div class="info-grid">
                <div class="info-item">
                    <span class="label">Library:</span>
                    <span class="value">${data.stateManagement}</span>
                </div>
            </div>
        </div>
    `;
}

/**
 * Render Backend Architecture Panel
 */
export function renderBackendPanel(backendData) {
    if (!backendData || Object.keys(backendData).length === 0) {
        return null;
    }
    
    const panel = document.createElement('div');
    panel.className = 'glass-panel architecture-panel';
    panel.setAttribute('data-section', 'backend');
    
    panel.innerHTML = `
        <div class="panel-header">
            <h2>⚙️ Backend Architecture</h2>
            <span class="panel-badge">${backendData.framework || 'API Service'}</span>
        </div>
        
        <div class="panel-content">
            <!-- Framework Info -->
            ${renderBackendFrameworkInfo(backendData)}
            
            <!-- API Endpoints -->
            ${renderEndpointsSection(backendData)}
            
            <!-- Services -->
            ${renderServicesSection(backendData)}
            
            <!-- Background Jobs -->
            ${renderBackgroundJobsSection(backendData)}
        </div>
    `;
    
    return panel;
}

function renderBackendFrameworkInfo(data) {
    return `
        <div class="info-section">
            <h3>Framework</h3>
            <div class="info-grid">
                ${data.framework ? `
                <div class="info-item">
                    <span class="label">Framework:</span>
                    <span class="value">${data.framework}</span>
                </div>
                ` : ''}
                ${data.version ? `
                <div class="info-item">
                    <span class="label">Version:</span>
                    <span class="value">${data.version}</span>
                </div>
                ` : ''}
                ${data.apiType ? `
                <div class="info-item">
                    <span class="label">API Type:</span>
                    <span class="value">${data.apiType}</span>
                </div>
                ` : ''}
                ${data.endpointCount ? `
                <div class="info-item">
                    <span class="label">Endpoints:</span>
                    <span class="value">${data.endpointCount}</span>
                </div>
                ` : ''}
            </div>
        </div>
    `;
}

function renderEndpointsSection(data) {
    if (!data.endpoints || data.endpoints.length === 0) return '';
    
    const endpointList = data.endpoints.slice(0, 15).map(ep => {
        const method = ep.method || 'GET';
        const methodClass = method.toLowerCase();
        
        return `
            <div class="list-item endpoint-item">
                <span class="http-method ${methodClass}">${method}</span>
                <span class="item-name">${ep.path || ep.route}</span>
                ${ep.handler ? `<span class="item-badge">${ep.handler}</span>` : ''}
            </div>
        `;
    }).join('');
    
    return `
        <div class="info-section">
            <h3>API Endpoints (${data.endpoints.length})</h3>
            <div class="scrollable-list">
                ${endpointList}
            </div>
            ${data.endpoints.length > 15 ? `
                <div class="show-more">+ ${data.endpoints.length - 15} more</div>
            ` : ''}
        </div>
    `;
}

function renderServicesSection(data) {
    if (!data.services || data.services.length === 0) return '';
    
    const serviceList = data.services.slice(0, 10).map(svc => `
        <div class="list-item">
            <span class="item-icon">🔧</span>
            <span class="item-name">${svc.name || svc}</span>
            ${svc.type ? `<span class="item-badge">${svc.type}</span>` : ''}
        </div>
    `).join('');
    
    return `
        <div class="info-section">
            <h3>Services (${data.services.length})</h3>
            <div class="scrollable-list">
                ${serviceList}
            </div>
        </div>
    `;
}

function renderBackgroundJobsSection(data) {
    if (!data.backgroundJobs || data.backgroundJobs.length === 0) return '';
    
    const jobList = data.backgroundJobs.map(job => `
        <div class="list-item">
            <span class="item-icon">⏱️</span>
            <span class="item-name">${job.name || job}</span>
            ${job.schedule ? `<span class="item-badge">${job.schedule}</span>` : ''}
        </div>
    `).join('');
    
    return `
        <div class="info-section">
            <h3>Background Jobs (${data.backgroundJobs.length})</h3>
            <div class="scrollable-list">
                ${jobList}
            </div>
        </div>
    `;
}

/**
 * Render Database Architecture Panel
 */
export function renderDatabasePanel(databaseData) {
    if (!databaseData || Object.keys(databaseData).length === 0) {
        return null;
    }
    
    const panel = document.createElement('div');
    panel.className = 'glass-panel architecture-panel';
    panel.setAttribute('data-section', 'database');
    
    panel.innerHTML = `
        <div class="panel-header">
            <h2>🗄️ Database Architecture</h2>
            <span class="panel-badge">${databaseData.platform || 'Database'}</span>
        </div>
        
        <div class="panel-content">
            <!-- Platform Info -->
            ${renderDatabasePlatformInfo(databaseData)}
            
            <!-- Schema Objects -->
            ${renderSchemaSection(databaseData)}
            
            <!-- Stored Procedures -->
            ${renderProceduresSection(databaseData)}
            
            <!-- Views -->
            ${renderViewsSection(databaseData)}
        </div>
    `;
    
    return panel;
}

function renderDatabasePlatformInfo(data) {
    return `
        <div class="info-section">
            <h3>Platform</h3>
            <div class="info-grid">
                ${data.platform ? `
                <div class="info-item">
                    <span class="label">Platform:</span>
                    <span class="value">${data.platform}</span>
                </div>
                ` : ''}
                ${data.version ? `
                <div class="info-item">
                    <span class="label">Version:</span>
                    <span class="value">${data.version}</span>
                </div>
                ` : ''}
                ${data.tableCount ? `
                <div class="info-item">
                    <span class="label">Tables:</span>
                    <span class="value">${data.tableCount}</span>
                </div>
                ` : ''}
                ${data.procedureCount ? `
                <div class="info-item">
                    <span class="label">Procedures:</span>
                    <span class="value">${data.procedureCount}</span>
                </div>
                ` : ''}
                ${data.viewCount ? `
                <div class="info-item">
                    <span class="label">Views:</span>
                    <span class="value">${data.viewCount}</span>
                </div>
                ` : ''}
            </div>
        </div>
    `;
}

function renderSchemaSection(data) {
    if (!data.tables || data.tables.length === 0) return '';
    
    const tableList = data.tables.slice(0, 15).map(table => {
        const tableName = table.name || table;
        const columnCount = table.columns ? table.columns.length : table.columnCount || 0;
        
        return `
            <div class="list-item">
                <span class="item-icon">📊</span>
                <span class="item-name">${tableName}</span>
                ${columnCount > 0 ? `<span class="item-badge">${columnCount} columns</span>` : ''}
            </div>
        `;
    }).join('');
    
    return `
        <div class="info-section">
            <h3>Tables (${data.tables.length})</h3>
            <div class="scrollable-list">
                ${tableList}
            </div>
            ${data.tables.length > 15 ? `
                <div class="show-more">+ ${data.tables.length - 15} more</div>
            ` : ''}
        </div>
    `;
}

function renderProceduresSection(data) {
    if (!data.procedures || data.procedures.length === 0) return '';
    
    const procList = data.procedures.slice(0, 10).map(proc => {
        const procName = proc.name || proc;
        const complexity = proc.complexity || 0;
        
        return `
            <div class="list-item">
                <span class="item-icon">⚡</span>
                <span class="item-name">${procName}</span>
                ${complexity > 0 ? `<span class="item-badge complexity-${getComplexityLevel(complexity)}">${complexity}</span>` : ''}
            </div>
        `;
    }).join('');
    
    return `
        <div class="info-section">
            <h3>Stored Procedures (${data.procedures.length})</h3>
            <div class="scrollable-list">
                ${procList}
            </div>
        </div>
    `;
}

function renderViewsSection(data) {
    if (!data.views || data.views.length === 0) return '';
    
    const viewList = data.views.slice(0, 10).map(view => `
        <div class="list-item">
            <span class="item-icon">👁️</span>
            <span class="item-name">${view.name || view}</span>
        </div>
    `).join('');
    
    return `
        <div class="info-section">
            <h3>Views (${data.views.length})</h3>
            <div class="scrollable-list">
                ${viewList}
            </div>
        </div>
    `;
}

function getComplexityLevel(complexity) {
    if (complexity < 10) return 'low';
    if (complexity < 20) return 'medium';
    return 'high';
}

/**
 * Render all architecture panels
 */
export function renderArchitecturePanels(architectureData) {
    const container = document.getElementById('architecture-panels-container');
    if (!container) {
        console.warn('Architecture panels container not found');
        return;
    }
    
    // Clear existing content
    container.innerHTML = '';
    
    // Render each panel
    if (architectureData.frontend) {
        const frontendPanel = renderFrontendPanel(architectureData.frontend);
        if (frontendPanel) container.appendChild(frontendPanel);
    }
    
    if (architectureData.backend) {
        const backendPanel = renderBackendPanel(architectureData.backend);
        if (backendPanel) container.appendChild(backendPanel);
    }
    
    if (architectureData.database) {
        const databasePanel = renderDatabasePanel(architectureData.database);
        if (databasePanel) container.appendChild(databasePanel);
    }
}
