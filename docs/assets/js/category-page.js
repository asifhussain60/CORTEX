// CORTEX Category Page JavaScript
// Author: Asif Hussain
// Version: 1.0.0

// Tab Switching with Keyboard Navigation
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        const tabId = button.getAttribute('aria-controls');
        const tabsContainer = button.closest('.tabs-container');
        
        // Deactivate all tabs
        tabsContainer.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
            btn.setAttribute('aria-selected', 'false');
        });
        
        tabsContainer.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
            content.hidden = true;
        });
        
        // Activate clicked tab
        button.classList.add('active');
        button.setAttribute('aria-selected', 'true');
        
        const targetContent = document.getElementById(tabId);
        targetContent.classList.add('active');
        targetContent.hidden = false;
        
        // Update URL hash
        window.history.replaceState(null, '', `#${button.dataset.tab}`);
    });
});

// Keyboard navigation for tabs (Arrow keys)
document.querySelectorAll('.tabs-nav').forEach(nav => {
    const tabs = Array.from(nav.querySelectorAll('.tab-button'));
    
    nav.addEventListener('keydown', (e) => {
        const currentIndex = tabs.indexOf(document.activeElement);
        
        if (e.key === 'ArrowRight') {
            e.preventDefault();
            const nextIndex = (currentIndex + 1) % tabs.length;
            tabs[nextIndex].focus();
            tabs[nextIndex].click();
        }
        
        if (e.key === 'ArrowLeft') {
            e.preventDefault();
            const prevIndex = (currentIndex - 1 + tabs.length) % tabs.length;
            tabs[prevIndex].focus();
            tabs[prevIndex].click();
        }
    });
});

// Load tab from URL hash on page load
window.addEventListener('load', () => {
    const hash = window.location.hash.slice(1);
    if (hash) {
        const button = document.querySelector(`[data-tab="${hash}"]`);
        if (button) button.click();
    }
});

// Accordion Toggle with ARIA
document.querySelectorAll('.accordion-header').forEach(header => {
    header.addEventListener('click', () => {
        const expanded = header.getAttribute('aria-expanded') === 'true';
        const contentId = header.getAttribute('aria-controls');
        const content = document.getElementById(contentId);
        
        header.setAttribute('aria-expanded', !expanded);
        
        if (expanded) {
            content.hidden = true;
        } else {
            content.hidden = false;
        }
    });
});

// Rule Card Expand/Collapse
function toggleRule(header) {
    const card = header.closest('.rule-card');
    const body = card.querySelector('.rule-body');
    const btn = header.querySelector('.expand-btn');
    
    const isExpanded = card.hasAttribute('data-expanded');
    
    if (isExpanded) {
        card.removeAttribute('data-expanded');
        body.hidden = true;
        btn.textContent = '+';
        btn.setAttribute('aria-label', 'Expand rule');
    } else {
        card.setAttribute('data-expanded', '');
        body.hidden = false;
        btn.textContent = '−';
        btn.setAttribute('aria-label', 'Collapse rule');
    }
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href !== '#' && href !== '#main-content') {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }
    });
});

// Add focus visible class for keyboard navigation
document.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
        document.body.classList.add('keyboard-nav');
    }
});

document.addEventListener('mousedown', () => {
    document.body.classList.remove('keyboard-nav');
});
