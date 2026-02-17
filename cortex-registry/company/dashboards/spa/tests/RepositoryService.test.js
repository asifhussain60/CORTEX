/**
 * RepositoryService Test Suite
 * 
 * Tests data loading coordination, request deduplication,
 * cache management, and embedded data support.
 * 
 * TDD Pattern: RED → GREEN → REFACTOR
 * Authority: CORE-008 (TDD mandatory)
 */

describe('RepositoryService', () => {
    let repositoryService;
    let mockStateManager;
    let mockValidationService;
    let mockFetch;

    beforeEach(() => {
        mockStateManager = {
            setState: jest.fn(),
            getState: jest.fn(() => ({
                currentRepo: null,
                data: null,
                isLoading: false
            }))
        };

        mockValidationService = {
            validateDataIntegrity: jest.fn(() => ({ valid: true, errors: [] })),
            sanitizeObject: jest.fn(data => data)
        };

        repositoryService = new RepositoryService(
            mockStateManager,
            mockValidationService
        );

        mockFetch = jest.fn();
        global.fetch = mockFetch;
    });

    afterEach(() => {
        jest.restoreAllMocks();
    });

    describe('Initialization', () => {
        it('should initialize with dependencies', () => {
            expect(repositoryService.stateManager).toBe(mockStateManager);
            expect(repositoryService.validationService).toBe(mockValidationService);
        });

        it('should initialize request cache', () => {
            expect(repositoryService.requestCache).toBeDefined();
            expect(repositoryService.requestCache.size).toBe(0);
        });

        it('should initialize abort controllers', () => {
            expect(repositoryService.abortControllers).toBeDefined();
        });
    });

    describe('Data Loading', () => {
        it('should load repository data', async () => {
            const mockData = {
                id: 'repo1',
                name: 'Test Repo',
                metrics: { files: 100 }
            };

            mockFetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockData
            });

            const result = await repositoryService.loadRepository('repo1');

            expect(result).toEqual(mockData);
            expect(mockValidationService.validateDataIntegrity).toHaveBeenCalled();
        });

        it('should handle fetch errors', async () => {
            mockFetch.mockRejectedValueOnce(new Error('Network error'));

            await expect(
                repositoryService.loadRepository('repo1')
            ).rejects.toThrow('Network error');
        });

        it('should handle HTTP errors', async () => {
            mockFetch.mockResolvedValueOnce({
                ok: false,
                status: 404,
                statusText: 'Not Found'
            });

            await expect(
                repositoryService.loadRepository('repo1')
            ).rejects.toThrow('404');
        });

        it('should update state after loading', async () => {
            const mockData = { id: 'repo1', name: 'Test' };

            mockFetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockData
            });

            await repositoryService.loadRepository('repo1');

            expect(mockStateManager.setState).toHaveBeenCalledWith(
                expect.objectContaining({
                    currentRepo: 'repo1',
                    data: mockData,
                    isLoading: false
                })
            );
        });
    });

    describe('Request Deduplication', () => {
        it('should deduplicate concurrent requests', async () => {
            const mockData = { id: 'repo1' };
            mockFetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockData
            });

            const promise1 = repositoryService.loadRepository('repo1');
            const promise2 = repositoryService.loadRepository('repo1');

            const [result1, result2] = await Promise.all([promise1, promise2]);

            expect(result1).toEqual(result2);
            expect(mockFetch).toHaveBeenCalledTimes(1); // Only one actual fetch
        });

        it('should cache results for subsequent requests', async () => {
            const mockData = { id: 'repo1' };
            mockFetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockData
            });

            await repositoryService.loadRepository('repo1');
            const cachedResult = await repositoryService.loadRepository('repo1');

            expect(cachedResult).toEqual(mockData);
            expect(mockFetch).toHaveBeenCalledTimes(1); // Only one fetch
        });

        it('should handle cache expiration', async () => {
            const mockData = { id: 'repo1' };
            mockFetch.mockResolvedValue({
                ok: true,
                json: async () => mockData
            });

            await repositoryService.loadRepository('repo1');
            
            jest.advanceTimersByTime(6 * 60 * 1000); // Advance past 5min TTL

            await repositoryService.loadRepository('repo1');

            expect(mockFetch).toHaveBeenCalledTimes(2); // Cache expired, fetch again
        });
    });

    describe('Abort Controller Management', () => {
        it('should create abort controller for request', async () => {
            mockFetch.mockResolvedValueOnce({
                ok: true,
                json: async () => ({ id: 'repo1' })
            });

            await repositoryService.loadRepository('repo1');

            expect(repositoryService.abortControllers.has('repo1')).toBe(true);
        });

        it('should cancel inflight requests', async () => {
            const abortSpy = jest.fn();
            mockFetch.mockImplementation(() =>
                new Promise(resolve => setTimeout(() => resolve({
                    ok: true,
                    json: async () => ({ id: 'repo1' })
                }), 1000))
            );

            const promise = repositoryService.loadRepository('repo1');

            const controller = repositoryService.abortControllers.get('repo1');
            controller.signal.addEventListener('abort', abortSpy);

            repositoryService.cancelRequest('repo1');

            await expect(promise).rejects.toThrow();
            expect(abortSpy).toHaveBeenCalled();
        });

        it('should cancel all requests', () => {
            const mockController1 = { abort: jest.fn() };
            const mockController2 = { abort: jest.fn() };

            repositoryService.abortControllers.set('req1', mockController1);
            repositoryService.abortControllers.set('req2', mockController2);

            repositoryService.cancelAllRequests();

            expect(mockController1.abort).toHaveBeenCalled();
            expect(mockController2.abort).toHaveBeenCalled();
        });
    });

    describe('Embedded Data Support', () => {
        it('should load embedded data from window object', async () => {
            const embeddedData = { id: 'repo1', embedded: true };
            global.CORTEX_DATA = { repo1: embeddedData };

            const result = await repositoryService.loadRepository('repo1');

            expect(result).toEqual(embeddedData);
            expect(mockFetch).not.toHaveBeenCalled();

            delete global.CORTEX_DATA;
        });

        it('should fallback to fetch if no embedded data', async () => {
            delete global.CORTEX_DATA;
            const mockData = { id: 'repo1' };

            mockFetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockData
            });

            const result = await repositoryService.loadRepository('repo1');

            expect(mockFetch).toHaveBeenCalled();
        });

        it('should handle file:// protocol URLs', async () => {
            const result = repositoryService.shouldUseEmbeddedData('file:///data/repo.json');

            expect(result).toBe(true);
        });
    });

    describe('Parallel Loading', () => {
        it('should load multiple repositories in parallel', async () => {
            const repos = ['repo1', 'repo2', 'repo3'];
            
            mockFetch.mockResolvedValue({
                ok: true,
                json: async () => ({ id: 'test' })
            });

            const start = Date.now();
            await repositoryService.loadMultiple(repos);
            const duration = Date.now() - start;

            expect(mockFetch).toHaveBeenCalledTimes(3);
            // Should be faster than sequential (3x time)
            expect(duration).toBeLessThan(3000);
        });

        it('should handle partial failures in parallel loading', async () => {
            mockFetch
                .mockResolvedValueOnce({
                    ok: true,
                    json: async () => ({ id: 'repo1' })
                })
                .mockRejectedValueOnce(new Error('Failed'))
                .mockResolvedValueOnce({
                    ok: true,
                    json: async () => ({ id: 'repo3' })
                });

            const result = await repositoryService.loadMultiple(
                ['repo1', 'repo2', 'repo3']
            );

            expect(result.fulfilled.length).toBe(2);
            expect(result.rejected.length).toBe(1);
        });

        it('should use Promise.allSettled for robustness', async () => {
            const repos = ['repo1', 'repo2', 'repo3'];
            
            mockFetch
                .mockResolvedValueOnce({ ok: true, json: async () => ({ id: 'repo1' }) })
                .mockRejectedValueOnce(new Error('Failed'))
                .mockResolvedValueOnce({ ok: true, json: async () => ({ id: 'repo3' }) });

            const results = await repositoryService.loadMultiple(repos);

            expect(results.fulfilled[0].value).toEqual({ id: 'repo1' });
            expect(results.rejected[0].reason).toBeInstanceOf(Error);
            expect(results.fulfilled[1].value).toEqual({ id: 'repo3' });
        });
    });

    describe('Schema Validation', () => {
        it('should validate loaded data against schema', async () => {
            const mockData = { id: 'repo1', name: 'Test' };

            mockFetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockData
            });

            mockValidationService.validateDataIntegrity.mockReturnValueOnce({
                valid: false,
                errors: ['Invalid structure']
            });

            await expect(
                repositoryService.loadRepository('repo1')
            ).rejects.toThrow();
        });

        it('should sanitize data before returning', async () => {
            const mockData = { id: 'repo1', html: '<script>alert(1)</script>' };
            const sanitizedData = { id: 'repo1', html: 'safe' };

            mockFetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockData
            });

            mockValidationService.sanitizeObject.mockReturnValueOnce(sanitizedData);

            const result = await repositoryService.loadRepository('repo1');

            expect(mockValidationService.sanitizeObject).toHaveBeenCalled();
        });
    });

    describe('Error Recovery', () => {
        it('should retry failed requests', async () => {
            let attempts = 0;

            mockFetch.mockImplementation(() => {
                attempts++;
                if (attempts < 3) {
                    return Promise.reject(new Error('Temp failure'));
                }
                return Promise.resolve({
                    ok: true,
                    json: async () => ({ id: 'repo1' })
                });
            });

            const result = await repositoryService.loadRepository('repo1', {
                retryCount: 3
            });

            expect(result.id).toBe('repo1');
            expect(attempts).toBe(3);
        });

        it('should apply backoff strategy', async () => {
            const timestamps = [];
            mockFetch.mockImplementation(() => {
                timestamps.push(Date.now());
                if (timestamps.length < 2) {
                    return Promise.reject(new Error('Temp failure'));
                }
                return Promise.resolve({
                    ok: true,
                    json: async () => ({ id: 'repo1' })
                });
            });

            await repositoryService.loadRepository('repo1', {
                retryCount: 2,
                baseDelay: 50
            });

            const backoffTime = timestamps[1] - timestamps[0];
            expect(backoffTime).toBeGreaterThanOrEqual(50);
        });
    });

    describe('Cache Management', () => {
        it('should clear cache', () => {
            repositoryService.requestCache.set('repo1', { data: 'test' });
            repositoryService.clearCache();

            expect(repositoryService.requestCache.size).toBe(0);
        });

        it('should invalidate specific cache entry', () => {
            repositoryService.requestCache.set('repo1', { data: 'test' });
            repositoryService.requestCache.set('repo2', { data: 'test' });

            repositoryService.invalidateCache('repo1');

            expect(repositoryService.requestCache.has('repo1')).toBe(false);
            expect(repositoryService.requestCache.has('repo2')).toBe(true);
        });

        it('should get cache statistics', () => {
            repositoryService.requestCache.set('repo1', { data: 'test' });
            repositoryService.requestCache.set('repo2', { data: 'test' });

            const stats = repositoryService.getCacheStats();

            expect(stats.size).toBe(2);
            expect(stats.entries).toBeDefined();
        });
    });
});
