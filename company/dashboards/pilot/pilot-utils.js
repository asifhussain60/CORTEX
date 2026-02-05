/**
 * CORTEX Dashboard Pilot - External JavaScript Test
 * 
 * This file proves that external JavaScript loading works.
 * It also provides utility functions that would be used in the real dashboard.
 */

console.log('[PILOT-UTILS] External JavaScript loaded successfully');
console.log('[PILOT-UTILS] Load time:', new Date().toISOString());

// ============================================================
// MARKER FUNCTION - Proves JS loaded (checked by test suite)
// ============================================================
window.pilotUtilsLoaded = function() {
    return true;
};

// ============================================================
// UTILITY FUNCTIONS (would be in real dashboard)
// ============================================================
window.PilotUtils = {
    /**
     * Format a number with locale-appropriate separators
     * @param {number} num - Number to format
     * @returns {string} Formatted number
     */
    formatNumber: function(num) {
        if (typeof num !== 'number') return String(num);
        return num.toLocaleString();
    },
    
    /**
     * Format a date string to locale format
     * @param {string|Date} date - Date to format
     * @returns {string} Formatted date
     */
    formatDate: function(date) {
        try {
            return new Date(date).toLocaleDateString();
        } catch (e) {
            return String(date);
        }
    },
    
    /**
     * Format a percentage value
     * @param {number} value - Value to format (0-100 or 0-1)
     * @param {number} decimals - Decimal places
     * @returns {string} Formatted percentage
     */
    formatPercent: function(value, decimals = 1) {
        const pct = value > 1 ? value : value * 100;
        return pct.toFixed(decimals) + '%';
    },
    
    /**
     * Debounce a function call
     * @param {Function} func - Function to debounce
     * @param {number} wait - Wait time in ms
     * @returns {Function} Debounced function
     */
    debounce: function(func, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    },
    
    /**
     * Safely parse JSON with error handling
     * @param {string} str - JSON string
     * @param {*} fallback - Fallback value on error
     * @returns {*} Parsed object or fallback
     */
    safeParseJSON: function(str, fallback = null) {
        try {
            return JSON.parse(str);
        } catch (e) {
            console.error('[PILOT-UTILS] JSON parse error:', e.message);
            return fallback;
        }
    },
    
    /**
     * Create a simple hash from a string (for caching)
     * @param {string} str - String to hash
     * @returns {string} Hash string
     */
    simpleHash: function(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash;
        }
        return Math.abs(hash).toString(16);
    },
    
    /**
     * Get color based on health score
     * @param {number} score - Health score (0-100)
     * @returns {string} CSS color
     */
    getHealthColor: function(score) {
        if (score >= 80) return '#00ff88';
        if (score >= 60) return '#ffaa00';
        if (score >= 40) return '#ff8800';
        return '#ff4444';
    }
};

// ============================================================
// DATA ADAPTER (would be used for JSON loading)
// ============================================================
window.PilotDataAdapter = {
    /**
     * Fetch and parse JSON data
     * @param {string} url - URL to fetch
     * @returns {Promise<Object>} Parsed data
     */
    fetchJSON: function(url) {
        console.log(`[PILOT-DATA] Fetching: ${url}`);
        const startTime = performance.now();
        
        return fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                const elapsed = (performance.now() - startTime).toFixed(2);
                console.log(`[PILOT-DATA] Loaded in ${elapsed}ms:`, Object.keys(data));
                return data;
            })
            .catch(error => {
                console.error(`[PILOT-DATA] Fetch failed: ${error.message}`);
                throw error;
            });
    },
    
    /**
     * Load dashboard data with caching
     * @param {string} repoName - Repository name
     * @returns {Promise<Object>} Dashboard data
     */
    loadDashboardData: function(repoName) {
        const cacheKey = `dashboard_${repoName}`;
        
        // Check cache (session storage)
        const cached = sessionStorage.getItem(cacheKey);
        if (cached) {
            console.log(`[PILOT-DATA] Cache hit for ${repoName}`);
            return Promise.resolve(JSON.parse(cached));
        }
        
        // Fetch fresh
        return this.fetchJSON(`./data/${repoName}-data.json`)
            .then(data => {
                // Cache it
                try {
                    sessionStorage.setItem(cacheKey, JSON.stringify(data));
                } catch (e) {
                    console.warn('[PILOT-DATA] Cache write failed:', e.message);
                }
                return data;
            });
    }
};

console.log('[PILOT-UTILS] Utilities registered:', Object.keys(window.PilotUtils));
console.log('[PILOT-UTILS] Data adapter registered:', Object.keys(window.PilotDataAdapter));
