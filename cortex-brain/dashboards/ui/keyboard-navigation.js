/**
 * Keyboard Navigation & Accessibility Module
 * 
 * Implements keyboard shortcuts, focus management, and ARIA labels
 * for improved accessibility and power user workflows.
 * 
 * Keyboard Shortcuts:
 * - Ctrl/Cmd + 1-7: Switch tabs
 * - Ctrl/Cmd + R: Refresh data
 * - Ctrl/Cmd + E: Export data
 * - Ctrl/Cmd + S: Save/Export JSON
 * - Ctrl/Cmd + P: Print/PDF export
 * - Ctrl/Cmd + K: Open command palette
 * - Escape: Close modals/overlays
 * - Tab: Navigate focusable elements
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Source-Available (Use Allowed, No Contributions)
 */

import { showSuccessToast } from './shared-utils.js';
import { exportToJson, exportToPdf } from './export-utils.js';

/**
 * Initialize keyboard navigation
 */
export function initKeyboardNavigation() {
    document.addEventListener('keydown', handleKeyboardShortcut);
    addAriaLabels();
    setupFocusManagement();
    console.log('Keyboard navigation initialized');
}

/**
 * Handle keyboard shortcuts
 * @param {KeyboardEvent} event - Keyboard event
 */
function handleKeyboardShortcut(event) {
    const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
    const modifierKey = isMac ? event.metaKey : event.ctrlKey;
    
    // Ignore if user is typing in an input field
    if (event.target.tagName === 'INPUT' || 
        event.target.tagName === 'TEXTAREA' || 
        event.target.isContentEditable) {
        return;
    }
    
    // Tab shortcuts: Ctrl/Cmd + 1-7
    if (modifierKey && event.key >= '1' && event.key <= '7') {
        event.preventDefault();
        const tabIndex = parseInt(event.key) - 1;
        const tabIds = ['overview', 'tech-stack', 'security', 'architecture', 'code-org', 'team', 'vendors'];
        if (tabIds[tabIndex]) {
            switchTab(tabIds[tabIndex]);
            showSuccessToast(`Switched to ${tabIds[tabIndex].replace('-', ' ')} tab`);
        }
        return;
    }
    
    // Refresh: Ctrl/Cmd + R
    if (modifierKey && event.key === 'r') {
        event.preventDefault();
        refreshData();
        return;
    }
    
    // Export: Ctrl/Cmd + E
    if (modifierKey && event.key === 'e') {
        event.preventDefault();
        exportCurrentView();
        return;
    }
    
    // Save JSON: Ctrl/Cmd + S
    if (modifierKey && event.key === 's') {
        event.preventDefault();
        saveAsJson();
        return;
    }
    
    // Print/PDF: Ctrl/Cmd + P
    if (modifierKey && event.key === 'p') {
        event.preventDefault();
        exportToPdf('Dashboard Report');
        return;
    }
    
    // Command Palette: Ctrl/Cmd + K
    if (modifierKey && event.key === 'k') {
        event.preventDefault();
        openCommandPalette();
        return;
    }
    
    // Escape: Close modals/overlays
    if (event.key === 'Escape') {
        closeOverlays();
        return;
    }
    
    // Arrow keys for tab navigation (when no modifier)
    if (!modifierKey && !event.shiftKey && !event.altKey) {
        if (event.key === 'ArrowRight') {
            navigateToNextTab();
            return;
        }
        if (event.key === 'ArrowLeft') {
            navigateToPreviousTab();
            return;
        }
    }
    
    // Question mark: Show keyboard shortcuts help
    if (event.key === '?' && !modifierKey) {
        event.preventDefault();
        showKeyboardShortcutsHelp();
        return;
    }
}

/**
 * Switch to a specific tab
 * @param {string} tabId - Tab identifier
 */
function switchTab(tabId) {
    // Dispatch custom event for app.js to handle
    window.dispatchEvent(new CustomEvent('tabChanged', { detail: { tab: tabId } }));
    
    // Update URL
    const url = new URL(window.location);
    url.searchParams.set('tab', tabId);
    window.history.pushState({}, '', url);
    
    // Update aria-selected on tab buttons
    document.querySelectorAll('[role="tab"]').forEach(tab => {
        tab.setAttribute('aria-selected', tab.dataset.tab === tabId ? 'true' : 'false');
    });
    
    // Focus the tab content
    const tabContent = document.getElementById(`${tabId}-container`);
    if (tabContent) {
        tabContent.setAttribute('tabindex', '-1');
        tabContent.focus();
    }
}

/**
 * Navigate to next tab
 */
function navigateToNextTab() {
    const tabIds = ['overview', 'tech-stack', 'security', 'architecture', 'code-org', 'team', 'vendors'];
    const url = new URL(window.location);
    const currentTab = url.searchParams.get('tab') || 'overview';
    const currentIndex = tabIds.indexOf(currentTab);
    const nextIndex = (currentIndex + 1) % tabIds.length;
    switchTab(tabIds[nextIndex]);
}

/**
 * Navigate to previous tab
 */
function navigateToPreviousTab() {
    const tabIds = ['overview', 'tech-stack', 'security', 'architecture', 'code-org', 'team', 'vendors'];
    const url = new URL(window.location);
    const currentTab = url.searchParams.get('tab') || 'overview';
    const currentIndex = tabIds.indexOf(currentTab);
    const prevIndex = (currentIndex - 1 + tabIds.length) % tabIds.length;
    switchTab(tabIds[prevIndex]);
}

/**
 * Refresh dashboard data
 */
function refreshData() {
    window.dispatchEvent(new CustomEvent('refreshData'));
    showSuccessToast('Refreshing data...');
}

/**
 * Export current view
 */
function exportCurrentView() {
    window.dispatchEvent(new CustomEvent('exportData'));
}

/**
 * Save as JSON
 */
function saveAsJson() {
    window.dispatchEvent(new CustomEvent('exportData'));
}

/**
 * Close overlays (loading, modals, etc.)
 */
function closeOverlays() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay && overlay.classList.contains('active')) {
        overlay.classList.remove('active');
    }
    
    const commandPalette = document.getElementById('commandPalette');
    if (commandPalette) {
        commandPalette.remove();
    }
    
    const helpModal = document.getElementById('keyboardHelpModal');
    if (helpModal) {
        helpModal.remove();
    }
}

/**
 * Open command palette
 */
function openCommandPalette() {
    // Remove existing palette if any
    const existing = document.getElementById('commandPalette');
    if (existing) {
        existing.remove();
        return;
    }
    
    const palette = document.createElement('div');
    palette.id = 'commandPalette';
    palette.className = 'fade-in';
    palette.style.cssText = `
        position: fixed;
        top: 20%;
        left: 50%;
        transform: translateX(-50%);
        width: 90%;
        max-width: 600px;
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-lg);
        z-index: 10000;
        padding: 1.5rem;
    `;
    
    palette.innerHTML = `
        <h3 style="margin-bottom: 1rem;">⌘ Command Palette</h3>
        <input 
            type="text" 
            id="commandInput" 
            placeholder="Type a command..."
            style="
                width: 100%;
                padding: 0.75rem;
                background: rgba(0, 0, 0, 0.3);
                border: 1px solid var(--glass-border);
                border-radius: var(--radius-sm);
                color: var(--text-primary);
                font-size: 1rem;
                outline: none;
            "
            autofocus
        />
        <div id="commandList" style="margin-top: 1rem; max-height: 400px; overflow-y: auto;">
            <div class="command-item" data-command="refresh">🔄 Refresh Data (Ctrl+R)</div>
            <div class="command-item" data-command="export">💾 Export Data (Ctrl+E)</div>
            <div class="command-item" data-command="pdf">📄 Export PDF (Ctrl+P)</div>
            <div class="command-item" data-command="help">❓ Keyboard Shortcuts (?)</div>
            <div class="command-item" data-command="overview">📊 Overview Tab (Ctrl+1)</div>
            <div class="command-item" data-command="tech-stack">🛠️ Tech Stack Tab (Ctrl+2)</div>
            <div class="command-item" data-command="security">🔒 Security Tab (Ctrl+3)</div>
            <div class="command-item" data-command="architecture">🏗️ Architecture Tab (Ctrl+4)</div>
            <div class="command-item" data-command="code-org">📊 Code Org Tab (Ctrl+5)</div>
            <div class="command-item" data-command="team">👥 Team Tab (Ctrl+6)</div>
            <div class="command-item" data-command="vendors">🔗 Vendors Tab (Ctrl+7)</div>
        </div>
        <style>
            .command-item {
                padding: 0.75rem;
                margin: 0.25rem 0;
                background: rgba(255, 255, 255, 0.05);
                border-radius: var(--radius-sm);
                cursor: pointer;
                transition: all var(--transition-base);
            }
            .command-item:hover {
                background: rgba(0, 212, 255, 0.2);
                transform: translateX(4px);
            }
        </style>
    `;
    
    document.body.appendChild(palette);
    
    // Handle command selection
    palette.querySelectorAll('.command-item').forEach(item => {
        item.addEventListener('click', () => {
            const command = item.dataset.command;
            executeCommand(command);
            palette.remove();
        });
    });
    
    // Handle escape to close
    const input = document.getElementById('commandInput');
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            palette.remove();
        }
    });
    
    // Filter commands
    input.addEventListener('input', (e) => {
        const filter = e.target.value.toLowerCase();
        palette.querySelectorAll('.command-item').forEach(item => {
            const text = item.textContent.toLowerCase();
            item.style.display = text.includes(filter) ? 'block' : 'none';
        });
    });
}

/**
 * Execute command from palette
 * @param {string} command - Command identifier
 */
function executeCommand(command) {
    switch (command) {
        case 'refresh':
            refreshData();
            break;
        case 'export':
            exportCurrentView();
            break;
        case 'pdf':
            exportToPdf('Dashboard Report');
            break;
        case 'help':
            showKeyboardShortcutsHelp();
            break;
        default:
            // Assume it's a tab name
            switchTab(command);
    }
}

/**
 * Show keyboard shortcuts help modal
 */
function showKeyboardShortcutsHelp() {
    const modal = document.createElement('div');
    modal.id = 'keyboardHelpModal';
    modal.className = 'fade-in';
    modal.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 90%;
        max-width: 700px;
        max-height: 80vh;
        overflow-y: auto;
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-lg);
        z-index: 10000;
        padding: 2rem;
    `;
    
    const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
    const modKey = isMac ? '⌘' : 'Ctrl';
    
    modal.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
            <h2>⌨️ Keyboard Shortcuts</h2>
            <button onclick="this.closest('#keyboardHelpModal').remove()" style="
                background: none;
                border: none;
                font-size: 1.5rem;
                cursor: pointer;
                color: var(--text-secondary);
            ">×</button>
        </div>
        
        <div style="display: grid; gap: 1rem;">
            <div class="shortcut-section">
                <h3 style="margin-bottom: 0.75rem; color: var(--accent-primary);">Navigation</h3>
                <div class="shortcut-item"><kbd>${modKey}+1-7</kbd> <span>Switch between tabs</span></div>
                <div class="shortcut-item"><kbd>←</kbd> <kbd>→</kbd> <span>Previous/Next tab</span></div>
                <div class="shortcut-item"><kbd>${modKey}+K</kbd> <span>Open command palette</span></div>
            </div>
            
            <div class="shortcut-section">
                <h3 style="margin-bottom: 0.75rem; color: var(--accent-primary);">Actions</h3>
                <div class="shortcut-item"><kbd>${modKey}+R</kbd> <span>Refresh data</span></div>
                <div class="shortcut-item"><kbd>${modKey}+E</kbd> <span>Export current view</span></div>
                <div class="shortcut-item"><kbd>${modKey}+S</kbd> <span>Save as JSON</span></div>
                <div class="shortcut-item"><kbd>${modKey}+P</kbd> <span>Export as PDF</span></div>
            </div>
            
            <div class="shortcut-section">
                <h3 style="margin-bottom: 0.75rem; color: var(--accent-primary);">General</h3>
                <div class="shortcut-item"><kbd>?</kbd> <span>Show this help</span></div>
                <div class="shortcut-item"><kbd>Esc</kbd> <span>Close modals/overlays</span></div>
                <div class="shortcut-item"><kbd>Tab</kbd> <span>Navigate focusable elements</span></div>
            </div>
        </div>
        
        <style>
            .shortcut-section {
                background: rgba(255, 255, 255, 0.05);
                padding: 1rem;
                border-radius: var(--radius-sm);
            }
            .shortcut-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0.5rem 0;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }
            .shortcut-item:last-child {
                border-bottom: none;
            }
            kbd {
                display: inline-block;
                padding: 0.25rem 0.5rem;
                background: rgba(0, 0, 0, 0.3);
                border: 1px solid var(--glass-border);
                border-radius: 4px;
                font-family: var(--font-mono);
                font-size: 0.875rem;
                color: var(--accent-primary);
                margin-right: 0.5rem;
            }
        </style>
    `;
    
    document.body.appendChild(modal);
}

/**
 * Add ARIA labels to elements
 */
function addAriaLabels() {
    // Add role and labels to tab navigation
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        const nav = sidebar.querySelector('.tab-nav');
        if (nav) {
            nav.setAttribute('role', 'tablist');
            nav.setAttribute('aria-label', 'Dashboard sections');
        }
    }
    
    // Add roles to tab items
    document.querySelectorAll('.tab-item').forEach((tab, index) => {
        tab.setAttribute('role', 'tab');
        tab.setAttribute('tabindex', index === 0 ? '0' : '-1');
        tab.setAttribute('aria-selected', index === 0 ? 'true' : 'false');
    });
    
    // Add roles to tab panels
    const containers = [
        'overview-container',
        'tech-stack-container',
        'security-container',
        'architecture-container',
        'code-org-container',
        'team-container',
        'vendors-container'
    ];
    
    containers.forEach(containerId => {
        const container = document.getElementById(containerId);
        if (container) {
            container.setAttribute('role', 'tabpanel');
            container.setAttribute('aria-labelledby', containerId.replace('-container', '-tab'));
        }
    });
    
    // Add aria-label to buttons
    document.querySelectorAll('button').forEach(button => {
        if (!button.getAttribute('aria-label') && button.textContent) {
            button.setAttribute('aria-label', button.textContent.trim());
        }
    });
}

/**
 * Setup focus management
 */
function setupFocusManagement() {
    // Skip to main content link
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.textContent = 'Skip to main content';
    skipLink.className = 'visually-hidden';
    skipLink.style.cssText = `
        position: absolute;
        top: -40px;
        left: 0;
        background: var(--accent-primary);
        color: var(--bg-primary);
        padding: 0.5rem 1rem;
        z-index: 10001;
        transition: top 0.2s;
    `;
    skipLink.addEventListener('focus', () => {
        skipLink.style.top = '0';
    });
    skipLink.addEventListener('blur', () => {
        skipLink.style.top = '-40px';
    });
    document.body.insertBefore(skipLink, document.body.firstChild);
    
    // Add ID to main content area
    const mainContent = document.querySelector('.content-area');
    if (mainContent) {
        mainContent.id = 'main-content';
        mainContent.setAttribute('role', 'main');
    }
    
    // Focus trap for modals
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Tab') {
            const modal = document.querySelector('#commandPalette, #keyboardHelpModal');
            if (modal) {
                trapFocus(e, modal);
            }
        }
    });
}

/**
 * Trap focus within an element
 * @param {KeyboardEvent} event - Tab key event
 * @param {HTMLElement} element - Element to trap focus in
 */
function trapFocus(event, element) {
    const focusableElements = element.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    const firstFocusable = focusableElements[0];
    const lastFocusable = focusableElements[focusableElements.length - 1];
    
    if (event.shiftKey) {
        if (document.activeElement === firstFocusable) {
            event.preventDefault();
            lastFocusable.focus();
        }
    } else {
        if (document.activeElement === lastFocusable) {
            event.preventDefault();
            firstFocusable.focus();
        }
    }
}

/**
 * Announce to screen readers
 * @param {string} message - Message to announce
 * @param {string} priority - 'polite' or 'assertive'
 */
export function announceToScreenReader(message, priority = 'polite') {
    const announcer = document.getElementById('screen-reader-announcer') || createAnnouncer();
    announcer.setAttribute('aria-live', priority);
    announcer.textContent = message;
    
    // Clear after announcement
    setTimeout(() => {
        announcer.textContent = '';
    }, 1000);
}

/**
 * Create screen reader announcer element
 * @returns {HTMLElement} Announcer element
 */
function createAnnouncer() {
    const announcer = document.createElement('div');
    announcer.id = 'screen-reader-announcer';
    announcer.className = 'visually-hidden';
    announcer.setAttribute('role', 'status');
    announcer.setAttribute('aria-live', 'polite');
    announcer.setAttribute('aria-atomic', 'true');
    document.body.appendChild(announcer);
    return announcer;
}
