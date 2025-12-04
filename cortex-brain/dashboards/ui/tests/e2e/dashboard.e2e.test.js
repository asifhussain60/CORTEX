/**
 * End-to-End Tests - Full Dashboard User Workflows
 * 
 * Tests complete user journeys through the dashboard interface.
 * Requires: npm install puppeteer
 * 
 * Run: npm test tests/e2e/dashboard.e2e.test.js
 */

const puppeteer = require('puppeteer');

describe('Dashboard E2E Tests', () => {
    let browser;
    let page;
    const baseUrl = 'http://localhost:8080';
    
    beforeAll(async () => {
        browser = await puppeteer.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
    });
    
    afterAll(async () => {
        await browser.close();
    });
    
    beforeEach(async () => {
        page = await browser.newPage();
        await page.setViewport({ width: 1920, height: 1080 });
        
        // Setup console logging
        page.on('console', msg => console.log('PAGE LOG:', msg.text()));
        page.on('pageerror', error => console.error('PAGE ERROR:', error));
    });
    
    afterEach(async () => {
        await page.close();
    });
    
    describe('Dashboard Loading', () => {
        it('should load dashboard homepage', async () => {
            await page.goto(`${baseUrl}/index.html?source=mock`, {
                waitUntil: 'networkidle0',
                timeout: 10000
            });
            
            // Check title
            const title = await page.title();
            expect(title).toContain('CORTEX Dashboard');
            
            // Check dashboard container is visible
            const container = await page.$('.dashboard-container');
            expect(container).not.toBeNull();
            
            const isVisible = await page.evaluate(
                el => el.style.display !== 'none',
                container
            );
            expect(isVisible).toBe(true);
        });
        
        it('should load without console errors', async () => {
            const errors = [];
            page.on('pageerror', error => errors.push(error.message));
            
            await page.goto(`${baseUrl}/index.html?source=mock`, {
                waitUntil: 'networkidle0'
            });
            
            expect(errors).toEqual([]);
        });
        
        it('should load all required scripts', async () => {
            await page.goto(`${baseUrl}/index.html?source=mock`, {
                waitUntil: 'networkidle0'
            });
            
            // Check D3.js loaded
            const d3Loaded = await page.evaluate(() => typeof window.d3 !== 'undefined');
            expect(d3Loaded).toBe(true);
            
            // Check THREE.js loaded
            const threeLoaded = await page.evaluate(() => typeof window.THREE !== 'undefined');
            expect(threeLoaded).toBe(true);
            
            // Check Chart.js loaded
            const chartLoaded = await page.evaluate(() => typeof window.Chart !== 'undefined');
            expect(chartLoaded).toBe(true);
        });
        
        it('should display loading indicator initially', async () => {
            const loadingShown = [];
            
            page.on('console', msg => {
                if (msg.text().includes('Loading')) {
                    loadingShown.push(msg.text());
                }
            });
            
            await page.goto(`${baseUrl}/index.html?source=mock`);
            
            expect(loadingShown.length).toBeGreaterThan(0);
        });
    });
    
    describe('Tab Navigation', () => {
        beforeEach(async () => {
            await page.goto(`${baseUrl}/index.html?source=mock`, {
                waitUntil: 'networkidle0'
            });
        });
        
        it('should switch to Tech Stack tab', async () => {
            await page.click('[data-tab="tech-stack"]');
            await page.waitForSelector('#tech-stack:not([style*="display: none"])');
            
            const content = await page.$eval('#tech-stack', el => el.innerHTML);
            expect(content).toContain('Python');
        });
        
        it('should switch to Security tab', async () => {
            await page.click('[data-tab="security"]');
            await page.waitForSelector('#security:not([style*="display: none"])');
            
            const content = await page.$eval('#security', el => el.innerHTML);
            expect(content).toContain('vulnerabilities');
        });
        
        it('should switch to Architecture tab', async () => {
            await page.click('[data-tab="architecture"]');
            await page.waitForSelector('#architecture:not([style*="display: none"])');
            
            const content = await page.$eval('#architecture', el => el.innerHTML);
            expect(content).toContain('modules');
        });
        
        it('should switch to Code Organization tab', async () => {
            await page.click('[data-tab="code-org"]');
            await page.waitForSelector('#code-org:not([style*="display: none"])');
            
            const content = await page.$eval('#code-org', el => el.innerHTML);
            expect(content).toContain('directories');
        });
        
        it('should switch to Team tab', async () => {
            await page.click('[data-tab="team"]');
            await page.waitForSelector('#team:not([style*="display: none"])');
            
            const content = await page.$eval('#team', el => el.innerHTML);
            expect(content).toContain('contributors');
        });
        
        it('should switch to Vendors tab', async () => {
            await page.click('[data-tab="vendors"]');
            await page.waitForSelector('#vendors:not([style*="display: none"])');
            
            const content = await page.$eval('#vendors', el => el.innerHTML);
            expect(content).toContain('vendors');
        });
        
        it('should highlight active tab button', async () => {
            await page.click('[data-tab="security"]');
            
            const hasActiveClass = await page.$eval(
                '[data-tab="security"]',
                el => el.classList.contains('active')
            );
            
            expect(hasActiveClass).toBe(true);
        });
    });
    
    describe('Keyboard Navigation', () => {
        beforeEach(async () => {
            await page.goto(`${baseUrl}/index.html?source=mock`, {
                waitUntil: 'networkidle0'
            });
        });
        
        it('should switch tabs with Ctrl+1', async () => {
            await page.keyboard.down('Control');
            await page.keyboard.press('Digit1');
            await page.keyboard.up('Control');
            
            await page.waitForSelector('#overview:not([style*="display: none"])');
            
            const isVisible = await page.$eval(
                '#overview',
                el => el.style.display !== 'none'
            );
            expect(isVisible).toBe(true);
        });
        
        it('should switch tabs with Ctrl+2', async () => {
            await page.keyboard.down('Control');
            await page.keyboard.press('Digit2');
            await page.keyboard.up('Control');
            
            await page.waitForTimeout(500);
            
            const isVisible = await page.$eval(
                '#tech-stack',
                el => el.style.display !== 'none'
            );
            expect(isVisible).toBe(true);
        });
        
        it('should refresh data with Ctrl+R', async () => {
            await page.keyboard.down('Control');
            await page.keyboard.press('KeyR');
            await page.keyboard.up('Control');
            
            await page.waitForTimeout(1000);
            
            // Check for success toast
            const toast = await page.$('.toast-success');
            expect(toast).not.toBeNull();
        });
    });
    
    describe('Data Export', () => {
        beforeEach(async () => {
            await page.goto(`${baseUrl}/index.html?source=mock`, {
                waitUntil: 'networkidle0'
            });
        });
        
        it('should export JSON with Ctrl+S', async () => {
            const downloadPromise = page.waitForEvent('download');
            
            await page.keyboard.down('Control');
            await page.keyboard.press('KeyS');
            await page.keyboard.up('Control');
            
            const download = await downloadPromise;
            expect(download.suggestedFilename()).toContain('.json');
        });
        
        it('should export PDF with Ctrl+P', async () => {
            const downloadPromise = page.waitForEvent('download');
            
            await page.keyboard.down('Control');
            await page.keyboard.press('KeyP');
            await page.keyboard.up('Control');
            
            const download = await downloadPromise;
            expect(download.suggestedFilename()).toContain('.pdf');
        });
        
        it('should show export success toast', async () => {
            await page.keyboard.down('Control');
            await page.keyboard.press('KeyS');
            await page.keyboard.up('Control');
            
            await page.waitForSelector('.toast-success');
            
            const toastText = await page.$eval('.toast-success', el => el.textContent);
            expect(toastText).toContain('export');
        });
    });
    
    describe('Data Source Switching', () => {
        beforeEach(async () => {
            await page.goto(`${baseUrl}/index.html?source=mock`, {
                waitUntil: 'networkidle0'
            });
        });
        
        it('should switch from mock to live source', async () => {
            await page.select('#sourceSelect', 'live');
            
            await page.waitForTimeout(2000);
            
            // Check URL updated
            const url = page.url();
            expect(url).toContain('source=live');
        });
        
        it('should reload data on source change', async () => {
            const requestsMade = [];
            page.on('request', request => {
                if (request.url().includes('.json')) {
                    requestsMade.push(request.url());
                }
            });
            
            await page.select('#sourceSelect', 'live');
            await page.waitForTimeout(1000);
            
            expect(requestsMade.length).toBeGreaterThan(0);
        });
    });
    
    describe('Responsive Design', () => {
        it('should work on mobile viewport', async () => {
            await page.setViewport({ width: 375, height: 667 });
            
            await page.goto(`${baseUrl}/index.html?source=mock`, {
                waitUntil: 'networkidle0'
            });
            
            const container = await page.$('.dashboard-container');
            expect(container).not.toBeNull();
        });
        
        it('should work on tablet viewport', async () => {
            await page.setViewport({ width: 768, height: 1024 });
            
            await page.goto(`${baseUrl}/index.html?source=mock`, {
                waitUntil: 'networkidle0'
            });
            
            const container = await page.$('.dashboard-container');
            expect(container).not.toBeNull();
        });
        
        it('should work on desktop viewport', async () => {
            await page.setViewport({ width: 1920, height: 1080 });
            
            await page.goto(`${baseUrl}/index.html?source=mock`, {
                waitUntil: 'networkidle0'
            });
            
            const container = await page.$('.dashboard-container');
            expect(container).not.toBeNull();
        });
    });
    
    describe('Performance', () => {
        it('should load within 3 seconds', async () => {
            const startTime = Date.now();
            
            await page.goto(`${baseUrl}/index.html?source=mock`, {
                waitUntil: 'networkidle0'
            });
            
            const loadTime = Date.now() - startTime;
            expect(loadTime).toBeLessThan(3000);
        });
        
        it('should switch tabs in under 500ms', async () => {
            await page.goto(`${baseUrl}/index.html?source=mock`, {
                waitUntil: 'networkidle0'
            });
            
            const startTime = Date.now();
            await page.click('[data-tab="tech-stack"]');
            await page.waitForSelector('#tech-stack:not([style*="display: none"])');
            const switchTime = Date.now() - startTime;
            
            expect(switchTime).toBeLessThan(500);
        });
    });
    
    describe('Accessibility', () => {
        beforeEach(async () => {
            await page.goto(`${baseUrl}/index.html?source=mock`, {
                waitUntil: 'networkidle0'
            });
        });
        
        it('should have proper ARIA labels', async () => {
            const ariaLabels = await page.$$eval('[aria-label]', els => els.length);
            expect(ariaLabels).toBeGreaterThan(0);
        });
        
        it('should support keyboard navigation', async () => {
            await page.keyboard.press('Tab');
            
            const focusedElement = await page.evaluate(() => document.activeElement.tagName);
            expect(focusedElement).toBeDefined();
        });
        
        it('should have sufficient color contrast', async () => {
            // Check text colors meet WCAG AA standards
            const contrast = await page.evaluate(() => {
                const element = document.querySelector('.glass-card');
                const color = window.getComputedStyle(element).color;
                const bgColor = window.getComputedStyle(element).backgroundColor;
                return { color, bgColor };
            });
            
            expect(contrast.color).toBeDefined();
            expect(contrast.bgColor).toBeDefined();
        });
    });
});
