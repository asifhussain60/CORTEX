/**
 * Integration Tests - Dashboard Loading
 * 
 * Tests dashboard initialization, data source loading, and error handling.
 */

import { mockFullDashboard, mockEmptyData } from '../fixtures/mock-full-data.js';

describe('Dashboard Loading Integration', () => {
    let originalFetch;
    
    beforeAll(() => {
        originalFetch = global.fetch;
    });
    
    afterAll(() => {
        global.fetch = originalFetch;
    });
    
    beforeEach(() => {
        // Setup minimal DOM
        document.body.innerHTML = `
            <div class="dashboard-container" style="display: none;">
                <div id="loading-overlay"></div>
                <div id="error-container"></div>
                <select id="sourceSelect">
                    <option value="mock">Mock</option>
                    <option value="cortex">CORTEX</option>
                </select>
                <div class="tabs">
                    <button class="tab-button active" data-tab="executive">Executive</button>
                    <button class="tab-button" data-tab="overview">Overview</button>
                    <button class="tab-button" data-tab="tech-stack">Tech Stack</button>
                    <button class="tab-button" data-tab="security">Security</button>
                    <button class="tab-button" data-tab="architecture">Architecture</button>
                    <button class="tab-button" data-tab="code-org">Code Org</button>
                    <button class="tab-button" data-tab="vendors">Vendors</button>
                    <button class="tab-button" data-tab="engineering">Engineering</button>
                </div>
                <div id="executive-tab" class="tab-content"></div>
                <div id="overview-tab" class="tab-content" style="display: none;"></div>
                <div id="tech-stack-tab" class="tab-content" style="display: none;"></div>
                <div id="security-tab" class="tab-content" style="display: none;"></div>
                <div id="architecture-tab" class="tab-content" style="display: none;"></div>
                <div id="code-org-tab" class="tab-content" style="display: none;"></div>
                <div id="vendors-tab" class="tab-content" style="display: none;"></div>
                <div id="engineering-tab" class="tab-content" style="display: none;"></div>
            </div>
        `;
        
        // Mock successful fetch
        global.fetch = jest.fn().mockResolvedValue({
            ok: true,
            json: async () => mockFullDashboard
        });
    });
    
    afterEach(() => {
        jest.clearAllMocks();
    });
    
    test('should show loading overlay during initialization', async () => {
        const loadingOverlay = document.getElementById('loading-overlay');
        expect(loadingOverlay).toBeTruthy();
    });
    
    test('should hide dashboard container initially', () => {
        const container = document.querySelector('.dashboard-container');
        expect(container.style.display).toBe('none');
    });
    
    test('should load mock data by default', async () => {
        const { loadDashboardData } = await import('../../data-loader.js');
        const data = await loadDashboardData('mock');
        
        expect(data).toBeDefined();
        expect(data.overview).toBeDefined();
        expect(data.techStack).toBeDefined();
    });
    
    test('should handle network errors gracefully', async () => {
        global.fetch = jest.fn().mockRejectedValue(new Error('Network error'));
        
        const { loadDashboardData } = await import('../../data-loader.js');
        
        await expect(loadDashboardData('mock')).rejects.toThrow();
    });
    
    test('should handle malformed JSON responses', async () => {
        global.fetch = jest.fn().mockResolvedValue({
            ok: true,
            json: async () => { throw new Error('Invalid JSON'); }
        });
        
        const { loadDashboardData } = await import('../../data-loader.js');
        
        await expect(loadDashboardData('mock')).rejects.toThrow();
    });
    
    test('should handle 404 responses', async () => {
        global.fetch = jest.fn().mockResolvedValue({
            ok: false,
            status: 404,
            statusText: 'Not Found'
        });
        
        const { loadDashboardData } = await import('../../data-loader.js');
        
        await expect(loadDashboardData('nonexistent')).rejects.toThrow();
    });
    
    test('should load all required data files', async () => {
        const { loadDashboardData } = await import('../../data-loader.js');
        const data = await loadDashboardData('mock');
        
        // Verify all expected data sections
        expect(data.overview).toBeDefined();
        expect(data.techStack).toBeDefined();
        expect(data.security).toBeDefined();
        expect(data.architecture).toBeDefined();
        expect(data.codeOrg).toBeDefined();
        expect(data.vendors).toBeDefined();
        expect(data.executive).toBeDefined();
    });
    
    test('should cache loaded data', async () => {
        const { loadDashboardData } = await import('../../data-loader.js');
        
        // First load
        await loadDashboardData('mock');
        const firstCallCount = global.fetch.mock.calls.length;
        
        // Second load (should use cache)
        await loadDashboardData('mock');
        const secondCallCount = global.fetch.mock.calls.length;
        
        expect(secondCallCount).toBe(firstCallCount); // No additional fetches
    });
    
    test('should clear cache when requested', async () => {
        const { loadDashboardData, clearCache } = await import('../../data-loader.js');
        
        // Load and cache
        await loadDashboardData('mock');
        
        // Clear cache
        clearCache();
        
        // Load again (should fetch)
        await loadDashboardData('mock');
        
        expect(global.fetch).toHaveBeenCalled();
    });
    
    test('should handle empty data gracefully', async () => {
        global.fetch = jest.fn().mockResolvedValue({
            ok: true,
            json: async () => mockEmptyData
        });
        
        const { loadDashboardData } = await import('../../data-loader.js');
        const data = await loadDashboardData('mock');
        
        expect(data).toBeDefined();
        expect(data.overview.health_categories).toEqual([]);
    });
});
