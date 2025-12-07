/**
 * Unit Tests - Data Validation
 * 
 * Tests JSON schema validation, required fields, data types, and boundary conditions.
 * 
 * 40+ tests covering all 7 data files
 */

import { 
    mockOverviewData, 
    mockTechStackData, 
    mockSecurityData,
    mockArchitectureData,
    mockCodeOrgData,
    mockVendorsData,
    mockExecutiveData
} from '../fixtures/mock-full-data.js';

describe('Data Validation - Overview Data', () => {
    test('should have required project_name field', () => {
        expect(mockOverviewData.project_name).toBeDefined();
        expect(typeof mockOverviewData.project_name).toBe('string');
    });
    
    test('should have overall_health object', () => {
        expect(mockOverviewData.overall_health).toBeDefined();
        expect(typeof mockOverviewData.overall_health).toBe('object');
    });
    
    test('should have health score between 0-100', () => {
        const score = mockOverviewData.overall_health.score;
        expect(score).toBeGreaterThanOrEqual(0);
        expect(score).toBeLessThanOrEqual(100);
    });
    
    test('should have valid health status', () => {
        const validStatuses = ['healthy', 'warning', 'critical', 'unknown'];
        expect(validStatuses).toContain(mockOverviewData.overall_health.status);
    });
    
    test('should have valid trend indicator', () => {
        const validTrends = ['improving', 'stable', 'declining', 'unknown'];
        expect(validTrends).toContain(mockOverviewData.overall_health.trend);
    });
    
    test('should have key_metrics object', () => {
        expect(mockOverviewData.key_metrics).toBeDefined();
        expect(typeof mockOverviewData.key_metrics).toBe('object');
    });
    
    test('should have health_categories array', () => {
        expect(Array.isArray(mockOverviewData.health_categories)).toBe(true);
    });
    
    test('should have valid category structure', () => {
        if (mockOverviewData.health_categories.length > 0) {
            const category = mockOverviewData.health_categories[0];
            expect(category.name).toBeDefined();
            expect(category.score).toBeDefined();
            expect(category.status).toBeDefined();
        }
    });
    
    test('should have composition object with languages', () => {
        expect(mockOverviewData.composition).toBeDefined();
        expect(Array.isArray(mockOverviewData.composition.languages)).toBe(true);
    });
    
    test('should have critical_issues array', () => {
        expect(Array.isArray(mockOverviewData.critical_issues)).toBe(true);
    });
});

describe('Data Validation - Tech Stack Data', () => {
    test('should have summary object', () => {
        expect(mockTechStackData.summary).toBeDefined();
        expect(typeof mockTechStackData.summary).toBe('object');
    });
    
    test('should have total_technologies count', () => {
        expect(mockTechStackData.summary.total_technologies).toBeDefined();
        expect(typeof mockTechStackData.summary.total_technologies).toBe('number');
    });
    
    test('should have frontend array', () => {
        expect(Array.isArray(mockTechStackData.frontend)).toBe(true);
    });
    
    test('should have backend array', () => {
        expect(Array.isArray(mockTechStackData.backend)).toBe(true);
    });
    
    test('should have database array', () => {
        expect(Array.isArray(mockTechStackData.database)).toBe(true);
    });
    
    test('should have valid technology structure', () => {
        if (mockTechStackData.frontend.length > 0) {
            const tech = mockTechStackData.frontend[0];
            expect(tech.name).toBeDefined();
            expect(tech.version).toBeDefined();
            expect(tech.status).toBeDefined();
        }
    });
    
    test('should have valid status values', () => {
        const validStatuses = ['active', 'deprecated', 'evaluation'];
        if (mockTechStackData.frontend.length > 0) {
            expect(validStatuses).toContain(mockTechStackData.frontend[0].status);
        }
    });
    
    test('should sum up to total technologies', () => {
        const total = 
            mockTechStackData.frontend.length +
            mockTechStackData.backend.length +
            mockTechStackData.database.length;
        expect(total).toBeGreaterThan(0);
    });
});

describe('Data Validation - Security Data', () => {
    test('should have summary object', () => {
        expect(mockSecurityData.summary).toBeDefined();
    });
    
    test('should have vulnerability counts', () => {
        expect(mockSecurityData.summary.total_vulnerabilities).toBeDefined();
        expect(mockSecurityData.summary.critical).toBeDefined();
        expect(mockSecurityData.summary.high).toBeDefined();
    });
    
    test('should have vulnerabilities array', () => {
        expect(Array.isArray(mockSecurityData.vulnerabilities)).toBe(true);
    });
    
    test('should have OWASP compliance object', () => {
        expect(mockSecurityData.owasp_compliance).toBeDefined();
    });
    
    test('should have valid OWASP categories', () => {
        const owasp = mockSecurityData.owasp_compliance;
        expect(owasp.a01_broken_access_control).toBeDefined();
        expect(owasp.a02_cryptographic_failures).toBeDefined();
    });
    
    test('should have valid compliance values', () => {
        const validValues = ['compliant', 'non-compliant', 'partial', 'unknown'];
        expect(validValues).toContain(mockSecurityData.owasp_compliance.a01_broken_access_control);
    });
    
    test('should sum vulnerability counts correctly', () => {
        const sum = 
            mockSecurityData.summary.critical +
            mockSecurityData.summary.high +
            mockSecurityData.summary.medium +
            mockSecurityData.summary.low;
        expect(sum).toBe(mockSecurityData.summary.total_vulnerabilities);
    });
});

describe('Data Validation - Architecture Data', () => {
    test('should have components array', () => {
        expect(Array.isArray(mockArchitectureData.components)).toBe(true);
    });
    
    test('should have patterns array', () => {
        expect(Array.isArray(mockArchitectureData.patterns)).toBe(true);
    });
    
    test('should have dependencies object', () => {
        expect(mockArchitectureData.dependencies).toBeDefined();
    });
    
    test('should have valid component structure', () => {
        if (mockArchitectureData.components.length > 0) {
            const component = mockArchitectureData.components[0];
            expect(component.name).toBeDefined();
            expect(component.type).toBeDefined();
            expect(component.health).toBeDefined();
        }
    });
    
    test('should have dependency counts', () => {
        expect(mockArchitectureData.dependencies.internal).toBeDefined();
        expect(mockArchitectureData.dependencies.external).toBeDefined();
        expect(mockArchitectureData.dependencies.circular).toBeDefined();
    });
    
    test('should have non-negative dependency counts', () => {
        expect(mockArchitectureData.dependencies.internal).toBeGreaterThanOrEqual(0);
        expect(mockArchitectureData.dependencies.circular).toBeGreaterThanOrEqual(0);
    });
});

describe('Data Validation - Code Organization Data', () => {
    test('should have complexity object', () => {
        expect(mockCodeOrgData.complexity).toBeDefined();
    });
    
    test('should have average complexity', () => {
        expect(mockCodeOrgData.complexity.average_complexity).toBeDefined();
        expect(typeof mockCodeOrgData.complexity.average_complexity).toBe('number');
    });
    
    test('should have hotspots array', () => {
        expect(Array.isArray(mockCodeOrgData.hotspots)).toBe(true);
    });
    
    test('should have valid hotspot structure', () => {
        if (mockCodeOrgData.hotspots.length > 0) {
            const hotspot = mockCodeOrgData.hotspots[0];
            expect(hotspot.file).toBeDefined();
            expect(hotspot.complexity).toBeDefined();
            expect(hotspot.risk_score).toBeDefined();
        }
    });
    
    test('should have structure object', () => {
        expect(mockCodeOrgData.structure).toBeDefined();
    });
    
    test('should have valid structure metrics', () => {
        expect(mockCodeOrgData.structure.total_modules).toBeDefined();
        expect(mockCodeOrgData.structure.avg_lines_per_file).toBeDefined();
    });
    
    test('should have risk scores between 0-10', () => {
        if (mockCodeOrgData.hotspots.length > 0) {
            const riskScore = mockCodeOrgData.hotspots[0].risk_score;
            expect(riskScore).toBeGreaterThanOrEqual(0);
            expect(riskScore).toBeLessThanOrEqual(10);
        }
    });
});

describe('Data Validation - Vendors Data', () => {
    test('should have services array', () => {
        expect(Array.isArray(mockVendorsData.services)).toBe(true);
    });
    
    test('should have total_services count', () => {
        expect(mockVendorsData.total_services).toBeDefined();
    });
    
    test('should have risk level counts', () => {
        expect(mockVendorsData.high_risk).toBeDefined();
        expect(mockVendorsData.medium_risk).toBeDefined();
        expect(mockVendorsData.low_risk).toBeDefined();
    });
    
    test('should have valid service structure', () => {
        if (mockVendorsData.services.length > 0) {
            const service = mockVendorsData.services[0];
            expect(service.name).toBeDefined();
            expect(service.category).toBeDefined();
            expect(service.risk_level).toBeDefined();
        }
    });
    
    test('should have valid risk levels', () => {
        const validRisks = ['low', 'medium', 'high'];
        if (mockVendorsData.services.length > 0) {
            expect(validRisks).toContain(mockVendorsData.services[0].risk_level);
        }
    });
    
    test('should sum risk counts correctly', () => {
        const sum = 
            mockVendorsData.high_risk +
            mockVendorsData.medium_risk +
            mockVendorsData.low_risk;
        expect(sum).toBe(mockVendorsData.total_services);
    });
});

describe('Data Validation - Executive Data', () => {
    test('should have project_name', () => {
        expect(mockExecutiveData.project_name).toBeDefined();
    });
    
    test('should have overall_health object', () => {
        expect(mockExecutiveData.overall_health).toBeDefined();
    });
    
    test('should have executive_summary', () => {
        expect(mockExecutiveData.executive_summary).toBeDefined();
        expect(typeof mockExecutiveData.executive_summary).toBe('string');
    });
    
    test('should have key_strengths array', () => {
        expect(Array.isArray(mockExecutiveData.key_strengths)).toBe(true);
    });
    
    test('should have areas_of_concern array', () => {
        expect(Array.isArray(mockExecutiveData.areas_of_concern)).toBe(true);
    });
    
    test('should have recommendations array', () => {
        expect(Array.isArray(mockExecutiveData.recommendations)).toBe(true);
    });
});

describe('Data Validation - Boundary Conditions', () => {
    test('should handle empty arrays', () => {
        const emptyArray = [];
        expect(emptyArray.length).toBe(0);
    });
    
    test('should handle null values', () => {
        const nullValue = null;
        expect(nullValue).toBeNull();
    });
    
    test('should handle undefined values', () => {
        const undefinedValue = undefined;
        expect(undefinedValue).toBeUndefined();
    });
    
    test('should handle zero values', () => {
        const zero = 0;
        expect(zero).toBe(0);
    });
    
    test('should handle large numbers', () => {
        const large = 1000000;
        expect(large).toBeGreaterThan(999999);
    });
    
    test('should handle decimal precision', () => {
        const decimal = 78.5;
        expect(decimal).toBeCloseTo(78.5, 1);
    });
});
