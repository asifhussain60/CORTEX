/**
 * STORY PAGE JAVASCRIPT
 * Handles reading progress, chapter navigation, and interactive elements
 */

(function() {
    'use strict';

    // Reading Progress Bar
    function updateReadingProgress() {
        const progressBar = document.getElementById('progressBar');
        if (!progressBar) return;

        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight - windowHeight;
        const scrolled = window.scrollY;
        const progress = (scrolled / documentHeight) * 100;

        progressBar.style.width = progress + '%';
    }

    // Chapter Navigation - Active Link Highlighting
    function updateActiveChapter() {
        const chapters = document.querySelectorAll('.story-chapter');
        const tocLinks = document.querySelectorAll('.toc-link');
        
        let activeChapter = null;
        const scrollPosition = window.scrollY + 150; // Offset for fixed header

        chapters.forEach(chapter => {
            const top = chapter.offsetTop;
            const bottom = top + chapter.offsetHeight;

            if (scrollPosition >= top && scrollPosition < bottom) {
                activeChapter = chapter.id;
            }
        });

        tocLinks.forEach(link => {
            link.classList.remove('active');
            const href = link.getAttribute('href');
            if (href && href.substring(1) === activeChapter) {
                link.classList.add('active');
            }
        });
    }

    // Smooth Scroll for TOC Links
    function setupSmoothScroll() {
        const tocLinks = document.querySelectorAll('.toc-link');
        
        tocLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const targetId = this.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    const offsetTop = targetElement.offsetTop - 100; // Account for fixed header
                    window.scrollTo({
                        top: offsetTop,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }

    // Back to Top Button
    function setupBackToTop() {
        const backToTopBtn = document.getElementById('backToTop');
        if (!backToTopBtn) return;

        window.addEventListener('scroll', function() {
            if (window.scrollY > 500) {
                backToTopBtn.classList.add('visible');
            } else {
                backToTopBtn.classList.remove('visible');
            }
        });

        backToTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // Scroll Event Listener (throttled for performance)
    let scrollTimeout;
    function handleScroll() {
        if (scrollTimeout) {
            window.cancelAnimationFrame(scrollTimeout);
        }
        
        scrollTimeout = window.requestAnimationFrame(function() {
            updateReadingProgress();
            updateActiveChapter();
        });
    }

    // Image Error Handling - Show placeholder on error
    function setupImageErrorHandling() {
        const images = document.querySelectorAll('.story-image-comic img, .chapter-image-comic img');
        
        images.forEach(img => {
            // If image hasn't loaded yet
            if (!img.complete) {
                img.addEventListener('load', function() {
                    console.log('Image loaded successfully:', this.src);
                });
            }
            
            // Already handled by onerror attribute, but add console logging
            img.addEventListener('error', function() {
                console.warn('Image failed to load, using placeholder:', this.src);
            });
        });
    }

    // Coffee Mug Counter Animation (optional enhancement)
    function animateCoffeeMugs() {
        const mugCount = document.getElementById('mugCount');
        if (!mugCount) return;

        // Add subtle pulsing animation on scroll
        let lastScrollY = window.scrollY;
        window.addEventListener('scroll', function() {
            const currentScrollY = window.scrollY;
            if (Math.abs(currentScrollY - lastScrollY) > 100) {
                mugCount.style.animation = 'pulse 0.5s ease-out';
                setTimeout(() => {
                    mugCount.style.animation = '';
                }, 500);
                lastScrollY = currentScrollY;
            }
        });
    }

    // Initialize Intersection Observer for Scroll Animations
    function setupScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -100px 0px'
        };

        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, observerOptions);

        // Animate chapters as they come into view
        const chapters = document.querySelectorAll('.story-chapter');
        chapters.forEach(chapter => {
            chapter.style.opacity = '0';
            chapter.style.transform = 'translateY(30px)';
            chapter.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
            observer.observe(chapter);
        });
    }

    // Print Functionality
    function setupPrintButton() {
        // Check if print button exists in navigation
        const printBtn = document.querySelector('.print-story-btn');
        if (printBtn) {
            printBtn.addEventListener('click', function(e) {
                e.preventDefault();
                window.print();
            });
        }
    }

    // Social Sharing (if implemented in future)
    function setupSocialSharing() {
        const shareButtons = document.querySelectorAll('.share-btn');
        
        shareButtons.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const platform = this.dataset.platform;
                const url = encodeURIComponent(window.location.href);
                const title = encodeURIComponent(document.title);
                
                let shareUrl = '';
                switch(platform) {
                    case 'twitter':
                        shareUrl = `https://twitter.com/intent/tweet?url=${url}&text=${title}`;
                        break;
                    case 'linkedin':
                        shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${url}`;
                        break;
                    case 'reddit':
                        shareUrl = `https://reddit.com/submit?url=${url}&title=${title}`;
                        break;
                }
                
                if (shareUrl) {
                    window.open(shareUrl, '_blank', 'width=600,height=400');
                }
            });
        });
    }

    // Initialize all features
    function init() {
        setupSmoothScroll();
        setupBackToTop();
        setupImageErrorHandling();
        setupScrollAnimations();
        animateCoffeeMugs();
        setupPrintButton();
        setupSocialSharing();
        setupChapterNavigation();
        
        // Initial updates
        updateReadingProgress();
        updateActiveChapter();
        
        // Attach scroll listener
        window.addEventListener('scroll', handleScroll);
        
        // Log initialization
        console.log('Story page initialized successfully');
        console.log('Image placeholders will show until real images are uploaded to illustrations/images/');
    }

    // Chapter Navigation Buttons
    function setupChapterNavigation() {
        const chapters = [
            { id: 'prologue', title: 'Prologue: The Basement Laboratory' },
            { id: 'chapter1', title: 'Chapter 1: The Goldfish Theory' },
            { id: 'chapter2', title: 'Chapter 2: The Brain Protector' },
            { id: 'chapter3', title: 'Chapter 3: The SQLite Intervention' },
            { id: 'chapter4', title: 'Chapter 4: The Agent Uprising' },
            { id: 'chapter5', title: 'Chapter 5: The Knowledge Graph Incident' },
            { id: 'chapter6', title: 'Chapter 6: The Token Crisis' },
            { id: 'chapter7', title: 'Chapter 7: The Hebb\'s Law Revelation' },
            { id: 'chapter8', title: 'Chapter 8: The Response Template Evolution' },
            { id: 'chapter9', title: 'Chapter 9: The Cross-Platform Challenge' },
            { id: 'chapter10', title: 'Chapter 10: The Awakening' },
            { id: 'chapter11', title: 'Chapter 11: The 3.0 Revolution' },
            { id: 'epilogue', title: 'Epilogue: Six Months Later' }
        ];

        chapters.forEach((chapter, index) => {
            const chapterElement = document.getElementById(chapter.id);
            if (!chapterElement) return;

            // Create navigation container
            const navContainer = document.createElement('div');
            navContainer.className = 'chapter-navigation';

            // Previous button (if not first chapter)
            if (index > 0) {
                const prevChapter = chapters[index - 1];
                const prevBtn = document.createElement('a');
                prevBtn.href = `#${prevChapter.id}`;
                prevBtn.className = 'chapter-nav-btn prev';
                prevBtn.innerHTML = `
                    <div class="nav-label">
                        <span class="nav-direction">Previous</span>
                        <span class="nav-title">${prevChapter.title}</span>
                    </div>
                `;
                navContainer.appendChild(prevBtn);
            } else {
                // Add spacer if no previous button
                const spacer = document.createElement('div');
                spacer.className = 'spacer';
                navContainer.appendChild(spacer);
            }

            // Next button (if not last chapter)
            if (index < chapters.length - 1) {
                const nextChapter = chapters[index + 1];
                const nextBtn = document.createElement('a');
                nextBtn.href = `#${nextChapter.id}`;
                nextBtn.className = 'chapter-nav-btn next';
                nextBtn.innerHTML = `
                    <div class="nav-label">
                        <span class="nav-direction">Next</span>
                        <span class="nav-title">${nextChapter.title}</span>
                    </div>
                `;
                navContainer.appendChild(nextBtn);
            }

            // Append navigation to end of chapter
            chapterElement.appendChild(navContainer);
        });

        // Add smooth scroll behavior to new buttons
        document.querySelectorAll('.chapter-nav-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const targetId = this.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    const offsetTop = targetElement.offsetTop - 100;
                    window.scrollTo({
                        top: offsetTop,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }

    // Run initialization when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();

// Add CSS animation for coffee mug pulse
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
`;
document.head.appendChild(style);
