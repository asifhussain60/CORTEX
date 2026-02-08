/**
 * PathResolver.js
 * Handles asset path resolution for file:// vs http:// protocols
 * 
 * Purpose: Fix 404 errors by computing correct paths for CSS, images, fonts
 * Author: Asif Hussain
 * Date: 2026-02-08
 * Authority: Dashboard Fix - Phase 53 (NEW)
 */

class PathResolver {
    constructor() {
        this.protocol = window.location.protocol;
        this.basePath = this._computeBasePath();
        this.brokenPaths = [];
        
        console.log('🔧 [PathResolver] Initialized', {
            protocol: this.protocol,
            basePath: this.basePath,
            href: window.location.href
        });
    }
    
    /**
     * Compute base path from current location
     * @returns {string} Base path for assets
     */
    _computeBasePath() {
        const href = window.location.href;
        
        if (this.protocol === 'file:') {
            // file:///D:/PROJECTS/CORTEX/company/dashboards/repos/ksessions/index.html
            // → D:/PROJECTS/CORTEX/company/dashboards/
            const parts = href.split('/');
            const dashboardsIndex = parts.findIndex(p => p === 'dashboards');
            
            if (dashboardsIndex !== -1) {
                return parts.slice(0, dashboardsIndex + 2).join('/') + '/';
            }
        } else {
            // http://localhost:3000/repos/ksessions/index.html
            // → http://localhost:3000/
            const url = new URL(href);
            return `${url.protocol}//${url.host}/`;
        }
        
        return '';
    }
    
    /**
     * Resolve asset path based on protocol
     * @param {string} relativePath - Relative path (e.g., "../../assets/css/main.css")
     * @returns {string} Resolved absolute path
     */
    resolveAssetPath(relativePath) {
        // Already absolute?
        if (relativePath.startsWith('http://') || relativePath.startsWith('https://')) {
            return relativePath;
        }
        
        // file:// protocol: resolve relative paths
        if (this.protocol === 'file:') {
            const currentDir = this._getCurrentDirectory();
            return this._resolveRelative(currentDir, relativePath);
        }
        
        // http:// protocol: use base path
        return this.basePath + relativePath.replace(/^\.\.\/|^\.\//, '');
    }
    
    /**
     * Get current directory from URL
     * @returns {string} Current directory path
     */
    _getCurrentDirectory() {
        const href = window.location.href;
        const lastSlash = href.lastIndexOf('/');
        return href.substring(0, lastSlash + 1);
    }
    
    /**
     * Resolve relative path from current directory
     * @param {string} base - Base directory
     * @param {string} relative - Relative path
     * @returns {string} Resolved path
     */
    _resolveRelative(base, relative) {
        const parts = base.split('/').filter(p => p);
        const relativeParts = relative.split('/');
        
        for (const part of relativeParts) {
            if (part === '..') {
                parts.pop();
            } else if (part !== '.') {
                parts.push(part);
            }
        }
        
        return parts.join('/');
    }
    
    /**
     * Preload critical assets and detect 404s
     * @param {Array<string>} assetPaths - Array of asset paths to preload
     * @returns {Promise<Object>} Results with success/failed arrays
     */
    async preloadCriticalAssets(assetPaths) {
        console.log('📦 [PathResolver] Preloading assets...', assetPaths.length);
        
        const results = {
            success: [],
            failed: [],
            total: assetPaths.length
        };
        
        // Skip fetch validation for file:// protocol (CORS restriction)
        if (this.protocol === 'file:') {
            console.log('ℹ️ [PathResolver] Skipping fetch validation (file:// protocol)');
            console.log('ℹ️ [PathResolver] Browser will load assets naturally');
            
            // Mark all as success (browser will handle loading)
            assetPaths.forEach(path => {
                const resolved = this.resolveAssetPath(path);
                results.success.push({ path, resolved, status: 'skipped' });
                console.log('✅ [PathResolver]', path, '→', resolved, '(browser-loaded)');
            });
            
            return results;
        }
        
        // HTTP protocol: perform fetch validation
        for (const path of assetPaths) {
            try {
                const resolved = this.resolveAssetPath(path);
                const response = await fetch(resolved, { method: 'HEAD' });
                
                if (response.ok) {
                    results.success.push({ path, resolved, status: response.status });
                    console.log('✅ [PathResolver]', path, '→', resolved);
                } else {
                    results.failed.push({ path, resolved, status: response.status });
                    this.brokenPaths.push({ path, resolved, error: `HTTP ${response.status}` });
                    console.error('❌ [PathResolver] 404:', path, '→', resolved);
                }
            } catch (error) {
                results.failed.push({ path, error: error.message });
                this.brokenPaths.push({ path, error: error.message });
                console.error('❌ [PathResolver] Failed:', path, error);
            }
        }
        
        console.log('📊 [PathResolver] Preload complete:', {
            success: results.success.length,
            failed: results.failed.length,
            successRate: `${((results.success.length / results.total) * 100).toFixed(1)}%`
        });
        
        return results;
    }
    
    /**
     * Report broken paths to console
     */
    reportBrokenPaths() {
        if (this.brokenPaths.length === 0) {
            console.log('✅ [PathResolver] No broken paths detected');
            return;
        }
        
        console.group('⚠️ [PathResolver] Broken Paths Detected');
        console.table(this.brokenPaths);
        console.groupEnd();
    }
    
    /**
     * Fix link/script href/src attributes in DOM
     * @param {string} selector - CSS selector for elements to fix
     */
    fixDOMPaths(selector = 'link[href], script[src], img[src]') {
        const elements = document.querySelectorAll(selector);
        let fixed = 0;
        
        elements.forEach(el => {
            const attr = el.tagName === 'LINK' ? 'href' : 'src';
            const original = el.getAttribute(attr);
            
            if (original && !original.startsWith('http://') && !original.startsWith('https://')) {
                const resolved = this.resolveAssetPath(original);
                el.setAttribute(attr, resolved);
                fixed++;
                console.log('🔧 [PathResolver] Fixed:', original, '→', resolved);
            }
        });
        
        console.log(`🔧 [PathResolver] Fixed ${fixed} DOM paths`);
    }
}

// Export for use in dashboard
window.PathResolver = PathResolver;
