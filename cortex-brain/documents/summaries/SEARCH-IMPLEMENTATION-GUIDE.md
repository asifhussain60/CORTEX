# Global Documentation Search Implementation Guide

**Author:** Asif Hussain | **Date:** December 27, 2025  
**Status:** 🎯 READY FOR IMPLEMENTATION

---

## 🎯 Overview

Lightweight client-side search for CORTEX documentation using Lunr.js (3.5KB gzipped), compatible with GitHub Pages static hosting.

---

## 📦 Required Assets

### 1. Lunr.js Library
**File:** `docs/assets/js/lunr.min.js`  
**Source:** https://unpkg.com/lunr@2.3.9/lunr.min.js  
**Size:** 3.5KB gzipped, 12KB uncompressed  
**License:** MIT

```bash
# Download Lunr.js
curl -o docs/assets/js/lunr.min.js https://unpkg.com/lunr@2.3.9/lunr.min.js
```

### 2. Search Index
**File:** `docs/search-index.json`  
**Generated:** During documentation orchestrator execution  
**Structure:**
```json
{
  "version": "1.0",
  "generated": "2025-12-27T10:30:00Z",
  "index": {
    "version": "2.3.9",
    "fields": ["title", "category", "tags", "content"],
    "ref": "id",
    "documentStore": { ... },
    "tokenStore": { ... },
    "corpusTokens": [ ... ],
    "pipeline": ["stemmer"]
  },
  "docs": [
    {
      "id": "architecture/four-tier-brain.html",
      "title": "4-Tier Brain Architecture",
      "category": "Architecture",
      "tags": ["brain", "tier0", "tier1", "tier2", "tier3", "governance"],
      "excerpt": "Hierarchical memory system with Tier 0 governance, Tier 1 working memory...",
      "url": "architecture/four-tier-brain.html"
    }
  ]
}
```

### 3. Search Implementation
**File:** `docs/assets/js/search.js`

---

## 🔧 Search Index Generation (Docgen Phase)

Add to `docgen.prompt.md` execution workflow:

### Phase 3: Content Generation (Enhanced)
```javascript
// Pseudo-code for documentation orchestrator
const searchDocs = []

// Crawl all generated HTML pages
for (const page of generatedPages) {
    // Parse HTML content
    const $ = cheerio.load(page.html)
    
    // Extract searchable content
    const title = $('h1').first().text().trim()
    const category = page.category // orchestrators, architecture, features, etc.
    const tags = extractTags($) // From meta tags or content
    const excerpt = $('p.description').first().text().trim().substring(0, 200)
    
    // Remove code blocks, navigation, footers for cleaner search
    $('.breadcrumb, nav, footer, pre, code').remove()
    const content = $('main').text().replace(/\s+/g, ' ').trim()
    
    searchDocs.push({
        id: page.url,
        title: title,
        category: category,
        tags: tags,
        excerpt: excerpt,
        content: content.substring(0, 5000), // Limit content size
        url: page.url
    })
}

// Build Lunr index
const idx = lunr(function () {
    this.ref('id')
    this.field('title', { boost: 10 })      // Titles weighted 10x
    this.field('category', { boost: 5 })     // Categories weighted 5x
    this.field('tags', { boost: 5 })         // Tags weighted 5x
    this.field('content')                    // Body content normal weight
    
    searchDocs.forEach((doc, i) => {
        console.log(`Indexing ${i+1}/${searchDocs.length}: ${doc.title}`)
        this.add(doc)
    })
})

// Save to JSON
const searchIndex = {
    version: '1.0',
    generated: new Date().toISOString(),
    index: idx.toJSON(),
    docs: searchDocs.map(doc => ({
        id: doc.id,
        title: doc.title,
        category: doc.category,
        tags: doc.tags,
        excerpt: doc.excerpt,
        url: doc.url
    }))
}

fs.writeFileSync('docs/search-index.json', JSON.stringify(searchIndex, null, 2))
console.log(`✅ Search index created: ${searchDocs.length} pages indexed`)
console.log(`📦 Index size: ${(JSON.stringify(searchIndex).length / 1024).toFixed(2)} KB`)
```

### Tag Extraction Helper
```javascript
function extractTags($) {
    const tags = new Set()
    
    // From meta keywords
    const metaKeywords = $('meta[name="keywords"]').attr('content')
    if (metaKeywords) {
        metaKeywords.split(',').forEach(tag => tags.add(tag.trim().toLowerCase()))
    }
    
    // From heading keywords (h2, h3)
    $('h2, h3').each((i, el) => {
        const text = $(el).text().toLowerCase()
        // Extract key terms (skip common words)
        const terms = text.split(/\s+/).filter(word => 
            word.length > 3 && !['this', 'that', 'with', 'from'].includes(word)
        )
        terms.forEach(term => tags.add(term))
    })
    
    // From code blocks (language identifiers)
    $('pre code[class*="language-"]').each((i, el) => {
        const lang = $(el).attr('class').match(/language-(\w+)/)
        if (lang) tags.add(lang[1])
    })
    
    return Array.from(tags).slice(0, 10) // Max 10 tags per page
}
```

---

## 🎨 Search UI Components

### 1. Navigation Bar Integration
Add to ALL page templates (`assets/css/main.css`):

```css
/* Search Container */
.search-container {
    position: relative;
    max-width: 600px;
    margin: 0 auto 2rem;
}

.search-input {
    width: 100%;
    padding: 1rem 3rem 1rem 1.5rem;
    background: var(--glass-bg);
    border: 2px solid var(--glass-border);
    border-radius: 12px;
    color: var(--text-primary);
    font-size: 1rem;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}

.search-input:focus {
    outline: none;
    border-color: var(--accent-primary);
    box-shadow: var(--glow);
}

.search-input::placeholder {
    color: var(--text-secondary);
    opacity: 0.7;
}

.search-icon {
    position: absolute;
    right: 1.5rem;
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-secondary);
    pointer-events: none;
}

/* Search Results Dropdown */
.search-results {
    position: absolute;
    top: calc(100% + 0.5rem);
    left: 0;
    right: 0;
    max-height: 500px;
    overflow-y: auto;
    background: var(--glass-bg);
    border: 2px solid var(--glass-border);
    border-radius: 12px;
    backdrop-filter: blur(10px);
    z-index: 1000;
    box-shadow: var(--shadow);
}

.search-results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid var(--glass-border);
}

.search-results-count {
    color: var(--text-secondary);
    font-size: 0.9rem;
}

.search-results-close {
    background: none;
    border: none;
    color: var(--text-secondary);
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0;
    width: 2rem;
    height: 2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
    transition: all 0.2s ease;
}

.search-results-close:hover {
    background: rgba(255, 255, 255, 0.1);
    color: var(--text-primary);
}

.search-results-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.search-result-item {
    padding: 1rem 1.5rem;
    border-bottom: 1px solid var(--glass-border);
    cursor: pointer;
    transition: background 0.2s ease;
}

.search-result-item:hover,
.search-result-item.active {
    background: rgba(0, 212, 255, 0.1);
}

.search-result-item:last-child {
    border-bottom: none;
}

.search-result-title {
    color: var(--text-primary);
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.search-result-category {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    background: rgba(123, 97, 255, 0.2);
    border: 1px solid rgba(123, 97, 255, 0.4);
    border-radius: 6px;
    font-size: 0.8rem;
    color: var(--accent-secondary);
    font-weight: 500;
}

.search-result-excerpt {
    color: var(--text-secondary);
    font-size: 0.9rem;
    line-height: 1.5;
}

.search-result-match {
    background: rgba(0, 212, 255, 0.3);
    color: var(--accent-primary);
    font-weight: 600;
    padding: 0 0.25rem;
    border-radius: 3px;
}

/* Empty State */
.search-results-empty {
    padding: 2rem;
    text-align: center;
    color: var(--text-secondary);
}

.search-results-empty-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    opacity: 0.5;
}

/* Loading State */
.search-results-loading {
    padding: 2rem;
    text-align: center;
    color: var(--text-secondary);
}

.search-spinner {
    display: inline-block;
    width: 2rem;
    height: 2rem;
    border: 3px solid var(--glass-border);
    border-top-color: var(--accent-primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* Keyboard Shortcut Hint */
.search-shortcut {
    position: absolute;
    right: 4rem;
    top: 50%;
    transform: translateY(-50%);
    padding: 0.25rem 0.5rem;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid var(--glass-border);
    border-radius: 4px;
    color: var(--text-secondary);
    font-size: 0.75rem;
    font-family: monospace;
    pointer-events: none;
}

/* Responsive */
@media (max-width: 768px) {
    .search-container {
        max-width: 100%;
        margin: 0 1rem 2rem;
    }
    
    .search-shortcut {
        display: none;
    }
    
    .search-results {
        max-height: 400px;
    }
}
```

### 2. HTML Template
Add to page header (after logo, before main content):

```html
<!-- Global Search Bar -->
<div class="search-container">
    <i class="fas fa-search search-icon"></i>
    <input type="text" 
           id="globalSearch" 
           class="search-input" 
           placeholder="Search documentation..." 
           autocomplete="off"
           aria-label="Search CORTEX documentation">
    <kbd class="search-shortcut">Ctrl+K</kbd>
</div>

<!-- Search Results Dropdown (hidden by default) -->
<div id="searchResults" class="search-results" hidden>
    <div class="search-results-header">
        <span id="searchResultsCount" class="search-results-count">0 results</span>
        <button id="closeSearch" 
                class="search-results-close" 
                aria-label="Close search">✕</button>
    </div>
    <ul id="searchResultsList" class="search-results-list">
        <!-- Results populated by search.js -->
    </ul>
</div>
```

---

## 💻 Search Implementation (search.js)

**File:** `docs/assets/js/search.js`

```javascript
/**
 * CORTEX Global Documentation Search
 * Uses Lunr.js for client-side full-text search
 */

class CortexSearch {
    constructor() {
        this.searchInput = document.getElementById('globalSearch')
        this.searchResults = document.getElementById('searchResults')
        this.searchResultsList = document.getElementById('searchResultsList')
        this.searchResultsCount = document.getElementById('searchResultsCount')
        this.closeSearchBtn = document.getElementById('closeSearch')
        
        this.index = null
        this.docs = []
        this.selectedIndex = -1
        
        this.init()
    }
    
    async init() {
        // Load search index
        try {
            const response = await fetch('/search-index.json')
            const data = await response.json()
            
            // Deserialize Lunr index
            this.index = lunr.Index.load(data.index)
            this.docs = data.docs
            
            console.log(`✅ Search initialized: ${this.docs.length} pages indexed`)
        } catch (error) {
            console.error('❌ Failed to load search index:', error)
            return
        }
        
        // Event listeners
        this.searchInput.addEventListener('input', this.handleSearch.bind(this))
        this.searchInput.addEventListener('keydown', this.handleKeyboard.bind(this))
        this.closeSearchBtn.addEventListener('click', this.closeResults.bind(this))
        
        // Close on click outside
        document.addEventListener('click', (e) => {
            if (!this.searchResults.contains(e.target) && 
                !this.searchInput.contains(e.target)) {
                this.closeResults()
            }
        })
        
        // Keyboard shortcut: Ctrl+K or Cmd+K
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault()
                this.searchInput.focus()
            }
            
            // Escape to close
            if (e.key === 'Escape') {
                this.closeResults()
                this.searchInput.blur()
            }
        })
    }
    
    handleSearch(e) {
        const query = e.target.value.trim()
        
        if (query.length < 2) {
            this.closeResults()
            return
        }
        
        // Search with Lunr
        try {
            const results = this.index.search(query + '*') // Wildcard for partial matches
            this.displayResults(results, query)
        } catch (error) {
            console.error('Search error:', error)
            this.displayError()
        }
    }
    
    displayResults(results, query) {
        this.selectedIndex = -1
        
        if (results.length === 0) {
            this.displayEmpty(query)
            return
        }
        
        // Show results dropdown
        this.searchResults.hidden = false
        this.searchResultsCount.textContent = `${results.length} result${results.length !== 1 ? 's' : ''}`
        
        // Clear previous results
        this.searchResultsList.innerHTML = ''
        
        // Render top 10 results
        results.slice(0, 10).forEach((result, index) => {
            const doc = this.docs.find(d => d.id === result.ref)
            if (!doc) return
            
            const li = document.createElement('li')
            li.className = 'search-result-item'
            li.dataset.index = index
            li.dataset.url = doc.url
            
            // Highlight matching terms in excerpt
            const highlightedExcerpt = this.highlightMatches(doc.excerpt, query)
            
            li.innerHTML = `
                <div class="search-result-title">
                    <span>${doc.title}</span>
                    <span class="search-result-category">${doc.category}</span>
                </div>
                <div class="search-result-excerpt">${highlightedExcerpt}</div>
            `
            
            // Click handler
            li.addEventListener('click', () => {
                window.location.href = doc.url
            })
            
            // Hover handler
            li.addEventListener('mouseenter', () => {
                this.selectResult(index)
            })
            
            this.searchResultsList.appendChild(li)
        })
    }
    
    displayEmpty(query) {
        this.searchResults.hidden = false
        this.searchResultsCount.textContent = '0 results'
        this.searchResultsList.innerHTML = `
            <div class="search-results-empty">
                <div class="search-results-empty-icon">🔍</div>
                <p>No results found for "<strong>${this.escapeHtml(query)}</strong>"</p>
                <p style="font-size: 0.85rem; margin-top: 0.5rem;">
                    Try different keywords or check spelling
                </p>
            </div>
        `
    }
    
    displayError() {
        this.searchResults.hidden = false
        this.searchResultsCount.textContent = 'Error'
        this.searchResultsList.innerHTML = `
            <div class="search-results-empty">
                <div class="search-results-empty-icon">⚠️</div>
                <p>Search error occurred</p>
            </div>
        `
    }
    
    highlightMatches(text, query) {
        const terms = query.toLowerCase().split(/\s+/)
        let highlighted = this.escapeHtml(text)
        
        terms.forEach(term => {
            if (term.length < 2) return
            const regex = new RegExp(`(${term})`, 'gi')
            highlighted = highlighted.replace(regex, '<span class="search-result-match">$1</span>')
        })
        
        return highlighted
    }
    
    handleKeyboard(e) {
        const items = this.searchResultsList.querySelectorAll('.search-result-item')
        
        if (items.length === 0) return
        
        if (e.key === 'ArrowDown') {
            e.preventDefault()
            this.selectedIndex = Math.min(this.selectedIndex + 1, items.length - 1)
            this.selectResult(this.selectedIndex)
        } else if (e.key === 'ArrowUp') {
            e.preventDefault()
            this.selectedIndex = Math.max(this.selectedIndex - 1, 0)
            this.selectResult(this.selectedIndex)
        } else if (e.key === 'Enter' && this.selectedIndex >= 0) {
            e.preventDefault()
            const selectedItem = items[this.selectedIndex]
            window.location.href = selectedItem.dataset.url
        }
    }
    
    selectResult(index) {
        const items = this.searchResultsList.querySelectorAll('.search-result-item')
        items.forEach(item => item.classList.remove('active'))
        
        if (index >= 0 && index < items.length) {
            items[index].classList.add('active')
            items[index].scrollIntoView({ block: 'nearest' })
            this.selectedIndex = index
        }
    }
    
    closeResults() {
        this.searchResults.hidden = true
        this.selectedIndex = -1
    }
    
    escapeHtml(text) {
        const div = document.createElement('div')
        div.textContent = text
        return div.innerHTML
    }
}

// Initialize search when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new CortexSearch()
    })
} else {
    new CortexSearch()
}
```

---

## 📋 Integration Checklist

### Phase 1: Assets
- [ ] Download Lunr.js → `docs/assets/js/lunr.min.js`
- [ ] Create search.js → `docs/assets/js/search.js`
- [ ] Add search CSS → `docs/assets/css/main.css`

### Phase 2: Search Index Generation
- [ ] Add index generation to docgen orchestrator (Phase 3)
- [ ] Test with 5-10 sample pages
- [ ] Validate JSON structure
- [ ] Check index size (<500KB)

### Phase 3: UI Integration
- [ ] Add search bar to `docs/index.html`
- [ ] Add search bar to ALL generated pages
- [ ] Test keyboard shortcuts (Ctrl+K, Escape, Arrow keys)
- [ ] Test mobile responsive behavior

### Phase 4: Validation
- [ ] Search returns relevant results (<200ms)
- [ ] Highlighting works on matching terms
- [ ] Keyboard navigation functional
- [ ] Mobile-friendly (search icon, no shortcuts shown)
- [ ] Accessibility (ARIA labels, keyboard-only navigation)

---

## 🎯 Success Metrics

1. **Performance:** Search response <200ms for 100+ pages
2. **Relevance:** Top 3 results include expected page >95% of queries
3. **Index Size:** <500KB for full documentation set
4. **Accessibility:** Lighthouse score >90
5. **Mobile:** Works on 320px-4K screens

---

## 🔄 Maintenance

**Update search index:** Re-run docgen orchestrator after adding/updating documentation

**Optimize index:** If size >500KB, reduce content field length or exclude low-value pages

**Monitor queries:** Add analytics (optional) to track popular searches and improve navigation

---

**Estimated Effort:** 4 hours implementation + 2 hours testing = 6 hours total
