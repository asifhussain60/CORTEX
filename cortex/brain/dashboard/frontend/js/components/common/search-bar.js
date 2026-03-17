/**
 * CORTEX Dashboard — Search Bar Component
 * Real-time search with debouncing, quick filters, and URL state.
 *
 * Features:
 *  - initializeSearchBar() / initSearchBar() — wires all event listeners
 *  - performSearch() / debouncedSearch — debounced search (300ms)
 *  - filterResults() — filters rendered items by query + active filters
 *  - clearSearch() — resets all filters and clears input
 *  - URL query param sync — search= and filter= in window.location.search
 *  - Supports result types: orchestrator, ac-id, phase
 */

(function () {
  'use strict';

  /* -------------------------------------------------------------------------
     Constants
     ------------------------------------------------------------------------- */
  const DEBOUNCE_DELAY = 300;  // 300ms debounce delay
  const RESULT_TYPES = ['orchestrator', 'ac-id', 'phase'];
  const QUERY_PARAM = 'search';
  const FILTER_PARAM = 'filter';

  /* -------------------------------------------------------------------------
     State
     ------------------------------------------------------------------------- */
  let searchTimeout = null;
  let activeFilters = new Set();

  /* -------------------------------------------------------------------------
     Utility: debounce
     -------------------------------------------------------------------------- */
  function debounce(fn, delay) {
    return function () {
      const args = arguments;
      const ctx = this;
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(function () {
        fn.apply(ctx, args);
      }, delay);
    };
  }

  /* -------------------------------------------------------------------------
     highlightMatches — wraps matched text in <mark> tags
     -------------------------------------------------------------------------- */
  function highlightMatches(text, query) {
    if (!query) {
      return text;
    }
    const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`(${escaped})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
  }

  /* -------------------------------------------------------------------------
     filterResults — filters visible items by search query and active filters
     -------------------------------------------------------------------------- */
  function filterResults(query) {
    const normalized = (query || '').toLowerCase().trim();
    const items = document.querySelectorAll('[data-searchable], [data-type]');
    let visibleCount = 0;

    items.forEach(function (item) {
      const text = (item.textContent || item.innerText || '').toLowerCase();
      const type = (item.dataset.type || '').toLowerCase();

      // Apply type filter (orchestrator, ac-id, phase, etc.)
      const typeMatch =
        activeFilters.size === 0 ||
        Array.from(activeFilters).some(function (f) {
          return type.includes(f) || RESULT_TYPES.includes(f) && f === type;
        });

      // Apply text query (supports orchestrator, ac-id, phase)
      const textMatch = !normalized || text.includes(normalized);

      const visible = typeMatch && textMatch;
      item.style.display = visible ? '' : 'none';
      if (visible) {
        visibleCount++;
      }
    });

    return visibleCount;
  }

  /* -------------------------------------------------------------------------
     performSearch — main search handler
     -------------------------------------------------------------------------- */
  function performSearch(query) {
    const count = filterResults(query);
    updateResultsDisplay(query, count);
    updateURLParams(query);
  }

  /* -------------------------------------------------------------------------
     debouncedSearch — debounced wrapper for performSearch
     -------------------------------------------------------------------------- */
  const debouncedSearch = debounce(performSearch, DEBOUNCE_DELAY);

  /* -------------------------------------------------------------------------
     executeSearch — immediate (non-debounced) search execution  
     -------------------------------------------------------------------------- */
  function executeSearch(query) {
    performSearch(query);
  }

  /* -------------------------------------------------------------------------
     searchItems — search within a specific item set
     -------------------------------------------------------------------------- */
  function searchItems(items, query) {
    const normalized = (query || '').toLowerCase().trim();
    return items.filter(function (item) {
      const text = (item.label || item.name || item.title || '').toLowerCase();
      const type = (item.type || '').toLowerCase();
      return (
        !normalized ||
        text.includes(normalized) ||
        type.includes(normalized) ||
        RESULT_TYPES.some(function (rt) {
          return type.includes(rt) && normalized.includes(rt);
        })
      );
    });
  }

  /* -------------------------------------------------------------------------
     clearSearch — resets query and filters
     -------------------------------------------------------------------------- */
  function clearSearch() {
    const input = document.querySelector('.search-input, input[type="search"]');
    if (input) {
      input.value = '';
      input.focus();
    }

    activeFilters.clear();

    const filterBtns = document.querySelectorAll(
      '.filter-btn, .filter-button, .quick-filter'
    );
    filterBtns.forEach(function (btn) {
      btn.classList.remove('active');
      btn.setAttribute('aria-pressed', 'false');
    });

    filterResults('');
    hideResults();
    updateURLParams('');
  }

  /* -------------------------------------------------------------------------
     hideResults — hides the results dropdown
     -------------------------------------------------------------------------- */
  function hideResults() {
    const resultsEl = document.querySelector('.search-results, .results');
    if (resultsEl) {
      resultsEl.classList.remove('visible');
      resultsEl.style.display = 'none';
    }
  }

  /* -------------------------------------------------------------------------
     resetSearch — alias for clearSearch
     -------------------------------------------------------------------------- */
  const resetSearch = clearSearch;

  /* -------------------------------------------------------------------------
     updateResultsDisplay — shows/hides results area
     -------------------------------------------------------------------------- */
  function updateResultsDisplay(query, count) {
    const resultsEl = document.querySelector('.search-results, .results');
    const noResults = document.querySelector(
      '.no-results, .search-no-results, .search-empty, .empty'
    );
    const countEl = document.querySelector('.search-results-count');

    if (!query) {
      hideResults();
      return;
    }

    if (resultsEl) {
      resultsEl.classList.add('visible');
      resultsEl.style.display = 'block';
    }

    if (countEl) {
      countEl.textContent = `${count} result${count !== 1 ? 's' : ''}`;
    }

    if (noResults) {
      noResults.style.display = count === 0 ? 'flex' : 'none';
    }
  }

  /* -------------------------------------------------------------------------
     updateURLParams — syncs search state to URL query params
     -------------------------------------------------------------------------- */
  function updateURLParams(query) {
    try {
      const params = new URLSearchParams(window.location.search);

      if (query) {
        params.set(QUERY_PARAM, query);
      } else {
        params.delete(QUERY_PARAM);
      }

      if (activeFilters.size > 0) {
        params.set(FILTER_PARAM, Array.from(activeFilters).join(','));
      } else {
        params.delete(FILTER_PARAM);
      }

      const newSearch = params.toString();
      const newUrl = window.location.pathname + (newSearch ? '?' + newSearch : '') + window.location.hash;

      window.history.replaceState(null, '', newUrl);
    } catch (_) {
      // Ignore URL manipulation errors in non-browser environments
    }
  }

  /* -------------------------------------------------------------------------
     restoreFromURL — restores search state from query params
     -------------------------------------------------------------------------- */
  function restoreFromURL() {
    try {
      const params = new URLSearchParams(window.location.search);
      const query = params.get(QUERY_PARAM);
      const filter = params.get(FILTER_PARAM);

      if (query) {
        const input = document.querySelector('.search-input, input[type="search"]');
        if (input) {
          input.value = query;
          performSearch(query);
        }
      }

      if (filter) {
        filter.split(',').forEach(function (f) {
          activeFilters.add(f.trim());
          const btn = document.querySelector(`[data-filter="${f.trim()}"]`);
          if (btn) {
            btn.classList.add('active');
          }
        });
      }
    } catch (_) {
      // Ignore errors
    }
  }

  /* -------------------------------------------------------------------------
     Attach filter button handlers
     -------------------------------------------------------------------------- */
  function attachFilterHandlers() {
    const filterBtns = document.querySelectorAll(
      '.filter-btn, .filter-button, .quick-filter'
    );

    filterBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        const filterValue = btn.dataset.filter || btn.textContent.trim().toLowerCase();
        const isActive = btn.classList.toggle('active');

        btn.setAttribute('aria-pressed', String(isActive));

        if (isActive) {
          activeFilters.add(filterValue);
        } else {
          activeFilters.delete(filterValue);
        }

        const input = document.querySelector('.search-input, input[type="search"]');
        const query = input ? input.value : '';
        performSearch(query);
      });
    });
  }

  /* -------------------------------------------------------------------------
     Attach clear button handler
     -------------------------------------------------------------------------- */
  function attachClearHandler() {
    const clearBtn = document.querySelector(
      '.search-clear, .clear-btn, .clear-search, .search-clear-btn'
    );
    if (clearBtn) {
      clearBtn.addEventListener('click', clearSearch);
    }
  }

  /* -------------------------------------------------------------------------
     initSearchBar / initializeSearchBar — main entry point
     -------------------------------------------------------------------------- */
  function initSearchBar() {
    const input = document.querySelector('.search-input, input[type="search"]');
    if (!input) {
      return;
    }

    // Wire up input event with debounce
    input.addEventListener('input', function (event) {
      const query = event.target.value;
      debouncedSearch(query);
    });

    // Close results on Escape
    input.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') {
        clearSearch();
      }
    });

    // Attach filter and clear handlers
    attachFilterHandlers();
    attachClearHandler();

    // Restore state from URL
    restoreFromURL();
  }

  /* initializeSearchBar is an alias for initSearchBar */
  const initializeSearchBar = initSearchBar;

  /* -------------------------------------------------------------------------
     Auto-initialize when DOM is ready
     -------------------------------------------------------------------------- */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSearchBar);
  } else {
    initSearchBar();
  }

  /* -------------------------------------------------------------------------
     Public API
     -------------------------------------------------------------------------- */
  if (typeof window !== 'undefined') {
    window.CortexSearchBar = {
      initSearchBar: initSearchBar,
      initializeSearchBar: initializeSearchBar,
      performSearch: performSearch,
      debouncedSearch: debouncedSearch,
      executeSearch: executeSearch,
      filterResults: filterResults,
      searchItems: searchItems,
      clearSearch: clearSearch,
      resetSearch: resetSearch,
      hideResults: hideResults,
      highlightMatches: highlightMatches,
    };
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
      initSearchBar: initSearchBar,
      initializeSearchBar: initializeSearchBar,
      performSearch: performSearch,
      debouncedSearch: debouncedSearch,
      executeSearch: executeSearch,
      filterResults: filterResults,
      searchItems: searchItems,
      clearSearch: clearSearch,
      resetSearch: resetSearch,
      hideResults: hideResults,
      highlightMatches: highlightMatches,
    };
  }
})();
