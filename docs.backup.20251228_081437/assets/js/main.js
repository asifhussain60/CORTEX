/**
 * CORTEX Enterprise Documentation - Main JavaScript
 * Handles navigation, progressive disclosure, and interactivity
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 */

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    initializeScrollToTop();
    initializeCollapsibles();
    initializeAnimations();
    initializeNavigationScrollEffect();
});

/**
 * Navigation glassmorphism scroll effect
 */
function initializeNavigationScrollEffect() {
    const nav = document.querySelector('.main-nav');
    if (!nav) return;
    
    let lastScroll = 0;
    
    window.addEventListener('scroll', () => {
        const currentScroll = window.scrollY;
        
        // Add scrolled class after 50px
        if (currentScroll > 50) {
            nav.classList.add('scrolled');
        } else {
            nav.classList.remove('scrolled');
        }
        
        lastScroll = currentScroll;
    });
}

/**
 * Scroll to top button functionality
 */
function initializeScrollToTop() {
    const scrollBtn = document.createElement('button');
    scrollBtn.className = 'scroll-to-top';
    scrollBtn.innerHTML = '↑';
    scrollBtn.setAttribute('aria-label', 'Scroll to top');
    document.body.appendChild(scrollBtn);

    // Show/hide based on scroll position
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            scrollBtn.classList.add('visible');
        } else {
            scrollBtn.classList.remove('visible');
        }
    });

    // Scroll to top on click
    scrollBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

/**
 * Initialize collapsible sections for progressive disclosure
 */
function initializeCollapsibles() {
    const collapsibles = document.querySelectorAll('.collapsible-header, .collapsible-tile-header');
    
    collapsibles.forEach(header => {
        header.addEventListener('click', () => {
            const collapsible = header.parentElement;
            const isExpanded = collapsible.classList.contains('expanded');
            
            // Toggle expanded state
            if (isExpanded) {
                collapsible.classList.remove('expanded');
                header.setAttribute('aria-expanded', 'false');
            } else {
                collapsible.classList.add('expanded');
                header.setAttribute('aria-expanded', 'true');
            }
        });
        
        // Set initial ARIA attribute
        header.setAttribute('aria-expanded', 'false');
        header.setAttribute('role', 'button');
    });
}

/**
 * Initialize scroll-triggered animations
 */
function initializeAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe all feature cards and metric cards
    document.querySelectorAll('.feature-card, .metric-card, .glass-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
        observer.observe(el);
    });
}

/**
 * Format numbers with commas for readability
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

/**
 * Load and display real metrics from system
 */
async function loadMetrics() {
    // This will be populated with real data from the system
    // For now, using the metrics from the enhancement plan
    const metrics = {
        operations: 302,
        tiers: 4,
        skullRules: 22,
        workingMemory: 70,
        queryTime: '<100ms',
        testSuccessRate: '94%'
    };

    return metrics;
}
