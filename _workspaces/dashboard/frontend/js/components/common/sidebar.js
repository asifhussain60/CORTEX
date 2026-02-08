/**
 * Sidebar Navigation Component
 * DO-002-01: Sidebar Navigation with Active States
 * 
 * Features:
 * - 5 main sections: Brain Observatory, Temporal Cortex, Orchestrators, Plan Hub, Admin
 * - Active section highlighting
 * - Collapse/expand toggle with state persistence
 * - Smooth transitions
 * - Mobile responsive (hidden on mobile)
 * 
 * Governance: CORE-012 (Google-style docstrings), CORE-028 (kebab-case)
 */

/**
 * Initialize sidebar navigation component.
 * Sets up event listeners, state persistence, and active section detection.
 * 
 * @returns {void}
 */
function initializeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const toggleButton = document.getElementById('sidebar-toggle');
    const navItems = document.querySelectorAll('.sidebar-nav-item');
    const mainContent = document.querySelector('.main-content');
    
    if (!sidebar) {
        console.warn('Sidebar element not found. Skipping initialization.');
        return;
    }
    
    // Restore collapsed state from localStorage
    restoreSidebarState();
    
    // Set up collapse/expand toggle
    if (toggleButton) {
        toggleButton.addEventListener('click', toggleSidebarCollapse);
    }
    
    // Set up navigation item click handlers
    navItems.forEach(item => {
        item.addEventListener('click', (e) => handleNavigationClick(e, item));
    });
    
    // Set active section based on current URL or page state
    setActiveSectionFromURL();
    
    // Handle mobile sidebar overlay close
    setupMobileSidebarClose();
    
    console.log('Γ£ô Sidebar navigation initialized');
}

/**
 * Toggle sidebar collapsed state.
 * Adds/removes 'collapsed' class and updates main content margin.
 * Persists state to localStorage.
 * 
 * @returns {void}
 */
function toggleSidebarCollapse() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');
    
    if (!sidebar) return;
    
    // Toggle collapsed class
    sidebar.classList.toggle('collapsed');
    
    // Update main content margin class
    if (mainContent) {
        mainContent.classList.toggle('sidebar-collapsed');
    }
    
    // Save state to localStorage
    const isCollapsed = sidebar.classList.contains('collapsed');
    saveSidebarState(isCollapsed);
    
    // Dispatch custom event for other components
    window.dispatchEvent(new CustomEvent('sidebarToggle', {
        detail: { collapsed: isCollapsed }
    }));
}

/**
 * Handle navigation item click.
 * Sets active state, prevents default anchor behavior, and triggers navigation.
 * 
 * @param {Event} event - Click event
 * @param {HTMLElement} clickedItem - Clicked navigation item element
 * @returns {void}
 */
function handleNavigationClick(event, clickedItem) {
    // Prevent default anchor behavior if it's a link
    if (clickedItem.tagName === 'A') {
        event.preventDefault();
    }
    
    // Get section name from data attribute or text content
    const sectionName = clickedItem.dataset.section || 
                       clickedItem.querySelector('.sidebar-nav-text')?.textContent.trim();
    
    if (!sectionName) {
        console.warn('Navigation item has no section name');
        return;
    }
    
    // Set active section
    setActiveSection(sectionName);
    
    // Update URL hash for bookmarkability
    window.location.hash = `section-${sectionName.toLowerCase().replace(/\s+/g, '-')}`;
    
    // Dispatch custom event for section change
    window.dispatchEvent(new CustomEvent('sectionChange', {
        detail: { section: sectionName }
    }));
    
    // Close mobile sidebar after navigation
    const sidebar = document.getElementById('sidebar');
    if (sidebar && sidebar.classList.contains('mobile-open')) {
        sidebar.classList.remove('mobile-open');
        document.body.style.overflow = ''; // Restore scroll
    }
    
    console.log(`Γ£ô Navigated to section: ${sectionName}`);
}

/**
 * Set active navigation section.
 * Removes active class from all items and adds it to the specified section.
 * 
 * @param {string} sectionName - Name of the section to activate
 * @returns {void}
 */
function setActiveSection(sectionName) {
    const navItems = document.querySelectorAll('.sidebar-nav-item');
    
    // Remove active class from all items
    navItems.forEach(item => {
        item.classList.remove('active');
        item.setAttribute('aria-current', 'false');
    });
    
    // Add active class to matching item
    navItems.forEach(item => {
        const itemSectionName = item.dataset.section || 
                               item.querySelector('.sidebar-nav-text')?.textContent.trim();
        
        if (itemSectionName === sectionName) {
            item.classList.add('active');
            item.setAttribute('aria-current', 'page');
        }
    });
}

/**
 * Set active section based on current URL hash.
 * Called on page load to restore navigation state.
 * 
 * @returns {void}
 */
function setActiveSectionFromURL() {
    const hash = window.location.hash;
    
    if (hash && hash.startsWith('#section-')) {
        // Extract section name from hash
        const sectionSlug = hash.replace('#section-', '');
        const sectionName = sectionSlug
            .split('-')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
        
        setActiveSection(sectionName);
    } else {
        // Default to first section (Brain Observatory)
        setActiveSection('Brain Observatory');
    }
}

/**
 * Save sidebar collapsed state to localStorage.
 * 
 * @param {boolean} isCollapsed - Whether sidebar is collapsed
 * @returns {void}
 */
function saveSidebarState(isCollapsed) {
    try {
        localStorage.setItem('cortex-sidebar-collapsed', JSON.stringify(isCollapsed));
    } catch (error) {
        console.warn('Failed to save sidebar state to localStorage:', error);
    }
}

/**
 * Restore sidebar collapsed state from localStorage.
 * 
 * @returns {void}
 */
function restoreSidebarState() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');
    
    if (!sidebar) return;
    
    try {
        const savedState = localStorage.getItem('cortex-sidebar-collapsed');
        
        if (savedState !== null) {
            const isCollapsed = JSON.parse(savedState);
            
            if (isCollapsed) {
                sidebar.classList.add('collapsed');
                if (mainContent) {
                    mainContent.classList.add('sidebar-collapsed');
                }
            }
        }
    } catch (error) {
        console.warn('Failed to restore sidebar state from localStorage:', error);
    }
}

/**
 * Set up mobile sidebar close behavior.
 * Closes sidebar when clicking outside on mobile.
 * 
 * @returns {void}
 */
function setupMobileSidebarClose() {
    const sidebar = document.getElementById('sidebar');
    
    if (!sidebar) return;
    
    // Close sidebar on window resize to desktop
    window.addEventListener('resize', () => {
        if (window.innerWidth >= 1024) {
            sidebar.classList.remove('mobile-open');
            document.body.style.overflow = '';
        }
    });
    
    // Close sidebar on Escape key (mobile)
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && sidebar.classList.contains('mobile-open')) {
            sidebar.classList.remove('mobile-open');
            document.body.style.overflow = '';
        }
    });
}

/**
 * Toggle mobile sidebar open/close.
 * Called by hamburger menu on mobile.
 * 
 * @returns {void}
 */
function toggleMobileSidebar() {
    const sidebar = document.getElementById('sidebar');
    
    if (!sidebar) return;
    
    sidebar.classList.toggle('mobile-open');
    
    // Lock body scroll when sidebar is open on mobile
    if (sidebar.classList.contains('mobile-open')) {
        document.body.style.overflow = 'hidden';
    } else {
        document.body.style.overflow = '';
    }
}

/**
 * Get current active section name.
 * 
 * @returns {string|null} Active section name or null if none active
 */
function getActiveSection() {
    const activeItem = document.querySelector('.sidebar-nav-item.active');
    
    if (!activeItem) return null;
    
    return activeItem.dataset.section || 
           activeItem.querySelector('.sidebar-nav-text')?.textContent.trim();
}

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initializeSidebar,
        toggleSidebarCollapse,
        setActiveSection,
        getActiveSection,
        toggleMobileSidebar,
    };
}
