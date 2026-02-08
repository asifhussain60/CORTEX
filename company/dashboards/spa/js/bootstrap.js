/**
 * Bootstrap - Application Entry Point with Dependency Injection
 * 
 * Architecture Pattern: Constructor Injection + Factory
 * 
 * Authority: violations.md § SOLID Principles & Dependency Inversion
 * Audit: AC_START: AC-SPA-001-06
 */

(async function bootstrapDashboard() {
    'use strict';
    
    console.log('[Bootstrap] Starting CORTEX Dashboard...');
    
    try {
        // ====================================================================
        // PHASE 1: Create Service Instances
        // ====================================================================
        
        const errorBoundary = new ErrorBoundary({
            maxRetries: 3,
            retryDelay: 1000,
            timeout: 5000,
            onError: (error, componentId) => {
                console.error(`[ErrorBoundary] ${componentId}:`, error);
            }
        });
        
        const stateManager = new StateManager();
        
        const validationService = new ValidationService();
        
        const repositoryService = new RepositoryService(errorBoundary);
        
        const controller = new DashboardController();
        
        console.log('[Bootstrap] Services created ✓');
        
        // ====================================================================
        // PHASE 2: Register Embedded Data (file:// protocol support)
        // ====================================================================
        
        const embeddedDataScripts = document.querySelectorAll('script[data-repo-data]');
        embeddedDataScripts.forEach(script => {
            try {
                const repoName = script.dataset.repoData;
                const data = JSON.parse(script.textContent);
                repositoryService.registerEmbeddedData(repoName, data);
                console.log(`[Bootstrap] Embedded data registered: ${repoName}`);
            } catch (e) {
                console.warn('[Bootstrap] Failed to parse embedded data:', e);
            }
        });
        
        // ====================================================================
        // PHASE 3: Initialize Controller with Dependencies
        // ====================================================================
        
        await controller.initialize({
            errorBoundary,
            stateManager,
            repositoryService,
            validationService
        });
        
        console.log('[Bootstrap] Controller initialized ✓');
        
        // ====================================================================
        // PHASE 4: Expose Global API
        // ====================================================================
        
        window.dashboardController = controller;
        window.dashboardState = stateManager;
        window.dashboardDiagnostics = () => controller.exportDiagnostics();
        
        console.log('[Bootstrap] Dashboard ready ✓');
        
        // ====================================================================
        // PHASE 5: Setup Global Error Handler
        // ====================================================================
        
        window.addEventListener('error', (event) => {
            console.error('[Global Error]', event.error);
            errorBoundary.wrapSync(
                'global',
                () => { throw event.error; },
                { message: event.message, filename: event.filename, lineno: event.lineno }
            );
        });
        
        window.addEventListener('unhandledrejection', (event) => {
            console.error('[Unhandled Rejection]', event.reason);
            errorBoundary.wrapSync(
                'promise',
                () => { throw event.reason; },
                { promise: event.promise }
            );
        });
        
        // ====================================================================
        // PHASE 6: Cleanup on Unload
        // ====================================================================
        
        window.addEventListener('beforeunload', () => {
            console.log('[Bootstrap] Cleanup...');
            repositoryService.cancelAll();
        });
        
        // ====================================================================
        // DEVELOPMENT HELPERS
        // ====================================================================
        
        if (window.location.hostname === 'localhost' || window.location.protocol === 'file:') {
            console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
            console.log('🚀 CORTEX Dashboard Development Mode');
            console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
            console.log('');
            console.log('Available Commands:');
            console.log('  window.dashboardDiagnostics()  - Export diagnostics');
            console.log('  window.dashboardState          - Access state manager');
            console.log('  window.dashboardController     - Access controller');
            console.log('');
            console.log('State Management:');
            console.log('  - Immutable state with versioning ✓');
            console.log('  - Race condition prevention ✓');
            console.log('  - Stale render rejection ✓');
            console.log('');
            console.log('Error Handling:');
            console.log('  - Component error boundaries ✓');
            console.log('  - Retry logic (3x exponential backoff) ✓');
            console.log('  - Timeout protection (5s) ✓');
            console.log('');
            console.log('Security:');
            console.log('  - XSS protection (HTML sanitization) ✓');
            console.log('  - Data validation before render ✓');
            console.log('  - Trust boundary enforcement ✓');
            console.log('');
            console.log('Performance:');
            console.log('  - Lazy tab loading ✓');
            console.log('  - Request deduplication ✓');
            console.log('  - LRU cache (10 items, 5min TTL) ✓');
            console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        }
        
    } catch (error) {
        console.error('[Bootstrap] Fatal error:', error);
        
        // Show fatal error UI
        document.body.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100vh; font-family: 'Inter', sans-serif; background: #0a0e27;">
                <div style="text-align: center; max-width: 500px; padding: 2rem;">
                    <div style="font-size: 4rem; color: #ef4444; margin-bottom: 1rem;">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                    <h1 style="color: #fff; margin-bottom: 1rem;">Dashboard Initialization Failed</h1>
                    <p style="color: #9ca3af; margin-bottom: 2rem;">
                        Unable to start the dashboard. Please check the console for details.
                    </p>
                    <button onclick="location.reload()" style="background: #3b82f6; color: #fff; border: none; padding: 0.75rem 1.5rem; border-radius: 0.5rem; cursor: pointer; font-size: 1rem;">
                        <i class="fas fa-redo"></i> Retry
                    </button>
                    <pre style="margin-top: 2rem; padding: 1rem; background: #1e293b; border-radius: 0.5rem; color: #ef4444; text-align: left; overflow: auto; max-height: 200px; font-size: 0.875rem;">
${error.stack || error.message}
                    </pre>
                </div>
            </div>
        `;
    }
})();

// AC_COMPLETE: AC-SPA-001-06 ✅ Bootstrap with dependency injection
