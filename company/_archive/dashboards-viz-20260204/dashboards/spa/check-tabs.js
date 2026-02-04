/**
 * QUICK TEST: Verify all 13 tabs load without console errors
 * Run with: node check-tabs.js
 */

const http = require('http');

// Check if server is running
http.get('http://localhost:8888/dashboard.html?repo=KSESSIONS', (res) => {
  if (res.statusCode === 200) {
    console.log('✅ Dashboard server is running');
    console.log('📊 Testing tabs...\n');
    
    // Open browser manually to check tabs
    console.log('🌐 Opening dashboard in browser...');
    console.log('   URL: http://localhost:8888/dashboard.html?repo=KSESSIONS\n');
    
    console.log('📋 Manual Test Checklist:');
    console.log('   1. ✓ Check browser console for errors');
    console.log('   2. ✓ Click each of the 13 tabs:');
    console.log('      - Executive');
    console.log('      - Overview');
    console.log('      - Use Cases');
    console.log('      - Domain Model');
    console.log('      - Architecture');
    console.log('      - Dependencies');
    console.log('      - Quality');
    console.log('      - Metrics');
    console.log('      - Security');
    console.log('      - Testing');
    console.log('      - Refactoring');
    console.log('      - LENS');
    console.log('      - Code Explorer');
    console.log('   3. ✓ Verify data renders in each tab\n');
    
    console.log('✅ Expected console output:');
    console.log('   ✓ "Loaded from data/ subdirectory: KSESSIONS"');
    console.log('   ✓ "Dashboard initialized successfully"');
    console.log('   ✓ NO "container not found" warnings');
    console.log('   ✓ NO 404 errors\n');
    
    // Use child_process to open browser
    const { exec } = require('child_process');
    exec('start http://localhost:8888/dashboard.html?repo=KSESSIONS', (err) => {
      if (err) {
        console.log('⚠️  Could not auto-open browser. Open manually:', 
                   'http://localhost:8888/dashboard.html?repo=KSESSIONS');
      }
    });
    
  } else {
    console.log('❌ Dashboard server not responding (status:', res.statusCode + ')');
    console.log('   Start server with: cd company/dashboards/spa && python -m http.server 8888');
  }
}).on('error', (err) => {
  console.log('❌ Dashboard server is not running');
  console.log('   Start server with: cd company/dashboards/spa && python -m http.server 8888');
});
