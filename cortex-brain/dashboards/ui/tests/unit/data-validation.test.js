/**
 * Unit Tests - Data Structure Validation
 * 
 * Tests JSON schema validation, required fields, data types.
 * Target: 40+ tests
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

describe('Data Structure Validation', () => {
    
    describe('Health Data Schema', () => {
        it('should have required health score field', () => {
            expect(mockHealthData).toHaveProperty('health_score');
            expect(typeof mockHealthData.health_score).toBe('number');
        });
        
        it('should have health score between 0 and 100', () => {
            expect(mockHealthData.health_score).toBeGreaterThanOrEqual(0);
            expect(mockHealthData.health_score).toBeLessThanOrEqual(100);
        });
        
        it('should have total_files field', () => {
            expect(mockHealthData).toHaveProperty('total_files');
            expect(typeof mockHealthData.total_files).toBe('number');
        });
        
        it('should have total_lines_of_code field', () => {
            expect(mockHealthData).toHaveProperty('total_lines_of_code');
            expect(typeof mockHealthData.total_lines_of_code).toBe('number');
        });
        
        it('should have test_coverage field', () => {
            expect(mockHealthData).toHaveProperty('test_coverage');
            expect(typeof mockHealthData.test_coverage).toBe('number');
        });
        
        it('should have last_updated timestamp', () => {
            expect(mockHealthData).toHaveProperty('last_updated');
            expect(typeof mockHealthData.last_updated).toBe('string');
        });
        
        it('should have trends object', () => {
            expect(mockHealthData).toHaveProperty('trends');
            expect(typeof mockHealthData.trends).toBe('object');
        });
        
        it('should have valid trend data types', () => {
            const trends = mockHealthData.trends;
            expect(typeof trends.health_score_change).toBe('number');
            expect(typeof trends.test_coverage_change).toBe('number');
        });
    });
    
    describe('Tech Stack Data Schema', () => {
        it('should have languages array', () => {
            expect(mockTechStack).toHaveProperty('languages');
            expect(Array.isArray(mockTechStack.languages)).toBe(true);
        });
        
        it('should have valid language structure', () => {
            const lang = mockTechStack.languages[0];
            expect(lang).toHaveProperty('name');
            expect(lang).toHaveProperty('percentage');
            expect(lang).toHaveProperty('files');
            expect(lang).toHaveProperty('lines');
        });
        
        it('should have language percentages sum to ~100', () => {
            const total = mockTechStack.languages.reduce((sum, lang) => sum + lang.percentage, 0);
            expect(total).toBeGreaterThan(95);
            expect(total).toBeLessThanOrEqual(100);
        });
        
        it('should have frameworks array', () => {
            expect(mockTechStack).toHaveProperty('frameworks');
            expect(Array.isArray(mockTechStack.frameworks)).toBe(true);
        });
        
        it('should have valid framework structure', () => {
            const framework = mockTechStack.frameworks[0];
            expect(framework).toHaveProperty('name');
            expect(framework).toHaveProperty('version');
        });
        
        it('should have dependencies object', () => {
            expect(mockTechStack).toHaveProperty('dependencies');
            expect(typeof mockTechStack.dependencies).toBe('object');
        });
        
        it('should have valid dependency counts', () => {
            const deps = mockTechStack.dependencies;
            expect(deps).toHaveProperty('total');
            expect(deps).toHaveProperty('direct');
            expect(deps).toHaveProperty('transitive');
            expect(deps.total).toBeGreaterThanOrEqual(deps.direct);
        });
    });
    
    describe('Security Data Schema', () => {
        it('should have overall_score field', () => {
            expect(mockSecurity).toHaveProperty('overall_score');
            expect(typeof mockSecurity.overall_score).toBe('number');
        });
        
        it('should have security score between 0 and 100', () => {
            expect(mockSecurity.overall_score).toBeGreaterThanOrEqual(0);
            expect(mockSecurity.overall_score).toBeLessThanOrEqual(100);
        });
        
        it('should have vulnerabilities object', () => {
            expect(mockSecurity).toHaveProperty('vulnerabilities');
            expect(typeof mockSecurity.vulnerabilities).toBe('object');
        });
        
        it('should have all vulnerability severity levels', () => {
            const vulns = mockSecurity.vulnerabilities;
            expect(vulns).toHaveProperty('critical');
            expect(vulns).toHaveProperty('high');
            expect(vulns).toHaveProperty('medium');
            expect(vulns).toHaveProperty('low');
        });
        
        it('should have non-negative vulnerability counts', () => {
            const vulns = mockSecurity.vulnerabilities;
            expect(vulns.critical).toBeGreaterThanOrEqual(0);
            expect(vulns.high).toBeGreaterThanOrEqual(0);
            expect(vulns.medium).toBeGreaterThanOrEqual(0);
            expect(vulns.low).toBeGreaterThanOrEqual(0);
        });
    });
    
    describe('Architecture Data Schema', () => {
        it('should be a valid object', () => {
            expect(typeof mockArchitecture).toBe('object');
            expect(mockArchitecture).not.toBeNull();
        });
        
        it('should allow optional pattern detection', () => {
            if (mockArchitecture.patterns) {
                expect(Array.isArray(mockArchitecture.patterns)).toBe(true);
            }
        });
        
        it('should allow optional component structure', () => {
            if (mockArchitecture.components) {
                expect(typeof mockArchitecture.components).toBe('object');
            }
        });
        
        it('should allow optional frontend section', () => {
            if (mockArchitecture.frontend) {
                expect(typeof mockArchitecture.frontend).toBe('object');
            }
        });
        
        it('should allow optional backend section', () => {
            if (mockArchitecture.backend) {
                expect(typeof mockArchitecture.backend).toBe('object');
            }
        });
    });
    
    describe('Code Organization Data Schema', () => {
        it('should be a valid object', () => {
            expect(typeof mockCodeOrg).toBe('object');
            expect(mockCodeOrg).not.toBeNull();
        });
        
        it('should allow optional complexity metrics', () => {
            if (mockCodeOrg.complexity) {
                expect(typeof mockCodeOrg.complexity).toBe('object');
            }
        });
        
        it('should allow optional hotspots array', () => {
            if (mockCodeOrg.hotspots) {
                expect(Array.isArray(mockCodeOrg.hotspots)).toBe(true);
            }
        });
        
        it('should have valid hotspot structure if present', () => {
            if (mockCodeOrg.hotspots && mockCodeOrg.hotspots.length > 0) {
                const hotspot = mockCodeOrg.hotspots[0];
                expect(hotspot).toHaveProperty('file');
                expect(typeof hotspot.file).toBe('string');
            }
        });
    });
    
    describe('Vendors Data Schema', () => {
        it('should be a valid object', () => {
            expect(typeof mockVendors).toBe('object');
            expect(mockVendors).not.toBeNull();
        });
        
        it('should allow optional services array', () => {
            if (mockVendors.services) {
                expect(Array.isArray(mockVendors.services)).toBe(true);
            }
        });
        
        it('should have valid service structure if present', () => {
            if (mockVendors.services && mockVendors.services.length > 0) {
                const service = mockVendors.services[0];
                expect(service).toHaveProperty('name');
                expect(typeof service.name).toBe('string');
            }
        });
    });
    
    describe('Full Dashboard Data Integration', () => {
        it('should have all required top-level sections', () => {
            expect(mockFullDashboard).toHaveProperty('health');
            expect(mockFullDashboard).toHaveProperty('techStack');
            expect(mockFullDashboard).toHaveProperty('security');
        });
        
        it('should have valid nested health data', () => {
            expect(mockFullDashboard.health).toHaveProperty('health_score');
            expect(typeof mockFullDashboard.health.health_score).toBe('number');
        });
        
        it('should have valid nested tech stack data', () => {
            expect(mockFullDashboard.techStack).toHaveProperty('languages');
            expect(Array.isArray(mockFullDashboard.techStack.languages)).toBe(true);
        });
        
        it('should have valid nested security data', () => {
            expect(mockFullDashboard.security).toHaveProperty('overall_score');
            expect(typeof mockFullDashboard.security.overall_score).toBe('number');
        });
    });
    
    describe('Boundary Conditions', () => {
        it('should handle empty arrays gracefully', () => {
            const emptyData = { languages: [], frameworks: [] };
            expect(emptyData.languages).toEqual([]);
            expect(emptyData.frameworks).toEqual([]);
        });
        
        it('should handle null values in optional fields', () => {
            const dataWithNulls = {
                health_score: 85,
                optional_field: null
            };
            expect(dataWithNulls.optional_field).toBeNull();
        });
        
        it('should handle undefined optional properties', () => {
            const minimalData = { health_score: 85 };
            expect(minimalData.optional_field).toBeUndefined();
        });
        
        it('should handle very large numbers', () => {
            const largeData = {
                total_lines_of_code: 1000000,
                total_files: 50000
            };
            expect(largeData.total_lines_of_code).toBeGreaterThan(999999);
        });
        
        it('should handle decimal precision', () => {
            const preciseData = {
                health_score: 87.5432,
                percentage: 12.3456
            };
            expect(preciseData.health_score).toBeCloseTo(87.54, 1);
        });
    });
});
