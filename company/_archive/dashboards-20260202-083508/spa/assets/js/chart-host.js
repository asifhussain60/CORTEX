/**
 * ChartHost - Visibility-Aware Chart Initialization
 * 
 * GPT Spec Section 8: Charts must render only when visible.
 * Solves: "diagrams not loading properly" class of issues.
 * 
 * Features:
 * - IntersectionObserver for visibility detection
 * - Tab activation event handling
 * - ResizeObserver for responsive charts
 * - Per-chart initialization guard
 * - requestAnimationFrame double-wait before init
 * 
 * @version 1.0.0
 * @license MIT
 */

(function(global) {
    'use strict';
    
    /**
     * ChartHost configuration defaults
     */
    const DEFAULT_CONFIG = {
        rootMargin: '50px',
        threshold: 0.1,
        debounceResize: 250,
        initDelay: 32 // ~2 RAF frames
    };
    
    /**
     * Track initialized charts to prevent double-init
     */
    const initializedCharts = new Map();
    
    /**
     * Active observers
     */
    const observers = {
        intersection: null,
        resize: new Map()
    };
    
    /**
     * ChartHost - Main visibility-aware chart wrapper
     */
    class ChartHost {
        /**
         * Create a ChartHost instance
         * @param {HTMLElement} container - Chart container element
         * @param {Object} options - Configuration options
         */
        constructor(container, options = {}) {
            this.container = container;
            this.chartId = container.id || `chart-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
            this.options = { ...DEFAULT_CONFIG, ...options };
            this.chart = null;
            this.initialized = false;
            this.visible = false;
            this.initCallback = null;
            
            // Ensure container has an ID
            if (!container.id) {
                container.id = this.chartId;
            }
            
            this._setupObservers();
        }
        
        /**
         * Set the initialization callback
         * @param {Function} callback - Function to call when chart should initialize
         * @returns {ChartHost} this for chaining
         */
        onInit(callback) {
            this.initCallback = callback;
            
            // Check if already visible
            if (this.visible && !this.initialized) {
                this._initializeChart();
            }
            
            return this;
        }
        
        /**
         * Get the chart instance (if initialized)
         * @returns {Object|null} Chart instance
         */
        getChart() {
            return this.chart;
        }
        
        /**
         * Manually trigger resize
         */
        resize() {
            if (this.chart && typeof this.chart.resize === 'function') {
                this.chart.resize();
            }
        }
        
        /**
         * Destroy the chart and cleanup
         */
        destroy() {
            // Remove from tracking
            initializedCharts.delete(this.chartId);
            
            // Cleanup resize observer
            if (observers.resize.has(this.chartId)) {
                observers.resize.get(this.chartId).disconnect();
                observers.resize.delete(this.chartId);
            }
            
            // Destroy chart if it has a destroy method
            if (this.chart) {
                if (typeof this.chart.dispose === 'function') {
                    this.chart.dispose(); // ECharts
                } else if (typeof this.chart.destroy === 'function') {
                    this.chart.destroy(); // Chart.js
                }
                this.chart = null;
            }
            
            this.initialized = false;
        }
        
        /**
         * Setup intersection and resize observers
         * @private
         */
        _setupObservers() {
            // Setup intersection observer (singleton)
            if (!observers.intersection) {
                observers.intersection = new IntersectionObserver(
                    (entries) => this._handleIntersection(entries),
                    {
                        rootMargin: this.options.rootMargin,
                        threshold: this.options.threshold
                    }
                );
            }
            
            // Observe container
            observers.intersection.observe(this.container);
            
            // Setup resize observer for this chart
            const resizeObserver = new ResizeObserver(
                this._debounce(() => this.resize(), this.options.debounceResize)
            );
            resizeObserver.observe(this.container);
            observers.resize.set(this.chartId, resizeObserver);
        }
        
        /**
         * Handle intersection observer callback
         * @private
         */
        _handleIntersection(entries) {
            for (const entry of entries) {
                if (entry.target === this.container) {
                    this.visible = entry.isIntersecting;
                    
                    if (this.visible && !this.initialized && this.initCallback) {
                        this._initializeChart();
                    }
                }
            }
        }
        
        /**
         * Initialize chart with RAF double-wait (GPT Spec: ensures layout settled)
         * @private
         */
        _initializeChart() {
            if (this.initialized || initializedCharts.has(this.chartId)) {
                return;
            }
            
            // Mark as initializing
            initializedCharts.set(this.chartId, 'initializing');
            
            // Double RAF for layout settling (GPT Spec Section 8)
            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    // Verify container has dimensions
                    const rect = this.container.getBoundingClientRect();
                    if (rect.width === 0 || rect.height === 0) {
                        console.warn(`ChartHost: Container ${this.chartId} has zero dimensions, delaying init`);
                        initializedCharts.delete(this.chartId);
                        
                        // Retry after delay
                        setTimeout(() => this._initializeChart(), this.options.initDelay * 2);
                        return;
                    }
                    
                    try {
                        this.chart = this.initCallback(this.container);
                        this.initialized = true;
                        initializedCharts.set(this.chartId, this.chart);
                        
                        console.debug(`ChartHost: Initialized ${this.chartId}`);
                    } catch (error) {
                        console.error(`ChartHost: Failed to initialize ${this.chartId}:`, error);
                        initializedCharts.delete(this.chartId);
                    }
                });
            });
        }
        
        /**
         * Debounce helper
         * @private
         */
        _debounce(fn, delay) {
            let timeoutId;
            return (...args) => {
                clearTimeout(timeoutId);
                timeoutId = setTimeout(() => fn.apply(this, args), delay);
            };
        }
    }
    
    /**
     * Tab activation handler
     * Re-renders charts when their parent tab becomes visible
     */
    class TabActivationHandler {
        constructor() {
            this.tabCharts = new Map(); // tabId -> Set<ChartHost>
            this._setupTabListeners();
        }
        
        /**
         * Register a chart with a tab
         * @param {string} tabId - Tab panel ID
         * @param {ChartHost} chartHost - ChartHost instance
         */
        register(tabId, chartHost) {
            if (!this.tabCharts.has(tabId)) {
                this.tabCharts.set(tabId, new Set());
            }
            this.tabCharts.get(tabId).add(chartHost);
        }
        
        /**
         * Handle tab activation
         * @param {string} tabId - Activated tab ID
         */
        onTabActivated(tabId) {
            const charts = this.tabCharts.get(tabId);
            if (!charts) return;
            
            // Trigger resize on all charts in this tab
            requestAnimationFrame(() => {
                charts.forEach(chartHost => {
                    if (chartHost.initialized) {
                        chartHost.resize();
                    }
                });
            });
        }
        
        /**
         * Setup global tab listeners
         * @private
         */
        _setupTabListeners() {
            // Listen for custom tab activation events
            document.addEventListener('tabActivated', (e) => {
                if (e.detail && e.detail.tabId) {
                    this.onTabActivated(e.detail.tabId);
                }
            });
            
            // Also listen for click on tab buttons (common pattern)
            document.addEventListener('click', (e) => {
                const tabButton = e.target.closest('[data-tab], .tab-button');
                if (tabButton) {
                    const tabId = tabButton.dataset.tab || tabButton.getAttribute('aria-controls');
                    if (tabId) {
                        // Delay to allow tab panel to become visible
                        setTimeout(() => this.onTabActivated(tabId), 50);
                    }
                }
            });
        }
    }
    
    // Create singleton tab handler
    const tabHandler = new TabActivationHandler();
    
    /**
     * Factory function to create a ChartHost
     * @param {string|HTMLElement} container - Container element or selector
     * @param {Object} options - Configuration options
     * @returns {ChartHost}
     */
    function createChartHost(container, options = {}) {
        const element = typeof container === 'string' 
            ? document.querySelector(container)
            : container;
            
        if (!element) {
            throw new Error(`ChartHost: Container not found: ${container}`);
        }
        
        return new ChartHost(element, options);
    }
    
    /**
     * Helper to create ECharts chart with ChartHost
     * @param {string|HTMLElement} container - Container
     * @param {Object} echartsOption - ECharts option
     * @param {string} tabId - Optional tab ID for tab activation handling
     * @returns {ChartHost}
     */
    function createEChartsHost(container, echartsOption, tabId = null) {
        const host = createChartHost(container);
        
        host.onInit((el) => {
            if (typeof echarts === 'undefined') {
                console.error('ChartHost: ECharts not loaded');
                return null;
            }
            
            const chart = echarts.init(el);
            chart.setOption(echartsOption);
            return chart;
        });
        
        if (tabId) {
            tabHandler.register(tabId, host);
        }
        
        return host;
    }
    
    /**
     * Helper to create Chart.js chart with ChartHost
     * @param {string|HTMLElement} container - Container (should be canvas parent)
     * @param {Object} chartConfig - Chart.js configuration
     * @param {string} tabId - Optional tab ID
     * @returns {ChartHost}
     */
    function createChartJSHost(container, chartConfig, tabId = null) {
        const host = createChartHost(container);
        
        host.onInit((el) => {
            if (typeof Chart === 'undefined') {
                console.error('ChartHost: Chart.js not loaded');
                return null;
            }
            
            // Find or create canvas
            let canvas = el.querySelector('canvas');
            if (!canvas) {
                canvas = document.createElement('canvas');
                el.appendChild(canvas);
            }
            
            return new Chart(canvas, chartConfig);
        });
        
        if (tabId) {
            tabHandler.register(tabId, host);
        }
        
        return host;
    }
    
    /**
     * Initialize all chart containers in a given scope
     * @param {HTMLElement} scope - Scope to search within (default: document)
     * @param {Object} chartConfigs - Map of containerId -> chart config
     */
    function initializeAllCharts(scope = document, chartConfigs = {}) {
        const containers = scope.querySelectorAll('[data-chart-type]');
        
        containers.forEach(container => {
            const chartType = container.dataset.chartType;
            const chartId = container.id;
            const config = chartConfigs[chartId] || {};
            
            // Find parent tab if any
            const tabPanel = container.closest('[role="tabpanel"], .tab-panel, .tab-content');
            const tabId = tabPanel ? tabPanel.id : null;
            
            switch (chartType) {
                case 'echarts':
                    createEChartsHost(container, config, tabId);
                    break;
                case 'chartjs':
                    createChartJSHost(container, config, tabId);
                    break;
                case 'd3':
                    // D3 requires custom init - just create host
                    const host = createChartHost(container);
                    if (config.init && typeof config.init === 'function') {
                        host.onInit(config.init);
                    }
                    if (tabId) {
                        tabHandler.register(tabId, host);
                    }
                    break;
                default:
                    console.warn(`ChartHost: Unknown chart type: ${chartType}`);
            }
        });
    }
    
    // Export to global
    global.ChartHost = ChartHost;
    global.createChartHost = createChartHost;
    global.createEChartsHost = createEChartsHost;
    global.createChartJSHost = createChartJSHost;
    global.initializeAllCharts = initializeAllCharts;
    global.tabActivationHandler = tabHandler;
    
})(typeof window !== 'undefined' ? window : this);
