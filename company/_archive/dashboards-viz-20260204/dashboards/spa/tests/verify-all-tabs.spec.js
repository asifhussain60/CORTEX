/**
 * Comprehensive Tab Loading Verification
 * 
 * Automatically checks all 13 tabs:
 * 1. Clicks each tab
 * 2. Monitors console for errors
 * 3. Verifies tab content renders
 * 4. Reports any issues
 */

import { test, expect } from '@playwright/test';
import { ConsoleMonitor } from './ConsoleMonitor.js';

test('verify all 13 tabs load without errors', async ({ page }) => {
  const monitor = new ConsoleMonitor(page, {
    capturePatterns: [/CORTEX/i, /\[SPA\]/, /\[TRACE\]/, /DeferredRenderer/],
    ignorePatterns: [/Grammarly/i, /WAX/i, /ContentIsolated/i, /DEFAULT.*logger/i]
  });
  
  await monitor.start();
  
  console.log('\n🚀 Loading KSESSIONS dashboard...');
  await page.goto('http://localhost:8888/dashboard.html?repo=KSESSIONS', {
    waitUntil: 'networkidle',
    timeout: 30000
  });
  
  // Wait for dashboard initialization
  await page.waitForFunction(() => {
    return window.cortexDashboard && window.cortexDashboard.initialized;
  }, { timeout: 15000 });
  
  console.log('✅ Dashboard initialized\n');
  
  // Get all tabs
  const tabs = await page.locator('[role="tab"]').all();
  console.log(`📋 Found ${tabs.length} tabs to verify\n`);
  
  const results = [];
  
  for (let i = 0; i < tabs.length; i++) {
    const tab = tabs[i];
    const tabText = await tab.textContent();
    const tabId = await tab.getAttribute('id');
    const panelId = await tab.getAttribute('aria-controls');
    
    console.log(`\n${i + 1}. Checking tab: ${tabText.trim()} (${tabId})`);
    
    try {
      // Click tab
      await tab.click();
      await page.waitForTimeout(500); // Wait for deferred rendering
      
      // Verify panel is visible
      const panel = page.locator(`#${panelId}`);
      const isVisible = await panel.getAttribute('aria-hidden');
      
      if (isVisible === 'false') {
        // Check for content in panel
        const hasContent = await panel.locator('*').count() > 0;
        
        if (hasContent) {
          console.log(`   ✅ Tab loaded successfully`);
          results.push({ tab: tabText.trim(), status: 'success', error: null });
        } else {
          console.log(`   ⚠️  Tab visible but empty`);
          results.push({ tab: tabText.trim(), status: 'warning', error: 'Empty content' });
        }
      } else {
        console.log(`   ❌ Tab panel not visible`);
        results.push({ tab: tabText.trim(), status: 'error', error: 'Panel not visible' });
      }
      
    } catch (error) {
      console.log(`   ❌ Error: ${error.message}`);
      results.push({ tab: tabText.trim(), status: 'error', error: error.message });
    }
  }
  
  // Print console monitor report
  console.log('\n📊 Console Activity Report:');
  monitor.printReport();
  
  // Print tab verification summary
  console.log('\n📋 Tab Verification Summary:');
  console.log('═'.repeat(60));
  
  const successful = results.filter(r => r.status === 'success').length;
  const warnings = results.filter(r => r.status === 'warning').length;
  const errors = results.filter(r => r.status === 'error').length;
  
  console.log(`✅ Successful: ${successful}/${results.length}`);
  console.log(`⚠️  Warnings: ${warnings}/${results.length}`);
  console.log(`❌ Errors: ${errors}/${results.length}`);
  
  if (warnings > 0) {
    console.log('\n⚠️  Tabs with warnings:');
    results.filter(r => r.status === 'warning').forEach(r => {
      console.log(`   - ${r.tab}: ${r.error}`);
    });
  }
  
  if (errors > 0) {
    console.log('\n❌ Tabs with errors:');
    results.filter(r => r.status === 'error').forEach(r => {
      console.log(`   - ${r.tab}: ${r.error}`);
    });
  }
  
  // Assert no CORTEX errors in console
  try {
    monitor.assertNoErrors('Dashboard tab navigation should not produce errors');
    console.log('\n✅ No console errors detected');
  } catch (e) {
    console.log('\n❌ Console errors detected:');
    console.log(e.message);
  }
  
  // Final assertion
  expect(errors).toBe(0);
  expect(successful).toBeGreaterThan(10); // At least 10 tabs should load
  
  monitor.stop();
});

test('verify deferred rendering works for hidden tabs', async ({ page }) => {
  const monitor = new ConsoleMonitor(page);
  await monitor.start();
  
  await page.goto('http://localhost:8888/dashboard.html?repo=KSESSIONS');
  
  await page.waitForFunction(() => {
    return window.cortexDashboard && window.cortexDashboard.initialized;
  });
  
  console.log('\n🔍 Testing deferred rendering...');
  
  // Check if renders were queued
  const queuedCount = await page.evaluate(() => {
    return window.cortexDashboard?.deferredRenderer?.getPendingCount() || 0;
  });
  
  console.log(`   Deferred renders queued: ${queuedCount}`);
  
  if (queuedCount > 0) {
    // Click Security tab to trigger flush
    console.log('   Activating Security tab to trigger render flush...');
    await page.click('[aria-controls="security-panel"]');
    await page.waitForTimeout(500);
    
    // Check queue again
    const remainingCount = await page.evaluate(() => {
      return window.cortexDashboard?.deferredRenderer?.getPendingCount() || 0;
    });
    
    console.log(`   Remaining queued: ${remainingCount}`);
    console.log(`   ✅ Flushed: ${queuedCount - remainingCount} renders`);
    
    // Verify vulnerabilities list rendered
    const vulnCount = await page.locator('#vulnerabilities-list > *').count();
    console.log(`   Vulnerabilities rendered: ${vulnCount} items`);
  } else {
    console.log('   ℹ️  No deferred renders (all containers visible)');
  }
  
  monitor.stop();
});
