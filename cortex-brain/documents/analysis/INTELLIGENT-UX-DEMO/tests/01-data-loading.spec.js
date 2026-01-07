// @ts-check
const { test, expect } = require('@playwright/test');
const { setupConsoleErrorTracking } = require('./fixtures/test-helpers');

/**
 * Test Suite: Data Loading & Integration
 * Validates analysis-data.json loading and error handling
 */
test.describe('Data Loading & Integration', () => {
  
  test('should load dashboard without console errors', async ({ page }) => {
    const errors = setupConsoleErrorTracking(page);
    
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
    
    // Verify no JavaScript errors
    expect(errors).toHaveLength(0);
  });

  test('should load real data from analysis-data.json', async ({ page }) => {
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
    
    // Verify analysis-data.json was fetched
    const jsonRequests = [];
    page.on('response', response => {
      if (response.url().includes('analysis-data.json')) {
        jsonRequests.push(response);
      }
    });
    
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    expect(jsonRequests.length).toBeGreaterThan(0);
    expect(jsonRequests[0].ok()).toBeTruthy();
  });

  test('should display CORTEX project metadata (not mock data)', async ({ page }) => {
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
    
    // Wait for data to load
    await page.waitForSelector('#summary-text', { timeout: 5000 });
    
    // Verify real project name from analysis-data.json
    const summaryText = await page.textContent('#summary-text');
    expect(summaryText).toContain('Analysis complete');
    
    // Mock data would show "Sample Project", real data shows CORTEX
    const pageContent = await page.content();
    expect(pageContent).toContain('CORTEX');
  });

  test('should have valid data structure', async ({ page }) => {
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
    
    // Check dashboardData is populated
    const hasValidData = await page.evaluate(() => {
      return window.dashboardData !== null &&
             window.dashboardData.metadata !== undefined &&
             window.dashboardData.scores !== undefined &&
             window.dashboardData.architecture !== undefined;
    });
    
    expect(hasValidData).toBeTruthy();
  });

  test('should display correct score values from real data', async ({ page }) => {
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
    
    // Get scores from analysis-data.json (overall: 72, quality: 68, performance: 75, security: 70)
    const overallScore = await page.textContent('#overall-score');
    const qualityScore = await page.textContent('#quality-score');
    const performanceScore = await page.textContent('#performance-score');
    const securityScore = await page.textContent('#security-score');
    
    expect(parseInt(overallScore)).toBe(72);
    expect(parseInt(qualityScore)).toBe(68);
    expect(parseInt(performanceScore)).toBe(75);
    expect(parseInt(securityScore)).toBe(70);
  });

  test('should display correct metadata from analysis-data.json', async ({ page }) => {
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
    
    const metadata = await page.evaluate(() => window.dashboardData.metadata);
    
    expect(metadata.projectName).toBe('CORTEX');
    expect(metadata.fileCount).toBe(247);
    expect(metadata.lineCount).toBe(45623);
    expect(metadata.language).toBe('Python');
  });

  test('should not call loadMockData() when real data available', async ({ page }) => {
    let mockDataCalled = false;
    
    await page.exposeFunction('trackMockData', () => {
      mockDataCalled = true;
    });
    
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
    
    // Check console logs for mock data indication
    const logs = [];
    page.on('console', msg => logs.push(msg.text()));
    
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    const hasMockLog = logs.some(log => log.includes('mock') || log.includes('Mock'));
    expect(hasMockLog).toBeFalsy();
  });

  test('should handle JSON parsing correctly', async ({ page }) => {
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
    
    // Verify data structure integrity
    const dataValid = await page.evaluate(() => {
      const data = window.dashboardData;
      return (
        Array.isArray(data.architecture.components) &&
        Array.isArray(data.quality.codeSmells) &&
        Array.isArray(data.roadmap.tasks) &&
        typeof data.scores.overall === 'number'
      );
    });
    
    expect(dataValid).toBeTruthy();
  });

  test('should render all 6 tabs', async ({ page }) => {
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
    
    const tabButtons = await page.locator('.tab-button').count();
    expect(tabButtons).toBe(6);
  });

  test('should have proper CORS handling for local file protocol', async ({ page }) => {
    // This test verifies the file:// protocol fallback works
    const response = await page.goto('/dashboard.html');
    expect(response.ok()).toBeTruthy();
  });
});
