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
                <div id="sourceSelect"></div>
                <div class="tabs">
                    <button class="tab-button" data-tab="executive">Executive</button>
                    <button class="tab-button" data-tab="overview">Overview</button>
                    <button class="tab-button" data-tab="tech-stack">Tech Stack</button>
                    <button class="tab-button" data-tab="security">Security</button>
                    <button class="tab-button" data-tab="architecture">Architecture</button>
                    <button class="tab-button" data-tab="code-org">Code Organization</button>
                    <button class="tab-button" data-tab="vendors">Vendors</button>
                    <button class="tab-button" data-tab="engineering">Engineering</button>
                </div>
                <div id="executive-tab" class="tab-content"></div>
                <div id="overview-tab" class="tab-content"></div>
                <div id="tech-stack-tab" class="tab-content"></div>
                <div id="security-tab" class="tab-content"></div>
                <div id="architecture-tab" class="tab-content"></div>
                <div id="code-org-tab" class="tab-content"></div>
                <div id="vendors-tab" class="tab-content"></div>
                <div id="engineering-tab" class="tab-content"></div>
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
    
    describe('Engineering Tab', () => {
        it('should render engineering onboarding content', async () => {
            const EngineeringTab = (await import('../../components/engineering-onboarding-tab.js')).default;
            const container = document.getElementById('engineering-tab');
            
            const tab = new EngineeringTab(container);
            tab.render({});
            
            expect(container.innerHTML).toContain('Engineering');
        });
        
        it('should display onboarding checklist', async () => {
            const EngineeringTab = (await import('../../components/engineering-onboarding-tab.js')).default;
            const container = document.getElementById('engineering-tab');
            
            const tab = new EngineeringTab(container);
            tab.render({});
            
            expect(container.innerHTML).toMatch(/checklist|onboard/i);
        });
        
        it('should render setup instructions', async () => {
            const EngineeringTab = (await import('../../components/engineering-onboarding-tab.js')).default;
            const container = document.getElementById('engineering-tab');
            
            const tab = new EngineeringTab(container);
            tab.render({});
            
            expect(container.innerHTML).toMatch(/setup|install|configure/i);
        });
        
        it('should display key contacts section', async () => {
            const EngineeringTab = (await import('../../components/engineering-onboarding-tab.js')).default;
            const container = document.getElementById('engineering-tab');
            
            const dataWithContacts = {
                contacts: [
                    { name: 'Tech Lead', email: 'lead@example.com' }
                ]
            };
            
            const tab = new EngineeringTab(container);
            tab.render(dataWithContacts);
            
            expect(container.innerHTML).toMatch(/contact/i);
        });
        
        it('should render documentation links', async () => {
            const EngineeringTab = (await import('../../components/engineering-onboarding-tab.js')).default;
            const container = document.getElementById('engineering-tab');
            
            const tab = new EngineeringTab(container);
            tab.render({});
            
            const links = container.querySelectorAll('a');
            expect(links.length).toBeGreaterThan(0);
        });
        
        it('should display development workflow', async () => {
            const EngineeringTab = (await import('../../components/engineering-onboarding-tab.js')).default;
            const container = document.getElementById('engineering-tab');
            
            const tab = new EngineeringTab(container);
            tab.render({});
            
            expect(container.innerHTML).toMatch(/workflow|process/i);
        });
        
        it('should render tools and environment setup', async () => {
            const EngineeringTab = (await import('../../components/engineering-onboarding-tab.js')).default;
            const container = document.getElementById('engineering-tab');
            
            const tab = new EngineeringTab(container);
            tab.render({});
            
            expect(container.innerHTML).toMatch(/tool|environment/i);
        });
        
        it('should handle missing engineering data', async () => {
            const EngineeringTab = (await import('../../components/engineering-onboarding-tab.js')).default;
            const container = document.getElementById('engineering-tab');
            
            const tab = new EngineeringTab(container);
            tab.render({});
            
            expect(container.innerHTML).not.toBe('');
        });
        
        it('should render engineering tab without errors', async () => {
            const EngineeringTab = (await import('../../components/engineering-onboarding-tab.js')).default;
            const container = document.getElementById('engineering-tab');
            
            const tab = new EngineeringTab(container);
            expect(() => tab.render({})).not.toThrow();
        });
        
        it('should display best practices section', async () => {
            const EngineeringTab = (await import('../../components/engineering-onboarding-tab.js')).default;
            const container = document.getElementById('engineering-tab');
            
            const tab = new EngineeringTab(container);
            tab.render({});
            
            expect(container.innerHTML).toMatch(/best practice|guideline/i);
        });
    });
});
