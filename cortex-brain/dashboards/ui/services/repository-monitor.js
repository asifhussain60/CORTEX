/**
 * Repository Monitor Service
 * 
 * Polls repository registry for changes and updates UI dynamically.
 * 
 * Features:
 * - Automatic change detection
 * - Smooth animations for updates
 * - Memory leak prevention
 * - Visual notifications
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 */

class RepositoryMonitor {
    constructor() {
        this.registryUrl = '/data/repository-registry.json';
        this.pollInterval = 5000; // 5 seconds
        this.lastRegistry = null;
        this.intervalId = null;
        this.isRunning = false;
    }
    
    /**
     * Start monitoring for repository changes
     */
    start() {
        if (this.isRunning) {
            console.warn('Repository monitor already running');
            return;
        }
        
        console.log('Starting repository monitor...');
        this.isRunning = true;
        
        // Initial load
        this.checkForUpdates();
        
        // Start polling
        this.intervalId = setInterval(() => {
            this.checkForUpdates();
        }, this.pollInterval);
    }
    
    /**
     * Stop monitoring
     */
    stop() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
        this.isRunning = false;
        console.log('Repository monitor stopped');
    }
    
    /**
     * Check for registry updates
     */
    async checkForUpdates() {
        try {
            const response = await fetch(this.registryUrl + '?_=' + Date.now());
            
            if (!response.ok) {
                console.debug('Registry not found or not accessible');
                return;
            }
            
            const registry = await response.json();
            
            // First load
            if (!this.lastRegistry) {
                this.lastRegistry = registry;
                console.log(`Monitoring ${registry.total_repositories} repositories`);
                return;
            }
            
            // Detect changes
            const changes = this.detectChanges(this.lastRegistry, registry);
            
            if (changes.added.length > 0 || changes.removed.length > 0) {
                console.log('Repository changes detected:', changes);
                this.handleChanges(changes);
                this.lastRegistry = registry;
            }
            
        } catch (error) {
            console.debug('Failed to check for updates:', error);
        }
    }
    
    /**
     * Detect changes between registries
     */
    detectChanges(oldRegistry, newRegistry) {
        const oldRepos = new Map(
            oldRegistry.repositories.map(r => [r.id, r])
        );
        const newRepos = new Map(
            newRegistry.repositories.map(r => [r.id, r])
        );
        
        const added = [];
        const removed = [];
        const updated = [];
        
        // Find added repositories
        for (const [id, repo] of newRepos) {
            if (!oldRepos.has(id)) {
                added.push(repo);
            } else {
                // Check for updates
                const oldRepo = oldRepos.get(id);
                if (oldRepo.last_updated !== repo.last_updated) {
                    updated.push(repo);
                }
            }
        }
        
        // Find removed repositories
        for (const [id, repo] of oldRepos) {
            if (!newRepos.has(id)) {
                removed.push(repo);
            }
        }
        
        return { added, removed, updated };
    }
    
    /**
     * Handle detected changes
     */
    handleChanges(changes) {
        // Handle additions
        for (const repo of changes.added) {
            this.onRepositoryAdded(repo);
        }
        
        // Handle removals
        for (const repo of changes.removed) {
            this.onRepositoryRemoved(repo);
        }
        
        // Handle updates
        for (const repo of changes.updated) {
            this.onRepositoryUpdated(repo);
        }
    }
    
    /**
     * Handle repository added
     */
    onRepositoryAdded(repo) {
        console.log(`Repository added: ${repo.name}`);
        
        // Show notification
        this.showNotification(`New repository discovered: ${repo.name}`, 'success');
        
        // Update left panel (if exists)
        if (window.updateRepositoryList) {
            window.updateRepositoryList();
        }
        
        // Trigger custom event
        this.dispatchEvent('repository-added', repo);
    }
    
    /**
     * Handle repository removed
     */
    onRepositoryRemoved(repo) {
        console.log(`Repository removed: ${repo.name}`);
        
        // Show notification
        this.showNotification(`Repository removed: ${repo.name}`, 'warning');
        
        // Update left panel
        if (window.updateRepositoryList) {
            window.updateRepositoryList();
        }
        
        // Trigger custom event
        this.dispatchEvent('repository-removed', repo);
    }
    
    /**
     * Handle repository updated
     */
    onRepositoryUpdated(repo) {
        console.log(`Repository updated: ${repo.name}`);
        
        // Show subtle notification
        this.showNotification(`${repo.name} data updated`, 'info', 2000);
        
        // Trigger custom event
        this.dispatchEvent('repository-updated', repo);
    }
    
    /**
     * Show notification to user
     */
    showNotification(message, type = 'info', duration = 5000) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Style notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '15px 20px',
            borderRadius: '8px',
            background: this.getNotificationColor(type),
            color: 'white',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
            zIndex: '10000',
            animation: 'slideInRight 0.3s ease-out',
            fontFamily: 'system-ui, -apple-system, sans-serif',
            fontSize: '14px',
            maxWidth: '350px',
            wordWrap: 'break-word'
        });
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto-remove
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, duration);
    }
    
    /**
     * Get notification background color
     */
    getNotificationColor(type) {
        const colors = {
            'success': 'linear-gradient(135deg, #00b894, #00cec9)',
            'warning': 'linear-gradient(135deg, #fdcb6e, #e17055)',
            'error': 'linear-gradient(135deg, #d63031, #e84393)',
            'info': 'linear-gradient(135deg, #0984e3, #6c5ce7)'
        };
        return colors[type] || colors.info;
    }
    
    /**
     * Dispatch custom event
     */
    dispatchEvent(eventName, data) {
        const event = new CustomEvent(eventName, {
            detail: data,
            bubbles: true
        });
        window.dispatchEvent(event);
    }
    
    /**
     * Force immediate update check
     */
    async forceCheck() {
        console.log('Forcing update check...');
        await this.checkForUpdates();
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Export
window.RepositoryMonitor = RepositoryMonitor;

// Auto-start if enabled
if (window.AUTO_START_MONITOR !== false) {
    window.repositoryMonitor = new RepositoryMonitor();
    // Start after page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            window.repositoryMonitor.start();
        });
    } else {
        window.repositoryMonitor.start();
    }
}
