/**
 * CORTEX Dashboard — Hamburger Menu Component
 * Mobile navigation menu with accessibility support
 *
 * Features:
 *  - Toggle open/close on button click
 *  - Body scroll lock when menu is open
 *  - Escape key to close
 *  - Auto-close on resize to desktop (>= 1024px)
 *  - Trap focus inside open menu for keyboard navigation
 */

(function () {
  'use strict';

  /* -------------------------------------------------------------------------
     State
     ------------------------------------------------------------------------- */
  let menuOpen = false;

  /* -------------------------------------------------------------------------
     Selectors / Configuration
     ------------------------------------------------------------------------- */
  const DESKTOP_BREAKPOINT = 1024;
  const MENU_OPEN_CLASS = 'menu-open';

  /* -------------------------------------------------------------------------
     toggleMenu — opens or closes the mobile navigation
     ------------------------------------------------------------------------- */
  function toggleMenu() {
    menuOpen = !menuOpen;

    const nav = document.querySelector('.nav-mobile');
    const button = document.querySelector('.hamburger-menu');

    if (menuOpen) {
      // Open: lock scroll and mark state
      document.body.style.overflow = 'hidden';
      document.body.classList.add(MENU_OPEN_CLASS);
      if (nav) {
        nav.classList.add(MENU_OPEN_CLASS);
        nav.setAttribute('aria-hidden', 'false');
      }
      if (button) {
        button.setAttribute('aria-expanded', 'true');
        button.setAttribute('aria-label', 'Close navigation menu');
      }
    } else {
      closeMenu();
    }
  }

  /* -------------------------------------------------------------------------
     closeMenu — force-closes the menu and restores scroll
     ------------------------------------------------------------------------- */
  function closeMenu() {
    menuOpen = false;

    const nav = document.querySelector('.nav-mobile');
    const button = document.querySelector('.hamburger-menu');

    document.body.style.overflow = '';
    document.body.classList.remove(MENU_OPEN_CLASS);

    if (nav) {
      nav.classList.remove(MENU_OPEN_CLASS);
      nav.setAttribute('aria-hidden', 'true');
    }
    if (button) {
      button.setAttribute('aria-expanded', 'false');
      button.setAttribute('aria-label', 'Open navigation menu');
    }
  }

  /* -------------------------------------------------------------------------
     handleKeyDown — Escape closes the menu
     ------------------------------------------------------------------------- */
  function handleKeyDown(event) {
    if (event.key === 'Escape' && menuOpen) {
      closeMenu();

      // Return focus to the hamburger button
      const button = document.querySelector('.hamburger-menu');
      if (button) {
        button.focus();
      }
    }
  }

  /* -------------------------------------------------------------------------
     handleResize — auto-close menu on resize to desktop width
     ------------------------------------------------------------------------- */
  function handleResize() {
    if (window.innerWidth >= 1024 && menuOpen) {
      closeMenu();
    }
  }

  /* -------------------------------------------------------------------------
     initializeHamburgerMenu — wire up all event listeners
     ------------------------------------------------------------------------- */
  function initializeHamburgerMenu() {
    const button = document.querySelector('.hamburger-menu');
    const nav = document.querySelector('.nav-mobile');

    if (!button) {
      // Hamburger button not present — desktop layout or not yet rendered
      return;
    }

    // Initial ARIA state
    button.setAttribute('aria-expanded', 'false');
    button.setAttribute('aria-label', 'Open navigation menu');
    button.setAttribute('aria-controls', 'nav-mobile');

    if (nav) {
      nav.setAttribute('aria-hidden', 'true');
      nav.setAttribute('id', 'nav-mobile');
    }

    // Toggle on click
    button.addEventListener('click', toggleMenu);

    // Escape key handler (document level)
    document.addEventListener('keydown', handleKeyDown);

    // Auto-close on resize to desktop
    window.addEventListener('resize', handleResize);
  }

  /* -------------------------------------------------------------------------
     Auto-initialize when DOM is ready
     ------------------------------------------------------------------------- */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeHamburgerMenu);
  } else {
    initializeHamburgerMenu();
  }

  /* -------------------------------------------------------------------------
     Public API — expose for testing and external access
     ------------------------------------------------------------------------- */
  if (typeof window !== 'undefined') {
    window.CortexHamburger = {
      initializeHamburgerMenu: initializeHamburgerMenu,
      toggleMenu: toggleMenu,
      closeMenu: closeMenu,
    };
  }

  /* -------------------------------------------------------------------------
     Module export for Node/Jest environments
     ------------------------------------------------------------------------- */
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
      initializeHamburgerMenu: initializeHamburgerMenu,
      toggleMenu: toggleMenu,
      closeMenu: closeMenu,
    };
  }
})();
