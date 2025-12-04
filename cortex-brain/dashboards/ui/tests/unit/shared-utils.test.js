/**
 * Unit Tests - Shared Utilities Module
 * 
 * Tests toast notifications, loading overlays, and utility functions.
 * 
 * Run: npm test tests/unit/shared-utils.test.js
 */

describe('Shared Utilities Module', () => {
    let sharedUtils;
    
    beforeAll(async () => {
        sharedUtils = await import('../../shared-utils.js');
    });
    
    beforeEach(() => {
        document.body.innerHTML = '';
    });
    
    describe('Toast Notifications', () => {
        it('should create and show success toast', () => {
            sharedUtils.showSuccessToast('Operation successful');
            
            const toast = document.querySelector('.toast-success');
            expect(toast).toBeDefined();
            expect(toast.textContent).toBe('Operation successful');
        });
        
        it('should create and show error toast', () => {
            sharedUtils.showErrorToast('Operation failed');
            
            const toast = document.querySelector('.toast-error');
            expect(toast).toBeDefined();
            expect(toast.textContent).toBe('Operation failed');
        });
        
        it('should create and show warning toast', () => {
            sharedUtils.showWarningToast('Warning message');
            
            const toast = document.querySelector('.toast-warning');
            expect(toast).toBeDefined();
            expect(toast.textContent).toBe('Warning message');
        });
        
        it('should auto-remove toast after duration', async () => {
            sharedUtils.showSuccessToast('Test', 100);
            
            let toast = document.querySelector('.toast-success');
            expect(toast).toBeDefined();
            
            // Wait for auto-removal
            await new Promise(resolve => setTimeout(resolve, 500));
            
            toast = document.querySelector('.toast-success');
            expect(toast).toBeNull();
        });
    });
    
    describe('Loading Overlay', () => {
        it('should show loading overlay', () => {
            sharedUtils.showLoading('Loading data...');
            
            const overlay = document.querySelector('.loading-overlay');
            expect(overlay).toBeDefined();
            expect(overlay.style.display).toBe('flex');
        });
        
        it('should hide loading overlay', () => {
            sharedUtils.showLoading('Loading...');
            sharedUtils.hideLoading();
            
            const overlay = document.querySelector('.loading-overlay');
            expect(overlay.style.display).toBe('none');
        });
        
        it('should update loading message', () => {
            sharedUtils.showLoading('Initial message');
            
            const message1 = document.querySelector('.loading-message');
            expect(message1.textContent).toBe('Initial message');
            
            sharedUtils.showLoading('Updated message');
            
            const message2 = document.querySelector('.loading-message');
            expect(message2.textContent).toBe('Updated message');
        });
    });
    
    describe('DOM Utilities', () => {
        it('should create element with class', () => {
            const el = sharedUtils.createElement('div', 'test-class');
            
            expect(el.tagName).toBe('DIV');
            expect(el.className).toBe('test-class');
        });
        
        it('should create element with text content', () => {
            const el = sharedUtils.createElement('p', '', 'Test text');
            
            expect(el.textContent).toBe('Test text');
        });
        
        it('should clear element children', () => {
            const parent = document.createElement('div');
            parent.innerHTML = '<p>Child 1</p><p>Child 2</p>';
            
            sharedUtils.clearElement(parent);
            
            expect(parent.children.length).toBe(0);
        });
    });
    
    describe('Date Formatting', () => {
        it('should format date correctly', () => {
            const formatted = sharedUtils.formatDate('2024-12-04');
            expect(formatted).toMatch(/Dec 4, 2024/);
        });
        
        it('should format datetime correctly', () => {
            const formatted = sharedUtils.formatDateTime('2024-12-04T10:30:00Z');
            expect(formatted).toContain('Dec 4, 2024');
            expect(formatted).toMatch(/\d{1,2}:\d{2}/);
        });
    });
    
    describe('Number Formatting', () => {
        it('should format large numbers with commas', () => {
            expect(sharedUtils.formatNumber(1234567)).toBe('1,234,567');
        });
        
        it('should format percentages', () => {
            expect(sharedUtils.formatPercent(87.456)).toBe('87.5%');
            expect(sharedUtils.formatPercent(87.456, 2)).toBe('87.46%');
        });
    });
    
    describe('Data Validation', () => {
        it('should validate object data', () => {
            expect(sharedUtils.isValidData({ key: 'value' })).toBe(true);
            expect(sharedUtils.isValidData(null)).toBe(false);
            expect(sharedUtils.isValidData([])).toBe(false);
            expect(sharedUtils.isValidData('string')).toBe(false);
        });
        
        it('should check required fields', () => {
            const data = { name: 'Test', age: 30 };
            
            expect(sharedUtils.hasRequiredFields(data, ['name', 'age'])).toBe(true);
            expect(sharedUtils.hasRequiredFields(data, ['name', 'email'])).toBe(false);
        });
    });
    
    describe('Debounce and Throttle', () => {
        it('should debounce function calls', async () => {
            let callCount = 0;
            const fn = () => callCount++;
            const debounced = sharedUtils.debounce(fn, 100);
            
            debounced();
            debounced();
            debounced();
            
            expect(callCount).toBe(0);
            
            await new Promise(resolve => setTimeout(resolve, 150));
            
            expect(callCount).toBe(1);
        });
        
        it('should throttle function calls', async () => {
            let callCount = 0;
            const fn = () => callCount++;
            const throttled = sharedUtils.throttle(fn, 100);
            
            throttled();
            throttled();
            throttled();
            
            expect(callCount).toBe(1);
            
            await new Promise(resolve => setTimeout(resolve, 150));
            
            throttled();
            expect(callCount).toBe(2);
        });
    });
});
