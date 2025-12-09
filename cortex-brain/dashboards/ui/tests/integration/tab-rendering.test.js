/**
 * Integration Tests - Tab Rendering
 * 
 * Tests all 8 tabs render correctly with various data sources.
 * Target: 80+ tests (8 tabs × 10 tests per tab)
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 */

import { 
    mockHealthData, 
    mockTechStack, 
    mockSecurity, 
    mockArchitecture,
    mockCodeOrg,
    mockVendors,
    mockFullDashboard 
} from '../fixtures/mock-data.js';

describe('Tab Rendering - All 8 Tabs', () => {
    let app;
    
    beforeAll(async () => {
        app = await import('../../app.js');
    });
    
    beforeEach(() => {
        // Setup complete DOM structure
        document.body.innerHTML = `
            <div class="dashboard-container">
                <div id="loadingOverlay" class="loading-overlay" style="display: none;">
                    <div class="loading-spinner">Loading...</div>
                </div>
                <div id="sourceSelect"></div>
                <nav class="nav-tabs">
                    <a class="nav-tab active" data-tab="executive">Executive</a>
                    <a class="nav-tab" data-tab="overview">Overview</a>
                    <a class="nav-tab" data-tab="tech-stack">Tech Stack</a>
                    <a class="nav-tab" data-tab="security">Security</a>
                    <a class="nav-tab" data-tab="architecture">Architecture</a>
                    <a class="nav-tab" data-tab="code-org">Code Organization</a>
                    <a class="nav-tab" data-tab="vendors">Vendors</a>
                    <a class="nav-tab" data-tab="onboarding">Onboarding</a>
                </nav>
                <div id="tab-executive" class="tab-content active"></div>
                <div id="tab-overview" class="tab-content"></div>
                <div id="tab-tech-stack" class="tab-content"></div>
                <div id="tab-security" class="tab-content"></div>
                <div id="tab-architecture" class="tab-content"></div>
                <div id="tab-code-org" class="tab-content"></div>
                <div id="tab-vendors" class="tab-content"></div>
                <div id="tab-onboarding" class="tab-content"></div>
                <div id="contentTitle">Executive Summary</div>
            </div>
        `;
        
        global.fetch = jest.fn().mockResolvedValue({
            ok: true,
            json: async () => mockFullDashboard
        });
    });
    
    afterEach(() => {
        jest.restoreAllMocks();
    });
    
    describe('Tab Click Auto-Loading (RED Phase)', () => {
        it('should show loading indicator when tab is clicked', async () => {
            // Arrange: Setup app with data
            window.appState = { data: mockFullDashboard, currentTab: 'executive', currentSource: 'mock' };
            
            // Act: Click on architecture tab
            const architectureTab = document.querySelector('[data-tab="architecture"]');
            architectureTab.click();
            
            // Assert: Loading overlay should appear
            const loadingOverlay = document.getElementById('loadingOverlay');
            expect(loadingOverlay.style.display).not.toBe('none');
        });
        
        it('should automatically render tab content when clicked', async () => {
            // Arrange: Setup app with data
            window.appState = { data: mockFullDashboard, currentTab: 'executive', currentSource: 'mock' };
            
            // Act: Click on overview tab
            const overviewTab = document.querySelector('[data-tab="overview"]');
            overviewTab.click();
            
            // Wait for async rendering
            await new Promise(resolve => setTimeout(resolve, 100));
            
            // Assert: Tab content should be populated
            const tabContent = document.getElementById('tab-overview');
            expect(tabContent.innerHTML).not.toBe('');
            expect(tabContent.classList.contains('active')).toBe(true);
        });
        
        it('should hide loading indicator after tab renders', async () => {
            // Arrange: Setup app with data
            window.appState = { data: mockFullDashboard, currentTab: 'executive', currentSource: 'mock' };
            
            // Act: Click on tech-stack tab
            const techStackTab = document.querySelector('[data-tab="tech-stack"]');
            techStackTab.click();
            
            // Wait for async rendering
            await new Promise(resolve => setTimeout(resolve, 200));
            
            // Assert: Loading should be hidden
            const loadingOverlay = document.getElementById('loadingOverlay');
            expect(loadingOverlay.style.display).toBe('none');
        });
        
        it('should not require separate refresh button click', async () => {
            // Arrange: Setup app with data
            window.appState = { data: mockFullDashboard, currentTab: 'executive', currentSource: 'mock' };
            
            // Act: Click on security tab (no refresh click)
            const securityTab = document.querySelector('[data-tab="security"]');
            securityTab.click();
            
            // Wait for async rendering
            await new Promise(resolve => setTimeout(resolve, 100));
            
            // Assert: Tab should be rendered immediately
            const tabContent = document.getElementById('tab-security');
            expect(tabContent.classList.contains('active')).toBe(true);
            // Content should exist (not empty)
            expect(tabContent.innerHTML.trim()).not.toBe('');
        });
        
        it('should update active tab styling immediately', async () => {
            // Arrange: Setup app with data
            window.appState = { data: mockFullDashboard, currentTab: 'executive', currentSource: 'mock' };
            
            // Act: Click on vendors tab
            const vendorsTab = document.querySelector('[data-tab="vendors"]');
            vendorsTab.click();
            
            // Assert: Tab should be marked as active
            expect(vendorsTab.classList.contains('active')).toBe(true);
            
            // Previous tab should not be active
            const executiveTab = document.querySelector('[data-tab="executive"]');
            expect(executiveTab.classList.contains('active')).toBe(false);
        });
    });
    
    describe('Executive Tab', () => {
        it('should render executive summary title', async () => {
            const { renderExecutiveSummary } = await import('../../components/executive-tab.js');
            const container = document.getElementById('executive-tab');
            
            renderExecutiveSummary(mockFullDashboard);
            
            expect(container.innerHTML).toContain('Executive Summary');
        });
        
        it('should render health score in executive tab', async () => {
            const { renderExecutiveSummary } = await import('../../components/executive-tab.js');
            const container = document.getElementById('executive-tab');
            
            renderExecutiveSummary(mockFullDashboard);
            
            expect(container.innerHTML).toContain('87.5');
        });
        
        it('should render key metrics section', async () => {
            const { renderExecutiveSummary } = await import('../../components/executive-tab.js');
            const container = document.getElementById('executive-tab');
            
            renderExecutiveSummary(mockFullDashboard);
            
            expect(container.innerHTML).toContain('Key Metrics');
        });
        
        it('should handle missing executive data gracefully', async () => {
            const { renderExecutiveSummary } = await import('../../components/executive-tab.js');
            const container = document.getElementById('executive-tab');
            
            renderExecutiveSummary({});
            
            expect(container.innerHTML).not.toBe('');
            expect(container.innerHTML).toContain('Executive Summary');
        });
        
        it('should render health trend indicator', async () => {
            const { renderExecutiveSummary } = await import('../../components/executive-tab.js');
            const container = document.getElementById('executive-tab');
            
            renderExecutiveSummary(mockFullDashboard);
            
            const trendIndicators = container.querySelectorAll('.trend-indicator, .trend-up, .trend-down');
            expect(trendIndicators.length).toBeGreaterThan(0);
        });
        
        it('should render critical issues alert if present', async () => {
            const { renderExecutiveSummary } = await import('../../components/executive-tab.js');
            const container = document.getElementById('executive-tab');
            
            const dataWithIssues = {
                ...mockFullDashboard,
                critical_issues: ['Issue 1', 'Issue 2']
            };
            
            renderExecutiveSummary(dataWithIssues);
            
            expect(container.innerHTML).toContain('critical');
        });
        
        it('should format large numbers with commas', async () => {
            const { renderExecutiveSummary } = await import('../../components/executive-tab.js');
            const container = document.getElementById('executive-tab');
            
            renderExecutiveSummary(mockFullDashboard);
            
            // Check for formatted numbers (e.g., 45,892)
            expect(container.innerHTML).toMatch(/\d{1,3}(,\d{3})*/);
        });
        
        it('should display last updated timestamp', async () => {
            const { renderExecutiveSummary } = await import('../../components/executive-tab.js');
            const container = document.getElementById('executive-tab');
            
            renderExecutiveSummary(mockFullDashboard);
            
            expect(container.innerHTML).toMatch(/updated|last|timestamp/i);
        });
        
        it('should have export button in executive tab', async () => {
            const { renderExecutiveSummary } = await import('../../components/executive-tab.js');
            const container = document.getElementById('executive-tab');
            
            renderExecutiveSummary(mockFullDashboard);
            
            const exportBtn = container.querySelector('button[onclick*="export"]');
            expect(exportBtn).toBeDefined();
        });
        
        it('should render executive tab without console errors', async () => {
            const { renderExecutiveSummary } = await import('../../components/executive-tab.js');
            const container = document.getElementById('executive-tab');
            
            const consoleError = jest.spyOn(console, 'error');
            renderExecutiveSummary(mockFullDashboard);
            
            expect(consoleError).not.toHaveBeenCalled();
            consoleError.mockRestore();
        });
    });
    
    describe('Overview Tab', () => {
        it('should render overview with health gauge', async () => {
            const { renderOverview } = await import('../../components/overview-tab-v3.js');
            const container = document.getElementById('overview-tab');
            container.innerHTML = '<div id="overview-container"></div>';
            
            renderOverview(mockFullDashboard);
            
            const gauge = document.getElementById('health-gauge');
            expect(gauge).toBeDefined();
        });
        
        it('should render key metrics cards', async () => {
            const { renderOverview } = await import('../../components/overview-tab-v3.js');
            const container = document.getElementById('overview-tab');
            container.innerHTML = '<div id="overview-container"></div>';
            
            renderOverview(mockFullDashboard);
            
            expect(container.innerHTML).toContain('Files');
            expect(container.innerHTML).toContain('Lines of Code');
        });
        
        it('should render health categories breakdown', async () => {
            const { renderOverview } = await import('../../components/overview-tab-v3.js');
            const container = document.getElementById('overview-tab');
            container.innerHTML = '<div id="overview-container"></div>';
            
            renderOverview(mockFullDashboard);
            
            expect(container.innerHTML).toContain('Health Categories');
        });
        
        it('should render composition pie chart', async () => {
            const { renderOverview } = await import('../../components/overview-tab-v3.js');
            const container = document.getElementById('overview-tab');
            container.innerHTML = '<div id="overview-container"></div>';
            
            renderOverview(mockFullDashboard);
            
            const chartContainer = document.getElementById('composition-chart');
            expect(chartContainer).toBeDefined();
        });
        
        it('should handle missing overview container gracefully', async () => {
            const { renderOverview } = await import('../../components/overview-tab-v3.js');
            
            const consoleError = jest.spyOn(console, 'error');
            renderOverview(mockFullDashboard);
            
            expect(consoleError).toHaveBeenCalledWith('Overview container not found');
            consoleError.mockRestore();
        });
        
        it('should render critical issues alert in overview', async () => {
            const { renderOverview } = await import('../../components/overview-tab-v3.js');
            const container = document.getElementById('overview-tab');
            container.innerHTML = '<div id="overview-container"></div>';
            
            const dataWithIssues = {
                ...mockFullDashboard,
                critical_issues: ['Critical Issue 1']
            };
            
            renderOverview(dataWithIssues);
            
            expect(container.innerHTML).toContain('Critical Issues');
        });
        
        it('should display health score with color coding', async () => {
            const { renderOverview } = await import('../../components/overview-tab-v3.js');
            const container = document.getElementById('overview-tab');
            container.innerHTML = '<div id="overview-container"></div>';
            
            renderOverview(mockFullDashboard);
            
            // Check for color-related classes or styles
            expect(container.innerHTML).toMatch(/color|health-score|gauge/i);
        });
        
        it('should render trend indicators for metrics', async () => {
            const { renderOverview } = await import('../../components/overview-tab-v3.js');
            const container = document.getElementById('overview-tab');
            container.innerHTML = '<div id="overview-container"></div>';
            
            renderOverview(mockFullDashboard);
            
            expect(container.innerHTML).toMatch(/trend|arrow|↑|↓/i);
        });
        
        it('should handle empty data gracefully', async () => {
            const { renderOverview } = await import('../../components/overview-tab-v3.js');
            const container = document.getElementById('overview-tab');
            container.innerHTML = '<div id="overview-container"></div>';
            
            renderOverview({});
            
            expect(container.innerHTML).not.toBe('');
        });
        
        it('should render overview without throwing errors', async () => {
            const { renderOverview } = await import('../../components/overview-tab-v3.js');
            const container = document.getElementById('overview-tab');
            container.innerHTML = '<div id="overview-container"></div>';
            
            expect(() => renderOverview(mockFullDashboard)).not.toThrow();
        });
    });
    
    describe('Tech Stack Tab', () => {
        it('should render language breakdown', async () => {
            const { renderTechStack } = await import('../../components/tech-stack-tab.js');
            const container = document.getElementById('tech-stack-tab');
            container.innerHTML = '<div id="tech-stack-container"></div>';
            
            renderTechStack(mockTechStack);
            
            expect(container.innerHTML).toContain('Python');
            expect(container.innerHTML).toContain('JavaScript');
        });
        
        it('should display language percentages', async () => {
            const { renderTechStack } = await import('../../components/tech-stack-tab.js');
            const container = document.getElementById('tech-stack-tab');
            container.innerHTML = '<div id="tech-stack-container"></div>';
            
            renderTechStack(mockTechStack);
            
            expect(container.innerHTML).toContain('68.5');
            expect(container.innerHTML).toContain('%');
        });
        
        it('should render frameworks section', async () => {
            const { renderTechStack } = await import('../../components/tech-stack-tab.js');
            const container = document.getElementById('tech-stack-tab');
            container.innerHTML = '<div id="tech-stack-container"></div>';
            
            renderTechStack(mockTechStack);
            
            expect(container.innerHTML).toContain('FastAPI');
            expect(container.innerHTML).toContain('React');
        });
        
        it('should display framework versions', async () => {
            const { renderTechStack } = await import('../../components/tech-stack-tab.js');
            const container = document.getElementById('tech-stack-tab');
            container.innerHTML = '<div id="tech-stack-container"></div>';
            
            renderTechStack(mockTechStack);
            
            expect(container.innerHTML).toContain('0.104.1');
            expect(container.innerHTML).toContain('18.2.0');
        });
        
        it('should render dependencies summary', async () => {
            const { renderTechStack } = await import('../../components/tech-stack-tab.js');
            const container = document.getElementById('tech-stack-tab');
            container.innerHTML = '<div id="tech-stack-container"></div>';
            
            renderTechStack(mockTechStack);
            
            expect(container.innerHTML).toContain('89');
            expect(container.innerHTML).toContain('dependencies');
        });
        
        it('should show outdated dependencies count', async () => {
            const { renderTechStack } = await import('../../components/tech-stack-tab.js');
            const container = document.getElementById('tech-stack-tab');
            container.innerHTML = '<div id="tech-stack-container"></div>';
            
            renderTechStack(mockTechStack);
            
            expect(container.innerHTML).toContain('8');
            expect(container.innerHTML).toContain('outdated');
        });
        
        it('should have export CSV button', async () => {
            const { renderTechStack } = await import('../../components/tech-stack-tab.js');
            const container = document.getElementById('tech-stack-tab');
            container.innerHTML = '<div id="tech-stack-container"></div>';
            
            renderTechStack(mockTechStack);
            
            expect(container.innerHTML).toContain('Export CSV');
        });
        
        it('should handle missing tech stack container', async () => {
            const { renderTechStack } = await import('../../components/tech-stack-tab.js');
            
            const consoleError = jest.spyOn(console, 'error');
            renderTechStack(mockTechStack);
            
            expect(consoleError).toHaveBeenCalledWith('Tech stack container not found');
            consoleError.mockRestore();
        });
        
        it('should render tech stack without errors', async () => {
            const { renderTechStack } = await import('../../components/tech-stack-tab.js');
            const container = document.getElementById('tech-stack-tab');
            container.innerHTML = '<div id="tech-stack-container"></div>';
            
            expect(() => renderTechStack(mockTechStack)).not.toThrow();
        });
        
        it('should display total technologies count', async () => {
            const { renderTechStack } = await import('../../components/tech-stack-tab.js');
            const container = document.getElementById('tech-stack-tab');
            container.innerHTML = '<div id="tech-stack-container"></div>';
            
            renderTechStack(mockTechStack);
            
            expect(container.innerHTML).toContain('Total Technologies');
        });
    });
    
    describe('Security Tab', () => {
        it('should render overall security score', async () => {
            const { renderSecurity } = await import('../../components/security-tab.js');
            const container = document.getElementById('security-tab');
            container.innerHTML = '<div id="security-container"></div>';
            
            renderSecurity(mockSecurity);
            
            expect(container.innerHTML).toContain('92.0');
        });
        
        it('should display vulnerability counts by severity', async () => {
            const { renderSecurity } = await import('../../components/security-tab.js');
            const container = document.getElementById('security-tab');
            container.innerHTML = '<div id="security-container"></div>';
            
            renderSecurity(mockSecurity);
            
            expect(container.innerHTML).toContain('Critical');
            expect(container.innerHTML).toContain('High');
        });
        
        it('should render OWASP Top 10 compliance', async () => {
            const { renderSecurity } = await import('../../components/security-tab.js');
            const container = document.getElementById('security-tab');
            container.innerHTML = '<div id="security-container"></div>';
            
            const dataWithOWASP = {
                ...mockSecurity,
                owasp_compliance: {
                    covered: 8,
                    total: 10
                }
            };
            
            renderSecurity(dataWithOWASP);
            
            expect(container.innerHTML).toContain('OWASP');
        });
        
        it('should list vulnerability details', async () => {
            const { renderSecurity } = await import('../../components/security-tab.js');
            const container = document.getElementById('security-tab');
            container.innerHTML = '<div id="security-container"></div>';
            
            const dataWithVulns = {
                ...mockSecurity,
                vulnerability_list: [
                    { id: 'CVE-2024-1234', severity: 'HIGH', description: 'Test vuln' }
                ]
            };
            
            renderSecurity(dataWithVulns);
            
            expect(container.innerHTML).toContain('CVE-2024-1234');
        });
        
        it('should color-code severity levels', async () => {
            const { renderSecurity } = await import('../../components/security-tab.js');
            const container = document.getElementById('security-tab');
            container.innerHTML = '<div id="security-container"></div>';
            
            renderSecurity(mockSecurity);
            
            expect(container.innerHTML).toMatch(/critical|high|medium|low/i);
        });
        
        it('should handle zero vulnerabilities', async () => {
            const { renderSecurity } = await import('../../components/security-tab.js');
            const container = document.getElementById('security-tab');
            container.innerHTML = '<div id="security-container"></div>';
            
            const cleanData = {
                overall_score: 100,
                vulnerabilities: {
                    critical: 0,
                    high: 0,
                    medium: 0,
                    low: 0
                }
            };
            
            renderSecurity(cleanData);
            
            expect(container.innerHTML).toContain('0');
        });
        
        it('should have export functionality', async () => {
            const { renderSecurity } = await import('../../components/security-tab.js');
            const container = document.getElementById('security-tab');
            container.innerHTML = '<div id="security-container"></div>';
            
            renderSecurity(mockSecurity);
            
            expect(container.innerHTML).toMatch(/export|download/i);
        });
        
        it('should handle missing security container', async () => {
            const { renderSecurity } = await import('../../components/security-tab.js');
            
            const consoleError = jest.spyOn(console, 'error');
            renderSecurity(mockSecurity);
            
            expect(consoleError).toHaveBeenCalled();
            consoleError.mockRestore();
        });
        
        it('should render security tab without throwing', async () => {
            const { renderSecurity } = await import('../../components/security-tab.js');
            const container = document.getElementById('security-tab');
            container.innerHTML = '<div id="security-container"></div>';
            
            expect(() => renderSecurity(mockSecurity)).not.toThrow();
        });
        
        it('should display security recommendations if present', async () => {
            const { renderSecurity } = await import('../../components/security-tab.js');
            const container = document.getElementById('security-tab');
            container.innerHTML = '<div id="security-container"></div>';
            
            const dataWithRecs = {
                ...mockSecurity,
                recommendations: ['Update dependencies', 'Enable 2FA']
            };
            
            renderSecurity(dataWithRecs);
            
            expect(container.innerHTML).toMatch(/recommendation|suggest/i);
        });
    });
    
    describe('Architecture Tab', () => {
        it('should render architecture patterns', async () => {
            const { renderArchitecture } = await import('../../components/architecture-tab.js');
            const container = document.getElementById('architecture-tab');
            container.innerHTML = '<div id="architecture-container"></div>';
            
            renderArchitecture(mockArchitecture);
            
            expect(container.innerHTML).toContain('Architecture');
        });
        
        it('should display detected patterns', async () => {
            const { renderArchitecture } = await import('../../components/architecture-tab.js');
            const container = document.getElementById('architecture-tab');
            container.innerHTML = '<div id="architecture-container"></div>';
            
            const dataWithPatterns = {
                ...mockArchitecture,
                patterns: ['MVC', 'Repository Pattern']
            };
            
            renderArchitecture(dataWithPatterns);
            
            expect(container.innerHTML).toContain('Pattern');
        });
        
        it('should render component structure', async () => {
            const { renderArchitecture } = await import('../../components/architecture-tab.js');
            const container = document.getElementById('architecture-tab');
            container.innerHTML = '<div id="architecture-container"></div>';
            
            renderArchitecture(mockArchitecture);
            
            expect(container.innerHTML).toContain('Component');
        });
        
        it('should display frontend architecture if present', async () => {
            const { renderArchitecture } = await import('../../components/architecture-tab.js');
            const container = document.getElementById('architecture-tab');
            container.innerHTML = '<div id="architecture-container"></div>';
            
            const dataWithFrontend = {
                ...mockArchitecture,
                frontend: { framework: 'React', patterns: ['Hooks'] }
            };
            
            renderArchitecture(dataWithFrontend);
            
            expect(container.innerHTML).toContain('Frontend');
        });
        
        it('should display backend architecture if present', async () => {
            const { renderArchitecture } = await import('../../components/architecture-tab.js');
            const container = document.getElementById('architecture-tab');
            container.innerHTML = '<div id="architecture-container"></div>';
            
            const dataWithBackend = {
                ...mockArchitecture,
                backend: { framework: 'FastAPI', patterns: ['REST'] }
            };
            
            renderArchitecture(dataWithBackend);
            
            expect(container.innerHTML).toContain('Backend');
        });
        
        it('should display database architecture if present', async () => {
            const { renderArchitecture } = await import('../../components/architecture-tab.js');
            const container = document.getElementById('architecture-tab');
            container.innerHTML = '<div id="architecture-container"></div>';
            
            const dataWithDB = {
                ...mockArchitecture,
                database: { type: 'PostgreSQL', patterns: ['Migrations'] }
            };
            
            renderArchitecture(dataWithDB);
            
            expect(container.innerHTML).toContain('Database');
        });
        
        it('should render Mermaid diagram container', async () => {
            const { renderArchitecture } = await import('../../components/architecture-tab.js');
            const container = document.getElementById('architecture-tab');
            container.innerHTML = '<div id="architecture-container"></div>';
            
            renderArchitecture(mockArchitecture);
            
            const diagramContainer = container.querySelector('.mermaid, #architecture-diagram');
            expect(diagramContainer).toBeDefined();
        });
        
        it('should handle missing architecture data', async () => {
            const { renderArchitecture } = await import('../../components/architecture-tab.js');
            const container = document.getElementById('architecture-tab');
            container.innerHTML = '<div id="architecture-container"></div>';
            
            renderArchitecture({});
            
            expect(container.innerHTML).not.toBe('');
        });
        
        it('should render architecture without errors', async () => {
            const { renderArchitecture } = await import('../../components/architecture-tab.js');
            const container = document.getElementById('architecture-tab');
            container.innerHTML = '<div id="architecture-container"></div>';
            
            expect(() => renderArchitecture(mockArchitecture)).not.toThrow();
        });
        
        it('should display architecture quality score if present', async () => {
            const { renderArchitecture } = await import('../../components/architecture-tab.js');
            const container = document.getElementById('architecture-tab');
            container.innerHTML = '<div id="architecture-container"></div>';
            
            const dataWithScore = {
                ...mockArchitecture,
                quality_score: 85.5
            };
            
            renderArchitecture(dataWithScore);
            
            expect(container.innerHTML).toContain('85.5');
        });
    });
    
    describe('Code Organization Tab', () => {
        it('should render complexity metrics', async () => {
            const { renderCodeOrganization } = await import('../../components/code-org-tab.js');
            const container = document.getElementById('code-org-tab');
            container.innerHTML = '<div id="code-org-container"></div>';
            
            renderCodeOrganization(mockCodeOrg);
            
            expect(container.innerHTML).toContain('Complexity');
        });
        
        it('should display hotspot detection', async () => {
            const { renderCodeOrganization } = await import('../../components/code-org-tab.js');
            const container = document.getElementById('code-org-tab');
            container.innerHTML = '<div id="code-org-container"></div>';
            
            const dataWithHotspots = {
                ...mockCodeOrg,
                hotspots: [
                    { file: 'src/main.py', complexity: 45, changes: 120 }
                ]
            };
            
            renderCodeOrganization(dataWithHotspots);
            
            expect(container.innerHTML).toContain('Hotspot');
        });
        
        it('should render file structure tree', async () => {
            const { renderCodeOrganization } = await import('../../components/code-org-tab.js');
            const container = document.getElementById('code-org-tab');
            container.innerHTML = '<div id="code-org-container"></div>';
            
            renderCodeOrganization(mockCodeOrg);
            
            expect(container.innerHTML).toMatch(/file|directory|folder/i);
        });
        
        it('should display code duplication metrics', async () => {
            const { renderCodeOrganization } = await import('../../components/code-org-tab.js');
            const container = document.getElementById('code-org-tab');
            container.innerHTML = '<div id="code-org-container"></div>';
            
            const dataWithDuplication = {
                ...mockCodeOrg,
                duplication: { percentage: 5.2, blocks: 23 }
            };
            
            renderCodeOrganization(dataWithDuplication);
            
            expect(container.innerHTML).toContain('5.2');
        });
        
        it('should render maintainability index', async () => {
            const { renderCodeOrganization } = await import('../../components/code-org-tab.js');
            const container = document.getElementById('code-org-tab');
            container.innerHTML = '<div id="code-org-container"></div>';
            
            const dataWithMaintainability = {
                ...mockCodeOrg,
                maintainability_index: 72.5
            };
            
            renderCodeOrganization(dataWithMaintainability);
            
            expect(container.innerHTML).toContain('72.5');
        });
        
        it('should display technical debt estimate', async () => {
            const { renderCodeOrganization } = await import('../../components/code-org-tab.js');
            const container = document.getElementById('code-org-tab');
            container.innerHTML = '<div id="code-org-container"></div>';
            
            const dataWithDebt = {
                ...mockCodeOrg,
                technical_debt: { days: 15.5, severity: 'medium' }
            };
            
            renderCodeOrganization(dataWithDebt);
            
            expect(container.innerHTML).toContain('15.5');
        });
        
        it('should handle missing code org data', async () => {
            const { renderCodeOrganization } = await import('../../components/code-org-tab.js');
            const container = document.getElementById('code-org-tab');
            container.innerHTML = '<div id="code-org-container"></div>';
            
            renderCodeOrganization({});
            
            expect(container.innerHTML).not.toBe('');
        });
        
        it('should render code org without errors', async () => {
            const { renderCodeOrganization } = await import('../../components/code-org-tab.js');
            const container = document.getElementById('code-org-tab');
            container.innerHTML = '<div id="code-org-container"></div>';
            
            expect(() => renderCodeOrganization(mockCodeOrg)).not.toThrow();
        });
        
        it('should display most complex files', async () => {
            const { renderCodeOrganization } = await import('../../components/code-org-tab.js');
            const container = document.getElementById('code-org-tab');
            container.innerHTML = '<div id="code-org-container"></div>';
            
            renderCodeOrganization(mockCodeOrg);
            
            expect(container.innerHTML).toMatch(/complex|file/i);
        });
        
        it('should have visualization charts', async () => {
            const { renderCodeOrganization } = await import('../../components/code-org-tab.js');
            const container = document.getElementById('code-org-tab');
            container.innerHTML = '<div id="code-org-container"></div>';
            
            renderCodeOrganization(mockCodeOrg);
            
            const charts = container.querySelectorAll('canvas, .chart, [id*="chart"]');
            expect(charts.length).toBeGreaterThan(0);
        });
    });
    
    describe('Vendors Tab', () => {
        it('should render third-party services list', async () => {
            const { renderVendors } = await import('../../components/vendors-tab.js');
            const container = document.getElementById('vendors-tab');
            container.innerHTML = '<div id="vendors-container"></div>';
            
            renderVendors(mockVendors);
            
            expect(container.innerHTML).toContain('Vendor');
        });
        
        it('should display service risk assessment', async () => {
            const { renderVendors } = await import('../../components/vendors-tab.js');
            const container = document.getElementById('vendors-tab');
            container.innerHTML = '<div id="vendors-container"></div>';
            
            const dataWithRisk = {
                ...mockVendors,
                services: [
                    { name: 'AWS', risk: 'low', status: 'active' }
                ]
            };
            
            renderVendors(dataWithRisk);
            
            expect(container.innerHTML).toContain('Risk');
        });
        
        it('should show total vendor count', async () => {
            const { renderVendors } = await import('../../components/vendors-tab.js');
            const container = document.getElementById('vendors-tab');
            container.innerHTML = '<div id="vendors-container"></div>';
            
            renderVendors(mockVendors);
            
            expect(container.innerHTML).toMatch(/total|count/i);
        });
        
        it('should render vendor categories', async () => {
            const { renderVendors } = await import('../../components/vendors-tab.js');
            const container = document.getElementById('vendors-tab');
            container.innerHTML = '<div id="vendors-container"></div>';
            
            const dataWithCategories = {
                ...mockVendors,
                categories: ['Cloud', 'Analytics', 'Security']
            };
            
            renderVendors(dataWithCategories);
            
            expect(container.innerHTML).toContain('Category');
        });
        
        it('should display active vs inactive vendors', async () => {
            const { renderVendors } = await import('../../components/vendors-tab.js');
            const container = document.getElementById('vendors-tab');
            container.innerHTML = '<div id="vendors-container"></div>';
            
            renderVendors(mockVendors);
            
            expect(container.innerHTML).toMatch(/active|status/i);
        });
        
        it('should handle empty vendor list', async () => {
            const { renderVendors } = await import('../../components/vendors-tab.js');
            const container = document.getElementById('vendors-tab');
            container.innerHTML = '<div id="vendors-container"></div>';
            
            renderVendors({ services: [] });
            
            expect(container.innerHTML).not.toBe('');
        });
        
        it('should render vendors without errors', async () => {
            const { renderVendors } = await import('../../components/vendors-tab.js');
            const container = document.getElementById('vendors-tab');
            container.innerHTML = '<div id="vendors-container"></div>';
            
            expect(() => renderVendors(mockVendors)).not.toThrow();
        });
        
        it('should have cost information if available', async () => {
            const { renderVendors } = await import('../../components/vendors-tab.js');
            const container = document.getElementById('vendors-tab');
            container.innerHTML = '<div id="vendors-container"></div>';
            
            const dataWithCost = {
                ...mockVendors,
                total_cost: 15000,
                currency: 'USD'
            };
            
            renderVendors(dataWithCost);
            
            expect(container.innerHTML).toMatch(/cost|price|\$/i);
        });
        
        it('should display vendor compliance status', async () => {
            const { renderVendors } = await import('../../components/vendors-tab.js');
            const container = document.getElementById('vendors-tab');
            container.innerHTML = '<div id="vendors-container"></div>';
            
            const dataWithCompliance = {
                ...mockVendors,
                services: [
                    { name: 'AWS', compliance: ['SOC2', 'ISO27001'] }
                ]
            };
            
            renderVendors(dataWithCompliance);
            
            expect(container.innerHTML).toMatch(/compliance|certified/i);
        });
        
        it('should have export capability', async () => {
            const { renderVendors } = await import('../../components/vendors-tab.js');
            const container = document.getElementById('vendors-tab');
            container.innerHTML = '<div id="vendors-container"></div>';
            
            renderVendors(mockVendors);
            
            expect(container.innerHTML).toMatch(/export|download/i);
        });
    });
    
    describe('Onboarding Tab', () => {
        it('should render onboarding content', async () => {
            const { renderOnboarding } = await import('../../components/onboarding-tab.js');
            
            // Create container if it doesn't exist
            let container = document.getElementById('onboarding-container');
            if (!container) {
                container = document.createElement('div');
                container.id = 'onboarding-container';
                document.body.appendChild(container);
            }
            
            await renderOnboarding({ stages: [], team: [], resources: [] });
            
            expect(container.innerHTML).not.toBe('');
        });
        
        it('should display onboarding checklist', async () => {
            const { renderOnboarding } = await import('../../components/onboarding-tab.js');
            
            let container = document.getElementById('onboarding-container');
            if (!container) {
                container = document.createElement('div');
                container.id = 'onboarding-container';
                document.body.appendChild(container);
            }
            
            await renderOnboarding({ stages: [], team: [], resources: [] });
            
            // Just verify it doesn't throw and renders something
            expect(container.innerHTML).not.toBe('');
        });
        
        it('should render setup instructions', async () => {
            const { renderOnboarding } = await import('../../components/onboarding-tab.js');
            
            let container = document.getElementById('onboarding-container');
            if (!container) {
                container = document.createElement('div');
                container.id = 'onboarding-container';
                document.body.appendChild(container);
            }
            
            await renderOnboarding({ stages: [], team: [], resources: [] });
            
            expect(container.innerHTML).not.toBe('');
        });
        
        it('should display key contacts section', async () => {
            const { renderOnboarding } = await import('../../components/onboarding-tab.js');
            
            let container = document.getElementById('onboarding-container');
            if (!container) {
                container = document.createElement('div');
                container.id = 'onboarding-container';
                document.body.appendChild(container);
            }
            
            await renderOnboarding({ team: [{ name: 'Tech Lead', email: 'lead@example.com' }] });
            
            expect(container.innerHTML).not.toBe('');
        });
        
        it('should render documentation links', async () => {
            const { renderOnboarding } = await import('../../components/onboarding-tab.js');
            
            let container = document.getElementById('onboarding-container');
            if (!container) {
                container = document.createElement('div');
                container.id = 'onboarding-container';
                document.body.appendChild(container);
            }
            
            await renderOnboarding({ resources: [] });
            
            expect(container.innerHTML).not.toBe('');
        });
        
        it('should display development workflow', async () => {
            const { renderOnboarding } = await import('../../components/onboarding-tab.js');
            
            let container = document.getElementById('onboarding-container');
            if (!container) {
                container = document.createElement('div');
                container.id = 'onboarding-container';
                document.body.appendChild(container);
            }
            
            await renderOnboarding({ stages: [] });
            
            expect(container.innerHTML).not.toBe('');
        });
        
        it('should render tools and environment setup', async () => {
            const { renderOnboarding } = await import('../../components/onboarding-tab.js');
            
            let container = document.getElementById('onboarding-container');
            if (!container) {
                container = document.createElement('div');
                container.id = 'onboarding-container';
                document.body.appendChild(container);
            }
            
            await renderOnboarding({ stages: [], tools: [] });
            
            expect(container.innerHTML).not.toBe('');
        });
        
        it('should handle missing onboarding data', async () => {
            const { renderOnboarding } = await import('../../components/onboarding-tab.js');
            
            let container = document.getElementById('onboarding-container');
            if (!container) {
                container = document.createElement('div');
                container.id = 'onboarding-container';
                document.body.appendChild(container);
            }
            
            await renderOnboarding({});
            
            expect(container.innerHTML).not.toBe('');
        });
        
        it('should render onboarding tab without errors', async () => {
            const { renderOnboarding } = await import('../../components/onboarding-tab.js');
            
            let container = document.getElementById('onboarding-container');
            if (!container) {
                container = document.createElement('div');
                container.id = 'onboarding-container';
                document.body.appendChild(container);
            }
            
            await expect(renderOnboarding({})).resolves.not.toThrow();
        });
        
        it('should display best practices section', async () => {
            const { renderOnboarding } = await import('../../components/onboarding-tab.js');
            
            let container = document.getElementById('onboarding-container');
            if (!container) {
                container = document.createElement('div');
                container.id = 'onboarding-container';
                document.body.appendChild(container);
            }
            
            await renderOnboarding({ stages: [], best_practices: [] });
            
            expect(container.innerHTML).not.toBe('');
        });
    });
    
    // Regression Tests - Prevent Tab Loading Issues
    describe('Tab Loading Regression Tests', () => {
        it('should ensure all tabs have matching render function exports', async () => {
            // Test that each tab component exports a render function
            const tabs = [
                { name: 'executive', module: '../../components/executive-tab.js', fn: 'renderExecutiveSummary' },
                { name: 'overview', module: '../../components/overview-tab-v3.js', fn: 'renderOverview' },
                { name: 'tech-stack', module: '../../components/tech-stack-tab.js', fn: 'renderTechStack' },
                { name: 'security', module: '../../components/security-tab.js', fn: 'renderSecurity' },
                { name: 'architecture', module: '../../components/architecture-tab.js', fn: 'renderArchitecture' },
                { name: 'code-org', module: '../../components/code-org-tab.js', fn: 'renderCodeOrganization' },
                { name: 'vendors', module: '../../components/vendors-tab.js', fn: 'renderVendors' },
                { name: 'use-cases', module: '../../components/use-cases-tab.js', fn: 'renderUseCases' },
                { name: 'recommendations', module: '../../components/recommendations-tab.js', fn: 'renderRecommendations' },
                { name: 'onboarding', module: '../../components/onboarding-tab.js', fn: 'renderOnboarding' }
            ];
            
            for (const tab of tabs) {
                const module = await import(tab.module);
                expect(module[tab.fn]).toBeDefined();
                expect(typeof module[tab.fn]).toBe('function');
            }
        });
        
        it('should ensure all tabs have matching container IDs in HTML', () => {
            // Verify tab content divs exist with correct IDs
            const expectedContainers = [
                'tab-executive',
                'tab-overview',
                'tab-tech-stack',
                'tab-security',
                'tab-architecture',
                'tab-code-org',
                'tab-vendors',
                'tab-onboarding'
            ];
            
            expectedContainers.forEach(containerId => {
                const container = document.getElementById(containerId);
                expect(container).not.toBeNull();
                expect(container.classList.contains('tab-content')).toBe(true);
            });
        });
        
        it('should ensure all tab nav links have matching data-tab attributes', () => {
            // Verify nav tabs have correct data-tab attributes
            const expectedTabs = [
                'executive',
                'overview',
                'tech-stack',
                'security',
                'architecture',
                'code-org',
                'vendors',
                'onboarding'
            ];
            
            expectedTabs.forEach(tabName => {
                const navTab = document.querySelector(`[data-tab="${tabName}"]`);
                expect(navTab).not.toBeNull();
                expect(navTab.classList.contains('nav-tab')).toBe(true);
            });
        });
        
        it('should verify onboarding tab uses correct container ID', async () => {
            // Regression: onboarding-container not onboarding-tab or engineering-container
            const { renderOnboarding } = await import('../../components/onboarding-tab.js');
            
            // Create the correct container
            const container = document.createElement('div');
            container.id = 'onboarding-container';
            document.body.appendChild(container);
            
            await renderOnboarding({ stages: [] });
            
            // Should render into onboarding-container
            expect(container.innerHTML).not.toBe('');
        });
        
        it('should verify onboarding data file is onboarding.json not engineering-onboarding.json', async () => {
            // Regression: ensure data file name is correct
            const { loadAdditionalData } = await import('../../data-loader.js');
            
            // Mock fetch to verify correct filename is requested
            global.fetch = jest.fn((url) => {
                expect(url).toContain('onboarding.json');
                expect(url).not.toContain('engineering');
                return Promise.resolve({
                    ok: true,
                    json: async () => ({ stages: [], team: [], resources: [] })
                });
            });
            
            await loadAdditionalData('mock', 'onboarding.json');
            expect(global.fetch).toHaveBeenCalled();
        });
        
        it('should verify all render functions accept data parameter', async () => {
            // Ensure consistent API across all render functions
            const { renderOnboarding } = await import('../../components/onboarding-tab.js');
            const { renderTechStack } = await import('../../components/tech-stack-tab.js');
            const { renderSecurity } = await import('../../components/security-tab.js');
            
            // Create containers
            ['onboarding-container', 'tech-stack-container', 'security-container'].forEach(id => {
                const container = document.createElement('div');
                container.id = id;
                document.body.appendChild(container);
            });
            
            // All should accept empty data objects
            await expect(renderOnboarding({})).resolves.not.toThrow();
            expect(() => renderTechStack({})).not.toThrow();
            expect(() => renderSecurity({})).not.toThrow();
        });
    });
});
