/**
 * VisualizationComponent - Base class for modular visualization components
 * 
 * Purpose: Break dashboard into reusable, composable visualization components
 * - Each component owns rendering, error handling, data validation
 * - Enables tab-based navigation with lazy loading
 * - Follows SOLID principles (single responsibility, composition over inheritance)
 * 
 * Authority: Phase 48 Holistic Validation Gate
 * TDD: Tests before implementation (40+ unit tests in tests/components/)
 * Governance: CORE-008 (TDD), CORE-011 (types), CORE-012 (docs)
 */

class VisualizationComponent {
    /**
     * Create a visualization component
     * @param {string} componentId - Unique component identifier
     * @param {string} containerId - DOM element ID for rendering
     * @param {Object} options - Configuration options
     */
    constructor(componentId, containerId, options = {}) {
        this.componentId = componentId;
        this.containerId = containerId;
        this.options = {
            retryCount: 3,
            retryDelayMs: 100,
            timeoutMs: 5000,
            ...options
        };
        
        this.container = null;
        this.data = null;
        this.isRendered = false;
        this.renderPromise = null;
    }

    /**
     * Initialize component (verify DOM ready)
     * @returns {boolean} - True if DOM element found
     */
    initialize() {
        this.container = document.getElementById(this.containerId);
        if (!this.container) {
            console.warn(`[Viz] Component ${this.componentId}: Container not found (${this.containerId})`);
            return false;
        }
        return true;
    }

    /**
     * Render component with data
     * @param {Object} data - Data to render
     * @returns {Promise<void>}
     */
    async render(data) {
        if (!this.container) {
            throw new Error(`Component ${this.componentId}: Container not initialized`);
        }

        this.renderPromise = this._renderWithRetry(data);
        return await this.renderPromise;
    }

    /**
     * Internal render with retry logic
     * @private
     */
    async _renderWithRetry(data) {
        let lastError;
        
        for (let attempt = 0; attempt < this.options.retryCount; attempt++) {
            try {
                // Validate data before rendering
                this.validateData(data);
                
                // Clear previous render
                this.container.innerHTML = '';
                
                // Execute render with timeout
                await this._executeWithTimeout(
                    () => this._render(data),
                    this.options.timeoutMs
                );
                
                this.data = data;
                this.isRendered = true;
                console.log(`[Viz] Component ${this.componentId}: Render successful`);
                return;
            } catch (error) {
                lastError = error;
                console.warn(`[Viz] Component ${this.componentId}: Attempt ${attempt + 1} failed:`, error.message);
                
                if (attempt < this.options.retryCount - 1) {
                    await this._delay(this.options.retryDelayMs * Math.pow(2, attempt));
                }
            }
        }
        
        // All retries failed
        this._renderErrorState(lastError);
        throw lastError;
    }

    /**
     * Execute function with timeout
     * @private
     */
    async _executeWithTimeout(fn, timeoutMs) {
        return new Promise((resolve, reject) => {
            const timeoutId = setTimeout(
                () => reject(new Error(`Render timeout after ${timeoutMs}ms`)),
                timeoutMs
            );
            
            Promise.resolve(fn())
                .then(result => {
                    clearTimeout(timeoutId);
                    resolve(result);
                })
                .catch(error => {
                    clearTimeout(timeoutId);
                    reject(error);
                });
        });
    }

    /**
     * Delay helper for retries
     * @private
     */
    _delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Validate data structure (override in subclasses)
     * @param {Object} data - Data to validate
     * @throws {Error} If data invalid
     */
    validateData(data) {
        if (!data || typeof data !== 'object') {
            throw new Error(`Component ${this.componentId}: Data must be an object`);
        }
    }

    /**
     * Render component (override in subclasses)
     * @protected
     */
    async _render(data) {
        throw new Error(`Component ${this.componentId}: _render() must be implemented by subclass`);
    }

    /**
     * Render error state with fallback UI
     * @private
     */
    _renderErrorState(error) {
        const message = error?.message || 'Render failed';
        const icon = 'fa-exclamation-triangle';
        
        this.container.innerHTML = `
            <div class="viz-error-state" style="
                padding: 40px 20px;
                text-align: center;
                background: rgba(220, 53, 69, 0.1);
                border: 1px solid rgba(220, 53, 69, 0.3);
                border-radius: 8px;
                color: #dc3545;
            ">
                <i class="fas ${icon}" style="font-size: 2em; margin-bottom: 10px; display: block;"></i>
                <h3>Visualization Error</h3>
                <p>${this._sanitize(message)}</p>
                <small>${this.componentId}</small>
            </div>
        `;
        
        this.isRendered = false;
    }

    /**
     * Render empty state (no data)
     * @protected
     */
    _renderEmptyState(message = 'No data available') {
        this.container.innerHTML = `
            <div class="viz-empty-state" style="
                padding: 40px 20px;
                text-align: center;
                background: rgba(10, 14, 39, 0.3);
                border: 1px dashed rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                color: rgba(255, 255, 255, 0.6);
            ">
                <i class="fas fa-inbox" style="font-size: 2em; margin-bottom: 10px; display: block;"></i>
                <h3>No Data</h3>
                <p>${this._sanitize(message)}</p>
            </div>
        `;
        
        this.isRendered = false;
    }

    /**
     * Basic HTML sanitization
     * @private
     */
    _sanitize(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Destroy component (cleanup)
     */
    destroy() {
        if (this.container) {
            this.container.innerHTML = '';
        }
        this.data = null;
        this.isRendered = false;
    }

    /**
     * Export diagnostics
     */
    exportDiagnostics() {
        return {
            componentId: this.componentId,
            containerId: this.containerId,
            isRendered: this.isRendered,
            hasData: this.data !== null,
            options: this.options
        };
    }
}

// AC_START: AC-DASHBOARD-COMPONENTS-001
