/**
 * DualFormatDataLoader Unit Tests
 * ================================
 * 
 * TDD tests for the dual-format data loader that supports both SQLite and JSON.
 * 
 * @author Asif Hussain
 * @version 1.0
 * @date 2026-02-03
 */

describe('DualFormatDataLoader', () => {
    let loader;
    let mockFetch;
    let originalFetch;

    beforeEach(() => {
        // Save original fetch
        originalFetch = global.fetch;

        // Create mock fetch
        mockFetch = jest.fn();
        global.fetch = mockFetch;

        // Create loader instance
        loader = new DualFormatDataLoader({
            basePath: '/repos',
            preferSQLite: true,
            logFormat: false
        });
    });

    afterEach(() => {
        // Restore original fetch
        global.fetch = originalFetch;
        loader = null;
    });

    // =========================================================================
    // FORMAT DETECTION TESTS
    // =========================================================================

    describe('Format detection', () => {
        test('detects SQLite format when .sqlite file exists', async () => {
            mockFetch.mockImplementation((url, options) => {
                if (options?.method === 'HEAD') {
                    return Promise.resolve({
                        ok: url.includes('.sqlite')
                    });
                }
            });

            const format = await loader._detectFormat('cortex');
            expect(format).toBe('sqlite');
        });

        test('falls back to JSON when SQLite not available', async () => {
            mockFetch.mockImplementation((url, options) => {
                if (options?.method === 'HEAD') {
                    return Promise.resolve({
                        ok: url.includes('.json')
                    });
                }
            });

            const format = await loader._detectFormat('cortex');
            expect(format).toBe('json');
        });

        test('returns none when no files exist', async () => {
            mockFetch.mockResolvedValue({ ok: false });

            const format = await loader._detectFormat('nonexistent');
            expect(format).toBe('none');
        });

        test('respects preferSQLite=false option', async () => {
            loader = new DualFormatDataLoader({
                preferSQLite: false
            });

            mockFetch.mockImplementation((url, options) => {
                if (options?.method === 'HEAD') {
                    return Promise.resolve({ ok: true });
                }
            });

            const format = await loader._detectFormat('cortex');
            expect(format).toBe('json');
        });
    });

    // =========================================================================
    // CACHING TESTS
    // =========================================================================

    describe('Caching', () => {
        test('caches loaded data layers', async () => {
            const mockData = { repo_summary: { id: 1 } };
            
            mockFetch.mockImplementation((url, options) => {
                if (options?.method === 'HEAD') {
                    return Promise.resolve({ ok: url.includes('.json') });
                }
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve(mockData)
                });
            });

            // First load
            await loader.load('cortex');
            
            // Second load should use cache
            await loader.load('cortex');

            // Fetch should only be called for HEAD (2x) and GET (1x)
            // Cache hit means no second GET
            const getCalls = mockFetch.mock.calls.filter(
                call => !call[1]?.method
            ).length;
            expect(getCalls).toBe(1);
        });

        test('clearCache removes specific slug', async () => {
            loader.cache.set('cortex', { mock: true });
            loader.cache.set('other', { mock: true });

            loader.clearCache('cortex');

            expect(loader.cache.has('cortex')).toBe(false);
            expect(loader.cache.has('other')).toBe(true);
        });

        test('clearCache without argument clears all', () => {
            loader.cache.set('cortex', { mock: true });
            loader.cache.set('other', { mock: true });

            loader.clearCache();

            expect(loader.cache.size).toBe(0);
        });
    });

    // =========================================================================
    // JSON LOADING TESTS
    // =========================================================================

    describe('JSON loading', () => {
        beforeEach(() => {
            // Mock JSONDataAdapter globally
            global.JSONDataAdapter = class {
                constructor(data, slug) {
                    this.data = data;
                    this.slug = slug;
                }
            };
        });

        afterEach(() => {
            delete global.JSONDataAdapter;
        });

        test('loads JSON data and creates adapter', async () => {
            const mockData = {
                repo_summary: { id: 1, repo_name: 'cortex' },
                use_cases: []
            };

            mockFetch.mockImplementation((url, options) => {
                if (options?.method === 'HEAD') {
                    return Promise.resolve({ ok: url.includes('.json') });
                }
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve(mockData)
                });
            });

            const dataLayer = await loader.load('cortex');

            expect(dataLayer).toBeDefined();
            expect(dataLayer.data).toEqual(mockData);
            expect(dataLayer.slug).toBe('cortex');
        });

        test('throws error for failed JSON fetch', async () => {
            mockFetch.mockImplementation((url, options) => {
                if (options?.method === 'HEAD') {
                    return Promise.resolve({ ok: url.includes('.json') });
                }
                return Promise.resolve({
                    ok: false,
                    statusText: 'Not Found'
                });
            });

            await expect(loader.load('cortex')).rejects.toThrow('Failed to load JSON data');
        });
    });

    // =========================================================================
    // ERROR HANDLING TESTS
    // =========================================================================

    describe('Error handling', () => {
        test('throws error when no data found', async () => {
            mockFetch.mockResolvedValue({ ok: false });

            await expect(loader.load('nonexistent')).rejects.toThrow('No data found');
        });

        test('handles network errors gracefully', async () => {
            mockFetch.mockRejectedValue(new Error('Network error'));

            const format = await loader._detectFormat('cortex');
            expect(format).toBe('none');
        });
    });

    // =========================================================================
    // PRELOAD MULTIPLE TESTS
    // =========================================================================

    describe('Preload multiple', () => {
        beforeEach(() => {
            global.JSONDataAdapter = class {
                constructor(data, slug) {
                    this.data = data;
                    this.slug = slug;
                }
            };
        });

        afterEach(() => {
            delete global.JSONDataAdapter;
        });

        test('loads multiple repositories in parallel', async () => {
            const mockData = { repo_summary: { id: 1 } };

            mockFetch.mockImplementation((url, options) => {
                if (options?.method === 'HEAD') {
                    return Promise.resolve({ ok: url.includes('.json') });
                }
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve(mockData)
                });
            });

            const result = await loader.preloadMultiple(['repo1', 'repo2', 'repo3']);

            expect(result.size).toBe(3);
            expect(result.has('repo1')).toBe(true);
            expect(result.has('repo2')).toBe(true);
            expect(result.has('repo3')).toBe(true);
        });

        test('continues loading even if some fail', async () => {
            global.JSONDataAdapter = class {
                constructor(data, slug) {
                    this.data = data;
                    this.slug = slug;
                }
            };

            let callCount = 0;
            mockFetch.mockImplementation((url, options) => {
                if (options?.method === 'HEAD') {
                    // Only repo1 exists
                    return Promise.resolve({ 
                        ok: url.includes('repo1') && url.includes('.json')
                    });
                }
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve({ repo_summary: {} })
                });
            });

            const result = await loader.preloadMultiple(['repo1', 'nonexistent']);

            // repo1 should be loaded, nonexistent returns null
            expect(result.get('repo1')).toBeDefined();
        });
    });

    // =========================================================================
    // FORMAT INFO TESTS
    // =========================================================================

    describe('Format info', () => {
        test('returns format info for existing repo', async () => {
            mockFetch.mockImplementation((url, options) => {
                if (options?.method === 'HEAD') {
                    if (url.includes('.json')) {
                        return Promise.resolve({
                            ok: true,
                            headers: {
                                get: (name) => name === 'content-length' ? '1024' : null
                            }
                        });
                    }
                }
                return Promise.resolve({ ok: false });
            });

            const info = await loader.getFormatInfo('cortex');

            expect(info.format).toBe('json');
            expect(info.available).toBe(true);
            expect(info.size).toBe(1024);
            expect(info.sizeFormatted).toBe('1 KB');
        });

        test('returns unavailable for non-existent repo', async () => {
            mockFetch.mockResolvedValue({ ok: false });

            const info = await loader.getFormatInfo('nonexistent');

            expect(info.format).toBe('none');
            expect(info.available).toBe(false);
        });
    });

    // =========================================================================
    // TEST CONNECTION TESTS
    // =========================================================================

    describe('Test connection', () => {
        beforeEach(() => {
            global.JSONDataAdapter = class {
                constructor(data, slug) {
                    this.data = data;
                    this.slug = slug;
                }
                query(sql) {
                    return [this.data.repo_summary];
                }
            };
        });

        afterEach(() => {
            delete global.JSONDataAdapter;
        });

        test('returns success for valid connection', async () => {
            const mockData = {
                repo_summary: { id: 1, repo_name: 'cortex', health_score: 85 }
            };

            mockFetch.mockImplementation((url, options) => {
                if (options?.method === 'HEAD') {
                    return Promise.resolve({ ok: url.includes('.json') });
                }
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve(mockData)
                });
            });

            const result = await loader.testConnection('cortex');

            expect(result.success).toBe(true);
            expect(result.repoName).toBe('cortex');
            expect(result.healthScore).toBe(85);
        });

        test('returns failure for invalid connection', async () => {
            mockFetch.mockResolvedValue({ ok: false });

            const result = await loader.testConnection('nonexistent');

            expect(result.success).toBe(false);
            expect(result.message).toContain('No data found');
        });
    });

    // =========================================================================
    // UTILITY METHOD TESTS
    // =========================================================================

    describe('Utility methods', () => {
        test('formatBytes formats bytes correctly', () => {
            expect(loader._formatBytes(0)).toBe('0 Bytes');
            expect(loader._formatBytes(500)).toBe('500 Bytes');
            expect(loader._formatBytes(1024)).toBe('1 KB');
            expect(loader._formatBytes(1536)).toBe('1.5 KB');
            expect(loader._formatBytes(1048576)).toBe('1 MB');
            expect(loader._formatBytes(1073741824)).toBe('1 GB');
        });
    });
});

// Mock DualFormatDataLoader class for testing (when not running in browser)
if (typeof DualFormatDataLoader === 'undefined') {
    // Load the actual implementation
    const DualFormatDataLoader = require('../js/data/DualFormatDataLoader.js');
    global.DualFormatDataLoader = DualFormatDataLoader;
}
