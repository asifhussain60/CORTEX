/**
 * SQLiteDataLayer.js - sql.js WASM SQLite Integration
 * ====================================================
 * 
 * Purpose: Native SQL operations on dashboard.sqlite via sql.js (WASM)
 * Created: 2026-02-03
 * Authority: PHASE-21-ENTERPRISE-REPOSITORY-INTELLIGENCE.yaml
 * 
 * Features:
 * - Native pagination (LIMIT/OFFSET)
 * - Full-text search (FTS5)
 * - Filtering, sorting, aggregation
 * - Prepared statements for security
 * - Zero external dependencies (pure SQL)
 * 
 * @class SQLiteDataLayer
 */

class SQLiteDataLayer {
    /**
     * Initialize SQLite data layer.
     * 
     * @param {SQL.Database} db - sql.js database instance
     * @param {string} slug - Repository slug
     */
    constructor(db, slug) {
        this.db = db;
        this.slug = slug;
        this._validateSchema();
    }

    /**
     * Validate database schema integrity.
     * 
     * @private
     * @throws {Error} If schema validation fails
     */
    _validateSchema() {
        // Check essential tables exist
        const requiredTables = [
            'repo_summary',
            'use_cases',
            'metrics_summary'
        ];

        for (const table of requiredTables) {
            const stmt = this.db.prepare(
                `SELECT name FROM sqlite_master WHERE type='table' AND name=?`
            );
            stmt.bind([table]);

            if (!stmt.step()) {
                throw new Error(`Missing required table: ${table}`);
            }

            stmt.free();
        }
    }

    // =========================================================================
    // CORE QUERY METHODS
    // =========================================================================

    /**
     * Execute SQL query and return results.
     * 
     * @param {string} sql - SQL query
     * @param {Array} [params=[]] - Query parameters (prepared statement)
     * @returns {Promise<Array<Object>>} Query results
     * 
     * @example
     * const results = await dataLayer.query(
     *     'SELECT * FROM use_cases WHERE priority = ? LIMIT ?',
     *     ['high', 20]
     * );
     */
    async query(sql, params = []) {
        try {
            const stmt = this.db.prepare(sql);

            if (params.length > 0) {
                stmt.bind(params);
            }

            const results = [];
            while (stmt.step()) {
                const row = stmt.getAsObject();
                
                // Parse JSON fields
                for (const [key, value] of Object.entries(row)) {
                    if (typeof value === 'string' && this._isJSONField(key)) {
                        try {
                            row[key] = JSON.parse(value);
                        } catch (e) {
                            // Keep as string if not valid JSON
                        }
                    }
                }
                
                results.push(row);
            }

            stmt.free();
            return results;

        } catch (error) {
            throw new Error(`Query failed: ${error.message}\nSQL: ${sql}`);
        }
    }

    /**
     * Execute query and return single row.
     * 
     * @param {string} sql - SQL query
     * @param {Array} [params=[]] - Query parameters
     * @returns {Promise<Object|null>} Single row or null
     */
    async queryOne(sql, params = []) {
        const results = await this.query(sql, params);
        return results.length > 0 ? results[0] : null;
    }

    /**
     * Execute query and return single value.
     * 
     * @param {string} sql - SQL query
     * @param {Array} [params=[]] - Query parameters
     * @returns {Promise<*>} Single value
     */
    async queryScalar(sql, params = []) {
        const row = await this.queryOne(sql, params);
        if (!row) return null;

        const values = Object.values(row);
        return values.length > 0 ? values[0] : null;
    }

    /**
     * Check if field contains JSON data.
     * 
     * @private
     * @param {string} fieldName - Field name
     * @returns {boolean} True if JSON field
     */
    _isJSONField(fieldName) {
        const jsonFields = [
            'tech_stack', 'user_stories', 'acceptance_criteria', 'related_files',
            'dependencies', 'attributes', 'methods', 'stereotypes', 'evidence'
        ];
        return jsonFields.includes(fieldName);
    }

    // =========================================================================
    // OVERVIEW & SUMMARY DATA
    // =========================================================================

    /**
     * Get repository summary (Overview tab).
     * 
     * @returns {Promise<Object>} Repository summary
     */
    async getRepoSummary() {
        return await this.queryOne('SELECT * FROM repo_summary WHERE id = 1');
    }

    /**
     * Get metrics summary (Metrics tab).
     * 
     * @returns {Promise<Object>} Metrics summary
     */
    async getMetricsSummary() {
        return await this.queryOne('SELECT * FROM metrics_summary WHERE id = 1');
    }

    /**
     * Get executive KPIs (Executive Summary tab).
     * 
     * @returns {Promise<Object>} Executive KPIs computed view
     */
    async getExecutiveKPIs() {
        return await this.queryOne('SELECT * FROM executive_kpis');
    }

    // =========================================================================
    // PAGINATED DATA (Use Cases, Vulnerabilities, Packages, etc.)
    // =========================================================================

    /**
     * Get paginated use cases.
     * 
     * @param {Object} options - Query options
     * @param {number} [options.page=1] - Page number (1-based)
     * @param {number} [options.pageSize=20] - Items per page
     * @param {string} [options.sortBy='priority'] - Sort column
     * @param {string} [options.sortOrder='DESC'] - Sort order (ASC|DESC)
     * @param {Object} [options.filters={}] - Filter conditions
     * @returns {Promise<Object>} { data: Array, total: number, page: number, pageSize: number }
     */
    async getUseCases(options = {}) {
        const {
            page = 1,
            pageSize = 20,
            sortBy = 'priority',
            sortOrder = 'DESC',
            filters = {}
        } = options;

        const offset = (page - 1) * pageSize;

        // Build WHERE clause from filters
        const whereClause = this._buildWhereClause(filters);
        const params = Object.values(filters);

        // Get total count
        const totalSql = `SELECT COUNT(*) as count FROM use_cases ${whereClause}`;
        const total = await this.queryScalar(totalSql, params);

        // Get paginated data
        const dataSql = `
            SELECT * FROM use_cases 
            ${whereClause}
            ORDER BY ${sortBy} ${sortOrder}
            LIMIT ? OFFSET ?
        `;
        const data = await this.query(dataSql, [...params, pageSize, offset]);

        return {
            data,
            total,
            page,
            pageSize,
            totalPages: Math.ceil(total / pageSize)
        };
    }

    /**
     * Get paginated vulnerabilities.
     * 
     * @param {Object} options - Query options
     * @returns {Promise<Object>} Paginated vulnerabilities
     */
    async getVulnerabilities(options = {}) {
        const {
            page = 1,
            pageSize = 20,
            sortBy = 'severity',
            sortOrder = 'DESC',
            filters = {}
        } = options;

        const offset = (page - 1) * pageSize;
        const whereClause = this._buildWhereClause(filters);
        const params = Object.values(filters);

        const total = await this.queryScalar(
            `SELECT COUNT(*) FROM vulnerabilities ${whereClause}`,
            params
        );

        const data = await this.query(
            `SELECT * FROM vulnerabilities ${whereClause} 
             ORDER BY 
                CASE severity 
                    WHEN 'critical' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    ELSE 4
                END,
                ${sortBy} ${sortOrder}
             LIMIT ? OFFSET ?`,
            [...params, pageSize, offset]
        );

        return { data, total, page, pageSize, totalPages: Math.ceil(total / pageSize) };
    }

    /**
     * Get paginated packages.
     * 
     * @param {Object} options - Query options
     * @returns {Promise<Object>} Paginated packages
     */
    async getPackages(options = {}) {
        const {
            page = 1,
            pageSize = 20,
            sortBy = 'package_name',
            sortOrder = 'ASC',
            filters = {}
        } = options;

        const offset = (page - 1) * pageSize;
        const whereClause = this._buildWhereClause(filters);
        const params = Object.values(filters);

        const total = await this.queryScalar(
            `SELECT COUNT(*) FROM packages ${whereClause}`,
            params
        );

        const data = await this.query(
            `SELECT * FROM packages ${whereClause} 
             ORDER BY ${sortBy} ${sortOrder}
             LIMIT ? OFFSET ?`,
            [...params, pageSize, offset]
        );

        return { data, total, page, pageSize, totalPages: Math.ceil(total / pageSize) };
    }

    /**
     * Get paginated code smells.
     * 
     * @param {Object} options - Query options
     * @returns {Promise<Object>} Paginated code smells
     */
    async getCodeSmells(options = {}) {
        return await this._getPaginatedData('code_smells', options);
    }

    /**
     * Get paginated files.
     * 
     * @param {Object} options - Query options
     * @returns {Promise<Object>} Paginated files
     */
    async getFiles(options = {}) {
        return await this._getPaginatedData('files', options);
    }

    /**
     * Generic paginated data retrieval.
     * 
     * @private
     */
    async _getPaginatedData(table, options = {}) {
        const {
            page = 1,
            pageSize = 20,
            sortBy = 'id',
            sortOrder = 'ASC',
            filters = {}
        } = options;

        const offset = (page - 1) * pageSize;
        const whereClause = this._buildWhereClause(filters);
        const params = Object.values(filters);

        const total = await this.queryScalar(
            `SELECT COUNT(*) FROM ${table} ${whereClause}`,
            params
        );

        const data = await this.query(
            `SELECT * FROM ${table} ${whereClause} 
             ORDER BY ${sortBy} ${sortOrder}
             LIMIT ? OFFSET ?`,
            [...params, pageSize, offset]
        );

        return { data, total, page, pageSize, totalPages: Math.ceil(total / pageSize) };
    }

    /**
     * Build WHERE clause from filters object.
     * 
     * @private
     * @param {Object} filters - Filter conditions
     * @returns {string} WHERE clause SQL
     */
    _buildWhereClause(filters) {
        if (Object.keys(filters).length === 0) {
            return '';
        }

        const conditions = Object.keys(filters).map(key => `${key} = ?`);
        return `WHERE ${conditions.join(' AND ')}`;
    }

    // =========================================================================
    // FULL-TEXT SEARCH (FTS5)
    // =========================================================================

    /**
     * Search use cases using full-text search.
     * 
     * @param {string} query - Search query
     * @param {Object} options - Search options
     * @returns {Promise<Array<Object>>} Matching use cases
     * 
     * @example
     * const results = await dataLayer.searchUseCases('authentication', { limit: 10 });
     */
    async searchUseCases(query, options = {}) {
        const { limit = 20, offset = 0 } = options;

        const sql = `
            SELECT u.* FROM use_cases u
            JOIN use_cases_fts fts ON u.id = fts.rowid
            WHERE use_cases_fts MATCH ?
            ORDER BY rank
            LIMIT ? OFFSET ?
        `;

        return await this.query(sql, [query, limit, offset]);
    }

    /**
     * Search packages using full-text search.
     * 
     * @param {string} query - Search query
     * @param {Object} options - Search options
     * @returns {Promise<Array<Object>>} Matching packages
     */
    async searchPackages(query, options = {}) {
        const { limit = 20, offset = 0 } = options;

        const sql = `
            SELECT p.* FROM packages p
            JOIN packages_fts fts ON p.id = fts.rowid
            WHERE packages_fts MATCH ?
            ORDER BY rank
            LIMIT ? OFFSET ?
        `;

        return await this.query(sql, [query, limit, offset]);
    }

    /**
     * Search files using full-text search.
     * 
     * @param {string} query - Search query
     * @param {Object} options - Search options
     * @returns {Promise<Array<Object>>} Matching files
     */
    async searchFiles(query, options = {}) {
        const { limit = 20, offset = 0 } = options;

        const sql = `
            SELECT f.* FROM files f
            JOIN files_fts fts ON f.id = fts.rowid
            WHERE files_fts MATCH ?
            ORDER BY rank
            LIMIT ? OFFSET ?
        `;

        return await this.query(sql, [query, limit, offset]);
    }

    // =========================================================================
    // DOMAIN MODEL & ARCHITECTURE
    // =========================================================================

    /**
     * Get all entities (Domain Model tab).
     * 
     * @returns {Promise<Array<Object>>} Entities
     */
    async getEntities() {
        return await this.query('SELECT * FROM entities ORDER BY name');
    }

    /**
     * Get all relationships (Domain Model tab).
     * 
     * @returns {Promise<Array<Object>>} Relationships
     */
    async getRelationships() {
        return await this.query('SELECT * FROM relationships');
    }

    /**
     * Get all components (Architecture tab).
     * 
     * @returns {Promise<Array<Object>>} Components
     */
    async getComponents() {
        return await this.query('SELECT * FROM components ORDER BY layer, name');
    }

    /**
     * Get components by layer (Architecture tab).
     * 
     * @param {string} layer - Layer name
     * @returns {Promise<Array<Object>>} Components in layer
     */
    async getComponentsByLayer(layer) {
        return await this.query(
            'SELECT * FROM components WHERE layer = ? ORDER BY name',
            [layer]
        );
    }

    // =========================================================================
    // TESTING & LENS
    // =========================================================================

    /**
     * Get test results (Testing tab).
     * 
     * @param {Object} options - Query options
     * @returns {Promise<Object>} Test results with statistics
     */
    async getTestResults(options = {}) {
        const { test_type, status } = options;

        let whereClause = '';
        const params = [];

        if (test_type) {
            whereClause += 'WHERE test_type = ?';
            params.push(test_type);
        }

        if (status) {
            whereClause += whereClause ? ' AND status = ?' : 'WHERE status = ?';
            params.push(status);
        }

        const results = await this.query(
            `SELECT * FROM test_results ${whereClause} ORDER BY run_at DESC`,
            params
        );

        // Calculate statistics
        const stats = await this.queryOne(`
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'pass' THEN 1 ELSE 0 END) as passed,
                SUM(CASE WHEN status = 'fail' THEN 1 ELSE 0 END) as failed,
                SUM(CASE WHEN status = 'skip' THEN 1 ELSE 0 END) as skipped,
                AVG(duration_ms) as avg_duration
            FROM test_results
            ${whereClause}
        `, params);

        return { results, stats };
    }

    /**
     * Get LENS insights (LENS Analysis tab).
     * 
     * @param {Object} options - Filter options
     * @returns {Promise<Array<Object>>} LENS insights
     */
    async getLENSInsights(options = {}) {
        const { insight_type, impact } = options;

        let whereClause = '';
        const params = [];

        if (insight_type) {
            whereClause += 'WHERE insight_type = ?';
            params.push(insight_type);
        }

        if (impact) {
            whereClause += whereClause ? ' AND impact = ?' : 'WHERE impact = ?';
            params.push(impact);
        }

        return await this.query(
            `SELECT * FROM lens_insights ${whereClause} 
             ORDER BY confidence DESC, impact DESC`,
            params
        );
    }

    /**
     * Get refactoring suggestions (Refactoring tab).
     * 
     * @returns {Promise<Array<Object>>} Refactoring suggestions view
     */
    async getRefactoringSuggestions() {
        return await this.query('SELECT * FROM refactoring_suggestions');
    }

    // =========================================================================
    // METRICS & DRILL-DOWN
    // =========================================================================

    /**
     * Get metrics by file for drill-down.
     * 
     * @param {Object} options - Filter options
     * @returns {Promise<Array<Object>>} File metrics
     */
    async getMetricsByFile(options = {}) {
        const { language, minComplexity, maxComplexity } = options;

        let whereClause = '';
        const params = [];

        if (language) {
            whereClause += 'WHERE language = ?';
            params.push(language);
        }

        if (minComplexity !== undefined) {
            whereClause += whereClause ? ' AND complexity >= ?' : 'WHERE complexity >= ?';
            params.push(minComplexity);
        }

        if (maxComplexity !== undefined) {
            whereClause += whereClause ? ' AND complexity <= ?' : 'WHERE complexity <= ?';
            params.push(maxComplexity);
        }

        return await this.query(
            `SELECT * FROM metrics_by_file ${whereClause} 
             ORDER BY complexity DESC, loc DESC`,
            params
        );
    }

    /**
     * Get top complex files.
     * 
     * @param {number} [limit=10] - Number of results
     * @returns {Promise<Array<Object>>} Top complex files
     */
    async getTopComplexFiles(limit = 10) {
        return await this.query(
            'SELECT * FROM metrics_by_file ORDER BY complexity DESC LIMIT ?',
            [limit]
        );
    }

    /**
     * Get high-churn files (frequently modified).
     * 
     * @param {number} [limit=10] - Number of results
     * @returns {Promise<Array<Object>>} High-churn files
     */
    async getHighChurnFiles(limit = 10) {
        return await this.query(
            'SELECT * FROM metrics_by_file ORDER BY churn_count DESC LIMIT ?',
            [limit]
        );
    }

    // =========================================================================
    // UTILITY METHODS
    // =========================================================================

    /**
     * Get database statistics.
     * 
     * @returns {Promise<Object>} Database stats
     */
    async getStats() {
        const tables = [
            'use_cases', 'vulnerabilities', 'packages', 'code_smells',
            'entities', 'relationships', 'components', 'files',
            'test_results', 'lens_insights'
        ];

        const stats = {};

        for (const table of tables) {
            const count = await this.queryScalar(`SELECT COUNT(*) FROM ${table}`);
            stats[table] = count;
        }

        return stats;
    }

    /**
     * Close database connection.
     */
    close() {
        if (this.db) {
            this.db.close();
            this.db = null;
        }
    }
}

/**
 * Export for global and module systems.
 */
if (typeof window !== 'undefined') {
    window.SQLiteDataLayer = SQLiteDataLayer;
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = SQLiteDataLayer;
}
