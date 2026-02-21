/**
 * CORTEX Dashboard - Search Bar Component
 *
 * Global search with debounced real-time filtering, quick filters,
 * URL state persistence, and result highlighting.
 *
 * Authority: DO-002-03 Search and Filter Bar
 */

'use strict';

/**
 * Initialize the CORTEX global search bar.
 *
 * @param {string} [inputSelector='#search-input'] - CSS selector for the search input
 * @returns {void}
 */
function initSearchBar(inputSelector) {
  var input = document.querySelector(inputSelector || '#search-input, .search-input');
  if (!input) return;

  var clearBtn = document.querySelector('.search-clear, .clear-btn, .clear-search');
  var resultsContainer = document.querySelector('.search-results, .results');
  var filterBtns = document.querySelectorAll('.filter-btn, .filter-button, .quick-filter');

  // Active filter state
  var activeFilters = {};
  var currentQuery = '';

  // Restore query from URL on init
  var params = new URLSearchParams(window.location.search);
  var urlQuery = params.get('q') || params.get('search') || '';
  if (urlQuery) {
    input.value = urlQuery;
    currentQuery = urlQuery;
    debouncedSearch(urlQuery);
  }

  // Attach debounced input handler
  input.addEventListener('input', function (event) {
    var query = event.target.value.trim();
    currentQuery = query;
    debouncedSearch(query);
  });

  // Clear button
  if (clearBtn) {
    clearBtn.addEventListener('click', function () {
      clearSearch();
    });
  }

  // Quick filter buttons
  filterBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var filterType = btn.dataset.filter || btn.textContent.trim().toLowerCase();
      if (btn.classList.contains('active')) {
        btn.classList.remove('active');
        delete activeFilters[filterType];
      } else {
        btn.classList.add('active');
        activeFilters[filterType] = true;
      }
      performSearch(currentQuery, activeFilters);
    });
  });

  /**
   * Debounced search trigger (300ms delay).
   *
   * @param {string} query - The search query string
   * @returns {void}
   */
  function debouncedSearch(query) {
    clearTimeout(debouncedSearch._timer);
    debouncedSearch._timer = setTimeout(function () {
      performSearch(query, activeFilters);
    }, 300);
  }

  /**
   * Execute search and display filtered results.
   *
   * @param {string} query - The search query string
   * @param {Object} filters - Active filter map
   * @returns {void}
   */
  function performSearch(query, filters) {
    // Update URL query param
    var searchParams = new URLSearchParams(window.location.search);
    if (query) {
      searchParams.set('q', query);
    } else {
      searchParams.delete('q');
    }
    var newUrl = window.location.pathname +
      (searchParams.toString() ? '?' + searchParams.toString() : '') +
      window.location.hash;
    window.history.replaceState(null, '', newUrl);

    // Collect all searchable items from the DOM
    var items = collectSearchItems();

    // Filter items: query match && active filter match
    var filtered = items.filter(function (item) {
      var matchesQuery = !query ||
        item.text.toLowerCase().indexOf(query.toLowerCase()) !== -1;

      var matchesFilters = Object.keys(filters).every(function (filterKey) {
        return filterResults(item, filterKey);
      });

      return matchesQuery && matchesFilters;
    });

    renderResults(filtered, query);
  }

  /**
   * Filter a single item against a filter key.
   *
   * @param {Object} item - The item to test
   * @param {string} filterKey - The filter to apply
   * @returns {boolean}
   */
  function filterResults(item, filterKey) {
    if (!filterKey) return true;
    var type = (item.type || '').toLowerCase();
    var status = (item.status || '').toLowerCase();

    if (filterKey === 'completed') return status === 'completed' || status === 'done';
    if (filterKey === 'in-progress') return status === 'in-progress' || status === 'active';
    if (filterKey === 'blocked') return status === 'blocked' || status === 'failed';
    if (filterKey === 'orchestrator') return type === 'orchestrator';
    if (filterKey === 'phase') return type === 'phase';
    if (filterKey === 'ac-id') return type === 'ac-id';
    return true;
  }

  /**
   * Collect searchable items from the current DOM.
   *
   * @returns {Array<Object>} Array of searchable item objects
   */
  function collectSearchItems() {
    var results = [];
    // Orchestrators
    document.querySelectorAll('[data-searchable]').forEach(function (el) {
      results.push({
        el: el,
        text: el.textContent || '',
        type: el.dataset.type || 'orchestrator',
        status: el.dataset.status || '',
        href: el.dataset.href || el.querySelector('a') && el.querySelector('a').href || '#',
      });
    });
    // Also search table rows tagged with type
    document.querySelectorAll('tr[data-type]').forEach(function (row) {
      results.push({
        el: row,
        text: row.textContent || '',
        type: row.dataset.type || 'ac-id',
        status: row.dataset.status || '',
        href: '#',
      });
    });
    return results;
  }

  /**
   * Render search results into the results container.
   *
   * @param {Array<Object>} items - Filtered items to display
   * @param {string} query - Current query string (for highlighting)
   * @returns {void}
   */
  function renderResults(items, query) {
    if (!resultsContainer) return;

    if (!query && Object.keys(activeFilters).length === 0) {
      hideResults();
      return;
    }

    if (items.length === 0) {
      resultsContainer.innerHTML =
        '<div class="no-results search-no-results">No results found for "' +
        escapeHtml(query) + '"</div>';
      resultsContainer.style.display = '';
      return;
    }

    var html = items.slice(0, 20).map(function (item) {
      var highlighted = highlightQuery(escapeHtml(item.text.trim().slice(0, 80)), query);
      var typeLabel = (item.type || 'item').toLowerCase();
      return '<div class="search-result-item" data-type="' + escapeHtml(typeLabel) + '">' +
        '<span class="search-result-icon">&#128269;</span>' +
        '<span class="search-result-text">' + highlighted + '</span>' +
        '<span class="search-result-type">' + escapeHtml(typeLabel) + '</span>' +
        '</div>';
    }).join('');

    resultsContainer.innerHTML = html;
    resultsContainer.style.display = '';
  }

  /**
   * Clear search input and reset all filters.
   *
   * @returns {void}
   */
  function clearSearch() {
    input.value = '';
    currentQuery = '';
    activeFilters = {};

    filterBtns.forEach(function (btn) {
      btn.classList.remove('active');
    });

    hideResults();

    // Clear URL params
    var searchParams = new URLSearchParams(window.location.search);
    searchParams.delete('q');
    searchParams.delete('search');
    var newUrl = window.location.pathname +
      (searchParams.toString() ? '?' + searchParams.toString() : '') +
      window.location.hash;
    window.history.replaceState(null, '', newUrl);
  }

  /**
   * Hide results container.
   *
   * @returns {void}
   */
  function hideResults() {
    if (resultsContainer) {
      resultsContainer.innerHTML = '';
      resultsContainer.style.display = 'none';
    }
  }

  /**
   * Highlight matching query text in a string.
   *
   * @param {string} text - The text to search within
   * @param {string} query - The query to highlight
   * @returns {string} HTML string with highlights
   */
  function highlightQuery(text, query) {
    if (!query) return text;
    var escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    return text.replace(new RegExp('(' + escaped + ')', 'gi'),
      '<mark class="search-highlight">$1</mark>');
  }

  /**
   * Escape HTML special characters.
   *
   * @param {string} str - Raw string
   * @returns {string} HTML-escaped string
   */
  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // Close results when clicking outside
  document.addEventListener('click', function (event) {
    if (!input.contains(event.target) &&
        (!resultsContainer || !resultsContainer.contains(event.target))) {
      hideResults();
    }
  });
}

// Auto-initialize on DOMContentLoaded
if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      initSearchBar();
    });
  } else {
    initSearchBar();
  }
}

// Export for module environments
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { initSearchBar: initSearchBar };
}
