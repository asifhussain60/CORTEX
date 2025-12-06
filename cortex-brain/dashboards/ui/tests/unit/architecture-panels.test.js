/**
 * Unit Tests - Architecture Panels
 * 
 * Tests panel rendering for Frontend, Backend, and Database architectures.
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 */

import { describe, it, expect, beforeEach } from '@jest/globals';
import { 
    renderFrontendPanel, 
    renderBackendPanel, 
    renderDatabasePanel,
    renderArchitecturePanels 
} from '../../architecture-panels.js';

// Mock DOM
beforeEach(() => {
    document.body.innerHTML = '<div id="architecture-panels-container"></div>';
});

describe('Architecture Panels', () => {
    
    describe('renderFrontendPanel()', () => {
        
        it('should render Angular frontend with components', () => {
            const frontendData = {
                framework: 'Angular',
                version: '17.0.0',
                components: [
                    { name: 'AppComponent', routes: ['/'], size: 250 },
                    { name: 'DashboardComponent', routes: ['/dashboard'], size: 450 },
                    { name: 'UserListComponent', routes: ['/users'], size: 320 }
                ],
                routes: [
                    { path: '/', component: 'AppComponent' },
                    { path: '/dashboard', component: 'DashboardComponent' },
                    { path: '/users', component: 'UserListComponent' }
                ],
                stateManagement: 'NgRx'
            };
            
            const container = document.getElementById('architecture-panels-container');
            renderFrontendPanel(frontendData, container);
            
            // Verify panel exists
            expect(container.querySelector('.architecture-panel.frontend-panel')).toBeTruthy();
            
            // Verify framework badge
            const badge = container.querySelector('.framework-badge');
            expect(badge).toBeTruthy();
            expect(badge.textContent).toContain('Angular');
            expect(badge.textContent).toContain('17.0.0');
            
            // Verify components rendered (top 10)
            const componentItems = container.querySelectorAll('.component-item');
            expect(componentItems.length).toBe(3);
            expect(componentItems[0].textContent).toContain('AppComponent');
            expect(componentItems[1].textContent).toContain('DashboardComponent');
            
            // Verify routes
            const routeItems = container.querySelectorAll('.route-item');
            expect(routeItems.length).toBe(3);
            
            // Verify state management
            expect(container.textContent).toContain('NgRx');
        });
        
        it('should render React frontend with state management', () => {
            const frontendData = {
                framework: 'React',
                version: '18.2.0',
                components: [
                    { name: 'App', size: 150 },
                    { name: 'UserProfile', size: 280 }
                ],
                stateManagement: 'Redux'
            };
            
            const container = document.getElementById('architecture-panels-container');
            renderFrontendPanel(frontendData, container);
            
            const badge = container.querySelector('.framework-badge');
            expect(badge.textContent).toContain('React');
            expect(container.textContent).toContain('Redux');
        });
        
        it('should handle frontend with no routes', () => {
            const frontendData = {
                framework: 'Vue',
                version: '3.3.0',
                components: [
                    { name: 'HelloWorld', size: 100 }
                ]
            };
            
            const container = document.getElementById('architecture-panels-container');
            renderFrontendPanel(frontendData, container);
            
            expect(container.querySelector('.frontend-panel')).toBeTruthy();
            expect(container.textContent).toContain('Vue');
        });
        
        it('should limit components to top 10', () => {
            const components = Array.from({ length: 25 }, (_, i) => ({
                name: `Component${i + 1}`,
                size: 100 + i * 10
            }));
            
            const frontendData = {
                framework: 'Angular',
                components
            };
            
            const container = document.getElementById('architecture-panels-container');
            renderFrontendPanel(frontendData, container);
            
            const componentItems = container.querySelectorAll('.component-item');
            expect(componentItems.length).toBe(10); // Top 10 only
        });
    });
    
    describe('renderBackendPanel()', () => {
        
        it('should render API endpoints with HTTP methods', () => {
            const backendData = {
                api: {
                    endpoints: [
                        { path: '/api/users', method: 'GET', controller: 'UserController' },
                        { path: '/api/users', method: 'POST', controller: 'UserController' },
                        { path: '/api/users/:id', method: 'PUT', controller: 'UserController' },
                        { path: '/api/users/:id', method: 'DELETE', controller: 'UserController' },
                        { path: '/api/auth/login', method: 'POST', controller: 'AuthController' }
                    ],
                    totalEndpoints: 5
                },
                services: [
                    { name: 'UserService', layer: 'business' },
                    { name: 'AuthService', layer: 'business' },
                    { name: 'DataService', layer: 'data' }
                ],
                backgroundJobs: [
                    { name: 'EmailNotificationJob', schedule: '*/15 * * * *' },
                    { name: 'DataCleanupJob', schedule: '0 2 * * *' }
                ]
            };
            
            const container = document.getElementById('architecture-panels-container');
            renderBackendPanel(backendData, container);
            
            // Verify panel exists
            expect(container.querySelector('.architecture-panel.backend-panel')).toBeTruthy();
            
            // Verify endpoints rendered
            const endpointItems = container.querySelectorAll('.endpoint-item');
            expect(endpointItems.length).toBe(5);
            
            // Verify HTTP method badges
            const getBadges = container.querySelectorAll('.http-method.get');
            const postBadges = container.querySelectorAll('.http-method.post');
            const putBadges = container.querySelectorAll('.http-method.put');
            const deleteBadges = container.querySelectorAll('.http-method.delete');
            
            expect(getBadges.length).toBe(1);
            expect(postBadges.length).toBe(2);
            expect(putBadges.length).toBe(1);
            expect(deleteBadges.length).toBe(1);
            
            // Verify services
            const serviceItems = container.querySelectorAll('.service-item');
            expect(serviceItems.length).toBe(3);
            
            // Verify background jobs
            const jobItems = container.querySelectorAll('.job-item');
            expect(jobItems.length).toBe(2);
        });
        
        it('should limit endpoints to top 15', () => {
            const endpoints = Array.from({ length: 30 }, (_, i) => ({
                path: `/api/endpoint${i + 1}`,
                method: 'GET',
                complexity: i % 3 === 0 ? 'high' : 'low'
            }));
            
            const backendData = {
                api: { endpoints, totalEndpoints: 30 }
            };
            
            const container = document.getElementById('architecture-panels-container');
            renderBackendPanel(backendData, container);
            
            const endpointItems = container.querySelectorAll('.endpoint-item');
            expect(endpointItems.length).toBe(15); // Top 15 only
        });
        
        it('should render without services or background jobs', () => {
            const backendData = {
                api: {
                    endpoints: [
                        { path: '/api/health', method: 'GET' }
                    ],
                    totalEndpoints: 1
                }
            };
            
            const container = document.getElementById('architecture-panels-container');
            renderBackendPanel(backendData, container);
            
            expect(container.querySelector('.backend-panel')).toBeTruthy();
            const endpointItems = container.querySelectorAll('.endpoint-item');
            expect(endpointItems.length).toBe(1);
        });
    });
    
    describe('renderDatabasePanel()', () => {
        
        it('should render SQL Server database with tables and procedures', () => {
            const databaseData = {
                platform: 'SQL Server',
                version: '2022',
                tables: [
                    { name: 'Users', rows: 10000, columns: 15 },
                    { name: 'Orders', rows: 50000, columns: 20 },
                    { name: 'Products', rows: 5000, columns: 12 }
                ],
                procedures: [
                    { name: 'sp_GetUserOrders', complexity: 'high', parameters: 3 },
                    { name: 'sp_CreateOrder', complexity: 'medium', parameters: 5 }
                ],
                views: [
                    { name: 'vw_ActiveUsers', tables: ['Users'] },
                    { name: 'vw_OrderSummary', tables: ['Orders', 'Users'] }
                ]
            };
            
            const container = document.getElementById('architecture-panels-container');
            renderDatabasePanel(databaseData, container);
            
            // Verify panel exists
            expect(container.querySelector('.architecture-panel.database-panel')).toBeTruthy();
            
            // Verify platform badge
            const badge = container.querySelector('.platform-badge');
            expect(badge).toBeTruthy();
            expect(badge.textContent).toContain('SQL Server');
            
            // Verify tables
            const tableItems = container.querySelectorAll('.table-item');
            expect(tableItems.length).toBe(3);
            expect(container.textContent).toContain('Users');
            expect(container.textContent).toContain('Orders');
            
            // Verify procedures
            const procedureItems = container.querySelectorAll('.procedure-item');
            expect(procedureItems.length).toBe(2);
            
            // Verify views
            const viewItems = container.querySelectorAll('.view-item');
            expect(viewItems.length).toBe(2);
            
            // Verify complexity indicators
            const highComplexity = container.querySelectorAll('.complexity-high');
            const mediumComplexity = container.querySelectorAll('.complexity-medium');
            expect(highComplexity.length).toBeGreaterThan(0);
            expect(mediumComplexity.length).toBeGreaterThan(0);
        });
        
        it('should limit tables to top 15 and procedures to top 10', () => {
            const tables = Array.from({ length: 30 }, (_, i) => ({
                name: `Table${i + 1}`,
                rows: 1000 * (i + 1)
            }));
            
            const procedures = Array.from({ length: 20 }, (_, i) => ({
                name: `sp_Procedure${i + 1}`,
                complexity: 'low'
            }));
            
            const databaseData = {
                platform: 'PostgreSQL',
                tables,
                procedures
            };
            
            const container = document.getElementById('architecture-panels-container');
            renderDatabasePanel(databaseData, container);
            
            const tableItems = container.querySelectorAll('.table-item');
            const procedureItems = container.querySelectorAll('.procedure-item');
            
            expect(tableItems.length).toBe(15); // Top 15 tables
            expect(procedureItems.length).toBe(10); // Top 10 procedures
        });
        
        it('should render database with only tables', () => {
            const databaseData = {
                platform: 'MySQL',
                version: '8.0',
                tables: [
                    { name: 'users', rows: 1000 }
                ]
            };
            
            const container = document.getElementById('architecture-panels-container');
            renderDatabasePanel(databaseData, container);
            
            expect(container.querySelector('.database-panel')).toBeTruthy();
            expect(container.textContent).toContain('MySQL');
        });
    });
    
    describe('renderArchitecturePanels()', () => {
        
        it('should render all three panels for full-stack project', () => {
            const architectureData = {
                frontend: {
                    framework: 'Angular',
                    components: [{ name: 'AppComponent' }]
                },
                backend: {
                    api: {
                        endpoints: [{ path: '/api/test', method: 'GET' }]
                    }
                },
                database: {
                    platform: 'SQL Server',
                    tables: [{ name: 'Users' }]
                }
            };
            
            const container = document.getElementById('architecture-panels-container');
            renderArchitecturePanels(architectureData, container);
            
            // All three panels should exist
            expect(container.querySelector('.frontend-panel')).toBeTruthy();
            expect(container.querySelector('.backend-panel')).toBeTruthy();
            expect(container.querySelector('.database-panel')).toBeTruthy();
        });
        
        it('should render only backend and database for api_only project', () => {
            const architectureData = {
                backend: {
                    api: {
                        endpoints: [{ path: '/api/users', method: 'GET' }]
                    }
                },
                database: {
                    platform: 'PostgreSQL',
                    tables: [{ name: 'users' }]
                }
            };
            
            const container = document.getElementById('architecture-panels-container');
            renderArchitecturePanels(architectureData, container);
            
            // Only backend and database panels
            expect(container.querySelector('.frontend-panel')).toBeFalsy();
            expect(container.querySelector('.backend-panel')).toBeTruthy();
            expect(container.querySelector('.database-panel')).toBeTruthy();
        });
        
        it('should render only frontend for spa_only project', () => {
            const architectureData = {
                frontend: {
                    framework: 'React',
                    components: [
                        { name: 'App' },
                        { name: 'Dashboard' }
                    ]
                }
            };
            
            const container = document.getElementById('architecture-panels-container');
            renderArchitecturePanels(architectureData, container);
            
            // Only frontend panel
            expect(container.querySelector('.frontend-panel')).toBeTruthy();
            expect(container.querySelector('.backend-panel')).toBeFalsy();
            expect(container.querySelector('.database-panel')).toBeFalsy();
        });
        
        it('should handle empty architecture data', () => {
            const container = document.getElementById('architecture-panels-container');
            renderArchitecturePanels({}, container);
            
            // No panels should be rendered
            expect(container.querySelector('.architecture-panel')).toBeFalsy();
        });
        
        it('should handle null container gracefully', () => {
            const architectureData = {
                frontend: { framework: 'Vue' }
            };
            
            // Should not throw error
            expect(() => {
                renderArchitecturePanels(architectureData, null);
            }).not.toThrow();
        });
    });
    
    describe('Edge Cases', () => {
        
        it('should handle missing optional fields gracefully', () => {
            const backendData = {
                api: {
                    endpoints: [
                        { path: '/api/test' } // Missing method, controller
                    ]
                }
            };
            
            const container = document.getElementById('architecture-panels-container');
            
            expect(() => {
                renderBackendPanel(backendData, container);
            }).not.toThrow();
        });
        
        it('should handle non-standard framework names', () => {
            const frontendData = {
                framework: 'CustomFramework',
                version: '1.0.0',
                components: [{ name: 'Test' }]
            };
            
            const container = document.getElementById('architecture-panels-container');
            renderFrontendPanel(frontendData, container);
            
            expect(container.textContent).toContain('CustomFramework');
        });
        
        it('should handle very large numbers gracefully', () => {
            const databaseData = {
                platform: 'Oracle',
                tables: [
                    { name: 'BigTable', rows: 1000000000, columns: 500 }
                ]
            };
            
            const container = document.getElementById('architecture-panels-container');
            renderDatabasePanel(databaseData, container);
            
            expect(container.querySelector('.database-panel')).toBeTruthy();
            // Should format large numbers with commas or abbreviations
        });
    });
});
