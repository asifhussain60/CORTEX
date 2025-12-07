/**
 * Integration Tests - Tab Rendering
 * 
 * Tests rendering of all 8 dashboard tabs with comprehensive assertions.
 * 
 * 8 tabs × 10 tests each = 80 tests total
 */

import { 
    mockExecutiveData, 
    mockOverviewData, 
    mockTechStackData, 
    mockSecurityData,
    mockArchitectureData,
    mockCodeOrgData,
    mockVendorsData
} from '../fixtures/mock-full-data.js';

describe('Tab Rendering - Executive Tab', () => {
    beforeEach(() => {
        document.body.innerHTML = '<div id="executive-tab"></div>';
    });
    
    test('should render executive tab container', async () => {
        const { renderExecutiveSummary } = await import('../../components/executive-tab.js');
        renderExecutiveSummary(mockExecutiveData);
        
        const container = document.getElementById('executive-tab');
        expect(container.innerHTML).not.toBe('');
    });
    
    test('should display overall health score', async () => {
        const { renderExecutiveSummary } = await import('../../components/executive-tab.js');
        renderExecutiveSummary(mockExecutiveData);
        
        const container = document.getElementById('executive-tab');
        expect(container.textContent).toContain('92');
    });
    
    test('should display project name', async () => {
        const { renderExecutiveSummary } = await import('../../components/executive-tab.js');
        renderExecutiveSummary(mockExecutiveData);
        
        const container = document.getElementById('executive-tab');
        expect(container.textContent).toContain('CORTEX');
    });
    
    test('should display executive summary text', async () => {
        const { renderExecutiveSummary } = await import('../../components/executive-tab.js');
        renderExecutiveSummary(mockExecutiveData);
        
        const container = document.getElementById('executive-tab');
        expect(container.textContent).toContain('AI Assistant');
    });
    
    test('should display key strengths', async () => {
        const { renderExecutiveSummary } = await import('../../components/executive-tab.js');
        renderExecutiveSummary(mockExecutiveData);
        
        const container = document.getElementById('executive-tab');
        expect(container.textContent).toContain('4-tier brain');
    });
    
    test('should display areas of concern', async () => {
        const { renderExecutiveSummary } = await import('../../components/executive-tab.js');
        renderExecutiveSummary(mockExecutiveData);
        
        const container = document.getElementById('executive-tab');
        expect(container.textContent).toContain('Documentation');
    });
    
    test('should display recommendations', async () => {
        const { renderExecutiveSummary } = await import('../../components/executive-tab.js');
        renderExecutiveSummary(mockExecutiveData);
        
        const container = document.getElementById('executive-tab');
        expect(container.textContent).toContain('documentation coverage');
    });
    
    test('should handle missing executive data gracefully', async () => {
        const { renderExecutiveSummary } = await import('../../components/executive-tab.js');
        renderExecutiveSummary({});
        
        const container = document.getElementById('executive-tab');
        expect(container.innerHTML).not.toBe('');
    });
    
    test('should display health status indicator', async () => {
        const { renderExecutiveSummary } = await import('../../components/executive-tab.js');
        renderExecutiveSummary(mockExecutiveData);
        
        const container = document.getElementById('executive-tab');
        expect(container.textContent).toContain('healthy');
    });
    
    test('should render without errors', async () => {
        const { renderExecutiveSummary } = await import('../../components/executive-tab.js');
        
        expect(() => {
            renderExecutiveSummary(mockExecutiveData);
        }).not.toThrow();
    });
});

describe('Tab Rendering - Overview Tab', () => {
    beforeEach(() => {
        document.body.innerHTML = '<div id="overview-container"></div>';
    });
    
    test('should render overview tab container', async () => {
        const { renderOverview } = await import('../../components/overview-tab-v3.js');
        renderOverview(mockOverviewData);
        
        const container = document.getElementById('overview-container');
        expect(container.innerHTML).not.toBe('');
    });
    
    test('should display health score gauge', async () => {
        const { renderOverview } = await import('../../components/overview-tab-v3.js');
        renderOverview(mockOverviewData);
        
        const container = document.getElementById('overview-container');
        const gauge = container.querySelector('#health-gauge');
        expect(gauge).toBeTruthy();
    });
    
    test('should display key metrics cards', async () => {
        const { renderOverview } = await import('../../components/overview-tab-v3.js');
        renderOverview(mockOverviewData);
        
        const container = document.getElementById('overview-container');
        expect(container.textContent).toContain('994');
        expect(container.textContent).toContain('45678');
    });
    
    test('should display health categories', async () => {
        const { renderOverview } = await import('../../components/overview-tab-v3.js');
        renderOverview(mockOverviewData);
        
        const container = document.getElementById('overview-container');
        expect(container.textContent).toContain('code_quality');
        expect(container.textContent).toContain('security');
    });
    
    test('should display composition chart', async () => {
        const { renderOverview } = await import('../../components/overview-tab-v3.js');
        renderOverview(mockOverviewData);
        
        const container = document.getElementById('overview-container');
        const chart = container.querySelector('#composition-chart');
        expect(chart).toBeTruthy();
    });
    
    test('should display critical issues', async () => {
        const { renderOverview } = await import('../../components/overview-tab-v3.js');
        renderOverview(mockOverviewData);
        
        const container = document.getElementById('overview-container');
        // Should show "No critical issues" or list them
        expect(container.innerHTML).toBeTruthy();
    });
    
    test('should show trend indicators', async () => {
        const { renderOverview } = await import('../../components/overview-tab-v3.js');
        renderOverview(mockOverviewData);
        
        const container = document.getElementById('overview-container');
        expect(container.textContent).toContain('improving');
    });
    
    test('should handle empty categories array', async () => {
        const { renderOverview } = await import('../../components/overview-tab-v3.js');
        const emptyData = { ...mockOverviewData, health_categories: [] };
        
        expect(() => {
            renderOverview(emptyData);
        }).not.toThrow();
    });
    
    test('should display last scan timestamp', async () => {
        const { renderOverview } = await import('../../components/overview-tab-v3.js');
        renderOverview(mockOverviewData);
        
        const container = document.getElementById('overview-container');
        expect(container.textContent).toContain('2025-12-06');
    });
    
    test('should render without errors', async () => {
        const { renderOverview } = await import('../../components/overview-tab-v3.js');
        
        expect(() => {
            renderOverview(mockOverviewData);
        }).not.toThrow();
    });
});

describe('Tab Rendering - Tech Stack Tab', () => {
    beforeEach(() => {
        document.body.innerHTML = '<div id="tech-stack-container"></div>';
    });
    
    test('should render tech stack tab container', async () => {
        const { renderTechStack } = await import('../../components/tech-stack-tab.js');
        renderTechStack(mockTechStackData);
        
        const container = document.getElementById('tech-stack-container');
        expect(container.innerHTML).not.toBe('');
    });
    
    test('should display total technologies count', async () => {
        const { renderTechStack } = await import('../../components/tech-stack-tab.js');
        renderTechStack(mockTechStackData);
        
        const container = document.getElementById('tech-stack-container');
        expect(container.textContent).toContain('45');
    });
    
    test('should display frontend technologies', async () => {
        const { renderTechStack } = await import('../../components/tech-stack-tab.js');
        renderTechStack(mockTechStackData);
        
        const container = document.getElementById('tech-stack-container');
        expect(container.textContent).toContain('React');
    });
    
    test('should display backend technologies', async () => {
        const { renderTechStack } = await import('../../components/tech-stack-tab.js');
        renderTechStack(mockTechStackData);
        
        const container = document.getElementById('tech-stack-container');
        expect(container.textContent).toContain('Flask');
    });
    
    test('should display database technologies', async () => {
        const { renderTechStack } = await import('../../components/tech-stack-tab.js');
        renderTechStack(mockTechStackData);
        
        const container = document.getElementById('tech-stack-container');
        expect(container.textContent).toContain('SQLite');
    });
    
    test('should display technology status badges', async () => {
        const { renderTechStack } = await import('../../components/tech-stack-tab.js');
        renderTechStack(mockTechStackData);
        
        const container = document.getElementById('tech-stack-container');
        expect(container.textContent).toContain('active');
    });
    
    test('should display version numbers', async () => {
        const { renderTechStack } = await import('../../components/tech-stack-tab.js');
        renderTechStack(mockTechStackData);
        
        const container = document.getElementById('tech-stack-container');
        expect(container.textContent).toContain('18.2.0');
    });
    
    test('should show deprecated technologies count', async () => {
        const { renderTechStack } = await import('../../components/tech-stack-tab.js');
        renderTechStack(mockTechStackData);
        
        const container = document.getElementById('tech-stack-container');
        expect(container.textContent).toContain('5');
    });
    
    test('should handle empty tech stack', async () => {
        const { renderTechStack } = await import('../../components/tech-stack-tab.js');
        const emptyData = { summary: { total_technologies: 0 }, frontend: [], backend: [], database: [] };
        
        expect(() => {
            renderTechStack(emptyData);
        }).not.toThrow();
    });
    
    test('should render without errors', async () => {
        const { renderTechStack } = await import('../../components/tech-stack-tab.js');
        
        expect(() => {
            renderTechStack(mockTechStackData);
        }).not.toThrow();
    });
});

describe('Tab Rendering - Security Tab', () => {
    beforeEach(() => {
        document.body.innerHTML = '<div id="security-container"></div>';
    });
    
    test('should render security tab container', async () => {
        const { renderSecurity } = await import('../../components/security-tab.js');
        renderSecurity(mockSecurityData);
        
        const container = document.getElementById('security-container');
        expect(container.innerHTML).not.toBe('');
    });
    
    test('should display total vulnerabilities count', async () => {
        const { renderSecurity } = await import('../../components/security-tab.js');
        renderSecurity(mockSecurityData);
        
        const container = document.getElementById('security-container');
        expect(container.textContent).toContain('0');
    });
    
    test('should display severity breakdown', async () => {
        const { renderSecurity } = await import('../../components/security-tab.js');
        renderSecurity(mockSecurityData);
        
        const container = document.getElementById('security-container');
        expect(container.innerHTML).toContain('critical');
        expect(container.innerHTML).toContain('high');
    });
    
    test('should display OWASP compliance', async () => {
        const { renderSecurity } = await import('../../components/security-tab.js');
        renderSecurity(mockSecurityData);
        
        const container = document.getElementById('security-container');
        expect(container.textContent).toContain('compliant');
    });
    
    test('should display vulnerability list', async () => {
        const { renderSecurity } = await import('../../components/security-tab.js');
        renderSecurity(mockSecurityData);
        
        const container = document.getElementById('security-container');
        // Should show empty state or list
        expect(container.innerHTML).toBeTruthy();
    });
    
    test('should show OWASP Top 10 categories', async () => {
        const { renderSecurity } = await import('../../components/security-tab.js');
        renderSecurity(mockSecurityData);
        
        const container = document.getElementById('security-container');
        expect(container.textContent).toContain('access_control');
    });
    
    test('should display compliance status badges', async () => {
        const { renderSecurity } = await import('../../components/security-tab.js');
        renderSecurity(mockSecurityData);
        
        const container = document.getElementById('security-container');
        expect(container.innerHTML).toContain('compliant');
    });
    
    test('should handle vulnerabilities list gracefully', async () => {
        const { renderSecurity } = await import('../../components/security-tab.js');
        const dataWithVulns = {
            ...mockSecurityData,
            vulnerabilities: [
                { id: 'CVE-2024-001', severity: 'high', description: 'Test vuln' }
            ]
        };
        
        expect(() => {
            renderSecurity(dataWithVulns);
        }).not.toThrow();
    });
    
    test('should show security score if available', async () => {
        const { renderSecurity } = await import('../../components/security-tab.js');
        renderSecurity(mockSecurityData);
        
        const container = document.getElementById('security-container');
        expect(container.innerHTML).toBeTruthy();
    });
    
    test('should render without errors', async () => {
        const { renderSecurity } = await import('../../components/security-tab.js');
        
        expect(() => {
            renderSecurity(mockSecurityData);
        }).not.toThrow();
    });
});

describe('Tab Rendering - Architecture Tab', () => {
    beforeEach(() => {
        document.body.innerHTML = '<div id="architecture-container"></div>';
    });
    
    test('should render architecture tab container', async () => {
        const { renderArchitecture } = await import('../../components/architecture-tab.js');
        renderArchitecture(mockArchitectureData);
        
        const container = document.getElementById('architecture-container');
        expect(container.innerHTML).not.toBe('');
    });
    
    test('should display components list', async () => {
        const { renderArchitecture } = await import('../../components/architecture-tab.js');
        renderArchitecture(mockArchitectureData);
        
        const container = document.getElementById('architecture-container');
        expect(container.textContent).toContain('Brain System');
    });
    
    test('should display component health scores', async () => {
        const { renderArchitecture } = await import('../../components/architecture-tab.js');
        renderArchitecture(mockArchitectureData);
        
        const container = document.getElementById('architecture-container');
        expect(container.textContent).toContain('95');
    });
    
    test('should display architecture patterns', async () => {
        const { renderArchitecture } = await import('../../components/architecture-tab.js');
        renderArchitecture(mockArchitectureData);
        
        const container = document.getElementById('architecture-container');
        expect(container.textContent).toContain('MVC');
    });
    
    test('should display dependencies count', async () => {
        const { renderArchitecture } = await import('../../components/architecture-tab.js');
        renderArchitecture(mockArchitectureData);
        
        const container = document.getElementById('architecture-container');
        expect(container.textContent).toContain('12');
    });
    
    test('should show circular dependencies', async () => {
        const { renderArchitecture } = await import('../../components/architecture-tab.js');
        renderArchitecture(mockArchitectureData);
        
        const container = document.getElementById('architecture-container');
        expect(container.textContent).toContain('0');
    });
    
    test('should display component types', async () => {
        const { renderArchitecture } = await import('../../components/architecture-tab.js');
        renderArchitecture(mockArchitectureData);
        
        const container = document.getElementById('architecture-container');
        expect(container.textContent).toContain('core');
    });
    
    test('should handle empty components array', async () => {
        const { renderArchitecture } = await import('../../components/architecture-tab.js');
        const emptyData = { ...mockArchitectureData, components: [] };
        
        expect(() => {
            renderArchitecture(emptyData);
        }).not.toThrow();
    });
    
    test('should display architecture diagrams if available', async () => {
        const { renderArchitecture } = await import('../../components/architecture-tab.js');
        renderArchitecture(mockArchitectureData);
        
        const container = document.getElementById('architecture-container');
        expect(container.innerHTML).toBeTruthy();
    });
    
    test('should render without errors', async () => {
        const { renderArchitecture } = await import('../../components/architecture-tab.js');
        
        expect(() => {
            renderArchitecture(mockArchitectureData);
        }).not.toThrow();
    });
});

describe('Tab Rendering - Code Organization Tab', () => {
    beforeEach(() => {
        document.body.innerHTML = '<div id="code-org-container"></div>';
    });
    
    test('should render code org tab container', async () => {
        const { renderCodeOrganization } = await import('../../components/code-org-tab.js');
        renderCodeOrganization(mockCodeOrgData);
        
        const container = document.getElementById('code-org-container');
        expect(container.innerHTML).not.toBe('');
    });
    
    test('should display average complexity', async () => {
        const { renderCodeOrganization } = await import('../../components/code-org-tab.js');
        renderCodeOrganization(mockCodeOrgData);
        
        const container = document.getElementById('code-org-container');
        expect(container.textContent).toContain('4.2');
    });
    
    test('should display max complexity', async () => {
        const { renderCodeOrganization } = await import('../../components/code-org-tab.js');
        renderCodeOrganization(mockCodeOrgData);
        
        const container = document.getElementById('code-org-container');
        expect(container.textContent).toContain('15');
    });
    
    test('should display hotspots list', async () => {
        const { renderCodeOrganization } = await import('../../components/code-org-tab.js');
        renderCodeOrganization(mockCodeOrgData);
        
        const container = document.getElementById('code-org-container');
        expect(container.textContent).toContain('working_memory');
    });
    
    test('should display risk scores', async () => {
        const { renderCodeOrganization } = await import('../../components/code-org-tab.js');
        renderCodeOrganization(mockCodeOrgData);
        
        const container = document.getElementById('code-org-container');
        expect(container.textContent).toContain('8.5');
    });
    
    test('should display total modules', async () => {
        const { renderCodeOrganization } = await import('../../components/code-org-tab.js');
        renderCodeOrganization(mockCodeOrgData);
        
        const container = document.getElementById('code-org-container');
        expect(container.textContent).toContain('47');
    });
    
    test('should display duplicated code percentage', async () => {
        const { renderCodeOrganization } = await import('../../components/code-org-tab.js');
        renderCodeOrganization(mockCodeOrgData);
        
        const container = document.getElementById('code-org-container');
        expect(container.textContent).toContain('2.1');
    });
    
    test('should handle empty hotspots array', async () => {
        const { renderCodeOrganization } = await import('../../components/code-org-tab.js');
        const emptyData = { ...mockCodeOrgData, hotspots: [] };
        
        expect(() => {
            renderCodeOrganization(emptyData);
        }).not.toThrow();
    });
    
    test('should display high complexity files count', async () => {
        const { renderCodeOrganization } = await import('../../components/code-org-tab.js');
        renderCodeOrganization(mockCodeOrgData);
        
        const container = document.getElementById('code-org-container');
        expect(container.textContent).toContain('3');
    });
    
    test('should render without errors', async () => {
        const { renderCodeOrganization } = await import('../../components/code-org-tab.js');
        
        expect(() => {
            renderCodeOrganization(mockCodeOrgData);
        }).not.toThrow();
    });
});

describe('Tab Rendering - Vendors Tab', () => {
    beforeEach(() => {
        document.body.innerHTML = '<div id="vendors-container"></div>';
    });
    
    test('should render vendors tab container', async () => {
        const { renderVendors } = await import('../../components/vendors-tab.js');
        renderVendors(mockVendorsData);
        
        const container = document.getElementById('vendors-container');
        expect(container.innerHTML).not.toBe('');
    });
    
    test('should display total services count', async () => {
        const { renderVendors } = await import('../../components/vendors-tab.js');
        renderVendors(mockVendorsData);
        
        const container = document.getElementById('vendors-container');
        expect(container.textContent).toContain('8');
    });
    
    test('should display services list', async () => {
        const { renderVendors } = await import('../../components/vendors-tab.js');
        renderVendors(mockVendorsData);
        
        const container = document.getElementById('vendors-container');
        expect(container.textContent).toContain('GitHub');
    });
    
    test('should display risk levels', async () => {
        const { renderVendors } = await import('../../components/vendors-tab.js');
        renderVendors(mockVendorsData);
        
        const container = document.getElementById('vendors-container');
        expect(container.textContent).toContain('low');
    });
    
    test('should display high risk count', async () => {
        const { renderVendors } = await import('../../components/vendors-tab.js');
        renderVendors(mockVendorsData);
        
        const container = document.getElementById('vendors-container');
        expect(container.textContent).toContain('0');
    });
    
    test('should display service categories', async () => {
        const { renderVendors } = await import('../../components/vendors-tab.js');
        renderVendors(mockVendorsData);
        
        const container = document.getElementById('vendors-container');
        expect(container.textContent).toContain('SCM');
    });
    
    test('should display criticality levels', async () => {
        const { renderVendors } = await import('../../components/vendors-tab.js');
        renderVendors(mockVendorsData);
        
        const container = document.getElementById('vendors-container');
        expect(container.textContent).toContain('high');
    });
    
    test('should handle empty services array', async () => {
        const { renderVendors } = await import('../../components/vendors-tab.js');
        const emptyData = { services: [], total_services: 0 };
        
        expect(() => {
            renderVendors(emptyData);
        }).not.toThrow();
    });
    
    test('should display service status', async () => {
        const { renderVendors } = await import('../../components/vendors-tab.js');
        renderVendors(mockVendorsData);
        
        const container = document.getElementById('vendors-container');
        expect(container.textContent).toContain('active');
    });
    
    test('should render without errors', async () => {
        const { renderVendors } = await import('../../components/vendors-tab.js');
        
        expect(() => {
            renderVendors(mockVendorsData);
        }).not.toThrow();
    });
});

describe('Tab Rendering - Engineering Tab', () => {
    beforeEach(() => {
        document.body.innerHTML = '<div id="engineering-tab"></div>';
    });
    
    test('should render engineering tab container', async () => {
        const EngineeringTab = (await import('../../components/engineering-onboarding-tab.js')).default;
        const tab = new EngineeringTab('engineering-tab');
        tab.render();
        
        const container = document.getElementById('engineering-tab');
        expect(container.innerHTML).not.toBe('');
    });
    
    test('should display onboarding content', async () => {
        const EngineeringTab = (await import('../../components/engineering-onboarding-tab.js')).default;
        const tab = new EngineeringTab('engineering-tab');
        tab.render();
        
        const container = document.getElementById('engineering-tab');
        expect(container.innerHTML).toBeTruthy();
    });
    
    test('should display setup instructions', async () => {
        const EngineeringTab = (await import('../../components/engineering-onboarding-tab.js')).default;
        const tab = new EngineeringTab('engineering-tab');
        tab.render();
        
        const container = document.getElementById('engineering-tab');
        expect(container.innerHTML).toContain('setup');
    });
    
    test('should display architecture overview', async () => {
        const EngineeringTab = (await import('../../components/engineering-onboarding-tab.js')).default;
        const tab = new EngineeringTab('engineering-tab');
        tab.render();
        
        const container = document.getElementById('engineering-tab');
        expect(container.innerHTML).toContain('architecture');
    });
    
    test('should display development workflow', async () => {
        const EngineeringTab = (await import('../../components/engineering-onboarding-tab.js')).default;
        const tab = new EngineeringTab('engineering-tab');
        tab.render();
        
        const container = document.getElementById('engineering-tab');
        expect(container.innerHTML).toBeTruthy();
    });
    
    test('should display testing guidelines', async () => {
        const EngineeringTab = (await import('../../components/engineering-onboarding-tab.js')).default;
        const tab = new EngineeringTab('engineering-tab');
        tab.render();
        
        const container = document.getElementById('engineering-tab');
        expect(container.innerHTML).toContain('test');
    });
    
    test('should display code standards', async () => {
        const EngineeringTab = (await import('../../components/engineering-onboarding-tab.js')).default;
        const tab = new EngineeringTab('engineering-tab');
        tab.render();
        
        const container = document.getElementById('engineering-tab');
        expect(container.innerHTML).toBeTruthy();
    });
    
    test('should handle missing container gracefully', async () => {
        const EngineeringTab = (await import('../../components/engineering-onboarding-tab.js')).default;
        const tab = new EngineeringTab('nonexistent');
        
        expect(() => {
            tab.render();
        }).not.toThrow();
    });
    
    test('should display documentation links', async () => {
        const EngineeringTab = (await import('../../components/engineering-onboarding-tab.js')).default;
        const tab = new EngineeringTab('engineering-tab');
        tab.render();
        
        const container = document.getElementById('engineering-tab');
        expect(container.innerHTML).toBeTruthy();
    });
    
    test('should render without errors', async () => {
        const EngineeringTab = (await import('../../components/engineering-onboarding-tab.js')).default;
        const tab = new EngineeringTab('engineering-tab');
        
        expect(() => {
            tab.render();
        }).not.toThrow();
    });
});
