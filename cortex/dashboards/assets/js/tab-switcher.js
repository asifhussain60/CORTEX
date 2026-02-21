/**
 * CORTEX Dashboard - Tab Switcher Component
 *
 * Handles tab-based view switching with URL hash persistence,
 * keyboard navigation, and smooth transitions.
 *
 * Authority: DO-002-02 Tab-based View Switching
 */

'use strict';

/**
 * No-arg canonical entry point for the tab switcher (used by index.html inline scripts).
 * Delegates to initializeTabSwitcher with default selector.
 * @returns {void}
 */
function initializeTabSwitcher() { return _initTabSwitcherImpl('.tab-container'); }

/**
 * Internal implementation of tab switcher initialization.
 * Attaches event listeners and restores tab state from URL hash.
 *
 * @param {string} containerSelector - CSS selector for tab container
 * @returns {void}
 */
function _initTabSwitcherImpl(containerSelector) {
  var selector = containerSelector || '.tab-container';
  var containers = document.querySelectorAll(selector);

  containers.forEach(function (container) {
    var tabList = container.querySelector('.tab-list, .tab-nav, [role="tablist"]');
    if (!tabList) return;

    var tabs = tabList.querySelectorAll('.tab-item, .tab, [role="tab"]');

    // Attach click handlers
    tabs.forEach(function (tab) {
      tab.addEventListener('click', function (event) {
        event.preventDefault();
        var targetId = tab.dataset.tab || tab.getAttribute('href') || tab.getAttribute('aria-controls');
        if (targetId) {
          switchTab(container, targetId.replace(/^#/, ''));
        }
      });
    });

    // Keyboard navigation
    tabList.addEventListener('keydown', function (event) {
      var currentTab = document.activeElement;
      var tabArray = Array.from(tabs);
      var currentIndex = tabArray.indexOf(currentTab);

      if (event.key === 'ArrowRight' || event.key === 'ArrowDown') {
        event.preventDefault();
        var nextIndex = (currentIndex + 1) % tabArray.length;
        tabArray[nextIndex].focus();
        tabArray[nextIndex].click();
      } else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
        event.preventDefault();
        var prevIndex = (currentIndex - 1 + tabArray.length) % tabArray.length;
        tabArray[prevIndex].focus();
        tabArray[prevIndex].click();
      } else if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        currentTab.click();
      }
    });
  });

  // Restore tab from URL hash on page load
  restoreTabFromURL();

  // Listen for hash changes
  window.addEventListener('hashchange', function () {
    restoreTabFromURL();
  });
}

/**
 * Switch to a specific tab by ID.
 *
 * @param {Element} container - The tab container element
 * @param {string} tabId - The ID of the tab to activate
 * @returns {void}
 */
function switchTab(container, tabId) {
  if (!container || !tabId) return;

  var tabs = container.querySelectorAll('.tab-item, .tab, [role="tab"]');
  var panels = container.querySelectorAll('.tab-panel, .tab-content > [id]');

  // Deactivate all tabs
  tabs.forEach(function (tab) {
    tab.classList.remove('active');
    tab.setAttribute('aria-selected', 'false');
    tab.setAttribute('tabindex', '-1');
  });

  // Hide all panels
  panels.forEach(function (panel) {
    panel.classList.add('hidden');
    panel.style.display = 'none';
    panel.setAttribute('hidden', '');
  });

  // Activate the target tab
  var targetTab = container.querySelector(
    '[data-tab="' + tabId + '"], [aria-controls="' + tabId + '"], [href="#' + tabId + '"]'
  );

  if (targetTab) {
    targetTab.classList.add('active');
    targetTab.setAttribute('aria-selected', 'true');
    targetTab.setAttribute('tabindex', '0');
  }

  // Show the target panel and lazy-load content if needed
  var targetPanel = container.querySelector('#' + tabId);
  if (targetPanel) {
    targetPanel.classList.remove('hidden');
    targetPanel.style.display = '';
    targetPanel.removeAttribute('hidden');
    loadTabContent(targetPanel, tabId);
  }

  // Update URL hash
  if (window.location.hash !== '#' + tabId) {
    window.location.hash = tabId;
  }
}

/**
 * Restore the active tab based on the current URL hash.
 *
 * @returns {void}
 */
function restoreTabFromURL() {
  var hash = window.location.hash;
  if (!hash) return;

  var tabId = hash.replace(/^#/, '');
  var containers = document.querySelectorAll('.tab-container');

  containers.forEach(function (container) {
    var matchingTab = container.querySelector(
      '[data-tab="' + tabId + '"], [aria-controls="' + tabId + '"], [href="#' + tabId + '"]'
    );
    if (matchingTab) {
      switchTab(container, tabId);
    }
  });
}

/**
 * Lazily load tab content when a tab is activated.
 * Uses data-src attribute to fetch content if not already loaded.
 *
 * @param {Element} panel - The tab panel element to load content into
 * @param {string} tabId - The ID of the tab being activated
 * @returns {void}
 */
function loadTabContent(panel, tabId) {
  if (!panel) return;

  // Check if content has already been loaded
  if (panel.dataset.loaded === 'true') return;

  var dataSrc = panel.dataset.src;
  if (!dataSrc) {
    panel.dataset.loaded = 'true';
    return;
  }

  // Mark as loading
  panel.dataset.loaded = 'loading';

  fetch(dataSrc)
    .then(function (response) {
      if (!response.ok) throw new Error('Failed to load tab content');
      return response.text();
    })
    .then(function (html) {
      panel.innerHTML = html;
      panel.dataset.loaded = 'true';
    })
    .catch(function (err) {
      console.error('Tab content load error for', tabId, err);
      panel.dataset.loaded = 'error';
    });
}

// Auto-initialize on DOMContentLoaded
// Canonical no-arg entry point: function initializeTabSwitcher()
if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      initializeTabSwitcher();
    });
  } else {
    initializeTabSwitcher();
  }
}

// Export for module environments
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { initializeTabSwitcher: initializeTabSwitcher, switchTab: switchTab, restoreTabFromURL: restoreTabFromURL, loadTabContent: loadTabContent };
}
