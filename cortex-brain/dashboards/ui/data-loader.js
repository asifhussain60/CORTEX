/**
 * Data Loader Module
 * 
 * Handles loading, caching, and validation of dashboard data from multiple sources.
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Source-Available (Use Allowed, No Contributions)
 */

// Data cache
const dataCache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

// Data source base paths
const DATA_SOURCES = {
    mock: '/mock/',
    cortex: '/cortex/',
    'noor-canvas': '/noor-canvas/',
    alist: '/alist/',
    ksessions: '/ksessions/',
    'v5-webservices-prevalidationws': '/v5-webservices-prevalidationws/'
};

// Data files to load
const DATA_FILES = [
    'health-data.json',
    'tech-stack.json',
    'security.json',
    'architecture.json',
    'code-organization.json',
    'team-metrics.json',
    'vendors.json'
];

/**
 * Load all dashboard data for a given source
 * @param {string} source - Data source ('mock', 'cortex', 'noor-canvas', etc.)
 * @returns {Promise<Object>} - Complete dashboard data
 */
export async function loadDashboardData(source = 'mock') {
    console.log(`Loading dashboard data from source: ${source}`);
    
    // Check cache first
    const cached = getCachedData(source);
    if (cached) {
        console.log(`Using cached data for ${source}`);
        return cached;
    }
    
    try {
        const basePath = DATA_SOURCES[source];
        if (!basePath) {
            throw new Error(`Unknown data source: ${source}`);
        }
        
        // Load all data files in parallel
        const dataPromises = DATA_FILES.map(file => 
            loadJsonFile(`${basePath}${file}`)
                .catch(error => {
                    console.warn(`Failed to load ${file}:`, error);
                    return null;
                })
        );
        
        const results = await Promise.all(dataPromises);
        
        // Build data object
        const data = {
            source,
            timestamp: new Date().toISOString(),
            healthData: results[0],
            techStack: results[1],
            security: results[2],
            architecture: results[3],
            codeOrganization: results[4],
            teamMetrics: results[5],
            vendors: results[6]
        };
        
        // Validate data (temporarily disabled for debugging)
        const validation = validateDataStructure(data);
        if (!validation.valid) {
            console.warn('Data validation warnings:', validation.errors);
            // Don't throw - allow dashboard to load with warnings
        }
        
        // Cache the data
        cacheData(source, data);
        
        console.log(`Successfully loaded data from ${source}`);
        return data;
        
    } catch (error) {
        console.error(`Error loading dashboard data from ${source}:`, error);
        throw error;
    }
}

/**
 * Load a single JSON file
 * @param {string} url - File URL
 * @returns {Promise<Object>} - Parsed JSON data
 */
async function loadJsonFile(url) {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return await response.json();
}

/**
 * Validate dashboard data structure
 * @param {Object} data - Dashboard data to validate
 * @returns {Object} - Validation result {valid: boolean, errors: string[]}
 */
export function validateDataStructure(data) {
    const errors = [];
    
    // Check required fields
    if (!data.source) errors.push('Missing source');
    if (!data.timestamp) errors.push('Missing timestamp');
    
    // Validate health data
    if (data.healthData) {
        if (!data.healthData.overall_health_score) {
            errors.push('Health data missing overall_health_score');
        }
        if (!data.healthData.status) {
            errors.push('Health data missing status');
        }
    } else {
        errors.push('Missing health data');
    }
    
    // Validate tech stack
    if (data.techStack) {
        if (!Array.isArray(data.techStack.frontend)) {
            errors.push('Tech stack missing frontend array');
        }
        if (!data.techStack.summary) {
            errors.push('Tech stack missing summary');
        }
    } else {
        errors.push('Missing tech stack data');
    }
    
    // Validate security
    if (data.security) {
        if (typeof data.security.overall_score !== 'number') {
            errors.push('Security missing overall_score');
        }
        if (!data.security.vulnerabilities) {
            errors.push('Security missing vulnerabilities');
        }
    } else {
        errors.push('Missing security data');
    }
    
    // Validate architecture
    if (data.architecture) {
        if (!data.architecture.style) {
            errors.push('Architecture missing style');
        }
        if (!Array.isArray(data.architecture.tiers)) {
            errors.push('Architecture missing tiers array');
        }
    } else {
        errors.push('Missing architecture data');
    }
    
    // Validate code organization
    if (data.codeOrganization) {
        if (!Array.isArray(data.codeOrganization.hotspots)) {
            errors.push('Code organization missing hotspots array');
        }
        if (!data.codeOrganization.summary) {
            errors.push('Code organization missing summary');
        }
    } else {
        errors.push('Missing code organization data');
    }
    
    // Validate team metrics
    if (data.teamMetrics) {
        if (!Array.isArray(data.teamMetrics.contributors)) {
            errors.push('Team metrics missing contributors array');
        }
        if (!data.teamMetrics.summary) {
            errors.push('Team metrics missing summary');
        }
    } else {
        errors.push('Missing team metrics data');
    }
    
    // Validate vendors
    if (data.vendors) {
        if (!Array.isArray(data.vendors.vendors)) {
            errors.push('Vendors missing vendors array');
        }
        if (!data.vendors.summary) {
            errors.push('Vendors missing summary');
        }
    } else {
        errors.push('Missing vendors data');
    }
    
    return {
        valid: errors.length === 0,
        errors
    };
}

/**
 * Get cached data if available and not expired
 * @param {string} source - Data source
 * @returns {Object|null} - Cached data or null
 */
function getCachedData(source) {
    const cached = dataCache.get(source);
    if (!cached) return null;
    
    const age = Date.now() - cached.cachedAt;
    if (age > CACHE_DURATION) {
        dataCache.delete(source);
        return null;
    }
    
    return cached.data;
}

/**
 * Cache dashboard data
 * @param {string} source - Data source
 * @param {Object} data - Dashboard data
 */
export function cacheData(source, data) {
    dataCache.set(source, {
        data,
        cachedAt: Date.now()
    });
    
    // Also store in localStorage for persistence
    try {
        localStorage.setItem(`dashboard_${source}`, JSON.stringify({
            data,
            cachedAt: Date.now()
        }));
    } catch (error) {
        console.warn('Failed to cache data in localStorage:', error);
    }
}

/**
 * Clear all cached data
 */
export function clearCache() {
    dataCache.clear();
    
    // Clear localStorage cache
    try {
        Object.keys(localStorage).forEach(key => {
            if (key.startsWith('dashboard_')) {
                localStorage.removeItem(key);
            }
        });
    } catch (error) {
        console.warn('Failed to clear localStorage cache:', error);
    }
    
    console.log('Cache cleared');
}

/**
 * Export data to JSON file
 * @param {Object} data - Data to export
 * @param {string} filename - Output filename
 */
export function exportToJson(data, filename = 'dashboard-data.json') {
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    
    URL.revokeObjectURL(url);
    console.log(`Exported data to ${filename}`);
}

/**
 * Export data to CSV format
 * @param {Object} data - Data to export
 * @param {string} filename - Output filename
 */
export function exportToCsv(data, filename = 'dashboard-data.csv') {
    // Convert to CSV format (simple key-value pairs)
    let csv = 'Category,Metric,Value\n';
    
    if (data.healthData) {
        csv += `Health,Overall Score,${data.healthData.overall_health_score}\n`;
        csv += `Health,Status,${data.healthData.status}\n`;
    }
    
    if (data.techStack && data.techStack.summary) {
        csv += `Tech Stack,Total Technologies,${data.techStack.summary.total_technologies}\n`;
        csv += `Tech Stack,Current Count,${data.techStack.summary.current_count}\n`;
        csv += `Tech Stack,Outdated Count,${data.techStack.summary.outdated_count}\n`;
    }
    
    if (data.security) {
        csv += `Security,Overall Score,${data.security.overall_score}\n`;
        if (data.security.vulnerabilities) {
            csv += `Security,Total Vulnerabilities,${data.security.vulnerabilities.total}\n`;
            csv += `Security,Critical Vulnerabilities,${data.security.vulnerabilities.critical}\n`;
        }
    }
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    
    URL.revokeObjectURL(url);
    console.log(`Exported data to ${filename}`);
}

/**
 * Get available data sources
 * @returns {string[]} - List of available sources
 */
export function getAvailableSources() {
    return Object.keys(DATA_SOURCES);
}

/**
 * Check if a data source is available
 * @param {string} source - Data source to check
 * @returns {Promise<boolean>} - True if source is available
 */
export async function isSourceAvailable(source) {
    try {
        const basePath = DATA_SOURCES[source];
        if (!basePath) return false;
        
        // Try to load metadata file
        const response = await fetch(`${basePath}metadata.json`);
        return response.ok;
    } catch (error) {
        return false;
    }
}

// Export utility functions
export default {
    loadDashboardData,
    validateDataStructure,
    cacheData,
    clearCache,
    exportToJson,
    exportToCsv,
    getAvailableSources,
    isSourceAvailable
};
