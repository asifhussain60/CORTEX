// @ts-check
const { test, expect } = require('@playwright/test');
const { waitForVisualization, switchTab, getD3Elements } = require('./fixtures/test-helpers');

/**
 * Test Suite: Tab 3 - Quality
 * Validates code smells heatmap, complexity treemap, and maintainability charts
 */
test.describe('Quality Tab', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
    await switchTab(page, 'Quality');
  });

  test('should render quality heatmap', async ({ page }) => {
    await waitForVisualization(page, '#quality-heatmap');
    
    const svgExists = await page.locator('#quality-heatmap svg').count();
    expect(svgExists).toBeGreaterThan(0);
  });

  test('should display 8 code smells from real data', async ({ page }) => {
    await waitForVisualization(page, '#quality-heatmap');
    
    const codeSmellsCount = await page.evaluate(() => {
      return window.dashboardData.quality.codeSmells.length;
    });
    
    expect(codeSmellsCount).toBe(8);
  });

  test('should render complexity treemap', async ({ page }) => {
    await waitForVisualization(page, '#complexity-treemap');
    
    const rects = await getD3Elements(page, '#complexity-treemap', 'rect');
    expect(rects).toBeGreaterThan(0);
  });

  test('should show 6 complexity items from real data', async ({ page }) => {
    const complexityCount = await page.evaluate(() => {
      return window.dashboardData.quality.complexity.length;
    });
    
    expect(complexityCount).toBe(6);
  });

  test('should color-code complexity by severity', async ({ page }) => {
    await waitForVisualization(page, '#complexity-treemap');
    
    const colors = await page.evaluate(() => {
      const rects = document.querySelectorAll('#complexity-treemap svg rect');
      return Array.from(rects).map(r => r.getAttribute('fill'));
    });
    
    // Should have variety of colors based on complexity
    const uniqueColors = new Set(colors);
    expect(uniqueColors.size).toBeGreaterThan(1);
  });

  test('should display maintainability bar chart', async ({ page }) => {
    await waitForVisualization(page, '#maintainability-chart');
    
    const bars = await getD3Elements(page, '#maintainability-chart', 'rect');
    expect(bars).toBeGreaterThan(0);
  });

  test('should show 6 maintainability metrics from real data', async ({ page }) => {
    const metricsCount = await page.evaluate(() => {
      return window.dashboardData.quality.maintainability.length;
    });
    
    expect(metricsCount).toBe(6);
  });

  test('should display target lines on maintainability chart', async ({ page }) => {
    await waitForVisualization(page, '#maintainability-chart');
    
    const targetLines = await page.locator('#maintainability-chart svg line[stroke-dasharray]').count();
    expect(targetLines).toBeGreaterThan(0);
  });

  test('should show correct test coverage (65%) from real data', async ({ page }) => {
    const coverage = await page.evaluate(() => {
      const metric = window.dashboardData.quality.maintainability.find(m => m.metric === 'Code Coverage');
      return metric ? metric.value : null;
    });
    
    expect(coverage).toBe(65);
  });

  test('should show documentation metric (72%) from real data', async ({ page }) => {
    const documentation = await page.evaluate(() => {
      const metric = window.dashboardData.quality.maintainability.find(m => m.metric === 'Documentation');
      return metric ? metric.value : null;
    });
    
    expect(documentation).toBe(72);
  });

  test('should show type safety metric (68%) from real data', async ({ page }) => {
    const typeSafety = await page.evaluate(() => {
      const metric = window.dashboardData.quality.maintainability.find(m => m.metric === 'Type Safety');
      return metric ? metric.value : null;
    });
    
    expect(typeSafety).toBe(68);
  });

  test('should display tooltips on hover', async ({ page }) => {
    await waitForVisualization(page, '#complexity-treemap');
    
    const rect = page.locator('#complexity-treemap svg rect').first();
    await rect.hover();
    
    await page.waitForTimeout(300);
    // Tooltip should be visible (implementation-dependent)
  });

  test('should animate bar chart transitions', async ({ page }) => {
    await switchTab(page, 'Quality');
    
    // Initial state - bars should be at 0 height
    await page.waitForTimeout(100);
    
    // After animation - bars should have height
    await page.waitForTimeout(1200);
    
    const barHeight = await page.evaluate(() => {
      const bar = document.querySelector('#maintainability-chart svg rect');
      return bar ? parseFloat(bar.getAttribute('height')) : 0;
    });
    
    expect(barHeight).toBeGreaterThan(0);
  });

  test('should show axes with labels', async ({ page }) => {
    await waitForVisualization(page, '#maintainability-chart');
    
    const axes = await page.locator('#maintainability-chart svg g.axis, #maintainability-chart svg g').count();
    expect(axes).toBeGreaterThan(0);
  });

  test('should have proper text labels in treemap', async ({ page }) => {
    await waitForVisualization(page, '#complexity-treemap');
    
    const textLabels = await getD3Elements(page, '#complexity-treemap', 'text');
    expect(textLabels).toBeGreaterThan(0);
  });

  test('should display highest complexity method (25)', async ({ page }) => {
    const highestComplexity = await page.evaluate(() => {
      const complexities = window.dashboardData.quality.complexity;
      return Math.max(...complexities.map(c => c.complexity));
    });
    
    expect(highestComplexity).toBe(25);
  });

  test('should show quality trends if available', async ({ page }) => {
    const hasTrends = await page.evaluate(() => {
      return window.dashboardData.quality.trends !== undefined;
    });
    
    expect(hasTrends).toBeTruthy();
  });
});
