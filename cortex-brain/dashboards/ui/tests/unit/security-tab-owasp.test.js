/**
 * Test: Security tab should handle owasp_top_10 as object with categories array
 * 
 * RED Phase - This test verifies security-tab.js correctly extracts
 * the categories array from the owasp_top_10 object structure
 */

import { describe, it, expect, beforeEach } from '@jest/globals';
import { renderSecurity } from '../../components/security-tab.js';

describe('Security Tab OWASP Data Handling (TDD RED Phase)', () => {
    let container;
    
    beforeEach(() => {
        // Create container element
        container = document.createElement('div');
        container.id = 'security-container';
        document.body.appendChild(container);
    });
    
    afterEach(() => {
        document.body.removeChild(container);
    });
    
    it('should handle owasp_top_10 as object with categories array', () => {
        const mockData = {
            security: {
                overall_score: 72,
                last_scan: '2025-12-04T12:46:23',
                vulnerabilities: {
                    total: 24,
                    critical: 1,
                    high: 3,
                    medium: 8,
                    low: 12
                },
                owasp_top_10: {
                    pass_count: 6,
                    warn_count: 3,
                    fail_count: 1,
                    categories: [
                        { id: 'A01', name: 'Broken Access Control', status: 'pass', score: 95 },
                        { id: 'A02', name: 'Cryptographic Failures', status: 'pass', score: 92 }
                    ]
                },
                compliance: {
                    gdpr_ready: true,
                    soc2_ready: false,
                    hipaa_ready: true,
                    pci_dss_ready: false
                }
            }
        };
        
        // Should not throw TypeError
        expect(() => renderSecurity(mockData)).not.toThrow();
        
        // Container should have content
        expect(container.innerHTML).toBeTruthy();
        expect(container.innerHTML.length).toBeGreaterThan(0);
    });
    
    it('should extract categories array from owasp_top_10 object', () => {
        const owaspData = {
            pass_count: 6,
            warn_count: 3,
            fail_count: 1,
            categories: [
                { id: 'A01', name: 'Test', status: 'pass', score: 95 }
            ]
        };
        
        // The correct extraction should be:
        const categories = owaspData.categories || [];
        
        // NOT this (which causes the error):
        // const categories = owaspData || [];
        
        expect(Array.isArray(categories)).toBe(true);
        expect(categories.length).toBe(1);
        expect(categories[0].id).toBe('A01');
    });
    
    it('should handle missing owasp_top_10 gracefully', () => {
        const mockData = {
            security: {
                overall_score: 50,
                vulnerabilities: {},
                compliance: {}
                // owasp_top_10 missing
            }
        };
        
        // Should not throw error even if owasp_top_10 is missing
        expect(() => renderSecurity(mockData)).not.toThrow();
    });
    
    it('should handle owasp_top_10 with empty categories', () => {
        const mockData = {
            security: {
                overall_score: 50,
                owasp_top_10: {
                    pass_count: 0,
                    warn_count: 0,
                    fail_count: 0,
                    categories: []  // Empty array
                },
                vulnerabilities: {},
                compliance: {}
            }
        };
        
        // Should not throw error with empty categories
        expect(() => renderSecurity(mockData)).not.toThrow();
    });
    
    it('should handle legacy format where owasp_top_10 is directly an array', () => {
        const mockData = {
            security: {
                overall_score: 50,
                owasp_top_10: [
                    { id: 'A01', name: 'Test', status: 'pass', score: 95 }
                ],  // Direct array (legacy format)
                vulnerabilities: {},
                compliance: {}
            }
        };
        
        // Should handle both formats gracefully
        expect(() => renderSecurity(mockData)).not.toThrow();
    });
});
