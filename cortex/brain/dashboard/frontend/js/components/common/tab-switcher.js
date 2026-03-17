/**
 * CORTEX Dashboard — Tab Switcher Component
 * Manages tab-based view switching with URL hash state persistence,
 * keyboard navigation, and lazy content loading support.
 */

(function () {
  'use strict';

  /* -------------------------------------------------------------------------
     Constants
     -------------------------------------------------------------------------- */
  var ACTIVE_CLASS = 'active';
  var TAB_CONTAINER_SELECTOR = '.tab-container, .tabs';
  var TAB_ITEM_SELECTOR = '.tab-item, .tab';
  var TAB_CONTENT_SELECTOR = '.tab-content, .tab-panel';

  /* -------------------------------------------------------------------------
     switchTab — activates a tab by ID or element
     -------------------------------------------------------------------------- */
  function switchTab(tabIdOrEl, container) {
    var root = container || document;
    var tabItems = root.querySelectorAll(TAB_ITEM_SELECTOR);
    var tabContents = root.querySelectorAll(TAB_CONTENT_SELECTOR);
    var targetId = typeof tabIdOrEl === 'string' ? tabIdOrEl : tabIdOrEl.dataset.tab;

    tabItems.forEach(function (item) {
      var isTarget = item.dataset.tab === targetId || item.id === targetId;
      if (isTarget) {
        item.classList.add(ACTIVE_CLASS);
        item.setAttribute('aria-selected', 'true');
      } else {
        item.classList.remove(ACTIVE_CLASS);
        item.setAttribute('aria-selected', 'false');
      }
    });

    tabContents.forEach(function (panel) {
      var panelId = panel.dataset.tabContent || panel.id;
      if (panelId === targetId) {
        panel.classList.remove('hidden');
        panel.removeAttribute('hidden');
        loadTabContent(panel);
      } else {
        panel.classList.add('hidden');
        panel.setAttribute('hidden', '');
      }
    });

    // Persist state in URL hash
    if (targetId) {
      window.location.hash = '#tab-' + targetId;
    }
  }

  /* -------------------------------------------------------------------------
     activateTab — alias for switchTab (used internally)
     -------------------------------------------------------------------------- */
  function activateTab(tabId, container) {
    switchTab(tabId, container);
  }

  /* -------------------------------------------------------------------------
     loadTabContent — lazy-loads tab panel content
     -------------------------------------------------------------------------- */
  function loadTabContent(panel) {
    var dataUrl = panel.dataset.src || panel.dataset.loaded;
    if (!dataUrl || panel.dataset.loaded === 'true') {
      return;
    }

    panel.dataset.loaded = 'true';

    var loadingEl = document.createElement('div');
    loadingEl.className = 'tab-loading';
    loadingEl.setAttribute('aria-live', 'polite');
    loadingEl.textContent = 'Loading…';
    panel.appendChild(loadingEl);

    // Lazy-load content via fetch
    fetchTabData(dataUrl, panel, loadingEl);
  }

  /* -------------------------------------------------------------------------
     fetchTabData — fetch remote tab content
     -------------------------------------------------------------------------- */
  function fetchTabData(url, panel, loadingEl) {
    if (typeof fetch === 'undefined') {
      if (loadingEl && loadingEl.parentNode) {
        loadingEl.parentNode.removeChild(loadingEl);
      }
      return;
    }

    fetch(url)
      .then(function (response) {
        if (!response.ok) {
          throw new Error('HTTP ' + response.status);
        }
        return response.text();
      })
      .then(function (html) {
        if (loadingEl && loadingEl.parentNode) {
          loadingEl.parentNode.removeChild(loadingEl);
        }
        var wrapper = document.createElement('div');
        wrapper.innerHTML = html;
        panel.appendChild(wrapper);
      })
      .catch(function (err) {
        if (loadingEl) {
          loadingEl.textContent = 'Failed to load content.';
        }
        console.warn('CORTEX TabSwitcher: fetchTabData error', err);
      });
  }

  /* -------------------------------------------------------------------------
     restoreTabFromURL — parses window.location.hash to restore active tab
     -------------------------------------------------------------------------- */
  function restoreTabFromURL(container) {
    var hash = window.location.hash;
    if (!hash) {
      return false;
    }

    var tabId = hash.replace(/^#tab-/, '');
    if (!tabId) {
      return false;
    }

    var root = container || document;
    var target = root.querySelector('[data-tab="' + tabId + '"]') ||
                 root.querySelector('#' + tabId);

    if (target) {
      switchTab(tabId, root);
      return true;
    }
    return false;
  }

  /* -------------------------------------------------------------------------
     setTabFromHash — alias for restoreTabFromURL
     -------------------------------------------------------------------------- */
  function setTabFromHash(container) {
    return restoreTabFromURL(container);
  }

  /* -------------------------------------------------------------------------
     activateTabFromHash — alias for restoreTabFromURL
     -------------------------------------------------------------------------- */
  function activateTabFromHash(container) {
    return restoreTabFromURL(container);
  }

  /* -------------------------------------------------------------------------
     attachClickHandlers — wire click events to tab items
     -------------------------------------------------------------------------- */
  function attachClickHandlers(container) {
    var tabItems = container.querySelectorAll(TAB_ITEM_SELECTOR);

    tabItems.forEach(function (item) {
      item.addEventListener('click', function (event) {
        event.preventDefault();
        switchTab(item, container);
      });

      // Keyboard navigation (Enter / Space / Arrow keys)
      item.addEventListener('keydown', function (event) {
        var allTabs = Array.from(container.querySelectorAll(TAB_ITEM_SELECTOR));
        var idx = allTabs.indexOf(item);

        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          switchTab(item, container);
        } else if (event.key === 'ArrowRight') {
          var next = allTabs[(idx + 1) % allTabs.length];
          if (next) {
            next.focus();
            switchTab(next, container);
          }
        } else if (event.key === 'ArrowLeft') {
          var prev = allTabs[(idx - 1 + allTabs.length) % allTabs.length];
          if (prev) {
            prev.focus();
            switchTab(prev, container);
          }
        }
      });
    });
  }

  /* -------------------------------------------------------------------------
     initializeTabSwitcher — main entry point
     -------------------------------------------------------------------------- */
  function initializeTabSwitcher() {
    var containers = document.querySelectorAll(TAB_CONTAINER_SELECTOR);

    containers.forEach(function (container) {
      attachClickHandlers(container);

      // Try to restore tab from URL hash first
      var restored = restoreTabFromURL(container);

      if (!restored) {
        // Activate the first tab by default
        var firstTab = container.querySelector(TAB_ITEM_SELECTOR);
        if (firstTab) {
          var firstTabId = firstTab.dataset.tab || firstTab.id;
          if (firstTabId) {
            switchTab(firstTabId, container);
          }
        }
      }
    });

    // Handle hash changes (browser back/forward)
    window.addEventListener('hashchange', function () {
      var containers2 = document.querySelectorAll(TAB_CONTAINER_SELECTOR);
      containers2.forEach(function (c) {
        restoreTabFromURL(c);
      });
    });
  }

  /* -------------------------------------------------------------------------
     Auto-initialize when DOM is ready
     -------------------------------------------------------------------------- */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeTabSwitcher);
  } else {
    initializeTabSwitcher();
  }

  /* -------------------------------------------------------------------------
     Public API
     -------------------------------------------------------------------------- */
  if (typeof window !== 'undefined') {
    window.CortexTabSwitcher = {
      initializeTabSwitcher: initializeTabSwitcher,
      switchTab: switchTab,
      activateTab: activateTab,
      restoreTabFromURL: restoreTabFromURL,
      setTabFromHash: setTabFromHash,
      activateTabFromHash: activateTabFromHash,
      loadTabContent: loadTabContent,
      fetchTabData: fetchTabData,
    };
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
      initializeTabSwitcher: initializeTabSwitcher,
      switchTab: switchTab,
      activateTab: activateTab,
      restoreTabFromURL: restoreTabFromURL,
      setTabFromHash: setTabFromHash,
      activateTabFromHash: activateTabFromHash,
      loadTabContent: loadTabContent,
      fetchTabData: fetchTabData,
    };
  }
})();
