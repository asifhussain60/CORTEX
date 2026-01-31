// Mobile Logo Scroll Animation
(function() {
    // Only run on mobile devices (≤768px)
    if (window.innerWidth > 768) return;
    
    const logo = document.querySelector('.hero-logo');
    if (!logo) return;
    
    // Start with expanded logo on mobile
    logo.classList.add('logo-expanded');
    
    let ticking = false;
    const scrollThreshold = 100; // px scrolled before shrinking
    
    function updateLogoSize() {
        const scrollY = window.scrollY || window.pageYOffset;
        
        if (scrollY < scrollThreshold) {
            // At top - expand logo
            logo.classList.add('logo-expanded');
        } else {
            // Scrolled down - shrink logo
            logo.classList.remove('logo-expanded');
        }
        
        ticking = false;
    }
    
    function requestTick() {
        if (!ticking) {
            window.requestAnimationFrame(updateLogoSize);
            ticking = true;
        }
    }
    
    // Listen to scroll events
    window.addEventListener('scroll', requestTick, { passive: true });
    
    // Handle window resize (if user rotates device)
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            logo.classList.remove('logo-expanded');
        } else {
            updateLogoSize();
        }
    });
    
    // Initial check
    updateLogoSize();
})();

// Demo Videos Tab Navigation
(function() {
    const tabs = document.querySelectorAll('.demo-tab-v');
    const panels = document.querySelectorAll('.demo-tab-panel');
    const infoContents = document.querySelectorAll('.demo-info-content');
    
    if (!tabs.length || !panels.length) return;
    
    function switchTab(targetTab) {
        const target = targetTab.getAttribute('data-tab');
        
        // Update tab states
        tabs.forEach(tab => {
            const isActive = tab === targetTab;
            tab.classList.toggle('active', isActive);
            tab.setAttribute('aria-selected', isActive);
        });
        
        // Update panel visibility with animation
        panels.forEach(panel => {
            const isActive = panel.id === `tab-${target}`;
            if (isActive) {
                panel.classList.add('active');
                // Pause video when switching to new tab
                const video = panel.querySelector('video');
                if (video) video.pause();
            } else {
                panel.classList.remove('active');
                // Pause videos in inactive panels
                const video = panel.querySelector('video');
                if (video) video.pause();
            }
        });
        
        // Update info panel content
        infoContents.forEach(info => {
            const isTarget = info.getAttribute('data-for') === target;
            info.classList.toggle('hidden', !isTarget);
        });
        
        // Reset play button visibility
        const activePanel = document.querySelector('.demo-tab-panel.active');
        if (activePanel) {
            const playBtn = activePanel.querySelector('.video-play-btn');
            if (playBtn) playBtn.classList.remove('hidden');
        }
    }
    
    // Click handler for tabs
    tabs.forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab));
    });
    
    // Keyboard navigation (A11y)
    tabs.forEach((tab, index) => {
        tab.addEventListener('keydown', (e) => {
            let targetIndex;
            
            if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
                e.preventDefault();
                targetIndex = (index + 1) % tabs.length;
            } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
                e.preventDefault();
                targetIndex = (index - 1 + tabs.length) % tabs.length;
            } else if (e.key === 'Home') {
                e.preventDefault();
                targetIndex = 0;
            } else if (e.key === 'End') {
                e.preventDefault();
                targetIndex = tabs.length - 1;
            }
            
            if (targetIndex !== undefined) {
                tabs[targetIndex].focus();
                switchTab(tabs[targetIndex]);
            }
        });
    });
    
    // Touch swipe support for mobile
    let touchStartX = 0;
    let touchEndX = 0;
    const videoArea = document.querySelector('.demo-video-area');
    
    if (videoArea) {
        videoArea.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });
        
        videoArea.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        }, { passive: true });
        
        function handleSwipe() {
            const swipeThreshold = 50;
            const diff = touchStartX - touchEndX;
            
            if (Math.abs(diff) < swipeThreshold) return;
            
            const currentIndex = Array.from(tabs).findIndex(tab => tab.classList.contains('active'));
            let targetIndex;
            
            if (diff > 0) {
                // Swipe left - next tab
                targetIndex = Math.min(currentIndex + 1, tabs.length - 1);
            } else {
                // Swipe right - previous tab
                targetIndex = Math.max(currentIndex - 1, 0);
            }
            
            if (targetIndex !== currentIndex) {
                switchTab(tabs[targetIndex]);
            }
        }
    }
    
    // Custom Play Button functionality
    document.querySelectorAll('.video-play-btn').forEach(btn => {
        const wrapper = btn.closest('.demo-video-wrapper');
        const video = wrapper ? wrapper.querySelector('video') : null;
        
        if (!video) return;
        
        // Click play button to start video
        btn.addEventListener('click', () => {
            video.play();
            btn.classList.add('hidden');
        });
        
        // Show play button when video is paused
        video.addEventListener('pause', () => {
            btn.classList.remove('hidden');
        });
        
        // Hide play button when video plays
        video.addEventListener('play', () => {
            btn.classList.add('hidden');
        });
        
        // Show play button when video ends
        video.addEventListener('ended', () => {
            btn.classList.remove('hidden');
        });
    });
})();

// Page Loading Overlay for Navigation
(function() {
    const overlay = document.getElementById('pageLoadingOverlay');
    const destinationText = document.getElementById('loadingDestination');
    
    if (!overlay || !destinationText) return;

    // Map of link href patterns to destination names
    const destinationNames = {
        'architecture': '🧠 Architecture',
        'security': '🛡️ Security',
        'orchestrators': '🎯 Orchestrators',
        'token-optimization': '💰 Token Optimization',
        'sts': '🔧 Sharpen The Saw',
        'knowledge': '📚 Best Practices',
        'lens': '🔍 CORTEX Lens',
        'getting-started': '🚀 Getting Started',
        'features': '✨ Features',
        'governance': '🛡️ SKULL Rules',
        'technical': '📚 Technical Docs',
        'faq': '❓ FAQ',
        'sitemap': '🗺️ Site Map',
        'story': '📖 The Awakening'
    };

    // Get friendly destination name from URL
    function getDestinationName(href) {
        for (const [key, name] of Object.entries(destinationNames)) {
            if (href.includes(key)) {
                return name;
            }
        }
        return 'CORTEX';
    }

    // Show loading overlay
    function showLoading(destinationName) {
        destinationText.textContent = destinationName;
        overlay.classList.add('active');
    }

    // Hide loading overlay (on page unload/navigation complete)
    function hideLoading() {
        overlay.classList.remove('active');
    }

    // Force hide overlay immediately on page load
    hideLoading();

    // Attach click handlers to navigation links
    // Target: btn-hero links (feature tiles) and glass-card links
    const navigationLinks = document.querySelectorAll(
        '.btn-hero[href], .glass-card.card-link[href], .btn-hero-story[href]'
    );

    navigationLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            // Skip if it's an anchor link, external link, or same page
            if (!href || href.startsWith('#') || href.startsWith('http') || href.startsWith('mailto:')) {
                return;
            }

            // Show loading overlay with destination name
            const destinationName = getDestinationName(href);
            showLoading(destinationName);
            
            // Note: Navigation will proceed naturally
            // The overlay provides visual feedback during the load time
        });
    });

    // Hide overlay when returning to page via back button
    window.addEventListener('pageshow', function(e) {
        if (e.persisted) {
            hideLoading();
        }
    });

    // Also hide on focus (for browser caching scenarios)
    window.addEventListener('focus', function() {
        setTimeout(hideLoading, 100);
    });

    // Prevent flash on initial page load
    document.addEventListener('DOMContentLoaded', function() {
        hideLoading();
        initStatsCounter();
    });
    
    // Stats Counter Animation
    function initStatsCounter() {
        const stats = document.querySelectorAll('.bwc-stat');
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const valueElement = entry.target.querySelector('.bwc-stat-value');
                    const targetValue = parseInt(valueElement.getAttribute('data-value'));
                    const isPercentage = valueElement.textContent.includes('%');
                    const hasPlus = valueElement.textContent.includes('+');
                    
                    if (targetValue > 0) {
                        animateValue(valueElement, 0, targetValue, 2000, isPercentage, hasPlus);
                    }
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        stats.forEach(stat => observer.observe(stat));
    }
    
    function animateValue(element, start, end, duration, isPercentage, hasPlus) {
        const startTime = performance.now();
        const range = end - start;
        
        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const current = Math.floor(start + range * easeOut);
            
            let displayValue = current;
            if (hasPlus) displayValue += '+';
            if (isPercentage) displayValue += '%';
            
            element.textContent = displayValue;
            
            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                let finalValue = end;
                if (hasPlus) finalValue += '+';
                if (isPercentage) finalValue += '%';
                element.textContent = finalValue;
            }
        }
        
        requestAnimationFrame(update);
    }
})();

// Generic Tabs for Cortex Panels (Security, Orchestrators, Governance & Audit)
(function() {
    const groups = document.querySelectorAll('.cortex-tabs');
    if (!groups.length) return;

    groups.forEach(group => {
        const tabs = group.querySelectorAll('.cortex-tab');
        const container = group.parentElement; // parent holds panels
        const panels = container.querySelectorAll('.cortex-tab-panel');

        function activate(targetId, clickedTab) {
            tabs.forEach(t => {
                const isActive = t === clickedTab;
                t.classList.toggle('active', isActive);
                t.setAttribute('aria-selected', isActive);
            });
            panels.forEach(p => {
                const isActive = p.id === targetId;
                p.classList.toggle('active', isActive);
                p.hidden = !isActive;
            });
        }

        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const target = tab.getAttribute('data-target');
                if (target) activate(target, tab);
            });
            // Keyboard support
            tab.addEventListener('keydown', (e) => {
                let idx = Array.from(tabs).indexOf(tab);
                let nextIdx = idx;
                if (e.key === 'ArrowRight') nextIdx = Math.min(idx + 1, tabs.length - 1);
                if (e.key === 'ArrowLeft') nextIdx = Math.max(idx - 1, 0);
                if (e.key === 'Home') nextIdx = 0;
                if (e.key === 'End') nextIdx = tabs.length - 1;
                if (nextIdx !== idx) {
                    e.preventDefault();
                    const nextTab = tabs[nextIdx];
                    nextTab.focus();
                    const target = nextTab.getAttribute('data-target');
                    if (target) activate(target, nextTab);
                }
            });
        });

        // Initialize: hide non-active panels
        panels.forEach(p => {
            if (!p.classList.contains('active')) p.hidden = true;
        });
    });
})();
