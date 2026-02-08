/**
 * Tab Switcher Component
 * DO-002-02: Tab-based View Switching
 * 
 * Features:
 * - Tab interface for switching between views
 * - URL hash navigation for bookmarkability
 * - Tab state persistence across page refreshes
 * - Smooth transitions (200ms)
 * - Lazy content loading support
 * - Keyboard navigation (Arrow keys)
 * 
 * Governance: CORE-012 (Google-style docstrings), CORE-028 (kebab-case)
 */

/**
 * Initialize all tab switchers on the page.
 * Finds all .tab-container elements and sets up tab switching.
 * 
 * @returns {void}
 */
function initializeTabSwitcher() {
    const tabContainers = document.querySelectorAll('.tab-container');
    
    if (tabContainers.length === 0) {
        console.warn('No tab containers found. Skipping tab switcher initialization.');
        return;
    }
    
    tabContainers.forEach(container => {
        setupTabContainer(container);
    });
    
    // Restore active tabs from URL hash on page load
    restoreTabsFromURL();
    
    // Handle browser back/forward navigation
    window.addEventListener('hashchange', restoreTabsFromURL);
    
    console.log(`Γ£ô Tab switcher initialized (${tabContainers.length} container(s))`);
}

/**
 * Set up a single tab container with event listeners and keyboard support.
 * 
 * @param {HTMLElement} container - Tab container element
 * @returns {void}
 */
function setupTabContainer(container) {
    const tabList = container.querySelector('.tab-list');
    const tabItems = container.querySelectorAll('.tab-item');
    const tabPanels = container.querySelectorAll('.tab-panel');
    
    if (!tabList || tabItems.length === 0) {
        console.warn('Tab container missing tab list or items', container);
        return;
    }
    
    // Store tab data in container for easy access
    container._tabData = {
        tabList,
        tabItems: Array.from(tabItems),
        tabPanels: Array.from(tabPanels),
        containerId: container.id || `tab-container-${Math.random().toString(36).substr(2, 9)}`
    };
    
    // Attach click handlers to tabs
    tabItems.forEach((tab, index) => {
        tab.addEventListener('click', (e) => handleTabClick(e, container, tab));
        
        // Store tab index for keyboard navigation
        tab.dataset.tabIndex = index;
        
        // ARIA attributes for accessibility
        tab.setAttribute('role', 'tab');
        tab.setAttribute('aria-selected', tab.classList.contains('active') ? 'true' : 'false');
        
        // Link tab to its panel
        const tabId = tab.dataset.tab || tab.id || `tab-${index}`;
        tab.setAttribute('aria-controls', tabId);
    });
    
    // Set up keyboard navigation
    setupTabKeyboardNavigation(container);
    
    // Mark first tab as active if none are active
    if (!Array.from(tabItems).some(tab => tab.classList.contains('active'))) {
        if (tabItems.length > 0) {
            activateTab(tabItems[0], container);
        }
    }
}

/**
 * Handle tab click event.
 * 
 * @param {Event} event - Click event
 * @param {HTMLElement} container - Tab container element
 * @param {HTMLElement} clickedTab - Clicked tab element
 * @returns {void}
 */
function handleTabClick(event, container, clickedTab) {
    event.preventDefault();
    
    // Activate the clicked tab
    activateTab(clickedTab, container);
    
    // Update URL hash
    const tabName = clickedTab.dataset.tab || clickedTab.textContent.trim().toLowerCase().replace(/\s+/g, '-');
    updateURLHash(container._tabData.containerId, tabName);
    
    // Dispatch custom event for other components
    window.dispatchEvent(new CustomEvent('tabChange', {
        detail: {
            containerId: container._tabData.containerId,
            tabName: tabName,
            tab: clickedTab
        }
    }));
}

/**
 * Activate a tab and show its content panel.
 * 
 * @param {HTMLElement} tab - Tab to activate
 * @param {HTMLElement} container - Tab container element
 * @returns {void}
 */
function activateTab(tab, container) {
    const { tabItems, tabPanels } = container._tabData;
    
    // Deactivate all tabs
    tabItems.forEach(item => {
        item.classList.remove('active');
        item.setAttribute('aria-selected', 'false');
    });
    
    // Activate clicked tab
    tab.classList.add('active');
    tab.setAttribute('aria-selected', 'true');
    
    // Get tab panel ID
    const tabPanelId = tab.dataset.tab || tab.getAttribute('aria-controls');
    
    // Hide all panels
    tabPanels.forEach(panel => {
        panel.classList.remove('active');
        panel.setAttribute('aria-hidden', 'true');
    });
    
    // Show active panel
    if (tabPanelId) {
        const activePanel = container.querySelector(`#${tabPanelId}`) ||
                          container.querySelector(`[data-tab-panel="${tabPanelId}"]`);
        
        if (activePanel) {
            activePanel.classList.add('active');
            activePanel.setAttribute('aria-hidden', 'false');
            
            // Lazy load content if needed
            if (!activePanel.dataset.loaded && activePanel.dataset.loadUrl) {
                loadTabContent(activePanel);
            }
        }
    }
}

/**
 * Load tab content via AJAX (lazy loading).
 * 
 * @param {HTMLElement} panel - Tab panel to load content into
 * @returns {Promise<void>}
 */
async function loadTabContent(panel) {
    const loadUrl = panel.dataset.loadUrl;
    
    if (!loadUrl) return;
    
    // Show loading state
    panel.innerHTML = `
        <div class="tab-panel-loading">
            <div class="tab-spinner"></div>
            <span style="margin-left: 0.5rem;">Loading...</span>
        </div>
    `;
    
    try {
        const response = await fetch(loadUrl);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const html = await response.text();
        panel.innerHTML = html;
        panel.dataset.loaded = 'true';
        
        console.log(`Γ£ô Tab content loaded: ${loadUrl}`);
    } catch (error) {
        console.error('Failed to load tab content:', error);
        panel.innerHTML = `
            <div class="tab-panel-error">
                <p>Failed to load content</p>
                <button onclick="loadTabContent(this.closest('.tab-panel'))" class="btn-primary mt-4">
                    Retry
                </button>
            </div>
        `;
    }
}

/**
 * Set up keyboard navigation for tabs.
 * Arrow keys to move between tabs, Enter/Space to activate.
 * 
 * @param {HTMLElement} container - Tab container element
 * @returns {void}
 */
function setupTabKeyboardNavigation(container) {
    const { tabItems } = container._tabData;
    
    container.addEventListener('keydown', (e) => {
        const focusedTab = document.activeElement;
        
        if (!focusedTab || !focusedTab.classList.contains('tab-item')) {
            return;
        }
        
        const currentIndex = parseInt(focusedTab.dataset.tabIndex, 10);
        let nextIndex = currentIndex;
        
        switch (e.key) {
            case 'ArrowRight':
            case 'ArrowDown':
                e.preventDefault();
                nextIndex = (currentIndex + 1) % tabItems.length;
                break;
                
            case 'ArrowLeft':
            case 'ArrowUp':
                e.preventDefault();
                nextIndex = (currentIndex - 1 + tabItems.length) % tabItems.length;
                break;
                
            case 'Home':
                e.preventDefault();
                nextIndex = 0;
                break;
                
            case 'End':
                e.preventDefault();
                nextIndex = tabItems.length - 1;
                break;
                
            case 'Enter':
            case ' ':
                e.preventDefault();
                activateTab(focusedTab, container);
                updateURLHash(container._tabData.containerId, 
                            focusedTab.dataset.tab || focusedTab.textContent.trim().toLowerCase().replace(/\s+/g, '-'));
                return;
                
            default:
                return;
        }
        
        // Focus next/previous tab
        if (nextIndex !== currentIndex) {
            tabItems[nextIndex].focus();
        }
    });
}

/**
 * Update URL hash with active tab state.
 * Format: #container-id:tab-name
 * 
 * @param {string} containerId - Container ID
 * @param {string} tabName - Tab name
 * @returns {void}
 */
function updateURLHash(containerId, tabName) {
    const hash = window.location.hash.substring(1);
    const hashParts = hash.split('&');
    const newTabState = `${containerId}:${tabName}`;
    
    // Replace or add tab state for this container
    const updatedParts = hashParts.filter(part => !part.startsWith(`${containerId}:`));
    updatedParts.push(newTabState);
    
    const newHash = updatedParts.filter(Boolean).join('&');
    
    // Update URL without triggering hashchange event
    history.replaceState(null, '', `#${newHash}`);
}

/**
 * Restore active tabs from URL hash.
 * Called on page load and hashchange events.
 * 
 * @returns {void}
 */
function restoreTabsFromURL() {
    const hash = window.location.hash.substring(1);
    
    if (!hash) return;
    
    // Parse hash: container-id:tab-name&container-id2:tab-name2
    const hashParts = hash.split('&');
    
    hashParts.forEach(part => {
        const [containerId, tabName] = part.split(':');
        
        if (!containerId || !tabName) return;
        
        // Find container
        const container = document.getElementById(containerId) ||
                         document.querySelector(`[data-tab-container="${containerId}"]`);
        
        if (!container || !container._tabData) return;
        
        // Find tab by name
        const tab = container._tabData.tabItems.find(item => {
            const itemTabName = item.dataset.tab || item.textContent.trim().toLowerCase().replace(/\s+/g, '-');
            return itemTabName === tabName;
        });
        
        if (tab) {
            activateTab(tab, container);
        }
    });
}

/**
 * Switch to a specific tab programmatically.
 * Public API for other components.
 * 
 * @param {string} containerId - Container ID
 * @param {string} tabName - Tab name or index
 * @returns {boolean} Success status
 */
function switchTab(containerId, tabName) {
    const container = document.getElementById(containerId) ||
                     document.querySelector(`[data-tab-container="${containerId}"]`);
    
    if (!container || !container._tabData) {
        console.warn(`Tab container not found: ${containerId}`);
        return false;
    }
    
    // Find tab by name or index
    let tab;
    
    if (typeof tabName === 'number') {
        tab = container._tabData.tabItems[tabName];
    } else {
        tab = container._tabData.tabItems.find(item => {
            const itemTabName = item.dataset.tab || item.textContent.trim().toLowerCase().replace(/\s+/g, '-');
            return itemTabName === tabName;
        });
    }
    
    if (!tab) {
        console.warn(`Tab not found: ${tabName}`);
        return false;
    }
    
    activateTab(tab, container);
    updateURLHash(containerId, tab.dataset.tab || tabName);
    
    return true;
}

/**
 * Get active tab for a container.
 * 
 * @param {string} containerId - Container ID
 * @returns {HTMLElement|null} Active tab element or null
 */
function getActiveTab(containerId) {
    const container = document.getElementById(containerId) ||
                     document.querySelector(`[data-tab-container="${containerId}"]`);
    
    if (!container || !container._tabData) {
        return null;
    }
    
    return container._tabData.tabItems.find(tab => tab.classList.contains('active')) || null;
}

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initializeTabSwitcher,
        switchTab,
        getActiveTab,
        activateTab,
        loadTabContent,
    };
}
