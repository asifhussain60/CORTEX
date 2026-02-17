/**
 * DeploymentMode - Runtime Environment Detection & Configuration
 * 
 * Fixes GPR-001: file:// vs HTTP Mode Distinction
 * - Detects runtime environment
 * - Enforces appropriate data loading strategy
 * - Disables fetch() in file:// mode
 * - Shows runtime mode in UI
 * 
 * Authority: gpr-recommendation.txt § Root Cause #1
 */

class DeploymentMode {
    constructor() {
        console.log('[DeploymentMode] Constructor: Initializing...');
        this.mode = this._detectMode();
        console.log('[DeploymentMode] Mode detected:', this.mode);
        this.config = this._getConfigForMode();
        console.log('[DeploymentMode] Config generated:', this.config);
    }

    /**
     * Detect current deployment mode
     */
    _detectMode() {
        console.log('[DeploymentMode] _detectMode: protocol =', window.location.protocol);
        if (window.location.protocol === 'file:') {
            console.log('[DeploymentMode] _detectMode: Detected FILE_MODE');
            return 'FILE_MODE';
        } else if (window.location.protocol === 'http:' || window.location.protocol === 'https:') {
            console.log('[DeploymentMode] _detectMode: Detected HTTP_MODE');
            return 'HTTP_MODE';
        }
        console.log('[DeploymentMode] _detectMode: UNKNOWN mode');
        return 'UNKNOWN';
    }

    /**
     * Get configuration for current mode
     */
    _getConfigForMode() {
        if (this.mode === 'FILE_MODE') {
            return {
                allowFetch: false,
                requireEmbeddedData: true,
                description: 'Offline (file://)',
                icon: '📁',
                fallbackStrategy: 'embedded_only',
                warning: 'Running in offline mode. Some features may be limited. Use HTTP server for full functionality.'
            };
        } else if (this.mode === 'HTTP_MODE') {
            return {
                allowFetch: true,
                requireEmbeddedData: false,
                description: 'HTTP Server',
                icon: '🌐',
                fallbackStrategy: 'fetch_with_fallback',
                warning: null
            };
        }
        return {
            allowFetch: false,
            requireEmbeddedData: true,
            description: 'Unknown',
            icon: '❓',
            fallbackStrategy: 'embedded_only',
            warning: 'Unknown deployment mode detected.'
        };
    }

    /**
     * Check if fetch is allowed
     */
    canFetch() {
        return this.config.allowFetch;
    }

    /**
     * Check if embedded data is required
     */
    requiresEmbeddedData() {
        return this.config.requireEmbeddedData;
    }

    /**
     * Get current mode
     */
    getMode() {
        return this.mode;
    }

    /**
     * Get mode description for UI
     */
    getDescription() {
        return this.config.description;
    }

    /**
     * Get mode icon
     */
    getIcon() {
        return this.config.icon;
    }

    /**
     * Get warning message if any
     */
    getWarning() {
        return this.config.warning;
    }

    /**
     * Get fallback strategy
     */
    getFallbackStrategy() {
        return this.config.fallbackStrategy;
    }

    /**
     * Check if mode allows normal operation
     */
    isHealthy() {
        return this.mode === 'HTTP_MODE';
    }

    /**
     * Display deployment mode in UI
     */
    displayInUI() {
        const badge = document.createElement('span');
        badge.className = 'deployment-mode-badge';
        badge.innerHTML = `
            <span class="deployment-icon">${this.getIcon()}</span>
            <span class="deployment-text">${this.getDescription()}</span>
        `;

        if (this.getWarning()) {
            badge.title = this.getWarning();
            badge.classList.add('warning');
        }

        return badge;
    }

    /**
     * Static method to get singleton instance
     */
    static getInstance() {
        if (!window._deploymentModeInstance) {
            window._deploymentModeInstance = new DeploymentMode();
        }
        return window._deploymentModeInstance;
    }

    /**
     * Static method for direct config access
     */
    static getConfig() {
        console.log('[DeploymentMode] getConfig: Getting instance...');
        const instance = this.getInstance();
        console.log('[DeploymentMode] getConfig: Instance mode =', instance.mode);
        
        // Defensive: ensure mode is always defined
        let modeName = 'unknown';
        if (instance.mode) {
            modeName = instance.mode.toLowerCase().replace('_mode', '');
        }
        
        const config = {
            mode: modeName,
            canFetch: instance.canFetch(),
            requiresEmbeddedData: instance.requiresEmbeddedData(),
            description: instance.getDescription(),
            icon: instance.getIcon(),
            warningMessage: instance.getWarning() || '',
            fallbackStrategy: instance.getFallbackStrategy(),
            isHealthy: instance.isHealthy()
        };
        console.log('[DeploymentMode] getConfig: Returning config:', config);
        return config;
    }
}

// Auto-initialize singleton
window.DeploymentMode = DeploymentMode.getInstance();
