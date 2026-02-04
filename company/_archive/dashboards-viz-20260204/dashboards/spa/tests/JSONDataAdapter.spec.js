/**
 * JSONDataAdapter Unit Tests
 * ==========================
 * 
 * TDD tests for the JSON data adapter that provides SQL-like query interface.
 * 
 * @author Asif Hussain
 * @version 1.0
 * @date 2026-02-03
 */

// Load the adapter (adjust path for test runner)
const JSONDataAdapter = require('../js/data/JSONDataAdapter.js');

describe('JSONDataAdapter', () => {
    let adapter;
    let mockData;

    beforeEach(() => {
        // Setup comprehensive mock data
        mockData = {
            repo_summary: {
                id: 1,
                repo_name: 'cortex',
                health_score: 85.5,
                total_files: 150,
                total_loc: 25000
            },
            metrics_summary: {
                id: 1,
                avg_complexity: 4.2,
                test_coverage: 78.5,
                maintainability_index: 72.0
            },
            use_cases: [
                { id: 1, title: 'User Login', priority: 'high', status: 'implemented', category: 'auth' },
                { id: 2, title: 'Dashboard View', priority: 'medium', status: 'in_progress', category: 'ui' },
                { id: 3, title: 'API Integration', priority: 'high', status: 'planned', category: 'api' },
                { id: 4, title: 'Report Generation', priority: 'low', status: 'implemented', category: 'reports' },
                { id: 5, title: 'User Logout', priority: 'low', status: 'implemented', category: 'auth' }
            ],
            vulnerabilities: [
                { id: 1, title: 'SQL Injection', severity: 'critical', cwe_id: 'CWE-89', status: 'open' },
                { id: 2, title: 'XSS Attack', severity: 'high', cwe_id: 'CWE-79', status: 'fixed' },
                { id: 3, title: 'Open Redirect', severity: 'medium', cwe_id: 'CWE-601', status: 'open' }
            ],
            packages: [
                { id: 1, package_name: 'fastapi', version: '0.100.0', package_type: 'runtime' },
                { id: 2, package_name: 'pytest', version: '7.4.0', package_type: 'dev' },
                { id: 3, package_name: 'pydantic', version: '2.0.0', package_type: 'runtime' }
            ],
            code_smells: [
                { id: 1, name: 'Long Method', location: 'src/main.py:50', severity: 'medium' },
                { id: 2, name: 'God Class', location: 'src/core.py:1', severity: 'high' }
            ],
            files: [
                { id: 1, file_path: 'src/main.py', loc: 500, complexity: 8 },
                { id: 2, file_path: 'src/core.py', loc: 1200, complexity: 15 },
                { id: 3, file_path: 'tests/test_main.py', loc: 300, complexity: 3 }
            ]
        };

        adapter = new JSONDataAdapter(mockData, 'cortex');
    });

    afterEach(() => {
        adapter = null;
        mockData = null;
    });

    // =========================================================================
    // BASIC QUERY TESTS
    // =========================================================================

    describe('Basic SELECT queries', () => {
        test('SELECT * FROM table returns all rows', () => {
            const results = adapter.query('SELECT * FROM use_cases');
            expect(results).toHaveLength(5);
            expect(results[0]).toHaveProperty('title', 'User Login');
        });

        test('SELECT specific columns returns only those columns', () => {
            const results = adapter.query('SELECT id, title FROM use_cases');
            expect(results).toHaveLength(5);
            expect(results[0]).toHaveProperty('id', 1);
            expect(results[0]).toHaveProperty('title', 'User Login');
            expect(results[0]).not.toHaveProperty('priority');
        });

        test('SELECT from singleton table returns array with single object', () => {
            const results = adapter.query('SELECT * FROM repo_summary');
            expect(results).toHaveLength(1);
            expect(results[0]).toHaveProperty('repo_name', 'cortex');
        });

        test('SELECT from non-existent table returns empty array', () => {
            const results = adapter.query('SELECT * FROM non_existent');
            expect(results).toEqual([]);
        });
    });

    // =========================================================================
    // WHERE CLAUSE TESTS
    // =========================================================================

    describe('WHERE clause filtering', () => {
        test('WHERE column = value filters correctly', () => {
            const results = adapter.query("SELECT * FROM use_cases WHERE priority = 'high'");
            expect(results).toHaveLength(2);
            results.forEach(r => expect(r.priority).toBe('high'));
        });

        test('WHERE with numeric comparison > works', () => {
            const results = adapter.query('SELECT * FROM files WHERE loc > 400');
            expect(results).toHaveLength(2);
            results.forEach(r => expect(r.loc).toBeGreaterThan(400));
        });

        test('WHERE with numeric comparison < works', () => {
            const results = adapter.query('SELECT * FROM files WHERE complexity < 10');
            expect(results).toHaveLength(2);
            results.forEach(r => expect(r.complexity).toBeLessThan(10));
        });

        test('WHERE with >= comparison works', () => {
            const results = adapter.query('SELECT * FROM files WHERE complexity >= 8');
            expect(results).toHaveLength(2);
        });

        test('WHERE with <= comparison works', () => {
            const results = adapter.query('SELECT * FROM files WHERE loc <= 500');
            expect(results).toHaveLength(2);
        });

        test('WHERE with != comparison works', () => {
            const results = adapter.query("SELECT * FROM use_cases WHERE status != 'implemented'");
            expect(results).toHaveLength(2);
            results.forEach(r => expect(r.status).not.toBe('implemented'));
        });

        test('WHERE with multiple AND conditions works', () => {
            const results = adapter.query("SELECT * FROM use_cases WHERE priority = 'high' AND status = 'implemented'");
            expect(results).toHaveLength(1);
            expect(results[0].title).toBe('User Login');
        });

        test('WHERE with LIKE pattern matching works', () => {
            const results = adapter.query("SELECT * FROM use_cases WHERE title LIKE '%Login%'");
            expect(results).toHaveLength(1);
            expect(results[0].title).toBe('User Login');
        });

        test('WHERE with LIKE % prefix matches ending', () => {
            const results = adapter.query("SELECT * FROM use_cases WHERE title LIKE '%View'");
            expect(results).toHaveLength(1);
            expect(results[0].title).toBe('Dashboard View');
        });

        test('WHERE with IN clause works', () => {
            const results = adapter.query("SELECT * FROM vulnerabilities WHERE severity IN ('critical', 'high')");
            expect(results).toHaveLength(2);
        });
    });

    // =========================================================================
    // ORDER BY TESTS
    // =========================================================================

    describe('ORDER BY sorting', () => {
        test('ORDER BY ASC sorts ascending', () => {
            const results = adapter.query('SELECT * FROM use_cases ORDER BY id ASC');
            expect(results[0].id).toBe(1);
            expect(results[4].id).toBe(5);
        });

        test('ORDER BY DESC sorts descending', () => {
            const results = adapter.query('SELECT * FROM use_cases ORDER BY id DESC');
            expect(results[0].id).toBe(5);
            expect(results[4].id).toBe(1);
        });

        test('ORDER BY string column sorts alphabetically', () => {
            const results = adapter.query('SELECT * FROM packages ORDER BY package_name ASC');
            expect(results[0].package_name).toBe('fastapi');
            expect(results[2].package_name).toBe('pytest');
        });

        test('ORDER BY defaults to ASC when not specified', () => {
            const results = adapter.query('SELECT * FROM use_cases ORDER BY id');
            expect(results[0].id).toBe(1);
        });
    });

    // =========================================================================
    // LIMIT & OFFSET TESTS
    // =========================================================================

    describe('LIMIT and OFFSET pagination', () => {
        test('LIMIT restricts result count', () => {
            const results = adapter.query('SELECT * FROM use_cases LIMIT 2');
            expect(results).toHaveLength(2);
        });

        test('OFFSET skips rows', () => {
            const results = adapter.query('SELECT * FROM use_cases OFFSET 2');
            expect(results).toHaveLength(3);
            expect(results[0].id).toBe(3);
        });

        test('LIMIT and OFFSET together paginate correctly', () => {
            const results = adapter.query('SELECT * FROM use_cases LIMIT 2 OFFSET 2');
            expect(results).toHaveLength(2);
            expect(results[0].id).toBe(3);
            expect(results[1].id).toBe(4);
        });

        test('OFFSET beyond data length returns empty array', () => {
            const results = adapter.query('SELECT * FROM use_cases OFFSET 100');
            expect(results).toEqual([]);
        });
    });

    // =========================================================================
    // AGGREGATE FUNCTION TESTS
    // =========================================================================

    describe('Aggregate functions', () => {
        test('COUNT(*) returns row count', () => {
            const results = adapter.query('SELECT COUNT(*) FROM use_cases');
            expect(results).toHaveLength(1);
            expect(results[0].count).toBe(5);
        });

        test('COUNT(*) with WHERE filters before counting', () => {
            const results = adapter.query("SELECT COUNT(*) FROM use_cases WHERE priority = 'high'");
            expect(results[0].count).toBe(2);
        });

        test('SUM(column) calculates sum', () => {
            const results = adapter.query('SELECT SUM(loc) FROM files');
            expect(results[0].sum).toBe(2000);
        });

        test('AVG(column) calculates average', () => {
            const results = adapter.query('SELECT AVG(loc) FROM files');
            expect(results[0].avg).toBeCloseTo(666.67, 1);
        });

        test('MAX(column) finds maximum', () => {
            const results = adapter.query('SELECT MAX(complexity) FROM files');
            expect(results[0].max).toBe(15);
        });

        test('MIN(column) finds minimum', () => {
            const results = adapter.query('SELECT MIN(complexity) FROM files');
            expect(results[0].min).toBe(3);
        });
    });

    // =========================================================================
    // HELPER METHOD TESTS
    // =========================================================================

    describe('Helper methods', () => {
        test('queryOne returns single row', () => {
            const result = adapter.queryOne('SELECT * FROM use_cases WHERE id = 1');
            expect(result).toBeTruthy();
            expect(result.title).toBe('User Login');
        });

        test('queryOne returns null for no match', () => {
            const result = adapter.queryOne('SELECT * FROM use_cases WHERE id = 999');
            expect(result).toBeNull();
        });

        test('queryScalar returns single value', () => {
            const result = adapter.queryScalar('SELECT COUNT(*) FROM use_cases');
            expect(result).toBe(5);
        });

        test('queryScalar returns null for no results', () => {
            const result = adapter.queryScalar('SELECT * FROM non_existent');
            expect(result).toBeNull();
        });
    });

    // =========================================================================
    // PARAMETERIZED QUERY TESTS
    // =========================================================================

    describe('Parameterized queries', () => {
        test('params substitute into WHERE clause', () => {
            // Simulating prepared statement style
            const results = adapter.query("SELECT * FROM use_cases WHERE priority = ?", ['high']);
            expect(results).toHaveLength(2);
        });
    });

    // =========================================================================
    // SEARCH TESTS (Fuzzy FTS5 fallback)
    // =========================================================================

    describe('Search functionality', () => {
        test('search finds matching rows by string content', () => {
            const results = adapter.search('use_cases', 'login');
            expect(results.length).toBeGreaterThan(0);
            expect(results.some(r => r.title.toLowerCase().includes('login'))).toBe(true);
        });

        test('search is case insensitive', () => {
            const resultsLower = adapter.search('use_cases', 'login');
            const resultsUpper = adapter.search('use_cases', 'LOGIN');
            expect(resultsLower).toEqual(resultsUpper);
        });

        test('search respects limit option', () => {
            const results = adapter.search('use_cases', 'u', { limit: 2 });
            expect(results.length).toBeLessThanOrEqual(2);
        });

        test('search respects offset option', () => {
            const allResults = adapter.search('use_cases', 'u');
            const offsetResults = adapter.search('use_cases', 'u', { offset: 1 });
            
            if (allResults.length > 1) {
                expect(offsetResults.length).toBe(allResults.length - 1);
            }
        });

        test('search returns empty array for no match', () => {
            const results = adapter.search('use_cases', 'xyznonexistent');
            expect(results).toEqual([]);
        });
    });

    // =========================================================================
    // HIGH-LEVEL API TESTS (SQLiteDataLayer compatible)
    // =========================================================================

    describe('High-level API methods', () => {
        test('getRepoSummary returns summary object', async () => {
            const summary = await adapter.getRepoSummary();
            expect(summary).toBeTruthy();
            expect(summary.repo_name).toBe('cortex');
            expect(summary.health_score).toBe(85.5);
        });

        test('getMetricsSummary returns metrics', async () => {
            const metrics = await adapter.getMetricsSummary();
            expect(metrics).toBeTruthy();
            expect(metrics.avg_complexity).toBe(4.2);
        });

        test('getUseCases returns paginated results', async () => {
            const result = await adapter.getUseCases({ page: 1, pageSize: 2 });
            
            expect(result).toHaveProperty('data');
            expect(result).toHaveProperty('total', 5);
            expect(result).toHaveProperty('page', 1);
            expect(result).toHaveProperty('pageSize', 2);
            expect(result).toHaveProperty('totalPages', 3);
            expect(result.data).toHaveLength(2);
        });

        test('getUseCases with filters works', async () => {
            const result = await adapter.getUseCases({
                filters: { category: 'auth' }
            });
            
            expect(result.data).toHaveLength(2);
            result.data.forEach(uc => expect(uc.category).toBe('auth'));
        });

        test('getVulnerabilities returns paginated results', async () => {
            const result = await adapter.getVulnerabilities();
            expect(result.total).toBe(3);
        });

        test('getPackages returns paginated results', async () => {
            const result = await adapter.getPackages();
            expect(result.total).toBe(3);
        });

        test('getCodeSmells returns paginated results', async () => {
            const result = await adapter.getCodeSmells();
            expect(result.total).toBe(2);
        });

        test('getFiles returns paginated results', async () => {
            const result = await adapter.getFiles();
            expect(result.total).toBe(3);
        });

        test('searchUseCases performs fuzzy search', async () => {
            const results = await adapter.searchUseCases('login');
            expect(results.length).toBeGreaterThan(0);
        });
    });

    // =========================================================================
    // EDGE CASES & ERROR HANDLING
    // =========================================================================

    describe('Edge cases and error handling', () => {
        test('empty data returns empty results', () => {
            const emptyAdapter = new JSONDataAdapter({});
            const results = emptyAdapter.query('SELECT * FROM anything');
            expect(results).toEqual([]);
        });

        test('null data is handled gracefully', () => {
            const nullAdapter = new JSONDataAdapter(null);
            const results = nullAdapter.query('SELECT * FROM test');
            expect(results).toEqual([]);
        });

        test('malformed SQL returns empty array', () => {
            const results = adapter.query('INVALID SQL STATEMENT');
            expect(results).toEqual([]);
        });

        test('complex query combines all clauses', () => {
            const results = adapter.query(`
                SELECT id, title 
                FROM use_cases 
                WHERE priority = 'high' 
                ORDER BY id DESC 
                LIMIT 1
            `);
            
            expect(results).toHaveLength(1);
            expect(results[0].id).toBe(3); // API Integration is id=3, sorted DESC
        });
    });
});
