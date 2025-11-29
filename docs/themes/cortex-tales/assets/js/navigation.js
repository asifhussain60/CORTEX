/**
 * CORTEX Navigation Controller
 * Dynamically filters left sidebar navigation based on active top-level section
 * Author: Asif Hussain | © 2024-2025
 */

(function() {
    'use strict';
    
    // Section mapping: URL patterns to section names
    const SECTIONS = {
        'story/': 'The CORTEX Birth',
        'governance/': 'Cortex Bible',
        'architecture': 'Architecture',
        'integration': 'Architecture',
        'operational': 'Architecture',
        'planning': 'Architecture',
        'reference/': 'Technical Docs',
        'guides/': 'User Guides',
        'getting-started/': 'Examples',
        'examples/': 'Examples'
    };
    
    /**
     * Detect active section from current URL
     */
    function detectActiveSection() {
        const path = window.location.pathname;
        
        // Home page - no filtering
        if (path === '/' || path.endsWith('index.html') || path.endsWith('/CORTEX/')) {
            return 'Home';
        }
        
        // Check URL against section patterns
        for (const pattern in SECTIONS) {
            if (path.includes(pattern)) {
                return SECTIONS[pattern];
            }
        }
        
        return null;
    }
    
    /**
     * Filter left sidebar navigation based on active section
     */
    function filterSidebar(activeSection) {
        const navTree = document.querySelector('.nav-tree');
        if (!navTree) return;
        
        const navGroups = navTree.querySelectorAll('.nav-group');
        
        if (activeSection === 'Home') {
            // Home page: hide all nav groups or show minimal navigation
            navGroups.forEach(function(group) {
                group.style.display = 'none';
            });
            return;
        }
        
        // Filter nav groups by active section
        navGroups.forEach(function(group) {
            const groupTitle = group.querySelector('strong');
            if (!groupTitle) return;
            
            const title = groupTitle.textContent.trim();
            
            if (title === activeSection) {
                group.style.display = 'block';
            } else {
                group.style.display = 'none';
            }
        });
    }
    
    /**
     * Highlight active top navigation item
     */
    function highlightTopNav(activeSection) {
        const navLinks = document.querySelectorAll('.horizontal-nav a');
        
        navLinks.forEach(function(link) {
            const linkText = link.textContent.trim();
            
            if (linkText === activeSection) {
                link.classList.add('active-section');
            } else {
                link.classList.remove('active-section');
            }
        });
    }
    
    /**
     * Initialize navigation controller
     */
    function init() {
        const activeSection = detectActiveSection();
        
        if (activeSection) {
            filterSidebar(activeSection);
            highlightTopNav(activeSection);
        }
    }
    
    // Run on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();
