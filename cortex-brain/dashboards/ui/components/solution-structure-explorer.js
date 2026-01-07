/**
 * Solution Structure Explorer Component
 * D3.js hierarchical tree: solutions → projects → frameworks
 * Features: Zoom/pan, collapsible nodes, lazy rendering, SVG export
 */

class SolutionStructureExplorer {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        
        // Configuration
        this.width = options.width || 1400;
        this.height = options.height || 800;
        this.nodeRadius = options.nodeRadius || 8;
        this.minZoom = options.minZoom || 0.1;
        this.maxZoom = options.maxZoom || 3;
        
        // State
        this.data = null;
        this.root = null;
        this.svg = null;
        this.g = null;
        this.zoom = null;
        this.tree = null;
        
        // Initialize
        this.initialize();
    }
    
    initialize() {
        // Create SVG container
        this.svg = d3.select(`#${this.containerId}`)
            .append('svg')
            .attr('width', '100%')
            .attr('height', this.height)
            .attr('viewBox', [0, 0, this.width, this.height]);
        
        // Create zoom behavior
        this.zoom = d3.zoom()
            .scaleExtent([this.minZoom, this.maxZoom])
            .on('zoom', (event) => {
                this.g.attr('transform', event.transform);
            });
        
        this.svg.call(this.zoom);
        
        // Create main group for tree
        this.g = this.svg.append('g')
            .attr('transform', `translate(${this.width / 2}, 50)`);
        
        // Create tree layout
        this.tree = d3.tree()
            .size([this.width - 200, this.height - 100])
            .separation((a, b) => (a.parent === b.parent ? 1 : 1.5));
    }
    
    async loadData(techStackPath) {
        try {
            const response = await fetch(techStackPath);
            const techStack = await response.json();
            this.data = this.transformData(techStack);
            this.render();
        } catch (error) {
            console.error('Error loading tech stack data:', error);
            this.showError('Failed to load data');
        }
    }
    
    transformData(techStack) {
        // Transform tech-stack.json into hierarchical structure
        const root = {
            name: 'Solutions',
            type: 'root',
            children: []
        };
        
        // Group by solution
        const solutionsMap = new Map();
        
        techStack.backend.forEach(backend => {
            const metadata = backend.metadata || {};
            const solutions = metadata.solutions || [];
            
            solutions.forEach(solution => {
                if (!solutionsMap.has(solution.name)) {
                    solutionsMap.set(solution.name, {
                        name: solution.name,
                        type: 'solution',
                        vsVersion: this.extractVSVersion(solution.vsVersion),
                        status: this.inferStatus(solution),
                        projects: [],
                        _collapsed: false
                    });
                }
                
                const solutionNode = solutionsMap.get(solution.name);
                
                // Add projects
                (solution.projects || []).forEach(project => {
                    const projectNode = {
                        name: project.name,
                        type: 'project',
                        framework: project.framework || 'Unknown',
                        packageCount: project.packageCount || 0,
                        loc: this.estimateLOC(project),
                        status: this.inferProjectStatus(project),
                        children: [],
                        _collapsed: true // Start collapsed for performance
                    };
                    
                    // Add frameworks
                    const frameworks = this.extractFrameworks(backend, project);
                    frameworks.forEach(framework => {
                        projectNode.children.push({
                            name: framework.name,
                            type: 'framework',
                            version: framework.version,
                            category: framework.category
                        });
                    });
                    
                    solutionNode.projects.push(projectNode);
                });
            });
        });
        
        // Convert map to array
        root.children = Array.from(solutionsMap.values()).map(solution => {
            solution.children = solution.projects;
            delete solution.projects;
            return solution;
        });
        
        return root;
    }
    
    extractVSVersion(vsVersion) {
        if (!vsVersion) return 'Unknown';
        const match = vsVersion.match(/(\d+)/);
        return match ? parseInt(match[1]) : 0;
    }
    
    inferStatus(solution) {
        const vsVersion = this.extractVSVersion(solution.vsVersion);
        if (vsVersion >= 17) return 'Active';
        if (vsVersion >= 16) return 'Maintenance';
        return 'Legacy';
    }
    
    inferProjectStatus(project) {
        const framework = project.framework || '';
        if (framework.includes('.NET 8') || framework.includes('.NET 7')) return 'Active';
        if (framework.includes('.NET 6') || framework.includes('.NET Core')) return 'Maintenance';
        return 'Legacy';
    }
    
    estimateLOC(project) {
        // Estimate LOC based on package count (rough heuristic)
        const packageCount = project.packageCount || 0;
        return packageCount * 150; // Rough estimate: 150 LOC per package
    }
    
    extractFrameworks(backend, project) {
        // Extract frameworks from metadata
        const frameworks = [];
        const metadata = backend.metadata || {};
        
        // Get frameworks from project metadata
        if (project.frameworks) {
            project.frameworks.forEach(fw => {
                frameworks.push(this.parseFramework(fw));
            });
        }
        
        // Get frameworks from backend metadata
        if (metadata.frameworks) {
            metadata.frameworks.forEach(fw => {
                if (!frameworks.some(f => f.name === this.parseFramework(fw).name)) {
                    frameworks.push(this.parseFramework(fw));
                }
            });
        }
        
        return frameworks;
    }
    
    parseFramework(frameworkString) {
        // Parse "Autofac 6.4.0 (DI Container)" format
        const withCategory = frameworkString.match(/^(.+?)\s+([\d.]+)\s*\((.+)\)$/);
        if (withCategory) {
            return {
                name: withCategory[1],
                version: withCategory[2],
                category: withCategory[3]
            };
        }
        
        // Parse "EntityFramework 6.4.4" format
        const withoutCategory = frameworkString.match(/^(.+?)\s+([\d.]+)$/);
        if (withoutCategory) {
            return {
                name: withoutCategory[1],
                version: withoutCategory[2],
                category: 'Other'
            };
        }
        
        return {
            name: frameworkString,
            version: 'Unknown',
            category: 'Other'
        };
    }
    
    render() {
        if (!this.data) return;
        
        // Create hierarchy
        this.root = d3.hierarchy(this.data);
        
        // Collapse all projects initially for performance
        this.root.descendants().forEach(d => {
            if (d.data.type === 'project' && d.children) {
                d._children = d.children;
                d.children = null;
            }
        });
        
        this.update(this.root);
        
        // Center view
        this.centerView();
    }
    
    update(source) {
        // Generate tree layout
        const treeData = this.tree(this.root);
        const nodes = treeData.descendants();
        const links = treeData.links();
        
        // Normalize for fixed-depth
        nodes.forEach(d => {
            d.y = d.depth * 200;
        });
        
        // Update nodes
        const node = this.g.selectAll('.node')
            .data(nodes, d => d.id || (d.id = ++this.nodeIdCounter || (this.nodeIdCounter = 1)));
        
        // Enter new nodes
        const nodeEnter = node.enter().append('g')
            .attr('class', 'node')
            .attr('transform', d => `translate(${source.y0 || 0}, ${source.x0 || 0})`)
            .on('click', (event, d) => this.handleNodeClick(event, d));
        
        // Add circles for nodes
        nodeEnter.append('circle')
            .attr('r', d => this.getNodeRadius(d))
            .attr('class', d => `node-circle ${d.data.type}`)
            .style('fill', d => this.getNodeColor(d))
            .style('stroke', '#2c3e50')
            .style('stroke-width', 2)
            .style('cursor', d => (d.children || d._children) ? 'pointer' : 'default');
        
        // Add labels
        nodeEnter.append('text')
            .attr('dy', '0.35em')
            .attr('x', d => (d.children || d._children) ? -15 : 15)
            .attr('text-anchor', d => (d.children || d._children) ? 'end' : 'start')
            .text(d => this.getNodeLabel(d))
            .style('font-size', '12px')
            .style('fill', '#2c3e50');
        
        // Transition nodes to their new position
        const nodeUpdate = nodeEnter.merge(node);
        
        nodeUpdate.transition()
            .duration(750)
            .attr('transform', d => `translate(${d.y}, ${d.x})`);
        
        nodeUpdate.select('circle')
            .attr('r', d => this.getNodeRadius(d))
            .style('fill', d => this.getNodeColor(d));
        
        // Remove exiting nodes
        const nodeExit = node.exit().transition()
            .duration(750)
            .attr('transform', d => `translate(${source.y}, ${source.x})`)
            .remove();
        
        nodeExit.select('circle')
            .attr('r', 0);
        
        nodeExit.select('text')
            .style('fill-opacity', 0);
        
        // Update links
        const link = this.g.selectAll('.link')
            .data(links, d => d.target.id);
        
        // Enter new links
        const linkEnter = link.enter().insert('path', 'g')
            .attr('class', 'link')
            .attr('d', d => {
                const o = {x: source.x0 || 0, y: source.y0 || 0};
                return this.diagonal(o, o);
            })
            .style('fill', 'none')
            .style('stroke', '#ccc')
            .style('stroke-width', 2);
        
        // Transition links to their new position
        const linkUpdate = linkEnter.merge(link);
        
        linkUpdate.transition()
            .duration(750)
            .attr('d', d => this.diagonal(d.source, d.target));
        
        // Remove exiting links
        link.exit().transition()
            .duration(750)
            .attr('d', d => {
                const o = {x: source.x, y: source.y};
                return this.diagonal(o, o);
            })
            .remove();
        
        // Store old positions for transition
        nodes.forEach(d => {
            d.x0 = d.x;
            d.y0 = d.y;
        });
    }
    
    diagonal(s, d) {
        // Create curved path between nodes
        return `M ${s.y} ${s.x}
                C ${(s.y + d.y) / 2} ${s.x},
                  ${(s.y + d.y) / 2} ${d.x},
                  ${d.y} ${d.x}`;
    }
    
    handleNodeClick(event, d) {
        if (d.children) {
            d._children = d.children;
            d.children = null;
        } else if (d._children) {
            d.children = d._children;
            d._children = null;
        }
        this.update(d);
    }
    
    getNodeRadius(d) {
        if (d.data.type === 'root') return 12;
        if (d.data.type === 'solution') return 10;
        if (d.data.type === 'project') {
            // Size based on LOC
            const loc = d.data.loc || 0;
            return Math.max(6, Math.min(12, 6 + (loc / 10000)));
        }
        return 6;
    }
    
    getNodeColor(d) {
        const status = d.data.status;
        
        if (d.data.type === 'root') return '#3498db';
        if (d.data.type === 'solution') {
            if (status === 'Active') return '#27ae60';
            if (status === 'Maintenance') return '#f39c12';
            return '#e74c3c';
        }
        if (d.data.type === 'project') {
            if (status === 'Active') return '#2ecc71';
            if (status === 'Maintenance') return '#f1c40f';
            return '#e67e22';
        }
        if (d.data.type === 'framework') {
            return '#95a5a6';
        }
        return '#bdc3c7';
    }
    
    getNodeLabel(d) {
        if (d.data.type === 'root') return d.data.name;
        if (d.data.type === 'solution') {
            const vsVersion = d.data.vsVersion;
            return `${d.data.name} (VS${vsVersion})`;
        }
        if (d.data.type === 'project') {
            const packageCount = d.data.packageCount;
            return `${d.data.name} (${packageCount} packages)`;
        }
        if (d.data.type === 'framework') {
            return `${d.data.name} ${d.data.version}`;
        }
        return d.data.name;
    }
    
    centerView() {
        // Center the view on the root node
        const bounds = this.g.node().getBBox();
        const fullWidth = this.width;
        const fullHeight = this.height;
        const width = bounds.width;
        const height = bounds.height;
        
        const midX = bounds.x + width / 2;
        const midY = bounds.y + height / 2;
        
        const scale = 0.9 / Math.max(width / fullWidth, height / fullHeight);
        const translate = [fullWidth / 2 - scale * midX, fullHeight / 2 - scale * midY];
        
        this.svg.transition()
            .duration(750)
            .call(
                this.zoom.transform,
                d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale)
            );
    }
    
    expandAll() {
        this.root.descendants().forEach(d => {
            if (d._children) {
                d.children = d._children;
                d._children = null;
            }
        });
        this.update(this.root);
    }
    
    collapseAll() {
        this.root.descendants().forEach(d => {
            if (d.children && d.data.type !== 'root') {
                d._children = d.children;
                d.children = null;
            }
        });
        this.update(this.root);
    }
    
    filterByStatus(status) {
        // Filter nodes by status
        this.root.descendants().forEach(d => {
            if (d.data.status === status) {
                // Expand path to this node
                let parent = d.parent;
                while (parent) {
                    if (parent._children) {
                        parent.children = parent._children;
                        parent._children = null;
                    }
                    parent = parent.parent;
                }
            }
        });
        this.update(this.root);
    }
    
    exportToSVG() {
        // Export current view to SVG file
        const svgElement = this.svg.node();
        const serializer = new XMLSerializer();
        const svgString = serializer.serializeToString(svgElement);
        
        // Add XML declaration and DOCTYPE
        const svgBlob = new Blob(
            ['<?xml version="1.0" standalone="no"?>\r\n', svgString],
            {type: 'image/svg+xml;charset=utf-8'}
        );
        
        const url = URL.createObjectURL(svgBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'solution-structure.svg';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }
    
    showError(message) {
        this.container.innerHTML = `
            <div style="padding: 3rem; text-align: center; color: #e74c3c;">
                <p style="font-size: 1.2rem; margin-bottom: 1rem;">⚠️ Error</p>
                <p>${message}</p>
            </div>
        `;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SolutionStructureExplorer;
}
