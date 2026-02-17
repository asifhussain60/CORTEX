/**
 * StateManager Test Suite
 * 
 * Tests immutable state management with version control,
 * stale render prevention, and race condition handling.
 * 
 * TDD Pattern: RED → GREEN → REFACTOR
 * Authority: CORE-008 (TDD mandatory)
 */

describe('StateManager', () => {
    let stateManager;

    beforeEach(() => {
        stateManager = new StateManager();
    });

    describe('Initialization', () => {
        it('should initialize with default state', () => {
            const state = stateManager.getState();
            expect(state.version).toBe(0);
            expect(state.generation).toBe(0);
            expect(state.currentRepo).toBeNull();
            expect(state.currentTab).toBe('overview');
        });

        it('should freeze initial state (immutability)', () => {
            const state = stateManager.getState();
            expect(() => {
                state.currentRepo = 'modified';
            }).toThrow();
        });

        it('should initialize empty history', () => {
            expect(stateManager._history.length).toBe(0);
        });
    });

    describe('State Mutation', () => {
        it('should create new frozen state on mutation', () => {
            const oldState = stateManager.getState();
            stateManager.setState({ currentRepo: 'test-repo' });
            const newState = stateManager.getState();

            expect(oldState).not.toBe(newState);
            expect(newState.currentRepo).toBe('test-repo');
            expect(() => {
                newState.currentRepo = 'modified';
            }).toThrow();
        });

        it('should increment version on mutation', () => {
            expect(stateManager.getState().version).toBe(0);
            stateManager.setState({ currentRepo: 'repo1' });
            expect(stateManager.getState().version).toBe(1);
        });

        it('should increment generation on mutation', () => {
            expect(stateManager.getGeneration()).toBe(0);
            stateManager.setState({ currentRepo: 'repo1' });
            expect(stateManager.getGeneration()).toBe(1);
        });

        it('should preserve unmodified properties', () => {
            stateManager.setState({ currentRepo: 'repo1' });
            const state1 = stateManager.getState();
            
            stateManager.setState({ currentTab: 'duplication' });
            const state2 = stateManager.getState();

            expect(state2.currentRepo).toBe('repo1');
            expect(state2.currentTab).toBe('duplication');
        });
    });

    describe('Stale Render Detection', () => {
        it('should detect stale renders with old generation', () => {
            const gen1 = stateManager.getGeneration();
            stateManager.setState({ currentTab: 'security' });
            const gen2 = stateManager.getGeneration();

            expect(stateManager.isStaleRender(gen1)).toBe(true);
            expect(stateManager.isStaleRender(gen2)).toBe(false);
        });

        it('should accept current or newer generations', () => {
            stateManager.setState({ currentTab: 'security' });
            const currentGen = stateManager.getGeneration();

            expect(stateManager.isStaleRender(currentGen)).toBe(false);
            expect(stateManager.isStaleRender(currentGen + 100)).toBe(false);
        });
    });

    describe('Caching', () => {
        it('should cache values', () => {
            stateManager.setCache('testKey', 'testValue');
            expect(stateManager.getCache('testKey')).toBe('testValue');
        });

        it('should respect TTL for cached items', async () => {
            stateManager.setCache('key', 'value', 100); // 100ms TTL
            expect(stateManager.getCache('key')).toBe('value');

            await new Promise(resolve => setTimeout(resolve, 150));
            expect(stateManager.getCache('key')).toBeNull();
        });

        it('should handle LRU eviction at capacity', () => {
            // Fill cache to capacity (10 items)
            for (let i = 0; i < 10; i++) {
                stateManager.setCache(`key${i}`, `value${i}`);
            }

            // Add 11th item (should evict oldest)
            stateManager.setCache('key10', 'value10');

            // key0 should be evicted (oldest)
            expect(stateManager.getCache('key0')).toBeNull();
            expect(stateManager.getCache('key10')).toBe('value10');
        });

        it('should clear cache', () => {
            stateManager.setCache('key1', 'value1');
            stateManager.setCache('key2', 'value2');
            stateManager.clearCache();

            expect(stateManager.getCache('key1')).toBeNull();
            expect(stateManager.getCache('key2')).toBeNull();
        });
    });

    describe('State History', () => {
        it('should maintain state history', () => {
            stateManager.setState({ currentRepo: 'repo1' });
            stateManager.setState({ currentTab: 'security' });

            const history = stateManager.getHistory();
            expect(history.length).toBe(2);
            expect(history[0].currentRepo).toBe('repo1');
            expect(history[1].currentTab).toBe('security');
        });

        it('should limit history to max items (50)', () => {
            for (let i = 0; i < 60; i++) {
                stateManager.setState({ version: i });
            }

            const history = stateManager.getHistory();
            expect(history.length).toBeLessThanOrEqual(50);
        });

        it('should allow reverting to previous state', () => {
            stateManager.setState({ currentRepo: 'repo1' });
            const version1 = stateManager.getState().version;

            stateManager.setState({ currentRepo: 'repo2' });
            expect(stateManager.getState().currentRepo).toBe('repo2');

            stateManager.revertToVersion(version1);
            expect(stateManager.getState().currentRepo).toBe('repo1');
        });

        it('should throw on invalid revert version', () => {
            expect(() => {
                stateManager.revertToVersion(999);
            }).toThrow();
        });
    });

    describe('Subscribers', () => {
        it('should notify subscribers on state change', () => {
            const callback = jest.fn();
            stateManager.subscribe('test', callback);

            stateManager.setState({ currentRepo: 'repo1' });

            expect(callback).toHaveBeenCalled();
            expect(callback).toHaveBeenCalledWith(
                expect.objectContaining({ currentRepo: 'repo1' })
            );
        });

        it('should support multiple subscribers', () => {
            const callback1 = jest.fn();
            const callback2 = jest.fn();

            stateManager.subscribe('sub1', callback1);
            stateManager.subscribe('sub2', callback2);

            stateManager.setState({ currentRepo: 'repo1' });

            expect(callback1).toHaveBeenCalled();
            expect(callback2).toHaveBeenCalled();
        });

        it('should unsubscribe', () => {
            const callback = jest.fn();
            stateManager.subscribe('test', callback);
            stateManager.unsubscribe('test');

            stateManager.setState({ currentRepo: 'repo1' });

            expect(callback).not.toHaveBeenCalled();
        });

        it('should handle errors in subscriber callbacks', () => {
            const errorCallback = jest.fn(() => {
                throw new Error('Subscriber error');
            });
            const normalCallback = jest.fn();

            stateManager.subscribe('error', errorCallback);
            stateManager.subscribe('normal', normalCallback);

            expect(() => {
                stateManager.setState({ currentRepo: 'repo1' });
            }).not.toThrow();

            expect(errorCallback).toHaveBeenCalled();
            expect(normalCallback).toHaveBeenCalled();
        });
    });

    describe('Race Condition Prevention', () => {
        it('should handle concurrent mutations safely', () => {
            const promises = [];
            for (let i = 0; i < 10; i++) {
                promises.push(
                    Promise.resolve().then(() => {
                        stateManager.setState({ version: i });
                    })
                );
            }

            return Promise.all(promises).then(() => {
                expect(stateManager.getState().version).toBeDefined();
                const state = stateManager.getState();
                expect(() => {
                    state.version = 'modified';
                }).toThrow();
            });
        });

        it('should maintain state consistency with getState calls', () => {
            const state1 = stateManager.getState();
            stateManager.setState({ currentRepo: 'repo1' });
            const state2 = stateManager.getState();
            
            // Old state should not be modified
            expect(state1.currentRepo).toBeNull();
            expect(state2.currentRepo).toBe('repo1');
        });
    });
});
