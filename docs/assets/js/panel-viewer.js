/**
 * CORTEX Panel Viewer - Enhanced with Token Renaming
 * Real-time panel rendering and token renaming for CORTEX integration
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
    <span class="panel-compact-cards__icon">⚡</span>
    <h3 class="panel-compact-cards__title">Real-Time Analysis</h3>
    <p class="panel-compact-cards__description">Live AST parsing</p>
  </div>
  <div class="panel-compact-cards__card">
    <span class="panel-compact-cards__icon">📐</span>
    <h3 class="panel-compact-cards__title">Pattern Detection</h3>
    <p class="panel-compact-cards__description">Architecture insights</p>
  </div>
  <div class="panel-compact-cards__card">
    <span class="panel-compact-cards__icon">🔗</span>
    <h3 class="panel-compact-cards__title">Dependency Graph</h3>
    <p class="panel-compact-cards__description">Module relationships</p>
  </div>
  <div class="panel-compact-cards__card">
    <span class="panel-compact-cards__icon">📊</span>
    <h3 class="panel-compact-cards__title">Metrics Dashboard</h3>
    <p class="panel-compact-cards__description">Code health scoring</p>
  </div>
  <div class="panel-compact-cards__card">
    <span class="panel-compact-cards__icon">🧪</span>
    <h3 class="panel-compact-cards__title">Test Coverage</h3>
    <p class="panel-compact-cards__description">Quality reporting</p>
  </div>
</div>`,
        css: `/* Tokens used: */
--glass-bg-card
--glass-bg-hover
--glass-blur-sm
--glass-border-subtle
--radius-md
--shadow-glass-sm
--shadow-glass-hover
--space-md
--transition-glass`
    },
    'grid-cards': {
        name: 'panel-grid-cards',
        type: 'Layout',
        tokens: 11,
        html: `<div class="panel-grid-cards">
  <article class="panel-grid-cards__card">
    <span class="panel-grid-cards__badge">Core</span>
    <h3 class="panel-grid-cards__title">Code Analysis Engine</h3>
    <p class="panel-grid-cards__description">
      AST parsing, pattern detection, and architectural insight extraction
    </p>
    <div class="panel-grid-cards__footer">
      <span class="panel-grid-cards__tag">Python</span>
      <span class="panel-grid-cards__tag">TypeScript</span>
    </div>
  </article>
  
  <article class="panel-grid-cards__card">
    <span class="panel-grid-cards__badge panel-grid-cards__badge--accent">New</span>
    <h3 class="panel-grid-cards__title">Visualization Layer</h3>
    <p class="panel-grid-cards__description">
      Interactive dependency graphs and architecture diagrams
    </p>
    <div class="panel-grid-cards__footer">
      <span class="panel-grid-cards__tag">D3.js</span>
      <span class="panel-grid-cards__tag">Canvas</span>
    </div>
  </article>
  
  <article class="panel-grid-cards__card">
    <span class="panel-grid-cards__badge">Beta</span>
    <h3 class="panel-grid-cards__title">AI Code Review</h3>
    <p class="panel-grid-cards__description">
      Automated code quality checks and improvement suggestions
    </p>
    <div class="panel-grid-cards__footer">
      <span class="panel-grid-cards__tag">GPT-4</span>
      <span class="panel-grid-cards__tag">Claude</span>
    </div>
  </article>
</div>`,
        css: `/* Tokens used: */
--glass-bg-card
--glass-bg-hover
--glass-blur-md
--glass-border-subtle
--glass-border-accent
--radius-lg
--shadow-glass-md
--shadow-glass-hover
--space-lg
--glass-accent-cyan
--glass-accent-purple
--transition-glass`
    },
    'hero-glass': {
        name: 'panel-hero-glass',
        type: 'Hero',
        tokens: 12,
        html: `<section class="panel-hero-glass">
  <div class="panel-hero-glass__content">
    <h1 class="panel-hero-glass__title">Unlock Your Codebase Intelligence</h1>
    <p class="panel-hero-glass__subtitle">
      CORTEX Lens transforms complex code into actionable insights. 
      Understand architecture, detect patterns, and optimize with confidence.
    </p>
    <div class="panel-hero-glass__cta-group">
      <a href="#" class="panel-hero-glass__cta panel-hero-glass__cta--primary">
        Start Free Trial
      </a>
      <a href="#" class="panel-hero-glass__cta panel-hero-glass__cta--secondary">
        Watch Demo
      </a>
    </div>
  </div>
</section>`,
        css: `/* Tokens used: */
--glass-bg-gradient-hero
--glass-blur-xl
--glass-border-gradient-neon
--radius-2xl
--shadow-hero
--shadow-glass-lg
--space-3xl
--space-xl
--glass-accent-gradient
--glass-text-hero
--transition-glass
--transition-morph`
    },
    'sidebar-glass': {
        name: 'panel-sidebar-glass',
        type: 'Navigation',
        tokens: 9,
        html: `<aside class="panel-sidebar-glass">
  <nav class="panel-sidebar-glass__nav">
    <a href="#" class="panel-sidebar-glass__link panel-sidebar-glass__link--active">
      <span class="panel-sidebar-glass__icon">🏠</span>
      Dashboard
    </a>
    <a href="#" class="panel-sidebar-glass__link">
      <span class="panel-sidebar-glass__icon">📊</span>
      Analytics
    </a>
    <a href="#" class="panel-sidebar-glass__link">
      <span class="panel-sidebar-glass__icon">🔍</span>
      Search
    </a>
    <a href="#" class="panel-sidebar-glass__link">
      <span class="panel-sidebar-glass__icon">⚙️</span>
      Settings
    </a>
  </nav>
</aside>`,
        css: `/* Tokens used: */
--glass-bg-sidebar
--glass-blur-md
--glass-border-subtle
--shadow-glass-sm
--space-md
--glass-bg-nav-active
--glass-bg-nav-hover
--radius-md
--transition-glass`
    },
    'modal-glass': {
        name: 'panel-modal-glass',
        type: 'Overlay',
        tokens: 10,
        html: `<div class="panel-modal-glass">
  <div class="panel-modal-glass__header">
    <h3 class="panel-modal-glass__title">Confirm Action</h3>
    <button class="panel-modal-glass__close">×</button>
  </div>
  <div class="panel-modal-glass__body">
    <p>Are you sure you want to proceed with this action? This cannot be undone.</p>
  </div>
  <div class="panel-modal-glass__footer">
    <button class="panel-modal-glass__btn panel-modal-glass__btn--secondary">Cancel</button>
    <button class="panel-modal-glass__btn panel-modal-glass__btn--primary">Confirm</button>
  </div>
</div>`,
        css: `/* Tokens used: */
--glass-bg-modal
--glass-blur-xl
--glass-border-subtle
--glass-border-accent
--radius-lg
--shadow-modal
--space-lg
--glass-bg-button
--glass-bg-button-hover
--transition-glass`
    },
    'toast-glass': {
        name: 'panel-toast-glass',
        type: 'Notification',
        tokens: 7,
        html: `<div class="panel-toast-glass panel-toast-glass--success">
  <span class="panel-toast-glass__icon">✅</span>
  <span class="panel-toast-glass__message">Action completed successfully!</span>
</div>

<div class="panel-toast-glass panel-toast-glass--error">
  <span class="panel-toast-glass__icon">❌</span>
  <span class="panel-toast-glass__message">An error occurred. Please try again.</span>
</div>

<div class="panel-toast-glass panel-toast-glass--warning">
  <span class="panel-toast-glass__icon">⚠️</span>
  <span class="panel-toast-glass__message">Warning: Action requires confirmation.</span>
</div>

<div class="panel-toast-glass panel-toast-glass--info">
  <span class="panel-toast-glass__icon">ℹ️</span>
  <span class="panel-toast-glass__message">New update available.</span>
</div>`,
        css: `/* Tokens used: */
--glass-bg-toast
--glass-blur-md
--glass-border-subtle
--radius-md
--shadow-glass-md
--space-sm
--transition-glass`
    },
    'blob-glass': {
        name: 'panel-blob-glass',
        type: 'Decorative',
        tokens: 8,
        html: `<div class="panel-blob-container">
  <div class="panel-blob-glass panel-blob-glass--lg panel-blob-glass--purple" 
       style="top: 10%; left: 10%; animation-delay: 0s;"></div>
  <div class="panel-blob-glass panel-blob-glass--md panel-blob-glass--cyan" 
       style="top: 50%; right: 20%; animation-delay: 2s;"></div>
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
let panelRenames = {}; // Changed from tokenRenames
let editMode = false; // Track if we're in edit mode

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

// Edit mode elements
const renameToggleBtn = document.getElementById('rename-toggle-btn');
const renameBanner = document.getElementById('rename-mode-banner');
const generatePromptFloating = document.getElementById('generate-prompt-floating');
const overlay = document.getElementById('overlay');
const promptOutput = document.getElementById('prompt-output');
const promptContent = document.getElementById('prompt-content');
const promptClose = document.getElementById('prompt-close');
const copyPromptBtn = document.getElementById('copy-prompt-btn');

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
    setupEditMode();
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

// Setup edit mode for inline panel renaming
function setupEditMode() {
    // Toggle edit mode
    renameToggleBtn.addEventListener('click', () => {
        editMode = !editMode;
        
        if (editMode) {
            enableEditMode();
        } else {
            disableEditMode();
        }
    });
    
    // Generate prompt button
    generatePromptFloating.addEventListener('click', generateRenamePrompt);
    
    // Close prompt output
    promptClose.addEventListener('click', () => {
        promptOutput.classList.remove('active');
        overlay.classList.remove('active');
    });
    
    // Copy prompt
    copyPromptBtn.addEventListener('click', () => {
        copyToClipboard(promptContent.textContent);
        showToast('Prompt copied to clipboard!');
    });
    
    // Close on overlay click
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            promptOutput.classList.remove('active');
            overlay.classList.remove('active');
        }
    });
}

// Enable edit mode
function enableEditMode() {
    renameBanner.style.display = 'block';
    renameToggleBtn.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
    renameToggleBtn.textContent = '✅';
    
    // Make all panel names editable
    document.querySelectorAll('.viewer-panel-item').forEach((item, index) => {
        const nameElement = item.querySelector('.viewer-panel-item__name');
        const classElement = item.querySelector('.viewer-panel-item__class');
        const panelId = item.dataset.panel;
        const panelData = PANEL_DATA[panelId];
        
        if (nameElement && classElement && panelData) {
            const currentClassName = panelData.name;
            const displayName = nameElement.textContent.trim();
            
            // Create input field
            const input = document.createElement('input');
            input.type = 'text';
            input.value = displayName;
            input.dataset.original = currentClassName;
            input.dataset.originalDisplay = displayName;
            input.style.cssText = `
                width: 100%;
                background: rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(99, 179, 237, 0.5);
                border-radius: 4px;
                padding: 0.25rem 0.5rem;
                color: #fff;
                font-family: 'Inter', sans-serif;
                font-size: 0.9375rem;
                font-weight: 600;
            `;
            
            input.addEventListener('input', (e) => {
                const original = e.target.dataset.original;
                const newValue = e.target.value.trim();
                const newClassName = newValue ? `panel-${newValue.toLowerCase().replace(/\s+/g, '-')}` : '';
                
                if (newClassName && newClassName !== original) {
                    panelRenames[original] = newClassName;
                    // Update the class name display
                    classElement.textContent = newClassName;
                } else {
                    delete panelRenames[original];
                    // Restore original class name
                    classElement.textContent = original;
                }
                
                // Show/hide generate button
                updateGenerateButton();
            });
            
            // Replace text with input
            nameElement.textContent = '';
            nameElement.appendChild(input);
        }
    });
}

// Disable edit mode
function disableEditMode() {
    renameBanner.style.display = 'none';
    renameToggleBtn.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    renameToggleBtn.textContent = '✏️';
    generatePromptFloating.style.display = 'none';
    
    // Restore panel names
    document.querySelectorAll('.viewer-panel-item').forEach(item => {
        const nameElement = item.querySelector('.viewer-panel-item__name');
        const classElement = item.querySelector('.viewer-panel-item__class');
        const panelId = item.dataset.panel;
        const panelData = PANEL_DATA[panelId];
        
        if (nameElement && panelData) {
            const input = nameElement.querySelector('input');
            if (input) {
                const displayName = input.dataset.originalDisplay || panelData.name.replace('panel-', '').replace(/-/g, ' ');
                nameElement.textContent = displayName;
            }
        }
        
        // Restore original class name if it was changed
        if (classElement && panelData) {
            classElement.textContent = panelData.name;
        }
    });
    
    // Clear renames if user cancels
    if (Object.keys(panelRenames).length === 0) {
        panelRenames = {};
    }
}

// Update generate button visibility
function updateGenerateButton() {
    if (Object.keys(panelRenames).length > 0) {
        generatePromptFloating.style.display = 'block';
    } else {
        generatePromptFloating.style.display = 'none';
    }
}

// Generate rename prompt
function generateRenamePrompt() {
    if (Object.keys(panelRenames).length === 0) {
        showToast('No panel renames specified');
        return;
    }
    
    let prompt = `🏷️ CORTEX Panel Class Rename Request

Please rename the following glassmorphism panel CSS classes across the entire codebase:

## Panel Class Renames

`;
    
    Object.entries(panelRenames).forEach(([oldClass, newClass]) => {
        prompt += `\`${oldClass}\` → \`${newClass}\`\n`;
    });
    
    prompt += `
## Instructions

1. **Search HTML files** for class references:
   - \`class="${oldClass}"\`
   - Update to new class names

2. **Search CSS files** for class definitions:
   - \`.${oldClass}\` selectors
   - \`.${oldClass}__*\` BEM child elements
   - \`.${oldClass}--*\` BEM modifiers
   - Update all to new class names

3. **Search JavaScript files** for class references:
   - String literals with old class names
   - PANEL_DATA entries
   - Update all references

## Files to Check

- \`docs/**/*.html\` (HTML class attributes)
- \`docs/assets/css/glass-named-panels.css\` (Panel definitions)
- \`docs/assets/css/*.css\` (Any additional references)
- \`docs/assets/js/panel-viewer.js\` (PANEL_DATA object)
- \`docs/design-system/**/*.html\` (Design system docs)

## Validation

After renaming:
- Verify no broken class references remain
- Check browser console for missing styles
- Test panel viewer functionality

Please confirm the changes and provide a summary of files modified.`;
    
    promptContent.textContent = prompt;
    promptOutput.classList.add('active');
    overlay.classList.add('active');
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);
