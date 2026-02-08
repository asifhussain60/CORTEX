/**
 * RepositoryService - Data Loading with Request Coordination
 * 
 * Addresses Critical Issues:
 * - Race conditions (request deduplication)
 * - No request cancellation
 * - No partial failure handling
 * - GPR-001: file:// protocol fetch failures
 * 
 * Authority: violations.md § Concurrency Hazards + GPR Recommendation
 * Audit: AC_START: AC-SPA-001-03 (EXTENDED)
 */

class RepositoryService {
    constructor(errorBoundary) {
        this.errorBoundary = errorBoundary;
        this.inFlightRequests = new Map();
        this.abortControllers = new Map();
        this.embeddedData = new Map();
        this.deploymentMode = DeploymentMode;  // GPR-001 FIX
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
     * GPR-001 FIX: Check deployment mode before attempting fetch()
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
                
                // GPR-001: Check if fetch is allowed in deployment mode
                const mode = this.deploymentMode.getConfig();
                if (!mode.canFetch) {
                    const msg = `[${mode.mode}] Cannot fetch ${repoName}. Must use embedded data. ${mode.warningMessage}`;
                    console.warn(msg);
                    throw new Error(msg);
                }
                
                // Fetch from JSON file - try multiple paths
                let url = `./data/${repoName}.json`;
                let response = await fetch(url, { signal });
                
                // If not found in data/, try repos/ directory (new location)
                if (!response.ok && response.status === 404) {
                    url = `../repos/${repoName}/dashboard-data.json`;
                    response = await fetch(url, { signal });
                }
                
                if (!response.ok) {
                    throw new Error(`Failed to load ${repoName}: ${response.status} ${response.statusText}`);
                }
                
                const data = await response.json();
                
                // Transform schema if needed (new format → old format)
                const transformedData = this._transformSchema(data);
                
                // Validate schema
                this._validateSchema(transformedData, repoName);
                
                return transformedData;
            },
            { repoName, url: `./data/${repoName}.json`, deploymentMode: this.deploymentMode.getConfig().mode }
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
        const data = this.embeddedData.get(repoName);
        return data ? this._transformSchema(data) : data;
    }
    
    /**
     * Transform new schema format to expected format
     * New: {repo, overview, metrics, security, dependencies, quality, use_cases}
     * Old: {metadata, overview, architecture, quality, security, dependencies}
     */
    _transformSchema(data) {
        // If already in old format, return as-is
        if (data.metadata) {
            return data;
        }
        
        // Transform new format to old format
        return {
            metadata: {
                name: data.repo?.display_name || data.repo?.slug || 'Unknown',
                slug: data.repo?.slug || 'unknown',
                description: data.repo?.description || '',
                owner: data.repo?.owner || 'Unknown',
                primary_language: data.repo?.primary_language || 'Unknown',
                version: data.repo?.version || '1.0',
                last_analyzed_at: data.repo?.last_analyzed_at || new Date().toISOString(),
                health_score: data.metrics?.health_score || 0,
                risk_score: data.metrics?.risk_score || 0,
                loc: data.metrics?.loc || 0,
                files: data.metrics?.files || 0,
                languages: data.metrics?.languages || {}
            },
            overview: data.overview || {},
            architecture: {
                languages: data.metrics?.languages || {},
                patterns: [],
                files: data.metrics?.files || 0
            },
            quality: data.quality || {},
            security: data.security || {},
            dependencies: data.dependencies || {},
            use_cases: data.use_cases || []
        };
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
            embedded: Array.from(this.embeddedData.keys()),
            deploymentMode: this.deploymentMode.getConfig()
        };
    }
}

// AC_COMPLETE: AC-SPA-001-03 ✅ RepositoryService with GPR-001 deployment mode awareness
