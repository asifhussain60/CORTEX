/**
 * DashboardControllerWithComponents - Enhanced DashboardController with modular components
 * 
 * Purpose:
 * - Integrates TabNavigationOrchestrator for component-based rendering
 * - Replaces monolithic visualization rendering with modular components
 * - Maintains backward compatibility with existing controller
 * - Adds proper error handling and lifecycle management
 * 
 * Authority: Phase 48 Holistic Validation Gate
 * Inherits from: DashboardController
 */

class DashboardControllerWithComponents extends DashboardController {
    constructor() {
        super();
        this.tabOrchestrator = null;
    }

    /**
     * Initialize with tab orchestration
     */
    async initialize(services) {
        // Call parent initialization first
        await super.initialize(services);

        // Initialize tab orchestrator
        this._initializeTabOrchestrator();
    }

    /**
     * Set up tab orchestrator with all components
     * @private
     */
    _initializeTabOrchestrator() {
        this.tabOrchestrator = new TabNavigationOrchestrator({
            lazyLoad: true,
            cacheComponents: true
        });

        // Register all 6 tabs with their components
        this.tabOrchestrator.registerTab(
            'overview',
            'Overview',
            OverviewComponent,
            'viz-overview'
        );

        this.tabOrchestrator.registerTab(
            'architecture',
            'Architecture',
            ArchitectureComponent,
            'viz-architecture'
        );

        this.tabOrchestrator.registerTab(
            'quality',
            'Quality',
            QualityComponent,
            'viz-quality'
        );

        this.tabOrchestrator.registerTab(
            'security',
            'Security',
            SecurityComponent,
            'viz-security'
        );

        this.tabOrchestrator.registerTab(
            'dependencies',
            'Dependencies',
            DependencyComponent,
            'viz-dependencies'
        );

        this.tabOrchestrator.registerTab(
            'usecases',
            'Use Cases',
            UseCaseComponent,
            'viz-usecases'
        );

        // Initialize all tab DOM references
        this.tabOrchestrator.initialize();

        console.log('[Controller] Tab orchestrator initialized with 6 components');
    }

    /**
     * Enhanced render current tab using components
     * @protected
     * @override
     */
    async _renderCurrentTab(data) {
        if (!this.tabOrchestrator) {
            // Fallback to parent implementation if orchestrator not initialized
            return super._renderCurrentTab(data);
        }

        const tabId = this.state.currentTab;

        try {
            await this.errorBoundary.wrap(
                `render_tab_${tabId}`,
                async () => {
                    console.log(`[Controller] Rendering tab: ${tabId}`);

                    // Use tab orchestrator to switch and render
                    await this.tabOrchestrator.switchTab(tabId, data);

                    console.log(`[Controller] ✓ Tab ${tabId} rendered successfully`);
                },
                { tabId }
            );
        } catch (error) {
            console.error(`[Controller] Error rendering tab ${tabId}:`, error);
            this._showRenderError(tabId, error);
        }
    }

    /**
     * Show render error in UI
     * @private
     */
    _showRenderError(tabId, error) {
        const container = document.getElementById(`viz-${tabId}`);
        if (!container) return;

        container.innerHTML = `
            <div class="viz-error-state" style="
                padding: 40px 20px;
                text-align: center;
                background: rgba(220, 53, 69, 0.1);
                border: 1px solid rgba(220, 53, 69, 0.3);
                border-radius: 8px;
                color: #dc3545;
            ">
                <i class="fas fa-exclamation-triangle" style="font-size: 2em; margin-bottom: 10px; display: block;"></i>
                <h3>Render Error</h3>
                <p>${error.message || 'Failed to render tab'}</p>
                <button onclick="location.reload()" style="
                    background: #dc3545;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    margin-top: 10px;
                ">Reload Dashboard</button>
            </div>
        `;
    }

    /**
     * Override destroy to clean up orchestrator
     * @protected
     * @override
     */
    destroy() {
        if (this.tabOrchestrator) {
            this.tabOrchestrator.destroyAll();
        }

        super.destroy();
    }

    /**
     * Export enhanced diagnostics
     * @override
     */
    exportDiagnostics() {
        const baseDiags = super.exportDiagnostics();

        return {
            ...baseDiags,
            tabOrchestrator: this.tabOrchestrator
                ? this.tabOrchestrator.exportDiagnostics()
                : null
        };
    }
}

// AC_COMPLETE: AC-DASHBOARD-COMPONENTS-005 ✅ Enhanced controller with components
