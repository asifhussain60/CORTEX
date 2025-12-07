/**
 * Multi-Solution Dashboard Component
 * 
 * Displays all .NET solutions in repository with project counts,
 * Visual Studio versions, and expandable project details.
 * 
 * Data Source: tech-stack.json → backend[].metadata.solutions[]
 * 
 * Features:
 * - Responsive card grid (3/2/1 columns for desktop/tablet/mobile)
 * - VS version color coding (17=green, 16=yellow, <16=red)
 * - Expandable project lists
 * - Summary statistics
 */

class MultiSolutionDashboard {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.solutions = [];
        this.expandedSolutions = new Set();
    }

    /**
     * Initialize dashboard with tech stack data
     * @param {Object} techStackData - Full tech-stack.json data
     */
    init(techStackData) {
        this.solutions = this.extractSolutions(techStackData);
        this.render();
    }

    /**
     * Extract solutions from tech stack data
     * @param {Object} techStackData - Tech stack JSON
     * @returns {Array} Array of solution objects with metadata
     */
    extractSolutions(techStackData) {
        const solutions = [];
        
        if (!techStackData || !techStackData.backend) {
            return solutions;
        }

        techStackData.backend.forEach(tech => {
            if (tech.metadata && tech.metadata.solutions) {
                tech.metadata.solutions.forEach(solution => {
                    solutions.push({
                        name: solution.name,
                        path: solution.path,
                        projectCount: solution.projects || 0,
                        vsVersion: solution.vs_version || 'Unknown',
                        projects: tech.metadata.projects || []
                    });
                });
            }
        });

        return solutions;
    }

    /**
     * Get VS version number for color coding
     * @param {string} vsVersionString - Full VS version string
     * @returns {number} Version number (e.g., 17, 16, 15)
     */
    getVSVersionNumber(vsVersionString) {
        const match = vsVersionString.match(/(\d+)\./);
        return match ? parseInt(match[1]) : 0;
    }

    /**
     * Get color class based on VS version
     * @param {string} vsVersionString - Full VS version string
     * @returns {string} CSS class name
     */
    getVSVersionColor(vsVersionString) {
        const version = this.getVSVersionNumber(vsVersionString);
        
        if (version >= 17) return 'vs-current';      // Green
        if (version === 16) return 'vs-recent';      // Yellow
        return 'vs-outdated';                         // Red
    }

    /**
     * Toggle solution expanded state
     * @param {string} solutionName - Name of solution to toggle
     */
    toggleSolution(solutionName) {
        if (this.expandedSolutions.has(solutionName)) {
            this.expandedSolutions.delete(solutionName);
        } else {
            this.expandedSolutions.add(solutionName);
        }
        this.render();
    }

    /**
     * Get projects belonging to a solution
     * @param {Object} solution - Solution object
     * @returns {Array} Array of project objects
     */
    getSolutionProjects(solution) {
        // Match projects by solution path prefix
        const solutionDir = solution.path.replace(/[^/]*\.sln$/, '');
        return solution.projects.filter(project => 
            project.path.startsWith(solutionDir)
        );
    }

    /**
     * Calculate summary statistics
     * @returns {Object} Summary stats
     */
    calculateSummary() {
        const totalSolutions = this.solutions.length;
        const totalProjects = this.solutions.reduce((sum, s) => sum + s.projectCount, 0);
        
        const vsVersions = {};
        this.solutions.forEach(solution => {
            const version = this.getVSVersionNumber(solution.vsVersion);
            const key = `VS ${version}`;
            vsVersions[key] = (vsVersions[key] || 0) + 1;
        });

        return {
            totalSolutions,
            totalProjects,
            vsVersions
        };
    }

    /**
     * Render the dashboard
     */
    render() {
        if (!this.container) return;

        const summary = this.calculateSummary();

        this.container.innerHTML = `
            <div class="multi-solution-dashboard">
                <!-- Summary Panel -->
                <div class="summary-panel">
                    <h3>Solution Overview</h3>
                    <div class="summary-stats">
                        <div class="stat-card">
                            <div class="stat-value">${summary.totalSolutions}</div>
                            <div class="stat-label">Solutions</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${summary.totalProjects}</div>
                            <div class="stat-label">Projects</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">Visual Studio Versions</div>
                            <div class="vs-version-breakdown">
                                ${Object.entries(summary.vsVersions)
                                    .map(([version, count]) => `
                                        <div class="vs-version-item">
                                            <span class="version">${version}</span>
                                            <span class="count">${count}</span>
                                        </div>
                                    `).join('')}
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Solution Cards Grid -->
                <div class="solution-cards-grid">
                    ${this.solutions.map(solution => this.renderSolutionCard(solution)).join('')}
                </div>
            </div>
        `;

        // Attach event listeners
        this.attachEventListeners();
    }

    /**
     * Render a single solution card
     * @param {Object} solution - Solution data
     * @returns {string} HTML for solution card
     */
    renderSolutionCard(solution) {
        const isExpanded = this.expandedSolutions.has(solution.name);
        const vsColorClass = this.getVSVersionColor(solution.vsVersion);
        const projects = this.getSolutionProjects(solution);

        return `
            <div class="solution-card ${vsColorClass}">
                <div class="solution-header" data-solution="${solution.name}">
                    <div class="solution-info">
                        <h4 class="solution-name">${solution.name}</h4>
                        <div class="solution-meta">
                            <span class="project-count">${solution.projectCount} projects</span>
                            <span class="vs-version">${solution.vsVersion}</span>
                        </div>
                    </div>
                    <button class="expand-button ${isExpanded ? 'expanded' : ''}">
                        ${isExpanded ? '▼' : '▶'}
                    </button>
                </div>
                
                ${isExpanded ? `
                    <div class="solution-projects">
                        <h5>Projects (${projects.length})</h5>
                        <ul class="project-list">
                            ${projects.map(project => `
                                <li class="project-item">
                                    <span class="project-name">${project.name}</span>
                                    <span class="project-type">${project.type || 'Unknown'}</span>
                                    ${project.packages ? `<span class="project-packages">${project.packages} packages</span>` : ''}
                                </li>
                            `).join('')}
                        </ul>
                        <div class="solution-path">${solution.path}</div>
                    </div>
                ` : ''}
            </div>
        `;
    }

    /**
     * Attach event listeners for interactive elements
     */
    attachEventListeners() {
        // Expand/collapse solution cards
        const headers = this.container.querySelectorAll('.solution-header');
        headers.forEach(header => {
            header.addEventListener('click', (e) => {
                const solutionName = e.currentTarget.dataset.solution;
                this.toggleSolution(solutionName);
            });
        });
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MultiSolutionDashboard;
}
