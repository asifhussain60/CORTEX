/**
 * CORTEX Dashboard JavaScript
 * 
 * Handles tab navigation, refresh functionality, and interactive features.
 * Works with Clean Architecture presentation layer templates.
 * 
 * Author: Asif Hussain
 */

(function() {
    'use strict';
    
    // Dashboard State
    const state = {
        currentTab: null,
        appId: null
    };
    
    /**
     * Initialize dashboard when DOM is ready
     */
    function initDashboard() {
        console.log('🧠 CORTEX Dashboard initialized');
        
        // Get app ID from page
        const appMetaElement = document.querySelector('.app-id');
        if (appMetaElement) {
            state.appId = appMetaElement.textContent.replace('App ID: ', '').trim();
        }
        
        // Setup event listeners
        setupTabNavigation();
        setupRefreshButton();
        
        // Set initial active tab
        const firstTab = document.querySelector('.tab-button');
        if (firstTab) {
            state.currentTab = firstTab.getAttribute('data-tab');
        }
        
        // Handle URL hash on load
        handleURLHash();
    }
    
    /**
     * Setup tab navigation with click handlers
     */
    function setupTabNavigation() {
        const tabButtons = document.querySelectorAll('.tab-button');
        
        tabButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const tabName = this.getAttribute('data-tab');
                switchTab(tabName);
            });
        });
    }
    
    /**
     * Switch to specified tab with animation
     */
    function switchTab(tabName) {
        if (!tabName) return;
        
        // Update button states
        document.querySelectorAll('.tab-button').forEach(btn => {
            if (btn.getAttribute('data-tab') === tabName) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
        
        // Update panel visibility
        document.querySelectorAll('.tab-panel').forEach(panel => {
            if (panel.id === 'tab-' + tabName) {
                panel.classList.add('active');
            } else {
                panel.classList.remove('active');
            }
        });
        
        // Update state
        state.currentTab = tabName;
        
        // Update URL hash without scrolling
        history.replaceState(null, null, '#' + tabName);
        
        console.log('Switched to tab: ' + tabName);
    }
    
    /**
     * Setup refresh button with AJAX functionality
     */
    function setupRefreshButton() {
        // Handle inline onclick refresh calls
        window.refreshDashboard = function() {
            if (!state.appId) {
                console.error('No app ID found for refresh');
                return;
            }
            
            console.log('Refreshing dashboard for ' + state.appId + '...');
            
            // Show loading state
            const refreshLinks = document.querySelectorAll('[onclick*="refreshDashboard"]');
            refreshLinks.forEach(function(link) {
                const originalText = link.textContent;
                link.textContent = 'Refreshing...';
                link.style.pointerEvents = 'none';
                
                // Call refresh endpoint
                fetch('/refresh/' + state.appId, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
                .then(function(response) {
                    return response.json();
                })
                .then(function(data) {
                    if (data.success) {
                        console.log('Dashboard refreshed successfully');
                        // Reload page to show updated data
                        window.location.reload();
                    } else {
                        console.error('Refresh failed:', data.error);
                        alert('Failed to refresh dashboard');
                        link.textContent = originalText;
                        link.style.pointerEvents = 'auto';
                    }
                })
                .catch(function(error) {
                    console.error('Refresh error:', error);
                    alert('Error refreshing dashboard');
                    link.textContent = originalText;
                    link.style.pointerEvents = 'auto';
                });
            });
        };
    }
    
    /**
     * Handle URL hash for direct tab navigation
     */
    function handleURLHash() {
        const hash = window.location.hash.substring(1);
        if (hash) {
            const tabButton = document.querySelector('[data-tab="' + hash + '"]');
            if (tabButton) {
                switchTab(hash);
            }
        }
    }
    
    /**
     * Utility: Format numbers with commas
     */
    function formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }
    
    /**
     * Utility: Format bytes to human-readable size
     */
    function formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initDashboard);
    } else {
        initDashboard();
    }
    
    // Handle hash changes (browser back/forward)
    window.addEventListener('hashchange', handleURLHash);
    
})();
