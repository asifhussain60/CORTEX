/**
 * CORTEX Global Documentation Search
 * Uses Lunr.js for client-side full-text search
 * 
 * @author Asif Hussain
 * @version 1.0
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
        
        // Initialize if search elements exist
        if (this.searchInput && this.searchResults) {
            this.init()
        }
    }
    
    async init() {
        // Load search index
        try {
            const response = await fetch('/search-index.json')
            if (!response.ok) {
                console.warn('⚠️  Search index not found. Run docgen to generate.')
                return
            }
            
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
                    <span>${this.escapeHtml(doc.title)}</span>
                    <span class="search-result-category">${this.escapeHtml(doc.category)}</span>
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
            const regex = new RegExp(`(${this.escapeRegex(term)})`, 'gi')
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
    
    escapeRegex(str) {
        return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
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
