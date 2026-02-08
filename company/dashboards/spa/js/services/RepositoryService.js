/**
 * RepositoryService - Data Loading with Request Coordination
 * 
 * Addresses Critical Issues:
 * - Race conditions (request deduplication)
 * - No request cancellation
 * - No partial failure handling
 * 
 * Authority: violations.md § Concurrency Hazards
 * Audit: AC_START: AC-SPA-001-03
 */

class RepositoryService {
    constructor(errorBoundary) {
        this.errorBoundary = errorBoundary;
        this.inFlightRequests = new Map();
        this.abortControllers = new Map();
        this.embeddedData = new Map();
    }
    
    /**
     * Load repository data with request coordination
     * @param {String} repoName
     * @param {Object} options
     * @returns {Promise<Object>}
     */
    async loadRepository(repoName, options = {}) {
        const cacheKey = `repo_${repoName}`;
        
        // Check in-flight request (deduplication)
        if (this.inFlightRequests.has(cacheKey)) {
            return await this.inFlightRequests.get(cacheKey);
        }
        
        // Cancel old request for different repo
        this._cancelOldRequests(cacheKey);
        
        // Create abort controller
        const abortController = new AbortController();
        this.abortControllers.set(cacheKey, abortController);
        
        // Create request promise
        const requestPromise = this._loadRepositoryInternal(repoName, abortController.signal, options);
        this.inFlightRequests.set(cacheKey, requestPromise);
        
        try {
            const result = await requestPromise;
            return result;
        } finally {
            // Cleanup
            this.inFlightRequests.delete(cacheKey);
            this.abortControllers.delete(cacheKey);
        }
    }
    
    /**
     * Internal load implementation
     */
    async _loadRepositoryInternal(repoName, signal, options) {
        return await this.errorBoundary.wrap(
            `repository_${repoName}`,
            async () => {
                // Try embedded data first
                const embedded = this._getEmbeddedData(repoName);
                if (embedded) {
                    return embedded;
                }
                
                // Fetch from JSON file
                const url = `./data/${repoName}.json`;
                const response = await fetch(url, { signal });
                
                if (!response.ok) {
                    throw new Error(`Failed to load ${repoName}: ${response.status} ${response.statusText}`);
                }
                
                const data = await response.json();
                
                // Validate schema
                this._validateSchema(data, repoName);
                
                return data;
            },
            { repoName, url: `./data/${repoName}.json` }
        );
    }
    
    /**
     * Cancel old requests
     */
    _cancelOldRequests(exceptKey = null) {
        for (const [key, controller] of this.abortControllers.entries()) {
            if (key !== exceptKey) {
                controller.abort();
                this.abortControllers.delete(key);
                this.inFlightRequests.delete(key);
            }
        }
    }
    
    /**
     * Register embedded data (file:// protocol support)
     */
    registerEmbeddedData(repoName, data) {
        this.embeddedData.set(repoName, data);
    }
    
    /**
     * Get embedded data
     */
    _getEmbeddedData(repoName) {
        return this.embeddedData.get(repoName);
    }
    
    /**
     * Validate repository data schema
     */
    _validateSchema(data, repoName) {
        const required = [
            'metadata',
            'overview',
            'architecture',
            'quality',
            'security',
            'dependencies'
        ];
        
        const missing = required.filter(field => !data[field]);
        
        if (missing.length > 0) {
            throw new Error(
                `Invalid schema for ${repoName}: Missing fields: ${missing.join(', ')}`
            );
        }
        
        // Validate metadata
        if (!data.metadata.name || !data.metadata.health_score) {
            throw new Error(`Invalid metadata for ${repoName}`);
        }
    }
    
    /**
     * Load all repositories (parallel)
     */
    async loadAllRepositories(repoNames) {
        const results = await Promise.allSettled(
            repoNames.map(name => this.loadRepository(name))
        );
        
        const successful = [];
        const failed = [];
        
        results.forEach((result, index) => {
            if (result.status === 'fulfilled') {
                successful.push({ name: repoNames[index], data: result.value });
            } else {
                failed.push({ name: repoNames[index], error: result.reason });
            }
        });
        
        return { successful, failed };
    }
    
    /**
     * Prefetch repository
     */
    async prefetch(repoName) {
        return await this.loadRepository(repoName);
    }
    
    /**
     * Cancel all in-flight requests
     */
    cancelAll() {
        this._cancelOldRequests();
    }
    
    /**
     * Export diagnostics
     */
    exportDiagnostics() {
        return {
            inFlightCount: this.inFlightRequests.size,
            embeddedDataCount: this.embeddedData.size,
            inFlight: Array.from(this.inFlightRequests.keys()),
            embedded: Array.from(this.embeddedData.keys())
        };
    }
}

// AC_COMPLETE: AC-SPA-001-03 ✅ RepositoryService with request coordination
