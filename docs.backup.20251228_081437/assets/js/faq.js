// FAQ Page JavaScript - Accordion & Search

document.addEventListener('DOMContentLoaded', function() {
    initializeAccordion();
    initializeSearch();
    initializeDeepLinking();
});

// Accordion Functionality
function initializeAccordion() {
    const questions = document.querySelectorAll('.faq-question');
    
    questions.forEach(question => {
        question.addEventListener('click', function() {
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            
            // Close all other items (optional - remove for multi-open)
            // questions.forEach(q => q.setAttribute('aria-expanded', 'false'));
            
            // Toggle this item
            this.setAttribute('aria-expanded', !isExpanded);
        });
    });
}

// Search Functionality
function initializeSearch() {
    const searchInput = document.getElementById('faqSearch');
    const searchCount = document.getElementById('searchCount');
    const faqItems = document.querySelectorAll('.faq-item');
    
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase().trim();
        let visibleCount = 0;
        
        if (searchTerm === '') {
            // Show all items when search is cleared
            faqItems.forEach(item => {
                item.classList.remove('hidden');
                visibleCount++;
            });
            searchCount.textContent = '';
        } else {
            // Filter items based on search
            faqItems.forEach(item => {
                const question = item.querySelector('.question-text').textContent.toLowerCase();
                const answer = item.querySelector('.faq-answer').textContent.toLowerCase();
                
                if (question.includes(searchTerm) || answer.includes(searchTerm)) {
                    item.classList.remove('hidden');
                    visibleCount++;
                    
                    // Auto-expand matching items
                    const questionBtn = item.querySelector('.faq-question');
                    questionBtn.setAttribute('aria-expanded', 'true');
                } else {
                    item.classList.add('hidden');
                }
            });
            
            searchCount.textContent = `${visibleCount} result${visibleCount !== 1 ? 's' : ''}`;
        }
    });
}

// Deep Linking - Open specific question from URL hash
function initializeDeepLinking() {
    const hash = window.location.hash;
    
    if (hash) {
        const targetCategory = document.querySelector(hash);
        if (targetCategory) {
            // Scroll to category
            targetCategory.scrollIntoView({ behavior: 'smooth', block: 'start' });
            
            // Expand first item in category
            const firstQuestion = targetCategory.querySelector('.faq-question');
            if (firstQuestion) {
                firstQuestion.setAttribute('aria-expanded', 'true');
            }
        }
    }
}

// Keyboard Navigation
document.addEventListener('keydown', function(e) {
    if (e.target.classList.contains('faq-question')) {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            e.target.click();
        }
    }
});

// Analytics (optional) - Track which questions are most opened
function trackQuestionOpen(questionText) {
    // Implement analytics tracking here
    console.log('Question opened:', questionText);
}

// Add tracking to questions
document.querySelectorAll('.faq-question').forEach(question => {
    question.addEventListener('click', function() {
        const questionText = this.querySelector('.question-text').textContent;
        trackQuestionOpen(questionText);
    });
});
