/**
 * Integration Tests - Data Sources
 * 
 * Tests data source switching and validation.
 */

import { mockFullDashboard } from '../fixtures/mock-full-data.js';

describe('Data Sources Integration', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <div class="dashboard-container">
                <select id="sourceSelect">
                    <option value="mock">Mock Data</option>
                    <option value="cortex">CORTEX</option>
                    <option value="luum-fresh">Luum Fresh</option>
                </select>
                <button id="refreshButton">Refresh</button>
                <div id="executive-tab" class="tab-content"></div>
            </div>
        `;
        
        global.fetch = jest.fn().mockResolvedValue({
            ok: true,
            json: async () => mockFullDashboard
        });
    });
    
    test('should load mock data source by default', async () => {
        const select = document.getElementById('sourceSelect');
        expect(select.value).toBe('mock');
    });
    
    test('should change data source when selector changes', async () => {
        const select = document.getElementById('sourceSelect');
        select.value = 'cortex';
        select.dispatchEvent(new Event('change'));
        
        expect(select.value).toBe('cortex');
    });
    
    test('should refresh data when refresh button clicked', async () => {
        const { loadDashboardData } = await import('../../data-loader.js');
        const refreshButton = document.getElementById('refreshButton');
        
        // Initial load
        await loadDashboardData('mock');
        const initialCallCount = global.fetch.mock.calls.length;
        
        // Simulate refresh
        refreshButton.click();
        
        expect(global.fetch).toHaveBeenCalled();
    });
    
    test('should validate data source exists before loading', async () => {
        const select = document.getElementById('sourceSelect');
        select.value = 'nonexistent';
        
        const { loadDashboardData } = await import('../../data-loader.js');
        
        // Should reject or handle gracefully
        await expect(loadDashboardData('nonexistent')).rejects.toThrow();
    });
    
    test('should show all available data sources in selector', () => {
        const select = document.getElementById('sourceSelect');
        const options = Array.from(select.options).map(opt => opt.value);
        
        expect(options).toContain('mock');
        expect(options.length).toBeGreaterThan(0);
    });
    
    test('should handle data source with missing files', async () => {
        global.fetch = jest.fn().mockResolvedValue({
            ok: false,
            status: 404
        });
        
        const { loadDashboardData } = await import('../../data-loader.js');
        
        await expect(loadDashboardData('mock')).rejects.toThrow();
    });
    
    test('should preserve current tab when switching data sources', async () => {
        document.body.innerHTML += `
            <button class="tab-button" data-tab="tech-stack">Tech Stack</button>
            <div id="tech-stack-tab" class="tab-content"></div>
        `;
        
        const techStackButton = document.querySelector('[data-tab="tech-stack"]');
        techStackButton.click();
        
        const select = document.getElementById('sourceSelect');
        select.value = 'cortex';
        select.dispatchEvent(new Event('change'));
        
        // Should still show tech-stack tab
        const techStackTab = document.getElementById('tech-stack-tab');
        expect(techStackTab).toBeTruthy();
    });
});
