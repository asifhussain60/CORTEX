/**
 * CORTEX 6.0 HTML Views - Shared Data Loader
 * ============================================================================
 * Utility functions for loading and parsing YAML, JSON, and Markdown files
 * Handles caching, error handling, and data transformation
 */

class DataLoader {
  constructor() {
    this.cache = {};
    this.baseUrl = '../../'; // Relative from viewer directory
    this.jsyamlUrl = 'https://cdn.jsdelivr.net/npm/js-yaml@4.1.0/dist/js-yaml.min.js';
  }

  /**
   * Load JS-YAML library if not already loaded
   */
  async loadYamlLibrary() {
    if (typeof jsyaml !== 'undefined') {
      return;
    }

    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = this.jsyamlUrl;
      script.onload = () => resolve();
      script.onerror = () => reject(new Error('Failed to load js-yaml library'));
      document.head.appendChild(script);
    });
  }

  /**
   * Load JSON file
   */
  async loadJSON(path) {
    const cacheKey = `json:${path}`;
    if (this.cache[cacheKey]) {
      return this.cache[cacheKey];
    }

    try {
      const response = await fetch(this.baseUrl + path);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      this.cache[cacheKey] = data;
      return data;
    } catch (error) {
      console.error(`Error loading JSON from ${path}:`, error);
      throw error;
    }
  }

  /**
   * Load YAML file
   */
  async loadYAML(path) {
    const cacheKey = `yaml:${path}`;
    if (this.cache[cacheKey]) {
      return this.cache[cacheKey];
    }

    try {
      await this.loadYamlLibrary();
      const response = await fetch(this.baseUrl + path);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const text = await response.text();
      const data = jsyaml.load(text);
      this.cache[cacheKey] = data;
      return data;
    } catch (error) {
      console.error(`Error loading YAML from ${path}:`, error);
      throw error;
    }
  }

  /**
   * Load Markdown file (returns raw text)
   */
  async loadMarkdown(path) {
    const cacheKey = `md:${path}`;
    if (this.cache[cacheKey]) {
      return this.cache[cacheKey];
    }

    try {
      const response = await fetch(this.baseUrl + path);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const text = await response.text();
      this.cache[cacheKey] = text;
      return text;
    } catch (error) {
      console.error(`Error loading Markdown from ${path}:`, error);
      throw error;
    }
  }

  /**
   * Clear cache
   */
  clearCache() {
    this.cache = {};
  }

  /**
   * Get cache info
   */
  getCacheInfo() {
    return {
      size: Object.keys(this.cache).length,
      keys: Object.keys(this.cache)
    };
  }
}

/**
 * Global data loader instance
 */
window.dataLoader = new DataLoader();

/**
 * Utility function to show loading state
 */
function showLoading(containerId) {
  const container = document.getElementById(containerId);
  if (container) {
    container.innerHTML = '<div class="flex-center p-3"><div class="loading"></div><span class="ml-2">Loading...</span></div>';
  }
}

/**
 * Utility function to show error
 */
function showError(containerId, message) {
  const container = document.getElementById(containerId);
  if (container) {
    container.innerHTML = `<div class="card" style="border-color: #ff006e;">
      <div class="card-header" style="color: #ff006e;">Error Loading Data</div>
      <div class="card-body">
        <p>${message}</p>
        <button class="btn btn-primary btn-small" onclick="location.reload()">Retry</button>
      </div>
    </div>`;
  }
}

/**
 * Format date to readable string
 */
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

/**
 * Format number with commas
 */
function formatNumber(num) {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

/**
 * Get color based on percentage/status
 */
function getStatusColor(value, thresholds = { danger: 33, warning: 66 }) {
  if (value >= thresholds.warning) return '#06ffa5'; // success
  if (value >= thresholds.danger) return '#ffbe0b'; // warning
  return '#ff006e'; // danger
}

/**
 * Create design score badge HTML
 */
function createDesignScoreBadge(score = 97, target = 95) {
  const percentage = (score / 100) * 100;
  return `
    <div class="design-score-badge">
      <div class="score-circle" data-score="${score}">
        <svg viewBox="0 0 100 100" style="width: 100px; height: 100px;">
          <circle class="score-bg" cx="50" cy="50" r="45" fill="none" stroke="#1a1f3a" stroke-width="8"/>
          <circle class="score-fill" cx="50" cy="50" r="45" fill="none" stroke="#00d4ff" stroke-width="8" 
                  stroke-dasharray="282.7" 
                  stroke-dashoffset="${282.7 - (282.7 * percentage / 100)}"/>
        </svg>
        <div class="score-value" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 28px; font-weight: 700; color: #00d4ff;">${score}</div>
      </div>
      <div class="score-breakdown">
        <div class="score-item">
          <span class="label">Target</span>
          <span class="value">${target}</span>
        </div>
        <div class="score-item">
          <span class="label">Status</span>
          <span class="value" style="color: ${score >= target ? '#06ffa5' : '#ffbe0b'};">${score >= target ? 'EXCEEDS ✓' : 'ON TRACK'}</span>
        </div>
      </div>
    </div>
  `;
}

/**
 * Create status badge HTML
 */
function createStatusBadge(status) {
  const statusMap = {
    'implemented': { class: 'badge-success', label: 'Implemented', icon: '✓' },
    'partial': { class: 'badge-warning', label: 'Partial', icon: '◐' },
    'planned': { class: 'badge-info', label: 'Planned', icon: '◯' },
    'blocked': { class: 'badge-danger', label: 'Blocked', icon: '✗' },
    'in_progress': { class: 'badge-warning', label: 'In Progress', icon: '→' },
    'complete': { class: 'badge-success', label: 'Complete', icon: '✓' }
  };
  
  const config = statusMap[status.toLowerCase().replace(/ /g, '_')] || statusMap['planned'];
  return `<span class="badge ${config.class}">${config.icon} ${config.label}</span>`;
}

/**
 * Parse AC-ID and extract category
 */
function parseACID(acId) {
  const match = acId.match(/^(AC-[A-Z]+)-(\d+)$/);
  if (match) {
    return {
      full: acId,
      category: match[1],
      number: parseInt(match[2])
    };
  }
  return null;
}

/**
 * Get color for category
 */
function getCategoryColor(category) {
  const colorMap = {
    'AC-AUDIT': '#06ffa5',
    'AC-GOV': '#7b2cbf',
    'AC-STATE': '#00d4ff',
    'AC-TODO': '#ffbe0b',
    'AC-TDD': '#ff006e',
    'AC-CRAWLER': '#06ffa5',
    'AC-GRAPH': '#00d4ff',
    'AC-STS': '#ffbe0b',
    'AC-LIFECYCLE': '#7b2cbf',
    'AC-EVIDENCE': '#ff006e',
    'AC-SECURITY': '#ff006e',
    'AC-TEST': '#06ffa5',
    'AC-ORCH': '#7b2cbf',
    'AC-KNOW': '#00d4ff'
  };
  return colorMap[category] || '#a0a0a0';
}

/**
 * Create AC-ID badge with color
 */
function createACIDBadge(acId) {
  const parsed = parseACID(acId);
  if (!parsed) return `<span class="badge badge-info">${acId}</span>`;
  
  const color = getCategoryColor(parsed.category);
  return `<span class="badge" style="background: ${color}22; color: ${color}; border: 1px solid ${color};">${acId}</span>`;
}

/**
 * Create progress bar HTML
 */
function createProgressBar(current, total, label = '') {
  const percentage = (current / total) * 100;
  const color = getStatusColor(percentage);
  return `
    <div class="progress-bar-container" style="margin-bottom: 10px;">
      ${label ? `<div style="margin-bottom: 5px; font-size: 0.9rem; color: #a0a0a0;">${label}</div>` : ''}
      <div style="width: 100%; height: 24px; background: rgba(0,0,0,0.5); border-radius: 12px; overflow: hidden; border: 1px solid #1a1f3a;">
        <div style="width: ${percentage}%; height: 100%; background: ${color}; transition: width 0.3s ease;">
          <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #fff; font-size: 0.8rem; font-weight: 700;">
            ${Math.round(percentage)}%
          </div>
        </div>
      </div>
      <div style="margin-top: 5px; font-size: 0.85rem; color: #a0a0a0;">${current}/${total}</div>
    </div>
  `;
}

/**
 * Deep clone object (utility)
 */
function deepClone(obj) {
  return JSON.parse(JSON.stringify(obj));
}

/**
 * Filter array of objects by multiple fields
 */
function filterByFields(array, filters) {
  return array.filter(item => {
    return Object.entries(filters).every(([key, value]) => {
      if (typeof value === 'string') {
        return item[key]?.toString().toLowerCase().includes(value.toLowerCase());
      }
      return item[key] === value;
    });
  });
}

/**
 * Group array by field
 */
function groupBy(array, key) {
  return array.reduce((result, item) => {
    const group = item[key];
    if (!result[group]) result[group] = [];
    result[group].push(item);
    return result;
  }, {});
}

/**
 * Sort array of objects
 */
function sortBy(array, key, direction = 'asc') {
  const sorted = [...array].sort((a, b) => {
    if (a[key] < b[key]) return direction === 'asc' ? -1 : 1;
    if (a[key] > b[key]) return direction === 'asc' ? 1 : -1;
    return 0;
  });
  return sorted;
}

/**
 * Export object to JSON file
 */
function exportJSON(data, filename = 'export.json') {
  const json = JSON.stringify(data, null, 2);
  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
