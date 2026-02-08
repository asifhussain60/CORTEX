/**
 * DashboardDataLoader.js
 * Robust data loading with validation, sanitization, and fallback handling
 * 
 * Purpose: Fail-fast data pipeline with schema validation
 * Author: Asif Hussain
 * Date: 2026-02-08
 * Authority: Dashboard Fix - Phase 53 (NEW)
 */

class DashboardDataLoader {
    constructor(logger) {
        this.logger = logger || console;
        this.data = null;
        this.source = null;
        this.loadTime = null;
        this.listeners = {
            'load:success': [],
            'load:error': [],
            'load:timeout': []
        };
        
        console.log('📥 [DataLoader] Initialized');
    }
    
    /**
     * Add event listener
     * @param {string} event - Event name (load:success|load:error|load:timeout)
     * @param {Function} callback - Callback function
     */
    on(event, callback) {
        if (this.listeners[event]) {
            this.listeners[event].push(callback);
        }
    }
    
    /**
     * Emit event to listeners
     * @param {string} event - Event name
     * @param {*} data - Event data
     */
    _emit(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(cb => cb(data));
        }
    }
    
    /**
     * Load dashboard data with fallback strategy
     * Priority: Embedded → HTTP → Error State
     * @param {Object} options - Load options
     * @returns {Promise<Object>} Dashboard data
     */
    async loadWithFallback(options = {}) {
        const {
            embeddedDataId = 'dashboard-data',
            httpEndpoint = null,
            timeout = 5000
        } = options;
        
        const startTime = performance.now();
        
        try {
            // Strategy 1: Try embedded data
            console.log('📦 [DataLoader] Attempting embedded data load...');
            const embedded = this._loadEmbedded(embeddedDataId);
            
            if (embedded) {
                this.data = embedded;
                this.source = 'embedded';
                this.loadTime = performance.now() - startTime;
                
                this.logger.logDataLoad && this.logger.logDataLoad(this.data, this.source, this.loadTime);
                this._emit('load:success', { data: this.data, source: this.source });
                
                console.log('✅ [DataLoader] Embedded data loaded:', this.loadTime.toFixed(2), 'ms');
                return this.data;
            }
            
            // Strategy 2: Try HTTP fetch
            if (httpEndpoint) {
                console.log('🌐 [DataLoader] Attempting HTTP fetch...');
                const http = await this._loadHTTP(httpEndpoint, timeout);
                
                if (http) {
                    this.data = http;
                    this.source = 'http';
                    this.loadTime = performance.now() - startTime;
                    
                    this.logger.logDataLoad && this.logger.logDataLoad(this.data, this.source, this.loadTime);
                    this._emit('load:success', { data: this.data, source: this.source });
                    
                    console.log('✅ [DataLoader] HTTP data loaded:', this.loadTime.toFixed(2), 'ms');
                    return this.data;
                }
            }
            
            // Strategy 3: Error state
            throw new Error('No data source available (embedded and HTTP failed)');
            
        } catch (error) {
            this.loadTime = performance.now() - startTime;
            this.logger.logError && this.logger.logError('data-loader', error, { loadTime: this.loadTime });
            this._emit('load:error', { error, loadTime: this.loadTime });
            
            console.error('❌ [DataLoader] Load failed:', error.message);
            throw error;
        }
    }
    
    /**
     * Load embedded data from script tag
     * @param {string} elementId - Script element ID
     * @returns {Object|null} Parsed data or null
     */
    _loadEmbedded(elementId) {
        const el = document.getElementById(elementId);
        
        if (!el || !el.textContent.trim()) {
            console.warn('⚠️ [DataLoader] No embedded data found');
            return null;
        }
        
        try {
            const raw = el.textContent.trim();
            
            // Empty object check
            if (raw === '{}') {
                console.warn('⚠️ [DataLoader] Embedded data is empty object');
                return null;
            }
            
            const data = JSON.parse(raw);
            
            // Validate not empty
            if (!data || Object.keys(data).length === 0) {
                console.warn('⚠️ [DataLoader] Embedded data is empty');
                return null;
            }
            
            // Validate schema
            const validation = this.validateJSON(data);
            if (!validation.valid) {
                console.error('❌ [DataLoader] Schema validation failed:', validation.errors);
                return null;
            }
            
            // Sanitize data
            return this.sanitizeData(data);
            
        } catch (error) {
            console.error('❌ [DataLoader] Failed to parse embedded data:', error);
            return null;
        }
    }
    
    /**
     * Load data via HTTP fetch
     * @param {string} url - Data URL
     * @param {number} timeout - Timeout in ms
     * @returns {Promise<Object|null>} Parsed data or null
     */
    async _loadHTTP(url, timeout) {
        return new Promise((resolve, reject) => {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => {
                controller.abort();
                this._emit('load:timeout', { url, timeout });
                reject(new Error(`HTTP fetch timeout after ${timeout}ms`));
            }, timeout);
            
            fetch(url, { signal: controller.signal })
                .then(response => {
                    clearTimeout(timeoutId);
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    return response.json();
                })
                .then(data => {
                    const validation = this.validateJSON(data);
                    if (!validation.valid) {
                        throw new Error(`Schema validation failed: ${validation.errors.join(', ')}`);
                    }
                    
                    resolve(this.sanitizeData(data));
                })
                .catch(error => {
                    clearTimeout(timeoutId);
                    
                    if (error.name === 'AbortError') {
                        console.error('❌ [DataLoader] HTTP timeout');
                    } else {
                        console.error('❌ [DataLoader] HTTP fetch failed:', error);
                    }
                    
                    resolve(null);
                });
        });
    }
    
    /**
     * Validate JSON against schema
     * @param {Object} data - Data to validate
     * @returns {Object} Validation result
     */
    validateJSON(data) {
        const errors = [];
        
        // Required fields
        if (!data.repository_name) errors.push('Missing: repository_name');
        if (!data.overview) errors.push('Missing: overview');
        if (!data.metrics) errors.push('Missing: metrics');
        
        // Type checks
        if (data.overview && typeof data.overview !== 'object') {
            errors.push('Invalid type: overview must be object');
        }
        if (data.metrics && typeof data.metrics !== 'object') {
            errors.push('Invalid type: metrics must be object');
        }
        
        return {
            valid: errors.length === 0,
            errors
        };
    }
    
    /**
     * Sanitize data (clean nulls, undefined, malformed)
     * @param {Object} data - Data to sanitize
     * @returns {Object} Sanitized data
     */
    sanitizeData(data) {
        const sanitized = JSON.parse(JSON.stringify(data, (key, value) => {
            // Replace null/undefined with appropriate defaults
            if (value === null || value === undefined) {
                return typeof value === 'number' ? 0 : '';
            }
            return value;
        }));
        
        console.log('🧹 [DataLoader] Data sanitized');
        return sanitized;
    }
    
    /**
     * Get loaded data
     * @returns {Object|null} Loaded data
     */
    getData() {
        return this.data;
    }
    
    /**
     * Get load metadata
     * @returns {Object} Load metadata
     */
    getMetadata() {
        return {
            source: this.source,
            loadTime: this.loadTime,
            size: this.data ? JSON.stringify(this.data).length : 0,
            loaded: !!this.data
        };
    }
}

// Export for use in dashboard
window.DashboardDataLoader = DashboardDataLoader;
