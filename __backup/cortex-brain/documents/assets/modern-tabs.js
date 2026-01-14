/**
 * CORTEX Modern Tab System - JavaScript Controller
 * Handles tab switching, state management, and accessibility
 * 
 * Author: Asif Hussain
 * Version: 1.0.0
 * Date: January 4, 2026
 */

class TabSystem {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`Tab container with ID "${containerId}" not found`);
            return;
        }
        
        this.tabButtons = this.container.querySelectorAll('.tab-button');
        this.tabPanels = this.container.querySelectorAll('.tab-panel');
        this.currentTab = 0;
        
        this.init();
    }
    
    init() {
        // Set up click handlers
        this.tabButtons.forEach((button, index) => {
            button.addEventListener('click', () => this.switchTab(index));
            
            // Keyboard navigation
            button.addEventListener('keydown', (e) => this.handleKeyboard(e, index));
        });
        
        // Set initial tab
        this.switchTab(0);
        
        // Set up ARIA attributes
        this.setupAria();
    }
    
    switchTab(index) {
        // Validate index
        if (index < 0 || index >= this.tabButtons.length) {
            return;
        }
        
        // Deactivate all tabs
        this.tabButtons.forEach((button, i) => {
            button.classList.toggle('active', i === index);
            button.setAttribute('aria-selected', i === index ? 'true' : 'false');
            button.setAttribute('tabindex', i === index ? '0' : '-1');
        });
        
        this.tabPanels.forEach((panel, i) => {
            panel.classList.toggle('active', i === index);
            panel.setAttribute('aria-hidden', i === index ? 'false' : 'true');
        });
        
        this.currentTab = index;
        
        // Save state to localStorage
        this.saveState();
        
        // Emit custom event
        this.container.dispatchEvent(new CustomEvent('tabChanged', {
            detail: { index, button: this.tabButtons[index] }
        }));
    }
    
    handleKeyboard(event, index) {
        let newIndex = index;
        
        switch (event.key) {
            case 'ArrowLeft':
                newIndex = index > 0 ? index - 1 : this.tabButtons.length - 1;
                event.preventDefault();
                break;
            case 'ArrowRight':
                newIndex = index < this.tabButtons.length - 1 ? index + 1 : 0;
                event.preventDefault();
                break;
            case 'Home':
                newIndex = 0;
                event.preventDefault();
                break;
            case 'End':
                newIndex = this.tabButtons.length - 1;
                event.preventDefault();
                break;
            default:
                return;
        }
        
        this.switchTab(newIndex);
        this.tabButtons[newIndex].focus();
    }
    
    setupAria() {
        // Set up ARIA attributes for accessibility
        const tabNav = this.container.querySelector('.tab-nav');
        if (tabNav) {
            tabNav.setAttribute('role', 'tablist');
        }
        
        this.tabButtons.forEach((button, index) => {
            button.setAttribute('role', 'tab');
            button.setAttribute('id', `tab-${this.container.id}-${index}`);
            button.setAttribute('aria-controls', `panel-${this.container.id}-${index}`);
        });
        
        this.tabPanels.forEach((panel, index) => {
            panel.setAttribute('role', 'tabpanel');
            panel.setAttribute('id', `panel-${this.container.id}-${index}`);
            panel.setAttribute('aria-labelledby', `tab-${this.container.id}-${index}`);
        });
    }
    
    saveState() {
        // Save current tab to localStorage for persistence
        const key = `cortex-tab-state-${this.container.id}`;
        localStorage.setItem(key, this.currentTab.toString());
    }
    
    restoreState() {
        // Restore previous tab selection
        const key = `cortex-tab-state-${this.container.id}`;
        const savedTab = localStorage.getItem(key);
        
        if (savedTab !== null) {
            const index = parseInt(savedTab, 10);
            if (!isNaN(index)) {
                this.switchTab(index);
            }
        }
    }
    
    // Public API
    getActiveTab() {
        return this.currentTab;
    }
    
    setActiveTab(index) {
        this.switchTab(index);
    }
    
    destroy() {
        this.tabButtons.forEach(button => {
            button.replaceWith(button.cloneNode(true));
        });
    }
}

// Auto-initialize all tab systems on page load
document.addEventListener('DOMContentLoaded', () => {
    const tabContainers = document.querySelectorAll('.tab-container[id]');
    
    tabContainers.forEach(container => {
        const tabSystem = new TabSystem(container.id);
        
        // Restore previous state if available
        tabSystem.restoreState();
        
        // Store instance for external access
        container.tabSystem = tabSystem;
    });
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TabSystem;
}
