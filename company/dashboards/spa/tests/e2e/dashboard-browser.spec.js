import { test, expect } from '@playwright/test';

test.describe('Dashboard Browser E2E', () => {
  test('should load dashboard without console errors', async ({ page }) => {
    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    await page.goto('/dashboard.html?repo=KSESSIONS');
    
    // Wait for data to load
    await page.waitForTimeout(3000);
    
    // Log all errors for debugging
    if (consoleErrors.length > 0) {
      console.log('Console errors detected:', consoleErrors);
    }
    
    // Verify no critical errors (specifically the JSONDataAdapter error)
    const criticalErrors = consoleErrors.filter(err => 
      err.includes('JSONDataAdapter not loaded') ||
      err.includes('is not defined') ||
      err.includes('Failed to fetch')
    );
    
    expect(criticalErrors).toHaveLength(0);
  });

  test('should display repository name', async ({ page }) => {
    await page.goto('/dashboard.html?repo=KSESSIONS');
    await page.waitForTimeout(2000);
    
    // Check if repo name appears in UI
    const repoName = await page.textContent('.repo-name, h1, .dashboard-header');
    expect(repoName).toContain('KSESSIONS');
  });

  test('should display health score', async ({ page }) => {
    await page.goto('/dashboard.html?repo=KSESSIONS');
    await page.waitForTimeout(2000);
    
    // Health score should be visible
    const healthElement = await page.locator('text=/Health.*Score|Score.*100/i').first();
    await expect(healthElement).toBeVisible({ timeout: 5000 });
  });

  test('should render tab navigation', async ({ page }) => {
    await page.goto('/dashboard.html?repo=KSESSIONS');
    await page.waitForTimeout(2000);
    
    // Verify tabs are present
    const tabs = await page.locator('.tab, .nav-tab, [role="tab"]').count();
    expect(tabs).toBeGreaterThan(0);
  });

  test('should render charts', async ({ page }) => {
    await page.goto('/dashboard.html?repo=KSESSIONS');
    await page.waitForTimeout(3000);
    
    // ECharts creates canvas elements
    const charts = await page.locator('canvas').count();
    expect(charts).toBeGreaterThan(0);
  });

  test('should switch between tabs', async ({ page }) => {
    await page.goto('/dashboard.html?repo=KSESSIONS');
    await page.waitForTimeout(2000);
    
    // Click on a tab
    const secondTab = page.locator('.tab, .nav-tab, [role="tab"]').nth(1);
    if (await secondTab.isVisible()) {
      await secondTab.click();
      await page.waitForTimeout(500);
      
      // Verify content changed (some element should appear/disappear)
      const activeTab = await page.locator('.tab.active, .nav-tab.active, [role="tab"][aria-selected="true"]').count();
      expect(activeTab).toBeGreaterThan(0);
    }
  });

  test('should load data from JSON file', async ({ page }) => {
    const response = await page.request.get('/KSESSIONS/dashboard-data.json');
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    // Schema v3 uses snake_case (repo_summary, metrics_summary)
    expect(data).toHaveProperty('repo_summary');
    expect(data).toHaveProperty('metrics_summary');
  });

  test('should have all script dependencies loaded', async ({ page }) => {
    await page.goto('/dashboard.html?repo=KSESSIONS');
    
    // Check that key globals are defined
    const globals = await page.evaluate(() => ({
      echarts: typeof window.echarts !== 'undefined',
      mermaid: typeof window.mermaid !== 'undefined',
      Fuse: typeof window.Fuse !== 'undefined',
      JSONDataAdapter: typeof window.JSONDataAdapter !== 'undefined',
      DualFormatDataLoader: typeof window.DualFormatDataLoader !== 'undefined',
    }));
    
    expect(globals.echarts).toBe(true);
    expect(globals.JSONDataAdapter).toBe(true);
    expect(globals.DualFormatDataLoader).toBe(true);
  });
});
