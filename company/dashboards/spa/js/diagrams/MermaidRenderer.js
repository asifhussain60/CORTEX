/**
 * CORTEX SPA - Mermaid Renderer
 * Renders UML diagrams using Mermaid.js library
 * Version: 1.0.0
 */

class MermaidRenderer {
    /**
     * Initialize Mermaid renderer
     * @param {Object} options - Configuration options
     */
    constructor(options = {}) {
        this.options = {
            theme: options.theme || 'dark',
            startOnLoad: false,
            securityLevel: 'loose',
            themeVariables: {
                primaryColor: '#4d8cff',
                primaryTextColor: '#fff',
                primaryBorderColor: '#7fb3ff',
                lineColor: '#7fb3ff',
                secondaryColor: '#22c55e',
                tertiaryColor: '#f59e0b',
                background: 'transparent',
                mainBkg: 'rgba(77, 140, 255, 0.1)',
                secondBkg: 'rgba(34, 197, 94, 0.1)',
                tertiaryBkg: 'rgba(245, 158, 11, 0.1)',
                darkMode: true,
                fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
                fontSize: '14px'
            },
            ...options
        };
        
        this.initialized = false;
        this.diagramCount = 0;
        
        this._checkMermaidAvailability();
    }
    
    /**
     * Check if Mermaid.js is available
     * @private
     */
    _checkMermaidAvailability() {
        if (typeof mermaid === 'undefined') {
            console.error('Mermaid.js library not loaded. Please include mermaid.min.js');
            return;
        }
        
        this._initializeMermaid();
    }
    
    /**
     * Initialize Mermaid with theme
     * @private
     */
    _initializeMermaid() {
        try {
            mermaid.initialize({
                startOnLoad: this.options.startOnLoad,
                theme: this.options.theme,
                securityLevel: this.options.securityLevel,
                themeVariables: this.options.themeVariables,
                logLevel: 'error',
                flowchart: {
                    curve: 'basis',
                    padding: 20,
                    nodeSpacing: 50,
                    rankSpacing: 50,
                    useMaxWidth: true
                },
                sequence: {
                    diagramMarginX: 50,
                    diagramMarginY: 10,
                    actorMargin: 50,
                    width: 150,
                    height: 65,
                    boxMargin: 10,
                    useMaxWidth: true
                },
                gantt: {
                    titleTopMargin: 25,
                    barHeight: 20,
                    barGap: 4,
                    topPadding: 50,
                    sidePadding: 75
                },
                er: {
                    diagramPadding: 20,
                    layoutDirection: 'TB',
                    minEntityWidth: 100,
                    minEntityHeight: 75,
                    entityPadding: 15,
                    stroke: 'gray',
                    fill: 'honeydew',
                    fontSize: 12,
                    useMaxWidth: true
                }
            });
            
            this.initialized = true;
        } catch (error) {
            console.error('Failed to initialize Mermaid:', error);
        }
    }
    
    /**
     * Render diagram from definition
     * @param {HTMLElement|string} container - DOM element or selector
     * @param {string} definition - Mermaid diagram definition
     * @param {Object} options - Render options
     * @returns {Promise<void>}
     */
    async render(container, definition, options = {}) {
        if (!this.initialized) {
            throw new Error('Mermaid renderer not initialized');
        }
        
        const element = typeof container === 'string' 
            ? document.querySelector(container) 
            : container;
            
        if (!element) {
            throw new Error('Container element not found');
        }
        
        const id = options.id || `mermaid-${this.diagramCount++}`;
        
        try {
            // Clear existing content
            element.innerHTML = '';
            
            // Create diagram container
            const diagramDiv = document.createElement('div');
            diagramDiv.id = id;
            diagramDiv.className = 'mermaid-diagram';
            element.appendChild(diagramDiv);
            
            // Render diagram
            const { svg } = await mermaid.render(id, definition);
            diagramDiv.innerHTML = svg;
            
            // Apply custom styles
            this._applyCustomStyles(diagramDiv);
            
            // Make diagram interactive if requested
            if (options.interactive) {
                this._makeInteractive(diagramDiv);
            }
            
        } catch (error) {
            console.error('Failed to render Mermaid diagram:', error);
            element.innerHTML = `
                <div class="mermaid-error">
                    <div class="mermaid-error__icon">⚠️</div>
                    <div class="mermaid-error__message">Failed to render diagram</div>
                    <div class="mermaid-error__details">${error.message}</div>
                </div>
            `;
            throw error;
        }
    }
    
    /**
     * Render class diagram
     * @param {HTMLElement|string} container - DOM element or selector
     * @param {Object} data - Class diagram data
     * @returns {Promise<void>}
     */
    async renderClassDiagram(container, data) {
        const definition = this._generateClassDiagram(data);
        return this.render(container, definition, { interactive: true });
    }
    
    /**
     * Render ER diagram
     * @param {HTMLElement|string} container - DOM element or selector
     * @param {Object} data - ER diagram data
     * @returns {Promise<void>}
     */
    async renderERDiagram(container, data) {
        const definition = this._generateERDiagram(data);
        return this.render(container, definition, { interactive: true });
    }
    
    /**
     * Render sequence diagram
     * @param {HTMLElement|string} container - DOM element or selector
     * @param {Object} data - Sequence diagram data
     * @returns {Promise<void>}
     */
    async renderSequenceDiagram(container, data) {
        const definition = this._generateSequenceDiagram(data);
        return this.render(container, definition, { interactive: true });
    }
    
    /**
     * Render flowchart
     * @param {HTMLElement|string} container - DOM element or selector
     * @param {Object} data - Flowchart data
     * @returns {Promise<void>}
     */
    async renderFlowchart(container, data) {
        const definition = this._generateFlowchart(data);
        return this.render(container, definition, { interactive: true });
    }
    
    /**
     * Generate class diagram definition
     * @private
     */
    _generateClassDiagram(data) {
        const { classes = [], relationships = [] } = data;
        
        let definition = 'classDiagram\n';
        
        // Add classes
        classes.forEach(cls => {
            definition += `    class ${cls.name} {\n`;
            
            // Add attributes
            if (cls.attributes) {
                cls.attributes.forEach(attr => {
                    const visibility = attr.visibility || '+';
                    const type = attr.type ? `: ${attr.type}` : '';
                    definition += `        ${visibility}${attr.name}${type}\n`;
                });
            }
            
            // Add methods
            if (cls.methods) {
                cls.methods.forEach(method => {
                    const visibility = method.visibility || '+';
                    const params = method.parameters ? method.parameters.join(', ') : '';
                    const returnType = method.returnType ? `: ${method.returnType}` : '';
                    definition += `        ${visibility}${method.name}(${params})${returnType}\n`;
                });
            }
            
            definition += '    }\n';
            
            // Add stereotype
            if (cls.stereotype) {
                definition += `    <<${cls.stereotype}>> ${cls.name}\n`;
            }
        });
        
        // Add relationships
        relationships.forEach(rel => {
            const arrow = this._getRelationshipArrow(rel.type);
            const label = rel.label ? ` : ${rel.label}` : '';
            definition += `    ${rel.from} ${arrow} ${rel.to}${label}\n`;
        });
        
        return definition;
    }
    
    /**
     * Generate ER diagram definition
     * @private
     */
    _generateERDiagram(data) {
        const { entities = [], relationships = [] } = data;
        
        let definition = 'erDiagram\n';
        
        // Add entities with attributes
        entities.forEach(entity => {
            definition += `    ${entity.name} {\n`;
            
            if (entity.attributes) {
                entity.attributes.forEach(attr => {
                    const key = attr.primaryKey ? 'PK' : attr.foreignKey ? 'FK' : '';
                    definition += `        ${attr.type} ${attr.name} ${key}\n`;
                });
            }
            
            definition += '    }\n';
        });
        
        // Add relationships
        relationships.forEach(rel => {
            const cardinality = rel.cardinality || '||--||';
            const label = rel.label ? ` : "${rel.label}"` : '';
            definition += `    ${rel.from} ${cardinality} ${rel.to}${label}\n`;
        });
        
        return definition;
    }
    
    /**
     * Generate sequence diagram definition
     * @private
     */
    _generateSequenceDiagram(data) {
        const { participants = [], interactions = [] } = data;
        
        let definition = 'sequenceDiagram\n';
        
        // Add participants
        participants.forEach(p => {
            const alias = p.alias ? ` as ${p.alias}` : '';
            definition += `    participant ${p.id}${alias}\n`;
        });
        
        // Add interactions
        interactions.forEach(interaction => {
            switch (interaction.type) {
                case 'message':
                    const arrow = interaction.async ? '->>' : '->';
                    definition += `    ${interaction.from}${arrow}${interaction.to}: ${interaction.label}\n`;
                    break;
                case 'activate':
                    definition += `    activate ${interaction.participant}\n`;
                    break;
                case 'deactivate':
                    definition += `    deactivate ${interaction.participant}\n`;
                    break;
                case 'note':
                    const position = interaction.position || 'right of';
                    definition += `    Note ${position} ${interaction.participant}: ${interaction.text}\n`;
                    break;
                case 'loop':
                    definition += `    loop ${interaction.label}\n`;
                    break;
                case 'alt':
                    definition += `    alt ${interaction.label}\n`;
                    break;
                case 'opt':
                    definition += `    opt ${interaction.label}\n`;
                    break;
                case 'end':
                    definition += `    end\n`;
                    break;
            }
        });
        
        return definition;
    }
    
    /**
     * Generate flowchart definition
     * @private
     */
    _generateFlowchart(data) {
        const { nodes = [], edges = [] } = data;
        
        let definition = 'flowchart TB\n';
        
        // Add nodes
        nodes.forEach(node => {
            const shape = this._getNodeShape(node.type);
            definition += `    ${node.id}${shape[0]}${node.label}${shape[1]}\n`;
            
            // Add styling
            if (node.style) {
                definition += `    style ${node.id} ${node.style}\n`;
            }
        });
        
        // Add edges
        edges.forEach(edge => {
            const arrow = edge.type === 'dotted' ? '-.->' : '-->';
            const label = edge.label ? `|${edge.label}|` : '';
            definition += `    ${edge.from} ${arrow}${label} ${edge.to}\n`;
        });
        
        return definition;
    }
    
    /**
     * Get relationship arrow for class diagrams
     * @private
     */
    _getRelationshipArrow(type) {
        const arrows = {
            inheritance: '<|--',
            composition: '*--',
            aggregation: 'o--',
            association: '--',
            dependency: '..>',
            realization: '..|>'
        };
        return arrows[type] || '--';
    }
    
    /**
     * Get node shape for flowcharts
     * @private
     */
    _getNodeShape(type) {
        const shapes = {
            process: ['[', ']'],
            decision: ['{', '}'],
            start: ['([', '])'],
            end: ['([', '])'],
            data: ['[/', '/]'],
            subroutine: ['[[', ']]'],
            default: ['[', ']']
        };
        return shapes[type] || shapes.default;
    }
    
    /**
     * Apply custom styles to rendered diagram
     * @private
     */
    _applyCustomStyles(element) {
        const svg = element.querySelector('svg');
        if (svg) {
            svg.style.maxWidth = '100%';
            svg.style.height = 'auto';
        }
    }
    
    /**
     * Make diagram interactive (zoom, pan)
     * @private
     */
    _makeInteractive(element) {
        const svg = element.querySelector('svg');
        if (!svg) return;
        
        let isPanning = false;
        let startPoint = { x: 0, y: 0 };
        let scale = 1;
        
        svg.style.cursor = 'grab';
        
        svg.addEventListener('mousedown', (e) => {
            isPanning = true;
            startPoint = { x: e.clientX, y: e.clientY };
            svg.style.cursor = 'grabbing';
        });
        
        svg.addEventListener('mousemove', (e) => {
            if (!isPanning) return;
            
            const dx = e.clientX - startPoint.x;
            const dy = e.clientY - startPoint.y;
            
            // Update SVG viewBox for panning
            const viewBox = svg.viewBox.baseVal;
            viewBox.x -= dx / scale;
            viewBox.y -= dy / scale;
            
            startPoint = { x: e.clientX, y: e.clientY };
        });
        
        svg.addEventListener('mouseup', () => {
            isPanning = false;
            svg.style.cursor = 'grab';
        });
        
        svg.addEventListener('wheel', (e) => {
            e.preventDefault();
            
            const delta = e.deltaY > 0 ? 0.9 : 1.1;
            scale *= delta;
            scale = Math.max(0.5, Math.min(scale, 3));
            
            const viewBox = svg.viewBox.baseVal;
            const centerX = viewBox.x + viewBox.width / 2;
            const centerY = viewBox.y + viewBox.height / 2;
            
            viewBox.width /= delta;
            viewBox.height /= delta;
            viewBox.x = centerX - viewBox.width / 2;
            viewBox.y = centerY - viewBox.height / 2;
        });
    }
    
    /**
     * Export diagram as SVG
     * @param {HTMLElement} container - Container with rendered diagram
     * @returns {string} SVG string
     */
    exportSVG(container) {
        const svg = container.querySelector('svg');
        if (!svg) {
            throw new Error('No diagram found in container');
        }
        return svg.outerHTML;
    }
    
    /**
     * Export diagram as PNG
     * @param {HTMLElement} container - Container with rendered diagram
     * @returns {Promise<Blob>}
     */
    async exportPNG(container) {
        const svg = container.querySelector('svg');
        if (!svg) {
            throw new Error('No diagram found in container');
        }
        
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();
        
        return new Promise((resolve, reject) => {
            img.onload = () => {
                canvas.width = img.width;
                canvas.height = img.height;
                ctx.drawImage(img, 0, 0);
                canvas.toBlob(resolve, 'image/png');
            };
            
            img.onerror = reject;
            
            const svgData = new XMLSerializer().serializeToString(svg);
            const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
            img.src = URL.createObjectURL(svgBlob);
        });
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MermaidRenderer;
}
