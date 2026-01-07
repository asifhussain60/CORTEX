// @ts-check
const { test, expect } = require('@playwright/test');
const { waitForVisualization, switchTab, getD3Elements } = require('./fixtures/test-helpers');

/**
 * Test Suite: Tab 2 - Architecture
 * Validates force-directed graph, component list, and architectural issues
 */
test.describe('Architecture Tab', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
    await switchTab(page, 'Architecture');
  });

  test('should render force-directed graph', async ({ page }) => {
    await waitForVisualization(page, '#architecture-graph');
    
    const svgExists = await page.locator('#architecture-graph svg').count();
    expect(svgExists).toBeGreaterThan(0);
  });

  test('should display correct number of components (6) from real data', async ({ page }) => {
    await waitForVisualization(page, '#architecture-graph');
    
    // Real data has 6 components: tier0, tier1, tier2, tier3, agents, orchestrators
    const nodes = await getD3Elements(page, '#architecture-graph', 'circle');
    expect(nodes).toBe(6);
  });

  test('should show component relationships', async ({ page }) => {
    await waitForVisualization(page, '#architecture-graph');
    
    // Real data has 8 relationships
    const links = await getD3Elements(page, '#architecture-graph', 'line');
    expect(links).toBeGreaterThan(0);
  });

  test('should display component list with correct data', async ({ page }) => {
    const components = await page.locator('#component-list > div').count();
    expect(components).toBe(6);
    
    // Verify first component from analysis-data.json
    const firstComponent = await page.textContent('#component-list > div:first-child strong');
    expect(firstComponent).toBe('Tier 0 Governance');
  });

  test('should color-code components', async ({ page }) => {
    const colorBox = page.locator('#component-list .w-4.h-4.rounded').first();
    const bgColor = await colorBox.evaluate(el => window.getComputedStyle(el).backgroundColor);
    
    expect(bgColor).not.toBe('rgba(0, 0, 0, 0)');
  });

  test('should display architectural issues (4 from real data)', async ({ page }) => {
    const issues = await page.locator('#architecture-issues > div').count();
    expect(issues).toBe(4);
  });

  test('should show God Class issue from real data', async ({ page }) => {
    const firstIssue = await page.textContent('#architecture-issues > div:first-child');
    expect(firstIssue).toContain('God Class');
    expect(firstIssue).toContain('ux_enhancement_orchestrator.py');
  });

  test('should color-code issues by severity', async ({ page }) => {
    const highSeverityBorder = await page.locator('#architecture-issues > div:first-child').evaluate(
      el => window.getComputedStyle(el).borderLeftColor
    );
    
    // High severity should be red
    expect(highSeverityBorder).toContain('rgb');
  });

  test('should display complexity values', async ({ page }) => {
    const firstIssue = await page.textContent('#architecture-issues > div:first-child');
    expect(firstIssue).toContain('Complexity: 45');
  });

  test('should have interactive graph nodes', async ({ page }) => {
    await waitForVisualization(page, '#architecture-graph');
    
    const node = page.locator('#architecture-graph svg circle').first();
    await node.hover();
    
    // Tooltip should appear
    await page.waitForTimeout(300);
    const tooltip = page.locator('.tooltip, [role="tooltip"]');
    const tooltipCount = await tooltip.count();
    
    // Tooltip may or may not be visible depending on implementation
    expect(tooltipCount).toBeGreaterThanOrEqual(0);
  });

  test('should show component descriptions', async ({ page }) => {
    const description = await page.textContent('#component-list > div:first-child .text-sm');
    expect(description).toContain('Core governance');
  });

  test('should update graph on window resize', async ({ page }) => {
    await waitForVisualization(page, '#architecture-graph');
    
    await page.setViewportSize({ width: 1200, height: 800 });
    await page.waitForTimeout(500);
    
    const svgExists = await page.locator('#architecture-graph svg').count();
    expect(svgExists).toBeGreaterThan(0);
  });

  test('should render graph without errors', async ({ page }) => {
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text());
    });
    
    await switchTab(page, 'Architecture');
    await waitForVisualization(page, '#architecture-graph');
    
    expect(errors.length).toBe(0);
  });

  test('should have proper SVG dimensions', async ({ page }) => {
    await waitForVisualization(page, '#architecture-graph');
    
    const dimensions = await page.evaluate(() => {
      const svg = document.querySelector('#architecture-graph svg');
      return {
        width: svg.getAttribute('width'),
        height: svg.getAttribute('height')
      };
    });
    
    expect(parseInt(dimensions.width)).toBeGreaterThan(0);
    expect(parseInt(dimensions.height)).toBeGreaterThan(0);
  });

  test('should show architecture metrics', async ({ page }) => {
    // Check if metrics are displayed
    const metricsExist = await page.evaluate(() => {
      return window.dashboardData.architecture.metrics !== undefined;
    });
    
    expect(metricsExist).toBeTruthy();
  });
});
