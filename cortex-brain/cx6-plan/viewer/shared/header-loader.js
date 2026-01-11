/**
 * CORTEX Header Template Loader
 * Version: 1.0.0
 * Author: Asif Hussain
 * Date: 2026-01-11
 * 
 * Purpose: Dynamically load and configure the standardized CORTEX header
 * across all HTML views without code duplication.
 * 
 * Usage:
 * <script src="shared/header-loader.js"></script>
 * <script>
 *   loadCortexHeader({
 *     pageTitle: "Dashboard",
 *     pageDescription: "Implementation Progress Overview",
 *     designScore: "97/95",
 *     breadcrumbs: [
 *       { text: "Home", link: "index.html" },
 *       { text: "Dashboard", link: null }
 *     ]
 *   });
 * </script>
 */

/**
 * Load the CORTEX header template with configuration
 * @param {Object} config - Header configuration
 * @param {string} config.pageTitle - Main page title
 * @param {string} config.pageDescription - Page description
 * @param {string} config.designScore - Design score (e.g., "97/95")
 * @param {Array} config.breadcrumbs - Optional breadcrumb array
 */
async function loadCortexHeader(config = {}) {
    const {
        pageTitle = "Page Title",
        pageDescription = "Page Description",
        designScore = "97/95",
        breadcrumbs = []
    } = config;

    try {
        // Fetch the header template
        const response = await fetch('shared/header-template.html');
        if (!response.ok) {
            throw new Error(`Failed to load header template: ${response.statusText}`);
        }
        
        let template = await response.text();
        
        // Replace template variables
        template = template.replace(/\{\{PAGE_TITLE\}\}/g, pageTitle);
        template = template.replace(/\{\{PAGE_DESCRIPTION\}\}/g, pageDescription);
        template = template.replace(/\{\{DESIGN_SCORE\}\}/g, designScore);
        
        // Generate breadcrumb HTML
        let breadcrumbHtml = '';
        if (breadcrumbs && breadcrumbs.length > 0) {
            breadcrumbHtml = breadcrumbs.map((crumb, index) => {
                const isActive = index === breadcrumbs.length - 1 || !crumb.link;
                if (isActive) {
                    return `<li class="breadcrumb-item active" aria-current="page">${crumb.text}</li>`;
                } else {
                    return `<li class="breadcrumb-item"><a href="${crumb.link}">${crumb.text}</a></li>`;
                }
            }).join('\n');
        }
        
        template = template.replace(/\{\{BREADCRUMB_HTML\}\}/g, breadcrumbHtml);
        
        // Insert template into the page
        const headerContainer = document.getElementById('cortex-header-container');
        if (headerContainer) {
            headerContainer.innerHTML = template;
            
            // Initialize breadcrumb visibility
            const breadcrumbRow = document.getElementById('breadcrumb-row');
            if (breadcrumbRow && breadcrumbs.length > 0) {
                breadcrumbRow.style.display = 'block';
            }
            
            console.log('✅ CORTEX header loaded successfully');
        } else {
            console.error('❌ Container element #cortex-header-container not found');
        }
        
    } catch (error) {
        console.error('❌ Failed to load CORTEX header:', error);
        
        // Fallback: Display basic header
        displayFallbackHeader(config);
    }
}

/**
 * Display a basic fallback header if template loading fails
 */
function displayFallbackHeader(config) {
    const headerContainer = document.getElementById('cortex-header-container');
    if (!headerContainer) return;
    
    const { pageTitle, pageDescription, designScore } = config;
    
    headerContainer.innerHTML = `
        <div class="header-glow" style="padding: 1rem 0; background: linear-gradient(135deg, #00d4ff33, #7b2cbf33);">
            <div class="container-fluid">
                <div class="row align-items-center">
                    <div class="col">
                        <h1 style="color: #00d4ff; margin-bottom: 0.25rem;">
                            CORTEX 6.0 | ${pageTitle}
                        </h1>
                        <p style="color: rgba(255,255,255,0.7); margin: 0; font-size: 0.9rem;">
                            ${pageDescription}
                        </p>
                    </div>
                    <div class="col-auto">
                        <div style="background: rgba(6,255,165,0.15); border: 1px solid #06ffa5; 
                                    border-radius: 8px; padding: 0.5rem 1rem; color: #06ffa5;">
                            Design Score: ${designScore}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    console.warn('⚠️  Using fallback header (template unavailable)');
}

/**
 * Update design score dynamically after page load
 * @param {string} newScore - New score value (e.g., "98/95")
 */
function updateDesignScore(newScore) {
    const scoreElement = document.querySelector('.score-value');
    if (scoreElement) {
        scoreElement.textContent = newScore;
        
        // Update badge styling based on score
        const badge = document.querySelector('.design-score-badge');
        if (badge) {
            const [current, target] = newScore.split('/').map(Number);
            
            if (current >= target) {
                badge.style.borderColor = 'var(--cortex-green)';
                badge.style.background = 'rgba(6, 255, 165, 0.15)';
            } else if (current >= target * 0.9) {
                badge.style.borderColor = 'var(--cortex-yellow)';
                badge.style.background = 'rgba(255, 190, 11, 0.15)';
            } else {
                badge.style.borderColor = 'var(--cortex-pink)';
                badge.style.background = 'rgba(255, 0, 110, 0.15)';
            }
        }
        
        console.log(`✅ Design score updated to ${newScore}`);
    }
}

/**
 * Load design score from master plan YAML
 * Requires YAML parser library (js-yaml)
 */
async function loadDesignScoreFromPlan() {
    try {
        const response = await fetch('../master-plan.yaml');
        if (!response.ok) return null;
        
        const yamlText = await response.text();
        
        // Simple regex extraction (for basic cases without full YAML parser)
        const match = yamlText.match(/design_score:\s*(\d+)/);
        if (match) {
            const score = match[1];
            return `${score}/95`;
        }
        
        return null;
    } catch (error) {
        console.warn('⚠️  Could not load design score from master plan:', error);
        return null;
    }
}

/**
 * Initialize header on page load
 * Automatically called if cortex-header-config is defined
 */
document.addEventListener('DOMContentLoaded', async () => {
    // Check if configuration is provided
    if (typeof cortexHeaderConfig !== 'undefined') {
        await loadCortexHeader(cortexHeaderConfig);
        
        // Optionally load design score from plan
        if (cortexHeaderConfig.loadScoreFromPlan) {
            const liveScore = await loadDesignScoreFromPlan();
            if (liveScore) {
                updateDesignScore(liveScore);
            }
        }
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        loadCortexHeader,
        updateDesignScore,
        loadDesignScoreFromPlan
    };
}
