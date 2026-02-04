/**
 * Orchestrator Grid Component
 * NO-003-01: Orchestrator Status Grid
 * Grid view of all orchestrators with real-time status
 */

async function renderOrchestratorGrid() {
    const grid = document.getElementById('orchestrator-grid');
    
    try {
        const data = await api.getOrchestrators();
        
        grid.innerHTML = data.orchestrators.map(orchestrator => `
            <div class="glass-panel">
                <div class="flex items-center justify-between mb-4">
                    <h4 class="font-semibold">${orchestrator.name}</h4>
                    <span class="badge ${getOrchestratorStatusClass(orchestrator.status)}">
                        ${orchestrator.status}
                    </span>
                </div>
                
                <div class="space-y-2 text-sm mb-4">
                    <div class="flex justify-between opacity-75">
                        <span>Operations:</span>
                        <span>${orchestrator.operations_executed}</span>
                    </div>
                    <div class="flex justify-between opacity-75">
                        <span>Errors:</span>
                        <span class="${orchestrator.errors > 0 ? 'text-rose-400' : ''}">${orchestrator.errors}</span>
                    </div>
                    <div class="flex justify-between opacity-75">
                        <span>Last Executed:</span>
                        <span class="text-xs">${formatTimeStamp(orchestrator.last_execution)}</span>
                    </div>
                </div>
                
                ${orchestrator.dependencies.length > 0 ? `
                    <div class="pt-4 border-t border-slate-700/50">
                        <p class="text-xs opacity-60 mb-2">Dependencies:</p>
                        <div class="flex flex-wrap gap-1">
                            ${orchestrator.dependencies.map(dep => `
                                <span class="text-xs bg-slate-700/50 px-2 py-1 rounded">${dep}</span>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `).join('');
        
        console.log('Γ£ô Orchestrator grid rendered:', data.orchestrators.length);
        
    } catch (error) {
        console.error('Γ£ù Error loading orchestrators:', error);
        grid.innerHTML = `
            <div class="col-span-full glass-panel p-4 text-amber-400 border-l-2 border-amber-500">
                <p class="text-sm">ΓÜá∩╕Å Unable to load orchestrator status</p>
                <p class="text-xs opacity-75 mt-1">Make sure FastAPI backend is running on port 8000</p>
            </div>
        `;
    }
}

function getOrchestratorStatusClass(status) {
    const classes = {
        'ACTIVE': 'badge-success',
        'IDLE': 'badge-info',
        'ERROR': 'badge-error',
        'DISABLED': 'badge-warning'
    };
    return classes[status] || 'badge-info';
}

function formatTimeStamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
}

// Render on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderOrchestratorGrid);
} else {
    // Already loaded
    renderOrchestratorGrid().catch(e => console.error('Orchestrator grid render failed:', e));
}
