/**
 * Concrete Visualization Components
 * 
 * Modular components for each dashboard tab
 * - OverviewComponent: Language distribution + health gauge
 * - ArchitectureComponent: Architecture diagram + file tree + dependencies
 * - QualityComponent: Health gauge + language metrics
 * - SecurityComponent: Security donut + vulnerability list
 * - DependencyComponent: Dependency graph
 * - UseCaseComponent: Use case treemap
 * 
 * Each component:
 * - Validates data before rendering
 * - Handles errors gracefully
 * - Provides empty state UI
 * - Integrates with D3.js visualizations
 */

/**
 * OverviewComponent - Renders language distribution and health gauge
 */
class OverviewComponent extends VisualizationComponent {
    validateData(data) {
        super.validateData(data);
        
        // Overview component needs metrics with language data
        if (!data.metrics || typeof data.metrics !== 'object') {
            throw new Error('Overview data missing metrics');
        }
    }

    async _render(data) {
        const languagesContainer = document.createElement('div');
        languagesContainer.id = 'viz-languages-overview';
        languagesContainer.className = 'viz-canvas';
        languagesContainer.style.minHeight = '400px';
        
        this.container.innerHTML = '';
        this.container.appendChild(languagesContainer);
        
        // Extract language data
        const languages = data.metrics?.languages || {};
        if (Object.keys(languages).length === 0) {
            this._renderEmptyState('No language distribution data');
            return;
        }
        
        // Call D3 visualization
        if (window.CortexViz?.createLanguageSunburst) {
            await window.CortexViz.createLanguageSunburst('viz-languages-overview', {
                name: 'codebase',
                value: Object.values(languages).reduce((a, b) => a + b, 0),
                children: Object.entries(languages).map(([lang, count]) => ({
                    name: lang,
                    value: count
                }))
            });
        }
    }
}

/**
 * ArchitectureComponent - Renders architecture diagram, file tree, dependencies
 */
class ArchitectureComponent extends VisualizationComponent {
    validateData(data) {
        super.validateData(data);
        
        if (!data.architecture || typeof data.architecture !== 'object') {
            throw new Error('Architecture data missing');
        }
    }

    async _render(data) {
        const architectureContainer = document.createElement('div');
        architectureContainer.id = 'viz-architecture';
        architectureContainer.className = 'viz-canvas';
        architectureContainer.style.minHeight = '400px';
        
        this.container.innerHTML = '';
        this.container.appendChild(architectureContainer);
        
        // Render architecture tab visualizations
        if (window.CortexViz?.renderArchitectureTab) {
            await window.CortexViz.renderArchitectureTab(data);
        } else {
            this._renderEmptyState('Architecture visualizations unavailable');
        }
    }
}

/**
 * QualityComponent - Renders health gauge and language metrics
 */
class QualityComponent extends VisualizationComponent {
    validateData(data) {
        super.validateData(data);
        
        if (!data.metrics || typeof data.metrics !== 'object') {
            throw new Error('Quality data missing metrics');
        }
    }

    async _render(data) {
        const qualityContainer = document.createElement('div');
        qualityContainer.id = 'viz-quality';
        qualityContainer.className = 'viz-canvas';
        qualityContainer.style.minHeight = '400px';
        
        this.container.innerHTML = '';
        this.container.appendChild(qualityContainer);
        
        // Render quality tab visualizations
        if (window.CortexViz?.renderQualityTab) {
            await window.CortexViz.renderQualityTab(data);
        } else {
            this._renderEmptyState('Quality visualizations unavailable');
        }
    }
}

/**
 * SecurityComponent - Renders security donut and vulnerability list
 */
class SecurityComponent extends VisualizationComponent {
    validateData(data) {
        super.validateData(data);
        
        if (!data.security || typeof data.security !== 'object') {
            throw new Error('Security data missing');
        }
    }

    async _render(data) {
        const securityContainer = document.createElement('div');
        securityContainer.id = 'viz-security';
        securityContainer.className = 'viz-canvas';
        securityContainer.style.minHeight = '400px';
        
        this.container.innerHTML = '';
        this.container.appendChild(securityContainer);
        
        // Render security visualizations
        if (window.CortexViz?.renderSecurityVisualizations) {
            await window.CortexViz.renderSecurityVisualizations(data);
        } else {
            this._renderEmptyState('Security visualizations unavailable');
        }
    }
}

/**
 * DependencyComponent - Renders dependency graph
 */
class DependencyComponent extends VisualizationComponent {
    validateData(data) {
        super.validateData(data);
        
        if (!data.dependencies || typeof data.dependencies !== 'object') {
            throw new Error('Dependencies data missing');
        }
        
        // Ensure packages is an array
        const packages = data.dependencies.packages;
        if (!Array.isArray(packages)) {
            throw new Error('Dependencies.packages must be an array');
        }
        
        if (packages.length === 0) {
            throw new Error('No packages in dependencies');
        }
    }

    async _render(data) {
        const depContainer = document.createElement('div');
        depContainer.id = 'viz-dependencies';
        depContainer.className = 'viz-canvas';
        depContainer.style.minHeight = '500px';
        
        this.container.innerHTML = '';
        this.container.appendChild(depContainer);
        
        // Extract packages array - THIS FIXES THE packages.slice() ERROR
        const packages = Array.isArray(data.dependencies)
            ? data.dependencies
            : data.dependencies.packages || [];
        
        if (packages.length === 0) {
            this._renderEmptyState('No dependencies available');
            return;
        }
        
        // Call D3 visualization
        if (window.CortexViz?.createDependencyGraph) {
            await window.CortexViz.createDependencyGraph('viz-dependencies', packages);
        }
    }
}

/**
 * UseCaseComponent - Renders use case treemap
 */
class UseCaseComponent extends VisualizationComponent {
    validateData(data) {
        super.validateData(data);
        
        // Use cases may not always be present, but if present should be valid
        if (data.usecases && typeof data.usecases !== 'object') {
            throw new Error('Use cases data must be an object');
        }
    }

    async _render(data) {
        const useCaseContainer = document.createElement('div');
        useCaseContainer.id = 'viz-usecases';
        useCaseContainer.className = 'viz-canvas';
        useCaseContainer.style.minHeight = '400px';
        
        this.container.innerHTML = '';
        this.container.appendChild(useCaseContainer);
        
        // Check if use cases data exists
        const usecases = data.usecases || {};
        if (!usecases || Object.keys(usecases).length === 0) {
            this._renderEmptyState('No use cases data available');
            return;
        }
        
        // Render use cases visualizations
        if (window.CortexViz?.renderUseCasesTab) {
            await window.CortexViz.renderUseCasesTab(data);
        } else {
            this._renderEmptyState('Use case visualizations unavailable');
        }
    }
}

// AC_COMPLETE: AC-DASHBOARD-COMPONENTS-001 ✅ Concrete visualization components
