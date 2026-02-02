// ============================================
// INSTANT TAB & CHART VERIFICATION TEST
// ============================================
// Paste this into browser console after opening dashboard-gpt.html

console.clear();
console.log('%c🚀 CORTEX Dashboard - Quick Test', 'font-size: 18px; font-weight: bold; color: #4d8cff;');
console.log('%c' + '='.repeat(60), 'color: #4d8cff;');

// Test 1: Check if DOMContentLoaded fired
if (typeof tabButtons !== 'undefined') {
    console.log('%c✅ JavaScript loaded successfully', 'color: #22c55e');
} else {
    console.log('%c❌ tabButtons not defined - script may not have loaded', 'color: #ef4444');
}

// Test 2: Check tab buttons exist
const tabs = document.querySelectorAll('.tab-button');
console.log(`\n📑 Tab Buttons Found: ${tabs.length}/9`);
if (tabs.length === 9) {
    console.log('%c✅ All tab buttons present', 'color: #22c55e');
} else {
    console.log('%c⚠️  Expected 9 tabs, found ' + tabs.length, 'color: #f59e0b');
}

// Test 3: Test tab clicks
console.log('\n🖱️  Testing Tab Clicks...');
let clicksPassed = 0;
let clicksFailed = 0;

tabs.forEach((tab, index) => {
    const tabName = tab.dataset.tab;
    try {
        tab.click();
        const targetContent = document.getElementById(`${tabName}-tab`);
        if (targetContent && targetContent.classList.contains('active')) {
            console.log(`  ✅ ${tabName} - Click works`);
            clicksPassed++;
        } else {
            console.log(`  ❌ ${tabName} - Content not activated`);
            clicksFailed++;
        }
    } catch (error) {
        console.log(`  ❌ ${tabName} - Error: ${error.message}`);
        clicksFailed++;
    }
});

// Test 4: Check chartConfigs
console.log('\n📊 Chart Configuration Check...');
if (typeof chartConfigs !== 'undefined') {
    const configuredCharts = Object.keys(chartConfigs);
    console.log(`✅ chartConfigs exists with ${configuredCharts.length} charts:`);
    configuredCharts.forEach(id => {
        console.log(`  • ${id}`);
    });
} else {
    console.log('❌ chartConfigs not found - charts will not initialize');
}

// Test 5: Check initializeChart function
if (typeof initializeChart === 'function') {
    console.log('\n✅ initializeChart function exists');
} else {
    console.log('\n❌ initializeChart function not found');
}

// Test 6: Try initializing a chart manually
console.log('\n🧪 Manual Chart Initialization Test...');
try {
    // Switch to vulnerabilities tab first
    const vulnTab = document.querySelector('[data-tab="vulnerabilities"]');
    if (vulnTab) {
        vulnTab.click();
        setTimeout(() => {
            // Click code smells sub-tab
            const codeSmellsSubTab = document.querySelector('[data-subtab="code-smells"]');
            if (codeSmellsSubTab) {
                codeSmellsSubTab.click();
                setTimeout(() => {
                    if (typeof initializeChart === 'function') {
                        initializeChart('code-smells-chart');
                        console.log('✅ Chart initialization triggered');
                    }
                }, 200);
            }
        }, 200);
    }
} catch (error) {
    console.log(`❌ Chart test failed: ${error.message}`);
}

// Summary
console.log('\n' + '='.repeat(60));
console.log('%c📊 Test Summary', 'font-size: 16px; font-weight: bold;');
console.log('='.repeat(60));
console.log(`%c✅ Tabs Working: ${clicksPassed}/${tabs.length}`, clicksPassed === tabs.length ? 'color: #22c55e; font-weight: bold' : 'color: #f59e0b');
console.log(`%c❌ Tabs Failed: ${clicksFailed}`, clicksFailed === 0 ? 'color: #666' : 'color: #ef4444; font-weight: bold');

if (clicksPassed === tabs.length && typeof chartConfigs !== 'undefined') {
    console.log('\n%c🎉 ALL TESTS PASSED! Dashboard is working correctly.', 'color: #22c55e; font-size: 14px; font-weight: bold; background: rgba(34, 197, 94, 0.1); padding: 8px;');
    console.log('\n💡 Next: Click through tabs to see charts render automatically!');
} else {
    console.log('\n%c⚠️  Some tests failed. Check errors above.', 'color: #f59e0b; font-size: 14px; font-weight: bold;');
}
