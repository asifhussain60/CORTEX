/**
 * CORTEX Technical Documentation - Navigation
 * Version: 1.0.0
 * Author: Asif Hussain
 * Copyright: © 2025 Asif Hussain. All rights reserved.
 */

class NavigationManager {
    constructor() {
        this.currentPath = window.location.pathname;
        this.init();
    }

    init() {
        this.highlightCurrentPage();
        this.addNavigationListeners();
        this.setupMobileMenu();
    }

    highlightCurrentPage() {
        const links = document.querySelectorAll('.sidebar-item, .nav-link');
        links.forEach(link => {
            if (link.href && window.location.href.includes(link.href)) {
                link.classList.add('active');
            }
        });
    }

    addNavigationListeners() {
        // Smooth scroll for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        });

        // Track navigation
        document.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                this.trackNavigation(link.href, link.textContent);
            });
        });
    }

    setupMobileMenu() {
        // Create mobile menu toggle if needed
        if (window.innerWidth <= 768) {
            const sidebar = document.querySelector('.sidebar');
            if (sidebar && !document.querySelector('.mobile-menu-toggle')) {
                const toggle = document.createElement('button');
                toggle.className = 'mobile-menu-toggle btn btn-primary';
                toggle.innerHTML = '<i class="fas fa-bars"></i>';
                toggle.style.position = 'fixed';
                toggle.style.bottom = '20px';
                toggle.style.right = '20px';
                toggle.style.zIndex = '1000';

                toggle.addEventListener('click', () => {
                    sidebar.classList.toggle('show');
                });

                document.body.appendChild(toggle);

                // Close menu when clicking outside
                document.addEventListener('click', (e) => {
                    if (!sidebar.contains(e.target) && !toggle.contains(e.target)) {
                        sidebar.classList.remove('show');
                    }
                });
            }
        }
    }

    trackNavigation(url, text) {
        // Track navigation for analytics (if implemented)
        console.log('Navigation:', { url, text, timestamp: new Date().toISOString() });
    }

    // Navigate to a specific page
    navigateTo(path) {
        window.location.href = path;
    }

    // Get current section
    getCurrentSection() {
        const path = this.currentPath;
        if (path.includes('/architecture/')) return 'architecture';
        if (path.includes('/api/')) return 'api';
        if (path.includes('/workflows/')) return 'workflows';
        if (path.includes('/integration/')) return 'integration';
        if (path.includes('/deployment/')) return 'deployment';
        if (path.includes('/setup-guides/')) return 'guides';
        return 'home';
    }

    // Get breadcrumb trail
    getBreadcrumbs() {
        const parts = this.currentPath.split('/').filter(p => p);
        const breadcrumbs = [{ label: 'Home', path: '/index.html' }];

        let currentPath = '';
        parts.forEach((part, index) => {
            currentPath += '/' + part;
            if (index < parts.length - 1) {
                breadcrumbs.push({
                    label: part.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
                    path: currentPath + '/index.html'
                });
            }
        });

        return breadcrumbs;
    }

    // Render breadcrumbs
    renderBreadcrumbs(container) {
        const breadcrumbs = this.getBreadcrumbs();
        const html = breadcrumbs.map((crumb, index) => {
            const isLast = index === breadcrumbs.length - 1;
            return isLast ? 
                `<span style="color: var(--text-secondary);">${crumb.label}</span>` :
                `<a href="${crumb.path}" style="color: var(--primary); text-decoration: none;">${crumb.label}</a>`;
        }).join(' <i class="fas fa-chevron-right" style="font-size: 10px; color: var(--text-muted);"></i> ');

        if (container) {
            container.innerHTML = html;
        }
        return html;
    }
}

// Initialize navigation on page load
document.addEventListener('DOMContentLoaded', () => {
    window.navManager = new NavigationManager();
    
    // Render breadcrumbs if container exists
    const breadcrumbContainer = document.getElementById('breadcrumbs');
    if (breadcrumbContainer) {
        window.navManager.renderBreadcrumbs(breadcrumbContainer);
    }
});
