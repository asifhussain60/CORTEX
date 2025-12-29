// @ts-check
/**
 * CORTEX Intelligent UX Dashboard - Test Helpers
 * Shared utilities for Playwright tests
 * @typedef {import('@playwright/test').Page} Page
 */

/**
 * Wait for D3 visualizations to render
 * @param {Page} page 
 * @param {string} selector - SVG container selector
 * @param {number} [timeout=5000] - Maximum wait time in ms
 */
export async function waitForVisualization(page, selector, timeout = 5000) {
  await page.waitForSelector(`${selector} svg`, { timeout });
  // Wait for D3 transitions to complete
  await page.waitForTimeout(1000);
}

/**
 * Verify data was loaded from analysis-data.json (not mock)
 * @param {Page} page 
 * @returns {Promise<boolean>}
 */
export async function verifyRealDataLoaded(page) {
  const projectName = await page.textContent('h1, .project-name');
  // Mock data uses "Sample Project", real data uses "CORTEX"
  return projectName && projectName.includes('CORTEX');
}

/**
 * Switch to a specific tab
 * @param {Page} page 
 * @param {string} tabName - Tab button text
 * @returns {Promise<void>}
 */
export async function switchTab(page, tabName) {
  await page.click(`button:has-text("${tabName}")`);
  await page.waitForTimeout(500); // Animation delay
}

/**
 * Get all D3 elements from a visualization
 * @param {Page} page 
 * @param {string} selector - Container selector
 * @param {string} elementType - SVG element type (rect, circle, path, etc.)
 * @returns {Promise<number>}
 */
export async function getD3Elements(page, selector, elementType) {
  return await page.locator(`${selector} svg ${elementType}`).count();
}

/**
 * Verify score is within expected range
 * @param {number} score 
 * @param {number} min 
 * @param {number} max 
 * @returns {boolean}
 */
export function assertScoreInRange(score, min, max) {
  return score >= min && score <= max;
}

/**
 * Take a screenshot with consistent naming
 * @param {Page} page 
 * @param {string} testName 
 * @param {string} context 
 * @returns {Promise<string>}
 */
export async function takeScreenshot(page, testName, context) {
  const filename = `${testName}-${context}-${Date.now()}.png`;
  await page.screenshot({ path: `test-results/screenshots/${filename}`, fullPage: true });
  return filename;
}

/**
 * Verify console has no errors
 * @param {Page} page 
 * @returns {string[]}
 */
export function setupConsoleErrorTracking(page) {
  /** @type {string[]} */
  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });
  return errors;
}

/**
 * Check if element is visible in viewport
 * @param {Page} page 
 * @param {string} selector 
 * @returns {Promise<boolean>}
 */
export async function isInViewport(page, selector) {
  return await page.evaluate((sel) => {
    const element = document.querySelector(sel);
    if (!element) return false;
    const rect = element.getBoundingClientRect();
    return (
      rect.top >= 0 &&
      rect.left >= 0 &&
      rect.bottom <= window.innerHeight &&
      rect.right <= window.innerWidth
    );
  }, selector);
}

/**
 * Get computed style property
 * @param {Page} page 
 * @param {string} selector 
 * @param {string} property 
 * @returns {Promise<any>}
 */
export async function getComputedStyle(page, selector, property) {
  return await page.evaluate(
    ({ sel, prop }) => window.getComputedStyle(document.querySelector(sel))[prop],
    { sel: selector, prop: property }
  );
}
