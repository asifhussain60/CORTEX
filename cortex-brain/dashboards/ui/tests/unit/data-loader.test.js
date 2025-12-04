/**
 * Unit Tests - Data Loader Module
 * 
 * Tests data loading, caching, and error handling.
 * 
 * Run: npm test tests/unit/data-loader.test.js
 */

import { mockFullDashboard, mockHealthData } from '../fixtures/mock-data.js';

describe('Data Loader Module', () => {
    let dataLoader;
    
    beforeAll(async () => {
        // Dynamic import to avoid circular dependencies
        dataLoader = await import('../../data-loader.js');
    });
    
    beforeEach(() => {
        // Clear any cached data
        if (dataLoader.clearCache) {
            dataLoader.clearCache();
        }
        
        // Mock fetch
        global.fetch = jest.fn();
    });
    
    afterEach(() => {
        jest.restoreAllMocks();
    });
    
    describe('loadDashboardData', () => {
        it('should load mock data successfully', async () => {
            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockFullDashboard
            });
            
            const data = await dataLoader.loadDashboardData('mock');
            
            expect(data).toBeDefined();
            expect(data.metadata).toEqual(mockFullDashboard.metadata);
            expect(data.health).toEqual(mockFullDashboard.health);
        });
        
        it('should handle network errors gracefully', async () => {
            global.fetch.mockRejectedValueOnce(new Error('Network error'));
            
            await expect(
                dataLoader.loadDashboardData('mock')
            ).rejects.toThrow('Network error');
        });
        
        it('should handle invalid JSON responses', async () => {
            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => { throw new Error('Invalid JSON'); }
            });
            
            await expect(
                dataLoader.loadDashboardData('mock')
            ).rejects.toThrow();
        });
        
        it('should handle 404 responses', async () => {
            global.fetch.mockResolvedValueOnce({
                ok: false,
                status: 404,
                statusText: 'Not Found'
            });
            
            await expect(
                dataLoader.loadDashboardData('nonexistent')
            ).rejects.toThrow();
        });
        
        it('should cache loaded data', async () => {
            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockFullDashboard
            });
            
            // First load
            await dataLoader.loadDashboardData('mock');
            
            // Second load should use cache (no new fetch)
            const data = await dataLoader.loadDashboardData('mock');
            
            expect(global.fetch).toHaveBeenCalledTimes(1);
            expect(data).toBeDefined();
        });
    });
    
    describe('clearCache', () => {
        it('should clear cached data', async () => {
            global.fetch.mockResolvedValue({
                ok: true,
                json: async () => mockFullDashboard
            });
            
            // Load and cache
            await dataLoader.loadDashboardData('mock');
            
            // Clear cache
            dataLoader.clearCache();
            
            // Should fetch again
            await dataLoader.loadDashboardData('mock');
            
            expect(global.fetch).toHaveBeenCalledTimes(2);
        });
    });
    
    describe('exportToJson', () => {
        it('should export data to JSON format', () => {
            const result = dataLoader.exportToJson(mockHealthData);
            
            expect(result).toBeDefined();
            expect(typeof result).toBe('string');
            expect(JSON.parse(result)).toEqual(mockHealthData);
        });
        
        it('should handle circular references', () => {
            const circular = { a: 1 };
            circular.self = circular;
            
            expect(() => {
                dataLoader.exportToJson(circular);
            }).not.toThrow();
        });
    });
    
    describe('exportToCsv', () => {
        it('should convert array data to CSV', () => {
            const data = [
                { name: 'File1', lines: 100, coverage: 80 },
                { name: 'File2', lines: 200, coverage: 90 }
            ];
            
            const csv = dataLoader.exportToCsv(data);
            
            expect(csv).toContain('name,lines,coverage');
            expect(csv).toContain('File1,100,80');
            expect(csv).toContain('File2,200,90');
        });
        
        it('should handle empty arrays', () => {
            expect(() => {
                dataLoader.exportToCsv([]);
            }).toThrow();
        });
        
        it('should handle custom column selection', () => {
            const data = [
                { name: 'File1', lines: 100, coverage: 80, extra: 'ignore' }
            ];
            
            const csv = dataLoader.exportToCsv(data, ['name', 'lines']);
            
            expect(csv).toContain('name,lines');
            expect(csv).not.toContain('coverage');
            expect(csv).not.toContain('extra');
        });
    });
});
