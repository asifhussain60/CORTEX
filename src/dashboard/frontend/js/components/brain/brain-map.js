/**
 * Brain Map Component
 * NO-001-01: Brain Tier Visualization
 * Interactive visualization of the 4-tier brain architecture
 */

async function renderBrainTiers() {
    const grid = document.getElementById('tier-grid');
    
    try {
        const data = await api.getBrainTiers();
        
        grid.innerHTML = data.tiers.map(tier => `
            <div class="glass-panel cursor-pointer hover:border-cyan-500/50 transition group">
                <div class="flex items-center justify-between mb-3">
                    <div>
                        <h4 class="text-sm opacity-75">${tier.name}</h4>
                        <h3 class="text-lg font-bold">${tier.label}</h3>
                    </div>
                    <div class="status-badge ${getStatusBadgeClass(tier.status)}">
                        ${tier.status}
                    </div>
                </div>
                
                <p class="text-xs opacity-60 mb-4">${tier.description}</p>
                
                <div class="space-y-2 text-sm">
                    ${Object.entries(tier.metrics).map(([key, value]) => `
                        <div class="flex justify-between items-center">
                            <span class="opacity-60">${formatMetricKey(key)}</span>
                            <span class="font-semibold">${formatMetricValue(value)}</span>
                        </div>
                    `).join('')}
                </div>
                
                <div class="mt-4 pt-4 border-t border-slate-700/50 opacity-0 group-hover:opacity-100 transition">
                    <button class="text-xs text-cyan-400 hover:text-cyan-300">View Details →</button>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        grid.innerHTML = '<div class="text-red-400">Failed to load tier data</div>';
    }
}

function getStatusBadgeClass(status) {
    const classes = {
        'HEALTHY': 'bg-emerald-500/20 text-emerald-400',
        'NOMINAL': 'bg-amber-500/20 text-amber-400',
        'DEGRADED': 'bg-rose-500/20 text-rose-400',
        'CRITICAL': 'bg-red-500/20 text-red-400'
    };
    return classes[status] || 'bg-slate-500/20 text-slate-400';
}

function formatMetricKey(key) {
    return key
        .replace(/_/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase());
}

function formatMetricValue(value) {
    if (typeof value === 'number' && value < 1) {
        return (value * 100).toFixed(1) + '%';
    }
    if (typeof value === 'number' && value > 100) {
        return value.toLocaleString();
    }
    return String(value);
}

// Render on page load
document.addEventListener('DOMContentLoaded', renderBrainTiers);
