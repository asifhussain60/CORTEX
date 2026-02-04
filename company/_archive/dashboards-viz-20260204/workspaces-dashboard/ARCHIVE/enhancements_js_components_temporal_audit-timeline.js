/**
 * Audit Timeline Component
 * NO-002-01: Audit Timeline View
 * Searchable, filterable timeline of audit log entries
 */

let auditWebSocket = null;

async function renderAuditTimeline() {
    const list = document.getElementById('audit-list');
    
    try {
        const data = await api.getAuditEntries(20);
        
        list.innerHTML = data.entries.map(entry => `
            <div class="glass-panel p-3 border-l-2 border-cyan-500/50 hover:border-cyan-500 transition">
                <div class="flex justify-between items-start mb-2">
                    <div>
                        <span class="font-mono text-xs text-cyan-400">${entry.ac_id}</span>
                        <span class="ml-2 font-mono text-xs opacity-60">${entry.operation}</span>
                    </div>
                    <span class="text-xs opacity-50">${formatTimeStamp(entry.timestamp)}</span>
                </div>
                <p class="text-sm">${entry.message}</p>
                <div class="flex gap-2 mt-2 text-xs opacity-50">
                    <span>≡ƒôè ${entry.orchestrator}</span>
                    <span class="ml-auto">Severity: ${entry.severity}</span>
                </div>
            </div>
        `).join('');
        
        // Connect WebSocket for real-time updates
        if (!auditWebSocket) {
            auditWebSocket = api.connectAuditStream((message) => {
                if (message.type === 'audit_entry') {
                    const newEntry = `
                        <div class="glass-panel p-3 border-l-2 border-emerald-500/50 fade-in">
                            <div class="flex justify-between items-start mb-2">
                                <div>
                                    <span class="font-mono text-xs text-emerald-400">${message.ac_id}</span>
                                    <span class="ml-2 font-mono text-xs opacity-60">${message.operation}</span>
                                </div>
                                <span class="text-xs opacity-50">now</span>
                            </div>
                            <p class="text-sm">${message.message}</p>
                        </div>
                    `;
                    list.insertAdjacentHTML('afterbegin', newEntry);
                    
                    // Keep only last 20
                    while (list.children.length > 20) {
                        list.removeChild(list.lastChild);
                    }
                }
            }, (error) => {
                console.warn('WebSocket connection issue, but REST API is working. Real-time updates unavailable.');
            });
        }
        
    } catch (error) {
        console.error('Error loading audit timeline:', error);
        list.innerHTML = `
            <div class="glass-panel p-4 text-amber-400 border-l-2 border-amber-500">
                <p class="text-sm">ΓÜá∩╕Å Unable to load audit timeline</p>
                <p class="text-xs opacity-75 mt-1">Make sure FastAPI backend is running on port 8000</p>
            </div>
        `;
    }
}

function formatTimeStamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
}

// Render on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderAuditTimeline);
} else {
    // Already loaded
    renderAuditTimeline().catch(e => console.error('Audit timeline render failed:', e));
}
