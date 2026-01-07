/**
 * Shared Utility Functions
 * 
 * Common utilities used across multiple modules.
 * This module has no dependencies to avoid circular imports.
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Source-Available (Use Allowed, No Contributions)
 */

/**
 * Toast notification system
 */
let toastContainer = null;

function ensureToastContainer() {
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container';
        toastContainer.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            gap: 10px;
        `;
        document.body.appendChild(toastContainer);
    }
    return toastContainer;
}

export function showToast(message, type = 'info', duration = 3000) {
    const container = ensureToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const colors = {
        success: 'rgba(34, 197, 94, 0.95)',
        error: 'rgba(239, 68, 68, 0.95)',
        warning: 'rgba(245, 158, 11, 0.95)',
        info: 'rgba(59, 130, 246, 0.95)'
    };
    
    toast.style.cssText = `
        background: ${colors[type] || colors.info};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        font-size: 14px;
        max-width: 300px;
        animation: slideIn 0.3s ease-out;
    `;
    
    toast.textContent = message;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

export function showSuccessToast(message, duration = 3000) {
    showToast(message, 'success', duration);
}

export function showErrorToast(message, duration = 5000) {
    showToast(message, 'error', duration);
}

export function showWarningToast(message, duration = 4000) {
    showToast(message, 'warning', duration);
}

export function showInfoToast(message, duration = 3000) {
    showToast(message, 'info', duration);
}

/**
 * Loading spinner system
 */
let loadingOverlay = null;

export function showLoading(message = 'Loading...') {
    if (!loadingOverlay) {
        loadingOverlay = document.createElement('div');
        loadingOverlay.className = 'loading-overlay';
        loadingOverlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            backdrop-filter: blur(5px);
        `;
        
        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner';
        spinner.innerHTML = `
            <div style="text-align: center; color: white;">
                <div class="spinner" style="
                    border: 4px solid rgba(255, 255, 255, 0.3);
                    border-radius: 50%;
                    border-top: 4px solid white;
                    width: 50px;
                    height: 50px;
                    margin: 0 auto 15px;
                    animation: spin 1s linear infinite;
                "></div>
                <div class="loading-message">${message}</div>
            </div>
        `;
        
        loadingOverlay.appendChild(spinner);
        document.body.appendChild(loadingOverlay);
    } else {
        const messageEl = loadingOverlay.querySelector('.loading-message');
        if (messageEl) messageEl.textContent = message;
    }
    
    loadingOverlay.style.display = 'flex';
}

export function hideLoading() {
    if (loadingOverlay) {
        loadingOverlay.style.display = 'none';
    }
}

/**
 * Show inline spinner for panels
 * @param {HTMLElement} container - Container to show spinner in
 * @param {string} message - Optional loading message
 */
export function showPanelSpinner(container, message = 'Loading...') {
    if (!container) return;
    
    container.innerHTML = `
        <div style="
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 3rem 1rem;
            min-height: 200px;
        ">
            <div class="panel-spinner" style="
                border: 4px solid rgba(255, 255, 255, 0.1);
                border-radius: 50%;
                border-top: 4px solid var(--accent-primary);
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
            "></div>
            <div style="
                margin-top: 1rem;
                color: var(--text-secondary);
                font-size: 0.875rem;
            ">${message}</div>
        </div>
    `;
}

/**
 * Hide inline spinner and restore content
 * @param {HTMLElement} container - Container to hide spinner from
 */
export function hidePanelSpinner(container) {
    if (!container) return;
    const spinner = container.querySelector('.panel-spinner');
    if (spinner && spinner.parentElement) {
        spinner.parentElement.remove();
    }
}

/**
 * DOM utility functions
 */
export function createElement(tag, className = '', textContent = '') {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (textContent) element.textContent = textContent;
    return element;
}

export function clearElement(element) {
    while (element.firstChild) {
        element.removeChild(element.firstChild);
    }
}

/**
 * Date formatting
 */
export function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

export function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Number formatting
 */
export function formatNumber(num) {
    return new Intl.NumberFormat('en-US').format(num);
}

export function formatPercent(num, decimals = 1) {
    return `${num.toFixed(decimals)}%`;
}

/**
 * Data validation
 */
export function isValidData(data) {
    return data && typeof data === 'object' && !Array.isArray(data);
}

export function hasRequiredFields(data, fields) {
    return fields.every(field => field in data);
}

/**
 * Error handling
 */
export function handleError(error, context = '') {
    console.error(`Error${context ? ' in ' + context : ''}:`, error);
    showErrorToast(`${context ? context + ': ' : ''}${error.message || 'An error occurred'}`);
}

/**
 * Debounce function
 */
export function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function
 */
export function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}
