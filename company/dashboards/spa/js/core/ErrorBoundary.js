/**
 * ErrorBoundary - Component-Level Error Handling with Fallback UI
 * 
 * Addresses Critical Issues:
 * - No error boundaries (white screen on failures)
 * - No retry logic (permanent failures)
 * - No partial failure handling
 * 
 * Authority: violations.md § Error Handling Vacuum
 * Audit: AC_START: AC-SPA-001-02
 */

class ErrorBoundary {
    constructor(options = {}) {
        this.options = {
            maxRetries: options.maxRetries || 3,
            retryDelay: options.retryDelay || 1000,
            timeout: options.timeout || 5000,
            fallbackUI: options.fallbackUI || this._defaultFallbackUI.bind(this),
            onError: options.onError || console.error,
            telemetry: options.telemetry || this._defaultTelemetry.bind(this)
        };
        
        this.errors = new Map();
        this.retryAttempts = new Map();
    }
    
    /**
     * Wrap async function with error boundary
     * @param {String} componentId - Component identifier
     * @param {Function} fn - Async function to wrap
     * @param {Object} context - Context for fallback
     * @returns {Promise}
     */
    async wrap(componentId, fn, context = {}) {
        const startTime = Date.now();
        
        try {
            // Set timeout
            const result = await Promise.race([
                fn(),
                this._timeout(this.options.timeout, componentId)
            ]);
            
            // Clear error on success
            this.clearError(componentId);
            
            // Log success telemetry
            this._logTelemetry(componentId, 'success', Date.now() - startTime);
            
            return result;
            
        } catch (error) {
            return await this._handleError(componentId, error, fn, context, startTime);
        }
    }
    
    /**
     * Wrap sync function with try-catch
     * @param {String} componentId
     * @param {Function} fn
     * @param {Object} context
     * @returns {*}
     */
    wrapSync(componentId, fn, context = {}) {
        try {
            const result = fn();
            this.clearError(componentId);
            return result;
        } catch (error) {
            this._recordError(componentId, error);
            this.options.onError(error, componentId);
            this._logTelemetry(componentId, 'error', 0, error);
            return this._renderFallback(componentId, error, context);
        }
    }
    
    /**
     * Handle error with retry logic
     */
    async _handleError(componentId, error, fn, context, startTime) {
        this._recordError(componentId, error);
        
        const attempts = this.retryAttempts.get(componentId) || 0;
        
        // Check if should retry
        if (this._shouldRetry(error) && attempts < this.options.maxRetries) {
            this.retryAttempts.set(componentId, attempts + 1);
            
            // Wait before retry (exponential backoff)
            const delay = this.options.retryDelay * Math.pow(2, attempts);
            await this._sleep(delay);
            
            // Retry
            this._logTelemetry(componentId, 'retry', Date.now() - startTime, error);
            return await this.wrap(componentId, fn, context);
            
        } else {
            // Max retries exceeded or non-retriable error
            this.retryAttempts.delete(componentId);
            this.options.onError(error, componentId);
            this._logTelemetry(componentId, 'error', Date.now() - startTime, error);
            
            return this._renderFallback(componentId, error, context);
        }
    }
    
    /**
     * Check if error is retriable
     */
    _shouldRetry(error) {
        // Network errors are retriable
        if (error.name === 'NetworkError' || error.name === 'TypeError') {
            return true;
        }
        
        // Timeout errors are retriable
        if (error.message && error.message.includes('timeout')) {
            return true;
        }
        
        // HTTP 5xx errors are retriable
        if (error.status && error.status >= 500) {
            return true;
        }
        
        return false;
    }
    
    /**
     * Render fallback UI
     */
    _renderFallback(componentId, error, context) {
        const fallbackHTML = this.options.fallbackUI(componentId, error, context);
        
        // Find component container
        const container = document.getElementById(componentId) || 
                         document.querySelector(`[data-component="${componentId}"]`);
        
        if (container) {
            container.innerHTML = fallbackHTML;
            container.classList.add('error-boundary-fallback');
        }
        
        return null;
    }
    
    /**
     * Default fallback UI
     */
    _defaultFallbackUI(componentId, error, context) {
        const attempts = this.retryAttempts.get(componentId) || 0;
        
        return `
            <div class="error-boundary-content">
                <div class="error-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <h3 class="error-title">Component Error</h3>
                <p class="error-message">${this._sanitizeError(error.message)}</p>
                <div class="error-details">
                    <div><strong>Component:</strong> ${componentId}</div>
                    <div><strong>Attempts:</strong> ${attempts}/${this.options.maxRetries}</div>
                    <div><strong>Time:</strong> ${new Date().toLocaleTimeString()}</div>
                </div>
                <button onclick="location.reload()" class="btn-retry">
                    <i class="fas fa-redo"></i> Reload Dashboard
                </button>
            </div>
        `;
    }
    
    /**
     * Sanitize error message (prevent XSS)
     */
    _sanitizeError(message) {
        const div = document.createElement('div');
        div.textContent = message || 'Unknown error';
        return div.innerHTML;
    }
    
    /**
     * Record error
     */
    _recordError(componentId, error) {
        this.errors.set(componentId, {
            error,
            timestamp: Date.now(),
            attempts: this.retryAttempts.get(componentId) || 0
        });
    }
    
    /**
     * Clear error
     */
    clearError(componentId) {
        this.errors.delete(componentId);
        this.retryAttempts.delete(componentId);
    }
    
    /**
     * Get error for component
     */
    getError(componentId) {
        return this.errors.get(componentId);
    }
    
    /**
     * Check if component has error
     */
    hasError(componentId) {
        return this.errors.has(componentId);
    }
    
    /**
     * Timeout promise
     */
    _timeout(ms, componentId) {
        return new Promise((_, reject) => {
            setTimeout(() => {
                const error = new Error(`Timeout: ${componentId} exceeded ${ms}ms`);
                error.name = 'TimeoutError';
                reject(error);
            }, ms);
        });
    }
    
    /**
     * Sleep utility
     */
    _sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    /**
     * Default telemetry (localStorage)
     */
    _defaultTelemetry(event) {
        try {
            const key = 'cortex_dashboard_telemetry';
            const data = JSON.parse(localStorage.getItem(key) || '[]');
            data.push(event);
            
            // Keep last 100 events
            if (data.length > 100) {
                data.shift();
            }
            
            localStorage.setItem(key, JSON.stringify(data));
        } catch (e) {
            // Ignore localStorage errors
        }
    }
    
    /**
     * Log telemetry event
     */
    _logTelemetry(componentId, type, duration, error = null) {
        this.options.telemetry({
            componentId,
            type,
            duration,
            timestamp: Date.now(),
            error: error ? {
                name: error.name,
                message: error.message,
                stack: error.stack
            } : null
        });
    }
    
    /**
     * Export diagnostics
     */
    exportDiagnostics() {
        return {
            errorCount: this.errors.size,
            errors: Array.from(this.errors.entries()).map(([id, data]) => ({
                componentId: id,
                error: data.error.message,
                timestamp: data.timestamp,
                attempts: data.attempts
            })),
            telemetry: this._getTelemetry()
        };
    }
    
    /**
     * Get telemetry data
     */
    _getTelemetry() {
        try {
            return JSON.parse(localStorage.getItem('cortex_dashboard_telemetry') || '[]');
        } catch {
            return [];
        }
    }
}

// AC_COMPLETE: AC-SPA-001-02 ✅ ErrorBoundary with retry logic and fallback UI
