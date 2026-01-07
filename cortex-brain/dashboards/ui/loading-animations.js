/**
 * Loading States & Animations Module
 * 
 * Provides loading indicators, skeleton loaders, and smooth transitions
 * for enhanced user feedback during data loading operations.
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Source-Available (Use Allowed, No Contributions)
 */

/**
 * Show loading overlay with spinner
 * @param {string} message - Optional loading message
 */
export function showLoading(message = 'Loading...') {
    let overlay = document.getElementById('loadingOverlay');
    
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loadingOverlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div style="text-align: center;">
                <div class="spinner"></div>
                <p id="loadingMessage" style="margin-top: 1.5rem; color: var(--text-secondary); font-size: 1rem;">
                    ${message}
                </p>
            </div>
        `;
        document.body.appendChild(overlay);
    }
    
    // Update message if provided
    const messageEl = document.getElementById('loadingMessage');
    if (messageEl) {
        messageEl.textContent = message;
    }
    
    // Trigger reflow to ensure transition works
    overlay.offsetHeight;
    overlay.classList.add('active');
}

/**
 * Hide loading overlay
 */
export function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
}

/**
 * Update loading message
 * @param {string} message - New loading message
 */
export function updateLoadingMessage(message) {
    const messageEl = document.getElementById('loadingMessage');
    if (messageEl) {
        messageEl.textContent = message;
    }
}

/**
 * Show skeleton loader in a container
 * @param {string} containerId - Container element ID
 * @param {string} type - Skeleton type: 'card', 'table', 'text', 'custom'
 */
export function showSkeleton(containerId, type = 'card') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    let skeletonHTML = '';
    
    switch (type) {
        case 'card':
            skeletonHTML = `
                <div class="glass-card fade-in">
                    <div class="skeleton skeleton-title"></div>
                    <div class="skeleton skeleton-text" style="width: 80%;"></div>
                    <div class="skeleton skeleton-text" style="width: 90%;"></div>
                    <div class="skeleton skeleton-text" style="width: 70%;"></div>
                    <div class="skeleton skeleton-card" style="margin-top: 1.5rem;"></div>
                </div>
            `;
            break;
            
        case 'table':
            skeletonHTML = `
                <div class="glass-card fade-in">
                    <div class="skeleton skeleton-title" style="width: 40%;"></div>
                    ${Array(5).fill(0).map(() => `
                        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1rem;">
                            <div class="skeleton skeleton-text"></div>
                            <div class="skeleton skeleton-text"></div>
                            <div class="skeleton skeleton-text"></div>
                            <div class="skeleton skeleton-text"></div>
                        </div>
                    `).join('')}
                </div>
            `;
            break;
            
        case 'text':
            skeletonHTML = `
                <div class="fade-in">
                    <div class="skeleton skeleton-title" style="width: 60%;"></div>
                    <div class="skeleton skeleton-text"></div>
                    <div class="skeleton skeleton-text" style="width: 85%;"></div>
                    <div class="skeleton skeleton-text" style="width: 75%;"></div>
                </div>
            `;
            break;
            
        case 'dashboard':
            skeletonHTML = `
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
                    ${Array(4).fill(0).map(() => `
                        <div class="glass-card fade-in">
                            <div class="skeleton skeleton-text" style="width: 40%; margin-bottom: 1rem;"></div>
                            <div class="skeleton skeleton-title" style="width: 30%; height: 3rem;"></div>
                        </div>
                    `).join('')}
                </div>
                <div class="glass-card fade-in">
                    <div class="skeleton skeleton-title" style="width: 30%;"></div>
                    <div class="skeleton skeleton-card"></div>
                </div>
            `;
            break;
            
        default:
            skeletonHTML = `
                <div class="glass-card fade-in">
                    <div class="skeleton skeleton-card"></div>
                </div>
            `;
    }
    
    container.innerHTML = skeletonHTML;
}

/**
 * Show error state with retry button
 * @param {string} containerId - Container element ID
 * @param {string} title - Error title
 * @param {string} message - Error message
 * @param {Function} retryCallback - Function to call on retry
 */
export function showError(containerId, title, message, retryCallback) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = `
        <div class="glass-card fade-in" style="text-align: center; padding: 3rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">⚠️</div>
            <h3 style="color: var(--danger); margin-bottom: 1rem;">${title}</h3>
            <p style="color: var(--text-secondary); margin-bottom: 2rem; max-width: 500px; margin-left: auto; margin-right: auto;">
                ${message}
            </p>
            <button id="retryButton" class="btn-primary">
                🔄 Retry
            </button>
        </div>
    `;
    
    if (retryCallback) {
        const retryButton = document.getElementById('retryButton');
        if (retryButton) {
            retryButton.addEventListener('click', retryCallback);
        }
    }
}

/**
 * Show success message
 * @param {string} message - Success message
 * @param {number} duration - Duration in ms (default 3000)
 */
export function showSuccessToast(message, duration = 3000) {
    const toast = document.createElement('div');
    toast.className = 'toast toast-success fade-in';
    toast.style.cssText = `
        position: fixed;
        top: 2rem;
        right: 2rem;
        background: rgba(0, 255, 136, 0.15);
        border: 1px solid var(--success);
        color: var(--success);
        padding: 1rem 1.5rem;
        border-radius: var(--radius-md);
        box-shadow: var(--shadow);
        z-index: 10000;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        backdrop-filter: blur(10px);
    `;
    toast.innerHTML = `
        <span style="font-size: 1.5rem;">✅</span>
        <span>${message}</span>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-10px)';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/**
 * Show warning message
 * @param {string} message - Warning message
 * @param {number} duration - Duration in ms (default 4000)
 */
export function showWarningToast(message, duration = 4000) {
    const toast = document.createElement('div');
    toast.className = 'toast toast-warning fade-in';
    toast.style.cssText = `
        position: fixed;
        top: 2rem;
        right: 2rem;
        background: rgba(255, 165, 0, 0.15);
        border: 1px solid var(--warning);
        color: var(--warning);
        padding: 1rem 1.5rem;
        border-radius: var(--radius-md);
        box-shadow: var(--shadow);
        z-index: 10000;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        backdrop-filter: blur(10px);
    `;
    toast.innerHTML = `
        <span style="font-size: 1.5rem;">⚠️</span>
        <span>${message}</span>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-10px)';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/**
 * Show error message
 * @param {string} message - Error message
 * @param {number} duration - Duration in ms (default 5000)
 */
export function showErrorToast(message, duration = 5000) {
    const toast = document.createElement('div');
    toast.className = 'toast toast-error fade-in';
    toast.style.cssText = `
        position: fixed;
        top: 2rem;
        right: 2rem;
        background: rgba(255, 68, 68, 0.15);
        border: 1px solid var(--danger);
        color: var(--danger);
        padding: 1rem 1.5rem;
        border-radius: var(--radius-md);
        box-shadow: var(--shadow);
        z-index: 10000;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        backdrop-filter: blur(10px);
    `;
    toast.innerHTML = `
        <span style="font-size: 1.5rem;">❌</span>
        <span>${message}</span>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-10px)';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/**
 * Show progress bar
 * @param {number} percent - Progress percentage (0-100)
 * @returns {HTMLElement} Progress bar element
 */
export function showProgressBar(percent = 0) {
    let progressContainer = document.getElementById('globalProgressBar');
    
    if (!progressContainer) {
        progressContainer = document.createElement('div');
        progressContainer.id = 'globalProgressBar';
        progressContainer.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 9998;
            height: 4px;
            background: rgba(255, 255, 255, 0.1);
        `;
        
        const progressBar = document.createElement('div');
        progressBar.id = 'progressBarFill';
        progressBar.style.cssText = `
            height: 100%;
            width: ${percent}%;
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
            transition: width 0.3s ease;
        `;
        
        progressContainer.appendChild(progressBar);
        document.body.appendChild(progressContainer);
    }
    
    return progressContainer;
}

/**
 * Update progress bar
 * @param {number} percent - Progress percentage (0-100)
 */
export function updateProgressBar(percent) {
    const progressBar = document.getElementById('progressBarFill');
    if (progressBar) {
        progressBar.style.width = `${Math.min(100, Math.max(0, percent))}%`;
    }
}

/**
 * Hide progress bar
 */
export function hideProgressBar() {
    const progressContainer = document.getElementById('globalProgressBar');
    if (progressContainer) {
        updateProgressBar(100);
        setTimeout(() => {
            progressContainer.style.opacity = '0';
            setTimeout(() => progressContainer.remove(), 300);
        }, 500);
    }
}

/**
 * Apply fade-in animation to element
 * @param {string|HTMLElement} element - Element ID or element
 * @param {number} delay - Delay before animation (ms)
 */
export function fadeIn(element, delay = 0) {
    const el = typeof element === 'string' ? document.getElementById(element) : element;
    if (!el) return;
    
    setTimeout(() => {
        el.classList.add('fade-in');
    }, delay);
}

/**
 * Apply slide-in animation to element
 * @param {string|HTMLElement} element - Element ID or element
 * @param {number} delay - Delay before animation (ms)
 */
export function slideIn(element, delay = 0) {
    const el = typeof element === 'string' ? document.getElementById(element) : element;
    if (!el) return;
    
    setTimeout(() => {
        el.classList.add('slide-in-left');
    }, delay);
}

/**
 * Stagger animations for multiple elements
 * @param {string} selector - CSS selector for elements
 * @param {number} stagger - Delay between each element (ms)
 */
export function staggerAnimation(selector, stagger = 100) {
    const elements = document.querySelectorAll(selector);
    elements.forEach((el, index) => {
        fadeIn(el, index * stagger);
    });
}
