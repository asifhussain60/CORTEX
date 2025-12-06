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

// Data source base paths (will be populated from registry)
const DATA_SOURCES = {
    mock: '/data/mock/'
};

// Repository registry (loaded on page load)
let REPOSITORY_REGISTRY = null;

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
 * Load repository registry and populate DATA_SOURCES
 */
async function loadRepositoryRegistry() {
    try {
        const response = await fetch('/data/repository-registry.json');
        if (!response.ok) {
            console.warn('Registry not found, using default sources');
            return null;
        }
        
        const registry = await response.json();
        REPOSITORY_REGISTRY = registry;
        console.log(`Loaded registry: ${registry.total_repositories} repositories`);
        
        // Update DATA_SOURCES from registry
        registry.repositories.forEach(repo => {
            DATA_SOURCES[repo.id] = `/data/repos/${repo.id}/`;
        });
        
        return registry;
    } catch (error) {
        console.error('Failed to load registry:', error);
        return null;
    }
}

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
        // Check if this is a collection trigger
        if (source.startsWith('collect:')) {
            const repoPath = source.substring(8);
            throw new Error(
                `Dashboard data not found for repository: ${repoPath}\n\n` +
                `To generate dashboard data, run:\n` +
                `python -m src.orchestrators.dashboard_collector --path "${repoPath}"`
            );
        }
        
        const basePath = DATA_SOURCES[source];
        if (!basePath) {
            // Provide helpful error with available sources
            const availableSources = Object.keys(DATA_SOURCES).join(', ');
            throw new Error(
                `Unknown data source: ${source}\n\n` +
                `Available sources: ${availableSources}\n\n` +
                `If this is a repository path, ensure dashboard data has been collected first.`
            );
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

/**
 * Extract architecture information from collected data
 * @param {Object} data - Dashboard data
 * @returns {Object} - Structured architecture info
 */
export function extractArchitectureInfo(data) {
    const archInfo = {
        frontend: extractFrontendInfo(data),
        backend: extractBackendInfo(data),
        database: extractDatabaseInfo(data),
        type: 'unknown',
        layers: []
    };
    
    // Determine architecture type
    const hasFrontend = archInfo.frontend && Object.keys(archInfo.frontend).length > 0;
    const hasBackend = archInfo.backend && Object.keys(archInfo.backend).length > 0;
    const hasDatabase = archInfo.database && Object.keys(archInfo.database).length > 0;
    
    if (hasFrontend && hasBackend && hasDatabase) {
        archInfo.type = 'full_stack';
        archInfo.layers = ['Presentation', 'Business Logic', 'Data Access'];
    } else if (hasBackend && hasDatabase && !hasFrontend) {
        archInfo.type = 'api_only';
        archInfo.layers = ['API', 'Business Logic', 'Data Access'];
    } else if (hasFrontend && !hasBackend) {
        archInfo.type = 'spa_only';
        archInfo.layers = ['Presentation', 'Client Services'];
    } else if (hasDatabase && !hasFrontend && !hasBackend) {
        archInfo.type = 'database_only';
        archInfo.layers = ['Database Schema'];
    }
    
    return archInfo;
}

/**
 * Extract frontend information
 */
function extractFrontendInfo(data) {
    const frontend = {};
    
    // Check architecture data
    if (data.architecture && data.architecture.frontend) {
        Object.assign(frontend, data.architecture.frontend);
    }
    
    // Check tech stack for frontend frameworks
    if (data.techStack) {
        const frontendTech = data.techStack.frontend || [];
        if (frontendTech.length > 0) {
            frontend.technologies = frontendTech;
            frontend.framework = frontendTech[0]?.name || 'Unknown';
        }
    }
    
    // Extract component counts if available
    if (data.codeOrganization && data.codeOrganization.components) {
        const components = data.codeOrganization.components;
        frontend.componentCount = components.length || 0;
    }
    
    return frontend;
}

/**
 * Extract backend information
 */
function extractBackendInfo(data) {
    const backend = {};
    
    // Check architecture data
    if (data.architecture && data.architecture.backend) {
        Object.assign(backend, data.architecture.backend);
    }
    
    // Check tech stack for backend frameworks
    if (data.techStack) {
        const backendTech = data.techStack.backend || [];
        if (backendTech.length > 0) {
            backend.technologies = backendTech;
            backend.framework = backendTech[0]?.name || 'Unknown';
        }
    }
    
    // Extract API information if available
    if (data.architecture && data.architecture.apis) {
        backend.apis = data.architecture.apis;
        backend.endpointCount = data.architecture.apis.length || 0;
    }
    
    return backend;
}

/**
 * Extract database information
 */
function extractDatabaseInfo(data) {
    const database = {};
    
    // Check architecture data
    if (data.architecture && data.architecture.database) {
        Object.assign(database, data.architecture.database);
    }
    
    // Check tech stack for database platforms
    if (data.techStack) {
        const dbTech = data.techStack.database || [];
        if (dbTech.length > 0) {
            database.technologies = dbTech;
            database.platform = dbTech[0]?.name || 'Unknown';
        }
    }
    
    // Extract schema information if available
    if (data.codeOrganization && data.codeOrganization.database) {
        const dbInfo = data.codeOrganization.database;
        database.tableCount = dbInfo.tables || 0;
        database.procedureCount = dbInfo.procedures || 0;
        database.viewCount = dbInfo.views || 0;
    }
    
    return database;
}

/**
 * Enrich dashboard data with architecture detection
 * @param {Object} data - Raw dashboard data
 * @returns {Object} - Enriched data with architecture info
 */
export function enrichDashboardData(data) {
    if (!data) return data;
    
    // Add architecture detection
    if (!data.architecture || !data.architecture.type) {
        const archInfo = extractArchitectureInfo(data);
        data.architecture = {
            ...data.architecture,
            ...archInfo
        };
    }
    
    return data;
}

// Initialize registry on module load
(async function initRegistry() {
    await loadRepositoryRegistry();
    console.log('Data loader initialized with registry');
})();

// Export utility functions
export default {
    loadDashboardData,
    validateDataStructure,
    cacheData,
    clearCache,
    exportToJson,
    exportToCsv,
    getAvailableSources,
    isSourceAvailable,
    extractArchitectureInfo,
    enrichDashboardData,
    loadRepositoryRegistry
};
