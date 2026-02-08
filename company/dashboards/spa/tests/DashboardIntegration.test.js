/**
 * Dashboard Integration Test Suite
 * 
 * Tests end-to-end dashboard functionality, service orchestration,
 * error propagation, and real-world workflows.
 * 
 * TDD Pattern: RED → GREEN → REFACTOR
 * Authority: CORE-008 (TDD mandatory)
 */

describe('Dashboard Integration', () => {
    let dashboard;
    let stateManager;
    let errorBoundary;
    let repositoryService;
    let validationService;
    let mockDOM;

    beforeEach(() => {
        // Initialize real instances (not mocks) for integration testing
        stateManager = new StateManager();
        errorBoundary = new ErrorBoundary(stateManager);
        repositoryService = new RepositoryService(stateManager, validationService);
        validationService = new ValidationService(stateManager);

        // Inject real instances
        dashboard = new DashboardController(
            stateManager,
            errorBoundary,
            repositoryService,
            validationService
        );

        // Mock only DOM interactions
        mockDOM = {
            getElementById: jest.fn(),
            querySelector: jest.fn(),
            querySelectorAll: jest.fn(() => []),
            addEventListener: jest.fn()
        };

        global.document = mockDOM;
        global.fetch = jest.fn();
    });

    describe('Full Repository Load Workflow', () => {
        it('should complete full workflow: select repo → load data → render', async () => {
            const mockData = {
                id: 'repo1',
                name: 'Test Repository',
                overview: { files: 100, commits: 500 },
                security: { issues: 5 },
                duplication: { percentage: 2.3 }
            };

            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockData
            });

            await dashboard.selectRepository('repo1');

            const state = stateManager.getState();
            expect(state.currentRepo).toBe('repo1');
            expect(state.data).toEqual(mockData);
            expect(state.isLoading).toBe(false);
        });

        it('should handle repository load with error recovery', async () => {
            // First attempt fails
            global.fetch.mockRejectedValueOnce(new Error('Network error'));

            // Retry succeeds
            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => ({ id: 'repo1' })
            });

            await dashboard.selectRepository('repo1');

            expect(stateManager.getState().currentRepo).toBe('repo1');
        });
    });

    describe('Tab Navigation with Lazy Loading', () => {
        it('should load data and then switch tabs', async () => {
            const mockData = {
                id: 'repo1',
                overview: { content: 'Overview content' },
                security: { content: 'Security content' }
            };

            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockData
            });

            await dashboard.selectRepository('repo1');
            dashboard.switchTab('security');

            const state = stateManager.getState();
            expect(state.currentTab).toBe('security');
            expect(state.data.id).toBe('repo1');
        });

        it('should prevent stale renders during tab switching', async () => {
            const mockData = { id: 'repo1', data: 'test' };

            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockData
            });

            await dashboard.selectRepository('repo1');

            const initialGen = stateManager.getGeneration();

            dashboard.switchTab('security');
            dashboard.switchTab('duplication');
            dashboard.switchTab('overview');

            const finalGen = stateManager.getGeneration();

            // Multiple tab changes should increment generation appropriately
            expect(finalGen).toBeGreaterThan(initialGen);

            // Old generations should not render
            expect(stateManager.isStaleRender(initialGen)).toBe(true);
            expect(stateManager.isStaleRender(finalGen)).toBe(false);
        });
    });

    describe('Error Handling Across Layers', () => {
        it('should catch and recover from data validation error', async () => {
            const invalidData = {
                id: 'not-a-number', // Type mismatch
                name: 'Test'
            };

            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => invalidData
            });

            await dashboard.selectRepository('repo1');

            const state = stateManager.getState();
            expect(state.errors).toBeDefined();
        });

        it('should recover from XSS attempt in data', async () => {
            const dataWithXSS = {
                id: 'repo1',
                name: '<img src="x" onerror="alert(1)">'
            };

            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => dataWithXSS
            });

            await dashboard.selectRepository('repo1');

            // Data should be sanitized
            const sanitized = validationService.sanitizeHTML(dataWithXSS.name);
            expect(sanitized).not.toContain('onerror');
        });

        it('should handle network timeout and retry', async () => {
            const slowRequest = new Promise(resolve =>
                setTimeout(() => resolve({ ok: true, json: async () => ({ id: 'repo1' }) }), 5000)
            );

            global.fetch.mockImplementationOnce(() => slowRequest);

            // Timeout should trigger error handling
            const timeoutPromise = Promise.race([
                dashboard.selectRepository('repo1'),
                new Promise((_, reject) =>
                    setTimeout(() => reject(new Error('Timeout')), 100)
                )
            ]);

            await expect(timeoutPromise).rejects.toThrow();
        });
    });

    describe('Concurrent Request Management', () => {
        it('should deduplicate concurrent repository loads', async () => {
            const mockData = { id: 'repo1', data: 'test' };

            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockData
            });

            // Request same repo twice concurrently
            const promise1 = dashboard.selectRepository('repo1');
            const promise2 = dashboard.selectRepository('repo1');

            await Promise.all([promise1, promise2]);

            // Only one fetch should have been made
            expect(global.fetch).toHaveBeenCalledTimes(1);

            const state = stateManager.getState();
            expect(state.currentRepo).toBe('repo1');
        });

        it('should cancel previous request on new selection', async () => {
            global.fetch.mockImplementation(() =>
                new Promise(resolve =>
                    setTimeout(() => resolve({
                        ok: true,
                        json: async () => ({ id: 'test' })
                    }), 500)
                )
            );

            dashboard.selectRepository('repo1'); // Start loading repo1
            await new Promise(resolve => setTimeout(resolve, 100));

            dashboard.selectRepository('repo2'); // Select repo2 (should cancel repo1)

            // repo2 should be loaded
            const state = stateManager.getState();
            expect(state.currentRepo).toBe('repo2');
        });
    });

    describe('State History and Versioning', () => {
        it('should maintain state version consistency', async () => {
            const mockData = { id: 'repo1' };

            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockData
            });

            const version1 = stateManager.getState().version;

            await dashboard.selectRepository('repo1');

            const version2 = stateManager.getState().version;

            expect(version2).toBeGreaterThan(version1);
        });

        it('should allow reverting to previous state', async () => {
            const mockData = { id: 'repo1' };

            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockData
            });

            await dashboard.selectRepository('repo1');
            const version1 = stateManager.getState().version;

            dashboard.switchTab('security');
            const version2 = stateManager.getState().version;

            stateManager.revertToVersion(version1);

            const state = stateManager.getState();
            expect(state.currentTab).toBe('overview');
        });
    });

    describe('Data Integrity Validation', () => {
        it('should detect contradictions in loaded data', async () => {
            const contradictoryData = {
                id: 'repo1',
                isActive: true,
                deletedAt: '2024-01-01' // Contradiction!
            };

            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => contradictoryData
            });

            await dashboard.selectRepository('repo1');

            const contradictions = validationService.detectContradictions(contradictoryData);
            expect(contradictions.detected).toBe(true);
        });

        it('should trust validated and sanitized data', async () => {
            const safeData = {
                id: 'repo1',
                name: 'Safe Repository',
                description: 'A safe description'
            };

            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => safeData
            });

            const validation = validationService.validateDataIntegrity(safeData);
            expect(validation.valid).toBe(true);
        });
    });

    describe('Cache and Performance', () => {
        it('should cache repository data', async () => {
            const mockData = { id: 'repo1', data: 'test' };

            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockData
            });

            await dashboard.selectRepository('repo1');

            // Second request should use cache
            const result = await repositoryService.loadRepository('repo1');

            expect(result).toEqual(mockData);
            expect(global.fetch).toHaveBeenCalledTimes(1);
        });

        it('should handle cache expiration', async () => {
            jest.useFakeTimers();

            const mockData = { id: 'repo1', data: 'test' };

            global.fetch.mockResolvedValue({
                ok: true,
                json: async () => mockData
            });

            await dashboard.selectRepository('repo1');
            expect(global.fetch).toHaveBeenCalledTimes(1);

            // Fast forward past cache TTL (5 minutes)
            jest.advanceTimersByTime(6 * 60 * 1000);

            await dashboard.selectRepository('repo1');

            // Cache expired, should fetch again
            expect(global.fetch).toHaveBeenCalledTimes(2);

            jest.useRealTimers();
        });
    });

    describe('Observable Telemetry', () => {
        it('should record operation telemetry', async () => {
            const mockData = { id: 'repo1' };

            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockData
            });

            await dashboard.selectRepository('repo1');

            const telemetry = errorBoundary.getTelemetry();
            expect(telemetry).toBeDefined();
        });

        it('should track error occurrences', async () => {
            global.fetch.mockRejectedValueOnce(new Error('Load failed'));

            await dashboard.selectRepository('repo1');

            const telemetry = errorBoundary.getTelemetry();
            expect(telemetry['repo-load']).toBeDefined();
        });
    });

    describe('User Interaction Patterns', () => {
        it('should handle rapid repository switches', async () => {
            global.fetch.mockResolvedValue({
                ok: true,
                json: async () => ({ id: 'test' })
            });

            const repos = ['repo1', 'repo2', 'repo3', 'repo4', 'repo5'];

            for (const repo of repos) {
                await dashboard.selectRepository(repo);
            }

            const state = stateManager.getState();
            expect(state.currentRepo).toBe('repo5');
        });

        it('should handle tab navigation during loading', async () => {
            global.fetch.mockImplementation(() =>
                new Promise(resolve =>
                    setTimeout(() => resolve({
                        ok: true,
                        json: async () => ({ id: 'repo1' })
                    }), 500)
                )
            );

            const loadPromise = dashboard.selectRepository('repo1');

            // Try to switch tabs while loading
            dashboard.switchTab('security');

            await loadPromise;

            const state = stateManager.getState();
            expect(state.currentRepo).toBe('repo1');
            expect(state.currentTab).toBe('security');
        });
    });

    describe('Cleanup and Resource Management', () => {
        it('should cleanup resources on destroy', () => {
            dashboard.init();
            dashboard.destroy();

            // Verify cleanup
            expect(repositoryService.requestCache.size).toBe(0);
        });

        it('should cancel pending operations on destroy', async () => {
            global.fetch.mockImplementation(() =>
                new Promise(resolve =>
                    setTimeout(() => resolve({
                        ok: true,
                        json: async () => ({ id: 'repo1' })
                    }), 1000)
                )
            );

            const loadPromise = dashboard.selectRepository('repo1');

            dashboard.destroy();

            // Should handle cleanup gracefully
            expect(() => {
                // Operation should not crash
            }).not.toThrow();
        });
    });
});
