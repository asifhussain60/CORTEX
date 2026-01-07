/**
 * CORTEX Lens - Unified Dashboard JavaScript
 * 
 * Features:
 * - Tab switching
 * - Theme toggle (dark/light)
 * - Scroll-responsive header animation
 * - Smooth animations
 * - Live reload friendly
 * 
 * Author: Asif Hussain
 * Version: 1.1.0
 */

// ========== Scroll Animation (Disabled - Fixed Sidebar) ==========
function initScrollAnimation() {
    // Fixed sidebar layout - no scroll animation needed
    return;
}

// ========== Tab System ==========
document.addEventListener('DOMContentLoaded', function() {
    const tabLinks = document.querySelectorAll('.tab-link');
    const tabContents = document.querySelectorAll('.tab-content');

    tabLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get target tab
            const targetTab = this.getAttribute('data-tab');
            
            // Remove active class from all tabs and contents
            tabLinks.forEach(l => l.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked tab and corresponding content
            this.classList.add('active');
            const targetContent = document.getElementById(targetTab);
            if (targetContent) {
                targetContent.classList.add('active');
                
                // Scroll main content to top
                const mainContent = document.querySelector('.main-content');
                if (mainContent) {
                    mainContent.scrollTop = 0;
                }
            }
            
            // Log for debugging
            console.log('🔄 Switched to tab:', targetTab);
        });
    });
});

// ========== Theme Toggle ==========
function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    html.setAttribute('data-theme', newTheme);
    
    // Update theme toggle icon
    const themeIcon = document.querySelector('.theme-icon');
    if (themeIcon) {
        themeIcon.textContent = newTheme === 'dark' ? '🌙' : '☀️';
    }
    
    // Save preference
    localStorage.setItem('cortex-theme', newTheme);
    
    console.log('🎨 Theme switched to:', newTheme);
}

// ========== Initialize Theme from Storage ==========
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('cortex-theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    const themeIcon = document.querySelector('.theme-icon');
    if (themeIcon) {
        themeIcon.textContent = savedTheme === 'dark' ? '🌙' : '☀️';
    }
});

// ========== Smooth Scroll ==========
document.addEventListener('DOMContentLoaded', function() {
    // Apply saved theme
    const savedTheme = localStorage.getItem('cortex-theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    // Initialize scroll animation
    initScrollAnimation();
    
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// ========== KPI Card Animations ==========
// Removed entrance animations - cards display immediately on load

// ========== Collapsible Use Case Tiles ==========
document.addEventListener('DOMContentLoaded', function() {
    const tiles = document.querySelectorAll('.use-case-tile');
    
    tiles.forEach(tile => {
        const header = tile.querySelector('.tile-header');
        
        header.addEventListener('click', function() {
            // Close all other tiles
            tiles.forEach(otherTile => {
                if (otherTile !== tile && otherTile.classList.contains('expanded')) {
                    otherTile.classList.remove('expanded');
                }
            });
            
            // Toggle current tile
            tile.classList.toggle('expanded');
            
            // Log for debugging
            const category = tile.getAttribute('data-category');
            const isExpanded = tile.classList.contains('expanded');
            console.log(`${isExpanded ? '▼' : '▶'} Use case tile: ${category}`);
        });
    });
    
    console.log('🎯 Collapsible tiles initialized:', tiles.length);
});

// ========== Live Reload Detection ==========
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ CORTEX Lens Dashboard Loaded');
    console.log('🔄 Live reload ready - changes will auto-refresh');
    console.log('📍 Current tab:', document.querySelector('.tab-link.active')?.getAttribute('data-tab'));
});

// ========== Helper Functions ==========
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function getScoreClass(score) {
    if (score >= 80) return 'excellent';
    if (score >= 60) return 'good';
    if (score >= 40) return 'fair';
    return 'poor';
}

function getScoreColor(score) {
    if (score >= 80) return '#00ff88';
    if (score >= 60) return '#ffaa00';
    if (score >= 40) return '#ff8800';
    return '#ff4444';
}
