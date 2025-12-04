/**
 * Performance Optimization Utilities
 * 
 * Provides lazy loading, debouncing, render optimization, and performance monitoring
 * to ensure the dashboard loads in <3 seconds and remains responsive.
 * 
 * Features:
 * - Lazy tab rendering (only render active tab)
 * - Debounced resize/scroll handlers
 * - Render cycle optimization for D3.js/Three.js
 * - Data compression before rendering
 * - Performance metrics collection
 * - Memory usage tracking
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Source-Available (Use Allowed, No Contributions)
 */

import { showSuccessToast, showWarningToast } from './loading-animations.js';

/**
 * Performance metrics
 */
const performanceMetrics = {
    pageLoadTime: 0,
    tabRenderTimes: {},
    dataLoadTime: 0,
    visualizationRenderTimes: {},
    memoryUsage: [],
    renderCycleCount: 0
};

/**
 * Rendered tabs tracking (for lazy loading)
 */
const renderedTabs = new Set();

/**
 * Initialize performance monitoring
 */
export function initPerformanceMonitoring() {
    // Record page load time
    if (performance && performance.timing) {
        window.addEventListener('load', () => {
            const timing = performance.timing;
            performanceMetrics.pageLoadTime = timing.loadEventEnd - timing.navigationStart;
            console.log(`Page load time: ${performanceMetrics.pageLoadTime}ms`);
            
            // Check if load time exceeds target
            if (performanceMetrics.pageLoadTime > 3000) {
                showWarningToast(`Load time: ${(performanceMetrics.pageLoadTime / 1000).toFixed(2)}s (target: <3s)`);
            } else {
                showSuccessToast(`Load time: ${(performanceMetrics.pageLoadTime / 1000).toFixed(2)}s`);
            }
        });
    }
    
    // Monitor memory usage (if available)
    if (performance.memory) {
        setInterval(() => {
            const memory = {
                used: performance.memory.usedJSHeapSize / 1048576, // MB
                total: performance.memory.totalJSHeapSize / 1048576,
                limit: performance.memory.jsHeapSizeLimit / 1048576,
                timestamp: Date.now()
            };
            performanceMetrics.memoryUsage.push(memory);
            
            // Keep only last 100 readings
            if (performanceMetrics.memoryUsage.length > 100) {
                performanceMetrics.memoryUsage.shift();
            }
            
            // Warn if memory usage > 90%
            if (memory.used / memory.limit > 0.9) {
                console.warn('High memory usage:', memory);
            }
        }, 5000); // Every 5 seconds
    }
    
    console.log('Performance monitoring initialized');
}

/**
 * Lazy render tab content (only render when tab is activated)
 * @param {string} tabId - Tab identifier
 * @param {Function} renderFunction - Render function for the tab
 * @param {Object} data - Data to pass to render function
 * @returns {Promise<void>}
 */
export async function lazyRenderTab(tabId, renderFunction, data) {
    // Skip if already rendered
    if (renderedTabs.has(tabId)) {
        console.log(`Tab ${tabId} already rendered, skipping`);
        return;
    }
    
    const startTime = performance.now();
    
    try {
        await renderFunction(data);
        renderedTabs.add(tabId);
        
        const renderTime = performance.now() - startTime;
        performanceMetrics.tabRenderTimes[tabId] = renderTime;
        console.log(`Tab ${tabId} rendered in ${renderTime.toFixed(2)}ms`);
        
        // Warn if render time > 1s
        if (renderTime > 1000) {
            console.warn(`Slow render for ${tabId}: ${renderTime.toFixed(2)}ms`);
        }
    } catch (error) {
        console.error(`Error rendering tab ${tabId}:`, error);
        throw error;
    }
}

/**
 * Force re-render of a tab (clears lazy render cache)
 * @param {string} tabId - Tab identifier
 */
export function forceRerender(tabId) {
    renderedTabs.delete(tabId);
    console.log(`Tab ${tabId} marked for re-render`);
}

/**
 * Clear all lazy render cache
 */
export function clearRenderCache() {
    renderedTabs.clear();
    console.log('All tabs marked for re-render');
}

/**
 * Debounce function calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
export function debounce(func, wait = 250) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function calls
 * @param {Function} func - Function to throttle
 * @param {number} limit - Minimum time between calls in milliseconds
 * @returns {Function} Throttled function
 */
export function throttle(func, limit = 250) {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func(...args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Optimize resize handlers with debouncing
 * @param {Function} callback - Resize callback
 * @param {number} delay - Debounce delay (default 250ms)
 * @returns {Function} Debounced resize handler
 */
export function optimizeResizeHandler(callback, delay = 250) {
    return debounce(callback, delay);
}

/**
 * Request animation frame wrapper for smooth animations
 * @param {Function} callback - Animation callback
 * @returns {number} Animation frame ID
 */
export function requestAnimationFrameSafe(callback) {
    if (window.requestAnimationFrame) {
        return window.requestAnimationFrame(callback);
    } else {
        return setTimeout(callback, 16); // ~60fps fallback
    }
}

/**
 * Cancel animation frame safely
 * @param {number} id - Animation frame ID
 */
export function cancelAnimationFrameSafe(id) {
    if (window.cancelAnimationFrame) {
        window.cancelAnimationFrame(id);
    } else {
        clearTimeout(id);
    }
}

/**
 * Measure render performance
 * @param {string} name - Measurement name
 * @param {Function} renderFunction - Function to measure
 * @returns {Promise<number>} Render time in milliseconds
 */
export async function measureRender(name, renderFunction) {
    const startTime = performance.now();
    
    try {
        await renderFunction();
        const renderTime = performance.now() - startTime;
        
        performanceMetrics.visualizationRenderTimes[name] = renderTime;
        performanceMetrics.renderCycleCount++;
        
        console.log(`${name} rendered in ${renderTime.toFixed(2)}ms`);
        return renderTime;
    } catch (error) {
        console.error(`Error measuring ${name}:`, error);
        throw error;
    }
}

/**
 * Optimize D3.js render cycles (prevent duplicate renders)
 */
export class D3RenderOptimizer {
    constructor() {
        this.pendingRenders = new Map();
        this.renderQueue = [];
        this.isRendering = false;
    }
    
    /**
     * Queue a D3.js render
     * @param {string} elementId - Element ID to render to
     * @param {Function} renderFunction - D3.js render function
     */
    queueRender(elementId, renderFunction) {
        // Cancel pending render for same element
        if (this.pendingRenders.has(elementId)) {
            cancelAnimationFrameSafe(this.pendingRenders.get(elementId));
        }
        
        // Queue new render
        const frameId = requestAnimationFrameSafe(() => {
            this.renderQueue.push({ elementId, renderFunction });
            this.processQueue();
        });
        
        this.pendingRenders.set(elementId, frameId);
    }
    
    /**
     * Process render queue
     */
    async processQueue() {
        if (this.isRendering || this.renderQueue.length === 0) {
            return;
        }
        
        this.isRendering = true;
        
        while (this.renderQueue.length > 0) {
            const { elementId, renderFunction } = this.renderQueue.shift();
            
            try {
                await measureRender(elementId, renderFunction);
                this.pendingRenders.delete(elementId);
            } catch (error) {
                console.error(`Error rendering ${elementId}:`, error);
            }
        }
        
        this.isRendering = false;
    }
    
    /**
     * Clear all pending renders
     */
    clearQueue() {
        this.pendingRenders.forEach(frameId => cancelAnimationFrameSafe(frameId));
        this.pendingRenders.clear();
        this.renderQueue = [];
        this.isRendering = false;
    }
}

/**
 * Global D3 render optimizer instance
 */
export const d3Optimizer = new D3RenderOptimizer();

/**
 * Compress large datasets before rendering
 * @param {Array} data - Dataset to compress
 * @param {number} maxPoints - Maximum data points to keep
 * @returns {Array} Compressed dataset
 */
export function compressDataset(data, maxPoints = 1000) {
    if (!data || data.length <= maxPoints) {
        return data;
    }
    
    const step = Math.ceil(data.length / maxPoints);
    const compressed = [];
    
    for (let i = 0; i < data.length; i += step) {
        compressed.push(data[i]);
    }
    
    console.log(`Dataset compressed: ${data.length} → ${compressed.length} points`);
    return compressed;
}

/**
 * Aggregate time-series data by interval
 * @param {Array} data - Time-series data with timestamp field
 * @param {string} interval - Aggregation interval: 'hour', 'day', 'week', 'month'
 * @param {string} timestampField - Field name containing timestamp
 * @returns {Array} Aggregated data
 */
export function aggregateTimeSeriesData(data, interval = 'day', timestampField = 'timestamp') {
    if (!data || data.length === 0) {
        return data;
    }
    
    const intervalMs = {
        'hour': 3600000,
        'day': 86400000,
        'week': 604800000,
        'month': 2592000000
    }[interval] || 86400000;
    
    const buckets = new Map();
    
    data.forEach(item => {
        const timestamp = new Date(item[timestampField]).getTime();
        const bucketKey = Math.floor(timestamp / intervalMs) * intervalMs;
        
        if (!buckets.has(bucketKey)) {
            buckets.set(bucketKey, []);
        }
        buckets.get(bucketKey).push(item);
    });
    
    const aggregated = Array.from(buckets.entries()).map(([timestamp, items]) => {
        // Average numeric fields
        const aggregatedItem = { [timestampField]: new Date(timestamp) };
        
        Object.keys(items[0]).forEach(key => {
            if (key !== timestampField && typeof items[0][key] === 'number') {
                aggregatedItem[key] = items.reduce((sum, item) => sum + item[key], 0) / items.length;
            }
        });
        
        return aggregatedItem;
    });
    
    console.log(`Time-series aggregated (${interval}): ${data.length} → ${aggregated.length} points`);
    return aggregated;
}

/**
 * Implement virtual scrolling for large lists
 * @param {HTMLElement} container - Container element
 * @param {Array} items - Array of items
 * @param {Function} renderItem - Function to render individual item
 * @param {number} itemHeight - Height of each item in pixels
 */
export function setupVirtualScroll(container, items, renderItem, itemHeight = 50) {
    const containerHeight = container.clientHeight;
    const visibleCount = Math.ceil(containerHeight / itemHeight) + 2; // +2 for buffer
    
    let scrollTop = 0;
    let startIndex = 0;
    
    const viewport = document.createElement('div');
    viewport.style.height = `${items.length * itemHeight}px`;
    viewport.style.position = 'relative';
    container.appendChild(viewport);
    
    const content = document.createElement('div');
    content.style.position = 'absolute';
    content.style.top = '0';
    content.style.width = '100%';
    viewport.appendChild(content);
    
    function render() {
        startIndex = Math.floor(scrollTop / itemHeight);
        const endIndex = Math.min(startIndex + visibleCount, items.length);
        
        content.innerHTML = '';
        content.style.transform = `translateY(${startIndex * itemHeight}px)`;
        
        for (let i = startIndex; i < endIndex; i++) {
            const itemElement = renderItem(items[i], i);
            itemElement.style.height = `${itemHeight}px`;
            content.appendChild(itemElement);
        }
    }
    
    container.addEventListener('scroll', throttle(() => {
        scrollTop = container.scrollTop;
        render();
    }, 16)); // ~60fps
    
    render();
}

/**
 * Get performance metrics
 * @returns {Object} Performance metrics
 */
export function getPerformanceMetrics() {
    const metrics = { ...performanceMetrics };
    
    // Calculate average tab render time
    const tabTimes = Object.values(metrics.tabRenderTimes);
    metrics.averageTabRenderTime = tabTimes.length > 0 
        ? tabTimes.reduce((sum, time) => sum + time, 0) / tabTimes.length 
        : 0;
    
    // Calculate average visualization render time
    const vizTimes = Object.values(metrics.visualizationRenderTimes);
    metrics.averageVisualizationRenderTime = vizTimes.length > 0
        ? vizTimes.reduce((sum, time) => sum + time, 0) / vizTimes.length
        : 0;
    
    // Current memory usage
    if (metrics.memoryUsage.length > 0) {
        const latest = metrics.memoryUsage[metrics.memoryUsage.length - 1];
        metrics.currentMemoryUsage = latest.used;
        metrics.memoryUtilization = (latest.used / latest.limit) * 100;
    }
    
    return metrics;
}

/**
 * Log performance report
 */
export function logPerformanceReport() {
    const metrics = getPerformanceMetrics();
    
    console.group('📊 Performance Report');
    console.log(`Page Load Time: ${metrics.pageLoadTime.toFixed(2)}ms`);
    console.log(`Average Tab Render: ${metrics.averageTabRenderTime.toFixed(2)}ms`);
    console.log(`Average Viz Render: ${metrics.averageVisualizationRenderTime.toFixed(2)}ms`);
    console.log(`Total Render Cycles: ${metrics.renderCycleCount}`);
    
    if (metrics.currentMemoryUsage) {
        console.log(`Memory Usage: ${metrics.currentMemoryUsage.toFixed(2)} MB (${metrics.memoryUtilization.toFixed(1)}%)`);
    }
    
    console.log('Tab Render Times:', metrics.tabRenderTimes);
    console.log('Visualization Render Times:', metrics.visualizationRenderTimes);
    console.groupEnd();
    
    return metrics;
}

/**
 * Optimize images for faster loading
 * @param {string} imageUrl - Image URL
 * @param {number} maxWidth - Maximum width
 * @param {number} maxHeight - Maximum height
 * @returns {Promise<string>} Optimized image data URL
 */
export async function optimizeImage(imageUrl, maxWidth = 1920, maxHeight = 1080) {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.crossOrigin = 'anonymous';
        
        img.onload = () => {
            let { width, height } = img;
            
            // Calculate new dimensions
            if (width > maxWidth || height > maxHeight) {
                const ratio = Math.min(maxWidth / width, maxHeight / height);
                width = width * ratio;
                height = height * ratio;
            }
            
            // Create canvas and resize
            const canvas = document.createElement('canvas');
            canvas.width = width;
            canvas.height = height;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0, width, height);
            
            resolve(canvas.toDataURL('image/jpeg', 0.85));
        };
        
        img.onerror = reject;
        img.src = imageUrl;
    });
}

/**
 * Preload critical resources
 * @param {Array<string>} urls - URLs to preload
 */
export function preloadResources(urls) {
    urls.forEach(url => {
        const link = document.createElement('link');
        link.rel = 'preload';
        
        if (url.endsWith('.css')) {
            link.as = 'style';
        } else if (url.endsWith('.js')) {
            link.as = 'script';
        } else if (url.match(/\.(jpg|jpeg|png|gif|webp)$/)) {
            link.as = 'image';
        } else {
            link.as = 'fetch';
            link.crossOrigin = 'anonymous';
        }
        
        link.href = url;
        document.head.appendChild(link);
    });
    
    console.log(`Preloaded ${urls.length} resources`);
}
