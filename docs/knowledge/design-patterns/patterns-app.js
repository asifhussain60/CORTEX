/**
 * CORTEX Design Patterns - Main Application
 * Handles search, filtering, and modal interactions
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 */

class PatternsApp {
    constructor() {
        this.patternMap = null;
        this.currentFilter = 'all';
        this.searchTerm = '';
        
        this.init();
    }
    
    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }
    
    setup() {
        // Initialize pattern map
        this.patternMap = new PatternMap('patternMap');
        
        // Set up event listeners
        this.setupSearch();
        this.setupTabs();
        this.setupMapControls();
        this.setupPatternChips();
        this.setupModal();
        
        // Listen for pattern detail events from map
        window.addEventListener('showPatternDetail', (e) => {
            this.showPatternModal(e.detail);
        });
    }
    
    setupSearch() {
        const searchInput = document.getElementById('pattern-search');
        if (!searchInput) return;
        
        searchInput.addEventListener('input', this.debounce((e) => {
            this.searchTerm = e.target.value.toLowerCase().trim();
            this.filterPatterns();
        }, 300));
    }
    
    setupTabs() {
        const tabs = document.querySelectorAll('.pattern-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                // Update active state
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                // Set filter
                this.currentFilter = tab.dataset.filter;
                this.filterPatterns();
            });
        });
    }
    
    setupMapControls() {
        const mapBtns = document.querySelectorAll('.map-btn[data-view]');
        mapBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                mapBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.patternMap.setView(btn.dataset.view);
            });
        });
        
        const resetBtn = document.getElementById('resetMapBtn');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                mapBtns.forEach(b => b.classList.remove('active'));
                document.querySelector('.map-btn[data-view="categories"]')?.classList.add('active');
                this.patternMap.reset();
            });
        }
    }
    
    setupPatternChips() {
        document.addEventListener('click', (e) => {
            const chip = e.target.closest('.pattern-chip');
            if (chip && chip.dataset.pattern) {
                this.showPatternModal(chip.dataset.pattern);
            }
        });
    }
    
    setupModal() {
        const modal = document.getElementById('pattern-modal');
        const closeBtn = modal?.querySelector('.modal-close');
        
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.hideModal());
        }
        
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideModal();
                }
            });
        }
        
        // ESC key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideModal();
            }
        });
    }
    
    filterPatterns() {
        const categoriesContainer = document.getElementById('categories-container');
        const noResults = document.getElementById('no-results');
        const categoryCards = document.querySelectorAll('.category-card');
        
        let hasVisibleCards = false;
        
        categoryCards.forEach(card => {
            const category = card.dataset.category;
            const chips = card.querySelectorAll('.pattern-chip');
            
            // Check category filter
            const categoryMatch = this.currentFilter === 'all' || category === this.currentFilter;
            
            if (!categoryMatch) {
                card.style.display = 'none';
                return;
            }
            
            // Check search filter on chips
            let hasVisibleChips = false;
            chips.forEach(chip => {
                const patternId = chip.dataset.pattern;
                const pattern = PATTERNS_DATA[patternId];
                
                if (!pattern) {
                    chip.style.display = 'none';
                    return;
                }
                
                const searchMatch = !this.searchTerm || 
                    pattern.name.toLowerCase().includes(this.searchTerm) ||
                    pattern.intent.toLowerCase().includes(this.searchTerm) ||
                    pattern.problem?.toLowerCase().includes(this.searchTerm) ||
                    (pattern.useCases && pattern.useCases.some(uc => uc.toLowerCase().includes(this.searchTerm)));
                
                if (searchMatch) {
                    chip.style.display = '';
                    hasVisibleChips = true;
                } else {
                    chip.style.display = 'none';
                }
            });
            
            // Show/hide category based on visible chips
            if (hasVisibleChips) {
                card.style.display = '';
                hasVisibleCards = true;
            } else {
                card.style.display = 'none';
            }
        });
        
        // Show/hide no results message
        if (noResults) {
            noResults.hidden = hasVisibleCards;
        }
    }
    
    showPatternModal(patternId) {
        const pattern = PATTERNS_DATA[patternId];
        if (!pattern) return;
        
        const modal = document.getElementById('pattern-modal');
        const title = document.getElementById('modal-title');
        const badge = document.getElementById('modal-badge');
        const body = document.getElementById('modal-body');
        
        if (!modal || !title || !badge || !body) return;
        
        // Set title and badge
        title.textContent = pattern.name;
        badge.textContent = pattern.type.charAt(0).toUpperCase() + pattern.type.slice(1);
        badge.className = `pattern-type-badge ${pattern.type}`;
        
        // Build modal content
        body.innerHTML = this.buildModalContent(pattern);
        
        // Apply syntax highlighting to code blocks
        if (typeof Prism !== 'undefined') {
            Prism.highlightAllUnder(body);
        }
        
        // Show modal
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    
    buildModalContent(pattern) {
        let html = '';
        
        // Intent
        html += `
            <section>
                <h3><i class="fas fa-bullseye"></i> Intent</h3>
                <p>${pattern.intent}</p>
            </section>
        `;
        
        // Problem
        if (pattern.problem) {
            html += `
                <section>
                    <h3><i class="fas fa-question-circle"></i> Problem</h3>
                    <p>${pattern.problem}</p>
                </section>
            `;
        }
        
        // Solution
        if (pattern.solution) {
            html += `
                <section>
                    <h3><i class="fas fa-lightbulb"></i> Solution</h3>
                    <p>${pattern.solution}</p>
                </section>
            `;
        }
        
        // Use Cases
        if (pattern.useCases && pattern.useCases.length > 0) {
            html += `
                <section>
                    <h3><i class="fas fa-check-circle"></i> Use Cases</h3>
                    <ul>
                        ${pattern.useCases.map(uc => `<li>${uc}</li>`).join('')}
                    </ul>
                </section>
            `;
        }
        
        // Consequences
        if (pattern.consequences) {
            html += `<section><h3><i class="fas fa-balance-scale"></i> Consequences</h3>`;
            
            if (pattern.consequences.positive && pattern.consequences.positive.length > 0) {
                html += `
                    <h4 style="color: var(--success); font-size: 0.95rem; margin-top: 0.75rem;">
                        <i class="fas fa-plus-circle"></i> Positive
                    </h4>
                    <ul>
                        ${pattern.consequences.positive.map(c => `<li>${c}</li>`).join('')}
                    </ul>
                `;
            }
            
            if (pattern.consequences.negative && pattern.consequences.negative.length > 0) {
                html += `
                    <h4 style="color: var(--warning); font-size: 0.95rem; margin-top: 0.75rem;">
                        <i class="fas fa-minus-circle"></i> Negative
                    </h4>
                    <ul>
                        ${pattern.consequences.negative.map(c => `<li>${c}</li>`).join('')}
                    </ul>
                `;
            }
            
            html += `</section>`;
        }
        
        // Code Example
        if (pattern.codeExample) {
            html += `
                <section>
                    <h3><i class="fas fa-code"></i> C# Implementation</h3>
                    <div class="code-block">
                        <pre><code class="language-csharp">${this.escapeHtml(pattern.codeExample)}</code></pre>
                    </div>
                </section>
            `;
        }
        
        // Related Patterns
        if (pattern.relatedPatterns && pattern.relatedPatterns.length > 0) {
            html += `
                <section>
                    <h3><i class="fas fa-link"></i> Related Patterns</h3>
                    <div class="pattern-chips">
                        ${pattern.relatedPatterns.map(rp => {
                            const rpId = rp.toLowerCase().replace(/ /g, '-');
                            const exists = PATTERNS_DATA[rpId];
                            return exists 
                                ? `<span class="pattern-chip" data-pattern="${rpId}">${rp}</span>`
                                : `<span class="pattern-chip" style="opacity: 0.5; cursor: default;">${rp}</span>`;
                        }).join('')}
                    </div>
                </section>
            `;
        }
        
        // CORTEX Integration
        if (pattern.cortexUsage) {
            html += `
                <div class="cortex-integration">
                    <h4><i class="fas fa-brain"></i> CORTEX Integration</h4>
                    <p>${pattern.cortexUsage}</p>
                </div>
            `;
        }
        
        return html;
    }
    
    hideModal() {
        const modal = document.getElementById('pattern-modal');
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Initialize app
const patternsApp = new PatternsApp();
