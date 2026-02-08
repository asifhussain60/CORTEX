/**
 * Architecture Tab Component (🏗️)
 * Renders system architecture with layers, modules, and design patterns
 * Phase S2.2: Architecture visualization and data binding
 */

class ArchitectureTabComponent {
  constructor(containerSelector = '#architecture-tab') {
    this.container = document.querySelector(containerSelector);
    this.data = null;
    this.metadata = null;
    this.initialized = false;
  }

  /**
   * Initialize component with dashboard data
   * @param {Object} dashboardData - Pydantic-validated dashboard schema
   */
  async init(dashboardData) {
    try {
      this.data = dashboardData.architecture;
      this.metadata = dashboardData.metadata;
      
      this.render();
      this.initialized = true;
      
      console.log('✅ Architecture Tab initialized', { 
        layers: this.data.layers?.length || 0,
        modules: Object.keys(this.data.modules || {}).length,
        patterns: this.data.design_patterns?.length || 0
      });
    } catch (error) {
      console.error('❌ Architecture Tab initialization failed:', error);
      this.renderError(error);
    }
  }

  /**
   * Main orchestration - render all architecture sections
   */
  render() {
    if (!this.container) {
      throw new Error('Architecture Tab container not found');
    }

    this.container.innerHTML = '';
    this.container.classList.add('architecture-tab');

    // Header
    this.renderHeader();

    // Content grid
    const contentDiv = document.createElement('div');
    contentDiv.className = 'architecture-content grid md:grid-cols-2 lg:grid-cols-3 gap-6';

    // Architecture layers section
    if (this.data.layers && this.data.layers.length > 0) {
      contentDiv.appendChild(this.renderLayersSection());
    }

    // Modules section
    if (Object.keys(this.data.modules || {}).length > 0) {
      contentDiv.appendChild(this.renderModulesSection());
    }

    // Design patterns section
    if (this.data.design_patterns && this.data.design_patterns.length > 0) {
      contentDiv.appendChild(this.renderPatternsSection());
    }

    // Architecture health metrics
    contentDiv.appendChild(this.renderArchitectureHealth());

    this.container.appendChild(contentDiv);

    // Summary and recommendations
    this.renderSummary();
  }

  /**
   * Render tab header with architecture overview
   */
  renderHeader() {
    const header = document.createElement('div');
    header.className = 'glass-card mb-6 p-6';

    const title = document.createElement('div');
    title.className = 'flex items-center gap-3 mb-2';
    title.innerHTML = `
      <span class="text-2xl">🏗️</span>
      <h1 class="text-2xl font-bold">System Architecture</h1>
    `;
    header.appendChild(title);

    // Quick stats
    const statsRow = document.createElement('div');
    statsRow.className = 'grid grid-cols-4 gap-4 mt-4';
    
    const layerCount = this.data.layers?.length || 0;
    const moduleCount = Object.keys(this.data.modules || {}).length;
    const patternCount = this.data.design_patterns?.length || 0;
    const totalComplexity = this.calculateTotalComplexity();

    const stats = [
      { label: 'Layers', value: layerCount, icon: '📚' },
      { label: 'Modules', value: moduleCount, icon: '📦' },
      { label: 'Design Patterns', value: patternCount, icon: '🎨' },
      { label: 'Avg Complexity', value: totalComplexity.toFixed(1), icon: '⚙️' }
    ];

    stats.forEach(stat => {
      const statDiv = document.createElement('div');
      statDiv.className = 'metric-card';
      statDiv.innerHTML = `
        <div class="flex items-center justify-between">
          <div>
            <div class="text-2xl font-bold">${stat.value}</div>
            <div class="text-sm text-gray-400">${stat.label}</div>
          </div>
          <span class="text-3xl">${stat.icon}</span>
        </div>
      `;
      statsRow.appendChild(statDiv);
    });

    header.appendChild(statsRow);
    this.container.appendChild(header);
  }

  /**
   * Render architecture layers visualization
   */
  renderLayersSection() {
    const section = document.createElement('div');
    section.className = 'glass-card p-6 lg:col-span-2';

    const title = document.createElement('h2');
    title.className = 'text-lg font-semibold mb-4 flex items-center gap-2';
    title.innerHTML = '<span>📚</span> Architecture Layers';
    section.appendChild(title);

    // Layers stack visualization (top to bottom)
    const layersContainer = document.createElement('div');
    layersContainer.className = 'flex flex-col gap-3';

    this.data.layers.forEach((layer, index) => {
      const layerDiv = document.createElement('div');
      layerDiv.className = 'glass-card border-l-4 border-blue-500 p-4 hover:shadow-lg transition';

      // Layer header
      const header = document.createElement('div');
      header.className = 'flex items-center justify-between mb-2';

      const name = document.createElement('div');
      name.className = 'font-semibold text-blue-300';
      name.textContent = `${index + 1}. ${layer.name}`;
      header.appendChild(name);

      const moduleCount = layer.modules?.length || 0;
      const badge = document.createElement('span');
      badge.className = 'text-xs px-2 py-1 rounded-full bg-blue-900/50 text-blue-300';
      badge.textContent = `${moduleCount} modules`;
      header.appendChild(badge);

      layerDiv.appendChild(header);

      // Description
      const desc = document.createElement('p');
      desc.className = 'text-sm text-gray-300 mb-3';
      desc.textContent = layer.description;
      layerDiv.appendChild(desc);

      // Modules in this layer
      if (layer.modules && layer.modules.length > 0) {
        const modulesDiv = document.createElement('div');
        modulesDiv.className = 'mb-3 text-sm';
        
        const modulesLabel = document.createElement('div');
        modulesLabel.className = 'text-xs text-gray-400 mb-1';
        modulesLabel.textContent = 'Modules:';
        modulesDiv.appendChild(modulesLabel);

        const moduleList = document.createElement('div');
        moduleList.className = 'flex flex-wrap gap-2';
        
        layer.modules.forEach(mod => {
          const modTag = document.createElement('span');
          modTag.className = 'px-2 py-1 bg-gray-800 rounded text-xs text-gray-300';
          modTag.textContent = mod;
          moduleList.appendChild(modTag);
        });

        modulesDiv.appendChild(moduleList);
        layerDiv.appendChild(modulesDiv);
      }

      // Technologies
      if (layer.technologies && layer.technologies.length > 0) {
        const techDiv = document.createElement('div');
        techDiv.className = 'text-sm';
        
        const techLabel = document.createElement('div');
        techLabel.className = 'text-xs text-gray-400 mb-1';
        techLabel.textContent = 'Technologies:';
        techDiv.appendChild(techLabel);

        const techList = document.createElement('div');
        techList.className = 'flex flex-wrap gap-2';
        
        layer.technologies.forEach(tech => {
          const techTag = document.createElement('span');
          techTag.className = 'px-2 py-1 bg-purple-900/50 rounded text-xs text-purple-300';
          techTag.textContent = tech;
          techList.appendChild(techTag);
        });

        techDiv.appendChild(techList);
        layerDiv.appendChild(techDiv);
      }

      layersContainer.appendChild(layerDiv);
    });

    section.appendChild(layersContainer);
    return section;
  }

  /**
   * Render code modules with metrics
   */
  renderModulesSection() {
    const section = document.createElement('div');
    section.className = 'glass-card p-6';

    const title = document.createElement('h2');
    title.className = 'text-lg font-semibold mb-4 flex items-center gap-2';
    title.innerHTML = '<span>📦</span> Key Modules';
    section.appendChild(title);

    const modulesContainer = document.createElement('div');
    modulesContainer.className = 'flex flex-col gap-3 max-h-96 overflow-y-auto';

    Object.entries(this.data.modules).slice(0, 10).forEach(([name, module]) => {
      const moduleDiv = document.createElement('div');
      moduleDiv.className = 'glass-card p-3 border-l-4 border-green-500 hover:shadow-lg transition';

      // Module name and LOC
      const header = document.createElement('div');
      header.className = 'flex items-center justify-between mb-2';
      
      const nameEl = document.createElement('div');
      nameEl.className = 'font-semibold text-green-300 truncate';
      nameEl.textContent = name;
      header.appendChild(nameEl);

      const locBadge = document.createElement('span');
      locBadge.className = 'text-xs px-2 py-1 rounded bg-green-900/50 text-green-300 whitespace-nowrap';
      locBadge.textContent = `${this.formatNumber(module.lines_of_code)} LOC`;
      header.appendChild(locBadge);

      moduleDiv.appendChild(header);

      // Metrics grid
      const metricsGrid = document.createElement('div');
      metricsGrid.className = 'grid grid-cols-3 gap-2 text-xs text-gray-400';

      const metrics = [
        { label: 'Files', value: module.files },
        { label: 'Complexity', value: module.complexity.toFixed(1) },
        { label: 'Sub-modules', value: module.sub_modules?.length || 0 }
      ];

      metrics.forEach(metric => {
        const metricEl = document.createElement('div');
        metricEl.className = 'text-center p-1 bg-gray-900/50 rounded';
        metricEl.innerHTML = `
          <div class="font-semibold text-gray-200">${metric.value}</div>
          <div class="text-xs text-gray-500">${metric.label}</div>
        `;
        metricsGrid.appendChild(metricEl);
      });

      moduleDiv.appendChild(metricsGrid);

      // Dependencies count
      if (module.dependencies && module.dependencies.length > 0) {
        const depsDiv = document.createElement('div');
        depsDiv.className = 'mt-2 text-xs text-gray-400';
        depsDiv.innerHTML = `
          <span class="text-orange-400">⚡ ${module.dependencies.length} dependencies</span>
        `;
        moduleDiv.appendChild(depsDiv);
      }

      modulesContainer.appendChild(moduleDiv);
    });

    section.appendChild(modulesContainer);
    return section;
  }

  /**
   * Render design patterns usage
   */
  renderPatternsSection() {
    const section = document.createElement('div');
    section.className = 'glass-card p-6';

    const title = document.createElement('h2');
    title.className = 'text-lg font-semibold mb-4 flex items-center gap-2';
    title.innerHTML = '<span>🎨</span> Design Patterns';
    section.appendChild(title);

    const patternsContainer = document.createElement('div');
    patternsContainer.className = 'flex flex-col gap-3 max-h-96 overflow-y-auto';

    this.data.design_patterns.forEach(pattern => {
      const patternDiv = document.createElement('div');
      patternDiv.className = 'glass-card p-3 border-l-4 border-cyan-500 hover:shadow-lg transition';

      // Pattern name and usage
      const header = document.createElement('div');
      header.className = 'flex items-center justify-between mb-1';
      
      const nameEl = document.createElement('div');
      nameEl.className = 'font-semibold text-cyan-300 text-sm';
      nameEl.textContent = pattern.name;
      header.appendChild(nameEl);

      const usageBadge = document.createElement('span');
      usageBadge.className = 'text-xs px-2 py-1 rounded bg-cyan-900/50 text-cyan-300';
      usageBadge.textContent = `${pattern.usage_count}x`;
      header.appendChild(usageBadge);

      patternDiv.appendChild(header);

      // Description
      const desc = document.createElement('p');
      desc.className = 'text-xs text-gray-400 mb-2 line-clamp-2';
      desc.textContent = pattern.description;
      patternDiv.appendChild(desc);

      // Location
      const location = document.createElement('div');
      location.className = 'text-xs text-gray-500';
      location.innerHTML = `<span class="text-gray-600">Location:</span> ${pattern.location}`;
      patternDiv.appendChild(location);

      patternsContainer.appendChild(patternDiv);
    });

    section.appendChild(patternsContainer);
    return section;
  }

  /**
   * Render architecture health metrics
   */
  renderArchitectureHealth() {
    const section = document.createElement('div');
    section.className = 'glass-card p-6';

    const title = document.createElement('h2');
    title.className = 'text-lg font-semibold mb-4 flex items-center gap-2';
    title.innerHTML = '<span>💪</span> Architecture Health';
    section.appendChild(title);

    // Calculate health metrics
    const moduleCount = Object.keys(this.data.modules || {}).length;
    const avgComplexity = this.calculateTotalComplexity();
    const layerCount = this.data.layers?.length || 0;

    // Health score calculation
    const healthScore = this.calculateArchitectureHealth();
    const healthStatus = this.getHealthStatus(healthScore);
    const healthClass = this.getHealthClass(healthScore);

    // Main health metric
    const healthDiv = document.createElement('div');
    healthDiv.className = `metric-card mb-4 border-l-4 ${healthClass}`;
    healthDiv.innerHTML = `
      <div class="flex items-center justify-between">
        <div>
          <div class="text-3xl font-bold">${healthScore}</div>
          <div class="text-sm text-gray-400">Health Score</div>
          <div class="text-xs text-gray-500 mt-1">${healthStatus}</div>
        </div>
        <div class="text-4xl">${this.getHealthEmoji(healthScore)}</div>
      </div>
    `;
    section.appendChild(healthDiv);

    // Detailed metrics
    const metricsDiv = document.createElement('div');
    metricsDiv.className = 'grid grid-cols-2 gap-3 text-sm';

    const details = [
      {
        label: 'Modularity',
        value: this.calculateModularity(),
        color: 'text-blue-400'
      },
      {
        label: 'Complexity',
        value: avgComplexity.toFixed(1),
        color: 'text-yellow-400'
      },
      {
        label: 'Layering',
        value: layerCount,
        color: 'text-green-400'
      },
      {
        label: 'Pattern Usage',
        value: this.data.design_patterns?.length || 0,
        color: 'text-purple-400'
      }
    ];

    details.forEach(detail => {
      const metricEl = document.createElement('div');
      metricEl.className = 'bg-gray-900/50 p-3 rounded';
      metricEl.innerHTML = `
        <div class="text-xs text-gray-400">${detail.label}</div>
        <div class="text-lg font-semibold ${detail.color}">${detail.value}</div>
      `;
      metricsDiv.appendChild(metricEl);
    });

    section.appendChild(metricsDiv);
    return section;
  }

  /**
   * Render summary and recommendations
   */
  renderSummary() {
    const summaryDiv = document.createElement('div');
    summaryDiv.className = 'glass-card mt-6 p-6';

    const title = document.createElement('h2');
    title.className = 'text-lg font-semibold mb-4 flex items-center gap-2';
    title.innerHTML = '<span>📋</span> Architectural Insights';
    summaryDiv.appendChild(title);

    const insights = this.generateInsights();
    const insightsList = document.createElement('ul');
    insightsList.className = 'space-y-2';

    insights.forEach(insight => {
      const li = document.createElement('li');
      li.className = 'flex gap-3 text-sm text-gray-300';
      li.innerHTML = `
        <span class="text-lg flex-shrink-0">${insight.icon}</span>
        <span>${insight.text}</span>
      `;
      insightsList.appendChild(li);
    });

    summaryDiv.appendChild(insightsList);
    this.container.appendChild(summaryDiv);
  }

  /**
   * Generate architectural insights based on metrics
   */
  generateInsights() {
    const insights = [];
    const layerCount = this.data.layers?.length || 0;
    const moduleCount = Object.keys(this.data.modules || {}).length;
    const avgComplexity = this.calculateTotalComplexity();
    const patternCount = this.data.design_patterns?.length || 0;

    // Layering insights
    if (layerCount <= 2) {
      insights.push({
        icon: '⚠️',
        text: 'Consider separating concerns into more distinct layers for better maintainability'
      });
    } else if (layerCount >= 5) {
      insights.push({
        icon: '✅',
        text: 'Well-structured layered architecture with clear separation of concerns'
      });
    }

    // Modularity insights
    if (moduleCount < 5) {
      insights.push({
        icon: '🔄',
        text: 'Consider breaking down larger modules into smaller, more focused components'
      });
    } else if (moduleCount > 50) {
      insights.push({
        icon: '✅',
        text: 'Strong modularity with numerous well-separated components'
      });
    }

    // Complexity insights
    if (avgComplexity > 20) {
      insights.push({
        icon: '⚠️',
        text: 'Average module complexity is high - consider refactoring complex modules'
      });
    } else if (avgComplexity < 5) {
      insights.push({
        icon: '✅',
        text: 'Modules maintain reasonable complexity levels'
      });
    }

    // Pattern insights
    if (patternCount < 3) {
      insights.push({
        icon: '💡',
        text: 'Explore design patterns to improve architecture and maintainability'
      });
    } else {
      insights.push({
        icon: '✅',
        text: `Strong adoption of ${patternCount} design patterns`
      });
    }

    return insights;
  }

  /**
   * Calculate total average complexity
   */
  calculateTotalComplexity() {
    const modules = Object.values(this.data.modules || {});
    if (modules.length === 0) return 0;
    return modules.reduce((sum, m) => sum + m.complexity, 0) / modules.length;
  }

  /**
   * Calculate modularity score
   */
  calculateModularity() {
    const moduleCount = Object.keys(this.data.modules || {}).length;
    return Math.min(10, Math.ceil(moduleCount / 5));
  }

  /**
   * Calculate overall architecture health score
   */
  calculateArchitectureHealth() {
    const layerCount = this.data.layers?.length || 0;
    const moduleCount = Object.keys(this.data.modules || {}).length;
    const avgComplexity = this.calculateTotalComplexity();
    const patternCount = this.data.design_patterns?.length || 0;

    let score = 70; // Base score

    // Layering: 0-10 points
    if (layerCount >= 3 && layerCount <= 5) score += 10;
    else if (layerCount > 0) score += 5;

    // Modularity: 0-10 points
    if (moduleCount >= 20) score += 10;
    else if (moduleCount >= 10) score += 5;

    // Complexity: 0-10 points
    if (avgComplexity < 8) score += 10;
    else if (avgComplexity < 15) score += 5;

    // Patterns: 0-10 points
    if (patternCount >= 5) score += 10;
    else if (patternCount > 0) score += 5;

    return Math.min(100, score);
  }

  /**
   * Get health status text
   */
  getHealthStatus(score) {
    if (score >= 85) return 'Excellent architecture';
    if (score >= 70) return 'Good architecture';
    if (score >= 50) return 'Fair architecture';
    return 'Needs improvement';
  }

  /**
   * Get health class for styling
   */
  getHealthClass(score) {
    if (score >= 85) return 'border-green-500';
    if (score >= 70) return 'border-blue-500';
    if (score >= 50) return 'border-yellow-500';
    return 'border-red-500';
  }

  /**
   * Get health emoji
   */
  getHealthEmoji(score) {
    if (score >= 85) return '🟢';
    if (score >= 70) return '🔵';
    if (score >= 50) return '🟡';
    return '🔴';
  }

  /**
   * Format number for display
   */
  formatNumber(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  }

  /**
   * Update a specific metric
   */
  updateMetric(name, value) {
    if (this.data.modules && this.data.modules[name]) {
      Object.assign(this.data.modules[name], value);
      this.render();
    }
  }

  /**
   * Export architecture data
   */
  exportData() {
    return {
      architecture: this.data,
      insights: this.generateInsights(),
      health_score: this.calculateArchitectureHealth(),
      export_date: new Date().toISOString()
    };
  }

  /**
   * Render error state
   */
  renderError(error) {
    if (!this.container) return;

    this.container.innerHTML = `
      <div class="glass-card p-6 border-l-4 border-red-500">
        <h2 class="text-lg font-semibold text-red-300 mb-2">⚠️ Architecture Tab Error</h2>
        <p class="text-sm text-gray-300 mb-4">${error.message}</p>
        <code class="text-xs bg-gray-900 p-2 rounded block text-gray-400 overflow-auto">
          ${error.stack}
        </code>
      </div>
    `;
  }
}

// Export for ES6 modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ArchitectureTabComponent;
}
