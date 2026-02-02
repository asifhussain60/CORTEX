// ============================================
// CORTEX Dashboard Chart Loading Test Suite
// ============================================
// Open dashboard-gpt.html in browser and paste this into the console

(function() {
    console.log('%c🧪 CORTEX Dashboard Chart Tests', 'font-size: 20px; font-weight: bold; color: #4d8cff;');
    console.log('%c' + '='.repeat(50), 'color: #4d8cff;');
    
    // Test configuration
    const chartTests = [
        { id: 'code-smells-chart', name: 'Code Smells Chart', tab: 'Vulnerabilities > Code Smells' },
        { id: 'anti-patterns-chart', name: 'Anti-Patterns Chart', tab: 'Vulnerabilities > Anti-Patterns' },
        { id: 'security-chart', name: 'Security Chart', tab: 'Vulnerabilities > Security' },
        { id: 'best-practices-chart', name: 'Best Practices Chart', tab: 'Vulnerabilities > Best Practices' },
        { id: 'dep-audit-chart', name: 'Dependency Audit Chart', tab: 'Security > Dependency Audit' },
        { id: 'license-chart', name: 'License Chart', tab: 'Dependencies' },
        { id: 'complexity-chart', name: 'Complexity Chart', tab: 'Quality' },
        { id: 'duplication-chart', name: 'Duplication Chart', tab: 'Quality' },
        { id: 'coverage-trend-chart', name: 'Coverage Trend Chart', tab: 'Testing' }
    ];

    let passed = 0;
    let failed = 0;
    const failures = [];

    console.log('\n📊 Running Chart Tests...\n');

    chartTests.forEach(test => {
        const container = document.getElementById(test.id);
        let status = '❌ FAIL';
        let reason = '';

        // Test 1: Container exists
        if (!container) {
            reason = 'Container not found in DOM';
            failed++;
            failures.push({ test: test.name, reason });
            console.log(`${status} ${test.name} [${test.tab}]`);
            console.log(`   └─ ${reason}`);
            return;
        }

        // Test 2: Container has dimensions
        const rect = container.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) {
            reason = `Container has no dimensions (${rect.width}x${rect.height}px)`;
            // This might be OK if chart is in hidden tab
            if (container.closest('.sub-tab-content:not(.active)') || 
                container.closest('.tab-content:not(.active)')) {
                reason += ' - Tab not active (OK)';
            }
        }

        // Test 3: ECharts loaded
        if (typeof echarts === 'undefined') {
            reason = 'ECharts library not loaded';
            failed++;
            failures.push({ test: test.name, reason });
            console.log(`${status} ${test.name} [${test.tab}]`);
            console.log(`   └─ ${reason}`);
            return;
        }

        // Test 4: Chart instance exists or will be created
        const chartInstance = echarts.getInstanceByDom(container);
        if (chartInstance) {
            status = '✅ PASS';
            passed++;
            console.log(`%c${status} ${test.name} [${test.tab}]`, 'color: #22c55e');
            console.log(`   └─ Chart initialized (${Math.round(rect.width)}x${Math.round(rect.height)}px)`);
        } else if (rect.width === 0 && rect.height === 0) {
            status = '⏳ PENDING';
            console.log(`%c${status} ${test.name} [${test.tab}]`, 'color: #f59e0b');
            console.log(`   └─ Container exists but chart not yet initialized (lazy loading)`);
        } else {
            reason = 'Container exists but chart instance not created';
            failed++;
            failures.push({ test: test.name, reason });
            console.log(`${status} ${test.name} [${test.tab}]`);
            console.log(`   └─ ${reason}`);
        }
    });

    // Summary
    console.log('\n' + '='.repeat(50));
    console.log('%c📊 Test Summary', 'font-size: 16px; font-weight: bold;');
    console.log('='.repeat(50));
    console.log(`%c✅ Passed: ${passed}`, 'color: #22c55e; font-weight: bold;');
    console.log(`%c❌ Failed: ${failed}`, 'color: #ef4444; font-weight: bold;');
    console.log(`📝 Total: ${chartTests.length}`);

    if (failures.length > 0) {
        console.log('\n%c⚠️  Failures:', 'color: #ef4444; font-weight: bold;');
        failures.forEach(f => {
            console.log(`   • ${f.test}: ${f.reason}`);
        });
    }

    // Instructions
    console.log('\n%c💡 Tips:', 'color: #4d8cff; font-weight: bold;');
    console.log('   • Charts use lazy loading - they initialize when tabs are clicked');
    console.log('   • Click on each tab to activate chart rendering');
    console.log('   • Run this test again after clicking tabs to verify lazy loading');
    console.log('   • Check browser console for ECharts initialization logs');

    // Return results for automation
    return {
        passed,
        failed,
        total: chartTests.length,
        failures,
        passRate: ((passed / chartTests.length) * 100).toFixed(1) + '%'
    };
})();
