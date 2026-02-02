// ============================================
// CORTEX Dashboard Automated Chart Test Suite
// ============================================
// Automatically clicks through all tabs and sub-tabs to test chart initialization
// Open dashboard-gpt.html in browser and paste this into the console

(async function() {
    console.log('%c🤖 CORTEX Automated Chart Tests', 'font-size: 20px; font-weight: bold; color: #4d8cff;');
    console.log('%c' + '='.repeat(50), 'color: #4d8cff;');
    
    // Wait helper
    const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));
    
    // Chart test configuration
    const testPlan = [
        { 
            tab: 'vulnerabilities',
            subTabs: [
                { button: 'code-smells', chart: 'code-smells-chart', name: 'Code Smells' },
                { button: 'anti-patterns', chart: 'anti-patterns-chart', name: 'Anti-Patterns' },
                { button: 'security-issues', chart: 'security-chart', name: 'Security Issues' },
                { button: 'best-practices', chart: 'best-practices-chart', name: 'Best Practices' }
            ]
        },
        {
            tab: 'security',
            subTabs: [
                { button: 'dep-audit', chart: 'dep-audit-chart', name: 'Dependency Audit' }
            ]
        },
        {
            tab: 'dependencies',
            subTabs: [
                { button: 'dep-licenses', chart: 'license-chart', name: 'License Distribution' }
            ]
        },
        {
            tab: 'quality',
            subTabs: [
                { button: 'complexity', chart: 'complexity-chart', name: 'Complexity' },
                { button: 'duplication', chart: 'duplication-chart', name: 'Duplication' }
            ]
        },
        {
            tab: 'testing',
            subTabs: [
                { button: 'coverage', chart: 'coverage-trend-chart', name: 'Coverage Trend' }
            ]
        }
    ];

    let totalPassed = 0;
    let totalFailed = 0;
    const failures = [];

    console.log('\n📊 Starting Automated Test Sequence...\n');

    // Test each tab
    for (const testTab of testPlan) {
        console.log(`\n%c▶️  Testing Tab: ${testTab.tab.toUpperCase()}`, 'color: #3b82f6; font-weight: bold;');
        
        // Click main tab
        const tabButton = document.querySelector(`[data-tab="${testTab.tab}"]`);
        if (!tabButton) {
            console.error(`   ❌ Tab button not found: ${testTab.tab}`);
            continue;
        }
        
        tabButton.click();
        await wait(300); // Wait for tab transition
        
        // Test each sub-tab
        for (const subTest of testTab.subTabs) {
            console.log(`\n   🔍 Sub-Tab: ${subTest.name}`);
            
            // Click sub-tab button
            const subTabButton = document.querySelector(`[data-subtab="${subTest.button}"]`);
            if (!subTabButton) {
                console.error(`      ❌ Sub-tab button not found: ${subTest.button}`);
                totalFailed++;
                failures.push({ 
                    tab: testTab.tab, 
                    subTab: subTest.name, 
                    reason: 'Sub-tab button not found' 
                });
                continue;
            }
            
            subTabButton.click();
            await wait(200); // Wait for chart initialization
            
            // Test chart
            const container = document.getElementById(subTest.chart);
            if (!container) {
                console.log(`      ❌ FAIL - Container not found: ${subTest.chart}`);
                totalFailed++;
                failures.push({ 
                    tab: testTab.tab, 
                    subTab: subTest.name, 
                    reason: 'Container not found in DOM' 
                });
                continue;
            }
            
            // Check ECharts instance
            if (typeof echarts === 'undefined') {
                console.log(`      ❌ FAIL - ECharts not loaded`);
                totalFailed++;
                failures.push({ 
                    tab: testTab.tab, 
                    subTab: subTest.name, 
                    reason: 'ECharts library not loaded' 
                });
                continue;
            }
            
            const chartInstance = echarts.getInstanceByDom(container);
            const rect = container.getBoundingClientRect();
            
            if (chartInstance) {
                console.log(`      %c✅ PASS - Chart initialized`, 'color: #22c55e; font-weight: bold;');
                console.log(`         Dimensions: ${Math.round(rect.width)}x${Math.round(rect.height)}px`);
                console.log(`         Chart ID: ${subTest.chart}`);
                totalPassed++;
            } else {
                console.log(`      ❌ FAIL - Chart instance not created`);
                console.log(`         Container: ${Math.round(rect.width)}x${Math.round(rect.height)}px`);
                totalFailed++;
                failures.push({ 
                    tab: testTab.tab, 
                    subTab: subTest.name, 
                    reason: 'Chart instance not created after initialization' 
                });
            }
        }
    }

    // Final Summary
    const totalTests = testPlan.reduce((sum, tab) => sum + tab.subTabs.length, 0);
    const passRate = ((totalPassed / totalTests) * 100).toFixed(1);
    
    console.log('\n\n' + '='.repeat(50));
    console.log('%c📊 FINAL TEST RESULTS', 'font-size: 18px; font-weight: bold;');
    console.log('='.repeat(50));
    console.log(`%c✅ Passed: ${totalPassed}/${totalTests}`, 'color: #22c55e; font-weight: bold; font-size: 14px;');
    console.log(`%c❌ Failed: ${totalFailed}/${totalTests}`, 'color: #ef4444; font-weight: bold; font-size: 14px;');
    console.log(`%c📈 Pass Rate: ${passRate}%`, passRate === '100.0' ? 'color: #22c55e; font-weight: bold; font-size: 14px;' : 'color: #f59e0b; font-weight: bold; font-size: 14px;');

    if (failures.length > 0) {
        console.log('\n%c⚠️  FAILURES:', 'color: #ef4444; font-weight: bold; font-size: 14px;');
        failures.forEach(f => {
            console.log(`   • ${f.tab} > ${f.subTab}: ${f.reason}`);
        });
    } else {
        console.log('\n%c🎉 ALL TESTS PASSED!', 'color: #22c55e; font-weight: bold; font-size: 16px;');
    }

    // Return results
    return {
        passed: totalPassed,
        failed: totalFailed,
        total: totalTests,
        passRate: passRate + '%',
        failures: failures,
        status: totalFailed === 0 ? 'SUCCESS' : 'FAILURE'
    };
})();
