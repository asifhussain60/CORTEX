/**
 * CORTEX CSS Layout Validator & Auto-Fixer
 * Validates and enforces consistent layout after DOM rendering
 * 
 * @author Asif Hussain
 * @version 1.0.0
 * @copyright © 2025 Asif Hussain. All rights reserved.
 */

class CORTEXLayoutValidator {
    constructor() {
        this.issues = [];
        this.fixes = [];
        this.config = {
            // Grid validation
            minGap: 24, // 1.5rem minimum
            maxGap: 48, // 3rem maximum
            optimalGap: 40, // 2.5rem optimal
            
            // Card validation
            minCardPadding: 32, // 2rem
            optimalCardPadding: 40, // 2.5rem
            
            // Tag validation
            minTagGap: 12, // 0.75rem
            minTagPadding: 8, // 0.5rem
            
            // Container validation
            maxContainerWidth: 1400,
            minContainerPadding: 24, // 1.5rem
            
            // Height validation
            maxHeightVariance: 50, // Max px difference between cards in same row
        };
    }

    /**
     * Main validation entry point
     */
    async validate() {
        console.log('🔍 CORTEX Layout Validator: Starting validation...');
        this.issues = [];
        this.fixes = [];

        // Wait for DOM to be fully rendered
        await this.waitForDOM();

        // Run all validation checks
        this.validateGridLayouts();
        this.validateCategoryPanels();
        this.validateLevel0Panels();
        this.validateContainers();
        this.validateResponsiveBreakpoints();
        this.validateCardHeights();
        this.validateTagSpacing();

        // Report results
        this.generateReport();

        // Auto-fix if enabled
        if (this.shouldAutoFix()) {
            this.applyFixes();
        }

        return {
            issues: this.issues,
            fixes: this.fixes,
            isValid: this.issues.length === 0
        };
    }

    /**
     * Wait for DOM and CSS to be fully loaded
     */
    waitForDOM() {
        return new Promise((resolve) => {
            if (document.readyState === 'complete') {
                setTimeout(resolve, 100); // Extra 100ms for CSS to settle
            } else {
                window.addEventListener('load', () => {
                    setTimeout(resolve, 100);
                });
            }
        });
    }

    /**
     * Validate category-panels-grid layouts
     */
    validateGridLayouts() {
        const grids = document.querySelectorAll('.category-panels-grid');
        
        grids.forEach((grid, index) => {
            const computedStyle = window.getComputedStyle(grid);
            const gap = parseInt(computedStyle.gap || computedStyle.gridGap);
            
            if (gap < this.config.minGap) {
                this.issues.push({
                    type: 'GRID_GAP_TOO_SMALL',
                    element: grid,
                    selector: `.category-panels-grid[${index}]`,
                    current: `${gap}px`,
                    expected: `${this.config.optimalGap}px`,
                    severity: 'HIGH'
                });
                
                this.fixes.push({
                    element: grid,
                    property: 'gap',
                    value: `${this.config.optimalGap}px`
                });
            }
            
            // Check grid-template-columns
            const columns = computedStyle.gridTemplateColumns;
            const width = grid.offsetWidth;
            
            if (width > 768 && !columns.includes('1fr 1fr')) {
                this.issues.push({
                    type: 'GRID_COLUMNS_INVALID',
                    element: grid,
                    selector: `.category-panels-grid[${index}]`,
                    current: columns,
                    expected: 'repeat(2, 1fr) for width > 768px',
                    severity: 'MEDIUM'
                });
            }
        });
    }

    /**
     * Validate category-subpanel cards
     */
    validateCategoryPanels() {
        const panels = document.querySelectorAll('.category-subpanel, .level0-category-subpanel');
        
        panels.forEach((panel, index) => {
            const computedStyle = window.getComputedStyle(panel);
            const padding = parseInt(computedStyle.paddingTop);
            
            // Check padding
            if (padding < this.config.minCardPadding) {
                this.issues.push({
                    type: 'CARD_PADDING_TOO_SMALL',
                    element: panel,
                    selector: panel.className,
                    current: `${padding}px`,
                    expected: `${this.config.optimalCardPadding}px`,
                    severity: 'MEDIUM'
                });
                
                this.fixes.push({
                    element: panel,
                    property: 'padding',
                    value: `${this.config.optimalCardPadding}px ${this.config.minCardPadding}px`
                });
            }
            
            // Check if flexbox is applied
            if (computedStyle.display !== 'flex') {
                this.issues.push({
                    type: 'CARD_MISSING_FLEXBOX',
                    element: panel,
                    selector: panel.className,
                    current: computedStyle.display,
                    expected: 'flex',
                    severity: 'HIGH'
                });
                
                this.fixes.push({
                    element: panel,
                    property: 'display',
                    value: 'flex'
                });
                this.fixes.push({
                    element: panel,
                    property: 'flex-direction',
                    value: 'column'
                });
            }
        });
    }

    /**
     * Validate Level 0 panel layouts
     */
    validateLevel0Panels() {
        const grids = document.querySelectorAll('.level0-categories-grid');
        
        grids.forEach((grid, index) => {
            const computedStyle = window.getComputedStyle(grid);
            const gap = parseInt(computedStyle.gap || computedStyle.gridGap);
            
            if (gap < this.config.minGap) {
                this.issues.push({
                    type: 'LEVEL0_GRID_GAP_TOO_SMALL',
                    element: grid,
                    selector: `.level0-categories-grid[${index}]`,
                    current: `${gap}px`,
                    expected: `${this.config.optimalGap}px`,
                    severity: 'HIGH'
                });
                
                this.fixes.push({
                    element: grid,
                    property: 'gap',
                    value: `${this.config.optimalGap}px`
                });
            }
        });
    }

    /**
     * Validate container widths
     */
    validateContainers() {
        const containers = document.querySelectorAll('.level0-container, .level0-main-panel-wrapper');
        
        containers.forEach((container, index) => {
            const computedStyle = window.getComputedStyle(container);
            const maxWidth = parseInt(computedStyle.maxWidth);
            
            if (maxWidth < 1200) {
                this.issues.push({
                    type: 'CONTAINER_WIDTH_TOO_NARROW',
                    element: container,
                    selector: container.className,
                    current: `${maxWidth}px`,
                    expected: `${this.config.maxContainerWidth}px`,
                    severity: 'MEDIUM'
                });
                
                this.fixes.push({
                    element: container,
                    property: 'max-width',
                    value: `${this.config.maxContainerWidth}px`
                });
            }
        });
    }

    /**
     * Validate responsive breakpoints are working
     */
    validateResponsiveBreakpoints() {
        const width = window.innerWidth;
        const grids = document.querySelectorAll('.category-panels-grid, .level0-categories-grid');
        
        grids.forEach((grid, index) => {
            const computedStyle = window.getComputedStyle(grid);
            const columns = computedStyle.gridTemplateColumns.split(' ').length;
            
            if (width >= 768 && columns !== 2) {
                this.issues.push({
                    type: 'RESPONSIVE_BREAKPOINT_FAILURE',
                    element: grid,
                    selector: grid.className,
                    current: `${columns} columns at ${width}px`,
                    expected: '2 columns for width >= 768px',
                    severity: 'HIGH'
                });
            }
            
            if (width < 768 && columns !== 1) {
                this.issues.push({
                    type: 'RESPONSIVE_BREAKPOINT_FAILURE',
                    element: grid,
                    selector: grid.className,
                    current: `${columns} columns at ${width}px`,
                    expected: '1 column for width < 768px',
                    severity: 'MEDIUM'
                });
            }
        });
    }

    /**
     * Validate card heights in same row
     */
    validateCardHeights() {
        const grids = document.querySelectorAll('.category-panels-grid, .level0-categories-grid');
        
        grids.forEach((grid) => {
            const panels = Array.from(grid.children);
            const computedStyle = window.getComputedStyle(grid);
            const columns = computedStyle.gridTemplateColumns.split(' ').length;
            
            // Group cards by row
            for (let i = 0; i < panels.length; i += columns) {
                const rowCards = panels.slice(i, i + columns);
                const heights = rowCards.map(card => card.offsetHeight);
                const maxHeight = Math.max(...heights);
                const minHeight = Math.min(...heights);
                const variance = maxHeight - minHeight;
                
                if (variance > this.config.maxHeightVariance) {
                    this.issues.push({
                        type: 'CARD_HEIGHT_VARIANCE',
                        element: grid,
                        selector: `${grid.className} row ${Math.floor(i / columns) + 1}`,
                        current: `${variance}px variance (${minHeight}px - ${maxHeight}px)`,
                        expected: `< ${this.config.maxHeightVariance}px variance`,
                        severity: 'LOW',
                        info: 'Consider adjusting content or setting min-height'
                    });
                }
            }
        });
    }

    /**
     * Validate tag spacing
     */
    validateTagSpacing() {
        const tagContainers = document.querySelectorAll('.category-tags, .level0-category-tags');
        
        tagContainers.forEach((container, index) => {
            const computedStyle = window.getComputedStyle(container);
            const gap = parseInt(computedStyle.gap);
            
            if (gap < this.config.minTagGap) {
                this.issues.push({
                    type: 'TAG_GAP_TOO_SMALL',
                    element: container,
                    selector: container.className,
                    current: `${gap}px`,
                    expected: `${this.config.minTagGap}px`,
                    severity: 'LOW'
                });
                
                this.fixes.push({
                    element: container,
                    property: 'gap',
                    value: `${this.config.minTagGap}px`
                });
            }
            
            // Check if margin-top: auto is applied (push tags to bottom)
            if (computedStyle.marginTop !== 'auto') {
                this.issues.push({
                    type: 'TAGS_NOT_BOTTOM_ALIGNED',
                    element: container,
                    selector: container.className,
                    current: computedStyle.marginTop,
                    expected: 'auto',
                    severity: 'LOW'
                });
                
                this.fixes.push({
                    element: container,
                    property: 'margin-top',
                    value: 'auto'
                });
            }
        });
    }

    /**
     * Generate validation report
     */
    generateReport() {
        console.group('📊 CORTEX Layout Validation Report');
        
        if (this.issues.length === 0) {
            console.log('%c✅ All layout checks passed!', 'color: #00ff88; font-weight: bold; font-size: 14px');
        } else {
            console.log(`%c⚠️ Found ${this.issues.length} layout issues`, 'color: #ffa500; font-weight: bold; font-size: 14px');
            
            // Group by severity
            const bySeverity = {
                HIGH: this.issues.filter(i => i.severity === 'HIGH'),
                MEDIUM: this.issues.filter(i => i.severity === 'MEDIUM'),
                LOW: this.issues.filter(i => i.severity === 'LOW')
            };
            
            ['HIGH', 'MEDIUM', 'LOW'].forEach(severity => {
                if (bySeverity[severity].length > 0) {
                    console.group(`${severity} (${bySeverity[severity].length})`);
                    bySeverity[severity].forEach(issue => {
                        console.log(`${issue.type}:`, {
                            selector: issue.selector,
                            current: issue.current,
                            expected: issue.expected,
                            info: issue.info || 'N/A'
                        });
                    });
                    console.groupEnd();
                }
            });
        }
        
        if (this.fixes.length > 0) {
            console.log(`%c🔧 ${this.fixes.length} automatic fixes available`, 'color: #00d4ff; font-weight: bold');
        }
        
        console.groupEnd();
    }

    /**
     * Check if auto-fix should be applied
     */
    shouldAutoFix() {
        // Check for data attribute or localStorage setting
        return document.documentElement.hasAttribute('data-cortex-autofix') ||
               localStorage.getItem('cortex-layout-autofix') === 'true';
    }

    /**
     * Apply fixes to DOM
     */
    applyFixes() {
        if (this.fixes.length === 0) {
            console.log('✅ No fixes to apply');
            return;
        }

        console.log(`🔧 Applying ${this.fixes.length} fixes...`);
        
        this.fixes.forEach(fix => {
            fix.element.style[fix.property] = fix.value;
        });
        
        console.log('%c✅ Fixes applied successfully!', 'color: #00ff88; font-weight: bold');
        
        // Mark as fixed
        document.documentElement.setAttribute('data-cortex-fixed', 'true');
    }

    /**
     * Enable auto-fix for future page loads
     */
    enableAutoFix() {
        localStorage.setItem('cortex-layout-autofix', 'true');
        document.documentElement.setAttribute('data-cortex-autofix', 'true');
        console.log('✅ Auto-fix enabled for future page loads');
    }

    /**
     * Disable auto-fix
     */
    disableAutoFix() {
        localStorage.removeItem('cortex-layout-autofix');
        document.documentElement.removeAttribute('data-cortex-autofix');
        console.log('❌ Auto-fix disabled');
    }
}

// Initialize validator
const cortexValidator = new CORTEXLayoutValidator();

// Auto-run on page load
window.addEventListener('load', () => {
    setTimeout(() => {
        cortexValidator.validate();
    }, 200); // Wait 200ms for all CSS to settle
});

// Expose to window for manual control
window.CORTEX = window.CORTEX || {};
window.CORTEX.validator = cortexValidator;

// Console commands
console.log('%c🧠 CORTEX Layout Validator loaded', 'color: #00d4ff; font-weight: bold; font-size: 14px');
console.log('%c   Commands:', 'color: #a0a6c0');
console.log('%c   CORTEX.validator.validate()       - Run validation', 'color: #a0a6c0');
console.log('%c   CORTEX.validator.applyFixes()     - Apply fixes manually', 'color: #a0a6c0');
console.log('%c   CORTEX.validator.enableAutoFix()  - Enable auto-fix', 'color: #a0a6c0');
console.log('%c   CORTEX.validator.disableAutoFix() - Disable auto-fix', 'color: #a0a6c0');
