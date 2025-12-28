/**
 * CORTEX Technical Documentation - Search
 * Version: 1.0.0
 * Author: Asif Hussain
 * Copyright: © 2025 Asif Hussain. All rights reserved.
 */

class SearchManager {
    constructor() {
        this.searchInput = document.getElementById('searchInput');
        this.searchIndex = [];
        this.resultContainer = null;
        this.init();
    }

    async init() {
        if (this.searchInput) {
            await this.loadSearchIndex();
            this.setupSearchUI();
            this.addSearchListeners();
        }
    }

    async loadSearchIndex() {
        try {
            const response = await fetch('search-index.json');
            this.searchIndex = await response.json();
        } catch (error) {
            console.warn('Search index not found, generating from page...');
            this.buildSearchIndexFromPage();
        }
    }

    buildSearchIndexFromPage() {
        // Fallback: build search index from current page content
        const contentElements = document.querySelectorAll('h1, h2, h3, p, .card');
        this.searchIndex = Array.from(contentElements).map((el, index) => ({
            id: `content-${index}`,
            title: el.tagName.match(/H[1-6]/) ? el.textContent : '',
            content: el.textContent,
            url: window.location.pathname,
            section: this.getSection(el)
        }));
    }

    setupSearchUI() {
        // Create results container
        this.resultContainer = document.createElement('div');
        this.resultContainer.className = 'search-results glass';
        this.resultContainer.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            max-height: 400px;
            overflow-y: auto;
            margin-top: 8px;
            padding: 12px;
            border-radius: 12px;
            display: none;
            z-index: 1000;
        `;
        this.searchInput.parentElement.appendChild(this.resultContainer);
    }

    addSearchListeners() {
        let debounceTimer;
        
        this.searchInput.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                this.performSearch(e.target.value);
            }, 300);
        });

        this.searchInput.addEventListener('focus', () => {
            if (this.searchInput.value.length >= 2) {
                this.performSearch(this.searchInput.value);
            }
        });

        // Close results when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.searchInput.parentElement.contains(e.target)) {
                this.hideResults();
            }
        });

        // Keyboard navigation
        this.searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideResults();
            }
        });
    }

    performSearch(query) {
        if (query.length < 2) {
            this.hideResults();
            return;
        }

        const results = this.search(query);
        this.displayResults(results, query);
    }

    search(query) {
        const lowerQuery = query.toLowerCase();
        const results = [];

        this.searchIndex.forEach(item => {
            let score = 0;
            const titleMatch = item.title?.toLowerCase().includes(lowerQuery);
            const contentMatch = item.content?.toLowerCase().includes(lowerQuery);

            if (titleMatch) score += 10;
            if (contentMatch) score += 5;

            // Fuzzy matching
            if (!titleMatch && !contentMatch) {
                const titleScore = this.fuzzyMatch(lowerQuery, item.title?.toLowerCase() || '');
                const contentScore = this.fuzzyMatch(lowerQuery, item.content?.toLowerCase() || '');
                score = Math.max(titleScore, contentScore);
            }

            if (score > 0) {
                results.push({ ...item, score });
            }
        });

        return results
            .sort((a, b) => b.score - a.score)
            .slice(0, 10);
    }

    fuzzyMatch(query, text) {
        let score = 0;
        let queryIndex = 0;

        for (let i = 0; i < text.length && queryIndex < query.length; i++) {
            if (text[i] === query[queryIndex]) {
                score++;
                queryIndex++;
            }
        }

        return queryIndex === query.length ? score : 0;
    }

    displayResults(results, query) {
        if (results.length === 0) {
            this.resultContainer.innerHTML = `
                <div style="color: var(--text-secondary); padding: 12px; text-align: center;">
                    <i class="fas fa-search"></i> No results found for "${query}"
                </div>
            `;
            this.showResults();
            return;
        }

        const html = results.map(result => `
            <a href="${result.url}" class="search-result-item" style="
                display: block;
                padding: 12px;
                margin-bottom: 8px;
                background: var(--bg-secondary);
                border-radius: 8px;
                text-decoration: none;
                color: var(--text-primary);
                transition: all 0.2s ease;
            ">
                <div style="font-weight: 600; margin-bottom: 4px; color: var(--primary);">
                    ${this.highlightQuery(result.title || 'Untitled', query)}
                </div>
                <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.4;">
                    ${this.truncate(this.highlightQuery(result.content, query), 100)}
                </div>
                ${result.section ? `
                    <div style="font-size: 11px; color: var(--text-muted); margin-top: 4px;">
                        <i class="fas fa-folder"></i> ${result.section}
                    </div>
                ` : ''}
            </a>
        `).join('');

        this.resultContainer.innerHTML = html;

        // Add hover effect
        this.resultContainer.querySelectorAll('.search-result-item').forEach(item => {
            item.addEventListener('mouseenter', function() {
                this.style.background = 'var(--bg-hover)';
                this.style.transform = 'translateX(4px)';
            });
            item.addEventListener('mouseleave', function() {
                this.style.background = 'var(--bg-secondary)';
                this.style.transform = 'translateX(0)';
            });
        });

        this.showResults();
    }

    highlightQuery(text, query) {
        if (!text) return '';
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<span style="background: var(--warning); color: var(--text-inverse); padding: 2px 4px; border-radius: 2px;">$1</span>');
    }

    truncate(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    showResults() {
        this.resultContainer.style.display = 'block';
    }

    hideResults() {
        this.resultContainer.style.display = 'none';
    }

    getSection(element) {
        // Try to determine section from URL or element hierarchy
        const path = window.location.pathname;
        if (path.includes('/architecture/')) return 'Architecture';
        if (path.includes('/api/')) return 'API Reference';
        if (path.includes('/workflows/')) return 'Workflows';
        if (path.includes('/integration/')) return 'Integration';
        if (path.includes('/deployment/')) return 'Deployment';
        if (path.includes('/setup-guides/')) return 'Setup Guides';
        return 'Documentation';
    }
}

// Initialize search on page load
document.addEventListener('DOMContentLoaded', () => {
    window.searchManager = new SearchManager();
});
