/**
 * Visual Polish & Enhancement Module
 * Smooth animations, loading states, tooltips, and micro-interactions
 * 
 * Features:
 * - Loading skeleton screens
 * - Progress indicators with animations
 * - Enhanced tooltips with smart positioning
 * - Smooth transitions and micro-interactions
 * - Visual feedback for user actions
 */

class VisualPolishManager {
    constructor() {
        this.init();
    }

    init() {
        this.setupLoadingStates();
        this.setupTooltips();
        this.setupMicroInteractions();
        this.setupProgressIndicators();
        this.addSmoothTransitions();
        console.log('Visual polish features initialized');
    }

    /**
     * Setup loading skeleton screens
     */
    setupLoadingStates() {
        // Add CSS for skeleton screens
        const style = document.createElement('style');
        style.textContent = `
            /* Skeleton screen animations */
            @keyframes skeleton-loading {
                0% {
                    background-position: -200px 0;
                }
                100% {
                    background-position: calc(200px + 100%) 0;
                }
            }
            
            .skeleton {
                background: linear-gradient(
                    90deg,
                    #f0f0f0 0px,
                    #e0e0e0 40px,
                    #f0f0f0 80px
                );
                background-size: 200px 100%;
                animation: skeleton-loading 1.5s infinite;
                border-radius: 4px;
            }
            
            .skeleton-text {
                height: 16px;
                margin-bottom: 8px;
            }
            
            .skeleton-title {
                height: 24px;
                width: 40%;
                margin-bottom: 16px;
            }
            
            .skeleton-card {
                height: 120px;
                border-radius: 8px;
            }
            
            .skeleton-chart {
                height: 300px;
                border-radius: 8px;
            }
            
            .skeleton-table-row {
                height: 48px;
                margin-bottom: 4px;
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Create skeleton screen for content
     */
    createSkeletonScreen(type = 'default') {
        const skeleton = document.createElement('div');
        skeleton.className = 'skeleton-container';
        
        switch(type) {
            case 'table':
                skeleton.innerHTML = `
                    <div class="skeleton skeleton-title"></div>
                    ${Array(5).fill().map(() => 
                        '<div class="skeleton skeleton-table-row"></div>'
                    ).join('')}
                `;
                break;
            case 'chart':
                skeleton.innerHTML = `
                    <div class="skeleton skeleton-title"></div>
                    <div class="skeleton skeleton-chart"></div>
                `;
                break;
            case 'cards':
                skeleton.innerHTML = `
                    <div class="skeleton skeleton-title"></div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;">
                        ${Array(4).fill().map(() => 
                            '<div class="skeleton skeleton-card"></div>'
                        ).join('')}
                    </div>
                `;
                break;
            default:
                skeleton.innerHTML = `
                    <div class="skeleton skeleton-title"></div>
                    ${Array(3).fill().map(() => 
                        '<div class="skeleton skeleton-text"></div>'
                    ).join('')}
                `;
        }
        
        return skeleton;
    }

    /**
     * Show loading indicator
     */
    showLoading(element, type = 'default') {
        const skeleton = this.createSkeletonScreen(type);
        element.innerHTML = '';
        element.appendChild(skeleton);
    }

    /**
     * Setup enhanced tooltips
     */
    setupTooltips() {
        const style = document.createElement('style');
        style.textContent = `
            .tooltip-container {
                position: relative;
                display: inline-block;
            }
            
            .tooltip {
                position: absolute;
                background: #333;
                color: #fff;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 0.875rem;
                white-space: nowrap;
                opacity: 0;
                pointer-events: none;
                transition: opacity 0.2s ease-in-out;
                z-index: 1000;
                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            }
            
            .tooltip.visible {
                opacity: 1;
            }
            
            .tooltip::before {
                content: '';
                position: absolute;
                border: 6px solid transparent;
            }
            
            /* Tooltip arrow positioning */
            .tooltip.top {
                bottom: 100%;
                left: 50%;
                transform: translateX(-50%) translateY(-8px);
                margin-bottom: 6px;
            }
            
            .tooltip.top::before {
                top: 100%;
                left: 50%;
                transform: translateX(-50%);
                border-top-color: #333;
            }
            
            .tooltip.bottom {
                top: 100%;
                left: 50%;
                transform: translateX(-50%) translateY(8px);
                margin-top: 6px;
            }
            
            .tooltip.bottom::before {
                bottom: 100%;
                left: 50%;
                transform: translateX(-50%);
                border-bottom-color: #333;
            }
            
            .tooltip.left {
                right: 100%;
                top: 50%;
                transform: translateY(-50%) translateX(-8px);
                margin-right: 6px;
            }
            
            .tooltip.left::before {
                left: 100%;
                top: 50%;
                transform: translateY(-50%);
                border-left-color: #333;
            }
            
            .tooltip.right {
                left: 100%;
                top: 50%;
                transform: translateY(-50%) translateX(8px);
                margin-left: 6px;
            }
            
            .tooltip.right::before {
                right: 100%;
                top: 50%;
                transform: translateY(-50%);
                border-right-color: #333;
            }
        `;
        document.head.appendChild(style);

        // Attach tooltips to elements with data-tooltip
        this.attachTooltips();
    }

    /**
     * Attach tooltips to elements
     */
    attachTooltips() {
        document.querySelectorAll('[data-tooltip]').forEach(element => {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = element.getAttribute('data-tooltip');
            
            const position = element.getAttribute('data-tooltip-position') || 'top';
            tooltip.classList.add(position);
            
            element.style.position = 'relative';
            element.appendChild(tooltip);
            
            element.addEventListener('mouseenter', () => {
                tooltip.classList.add('visible');
            });
            
            element.addEventListener('mouseleave', () => {
                tooltip.classList.remove('visible');
            });
        });
    }

    /**
     * Setup micro-interactions
     */
    setupMicroInteractions() {
        const style = document.createElement('style');
        style.textContent = `
            /* Smooth transitions for all interactive elements */
            .tab-button,
            button,
            a,
            .metric-card,
            .chart-container,
            .table-row {
                transition: all 0.2s ease-in-out;
            }
            
            /* Button press effect */
            button:active,
            .tab-button:active {
                transform: scale(0.97);
            }
            
            /* Hover effects */
            .tab-button:hover:not(.active) {
                background-color: rgba(0, 102, 204, 0.1);
                transform: translateY(-2px);
            }
            
            button:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            
            .metric-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 6px 12px rgba(0,0,0,0.1);
            }
            
            /* Table row hover */
            .table-row:hover {
                background-color: rgba(0, 102, 204, 0.05);
            }
            
            /* Loading spinner */
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .spinner {
                border: 3px solid #f3f3f3;
                border-top: 3px solid #0066cc;
                border-radius: 50%;
                width: 24px;
                height: 24px;
                animation: spin 1s linear infinite;
            }
            
            /* Pulse animation for loading states */
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            
            .pulse {
                animation: pulse 1.5s ease-in-out infinite;
            }
            
            /* Fade in animation */
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            .fade-in {
                animation: fadeIn 0.3s ease-in-out;
            }
            
            /* Slide in animation */
            @keyframes slideInUp {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .slide-in-up {
                animation: slideInUp 0.4s ease-out;
            }
            
            /* Success checkmark animation */
            @keyframes checkmark {
                0% {
                    stroke-dashoffset: 100;
                }
                100% {
                    stroke-dashoffset: 0;
                }
            }
            
            .checkmark {
                stroke-dasharray: 100;
                stroke-dashoffset: 100;
                animation: checkmark 0.5s ease-out forwards;
            }
        `;
        document.head.appendChild(style);

        // Add ripple effect to buttons
        this.addRippleEffect();
    }

    /**
     * Add ripple effect to buttons
     */
    addRippleEffect() {
        document.querySelectorAll('button, .tab-button').forEach(button => {
            button.addEventListener('click', function(e) {
                const ripple = document.createElement('span');
                ripple.className = 'ripple';
                
                const rect = this.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.cssText = `
                    position: absolute;
                    width: ${size}px;
                    height: ${size}px;
                    left: ${x}px;
                    top: ${y}px;
                    border-radius: 50%;
                    background: rgba(255, 255, 255, 0.6);
                    transform: scale(0);
                    animation: ripple-effect 0.6s ease-out;
                    pointer-events: none;
                `;
                
                this.style.position = 'relative';
                this.style.overflow = 'hidden';
                this.appendChild(ripple);
                
                setTimeout(() => ripple.remove(), 600);
            });
        });

        const style = document.createElement('style');
        style.textContent = `
            @keyframes ripple-effect {
                to {
                    transform: scale(2);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Setup progress indicators
     */
    setupProgressIndicators() {
        const style = document.createElement('style');
        style.textContent = `
            /* Progress bar */
            .progress-bar {
                width: 100%;
                height: 8px;
                background: #e0e0e0;
                border-radius: 4px;
                overflow: hidden;
                position: relative;
            }
            
            .progress-bar-fill {
                height: 100%;
                background: linear-gradient(90deg, #0066cc, #0088ee);
                transition: width 0.3s ease-out;
                border-radius: 4px;
            }
            
            .progress-bar-indeterminate .progress-bar-fill {
                width: 30%;
                animation: progress-indeterminate 1.5s ease-in-out infinite;
            }
            
            @keyframes progress-indeterminate {
                0% {
                    left: -30%;
                }
                100% {
                    left: 100%;
                }
            }
            
            /* Circular progress */
            .circular-progress {
                width: 40px;
                height: 40px;
                position: relative;
            }
            
            .circular-progress svg {
                transform: rotate(-90deg);
            }
            
            .circular-progress circle {
                fill: none;
                stroke-width: 4;
            }
            
            .circular-progress .bg-circle {
                stroke: #e0e0e0;
            }
            
            .circular-progress .progress-circle {
                stroke: #0066cc;
                stroke-dasharray: 126;
                stroke-dashoffset: 126;
                transition: stroke-dashoffset 0.3s ease-out;
            }
            
            /* Status badges */
            .status-badge {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .status-badge.success {
                background: #d4edda;
                color: #155724;
            }
            
            .status-badge.warning {
                background: #fff3cd;
                color: #856404;
            }
            
            .status-badge.danger {
                background: #f8d7da;
                color: #721c24;
            }
            
            .status-badge.info {
                background: #d1ecf1;
                color: #0c5460;
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Create linear progress bar
     */
    createProgressBar(value = 0, indeterminate = false) {
        const container = document.createElement('div');
        container.className = `progress-bar${indeterminate ? ' progress-bar-indeterminate' : ''}`;
        
        const fill = document.createElement('div');
        fill.className = 'progress-bar-fill';
        if (!indeterminate) {
            fill.style.width = `${Math.min(100, Math.max(0, value))}%`;
        }
        
        container.appendChild(fill);
        return container;
    }

    /**
     * Update progress bar value
     */
    updateProgressBar(progressBar, value) {
        const fill = progressBar.querySelector('.progress-bar-fill');
        if (fill) {
            fill.style.width = `${Math.min(100, Math.max(0, value))}%`;
        }
    }

    /**
     * Create circular progress indicator
     */
    createCircularProgress(value = 0) {
        const container = document.createElement('div');
        container.className = 'circular-progress';
        
        const radius = 18;
        const circumference = 2 * Math.PI * radius;
        const offset = circumference - (value / 100) * circumference;
        
        container.innerHTML = `
            <svg width="40" height="40" viewBox="0 0 40 40">
                <circle class="bg-circle" cx="20" cy="20" r="${radius}"></circle>
                <circle class="progress-circle" cx="20" cy="20" r="${radius}" 
                        style="stroke-dashoffset: ${offset}"></circle>
            </svg>
        `;
        
        return container;
    }

    /**
     * Add smooth transitions to page elements
     */
    addSmoothTransitions() {
        // Add fade-in to tab content when switching
        const observer = new MutationObserver(mutations => {
            mutations.forEach(mutation => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                    const target = mutation.target;
                    if (target.classList.contains('tab-content') && 
                        target.style.display === 'block') {
                        target.classList.add('fade-in');
                    }
                }
            });
        });

        document.querySelectorAll('.tab-content').forEach(content => {
            observer.observe(content, { attributes: true });
        });

        // Stagger animation for metrics cards
        const cards = document.querySelectorAll('.metric-card');
        cards.forEach((card, index) => {
            card.style.animation = `slideInUp 0.4s ease-out ${index * 0.1}s both`;
        });
    }

    /**
     * Show success message with animation
     */
    showSuccess(message, duration = 3000) {
        const toast = document.createElement('div');
        toast.className = 'toast success slide-in-up';
        toast.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 20 20" style="margin-right: 8px;">
                <circle cx="10" cy="10" r="9" fill="#28a745" />
                <path d="M6 10 L9 13 L14 7" stroke="white" stroke-width="2" 
                      fill="none" stroke-linecap="round" stroke-linejoin="round" 
                      class="checkmark" />
            </svg>
            <span>${message}</span>
        `;
        
        this.showToast(toast, duration);
    }

    /**
     * Show error message with animation
     */
    showError(message, duration = 4000) {
        const toast = document.createElement('div');
        toast.className = 'toast error slide-in-up';
        toast.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 20 20" style="margin-right: 8px;">
                <circle cx="10" cy="10" r="9" fill="#dc3545" />
                <path d="M7 7 L13 13 M13 7 L7 13" stroke="white" stroke-width="2" 
                      stroke-linecap="round" />
            </svg>
            <span>${message}</span>
        `;
        
        this.showToast(toast, duration);
    }

    /**
     * Show toast notification
     */
    showToast(toast, duration) {
        const style = document.createElement('style');
        style.textContent = `
            .toast {
                position: fixed;
                bottom: 24px;
                right: 24px;
                background: white;
                padding: 16px 20px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                display: flex;
                align-items: center;
                z-index: 10000;
                font-size: 0.875rem;
                max-width: 400px;
            }
            
            .toast.success {
                border-left: 4px solid #28a745;
            }
            
            .toast.error {
                border-left: 4px solid #dc3545;
            }
        `;
        
        if (!document.querySelector('style[data-toast-styles]')) {
            style.setAttribute('data-toast-styles', 'true');
            document.head.appendChild(style);
        }
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'fadeOut 0.3s ease-out';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
}

// Initialize visual polish features when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.visualPolishManager = new VisualPolishManager();
    });
} else {
    window.visualPolishManager = new VisualPolishManager();
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VisualPolishManager;
}
