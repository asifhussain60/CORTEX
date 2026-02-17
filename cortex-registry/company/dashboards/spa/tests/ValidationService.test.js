/**
 * ValidationService Test Suite
 * 
 * Tests XSS protection, data integrity, contradiction detection,
 * and security boundary enforcement.
 * 
 * TDD Pattern: RED → GREEN → REFACTOR
 * Authority: CORE-008 (TDD mandatory), OWASP
 */

describe('ValidationService', () => {
    let validationService;
    let mockStateManager;

    beforeEach(() => {
        mockStateManager = {
            setState: jest.fn()
        };
        validationService = new ValidationService(mockStateManager);
    });

    describe('Initialization', () => {
        it('should initialize with state manager', () => {
            expect(validationService.stateManager).toBe(mockStateManager);
        });

        it('should initialize validation rules', () => {
            expect(validationService.rules).toBeDefined();
            expect(validationService.rules.length).toBeGreaterThan(0);
        });
    });

    describe('XSS Protection', () => {
        it('should sanitize HTML tags', () => {
            const dirty = '<img src="x" onerror="alert(1)">';
            const clean = validationService.sanitizeHTML(dirty);

            expect(clean).not.toContain('onerror');
            expect(clean).not.toContain('alert');
        });

        it('should remove script tags', () => {
            const dirty = 'Hello <script>alert("XSS")</script> World';
            const clean = validationService.sanitizeHTML(dirty);

            expect(clean).not.toContain('<script>');
            expect(clean).toContain('Hello');
            expect(clean).toContain('World');
        });

        it('should remove event attributes', () => {
            const dirty = '<div onclick="alert(1)" onmouseover="alert(2)">Click me</div>';
            const clean = validationService.sanitizeHTML(dirty);

            expect(clean).not.toContain('onclick');
            expect(clean).not.toContain('onmouseover');
        });

        it('should allow safe HTML tags', () => {
            const safe = '<p>Safe <b>text</b> here</p>';
            const clean = validationService.sanitizeHTML(safe);

            expect(clean).toContain('<p>');
            expect(clean).toContain('<b>');
            expect(clean).toContain('</b>');
        });

        it('should handle data URLs in img src', () => {
            const dirty = '<img src="data:text/html,<script>alert(1)</script>">';
            const clean = validationService.sanitizeHTML(dirty);

            expect(clean).not.toContain('data:text/html');
        });

        it('should encode special characters', () => {
            const dirty = 'Hello & <World> "quotes" \'single\'';
            const clean = validationService.sanitizeHTML(dirty);

            expect(clean).toContain('&amp;');
            expect(clean).toContain('&lt;');
            expect(clean).toContain('&quot;');
        });
    });

    describe('Data Integrity Checks', () => {
        it('should detect missing required fields', () => {
            const data = { name: 'Test' }; // Missing 'id'
            const result = validationService.validateDataIntegrity(data);

            expect(result.valid).toBe(false);
            expect(result.errors).toContain('Missing required field: id');
        });

        it('should detect type mismatches', () => {
            const data = {
                id: 'not-a-number',
                name: 'Test',
                count: 'should-be-number'
            };
            const result = validationService.validateDataIntegrity(data);

            expect(result.valid).toBe(false);
            expect(result.errors.length).toBeGreaterThan(0);
        });

        it('should validate string lengths', () => {
            const data = {
                id: 1,
                name: 'A'.repeat(1000), // Exceeds max length
                count: 5
            };
            const result = validationService.validateDataIntegrity(data);

            expect(result.valid).toBe(false);
        });

        it('should detect range violations', () => {
            const data = {
                id: 1,
                name: 'Test',
                count: -1 // Should be >= 0
            };
            const result = validationService.validateDataIntegrity(data);

            expect(result.valid).toBe(false);
        });

        it('should allow valid data', () => {
            const data = {
                id: 1,
                name: 'Valid Test',
                count: 42
            };
            const result = validationService.validateDataIntegrity(data);

            expect(result.valid).toBe(true);
            expect(result.errors.length).toBe(0);
        });
    });

    describe('Contradiction Detection', () => {
        it('should detect contradictory data patterns', () => {
            const data = {
                isActive: true,
                deletedAt: '2024-01-01' // Active but deleted?
            };
            const result = validationService.detectContradictions(data);

            expect(result.detected).toBe(true);
            expect(result.contradictions.length).toBeGreaterThan(0);
        });

        it('should detect conflicting status indicators', () => {
            const data = {
                status: 'pending',
                isComplete: true,
                progressPercent: 0
            };
            const result = validationService.detectContradictions(data);

            expect(result.detected).toBe(true);
        });

        it('should calculate confidence score', () => {
            const data = {
                isActive: true,
                deletedAt: '2024-01-01'
            };
            const result = validationService.detectContradictions(data);

            expect(result.confidence).toBeGreaterThan(0);
            expect(result.confidence).toBeLessThanOrEqual(1);
        });

        it('should detect time-based contradictions', () => {
            const futureDate = new Date(Date.now() + 86400000);
            const data = {
                startDate: futureDate,
                endDate: new Date()
            };
            const result = validationService.detectContradictions(data);

            expect(result.detected).toBe(true);
        });

        it('should allow consistent data', () => {
            const data = {
                isActive: true,
                deletedAt: null,
                status: 'running',
                progressPercent: 50
            };
            const result = validationService.detectContradictions(data);

            expect(result.detected).toBe(false);
        });
    });

    describe('Schema Validation', () => {
        it('should validate against schema', () => {
            const schema = {
                type: 'object',
                properties: {
                    id: { type: 'number' },
                    name: { type: 'string' }
                },
                required: ['id', 'name']
            };

            const validData = { id: 1, name: 'Test' };
            const result = validationService.validateSchema(validData, schema);

            expect(result.valid).toBe(true);
        });

        it('should reject invalid schema data', () => {
            const schema = {
                type: 'object',
                properties: {
                    id: { type: 'number' },
                    name: { type: 'string' }
                },
                required: ['id', 'name']
            };

            const invalidData = { id: 'not-a-number', name: 123 };
            const result = validationService.validateSchema(invalidData, schema);

            expect(result.valid).toBe(false);
        });

        it('should validate nested objects', () => {
            const schema = {
                type: 'object',
                properties: {
                    user: {
                        type: 'object',
                        properties: {
                            id: { type: 'number' },
                            profile: {
                                type: 'object',
                                properties: {
                                    name: { type: 'string' }
                                }
                            }
                        }
                    }
                }
            };

            const data = {
                user: {
                    id: 1,
                    profile: {
                        name: 'John'
                    }
                }
            };

            const result = validationService.validateSchema(data, schema);
            expect(result.valid).toBe(true);
        });

        it('should validate arrays', () => {
            const schema = {
                type: 'array',
                items: { type: 'number' }
            };

            const validData = [1, 2, 3];
            expect(validationService.validateSchema(validData, schema).valid).toBe(true);

            const invalidData = [1, 'two', 3];
            expect(validationService.validateSchema(invalidData, schema).valid).toBe(false);
        });
    });

    describe('Trust Boundary Enforcement', () => {
        it('should mark external data as untrusted', () => {
            const data = { source: 'external', content: '<script>alert(1)</script>' };
            const marked = validationService.markUntrusted(data);

            expect(marked.__trusted).toBe(false);
        });

        it('should enforce trust boundaries on rendering', () => {
            const untrustedData = {
                __trusted: false,
                html: '<img src="x" onerror="alert(1)">'
            };

            const result = validationService.enforceRenderTrust(untrustedData);

            expect(result.allowed).toBe(false);
        });

        it('should allow trusted data through', () => {
            const trustedData = {
                __trusted: true,
                html: '<p>Safe content</p>'
            };

            const result = validationService.enforceRenderTrust(trustedData);

            expect(result.allowed).toBe(true);
        });

        it('should upgrade trust after validation', () => {
            const data = { html: '<p>Safe</p>' };
            validationService.markUntrusted(data);

            validationService.validateDataIntegrity(data);
            const upgraded = validationService.upgradeTrust(data);

            expect(upgraded.__trusted).toBe(true);
        });
    });

    describe('Sanitization Batching', () => {
        it('should batch sanitize multiple values', () => {
            const values = [
                '<script>alert(1)</script>',
                '<img onerror="alert(2)">',
                'Safe text'
            ];

            const cleaned = validationService.sanitizeBatch(values);

            expect(cleaned[0]).not.toContain('<script>');
            expect(cleaned[1]).not.toContain('onerror');
            expect(cleaned[2]).toBe('Safe text');
        });

        it('should sanitize object properties', () => {
            const obj = {
                title: '<script>alert(1)</script>',
                description: '<img onerror="alert(2)">',
                count: 42
            };

            const cleaned = validationService.sanitizeObject(obj);

            expect(cleaned.title).not.toContain('<script>');
            expect(cleaned.description).not.toContain('onerror');
            expect(cleaned.count).toBe(42);
        });
    });

    describe('Validation Error Handling', () => {
        it('should collect all validation errors', () => {
            const data = {
                id: 'invalid',
                name: 'A'.repeat(1000),
                count: -5
            };

            const result = validationService.validateDataIntegrity(data);

            expect(result.errors.length).toBeGreaterThan(1);
        });

        it('should provide detailed error information', () => {
            const data = { id: 'not-a-number' };
            const result = validationService.validateDataIntegrity(data);

            const error = result.errors[0];
            expect(error).toHaveProperty('field');
            expect(error).toHaveProperty('message');
            expect(error).toHaveProperty('type');
        });

        it('should suggest corrections for common issues', () => {
            const data = { name: '  test  ' };
            const result = validationService.validateAndSuggestFix(data);

            expect(result.suggestions).toBeDefined();
            expect(result.suggestions.length).toBeGreaterThan(0);
        });
    });

    describe('Performance', () => {
        it('should handle large data objects efficiently', () => {
            const largeData = {};
            for (let i = 0; i < 1000; i++) {
                largeData[`field${i}`] = `value${i}`;
            }

            const start = performance.now();
            validationService.sanitizeObject(largeData);
            const duration = performance.now() - start;

            expect(duration).toBeLessThan(100); // Should complete in <100ms
        });

        it('should cache validation rules', () => {
            const schema = { type: 'object', properties: { id: { type: 'number' } } };

            validationService.validateSchema({ id: 1 }, schema);
            const result = validationService.validateSchema({ id: 2 }, schema);

            expect(result.valid).toBe(true);
        });
    });
});
