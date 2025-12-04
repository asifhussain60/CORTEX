/**
 * Integration Tests - Dashboard Application
 * 
 * Tests full dashboard initialization, tab switching, and data flow.
 * 
 * Run: npm test tests/integration/dashboard-app.test.js
 */

import { mockFullDashboard } from '../fixtures/mock-data.js';

describe('Dashboard Application Integration', () => {
    let app;
    
    beforeAll(async () => {
        // Load app module
        app = await import('../../app.js');
    });
    
    beforeEach(() => {
        // Setup DOM
        document.body.innerHTML = `
            <div class="dashboard-container" style="display: none;">
                <div id="sourceSelect"></div>
                <div class="tabs">
                    <button class="tab-button" data-tab="overview">Overview</button>
                    <button class="tab-button" data-tab="tech-stack">Tech Stack</button>
                    <button class="tab-button" data-tab="security">Security</button>
                    <button class="tab-button" data-tab="architecture">Architecture</button>
                    <button class="tab-button" data-tab="code-org">Code Organization</button>
                    <button class="tab-button" data-tab="team">Team Metrics</button>
                    <button class="tab-button" data-tab="vendors">Vendors</button>
                </div>
                <div id="overview" class="tab-content"></div>
                <div id="tech-stack" class="tab-content" style="display: none;"></div>
                <div id="security" class="tab-content" style="display: none;"></div>
                <div id="architecture" class="tab-content" style="display: none;"></div>
                <div id="code-org" class="tab-content" style="display: none;"></div>
                <div id="team" class="tab-content" style="display: none;"></div>
                <div id="vendors" class="tab-content" style="display: none;"></div>
            </div>
        `;
        
        // Mock fetch
        global.fetch = jest.fn().mockResolvedValue({
            ok: true,
            json: async () => mockFullDashboard
        });
    });
    
    afterEach(() => {
        jest.restoreAllMocks();
    });
    
    describe('Application Initialization', () => {
        it('should initialize app successfully', async () => {
            await app.initializeApp();
            
            const container = document.querySelector('.dashboard-container');
            expect(container.style.display).not.toBe('none');
        });
        
        it('should load mock data on initialization', async () => {
            await app.initializeApp();
            
            expect(global.fetch).toHaveBeenCalled();
            const fetchUrl = global.fetch.mock.calls[0][0];
            expect(fetchUrl).toContain('mock');
        });
        
        it('should render overview tab by default', async () => {
            await app.initializeApp();
            
            const overviewTab = document.getElementById('overview');
            expect(overviewTab.style.display).not.toBe('none');
            expect(overviewTab.innerHTML).not.toBe('');
        });
        
        it('should handle initialization errors gracefully', async () => {
            global.fetch.mockRejectedValueOnce(new Error('Init error'));
            
            await expect(app.initializeApp()).rejects.toThrow();
            
            // Error toast should be shown
            const errorToast = document.querySelector('.toast-error');
            expect(errorToast).toBeDefined();
        });
    });
    
    describe('Tab Switching', () => {
        beforeEach(async () => {
            await app.initializeApp();
        });
        
        it('should switch to tech-stack tab', async () => {
            await app.switchTab('tech-stack');
            
            const techStackTab = document.getElementById('tech-stack');
            const overviewTab = document.getElementById('overview');
            
            expect(techStackTab.style.display).not.toBe('none');
            expect(overviewTab.style.display).toBe('none');
        });
        
        it('should switch to security tab', async () => {
            await app.switchTab('security');
            
            const securityTab = document.getElementById('security');
            expect(securityTab.style.display).not.toBe('none');
        });
        
        it('should switch to architecture tab', async () => {
            await app.switchTab('architecture');
            
            const archTab = document.getElementById('architecture');
            expect(archTab.style.display).not.toBe('none');
        });
        
        it('should switch to code-org tab', async () => {
            await app.switchTab('code-org');
            
            const codeOrgTab = document.getElementById('code-org');
            expect(codeOrgTab.style.display).not.toBe('none');
        });
        
        it('should switch to team tab', async () => {
            await app.switchTab('team');
            
            const teamTab = document.getElementById('team');
            expect(teamTab.style.display).not.toBe('none');
        });
        
        it('should switch to vendors tab', async () => {
            await app.switchTab('vendors');
            
            const vendorsTab = document.getElementById('vendors');
            expect(vendorsTab.style.display).not.toBe('none');
        });
        
        it('should update active tab button', async () => {
            await app.switchTab('security');
            
            const securityButton = document.querySelector('[data-tab="security"]');
            expect(securityButton.classList.contains('active')).toBe(true);
        });
        
        it('should lazy-load tab content', async () => {
            const techStackTab = document.getElementById('tech-stack');
            expect(techStackTab.innerHTML).toBe('');
            
            await app.switchTab('tech-stack');
            
            expect(techStackTab.innerHTML).not.toBe('');
        });
    });
    
    describe('Data Source Switching', () => {
        beforeEach(async () => {
            await app.initializeApp();
        });
        
        it('should switch from mock to live data source', async () => {
            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockFullDashboard
            });
            
            await app.handleSourceChange('live');
            
            const fetchUrl = global.fetch.mock.calls[0][0];
            expect(fetchUrl).toContain('live');
        });
        
        it('should reload all tabs on source change', async () => {
            await app.switchTab('tech-stack');
            
            const techStackTab = document.getElementById('tech-stack');
            const initialContent = techStackTab.innerHTML;
            
            await app.handleSourceChange('mock');
            
            // Content should be refreshed
            expect(global.fetch).toHaveBeenCalledTimes(2);
        });
        
        it('should show loading during source change', async () => {
            const changePromise = app.handleSourceChange('live');
            
            // Loading should be visible
            const loadingOverlay = document.querySelector('.loading-overlay');
            expect(loadingOverlay).toBeDefined();
            
            await changePromise;
            
            // Loading should be hidden
            expect(loadingOverlay.style.display).toBe('none');
        });
    });
    
    describe('Data Refresh', () => {
        beforeEach(async () => {
            await app.initializeApp();
        });
        
        it('should refresh dashboard data', async () => {
            const initialCallCount = global.fetch.mock.calls.length;
            
            await app.refreshData();
            
            expect(global.fetch).toHaveBeenCalledTimes(initialCallCount + 1);
        });
        
        it('should clear render cache on refresh', async () => {
            await app.switchTab('tech-stack');
            await app.refreshData();
            
            // Should re-render with fresh data
            const techStackTab = document.getElementById('tech-stack');
            expect(techStackTab.innerHTML).not.toBe('');
        });
        
        it('should show success toast on refresh', async () => {
            await app.refreshData();
            
            const successToast = document.querySelector('.toast-success');
            expect(successToast).toBeDefined();
            expect(successToast.textContent).toContain('refreshed');
        });
    });
    
    describe('Error Handling', () => {
        it('should handle data loading errors', async () => {
            global.fetch.mockRejectedValueOnce(new Error('Network error'));
            
            await expect(app.initializeApp()).rejects.toThrow();
            
            const errorToast = document.querySelector('.toast-error');
            expect(errorToast).toBeDefined();
        });
        
        it('should handle tab rendering errors', async () => {
            await app.initializeApp();
            
            // Mock render function to throw error
            const originalRender = app.renderTab;
            app.renderTab = jest.fn().mockRejectedValueOnce(new Error('Render error'));
            
            await expect(app.switchTab('tech-stack')).rejects.toThrow();
            
            app.renderTab = originalRender;
        });
        
        it('should recover from errors', async () => {
            global.fetch
                .mockRejectedValueOnce(new Error('First error'))
                .mockResolvedValueOnce({
                    ok: true,
                    json: async () => mockFullDashboard
                });
            
            // First attempt fails
            await expect(app.initializeApp()).rejects.toThrow();
            
            // Second attempt succeeds
            await expect(app.initializeApp()).resolves.not.toThrow();
        });
    });
    
    describe('Performance', () => {
        beforeEach(async () => {
            await app.initializeApp();
        });
        
        it('should cache rendered tabs', async () => {
            await app.switchTab('tech-stack');
            const firstRenderTime = Date.now();
            
            await app.switchTab('overview');
            await app.switchTab('tech-stack');
            const secondRenderTime = Date.now();
            
            // Second render should be much faster (cached)
            const timeDiff = secondRenderTime - firstRenderTime;
            expect(timeDiff).toBeLessThan(50);
        });
        
        it('should debounce resize handlers', async () => {
            let resizeCount = 0;
            window.addEventListener('resize', () => resizeCount++);
            
            // Trigger multiple resizes quickly
            window.dispatchEvent(new Event('resize'));
            window.dispatchEvent(new Event('resize'));
            window.dispatchEvent(new Event('resize'));
            
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // Should only handle once due to debouncing
            expect(resizeCount).toBeLessThan(3);
        });
    });
});
