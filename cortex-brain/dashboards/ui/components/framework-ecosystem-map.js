/**
 * Framework Ecosystem Map Component
 * 
 * Analyzes and displays framework usage across projects, detecting
 * redundancies and consolidation opportunities.
 * 
 * Data Source: tech-stack.json → backend[].metadata.frameworks[]
 * 
 * Features:
 * - Category-based accordion (DI Container, Logging, JSON, Security, etc.)
 * - Redundancy detection (multiple frameworks in same category)
 * - Consolidation recommendations
 * - Framework version tracking
 * - Badge counts per category
 */

class FrameworkEcosystemMap {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.frameworks = [];
        this.categories = {};
        this.redundancies = [];
        this.expandedCategories = new Set();
    }

    /**
     * Initialize map with tech stack data
     * @param {Object} techStackData - Full tech-stack.json data
     */
    init(techStackData) {
        this.frameworks = this.extractFrameworks(techStackData);
        this.categories = this.groupByCategory(this.frameworks);
        this.redundancies = this.detectRedundancies(this.categories);
        this.render();
    }

    /**
     * Extract frameworks from tech stack data
     * @param {Object} techStackData - Tech stack JSON
     * @returns {Array} Array of framework objects with parsed metadata
     */
    extractFrameworks(techStackData) {
        const frameworks = [];
        const seen = new Set();
        
        if (!techStackData || !techStackData.backend) {
            return frameworks;
        }

        techStackData.backend.forEach(tech => {
            if (tech.metadata && tech.metadata.frameworks) {
                tech.metadata.frameworks.forEach(frameworkString => {
                    const parsed = this.parseFrameworkString(frameworkString);
                    const key = `${parsed.name}_${parsed.version}`;
                    
                    if (!seen.has(key)) {
                        seen.add(key);
                        frameworks.push(parsed);
                    }
                });
            }
        });

        return frameworks;
    }

    /**
     * Parse framework string to extract name, version, and category
     * Format: "Autofac 6.4.0 (DI Container)" or "EntityFramework 6.4.4"
     * @param {string} frameworkString - Raw framework string
     * @returns {Object} Parsed framework object
     */
    parseFrameworkString(frameworkString) {
        // Pattern: Name Version (Category) or Name Version
        const withCategory = frameworkString.match(/(.+?)\s+([\d.]+)\s*\((.+?)\)/);
        const withoutCategory = frameworkString.match(/(.+?)\s+([\d.]+)/);
        
        if (withCategory) {
            return {
                name: withCategory[1].trim(),
                version: withCategory[2].trim(),
                category: withCategory[3].trim(),
                raw: frameworkString
            };
        } else if (withoutCategory) {
            return {
                name: withoutCategory[1].trim(),
                version: withoutCategory[2].trim(),
                category: this.inferCategory(withoutCategory[1].trim()),
                raw: frameworkString
            };
        }
        
        // Fallback for malformed strings
        return {
            name: frameworkString,
            version: 'Unknown',
            category: 'Uncategorized',
            raw: frameworkString
        };
    }

    /**
     * Infer category from framework name if not explicitly stated
     * @param {string} name - Framework name
     * @returns {string} Inferred category
     */
    inferCategory(name) {
        const nameLower = name.toLowerCase();
        
        if (nameLower.includes('autofac') || nameLower.includes('unity') || 
            nameLower.includes('ninject') || nameLower.includes('container')) {
            return 'DI Container';
        }
        if (nameLower.includes('log') || nameLower.includes('serilog') || 
            nameLower.includes('nlog')) {
            return 'Logging';
        }
        if (nameLower.includes('json') || nameLower.includes('newtonsoft')) {
            return 'JSON Serialization';
        }
        if (nameLower.includes('entity') || nameLower.includes('dapper') || 
            nameLower.includes('orm')) {
            return 'Data Access';
        }
        if (nameLower.includes('mvc') || nameLower.includes('webapi')) {
            return 'Web Framework';
        }
        if (nameLower.includes('xunit') || nameLower.includes('nunit') || 
            nameLower.includes('moq')) {
            return 'Testing';
        }
        
        return 'Other';
    }

    /**
     * Group frameworks by category
     * @param {Array} frameworks - Array of framework objects
     * @returns {Object} Categories with framework arrays
     */
    groupByCategory(frameworks) {
        const categories = {};
        
        frameworks.forEach(framework => {
            const category = framework.category;
            if (!categories[category]) {
                categories[category] = [];
            }
            categories[category].push(framework);
        });

        return categories;
    }

    /**
     * Detect redundancies (multiple frameworks in same category)
     * @param {Object} categories - Categorized frameworks
     * @returns {Array} Array of redundancy objects
     */
    detectRedundancies(categories) {
        const redundancies = [];
        
        Object.entries(categories).forEach(([category, frameworks]) => {
            if (frameworks.length > 1) {
                redundancies.push({
                    category,
                    count: frameworks.length,
                    frameworks: frameworks.map(f => `${f.name} ${f.version}`),
                    recommendation: this.getConsolidationRecommendation(category, frameworks)
                });
            }
        });

        return redundancies.sort((a, b) => b.count - a.count);
    }

    /**
     * Get consolidation recommendation for redundant category
     * @param {string} category - Category name
     * @param {Array} frameworks - Frameworks in category
     * @returns {string} Recommendation text
     */
    getConsolidationRecommendation(category, frameworks) {
        const names = frameworks.map(f => f.name);
        
        // Category-specific recommendations
        if (category === 'DI Container') {
            if (names.includes('Autofac') && names.includes('Unity')) {
                return 'Migrate to Autofac (modern, actively maintained). Unity is in maintenance mode.';
            }
            return 'Standardize on one DI container to reduce complexity and improve consistency.';
        }
        
        if (category === 'Logging') {
            if (names.includes('Serilog') && names.includes('log4net')) {
                return 'Migrate to Serilog (structured logging, better diagnostics). log4net is legacy.';
            }
            return 'Consolidate to Serilog for structured logging and modern diagnostics.';
        }
        
        if (category === 'JSON Serialization') {
            if (names.includes('Newtonsoft.Json') && names.includes('System.Text.Json')) {
                return 'Prefer System.Text.Json for .NET 6+ (performance, built-in). Keep Newtonsoft for legacy compatibility.';
            }
            return 'Use System.Text.Json for new code (performance, modern features).';
        }
        
        // Generic recommendation
        return `Review ${category.toLowerCase()} frameworks and consolidate to reduce maintenance overhead.`;
    }

    /**
     * Toggle category expanded state
     * @param {string} category - Category name
     */
    toggleCategory(category) {
        if (this.expandedCategories.has(category)) {
            this.expandedCategories.delete(category);
        } else {
            this.expandedCategories.add(category);
        }
        this.render();
    }

    /**
     * Render the map
     */
    render() {
        if (!this.container) return;

        const sortedCategories = Object.keys(this.categories).sort();

        this.container.innerHTML = `
            <div class="framework-ecosystem-map">
                <!-- Summary -->
                <div class="ecosystem-summary">
                    <h3>Framework Ecosystem Analysis</h3>
                    <div class="summary-stats">
                        <div class="stat">
                            <span class="stat-value">${this.frameworks.length}</span>
                            <span class="stat-label">Total Frameworks</span>
                        </div>
                        <div class="stat">
                            <span class="stat-value">${sortedCategories.length}</span>
                            <span class="stat-label">Categories</span>
                        </div>
                        <div class="stat ${this.redundancies.length > 0 ? 'warning' : ''}">
                            <span class="stat-value">${this.redundancies.length}</span>
                            <span class="stat-label">Redundancies</span>
                        </div>
                    </div>
                </div>

                <!-- Redundancies Alert -->
                ${this.redundancies.length > 0 ? this.renderRedundancies() : ''}

                <!-- Category Accordion -->
                <div class="category-accordion">
                    ${sortedCategories.map(category => this.renderCategory(category)).join('')}
                </div>
            </div>
        `;

        this.attachEventListeners();
    }

    /**
     * Render redundancies alert section
     * @returns {string} HTML for redundancies
     */
    renderRedundancies() {
        return `
            <div class="redundancies-alert">
                <h4>⚠️ Consolidation Opportunities (${this.redundancies.length})</h4>
                <div class="redundancies-grid">
                    ${this.redundancies.map(redundancy => `
                        <div class="redundancy-card">
                            <div class="redundancy-header">
                                <h5>${redundancy.category}</h5>
                                <span class="redundancy-badge">${redundancy.count} frameworks</span>
                            </div>
                            <div class="redundancy-frameworks">
                                ${redundancy.frameworks.map(f => `<span class="framework-tag">${f}</span>`).join('')}
                            </div>
                            <div class="redundancy-recommendation">
                                <strong>💡 Recommendation:</strong> ${redundancy.recommendation}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    /**
     * Render a category card
     * @param {string} category - Category name
     * @returns {string} HTML for category
     */
    renderCategory(category) {
        const frameworks = this.categories[category];
        const isExpanded = this.expandedCategories.has(category);
        const hasRedundancy = this.redundancies.some(r => r.category === category);

        return `
            <div class="category-card ${hasRedundancy ? 'has-redundancy' : ''}">
                <div class="category-header" data-category="${category}">
                    <div class="category-info">
                        <h4>${category}</h4>
                        <span class="framework-count">${frameworks.length} framework${frameworks.length !== 1 ? 's' : ''}</span>
                    </div>
                    <div class="category-actions">
                        ${hasRedundancy ? '<span class="redundancy-icon">⚠️</span>' : ''}
                        <button class="expand-button ${isExpanded ? 'expanded' : ''}">
                            ${isExpanded ? '▼' : '▶'}
                        </button>
                    </div>
                </div>
                
                ${isExpanded ? `
                    <div class="category-content">
                        <table class="frameworks-table">
                            <thead>
                                <tr>
                                    <th>Framework</th>
                                    <th>Version</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${frameworks.map(f => `
                                    <tr>
                                        <td class="framework-name">${f.name}</td>
                                        <td class="framework-version">${f.version}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                ` : ''}
            </div>
        `;
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        const headers = this.container.querySelectorAll('.category-header');
        headers.forEach(header => {
            header.addEventListener('click', (e) => {
                const category = e.currentTarget.dataset.category;
                this.toggleCategory(category);
            });
        });
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FrameworkEcosystemMap;
}
