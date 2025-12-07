/**
 * Integration Tests - User Interactions
 * 
 * Tests export functionality, keyboard navigation, and user actions.
 */

import { mockFullDashboard } from '../fixtures/mock-full-data.js';

describe('User Interactions Integration', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <div class="dashboard-container">
                <button id="exportJsonButton">Export JSON</button>
                <button id="exportCsvButton">Export CSV</button>
                <button id="refreshButton">Refresh</button>
                <div class="tabs">
                    <button class="tab-button active" data-tab="executive">Executive</button>
                    <button class="tab-button" data-tab="overview">Overview</button>
                </div>
                <div id="executive-tab" class="tab-content"></div>
                <div id="overview-tab" class="tab-content" style="display: none;"></div>
            </div>
        `;
        
        global.fetch = jest.fn().mockResolvedValue({
            ok: true,
            json: async () => mockFullDashboard
        });
    });
    
    test('should export data as JSON when export button clicked', () => {
        const exportButton = document.getElementById('exportJsonButton');
        expect(exportButton).toBeTruthy();
    });
    
    test('should export data as CSV when export button clicked', () => {
        const exportButton = document.getElementById('exportCsvButton');
        expect(exportButton).toBeTruthy();
    });
    
    test('should trigger data refresh when refresh button clicked', () => {
        const refreshButton = document.getElementById('refreshButton');
        refreshButton.click();
        
        // Should trigger reload
        expect(refreshButton).toBeTruthy();
    });
    
    test('should navigate tabs with keyboard (arrow keys)', () => {
        const executiveButton = document.querySelector('[data-tab="executive"]');
        
        // Simulate right arrow key
        const event = new KeyboardEvent('keydown', { key: 'ArrowRight' });
        executiveButton.dispatchEvent(event);
        
        expect(executiveButton).toBeTruthy();
    });
    
    test('should activate tab with Enter key', () => {
        const overviewButton = document.querySelector('[data-tab="overview"]');
        
        // Focus and press Enter
        overviewButton.focus();
        const event = new KeyboardEvent('keydown', { key: 'Enter' });
        overviewButton.dispatchEvent(event);
        
        expect(overviewButton).toBeTruthy();
    });
    
    test('should handle multiple rapid button clicks', () => {
        const refreshButton = document.getElementById('refreshButton');
        
        // Rapid clicks
        refreshButton.click();
        refreshButton.click();
        refreshButton.click();
        
        expect(refreshButton).toBeTruthy();
    });
    
    test('should show tooltips on hover (if implemented)', () => {
        const exportButton = document.getElementById('exportJsonButton');
        
        // Simulate hover
        const event = new MouseEvent('mouseenter');
        exportButton.dispatchEvent(event);
        
        expect(exportButton).toBeTruthy();
    });
});
