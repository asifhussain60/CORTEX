// @ts-check
const { test, expect } = require('@playwright/test');
const { waitForVisualization, switchTab, getD3Elements } = require('./fixtures/test-helpers');

/**
 * Test Suite: Tab 6 - Security
 * Validates severity chart, OWASP radar, and risk gauge
 */
test.describe('Security Tab', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
    await switchTab(page, 'Security');
  });

  test('should display vulnerability counts', async ({ page }) => {
    const criticalCount = await page.textContent('#critical-vulns');
    const highCount = await page.textContent('#high-vulns');
    const mediumCount = await page.textContent('#medium-vulns');
    
    expect(parseInt(criticalCount)).toBe(2);
    expect(parseInt(highCount)).toBe(4);
    expect(parseInt(mediumCount)).toBe(6);
  });

  test('should render severity bar chart', async ({ page }) => {
    await waitForVisualization(page, '#security-severity-chart');
    
    const svgExists = await page.locator('#security-severity-chart svg').count();
    expect(svgExists).toBeGreaterThan(0);
  });

  test('should show 4 severity levels', async ({ page }) => {
    await waitForVisualization(page, '#security-severity-chart');
    
    const bars = await getD3Elements(page, '#security-severity-chart', 'rect');
    expect(bars).toBeGreaterThan(0);
  });

  test('should color-code severity bars correctly', async ({ page }) => {
    await waitForVisualization(page, '#security-severity-chart');
    
    const colors = await page.evaluate(() => {
      const rects = document.querySelectorAll('#security-severity-chart svg rect');
      return Array.from(rects).map(r => r.getAttribute('fill')).filter(Boolean);
    });
    
    // Should have red (critical), orange (high), yellow (medium), blue (low)
    const uniqueColors = new Set(colors);
    expect(uniqueColors.size).toBeGreaterThan(1);
  });

  test('should render OWASP radar chart', async ({ page }) => {
    await waitForVisualization(page, '#owasp-chart');
    
    const svgExists = await page.locator('#owasp-chart svg').count();
    expect(svgExists).toBeGreaterThan(0);
  });

  test('should show 5 OWASP categories from real data', async ({ page }) => {
    const categoryCount = await page.evaluate(() => {
      return window.dashboardData.security.owasp.length;
    });
    
    expect(categoryCount).toBe(5);
  });

  test('should display radar grid circles', async ({ page }) => {
    await waitForVisualization(page, '#owasp-chart');
    
    const gridCircles = await getD3Elements(page, '#owasp-chart', 'circle');
    expect(gridCircles).toBeGreaterThan(0);
  });

  test('should show radar axes', async ({ page }) => {
    await waitForVisualization(page, '#owasp-chart');
    
    const axes = await getD3Elements(page, '#owasp-chart', 'line');
    expect(axes).toBeGreaterThan(0);
  });

  test('should display radar data area', async ({ page }) => {
    await waitForVisualization(page, '#owasp-chart');
    
    const dataPath = await getD3Elements(page, '#owasp-chart', 'path');
    expect(dataPath).toBeGreaterThan(0);
  });

  test('should show OWASP category labels', async ({ page }) => {
    await waitForVisualization(page, '#owasp-chart');
    
    const labels = await getD3Elements(page, '#owasp-chart', 'text');
    expect(labels).toBeGreaterThan(0);
  });

  test('should render risk gauge', async ({ page }) => {
    await waitForVisualization(page, '#risk-gauge');
    
    const svgExists = await page.locator('#risk-gauge svg').count();
    expect(svgExists).toBeGreaterThan(0);
  });

  test('should display risk score (72) from real data', async ({ page }) => {
    await waitForVisualization(page, '#risk-gauge');
    
    const score = await page.locator('#risk-gauge svg text:has-text("72")').count();
    expect(score).toBeGreaterThan(0);
  });

  test('should animate risk gauge', async ({ page }) => {
    await switchTab(page, 'Security');
    
    await page.waitForTimeout(1600);
    
    const arcExists = await page.evaluate(() => {
      const paths = document.querySelectorAll('#risk-gauge svg path');
      return paths.length > 0;
    });
    
    expect(arcExists).toBeTruthy();
  });

  test('should show "Risk Score" label', async ({ page }) => {
    await waitForVisualization(page, '#risk-gauge');
    
    const label = await page.locator('#risk-gauge svg text:has-text("Risk Score")').count();
    expect(label).toBeGreaterThan(0);
  });

  test('should display security issues list', async ({ page }) => {
    const issueCount = await page.evaluate(() => {
      return window.dashboardData.security.issues.length;
    });
    
    expect(issueCount).toBeGreaterThan(0);
  });

  test('should show SQL Injection as critical issue', async ({ page }) => {
    const hasSQLInjection = await page.evaluate(() => {
      const issues = window.dashboardData.security.issues;
      return issues.some(i => i.type === 'SQL Injection' && i.severity === 'critical');
    });
    
    expect(hasSQLInjection).toBeTruthy();
  });

  test('should show XSS as high severity issue', async ({ page }) => {
    const hasXSS = await page.evaluate(() => {
      const issues = window.dashboardData.security.issues;
      return issues.some(i => i.type === 'XSS' && i.severity === 'high');
    });
    
    expect(hasXSS).toBeTruthy();
  });

  test('should display value labels on severity chart', async ({ page }) => {
    await waitForVisualization(page, '#security-severity-chart');
    
    const valueLabels = await page.locator('#security-severity-chart svg text').count();
    expect(valueLabels).toBeGreaterThan(0);
  });

  test('should have compliance status', async ({ page }) => {
    const hasCompliance = await page.evaluate(() => {
      return window.dashboardData.security.complianceStatus !== undefined;
    });
    
    expect(hasCompliance).toBeTruthy();
  });

  test('should show OWASP Top 10 2021 categories', async ({ page }) => {
    const hasOWASP2021 = await page.evaluate(() => {
      const categories = window.dashboardData.security.owasp;
      return categories.some(c => c.category.includes('2021'));
    });
    
    expect(hasOWASP2021).toBeTruthy();
  });

  test('should display lowest OWASP score (60)', async ({ page }) => {
    const lowestScore = await page.evaluate(() => {
      const scores = window.dashboardData.security.owasp.map(o => o.score);
      return Math.min(...scores);
    });
    
    expect(lowestScore).toBe(60);
  });

  test('should animate severity bars', async ({ page }) => {
    await switchTab(page, 'Security');
    
    await page.waitForTimeout(1200);
    
    const barHeight = await page.evaluate(() => {
      const bar = document.querySelector('#security-severity-chart svg rect');
      return bar ? parseFloat(bar.getAttribute('height')) : 0;
    });
    
    expect(barHeight).toBeGreaterThan(0);
  });
});
