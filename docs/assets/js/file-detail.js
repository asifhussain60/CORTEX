// CORTEX File Detail Page JavaScript
// Author: Asif Hussain
// Version: 1.0.0

// Smooth scroll for TOC links
document.querySelectorAll('.toc-link').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const targetId = link.getAttribute('href').substring(1);
        const target = document.getElementById(targetId);
        
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
            
            // Update active TOC link
            document.querySelectorAll('.toc-link').forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        }
    });
});

// Intersection Observer for TOC highlighting
const observerOptions = {
    root: null,
    rootMargin: '-100px 0px -80% 0px',
    threshold: 0
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const id = entry.target.getAttribute('id');
            document.querySelectorAll('.toc-link').forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${id}`) {
                    link.classList.add('active');
                }
            });
        }
    });
}, observerOptions);

// Observe all content sections
document.querySelectorAll('.content-section').forEach(section => {
    observer.observe(section);
});

// Copy code button functionality
document.querySelectorAll('pre code').forEach((block) => {
    const button = document.createElement('button');
    button.className = 'copy-code-btn';
    button.textContent = 'Copy';
    button.setAttribute('aria-label', 'Copy code to clipboard');
    
    const pre = block.parentElement;
    pre.style.position = 'relative';
    pre.appendChild(button);
    
    button.addEventListener('click', async () => {
        try {
            await navigator.clipboard.writeText(block.textContent);
            button.textContent = 'Copied!';
            button.classList.add('copied');
            
            setTimeout(() => {
                button.textContent = 'Copy';
                button.classList.remove('copied');
            }, 2000);
        } catch (err) {
            console.error('Failed to copy:', err);
            button.textContent = 'Failed';
        }
    });
});

// Expand/collapse code examples on mobile
const mediaQuery = window.matchMedia('(max-width: 768px)');

function handleMobileCodeBlocks(e) {
    if (e.matches) {
        document.querySelectorAll('.code-comparison-grid').forEach(grid => {
            const codeBlocks = grid.querySelectorAll('.code-example');
            codeBlocks.forEach((block, index) => {
                if (index > 0) {
                    block.style.maxHeight = '0';
                    block.style.overflow = 'hidden';
                    
                    const header = block.querySelector('h4');
                    header.style.cursor = 'pointer';
                    header.addEventListener('click', () => {
                        if (block.style.maxHeight === '0px') {
                            block.style.maxHeight = block.scrollHeight + 'px';
                        } else {
                            block.style.maxHeight = '0';
                        }
                    });
                }
            });
        });
    }
}

handleMobileCodeBlocks(mediaQuery);
mediaQuery.addListener(handleMobileCodeBlocks);

// Add focus visible class for keyboard navigation
document.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
        document.body.classList.add('keyboard-nav');
    }
});

document.addEventListener('mousedown', () => {
    document.body.classList.remove('keyboard-nav');
});

// Print friendly - expand all code blocks
window.addEventListener('beforeprint', () => {
    document.querySelectorAll('.code-example').forEach(block => {
        block.style.maxHeight = 'none';
    });
});
