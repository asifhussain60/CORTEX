/**
 * Integration Tests - Tab Navigation
 * 
 * Tests tab switching, state management, and navigation flows.
 */

import { mockFullDashboard } from '../fixtures/mock-full-data.js';

describe('Tab Navigation Integration', () => {
    beforeEach(() => {
        // Setup DOM with all 8 tabs
        document.body.innerHTML = `
            <div class="dashboard-container">
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
        
        // Mock fetch
        global.fetch = jest.fn().mockResolvedValue({
            ok: true,
            json: async () => mockFullDashboard
        });
    });
    
    test('should start with executive tab active', () => {
        const executiveButton = document.querySelector('[data-tab="executive"]');
        const executiveTab = document.getElementById('executive-tab');
        
        expect(executiveButton.classList.contains('active')).toBe(true);
        expect(executiveTab.style.display).not.toBe('none');
    });
    
    test('should switch to overview tab when clicked', () => {
        const overviewButton = document.querySelector('[data-tab="overview"]');
        overviewButton.click();
        
        const overviewTab = document.getElementById('overview-tab');
        expect(overviewTab.style.display).not.toBe('none');
    });
    
    test('should hide previous tab when switching', () => {
        const executiveTab = document.getElementById('executive-tab');
        const overviewButton = document.querySelector('[data-tab="overview"]');
        
        overviewButton.click();
        
        expect(executiveTab.style.display).toBe('none');
    });
    
    test('should update active button state', () => {
        const executiveButton = document.querySelector('[data-tab="executive"]');
        const overviewButton = document.querySelector('[data-tab="overview"]');
        
        overviewButton.click();
        
        expect(executiveButton.classList.contains('active')).toBe(false);
        expect(overviewButton.classList.contains('active')).toBe(true);
    });
    
    test('should switch through all 8 tabs sequentially', () => {
        const tabs = ['overview', 'tech-stack', 'security', 'architecture', 'code-org', 'vendors', 'engineering', 'executive'];
        
        tabs.forEach(tabName => {
            const button = document.querySelector(`[data-tab="${tabName}"]`);
            button.click();
            
            const tabContent = document.getElementById(`${tabName}-tab`);
            expect(tabContent.style.display).not.toBe('none');
        });
    });
    
    test('should handle rapid tab switching', () => {
        const overviewButton = document.querySelector('[data-tab="overview"]');
        const techStackButton = document.querySelector('[data-tab="tech-stack"]');
        const securityButton = document.querySelector('[data-tab="security"]');
        
        overviewButton.click();
        techStackButton.click();
        securityButton.click();
        
        const securityTab = document.getElementById('security-tab');
        expect(securityTab.style.display).not.toBe('none');
        expect(securityButton.classList.contains('active')).toBe(true);
    });
    
    test('should preserve tab state when switching back', () => {
        const overviewButton = document.querySelector('[data-tab="overview"]');
        const techStackButton = document.querySelector('[data-tab="tech-stack"]');
        
        // Add content to overview tab
        const overviewTab = document.getElementById('overview-tab');
        overviewTab.innerHTML = '<div id="test-content">Test</div>';
        
        // Switch to tech-stack
        techStackButton.click();
        
        // Switch back to overview
        overviewButton.click();
        
        // Content should still be there
        expect(document.getElementById('test-content')).toBeTruthy();
    });
    
    test('should only have one visible tab at a time', () => {
        const techStackButton = document.querySelector('[data-tab="tech-stack"]');
        techStackButton.click();
        
        const allTabs = document.querySelectorAll('.tab-content');
        const visibleTabs = Array.from(allTabs).filter(tab => tab.style.display !== 'none');
        
        expect(visibleTabs.length).toBe(1);
    });
    
    test('should only have one active button at a time', () => {
        const overviewButton = document.querySelector('[data-tab="overview"]');
        overviewButton.click();
        
        const activeButtons = document.querySelectorAll('.tab-button.active');
        expect(activeButtons.length).toBe(1);
    });
});
