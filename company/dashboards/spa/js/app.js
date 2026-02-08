/**
 * CORTEX Dashboard SPA Controller
 * Manages data loading, routing, and UI interactions
 * 
 * Version: 2.0.0
 * Features:
 * - URL parameter routing (?repo=name)
 * - Embedded data pattern (file:// protocol support)
 * - Tab navigation with history
 * - Responsive data binding
 * 
 * Last Updated: 2026-02-08
 */

// ============================================================================
// CONFIGURATION
// ============================================================================

const CONFIG = {
    REPOSITORIES: ['cortex', 'ksessions', 'kashkole', 'alist', 'noor-canvas'],
    DATA_DIR: './data',
    DEFAULT_REPO: 'ksessions',
    TABS: [
        { id: 'overview', icon: 'fas fa-chart-line', label: 'Overview' },
        { id: 'architecture', icon: 'fas fa-sitemap', label: 'Architecture' },
        { id: 'quality', icon: 'fas fa-medal', label: 'Quality' },
        { id: 'security', icon: 'fas fa-shield-alt', label: 'Security' },
        { id: 'dependencies', icon: 'fas fa-cubes', label: 'Dependencies' }
    ]
};

// ============================================================================
// APPLICATION STATE
// ============================================================================

const AppState = {
    currentRepo: null,
    currentTab: 'overview',
    data: null,
    isLoading: false,
    cache: new Map()
};

// ============================================================================
// DOM ELEMENTS
// ============================================================================

let DOM = {};

function initDOMReferences() {
    DOM = {
        // Loading
        loadingOverlay: document.getElementById('loading-overlay'),
        
        // Navigation
        repoTitle: document.getElementById('repo-title'),
        repoSubtitle: document.getElementById('repo-subtitle'),
        statusTdd: document.getElementById('status-tdd'),
        statusGit: document.getElementById('status-git'),
        statusErrors: document.getElementById('status-errors'),
        
        // Tabs
        tabNav: document.getElementById('tab-nav'),
        tabContents: document.querySelectorAll('.tab-content'),
        
        // Modal
        modalOverlay: document.getElementById('modal-overlay'),
        modalClose: document.getElementById('modal-close'),
        repoGrid: document.getElementById('repo-grid'),
        repoSelectorBtn: document.getElementById('repo-selector-btn'),
        
        // Metrics
        healthScore: document.getElementById('health-score'),
        primaryLang: document.getElementById('primary-lang'),
        totalFiles: document.getElementById('total-files'),
        lastUpdated: document.getElementById('last-updated'),
        
        // Visualizations
        vizLanguages: document.getElementById('viz-languages'),
        vizHealth: document.getElementById('viz-health'),
        vizSecurity: document.getElementById('viz-security'),
        vizDeps: document.getElementById('viz-deps'),
        vizFiles: document.getElementById('viz-files'),
        
        // Content areas
        overviewSummary: document.getElementById('overview-summary'),
        keyFindings: document.getElementById('key-findings'),
        depTable: document.getElementById('dep-table'),
        secVulnList: document.getElementById('sec-vuln-list')
    };
}

// ============================================================================
// URL HANDLING
// ============================================================================

function parseUrlParams() {
    const params = new URLSearchParams(window.location.search);
    return {
        repo: params.get('repo')
    };
}

function updateUrl(repo) {
    const url = new URL(window.location);
    url.searchParams.set('repo', repo);
    window.history.pushState({ repo }, '', url);
}

// ============================================================================
// DATA LOADING
// ============================================================================

async function loadRepoData(repoName) {
    // Check cache
    if (AppState.cache.has(repoName)) {
        console.log(`[Cache HIT] ${repoName}`);
        return AppState.cache.get(repoName);
    }
    
    // Try embedded data first (file:// protocol)
    const embeddedEl = document.getElementById(`data-${repoName}`);
    if (embeddedEl) {
        try {
            const data = JSON.parse(embeddedEl.textContent);
            AppState.cache.set(repoName, data);
            console.log(`[Embedded] Loaded ${repoName}`);
            return data;
        } catch (e) {
            console.error(`[Embedded] Parse error for ${repoName}:`, e);
        }
    }
    
    // Fallback to fetch (HTTP)
    try {
        const response = await fetch(`${CONFIG.DATA_DIR}/${repoName}.json`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        AppState.cache.set(repoName, data);
        console.log(`[Fetch] Loaded ${repoName}`);
        return data;
    } catch (e) {
        console.error(`[Fetch] Error loading ${repoName}:`, e);
        throw e;
    }
}

// ============================================================================
// UI UPDATES
// ============================================================================

function showLoading(show) {
    AppState.isLoading = show;
    if (DOM.loadingOverlay) {
        DOM.loadingOverlay.classList.toggle('hidden', !show);
    }
}

function updateHeader(data) {
    const repo = data.repo || {};
    const metrics = data.metrics || {};
    
    // Title & subtitle
    if (DOM.repoTitle) {
        DOM.repoTitle.textContent = repo.display_name || repo.slug || 'Dashboard';
    }
    if (DOM.repoSubtitle) {
        DOM.repoSubtitle.textContent = repo.description || 'Repository analytics';
    }
    
    // Status badges
    updateStatusBadges(data);
}

function updateStatusBadges(data) {
    const security = data.security || {};
    const hasVulns = (security.critical_count || 0) + (security.high_count || 0) > 0;
    
    // TDD Status (demo - always pass)
    if (DOM.statusTdd) {
        DOM.statusTdd.className = 'status-badge success';
        DOM.statusTdd.innerHTML = '<i class="fas fa-vial"></i> TDD Pass';
    }
    
    // Git Status (demo - always clean)
    if (DOM.statusGit) {
        DOM.statusGit.className = 'status-badge success';
        DOM.statusGit.innerHTML = '<i class="fab fa-git-alt"></i> Git Clean';
    }
    
    // Error Status
    if (DOM.statusErrors) {
        if (hasVulns) {
            DOM.statusErrors.className = 'status-badge warning';
            DOM.statusErrors.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${security.total_count || 0} Issues`;
        } else {
            DOM.statusErrors.className = 'status-badge success';
            DOM.statusErrors.innerHTML = '<i class="fas fa-check-circle"></i> 0 Errors';
        }
    }
}

function updateMetrics(data) {
    const repo = data.repo || {};
    const metrics = data.metrics || {};
    const languages = metrics.languages || {};
    
    // Health Score
    if (DOM.healthScore) {
        DOM.healthScore.textContent = metrics.health_score || 0;
    }
    
    // Primary Language
    if (DOM.primaryLang) {
        const sortedLangs = Object.entries(languages).sort((a, b) => b[1] - a[1]);
        DOM.primaryLang.textContent = sortedLangs[0]?.[0] || 'N/A';
    }
    
    // Total Files
    if (DOM.totalFiles) {
        DOM.totalFiles.textContent = metrics.files || Object.keys(languages).length;
    }
    
    // Last Updated
    if (DOM.lastUpdated) {
        const date = repo.last_analyzed_at ? new Date(repo.last_analyzed_at) : new Date();
        DOM.lastUpdated.textContent = date.toISOString().split('T')[0];
    }
}

function updateOverview(data) {
    const overview = data.overview || {};
    
    // Business summary
    if (DOM.overviewSummary) {
        DOM.overviewSummary.innerHTML = overview.business_summary || overview.summary || 'No summary available.';
    }
    
    // Key findings
    if (DOM.keyFindings && overview.key_findings) {
        DOM.keyFindings.innerHTML = overview.key_findings
            .map(finding => `
                <li>
                    <i class="fas fa-check-circle" style="color: var(--accent-tertiary); margin-right: 8px;"></i>
                    ${finding}
                </li>
            `).join('');
    }
}

function updateDependencies(data) {
    const deps = data.dependencies || {};
    const packages = deps.packages || [];
    
    if (DOM.depTable) {
        const rows = packages.slice(0, 20).map(pkg => `
            <tr>
                <td style="font-family: var(--font-mono); color: var(--accent-primary);">${pkg.name}</td>
                <td style="font-family: var(--font-mono);">${pkg.version || 'N/A'}</td>
                <td>
                    <span class="badge ${pkg.is_direct ? 'badge-info' : 'badge-success'}">
                        ${pkg.is_direct ? 'Direct' : 'Transitive'}
                    </span>
                </td>
                <td>${pkg.license || '—'}</td>
            </tr>
        `).join('');
        
        DOM.depTable.innerHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Package</th>
                        <th>Version</th>
                        <th>Type</th>
                        <th>License</th>
                    </tr>
                </thead>
                <tbody>${rows}</tbody>
            </table>
            <p class="text-muted mt-md">Showing ${Math.min(20, packages.length)} of ${deps.total_count || packages.length} packages</p>
        `;
    }
}

function updateSecurity(data) {
    const security = data.security || {};
    const vulns = security.vulnerabilities || [];
    
    if (DOM.secVulnList) {
        if (vulns.length === 0) {
            DOM.secVulnList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-shield-alt"></i>
                    <h3 style="color: var(--status-success);">All Clear!</h3>
                    <p>No security vulnerabilities detected in this repository.</p>
                </div>
            `;
        } else {
            DOM.secVulnList.innerHTML = vulns.slice(0, 10).map(vuln => `
                <div class="glass-card mb-md" style="padding: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 600;">${vuln.id || vuln.cve || 'Unknown'}</span>
                        <span class="badge badge-${getSeverityClass(vuln.severity)}">${vuln.severity}</span>
                    </div>
                    <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.9rem;">
                        ${vuln.description || 'No description available'}
                    </p>
                </div>
            `).join('');
        }
    }
}

function getSeverityClass(severity) {
    const map = { critical: 'danger', high: 'warning', medium: 'info', low: 'success' };
    return map[severity?.toLowerCase()] || 'info';
}

// ============================================================================
// VISUALIZATIONS
// ============================================================================

function renderVisualizations(data) {
    const metrics = data.metrics || {};
    const security = data.security || {};
    const deps = data.dependencies || {};
    
    // Delay to ensure DOM is ready
    requestAnimationFrame(() => {
        // Language sunburst
        if (DOM.vizLanguages && metrics.languages && window.CortexViz) {
            CortexViz.createLanguageSunburst('viz-languages', metrics.languages);
        }
        
        // Health gauge
        if (DOM.vizHealth && window.CortexViz) {
            CortexViz.createHealthGauge('viz-health', metrics.health_score || 0);
        }
        
        // Security donut
        if (DOM.vizSecurity && window.CortexViz) {
            CortexViz.createSecurityDonut('viz-security', security);
        }
        
        // Dependency graph
        if (DOM.vizDeps && deps.packages && window.CortexViz) {
            CortexViz.createDependencyGraph('viz-deps', deps.packages);
        }
        
        // File treemap
        if (DOM.vizFiles && metrics.languages && window.CortexViz) {
            CortexViz.createFileTree('viz-files', metrics);
        }
    });
}

// ============================================================================
// TAB NAVIGATION
// ============================================================================

function initTabs() {
    if (!DOM.tabNav) return;
    
    // Render tab buttons
    DOM.tabNav.innerHTML = CONFIG.TABS.map(tab => `
        <button class="tab-btn ${tab.id === AppState.currentTab ? 'active' : ''}" 
                data-tab="${tab.id}">
            <i class="${tab.icon}"></i>
            ${tab.label}
        </button>
    `).join('');
    
    // Event listeners
    DOM.tabNav.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });
}

function switchTab(tabId) {
    AppState.currentTab = tabId;
    
    // Update buttons
    DOM.tabNav?.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabId);
    });
    
    // Update content
    DOM.tabContents?.forEach(content => {
        content.classList.toggle('active', content.id === `tab-${tabId}`);
    });
    
    // Re-render visualizations for the tab
    if (AppState.data) {
        renderVisualizations(AppState.data);
    }
}

// ============================================================================
// MODAL
// ============================================================================

function initModal() {
    // Open modal
    DOM.repoSelectorBtn?.addEventListener('click', openModal);
    
    // Close modal
    DOM.modalClose?.addEventListener('click', closeModal);
    DOM.modalOverlay?.addEventListener('click', (e) => {
        if (e.target === DOM.modalOverlay) closeModal();
    });
    
    // Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && DOM.modalOverlay?.classList.contains('active')) {
            closeModal();
        }
    });
    
    // Populate repo grid
    if (DOM.repoGrid) {
        DOM.repoGrid.innerHTML = CONFIG.REPOSITORIES.map(repo => `
            <div class="repo-card ${repo === AppState.currentRepo ? 'active' : ''}" 
                 data-repo="${repo}">
                <div class="repo-name">${repo.toUpperCase()}</div>
                <div class="repo-lang">Repository</div>
            </div>
        `).join('');
        
        DOM.repoGrid.querySelectorAll('.repo-card').forEach(card => {
            card.addEventListener('click', () => {
                const repo = card.dataset.repo;
                closeModal();
                loadRepository(repo);
            });
        });
    }
}

function openModal() {
    DOM.modalOverlay?.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    DOM.modalOverlay?.classList.remove('active');
    document.body.style.overflow = '';
}

// ============================================================================
// MAIN LOADER
// ============================================================================

async function loadRepository(repoName) {
    if (!CONFIG.REPOSITORIES.includes(repoName)) {
        console.warn(`Unknown repository: ${repoName}`);
        repoName = CONFIG.DEFAULT_REPO;
    }
    
    showLoading(true);
    AppState.currentRepo = repoName;
    updateUrl(repoName);
    
    try {
        AppState.data = await loadRepoData(repoName);
        
        // Update all UI
        updateHeader(AppState.data);
        updateMetrics(AppState.data);
        updateOverview(AppState.data);
        updateDependencies(AppState.data);
        updateSecurity(AppState.data);
        renderVisualizations(AppState.data);
        
        // Update modal selection
        DOM.repoGrid?.querySelectorAll('.repo-card').forEach(card => {
            card.classList.toggle('active', card.dataset.repo === repoName);
        });
        
        console.log(`✅ Loaded ${repoName}`);
    } catch (error) {
        console.error(`❌ Failed to load ${repoName}:`, error);
        showError(repoName, error);
    } finally {
        showLoading(false);
    }
}

function showError(repoName, error) {
    if (DOM.overviewSummary) {
        DOM.overviewSummary.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-exclamation-circle" style="color: var(--status-danger);"></i>
                <h3>Failed to Load Dashboard</h3>
                <p>Could not load data for <strong>${repoName}</strong>.</p>
                <p class="text-muted">${error.message}</p>
                <button class="btn btn-primary mt-md" onclick="loadRepository('${CONFIG.DEFAULT_REPO}')">
                    <i class="fas fa-sync"></i> Try Default
                </button>
            </div>
        `;
    }
}

// ============================================================================
// INITIALIZATION
// ============================================================================

function init() {
    console.log('🚀 CORTEX Dashboard SPA initializing...');
    
    // Initialize DOM references
    initDOMReferences();
    
    // Initialize tabs
    initTabs();
    
    // Initialize modal
    initModal();
    
    // Parse URL and load repository
    const { repo } = parseUrlParams();
    const targetRepo = repo || CONFIG.DEFAULT_REPO;
    
    loadRepository(targetRepo);
    
    // Handle browser back/forward
    window.addEventListener('popstate', (e) => {
        if (e.state?.repo) {
            loadRepository(e.state.repo);
        }
    });
    
    console.log('✅ CORTEX Dashboard SPA ready');
}

// Start when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// ============================================================================
// LANGUAGE BAR HELPER
// ============================================================================

function renderLanguageBar(containerId, languages) {
    const container = document.getElementById(containerId);
    if (!container || !languages) return;
    
    const total = Object.values(languages).reduce((a, b) => a + b, 0);
    const sorted = Object.entries(languages).sort((a, b) => b[1] - a[1]);
    
    const barHtml = sorted.map(([lang, lines]) => {
        const pct = (lines / total * 100).toFixed(1);
        return `<div class="language-segment" data-lang="${lang}" style="width: ${pct}%;" title="${lang}: ${lines.toLocaleString()} lines (${pct}%)"></div>`;
    }).join('');
    
    const legendHtml = sorted.slice(0, 6).map(([lang, lines]) => {
        const pct = (lines / total * 100).toFixed(1);
        const colors = {
            JavaScript: '#f7df1e',
            TypeScript: '#3178c6',
            Python: '#3572A5',
            'C#': '#178600',
            HTML: '#e34c26',
            CSS: '#563d7c',
            SQL: '#e38c00',
            Config: '#6b7280'
        };
        return `
            <div class="language-item">
                <span class="language-dot" style="background: ${colors[lang] || '#6b7280'};"></span>
                <span>${lang}</span>
                <span class="text-muted">${pct}%</span>
            </div>
        `;
    }).join('');
    
    container.innerHTML = `
        <div class="language-bar">${barHtml}</div>
        <div class="language-legend">${legendHtml}</div>
    `;
}

// Export for inline usage
window.renderLanguageBar = renderLanguageBar;
