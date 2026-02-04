/**
 * DO-001-04: Responsive Navigation (Hamburger Menu)
 * 
 * Handles mobile navigation menu toggle with hamburger icon animation.
 * 
 * Features:
 * - Hamburger menu toggle for mobile/tablet (< 1024px)
 * - Smooth slide-in navigation panel
 * - Overlay background with click-to-close
 * - Keyboard accessible (Escape to close)
 * - Body scroll lock when menu is open
 * 
 * AC-ID: DO-001-04
 * Phase: PHASE-15-DASHBOARD-ENHANCEMENT
 * 
 * @module hamburger-menu
 */

/**
 * Initialize hamburger menu component with event listeners.
 * 
 * @returns {void}
 */
function initializeHamburgerMenu() {
  const hamburger = document.getElementById('hamburger-menu');
  const navMobile = document.getElementById('nav-mobile');
  const navOverlay = document.getElementById('nav-mobile-overlay');
  
  if (!hamburger || !navMobile || !navOverlay) {
    console.warn('ΓÜá∩╕Å Hamburger menu elements not found in DOM');
    return;
  }
  
  /**
   * Toggle mobile navigation menu open/closed.
   * 
   * @returns {void}
   */
  function toggleMenu() {
    const isActive = hamburger.classList.contains('active');
    
    if (isActive) {
      closeMenu();
    } else {
      openMenu();
    }
  }
  
  /**
   * Open mobile navigation menu.
   * 
   * @returns {void}
   */
  function openMenu() {
    hamburger.classList.add('active');
    navMobile.classList.add('active');
    navOverlay.classList.add('active');
    document.body.style.overflow = 'hidden'; // Lock body scroll
    
    console.log('≡ƒìö Mobile menu opened');
  }
  
  /**
   * Close mobile navigation menu.
   * 
   * @returns {void}
   */
  function closeMenu() {
    hamburger.classList.remove('active');
    navMobile.classList.remove('active');
    navOverlay.classList.remove('active');
    document.body.style.overflow = ''; // Restore body scroll
    
    console.log('≡ƒìö Mobile menu closed');
  }
  
  // Click handler for hamburger button
  hamburger.addEventListener('click', (e) => {
    e.stopPropagation();
    toggleMenu();
  });
  
  // Click handler for overlay (close menu)
  navOverlay.addEventListener('click', closeMenu);
  
  // Keyboard handler (Escape key)
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && hamburger.classList.contains('active')) {
      closeMenu();
    }
  });
  
  // Close menu on navigation link click
  const navLinks = navMobile.querySelectorAll('a, button');
  navLinks.forEach(link => {
    link.addEventListener('click', closeMenu);
  });
  
  // Close menu when window resizes to desktop
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      if (window.innerWidth >= 1024 && hamburger.classList.contains('active')) {
        closeMenu();
      }
    }, 250);
  });
  
  console.log('Γ£à Hamburger menu initialized (DO-001-04)');
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeHamburgerMenu);
} else {
  initializeHamburgerMenu();
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { initializeHamburgerMenu };
}
