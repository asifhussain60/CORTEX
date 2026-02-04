/**
 * CORTEX SPA - Tab Manager Component
 * Handles tab navigation with keyboard support and ARIA
 * Version: 1.0.0
 */

class TabManager {
    constructor(container) {
        this.container = container;
        this.tabs = [];
        this.panels = [];
        this.activeIndex = 0;
        this.onTabChange = null;
        
        this.init();
    }
    
    init() {
        this.tabs = Array.from(this.container.querySelectorAll('[role="tab"]'));
        this.panels = Array.from(this.container.querySelectorAll('[role="tabpanel"]'));
        
        if (this.tabs.length === 0) {
            console.warn('TabManager: No tabs found');
            return;
        }
        
        this.tabs.forEach((tab, index) => {
            tab.addEventListener('click', () => this.activateTab(index));
            tab.addEventListener('keydown', (e) => this.handleKeydown(e, index));
        });
        
        // Activate first tab or tab with active class
        const activeTab = this.tabs.findIndex(t => t.classList.contains('active') || t.getAttribute('aria-selected') === 'true');
        this.activateTab(activeTab >= 0 ? activeTab : 0);
    }
    
    activateTab(index) {
        if (index < 0 || index >= this.tabs.length) return;
        
        // Deactivate all tabs
        this.tabs.forEach((tab, i) => {
            tab.setAttribute('aria-selected', 'false');
            tab.classList.remove('active');
            tab.setAttribute('tabindex', '-1');
        });
        
        // Hide all panels
        this.panels.forEach(panel => {
            panel.setAttribute('aria-hidden', 'true');
            panel.classList.remove('active');
        });
        
        // Activate selected tab
        const tab = this.tabs[index];
        tab.setAttribute('aria-selected', 'true');
        tab.classList.add('active');
        tab.setAttribute('tabindex', '0');
        
        // Show corresponding panel
        const panelId = tab.getAttribute('aria-controls');
        const panel = document.getElementById(panelId);
        if (panel) {
            panel.setAttribute('aria-hidden', 'false');
            panel.classList.add('active');
        }
        
        this.activeIndex = index;
        
        // Trigger callback
        if (this.onTabChange) {
            this.onTabChange(index, tab, panel);
        }
        
        // Dispatch custom event
        this.container.dispatchEvent(new CustomEvent('tabchange', {
            detail: { index, tab, panel }
        }));
    }
    
    handleKeydown(event, currentIndex) {
        let newIndex;
        
        switch (event.key) {
            case 'ArrowLeft':
            case 'ArrowUp':
                newIndex = currentIndex - 1;
                if (newIndex < 0) newIndex = this.tabs.length - 1;
                break;
            case 'ArrowRight':
            case 'ArrowDown':
                newIndex = currentIndex + 1;
                if (newIndex >= this.tabs.length) newIndex = 0;
                break;
            case 'Home':
                newIndex = 0;
                break;
            case 'End':
                newIndex = this.tabs.length - 1;
                break;
            default:
                return;
        }
        
        event.preventDefault();
        this.activateTab(newIndex);
        this.tabs[newIndex].focus();
    }
    
    showTab(idOrIndex) {
        if (typeof idOrIndex === 'string') {
            const index = this.tabs.findIndex(t => 
                t.getAttribute('aria-controls') === idOrIndex || 
                t.id === idOrIndex
            );
            if (index >= 0) this.activateTab(index);
        } else {
            this.activateTab(idOrIndex);
        }
    }
    
    hideTab(idOrIndex) {
        const tab = typeof idOrIndex === 'string' 
            ? this.tabs.find(t => t.getAttribute('aria-controls') === idOrIndex)
            : this.tabs[idOrIndex];
        
        if (tab) {
            tab.style.display = 'none';
        }
    }
    
    showAllTabs() {
        this.tabs.forEach(tab => {
            tab.style.display = '';
        });
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TabManager;
}
