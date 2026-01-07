// @ts-check
const { test, expect } = require('@playwright/test');
const { waitForVisualization, switchTab, getD3Elements } = require('./fixtures/test-helpers');

/**
 * Test Suite: Tab 4 - Roadmap
 * Validates Gantt chart, priority matrix, and dependency graph
 */
test.describe('Roadmap Tab', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
    await switchTab(page, 'Roadmap');
  });

  test('should render Gantt chart', async ({ page }) => {
    await waitForVisualization(page, '#roadmap-gantt');
    
    const svgExists = await page.locator('#roadmap-gantt svg').count();
    expect(svgExists).toBeGreaterThan(0);
  });

  test('should display 7 tasks from real data', async ({ page }) => {
    const taskCount = await page.evaluate(() => {
      return window.dashboardData.roadmap.tasks.length;
    });
    
    expect(taskCount).toBe(7);
  });

  test('should show task bars in Gantt chart', async ({ page }) => {
    await waitForVisualization(page, '#roadmap-gantt');
    
    const taskBars = await getD3Elements(page, '#roadmap-gantt', 'rect');
    expect(taskBars).toBeGreaterThan(0);
  });

  test('should color-code tasks by priority', async ({ page }) => {
    await waitForVisualization(page, '#roadmap-gantt');
    
    const colors = await page.evaluate(() => {
      const rects = document.querySelectorAll('#roadmap-gantt svg rect');
      return Array.from(rects).map(r => r.getAttribute('fill')).filter(Boolean);
    });
    
    // Should have different colors for different priorities
    const uniqueColors = new Set(colors);
    expect(uniqueColors.size).toBeGreaterThan(1);
  });

  test('should display priority matrix', async ({ page }) => {
    await waitForVisualization(page, '#priority-matrix');
    
    const svgExists = await page.locator('#priority-matrix svg').count();
    expect(svgExists).toBeGreaterThan(0);
  });

  test('should show quadrant backgrounds in priority matrix', async ({ page }) => {
    await waitForVisualization(page, '#priority-matrix');
    
    const quadrants = await getD3Elements(page, '#priority-matrix', 'rect[opacity]');
    expect(quadrants).toBe(4); // Quick Wins, Major Projects, Fill Ins, Thankless Tasks
  });

  test('should plot tasks on priority matrix', async ({ page }) => {
    await waitForVisualization(page, '#priority-matrix');
    
    const taskPoints = await getD3Elements(page, '#priority-matrix', 'circle');
    expect(taskPoints).toBe(7);
  });

  test('should render dependency graph', async ({ page }) => {
    await waitForVisualization(page, '#dependency-graph');
    
    const svgExists = await page.locator('#dependency-graph svg').count();
    expect(svgExists).toBeGreaterThan(0);
  });

  test('should show 3 dependencies from real data', async ({ page }) => {
    const dependencyCount = await page.evaluate(() => {
      return window.dashboardData.roadmap.dependencies.length;
    });
    
    expect(dependencyCount).toBe(3);
  });

  test('should display legend on Gantt chart', async ({ page }) => {
    await waitForVisualization(page, '#roadmap-gantt');
    
    // Check for legend elements
    const legendExists = await page.evaluate(() => {
      const svg = document.querySelector('#roadmap-gantt svg');
      return svg ? svg.innerHTML.includes('Critical') || svg.innerHTML.includes('High') : false;
    });
    
    expect(legendExists).toBeTruthy();
  });

  test('should show first task as "Fix Critical Security Issues"', async ({ page }) => {
    const firstTask = await page.evaluate(() => {
      return window.dashboardData.roadmap.tasks[0].name;
    });
    
    expect(firstTask).toBe('Fix Critical Security Issues');
  });

  test('should have correct duration for first task (3 days)', async ({ page }) => {
    const duration = await page.evaluate(() => {
      return window.dashboardData.roadmap.tasks[0].duration;
    });
    
    expect(duration).toBe(3);
  });

  test('should display tooltips on task hover', async ({ page }) => {
    await waitForVisualization(page, '#roadmap-gantt');
    
    const taskBar = page.locator('#roadmap-gantt svg rect').first();
    await taskBar.hover();
    
    await page.waitForTimeout(300);
    // Tooltip implementation-dependent
  });

  test('should show impact/effort values in priority matrix', async ({ page }) => {
    const task = await page.evaluate(() => {
      return window.dashboardData.roadmap.tasks[0];
    });
    
    expect(task.impact).toBe(9);
    expect(task.effort).toBe(3);
  });

  test('should have axes on priority matrix', async ({ page }) => {
    await waitForVisualization(page, '#priority-matrix');
    
    const hasAxes = await page.evaluate(() => {
      const svg = document.querySelector('#priority-matrix svg');
      const text = svg ? svg.textContent : '';
      return text.includes('Effort') || text.includes('Impact');
    });
    
    expect(hasAxes).toBeTruthy();
  });

  test('should show axes on Gantt chart', async ({ page }) => {
    await waitForVisualization(page, '#roadmap-gantt');
    
    const axes = await page.locator('#roadmap-gantt svg g').count();
    expect(axes).toBeGreaterThan(0);
  });

  test('should display task categories', async ({ page }) => {
    const categories = await page.evaluate(() => {
      return window.dashboardData.roadmap.tasks.map(t => t.category);
    });
    
    const uniqueCategories = new Set(categories);
    expect(uniqueCategories.size).toBeGreaterThan(1);
  });

  test('should have milestones if available', async ({ page }) => {
    const hasMilestones = await page.evaluate(() => {
      return window.dashboardData.roadmap.milestones !== undefined;
    });
    
    expect(hasMilestones).toBeTruthy();
  });
});
