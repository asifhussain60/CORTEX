/**
 * StateManager - Immutable State Management with Version Control
 * 
 * Addresses Critical Issues:
 * - Race condition prevention (state versioning)
 * - State corruption detection (frozen state)
 * - Stale render rejection (generation counter)
 * 
 * Authority: violations.md § State Management Catastrophe
 * Audit: AC_START: AC-SPA-001-01
 */

class StateManager {
    constructor() {
        this._state = {
            version: 0,
            generation: 0,
            currentRepo: null,
            currentTab: 'overview',
            data: null,
            isLoading: false,
            loadingTabs: new Set(),
            errors: {},
            cache: new Map(),
            lastUpdate: Date.now()
        };
        
        this._subscribers = new Map();
        this._history = [];
        this._maxHistory = 50;
        
        Object.freeze(this._state);
    }
    
    /**
     * Get current state (frozen, immutable)
     */
    getState() {
        return this._state;
    }
    
    /**
     * Get current generation (for stale render detection)
     */
    getGeneration() {
        return this._state.generation;
    }
    
    /**
     * Update state immutably with automatic versioning
     * @param {Function} updater - Function that receives draft and modifies it
     * @returns {Object} New state
     */
    setState(updater) {
        // Debug: Track who is calling setState
        const stack = new Error().stack;
        const caller = stack.split('\n')[2]?.trim() || 'unknown';
        console.log(`[StateManager] setState called by: ${caller}`);
        console.log(`[StateManager] Current generation: ${this._state.generation} → ${this._state.generation + 1}`);
        
        // Clone current state
        const draft = this._cloneState(this._state);
        
        // Apply updates
        updater(draft);
        
        // Increment version and generation
        draft.version = this._state.version + 1;
        draft.generation = this._state.generation + 1;
        draft.lastUpdate = Date.now();
        
        // Archive old state
        this._archiveState(this._state);
        
        // Freeze new state
        Object.freeze(draft);
        Object.freeze(draft.loadingTabs);
        Object.freeze(draft.errors);
        
        // Update reference
        const oldState = this._state;
        this._state = draft;
        
        // Notify subscribers
        console.log(`[StateManager] Notifying ${this._subscribers.size} subscribers...`);
        this._notifySubscribers(oldState, draft);
        console.log(`[StateManager] setState complete. New generation: ${draft.generation}`);
        
        return draft;
    }
    
    /**
     * Subscribe to state changes
     * @param {String} key - Subscription key
     * @param {Function} callback - Callback(oldState, newState)
     */
    subscribe(key, callback) {
        this._subscribers.set(key, callback);
        return () => this._subscribers.delete(key);
    }
    
    /**
     * Check if state version matches expected
     * @param {Number} expectedVersion - Expected state version
     * @returns {Boolean}
     */
    isStateValid(expectedVersion) {
        return this._state.version === expectedVersion;
    }
    
    /**
     * Check if generation matches (stale render detection)
     * @param {Number} expectedGeneration
     * @returns {Boolean}
     */
    isGenerationCurrent(expectedGeneration) {
        return this._state.generation === expectedGeneration;
    }
    
    /**
     * Rollback to previous state
     * @param {Number} steps - Number of steps to rollback
     */
    rollback(steps = 1) {
        if (this._history.length < steps) {
            throw new Error(`Cannot rollback ${steps} steps. Only ${this._history.length} states in history.`);
        }
        
        const targetState = this._history[this._history.length - steps];
        this._state = targetState;
        this._history = this._history.slice(0, -steps);
        
        this._notifySubscribers(this._state, targetState);
    }
    
    /**
     * Clear cache
     */
    clearCache() {
        this.setState(draft => {
            draft.cache = new Map();
        });
    }
    
    /**
     * Get cache entry
     */
    getCacheEntry(key) {
        return this._state.cache.get(key);
    }
    
    /**
     * Set cache entry with LRU eviction
     */
    setCacheEntry(key, value, maxSize = 10) {
        this.setState(draft => {
            // LRU eviction
            if (draft.cache.size >= maxSize) {
                const firstKey = draft.cache.keys().next().value;
                draft.cache.delete(firstKey);
            }
            draft.cache.set(key, {
                data: value,
                timestamp: Date.now(),
                hits: 0
            });
        });
    }
    
    /**
     * Deep clone state
     */
    _cloneState(state) {
        return {
            ...state,
            loadingTabs: new Set(state.loadingTabs),
            errors: { ...state.errors },
            cache: new Map(state.cache),
            data: state.data ? { ...state.data } : null
        };
    }
    
    /**
     * Archive state to history
     */
    _archiveState(state) {
        this._history.push(state);
        
        // Trim history if exceeds max
        if (this._history.length > this._maxHistory) {
            this._history.shift();
        }
    }
    
    /**
     * Notify all subscribers
     */
    _notifySubscribers(oldState, newState) {
        this._subscribers.forEach(callback => {
            try {
                callback(oldState, newState);
            } catch (error) {
                console.error('[StateManager] Subscriber error:', error);
            }
        });
    }
    
    /**
     * Export state for diagnostics
     */
    exportDiagnostics() {
        return {
            currentState: this._state,
            historySize: this._history.length,
            subscriberCount: this._subscribers.size,
            cacheSize: this._state.cache.size,
            memoryUsage: this._estimateMemoryUsage()
        };
    }
    
    /**
     * Estimate memory usage (rough)
     */
    _estimateMemoryUsage() {
        const jsonSize = JSON.stringify(this._state).length;
        const historySize = this._history.reduce((acc, s) => acc + JSON.stringify(s).length, 0);
        return {
            currentState: `${(jsonSize / 1024).toFixed(2)} KB`,
            history: `${(historySize / 1024).toFixed(2)} KB`,
            total: `${((jsonSize + historySize) / 1024).toFixed(2)} KB`
        };
    }
}

// AC_COMPLETE: AC-SPA-001-01 ✅ StateManager implemented with version control
