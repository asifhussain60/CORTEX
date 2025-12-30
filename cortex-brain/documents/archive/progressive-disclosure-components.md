# Progressive Disclosure Components

**Created:** December 28, 2025  
**Author:** Asif Hussain  
**Plan:** Knowledge Library Documentation & Learning Hub v2.0  
**Purpose:** Reusable UI patterns for complexity management

---

## 🎯 Overview

Progressive disclosure is a design pattern that sequences information and actions across multiple screens to reduce cognitive overload. The Knowledge Library implements 5 key patterns:

1. **Collapsible Accordions** - Expand/collapse content sections
2. **Tabbed Interfaces** - Organize related content into tabs
3. **Expandable Cards** - Show summary, expand for details
4. **Sticky Navigation** - Breadcrumbs and back buttons
5. **Lazy Loading** - Load content on demand

---

## 1️⃣ Collapsible Accordions

**Use Case:** Knowledge files list on Level 3 (Category Detail pages)

### HTML Structure

```html
<div class="knowledge-files-accordion">
    <div class="accordion-item">
        <button class="accordion-header" aria-expanded="false" aria-controls="react-content">
            <span class="accordion-icon">📄</span>
            <div class="accordion-title-group">
                <h3 class="accordion-title">React Best Practices</h3>
                <p class="accordion-subtitle">Component design, hooks, performance</p>
            </div>
            <span class="badge">25 rules</span>
            <svg class="accordion-chevron" aria-hidden="true">
                <use href="#chevron-down"></use>
            </svg>
        </button>
        
        <div id="react-content" class="accordion-content" hidden>
            <p>Component design, hooks, state management, performance optimization...</p>
            
            <h4>Featured Rules:</h4>
            <ul class="feature-list">
                <li>Use Function Components with Hooks</li>
                <li>Implement React.memo for Pure Components</li>
                <li>Always Specify Effect Dependencies</li>
            </ul>
            
            <a href="frontend/react-best-practices.html" class="btn-link">
                View Full Documentation →
            </a>
        </div>
    </div>
    
    <!-- More accordion items -->
</div>
```

### CSS Styling

```css
/* Accordion Container */
.knowledge-files-accordion {
    margin: var(--spacing-2xl) 0;
}

.accordion-item {
    margin-bottom: var(--spacing-md);
}

/* Accordion Header */
.accordion-header {
    width: 100%;
    padding: var(--spacing-md) var(--spacing-lg);
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    cursor: pointer;
    transition: all var(--transition-base);
    text-align: left;
}

.accordion-header:hover {
    background: rgba(26, 31, 58, 0.9);
    border-color: var(--accent-primary);
    transform: translateX(4px);
}

.accordion-header:focus {
    outline: 2px solid var(--accent-primary);
    outline-offset: 2px;
}

/* Icon */
.accordion-icon {
    font-size: 2rem;
    flex-shrink: 0;
}

/* Title Group */
.accordion-title-group {
    flex: 1;
}

.accordion-title {
    margin: 0;
    font-size: 1.125rem;
    color: var(--text-primary);
}

.accordion-subtitle {
    margin: 0.25rem 0 0 0;
    font-size: 0.875rem;
    color: var(--text-secondary);
}

/* Badge */
.badge {
    padding: 0.25rem 0.75rem;
    background: rgba(0, 212, 255, 0.2);
    color: var(--accent-primary);
    border-radius: var(--radius-sm);
    font-size: 0.875rem;
    font-weight: 600;
}

/* Chevron */
.accordion-chevron {
    width: 1.5rem;
    height: 1.5rem;
    color: var(--text-secondary);
    transition: transform var(--transition-base);
}

.accordion-header[aria-expanded="true"] .accordion-chevron {
    transform: rotate(180deg);
}

/* Accordion Content */
.accordion-content {
    padding: var(--spacing-lg);
    background: rgba(26, 31, 58, 0.5);
    border: 1px solid var(--glass-border);
    border-top: none;
    border-radius: 0 0 var(--radius-md) var(--radius-md);
    animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Mobile Optimizations */
@media (max-width: 767px) {
    .accordion-header {
        padding: var(--spacing-sm) var(--spacing-md);
        flex-wrap: wrap;
    }
    
    .accordion-title {
        font-size: 1rem;
    }
    
    .badge {
        order: -1;  /* Move badge to top */
        margin-bottom: 0.5rem;
    }
}
```

### JavaScript

```javascript
// Accordion Toggle
document.querySelectorAll('.accordion-header').forEach(header => {
    header.addEventListener('click', () => {
        const expanded = header.getAttribute('aria-expanded') === 'true';
        const contentId = header.getAttribute('aria-controls');
        const content = document.getElementById(contentId);
        
        // Toggle state
        header.setAttribute('aria-expanded', !expanded);
        
        if (expanded) {
            content.hidden = true;
        } else {
            content.hidden = false;
        }
    });
    
    // Keyboard accessibility
    header.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            header.click();
        }
    });
});
```

---

## 2️⃣ Tabbed Interfaces

**Use Case:** Category detail pages (Level 3) - Overview, Files, Resources, CORTEX Usage

### HTML Structure

```html
<div class="tabs-container">
    <div class="tabs-nav" role="tablist" aria-label="Category sections">
        <button class="tab-button active" 
                role="tab" 
                aria-selected="true" 
                aria-controls="overview-tab"
                id="overview-btn"
                data-tab="overview">
            Overview
        </button>
        <button class="tab-button" 
                role="tab" 
                aria-selected="false" 
                aria-controls="files-tab"
                id="files-btn"
                data-tab="files">
            Knowledge Files
        </button>
        <button class="tab-button" 
                role="tab" 
                aria-selected="false" 
                aria-controls="resources-tab"
                id="resources-btn"
                data-tab="resources">
            Learning Resources
        </button>
        <button class="tab-button" 
                role="tab" 
                aria-selected="false" 
                aria-controls="usage-tab"
                id="usage-btn"
                data-tab="usage">
            CORTEX Usage
        </button>
    </div>
    
    <div class="tab-content active" id="overview-tab" role="tabpanel" aria-labelledby="overview-btn">
        <!-- Overview content: description, Mermaid diagram, high-priority rules -->
    </div>
    
    <div class="tab-content" id="files-tab" role="tabpanel" aria-labelledby="files-btn" hidden>
        <!-- Accordion with knowledge files -->
    </div>
    
    <div class="tab-content" id="resources-tab" role="tabpanel" aria-labelledby="resources-btn" hidden>
        <!-- Learning resources links -->
    </div>
    
    <div class="tab-content" id="usage-tab" role="tabpanel" aria-labelledby="usage-btn" hidden>
        <!-- How CORTEX uses this knowledge -->
    </div>
</div>
```

### CSS Styling

```css
/* Tabs Container */
.tabs-container {
    margin: var(--spacing-2xl) 0;
}

/* Tabs Navigation */
.tabs-nav {
    display: flex;
    gap: 0.5rem;
    border-bottom: 2px solid var(--glass-border);
    margin-bottom: var(--spacing-xl);
    overflow-x: auto;  /* Mobile: horizontal scroll */
    -webkit-overflow-scrolling: touch;
}

/* Tab Button */
.tab-button {
    padding: 1rem 1.5rem;
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    color: var(--text-secondary);
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    white-space: nowrap;
    transition: all var(--transition-base);
    position: relative;
    bottom: -2px;  /* Align with bottom border */
}

.tab-button:hover {
    color: var(--text-primary);
    background: rgba(0, 212, 255, 0.1);
}

.tab-button.active {
    color: var(--accent-primary);
    border-bottom-color: var(--accent-primary);
}

.tab-button:focus {
    outline: 2px solid var(--accent-primary);
    outline-offset: 4px;
}

/* Tab Content */
.tab-content {
    animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Mobile Optimizations */
@media (max-width: 767px) {
    .tabs-nav {
        border-bottom: none;
        background: var(--glass-bg);
        border-radius: var(--radius-md);
        padding: 0.5rem;
    }
    
    .tab-button {
        padding: 0.75rem 1rem;
        font-size: 0.875rem;
        border-radius: var(--radius-sm);
    }
    
    .tab-button.active {
        background: var(--accent-primary);
        color: var(--bg-primary);
        border-bottom-color: transparent;
    }
}
```

### JavaScript

```javascript
// Tab Switching
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        const tabId = button.getAttribute('aria-controls');
        const tabsContainer = button.closest('.tabs-container');
        
        // Deactivate all tabs
        tabsContainer.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
            btn.setAttribute('aria-selected', 'false');
        });
        
        tabsContainer.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
            content.hidden = true;
        });
        
        // Activate clicked tab
        button.classList.add('active');
        button.setAttribute('aria-selected', 'true');
        
        const targetContent = document.getElementById(tabId);
        targetContent.classList.add('active');
        targetContent.hidden = false;
        
        // Update URL hash
        window.history.replaceState(null, '', `#${button.dataset.tab}`);
    });
});

// Keyboard navigation (Arrow keys)
document.querySelectorAll('.tabs-nav').forEach(nav => {
    const tabs = Array.from(nav.querySelectorAll('.tab-button'));
    
    nav.addEventListener('keydown', (e) => {
        const currentIndex = tabs.indexOf(document.activeElement);
        
        if (e.key === 'ArrowRight') {
            e.preventDefault();
            const nextIndex = (currentIndex + 1) % tabs.length;
            tabs[nextIndex].focus();
            tabs[nextIndex].click();
        }
        
        if (e.key === 'ArrowLeft') {
            e.preventDefault();
            const prevIndex = (currentIndex - 1 + tabs.length) % tabs.length;
            tabs[prevIndex].focus();
            tabs[prevIndex].click();
        }
    });
});

// Load tab from URL hash on page load
window.addEventListener('load', () => {
    const hash = window.location.hash.slice(1);  // Remove #
    if (hash) {
        const button = document.querySelector(`[data-tab="${hash}"]`);
        if (button) button.click();
    }
});
```

---

## 3️⃣ Expandable Cards

**Use Case:** Rules showcase on Level 3 (Category Detail pages)

### HTML Structure

```html
<div class="rules-showcase">
    <h2>High-Priority Rules</h2>
    
    <div class="rule-card" data-expandable>
        <div class="rule-header" onclick="toggleRule(this)">
            <span class="rule-icon">⚠️</span>
            <div class="rule-title-group">
                <h3>Use Function Components with Hooks</h3>
                <span class="severity-badge severity-high">HIGH</span>
            </div>
            <button class="expand-btn" aria-label="Expand rule">+</button>
        </div>
        
        <div class="rule-body" hidden>
            <p><strong>Description:</strong> Modern React uses function components with hooks instead of class components.</p>
            
            <div class="code-comparison">
                <div class="code-good">
                    <h4>✅ Good</h4>
                    <pre><code class="language-jsx">
function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>
    Count: {count}
  </button>;
}
                    </code></pre>
                </div>
                
                <div class="code-bad">
                    <h4>❌ Bad</h4>
                    <pre><code class="language-jsx">
class Counter extends React.Component {
  constructor(props) {
    super(props);
    this.state = { count: 0 };
  }
  render() {
    return <button>...</button>;
  }
}
                    </code></pre>
                </div>
            </div>
            
            <a href="frontend/react-best-practices.html#hooks" class="btn-link">
                View Full Rule →
            </a>
        </div>
    </div>
    
    <!-- More rule cards -->
</div>
```

### CSS Styling

```css
/* Rules Showcase */
.rules-showcase {
    margin: var(--spacing-2xl) 0;
}

/* Rule Card */
.rule-card {
    margin-bottom: var(--spacing-md);
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-md);
    transition: all var(--transition-base);
}

.rule-card:hover {
    border-color: var(--accent-primary);
}

/* Rule Header */
.rule-header {
    padding: var(--spacing-md);
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    cursor: pointer;
}

.rule-icon {
    font-size: 2rem;
    flex-shrink: 0;
}

.rule-title-group {
    flex: 1;
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}

.rule-title-group h3 {
    margin: 0;
    font-size: 1.125rem;
}

/* Severity Badges */
.severity-badge {
    padding: 0.25rem 0.5rem;
    border-radius: var(--radius-sm);
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
}

.severity-high {
    background: rgba(255, 23, 68, 0.2);
    color: #ff1744;
}

.severity-medium {
    background: rgba(255, 165, 0, 0.2);
    color: #ffa500;
}

.severity-low {
    background: rgba(0, 212, 255, 0.2);
    color: var(--accent-primary);
}

/* Expand Button */
.expand-btn {
    width: 2.5rem;
    height: 2.5rem;
    background: rgba(0, 212, 255, 0.1);
    border: 1px solid var(--accent-primary);
    border-radius: 50%;
    color: var(--accent-primary);
    font-size: 1.5rem;
    cursor: pointer;
    transition: all var(--transition-base);
}

.expand-btn:hover {
    background: var(--accent-primary);
    color: var(--bg-primary);
    transform: rotate(90deg);
}

.rule-card[data-expanded] .expand-btn {
    transform: rotate(45deg);
}

/* Rule Body */
.rule-body {
    padding: 0 var(--spacing-md) var(--spacing-md) var(--spacing-md);
    animation: slideDown 0.3s ease-out;
}

/* Code Comparison */
.code-comparison {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-md);
    margin: var(--spacing-md) 0;
}

.code-good,
.code-bad {
    background: rgba(0, 0, 0, 0.3);
    border-radius: var(--radius-sm);
    padding: var(--spacing-sm);
}

.code-good h4 {
    color: var(--success);
}

.code-bad h4 {
    color: #ff1744;
}

/* Mobile: Stack code blocks */
@media (max-width: 767px) {
    .code-comparison {
        grid-template-columns: 1fr;
    }
}
```

### JavaScript

```javascript
function toggleRule(header) {
    const card = header.closest('.rule-card');
    const body = card.querySelector('.rule-body');
    const btn = header.querySelector('.expand-btn');
    
    const isExpanded = card.hasAttribute('data-expanded');
    
    if (isExpanded) {
        card.removeAttribute('data-expanded');
        body.hidden = true;
        btn.textContent = '+';
        btn.setAttribute('aria-label', 'Expand rule');
    } else {
        card.setAttribute('data-expanded', '');
        body.hidden = false;
        btn.textContent = '−';
        btn.setAttribute('aria-label', 'Collapse rule');
    }
}
```

---

## 4️⃣ Sticky Navigation

**Use Case:** All pages for consistent navigation

### HTML Structure

```html
<nav class="breadcrumb-container sticky-nav" aria-label="Breadcrumb">
    <button class="back-button" onclick="history.back()" aria-label="Go back">
        ← Back
    </button>
    
    <ol class="breadcrumb">
        <li><a href="../index.html">Home</a></li>
        <li><a href="index.html">Knowledge Library</a></li>
        <li><a href="index.html#frontend-ui">Frontend & UI</a></li>
        <li aria-current="page">Frontend</li>
    </ol>
</nav>
```

### CSS Styling

```css
/* Sticky Nav Container */
.sticky-nav {
    position: sticky;
    top: 0;
    z-index: 100;
    background: rgba(10, 14, 39, 0.95);
    backdrop-filter: blur(10px);
    padding: var(--spacing-md) var(--spacing-lg);
    border-bottom: 1px solid var(--glass-border);
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
}

/* Back Button */
.back-button {
    padding: 0.5rem 1rem;
    background: rgba(0, 212, 255, 0.1);
    border: 1px solid var(--accent-primary);
    border-radius: var(--radius-sm);
    color: var(--accent-primary);
    font-size: 0.875rem;
    cursor: pointer;
    transition: all var(--transition-base);
}

.back-button:hover {
    background: var(--accent-primary);
    color: var(--bg-primary);
}

/* Breadcrumb */
.breadcrumb {
    display: flex;
    list-style: none;
    padding: 0;
    margin: 0;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.breadcrumb li {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.breadcrumb li:not(:last-child)::after {
    content: "›";
    color: var(--text-secondary);
}

.breadcrumb a {
    color: var(--accent-primary);
    text-decoration: none;
    transition: color var(--transition-base);
}

.breadcrumb a:hover {
    text-decoration: underline;
}

.breadcrumb li[aria-current="page"] {
    color: var(--text-primary);
}

/* Mobile: Hide back button on desktop */
@media (min-width: 1024px) {
    .back-button {
        display: none;
    }
}

/* Mobile: Truncate breadcrumb */
@media (max-width: 767px) {
    .breadcrumb {
        font-size: 0.875rem;
    }
    
    .breadcrumb li:not(:first-child):not(:last-child) {
        display: none;  /* Hide middle items */
    }
}
```

---

## 5️⃣ Lazy Loading

**Use Case:** D3 diagrams, Mermaid, heavy content

### HTML Structure

```html
<div class="lazy-container" data-lazy-load="d3-diagram">
    <!-- Skeleton while loading -->
    <div class="skeleton-loader">
        <div class="skeleton-pulse"></div>
        <p>Loading diagram...</p>
    </div>
    
    <!-- Actual content (hidden initially) -->
    <div class="lazy-content" hidden>
        <svg id="d3-diagram"></svg>
    </div>
</div>
```

### CSS Styling

```css
/* Skeleton Loader */
.skeleton-loader {
    padding: 3rem;
    text-align: center;
}

.skeleton-pulse {
    width: 100%;
    height: 400px;
    background: linear-gradient(
        90deg,
        rgba(255, 255, 255, 0.05) 0%,
        rgba(255, 255, 255, 0.1) 50%,
        rgba(255, 255, 255, 0.05) 100%
    );
    background-size: 200% 100%;
    animation: pulse 1.5s infinite;
    border-radius: var(--radius-md);
}

@keyframes pulse {
    0% {
        background-position: 200% 0;
    }
    100% {
        background-position: -200% 0;
    }
}
```

### JavaScript

```javascript
// Intersection Observer for lazy loading
const lazyObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const container = entry.target;
            const type = container.dataset.lazyLoad;
            
            // Load content based on type
            if (type === 'd3-diagram') {
                loadD3Diagram(container);
            } else if (type === 'mermaid') {
                loadMermaidDiagram(container);
            }
            
            // Unobserve after loading
            lazyObserver.unobserve(container);
        }
    });
}, {
    rootMargin: '100px'  // Load 100px before entering viewport
});

// Observe all lazy containers
document.querySelectorAll('[data-lazy-load]').forEach(el => {
    lazyObserver.observe(el);
});

function loadD3Diagram(container) {
    // Hide skeleton
    container.querySelector('.skeleton-loader').hidden = true;
    
    // Show content
    const content = container.querySelector('.lazy-content');
    content.hidden = false;
    
    // Initialize D3
    // ... D3 code ...
}
```

---

## ✅ Component Checklist

**Accordions:**
- [ ] ARIA attributes (aria-expanded, aria-controls)
- [ ] Keyboard accessible (Enter, Space)
- [ ] Smooth animations
- [ ] Mobile-optimized

**Tabs:**
- [ ] ARIA attributes (role="tab", aria-selected)
- [ ] Keyboard navigation (Arrow keys)
- [ ] URL hash support
- [ ] Mobile scroll

**Expandable Cards:**
- [ ] Click to expand
- [ ] Animated transitions
- [ ] Severity badges color-coded
- [ ] Good/bad code comparison

**Sticky Navigation:**
- [ ] Breadcrumbs on all pages
- [ ] Back button (mobile only)
- [ ] Deep linking support
- [ ] Responsive truncation

**Lazy Loading:**
- [ ] Intersection Observer
- [ ] Skeleton loaders
- [ ] Progressive enhancement
- [ ] Error handling

---

**Status:** COMPONENTS DEFINED - Ready for implementation

---

**Copyright © 2025 Asif Hussain. All rights reserved.**
