/**
 * Tab Verification Script
 * Runs Playwright programmatically to check all tabs and console logs
 */

import { chromium } from 'playwright';

async function verifyAllTabs() {
  console.log('🚀 Starting dashboard verification...\n');
  
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  // Collect console messages
  const consoleMessages = {
    log: [],
    error: [],
    warning: [],
    info: []
  };
  
  const cortexMessages = [];
  
  page.on('console', msg => {
    const type = msg.type();
    const text = msg.text();
    
    // Store all messages
    consoleMessages[type]?.push(text);
    
    // Filter CORTEX-specific
    if (text.includes('CORTEX') || text.includes('[SPA]') || text.includes('[TRACE]') || text.includes('DeferredRenderer')) {
      if (!text.includes('Grammarly') && !text.includes('WAX')) {
        cortexMessages.push({ type, text });
        console.log(`[${type.toUpperCase()}] ${text}`);
      }
    }
  });
  
  page.on('pageerror', error => {
    console.log(`❌ [PAGE ERROR] ${error.message}`);
    consoleMessages.error.push(error.message);
  });
  
  try {
    // Navigate to dashboard
    console.log('📡 Loading http://localhost:8888/dashboard.html?repo=KSESSIONS\n');
    await page.goto('http://localhost:8888/dashboard.html?repo=KSESSIONS', {
      waitUntil: 'networkidle',
      timeout: 30000
    });
    
    // Wait for initialization
    await page.waitForFunction(() => {
      return window.cortexDashboard && window.cortexDashboard.initialized;
    }, { timeout: 15000 });
    
    console.log('\n✅ Dashboard initialized\n');
    console.log('═'.repeat(60));
    console.log('Tab Verification');
    console.log('═'.repeat(60));
    
    // Get all tabs
    const tabs = await page.locator('[role="tab"]').all();
    console.log(`\nFound ${tabs.length} tabs\n`);
    
    const results = [];
    
    for (let i = 0; i < tabs.length; i++) {
      const tab = tabs[i];
      const tabText = (await tab.textContent()).trim().split('\n')[0]; // Get first line only
      const panelId = await tab.getAttribute('aria-controls');
      
      console.log(`${i + 1}. ${tabText.padEnd(20)} `, { newline: false });
      
      try {
        await tab.click();
        await page.waitForTimeout(500);
        
        const panel = page.locator(`#${panelId}`);
        const isHidden = await panel.getAttribute('aria-hidden');
        const childCount = await panel.locator('> *').count();
        
        if (isHidden === 'false' && childCount > 0) {
          console.log(`✅ Success (${childCount} elements)`);
          results.push({ tab: tabText, status: 'success', elements: childCount });
        } else if (isHidden === 'false') {
          console.log(`⚠️  Empty`);
          results.push({ tab: tabText, status: 'warning', elements: 0 });
        } else {
          console.log(`❌ Hidden`);
          results.push({ tab: tabText, status: 'error', elements: 0 });
        }
      } catch (error) {
        console.log(`❌ Error: ${error.message}`);
        results.push({ tab: tabText, status: 'error', error: error.message });
      }
    }
    
    // Summary
    console.log('\n' + '═'.repeat(60));
    console.log('Summary');
    console.log('═'.repeat(60));
    
    const successful = results.filter(r => r.status === 'success').length;
    const warnings = results.filter(r => r.status === 'warning').length;
    const errors = results.filter(r => r.status === 'error').length;
    
    console.log(`\n✅ Successful: ${successful}/${results.length}`);
    console.log(`⚠️  Warnings: ${warnings}/${results.length}`);
    console.log(`❌ Errors: ${errors}/${results.length}`);
    
    // Console errors
    console.log('\n' + '═'.repeat(60));
    console.log('Console Activity');
    console.log('═'.repeat(60));
    
    const cortexErrors = cortexMessages.filter(m => m.type === 'error');
    const cortexWarnings = cortexMessages.filter(m => m.type === 'warning');
    
    console.log(`\n📊 CORTEX Messages:`);
    console.log(`   Total: ${cortexMessages.length}`);
    console.log(`   Errors: ${cortexErrors.length} 🔴`);
    console.log(`   Warnings: ${cortexWarnings.length} 🟡`);
    
    if (cortexErrors.length > 0) {
      console.log('\n🔴 Console Errors:');
      cortexErrors.forEach(e => console.log(`   - ${e.text}`));
    }
    
    if (cortexWarnings.length > 0) {
      console.log('\n🟡 Console Warnings:');
      cortexWarnings.slice(0, 5).forEach(w => console.log(`   - ${w.text}`));
      if (cortexWarnings.length > 5) {
        console.log(`   ... and ${cortexWarnings.length - 5} more`);
      }
    }
    
    console.log('\n✅ Verification complete!\n');
    
    // Keep browser open for manual inspection
    console.log('Browser will remain open for 30 seconds for manual inspection...');
    console.log('Press Ctrl+C to close immediately.\n');
    await page.waitForTimeout(30000);
    
  } catch (error) {
    console.error('\n❌ Verification failed:', error.message);
  } finally {
    await browser.close();
  }
}

verifyAllTabs().catch(console.error);
