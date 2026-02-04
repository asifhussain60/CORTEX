/**
 * JSONDataLayer.js - Phase 21 JSON-First Data Loading
 * 
 * Replaces SQLiteDataLayer with JSON-first architecture.
 * Features:
 * - HTTP detection (file:// vs http://)
 * - Async/await JSON loading
 * - Error handling (404, schema validation)
 * - Integration with DataBinder component
 * 
 * Authority: PHASE-21-JSON-FIRST-REWRITE.yaml
 * Status: Phase B (GREEN) implementation
 * Author: Asif Hussain
 * Date: 2026-02-04
 */

class JSONDataLayer {
  /**
   * Detect whether we're running in file:// or http:// context
   * @returns {string} 'file' or 'http'
   */
  static detectContext() {
    return window.location.protocol === 'file:' ? 'file' : 'http';
  }

  /**
   * Get the base path for data files
   * file:// context: relative path to cortex/visualization/dashboards/data/
   * http:// context: /api/dashboards/
   * @returns {string} Base path
   */
  static getBasePath() {
    const context = this.detectContext();
    if (context === 'file') {
      // Relative path: from spa/dashboard.html to data/
      return 'data/';
    } else {
      // API endpoint
      return '/api/dashboards/';
    }
  }

  /**
   * Get the data file path for a repository
   * @param {string} repoSlug - Repository slug (e.g., 'cortex')
   * @returns {string} Path to dashboard.json
   */
  static getDataPath(repoSlug) {
    const basePath = this.getBasePath();
    const context = this.detectContext();

    if (context === 'file') {
      // file://: cortex/visualization/dashboards/spa/data/{slug}/dashboard.json
      return `${basePath}${repoSlug}/dashboard.json`;
    } else {
      // http://: /api/dashboards/{slug}
      return `${basePath}${repoSlug}`;
    }
  }

  /**
   * Load dashboard data for a repository
   * @param {string} repoSlug - Repository slug
   * @returns {Promise<Object>} Dashboard data object
   * @throws {Error} On network error, 404, or schema validation failure
   */
  static async load(repoSlug) {
    try {
      const dataPath = this.getDataPath(repoSlug);
      
      // Fetch data
      const response = await fetch(dataPath);
      
      // Handle 404
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Dashboard not found for repository: ${repoSlug}`);
        }
        throw new Error(`Failed to load dashboard: ${response.statusText}`);
      }

      // Parse JSON
      const data = await response.json();

      // Validate schema
      this.validateSchema(data);

      return data;
    } catch (error) {
      console.error(`[JSONDataLayer] Error loading ${repoSlug}:`, error.message);
      throw error;
    }
  }

  /**
   * Validate dashboard data schema
   * Ensures required top-level keys exist
   * @param {Object} data - Dashboard data to validate
   * @throws {Error} If schema is invalid
   */
  static validateSchema(data) {
    const requiredKeys = [
      'repo',
      'overview',
      'metrics',
    ];

    for (const key of requiredKeys) {
      if (!(key in data)) {
        throw new Error(`Missing required field: ${key}`);
      }
      if (typeof data[key] !== 'object') {
        throw new Error(`Invalid type for ${key}: expected object`);
      }
    }
  }

  /**
   * Load registry (list of all repositories)
   * Used by landing page (index.html)
   * @returns {Promise<Object>} Registry with repos array
   */
  static async loadRegistry() {
    try {
      const context = this.detectContext();
      let registryPath;

      if (context === 'file') {
        // file://: registry.json in spa directory
        registryPath = 'registry.json';
      } else {
        // http://: /api/repositories
        registryPath = '/api/repositories';
      }

      const response = await fetch(registryPath);
      if (!response.ok) {
        throw new Error(`Failed to load registry: ${response.statusText}`);
      }

      const data = await response.json();

      // Validate registry structure
      if (!Array.isArray(data.repos)) {
        throw new Error('Invalid registry: repos must be an array');
      }

      return data;
    } catch (error) {
      console.error('[JSONDataLayer] Error loading registry:', error.message);
      throw error;
    }
  }

  /**
   * Get repository slug from URL parameters
   * Used by dashboard.html to determine which repo to load
   * @returns {string|null} Repository slug or null if not specified
   */
  static getRepoSlugFromURL() {
    const params = new URLSearchParams(window.location.search);
    return params.get('repo') || params.get('slug') || 'cortex'; // Default to cortex
  }

  /**
   * Save dashboard data (placeholder for future SQLite adapter)
   * Currently no-op for JSON-first approach
   * @param {string} repoSlug - Repository slug
   * @param {Object} data - Dashboard data
   * @returns {Promise<void>}
   */
  static async save(repoSlug, data) {
    console.warn('[JSONDataLayer] save() is not supported for JSON-first architecture');
    // Future: implement when SQLite adapter is added
  }
}

// Export for use in app.js and other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = JSONDataLayer;
}
