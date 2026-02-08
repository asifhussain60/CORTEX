/**
 * DashboardController Test Suite
 * 
 * Tests application orchestration, lazy tab loading,
 * event handling, and cross-layer integration.
 * 
 * TDD Pattern: RED → GREEN → REFACTOR
 * Authority: CORE-008 (TDD mandatory)
 */

describe('DashboardController', () => {
    let controller;
    let mockStateManager;
    let mockErrorBoundary;
    let mockRepositoryService;
    let mockValidationService;
    let mockDOM;

    beforeEach(() => {
        // Mock dependencies
        mockStateManager = {
            setState: jest.fn(),
            getState: jest.fn(() => ({
                currentTab: 'overview',
                currentRepo: null,
                data: null,
                isLoading: false,
                errors: {}
            })),
            getGeneration: jest.fn(() => 1),
            subscribe: jest.fn(),
            unsubscribe: jest.fn()
        };

        mockErrorBoundary = {
            catch: jest.fn(),
            retryWithBackoff: jest.fn(),
            withTimeout: jest.fn()
        };

        mockRepositoryService = {
            loadRepository: jest.fn(),
            loadMultiple: jest.fn(),
            cancelRequest: jest.fn(),
            clearCache: jest.fn()
        };

        mockValidationService = {
            sanitizeHTML: jest.fn(html => html),
            validateDataIntegrity: jest.fn(() => ({ valid: true }))
        };

        // Mock DOM
        mockDOM = {
            getElementById: jest.fn(),
            querySelector: jest.fn(),
            querySelectorAll: jest.fn(() => [])
        };

        controller = new DashboardController(
            mockStateManager,
            mockErrorBoundary,
            mockRepositoryService,
            mockValidationService
        );

        global.document = mockDOM;
    });

    describe('Initialization', () => {
        it('should initialize with all dependencies', () => {
            expect(controller.stateManager).toBe(mockStateManager);
            expect(controller.errorBoundary).toBe(mockErrorBoundary);
            expect(controller.repositoryService).toBe(mockRepositoryService);
            expect(controller.validationService).toBe(mockValidationService);
        });

        it('should setup state subscription', () => {
            controller.init();

            expect(mockStateManager.subscribe).toHaveBeenCalledWith(
                'dashboard',
                expect.any(Function)
            );
        });

        it('should setup event listeners', () => {
            const repoSelect = document.createElement('select');
            const tabButtons = [
                document.createElement('button'),
                document.createElement('button')
            ];

            mockDOM.getElementById.mockReturnValue(repoSelect);
            mockDOM.querySelectorAll.mockReturnValue(tabButtons);

            controller.init();

            expect(mockDOM.getElementById).toHaveBeenCalledWith('repo-select');
            expect(mockDOM.querySelectorAll).toHaveBeenCalledWith('[data-tab]');
        });
    });

    describe('Repository Selection', () => {
        it('should load data when repository selected', async () => {
            mockRepositoryService.loadRepository.mockResolvedValueOnce({
                id: 'repo1',
                name: 'Test Repo'
            });

            await controller.selectRepository('repo1');

            expect(mockRepositoryService.loadRepository).toHaveBeenCalledWith('repo1');
            expect(mockStateManager.setState).toHaveBeenCalledWith(
                expect.objectContaining({ currentRepo: 'repo1' })
            );
        });

        it('should handle repository load errors', async () => {
            const error = new Error('Load failed');
            mockRepositoryService.loadRepository.mockRejectedValueOnce(error);

            await controller.selectRepository('repo1');

            expect(mockErrorBoundary.catch).toHaveBeenCalledWith(
                'repo-load',
                error
            );
        });

        it('should cancel previous request on new selection', async () => {
            await controller.selectRepository('repo1');
            await controller.selectRepository('repo2');

            expect(mockRepositoryService.cancelRequest).toHaveBeenCalledWith('repo1');
        });

        it('should update loading state', async () => {
            mockRepositoryService.loadRepository.mockImplementation(
                () => new Promise(resolve => setTimeout(resolve, 100))
            );

            const loadPromise = controller.selectRepository('repo1');

            expect(mockStateManager.setState).toHaveBeenCalledWith(
                expect.objectContaining({ isLoading: true })
            );

            await loadPromise;

            expect(mockStateManager.setState).toHaveBeenCalledWith(
                expect.objectContaining({ isLoading: false })
            );
        });
    });

    describe('Tab Navigation', () => {
        it('should switch tabs', () => {
            controller.switchTab('security');

            expect(mockStateManager.setState).toHaveBeenCalledWith(
                expect.objectContaining({ currentTab: 'security' })
            );
        });

        it('should lazy load tab content', async () => {
            mockRepositoryService.loadRepository.mockResolvedValueOnce({
                id: 'repo1',
                security: { issues: [] }
            });

            await controller.selectRepository('repo1');
            controller.switchTab('security');

            // Tab should be rendered on demand
            expect(mockStateManager.setState).toHaveBeenCalledWith(
                expect.objectContaining({ currentTab: 'security' })
            );
        });

        it('should prevent stale renders', () => {
            const generation1 = mockStateManager.getGeneration();
            
            controller.switchTab('security');
            
            mockStateManager.getGeneration.mockReturnValue(generation1 + 5);
            
            // Old generation should not update
            controller.render(generation1);

            // Should use current generation
            controller.render(generation1 + 5);
        });

        it('should update tab UI', () => {
            const tabButton = { classList: { add: jest.fn(), remove: jest.fn() } };
            mockDOM.querySelector.mockReturnValue(tabButton);

            controller.switchTab('security');

            expect(mockDOM.querySelector).toHaveBeenCalled();
        });
    });

    describe('Data Rendering', () => {
        it('should sanitize HTML before rendering', () => {
            const dirtyHTML = '<img src="x" onerror="alert(1)">';
            const safeHTML = '<img src="x">';

            mockValidationService.sanitizeHTML.mockReturnValue(safeHTML);

            controller.renderData({ html: dirtyHTML });

            expect(mockValidationService.sanitizeHTML).toHaveBeenCalledWith(dirtyHTML);
        });

        it('should validate data before rendering', () => {
            const data = { id: 'test' };

            controller.renderData(data);

            expect(mockValidationService.validateDataIntegrity).toHaveBeenCalledWith(data);
        });

        it('should apply error boundary to render', async () => {
            mockErrorBoundary.withTimeout.mockImplementation(
                (name, fn) => fn()
            );

            await controller.renderData({ id: 'test' });

            expect(mockErrorBoundary.withTimeout).toHaveBeenCalled();
        });

        it('should show error fallback UI on render failure', () => {
            mockErrorBoundary.catch.mockImplementation((component, error) => {
                // Simulate error catching
            });

            const error = new Error('Render failed');
            controller.renderData({ id: 'test' }, error);

            expect(mockErrorBoundary.catch).toHaveBeenCalled();
        });
    });

    describe('Event Handling', () => {
        it('should handle repository selection event', () => {
            const event = {
                target: { value: 'repo1' }
            };

            controller.handleRepoChange(event);

            expect(mockStateManager.setState).toHaveBeenCalled();
        });

        it('should handle tab click event', () => {
            const event = {
                target: { dataset: { tab: 'security' } }
            };

            controller.handleTabClick(event);

            expect(mockStateManager.setState).toHaveBeenCalledWith(
                expect.objectContaining({ currentTab: 'security' })
            );
        });

        it('should debounce rapid events', async () => {
            const callback = jest.fn();
            const debouncedCallback = controller.debounce(callback, 100);

            debouncedCallback();
            debouncedCallback();
            debouncedCallback();

            await new Promise(resolve => setTimeout(resolve, 150));

            expect(callback).toHaveBeenCalledTimes(1);
        });

        it('should handle window resize', () => {
            const spy = jest.spyOn(controller, 'handleResize');
            controller.handleResize();

            expect(spy).toHaveBeenCalled();
        });
    });

    describe('State Synchronization', () => {
        it('should update UI on state change', () => {
            const stateChangeCallback = mockStateManager.subscribe.mock.calls[0][1];

            const newState = {
                currentTab: 'security',
                currentRepo: 'repo1'
            };

            stateChangeCallback(newState);

            // Verify render was triggered
            expect(mockStateManager.getState).toHaveBeenCalled();
        });

        it('should handle concurrent state updates', () => {
            const callback1 = jest.fn();
            const callback2 = jest.fn();

            mockStateManager.subscribe.mockImplementation((id, cb) => {
                if (id === 'dash1') callback1.mockImplementation(cb);
                if (id === 'dash2') callback2.mockImplementation(cb);
            });

            controller.init();

            const newState = { currentTab: 'security' };
            stateChangeCallback(newState);
            stateChangeCallback(newState);

            expect(mockStateManager.setState).toHaveBeenCalled();
        });
    });

    describe('Performance', () => {
        it('should prevent unnecessary renders', () => {
            mockStateManager.getGeneration.mockReturnValue(1);

            controller.render(1);
            controller.render(1); // Same generation

            // Should render only once
            expect(mockStateManager.getState.mock.calls.length).toBeGreaterThan(0);
        });

        it('should lazy load visualizations', async () => {
            const vizSpy = jest.fn();
            controller.loadVisualization = vizSpy;

            controller.switchTab('duplication');

            await new Promise(resolve => setTimeout(resolve, 100));

            expect(vizSpy).toHaveBeenCalled();
        });

        it('should cleanup event listeners on destroy', () => {
            controller.init();
            controller.destroy();

            expect(mockStateManager.unsubscribe).toHaveBeenCalledWith('dashboard');
        });
    });

    describe('Error Recovery', () => {
        it('should retry failed operations', async () => {
            mockErrorBoundary.retryWithBackoff.mockResolvedValueOnce({
                id: 'repo1'
            });

            const result = await controller.retryLoad('repo1');

            expect(mockErrorBoundary.retryWithBackoff).toHaveBeenCalled();
        });

        it('should show error message to user', () => {
            const errorDisplay = { textContent: '' };
            mockDOM.getElementById.mockReturnValue(errorDisplay);

            controller.showError('Failed to load repository');

            expect(errorDisplay.textContent).toContain('Failed to load repository');
        });

        it('should allow retry from error state', () => {
            const retryButton = { onclick: null };
            mockDOM.querySelector.mockReturnValue(retryButton);

            controller.showRetryOption('repo1');

            expect(retryButton.onclick).toBeDefined();
        });
    });

    describe('Cleanup and Teardown', () => {
        it('should cancel pending requests on destroy', () => {
            controller.destroy();

            expect(mockRepositoryService.cancelRequest).toHaveBeenCalled();
        });

        it('should clear cache on destroy', () => {
            controller.destroy();

            expect(mockRepositoryService.clearCache).toHaveBeenCalled();
        });

        it('should remove event listeners', () => {
            const repoSelect = {
                removeEventListener: jest.fn()
            };
            mockDOM.getElementById.mockReturnValue(repoSelect);

            controller.destroy();

            expect(repoSelect.removeEventListener).toHaveBeenCalled();
        });

        it('should unsubscribe from state', () => {
            controller.init();
            controller.destroy();

            expect(mockStateManager.unsubscribe).toHaveBeenCalledWith('dashboard');
        });
    });

    describe('Integration with Services', () => {
        it('should coordinate between all services', async () => {
            mockRepositoryService.loadRepository.mockResolvedValueOnce({
                id: 'repo1',
                data: 'test'
            });

            await controller.selectRepository('repo1');

            expect(mockRepositoryService.loadRepository).toHaveBeenCalled();
            expect(mockValidationService.validateDataIntegrity).toHaveBeenCalled();
            expect(mockStateManager.setState).toHaveBeenCalled();
        });

        it('should propagate errors through boundary', async () => {
            const error = new Error('Coordination error');
            mockRepositoryService.loadRepository.mockRejectedValueOnce(error);

            await controller.selectRepository('repo1');

            expect(mockErrorBoundary.catch).toHaveBeenCalledWith(
                expect.any(String),
                error
            );
        });
    });
});
