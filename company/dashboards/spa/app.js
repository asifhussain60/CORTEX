/**
 * CORTEX Dashboard SPA Controller
 * Unified application controller for repository dashboards
 * 
 * Authority: Phase 53 Stage 1 - Unified SPA Foundation
 * Features:
 * - URL parameter routing (?repo=cortex)
 * - JSON data loading via Fetch API
 * - HTTP vs file:// protocol detection
 * - Data binding to DOM elements
 * - Tab navigation
 * - Accessibility compliance
 */

// ============================================================================
// CONFIGURATION & CONSTANTS
// ============================================================================

const CONFIG = {
    REPOSITORIES: ["cortex", "ksessions", "kashkole", "alist", "noor-canvas"],
    DATA_DIR: "./data",
    SUPPORTED_TABS: ["overview", "architecture", "quality", "security", "vulnerabilities", "dependencies", "patterns", "testing", "usecases"],
    CACHE_TTL_MS: 5 * 60 * 1000, // 5 minutes
};

// Global state
const APP_STATE = {
    initialized: false,
    currentRepo: null,
    dashboardData: null,
    cache: new Map(),
    cacheTimestamps: new Map(),
};

// ============================================================================
// PROTOCOL DETECTION
// ============================================================================

/**
 * Detect if SPA is served via HTTP or file:// protocol
 * @returns {string} "http" or "file"
 */
function detectProtocol() {
    return window.location.protocol.startsWith("http") ? "http" : "file";
}

/**
 * Get base URL for data loading
 * @returns {string} Base URL path
 */
function getDataBaseUrl() {
    const protocol = detectProtocol();
    
    if (protocol === "http") {
        // HTTP: use relative path
        return "./data";
    } else {
        // file:// protocol: use absolute file path
        return window.location.pathname.replace("/index.html", "") + "/data";
    }
}

// ============================================================================
// URL PARAMETER PARSING
// ============================================================================

/**
 * Parse URL parameters
 * @returns {Object} Parsed query parameters
 */
function parseUrlParameters() {
    const params = new URLSearchParams(window.location.search);
    return {
        repo: params.get("repo") || null,
    };
}

/**
 * Validate repository name
 * @param {string} repoName Repository name
 * @returns {boolean} True if valid
 */
function validateRepoName(repoName) {
    if (!repoName) return false;
    return CONFIG.REPOSITORIES.includes(repoName.toLowerCase());
}

/**
 * Get data file path for repository
 * @param {string} repoName Repository name
 * @returns {string} Path to data JSON file
 */
function getDataFilePath(repoName) {
    const baseUrl = getDataBaseUrl();
    return `${baseUrl}/${repoName.toLowerCase()}.json`;
}

// ============================================================================
// DATA LOADING & CACHING
// ============================================================================

/**
 * Load JSON data for repository
 * @param {string} repoName Repository name
 * @returns {Promise<Object>} Parsed JSON data
 */
async function loadDashboardData(repoName) {
    // Check cache
    if (APP_STATE.cache.has(repoName)) {
        const timestamp = APP_STATE.cacheTimestamps.get(repoName);
        if (Date.now() - timestamp < CONFIG.CACHE_TTL_MS) {
            console.log(`[Cache HIT] ${repoName}`);
            return APP_STATE.cache.get(repoName);
        }
    }

    try {
        // FILE PROTOCOL FIX: Check for embedded data first (CORS workaround)
        const embeddedDataElement = document.getElementById(`data-${repoName}`);
        if (embeddedDataElement) {
            console.log(`[Loading] Embedded data for ${repoName}`);
            const data = JSON.parse(embeddedDataElement.textContent);
            
            // Cache data
            APP_STATE.cache.set(repoName, data);
            APP_STATE.cacheTimestamps.set(repoName, Date.now());
            
            console.log(`[Loaded] ${repoName} from embedded data (${Object.keys(data).length} sections)`);
            return data;
        }
        
        // Fallback to fetch for HTTP protocol
        const dataPath = getDataFilePath(repoName);
        console.log(`[Loading] ${dataPath}`);
        
        const response = await fetch(dataPath);
        
        if (!response.ok) {
            if (response.status === 404) {
                throw new Error(`Dashboard data not found for ${repoName}`);
            }
            throw new Error(`Failed to load dashboard: ${response.statusText}`);
        }

        const data = await response.json();
        
        // Validate schema
        if (!data.repository || !data.overview) {
            throw new Error(`Invalid dashboard schema for ${repoName}`);
        }

        // Cache data
        APP_STATE.cache.set(repoName, data);
        APP_STATE.cacheTimestamps.set(repoName, Date.now());
        
        console.log(`[Loaded] ${repoName} (${Object.keys(data).length} sections)`);
        return data;
    } catch (error) {
        console.error(`[Error] Failed to load ${repoName}:`, error);
        throw error;
    }
}

// ============================================================================
// DATA BINDING
// ============================================================================

/**
 * Bind data to DOM element using data-bind attribute
 * @param {Element} element DOM element with data-bind attribute
 * @param {Object} data Dashboard data object
 */
function bindData(element, data) {
    const bindPath = element.getAttribute("data-bind");
    if (!bindPath) return;

    const value = getNestedValue(data, bindPath);
    
    if (value !== undefined && value !== null) {
        if (element.tagName === "DIV" || element.tagName === "P" || element.tagName === "SPAN") {
            element.textContent = value;
        } else if (element.tagName === "INPUT") {
            element.value = value;
        }
    } else {
        // Use fallback
        const fallback = element.getAttribute("data-fallback");
        if (fallback) {
            element.textContent = fallback;
        }
    }
}

/**
 * Get nested value from object using dot notation
 * @param {Object} obj Object to query
 * @param {string} path Dot-notation path (e.g., "repository.health_score")
 * @returns {*} Value or undefined
 */
function getNestedValue(obj, path) {
    return path.split(".").reduce((current, prop) => current?.[prop], obj);
}

/**
 * Bind all data-bind elements in DOM
 * @param {Object} data Dashboard data
 */
function bindAllData(data) {
    const bindElements = document.querySelectorAll("[data-bind]");
    
    bindElements.forEach(element => {
        bindData(element, data);
    });
}

/**
 * Show/hide elements based on data-show-if attribute
 * @param {Object} data Dashboard data
 */
function applyConditionalVisibility(data) {
    const conditionalElements = document.querySelectorAll("[data-show-if]");
    
    conditionalElements.forEach(element => {
        const fieldPath = element.getAttribute("data-show-if");
        const value = getNestedValue(data, fieldPath);
        
        // Show if field exists and is truthy (or non-empty array/object)
        const shouldShow = value && (
            typeof value === "object" ? Object.keys(value).length > 0 : true
        );
        
        element.style.display = shouldShow ? "" : "none";
    });
}

// ============================================================================
// TAB NAVIGATION
// ============================================================================

/**
 * Initialize tab navigation
 */
function initializeTabs() {
    const tabButtons = document.querySelectorAll(".tab-button");
    const tabPanels = document.querySelectorAll(".tab-panel");

    tabButtons.forEach(button => {
        button.addEventListener("click", () => {
            const tabName = button.getAttribute("data-tab");
            switchTab(tabName, tabButtons, tabPanels);
        });
    });
}

/**
 * Switch to specified tab
 * @param {string} tabName Tab name to switch to
 * @param {NodeList} tabButtons All tab buttons
 * @param {NodeList} tabPanels All tab panels
 */
function switchTab(tabName, tabButtons, tabPanels) {
    // Deactivate all
    tabButtons.forEach(btn => btn.classList.remove("active"));
    tabPanels.forEach(panel => {
        panel.classList.remove("active");
        panel.style.display = "none";
    });

    // Activate selected
    document.querySelector(`[data-tab="${tabName}"]`)?.classList.add("active");
    const panel = document.getElementById(`panel-${tabName}`);
    if (panel) {
        panel.classList.add("active");
        panel.style.display = "";
    }
}

// ============================================================================
// UI STATE MANAGEMENT
// ============================================================================

/**
 * Show loading spinner
 */
function showLoading() {
    document.getElementById("loading-spinner").style.display = "flex";
    document.getElementById("tab-navigation").style.display = "none";
    document.querySelector(".tab-panels").style.display = "none";
}

/**
 * Hide loading spinner
 */
function hideLoading() {
    document.getElementById("loading-spinner").style.display = "none";
    document.getElementById("tab-navigation").style.display = "flex";
    document.querySelector(".tab-panels").style.display = "block";
}

/**
 * Show error message
 * @param {string} message Error message to display
 */
function showError(message) {
    document.getElementById("error-text").textContent = message;
    document.getElementById("error-message").style.display = "flex";
    document.getElementById("tab-navigation").style.display = "none";
    document.querySelector(".tab-panels").style.display = "none";
}

/**
 * Hide error message
 */
function hideError() {
    document.getElementById("error-message").style.display = "none";
}

// ============================================================================
// REPOSITORY SELECTOR
// ============================================================================

/**
 * Render repository selector list
 */
function renderRepositoryList() {
    const repoList = document.getElementById("repo-list");
    repoList.innerHTML = "";

    CONFIG.REPOSITORIES.forEach(repo => {
        const repoItem = document.createElement("div");
        repoItem.className = "repo-item";
        repoItem.innerHTML = `
            <button class="repo-tile" data-repo="${repo}">
                <i class="fas fa-folder"></i>
                <span>${repo.replace("-", " ").toUpperCase()}</span>
            </button>
        `;
        repoList.appendChild(repoItem);

        repoItem.querySelector(".repo-tile").addEventListener("click", (e) => {
            e.preventDefault();
            selectRepository(repo);
        });
    });
}

/**
 * Select repository and navigate to it
 * @param {string} repoName Repository name
 */
function selectRepository(repoName) {
    const url = new URL(window.location);
    url.searchParams.set("repo", repoName);
    window.location.href = url.toString();
}

/**
 * Initialize repository selector modal
 */
function initializeRepositorySelector() {
    const modalBtn = document.getElementById("repo-selector-btn");
    const modal = document.getElementById("repo-modal");
    const closeBtn = document.getElementById("modal-close");

    modalBtn.addEventListener("click", () => {
        modal.style.display = "flex";
        renderRepositoryList();
    });

    closeBtn.addEventListener("click", () => {
        modal.style.display = "none";
    });

    // Close on background click
    modal.addEventListener("click", (e) => {
        if (e.target === modal) {
            modal.style.display = "none";
        }
    });

    // Back button in error state
    document.getElementById("error-back-btn").addEventListener("click", () => {
        modal.style.display = "flex";
        renderRepositoryList();
        hideError();
    });
}

// ============================================================================
// MAIN APPLICATION FLOW
// ============================================================================

/**
 * Initialize application
 */
async function initializeApp() {
    console.log("[Init] Starting SPA initialization...");
    
    // Parse URL parameters
    const params = parseUrlParameters();
    const repoName = params.repo;

    // If no repo specified, show repository selector
    if (!repoName) {
        console.log("[Init] No repository specified, showing selector");
        document.getElementById("repo-modal").style.display = "flex";
        renderRepositoryList();
        APP_STATE.initialized = true;
        return;
    }

    // Validate repo name
    if (!validateRepoName(repoName)) {
        console.error(`[Error] Invalid repository: ${repoName}`);
        showError(`Invalid repository: ${repoName}`);
        return;
    }

    // Load dashboard data
    showLoading();
    try {
        const data = await loadDashboardData(repoName);
        APP_STATE.currentRepo = repoName;
        APP_STATE.dashboardData = data;

        // Update UI
        hideLoading();
        bindAllData(data);
        applyConditionalVisibility(data);
        initializeTabs();
        
        console.log(`[Init] Dashboard ready for ${repoName}`);
    } catch (error) {
        console.error("[Error] Failed to initialize dashboard:", error);
        hideLoading();
        showError(error.message);
    }

    // Initialize repository selector
    initializeRepositorySelector();
    APP_STATE.initialized = true;
}

// ============================================================================
// ENTRY POINT
// ============================================================================

// Initialize when DOM is ready
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeApp);
} else {
    initializeApp();
}

console.log("[App] Dashboard SPA loaded successfully");
