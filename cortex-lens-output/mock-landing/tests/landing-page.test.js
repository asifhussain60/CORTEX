/**
 * CORTEX Lens V3 - Landing Page Test Suite
 * 
 * Purpose: Prevent regressions in layout, styling, and functionality
 * Coverage: Structure, CSS properties, JavaScript behavior, responsiveness
 * 
 * Run: Open tests/test-runner.html in browser
 * 
 * Author: Asif Hussain
 * Version: 1.0.0
 */

const LandingPageTests = {
    results: [],
    
    // Test runner
    async runAll() {
        console.log('🧪 Starting CORTEX Landing Page Tests...\n');
        this.results = [];
        
        await this.testStructure();
        await this.testLayout();
        await this.testStyling();
        await this.testResponsiveness();
        await this.testJavaScript();
        
        this.reportResults();
    },
    
    // Helper: Assert condition
    assert(condition, testName, errorMsg = '') {
        const result = {
            name: testName,
            passed: condition,
            error: condition ? null : errorMsg
        };
        this.results.push(result);
        
        const icon = condition ? '✅' : '❌';
        console.log(`${icon} ${testName}${errorMsg ? `: ${errorMsg}` : ''}`);
    },
    
    // Test Suite 1: HTML Structure
    async testStructure() {
        console.log('\n📋 Testing HTML Structure...');
        
        // Header exists
        const header = document.querySelector('.dashboard-header');
        this.assert(!!header, 'Header element exists');
        
        // Logo-sidebar container exists and is fixed
        const logoContainer = document.querySelector('.logo-sidebar-container');
        this.assert(!!logoContainer, 'Logo-sidebar container exists');
        
        const logoContainerStyle = window.getComputedStyle(logoContainer);
        this.assert(
            logoContainerStyle.position === 'fixed',
            'Logo-sidebar container is position: fixed',
            `Expected 'fixed', got '${logoContainerStyle.position}'`
        );
        
        // Logo exists with correct size
        const logo = document.querySelector('.cortex-logo');
        this.assert(!!logo, 'CORTEX logo exists');
        
        const logoWidth = parseInt(window.getComputedStyle(logo).width);
        this.assert(
            logoWidth === 150,
            'Logo width is 150px',
            `Expected 150px, got ${logoWidth}px`
        );
        
        // Sidebar exists
        const sidebar = document.querySelector('.sidebar');
        this.assert(!!sidebar, 'Sidebar navigation exists');
        
        // Tab list has no bullets
        const tabList = document.querySelector('.tab-list');
        const tabListStyle = window.getComputedStyle(tabList);
        this.assert(
            tabListStyle.listStyle === 'none' || tabListStyle.listStyleType === 'none',
            'Tab list has no bullets',
            `Expected 'none', got '${tabListStyle.listStyle}'`
        );
        
        // 5 navigation tabs exist
        const tabs = document.querySelectorAll('.tab-link');
        this.assert(
            tabs.length === 5,
            '5 navigation tabs exist',
            `Expected 5, found ${tabs.length}`
        );
        
        // Main content exists
        const mainContent = document.querySelector('.main-content');
        this.assert(!!mainContent, 'Main content area exists');
        
        // Main content has left margin for fixed sidebar
        const mainStyle = window.getComputedStyle(mainContent);
        const marginLeft = parseInt(mainStyle.marginLeft);
        this.assert(
            marginLeft === 280,
            'Main content has 280px left margin',
            `Expected 280px, got ${marginLeft}px`
        );
        
        // KPI grid exists
        const kpiGrid = document.querySelector('.kpi-grid');
        this.assert(!!kpiGrid, 'KPI grid exists');
        
        // 6 KPI cards exist
        const kpiCards = document.querySelectorAll('.kpi-card');
        this.assert(
            kpiCards.length === 6,
            '6 KPI cards exist',
            `Expected 6, found ${kpiCards.length}`
        );
        
        // Health chart canvas exists
        const chartCanvas = document.getElementById('healthChart');
        this.assert(!!chartCanvas, 'Health chart canvas exists');
    },
    
    // Test Suite 2: Layout Behavior
    async testLayout() {
        console.log('\n📐 Testing Layout Behavior...');
        
        // Sidebar is full height
        const logoContainer = document.querySelector('.logo-sidebar-container');
        const containerHeight = logoContainer.offsetHeight;
        const viewportHeight = window.innerHeight;
        const expectedHeight = viewportHeight - 80; // minus header height
        
        this.assert(
            Math.abs(containerHeight - expectedHeight) < 5,
            'Sidebar spans full viewport height',
            `Expected ~${expectedHeight}px, got ${containerHeight}px`
        );
        
        // Main content is scrollable
        const mainContent = document.querySelector('.main-content');
        const mainHeight = mainContent.scrollHeight;
        this.assert(
            mainHeight > viewportHeight,
            'Main content is scrollable (height > viewport)',
            `Main height: ${mainHeight}px, Viewport: ${viewportHeight}px`
        );
        
        // Sidebar does not scroll with page
        const sidebarPosition = window.getComputedStyle(logoContainer).position;
        this.assert(
            sidebarPosition === 'fixed',
            'Sidebar remains fixed during scroll',
            `Expected 'fixed', got '${sidebarPosition}'`
        );
        
        // No dashboard-layout wrapper exists (removed to fix grid conflict)
        const dashboardLayout = document.querySelector('.dashboard-layout');
        this.assert(
            !dashboardLayout,
            'No dashboard-layout wrapper exists',
            'Dashboard-layout should have been removed'
        );
    },
    
    // Test Suite 3: CSS Styling
    async testStyling() {
        console.log('\n🎨 Testing CSS Styling...');
        
        // Glassmorphism effects on cards
        const glassCards = document.querySelectorAll('.glass-card');
        this.assert(
            glassCards.length > 0,
            'Glass cards exist in DOM',
            `Found ${glassCards.length} cards`
        );
        
        const firstCard = glassCards[0];
        const cardStyle = window.getComputedStyle(firstCard);
        this.assert(
            cardStyle.backdropFilter.includes('blur'),
            'Glass cards have backdrop-filter blur',
            `Got: ${cardStyle.backdropFilter}`
        );
        
        // Logo has drop-shadow effect
        const logo = document.querySelector('.cortex-logo');
        const logoStyle = window.getComputedStyle(logo);
        this.assert(
            logoStyle.filter.includes('drop-shadow'),
            'Logo has drop-shadow effect',
            `Got: ${logoStyle.filter}`
        );
        
        // KPI cards have min-height
        const kpiCard = document.querySelector('.kpi-card');
        const kpiStyle = window.getComputedStyle(kpiCard);
        const minHeight = parseInt(kpiStyle.minHeight);
        this.assert(
            minHeight >= 200,
            'KPI cards have min-height >= 200px',
            `Expected >=200px, got ${minHeight}px`
        );
        
        // Theme toggle button exists
        const themeToggle = document.getElementById('themeToggle');
        this.assert(!!themeToggle, 'Theme toggle button exists');
        
        // Current theme is set
        const currentTheme = document.documentElement.getAttribute('data-theme');
        this.assert(
            currentTheme === 'dark' || currentTheme === 'light',
            'Valid theme is applied',
            `Expected 'dark' or 'light', got '${currentTheme}'`
        );
    },
    
    // Test Suite 4: Responsiveness
    async testResponsiveness() {
        console.log('\n📱 Testing Responsiveness...');
        
        // Store original width
        const originalWidth = window.innerWidth;
        
        // KPI grid is responsive (should be grid layout)
        const kpiGrid = document.querySelector('.kpi-grid');
        const gridStyle = window.getComputedStyle(kpiGrid);
        this.assert(
            gridStyle.display === 'grid',
            'KPI grid uses CSS Grid',
            `Expected 'grid', got '${gridStyle.display}'`
        );
        
        // Tab links are flex containers
        const tabLink = document.querySelector('.tab-link');
        const tabStyle = window.getComputedStyle(tabLink);
        this.assert(
            tabStyle.display === 'flex',
            'Tab links use flexbox',
            `Expected 'flex', got '${tabStyle.display}'`
        );
        
        // Responsive breakpoints exist (check media query support)
        const hasResponsiveCSS = Array.from(document.styleSheets)
            .some(sheet => {
                try {
                    return Array.from(sheet.cssRules || [])
                        .some(rule => rule.type === CSSRule.MEDIA_RULE);
                } catch (e) {
                    return false;
                }
            });
        
        this.assert(
            hasResponsiveCSS,
            'Responsive media queries defined',
            'No media queries found in stylesheets'
        );
    },
    
    // Test Suite 5: JavaScript Functionality
    async testJavaScript() {
        console.log('\n⚙️ Testing JavaScript Functionality...');
        
        // Theme toggle function exists
        this.assert(
            typeof toggleTheme === 'function',
            'toggleTheme function exists'
        );
        
        // Tab switching works
        const tabs = document.querySelectorAll('.tab-link');
        const firstTab = tabs[0];
        const secondTab = tabs[1];
        
        // Simulate click on second tab
        secondTab.click();
        
        // Wait for animation
        await new Promise(resolve => setTimeout(resolve, 100));
        
        this.assert(
            secondTab.classList.contains('active'),
            'Tab switching updates active class',
            'Second tab should have active class after click'
        );
        
        // Check if content visibility toggled
        const tabContents = document.querySelectorAll('.tab-content');
        const activeContent = document.querySelector('.tab-content.active');
        this.assert(
            !!activeContent,
            'One tab content is active',
            'No active tab content found'
        );
        
        // Restore first tab
        firstTab.click();
        
        // Analysis data exists
        this.assert(
            typeof analysisData !== 'undefined',
            'analysisData object exists'
        );
        
        // Analysis data has required structure
        if (typeof analysisData !== 'undefined') {
            this.assert(
                analysisData.health && analysisData.metadata,
                'analysisData has health and metadata properties'
            );
            
            this.assert(
                analysisData.health.overall_score !== undefined,
                'Health score is defined in analysisData'
            );
        }
        
        // Chart.js is loaded
        this.assert(
            typeof Chart !== 'undefined',
            'Chart.js library is loaded'
        );
    },
    
    // Report results
    reportResults() {
        console.log('\n' + '='.repeat(50));
        console.log('📊 TEST RESULTS SUMMARY');
        console.log('='.repeat(50));
        
        const total = this.results.length;
        const passed = this.results.filter(r => r.passed).length;
        const failed = total - passed;
        const passRate = ((passed / total) * 100).toFixed(1);
        
        console.log(`Total Tests: ${total}`);
        console.log(`✅ Passed: ${passed}`);
        console.log(`❌ Failed: ${failed}`);
        console.log(`Pass Rate: ${passRate}%\n`);
        
        if (failed > 0) {
            console.log('Failed Tests:');
            this.results.filter(r => !r.passed).forEach(r => {
                console.log(`  ❌ ${r.name}`);
                if (r.error) console.log(`     ${r.error}`);
            });
        }
        
        // Visual result indicator
        const resultDiv = document.createElement('div');
        resultDiv.id = 'test-results';
        resultDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 20px;
            background: ${failed === 0 ? '#10b981' : '#ef4444'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 9999;
            font-family: monospace;
        `;
        resultDiv.innerHTML = `
            <strong>${failed === 0 ? '✅ ALL TESTS PASSED' : '❌ TESTS FAILED'}</strong><br>
            ${passed}/${total} tests passed (${passRate}%)
        `;
        document.body.appendChild(resultDiv);
        
        // Auto-hide after 5 seconds
        setTimeout(() => resultDiv.remove(), 5000);
        
        return {
            total,
            passed,
            failed,
            passRate,
            allPassed: failed === 0
        };
    }
};

// Auto-run tests when page loads
window.addEventListener('load', () => {
    // Wait for everything to settle
    setTimeout(() => {
        LandingPageTests.runAll();
    }, 1000);
});

// Export for manual testing
window.LandingPageTests = LandingPageTests;
