/**
 * CORTEX Dashboard - Hamburger Menu Component
 *
 * Controls mobile navigation menu toggle with scroll lock,
 * Escape key handler, and auto-close on desktop resize.
 *
 * Authority: DO-001-04 Responsive Design Validation
 */

'use strict';

/** @type {boolean} Current open state of the hamburger menu */
var _menuOpen = false;

/**
 * Initialize the hamburger menu component.
 * Attaches click, keyboard, resize, and overlay event listeners.
 *
 * @returns {void}
 */
function initializeHamburgerMenu() {
  var hamburgerBtn = document.getElementById('hamburger-menu') ||
    document.querySelector('.hamburger-menu');
  var mobileNav = document.getElementById('nav-mobile') ||
    document.querySelector('.nav-mobile');
  var overlay = document.getElementById('nav-mobile-overlay') ||
    document.querySelector('.nav-mobile-overlay');

  if (!hamburgerBtn) return;

  // Click handler
  hamburgerBtn.addEventListener('click', function () {
    toggleMenu();
  });

  // Overlay click — close menu
  if (overlay) {
    overlay.addEventListener('click', function () {
      closeMenu();
    });
  }

  // Escape key — close menu
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' || event.keyCode === 27) {
      if (_menuOpen) {
        closeMenu();
      }
    }
  });

  // Auto-close on resize to desktop
  window.addEventListener('resize', function () {
    if (window.innerWidth >= 1024 && _menuOpen) {
      closeMenu();
    }
  });

  /**
   * Open the mobile menu.
   *
   * @returns {void}
   */
  function openMenu() {
    _menuOpen = true;
    hamburgerBtn.classList.add('open');
    hamburgerBtn.setAttribute('aria-expanded', 'true');

    if (mobileNav) {
      mobileNav.classList.add('open');
      mobileNav.setAttribute('aria-hidden', 'false');
    }

    if (overlay) {
      overlay.classList.add('open');
    }

    // Lock body scroll
    document.body.style.overflow = 'hidden';
  }

  /**
   * Close the mobile menu.
   *
   * @returns {void}
   */
  function closeMenu() {
    _menuOpen = false;
    hamburgerBtn.classList.remove('open');
    hamburgerBtn.setAttribute('aria-expanded', 'false');

    if (mobileNav) {
      mobileNav.classList.remove('open');
      mobileNav.setAttribute('aria-hidden', 'true');
    }

    if (overlay) {
      overlay.classList.remove('open');
    }

    // Restore body scroll
    document.body.style.overflow = '';
  }

  /**
   * Toggle the mobile menu open/closed state.
   *
   * @returns {void}
   */
  function toggleMenu() {
    if (_menuOpen) {
      closeMenu();
    } else {
      openMenu();
    }
  }

  // Expose toggle for external callers
  hamburgerBtn._toggleMenu = toggleMenu;
  hamburgerBtn._closeMenu = closeMenu;
  hamburgerBtn._openMenu = openMenu;
}

/**
 * Toggle the hamburger menu from an external caller.
 *
 * @returns {void}
 */
function toggleMenu() {
  var btn = document.getElementById('hamburger-menu') ||
    document.querySelector('.hamburger-menu');
  if (btn && typeof btn._toggleMenu === 'function') {
    btn._toggleMenu();
  }
}

// Auto-initialize on DOMContentLoaded
if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      initializeHamburgerMenu();
    });
  } else {
    initializeHamburgerMenu();
  }
}

// Export for module environments
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    initializeHamburgerMenu: initializeHamburgerMenu,
    toggleMenu: toggleMenu,
  };
}
