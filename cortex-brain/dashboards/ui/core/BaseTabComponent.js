/**
 * BaseTabComponent - Abstract base class for dashboard tabs
 * 
 * Provides common functionality for all dashboard tab components:
 * - Lifecycle management (init, render, destroy)
 * - Loading state handling
 * - Error state handling
 * - Container management
 * 
 * Usage:
 *   class MyTab extends BaseTabComponent {
 *     constructor(containerId) {
 *       super(containerId);
 *     }
 *     
 *     render() {
 *       this.container.innerHTML = `<div>My content</div>`;
 *     }
 *   }
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Source-Available (Use Allowed, No Contributions)
 */

class BaseTabComponent {
    /**
     * Create a new tab component
     * @param {string} containerId - DOM element ID for this tab's container
     */
    constructor(containerId) {
        if (new.target === BaseTabComponent) {
            throw new Error('BaseTabComponent is abstract and cannot be instantiated directly');
        }
        
        this.containerId = containerId;
        this.container = null;
        this.data = null;
        this.loading = false;
        this.error = null;
    }
    
    /**
     * Initialize the tab component with data
     * @param {Object} data - Tab-specific data to render
     * @returns {Promise<void>}
     */
    async init(data) {
        this.container = document.getElementById(this.containerId);
        
        if (!this.container) {
            throw new Error(`Container element '${this.containerId}' not found`);
        }
        
        this.data = data;
        this.showLoading();
        
        try {
            await this.render();
            this.hideLoading();
        } catch (err) {
            this.hideLoading();
            this.showError(err.message);
            throw err;
        }
    }
    
    /**
     * Render the tab content (must be implemented by subclasses)
     * @abstract
     * @returns {Promise<void>|void}
     */
    render() {
        throw new Error('render() must be implemented by subclass');
    }
    
    /**
     * Clean up tab resources
     */
    destroy() {
        if (this.container) {
            this.container.innerHTML = '';
        }
        this.data = null;
        this.error = null;
        this.loading = false;
    }
    
    /**
     * Show loading state
     */
    showLoading() {
        this.loading = true;
        if (this.container) {
            this.container.innerHTML = `
                <div class="loading-state">
                    <div class="spinner"></div>
                    <p>Loading...</p>
                </div>
            `;
        }
    }
    
    /**
     * Hide loading state
     */
    hideLoading() {
        this.loading = false;
        // Loading UI will be replaced by render() content
    }
    
    /**
     * Show error state
     * @param {string} message - Error message to display
     */
    showError(message) {
        this.error = message;
        if (this.container) {
            this.container.innerHTML = `
                <div class="error-state">
                    <div class="error-icon">⚠️</div>
                    <h3>Error Loading Tab</h3>
                    <p>${this.escapeHtml(message)}</p>
                    <button onclick="location.reload()">Reload Page</button>
                </div>
            `;
        }
    }
    
    /**
     * Escape HTML to prevent XSS
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Update tab with new data
     * @param {Object} data - New data to render
     * @returns {Promise<void>}
     */
    async update(data) {
        this.data = data;
        this.showLoading();
        
        try {
            await this.render();
            this.hideLoading();
        } catch (err) {
            this.hideLoading();
            this.showError(err.message);
            throw err;
        }
    }
    
    /**
     * Check if tab is currently loading
     * @returns {boolean}
     */
    isLoading() {
        return this.loading;
    }
    
    /**
     * Check if tab has an error
     * @returns {boolean}
     */
    hasError() {
        return this.error !== null;
    }
    
    /**
     * Get current error message
     * @returns {string|null}
     */
    getError() {
        return this.error;
    }
}

// Export for ES6 modules
export { BaseTabComponent };
