/**
 * DO-001-01: CORTEX Logo Component
 * 
 * Handles logo display, dark mode variants, responsive scaling, and interactivity.
 * 
 * Features:
 * - Responsive sizing (96px mobile → 128px tablet → 200px desktop)
 * - Dark mode auto-detection and variant switching
 * - Hover effects (scale 1.05x + cyan glow)
 * - Keyboard accessibility (Tab + Enter navigation)
 * - Tooltip display ("CORTEX v2.0")
 * 
 * AC-ID: DO-001-01
 * Phase: PHASE-15-DASHBOARD-ENHANCEMENT
 * 
 * @module header-logo
 */

/**
 * Initialize logo component with dark mode detection and interactivity.
 * 
 * This function sets up:
 * - Dark mode media query listener
 * - Logo variant switching based on theme
 * - Click handler for dashboard navigation
 * - Keyboard focus management
 * 
 * @returns {void}
 */
function initializeLogoComponent() {
  const logoImage = document.getElementById('logo-image');
  const logoLink = document.getElementById('cortex-logo');
  
  if (!logoImage || !logoLink) {
    console.warn('⚠️ Logo elements not found in DOM');
    return;
  }
  
  /**
   * Update logo source based on current theme (light/dark).
   * 
   * @param {boolean} isDark - Whether dark mode is active
   * @returns {void}
   */
  function updateLogoVariant(isDark) {
    const logoPath = isDark 
      ? '/assets/cortex-logo-white.svg' 
      : '/assets/cortex-logo.svg';
    
    logoImage.src = logoPath;
    console.log(`🎨 Logo variant updated: ${isDark ? 'dark' : 'light'} mode`);
  }
  
  // Detect initial theme preference
  const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
  updateLogoVariant(darkModeQuery.matches);
  
  // Listen for theme changes
  darkModeQuery.addEventListener('change', (e) => {
    updateLogoVariant(e.matches);
  });
  
  // Handle logo click navigation
  logoLink.addEventListener('click', (e) => {
    e.preventDefault();
    console.log('🏠 Navigating to dashboard home');
    
    // Smooth navigation to home (reload page for now)
    window.location.href = '/';
  });
  
  // Handle keyboard navigation (Enter key)
  logoLink.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      logoLink.click();
    }
  });
  
  // Add visual feedback on interaction
  logoLink.addEventListener('mouseenter', () => {
    logoImage.style.transform = 'scale(1.05)';
  });
  
  logoLink.addEventListener('mouseleave', () => {
    logoImage.style.transform = 'scale(1)';
  });
  
  console.log('✅ Logo component initialized (DO-001-01)');
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeLogoComponent);
} else {
  initializeLogoComponent();
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { initializeLogoComponent };
}
