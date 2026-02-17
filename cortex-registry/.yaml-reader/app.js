// ============================================================================
// CORTEX YAML Reader Application Logic
// Designed for file:// protocol - NO fetch() calls
// ============================================================================

// Application State
const state = {
    loadedFiles: [],
    currentFile: null,
    currentView: 'overview', // Default to overview instead of tree
    explorerTab: 'loaded',
    recentFiles: [],
    filters: {
        status: 'all',
        type: 'all',
        tag: 'all'
    }
};

// DOM Elements
const elements = {
    fileInput: document.getElementById('fileInput'),
    openFileBtn: document.getElementById('openFileBtn'),
    clearAllBtn: document.getElementById('clearAllBtn'),
    searchInput: document.getElementById('searchInput'),
    explorerContent: document.getElementById('explorerContent'),
    contentArea: document.getElementById('contentArea'),
    dropZoneOverlay: document.getElementById('dropZoneOverlay'),
    toast: document.getElementById('toast'),
    fileCount: document.getElementById('fileCount')
};

// Initialize
function init() {
    loadRecentFiles();
    setupEventListeners();
    console.log('✅ CORTEX YAML Reader initialized (file:// mode)');
}

// Event Listeners
function setupEventListeners() {
    // File selection
    elements.openFileBtn.addEventListener('click', () => {
        elements.fileInput.click();
    });
    
    elements.fileInput.addEventListener('change', handleFileSelect);
    
    // Clear all
    elements.clearAllBtn.addEventListener('click', clearAllFiles);
    
    // Search
    let searchTimeout;
    elements.searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            performSearch(e.target.value);
        }, 300);
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.key === '/' && document.activeElement !== elements.searchInput) {
            e.preventDefault();
            elements.searchInput.focus();
        }
        if (e.key === 'Escape') {
            elements.searchInput.value = '';
            performSearch('');
            elements.searchInput.blur();
            // Close spotlight modal
            document.querySelector('.spotlight-modal')?.classList.remove('active');
        }
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            showSpotlight();
        }
    });
    
    // Drag and drop
    document.body.addEventListener('dragenter', handleDragEnter);
    document.body.addEventListener('dragover', handleDragOver);
    document.body.addEventListener('dragleave', handleDragLeave);
    document.body.addEventListener('drop', handleDrop);
    
    // Explorer tabs
    document.querySelectorAll('.explorer-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.explorer-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            state.explorerTab = tab.dataset.tab;
            renderExplorer();
        });
    });
}

// File Selection Handler
async function handleFileSelect(event) {
    const files = Array.from(event.target.files);
    await processFiles(files);
    event.target.value = '';
}

// Process Files
async function processFiles(files) {
    for (const file of files) {
        if (!file.name.endsWith('.yml') && !file.name.endsWith('.yaml')) {
            showToast(`Skipped ${file.name}: Not a YAML file`, 'warning');
            continue;
        }
        
        try {
            const content = await readFileContent(file);
            const parsed = jsyaml.load(content);
            
            // NEW: Infer schema using SchemaInference
            const schemaResult = SchemaInference.infer(parsed);
            console.log('Schema inference result:', {
                type: schemaResult.type,
                confidence: schemaResult.confidence,
                entityCount: schemaResult.entities?.length || 0,
                graphNodes: schemaResult.graph?.nodes?.length || 0
            });
            
            const fileData = {
                id: generateId(),
                name: file.name,
                size: file.size,
                lastModified: file.lastModified,
                content: content,
                parsed: parsed,
                schema: schemaResult // Store schema inference results
            };
            
            state.loadedFiles.push(fileData);
            addToRecent(fileData);
            
            showToast(`Loaded ${file.name} (${schemaResult.type} schema detected)`, 'success');
        } catch (error) {
            showToast(`Error loading ${file.name}: ${error.message}`, 'error');
            
            const fileData = {
                id: generateId(),
                name: file.name,
                size: file.size,
                lastModified: file.lastModified,
                content: await readFileContent(file),
                error: error.message
            };
            state.loadedFiles.push(fileData);
        }
    }
    
    updateFileCount();
    renderExplorer();
    
    if (!state.currentFile && state.loadedFiles.length > 0) {
        selectFile(state.loadedFiles[0].id);
    }
}

// Read File Content (File API - works in file:// protocol)
function readFileContent(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = () => reject(new Error('Failed to read file'));
        reader.readAsText(file);
    });
}

// Drag & Drop Handlers
function handleDragEnter(e) {
    e.preventDefault();
    e.stopPropagation();
    elements.dropZoneOverlay.classList.add('active');
}

function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    if (e.target === elements.dropZoneOverlay) {
        elements.dropZoneOverlay.classList.remove('active');
    }
}

async function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    elements.dropZoneOverlay.classList.remove('active');
    
    const files = Array.from(e.dataTransfer.files);
    await processFiles(files);
}

// Render Explorer
function renderExplorer() {
    const container = elements.explorerContent;
    
    if (state.explorerTab === 'loaded') {
        if (state.loadedFiles.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📁</div>
                    <div>No files loaded yet</div>
                    <div style="font-size: 0.8rem; margin-top: 0.5rem;">
                        Drag & drop YAML files here or use the Open button
                    </div>
                </div>
            `;
        } else {
            container.innerHTML = state.loadedFiles.map(file => `
                <div class="file-list-item ${state.currentFile?.id === file.id ? 'active' : ''}" 
                     onclick="selectFile('${file.id}')">
                    <div class="file-icon">${file.error ? '⚠️' : '📄'}</div>
                    <div class="file-info">
                        <div class="file-name">${escapeHtml(file.name)}</div>
                        <div class="file-meta">${formatFileSize(file.size)}</div>
                    </div>
                    <div class="file-close" onclick="event.stopPropagation(); removeFile('${file.id}')">✕</div>
                </div>
            `).join('');
        }
    } else if (state.explorerTab === 'recent') {
        if (state.recentFiles.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">🕐</div>
                    <div>No recent files</div>
                </div>
            `;
        } else {
            container.innerHTML = state.recentFiles.map(file => `
                <div class="file-list-item">
                    <div class="file-icon">📄</div>
                    <div class="file-info">
                        <div class="file-name">${escapeHtml(file.name)}</div>
                        <div class="file-meta">${new Date(file.lastModified).toLocaleDateString()}</div>
                    </div>
                </div>
            `).join('');
        }
    }
}

// Select File
function selectFile(fileId) {
    const file = state.loadedFiles.find(f => f.id === fileId);
    if (!file) return;
    
    state.currentFile = file;
    renderExplorer();
    renderContent();
}

// Remove File
function removeFile(fileId) {
    state.loadedFiles = state.loadedFiles.filter(f => f.id !== fileId);
    
    if (state.currentFile?.id === fileId) {
        state.currentFile = state.loadedFiles.length > 0 ? state.loadedFiles[0] : null;
    }
    
    updateFileCount();
    renderExplorer();
    
    if (state.currentFile) {
        renderContent();
    } else {
        showWelcomeScreen();
    }
}

// Clear All Files
function clearAllFiles() {
    if (state.loadedFiles.length === 0) return;
    
    if (confirm(`Clear all ${state.loadedFiles.length} loaded files?`)) {
        state.loadedFiles = [];
        state.currentFile = null;
        updateFileCount();
        renderExplorer();
        showWelcomeScreen();
        showToast('All files cleared', 'success');
    }
}

// Render Content
function renderContent() {
    const file = state.currentFile;
    if (!file) {
        showWelcomeScreen();
        return;
    }
    
    // Determine available views based on schema
    const availableViews = ['raw'];
    if (!file.error && file.schema) {
        availableViews.unshift('overview', 'cards', 'tree');
        if (file.schema.graph && file.schema.graph.nodes.length > 0) {
            availableViews.push('relationships');
        }
        if (file.schema.type === 'workflow') {
            availableViews.push('workflow');
        }
    }
    
    // Ensure current view is available
    if (!availableViews.includes(state.currentView)) {
        state.currentView = availableViews[0];
    }
    
    // Build view tabs HTML
    const viewTabsHTML = availableViews.map(view => {
        const icons = {
            overview: '📊',
            cards: '🎴',
            tree: '🌲',
            relationships: '🔗',
            workflow: '🔄',
            raw: '📝'
        };
        const labels = {
            overview: 'Overview',
            cards: 'Cards',
            tree: 'Tree',
            relationships: 'Relationships',
            workflow: 'Workflow',
            raw: 'Raw'
        };
        return `<button class="view-tab ${state.currentView === view ? 'active' : ''}" 
                        onclick="changeView('${view}')">${icons[view]} ${labels[view]}</button>`;
    }).join('');
    
    let html = `
        <div class="content-header">
            <div class="filename-display">📄 ${escapeHtml(file.name)}</div>
            ${file.schema ? renderSchemaBadge(file.schema) : '<div class="schema-badge">YAML</div>'}
            <div class="view-tabs">${viewTabsHTML}</div>
        </div>
        <div style="flex: 1; overflow-y: auto;">
    `;
    
    if (file.error) {
        html += ViewRenderers.renderError(file.error, file.name);
    } else {
        // Route to appropriate renderer based on current view
        if (state.currentView === 'overview') {
            html += ViewRenderers.renderOverview(file.schema, file.name);
        } else if (state.currentView === 'cards') {
            html += ViewRenderers.renderCards(file.schema.entities, state.filters);
        } else if (state.currentView === 'tree') {
            html += '<div style="padding: 1.5rem;">' + renderTreeView(file.parsed) + '</div>';
        } else if (state.currentView === 'relationships') {
            html += '<div id="graphViewContainer" style="padding: 1.5rem; min-height: 650px;"></div>';
            setTimeout(() => {
                console.log('Calling DiagramGenerator.renderRelationshipGraph with:', file.schema.graph);
                DiagramGenerator.renderRelationshipGraph(file.schema.graph, 'graphViewContainer');
            }, 100);
        } else if (state.currentView === 'workflow') {
            html += '<div id="workflowViewContainer" style="padding: 1.5rem;"></div>';
            setTimeout(() => DiagramGenerator.renderWorkflowDiagram(file.schema.entities, 'workflowViewContainer'), 100);
        } else if (state.currentView === 'raw') {
            html += ViewRenderers.renderRaw(file.content, file.name);
        }
    }
    
    html += '</div>';
    elements.contentArea.innerHTML = html;
    
    // Attach filter listeners if cards view
    if (state.currentView === 'cards' && !file.error) {
        attachFilterListeners();
    }
}

// Render Schema Badge
function renderSchemaBadge(schema) {
    const classNames = {
        registry: 'schema-registry',
        workflow: 'schema-workflow',
        collection: 'schema-collection',
        graph: 'schema-graph',
        generic: 'schema-generic'
    };
    const icons = {
        registry: '📋',
        workflow: '🔄',
        collection: '📦',
        graph: '🕸️',
        generic: '📄'
    };
    const confidence = Math.round(schema.confidence * 100);
    return `
        <div class="schema-badge ${classNames[schema.type] || classNames.generic}">
            ${icons[schema.type] || icons.generic} ${schema.type.toUpperCase()} 
            <span style="opacity: 0.7; font-size: 0.8em;">(${confidence}%)</span>
        </div>
    `;
}

// Attach Filter Listeners (for Cards view)
function attachFilterListeners() {
    const statusSelect = document.getElementById('filterStatus');
    const typeSelect = document.getElementById('filterType');
    const tagSelect = document.getElementById('filterTag');
    const resetBtn = document.getElementById('resetFilters');
    
    if (statusSelect) {
        statusSelect.addEventListener('change', (e) => {
            state.filters.status = e.target.value;
            renderContent();
        });
    }
    if (typeSelect) {
        typeSelect.addEventListener('change', (e) => {
            state.filters.type = e.target.value;
            renderContent();
        });
    }
    if (tagSelect) {
        tagSelect.addEventListener('change', (e) => {
            state.filters.tag = e.target.value;
            renderContent();
        });
    }
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            state.filters = { status: 'all', type: 'all', tag: 'all' };
            renderContent();
        });
    }
}

// Render Tree View (Kept for legacy Tree tab)
function renderTreeView(obj, level = 0) {
    if (obj === null || obj === undefined) {
        return '<span class="tree-value">null</span>';
    }
    
    if (typeof obj !== 'object') {
        const type = typeof obj;
        return `<span class="tree-value ${type}">${escapeHtml(String(obj))}</span>`;
    }
    
    if (Array.isArray(obj)) {
        if (obj.length === 0) return '<span class="tree-value">[]</span>';
        
        let html = '<div class="tree-children">';
        obj.forEach((item, index) => {
            html += `
                <div class="tree-node">
                    <span class="tree-key">[${index}]</span>
                    ${renderTreeView(item, level + 1)}
                </div>
            `;
        });
        html += '</div>';
        return html;
    }
    
    const keys = Object.keys(obj);
    if (keys.length === 0) return '<span class="tree-value">{}</span>';
    
    let html = '<div class="tree-children">';
    keys.forEach(key => {
        const value = obj[key];
        const isObject = value !== null && typeof value === 'object';
        
        html += `
            <div class="tree-node">
                <span class="tree-key" onclick="toggleTreeNode(this)">
                    ${isObject ? '<span class="tree-collapse-icon">▼</span>' : ''}
                    ${escapeHtml(key)}:
                </span>
                ${isObject ? '' : renderTreeView(value, level + 1)}
                ${isObject ? renderTreeView(value, level + 1) : ''}
            </div>
        `;
    });
    html += '</div>';
    return html;
}

// Toggle Tree Node
window.toggleTreeNode = function(element) {
    const node = element.closest('.tree-node');
    node.classList.toggle('collapsed');
};

// Render Cards View
function renderCardsView(obj) {
    if (typeof obj !== 'object' || obj === null) {
        return '<div class="yaml-card"><div class="card-body">Not a structured object</div></div>';
    }
    
    let html = '<div class="card-grid">';
    
    if (Array.isArray(obj)) {
        obj.forEach((item, index) => {
            html += renderCard(`Item ${index}`, item);
        });
    } else {
        Object.entries(obj).forEach(([key, value]) => {
            html += renderCard(key, value);
        });
    }
    
    html += '</div>';
    return html;
}

function renderCard(title, data) {
    const jsonStr = JSON.stringify(data);
    
    return `
        <div class="yaml-card">
            <div class="card-header">
                <span>${escapeHtml(title)}</span>
                <button class="copy-btn" onclick='copyToClipboard(${jsonStr})'>
                    Copy
                </button>
            </div>
            <div class="card-body">
                ${renderCardContent(data)}
            </div>
        </div>
    `;
}

function renderCardContent(data) {
    if (data === null || data === undefined) {
        return '<em>null</em>';
    }
    
    if (typeof data !== 'object') {
        return escapeHtml(String(data));
    }
    
    if (Array.isArray(data)) {
        if (data.length === 0) return '<em>Empty array</em>';
        return '<ul>' + data.slice(0, 10).map(item => 
            `<li>${escapeHtml(String(item).substring(0, 100))}</li>`
        ).join('') + 
        (data.length > 10 ? '<li><em>... and more</em></li>' : '') + '</ul>';
    }
    
    const entries = Object.entries(data);
    if (entries.length === 0) return '<em>Empty object</em>';
    
    return '<dl>' + entries.slice(0, 10).map(([k, v]) => {
        const displayValue = typeof v === 'object' ? 
            JSON.stringify(v).substring(0, 100) : 
            String(v).substring(0, 100);
        return `<dt>${escapeHtml(k)}</dt><dd>${escapeHtml(displayValue)}</dd>`;
    }).join('') + 
    (entries.length > 10 ? '<dt>...</dt><dd><em>and more</em></dd>' : '') + 
    '</dl>';
}

// Render Graph View
function renderGraphView(obj) {
    const graphData = extractGraphData(obj);
    
    const container = document.getElementById('graphViewContainer');
    if (!container) return;
    
    if (graphData.nodes.length === 0) {
        container.innerHTML = `
            <div class="error-panel" style="background: rgba(245, 158, 11, 0.1); border-color: var(--warning);">
                <div class="error-header" style="color: var(--warning);">
                    <span>ℹ️</span>
                    <span>No Graph Structure Detected</span>
                </div>
                <div style="color: var(--text-secondary); margin-top: 1rem;">
                    This YAML doesn't contain recognizable graph relationships like:
                    <ul style="margin-top: 0.5rem; margin-left: 2rem;">
                        <li>id/name + dependencies/depends_on</li>
                        <li>steps/transitions with connections</li>
                        <li>inputs/outputs/routes</li>
                    </ul>
                </div>
            </div>
        `;
        return;
    }
    
    container.innerHTML = '<div class="graph-container"><svg id="graph-canvas"></svg></div>';
    
    setTimeout(() => {
        const svg = d3.select('#graph-canvas');
        const graphContainer = document.querySelector('.graph-container');
        const width = graphContainer.clientWidth;
        const height = graphContainer.clientHeight;
        
        svg.attr('width', width).attr('height', height);
        svg.selectAll('*').remove();
        
        const g = svg.append('g');
        
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on('zoom', (event) => {
                g.attr('transform', event.transform);
            });
        
        svg.call(zoom);
        
        const simulation = d3.forceSimulation(graphData.nodes)
            .force('link', d3.forceLink(graphData.links).id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2));
        
        const link = g.append('g')
            .selectAll('line')
            .data(graphData.links)
            .join('line')
            .attr('stroke', '#7b61ff')
            .attr('stroke-opacity', 0.6)
            .attr('stroke-width', 2);
        
        const node = g.append('g')
            .selectAll('circle')
            .data(graphData.nodes)
            .join('circle')
            .attr('r', 10)
            .attr('fill', '#00d4ff')
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended));
        
        const label = g.append('g')
            .selectAll('text')
            .data(graphData.nodes)
            .join('text')
            .text(d => d.label)
            .attr('font-size', 12)
            .attr('fill', '#ffffff')
            .attr('dx', 15)
            .attr('dy', 4);
        
        simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);
            
            node
                .attr('cx', d => d.x)
                .attr('cy', d => d.y);
            
            label
                .attr('x', d => d.x)
                .attr('y', d => d.y);
        });
        
        function dragstarted(event) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }
        
        function dragged(event) {
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }
        
        function dragended(event) {
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }
    }, 100);
}

// Extract Graph Data
function extractGraphData(obj) {
    const nodes = [];
    const links = [];
    const nodeMap = new Map();
    
    function traverse(data, path = '') {
        if (!data || typeof data !== 'object') return;
        
        if (Array.isArray(data)) {
            data.forEach((item, index) => {
                traverse(item, `${path}[${index}]`);
            });
            return;
        }
        
        const id = data.id || data.name || path;
        if (id && !nodeMap.has(id)) {
            nodeMap.set(id, {
                id: id,
                label: (data.name || data.id || path).toString().substring(0, 30),
                type: data.type || 'node'
            });
            nodes.push(nodeMap.get(id));
        }
        
        const deps = data.dependencies || data.depends_on || data.requires || [];
        const depsArray = Array.isArray(deps) ? deps : [deps];
        
        depsArray.forEach(dep => {
            if (dep) {
                links.push({
                    source: id,
                    target: dep,
                    type: 'dependency'
                });
            }
        });
        
        Object.values(data).forEach(value => {
            if (typeof value === 'object') {
                traverse(value, path);
            }
        });
    }
    
    traverse(obj);
    
    return { nodes, links };
}

// Render Raw View
function renderRawView(content) {
    return `
        <div style="position: relative;">
            <button class="copy-btn" style="position: absolute; top: 1rem; right: 1rem; z-index: 10;" 
                    onclick='copyToClipboard(${JSON.stringify(content)})'>
                Copy All
            </button>
            <pre style="background: rgba(0, 0, 0, 0.3); padding: 2rem; border-radius: 12px; overflow-x: auto; font-family: var(--font-mono); font-size: 0.85rem; line-height: 1.6;">${escapeHtml(content)}</pre>
        </div>
    `;
}

// Change View
window.changeView = function(view) {
    state.currentView = view;
    renderContent();
};

// Copy to Clipboard
window.copyToClipboard = async function(text) {
    try {
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(text);
            showToast('Copied to clipboard', 'success');
        } else {
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.left = '-999999px';
            document.body.appendChild(textarea);
            textarea.select();
            
            try {
                document.execCommand('copy');
                showToast('Copied to clipboard', 'success');
            } catch (err) {
                showToast('Copy failed - clipboard access restricted', 'warning');
            }
            
            document.body.removeChild(textarea);
        }
    } catch (err) {
        showToast('Copy failed - user interaction required', 'warning');
    }
};

// Search
function performSearch(query) {
    if (!state.currentFile || !query.trim()) {
        if (state.currentFile) {
            renderContent();
        }
        return;
    }
    renderContent();
}

// Recent Files Management
function loadRecentFiles() {
    try {
        const stored = localStorage.getItem('cortex_yaml_recent');
        if (stored) {
            state.recentFiles = JSON.parse(stored);
        }
    } catch (err) {
        console.warn('Failed to load recent files:', err);
    }
}

function addToRecent(fileData) {
    const recent = {
        name: fileData.name,
        size: fileData.size,
        lastModified: fileData.lastModified
    };
    
    state.recentFiles = state.recentFiles.filter(f => f.name !== recent.name);
    state.recentFiles.unshift(recent);
    state.recentFiles = state.recentFiles.slice(0, 20);
    
    try {
        localStorage.setItem('cortex_yaml_recent', JSON.stringify(state.recentFiles));
    } catch (err) {
        console.warn('Failed to save recent files:', err);
    }
}

// Utilities
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function updateFileCount() {
    elements.fileCount.textContent = `${state.loadedFiles.length} file${state.loadedFiles.length !== 1 ? 's' : ''}`;
}

function showWelcomeScreen() {
    elements.contentArea.innerHTML = `
        <div class="welcome-screen">
            <div class="welcome-icon">🎯</div>
            <h1 class="welcome-title">CORTEX Registry YAML Reader</h1>
            <p class="welcome-text">
                A fully offline YAML viewer designed for the file:// protocol.
                Load, explore, and visualize YAML files with zero HTTP dependencies.
            </p>
            <button class="btn btn-primary" onclick="document.getElementById('openFileBtn').click()">
                <span>📂</span>
                <span>Get Started - Open YAML File</span>
            </button>
            <div class="welcome-hint">
                💡 <strong>Pro Tips:</strong><br>
                • Drag & drop multiple YAML files anywhere<br>
                • Press <span class="keyboard-hint">/</span> to search within content<br>
                • Press <span class="keyboard-hint">Esc</span> to clear search<br>
                • Files are never uploaded - all processing is local
            </div>
            <div class="welcome-hint" style="margin-top: 1rem; background: rgba(239, 68, 68, 0.1); border: 1px solid var(--danger);">
                ⚠️ <strong>Browser Limitations:</strong><br>
                Under file:// protocol, clipboard access requires user interaction.
                Some features may prompt for permissions on first use.
            </div>
        </div>
    `;
}

function showToast(message, type = 'success') {
    const toast = elements.toast;
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Change View
window.changeView = function(viewName) {
    state.currentView = viewName;
    renderContent();
};

// Spotlight Search
function showSpotlight() {
    const modal = document.querySelector('.spotlight-modal');
    if (!modal || !state.currentFile || !state.currentFile.schema) return;
    
    modal.classList.add('active');
    const input = document.getElementById('spotlightInput');
    if (input) {
        input.value = '';
        input.focus();
        performSpotlightSearch('');
    }
}

function performSpotlightSearch(query) {
    const resultsContainer = document.getElementById('spotlightResults');
    if (!resultsContainer || !state.currentFile || !state.currentFile.schema) return;
    
    const entities = state.currentFile.schema.entities || [];
    
    if (!query.trim()) {
        resultsContainer.innerHTML = '<div class="spotlight-result-item" style="text-align: center; color: var(--text-secondary);">Type to search entities...</div>';
        return;
    }
    
    const lowerQuery = query.toLowerCase();
    const filtered = entities.filter(e => 
        e.label.toLowerCase().includes(lowerQuery) ||
        e.id.toLowerCase().includes(lowerQuery) ||
        (e.summary && e.summary.toLowerCase().includes(lowerQuery)) ||
        (e.tags && e.tags.some(tag => tag.toLowerCase().includes(lowerQuery)))
    );
    
    if (filtered.length === 0) {
        resultsContainer.innerHTML = '<div class="spotlight-result-item" style="text-align: center; color: var(--text-secondary);">No matching entities found</div>';
        return;
    }
    
    resultsContainer.innerHTML = filtered.slice(0, 10).map(entity => `
        <div class="spotlight-result-item" onclick="selectSpotlightEntity('${entity.id}')">
            <div class="spotlight-result-title">${escapeHtml(entity.label)}</div>
            <div class="spotlight-result-meta">
                ${entity.kind ? `<span class="type-badge">${escapeHtml(entity.kind)}</span>` : ''}
                ${entity.status ? `<span class="status-pill status-${entity.status}">${escapeHtml(entity.status)}</span>` : ''}
                ${entity.summary ? ` • ${escapeHtml(entity.summary.substring(0, 80))}...` : ''}
            </div>
        </div>
    `).join('');
}

window.selectSpotlightEntity = function(entityId) {
    // Close spotlight
    document.querySelector('.spotlight-modal')?.classList.remove('active');
    
    // Switch to cards view and scroll to entity (future enhancement)
    state.currentView = 'cards';
    renderContent();
    
    // Try to scroll to the entity card (after render)
    setTimeout(() => {
        const card = document.querySelector(`[data-entity-id="${entityId}"]`);
        if (card) {
            card.scrollIntoView({ behavior: 'smooth', block: 'center' });
            card.style.animation = 'highlight 1s ease';
        }
    }, 100);
};

// Add spotlight input listener
document.addEventListener('DOMContentLoaded', () => {
    const spotlightInput = document.getElementById('spotlightInput');
    if (spotlightInput) {
        spotlightInput.addEventListener('input', (e) => {
            performSpotlightSearch(e.target.value);
        });
    }
    
    // Close spotlight on background click
    document.querySelector('.spotlight-modal')?.addEventListener('click', (e) => {
        if (e.target.classList.contains('spotlight-modal')) {
            e.target.classList.remove('active');
        }
    });
});

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
