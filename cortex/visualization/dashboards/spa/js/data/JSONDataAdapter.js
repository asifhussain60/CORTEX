/**
 * JSONDataAdapter.js
 * ===================
 * 
 * Purpose: Wrap JSON data with SQL-like query interface for backward compatibility
 * Created: 2026-02-03
 * Authority: PHASE-21-ENTERPRISE-REPOSITORY-INTELLIGENCE.yaml lines 750-760
 * 
 * Features:
 * - Parses limited SQL subset (SELECT, WHERE, LIMIT, OFFSET, ORDER BY, COUNT, LIKE, IN)
 * - Executes against JSON data using array methods
 * - Returns results matching SQLite format
 * - Fallback for repositories without dashboard.sqlite
 * - Fuzzy search via Fuse.js (optional)
 * - API-compatible with SQLiteDataLayer
 * 
 * Usage:
 *   const adapter = new JSONDataAdapter(jsonData);
 *   const results = adapter.query('SELECT * FROM use_cases LIMIT 20 OFFSET 40');
 */

class JSONDataAdapter {
    /**
     * Create JSON data adapter.
     * 
     * @param {Object} data - JSON data object with table-like structures
     * @param {string} [slug] - Repository slug (optional)
     */
    constructor(data, slug = null) {
        this.data = data || {};
        this.slug = slug;
        this._fuseInstances = new Map(); // Cache Fuse.js instances per table
    }

    /**
     * Execute SQL-like query against JSON data.
     * 
     * Supported syntax:
     * - SELECT * FROM table
     * - SELECT column1, column2 FROM table
     * - SELECT COUNT(*) FROM table
     * - SELECT SUM(column), AVG(column), MAX(column), MIN(column) FROM table
     * - WHERE column = 'value' (equality)
     * - WHERE column > value (comparison operators: >, <, >=, <=, !=)
     * - WHERE column LIKE '%pattern%' (pattern matching)
     * - WHERE column IN ('val1', 'val2') (set membership)
     * - WHERE cond1 AND cond2 (multiple conditions)
     * - ORDER BY column ASC|DESC
     * - LIMIT n
     * - OFFSET n
     * 
     * @param {string} sql - SQL query string
     * @param {Array} [params=[]] - Query parameters (for prepared statement compatibility)
     * @returns {Array<Object>} Query results
     */
    query(sql, params = []) {
        try {
            const parsed = this._parseSQL(sql);
            
            // Substitute parameters into query
            if (params.length > 0) {
                parsed.where = this._substituteParams(parsed.where, params);
            }
            
            let results = this._getTableData(parsed.table);

            // Apply WHERE filter
            if (parsed.where) {
                results = this._applyWhere(results, parsed.where);
            }

            // Handle aggregates (COUNT, SUM, AVG, etc.)
            if (parsed.aggregate) {
                return [this._applyAggregate(results, parsed.aggregate)];
            }

            // Apply ORDER BY
            if (parsed.orderBy) {
                results = this._applyOrderBy(results, parsed.orderBy);
            }

            // Apply OFFSET
            if (parsed.offset > 0) {
                results = results.slice(parsed.offset);
            }

            // Apply LIMIT
            if (parsed.limit > 0) {
                results = results.slice(0, parsed.limit);
            }

            // Apply column selection
            if (parsed.columns.length > 0 && parsed.columns[0] !== '*') {
                results = this._selectColumns(results, parsed.columns);
            }

            return results;

        } catch (error) {
            console.error('JSONDataAdapter query error:', error);
            return [];
        }
    }

    /**
     * Execute query and return single row.
     * 
     * @param {string} sql - SQL query
     * @param {Array} [params=[]] - Query parameters
     * @returns {Object|null} Single row or null
     */
    queryOne(sql, params = []) {
        const results = this.query(sql, params);
        return results.length > 0 ? results[0] : null;
    }

    /**
     * Execute query and return single value.
     * 
     * @param {string} sql - SQL query
     * @param {Array} [params=[]] - Query parameters
     * @returns {*} Single value
     */
    queryScalar(sql, params = []) {
        const row = this.queryOne(sql, params);
        if (!row) return null;

        const values = Object.values(row);
        return values.length > 0 ? values[0] : null;
    }

    /**
     * Search table with fuzzy matching (fallback for FTS5).
     * Uses Fuse.js if available, otherwise basic string includes.
     * 
     * @param {string} table - Table name
     * @param {string} query - Search query
     * @param {Object} [options] - Search options
     * @param {number} [options.limit=20] - Max results
     * @param {number} [options.offset=0] - Skip N results
     * @param {number} [options.threshold=0.3] - Fuse.js threshold (0 = exact, 1 = match anything)
     * @returns {Array<Object>} Matching rows
     */
    search(table, query, options = {}) {
        const { limit = 20, offset = 0, threshold = 0.3 } = options;
        const data = this._getTableData(table);
        
        if (!data || data.length === 0) {
            return [];
        }

        const lowerQuery = query.toLowerCase();
        
        // Try Fuse.js if available
        if (typeof Fuse !== 'undefined') {
            return this._fuseSearch(table, data, query, { limit, offset, threshold });
        }
        
        // Fallback: basic string matching
        let results = data.filter(row => {
            // Search all string fields
            return Object.values(row).some(value => {
                if (typeof value === 'string') {
                    return value.toLowerCase().includes(lowerQuery);
                }
                return false;
            });
        });
        
        // Apply pagination
        if (offset > 0) {
            results = results.slice(offset);
        }
        if (limit > 0) {
            results = results.slice(0, limit);
        }
        
        return results;
    }
    
    /**
     * Search using Fuse.js for fuzzy matching.
     * 
     * @private
     * @param {string} table - Table name
     * @param {Array<Object>} data - Table data
     * @param {string} query - Search query
     * @param {Object} options - Search options
     * @returns {Array<Object>} Matching rows
     */
    _fuseSearch(table, data, query, options) {
        // Get or create Fuse instance for this table
        if (!this._fuseInstances.has(table)) {
            // Auto-detect searchable keys (string fields)
            const sampleRow = data[0] || {};
            const keys = Object.keys(sampleRow).filter(key => {
                const value = sampleRow[key];
                return typeof value === 'string' || typeof value === 'number';
            });
            
            this._fuseInstances.set(table, new Fuse(data, {
                keys,
                threshold: options.threshold,
                includeScore: true,
                ignoreLocation: true
            }));
        }
        
        const fuse = this._fuseInstances.get(table);
        const results = fuse.search(query);
        
        // Apply pagination and extract items
        let items = results.slice(options.offset, options.offset + options.limit);
        return items.map(r => r.item);
    }

    /**
     * Parse SQL query string.
     * 
     * @param {string} sql - SQL query
     * @returns {Object} Parsed query components
     * @private
     */
    _parseSQL(sql) {
        const result = {
            columns: [],
            table: '',
            where: null,
            limit: 0,
            offset: 0,
            orderBy: null,
            aggregate: null
        };

        // Remove extra whitespace
        sql = sql.trim().replace(/\s+/g, ' ');

        // Check for aggregate functions
        const countMatch = sql.match(/SELECT\s+COUNT\s*\(\s*\*\s*\)\s*(as\s+\w+)?\s+FROM/i);
        if (countMatch) {
            result.aggregate = { type: 'COUNT', column: '*', alias: 'count' };
        }
        
        const aggMatch = sql.match(/SELECT\s+(SUM|AVG|MAX|MIN)\s*\(\s*(\w+)\s*\)\s*(as\s+(\w+))?\s+FROM/i);
        if (aggMatch) {
            result.aggregate = { 
                type: aggMatch[1].toUpperCase(), 
                column: aggMatch[2],
                alias: aggMatch[4] || aggMatch[1].toLowerCase()
            };
        }

        // Extract SELECT columns (if not aggregate)
        if (!result.aggregate) {
            const selectMatch = sql.match(/SELECT\s+(.+?)\s+FROM/i);
            if (selectMatch) {
                const columnsStr = selectMatch[1].trim();
                if (columnsStr === '*') {
                    result.columns = ['*'];
                } else {
                    result.columns = columnsStr.split(',').map(c => c.trim());
                }
            }
        }

        // Extract FROM table
        const fromMatch = sql.match(/FROM\s+(\w+)/i);
        if (fromMatch) {
            result.table = fromMatch[1];
        }

        // Extract WHERE clause (supports multiple conditions with AND)
        const whereMatch = sql.match(/WHERE\s+(.+?)(?:\s+ORDER|\s+LIMIT|\s+OFFSET|$)/i);
        if (whereMatch) {
            result.where = this._parseWhereClause(whereMatch[1].trim());
        }

        // Extract ORDER BY
        const orderByMatch = sql.match(/ORDER\s+BY\s+(\w+)(?:\s+(ASC|DESC))?/i);
        if (orderByMatch) {
            result.orderBy = {
                column: orderByMatch[1],
                direction: (orderByMatch[2] || 'ASC').toUpperCase()
            };
        }

        // Extract LIMIT
        const limitMatch = sql.match(/LIMIT\s+(\d+)/i);
        if (limitMatch) {
            result.limit = parseInt(limitMatch[1], 10);
        }

        // Extract OFFSET
        const offsetMatch = sql.match(/OFFSET\s+(\d+)/i);
        if (offsetMatch) {
            result.offset = parseInt(offsetMatch[1], 10);
        }

        return result;
    }
    
    /**
     * Parse WHERE clause into structured conditions.
     * 
     * @private
     * @param {string} whereStr - WHERE clause string (without WHERE keyword)
     * @returns {Object} Parsed conditions
     */
    _parseWhereClause(whereStr) {
        // Split by AND (simple approach - doesn't handle nested parens)
        const conditionStrs = whereStr.split(/\s+AND\s+/i);
        const conditions = conditionStrs.map(cond => this._parseCondition(cond.trim()));
        
        return { type: 'AND', conditions };
    }
    
    /**
     * Parse a single condition.
     * 
     * @private
     * @param {string} condStr - Condition string (e.g., "column = 'value'")
     * @returns {Object} Parsed condition
     */
    _parseCondition(condStr) {
        // Check for IN clause: column IN ('val1', 'val2')
        const inMatch = condStr.match(/(\w+)\s+IN\s*\(\s*(.+?)\s*\)/i);
        if (inMatch) {
            const values = inMatch[2].split(',').map(v => 
                v.trim().replace(/^['"]|['"]$/g, '')
            );
            return { column: inMatch[1], operator: 'IN', values };
        }
        
        // Check for LIKE clause: column LIKE '%pattern%'
        const likeMatch = condStr.match(/(\w+)\s+LIKE\s+['"](.+?)['"]/i);
        if (likeMatch) {
            return { column: likeMatch[1], operator: 'LIKE', pattern: likeMatch[2] };
        }
        
        // Check for comparison operators: >=, <=, !=, >, <, =
        const compMatch = condStr.match(/(\w+)\s*(>=|<=|!=|<>|>|<|=)\s*['"]?([^'"]+)['"]?/);
        if (compMatch) {
            let value = compMatch[3].trim();
            // Try to convert to number
            const numValue = parseFloat(value);
            if (!isNaN(numValue) && value === String(numValue)) {
                value = numValue;
            }
            return { 
                column: compMatch[1], 
                operator: compMatch[2] === '<>' ? '!=' : compMatch[2], 
                value 
            };
        }
        
        // Fallback: treat as equality with placeholder
        return { column: condStr, operator: '=', value: '?' };
    }
    
    /**
     * Substitute parameters into WHERE conditions.
     * 
     * @private
     * @param {Object} where - Parsed WHERE clause
     * @param {Array} params - Parameters to substitute
     * @returns {Object} WHERE clause with substituted values
     */
    _substituteParams(where, params) {
        if (!where) return null;
        
        let paramIndex = 0;
        
        const substituteCondition = (cond) => {
            if (cond.value === '?') {
                return { ...cond, value: params[paramIndex++] };
            }
            return cond;
        };
        
        if (where.type === 'AND') {
            return {
                type: 'AND',
                conditions: where.conditions.map(substituteCondition)
            };
        }
        
        return substituteCondition(where);
    }

    /**
     * Get data for table.
     * 
     * @param {string} table - Table name
     * @returns {Array<Object>} Table data
     * @private
     */
    _getTableData(table) {
        // Handle singleton tables (repo_summary, metrics_summary)
        if (table === 'repo_summary' || table === 'metrics_summary') {
            const data = this.data[table];
            return data ? [data] : [];
        }

        // Handle array tables
        const data = this.data[table];
        return Array.isArray(data) ? data : [];
    }

    /**
     * Apply WHERE filter (supports multiple conditions with AND).
     * 
     * @param {Array<Object>} data - Input data
     * @param {Object} where - WHERE clause (parsed)
     * @returns {Array<Object>} Filtered data
     * @private
     */
    _applyWhere(data, where) {
        if (!where) return data;
        
        return data.filter(row => {
            if (where.type === 'AND') {
                return where.conditions.every(cond => this._evaluateCondition(row, cond));
            }
            return this._evaluateCondition(row, where);
        });
    }
    
    /**
     * Evaluate a single condition against a row.
     * 
     * @private
     * @param {Object} row - Data row
     * @param {Object} cond - Condition
     * @returns {boolean} True if condition matches
     */
    _evaluateCondition(row, cond) {
        const rowValue = row[cond.column];
        
        if (rowValue === undefined) {
            return false;
        }
        
        switch (cond.operator) {
            case '=':
                return String(rowValue) === String(cond.value);
            case '!=':
                return String(rowValue) !== String(cond.value);
            case '>':
                return rowValue > cond.value;
            case '>=':
                return rowValue >= cond.value;
            case '<':
                return rowValue < cond.value;
            case '<=':
                return rowValue <= cond.value;
            case 'IN':
                return cond.values.some(v => String(rowValue) === String(v));
            case 'LIKE':
                return this._matchLikePattern(String(rowValue), cond.pattern);
            default:
                return String(rowValue) === String(cond.value);
        }
    }
    
    /**
     * Match SQL LIKE pattern (% = any chars, _ = single char).
     * 
     * @private
     * @param {string} value - Value to test
     * @param {string} pattern - LIKE pattern
     * @returns {boolean} True if matches
     */
    _matchLikePattern(value, pattern) {
        // Convert SQL LIKE pattern to regex
        // % -> .* (any chars), _ -> . (single char)
        const regexPattern = pattern
            .replace(/[.*+?^${}()|[\]\\]/g, '\\$&') // Escape regex special chars
            .replace(/%/g, '.*')
            .replace(/_/g, '.');
        
        const regex = new RegExp(`^${regexPattern}$`, 'i');
        return regex.test(value);
    }
    
    /**
     * Apply aggregate function.
     * 
     * @private
     * @param {Array<Object>} data - Input data
     * @param {Object} aggregate - Aggregate config
     * @returns {Object} Aggregate result
     */
    _applyAggregate(data, aggregate) {
        const { type, column, alias } = aggregate;
        let value;
        
        switch (type) {
            case 'COUNT':
                value = data.length;
                break;
            case 'SUM':
                value = data.reduce((sum, row) => sum + (Number(row[column]) || 0), 0);
                break;
            case 'AVG':
                value = data.length > 0 
                    ? data.reduce((sum, row) => sum + (Number(row[column]) || 0), 0) / data.length
                    : 0;
                break;
            case 'MAX':
                value = data.reduce((max, row) => {
                    const v = row[column];
                    return v > max ? v : max;
                }, data[0]?.[column] ?? null);
                break;
            case 'MIN':
                value = data.reduce((min, row) => {
                    const v = row[column];
                    return v < min ? v : min;
                }, data[0]?.[column] ?? null);
                break;
            default:
                value = null;
        }
        
        return { [alias]: value };
    }

    /**
     * Apply ORDER BY.
     * 
     * @param {Array<Object>} data - Input data
     * @param {Object} orderBy - ORDER BY clause
     * @returns {Array<Object>} Sorted data
     * @private
     */
    _applyOrderBy(data, orderBy) {
        const sorted = [...data];
        sorted.sort((a, b) => {
            const aVal = a[orderBy.column];
            const bVal = b[orderBy.column];

            if (aVal === bVal) return 0;

            let comparison = 0;
            if (typeof aVal === 'string' && typeof bVal === 'string') {
                comparison = aVal.localeCompare(bVal);
            } else {
                comparison = aVal < bVal ? -1 : 1;
            }

            return orderBy.direction === 'DESC' ? -comparison : comparison;
        });
        return sorted;
    }

    /**
     * Select specific columns.
     * 
     * @param {Array<Object>} data - Input data
     * @param {Array<string>} columns - Column names
     * @returns {Array<Object>} Data with selected columns only
     * @private
     */
    _selectColumns(data, columns) {
        return data.map(row => {
            const selected = {};
            columns.forEach(col => {
                if (row.hasOwnProperty(col)) {
                    selected[col] = row[col];
                }
            });
            return selected;
        });
    }

    // =========================================================================
    // HIGH-LEVEL API (SQLiteDataLayer compatible)
    // =========================================================================

    /**
     * Get repository summary (Overview tab).
     * 
     * @returns {Promise<Object>} Repository summary
     */
    async getRepoSummary() {
        return this.queryOne('SELECT * FROM repo_summary WHERE id = 1');
    }

    /**
     * Get metrics summary (Metrics tab).
     * 
     * @returns {Promise<Object>} Metrics summary
     */
    async getMetricsSummary() {
        return this.queryOne('SELECT * FROM metrics_summary WHERE id = 1');
    }

    /**
     * Get executive KPIs (Executive Summary tab).
     * 
     * @returns {Promise<Object>} Executive KPIs
     */
    async getExecutiveKPIs() {
        return this.queryOne('SELECT * FROM executive_kpis');
    }

    /**
     * Get paginated use cases.
     * 
     * @param {Object} options - Query options
     * @param {number} [options.page=1] - Page number (1-based)
     * @param {number} [options.pageSize=20] - Items per page
     * @param {string} [options.sortBy='priority'] - Sort column
     * @param {string} [options.sortOrder='DESC'] - Sort order
     * @param {Object} [options.filters={}] - Filter conditions
     * @returns {Promise<Object>} { data, total, page, pageSize, totalPages }
     */
    async getUseCases(options = {}) {
        return this._getPaginatedData('use_cases', {
            sortBy: 'priority',
            sortOrder: 'DESC',
            ...options
        });
    }

    /**
     * Get paginated vulnerabilities.
     * 
     * @param {Object} options - Query options
     * @returns {Promise<Object>} Paginated vulnerabilities
     */
    async getVulnerabilities(options = {}) {
        return this._getPaginatedData('vulnerabilities', {
            sortBy: 'severity',
            sortOrder: 'DESC',
            ...options
        });
    }

    /**
     * Get paginated packages.
     * 
     * @param {Object} options - Query options
     * @returns {Promise<Object>} Paginated packages
     */
    async getPackages(options = {}) {
        return this._getPaginatedData('packages', {
            sortBy: 'package_name',
            sortOrder: 'ASC',
            ...options
        });
    }

    /**
     * Get paginated code smells.
     * 
     * @param {Object} options - Query options
     * @returns {Promise<Object>} Paginated code smells
     */
    async getCodeSmells(options = {}) {
        return this._getPaginatedData('code_smells', options);
    }

    /**
     * Get paginated files.
     * 
     * @param {Object} options - Query options
     * @returns {Promise<Object>} Paginated files
     */
    async getFiles(options = {}) {
        return this._getPaginatedData('files', options);
    }

    /**
     * Get domain entities.
     * 
     * @param {Object} options - Query options
     * @returns {Promise<Object>} Paginated entities
     */
    async getEntities(options = {}) {
        return this._getPaginatedData('entities', options);
    }

    /**
     * Get domain relationships.
     * 
     * @param {Object} options - Query options
     * @returns {Promise<Object>} Paginated relationships
     */
    async getRelationships(options = {}) {
        return this._getPaginatedData('relationships', options);
    }

    /**
     * Get test results.
     * 
     * @param {Object} options - Query options
     * @returns {Promise<Object>} Paginated test results
     */
    async getTestResults(options = {}) {
        return this._getPaginatedData('test_results', options);
    }

    /**
     * Get LENS insights.
     * 
     * @param {Object} options - Query options
     * @returns {Promise<Object>} Paginated insights
     */
    async getLENSInsights(options = {}) {
        return this._getPaginatedData('lens_insights', options);
    }

    /**
     * Get refactoring suggestions.
     * 
     * @param {Object} options - Query options
     * @returns {Promise<Object>} Paginated suggestions
     */
    async getRefactoringSuggestions(options = {}) {
        return this._getPaginatedData('refactoring_suggestions', {
            sortBy: 'priority',
            sortOrder: 'DESC',
            ...options
        });
    }

    /**
     * Generic paginated data retrieval.
     * 
     * @private
     * @param {string} table - Table name
     * @param {Object} options - Query options
     * @returns {Promise<Object>} Paginated results
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
        let data = this._getTableData(table);

        // Apply filters
        if (Object.keys(filters).length > 0) {
            const whereClause = {
                type: 'AND',
                conditions: Object.entries(filters).map(([column, value]) => ({
                    column,
                    operator: '=',
                    value
                }))
            };
            data = this._applyWhere(data, whereClause);
        }

        const total = data.length;

        // Apply sorting
        data = this._applyOrderBy(data, { column: sortBy, direction: sortOrder });

        // Apply pagination
        data = data.slice(offset, offset + pageSize);

        return {
            data,
            total,
            page,
            pageSize,
            totalPages: Math.ceil(total / pageSize)
        };
    }

    /**
     * Search use cases using fuzzy search.
     * 
     * @param {string} query - Search query
     * @param {Object} options - Search options
     * @returns {Promise<Array<Object>>} Matching use cases
     */
    async searchUseCases(query, options = {}) {
        return this.search('use_cases', query, options);
    }

    /**
     * Search packages using fuzzy search.
     * 
     * @param {string} query - Search query
     * @param {Object} options - Search options
     * @returns {Promise<Array<Object>>} Matching packages
     */
    async searchPackages(query, options = {}) {
        return this.search('packages', query, options);
    }

    /**
     * Search files using fuzzy search.
     * 
     * @param {string} query - Search query
     * @param {Object} options - Search options
     * @returns {Promise<Array<Object>>} Matching files
     */
    async searchFiles(query, options = {}) {
        return this.search('files', query, options);
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = JSONDataAdapter;
}
