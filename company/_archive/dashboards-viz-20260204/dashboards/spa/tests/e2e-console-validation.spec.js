/**
 * Enhanced E2E Tests with Console Monitoring
 * 
 * Demonstrates usage of ConsoleMonitor to detect:
 * - Missing DOM containers
 * - Data loading failures
 * - JavaScript errors
 */

import { test, expect } from '@playwright/test';
import { ConsoleMonitor, withConsoleMonitoring } from './ConsoleMonitor.js';

test.describe('Dashboard E2E with Console Validation', () => {
  
  test('dashboard loads without console errors', async ({ page }) => {
    const monitor = new ConsoleMonitor(page);
    await monitor.start();
    
    await page.goto('/dashboard.html?repo=KSESSIONS');
    
    // Wait for dashboard initialization
    await page.waitForFunction(() => {
      return window.cortexDashboard && window.cortexDashboard.initialized;
    }, { timeout: 10000 });
    
    // Assert no CORTEX-specific errors
    monitor.assertNoErrors('Dashboard initialization should not produce errors');
    
    // Verify critical success messages were logged
    monitor.assertMessageLogged(/Dashboard initialized successfully/, 'log');
    monitor.assertMessageLogged(/Data loaded successfully/, 'log');
    
    monitor.printReport();
  });
  
  test('all containers render without warnings', async ({ page }) => {
    await withConsoleMonitoring(page, async (monitor) => {
      await page.goto('/dashboard.html?repo=KSESSIONS');
      
      // Activate Security tab (triggers deferred rendering)
      await page.click('[aria-controls="security-panel"]');
      await page.waitForTimeout(500); // Wait for deferred render flush
      
      // Should not have "container not found" warnings
      monitor.assertNoWarnings([/container.*not found/i, /missing.*container/i]);
      
      // Verify containers are visible
      await expect(page.locator('#vulnerabilities-list')).toBeVisible();
      await expect(page.locator('#vuln-types-list')).toBeVisible();
    }, { printReport: true });
  });
  
  test('data loading from data/ subdirectory succeeds', async ({ page }) => {
    const monitor = new ConsoleMonitor(page, {
      capturePatterns: [/\[SPA\]/, /data/i]
    });
    await monitor.start();
    
    await page.goto('/dashboard.html?repo=KSESSIONS');
    
    // Wait for data load
    await page.waitForFunction(() => {
      return document.querySelector('[data-bind="repo.display_name"]')?.textContent !== 'Repository';
    });
    
    // Assert correct data path was used
    monitor.assertMessageLogged(/Loaded from data\/.*subdirectory/, 'log');
    
    // Verify no 404 errors
    const errors = monitor.getErrors();
    const has404 = errors.some(e => e.text.includes('404'));
    expect(has404, 'Should not have 404 errors').toBe(false);
    
    monitor.stop();
  });
  
  test('tab switching does not cause errors', async ({ page }) => {
    await withConsoleMonitoring(page, async (monitor) => {
      await page.goto('/dashboard.html?repo=KSESSIONS');
      
      // Switch through all tabs
      const tabs = await page.locator('[role="tab"]').all();
      
      for (const tab of tabs) {
        await tab.click();
        await page.waitForTimeout(300); // Wait for tab content render
      }
      
      // No errors should occur during tab navigation
      monitor.assertNoErrors('Tab switching should not produce errors');
      
    }, { printReport: true });
  });
  
  test('chart rendering without console errors', async ({ page }) => {
    const monitor = new ConsoleMonitor(page, {
      capturePatterns: [/chart/i, /echarts/i]
    });
    await monitor.start();
    
    await page.goto('/dashboard.html?repo=KSESSIONS');
    
    // Wait for charts to initialize
    await page.waitForSelector('.echarts-chart', { timeout: 5000 });
    
    // Verify no chart errors
    const errors = monitor.getErrors();
    const chartErrors = errors.filter(e => /chart|echarts/i.test(e.text));
    expect(chartErrors.length, 'No chart rendering errors').toBe(0);
    
    monitor.stop();
  });
  
  test('captures only CORTEX errors, ignores third-party', async ({ page }) => {
    const monitor = new ConsoleMonitor(page);
    await monitor.start();
    
    await page.goto('/dashboard.html?repo=KSESSIONS');
    await page.waitForLoadState('networkidle');
    
    const summary = monitor.getSummary();
    
    // Should have filtered out many messages
    expect(summary.ignored).toBeGreaterThan(0);
    
    // Raw messages should include Grammarly/WAX
    const hasNoise = monitor.rawMessages.some(m => 
      /grammarly|wax|contentisola/i.test(m.text)
    );
    expect(hasNoise, 'Should capture raw third-party messages').toBe(true);
    
    // Filtered messages should NOT include noise
    const cortexErrors = monitor.getErrors();
    const hasNoiseInFiltered = cortexErrors.some(e => 
      /grammarly|wax/i.test(e.text)
    );
    expect(hasNoiseInFiltered, 'Should filter out third-party from errors').toBe(false);
    
    monitor.printReport();
  });
});
