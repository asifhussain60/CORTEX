/**
 * DualFormatDataLoader.js - Backward Compatible Data Loader
 * ==========================================================
 * 
 * Purpose: Load dashboard data from SQLite OR JSON (migration adapter)
 * Created: 2026-02-03
 * Authority: PHASE-21-ENTERPRISE-REPOSITORY-INTELLIGENCE.yaml
 * 
 * Architecture:
 * - Detects available data format (SQLite preferred, JSON fallback)
 * - Provides unified API regardless of backend format
 * - Enables gradual migration from JSON to SQLite
 * - Zero breaking changes to existing dashboards
 * 
 * Migration Timeline:
 * - Phase 1: Both formats work (this component)
 * - Phase 2: Migrate existing repos to SQLite
 * - Phase 3: Deprecate JSON support (log warnings)
 * - Phase 4: Remove JSON support entirely
 * 
 * @class DualFormatDataLoader
 */

class DualFormatDataLoader {
    /**
     * Initialize dual-format data loader.
     * 
     * @param {Object} options - Configuration options
     * @param {string} options.basePath - Base path to repos directory (default: '/repos')
     * @param {boolean} options.preferSQLite - Prefer SQLite over JSON (default: true)
     * @param {boolean} options.logFormat - Log which format is used (default: false)
     */
    constructor(options = {}) {
        this.basePath = options.basePath || '/repos';
        this.preferSQLite = options.preferSQLite !== false;
        this.logFormat = options.logFormat || false;
        this.cache = new Map(); // Cache loaded data layers
    }

    /**
     * Load repository data with automatic format detection.
     * 
     * @param {string} slug - Repository slug
     * @returns {Promise<DataLayer>} Data layer instance (SQLite or JSON adapter)
     * 
     * @example
     * const loader = new DualFormatDataLoader();
     * const dataLayer = await loader.load('cortex');
     * const useCases = await dataLayer.query('SELECT * FROM use_cases LIMIT 20');
     */
    async load(slug) {
        // Check cache first
        if (this.cache.has(slug)) {
            return this.cache.get(slug);
        }

        const format = await this._detectFormat(slug);

        if (this.logFormat) {
            console.log(`[DualFormatDataLoader] Loading ${slug} using ${format} format`);
        }

        let dataLayer;
        if (format === 'sqlite') {
            dataLayer = await this._loadSQLite(slug);
        } else if (format === 'json') {
            dataLayer = await this._loadJSON(slug);
        } else {
            throw new Error(`No data found for repository: ${slug}`);
        }

        // Cache for reuse
        this.cache.set(slug, dataLayer);

        return dataLayer;
    }

    /**
     * Detect available data format for repository.
     * 
     * @private
     * @param {string} slug - Repository slug
     * @returns {Promise<string>} Format type: 'sqlite' | 'json' | 'none'
     */
    async _detectFormat(slug) {
        if (this.preferSQLite) {
            // Try SQLite first
            const sqliteExists = await this._fileExists(`${this.basePath}/${slug}/dashboard.sqlite`);
            if (sqliteExists) {
                return 'sqlite';
            }

            // Fallback to JSON
            const jsonExists = await this._fileExists(`${this.basePath}/${slug}/dashboard-data.json`);
            if (jsonExists) {
                return 'json';
            }
        } else {
            // Try JSON first (reverse order)
            const jsonExists = await this._fileExists(`${this.basePath}/${slug}/dashboard-data.json`);
            if (jsonExists) {
                return 'json';
            }

            const sqliteExists = await this._fileExists(`${this.basePath}/${slug}/dashboard.sqlite`);
            if (sqliteExists) {
                return 'sqlite';
            }
        }

        return 'none';
    }

    /**
     * Check if file exists via HEAD request.
     * 
     * @private
     * @param {string} url - File URL
     * @returns {Promise<boolean>} True if file exists
     */
    async _fileExists(url) {
        try {
            const response = await fetch(url, { method: 'HEAD' });
            return response.ok;
        } catch (error) {
            return false;
        }
    }

    /**
     * Load data from SQLite file.
     * 
     * @private
     * @param {string} slug - Repository slug
     * @returns {Promise<SQLiteDataLayer>} SQLite data layer instance
     */
    async _loadSQLite(slug) {
        const url = `${this.basePath}/${slug}/dashboard.sqlite`;

        // Load sql.js library if not already loaded
        if (typeof initSqlJs === 'undefined') {
            throw new Error('sql.js library not loaded. Include sql-wasm.js before using SQLite data.');
        }

        // Initialize sql.js
        const SQL = await initSqlJs({
            locateFile: file => `/spa/vendor/${file}`
        });

        // Fetch SQLite database file
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Failed to load SQLite database: ${response.statusText}`);
        }

        const buffer = await response.arrayBuffer();
        const db = new SQL.Database(new Uint8Array(buffer));

        // Import SQLiteDataLayer (must be loaded separately)
        if (typeof SQLiteDataLayer === 'undefined') {
            throw new Error('SQLiteDataLayer not loaded. Include SQLiteDataLayer.js.');
        }

        return new SQLiteDataLayer(db, slug);
    }

    /**
     * Load data from JSON file.
     * 
     * @private
     * @param {string} slug - Repository slug
     * @returns {Promise<JSONDataAdapter>} JSON data adapter instance
     */
    async _loadJSON(slug) {
        const url = `${this.basePath}/${slug}/dashboard-data.json`;

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Failed to load JSON data: ${response.statusText}`);
        }

        const data = await response.json();

        // Import JSONDataAdapter (must be loaded separately)
        if (typeof JSONDataAdapter === 'undefined') {
            throw new Error('JSONDataAdapter not loaded. Include JSONDataAdapter.js.');
        }

        return new JSONDataAdapter(data, slug);
    }

    /**
     * Preload multiple repositories.
     * 
     * @param {string[]} slugs - Array of repository slugs
     * @returns {Promise<Map<string, DataLayer>>} Map of slug to data layer
     * 
     * @example
     * const loader = new DualFormatDataLoader();
     * const dataLayers = await loader.preloadMultiple(['cortex', 'cortex-brain']);
     */
    async preloadMultiple(slugs) {
        const promises = slugs.map(slug => this.load(slug).catch(err => {
            console.warn(`Failed to load ${slug}:`, err);
            return null;
        }));

        await Promise.all(promises);

        return this.cache;
    }

    /**
     * Clear cached data layers.
     * 
     * @param {string} [slug] - Optional specific slug to clear (clears all if omitted)
     */
    clearCache(slug) {
        if (slug) {
            this.cache.delete(slug);
        } else {
            this.cache.clear();
        }
    }

    /**
     * Get format information for repository.
     * 
     * @param {string} slug - Repository slug
     * @returns {Promise<Object>} Format metadata
     * 
     * @example
     * const info = await loader.getFormatInfo('cortex');
     * // { format: 'sqlite', size: 2048576, available: true }
     */
    async getFormatInfo(slug) {
        const format = await this._detectFormat(slug);

        if (format === 'none') {
            return { format: 'none', available: false };
        }

        const url = format === 'sqlite'
            ? `${this.basePath}/${slug}/dashboard.sqlite`
            : `${this.basePath}/${slug}/dashboard-data.json`;

        try {
            const response = await fetch(url, { method: 'HEAD' });
            const size = parseInt(response.headers.get('content-length') || '0', 10);

            return {
                format,
                size,
                sizeFormatted: this._formatBytes(size),
                available: true,
                url
            };
        } catch (error) {
            return {
                format,
                available: false,
                error: error.message
            };
        }
    }

    /**
     * Format bytes to human-readable string.
     * 
     * @private
     * @param {number} bytes - Bytes
     * @returns {string} Formatted string (e.g., "2.5 MB")
     */
    _formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';

        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));

        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * Test connection to repository data.
     * 
     * @param {string} slug - Repository slug
     * @returns {Promise<Object>} Test results
     * 
     * @example
     * const test = await loader.testConnection('cortex');
     * if (test.success) {
     *     console.log('Connected successfully');
     * }
     */
    async testConnection(slug) {
        try {
            const dataLayer = await this.load(slug);

            // Test query
            const result = await dataLayer.query('SELECT * FROM repo_summary WHERE id = 1');

            return {
                success: true,
                format: await this._detectFormat(slug),
                repoName: result[0]?.repo_name || 'Unknown',
                healthScore: result[0]?.health_score || 0,
                message: 'Connection successful'
            };
        } catch (error) {
            return {
                success: false,
                format: await this._detectFormat(slug),
                message: error.message,
                error
            };
        }
    }
}

/**
 * Create global instance for convenience.
 * 
 * @example
 * // In dashboard.html
 * const dataLayer = await window.dataLoader.load('cortex');
 */
if (typeof window !== 'undefined') {
    window.DualFormatDataLoader = DualFormatDataLoader;

    // Create default instance
    window.dataLoader = new DualFormatDataLoader({
        logFormat: true // Enable logging during migration phase
    });
}

// Export for module systems AND browser globals
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DualFormatDataLoader;
}
// Browser global export
if (typeof window !== 'undefined') {
    window.DualFormatDataLoader = DualFormatDataLoader;
}
