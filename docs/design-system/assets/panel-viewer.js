/**
 * CORTEX Panel Viewer - Interactivity
 * Real-time panel rendering and interaction logic
 * 
 * Author: Asif Hussain
 * Copyright © 2024-2026 Asif Hussain. All rights reserved.
 */

// Panel data configuration
const PANEL_DATA = {
    'tetris': {
        name: 'panel-tetris',
        type: 'Layout',
        tokens: 8,
        html: `<div class="panel-tetris">
  <div class="panel-tetris__tile">
    <div class="panel-tetris__icon">📊</div>
    <div class="panel-tetris__content">
      <div class="panel-tetris__value">847</div>
      <div class="panel-tetris__label">AST Nodes</div>
    </div>
  </div>
  <div class="panel-tetris__tile">
    <div class="panel-tetris__icon">🔍</div>
    <div class="panel-tetris__content">
      <div class="panel-tetris__value">23</div>
      <div class="panel-tetris__label">Patterns</div>
    </div>
  </div>
  <div class="panel-tetris__tile">
    <div class="panel-tetris__icon">🧠</div>
    <div class="panel-tetris__content">
      <div class="panel-tetris__value">15</div>
      <div class="panel-tetris__label">Insights</div>
    </div>
  </div>
  <div class="panel-tetris__tile">
    <div class="panel-tetris__icon">📦</div>
    <div class="panel-tetris__content">
      <div class="panel-tetris__value">42</div>
      <div class="panel-tetris__label">Modules</div>
    </div>
  </div>
  <div class="panel-tetris__tile">
    <div class="panel-tetris__icon">⚡</div>
    <div class="panel-tetris__content">
      <div class="panel-tetris__value">30</div>
      <div class="panel-tetris__label">Score</div>
    </div>
  </div>
  <div class="panel-tetris__tile">
    <div class="panel-tetris__icon">📅</div>
    <div class="panel-tetris__content">
      <div class="panel-tetris__value">Jan</div>
      <div class="panel-tetris__label">2026</div>
    </div>
  </div>
</div>`,
        css: `/* Tokens used: */
--glass-bg-base
--glass-blur-md
--glass-border-subtle
--glass-border-standard
--radius-lg
--shadow-glass-md
--space-lg
--gap-sm
--glass-bg-tile
--glass-bg-hover
--transition-glass`
    },
    'intro': {
        name: 'panel-intro',
        type: 'Hero',
        tokens: 10,
        html: `<div class="panel-intro">
  <h2 class="panel-intro__title">What Is CORTEX Lens?</h2>
  <p class="panel-intro__description">
    Extract actionable intelligence from any codebase. 
    CORTEX Lens analyzes structure, patterns, and dependencies 
    to provide instant architectural insights.
  </p>
  <a href="#" class="panel-intro__cta">
    Explore Capabilities →
  </a>
</div>`,
        css: `/* Tokens used: */
--glass-bg-gradient-hero
--glass-blur-lg
--glass-border-accent
--glass-border-neon
--radius-xl
--shadow-hero
--shadow-glass-hover
--space-2xl
--glass-accent-cyan-medium
--glass-accent-cyan-strong
--transition-glass
--transition-fast`
    },
    'compact-cards': {
        name: 'panel-compact-cards',
        type: 'Layout',
        tokens: 9,
        html: `<div class="panel-compact-cards">
  <div class="panel-compact-cards__card">
    <div class="panel-compact-cards__icon">🔍</div>
    <h3 class="panel-compact-cards__title">AST Analysis</h3>
    <p class="panel-compact-cards__description">
      Parse and analyze abstract syntax trees with precision.
    </p>
  </div>
  <div class="panel-compact-cards__card">
    <div class="panel-compact-cards__icon">🧬</div>
    <h3 class="panel-compact-cards__title">Pattern Detection</h3>
    <p class="panel-compact-cards__description">
      Identify design patterns and anti-patterns automatically.
    </p>
  </div>
  <div class="panel-compact-cards__card">
    <div class="panel-compact-cards__icon">📦</div>
    <h3 class="panel-compact-cards__title">Dependency Mapping</h3>
    <p class="panel-compact-cards__description">
      Visualize module relationships and dependencies.
    </p>
  </div>
  <div class="panel-compact-cards__card">
    <div class="panel-compact-cards__icon">🧠</div>
    <h3 class="panel-compact-cards__title">Intel Extraction</h3>
    <p class="panel-compact-cards__description">
      Extract actionable intelligence from code structure.
    </p>
  </div>
  <div class="panel-compact-cards__card">
    <div class="panel-compact-cards__icon">🔧</div>
    <h3 class="panel-compact-cards__title">Reverse Engineering</h3>
    <p class="panel-compact-cards__description">
      Understand legacy systems through automated analysis.
    </p>
  </div>
</div>`,
        css: `/* Tokens used: */
--glass-bg-card
--glass-blur-md
--glass-border-subtle
--glass-border-standard
--radius-md
--shadow-glass-sm
--shadow-glass-md
--space-xl
--gap-md
--glass-bg-hover
--glass-accent-cyan-subtle
--transition-glass`
    },
    'grid-cards': {
        name: 'panel-grid-cards',
        type: 'Layout',
        tokens: 11,
        html: `<div class="panel-grid-cards">
  <div class="panel-grid-cards__card">
    <div class="panel-grid-cards__icon">🔍</div>
    <h3 class="panel-grid-cards__title">AST Analysis</h3>
    <p class="panel-grid-cards__description">
      Parse and analyze abstract syntax trees with precision. 
      Identify code structure and relationships at the node level.
    </p>
    <div class="panel-grid-cards__badges">
      <span class="panel-grid-cards__badge">NEW</span>
      <span class="panel-grid-cards__badge">AI-POWERED</span>
    </div>
  </div>
  <div class="panel-grid-cards__card">
    <div class="panel-grid-cards__icon">🧬</div>
    <h3 class="panel-grid-cards__title">Pattern Detection</h3>
    <p class="panel-grid-cards__description">
      Automatically identify design patterns, anti-patterns, 
      and code smells throughout your codebase.
    </p>
    <div class="panel-grid-cards__badges">
      <span class="panel-grid-cards__badge">BETA</span>
    </div>
  </div>
  <div class="panel-grid-cards__card">
    <div class="panel-grid-cards__icon">📦</div>
    <h3 class="panel-grid-cards__title">Dependency Mapping</h3>
    <p class="panel-grid-cards__description">
      Visualize module relationships and dependencies. 
      Understand coupling and cohesion metrics.
    </p>
    <div class="panel-grid-cards__badges">
      <span class="panel-grid-cards__badge">STABLE</span>
    </div>
  </div>
  <div class="panel-grid-cards__card">
    <div class="panel-grid-cards__icon">🏗️</div>
    <h3 class="panel-grid-cards__title">Architecture Extraction</h3>
    <p class="panel-grid-cards__description">
      Extract high-level architecture from code structure. 
      Generate architecture diagrams automatically.
    </p>
    <div class="panel-grid-cards__badges">
      <span class="panel-grid-cards__badge">NEW</span>
    </div>
  </div>
  <div class="panel-grid-cards__card">
    <div class="panel-grid-cards__icon">🐛</div>
    <h3 class="panel-grid-cards__title">Code Smell Detection</h3>
    <p class="panel-grid-cards__description">
      Identify potential issues and technical debt. 
      Get actionable recommendations for improvement.
    </p>
    <div class="panel-grid-cards__badges">
      <span class="panel-grid-cards__badge">BETA</span>
    </div>
  </div>
  <div class="panel-grid-cards__card">
    <div class="panel-grid-cards__icon">📊</div>
    <h3 class="panel-grid-cards__title">Complexity Metrics</h3>
    <p class="panel-grid-cards__description">
      Calculate cyclomatic complexity, cognitive complexity, 
      and maintainability index scores.
    </p>
    <div class="panel-grid-cards__badges">
      <span class="panel-grid-cards__badge">STABLE</span>
    </div>
  </div>
</div>`,
        css: `/* Tokens used: */
--glass-bg-card
--glass-blur-md
--glass-border-subtle
--glass-border-accent
--radius-lg
--shadow-glass-md
--shadow-glass-lg
--space-xl
--gap-lg
--glass-bg-hover
--glass-accent-cyan-medium
--glass-accent-cyan-subtle
--radius-sm
--transition-glass`
    },
    'hero-glass': {
        name: 'panel-hero-glass',
        type: 'Hero',
        tokens: 7,
        html: `<div class="panel-hero-glass">
  <h1 class="panel-hero-glass__title">
    Welcome to CORTEX
  </h1>
  <p class="panel-hero-glass__subtitle">
    AI-powered codebase intelligence and architectural analysis
  </p>
  <div class="panel-hero-glass__actions">
    <a href="#" class="panel-intro__cta">Get Started</a>
    <a href="#" class="panel-intro__cta">Learn More</a>
  </div>
</div>`,
        css: `/* Tokens used: */
--glass-bg-gradient-hero
--glass-blur-lg
--glass-border-accent
--radius-xl
--shadow-hero
--space-2xl
--transition-glass`
    },
    'sidebar-glass': {
        name: 'panel-sidebar-glass',
        type: 'Navigation',
        tokens: 9,
        html: `<div class="panel-sidebar-glass">
  <h2 class="panel-sidebar-glass__title">Navigation</h2>
  
  <div class="panel-sidebar-glass__section">
    <div class="panel-sidebar-glass__section-title">Main</div>
    <a href="#" class="panel-sidebar-glass__item panel-sidebar-glass__item--active">
      🏠 Dashboard
    </a>
    <a href="#" class="panel-sidebar-glass__item">
      📊 Analytics
    </a>
    <a href="#" class="panel-sidebar-glass__item">
      🔍 Search
    </a>
  </div>
  
  <div class="panel-sidebar-glass__section">
    <div class="panel-sidebar-glass__section-title">Tools</div>
    <a href="#" class="panel-sidebar-glass__item">
      🛠️ Settings
    </a>
    <a href="#" class="panel-sidebar-glass__item">
      📚 Documentation
    </a>
  </div>
</div>`,
        css: `/* Tokens used: */
--glass-bg-base
--glass-blur-sm
--glass-border-subtle
--radius-lg
--radius-sm
--shadow-glass-md
--space-lg
--glass-bg-tile
--glass-accent-cyan-subtle
--transition-fast`
    },
    'modal-glass': {
        name: 'panel-modal-glass',
        type: 'UI Component',
        tokens: 10,
        html: `<div class="panel-modal-glass">
  <div class="panel-modal-glass__header">
    <h2 class="panel-modal-glass__title">Confirmation</h2>
    <button class="panel-modal-glass__close">✕</button>
  </div>
  
  <div class="panel-modal-glass__content">
    <p>Are you sure you want to proceed with this action? 
    This operation cannot be undone.</p>
  </div>
  
  <div class="panel-modal-glass__footer">
    <button class="panel-intro__cta" style="background: var(--glass-bg-tile);">
      Cancel
    </button>
    <button class="panel-intro__cta">
      Confirm
    </button>
  </div>
</div>`,
        css: `/* Tokens used: */
--glass-bg-modal
--glass-blur-lg
--glass-border-standard
--radius-lg
--radius-sm
--shadow-hero
--space-xl
--glass-bg-tile
--glass-accent-danger-subtle
--transition-fast
--z-index-modal
--z-index-modal-backdrop`
    },
    'toast-glass': {
        name: 'panel-toast-glass',
        type: 'UI Component',
        tokens: 7,
        html: `<!-- Success Toast -->
<div class="panel-toast-glass panel-toast-glass--success">
  <div class="panel-toast-glass__container">
    <div class="panel-toast-glass__icon">✅</div>
    <div class="panel-toast-glass__content">
      <div class="panel-toast-glass__title">Success!</div>
      <div class="panel-toast-glass__message">
        Your changes have been saved successfully.
      </div>
    </div>
    <button class="panel-toast-glass__close">✕</button>
  </div>
</div>

<!-- Error Toast -->
<div class="panel-toast-glass panel-toast-glass--error" style="top: 5rem;">
  <div class="panel-toast-glass__container">
    <div class="panel-toast-glass__icon">❌</div>
    <div class="panel-toast-glass__content">
      <div class="panel-toast-glass__title">Error</div>
      <div class="panel-toast-glass__message">
        Failed to process your request. Please try again.
      </div>
    </div>
    <button class="panel-toast-glass__close">✕</button>
  </div>
</div>`,
        css: `/* Tokens used: */
--glass-bg-toast
--glass-blur-md
--glass-border-standard
--radius-md
--shadow-glass-lg
--space-lg
--z-index-toast
--transition-fast`
    },
    'blob-glass': {
        name: 'panel-blob-glass',
        type: 'Decorative',
        tokens: 5,
        html: `<div style="position: relative; height: 400px; overflow: hidden;">
  <div class="panel-blob-glass panel-blob-glass--md panel-blob-glass--cyan" 
       style="top: 20%; left: 10%;"></div>
  <div class="panel-blob-glass panel-blob-glass--lg panel-blob-glass--purple" 
       style="top: 40%; right: 15%; animation-delay: 2s;"></div>
  <div class="panel-blob-glass panel-blob-glass--sm panel-blob-glass--cyan" 
       style="bottom: 20%; left: 60%; animation-delay: 4s;"></div>
</div>`,
        css: `/* Tokens used: */
--glass-bg-base
--glass-blur-lg
--glass-border-subtle
--shadow-glass-md
--glass-accent-cyan-subtle
--glass-accent-purple-subtle
--glass-border-accent
--transition-morph`
    },
    'neon-glass': {
        name: 'panel-neon-glass',
        type: 'Accent',
        tokens: 8,
        html: `<div class="panel-neon-glass">
  <h3 class="panel-neon-glass__title">🚀 Try CORTEX Today</h3>
  <p class="panel-neon-glass__content">
    Start analyzing your codebase in seconds. Get instant insights 
    into architecture, patterns, and technical debt. No setup required.
  </p>
  <a href="#" class="panel-intro__cta">
    Start Free Trial →
  </a>
</div>`,
        css: `/* Tokens used: */
--glass-bg-base
--glass-blur-md
--glass-border-gradient-neon
--radius-lg
--shadow-glass-md
--shadow-glass-lg
--space-lg
--glass-bg-hover
--transition-glass`
    },
    'agent-showcase': {
        name: 'panel-agent-showcase',
        type: 'Layout',
        tokens: 12,
        html: `<div class="panel-agent-showcase">
  <div class="panel-agent-showcase__header">
    <span class="panel-agent-showcase__icon">✅</span>
    <div class="panel-agent-showcase__header-text">
      <h2 class="panel-agent-showcase__title">Planning Agent</h2>
      <p class="panel-agent-showcase__subtitle">Task Decomposition & Workflow Design</p>
    </div>
  </div>
  
  <div class="panel-agent-showcase__grid">
    <div class="panel-agent-showcase__card">
      <span class="panel-agent-showcase__card-icon">🧩</span>
      <h3 class="panel-agent-showcase__card-title">Task Decomposition</h3>
      <p class="panel-agent-showcase__card-description">Break complex tasks into phases</p>
    </div>
    
    <div class="panel-agent-showcase__card">
      <span class="panel-agent-showcase__card-icon">≡</span>
      <h3 class="panel-agent-showcase__card-title">Dependency Sequencing</h3>
      <p class="panel-agent-showcase__card-description">Logical workflow ordering</p>
    </div>
    
    <div class="panel-agent-showcase__card">
      <span class="panel-agent-showcase__card-icon">⏱</span>
      <h3 class="panel-agent-showcase__card-title">Effort Estimation</h3>
      <p class="panel-agent-showcase__card-description">Duration & resource planning</p>
    </div>
    
    <div class="panel-agent-showcase__card">
      <span class="panel-agent-showcase__card-icon">⚠</span>
      <h3 class="panel-agent-showcase__card-title">Risk Identification</h3>
      <p class="panel-agent-showcase__card-description">Detect blockers early</p>
    </div>
  </div>
  
  <div class="panel-agent-showcase__tag-section">
    <span class="panel-agent-showcase__tag-label">🔧 USED BY</span>
    <span class="panel-agent-showcase__tag">Planning System</span>
    <span class="panel-agent-showcase__tag">ADO Orchestrator</span>
    <span class="panel-agent-showcase__tag">Execution Orchestrator</span>
  </div>
</div>`,
        css: `/* Tokens used: */
--glass-bg-base
--glass-bg-card
--glass-bg-hover
--glass-blur-md
--glass-blur-sm
--glass-border-subtle
--glass-border-accent
--shadow-glass-md
--shadow-glass-hover
--glass-accent-cyan
--glass-accent-purple
--glass-text-primary
--glass-text-secondary
--glass-text-tertiary
--radius-lg
--radius-md
--radius-full
--space-xl
--space-lg
--space-md
--transition-glass`
    }
};

// State management
let currentPanel = 'tetris';
let currentTheme = 'dark';
let currentMode = 'desktop';
let currentCodeTab = 'html';

// DOM elements
const panelItems = document.querySelectorAll('.viewer-panel-item');
const previewTitle = document.getElementById('preview-title');
const previewContent = document.getElementById('preview-content');
const previewViewport = document.getElementById('preview-viewport');
const tokenCount = document.getElementById('token-count');
const panelType = document.getElementById('panel-type');
const codeHtml = document.querySelector('#code-html code');
const codeCss = document.querySelector('#code-css code');
const copyClassBtn = document.getElementById('copy-class-btn');
const copyCodeBtn = document.getElementById('copy-code-btn');
const themeToggle = document.getElementById('theme-toggle');
const responsiveBtns = document.querySelectorAll('.viewer-responsive-btn');
const codeTabs = document.querySelectorAll('.viewer-code-tab');
const codeBlocks = document.querySelectorAll('.viewer-code-block');
const toast = document.getElementById('toast-notification');

// Initialize
function init() {
    // Load initial panel
    loadPanel(currentPanel);
    
    // Setup event listeners
    setupPanelSelection();
    setupCodeTabs();
    setupCopyButtons();
    setupThemeToggle();
    setupResponsiveToggle();
}

// Setup panel selection
function setupPanelSelection() {
    panelItems.forEach(item => {
        item.addEventListener('click', () => {
            const panelId = item.dataset.panel;
            
            // Update active state
            panelItems.forEach(i => i.classList.remove('viewer-panel-item--active'));
            item.classList.add('viewer-panel-item--active');
            
            // Load panel
            loadPanel(panelId);
        });
    });
}

// Load panel
function loadPanel(panelId) {
    currentPanel = panelId;
    const data = PANEL_DATA[panelId];
    
    if (!data) return;
    
    // Update header
    previewTitle.textContent = data.name;
    tokenCount.textContent = data.tokens;
    panelType.textContent = data.type;
    
    // Update preview
    previewContent.innerHTML = data.html;
    
    // Update code blocks
    codeHtml.textContent = data.html;
    codeCss.textContent = data.css;
}

// Setup code tabs
function setupCodeTabs() {
    codeTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.dataset.tab;
            
            // Update active tab
            codeTabs.forEach(t => t.classList.remove('viewer-code-tab--active'));
            tab.classList.add('viewer-code-tab--active');
            
            // Update visible code block
            codeBlocks.forEach(block => {
                block.classList.remove('viewer-code-block--active');
            });
            document.getElementById(`code-${tabName}`).classList.add('viewer-code-block--active');
            
            currentCodeTab = tabName;
        });
    });
}

// Setup copy buttons
function setupCopyButtons() {
    // Copy class name
    copyClassBtn.addEventListener('click', () => {
        const className = `.${PANEL_DATA[currentPanel].name}`;
        copyToClipboard(className);
        showToast('Class name copied!');
    });
    
    // Copy code
    copyCodeBtn.addEventListener('click', () => {
        const code = currentCodeTab === 'html' ? 
            PANEL_DATA[currentPanel].html : 
            PANEL_DATA[currentPanel].css;
        copyToClipboard(code);
        showToast('Code copied!');
    });
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).catch(err => {
        console.error('Failed to copy:', err);
    });
}

// Show toast notification
function showToast(message) {
    const toastMessage = toast.querySelector('.viewer-toast__message');
    toastMessage.textContent = message;
    
    toast.style.display = 'flex';
    
    setTimeout(() => {
        toast.style.display = 'none';
    }, 2000);
}

// Setup theme toggle
function setupThemeToggle() {
    themeToggle.addEventListener('click', () => {
        currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.body.classList.toggle('light-theme');
    });
}

// Setup responsive toggle
function setupResponsiveToggle() {
    responsiveBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const mode = btn.dataset.mode;
            
            // Update active button
            responsiveBtns.forEach(b => b.classList.remove('viewer-responsive-btn--active'));
            btn.classList.add('viewer-responsive-btn--active');
            
            // Update viewport
            previewViewport.className = 'viewer-preview__viewport';
            if (mode !== 'desktop') {
                previewViewport.classList.add(`mode-${mode}`);
            }
            
            currentMode = mode;
        });
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);
