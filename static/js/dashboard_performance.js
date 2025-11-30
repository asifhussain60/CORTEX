/**
 * CORTEX Dashboard - Performance Optimization Module
 * 
 * Implements lazy loading, caching, and D3.js optimization for improved performance.
 * 
 * Author: Asif Hussain
 * Created: 2025-11-30
 * CORTEX Version: 3.3.0
 * 
 * Performance Features:
 * - Lazy loading for UML diagrams and large datasets
 * - Client-side data caching
 * - D3.js rendering optimization (batch updates, virtual scrolling)
 * - Progressive rendering with visual feedback
 */

// ========== Configuration ==========
const PERFORMANCE_CONFIG = {
    lazyLoad: {
        batchSize: 50,  // Items per batch for tables
        initialBatch: 25,  // Smaller first batch
        scrollThreshold: 0.8,  // Load more at 80% scroll
        enableVirtualization: true
    },
    caching: {
        maxCacheSize: 50 * 1024 * 1024,  // 50MB max cache
        ttlMinutes: 30,  // 30 minute cache TTL
        enablePersistence: true  // Use localStorage
    },
    d3Optimization: {
        batchUpdateSize: 10,  // D3 batch updates
        animationDuration: 200,  // Shorter animations
        lazyRender: true,  // Render on visibility
        maxNodesBeforeOptimization: 100
    }
};

// ========== Client-Side Cache ==========
class DashboardCache {
    constructor() {
        this.cache = new Map();
        this.cacheTimestamps = new Map();
        this.cacheSize = 0;
        this.stats = { hits: 0, misses: 0 };
        
        // Load from localStorage if available
        if (PERFORMANCE_CONFIG.caching.enablePersistence) {
            this._loadFromStorage();
        }
        
        console.log('[Performance] DashboardCache initialized');
    }
    
    get(key) {
        const cached = this.cache.get(key);
        const timestamp = this.cacheTimestamps.get(key);
        
        if (!cached || !timestamp) {
            this.stats.misses++;
            return null;
        }
        
        // Check TTL expiration
        const age = (Date.now() - timestamp) / 1000 / 60;  // minutes
        if (age > PERFORMANCE_CONFIG.caching.ttlMinutes) {
            this.invalidate(key);
            this.stats.misses++;
            console.log(`[Performance] Cache EXPIRED: ${key} (age: ${age.toFixed(1)}m)`);
            return null;
        }
        
        this.stats.hits++;
        console.log(`[Performance] Cache HIT: ${key} (age: ${age.toFixed(1)}m)`);
        return cached;
    }
    
    set(key, value) {
        try {
            const valueSize = JSON.stringify(value).length;
            
            // Ensure we don't exceed max cache size
            while (this.cacheSize + valueSize > PERFORMANCE_CONFIG.caching.maxCacheSize && this.cache.size > 0) {
                this._evictOldest();
            }
            
            this.cache.set(key, value);
            this.cacheTimestamps.set(key, Date.now());
            this.cacheSize += valueSize;
            
            console.log(`[Performance] Cache SET: ${key} (size: ${(valueSize/1024).toFixed(1)}KB)`);
            
            // Persist to localStorage
            if (PERFORMANCE_CONFIG.caching.enablePersistence) {
                this._saveToStorage();
            }
        } catch (e) {
            console.warn('[Performance] Cache set failed:', e);
        }
    }
    
    invalidate(key) {
        if (this.cache.has(key)) {
            const valueSize = JSON.stringify(this.cache.get(key)).length;
            this.cache.delete(key);
            this.cacheTimestamps.delete(key);
            this.cacheSize -= valueSize;
            
            console.log(`[Performance] Cache INVALIDATED: ${key}`);
            return true;
        }
        return false;
    }
    
    clear() {
        const count = this.cache.size;
        this.cache.clear();
        this.cacheTimestamps.clear();
        this.cacheSize = 0;
        
        if (PERFORMANCE_CONFIG.caching.enablePersistence) {
            localStorage.removeItem('cortex_dashboard_cache');
        }
        
        console.log(`[Performance] Cache CLEARED: ${count} entries`);
    }
    
    getStats() {
        const hitRate = this.stats.hits + this.stats.misses > 0
            ? (this.stats.hits / (this.stats.hits + this.stats.misses))
            : 0;
        
        return {
            hits: this.stats.hits,
            misses: this.stats.misses,
            hitRate: hitRate,
            entries: this.cache.size,
            sizeKB: (this.cacheSize / 1024).toFixed(1)
        };
    }
    
    _evictOldest() {
        let oldest = null;
        let oldestTime = Date.now();
        
        for (const [key, timestamp] of this.cacheTimestamps) {
            if (timestamp < oldestTime) {
                oldestTime = timestamp;
                oldest = key;
            }
        }
        
        if (oldest) {
            console.log(`[Performance] Cache EVICTION (LRU): ${oldest}`);
            this.invalidate(oldest);
        }
    }
    
    _saveToStorage() {
        try {
            const cacheData = {
                cache: Array.from(this.cache.entries()),
                timestamps: Array.from(this.cacheTimestamps.entries())
            };
            localStorage.setItem('cortex_dashboard_cache', JSON.stringify(cacheData));
        } catch (e) {
            console.warn('[Performance] Failed to save cache to localStorage:', e);
        }
    }
    
    _loadFromStorage() {
        try {
            const stored = localStorage.getItem('cortex_dashboard_cache');
            if (stored) {
                const cacheData = JSON.parse(stored);
                this.cache = new Map(cacheData.cache);
                this.cacheTimestamps = new Map(cacheData.timestamps);
                this.cacheSize = JSON.stringify(Array.from(this.cache.values())).length;
                console.log(`[Performance] Cache loaded from localStorage: ${this.cache.size} entries`);
            }
        } catch (e) {
            console.warn('[Performance] Failed to load cache from localStorage:', e);
        }
    }
}

// Global cache instance
const dashboardCache = new DashboardCache();

// ========== Lazy Loading Manager ==========
class LazyLoader {
    constructor(data, config = PERFORMANCE_CONFIG.lazyLoad) {
        this.data = data;
        this.config = config;
        this.currentIndex = 0;
        this.batchesLoaded = 0;
        this.container = null;
        this.onBatchLoaded = null;
        
        console.log(`[Performance] LazyLoader initialized: ${data.length} items`);
    }
    
    getNextBatch() {
        if (this.currentIndex >= this.data.length) {
            return [];
        }
        
        const batchSize = this.batchesLoaded === 0
            ? this.config.initialBatch
            : this.config.batchSize;
        
        const endIndex = Math.min(this.currentIndex + batchSize, this.data.length);
        const batch = this.data.slice(this.currentIndex, endIndex);
        
        this.currentIndex = endIndex;
        this.batchesLoaded++;
        
        console.log(
            `[Performance] Loaded batch ${this.batchesLoaded}: ${batch.length} items ` +
            `(${this.currentIndex}/${this.data.length})`
        );
        
        return batch;
    }
    
    hasMore() {
        return this.currentIndex < this.data.length;
    }
    
    getProgress() {
        return this.data.length > 0 ? (this.currentIndex / this.data.length) : 1.0;
    }
    
    attachScrollHandler(container, renderFunction) {
        this.container = container;
        
        container.addEventListener('scroll', () => {
            const scrollPercentage = (container.scrollTop + container.clientHeight) / container.scrollHeight;
            
            if (scrollPercentage >= this.config.scrollThreshold && this.hasMore()) {
                const batch = this.getNextBatch();
                if (batch.length > 0) {
                    renderFunction(batch);
                }
            }
        });
        
        console.log('[Performance] Scroll-based lazy loading attached');
    }
}

// ========== UML Diagram Lazy Loader ==========
class UMLLazyLoader {
    constructor() {
        this.loadedDiagrams = new Map();
        this.loadingStates = new Map();
        this.observers = new Map();
        
        console.log('[Performance] UMLLazyLoader initialized');
    }
    
    setupLazyLoading(diagramId, containerSelector, loadFunction) {
        const container = document.querySelector(containerSelector);
        if (!container) {
            console.warn(`[Performance] Container not found: ${containerSelector}`);
            return;
        }
        
        // Check if already loaded
        if (this.loadedDiagrams.has(diagramId)) {
            container.innerHTML = this.loadedDiagrams.get(diagramId);
            console.log(`[Performance] UML diagram ${diagramId} loaded from cache`);
            return;
        }
        
        // Setup Intersection Observer for lazy loading
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !this.loadingStates.get(diagramId)) {
                    this.loadingStates.set(diagramId, true);
                    
                    // Show loading placeholder
                    container.innerHTML = '<div class="loading-spinner">Loading UML diagram...</div>';
                    
                    console.log(`[Performance] Loading UML diagram: ${diagramId}`);
                    
                    // Load diagram
                    setTimeout(() => {
                        const diagramHTML = loadFunction();
                        container.innerHTML = diagramHTML;
                        this.loadedDiagrams.set(diagramId, diagramHTML);
                        this.loadingStates.set(diagramId, false);
                        
                        console.log(`[Performance] UML diagram ${diagramId} loaded and cached`);
                    }, 100);
                    
                    // Unobserve after loading
                    observer.unobserve(entry.target);
                }
            });
        }, {
            rootMargin: '100px'  // Start loading 100px before visible
        });
        
        observer.observe(container);
        this.observers.set(diagramId, observer);
    }
    
    getCachedDiagram(diagramId) {
        return this.loadedDiagrams.get(diagramId);
    }
    
    clearCache() {
        this.loadedDiagrams.clear();
        this.loadingStates.clear();
        console.log('[Performance] UML diagram cache cleared');
    }
}

// Global UML lazy loader
const umlLazyLoader = new UMLLazyLoader();

// ========== D3.js Optimization Utilities ==========
const D3Optimization = {
    /**
     * Batch update D3 elements to minimize reflows.
     */
    batchUpdate(selection, data, updateFn) {
        const batches = [];
        const batchSize = PERFORMANCE_CONFIG.d3Optimization.batchUpdateSize;
        
        for (let i = 0; i < data.length; i += batchSize) {
            batches.push(data.slice(i, i + batchSize));
        }
        
        console.log(`[Performance] D3 batch update: ${batches.length} batches`);
        
        let currentBatch = 0;
        function processBatch() {
            if (currentBatch < batches.length) {
                updateFn(selection, batches[currentBatch]);
                currentBatch++;
                requestAnimationFrame(processBatch);
            }
        }
        
        processBatch();
    },
    
    /**
     * Optimize D3 transitions for performance.
     */
    optimizedTransition(selection) {
        return selection
            .transition()
            .duration(PERFORMANCE_CONFIG.d3Optimization.animationDuration);
    },
    
    /**
     * Use Canvas for large node counts (>100 nodes).
     */
    shouldUseCanvas(nodeCount) {
        return nodeCount > PERFORMANCE_CONFIG.d3Optimization.maxNodesBeforeOptimization;
    },
    
    /**
     * Throttle D3 zoom/pan events.
     */
    throttledZoom(callback, delay = 50) {
        let timeoutId;
        return function(...args) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => callback.apply(this, args), delay);
        };
    }
};

// ========== Performance Monitoring ==========
class PerformanceMonitor {
    constructor() {
        this.marks = new Map();
        this.measures = [];
    }
    
    mark(name) {
        this.marks.set(name, performance.now());
        console.log(`[Performance] Mark: ${name}`);
    }
    
    measure(name, startMark, endMark = null) {
        const startTime = this.marks.get(startMark);
        const endTime = endMark ? this.marks.get(endMark) : performance.now();
        
        if (!startTime) {
            console.warn(`[Performance] Start mark not found: ${startMark}`);
            return null;
        }
        
        const duration = endTime - startTime;
        this.measures.push({ name, duration, timestamp: Date.now() });
        
        console.log(`[Performance] ${name}: ${duration.toFixed(2)}ms`);
        return duration;
    }
    
    getReport() {
        return {
            measures: this.measures,
            cacheStats: dashboardCache.getStats()
        };
    }
}

// Global performance monitor
const performanceMonitor = new PerformanceMonitor();

// ========== Export Public API ==========
window.DashboardPerformance = {
    cache: dashboardCache,
    LazyLoader: LazyLoader,
    umlLazyLoader: umlLazyLoader,
    D3Optimization: D3Optimization,
    performanceMonitor: performanceMonitor,
    config: PERFORMANCE_CONFIG
};

console.log('[Performance] Performance optimization module loaded');
