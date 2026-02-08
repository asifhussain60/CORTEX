/**
 * CORTEX Repository Dashboard - Overview Tab (📊)
 * Executive health dashboard with metrics, scoring, and audience personas
 * Phase S2.2 Implementation
 */

// ============================================================================
// OVERVIEW TAB COMPONENT CLASS
// ============================================================================

class OverviewTabComponent {
  constructor(containerSelector = '#overview-tab') {
    this.container = document.querySelector(containerSelector);
    this.data = null;
    this.initialized = false;
  }

  /**
   * Initialize component with dashboard data
   * @param {Object} dashboardData - Complete dashboard schema data
   */
  async init(dashboardData) {
    try {
      this.data = dashboardData.overview;
      this.metadata = dashboardData.metadata;
      
      // Render all overview sections
      this.render();
      this.initialized = true;
      
      console.log('✅ Overview Tab initialized', { 
        healthScore: this.data.health_score,
        codeQuality: this.data.code_quality
      });
    } catch (error) {
      console.error('❌ Overview Tab initialization failed:', error);
      this.renderError(error);
    }
  }

  /**
   * Main render method - orchestrates all sections
   */
  render() {
    if (!this.container) {
      console.error('Container not found');
      return;
    }

    this.container.innerHTML = '';
    this.container.classList.add('overview-tab', 'tab-panel');

    // Build all sections
    this.container.appendChild(this.renderHeader());
    this.container.appendChild(this.renderHealthMetrics());
    this.container.appendChild(this.renderDetailedMetrics());
    this.container.appendChild(this.renderLanguageDistribution());
    this.container.appendChild(this.renderAudiencePersonas());
    this.container.appendChild(this.renderSummary());
  }

  /**
   * Render header section with repository info
   */
  renderHeader() {
    const header = document.createElement('div');
    header.className = 'overview-header glass-card';
    
    header.innerHTML = `
      <div class="flex flex-col gap-4">
        <div class="flex items-center gap-3">
          <h2 class="text-3xl font-bold text-white">${this.metadata.name}</h2>
          <span class="badge primary">${this.metadata.primary_language}</span>
        </div>
        <p class="text-muted text-sm">${this.metadata.description || this.metadata.path}</p>
        <div class="flex gap-4 text-sm text-gray">
          <span>📁 ${this.formatNumber(this.metadata.total_files)} files</span>
          <span>📝 ${this.formatNumber(this.metadata.total_lines)} lines</span>
          <span>👥 ${this.metadata.contributors} contributors</span>
          <span>📅 ${this.formatDays(this.metadata.repo_age_days)} old</span>
        </div>
      </div>
    `;
    
    return header;
  }

  /**
   * Render primary health score metrics
   */
  renderHealthMetrics() {
    const section = document.createElement('div');
    section.className = 'grid cols-md-2 cols-lg-4 gap-4 p-4';
    section.innerHTML = `
      ${this.renderMetricCard(
        '📊',
        'Health Score',
        this.data.health_score,
        '%',
        this.getHealthStatus(this.data.health_score)
      )}
      ${this.renderMetricCard(
        '⭐',
        'Code Quality',
        this.data.code_quality,
        '/10',
        this.getQualityStatus(this.data.code_quality)
      )}
      ${this.renderMetricCard(
        '✅',
        'Test Coverage',
        this.data.test_coverage,
        '%',
        this.getCoverageStatus(this.data.test_coverage)
      )}
      ${this.renderMetricCard(
        '🔧',
        'Maintainability',
        this.data.maintainability_index,
        '/100',
        this.getMaintainabilityStatus(this.data.maintainability_index)
      )}
    `;
    
    return section;
  }

  /**
   * Render detailed metrics section
   */
  renderDetailedMetrics() {
    const section = document.createElement('div');
    section.className = 'glass-card p-6 m-4';
    section.innerHTML = `
      <h3 class="text-xl font-semibold text-white mb-4">Detailed Metrics</h3>
      
      <div class="space-y-4">
        ${this.renderProgressBar(
          'Health Score',
          this.data.health_score,
          'primary',
          this.getHealthClass(this.data.health_score)
        )}
        ${this.renderProgressBar(
          'Test Coverage',
          this.data.test_coverage,
          'success',
          this.getCoverageClass(this.data.test_coverage)
        )}
        ${this.renderProgressBar(
          'Maintainability',
          this.data.maintainability_index,
          'secondary',
          this.getMaintainabilityClass(this.data.maintainability_index)
        )}
        ${this.renderProgressBar(
          'Code Quality',
          (this.data.code_quality / 10) * 100,
          'primary',
          this.getQualityClass(this.data.code_quality)
        )}
      </div>
      
      <div class="grid cols-md-2 gap-4 mt-6 pt-6 border-top">
        <div>
          <p class="text-muted text-sm mb-1">⏰ Technical Debt</p>
          <p class="text-2xl font-bold text-white">${this.data.technical_debt_hours}h</p>
          <p class="text-xs text-gray mt-1">estimated effort</p>
        </div>
        <div>
          <p class="text-muted text-sm mb-1">📊 Status</p>
          <p class="text-2xl font-bold ${this.getHealthColorClass(this.data.health_score)}">
            ${this.getHealthText(this.data.health_score)}
          </p>
        </div>
      </div>
    `;
    
    return section;
  }

  /**
   * Render language distribution
   */
  renderLanguageDistribution() {
    const section = document.createElement('div');
    section.className = 'glass-card p-6 m-4';
    
    const languages = this.data.languages || {};
    const totalLines = Object.values(languages).reduce((a, b) => a + b, 0);
    
    let languageHtml = '<div class="space-y-3">';
    
    for (const [lang, lines] of Object.entries(languages)) {
      const percentage = totalLines > 0 ? (lines / totalLines) * 100 : 0;
      languageHtml += `
        <div>
          <div class="flex justify-between items-center mb-2">
            <span class="text-sm font-medium text-white">${lang}</span>
            <span class="text-xs text-gray">${this.formatNumber(lines)} lines (${percentage.toFixed(1)}%)</span>
          </div>
          <div class="h-2 bg-gray-800 rounded-full overflow-hidden">
            <div class="h-full bg-gradient-to-r from-accent to-secondary" 
                 style="width: ${percentage}%; transition: width 0.3s ease-out;"></div>
          </div>
        </div>
      `;
    }
    languageHtml += '</div>';
    
    section.innerHTML = `
      <h3 class="text-xl font-semibold text-white mb-4">Language Distribution</h3>
      ${languageHtml}
      <p class="text-xs text-muted mt-4">Total: ${this.formatNumber(totalLines)} lines</p>
    `;
    
    return section;
  }

  /**
   * Render audience personas
   */
  renderAudiencePersonas() {
    if (!this.data.audiences || this.data.audiences.length === 0) {
      return document.createElement('div'); // Empty element
    }

    const section = document.createElement('div');
    section.className = 'glass-card p-6 m-4';
    section.innerHTML = '<h3 class="text-xl font-semibold text-white mb-4">Dashboard Audiences</h3>';
    
    const audienceGrid = document.createElement('div');
    audienceGrid.className = 'grid cols-md-2 cols-lg-3 gap-4';
    
    for (const audience of this.data.audiences) {
      const card = document.createElement('div');
      card.className = 'glass-card-clickable p-4 cursor-pointer group';
      card.innerHTML = `
        <div class="flex items-start gap-3">
          <span class="text-3xl">${audience.icon}</span>
          <div class="flex-1">
            <h4 class="font-semibold text-white group-hover:text-accent transition-colors">
              ${audience.persona}
            </h4>
            <p class="text-sm text-gray mt-1">${audience.description}</p>
          </div>
        </div>
      `;
      audienceGrid.appendChild(card);
    }
    
    section.appendChild(audienceGrid);
    return section;
  }

  /**
   * Render summary insights section
   */
  renderSummary() {
    const section = document.createElement('div');
    section.className = 'glass-card p-6 m-4';
    
    const insights = this.generateInsights();
    
    section.innerHTML = `
      <h3 class="text-xl font-semibold text-white mb-4">📋 Summary & Insights</h3>
      <ul class="space-y-2">
        ${insights.map(insight => `
          <li class="flex gap-2 items-start">
            <span class="text-accent mt-0.5">→</span>
            <span class="text-sm text-gray">${insight}</span>
          </li>
        `).join('')}
      </ul>
    `;
    
    return section;
  }

  /**
   * Render individual metric card
   */
  renderMetricCard(icon, label, value, unit, statusClass) {
    const card = document.createElement('div');
    card.className = `metric-card ${statusClass || ''}`;
    
    const displayValue = typeof value === 'number' ? value.toFixed(1) : value;
    
    card.innerHTML = `
      <div class="flex items-start justify-between">
        <div>
          <p class="metric-card__label">${label}</p>
          <p class="metric-card__value">${displayValue}<span class="metric-card__unit">${unit}</span></p>
        </div>
        <span class="text-3xl opacity-50">${icon}</span>
      </div>
    `;
    
    return card.outerHTML;
  }

  /**
   * Render progress bar with label and percentage
   */
  renderProgressBar(label, value, variant = 'primary', cssClass = '') {
    const percentage = Math.min(100, Math.max(0, value));
    
    return `
      <div class="progress-bar ${cssClass}">
        <span class="progress-bar__label">${label}</span>
        <div class="progress-bar__track">
          <div class="progress-bar__fill" style="width: ${percentage}%"></div>
        </div>
        <span class="progress-bar__value">${percentage.toFixed(1)}%</span>
      </div>
    `;
  }

  /**
   * Error rendering
   */
  renderError(error) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'glass-card p-6 m-4 bg-red-900 border-red-500';
    errorDiv.innerHTML = `
      <h3 class="text-lg font-semibold text-error mb-2">❌ Error Loading Overview</h3>
      <p class="text-sm text-gray">${error.message}</p>
    `;
    this.container.appendChild(errorDiv);
  }

  // ========================================================================
  // UTILITY METHODS
  // ========================================================================

  formatNumber(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  }

  formatDays(days) {
    if (days >= 365) return `${(days / 365).toFixed(1)}y`;
    if (days >= 30) return `${Math.floor(days / 30)}mo`;
    return `${days}d`;
  }

  getHealthStatus(score) {
    if (score >= 85) return 'border-success glow-success';
    if (score >= 70) return 'border-warning';
    return 'border-error glow-error';
  }

  getHealthClass(score) {
    if (score >= 85) return 'success';
    if (score >= 70) return 'warning';
    return 'error';
  }

  getHealthColorClass(score) {
    if (score >= 85) return 'text-success-light';
    if (score >= 70) return 'text-warning-light';
    return 'text-error-light';
  }

  getHealthText(score) {
    if (score >= 90) return 'Excellent';
    if (score >= 75) return 'Good';
    if (score >= 60) return 'Fair';
    return 'Poor';
  }

  getQualityStatus(quality) {
    if (quality >= 8) return 'border-success';
    if (quality >= 6) return 'border-warning';
    return 'border-error';
  }

  getQualityClass(quality) {
    if (quality >= 8) return 'success';
    if (quality >= 6) return 'warning';
    return 'error';
  }

  getCoverageStatus(coverage) {
    if (coverage >= 80) return 'border-success glow-success';
    if (coverage >= 60) return 'border-warning';
    return 'border-error glow-error';
  }

  getCoverageClass(coverage) {
    if (coverage >= 80) return 'success';
    if (coverage >= 60) return 'warning';
    return 'error';
  }

  getMaintainabilityStatus(index) {
    if (index >= 80) return 'border-success';
    if (index >= 60) return 'border-warning';
    return 'border-error';
  }

  getMaintainabilityClass(index) {
    if (index >= 80) return 'success';
    if (index >= 60) return 'warning';
    return 'error';
  }

  /**
   * Generate executive insights from data
   */
  generateInsights() {
    const insights = [];

    // Health score insights
    if (this.data.health_score >= 85) {
      insights.push(`🟢 Repository health is excellent (${this.data.health_score}%). Maintain current quality standards.`);
    } else if (this.data.health_score >= 70) {
      insights.push(`🟡 Repository health is good (${this.data.health_score}%). Focus on improving test coverage and reducing technical debt.`);
    } else {
      insights.push(`🔴 Repository health needs attention (${this.data.health_score}%). Prioritize quality improvements.`);
    }

    // Coverage insights
    if (this.data.test_coverage >= 80) {
      insights.push(`✅ Test coverage is strong at ${this.data.test_coverage}%. Continue maintaining high coverage standards.`);
    } else if (this.data.test_coverage >= 60) {
      insights.push(`⚠️ Test coverage at ${this.data.test_coverage}%. Target: 80%+. Add tests for critical paths.`);
    } else {
      insights.push(`❌ Test coverage is low at ${this.data.test_coverage}%. Urgent: Add comprehensive tests.`);
    }

    // Technical debt insights
    if (this.data.technical_debt_hours < 100) {
      insights.push(`💪 Technical debt is minimal (${this.data.technical_debt_hours}h). Focus on feature development.`);
    } else if (this.data.technical_debt_hours < 300) {
      insights.push(`📊 Technical debt estimated at ${this.data.technical_debt_hours}h. Schedule refactoring tasks.`);
    } else {
      insights.push(`⚠️ Technical debt is high (${this.data.technical_debt_hours}h). Allocate sprint capacity for technical improvements.`);
    }

    // Code quality insights
    if (this.data.code_quality >= 8) {
      insights.push(`🎯 Code quality score is excellent (${this.data.code_quality}/10). Continue best practices.`);
    } else if (this.data.code_quality >= 6) {
      insights.push(`👍 Code quality is acceptable (${this.data.code_quality}/10). Target: 8+. Focus on code reviews.`);
    } else {
      insights.push(`⚠️ Code quality needs improvement (${this.data.code_quality}/10). Implement refactoring plan.`);
    }

    // Language diversity
    const langCount = Object.keys(this.data.languages || {}).length;
    if (langCount === 1) {
      insights.push(`📝 Single language project (${Object.keys(this.data.languages)[0]}). Focused and maintainable.`);
    } else {
      insights.push(`🌍 Multi-language codebase (${langCount} languages). Ensure consistent quality standards.`);
    }

    return insights;
  }

  /**
   * Update specific metric (for live updates)
   */
  updateMetric(metricName, newValue) {
    if (this.data.hasOwnProperty(metricName)) {
      this.data[metricName] = newValue;
      this.render(); // Re-render on data change
    }
  }

  /**
   * Export overview data as JSON
   */
  exportData() {
    return {
      timestamp: new Date().toISOString(),
      metadata: this.metadata,
      overview: this.data,
      insights: this.generateInsights()
    };
  }
}

// ============================================================================
// EXPORT FOR MODULE SYSTEMS
// ============================================================================

if (typeof module !== 'undefined' && module.exports) {
  module.exports = OverviewTabComponent;
}
