// ============================================
// RA-Domain Analysis - Main JavaScript
// Interactive Features for Business Presentation
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
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

    // Content sections are now visible immediately (no scroll animations)
    // All content loads fully on page load

    // Collapsible panels functionality
    const collapsibleHeaders = document.querySelectorAll('.collapsible-header');
    collapsibleHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const panel = this.parentElement;
            const wasActive = panel.classList.contains('active');
            
            // Optional: Close other panels in the same section (accordion mode)
            // Uncomment the next 3 lines for accordion behavior
            // const section = panel.closest('.content-section');
            // section.querySelectorAll('.collapsible-panel.active').forEach(p => p.classList.remove('active'));
            
            // Toggle current panel
            if (wasActive) {
                panel.classList.remove('active');
            } else {
                panel.classList.add('active');
            }
        });
    });

    // Add tooltips for badges
    const badges = document.querySelectorAll('.badge');
    badges.forEach(badge => {
        badge.title = badge.textContent;
    });

    // Copy code blocks on click (for technical pages)
    const codeBlocks = document.querySelectorAll('pre code');
    codeBlocks.forEach(block => {
        block.style.cursor = 'pointer';
        block.title = 'Click to copy';
        block.addEventListener('click', function() {
            const text = this.textContent;
            navigator.clipboard.writeText(text).then(() => {
                const originalTitle = this.title;
                this.title = 'Copied!';
                setTimeout(() => {
                    this.title = originalTitle;
                }, 2000);
            });
        });
    });

    // Mobile menu toggle
    const navToggle = document.createElement('button');
    navToggle.className = 'nav-toggle';
    navToggle.innerHTML = '<i class="fas fa-bars"></i>';
    navToggle.style.display = 'none';

    const navbar = document.querySelector('.navbar .container');
    if (navbar) {
        navbar.appendChild(navToggle);
    }

    navToggle.addEventListener('click', function() {
        const navMenu = document.querySelector('.nav-menu');
        if (navMenu) {
            navMenu.classList.toggle('active');
        }
    });

    // Show mobile toggle on small screens
    function checkScreenSize() {
        if (window.innerWidth <= 768) {
            navToggle.style.display = 'block';
        } else {
            navToggle.style.display = 'none';
            const navMenu = document.querySelector('.nav-menu');
            if (navMenu) {
                navMenu.classList.remove('active');
            }
        }
    }

    window.addEventListener('resize', checkScreenSize);
    checkScreenSize();

    // Add search functionality (if search box exists)
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const sections = document.querySelectorAll('.content-section');

            sections.forEach(section => {
                const text = section.textContent.toLowerCase();
                if (text.includes(searchTerm) || searchTerm === '') {
                    section.style.display = 'block';
                } else {
                    section.style.display = 'none';
                }
            });
        });
    }

    // Print functionality
    const printButtons = document.querySelectorAll('.btn-print');
    printButtons.forEach(button => {
        button.addEventListener('click', function() {
            window.print();
        });
    });

    // Export to PDF functionality (placeholder)
    const exportButtons = document.querySelectorAll('.btn-export-pdf');
    exportButtons.forEach(button => {
        button.addEventListener('click', function() {
            alert('PDF export would require a server-side solution or browser print dialog. Use File > Print > Save as PDF');
        });
    });

    console.log('RA-Domain Analysis site loaded successfully');
});

// Utility functions
function formatNumber(num) {
    return num.toLocaleString();
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Export utilities for use in other pages
window.RADomain = {
    formatNumber,
    formatCurrency,
    formatDate
};
