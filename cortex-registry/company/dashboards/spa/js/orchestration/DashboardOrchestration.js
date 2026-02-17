/**
 * CORTEX Dashboard Orchestration Specification
 * 
 * Defines formalized service contracts, orchestration patterns,
 * dependency injection container, and error propagation.
 * 
 * Authority: MCP-FIRST Architecture, SOLID Principles
 * Version: 2.0 (Refactored with TDD)
 */

/**
 * Service Container - Dependency Injection Implementation
 * 
 * Provides:
 * - Centralized service registration
 * - Lazy initialization
 * - Circular dependency detection
 * - Service discovery
 */
class ServiceContainer {
    constructor() {
        this.services = new Map();
        this.singletons = new Map();
        this.factories = new Map();
        this.dependencies = new Map();
        this._initializing = new Set();
    }

    /**
     * Register a singleton service
     * @param {string} name - Service name
     * @param {Function|Object} definition - Service class or factory
     * @param {string[]} dependencies - Service dependencies
     */
    registerSingleton(name, definition, dependencies = []) {
        this.services.set(name, { definition, dependencies, isSingleton: true });
        this.dependencies.set(name, dependencies);
    }

    /**
     * Register a factory service (new instance each time)
     * @param {string} name - Service name
     * @param {Function} factory - Factory function
     * @param {string[]} dependencies - Service dependencies
     */
    registerFactory(name, factory, dependencies = []) {
        this.factories.set(name, { factory, dependencies });
        this.dependencies.set(name, dependencies);
    }

    /**
     * Get service instance with dependency resolution
     * @param {string} name - Service name
     * @returns {Object} Service instance
     */
    get(name) {
        // Circular dependency detection
        if (this._initializing.has(name)) {
            throw new Error(`Circular dependency detected: ${name}`);
        }

        // Check singleton cache
        if (this.singletons.has(name)) {
            return this.singletons.get(name);
        }

        const serviceDefinition = this.services.get(name);
        if (!serviceDefinition) {
            throw new Error(`Service not found: ${name}`);
        }

        this._initializing.add(name);

        try {
            // Resolve dependencies
            const dependencies = serviceDefinition.dependencies.map(dep => this.get(dep));

            // Create instance
            const instance = serviceDefinition.isSingleton
                ? new serviceDefinition.definition(...dependencies)
                : new serviceDefinition.definition(...dependencies);

            // Cache if singleton
            if (serviceDefinition.isSingleton) {
                this.singletons.set(name, instance);
            }

            return instance;
        } finally {
            this._initializing.delete(name);
        }
    }

    /**
     * Get all available services
     * @returns {Array} List of service names
     */
    getServiceNames() {
        return Array.from(this.services.keys());
    }

    /**
     * Get dependency graph for service
     * @param {string} name - Service name
     * @returns {Object} Dependency information
     */
    getDependencies(name) {
        return {
            direct: this.dependencies.get(name) || [],
            transitive: this._getTransitiveDeps(name)
        };
    }

    _getTransitiveDeps(name, visited = new Set()) {
        if (visited.has(name)) return [];

        visited.add(name);
        const direct = this.dependencies.get(name) || [];
        const transitive = [];

        direct.forEach(dep => {
            transitive.push(...this._getTransitiveDeps(dep, visited));
        });

        return [...direct, ...transitive];
    }
}

/**
 * Orchestration Layer - Coordinates service interactions
 * 
 * Responsibilities:
 * - Route user actions to appropriate services
 * - Coordinate state transitions
 * - Handle error propagation
 * - Manage loading states
 */
class DashboardOrchestrator {
    constructor(container) {
        this.container = container;
        this.stateManager = container.get('stateManager');
        this.errorBoundary = container.get('errorBoundary');
        this.repositoryService = container.get('repositoryService');
        this.validationService = container.get('validationService');
    }

    /**
     * Orchestrate repository selection workflow
     * @param {string} repoId - Repository ID
     * @returns {Promise<Object>} Repository data
     */
    async selectRepository(repoId) {
        try {
            // 1. Update loading state
            this.stateManager.setState({ isLoading: true, currentRepo: repoId });

            // 2. Load with error boundary and timeout
            const data = await this.errorBoundary.withTimeout(
                'repo-load',
                () => this.repositoryService.loadRepository(repoId),
                30000 // 30s timeout
            );

            // 3. Validate loaded data
            const validation = this.validationService.validateDataIntegrity(data);
            if (!validation.valid) {
                throw new Error(`Data validation failed: ${validation.errors.join(', ')}`);
            }

            // 4. Detect contradictions
            const contradictions = this.validationService.detectContradictions(data);
            if (contradictions.detected && contradictions.confidence > 0.85) {
                console.warn('Data contradictions detected:', contradictions);
            }

            // 5. Update state with validated data
            this.stateManager.setState({
                currentRepo: repoId,
                data: data,
                isLoading: false,
                errors: {}
            });

            return data;
        } catch (error) {
            // 6. Error handling and recovery
            this.errorBoundary.catch('repository-selection', error);
            this.stateManager.setState({
                isLoading: false,
                errors: { 'repository-selection': error.message }
            });

            // 7. Attempt retry with backoff
            return this.errorBoundary.retryWithBackoff(
                'repository-selection-retry',
                () => this.repositoryService.loadRepository(repoId),
                { maxRetries: 3, baseDelay: 1000 }
            );
        }
    }

    /**
     * Orchestrate tab navigation workflow
     * @param {string} tabName - Tab identifier
     */
    switchTab(tabName) {
        try {
            // 1. Validate tab exists
            const validTabs = ['overview', 'security', 'duplication', 'complexity'];
            if (!validTabs.includes(tabName)) {
                throw new Error(`Invalid tab: ${tabName}`);
            }

            // 2. Get current state for stale render check
            const currentGeneration = this.stateManager.getGeneration();

            // 3. Update state
            this.stateManager.setState({ currentTab: tabName });

            // 4. Return generation for stale render detection
            return currentGeneration;
        } catch (error) {
            this.errorBoundary.catch('tab-navigation', error);
            throw error;
        }
    }

    /**
     * Orchestrate data rendering workflow
     * @param {Object} data - Data to render
     * @param {Number} generation - State generation for stale render detection
     */
    async renderData(data, generation) {
        try {
            // 1. Check for stale renders
            if (this.stateManager.isStaleRender(generation)) {
                console.warn('Stale render prevented:', generation);
                return;
            }

            // 2. Validate data
            const validation = this.validationService.validateDataIntegrity(data);
            if (!validation.valid) {
                throw new Error('Render data validation failed');
            }

            // 3. Sanitize sensitive content
            const sanitized = this.validationService.sanitizeObject(data);

            // 4. Apply error boundary during render
            const result = await this.errorBoundary.withTimeout(
                'data-render',
                () => this._performRender(sanitized),
                5000
            );

            return result;
        } catch (error) {
            this.errorBoundary.catch('data-render', error);
            throw error;
        }
    }

    _performRender(data) {
        // Actual rendering implementation
        return Promise.resolve(data);
    }

    /**
     * Get orchestration metrics
     * @returns {Object} Metrics data
     */
    getMetrics() {
        return {
            stateVersion: this.stateManager.getState().version,
            generation: this.stateManager.getGeneration(),
            errorCount: Object.keys(this.stateManager.getState().errors).length,
            cacheStats: this.repositoryService.getCacheStats(),
            telemetry: this.errorBoundary.getTelemetry()
        };
    }
}

/**
 * Service Contract Definitions
 * 
 * Formal specifications for service interfaces
 */
const ServiceContracts = {
    StateManager: {
        methods: [
            'getState()',
            'setState(changes)',
            'getGeneration()',
            'isStaleRender(generation)',
            'setCache(key, value, ttl)',
            'getCache(key)',
            'subscribe(id, callback)',
            'unsubscribe(id)',
            'getHistory()',
            'revertToVersion(version)'
        ],
        guarantees: [
            'State is frozen (immutable)',
            'State versions increment monotonically',
            'Generation increments on every mutation',
            'Cache respects TTL',
            'Subscribers notified atomically',
            'History limited to 50 items'
        ]
    },

    ErrorBoundary: {
        methods: [
            'catch(component, error)',
            'retryWithBackoff(name, task, options)',
            'withTimeout(name, task, ms)',
            'getFallbackUI(component, error)',
            'recover(component)',
            'recoverAll()',
            'getTelemetry()',
            'clearTelemetry()'
        ],
        guarantees: [
            'Errors caught and logged',
            'Retries use exponential backoff',
            'Operations timeout after specified duration',
            'Fallback UI provided on failure',
            'Error context preserved',
            'Telemetry persisted to localStorage'
        ]
    },

    RepositoryService: {
        methods: [
            'loadRepository(id)',
            'loadMultiple(ids)',
            'cancelRequest(id)',
            'cancelAllRequests()',
            'clearCache()',
            'invalidateCache(id)',
            'getCacheStats()'
        ],
        guarantees: [
            'Concurrent requests deduplicated',
            'Requests cancellable via AbortController',
            'Cache respects 5 minute TTL',
            'Embedded data support (file://)',
            'Request validation before response',
            'Parallel loading with Promise.allSettled'
        ]
    },

    ValidationService: {
        methods: [
            'sanitizeHTML(html)',
            'validateDataIntegrity(data)',
            'detectContradictions(data)',
            'validateSchema(data, schema)',
            'enforceRenderTrust(data)',
            'sanitizeObject(obj)',
            'sanitizeBatch(values)'
        ],
        guarantees: [
            'XSS prevention via HTML sanitization',
            'Type validation on all inputs',
            'Contradiction detection with confidence',
            'Schema validation support',
            'Trust boundaries enforced',
            'Batch operations optimized'
        ]
    },

    DashboardController: {
        methods: [
            'selectRepository(id)',
            'switchTab(name)',
            'renderData(data)',
            'handleRepoChange(event)',
            'handleTabClick(event)',
            'init()',
            'destroy()'
        ],
        guarantees: [
            'Coordinates all service interactions',
            'Prevents stale renders',
            'Propagates errors through boundary',
            'Lazy loads tab content',
            'Cleans up resources on destroy',
            'Maintains SOLID principles'
        ]
    }
};

/**
 * Bootstrap Function - Initialize Orchestration
 * @returns {Object} Initialized system
 */
function initializeDashboard() {
    // Create DI container
    const container = new ServiceContainer();

    // Register services
    container.registerSingleton('stateManager', StateManager, []);
    container.registerSingleton('errorBoundary', ErrorBoundary, ['stateManager']);
    container.registerSingleton('validationService', ValidationService, ['stateManager']);
    container.registerSingleton('repositoryService', RepositoryService, [
        'stateManager',
        'validationService'
    ]);
    container.registerSingleton('controller', DashboardController, [
        'stateManager',
        'errorBoundary',
        'repositoryService',
        'validationService'
    ]);
    container.registerSingleton('orchestrator', DashboardOrchestrator, ['container']);

    // Get instances
    const controller = container.get('controller');
    const orchestrator = container.get('orchestrator');

    return {
        controller,
        orchestrator,
        container,
        services: ServiceContracts
    };
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        ServiceContainer,
        DashboardOrchestrator,
        ServiceContracts,
        initializeDashboard
    };
}
