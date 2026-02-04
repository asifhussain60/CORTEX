/**
 * JSONDataAdapter.js
 * ===================
 * 
 * Purpose: Wrap JSON data with SQL-like query interface for backward compatibility
 * Created: 2026-02-03
 * Authority: PHASE-21-ENTERPRISE-REPOSITORY-INTELLIGENCE.yaml lines 750-760
 * 
 * Features:
 * - Parses limited SQL subset (SELECT, WHERE, LIMIT, OFFSET)
 * - Executes against JSON data using array methods
 * - Returns results matching SQLite format
 * - Fallback for repositories without dashboard.sqlite
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
     */
    constructor(data) {
        this.data = data || {};
    }

    /**
     * Execute SQL-like query against JSON data.
     * 
     * Supported syntax:
     * - SELECT * FROM table
     * - SELECT column1, column2 FROM table
     * - WHERE column = 'value' (single condition only)
     * - LIMIT n
     * - OFFSET n
     * - ORDER BY column ASC|DESC
     * 
     * @param {string} sql - SQL query string
     * @returns {Array<Object>} Query results
     */
    query(sql) {
        try {
            const parsed = this._parseSQL(sql);
            let results = this._getTableData(parsed.table);

            // Apply WHERE filter
            if (parsed.where) {
                results = this._applyWhere(results, parsed.where);
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
     * Search table with fuzzy matching (fallback for FTS5).
     * 
     * @param {string} table - Table name
     * @param {string} query - Search query
     * @returns {Array<Object>} Matching rows
     */
    search(table, query) {
        const data = this._getTableData(table);
        if (!data || data.length === 0) {
            return [];
        }

        const lowerQuery = query.toLowerCase();
        
        return data.filter(row => {
            // Search all string fields
            return Object.values(row).some(value => {
                if (typeof value === 'string') {
                    return value.toLowerCase().includes(lowerQuery);
                }
                return false;
            });
        });
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
            orderBy: null
        };

        // Remove extra whitespace
        sql = sql.trim().replace(/\s+/g, ' ');

        // Extract SELECT columns
        const selectMatch = sql.match(/SELECT\s+(.+?)\s+FROM/i);
        if (selectMatch) {
            const columnsStr = selectMatch[1].trim();
            if (columnsStr === '*') {
                result.columns = ['*'];
            } else {
                result.columns = columnsStr.split(',').map(c => c.trim());
            }
        }

        // Extract FROM table
        const fromMatch = sql.match(/FROM\s+(\w+)/i);
        if (fromMatch) {
            result.table = fromMatch[1];
        }

        // Extract WHERE clause (simple: column = 'value')
        const whereMatch = sql.match(/WHERE\s+(\w+)\s*=\s*['"]([^'"]+)['"]/i);
        if (whereMatch) {
            result.where = {
                column: whereMatch[1],
                value: whereMatch[2]
            };
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
     * Apply WHERE filter.
     * 
     * @param {Array<Object>} data - Input data
     * @param {Object} where - WHERE clause
     * @returns {Array<Object>} Filtered data
     * @private
     */
    _applyWhere(data, where) {
        return data.filter(row => {
            const rowValue = row[where.column];
            if (rowValue === undefined) {
                return false;
            }
            // Convert both to strings for comparison
            return String(rowValue) === String(where.value);
        });
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
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = JSONDataAdapter;
}
