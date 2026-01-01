# 🎨 Glassmorphism Design Standard

**Version:** 3.2.0 | **Status:** ✅ PRODUCTION  
**Author:** Asif Hussain | **Last Updated:** December 31, 2025  
**Copyright © 2025 Asif Hussain. All rights reserved.**

---

## 📋 Purpose

This standard defines **modern glassmorphism patterns** for CORTEX documentation and UI components, incorporating **cutting-edge 2025 design techniques** including multi-layer depth, dynamic lighting, micro-interactions, and performance optimization.

**Target:** HTML documentation, dashboards, STS showcases, interactive visualizations  
**Compatibility:** Chrome 90+, Firefox 88+, Safari 14+, Edge 90+

---

## 🎯 Core Principles

1. **Multi-Layer Depth** - Stacked glass layers with varying opacity
2. **Dynamic Lighting** - Simulated light sources for realism
3. **Smooth Interactions** - Micro-animations with cubic-bezier easing
4. **GPU Acceleration** - Hardware-accelerated transforms
5. **Performance First** - Conditional blur, lazy loading
6. **Accessibility** - WCAG 2.1 AA compliance, reduced-motion support
7. **Subtle by Default** - T1 animations for all standard pages (v3.2.0)

---

## 🎬 Animation Tier System (NEW v3.2.0)

### ⛔ CRITICAL: Subtle Animations by Default

All documentation pages use **T1 (Subtle)** animations. Dramatic animations are reserved for hero sections only.

### Animation Tiers

| Tier | Name | Use Case | Duration | Effects |
|------|------|----------|----------|---------|
| **T1** | Subtle | All standard pages, documentation, feature pages | 0.2-0.3s | Opacity, light transforms, simple transitions |
| **T2** | Accent | Interactive elements requiring user feedback | 0.1-0.2s | Button press, form focus, selection highlight |
| **T3** | Dramatic | HERO sections, landing pages ONLY | 2-10s | borderGlowSweep, blobMorph, particle effects |

### T1: Subtle Animations (DEFAULT)

**✅ REQUIRED for all Level 1, Level 2, and Level 3 pages**

```css
/* T1 Subtle Hover - APPROVED DEFAULT */
.glass-card-subtle {
    transition: transform 0.2s ease, opacity 0.2s ease, box-shadow 0.2s ease;
}

.glass-card-subtle:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

/* T1 Subtle Focus - APPROVED */
.interactive-element:focus {
    outline: 2px solid var(--accent-primary);
    outline-offset: 2px;
    transition: outline-color 0.2s ease;
}

/* T1 Subtle Nav Link - APPROVED */
.nav-link {
    transition: color 0.2s ease, background-color 0.2s ease;
}
```

**T1 Properties:**
- `transition-duration: 0.2s - 0.3s`
- `transform: translateY(-2px to -4px)` maximum
- No infinite animations
- No keyframe animations on cards
- No glow pulses or sweeps
- No filter effects

### T2: Accent Animations (Interactive Feedback)

**✅ APPROVED for buttons, forms, tabs**

```css
/* T2 Button Feedback - APPROVED */
.btn-glass:active {
    transform: scale(0.98);
    transition: transform 0.1s ease;
}

/* T2 Form Focus - APPROVED */
input:focus {
    border-color: var(--accent-primary);
    box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.2);
    transition: all 0.2s ease;
}

/* T2 Tab Selection - APPROVED */
.tab-active {
    border-bottom: 2px solid var(--accent-primary);
    transition: border-color 0.2s ease;
}
```

### T3: Dramatic Animations (RESTRICTED)

**⛔ ONLY ALLOWED ON:**
- `docs/index.html` (Home page hero section)
- Landing page hero sections
- Explicitly marked showcase pages

**❌ FORBIDDEN ON:**
- Level 2 feature pages
- Documentation content pages
- Architecture visualization pages
- Orchestrator detail pages
- Any page with primary content focus

```css
/* T3 Dramatic - HERO SECTIONS ONLY */
@keyframes borderGlowSweep {
    0%, 100% { background-position: -200% 0; }
    50% { background-position: 200% 0; }
}

@keyframes blobMorph {
    0%, 100% { border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%; }
    50% { border-radius: 30% 60% 70% 40% / 50% 60% 30% 60%; }
}

@keyframes lightLeakPrimary {
    0% { transform: translate(-50%, -50%) scale(1); opacity: 0.3; }
    100% { transform: translate(-30%, -30%) scale(1.2); opacity: 0.5; }
}

@keyframes glowPulse {
    0%, 100% { box-shadow: 0 0 20px rgba(0, 212, 255, 0.3); }
    50% { box-shadow: 0 0 40px rgba(0, 212, 255, 0.6); }
}
```

### Animation Tier Quick Reference

| Animation | Tier | Allowed Pages |
|-----------|------|---------------|
| `transition: transform 0.2s` | T1 | ✅ All pages |
| `transition: opacity 0.2s` | T1 | ✅ All pages |
| `transform: translateY(-2px)` | T1 | ✅ All pages |
| `transform: scale(0.98)` | T2 | ✅ Buttons only |
| `outline` focus states | T2 | ✅ All interactive elements |
| `borderGlowSweep` | T3 | ⛔ Hero only |
| `blobMorph` | T3 | ⛔ Hero only |
| `lightLeakPrimary` | T3 | ⛔ Hero only |
| `glowPulse` | T3 | ⛔ Hero only |
| Infinite animations | T3 | ⛔ Hero only |
| SVG filter glow effects | T3 | ⛔ Hero only |

### Migration from T3 to T1

When simplifying dramatic animations:

```css
/* ❌ BEFORE (T3 Dramatic) */
.glass-card::after {
    animation: borderGlowSweep 2s ease-in-out infinite;
}

.glass-card:hover {
    transform: translateY(-4px) scale(1.01);
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5),
                0 0 0 1px rgba(0, 212, 255, 0.5);
}

/* ✅ AFTER (T1 Subtle) */
.glass-card {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.glass-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}
/* Remove ::after with borderGlowSweep entirely */
```

---

## 🏗️ Pattern Library

### Pattern 1: Multi-Layer Glass Card (PRIMARY)

**Use Case:** Default card pattern for all content containers

**Implementation:**
```css
.glass-card {
    /* Layer 1: Frosted background with gradient */
    position: relative;
    background: linear-gradient(
        135deg,
        rgba(26, 31, 58, 0.7) 0%,
        rgba(26, 31, 58, 0.4) 100%
    );
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    
    /* Gradient border */
    border: 1px solid;
    border-image: linear-gradient(
        135deg,
        rgba(255, 255, 255, 0.3),
        rgba(255, 255, 255, 0.05)
    ) 1;
    
    /* Depth shadows */
    box-shadow: 
        0 8px 32px rgba(0, 0, 0, 0.37),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);
    
    border-radius: 16px;
    padding: var(--space-lg);
    
    /* GPU acceleration */
    transform: translateZ(0);
    will-change: transform, opacity;
    backface-visibility: hidden;
    
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Layer 2: Inner glow (light source simulation) */
.glass-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 40%;
    background: linear-gradient(
        180deg,
        rgba(255, 255, 255, 0.15) 0%,
        transparent 100%
    );
    border-radius: inherit;
    pointer-events: none;
}

/* Layer 3: Hover depth effect */
.glass-card:hover {
    backdrop-filter: blur(25px) saturate(200%);
    transform: translateY(-4px) scale(1.01);
    box-shadow: 
        0 16px 48px rgba(0, 0, 0, 0.5),
        inset 0 2px 0 rgba(255, 255, 255, 0.3),
        0 0 0 1px rgba(0, 212, 255, 0.5);
}

/* Layer 4: Animated border glow */
.glass-card::after {
    content: '';
    position: absolute;
    inset: -2px;
    background: linear-gradient(
        45deg,
        transparent 30%,
        rgba(0, 212, 255, 0.3) 50%,
        transparent 70%
    );
    background-size: 200% 200%;
    border-radius: inherit;
    opacity: 0;
    transition: opacity 0.4s ease;
    pointer-events: none;
    z-index: -1;
}

.glass-card:hover::after {
    opacity: 1;
    animation: borderGlowSweep 2s ease-in-out infinite;
}

@keyframes borderGlowSweep {
    0%, 100% { background-position: -200% 0; }
    50% { background-position: 200% 0; }
}
```

**HTML Structure:**
```html
<div class="glass-card">
    <h2>Card Title</h2>
    <p>Content goes here...</p>
</div>
```

**Variables Used:**
- `--space-lg`: 2rem (32px)
- `--accent-primary`: #00d4ff (cyan)

---

### Pattern 2: Neuglass Card (Neumorphism + Glass)

**Use Case:** Dashboard widgets, settings panels, interactive controls

**Implementation:**
```css
.neuglass-card {
    background: linear-gradient(
        145deg,
        rgba(26, 31, 58, 0.8) 0%,
        rgba(16, 20, 40, 0.9) 100%
    );
    backdrop-filter: blur(15px) saturate(150%);
    border-radius: 24px;
    padding: var(--space-lg);
    
    /* Soft neumorphic shadows */
    box-shadow: 
        12px 12px 24px rgba(0, 0, 0, 0.6),
        -12px -12px 24px rgba(255, 255, 255, 0.05),
        inset 2px 2px 4px rgba(255, 255, 255, 0.1),
        inset -2px -2px 4px rgba(0, 0, 0, 0.3);
    
    border: 1px solid rgba(255, 255, 255, 0.08);
    transition: all 0.3s ease;
}

.neuglass-card:hover {
    box-shadow: 
        6px 6px 12px rgba(0, 0, 0, 0.7),
        -6px -6px 12px rgba(255, 255, 255, 0.03),
        inset 4px 4px 8px rgba(0, 0, 0, 0.4),
        inset -2px -2px 4px rgba(255, 255, 255, 0.1);
    transform: translateY(2px);
}
```

---

### Pattern 3: Morphing Glass Card

**Use Case:** Expandable content, detail views, interactive showcases

**Implementation:**
```css
.morph-card {
    background: var(--glass-bg);
    backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: var(--space-lg);
    cursor: pointer;
    transition: 
        border-radius 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55),
        transform 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55),
        box-shadow 0.6s ease;
}

.morph-card:hover {
    border-radius: 50px;
    transform: scale(1.05);
    box-shadow: 
        0 20px 60px rgba(0, 0, 0, 0.5),
        0 0 40px rgba(0, 212, 255, 0.3);
}

.morph-card.expanded {
    position: fixed;
    inset: 20px;
    border-radius: 0;
    transform: scale(1);
    z-index: 9999;
    animation: morphToFullscreen 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes morphToFullscreen {
    0% {
        border-radius: 50px;
        transform: scale(1.05);
    }
    100% {
        border-radius: 0;
        transform: scale(1);
    }
}
```

**JavaScript Toggle:**
```javascript
document.querySelectorAll('.morph-card').forEach(card => {
    card.addEventListener('click', () => {
        card.classList.toggle('expanded');
    });
});
```

---

### Pattern 4: Light Leak Glass

**Use Case:** Hero sections, feature highlights, ambient backgrounds

**Implementation:**
```css
.light-leak-glass {
    position: relative;
    background: rgba(26, 31, 58, 0.7);
    backdrop-filter: blur(15px);
    overflow: hidden;
    border-radius: 16px;
    padding: var(--space-xl);
}

/* Light source top-left (cyan) */
.light-leak-glass::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(
        circle at 30% 30%,
        rgba(0, 212, 255, 0.3) 0%,
        transparent 50%
    );
    pointer-events: none;
    mix-blend-mode: overlay;
    animation: lightLeakPrimary 8s ease-in-out infinite alternate;
}

@keyframes lightLeakPrimary {
    0% {
        transform: translate(0, 0);
        opacity: 0.5;
    }
    100% {
        transform: translate(10%, 10%);
        opacity: 0.8;
    }
}

/* Light source bottom-right (purple) */
.light-leak-glass::after {
    content: '';
    position: absolute;
    bottom: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(
        circle at 70% 70%,
        rgba(123, 97, 255, 0.2) 0%,
        transparent 50%
    );
    pointer-events: none;
    mix-blend-mode: overlay;
    animation: lightLeakSecondary 8s ease-in-out infinite alternate-reverse;
}

@keyframes lightLeakSecondary {
    0% {
        transform: translate(0, 0);
        opacity: 0.4;
    }
    100% {
        transform: translate(-10%, -10%);
        opacity: 0.7;
    }
}
```

---

### Pattern 5: Liquid Blob Glass

**Use Case:** Decorative elements, hero backgrounds, feature showcases

**Implementation:**
```css
.liquid-blob {
    background: linear-gradient(
        135deg,
        rgba(0, 212, 255, 0.3) 0%,
        rgba(123, 97, 255, 0.3) 100%
    );
    backdrop-filter: blur(40px) saturate(200%);
    border-radius: 40% 60% 60% 40% / 60% 40% 60% 40%;
    padding: 3rem;
    box-shadow: 
        0 20px 60px rgba(0, 0, 0, 0.4),
        inset 0 0 40px rgba(255, 255, 255, 0.1);
    animation: blobMorph 10s ease-in-out infinite;
    will-change: border-radius;
}

@keyframes blobMorph {
    0%, 100% {
        border-radius: 40% 60% 60% 40% / 60% 40% 60% 40%;
    }
    25% {
        border-radius: 60% 40% 40% 60% / 40% 60% 40% 60%;
    }
    50% {
        border-radius: 50% 50% 50% 50% / 50% 50% 50% 50%;
    }
    75% {
        border-radius: 40% 60% 40% 60% / 60% 40% 60% 40%;
    }
}

.liquid-blob:hover {
    border-radius: 30% 70% 70% 30% / 70% 30% 70% 30%;
    animation-play-state: paused;
}
```

---

## 🎨 UI Component Patterns

### Modal/Dialog
```css
.glass-modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(10, 14, 39, 0.8);
    backdrop-filter: blur(20px) saturate(180%);
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: fadeIn 0.3s ease;
}

.glass-modal {
    background: rgba(26, 31, 58, 0.9);
    backdrop-filter: blur(30px);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 24px;
    padding: 3rem;
    max-width: 600px;
    width: 90%;
    box-shadow: 
        0 30px 80px rgba(0, 0, 0, 0.6),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);
    animation: modalSlideUp 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes modalSlideUp {
    from {
        opacity: 0;
        transform: translateY(50px) scale(0.9);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}
```

### Toast Notification
```css
.glass-toast {
    position: fixed;
    top: 20px;
    right: 20px;
    background: rgba(26, 31, 58, 0.95);
    backdrop-filter: blur(20px);
    border-left: 4px solid var(--accent-primary);
    border-radius: 12px;
    padding: 1rem 1.5rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    animation: toastSlideIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    z-index: 10000;
}

@keyframes toastSlideIn {
    from {
        transform: translateX(400px);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

/* Auto-dismiss after 5s */
.glass-toast.dismissing {
    animation: toastSlideOut 0.3s ease forwards;
}

@keyframes toastSlideOut {
    to {
        transform: translateX(400px);
        opacity: 0;
    }
}
```

### Sidebar/Drawer
```css
.glass-drawer {
    position: fixed;
    top: 0;
    right: 0;
    width: 400px;
    height: 100vh;
    background: rgba(26, 31, 58, 0.85);
    backdrop-filter: blur(30px) saturate(200%);
    border-left: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: -10px 0 40px rgba(0, 0, 0, 0.5);
    transform: translateX(100%);
    transition: transform 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    z-index: 9998;
    overflow-y: auto;
}

.glass-drawer.open {
    transform: translateX(0);
}
```

### Dropdown/Select
```css
.glass-dropdown {
    position: absolute;
    top: calc(100% + 0.5rem);
    left: 0;
    width: 100%;
    background: rgba(26, 31, 58, 0.95);
    backdrop-filter: blur(25px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
    max-height: 300px;
    overflow-y: auto;
    animation: dropdownFadeIn 0.2s ease;
    z-index: 1000;
}

@keyframes dropdownFadeIn {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.glass-dropdown-item {
    padding: 0.75rem 1rem;
    transition: background 0.2s ease;
    cursor: pointer;
}

.glass-dropdown-item:hover {
    background: rgba(0, 212, 255, 0.15);
}

.glass-dropdown-item:active {
    background: rgba(0, 212, 255, 0.25);
}
```

### Enhanced Tooltip
```css
.glass-tooltip {
    position: absolute;
    background: rgba(0, 0, 0, 0.95);
    backdrop-filter: blur(15px);
    color: white;
    padding: 0.75rem 1rem;
    border-radius: 8px;
    font-size: 0.875rem;
    border: 1px solid rgba(0, 212, 255, 0.3);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.7);
    pointer-events: none;
    opacity: 0;
    transform: translateY(-5px);
    transition: all 0.2s ease;
    z-index: 10001;
    white-space: nowrap;
}

.glass-tooltip::after {
    content: '';
    position: absolute;
    bottom: -6px;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 0;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 6px solid rgba(0, 212, 255, 0.3);
}

[data-tooltip]:hover .glass-tooltip {
    opacity: 1;
    transform: translateY(0);
}
```

---

## ✨ Micro-Interactions Library

### Ripple Effect (Click Feedback)
```css
.ripple-glass {
    position: relative;
    overflow: hidden;
}

.ripple-glass::after {
    content: '';
    position: absolute;
    top: var(--ripple-y, 50%);
    left: var(--ripple-x, 50%);
    width: 0;
    height: 0;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.4);
    transform: translate(-50%, -50%);
    animation: rippleEffect 0.6s ease-out;
    pointer-events: none;
}

@keyframes rippleEffect {
    0% {
        width: 0;
        height: 0;
        opacity: 1;
    }
    100% {
        width: 300px;
        height: 300px;
        opacity: 0;
    }
}
```

**JavaScript (Optional - for click position):**
```javascript
document.querySelectorAll('.ripple-glass').forEach(el => {
    el.addEventListener('click', (e) => {
        const rect = el.getBoundingClientRect();
        el.style.setProperty('--ripple-x', `${e.clientX - rect.left}px`);
        el.style.setProperty('--ripple-y', `${e.clientY - rect.top}px`);
    });
});
```

### 3D Tilt Effect (Hover)
```css
.tilt-glass {
    transform-style: preserve-3d;
    transition: transform 0.3s ease;
}

.tilt-glass:hover {
    transform: perspective(1000px) rotateX(5deg) rotateY(5deg);
}
```

### Glow Pulse (Focus/Active)
```css
.pulse-glow-glass:focus,
.pulse-glow-glass.active {
    animation: glowPulse 2s ease-in-out infinite;
    outline: none;
}

@keyframes glowPulse {
    0%, 100% {
        box-shadow: 
            0 0 20px rgba(0, 212, 255, 0.3),
            0 0 40px rgba(0, 212, 255, 0.2);
    }
    50% {
        box-shadow: 
            0 0 40px rgba(0, 212, 255, 0.5),
            0 0 80px rgba(0, 212, 255, 0.3);
    }
}
```

### Shimmer Effect (Loading)
```css
.shimmer-glass {
    background: linear-gradient(
        90deg,
        rgba(26, 31, 58, 0.6) 0%,
        rgba(255, 255, 255, 0.1) 50%,
        rgba(26, 31, 58, 0.6) 100%
    );
    background-size: 200% 100%;
    animation: shimmerSlide 2s linear infinite;
}

@keyframes shimmerSlide {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
```

### Magnetic Hover (Cursor Pull)
```css
.magnetic-glass {
    transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.magnetic-glass:hover {
    transform: scale(1.05);
}
```

---

## 🚀 Performance Optimization

### GPU Acceleration
```css
/* Apply to all glass elements */
.glass-optimized {
    transform: translateZ(0);
    will-change: transform, opacity;
    backface-visibility: hidden;
    perspective: 1000px;
}
```

### Conditional Blur (Device-Aware)
```css
/* Disable blur on low-end devices */
@media (max-width: 768px) and (max-resolution: 1dppx) {
    .glass-card {
        backdrop-filter: none;
        background: rgba(26, 31, 58, 0.95); /* More opaque */
    }
}

/* Enhanced blur on high-DPI displays */
@media (min-resolution: 2dppx) {
    .glass-card {
        backdrop-filter: blur(25px) saturate(200%);
    }
}
```

### Reduced Motion Support
```css
@media (prefers-reduced-motion: reduce) {
    .glass-card,
    .morph-card,
    .liquid-blob,
    .light-leak-glass::before,
    .light-leak-glass::after {
        animation: none !important;
        transition: none !important;
    }
}
```

### Lazy Animation Loading
```javascript
// Only animate visible elements
const glassObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-glass');
            glassObserver.unobserve(entry.target);
        }
    });
}, { rootMargin: '50px' });

document.querySelectorAll('.glass-card').forEach(card => {
    glassObserver.observe(card);
});
```

---

## 🎨 CSS Variables (Design Tokens)

```css
:root {
    /* Colors */
    --accent-primary: #00d4ff;
    --accent-secondary: #7b61ff;
    --glass-bg: rgba(26, 31, 58, 0.6);
    --glass-border: rgba(255, 255, 255, 0.1);
    
    /* Spacing */
    --space-xs: 0.5rem;   /* 8px */
    --space-sm: 1rem;     /* 16px */
    --space-md: 1.5rem;   /* 24px */
    --space-lg: 2rem;     /* 32px */
    --space-xl: 3rem;     /* 48px */
    
    /* Blur Levels */
    --blur-sm: 10px;
    --blur-md: 20px;
    --blur-lg: 30px;
    
    /* Border Radius */
    --radius-sm: 8px;
    --radius-md: 16px;
    --radius-lg: 24px;
    
    /* Transitions */
    --transition-fast: 0.2s ease;
    --transition-normal: 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-slow: 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
```

---

## 📱 Responsive Breakpoints

```css
/* Mobile First */
@media (min-width: 320px) {
    /* Small mobile */
    .glass-card { padding: var(--space-sm); }
}

@media (min-width: 480px) {
    /* Mobile landscape */
    .glass-card { padding: var(--space-md); }
}

@media (min-width: 768px) {
    /* Tablet */
    .glass-card { padding: var(--space-lg); }
}

@media (min-width: 1024px) {
    /* Desktop */
    .glass-card { padding: var(--space-lg); }
}

@media (min-width: 1440px) {
    /* Large desktop */
    .glass-card { padding: var(--space-xl); }
}
```

---

## 🧪 Testing Checklist

### Visual Testing
- [ ] Blur effect renders correctly (Chrome DevTools → Rendering → Show layer borders)
- [ ] Border gradients display properly
- [ ] Animations run at 60fps (Performance monitor)
- [ ] Hover states trigger smoothly

### Cross-Browser Testing
- [ ] Chrome 90+ (backdrop-filter support)
- [ ] Firefox 88+ (backdrop-filter support)
- [ ] Safari 14+ (webkit-backdrop-filter)
- [ ] Edge 90+ (chromium-based)

### Performance Testing
- [ ] Page load <3s on 3G
- [ ] Animation FPS ≥60
- [ ] GPU memory <50MB
- [ ] No layout thrashing (DevTools → Performance)

### Accessibility Testing
- [ ] Keyboard navigation works (Tab, Enter, Esc)
- [ ] Focus indicators visible
- [ ] Reduced-motion respected
- [ ] Screen reader compatible (ARIA labels)

---

## 🛠️ Implementation Scripts

### Auto-Apply Glass Classes (JavaScript)
```javascript
// Automatically apply glass patterns to elements
class GlassManager {
    constructor() {
        this.applyGlassPatterns();
        this.initInteractions();
    }
    
    applyGlassPatterns() {
        // Auto-detect card containers
        document.querySelectorAll('[data-glass="card"]').forEach(el => {
            el.classList.add('glass-card');
        });
        
        // Auto-detect modals
        document.querySelectorAll('[data-glass="modal"]').forEach(el => {
            el.classList.add('glass-modal');
        });
        
        // Auto-detect tooltips
        document.querySelectorAll('[data-tooltip]').forEach(el => {
            this.createTooltip(el);
        });
    }
    
    initInteractions() {
        // Ripple effect
        document.querySelectorAll('.ripple-glass').forEach(el => {
            el.addEventListener('click', this.createRipple.bind(this));
        });
        
        // Modal triggers
        document.querySelectorAll('[data-modal-trigger]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modalId = e.target.dataset.modalTrigger;
                this.openModal(modalId);
            });
        });
    }
    
    createRipple(e) {
        const el = e.currentTarget;
        const rect = el.getBoundingClientRect();
        el.style.setProperty('--ripple-x', `${e.clientX - rect.left}px`);
        el.style.setProperty('--ripple-y', `${e.clientY - rect.top}px`);
    }
    
    createTooltip(el) {
        const text = el.dataset.tooltip;
        const tooltip = document.createElement('div');
        tooltip.className = 'glass-tooltip';
        tooltip.textContent = text;
        el.style.position = 'relative';
        el.appendChild(tooltip);
    }
    
    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'flex';
            setTimeout(() => modal.classList.add('open'), 10);
        }
    }
    
    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('open');
            setTimeout(() => modal.style.display = 'none', 300);
        }
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.glassManager = new GlassManager();
});
```

### Performance Monitor
```javascript
// Monitor glassmorphism performance
class GlassPerformanceMonitor {
    constructor() {
        this.fpsSamples = [];
        this.lastFrame = performance.now();
        this.monitoring = false;
    }
    
    start() {
        this.monitoring = true;
        this.measure();
    }
    
    stop() {
        this.monitoring = false;
        return this.getReport();
    }
    
    measure() {
        if (!this.monitoring) return;
        
        const now = performance.now();
        const delta = now - this.lastFrame;
        const fps = 1000 / delta;
        
        this.fpsSamples.push(fps);
        if (this.fpsSamples.length > 60) {
            this.fpsSamples.shift();
        }
        
        this.lastFrame = now;
        requestAnimationFrame(() => this.measure());
    }
    
    getReport() {
        const avgFps = this.fpsSamples.reduce((a, b) => a + b, 0) / this.fpsSamples.length;
        const minFps = Math.min(...this.fpsSamples);
        const maxFps = Math.max(...this.fpsSamples);
        
        return {
            average: avgFps.toFixed(2),
            min: minFps.toFixed(2),
            max: maxFps.toFixed(2),
            status: avgFps >= 55 ? '✅ GOOD' : '⚠️ NEEDS OPTIMIZATION'
        };
    }
}

// Usage:
// const monitor = new GlassPerformanceMonitor();
// monitor.start();
// ... interact with glass elements ...
// const report = monitor.stop();
// console.log('Glass Performance:', report);
```

---

## 📐 Layout Patterns

### Pattern 6: Metrics Dashboard (Centered Flexbox)

**Use Case:** Hero section KPI cards, statistics displays, feature highlights

**Implementation:**
```css
.metrics-dashboard {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    align-items: center;
    gap: var(--spacing-lg);
    width: 100%;
    margin: 0 auto var(--spacing-3xl);
    padding: 0 var(--spacing-lg);
}

.metric-card {
    text-align: center;
    padding: var(--spacing-xl) var(--spacing-2xl);
    min-width: 140px;
    flex: 0 1 auto;
}

.metric-value {
    font-size: var(--font-3xl);
    font-weight: 800;
    margin-bottom: var(--spacing-xs);
}

.metric-label {
    font-size: var(--font-sm);
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
```

**Why Flexbox over Grid:**
- Grid with `auto-fit` creates unequal spacing when cards don't fill row
- Flexbox with `justify-content: center` ensures cards are always centered
- `flex: 0 1 auto` prevents cards from stretching

---

### Pattern 7: Balanced Navigation Footer

**Use Case:** Page-to-page navigation with prev/next buttons

**Implementation:**
```css
/* Container */
.nav-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1200px;
    margin: 0 auto var(--spacing-2xl);
    padding: var(--spacing-xl);
}

/* Navigation Links - Equal Width for Visual Balance */
.nav-link {
    min-width: 220px;
    text-align: center;
    padding: var(--spacing-md) var(--spacing-lg);
    background: var(--glass-bg);
    backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    text-decoration: none;
    transition: all 0.3s ease;
}

.nav-link:hover {
    background: rgba(0, 212, 255, 0.1);
    border-color: var(--accent-primary);
    transform: translateY(-2px);
}
```

**Inline Override (for existing pages):**
```html
<nav class="nav-footer" style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto var(--spacing-2xl); padding: var(--spacing-xl);">
    <a href="prev.html" class="nav-link prev" style="min-width: 220px; text-align: center;">
        ← Previous Page
    </a>
    <a href="next.html" class="nav-link next" style="min-width: 220px; text-align: center;">
        Next Page →
    </a>
</nav>
```

**Key Requirements:**
- Equal `min-width` on both buttons (220px)
- Centered text within each button
- `max-width: 1200px` on container with `margin: 0 auto` for page centering
- `justify-content: space-between` pushes buttons to edges
- Bottom margin (`margin-bottom: var(--spacing-2xl)`) for page breathing room

---

## 🎓 Best Practices

### DO ✅
- Use `backdrop-filter` for glass effect (not just opacity)
- Add GPU acceleration hints (`transform: translateZ(0)`)
- Provide reduced-motion fallbacks
- Test on mobile devices (blur is expensive)
- Use CSS variables for consistency
- Layer multiple glass effects for depth
- Add subtle animations (0.3-0.6s duration)

### DON'T ❌
- Overuse blur (>30px becomes unreadable)
- Animate backdrop-filter directly (use transform/opacity instead)
- Forget vendor prefixes (`-webkit-backdrop-filter`)
- Apply glass to text-heavy content (readability issues)
- Use glass on low-contrast backgrounds
- Chain multiple backdrop-filters (performance hit)
- Ignore mobile performance (disable blur on low-end devices)

---

## 📊 Pattern Selection Guide

| Use Case | Pattern | Why |
|----------|---------|-----|
| Default card | Multi-Layer Glass Card | Balanced depth + performance |
| Dashboard widget | Neuglass Card | Tactile feel, soft shadows |
| Expandable content | Morphing Glass Card | Smooth transitions |
| Hero section | Light Leak Glass | Ambient motion, depth |
| Decorative element | Liquid Blob Glass | Eye-catching, organic |
| Modal overlay | Glass Modal | Focus + backdrop blur |
| Notification | Glass Toast | Quick feedback, auto-dismiss |
| Side navigation | Glass Drawer | Slide-in animation |
| Form control | Glass Dropdown | Clear hierarchy |
| Info bubble | Glass Tooltip | Subtle, non-intrusive |

---

## 🔄 Migration from v2.x

**Breaking Changes:**
- Removed single-layer `.glass-basic` (use `.glass-card` instead)
- Renamed `--glass-opacity` → `--glass-bg`
- Changed default blur from 10px → 20px
- Updated transition timing (now uses cubic-bezier)

**Migration Script:**
```javascript
// Auto-migrate v2.x to v3.0
document.querySelectorAll('.glass-basic').forEach(el => {
    el.classList.remove('glass-basic');
    el.classList.add('glass-card');
});

// Update CSS variables
document.documentElement.style.setProperty('--glass-bg', 'rgba(26, 31, 58, 0.6)');
```

---

## 📚 External Resources

- **MDN backdrop-filter:** https://developer.mozilla.org/en-US/docs/Web/CSS/backdrop-filter
- **Can I Use:** https://caniuse.com/css-backdrop-filter
- **Performance Guide:** https://web.dev/backdrop-filter/
- **Glassmorphism.com:** Design inspiration

---

## 📄 Version History

### v3.1.0 (December 31, 2025)
- ✨ Added Pattern 6: Metrics Dashboard (Centered Flexbox)
- ✨ Added Pattern 7: Balanced Navigation Footer
- 📚 Documented flexbox vs grid trade-offs for centered layouts
- 📚 Added inline override examples for existing pages

### v3.0.0 (December 31, 2025)
- ✨ Added multi-layer glassmorphism system
- ✨ Added neuglass, morphing, light leak, liquid blob patterns
- ✨ Added 5 UI component patterns (modal, toast, drawer, dropdown, tooltip)
- ✨ Added micro-interactions library (ripple, tilt, glow, shimmer, magnetic)
- ✨ Added performance optimization (GPU acceleration, conditional blur, lazy loading)
- ✨ Added GlassManager and GlassPerformanceMonitor scripts
- 🔄 Changed default blur from 10px → 20px
- 🔄 Updated transitions to cubic-bezier easing
- 📚 Added pattern selection guide

### v2.3.0 (December 31, 2025)
- Added Contained Action Panel pattern
- Added Adaptive Code Panel Height Algorithm
- Added D3.js Layout Pattern Selection Guide

### v2.2.0 (Previous)
- Added STS Code Panel Height Algorithm
- Added responsive breakpoints

### v2.1.0 (Previous)
- Added FontAwesome icon standards
- Added breadcrumb navigation

### v2.0.0 (Previous)
- Initial glassmorphism design system
- Basic glass card pattern
- Mobile responsiveness

---

**Generated by:** CORTEX Optimization Engine v1.0.0  
**Standard Version:** 3.1.0  
**Last Review:** December 31, 2025  
**Next Review:** Q2 2026
