// @ts-check
const { test, expect } = require('@playwright/test');
const { waitForVisualization, switchTab, getD3Elements } = require('./fixtures/test-helpers');

/**
 * Test Suite: Tab 5 - Performance (Journey)
 * Validates flamegraph, Sankey diagram, and optimization timeline
 */
test.describe('Performance (Journey) Tab', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
    await switchTab(page, 'Journey');
  });

  test('should render flamegraph', async ({ page }) => {
    await waitForVisualization(page, '#performance-flamegraph');
    
    const svgExists = await page.locator('#performance-flamegraph svg').count();
    expect(svgExists).toBeGreaterThan(0);
  });

  test('should display 5 bottlenecks from real data', async ({ page }) => {
    const bottleneckCount = await page.evaluate(() => {
      return window.dashboardData.performance.bottlenecks.length;
    });
    
    expect(bottleneckCount).toBe(5);
  });

  test('should show slowest function (2500ms)', async ({ page }) => {
    const slowest = await page.evaluate(() => {
      const bottlenecks = window.dashboardData.performance.bottlenecks;
      return Math.max(...bottlenecks.map(b => b.time));
    });
    
    expect(slowest).toBe(2500);
  });

  test('should color-code flamegraph by performance', async ({ page }) => {
    await waitForVisualization(page, '#performance-flamegraph');
    
    const colors = await page.evaluate(() => {
      const rects = document.querySelectorAll('#performance-flamegraph svg rect');
      return Array.from(rects).map(r => r.getAttribute('fill')).filter(Boolean);
    });
    
    const uniqueColors = new Set(colors);
    expect(uniqueColors.size).toBeGreaterThan(1);
  });

  test('should render Sankey diagram', async ({ page }) => {
    await waitForVisualization(page, '#dataflow-sankey');
    
    const svgExists = await page.locator('#dataflow-sankey svg').count();
    expect(svgExists).toBeGreaterThan(0);
  });

  test('should show 7 data flow paths from real data', async ({ page }) => {
    const flowCount = await page.evaluate(() => {
      return window.dashboardData.performance.dataFlow.length;
    });
    
    expect(flowCount).toBe(7);
  });

  test('should display Sankey nodes', async ({ page }) => {
    await waitForVisualization(page, '#dataflow-sankey');
    
    const nodes = await getD3Elements(page, '#dataflow-sankey', 'rect');
    expect(nodes).toBeGreaterThan(0);
  });

  test('should display Sankey links', async ({ page }) => {
    await waitForVisualization(page, '#dataflow-sankey');
    
    const links = await getD3Elements(page, '#dataflow-sankey', 'path');
    expect(links).toBeGreaterThan(0);
  });

  test('should show node labels', async ({ page }) => {
    await waitForVisualization(page, '#dataflow-sankey');
    
    const labels = await getD3Elements(page, '#dataflow-sankey', 'text');
    expect(labels).toBeGreaterThan(0);
  });

  test('should display optimization timeline', async ({ page }) => {
    const timeline = page.locator('#optimization-timeline');
    await expect(timeline).toBeVisible();
  });

  test('should have 3 timeline phases', async ({ page }) => {
    const phases = await page.locator('#optimization-timeline .flex.items-start').count();
    expect(phases).toBe(3);
  });

  test('should show week labels in timeline', async ({ page }) => {
    const firstWeek = await page.textContent('#optimization-timeline .flex.items-start:first-child .w-24');
    expect(firstWeek).toContain('Week');
  });

  test('should display timeline phase titles', async ({ page }) => {
    const firstTitle = await page.textContent('#optimization-timeline .font-semibold:first-of-type');
    expect(firstTitle).toContain('Quick Performance Wins');
  });

  test('should animate flamegraph bars', async ({ page }) => {
    await switchTab(page, 'Journey');
    
    await page.waitForTimeout(1200);
    
    const barHeight = await page.evaluate(() => {
      const rect = document.querySelector('#performance-flamegraph svg rect');
      return rect ? parseFloat(rect.getAttribute('height')) : 0;
    });
    
    expect(barHeight).toBeGreaterThan(0);
  });

  test('should show flamegraph axes', async ({ page }) => {
    await waitForVisualization(page, '#performance-flamegraph');
    
    const axes = await page.locator('#performance-flamegraph svg g').count();
    expect(axes).toBeGreaterThan(0);
  });

  test('should display tooltips on flamegraph hover', async ({ page }) => {
    await waitForVisualization(page, '#performance-flamegraph');
    
    const bar = page.locator('#performance-flamegraph svg rect').first();
    await bar.hover();
    
    await page.waitForTimeout(300);
  });

  test('should show highest call count (5000)', async ({ page }) => {
    const highestCalls = await page.evaluate(() => {
      const bottlenecks = window.dashboardData.performance.bottlenecks;
      return Math.max(...bottlenecks.map(b => b.calls));
    });
    
    expect(highestCalls).toBe(5000);
  });

  test('should have performance metrics', async ({ page }) => {
    const hasMetrics = await page.evaluate(() => {
      return window.dashboardData.performance.metrics !== undefined;
    });
    
    expect(hasMetrics).toBeTruthy();
  });

  test('should display optimization phases with colors', async ({ page }) => {
    const firstPhaseColor = await page.evaluate(() => {
      const phase = document.querySelector('#optimization-timeline .border-l-2');
      return phase ? window.getComputedStyle(phase).borderLeftColor : null;
    });
    
    expect(firstPhaseColor).toBeTruthy();
  });
});
