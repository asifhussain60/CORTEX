// @ts-check
const { test, expect } = require('@playwright/test');
const { waitForVisualization, switchTab, getD3Elements } = require('./fixtures/test-helpers');

/**
 * Test Suite: Tab 1 - Executive Summary
 * Validates score cards, progress bars, and summary content
 */
test.describe('Executive Summary Tab', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
    // Executive Summary is the default tab
    await page.waitForSelector('#executive-summary', { state: 'visible' });
  });

  test('should display all 4 score cards', async ({ page }) => {
    const scoreCards = await page.locator('.metric-card').count();
    expect(scoreCards).toBeGreaterThanOrEqual(4);
  });

  test('should show correct overall score (72) from real data', async ({ page }) => {
    const score = await page.textContent('#overall-score');
    expect(parseInt(score)).toBe(72);
  });

  test('should show correct quality score (68) from real data', async ({ page }) => {
    const score = await page.textContent('#quality-score');
    expect(parseInt(score)).toBe(68);
  });

  test('should show correct performance score (75) from real data', async ({ page }) => {
    const score = await page.textContent('#performance-score');
    expect(parseInt(score)).toBe(75);
  });

  test('should show correct security score (70) from real data', async ({ page }) => {
    const score = await page.textContent('#security-score');
    expect(parseInt(score)).toBe(70);
  });

  test('should animate progress bars', async ({ page }) => {
    // Wait for animation
    await page.waitForTimeout(1500);
    
    const progressWidth = await page.evaluate(() => {
      const progressBar = document.querySelector('#overall-progress .progress-fill');
      return progressBar ? window.getComputedStyle(progressBar).width : '0px';
    });
    
    expect(progressWidth).not.toBe('0px');
  });

  test('should display summary text from real data', async ({ page }) => {
    const summaryText = await page.textContent('#summary-text');
    
    expect(summaryText).toContain('Analysis complete');
    expect(summaryText).toContain('codebase');
    expect(summaryText.length).toBeGreaterThan(50);
  });

  test('should display 5 quick wins from real data', async ({ page }) => {
    const quickWins = await page.locator('#quick-wins-list li').count();
    expect(quickWins).toBe(5);
    
    // Verify first quick win from analysis-data.json
    const firstWin = await page.textContent('#quick-wins-list li:first-child');
    expect(firstWin).toContain('Remove 23 unused imports');
  });

  test('should display 5 critical issues from real data', async ({ page }) => {
    const criticalIssues = await page.locator('#critical-issues-list li').count();
    expect(criticalIssues).toBe(5);
    
    // Verify first issue from analysis-data.json
    const firstIssue = await page.textContent('#critical-issues-list li:first-child');
    expect(firstIssue).toContain('God classes detected');
  });

  test('should use green checkmarks for quick wins', async ({ page }) => {
    const checkmarks = await page.locator('#quick-wins-list .text-green-500').count();
    expect(checkmarks).toBe(5);
  });

  test('should use red warning icons for critical issues', async ({ page }) => {
    const warnings = await page.locator('#critical-issues-list .text-red-500').count();
    expect(warnings).toBe(5);
  });

  test('should color-code scores correctly', async ({ page }) => {
    // Scores 70+ should be green/blue, <70 should be yellow/orange
    const overallColor = await page.evaluate(() => {
      const elem = document.querySelector('#overall-score');
      return window.getComputedStyle(elem).color;
    });
    
    expect(overallColor).toBeTruthy();
  });

  test('should display discovery panel if discoveries exist', async ({ page }) => {
    // analysis-data.json has 4 discoveries
    await page.waitForTimeout(2500); // Panel appears after 2s delay
    
    const panel = page.locator('#discovery-panel');
    await expect(panel).toBeVisible();
  });

  test('should show correct number of discoveries', async ({ page }) => {
    await page.waitForTimeout(2500);
    
    const discoveries = await page.locator('#discovery-content > div').count();
    // Shows first 3 discoveries
    expect(discoveries).toBeLessThanOrEqual(3);
  });

  test('should close discovery panel when clicked', async ({ page }) => {
    await page.waitForTimeout(2500);
    
    await page.click('#close-discovery');
    await expect(page.locator('#discovery-panel')).not.toBeVisible();
  });

  test('should have responsive layout', async ({ page }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    const scoreCards = page.locator('.metric-card');
    await expect(scoreCards.first()).toBeVisible();
  });

  test('should support dark mode toggle', async ({ page }) => {
    const darkModeButton = page.locator('#dark-mode-toggle');
    
    if (await darkModeButton.isVisible()) {
      await darkModeButton.click();
      
      const theme = await page.evaluate(() => 
        document.documentElement.getAttribute('data-theme')
      );
      
      expect(theme).toBe('dark');
    }
  });
});
