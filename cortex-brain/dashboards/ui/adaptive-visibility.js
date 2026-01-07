/**
 * Adaptive Visibility Engine
 * 
 * Intelligently shows/hides dashboard sections based on project architecture.
 * Detects project type (API-only, SPA-only, Full-Stack, Database-only) and
 * adapts UI accordingly.
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Source-Available (Use Allowed, No Contributions)
 */

/**
 * Project type profiles
 */
const PROJECT_PROFILES = {
    api_only: {
        show: ['backend', 'database', 'metrics', 'security', 'team'],
        hide: ['frontend', 'ui-components']
    },
    spa_only: {
        show: ['frontend', 'ui-components', 'metrics', 'security', 'team'],
        hide: ['backend', 'database']
    },
    full_stack: {
        show: ['frontend', 'backend', 'database', 'ui-components', 'metrics', 'security', 'team'],
        hide: []
    },
    database_only: {
        show: ['database', 'metrics', 'security'],
        hide: ['frontend', 'backend', 'ui-components', 'team']
    },
    unknown: {
        show: ['metrics', 'security', 'team'],
        hide: []
    }
};

/**
 * Detect project type from architecture data
 * @param {Object} data - Dashboard data with architecture information
 * @returns {string} - Project profile type
 */
export function detectProjectType(data) {
    if (!data) return 'unknown';
    
    // Check for architecture data
    const architecture = data.architecture || {};
    const frontend = data.frontend || architecture.frontend || {};
    const backend = data.backend || architecture.backend || {};
    const database = data.database || architecture.database || {};
    const techStack = data.techStack || {};
    
    // Analyze what exists
    const hasFrontend = hasValidData(frontend) || 
                        hasTechnologyStack(techStack, ['typescript', 'javascript', 'angular', 'react', 'vue']);
    const hasBackend = hasValidData(backend) || 
                       hasTechnologyStack(techStack, ['csharp', 'python', 'java', 'coldfusion']);
    const hasDatabase = hasValidData(database) || 
                        hasTechnologyStack(techStack, ['sql', 'database', 'oracle', 'mysql']);
    
    // Classify project type
    if (hasFrontend && hasBackend && hasDatabase) {
        return 'full_stack';
    } else if (hasBackend && hasDatabase && !hasFrontend) {
        return 'api_only';
    } else if (hasFrontend && !hasBackend) {
        return 'spa_only';
    } else if (hasDatabase && !hasFrontend && !hasBackend) {
        return 'database_only';
    }
    
    return 'unknown';
}

/**
 * Check if object has valid data (non-empty, non-null values)
 */
function hasValidData(obj) {
    if (!obj || typeof obj !== 'object') return false;
    
    // Check if object has any non-empty values
    return Object.keys(obj).length > 0 && 
           Object.values(obj).some(val => {
               if (Array.isArray(val)) return val.length > 0;
               if (typeof val === 'object' && val !== null) return Object.keys(val).length > 0;
               if (typeof val === 'number') return val > 0;
               if (typeof val === 'string') return val.length > 0;
               return val != null;
           });
}

/**
 * Check if technology stack contains specific technologies
 */
function hasTechnologyStack(techStack, keywords) {
    if (!techStack) return false;
    
    const stackStr = JSON.stringify(techStack).toLowerCase();
    return keywords.some(keyword => stackStr.includes(keyword.toLowerCase()));
}

/**
 * Apply adaptive visibility to dashboard sections
 * @param {string} projectType - Detected project type
 */
export function applyAdaptiveVisibility(projectType) {
    console.log(`[Adaptive Visibility] Applying profile: ${projectType}`);
    
    const profile = PROJECT_PROFILES[projectType] || PROJECT_PROFILES.unknown;
    
    // Show applicable sections
    profile.show.forEach(sectionId => {
        const section = document.querySelector(`[data-section="${sectionId}"]`);
        if (section) {
            section.style.display = '';
            section.classList.remove('hidden');
            console.log(`  ✅ Showing: ${sectionId}`);
        }
    });
    
    // Hide non-applicable sections
    profile.hide.forEach(sectionId => {
        const section = document.querySelector(`[data-section="${sectionId}"]`);
        if (section) {
            section.style.display = 'none';
            section.classList.add('hidden');
            console.log(`  ❌ Hiding: ${sectionId}`);
        }
    });
    
    // Update UI with project type badge
    updateProjectTypeBadge(projectType);
}

/**
 * Update project type badge in UI
 */
function updateProjectTypeBadge(projectType) {
    const badge = document.getElementById('project-type-badge');
    if (!badge) return;
    
    const typeLabels = {
        api_only: '🔌 API Project',
        spa_only: '🎨 SPA Application',
        full_stack: '🏗️ Full-Stack Application',
        database_only: '🗄️ Database Project',
        unknown: '❓ Unknown Type'
    };
    
    badge.textContent = typeLabels[projectType] || typeLabels.unknown;
    badge.className = `repo-type ${projectType}`;
}

/**
 * Get section visibility status
 * @param {string} sectionId - Section identifier
 * @returns {boolean} - True if section should be visible
 */
export function shouldShowSection(sectionId, data) {
    const projectType = detectProjectType(data);
    const profile = PROJECT_PROFILES[projectType] || PROJECT_PROFILES.unknown;
    
    // If explicitly hidden, return false
    if (profile.hide.includes(sectionId)) {
        return false;
    }
    
    // If explicitly shown or unknown profile, return true
    if (profile.show.includes(sectionId) || projectType === 'unknown') {
        return true;
    }
    
    // Default: show
    return true;
}

/**
 * Initialize adaptive visibility system
 * @param {Object} data - Dashboard data
 */
export function initializeAdaptiveVisibility(data) {
    console.log('[Adaptive Visibility] Initializing...');
    
    try {
        const projectType = detectProjectType(data);
        console.log(`[Adaptive Visibility] Detected type: ${projectType}`);
        
        applyAdaptiveVisibility(projectType);
        
        console.log('[Adaptive Visibility] Initialization complete');
        return projectType;
    } catch (error) {
        console.error('[Adaptive Visibility] Initialization failed:', error);
        return 'unknown';
    }
}

/**
 * Get human-readable description of project type
 */
export function getProjectTypeDescription(projectType) {
    const descriptions = {
        api_only: 'Backend API service with database integration. Focus on endpoints, business logic, and data access.',
        spa_only: 'Frontend single-page application. Focus on UI components, state management, and user experience.',
        full_stack: 'Complete application with frontend, backend, and database layers. Full system visibility.',
        database_only: 'Database schema and stored procedures. Focus on data structures and query performance.',
        unknown: 'Mixed or unrecognized architecture. All available sections displayed.'
    };
    
    return descriptions[projectType] || descriptions.unknown;
}
