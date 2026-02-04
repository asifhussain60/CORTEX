/**
 * CORTEX SPA - SubTabs Component
 * Secondary tab navigation within main tabs (e.g., Code Explorer)
 * Version: 1.0.0
 */

class SubTabs {
    /**
     * Initialize sub-tabs
     * @param {string} containerSelector - CSS selector for sub-tabs container
     * @param {Object} options - Configuration options
     */
    constructor(containerSelector, options = {}) {
        this.container = document.querySelector(containerSelector);
        if (!this.container) {
            throw new Error(`SubTabs container not found: ${containerSelector}`);
        }
        
        this.options = {
            onTabChange: options.onTabChange || (() => {}),
            defaultTab: options.defaultTab || 0,
            saveState: options.saveState !== false,
            stateKey: options.stateKey || 'cortex-subtabs-state',
            ...options
        };
        
        this.currentTab = null;
        this.tabs = [];
        this.panels = [];
        
        this._initialize();
    }
    
    /**
     * Initialize sub-tabs DOM structure
     * @private
     */
    _initialize() {
        // Find tab headers
        const tabList = this.container.querySelector('.sub-tabs__list');
        if (!tabList) {
            console.warn('Sub-tabs list not found');
            return;
        }
        
        this.tabElements = Array.from(tabList.querySelectorAll('.sub-tab'));
        this.tabs = this.tabElements.map((el, i) => ({
            id: el.dataset.subTab || `tab-${i}`,
            element: el,
            label: el.textContent.trim(),
            enabled: !el.hasAttribute('disabled')
        }));
        
        // Find tab panels
        this.panelElements = Array.from(this.container.querySelectorAll('.sub-tab-panel'));
        this.panels = this.panelElements.map((el, i) => ({
            id: el.dataset.subTabPanel || `panel-${i}`,
            element: el
        }));
        
        if (this.tabs.length === 0) {
            console.warn('No sub-tabs found');
            return;
        }
        
        // Add click handlers
        this.tabElements.forEach((tab, i) => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                if (!tab.hasAttribute('disabled')) {
                    this.switchTo(i);
                }
            });
        });
        
        // Restore saved state or use default
        const savedTab = this.options.saveState ? this._loadState() : null;
        const initialTab = savedTab !== null ? savedTab : this.options.defaultTab;
        this.switchTo(initialTab);
    }
    
    /**
     * Switch to specific tab
     * @param {number|string} tabIndexOrId - Tab index or ID to switch to
     */
    switchTo(tabIndexOrId) {
        let tabIndex;
        
        if (typeof tabIndexOrId === 'number') {
            tabIndex = tabIndexOrId;
        } else {
            tabIndex = this.tabs.findIndex(t => t.id === tabIndexOrId);
        }
        
        if (tabIndex < 0 || tabIndex >= this.tabs.length) {
            console.warn(`Invalid tab: ${tabIndexOrId}`);
            return;
        }
        
        if (!this.tabs[tabIndex].enabled) {
            console.warn(`Tab is disabled: ${tabIndexOrId}`);
            return;
        }
        
        const previousTab = this.currentTab;
        
        // Update tab states
        this.tabElements.forEach((el, i) => {
            el.classList.toggle('active', i === tabIndex);
        });
        
        // Update panel visibility
        this.panelElements.forEach((el, i) => {
            el.classList.toggle('active', i === tabIndex);
        });
        
        this.currentTab = tabIndex;
        
        // Save state
        if (this.options.saveState) {
            this._saveState(tabIndex);
        }
        
        // Trigger callback
        this.options.onTabChange({
            currentTab: tabIndex,
            previousTab: previousTab,
            tab: this.tabs[tabIndex]
        });
    }
    
    /**
     * Enable a tab
     * @param {number|string} tabIndexOrId - Tab index or ID
     */
    enable(tabIndexOrId) {
        const tabIndex = typeof tabIndexOrId === 'number' 
            ? tabIndexOrId 
            : this.tabs.findIndex(t => t.id === tabIndexOrId);
        
        if (tabIndex >= 0 && tabIndex < this.tabs.length) {
            this.tabs[tabIndex].enabled = true;
            this.tabElements[tabIndex].removeAttribute('disabled');
        }
    }
    
    /**
     * Disable a tab
     * @param {number|string} tabIndexOrId - Tab index or ID
     */
    disable(tabIndexOrId) {
        const tabIndex = typeof tabIndexOrId === 'number' 
            ? tabIndexOrId 
            : this.tabs.findIndex(t => t.id === tabIndexOrId);
        
        if (tabIndex >= 0 && tabIndex < this.tabs.length) {
            this.tabs[tabIndex].enabled = false;
            this.tabElements[tabIndex].setAttribute('disabled', '');
            
            // Switch away if currently active
            if (this.currentTab === tabIndex) {
                const nextEnabled = this.tabs.findIndex(t => t.enabled);
                if (nextEnabled >= 0) {
                    this.switchTo(nextEnabled);
                }
            }
        }
    }
    
    /**
     * Get current tab index
     * @returns {number}
     */
    getCurrentTab() {
        return this.currentTab;
    }
    
    /**
     * Get current tab ID
     * @returns {string}
     */
    getCurrentTabId() {
        return this.tabs[this.currentTab]?.id;
    }
    
    /**
     * Get total number of tabs
     * @returns {number}
     */
    getTotalTabs() {
        return this.tabs.length;
    }
    
    /**
     * Save state to localStorage
     * @private
     */
    _saveState(tabIndex) {
        try {
            localStorage.setItem(this.options.stateKey, tabIndex.toString());
        } catch (e) {
            console.warn('Failed to save sub-tab state:', e);
        }
    }
    
    /**
     * Load state from localStorage
     * @private
     * @returns {number|null}
     */
    _loadState() {
        try {
            const saved = localStorage.getItem(this.options.stateKey);
            return saved !== null ? parseInt(saved, 10) : null;
        } catch (e) {
            console.warn('Failed to load sub-tab state:', e);
            return null;
        }
    }
    
    /**
     * Clear saved state
     */
    clearState() {
        try {
            localStorage.removeItem(this.options.stateKey);
        } catch (e) {
            console.warn('Failed to clear sub-tab state:', e);
        }
    }
    
    /**
     * Destroy sub-tabs instance
     */
    destroy() {
        this.tabElements.forEach(el => {
            el.classList.remove('active');
            el.replaceWith(el.cloneNode(true)); // Remove event listeners
        });
        
        this.panelElements.forEach(el => {
            el.classList.remove('active');
        });
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SubTabs;
}
