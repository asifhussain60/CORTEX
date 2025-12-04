/**
 * Integration Tests - All Dashboard Components
 * 
 * Tests rendering of all 7 dashboard tabs with mock data.
 * 
 * Run: npm test tests/integration/components.test.js
 */

import {
    mockHealthData,
    mockTechStack,
    mockSecurity,
    mockArchitecture,
    mockCodeOrganization,
    mockTeamMetrics,
    mockVendors
} from '../fixtures/mock-data.js';

describe('Dashboard Components', () => {
    let components;
    
    beforeAll(async () => {
        // Load all component modules
        components = {
            overview: await import('../../components/overview-tab.js'),
            techStack: await import('../../components/tech-stack-tab.js'),
            security: await import('../../components/security-tab.js'),
            architecture: await import('../../components/architecture-tab.js'),
            codeOrg: await import('../../components/code-org-tab.js'),
            team: await import('../../components/team-tab.js'),
            vendors: await import('../../components/vendors-tab.js')
        };
    });
    
    beforeEach(() => {
        document.body.innerHTML = '<div id="test-container"></div>';
    });
    
    describe('Overview Tab', () => {
        let container;
        
        beforeEach(() => {
            container = document.getElementById('test-container');
        });
        
        it('should render health score', () => {
            components.overview.renderOverview(container, mockHealthData);
            
            expect(container.innerHTML).toContain('87.5');
            expect(container.innerHTML).toContain('health');
        });
        
        it('should render file metrics', () => {
            components.overview.renderOverview(container, mockHealthData);
            
            expect(container.innerHTML).toContain('1,248');
            expect(container.innerHTML).toContain('files');
        });
        
        it('should render lines of code', () => {
            components.overview.renderOverview(container, mockHealthData);
            
            expect(container.innerHTML).toContain('45,892');
            expect(container.innerHTML).toContain('lines');
        });
        
        it('should render test coverage', () => {
            components.overview.renderOverview(container, mockHealthData);
            
            expect(container.innerHTML).toContain('78.3');
            expect(container.innerHTML).toContain('coverage');
        });
        
        it('should render trend indicators', () => {
            components.overview.renderOverview(container, mockHealthData);
            
            const trends = container.querySelectorAll('.trend');
            expect(trends.length).toBeGreaterThan(0);
        });
        
        it('should use glass card styling', () => {
            components.overview.renderOverview(container, mockHealthData);
            
            const cards = container.querySelectorAll('.glass-card');
            expect(cards.length).toBeGreaterThan(0);
        });
    });
    
    describe('Tech Stack Tab', () => {
        let container;
        
        beforeEach(() => {
            container = document.getElementById('test-container');
        });
        
        it('should render language distribution', () => {
            components.techStack.renderTechStack(container, mockTechStack);
            
            expect(container.innerHTML).toContain('Python');
            expect(container.innerHTML).toContain('68.5');
        });
        
        it('should render all languages', () => {
            components.techStack.renderTechStack(container, mockTechStack);
            
            expect(container.innerHTML).toContain('JavaScript');
            expect(container.innerHTML).toContain('TypeScript');
            expect(container.innerHTML).toContain('HTML/CSS');
        });
        
        it('should render frameworks', () => {
            components.techStack.renderTechStack(container, mockTechStack);
            
            expect(container.innerHTML).toContain('FastAPI');
            expect(container.innerHTML).toContain('React');
            expect(container.innerHTML).toContain('pytest');
        });
        
        it('should render framework versions', () => {
            components.techStack.renderTechStack(container, mockTechStack);
            
            expect(container.innerHTML).toContain('0.104.1');
            expect(container.innerHTML).toContain('18.2.0');
        });
        
        it('should render dependency counts', () => {
            components.techStack.renderTechStack(container, mockTechStack);
            
            expect(container.innerHTML).toContain('89');
            expect(container.innerHTML).toContain('dependencies');
        });
        
        it('should create pie chart for languages', () => {
            components.techStack.renderTechStack(container, mockTechStack);
            
            const svg = container.querySelector('svg');
            expect(svg).toBeDefined();
        });
    });
    
    describe('Security Tab', () => {
        let container;
        
        beforeEach(() => {
            container = document.getElementById('test-container');
        });
        
        it('should render security score', () => {
            components.security.renderSecurity(container, mockSecurity);
            
            expect(container.innerHTML).toContain('92.0');
            expect(container.innerHTML).toContain('security');
        });
        
        it('should render vulnerability counts', () => {
            components.security.renderSecurity(container, mockSecurity);
            
            expect(container.innerHTML).toContain('0'); // critical
            expect(container.innerHTML).toContain('2'); // high
            expect(container.innerHTML).toContain('5'); // medium
        });
        
        it('should render vulnerability issues', () => {
            components.security.renderSecurity(container, mockSecurity);
            
            expect(container.innerHTML).toContain('SEC-001');
            expect(container.innerHTML).toContain('Hardcoded API key');
        });
        
        it('should render issue severity badges', () => {
            components.security.renderSecurity(container, mockSecurity);
            
            const highBadges = container.querySelectorAll('.badge-high');
            expect(highBadges.length).toBeGreaterThan(0);
        });
        
        it('should render compliance status', () => {
            components.security.renderSecurity(container, mockSecurity);
            
            expect(container.innerHTML).toContain('OWASP');
            expect(container.innerHTML).toContain('PCI DSS');
            expect(container.innerHTML).toContain('GDPR');
        });
        
        it('should render last scan date', () => {
            components.security.renderSecurity(container, mockSecurity);
            
            expect(container.innerHTML).toContain('Dec 4, 2024');
        });
    });
    
    describe('Architecture Tab', () => {
        let container;
        
        beforeEach(() => {
            container = document.getElementById('test-container');
        });
        
        it('should render module counts', () => {
            components.architecture.renderArchitecture(container, mockArchitecture);
            
            expect(container.innerHTML).toContain('45');
            expect(container.innerHTML).toContain('modules');
        });
        
        it('should render class and function counts', () => {
            components.architecture.renderArchitecture(container, mockArchitecture);
            
            expect(container.innerHTML).toContain('234');
            expect(container.innerHTML).toContain('1,456');
        });
        
        it('should render layer structure', () => {
            components.architecture.renderArchitecture(container, mockArchitecture);
            
            expect(container.innerHTML).toContain('Tier 0');
            expect(container.innerHTML).toContain('Tier 1');
            expect(container.innerHTML).toContain('Tier 2');
            expect(container.innerHTML).toContain('Tier 3');
        });
        
        it('should render complexity metrics', () => {
            components.architecture.renderArchitecture(container, mockArchitecture);
            
            expect(container.innerHTML).toContain('4.2');
            expect(container.innerHTML).toContain('cyclomatic');
        });
        
        it('should create dependency graph', () => {
            components.architecture.renderArchitecture(container, mockArchitecture);
            
            const svg = container.querySelector('svg');
            expect(svg).toBeDefined();
        });
        
        it('should render 3D architecture view', () => {
            components.architecture.renderArchitecture(container, mockArchitecture);
            
            const canvas = container.querySelector('canvas');
            expect(canvas).toBeDefined();
        });
    });
    
    describe('Code Organization Tab', () => {
        let container;
        
        beforeEach(() => {
            container = document.getElementById('test-container');
        });
        
        it('should render directory counts', () => {
            components.codeOrg.renderCodeOrganization(container, mockCodeOrganization);
            
            expect(container.innerHTML).toContain('156');
            expect(container.innerHTML).toContain('directories');
        });
        
        it('should render file statistics', () => {
            components.codeOrg.renderCodeOrganization(container, mockCodeOrganization);
            
            expect(container.innerHTML).toContain('1,248');
            expect(container.innerHTML).toContain('files');
        });
        
        it('should render file size metrics', () => {
            components.codeOrg.renderCodeOrganization(container, mockCodeOrganization);
            
            expect(container.innerHTML).toContain('367'); // average
            expect(container.innerHTML).toContain('2,845'); // largest
        });
        
        it('should render module structure', () => {
            components.codeOrg.renderCodeOrganization(container, mockCodeOrganization);
            
            expect(container.innerHTML).toContain('src/tier0');
            expect(container.innerHTML).toContain('src/tier1');
            expect(container.innerHTML).toContain('src/cortex_agents');
        });
        
        it('should render maintainability index', () => {
            components.codeOrg.renderCodeOrganization(container, mockCodeOrganization);
            
            expect(container.innerHTML).toContain('72.5');
            expect(container.innerHTML).toContain('maintainability');
        });
        
        it('should create treemap visualization', () => {
            components.codeOrg.renderCodeOrganization(container, mockCodeOrganization);
            
            const svg = container.querySelector('svg');
            expect(svg).toBeDefined();
        });
    });
    
    describe('Team Metrics Tab', () => {
        let container;
        
        beforeEach(() => {
            container = document.getElementById('test-container');
        });
        
        it('should render contributor counts', () => {
            components.team.renderTeamMetrics(container, mockTeamMetrics);
            
            expect(container.innerHTML).toContain('12');
            expect(container.innerHTML).toContain('contributors');
        });
        
        it('should render commit statistics', () => {
            components.team.renderTeamMetrics(container, mockTeamMetrics);
            
            expect(container.innerHTML).toContain('2,456');
            expect(container.innerHTML).toContain('commits');
        });
        
        it('should render contributor list', () => {
            components.team.renderTeamMetrics(container, mockTeamMetrics);
            
            expect(container.innerHTML).toContain('Asif Hussain');
            expect(container.innerHTML).toContain('Developer B');
        });
        
        it('should render contributor metrics', () => {
            components.team.renderTeamMetrics(container, mockTeamMetrics);
            
            expect(container.innerHTML).toContain('1,456'); // commits
            expect(container.innerHTML).toContain('89,234'); // additions
        });
        
        it('should create activity timeline chart', () => {
            components.team.renderTeamMetrics(container, mockTeamMetrics);
            
            const canvas = container.querySelector('canvas');
            expect(canvas).toBeDefined();
        });
        
        it('should render recent activity', () => {
            components.team.renderTeamMetrics(container, mockTeamMetrics);
            
            expect(container.innerHTML).toContain('Dec 1');
            expect(container.innerHTML).toContain('Dec 4');
        });
    });
    
    describe('Vendors Tab', () => {
        let container;
        
        beforeEach(() => {
            container = document.getElementById('test-container');
        });
        
        it('should render vendor counts', () => {
            components.vendors.renderVendors(container, mockVendors);
            
            expect(container.innerHTML).toContain('45');
            expect(container.innerHTML).toContain('vendors');
        });
        
        it('should render category breakdown', () => {
            components.vendors.renderVendors(container, mockVendors);
            
            expect(container.innerHTML).toContain('Cloud Services');
            expect(container.innerHTML).toContain('Development Tools');
            expect(container.innerHTML).toContain('Security');
        });
        
        it('should render vendor list', () => {
            components.vendors.renderVendors(container, mockVendors);
            
            expect(container.innerHTML).toContain('GitHub');
            expect(container.innerHTML).toContain('AWS');
        });
        
        it('should render cost information', () => {
            components.vendors.renderVendors(container, mockVendors);
            
            expect(container.innerHTML).toContain('8,945');
            expect(container.innerHTML).toContain('monthly');
        });
        
        it('should render vendor status', () => {
            components.vendors.renderVendors(container, mockVendors);
            
            const activeBadges = container.querySelectorAll('.badge-active');
            expect(activeBadges.length).toBeGreaterThan(0);
        });
        
        it('should create cost breakdown chart', () => {
            components.vendors.renderVendors(container, mockVendors);
            
            const canvas = container.querySelector('canvas');
            expect(canvas).toBeDefined();
        });
    });
});
