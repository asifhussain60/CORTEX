/**
 * CORTEX Dashboard - Sidebar Navigation Component
 *
 * Manages sidebar navigation: initialization, active state management,
 * collapse/expand toggle, and mobile hamburger menu.
 *
 * Authority: DO-002-01 Sidebar Navigation with Active States
 * Governance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
 */

'use strict';

// === Constants ===
const SIDEBAR_COLLAPSED_KEY = 'cortex_sidebar_collapsed';
const ACTIVE_CLASS = 'active';
const COLLAPSED_CLASS = 'collapsed';
const MOBILE_OPEN_CLASS = 'mobile-open';

/**
 * Initialize the sidebar navigation component.
 *
 * Sets up event listeners, restores persisted state, and activates
 * the current page section in the navigation.
 */
function initializeSidebar() {
  const sidebar = document.getElementById('sidebar') || document.querySelector('.sidebar');
  if (!sidebar) return;

  // Restore persisted collapsed state
  const isCollapsed = localStorage.getItem(SIDEBAR_COLLAPSED_KEY) === 'true';
  if (isCollapsed) {
    sidebar.classList.add(COLLAPSED_CLASS);
  }

  // Set active section based on current URL
  const currentPath = window.location.pathname;
  setActiveSection(currentPath);

  // Attach collapse toggle
  const toggleBtn = document.querySelector('.sidebar-toggle');
  if (toggleBtn) {
    toggleBtn.addEventListener('click', function () {
      toggleSidebarCollapse();
    });
  }

  // Attach navigation click handlers
  const navItems = document.querySelectorAll('.sidebar-nav-item, .sidebar-link, .nav-item');
  navItems.forEach(function (item) {
    item.addEventListener('click', function (event) {
      const href = item.getAttribute('href') || item.dataset.href;
      if (href && href !== '#') {
        // Let navigation happen
        return;
      }
      // Prevent default for non-navigating items
      event.preventDefault();
      const sectionId = item.dataset.section;
      if (sectionId) {
        setActiveSection(sectionId);
      }
    });
  });

  // Mobile hamburger menu
  const hamburger = document.querySelector('.hamburger-menu, .mobile-menu-btn');
  if (hamburger) {
    hamburger.addEventListener('click', function () {
      toggleMobileSidebar();
    });
  }
}

/**
 * Set the active navigation section.
 *
 * Removes .active class from all nav items and adds it to the item
 * matching the given section identifier or URL path.
 *
 * @param {string} sectionId - Section identifier or URL path
 */
function setActiveSection(sectionId) {
  // Remove active from all items
  const allNavItems = document.querySelectorAll('.sidebar-nav-item, .sidebar-link, .nav-item');
  allNavItems.forEach(function (item) {
    item.classList.remove(ACTIVE_CLASS);
  });

  if (!sectionId) return;

  // Find matching nav item by href, data-section, or text content
  let activeItem = document.querySelector(`[href="${sectionId}"]`) ||
    document.querySelector(`[data-section="${sectionId}"]`) ||
    document.querySelector(`[data-href="${sectionId}"]`);

  // Fallback: partial path match
  if (!activeItem) {
    allNavItems.forEach(function (item) {
      const href = item.getAttribute('href') || '';
      if (href && sectionId.includes(href) && href !== '/') {
        activeItem = item;
      }
    });
  }

  if (activeItem) {
    activeItem.classList.add(ACTIVE_CLASS);
  }
}

/**
 * Toggle sidebar collapse/expand state.
 *
 * Adds or removes the .collapsed class and persists the state to localStorage.
 */
function toggleSidebarCollapse() {
  const sidebar = document.getElementById('sidebar') || document.querySelector('.sidebar');
  if (!sidebar) return;

  sidebar.classList.toggle(COLLAPSED_CLASS);

  // Persist state
  const isCollapsed = sidebar.classList.contains(COLLAPSED_CLASS);
  localStorage.setItem(SIDEBAR_COLLAPSED_KEY, String(isCollapsed));
}

/**
 * Toggle sidebar visibility on mobile.
 *
 * Adds or removes the .mobile-open class on the sidebar.
 */
function toggleMobileSidebar() {
  const sidebar = document.getElementById('sidebar') || document.querySelector('.sidebar');
  if (!sidebar) return;

  sidebar.classList.toggle(MOBILE_OPEN_CLASS);
}

/**
 * Close mobile sidebar.
 *
 * Used when a navigation item is clicked on mobile.
 */
function closeMobileSidebar() {
  const sidebar = document.getElementById('sidebar') || document.querySelector('.sidebar');
  if (sidebar) {
    sidebar.classList.remove(MOBILE_OPEN_CLASS);
  }
}

// Auto-initialize when DOM is ready
if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeSidebar);
  } else {
    initializeSidebar();
  }
}

// Export for module environments
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    initializeSidebar,
    setActiveSection,
    toggleSidebarCollapse,
    toggleMobileSidebar,
    closeMobileSidebar,
  };
}
