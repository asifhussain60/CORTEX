/**
 * CORTEX Dashboard Header Component
 * Displays navigation header with CORTEX logo, title, and navigation controls
 * 
 * @module header
 * @author Asif Hussain
 * @copyright ┬⌐ 2025-2026 Asif Hussain. All rights reserved.
 */

class CORTEXHeader {
  constructor(options = {}) {
    this.options = {
      logoPath: options.logoPath || './assets/cortex-logo.png',
      logoWhitePath: options.logoWhitePath || './assets/cortex-logo-white.png',
      title: options.title || 'CORTEX Neural Observatory',
      onLogoClick: options.onLogoClick || (() => window.location.hash = '#/'),
      darkMode: options.darkMode || false,
      ...options
    };
    
    this.headerElement = null;
    this.isOpen = false;
    this.darkModeToggle = null;
    
    this.init();
  }
  
  /**
   * Initialize header component
   */
  init() {
    this.render();
    this.setupEventListeners();
    this.setupResponsiveMenu();
  }
  
  /**
   * Render header HTML
   */
  render() {
    const headerHTML = `
      <header class="cortex-header">
        <!-- Logo and Title Section -->
        <div class="header-brand">
          <button class="logo-button" id="logo-btn" aria-label="Return to dashboard home">
            <img 
              src="${this.options.logoPath}" 
              alt="CORTEX Logo" 
              class="cortex-logo"
              id="header-logo"
            />
          </button>
          
          <div class="title-section">
            <h1 class="header-title">${this.options.title}</h1>
            <p class="header-subtitle">Brain Visualization & Governance Hub</p>
          </div>
        </div>
        
        <!-- Navigation Menu (Desktop) -->
        <nav class="header-nav desktop-only">
          <a href="#/" class="nav-link active" data-view="observatory">Brain Observatory</a>
          <a href="#/temporal" class="nav-link" data-view="temporal">Temporal Cortex</a>
          <a href="#/orchestrators" class="nav-link" data-view="constellation">Orchestrators</a>
          <a href="#/plans" class="nav-link" data-view="plans">Plan Hub</a>
          <a href="#/admin" class="nav-link" data-view="admin">Admin</a>
        </nav>
        
        <!-- Header Controls -->
        <div class="header-controls">
          <!-- Search -->
          <div class="search-box">
            <input 
              type="text" 
              class="search-input" 
              placeholder="Search AC-IDs, phases, orchestrators..."
              id="global-search"
              aria-label="Global search"
            />
            <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="11" cy="11" r="8"></circle>
              <path d="m21 21-4.35-4.35"></path>
            </svg>
          </div>
          
          <!-- Notification Bell -->
          <button class="header-button" id="notifications-btn" aria-label="Notifications">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="icon-bell">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
              <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
            </svg>
            <span class="notification-badge" id="notification-count" style="display: none;">0</span>
          </button>
          
          <!-- Dark Mode Toggle -->
          <button class="header-button" id="dark-mode-btn" aria-label="Toggle dark mode">
            <svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="5"></circle>
              <line x1="12" y1="1" x2="12" y2="3"></line>
              <line x1="12" y1="21" x2="12" y2="23"></line>
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
              <line x1="1" y1="12" x2="3" y2="12"></line>
              <line x1="21" y1="12" x2="23" y2="12"></line>
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
            </svg>
            <svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="display: none;">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
            </svg>
          </button>
          
          <!-- Mobile Menu Toggle -->
          <button class="header-button mobile-only" id="menu-toggle" aria-label="Toggle menu">
            <svg class="icon-menu" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <line x1="3" y1="12" x2="21" y2="12"></line>
              <line x1="3" y1="18" x2="21" y2="18"></line>
            </svg>
            <svg class="icon-close" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="display: none;">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
      </header>
      
      <!-- Mobile Navigation Menu -->
      <nav class="header-nav-mobile" id="mobile-nav" style="display: none;">
        <a href="#/" class="nav-link-mobile" data-view="observatory">Brain Observatory</a>
        <a href="#/temporal" class="nav-link-mobile" data-view="temporal">Temporal Cortex</a>
        <a href="#/orchestrators" class="nav-link-mobile" data-view="constellation">Orchestrators</a>
        <a href="#/plans" class="nav-link-mobile" data-view="plans">Plan Hub</a>
        <a href="#/admin" class="nav-link-mobile" data-view="admin">Admin</a>
      </nav>
      
      <!-- Notification Center (Dropdown) -->
      <div class="notification-dropdown" id="notification-dropdown" style="display: none;">
        <div class="notification-header">
          <h3>Notifications</h3>
          <button class="notification-close" id="notification-close">├ù</button>
        </div>
        <div class="notification-list" id="notification-list">
          <div class="notification-empty">No notifications</div>
        </div>
      </div>
    `;
    
    // Insert into DOM
    this.headerElement = document.createElement('div');
    this.headerElement.innerHTML = headerHTML;
    document.body.insertBefore(this.headerElement, document.body.firstChild);
  }
  
  /**
   * Setup event listeners
   */
  setupEventListeners() {
    // Logo click
    document.getElementById('logo-btn').addEventListener('click', () => {
      this.options.onLogoClick();
    });
    
    // Dark mode toggle
    const darkModeBtn = document.getElementById('dark-mode-btn');
    darkModeBtn.addEventListener('click', () => this.toggleDarkMode());
    
    // Notification button
    const notificationsBtn = document.getElementById('notifications-btn');
    notificationsBtn.addEventListener('click', () => this.toggleNotificationDropdown());
    
    // Close notification dropdown
    document.getElementById('notification-close')?.addEventListener('click', () => {
      this.closeNotificationDropdown();
    });
    
    // Mobile menu toggle
    const menuToggle = document.getElementById('menu-toggle');
    menuToggle?.addEventListener('click', () => this.toggleMobileMenu());
    
    // Global search
    document.getElementById('global-search').addEventListener('input', (e) => {
      this.handleGlobalSearch(e.target.value);
    });
    
    // Navigation links
    document.querySelectorAll('.nav-link, .nav-link-mobile').forEach(link => {
      link.addEventListener('click', (e) => {
        this.setActiveNav(e.target);
        this.closeMobileMenu();
      });
    });
  }
  
  /**
   * Setup responsive menu behavior
   */
  setupResponsiveMenu() {
    // Handle window resize
    window.addEventListener('resize', () => {
      if (window.innerWidth > 768) {
        this.closeMobileMenu();
      }
    });
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', (e) => {
      const header = document.querySelector('.cortex-header');
      const mobileNav = document.getElementById('mobile-nav');
      
      if (!header?.contains(e.target) && !mobileNav?.contains(e.target)) {
        this.closeMobileMenu();
      }
    });
  }
  
  /**
   * Toggle dark mode
   */
  toggleDarkMode() {
    const isDarkMode = document.documentElement.classList.toggle('dark-mode');
    const sunIcon = document.querySelector('.icon-sun');
    const moonIcon = document.querySelector('.icon-moon');
    
    if (isDarkMode) {
      sunIcon.style.display = 'none';
      moonIcon.style.display = 'block';
      localStorage.setItem('cortex-dark-mode', 'true');
      this.updateLogoForDarkMode(true);
    } else {
      sunIcon.style.display = 'block';
      moonIcon.style.display = 'none';
      localStorage.setItem('cortex-dark-mode', 'false');
      this.updateLogoForDarkMode(false);
    }
    
    // Dispatch event for other components to listen to
    window.dispatchEvent(new CustomEvent('cortex-dark-mode-changed', { 
      detail: { isDarkMode } 
    }));
  }
  
  /**
   * Update logo based on dark mode
   */
  updateLogoForDarkMode(isDarkMode) {
    const logo = document.getElementById('header-logo');
    if (isDarkMode) {
      logo.src = this.options.logoWhitePath;
    } else {
      logo.src = this.options.logoPath;
    }
  }
  
  /**
   * Toggle notification dropdown
   */
  toggleNotificationDropdown() {
    const dropdown = document.getElementById('notification-dropdown');
    dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
  }
  
  /**
   * Close notification dropdown
   */
  closeNotificationDropdown() {
    document.getElementById('notification-dropdown').style.display = 'none';
  }
  
  /**
   * Toggle mobile menu
   */
  toggleMobileMenu() {
    if (this.isOpen) {
      this.closeMobileMenu();
    } else {
      this.openMobileMenu();
    }
  }
  
  /**
   * Open mobile menu
   */
  openMobileMenu() {
    const mobileNav = document.getElementById('mobile-nav');
    const menuIcon = document.querySelector('.icon-menu');
    const closeIcon = document.querySelector('.icon-close');
    
    mobileNav.style.display = 'block';
    menuIcon.style.display = 'none';
    closeIcon.style.display = 'block';
    this.isOpen = true;
  }
  
  /**
   * Close mobile menu
   */
  closeMobileMenu() {
    const mobileNav = document.getElementById('mobile-nav');
    const menuIcon = document.querySelector('.icon-menu');
    const closeIcon = document.querySelector('.icon-close');
    
    mobileNav.style.display = 'none';
    menuIcon.style.display = 'block';
    closeIcon.style.display = 'none';
    this.isOpen = false;
  }
  
  /**
   * Set active navigation link
   */
  setActiveNav(element) {
    document.querySelectorAll('.nav-link, .nav-link-mobile').forEach(link => {
      link.classList.remove('active');
    });
    element.classList.add('active');
  }
  
  /**
   * Handle global search
   */
  handleGlobalSearch(query) {
    // Dispatch search event for other components to listen to
    window.dispatchEvent(new CustomEvent('cortex-global-search', { 
      detail: { query } 
    }));
  }
  
  /**
   * Add notification
   */
  addNotification(notification) {
    const { type = 'info', title, message, duration = 5000 } = notification;
    
    const notificationList = document.getElementById('notification-list');
    const badge = document.getElementById('notification-count');
    
    // Create notification element
    const notifElement = document.createElement('div');
    notifElement.className = `notification-item notification-${type}`;
    notifElement.innerHTML = `
      <div class="notification-content">
        <div class="notification-title">${title}</div>
        <div class="notification-message">${message}</div>
      </div>
      <button class="notification-dismiss">├ù</button>
    `;
    
    notificationList.appendChild(notifElement);
    
    // Update badge
    const count = parseInt(badge.textContent || 0) + 1;
    badge.textContent = count;
    badge.style.display = count > 0 ? 'flex' : 'none';
    
    // Auto-dismiss info notifications
    if (type === 'info' && duration > 0) {
      setTimeout(() => {
        notifElement.remove();
        const newCount = Math.max(0, parseInt(badge.textContent || 1) - 1);
        badge.textContent = newCount;
        badge.style.display = newCount > 0 ? 'flex' : 'none';
      }, duration);
    }
    
    // Dismiss button
    notifElement.querySelector('.notification-dismiss').addEventListener('click', () => {
      notifElement.remove();
      const newCount = Math.max(0, parseInt(badge.textContent || 1) - 1);
      badge.textContent = newCount;
      badge.style.display = newCount > 0 ? 'flex' : 'none';
    });
  }
  
  /**
   * Clear all notifications
   */
  clearNotifications() {
    document.getElementById('notification-list').innerHTML = '<div class="notification-empty">No notifications</div>';
    document.getElementById('notification-count').style.display = 'none';
  }
  
  /**
   * Initialize dark mode from localStorage
   */
  initializeDarkMode() {
    const isDarkMode = localStorage.getItem('cortex-dark-mode') === 'true';
    if (isDarkMode) {
      document.documentElement.classList.add('dark-mode');
      const sunIcon = document.querySelector('.icon-sun');
      const moonIcon = document.querySelector('.icon-moon');
      sunIcon.style.display = 'none';
      moonIcon.style.display = 'block';
      this.updateLogoForDarkMode(true);
    }
  }
}

// Initialize header on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  const header = new CORTEXHeader({
    logoPath: './assets/cortex-logo.png',
    logoWhitePath: './assets/cortex-logo-white.png',
    title: 'CORTEX Neural Observatory',
    onLogoClick: () => window.location.hash = '#/'
  });
  
  header.initializeDarkMode();
  
  // Make available globally
  window.CORTEXHeader = header;
});

export { CORTEXHeader };
