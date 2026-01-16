/**
 * Main App Initialization
 * Initializes CORTEX Neural Observatory
 */

document.addEventListener('DOMContentLoaded', () => {
    console.log('✓ CORTEX Neural Observatory initializing');
    
    // Initialize common UI components (DO-001-01, DO-001-04, DO-002-01, DO-002-02)
    initializeLogoComponent();
    initializeHamburgerMenu();
    initializeSidebar();
    initializeTabSwitcher();
    
    // Verify API connectivity
    api.get('/api/health')
        .then(response => {
            console.log('✓ Connected to API on port 8000');
            
            // Load all dashboard components with error handling
            Promise.allSettled([
                renderBrainTiers().catch(e => {
                    console.error('⚠️ Brain map failed:', e);
                    document.getElementById('brain-map').innerHTML = '<div class="text-amber-400 p-4">Unable to load brain visualization</div>';
                }),
                updateNeuralPulse().catch(e => {
                    console.error('⚠️ Neural pulse failed:', e);
                }),
                renderAuditTimeline().catch(e => {
                    console.error('⚠️ Audit timeline failed:', e);
                    document.getElementById('audit-list').innerHTML = '<div class="text-amber-400 p-4">Unable to load audit timeline</div>';
                }),
                renderOrchestratorGrid().catch(e => {
                    console.error('⚠️ Orchestrator grid failed:', e);
                    document.getElementById('orchestrator-grid').innerHTML = '<div class="text-amber-400 p-4">Unable to load orchestrator status</div>';
                })
            ]).then(() => {
                console.log('✓ All dashboard components loaded');
            });
        })
        .catch(error => {
            console.error('✗ Cannot connect to API backend on port 8000');
            console.error('Details:', error.message);
            console.log('');
            console.log('🔧 Fix: Start FastAPI backend with:');
            console.log('   python -m uvicorn src.dashboard.api.main:app --host 0.0.0.0 --port 8000 --reload');
            console.log('');
            
            // Show offline message
            document.body.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: center; min-height: 100vh; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);">
                    <div style="text-align: center; color: #e2e8f0; font-family: Inter, sans-serif;">
                        <div style="font-size: 48px; margin-bottom: 16px;">⚠️</div>
                        <h1 style="font-size: 24px; font-weight: bold; margin-bottom: 8px;">Backend Offline</h1>
                        <p style="font-size: 14px; opacity: 0.75; margin-bottom: 24px;">FastAPI server is not running on port 8000</p>
                        <p style="font-size: 12px; opacity: 0.5; font-family: monospace;">Run: python -m uvicorn src.dashboard.api.main:app --port 8000 --reload</p>
                    </div>
                </div>
            `;
        });
});
