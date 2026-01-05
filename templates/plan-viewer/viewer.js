/**
 * CORTEX Plan Viewer - Data-Driven Renderer
 * Version: 1.0.0
 * Date: January 5, 2026
 * Author: Asif Hussain
 * 
 * Design Patterns:
 * - Observer Pattern: Auto-refresh for live updates
 * - Strategy Pattern: Data fetchers (JSON sources)
 * - Model-View Pattern: Separation of data and rendering
 * - Single Responsibility: Each method handles one concern
 */

class PlanViewer {
    constructor() {
        this.planData = null;
        this.progressData = null;
        this.refreshInterval = 5000; // 5 seconds
        this.refreshTimer = null;
        this.lastUpdateTime = null;
    }

    /**
     * Initialize plan viewer - Entry point
     */
    async init() {
        try {
            await this.loadPlanData();
            await this.loadProgressData();
            this.render();
            this.startAutoRefresh();
        } catch (error) {
            this.showError('Failed to initialize plan viewer', error);
        }
    }

    /**
     * Load static plan metadata (generated once)
     */
    async loadPlanData() {
        try {
            const response = await fetch('./plan-data.json');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            this.planData = await response.json();
        } catch (error) {
            console.error('Failed to load plan data:', error);
            throw error;
        }
    }

    /**
     * Load live progress data (updates frequently)
     */
    async loadProgressData() {
        try {
            const response = await fetch('./tracking/progress-tracker.json');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            this.progressData = await response.json();
            this.lastUpdateTime = new Date();
        } catch (error) {
            console.error('Failed to load progress data:', error);
            // Don't throw - allow viewer to work with just plan data
            this.progressData = this.getDefaultProgressData();
        }
    }

    /**
     * Get default progress data structure
     */
    getDefaultProgressData() {
        return {
            phases: [],
            percent_complete: 0,
            actual_total_hours: 0,
            estimated_total_hours: this.planData?.estimated_hours || 0,
            status: 'not_started'
        };
    }

    /**
     * Render all sections
     */
    render() {
        this.renderHeader();
        this.renderProgress();
        this.renderPhases();
        this.renderArtifacts();
        this.renderFooter();
    }

    /**
     * Render header section
     */
    renderHeader() {
        if (!this.planData) return;

        document.getElementById('plan-title').textContent = this.planData.plan_title || 'Untitled Plan';
        document.getElementById('plan-id').textContent = `Plan ID: ${this.planData.plan_id || 'N/A'}`;
        
        const statusBadge = document.getElementById('plan-status');
        const status = this.progressData?.status || this.planData.status || 'not_started';
        statusBadge.textContent = status.replace('_', ' ').toUpperCase();
        statusBadge.className = `status-badge ${status.replace('_', '-')}`;
    }

    /**
     * Render progress section
     */
    renderProgress() {
        if (!this.progressData) return;

        // Calculate overall progress
        const percentage = this.progressData.percent_complete || 0;
        const completed = this.progressData.actual_total_hours || 0;
        const total = this.progressData.estimated_total_hours || this.planData?.estimated_hours || 0;
        const remaining = Math.max(0, total - completed);

        // Render progress bar (20-character ASCII bar)
        const filled = Math.round(percentage / 5); // 0-20 characters
        const empty = 20 - filled;
        const progressBar = '█'.repeat(filled) + '░'.repeat(empty);

        document.getElementById('progress-bar').textContent = progressBar;
        document.getElementById('progress-percentage').textContent = `${percentage}%`;
        
        // Status emoji
        let statusEmoji = '⏸️ NOT STARTED';
        if (percentage === 100) statusEmoji = '✅ COMPLETE';
        else if (percentage > 0) statusEmoji = '🔄 IN PROGRESS';
        document.getElementById('progress-status').textContent = statusEmoji;

        // Stats
        document.getElementById('stat-completed').textContent = `${completed.toFixed(2)} hours`;
        document.getElementById('stat-remaining').textContent = `${remaining.toFixed(2)} hours`;
        document.getElementById('stat-total').textContent = `${total.toFixed(2)} hours`;
    }

    /**
     * Render phases section
     */
    renderPhases() {
        const phasesList = document.getElementById('phases-list');
        phasesList.innerHTML = ''; // Clear existing

        const phases = this.progressData?.phases || [];
        
        if (phases.length === 0) {
            phasesList.innerHTML = '<p style="color: var(--color-text-secondary);">No phases defined yet.</p>';
            return;
        }

        phases.forEach((phase, index) => {
            const phaseItem = this.createPhaseElement(phase, index);
            phasesList.appendChild(phaseItem);
        });
    }

    /**
     * Create phase DOM element
     */
    createPhaseElement(phase, index) {
        const div = document.createElement('div');
        div.className = 'phase-item';

        // Calculate phase progress bar
        let phaseProgress = '░░░░░░░░░░'; // 10 chars
        if (phase.status === 'complete' || phase.status === 'completed') {
            phaseProgress = '██████████';
        } else if (phase.status === 'in-progress' || phase.status === 'in_progress') {
            phaseProgress = '█████░░░░░'; // 50%
        }

        div.innerHTML = `
            <div class="phase-header">
                <div class="phase-title">
                    Phase ${phase.number}: ${phase.name}
                </div>
                <div class="phase-status ${(phase.status || 'not-started').replace('_', '-')}">
                    ${this.getStatusEmoji(phase.status)} ${(phase.status || 'not_started').replace('_', ' ').toUpperCase()}
                </div>
            </div>
            <div class="phase-progress">${phaseProgress}</div>
            <div class="phase-details">
                <span>⏱️ Est: ${phase.estimated_hours || 0}h</span>
                <span>✓ Actual: ${phase.actual_hours || 0}h</span>
            </div>
        `;

        return div;
    }

    /**
     * Get status emoji
     */
    getStatusEmoji(status) {
        const emojiMap = {
            'complete': '✅',
            'completed': '✅',
            'in-progress': '🔄',
            'in_progress': '🔄',
            'not-started': '⏸️',
            'not_started': '⏸️',
            'failed': '❌',
            'blocked': '🚫',
            'paused': '⏸️'
        };
        return emojiMap[status] || '⏸️';
    }

    /**
     * Render artifacts section
     */
    renderArtifacts() {
        const artifactsList = document.getElementById('artifacts-list');
        artifactsList.innerHTML = ''; // Clear existing

        // Collect artifacts from phases
        const artifacts = [];
        const phases = this.progressData?.phases || [];
        phases.forEach(phase => {
            if (phase.outputs && Array.isArray(phase.outputs)) {
                phase.outputs.forEach(output => {
                    artifacts.push({
                        name: output,
                        type: this.getArtifactType(output),
                        phase: phase.number
                    });
                });
            }
        });

        if (artifacts.length === 0) {
            artifactsList.innerHTML = '<p style="color: var(--color-text-secondary);">No artifacts generated yet.</p>';
            return;
        }

        artifacts.forEach(artifact => {
            const artifactItem = this.createArtifactElement(artifact);
            artifactsList.appendChild(artifactItem);
        });
    }

    /**
     * Create artifact DOM element
     */
    createArtifactElement(artifact) {
        const div = document.createElement('div');
        div.className = 'artifact-item';

        div.innerHTML = `
            <div class="artifact-name">${artifact.name}</div>
            <div class="artifact-type">
                📄 ${artifact.type} (Phase ${artifact.phase})
            </div>
        `;

        return div;
    }

    /**
     * Get artifact type from filename
     */
    getArtifactType(filename) {
        if (filename.endsWith('.md')) return 'Markdown';
        if (filename.endsWith('.py')) return 'Python';
        if (filename.endsWith('.yaml') || filename.endsWith('.yml')) return 'YAML';
        if (filename.endsWith('.json')) return 'JSON';
        if (filename.endsWith('.html')) return 'HTML';
        if (filename.endsWith('.css')) return 'CSS';
        if (filename.endsWith('.js')) return 'JavaScript';
        return 'File';
    }

    /**
     * Render footer
     */
    renderFooter() {
        const lastUpdated = document.getElementById('last-updated');
        if (this.lastUpdateTime) {
            lastUpdated.textContent = `Last updated: ${this.lastUpdateTime.toLocaleTimeString()}`;
        }
    }

    /**
     * Start auto-refresh timer
     */
    startAutoRefresh() {
        this.stopAutoRefresh(); // Clear any existing timer

        this.refreshTimer = setInterval(async () => {
            try {
                await this.loadProgressData();
                this.renderProgress();
                this.renderPhases();
                this.renderArtifacts();
                this.renderFooter();
                console.log('Auto-refreshed at', new Date().toLocaleTimeString());
            } catch (error) {
                console.error('Auto-refresh failed:', error);
            }
        }, this.refreshInterval);

        console.log(`Auto-refresh started (${this.refreshInterval / 1000}s interval)`);
    }

    /**
     * Stop auto-refresh timer
     */
    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
            console.log('Auto-refresh stopped');
        }
    }

    /**
     * Show error message
     */
    showError(message, error) {
        console.error(message, error);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error';
        errorDiv.innerHTML = `
            <strong>⚠️ Error:</strong> ${message}<br>
            <small>${error.message || 'Unknown error'}</small>
        `;
        
        document.getElementById('app').prepend(errorDiv);
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    const viewer = new PlanViewer();
    viewer.init().catch(error => {
        console.error('Failed to initialize plan viewer:', error);
    });

    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        viewer.stopAutoRefresh();
    });
});
