/**
 * AuditLogger.js
 * Structured logging for dashboard operations with performance tracking
 * 
 * Purpose: Comprehensive observability for debugging dashboard issues
 * Author: Asif Hussain
 * Date: 2026-02-08
 * Authority: Dashboard Fix - Phase 53 (NEW)
 */

class AuditLogger {
    constructor() {
        this.logs = [];
        this.errors = [];
        this.metrics = {
            dataLoad: null,
            renderCycles: [],
            domMutations: []
        };
        this.sessionId = this._generateSessionId();
        this.startTime = performance.now();
        
        console.log('📝 [AuditLogger] Initialized', {
            sessionId: this.sessionId,
            timestamp: new Date().toISOString()
        });
    }
    
    /**
     * Generate unique session ID
     * @returns {string} Session ID
     */
    _generateSessionId() {
        return `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }
    
    /**
     * Log data loading event
     * @param {Object} data - Data object or metadata
     * @param {string} source - Source of data (embedded|http|cache)
     * @param {number} duration - Load duration in ms
     */
    logDataLoad(data, source, duration) {
        const entry = {
            type: 'data-load',
            timestamp: new Date().toISOString(),
            elapsed: (performance.now() - this.startTime).toFixed(2),
            source,
            duration: duration.toFixed(2),
            size: JSON.stringify(data).length,
            hasRepo: !!data.repository_name,
            hasMetrics: !!data.metrics,
            hasSecurity: !!data.security,
            schemaCompliance: this._validateSchema(data)
        };
        
        this.logs.push(entry);
        this.metrics.dataLoad = entry;
        
        console.log('📊 [AuditLogger] Data Load:', entry);
        performance.mark('data-load-complete');
    }
    
    /**
     * Validate data schema compliance
     * @param {Object} data - Data to validate
     * @returns {Object} Validation result
     */
    _validateSchema(data) {
        const required = ['repository_name', 'overview', 'metrics'];
        const missing = required.filter(key => !data[key]);
        
        return {
            valid: missing.length === 0,
            missing,
            score: ((required.length - missing.length) / required.length * 100).toFixed(1)
        };
    }
    
    /**
     * Log render cycle for tab/section
     * @param {string} target - Tab or section name
     * @param {boolean} success - Render success
     * @param {number} duration - Render duration in ms
     * @param {Object} metadata - Additional metadata
     */
    logRenderCycle(target, success, duration, metadata = {}) {
        const entry = {
            type: 'render',
            timestamp: new Date().toISOString(),
            elapsed: (performance.now() - this.startTime).toFixed(2),
            target,
            success,
            duration: duration.toFixed(2),
            ...metadata
        };
        
        this.logs.push(entry);
        this.metrics.renderCycles.push(entry);
        
        const icon = success ? '✅' : '❌';
        console.log(`${icon} [AuditLogger] Render:`, entry);
        performance.mark(`render-${target}-${success ? 'success' : 'fail'}`);
    }
    
    /**
     * Log DOM mutation event
     * @param {string} type - Mutation type (add|remove|update)
     * @param {string} target - Target element
     * @param {Object} details - Mutation details
     */
    logDOMMutation(type, target, details = {}) {
        const entry = {
            type: 'dom-mutation',
            timestamp: new Date().toISOString(),
            elapsed: (performance.now() - this.startTime).toFixed(2),
            mutationType: type,
            target,
            ...details
        };
        
        this.logs.push(entry);
        this.metrics.domMutations.push(entry);
        
        console.log('🔄 [AuditLogger] DOM Mutation:', entry);
    }
    
    /**
     * Log error with context
     * @param {string} source - Error source (data-load|render|dom)
     * @param {Error} error - Error object
     * @param {Object} context - Additional context
     */
    logError(source, error, context = {}) {
        const entry = {
            type: 'error',
            timestamp: new Date().toISOString(),
            elapsed: (performance.now() - this.startTime).toFixed(2),
            source,
            message: error.message,
            stack: error.stack,
            ...context
        };
        
        this.logs.push(entry);
        this.errors.push(entry);
        
        console.error('🚨 [AuditLogger] Error:', entry);
    }
    
    /**
     * Log performance metric
     * @param {string} metric - Metric name
     * @param {number} value - Metric value
     * @param {string} unit - Unit (ms|bytes|count)
     */
    logMetric(metric, value, unit = 'ms') {
        const entry = {
            type: 'metric',
            timestamp: new Date().toISOString(),
            elapsed: (performance.now() - this.startTime).toFixed(2),
            metric,
            value,
            unit
        };
        
        this.logs.push(entry);
        console.log('📈 [AuditLogger] Metric:', entry);
    }
    
    /**
     * Export audit trail as JSON
     * @returns {Object} Complete audit trail
     */
    exportAuditTrail() {
        const trail = {
            sessionId: this.sessionId,
            startTime: new Date(this.startTime).toISOString(),
            duration: (performance.now() - this.startTime).toFixed(2),
            summary: {
                totalLogs: this.logs.length,
                totalErrors: this.errors.length,
                renderCycles: this.metrics.renderCycles.length,
                domMutations: this.metrics.domMutations.length,
                errorRate: ((this.errors.length / this.logs.length) * 100).toFixed(1)
            },
            metrics: this.metrics,
            logs: this.logs,
            errors: this.errors
        };
        
        console.log('📦 [AuditLogger] Audit Trail:', trail);
        return trail;
    }
    
    /**
     * Display audit summary in console
     */
    displaySummary() {
        const summary = {
            'Session ID': this.sessionId,
            'Duration (ms)': (performance.now() - this.startTime).toFixed(2),
            'Total Logs': this.logs.length,
            'Errors': this.errors.length,
            'Render Cycles': this.metrics.renderCycles.length,
            'DOM Mutations': this.metrics.domMutations.length,
            'Data Load Time (ms)': this.metrics.dataLoad?.duration || 'N/A',
            'Schema Compliance': this.metrics.dataLoad?.schemaCompliance.score || 'N/A'
        };
        
        console.group('📊 [AuditLogger] Session Summary');
        console.table(summary);
        
        if (this.errors.length > 0) {
            console.group('🚨 Errors');
            console.table(this.errors.map(e => ({
                Source: e.source,
                Message: e.message,
                Elapsed: e.elapsed
            })));
            console.groupEnd();
        }
        
        console.groupEnd();
    }
    
    /**
     * Measure performance for a function
     * @param {string} label - Performance label
     * @param {Function} fn - Function to measure
     * @returns {*} Function result
     */
    async measure(label, fn) {
        const start = performance.now();
        performance.mark(`${label}-start`);
        
        try {
            const result = await fn();
            const duration = performance.now() - start;
            
            performance.mark(`${label}-end`);
            performance.measure(label, `${label}-start`, `${label}-end`);
            
            this.logMetric(label, duration, 'ms');
            console.log(`⏱️ [AuditLogger] ${label}: ${duration.toFixed(2)}ms`);
            
            return result;
        } catch (error) {
            const duration = performance.now() - start;
            this.logError(label, error, { duration });
            throw error;
        }
    }
}

// Export for use in dashboard
window.AuditLogger = AuditLogger;
