/**
 * Tab Controller Component for CORTEX LENS Dashboard
 * 
 * Alpine.js component for managing tab switching, lazy module loading,
 * and tab state persistence.
 * 
 * Author: Asif Hussain
 * Orchestrator: LENSVisualizationOrchestrator
 * AC-ID: LENS-013
 */

/**
 * Creates a tab controller Alpine.js component.
 * 
 * @param {Array<Object>} tabs - Array of tab configurations
 * @param {string} defaultTab - Default active tab ID
 * @returns {Object} Alpine.js component data and methods
 */
function tabController(tabs = [], defaultTab = null) {
  return {
    // State
    tabs: tabs,
    activeTab: defaultTab || (tabs.length > 0 ? tabs[0].id : null),
    loadedModules: new Set(['alpine', 'tailwind']),
    loadingTabs: new Set(),
    
    // Initialization
    init() {
      // Load active tab from URL hash or localStorage
      const urlHash = window.location.hash.slice(1);
      const savedTab = localStorage.getItem('cortex_active_tab');
      
      if (urlHash && this.tabs.find(t => t.id === urlHash)) {
        this.activeTab = urlHash;
      } else if (savedTab && this.tabs.find(t => t.id === savedTab)) {
        this.activeTab = savedTab;
      }
      
      // Load initial tab data
      this.loadTabData(this.activeTab);
      
      // Listen for hash changes
      window.addEventListener('hashchange', () => {
        const newTab = window.location.hash.slice(1);
        if (newTab && this.tabs.find(t => t.id === newTab)) {
          this.switchTab(newTab);
        }
      });
    },
    
    /**
     * Switch to a different tab.
     * 
     * @param {string} tabId - ID of tab to switch to
     */
    async switchTab(tabId) {
      if (this.activeTab === tabId) return;
      
      const tab = this.tabs.find(t => t.id === tabId);
      if (!tab) {
        console.error(`Tab not found: ${tabId}`);
        return;
      }
      
      // Update active tab
      this.activeTab = tabId;
      
      // Save to localStorage
      localStorage.setItem('cortex_active_tab', tabId);
      
      // Update URL hash
      window.location.hash = tabId;
      
      // Load tab data and required modules
      await this.loadTabData(tabId);
      
      // Emit tab change event
      this.$dispatch('tab-changed', { tabId, tab });
    },
    
    /**
     * Load data and modules required for a tab.
     * 
     * @param {string} tabId - ID of tab to load
     */
    async loadTabData(tabId) {
      if (this.loadingTabs.has(tabId)) return;
      
      const tab = this.tabs.find(t => t.id === tabId);
      if (!tab) return;
      
      this.loadingTabs.add(tabId);
      
      try {
        // Load required modules for this tab
        if (tab.modules && tab.modules.length > 0) {
          await this.loadModules(tab.modules);
        }
        
        // Fetch tab data if endpoint provided
        if (tab.dataEndpoint) {
          await this.fetchTabData(tab.dataEndpoint, tabId);
        }
        
        // Initialize tab-specific visualizations
        if (tab.onLoad && typeof tab.onLoad === 'function') {
          await tab.onLoad();
        }
      } catch (error) {
        console.error(`Error loading tab ${tabId}:`, error);
      } finally {
        this.loadingTabs.delete(tabId);
      }
    },
    
    /**
     * Load required JavaScript modules for visualization.
     * 
     * @param {Array<string>} modules - Module names to load (e.g., ['d3', 'mermaid'])
     */
    async loadModules(modules) {
      const modulesToLoad = modules.filter(m => !this.loadedModules.has(m));
      
      if (modulesToLoad.length === 0) return;
      
      // Use module loader if available
      if (window.CortexModuleLoader) {
        for (const module of modulesToLoad) {
          try {
            await window.CortexModuleLoader.load(module);
            this.loadedModules.add(module);
          } catch (error) {
            console.error(`Failed to load module ${module}:`, error);
          }
        }
      }
    },
    
    /**
     * Fetch data for a tab from API endpoint.
     * 
     * @param {string} endpoint - API endpoint URL
     * @param {string} tabId - Tab ID for caching
     */
    async fetchTabData(endpoint, tabId) {
      try {
        const response = await fetch(endpoint);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Store data in tab object
        const tab = this.tabs.find(t => t.id === tabId);
        if (tab) {
          tab.data = data;
        }
        
        return data;
      } catch (error) {
        console.error(`Error fetching data for ${tabId}:`, error);
        return null;
      }
    },
    
    /**
     * Check if a tab is currently active.
     * 
     * @param {string} tabId - Tab ID to check
     * @returns {boolean} True if tab is active
     */
    isActive(tabId) {
      return this.activeTab === tabId;
    },
    
    /**
     * Check if a tab is currently loading.
     * 
     * @param {string} tabId - Tab ID to check
     * @returns {boolean} True if tab is loading
     */
    isLoading(tabId) {
      return this.loadingTabs.has(tabId);
    },
    
    /**
     * Get active tab object.
     * 
     * @returns {Object|null} Active tab configuration
     */
    getActiveTab() {
      return this.tabs.find(t => t.id === this.activeTab) || null;
    },
    
    /**
     * Navigate to next tab.
     */
    nextTab() {
      const currentIndex = this.tabs.findIndex(t => t.id === this.activeTab);
      if (currentIndex < this.tabs.length - 1) {
        this.switchTab(this.tabs[currentIndex + 1].id);
      }
    },
    
    /**
     * Navigate to previous tab.
     */
    prevTab() {
      const currentIndex = this.tabs.findIndex(t => t.id === this.activeTab);
      if (currentIndex > 0) {
        this.switchTab(this.tabs[currentIndex - 1].id);
      }
    },
    
    /**
     * Reload current tab data.
     */
    async reloadTab() {
      const tab = this.getActiveTab();
      if (tab) {
        // Clear cached data
        tab.data = null;
        
        // Reload
        await this.loadTabData(this.activeTab);
        
        this.$dispatch('tab-reloaded', { tabId: this.activeTab });
      }
    }
  };
}

/**
 * Example tab configuration:
 * 
 * const tabs = [
 *   {
 *     id: 'repository_overview',
 *     name: 'Repository Overview',
 *     icon: '🏠',
 *     modules: [], // No special modules needed
 *     dataEndpoint: '/api/repositories/overview',
 *     onLoad: async () => {
 *       // Initialize any custom visualizations
 *     }
 *   },
 *   {
 *     id: 'dependency_graph',
 *     name: 'Dependency Graph',
 *     icon: '🔗',
 *     modules: ['d3'], // Requires D3.js
 *     dataEndpoint: '/api/dependency/graph',
 *     onLoad: async () => {
 *       // Render D3 graph
 *       renderDependencyGraph();
 *     }
 *   },
 *   {
 *     id: 'class_diagram',
 *     name: 'Class Diagram',
 *     icon: '📐',
 *     modules: ['mermaid'], // Requires Mermaid
 *     dataEndpoint: '/api/class/diagram',
 *     onLoad: async () => {
 *       // Render Mermaid diagram
 *       mermaid.init();
 *     }
 *   }
 * ];
 * 
 * // Usage in Alpine.js:
 * <div x-data="tabController(tabs, 'repository_overview')">
 *   <!-- Tab navigation -->
 *   <div class="tab-nav">
 *     <template x-for="tab in tabs" :key="tab.id">
 *       <button 
 *         @click="switchTab(tab.id)"
 *         :class="{ 'active': isActive(tab.id) }"
 *         class="tab-button"
 *       >
 *         <span x-text="tab.icon"></span>
 *         <span x-text="tab.name"></span>
 *       </button>
 *     </template>
 *   </div>
 *   
 *   <!-- Tab panels -->
 *   <template x-for="tab in tabs" :key="tab.id">
 *     <div x-show="isActive(tab.id)" x-transition>
 *       <!-- Tab content -->
 *     </div>
 *   </template>
 * </div>
 */

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { tabController };
}
