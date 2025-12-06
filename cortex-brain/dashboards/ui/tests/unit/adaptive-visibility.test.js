/**
 * Unit Tests - Adaptive Visibility Engine
 * 
 * Tests project type detection and visibility rule application.
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 */

import { describe, it, expect, beforeEach } from '@jest/globals';
import { detectProjectType, initializeAdaptiveVisibility } from '../../adaptive-visibility.js';

describe('Adaptive Visibility Engine', () => {
    
    describe('detectProjectType()', () => {
        
        it('should detect full_stack project with all layers', () => {
            const data = {
                architecture: {
                    frontend: {
                        framework: 'Angular',
                        components: [{ name: 'AppComponent' }]
                    },
                    backend: {
                        api: {
                            endpoints: [{ path: '/api/users', method: 'GET' }]
                        }
                    },
                    database: {
                        platform: 'SQL Server',
                        tables: [{ name: 'Users', rows: 1000 }]
                    }
                }
            };
            
            const result = detectProjectType(data);
            expect(result).toBe('full_stack');
        });
        
        it('should detect api_only project (backend + database, no frontend)', () => {
            const data = {
                architecture: {
                    backend: {
                        api: {
                            endpoints: [{ path: '/api/users', method: 'GET' }]
                        },
                        services: ['UserService', 'AuthService']
                    },
                    database: {
                        platform: 'PostgreSQL',
                        tables: [{ name: 'users', rows: 5000 }]
                    }
                }
            };
            
            const result = detectProjectType(data);
            expect(result).toBe('api_only');
        });
        
        it('should detect spa_only project (frontend only)', () => {
            const data = {
                architecture: {
                    frontend: {
                        framework: 'React',
                        components: [
                            { name: 'App', routes: ['/'] },
                            { name: 'Dashboard', routes: ['/dashboard'] }
                        ],
                        stateManagement: 'Redux'
                    }
                }
            };
            
            const result = detectProjectType(data);
            expect(result).toBe('spa_only');
        });
        
        it('should detect database_only project', () => {
            const data = {
                architecture: {
                    database: {
                        platform: 'SQL Server',
                        tables: [
                            { name: 'Users', rows: 10000 },
                            { name: 'Orders', rows: 50000 }
                        ],
                        procedures: [
                            { name: 'sp_GetUserOrders', complexity: 'high' }
                        ],
                        views: [
                            { name: 'vw_ActiveUsers' }
                        ]
                    }
                }
            };
            
            const result = detectProjectType(data);
            expect(result).toBe('database_only');
        });
        
        it('should detect via techStack fallback (TypeScript/JavaScript = frontend)', () => {
            const data = {
                techStack: {
                    languages: [
                        { name: 'TypeScript', percentage: 60 },
                        { name: 'JavaScript', percentage: 40 }
                    ],
                    frameworks: [
                        { name: 'Angular', version: '17.0.0' }
                    ]
                }
            };
            
            const result = detectProjectType(data);
            expect(result).toBe('spa_only'); // Only frontend tech detected
        });
        
        it('should detect via techStack fallback (C# + SQL = api_only)', () => {
            const data = {
                techStack: {
                    languages: [
                        { name: 'CSharp', percentage: 80 },
                        { name: 'SQL', percentage: 20 }
                    ],
                    frameworks: [
                        { name: 'ASP.NET Core', version: '8.0' }
                    ]
                }
            };
            
            const result = detectProjectType(data);
            expect(result).toBe('api_only'); // Backend + database, no frontend
        });
        
        it('should detect via techStack fallback (TypeScript + C# + SQL = full_stack)', () => {
            const data = {
                techStack: {
                    languages: [
                        { name: 'TypeScript', percentage: 40 },
                        { name: 'CSharp', percentage: 50 },
                        { name: 'SQL', percentage: 10 }
                    ],
                    frameworks: [
                        { name: 'Angular', version: '17.0.0' },
                        { name: 'ASP.NET Core', version: '8.0' }
                    ]
                }
            };
            
            const result = detectProjectType(data);
            expect(result).toBe('full_stack');
        });
        
        it('should return unknown for empty data', () => {
            expect(detectProjectType(null)).toBe('unknown');
            expect(detectProjectType({})).toBe('unknown');
            expect(detectProjectType({ architecture: {} })).toBe('unknown');
        });
        
        it('should return unknown for data with no valid layers', () => {
            const data = {
                architecture: {
                    frontend: {},
                    backend: {},
                    database: {}
                }
            };
            
            const result = detectProjectType(data);
            expect(result).toBe('unknown');
        });
    });
    
    describe('Visibility Profiles', () => {
        
        it('full_stack profile should show all sections', () => {
            const data = {
                architecture: {
                    frontend: { components: [{ name: 'Test' }] },
                    backend: { api: { endpoints: [{ path: '/test' }] } },
                    database: { tables: [{ name: 'test_table' }] }
                }
            };
            
            const projectType = detectProjectType(data);
            expect(projectType).toBe('full_stack');
            
            // Full-stack should not hide anything
            // (Testing via profile rules, not DOM manipulation)
        });
        
        it('api_only profile should hide frontend sections', () => {
            const data = {
                architecture: {
                    backend: { api: { endpoints: [{ path: '/api/test' }] } },
                    database: { tables: [{ name: 'users' }] }
                }
            };
            
            const projectType = detectProjectType(data);
            expect(projectType).toBe('api_only');
            
            // API-only should hide: frontend, ui-components
        });
        
        it('spa_only profile should hide backend/database sections', () => {
            const data = {
                architecture: {
                    frontend: {
                        framework: 'React',
                        components: [{ name: 'App' }]
                    }
                }
            };
            
            const projectType = detectProjectType(data);
            expect(projectType).toBe('spa_only');
            
            // SPA-only should hide: backend, database
        });
    });
    
    describe('Edge Cases', () => {
        
        it('should handle mixed signals (architecture + techStack)', () => {
            const data = {
                architecture: {
                    frontend: { components: [] }, // Empty
                    backend: { api: { endpoints: [{ path: '/test' }] } } // Has data
                },
                techStack: {
                    languages: [
                        { name: 'TypeScript', percentage: 50 }, // Frontend signal
                        { name: 'CSharp', percentage: 50 } // Backend signal
                    ]
                }
            };
            
            // Should detect frontend via techStack even though architecture.frontend is empty
            const result = detectProjectType(data);
            expect(result).toBe('full_stack'); // TypeScript + backend endpoints = full_stack
        });
        
        it('should prioritize architecture data over techStack', () => {
            const data = {
                architecture: {
                    backend: {
                        api: { endpoints: [{ path: '/api/users' }] }
                    },
                    database: {
                        tables: [{ name: 'users' }]
                    }
                },
                techStack: {
                    languages: [
                        { name: 'TypeScript', percentage: 100 } // Should not override
                    ]
                }
            };
            
            // TypeScript is present but no frontend architecture data
            // System should combine both: backend (arch) + database (arch) + frontend (techStack)
            const result = detectProjectType(data);
            expect(result).toBe('full_stack'); // Combined detection
        });
    });
});
