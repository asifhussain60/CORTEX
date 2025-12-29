// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Test Suite: Visual Regression Tests
 * Snapshot tests for all visualizations to detect rendering issues
 */
test.describe('Visual Regression Tests', () => {
  
  test('should match Executive Summary snapshot', async ({ page }) => {
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000); // Wait for animations
    
    const summary = page.locator('#executive-summary');
    await expect(summary).toHaveScreenshot('executive-summary.png', {
      maxDiffPixels: 100
    });
  });

  test('should match Architecture Graph snapshot', async ({ page }) => {
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
    await page.click('button:has-text("Architecture")');
    await page.waitForTimeout(2000);
    
    const graph = page.locator('#architecture-graph');
    await expect(graph).toHaveScreenshot('architecture-graph.png', {
      maxDiffPixels: 200 // Force-directed graphs have slight variations
    });
  });

  test('should match Quality Heatmap snapshot', async ({ page }) => {
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
    await page.click('button:has-text("Quality")');
    await page.waitForTimeout(2000);
    
    const heatmap = page.locator('#quality-heatmap');
    await expect(heatmap).toHaveScreenshot('quality-heatmap.png', {
      maxDiffPixels: 100
    });
  });

  test('should match Complexity Treemap snapshot', async ({ page }) => {
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
    await page.click('button:has-text("Quality")');
    await page.waitForTimeout(2000);
    
    const treemap = page.locator('#complexity-treemap');
    await expect(treemap).toHaveScreenshot('complexity-treemap.png', {
      maxDiffPixels: 100
    });
  });

  test('should match Roadmap Gantt Chart snapshot', async ({ page }) => {
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
    await page.click('button:has-text("Roadmap")');
    await page.waitForTimeout(2000);
    
    const gantt = page.locator('#roadmap-gantt');
    await expect(gantt).toHaveScreenshot('roadmap-gantt.png', {
      maxDiffPixels: 100
    });
  });

  test('should match Priority Matrix snapshot', async ({ page }) => {
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
    await page.click('button:has-text("Roadmap")');
    await page.waitForTimeout(2000);
    
    const matrix = page.locator('#priority-matrix');
    await expect(matrix).toHaveScreenshot('priority-matrix.png', {
      maxDiffPixels: 100
    });
  });

  test('should match Performance Flamegraph snapshot', async ({ page }) => {
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
    await page.click('button:has-text("Journey")');
    await page.waitForTimeout(2000);
    
    const flamegraph = page.locator('#performance-flamegraph');
    await expect(flamegraph).toHaveScreenshot('performance-flamegraph.png', {
      maxDiffPixels: 100
    });
  });

  test('should match Sankey Diagram snapshot', async ({ page }) => {
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
    await page.click('button:has-text("Journey")');
    await page.waitForTimeout(2000);
    
    const sankey = page.locator('#dataflow-sankey');
    await expect(sankey).toHaveScreenshot('sankey-diagram.png', {
      maxDiffPixels: 100
    });
  });

  test('should match Security Severity Chart snapshot', async ({ page }) => {
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
    await page.click('button:has-text("Security")');
    await page.waitForTimeout(2000);
    
    const chart = page.locator('#security-severity-chart');
    await expect(chart).toHaveScreenshot('security-severity.png', {
      maxDiffPixels: 100
    });
  });

  test('should match OWASP Radar Chart snapshot', async ({ page }) => {
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
    await page.click('button:has-text("Security")');
    await page.waitForTimeout(2000);
    
    const radar = page.locator('#owasp-chart');
    await expect(radar).toHaveScreenshot('owasp-radar.png', {
      maxDiffPixels: 100
    });
  });

  test('should match Risk Gauge snapshot', async ({ page }) => {
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
    await page.click('button:has-text("Security")');
    await page.waitForTimeout(2000);
    
    const gauge = page.locator('#risk-gauge');
    await expect(gauge).toHaveScreenshot('risk-gauge.png', {
      maxDiffPixels: 100
    });
  });

  test('should match full dashboard snapshot', async ({ page }) => {
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    await expect(page).toHaveScreenshot('full-dashboard.png', {
      fullPage: true,
      maxDiffPixels: 500
    });
  });

  test('should match dark mode snapshot', async ({ page }) => {
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
    
    const darkModeButton = page.locator('#dark-mode-toggle');
    if (await darkModeButton.isVisible()) {
      await darkModeButton.click();
      await page.waitForTimeout(500);
      
      await expect(page).toHaveScreenshot('dashboard-dark-mode.png', {
        fullPage: true,
        maxDiffPixels: 500
      });
    }
  });

  test('should match mobile view snapshot', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    await expect(page).toHaveScreenshot('dashboard-mobile.png', {
      fullPage: true,
      maxDiffPixels: 500
    });
  });
});
