/**
 * CORTEX SPA - ChartHost Component
 * Lazy chart initialization with IntersectionObserver
 * Version: 1.0.0
 */

class ChartHost {
    constructor(options = {}) {
        this.charts = new Map();
        this.observers = new Map();
        this.initQueue = [];
        this.options = {
            rootMargin: '50px',
            threshold: 0.1,
            ...options
        };
        
        this.intersectionObserver = new IntersectionObserver(
            this.handleIntersection.bind(this),
            {
                rootMargin: this.options.rootMargin,
                threshold: this.options.threshold
            }
        );
    }
    
    /**
     * Register a chart for lazy initialization
     * @param {string} containerId - Container element ID
     * @param {Function} initFn - Function that creates and returns the chart
     * @param {Object} options - Chart options
     */
    register(containerId, initFn, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.warn(`ChartHost: Container not found: ${containerId}`);
            return;
        }
        
        this.initQueue.push({
            containerId,
            initFn,
            options,
            initialized: false
        });
        
        this.intersectionObserver.observe(container);
    }
    
    handleIntersection(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const containerId = entry.target.id;
                const queueItem = this.initQueue.find(q => q.containerId === containerId);
                
                if (queueItem && !queueItem.initialized) {
                    this.initializeChart(queueItem);
                }
            }
        });
    }
    
    initializeChart(queueItem) {
        const { containerId, initFn, options } = queueItem;
        const container = document.getElementById(containerId);
        
        if (!container) return;
        
        // Use RAF double-wait for layout stability
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                try {
                    const chart = initFn(container, options);
                    this.charts.set(containerId, chart);
                    queueItem.initialized = true;
                    
                    // Setup resize observer
                    this.setupResizeObserver(containerId, chart);
                    
                    console.log(`✓ Chart initialized: ${containerId}`);
                } catch (error) {
                    console.error(`ChartHost: Failed to initialize ${containerId}:`, error);
                }
            });
        });
    }
    
    setupResizeObserver(containerId, chart) {
        const container = document.getElementById(containerId);
        if (!container || !chart) return;
        
        const resizeObserver = new ResizeObserver(entries => {
            for (const entry of entries) {
                if (chart.resize && typeof chart.resize === 'function') {
                    chart.resize();
                }
            }
        });
        
        resizeObserver.observe(container);
        this.observers.set(containerId, resizeObserver);
    }
    
    /**
     * Get a chart instance by container ID
     */
    getChart(containerId) {
        return this.charts.get(containerId);
    }
    
    /**
     * Force refresh a chart
     */
    refresh(containerId) {
        const chart = this.charts.get(containerId);
        if (chart && chart.resize) {
            chart.resize();
        }
    }
    
    /**
     * Refresh all charts (useful after tab change)
     */
    refreshAll() {
        this.charts.forEach((chart, id) => {
            if (chart && chart.resize) {
                setTimeout(() => chart.resize(), 100);
            }
        });
    }
    
    /**
     * Destroy a chart and cleanup
     */
    destroy(containerId) {
        const chart = this.charts.get(containerId);
        if (chart && chart.dispose) {
            chart.dispose();
        }
        
        const observer = this.observers.get(containerId);
        if (observer) {
            observer.disconnect();
        }
        
        this.charts.delete(containerId);
        this.observers.delete(containerId);
    }
    
    /**
     * Destroy all charts
     */
    destroyAll() {
        this.charts.forEach((chart, id) => this.destroy(id));
        this.intersectionObserver.disconnect();
    }
}

// Singleton instance
window.chartHost = window.chartHost || new ChartHost();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChartHost;
}
