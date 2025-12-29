/**
 * Adaptive Code Panel Height Algorithm
 * =====================================
 * Dynamically adjusts code panel height based on content length
 * Implements glassmorphism-design-standards-v2.md v2.2.0
 * 
 * @author Asif Hussain
 * @version 2.2.0
 * @date December 29, 2025
 */

(function() {
    'use strict';

    // ==========================================================================
    // Configuration Constants
    // ==========================================================================

    const CONFIG = {
        LINE_HEIGHT_PX: 24,           // Typical code line height
        MIN_PANEL_HEIGHT: 200,        // Minimum panel height (px)
        MAX_AUTO_HEIGHT_DESKTOP: 600, // Desktop max before scroll (px)
        MAX_AUTO_HEIGHT_MOBILE: 400,  // Mobile max before scroll (px)
        MOBILE_BREAKPOINT: 768,       // Viewport width threshold (px)
        PADDING_PX: 32,               // Top/bottom padding (1rem each)
        SCROLL_THRESHOLD_DESKTOP: 25, // Lines before scrollbar (desktop)
        SCROLL_THRESHOLD_MOBILE: 16,  // Lines before scrollbar (mobile)
    };

    // ==========================================================================
    // Viewport Detection
    // ==========================================================================

    /**
     * Check if viewport is mobile size
     * @returns {boolean} True if mobile viewport
     */
    function isMobileViewport() {
        return window.innerWidth < CONFIG.MOBILE_BREAKPOINT;
    }

    /**
     * Get max auto height based on viewport
     * @returns {number} Max height in pixels
     */
    function getMaxAutoHeight() {
        return isMobileViewport() 
            ? CONFIG.MAX_AUTO_HEIGHT_MOBILE 
            : CONFIG.MAX_AUTO_HEIGHT_DESKTOP;
    }

    /**
     * Get scroll threshold based on viewport
     * @returns {number} Line count threshold
     */
    function getScrollThreshold() {
        return isMobileViewport()
            ? CONFIG.SCROLL_THRESHOLD_MOBILE
            : CONFIG.SCROLL_THRESHOLD_DESKTOP;
    }

    // ==========================================================================
    // Line Counting Logic
    // ==========================================================================

    /**
     * Count lines in a code block
     * @param {HTMLElement} codeElement - <code> or <pre> element
     * @returns {number} Line count
     */
    function countLines(codeElement) {
        if (!codeElement) return 0;

        const text = codeElement.textContent || '';
        const lines = text.split('\n');
        
        // Filter out empty trailing lines
        const nonEmptyLines = lines.filter((line, idx) => {
            // Keep all lines except trailing empty ones
            return idx < lines.length - 1 || line.trim().length > 0;
        });

        return nonEmptyLines.length;
    }

    // ==========================================================================
    // Height Calculation
    // ==========================================================================

    /**
     * Calculate optimal panel height
     * @param {number} lineCount - Number of lines in code block
     * @returns {Object} { height: number, useScrollbar: boolean }
     */
    function calculatePanelHeight(lineCount) {
        const maxAutoHeight = getMaxAutoHeight();
        const scrollThreshold = getScrollThreshold();
        
        // Calculate natural height (lines * line height + padding)
        const naturalHeight = (lineCount * CONFIG.LINE_HEIGHT_PX) + CONFIG.PADDING_PX;
        
        // Decision logic
        if (naturalHeight < CONFIG.MIN_PANEL_HEIGHT) {
            // Very short code: use minimum height
            return {
                height: CONFIG.MIN_PANEL_HEIGHT,
                useScrollbar: false,
                mode: 'minimum'
            };
        } else if (lineCount <= scrollThreshold && naturalHeight <= maxAutoHeight) {
            // Medium code: auto-height (no scrollbar)
            return {
                height: naturalHeight,
                useScrollbar: false,
                mode: 'auto-height'
            };
        } else {
            // Long code: fixed height with scrollbar
            return {
                height: maxAutoHeight,
                useScrollbar: true,
                mode: 'fixed-scroll'
            };
        }
    }

    // ==========================================================================
    // Panel Styling
    // ==========================================================================

    /**
     * Apply height styles to a code panel
     * @param {HTMLElement} panel - .before-panel or .after-panel element
     */
    function stylePanelHeight(panel) {
        if (!panel) return;

        const pre = panel.querySelector('pre');
        const code = pre ? pre.querySelector('code') : null;
        
        if (!pre || !code) {
            console.warn('Adaptive Panels: No <pre><code> found in panel', panel);
            return;
        }

        const lineCount = countLines(code);
        const { height, useScrollbar, mode } = calculatePanelHeight(lineCount);

        // Apply height to <pre> element
        pre.style.height = `${height}px`;
        pre.style.minHeight = `${CONFIG.MIN_PANEL_HEIGHT}px`;
        
        // Configure scrolling
        if (useScrollbar) {
            pre.style.overflowY = 'auto';
            pre.classList.add('fixed-height');
            pre.classList.remove('auto-height');
        } else {
            pre.style.overflowY = 'visible';
            pre.classList.add('auto-height');
            pre.classList.remove('fixed-height');
        }

        // Always allow horizontal scroll for long lines
        pre.style.overflowX = 'auto';

        // Debug logging (remove in production)
        console.debug(`Adaptive Panel [${mode}]:`, {
            lineCount,
            height: `${height}px`,
            useScrollbar,
            viewport: isMobileViewport() ? 'mobile' : 'desktop',
            panel: panel.className
        });
    }

    // ==========================================================================
    // Panel Discovery & Processing
    // ==========================================================================

    /**
     * Process all code panels on the page
     */
    function processAllPanels() {
        const panels = document.querySelectorAll('.before-panel, .after-panel');
        
        console.log(`Adaptive Panels: Processing ${panels.length} panels...`);
        
        panels.forEach((panel, idx) => {
            try {
                stylePanelHeight(panel);
            } catch (error) {
                console.error(`Error processing panel ${idx}:`, error, panel);
            }
        });
    }

    // ==========================================================================
    // Responsive Recalculation
    // ==========================================================================

    let resizeTimer;
    
    /**
     * Handle viewport resize with debouncing
     */
    function handleResize() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            console.log('Adaptive Panels: Recalculating for new viewport...');
            processAllPanels();
        }, 250); // 250ms debounce
    }

    // ==========================================================================
    // Initialization
    // ==========================================================================

    /**
     * Initialize adaptive panels system
     */
    function init() {
        // Wait for DOM and syntax highlighting to complete
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }

        // Wait for highlight.js to finish
        setTimeout(() => {
            console.log('Adaptive Panels v2.2.0: Initializing...');
            processAllPanels();
            
            // Add resize listener for responsive behavior
            window.addEventListener('resize', handleResize);
            
            console.log('Adaptive Panels: Initialization complete ✓');
        }, 500); // Give highlight.js time to process
    }

    // ==========================================================================
    // Public API (if needed for manual triggering)
    // ==========================================================================

    window.AdaptivePanels = {
        version: '2.2.0',
        refresh: processAllPanels,
        config: CONFIG
    };

    // Auto-initialize
    init();

})();
