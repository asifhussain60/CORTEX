/**
 * CORTEX Dashboard Search Bar Component
 * 
 * Provides intelligent search with debouncing, keyboard navigation,
 * and real-time suggestions across orchestrators, AC-IDs, and phases.
 * 
 * @module search-bar
 * @author Asif Hussain
 * @copyright © 2025-2026 Asif Hussain. All rights reserved.
 */

/**
 * Debounce function to limit rapid function calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, wait = 300) {
  let timeout = null;
  
  return function debounced(...args) {
    const later = () => {
      timeout = null;
      func.apply(this, args);
    };
    
    if (timeout !== null) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(later, wait);
  };
}

/**
 * Search Bar Component
 * Provides global search functionality for the CORTEX dashboard
 */
class CORTEXSearchBar {
  /**
   * Create a search bar instance
   * @param {Object} options - Configuration options
   * @param {string} options.containerId - ID of the container element
   * @param {Function} options.onSearch - Callback for search execution
   * @param {Function} options.onSelect - Callback when result is selected
   * @param {number} options.debounceMs - Debounce delay in milliseconds
   * @param {number} options.minChars - Minimum characters before search
   */
  constructor(options = {}) {
    this.options = {
      containerId: options.containerId || 'search-container',
      onSearch: options.onSearch || this.defaultSearch.bind(this),
      onSelect: options.onSelect || this.defaultSelect.bind(this),
      debounceMs: options.debounceMs || 300,
      minChars: options.minChars || 2,
      placeholder: options.placeholder || 'Search AC-IDs, phases, orchestrators...',
      maxResults: options.maxResults || 10,
      ...options
    };
    
    this.container = null;
    this.inputElement = null;
    this.resultsElement = null;
    this.clearButton = null;
    
    this.results = [];
    this.highlightedIndex = -1;
    this.isOpen = false;
    this.isLoading = false;
    
    // Bind methods
    this.handleInput = this.handleInput.bind(this);
    this.handleKeydown = this.handleKeydown.bind(this);
    this.handleClear = this.handleClear.bind(this);
    this.handleClickOutside = this.handleClickOutside.bind(this);
    
    // Create debounced search
    this.debouncedSearch = debounce(
      this.executeSearch.bind(this),
      this.options.debounceMs
    );
    
    this.init();
  }
  
  /**
   * Initialize the search bar
   */
  init() {
    this.container = document.getElementById(this.options.containerId);
    if (!this.container) {
      this.render();
    }
    
    this.bindElements();
    this.setupEventListeners();
  }
  
  /**
   * Render search bar HTML if container doesn't exist
   */
  render() {
    const html = `
      <div class="search-container" id="${this.options.containerId}">
        <div class="search-input-wrapper">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.35-4.35"></path>
          </svg>
          <input 
            type="text" 
            class="search-input" 
            id="cortex-search-input"
            placeholder="${this.options.placeholder}"
            autocomplete="off"
            aria-label="Search"
            aria-autocomplete="list"
            aria-expanded="false"
            aria-controls="search-results-list"
          />
          <button 
            class="search-clear-btn" 
            id="search-clear-btn"
            aria-label="Clear search"
            type="button"
          >
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 6L6 18M6 6l12 12"></path>
            </svg>
          </button>
          <span class="search-shortcut">⌘K</span>
        </div>
        <div class="search-results" id="search-results-list" role="listbox" aria-label="Search results">
        </div>
      </div>
    `;
    
    // Find or create parent container
    const parent = document.querySelector('.header-controls') || document.body;
    const wrapper = document.createElement('div');
    wrapper.innerHTML = html;
    parent.insertBefore(wrapper.firstElementChild, parent.firstChild);
    
    this.container = document.getElementById(this.options.containerId);
  }
  
  /**
   * Bind DOM elements
   */
  bindElements() {
    this.inputElement = this.container.querySelector('.search-input') 
      || document.getElementById('cortex-search-input');
    this.resultsElement = this.container.querySelector('.search-results')
      || document.getElementById('search-results-list');
    this.clearButton = this.container.querySelector('.search-clear-btn')
      || document.getElementById('search-clear-btn');
  }
  
  /**
   * Set up event listeners
   */
  setupEventListeners() {
    if (this.inputElement) {
      this.inputElement.addEventListener('input', this.handleInput);
      this.inputElement.addEventListener('keydown', this.handleKeydown);
      this.inputElement.addEventListener('focus', () => this.showResults());
    }
    
    if (this.clearButton) {
      this.clearButton.addEventListener('click', this.handleClear);
    }
    
    // Click outside to close
    document.addEventListener('click', this.handleClickOutside);
    
    // Keyboard shortcut (Cmd/Ctrl + K)
    document.addEventListener('keydown', (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        this.focus();
      }
      // Escape to close
      if (e.key === 'Escape' && this.isOpen) {
        this.hideResults();
      }
    });
  }
  
  /**
   * Handle input changes
   * @param {Event} event - Input event
   */
  handleInput(event) {
    const query = event.target.value.trim();
    
    // Update clear button visibility
    if (this.clearButton) {
      this.clearButton.classList.toggle('visible', query.length > 0);
    }
    
    // Check minimum characters
    if (query.length < this.options.minChars) {
      this.hideResults();
      return;
    }
    
    // Show loading and trigger debounced search
    this.showLoading();
    this.debouncedSearch(query);
  }
  
  /**
   * Handle keyboard navigation
   * @param {KeyboardEvent} event - Keyboard event
   */
  handleKeydown(event) {
    if (!this.isOpen || this.results.length === 0) return;
    
    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        this.highlightNext();
        break;
        
      case 'ArrowUp':
        event.preventDefault();
        this.highlightPrevious();
        break;
        
      case 'Enter':
        event.preventDefault();
        if (this.highlightedIndex >= 0) {
          this.selectResult(this.results[this.highlightedIndex]);
        }
        break;
        
      case 'Escape':
        this.hideResults();
        this.inputElement.blur();
        break;
    }
  }
  
  /**
   * Handle clear button click
   */
  handleClear() {
    this.inputElement.value = '';
    this.clearButton.classList.remove('visible');
    this.hideResults();
    this.inputElement.focus();
  }
  
  /**
   * Handle click outside to close results
   * @param {Event} event - Click event
   */
  handleClickOutside(event) {
    if (!this.container.contains(event.target)) {
      this.hideResults();
    }
  }
  
  /**
   * Execute search query
   * @param {string} query - Search query
   */
  async executeSearch(query) {
    try {
      const results = await this.options.onSearch(query);
      this.results = results.slice(0, this.options.maxResults);
      this.highlightedIndex = -1;
      this.renderResults();
    } catch (error) {
      console.error('Search error:', error);
      this.renderError('Search failed. Please try again.');
    }
  }
  
  /**
   * Default search implementation
   * @param {string} query - Search query
   * @returns {Promise<Array>} Search results
   */
  async defaultSearch(query) {
    // This is a placeholder - override with actual search logic
    const lowerQuery = query.toLowerCase();
    
    // Mock data for demonstration
    const mockData = [
      { type: 'orchestrator', id: 'brain-orchestrator', title: 'Brain Orchestrator', description: 'Core brain visualization' },
      { type: 'orchestrator', id: 'temporal-orchestrator', title: 'Temporal Orchestrator', description: 'Time-based operations' },
      { type: 'ac-id', id: 'AC-001', title: 'AC-001', description: 'Initial acceptance criteria' },
      { type: 'phase', id: 'phase-a', title: 'Phase A', description: 'Foundation phase' },
      { type: 'phase', id: 'phase-b', title: 'Phase B', description: 'Build phase' },
    ];
    
    return mockData.filter(item => 
      item.title.toLowerCase().includes(lowerQuery) ||
      item.description.toLowerCase().includes(lowerQuery) ||
      item.id.toLowerCase().includes(lowerQuery)
    );
  }
  
  /**
   * Default select handler
   * @param {Object} result - Selected result
   */
  defaultSelect(result) {
    console.log('Selected:', result);
    window.location.hash = `#/${result.type}/${result.id}`;
  }
  
  /**
   * Render search results
   */
  renderResults() {
    this.isLoading = false;
    
    if (this.results.length === 0) {
      this.resultsElement.innerHTML = `
        <div class="search-no-results">
          <svg class="search-no-results-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.35-4.35"></path>
          </svg>
          <div class="search-no-results-title">No results found</div>
          <div class="search-no-results-hint">Try different keywords</div>
        </div>
      `;
    } else {
      this.resultsElement.innerHTML = this.results.map((result, index) => `
        <div 
          class="search-result-item ${index === this.highlightedIndex ? 'highlighted' : ''}" 
          data-index="${index}"
          role="option"
          aria-selected="${index === this.highlightedIndex}"
        >
          <div class="search-result-icon">
            ${this.getResultIcon(result.type)}
          </div>
          <div class="search-result-content">
            <div class="search-result-title">${this.highlightMatch(result.title)}</div>
            <div class="search-result-description">${result.description || ''}</div>
          </div>
        </div>
      `).join('');
      
      // Add click handlers to results
      this.resultsElement.querySelectorAll('.search-result-item').forEach((item, index) => {
        item.addEventListener('click', () => this.selectResult(this.results[index]));
      });
    }
    
    this.showResults();
  }
  
  /**
   * Render loading state
   */
  showLoading() {
    this.isLoading = true;
    this.resultsElement.innerHTML = `
      <div class="search-loading">
        <div class="search-loading-spinner"></div>
      </div>
    `;
    this.showResults();
  }
  
  /**
   * Render error state
   * @param {string} message - Error message
   */
  renderError(message) {
    this.resultsElement.innerHTML = `
      <div class="search-no-results">
        <div class="search-no-results-title">${message}</div>
      </div>
    `;
    this.showResults();
  }
  
  /**
   * Get icon SVG for result type
   * @param {string} type - Result type
   * @returns {string} SVG markup
   */
  getResultIcon(type) {
    const icons = {
      orchestrator: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"></circle><path d="M12 2v4M12 18v4M2 12h4M18 12h4"></path></svg>',
      'ac-id': '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"></path><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"></path></svg>',
      phase: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12,6 12,12 16,14"></polyline></svg>',
      default: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><path d="m21 21-4.35-4.35"></path></svg>'
    };
    
    return icons[type] || icons.default;
  }
  
  /**
   * Highlight matching text
   * @param {string} text - Text to highlight
   * @returns {string} HTML with highlights
   */
  highlightMatch(text) {
    const query = this.inputElement.value.trim();
    if (!query) return text;
    
    const regex = new RegExp(`(${this.escapeRegex(query)})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
  }
  
  /**
   * Escape regex special characters
   * @param {string} str - String to escape
   * @returns {string} Escaped string
   */
  escapeRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }
  
  /**
   * Show results dropdown
   */
  showResults() {
    this.isOpen = true;
    this.resultsElement.classList.add('active');
    this.inputElement.setAttribute('aria-expanded', 'true');
  }
  
  /**
   * Hide results dropdown
   */
  hideResults() {
    this.isOpen = false;
    this.resultsElement.classList.remove('active');
    this.inputElement.setAttribute('aria-expanded', 'false');
    this.highlightedIndex = -1;
  }
  
  /**
   * Highlight next result
   */
  highlightNext() {
    this.highlightedIndex = Math.min(
      this.highlightedIndex + 1,
      this.results.length - 1
    );
    this.updateHighlight();
  }
  
  /**
   * Highlight previous result
   */
  highlightPrevious() {
    this.highlightedIndex = Math.max(this.highlightedIndex - 1, 0);
    this.updateHighlight();
  }
  
  /**
   * Update visual highlight
   */
  updateHighlight() {
    const items = this.resultsElement.querySelectorAll('.search-result-item');
    items.forEach((item, index) => {
      item.classList.toggle('highlighted', index === this.highlightedIndex);
      item.setAttribute('aria-selected', index === this.highlightedIndex);
    });
    
    // Scroll highlighted item into view
    const highlighted = items[this.highlightedIndex];
    if (highlighted) {
      highlighted.scrollIntoView({ block: 'nearest' });
    }
  }
  
  /**
   * Select a result
   * @param {Object} result - Selected result
   */
  selectResult(result) {
    this.inputElement.value = result.title;
    this.hideResults();
    this.options.onSelect(result);
  }
  
  /**
   * Focus the search input
   */
  focus() {
    this.inputElement.focus();
  }
  
  /**
   * Destroy the component
   */
  destroy() {
    document.removeEventListener('click', this.handleClickOutside);
    if (this.inputElement) {
      this.inputElement.removeEventListener('input', this.handleInput);
      this.inputElement.removeEventListener('keydown', this.handleKeydown);
    }
    if (this.clearButton) {
      this.clearButton.removeEventListener('click', this.handleClear);
    }
  }
}

/**
 * Initialize search bar on DOM ready
 */
function initSearchBar(options = {}) {
  return new CORTEXSearchBar(options);
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { CORTEXSearchBar, debounce, initSearchBar };
}

// Auto-initialize if DOM is ready
if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => initSearchBar());
  }
}
