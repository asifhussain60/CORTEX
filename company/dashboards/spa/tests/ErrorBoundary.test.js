/**
 * ErrorBoundary Test Suite
 * 
 * Tests fault tolerance, retry logic, timeout handling,
 * and error recovery mechanisms.
 * 
 * TDD Pattern: RED → GREEN → REFACTOR
 * Authority: CORE-008 (TDD mandatory)
 */

describe('ErrorBoundary', () => {
    let errorBoundary;
    let mockStateManager;

    beforeEach(() => {
        mockStateManager = {
            setState: jest.fn(),
            getState: jest.fn(() => ({
                errors: {},
                isLoading: false
            }))
        };
        errorBoundary = new ErrorBoundary(mockStateManager);
    });

    describe('Initialization', () => {
        it('should initialize with state manager', () => {
            expect(errorBoundary.stateManager).toBe(mockStateManager);
        });

        it('should initialize error tracking', () => {
            expect(errorBoundary.errors).toEqual({});
        });
    });

    describe('Error Catching', () => {
        it('should catch errors and update state', () => {
            const error = new Error('Test error');
            errorBoundary.catch('test-component', error);

            expect(mockStateManager.setState).toHaveBeenCalledWith(
                expect.objectContaining({
                    errors: expect.objectContaining({
                        'test-component': expect.any(Object)
                    })
                })
            );
        });

        it('should record error timestamp', () => {
            const error = new Error('Test error');
            const before = Date.now();
            errorBoundary.catch('test-component', error);
            const after = Date.now();

            const errorRecord = errorBoundary.errors['test-component'];
            expect(errorRecord.timestamp).toBeGreaterThanOrEqual(before);
            expect(errorRecord.timestamp).toBeLessThanOrEqual(after);
        });

        it('should increment retry count on same error', () => {
            const error = new Error('Test error');
            errorBoundary.catch('test-component', error);
            errorBoundary.catch('test-component', error);

            expect(errorBoundary.errors['test-component'].retries).toBe(1);
        });

        it('should store error message and stack', () => {
            const error = new Error('Test error message');
            errorBoundary.catch('test-component', error);

            const errorRecord = errorBoundary.errors['test-component'];
            expect(errorRecord.message).toBe('Test error message');
            expect(errorRecord.stack).toBeDefined();
        });
    });

    describe('Retry Logic', () => {
        it('should allow retry with exponential backoff', async () => {
            let attempt = 0;
            const task = jest.fn(() => {
                attempt++;
                if (attempt < 3) {
                    throw new Error('Failed');
                }
                return 'Success';
            });

            const startTime = Date.now();
            const result = await errorBoundary.retryWithBackoff(
                'test-op',
                task,
                { maxRetries: 3, baseDelay: 10 }
            );
            const duration = Date.now() - startTime;

            expect(result).toBe('Success');
            expect(task).toHaveBeenCalledTimes(3);
            expect(duration).toBeGreaterThan(20); // 10 + 20 = 30ms total
        });

        it('should throw after max retries exceeded', async () => {
            const task = jest.fn(() => {
                throw new Error('Always fails');
            });

            await expect(
                errorBoundary.retryWithBackoff('test-op', task, {
                    maxRetries: 2,
                    baseDelay: 10
                })
            ).rejects.toThrow('Always fails');

            expect(task).toHaveBeenCalledTimes(3); // Initial + 2 retries
        });

        it('should not retry on non-retriable errors', async () => {
            const error = new Error('Non-retriable');
            error.retriable = false;

            const task = jest.fn(() => {
                throw error;
            });

            await expect(
                errorBoundary.retryWithBackoff('test-op', task)
            ).rejects.toThrow('Non-retriable');

            expect(task).toHaveBeenCalledTimes(1);
        });
    });

    describe('Timeout Protection', () => {
        it('should timeout long-running operations', async () => {
            const slowTask = jest.fn(() =>
                new Promise(resolve => setTimeout(resolve, 1000))
            );

            await expect(
                errorBoundary.withTimeout('slow-op', slowTask, 100)
            ).rejects.toThrow('timeout');

            expect(slowTask).toHaveBeenCalled();
        });

        it('should complete fast operations without timeout', async () => {
            const fastTask = jest.fn(() =>
                Promise.resolve('Quick result')
            );

            const result = await errorBoundary.withTimeout(
                'fast-op',
                fastTask,
                1000
            );

            expect(result).toBe('Quick result');
        });

        it('should handle timeout with custom message', async () => {
            const slowTask = () =>
                new Promise(resolve => setTimeout(resolve, 1000));

            await expect(
                errorBoundary.withTimeout('op', slowTask, 100, 'Custom timeout message')
            ).rejects.toThrow('Custom timeout message');
        });
    });

    describe('Fallback UI Rendering', () => {
        it('should generate error UI element', () => {
            const error = new Error('Component failed');
            const ui = errorBoundary.getFallbackUI('test-component', error);

            expect(ui).toBeInstanceOf(HTMLElement);
            expect(ui.textContent).toContain('Component failed');
        });

        it('should include retry button in fallback UI', () => {
            const error = new Error('Component failed');
            const ui = errorBoundary.getFallbackUI('test-component', error);

            const retryButton = ui.querySelector('[data-action="retry"]');
            expect(retryButton).toBeDefined();
        });

        it('should include error details in UI', () => {
            const error = new Error('Detailed error');
            error.details = { code: 'ERR_001', status: 500 };
            
            const ui = errorBoundary.getFallbackUI('test-component', error);

            expect(ui.textContent).toContain('ERR_001');
            expect(ui.textContent).toContain('500');
        });

        it('should provide dismiss action', () => {
            const error = new Error('Component failed');
            const ui = errorBoundary.getFallbackUI('test-component', error);

            const dismissButton = ui.querySelector('[data-action="dismiss"]');
            expect(dismissButton).toBeDefined();
        });
    });

    describe('Telemetry', () => {
        it('should record errors to telemetry', () => {
            const error = new Error('Test error');
            errorBoundary.catch('test-component', error);

            const telemetry = errorBoundary.getTelemetry();
            expect(telemetry['test-component']).toBeDefined();
            expect(telemetry['test-component'].count).toBeGreaterThan(0);
        });

        it('should track error frequency', () => {
            const error = new Error('Test error');
            for (let i = 0; i < 5; i++) {
                errorBoundary.catch('test-component', error);
            }

            const telemetry = errorBoundary.getTelemetry();
            expect(telemetry['test-component'].count).toBe(5);
        });

        it('should persist telemetry to localStorage', () => {
            const error = new Error('Test error');
            errorBoundary.catch('test-component', error);

            const stored = JSON.parse(localStorage.getItem('cortex.telemetry.errors'));
            expect(stored['test-component']).toBeDefined();
        });

        it('should clear telemetry', () => {
            errorBoundary.catch('test-component', new Error('Error'));
            errorBoundary.clearTelemetry();

            expect(errorBoundary.getTelemetry()).toEqual({});
        });
    });

    describe('Recovery', () => {
        it('should recover from error state', () => {
            const error = new Error('Component error');
            errorBoundary.catch('test-component', error);

            expect(errorBoundary.hasError('test-component')).toBe(true);

            errorBoundary.recover('test-component');

            expect(errorBoundary.hasError('test-component')).toBe(false);
        });

        it('should clear error from state', () => {
            errorBoundary.catch('test-component', new Error('Error'));
            errorBoundary.recover('test-component');

            expect(mockStateManager.setState).toHaveBeenLastCalledWith(
                expect.objectContaining({
                    errors: {}
                })
            );
        });

        it('should support batch recovery', () => {
            errorBoundary.catch('comp1', new Error('Error 1'));
            errorBoundary.catch('comp2', new Error('Error 2'));

            errorBoundary.recoverAll();

            expect(errorBoundary.hasError('comp1')).toBe(false);
            expect(errorBoundary.hasError('comp2')).toBe(false);
        });
    });

    describe('Context Propagation', () => {
        it('should preserve error context through recovery', () => {
            const error = new Error('Test error');
            error.context = { userId: 123, action: 'load' };

            errorBoundary.catch('test-component', error);
            const errorRecord = errorBoundary.errors['test-component'];

            expect(errorRecord.context).toEqual({
                userId: 123,
                action: 'load'
            });
        });

        it('should propagate root cause chain', () => {
            const rootError = new Error('Root cause');
            const chainedError = new Error('Wrapped error');
            chainedError.originalError = rootError;

            errorBoundary.catch('test-component', chainedError);
            const errorRecord = errorBoundary.errors['test-component'];

            expect(errorRecord.originalError).toBe(rootError);
        });
    });

    describe('Integration with Multiple Components', () => {
        it('should handle errors from multiple components independently', () => {
            errorBoundary.catch('comp1', new Error('Error 1'));
            errorBoundary.catch('comp2', new Error('Error 2'));

            expect(errorBoundary.hasError('comp1')).toBe(true);
            expect(errorBoundary.hasError('comp2')).toBe(true);

            errorBoundary.recover('comp1');

            expect(errorBoundary.hasError('comp1')).toBe(false);
            expect(errorBoundary.hasError('comp2')).toBe(true);
        });

        it('should isolate error recovery', () => {
            const error1 = new Error('Error 1');
            const error2 = new Error('Error 2');

            errorBoundary.catch('comp1', error1);
            errorBoundary.catch('comp2', error2);

            const ui1 = errorBoundary.getFallbackUI('comp1', error1);
            const ui2 = errorBoundary.getFallbackUI('comp2', error2);

            expect(ui1.textContent).toContain('Error 1');
            expect(ui2.textContent).toContain('Error 2');
        });
    });
});
