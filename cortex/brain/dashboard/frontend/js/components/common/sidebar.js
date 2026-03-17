/**
 * CORTEX Dashboard — Sidebar Navigation Component
 * Manages active states, collapse/expand, and navigation.
 *
 * Features:
 *  - initializeSidebar() — wires all event listeners
 *  - setActiveSection() — marks current navigation item as active
 *  - toggleSidebarCollapse() — collapses/expands sidebar
 *  - Click handlers for all navigation items
 *  - localStorage persistence for collapsed state
 */

(function () {
  'use strict';

  /* -------------------------------------------------------------------------
     State
     ------------------------------------------------------------------------- */
  const COLLAPSED_KEY = 'cortex-sidebar-collapsed';
  const ACTIVE_CLASS = 'active';
  const COLLAPSED_CLASS = 'collapsed';

  /* -------------------------------------------------------------------------
     setActiveSection — marks the matching nav item as active
     ------------------------------------------------------------------------- */
  function setActiveSection(sectionId) {
    const navItems = document.querySelectorAll(
      '.sidebar-nav-item, .sidebar-link, .nav-item'
    );

    navItems.forEach(function (item) {
      item.classList.remove(ACTIVE_CLASS);
      item.removeAttribute('aria-current');
    });

    if (sectionId) {
      const target = document.querySelector(
        `[data-section="${sectionId}"], [href="#${sectionId}"]`
      );
      if (target) {
        target.classList.add(ACTIVE_CLASS);
        target.setAttribute('aria-current', 'page');
      }
    }
  }

  /* -------------------------------------------------------------------------
     toggleSidebarCollapse — collapses or expands the sidebar
     -------------------------------------------------------------------------- */
  function toggleSidebarCollapse() {
    const sidebar = document.querySelector('.sidebar');
    if (!sidebar) {
      return;
    }

    const isCollapsed = sidebar.classList.toggle(COLLAPSED_CLASS);

    // Persist state
    try {
      localStorage.setItem(COLLAPSED_KEY, isCollapsed ? '1' : '0');
    } catch (_) {
      // localStorage may be unavailable (private browsing)
    }

    // Update toggle button accessible label
    const toggleBtn = document.querySelector(
      '.sidebar-collapse-btn, .sidebar-toggle-btn'
    );
    if (toggleBtn) {
      toggleBtn.setAttribute(
        'aria-label',
        isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'
      );
      toggleBtn.setAttribute('aria-expanded', String(!isCollapsed));
    }
  }

  /* -------------------------------------------------------------------------
     Restore collapsed state from localStorage
     -------------------------------------------------------------------------- */
  function restoreCollapsedState() {
    try {
      const stored = localStorage.getItem(COLLAPSED_KEY);
      if (stored === '1') {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
          sidebar.classList.add(COLLAPSED_CLASS);
        }
      }
    } catch (_) {
      // Ignore storage errors
    }
  }

  /* -------------------------------------------------------------------------
     Attach navigation click handlers
     -------------------------------------------------------------------------- */
  function attachNavigationHandlers() {
    const navItems = document.querySelectorAll(
      '.sidebar-nav-item, .sidebar-link, .nav-item'
    );

    navItems.forEach(function (item) {
      item.addEventListener('click', function (event) {
        const href = item.getAttribute('href');
        if (href && href !== '#') {
          // Allow normal link navigation
          return;
        }

        event.preventDefault();

        // Set this item as active
        navItems.forEach(function (n) {
          n.classList.remove(ACTIVE_CLASS);
          n.removeAttribute('aria-current');
        });

        item.classList.add(ACTIVE_CLASS);
        item.setAttribute('aria-current', 'page');

        const sectionId = item.dataset.section;
        if (sectionId) {
          const target = document.querySelector(`#${sectionId}`);
          if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        }
      });
    });
  }

  /* -------------------------------------------------------------------------
     Attach collapse/expand toggle
     -------------------------------------------------------------------------- */
  function attachCollapseHandler() {
    const toggleBtn = document.querySelector(
      '.sidebar-collapse-btn, .sidebar-toggle-btn'
    );
    if (toggleBtn) {
      toggleBtn.addEventListener('click', toggleSidebarCollapse);
    }
  }

  /* -------------------------------------------------------------------------
     Auto-detect active section from URL
     -------------------------------------------------------------------------- */
  function detectActiveFromURL() {
    const hash = window.location.hash.replace('#', '');
    const path = window.location.pathname;

    const navItems = document.querySelectorAll(
      '.sidebar-nav-item, .sidebar-link, .nav-item'
    );

    navItems.forEach(function (item) {
      const href = item.getAttribute('href') || '';
      if (
        (hash && href.includes(hash)) ||
        (path && href === path) ||
        (item.dataset.section && path.includes(item.dataset.section))
      ) {
        item.classList.add(ACTIVE_CLASS);
        item.setAttribute('aria-current', 'page');
      }
    });
  }

  /* -------------------------------------------------------------------------
     initializeSidebar — main entry point
     -------------------------------------------------------------------------- */
  function initializeSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (!sidebar) {
      return;
    }

    // Restore persisted state first
    restoreCollapsedState();

    // Attach all handlers
    attachNavigationHandlers();
    attachCollapseHandler();

    // Detect active section from current URL
    detectActiveFromURL();

    // Mark sidebar as initialized
    sidebar.setAttribute('data-initialized', 'true');
  }

  /* -------------------------------------------------------------------------
     Auto-initialize when DOM is ready
     -------------------------------------------------------------------------- */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeSidebar);
  } else {
    initializeSidebar();
  }

  /* -------------------------------------------------------------------------
     Public API
     -------------------------------------------------------------------------- */
  if (typeof window !== 'undefined') {
    window.CortexSidebar = {
      initializeSidebar: initializeSidebar,
      setActiveSection: setActiveSection,
      toggleSidebarCollapse: toggleSidebarCollapse,
    };
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
      initializeSidebar: initializeSidebar,
      setActiveSection: setActiveSection,
      toggleSidebarCollapse: toggleSidebarCollapse,
    };
  }
})();
