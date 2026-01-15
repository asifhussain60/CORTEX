/**
 * Neural Pulse Component
 * NO-001-02: Neural Pulse System
 * Visual health indicator showing brain operational status
 */

const statusConfigs = {
    'OPTIMAL': {
        label: 'All systems optimal',
        color: 'healthy',
        message: 'All systems healthy, hash chain valid'
    },
    'NOMINAL': {
        label: 'Operating normally',
        color: 'nominal',
        message: 'Minor warnings, non-blocking issues'
    },
    'DEGRADED': {
        label: 'Performance issues',
        color: 'degraded',
        message: 'Performance degradation, recoverable errors'
    },
    'CRITICAL': {
        label: 'Critical alerts',
        color: 'critical',
        message: 'System failures, immediate attention needed'
    },
    'DORMANT': {
        label: 'System dormant',
        color: 'dormant',
        message: 'No recent activity, standby mode'
    }
};

async function updateNeuralPulse() {
    try {
        const metrics = await api.getSSOTMetrics();
        const indicator = document.getElementById('pulse-indicator');
        const badge = document.getElementById('status-badge');
        const message = document.getElementById('status-message');
        
        // Determine status based on metrics
        let status = 'OPTIMAL';
        
        if (!metrics.audit.hash_chain_valid) {
            status = 'CRITICAL';
        } else if (metrics.progress_percentage < 50) {
            status = 'DEGRADED';
        } else if (metrics.progress_percentage < 75) {
            status = 'NOMINAL';
        }
        
        const config = statusConfigs[status];
        
        // Update indicator
        indicator.className = `pulse-indicator ${config.color}`;
        
        // Update badge
        badge.className = `badge badge-${config.color === 'healthy' ? 'success' : config.color === 'nominal' ? 'warning' : 'error'}`;
        badge.textContent = status;
        
        // Update message
        message.textContent = config.message;
        
    } catch (error) {
        console.error('Error updating neural pulse:', error);
    }
}

// Update on page load and every 5 seconds
document.addEventListener('DOMContentLoaded', () => {
    updateNeuralPulse();
    setInterval(updateNeuralPulse, 5000);
});
