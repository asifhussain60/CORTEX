/**
 * Quality Tab Component (✅)
 * Renders code quality metrics, coverage, and assessments
 * Phase S2.3: Quality visualization with detailed metrics
 */

class QualityTabComponent {
  constructor(containerSelector = '#quality-tab') {
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
      this.data = dashboardData.quality;
      this.metadata = dashboardData.metadata;
      
      this.render();
      this.initialized = true;
      
      console.log('✅ Quality Tab initialized', { 
        quality_score: this.data.code_quality_score,
        coverage: this.data.test_coverage,
        debt_hours: this.data.technical_debt_hours
      });
    } catch (error) {
      console.error('❌ Quality Tab initialization failed:', error);
      this.renderError(error);
    }
  }

  /**
   * Main orchestration - render all quality sections
   */
  render() {
    if (!this.container) {
      throw new Error('Quality Tab container not found');
    }

    this.container.innerHTML = '';
    this.container.classList.add('quality-tab');

    // Header with quality overview
    this.renderHeader();

    // Main metrics grid
    const contentDiv = document.createElement('div');
    contentDiv.className = 'quality-content grid md:grid-cols-2 lg:grid-cols-3 gap-6';

    // Core quality metrics
    contentDiv.appendChild(this.renderQualityMetrics());
    
    // Code health cards
    contentDiv.appendChild(this.renderCodeHealth());
    
    // Coverage visualization
    contentDiv.appendChild(this.renderCoverage());
    
    // Technical debt
    contentDiv.appendChild(this.renderTechnicalDebt());

    this.container.appendChild(contentDiv);

    // Detailed analysis
    this.renderDetailedAnalysis();
  }

  /**
   * Render tab header with quality overview
   */
  renderHeader() {
    const header = document.createElement('div');
    header.className = 'glass-card mb-6 p-6';

    const title = document.createElement('div');
    title.className = 'flex items-center gap-3 mb-2';
    title.innerHTML = `
      <span class="text-2xl">✅</span>
      <h1 class="text-2xl font-bold">Code Quality</h1>
    `;
    header.appendChild(title);

    // Quality score gauge
    const gaugeContainer = document.createElement('div');
    gaugeContainer.className = 'mt-4 grid grid-cols-3 gap-4';

    const scoreDiv = document.createElement('div');
    scoreDiv.className = 'glass-card p-4 text-center';
    
    const qualityScore = this.data.code_quality_score;
    const qualityClass = this.getQualityClass(qualityScore);
    const qualityText = this.getQualityText(qualityScore);
    const qualityEmoji = this.getQualityEmoji(qualityScore);

    scoreDiv.innerHTML = `
      <div class="text-3xl mb-2">${qualityEmoji}</div>
      <div class="text-4xl font-bold ${qualityClass}">${qualityScore.toFixed(1)}/10</div>
      <div class="text-sm text-gray-400 mt-2">${qualityText}</div>
    `;
    gaugeContainer.appendChild(scoreDiv);

    // Maintainability gauge
    const maintDiv = document.createElement('div');
    maintDiv.className = 'glass-card p-4 text-center';
    
    const maintScore = this.data.maintainability_index;
    const maintClass = this.getMaintainabilityClass(maintScore);
    const maintEmoji = this.getMaintainabilityEmoji(maintScore);

    maintDiv.innerHTML = `
      <div class="text-3xl mb-2">${maintEmoji}</div>
      <div class="text-4xl font-bold ${maintClass}">${maintScore.toFixed(1)}</div>
      <div class="text-sm text-gray-400 mt-2">Maintainability</div>
    `;
    gaugeContainer.appendChild(maintDiv);

    // Coverage gauge
    const covDiv = document.createElement('div');
    covDiv.className = 'glass-card p-4 text-center';
    
    const coverage = this.data.test_coverage;
    const covClass = this.getCoverageClass(coverage);
    const covEmoji = this.getCoverageEmoji(coverage);

    covDiv.innerHTML = `
      <div class="text-3xl mb-2">${covEmoji}</div>
      <div class="text-4xl font-bold ${covClass}">${coverage.toFixed(1)}%</div>
      <div class="text-sm text-gray-400 mt-2">Test Coverage</div>
    `;
    gaugeContainer.appendChild(covDiv);

    header.appendChild(gaugeContainer);
    this.container.appendChild(header);
  }

  /**
   * Render core quality metrics
   */
  renderQualityMetrics() {
    const section = document.createElement('div');
    section.className = 'glass-card p-6 lg:col-span-2';

    const title = document.createElement('h2');
    title.className = 'text-lg font-semibold mb-4 flex items-center gap-2';
    title.innerHTML = '<span>📊</span> Quality Metrics';
    section.appendChild(title);

    const metricsGrid = document.createElement('div');
    metricsGrid.className = 'space-y-3';

    const metrics = [
      {
        label: 'Code Quality Score',
        value: this.data.code_quality_score,
        max: 10,
        icon: '⭐',
        color: 'blue',
        unit: '/10'
      },
      {
        label: 'Maintainability Index',
        value: this.data.maintainability_index,
        max: 100,
        icon: '🔧',
        color: 'green',
        unit: '/100'
      },
      {
        label: 'Test Coverage',
        value: this.data.test_coverage,
        max: 100,
        icon: '🎯',
        color: 'purple',
        unit: '%'
      },
      {
        label: 'Code Duplication',
        value: this.data.duplication_percentage,
        max: 100,
        icon: '📋',
        color: 'orange',
        unit: '%',
        invert: true
      }
    ];

    metrics.forEach(metric => {
      const metricEl = document.createElement('div');
      metricEl.className = 'space-y-2';

      // Header
      const header = document.createElement('div');
      header.className = 'flex items-center justify-between';

      const labelDiv = document.createElement('div');
      labelDiv.className = 'flex items-center gap-2';
      labelDiv.innerHTML = `
        <span class="text-lg">${metric.icon}</span>
        <span class="font-semibold text-gray-200">${metric.label}</span>
      `;
      header.appendChild(labelDiv);

      const valueDiv = document.createElement('div');
      valueDiv.className = `text-lg font-bold text-${metric.color}-400`;
      valueDiv.textContent = `${metric.value.toFixed(2)}${metric.unit}`;
      header.appendChild(valueDiv);

      metricEl.appendChild(header);

      // Progress bar
      const progressDiv = document.createElement('div');
      progressDiv.className = 'bg-gray-900 rounded-full h-2 overflow-hidden';

      const barDiv = document.createElement('div');
      barDiv.className = `bg-gradient-to-r from-${metric.color}-600 to-${metric.color}-400 h-full transition-all duration-300`;
      
      const percentage = metric.invert 
        ? 100 - (metric.value / metric.max * 100)
        : (metric.value / metric.max * 100);
      barDiv.style.width = `${percentage}%`;
      
      progressDiv.appendChild(barDiv);
      metricEl.appendChild(progressDiv);

      metricsGrid.appendChild(metricEl);
    });

    section.appendChild(metricsGrid);
    return section;
  }

  /**
   * Render code health status
   */
  renderCodeHealth() {
    const section = document.createElement('div');
    section.className = 'glass-card p-6';

    const title = document.createElement('h2');
    title.className = 'text-lg font-semibold mb-4 flex items-center gap-2';
    title.innerHTML = '<span>💪</span> Code Health';
    section.appendChild(title);

    const healthCards = document.createElement('div');
    healthCards.className = 'space-y-3';

    // Code Smells
    const smellsDiv = document.createElement('div');
    smellsDiv.className = 'glass-card border-l-4 border-red-500 p-4';

    const smellsCount = this.data.code_smells || 0;
    const smellsStatus = this.getSmellsStatus(smellsCount);
    const smellsEmoji = this.getSmellsEmoji(smellsCount);

    smellsDiv.innerHTML = `
      <div class="flex items-center justify-between mb-1">
        <div class="flex items-center gap-2">
          <span class="text-xl">${smellsEmoji}</span>
          <span class="font-semibold text-red-300">Code Smells</span>
        </div>
        <span class="text-2xl font-bold text-red-400">${smellsCount}</span>
      </div>
      <div class="text-xs text-gray-400">${smellsStatus}</div>
    `;
    healthCards.appendChild(smellsDiv);

    // Technical Debt
    const debtDiv = document.createElement('div');
    debtDiv.className = 'glass-card border-l-4 border-yellow-500 p-4';

    const debtHours = this.data.technical_debt_hours || 0;
    const debtStatus = this.getDebtStatus(debtHours);
    const debtEmoji = this.getDebtEmoji(debtHours);
    const debtDisplay = this.formatDays(debtHours);

    debtDiv.innerHTML = `
      <div class="flex items-center justify-between mb-1">
        <div class="flex items-center gap-2">
          <span class="text-xl">${debtEmoji}</span>
          <span class="font-semibold text-yellow-300">Technical Debt</span>
        </div>
        <span class="text-2xl font-bold text-yellow-400">${debtDisplay}</span>
      </div>
      <div class="text-xs text-gray-400">${debtStatus}</div>
    `;
    healthCards.appendChild(debtDiv);

    section.appendChild(healthCards);
    return section;
  }

  /**
   * Render test coverage visualization
   */
  renderCoverage() {
    const section = document.createElement('div');
    section.className = 'glass-card p-6';

    const title = document.createElement('h2');
    title.className = 'text-lg font-semibold mb-4 flex items-center gap-2';
    title.innerHTML = '<span>🎯</span> Test Coverage';
    section.appendChild(title);

    const coverage = this.data.test_coverage;
    const coverageClass = this.getCoverageClass(coverage);

    // Large coverage display
    const coverageDiv = document.createElement('div');
    coverageDiv.className = 'text-center mb-4';
    
    const coverageCircle = document.createElement('div');
    coverageCircle.className = `mx-auto w-32 h-32 rounded-full flex items-center justify-center ${coverageClass} bg-opacity-20 border-2 ${coverageClass} flex flex-col`;

    const coveragePercent = document.createElement('div');
    coveragePercent.className = `text-4xl font-bold ${coverageClass}`;
    coveragePercent.textContent = `${coverage.toFixed(1)}%`;
    
    const coverageLabel = document.createElement('div');
    coverageLabel.className = 'text-xs text-gray-400 mt-1';
    coverageLabel.textContent = 'Coverage';

    coverageCircle.appendChild(coveragePercent);
    coverageCircle.appendChild(coverageLabel);
    coverageDiv.appendChild(coverageCircle);

    section.appendChild(coverageDiv);

    // Coverage assessment
    const assessmentDiv = document.createElement('div');
    assessmentDiv.className = 'text-sm text-gray-300 text-center';
    assessmentDiv.textContent = this.getCoverageAssessment(coverage);
    section.appendChild(assessmentDiv);

    return section;
  }

  /**
   * Render technical debt details
   */
  renderTechnicalDebt() {
    const section = document.createElement('div');
    section.className = 'glass-card p-6 lg:col-span-2';

    const title = document.createElement('h2');
    title.className = 'text-lg font-semibold mb-4 flex items-center gap-2';
    title.innerHTML = '<span>⚡</span> Technical Debt Analysis';
    section.appendChild(title);

    const debtHours = this.data.technical_debt_hours || 0;
    const debtDays = debtHours / 8;
    const debtWeeks = debtDays / 5;

    // Debt breakdown
    const breakdownDiv = document.createElement('div');
    breakdownDiv.className = 'grid grid-cols-3 gap-3 mb-4';

    const breakdownItems = [
      { label: 'Total Hours', value: debtHours.toFixed(0), unit: 'h' },
      { label: 'In Days', value: debtDays.toFixed(1), unit: 'd' },
      { label: 'In Weeks', value: debtWeeks.toFixed(1), unit: 'w' }
    ];

    breakdownItems.forEach(item => {
      const itemDiv = document.createElement('div');
      itemDiv.className = 'bg-gray-900 p-3 rounded text-center';
      itemDiv.innerHTML = `
        <div class="text-2xl font-bold text-yellow-400">${item.value}</div>
        <div class="text-xs text-gray-400">${item.label}</div>
        <div class="text-xs text-yellow-600">${item.unit}</div>
      `;
      breakdownDiv.appendChild(itemDiv);
    });

    section.appendChild(breakdownDiv);

    // Debt priority
    const priorityDiv = document.createElement('div');
    priorityDiv.className = 'text-sm text-gray-300';
    priorityDiv.innerHTML = `
      <div class="font-semibold mb-2">Priority:</div>
      <div class="text-xs text-gray-400">${this.getDebtPriority(debtHours)}</div>
    `;
    section.appendChild(priorityDiv);

    return section;
  }

  /**
   * Render detailed quality analysis
   */
  renderDetailedAnalysis() {
    const analysisDiv = document.createElement('div');
    analysisDiv.className = 'glass-card mt-6 p-6';

    const title = document.createElement('h2');
    title.className = 'text-lg font-semibold mb-4 flex items-center gap-2';
    title.innerHTML = '<span>📈</span> Quality Assessment';
    analysisDiv.appendChild(title);

    const insights = this.generateQualityInsights();
    const insightsList = document.createElement('ul');
    insightsList.className = 'space-y-2';

    insights.forEach(insight => {
      const li = document.createElement('li');
      li.className = 'flex gap-3 text-sm';
      
      const icon = document.createElement('span');
      icon.className = 'text-lg flex-shrink-0';
      icon.textContent = insight.icon;
      
      const text = document.createElement('span');
      text.className = insight.color;
      text.textContent = insight.text;

      li.appendChild(icon);
      li.appendChild(text);
      insightsList.appendChild(li);
    });

    analysisDiv.appendChild(insightsList);
    this.container.appendChild(analysisDiv);
  }

  /**
   * Generate quality insights
   */
  generateQualityInsights() {
    const insights = [];

    // Quality insights
    if (this.data.code_quality_score >= 8) {
      insights.push({
        icon: '✅',
        text: 'Excellent code quality - maintain current standards',
        color: 'text-green-400'
      });
    } else if (this.data.code_quality_score >= 7) {
      insights.push({
        icon: '🟢',
        text: 'Good code quality - minor improvements possible',
        color: 'text-green-400'
      });
    } else if (this.data.code_quality_score >= 5) {
      insights.push({
        icon: '🟡',
        text: 'Moderate code quality - refactoring recommended',
        color: 'text-yellow-400'
      });
    } else {
      insights.push({
        icon: '⚠️',
        text: 'Low code quality - significant improvements needed',
        color: 'text-red-400'
      });
    }

    // Coverage insights
    if (this.data.test_coverage >= 90) {
      insights.push({
        icon: '✅',
        text: 'Excellent test coverage - well-tested codebase',
        color: 'text-green-400'
      });
    } else if (this.data.test_coverage >= 70) {
      insights.push({
        icon: '🟢',
        text: 'Good test coverage - consider expanding tests',
        color: 'text-green-400'
      });
    } else if (this.data.test_coverage >= 50) {
      insights.push({
        icon: '🟡',
        text: 'Moderate test coverage - increase test suite',
        color: 'text-yellow-400'
      });
    } else {
      insights.push({
        icon: '⚠️',
        text: 'Low test coverage - expand test suite significantly',
        color: 'text-red-400'
      });
    }

    // Code smell insights
    if (this.data.code_smells <= 10) {
      insights.push({
        icon: '✅',
        text: `Few code smells (${this.data.code_smells}) - codebase is clean`,
        color: 'text-green-400'
      });
    } else if (this.data.code_smells <= 50) {
      insights.push({
        icon: '🟡',
        text: `Moderate code smells (${this.data.code_smells}) - refactoring advised`,
        color: 'text-yellow-400'
      });
    } else {
      insights.push({
        icon: '⚠️',
        text: `Many code smells (${this.data.code_smells}) - major cleanup needed`,
        color: 'text-red-400'
      });
    }

    // Technical debt insights
    if (this.data.technical_debt_hours <= 100) {
      insights.push({
        icon: '✅',
        text: 'Low technical debt - good maintenance status',
        color: 'text-green-400'
      });
    } else if (this.data.technical_debt_hours <= 500) {
      insights.push({
        icon: '🟡',
        text: 'Moderate technical debt - plan refactoring',
        color: 'text-yellow-400'
      });
    } else {
      insights.push({
        icon: '⚠️',
        text: 'High technical debt - prioritize refactoring',
        color: 'text-red-400'
      });
    }

    return insights;
  }

  /**
   * Helper methods
   */
  getQualityClass(score) {
    if (score >= 8.5) return 'text-green-400';
    if (score >= 7) return 'text-blue-400';
    if (score >= 5) return 'text-yellow-400';
    return 'text-red-400';
  }

  getQualityText(score) {
    if (score >= 8.5) return 'Excellent';
    if (score >= 7) return 'Good';
    if (score >= 5) return 'Fair';
    return 'Poor';
  }

  getQualityEmoji(score) {
    if (score >= 8.5) return '🟢';
    if (score >= 7) return '🔵';
    if (score >= 5) return '🟡';
    return '🔴';
  }

  getMaintainabilityClass(score) {
    if (score >= 85) return 'text-green-400';
    if (score >= 70) return 'text-blue-400';
    if (score >= 50) return 'text-yellow-400';
    return 'text-red-400';
  }

  getMaintainabilityEmoji(score) {
    if (score >= 85) return '✅';
    if (score >= 70) return '🔵';
    if (score >= 50) return '🟡';
    return '⚠️';
  }

  getCoverageClass(coverage) {
    if (coverage >= 90) return 'text-green-400';
    if (coverage >= 70) return 'text-blue-400';
    if (coverage >= 50) return 'text-yellow-400';
    return 'text-red-400';
  }

  getCoverageEmoji(coverage) {
    if (coverage >= 90) return '✅';
    if (coverage >= 70) return '🔵';
    if (coverage >= 50) return '🟡';
    return '⚠️';
  }

  getCoverageAssessment(coverage) {
    if (coverage >= 90) return 'Excellent test coverage';
    if (coverage >= 70) return 'Good test coverage';
    if (coverage >= 50) return 'Moderate test coverage';
    return 'Low test coverage - needs improvement';
  }

  getSmellsStatus(count) {
    if (count <= 5) return 'Very clean - minimal issues';
    if (count <= 20) return 'Acceptable - some refactoring possible';
    if (count <= 50) return 'Needs attention - recommend review';
    return 'Significant issues - refactoring required';
  }

  getSmellsEmoji(count) {
    if (count <= 5) return '✨';
    if (count <= 20) return '🟢';
    if (count <= 50) return '🟡';
    return '🔴';
  }

  getDebtStatus(hours) {
    if (hours <= 50) return 'Minimal - well maintained';
    if (hours <= 200) return 'Moderate - address periodically';
    if (hours <= 500) return 'Significant - plan refactoring';
    return 'Critical - prioritize resolution';
  }

  getDebtEmoji(hours) {
    if (hours <= 50) return '✅';
    if (hours <= 200) return '🟢';
    if (hours <= 500) return '🟡';
    return '🔴';
  }

  getDebtPriority(hours) {
    if (hours <= 50) return '🟢 Low - Monitor in regular maintenance cycles';
    if (hours <= 200) return '🟡 Medium - Address in next sprint planning';
    if (hours <= 500) return '🔴 High - Allocate resources for refactoring';
    return '🔴 Critical - Requires immediate attention';
  }

  formatDays(hours) {
    const days = hours / 8;
    if (days < 1) return `${hours.toFixed(0)}h`;
    if (days < 30) return `${days.toFixed(1)}d`;
    return `${(days / 7).toFixed(1)}w`;
  }

  /**
   * Export quality data
   */
  exportData() {
    return {
      quality: this.data,
      insights: this.generateQualityInsights(),
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
        <h2 class="text-lg font-semibold text-red-300 mb-2">⚠️ Quality Tab Error</h2>
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
  module.exports = QualityTabComponent;
}
