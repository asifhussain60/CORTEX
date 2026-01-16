# CORTEX Branding Guidelines

**Document Version:** 2.0  
**Last Updated:** January 16, 2026  
**Author:** Asif Hussain  
**Copyright:** © 2025-2026 Asif Hussain. All rights reserved.

---

## 1. Brand Overview

**CORTEX** is an AI-powered development orchestration system with a focus on governance, observability, and intelligent automation. The brand identity reflects sophistication, intelligence, and reliability through a modern glassmorphism design system.

### Brand Personality
- **Professional**: Enterprise-grade governance and reliability
- **Intelligent**: AI-powered orchestration and automation
- **Trustworthy**: Immutable audit trails and hash chain integrity
- **Modern**: Glassmorphism design with smooth animations
- **Accessible**: WCAG 2.1 AA compliance, inclusive design

---

## 2. Logo Specifications

### Logo Variants

#### Primary Logo (200x200px)
- **File**: `.github/branding/cortex-logo.png`
- **Usage**: Main header, branding materials, documentation
- **Background**: Works on light and dark backgrounds
- **Color**: Full color (cyan gradient with accent)
- **Minimum Size**: 48px (responsive)

#### White Variant (200x200px)
- **File**: `.github/branding/cortex-logo-white.png`
- **Usage**: Dark mode, dark backgrounds, print materials
- **Color**: White/light with transparency support
- **Minimum Size**: 48px

#### Icon Variant (32x32px)
- **File**: `.github/branding/cortex-logo-icon.png`
- **Usage**: Favicon, browser tabs, app icons
- **Color**: Simplified, high contrast
- **Use Cases**: Favicon, shortcut icons, bookmarks

#### Small Logo (128x128px)
- **File**: `.github/branding/cortex-logo-small.png`
- **Usage**: Sidebar, cards, mobile header
- **Background**: Glassmorphic frame recommended
- **Minimum Size**: 64px on mobile

---

## 3. Logo Placement

### Header Placement (Primary)
```
┌──────────────────────────────────────────────────────────────┐
│  [LOGO] CORTEX Neural Observatory      [Search] [⚙] [☀/☾]   │
│  (200px)  Brain Visualization & Governance Hub                │
└──────────────────────────────────────────────────────────────┘
```

**Specifications:**
- **Position**: Top-left corner of header
- **Size**: 200x200px on desktop, scales down responsively
- **Spacing**: 1rem margin from left edge, 1.5rem gap to title
- **Click Action**: Navigate to dashboard home (`#/`)
- **Hover Effect**: Scale (1.05x) with glow effect
- **Accessibility**: Alt text "CORTEX Logo", ARIA label for button

### Sidebar Placement (Secondary)
```
┌─────────────────┐
│    [LOGO]       │  ← 128x128px, centered
│   (128px)       │
├─────────────────┤
│ Brain Observatory
│ Temporal Cortex │
│ Orchestrators   │
│ Plan Hub        │
│ Admin           │
└─────────────────┘
```

**Specifications:**
- **Position**: Top of sidebar
- **Size**: 128x128px
- **Background**: Glassmorphic frame (rgba(255, 255, 255, 0.08))
- **Spacing**: 20px margin below logo before nav items

### Favicon
- **File**: `.github/branding/cortex-favicon.ico`
- **Size**: 32x32px multi-format
- **Usage**: Browser tab, bookmarks, shortcuts
- **Formats**: ICO, PNG, SVG

### Export/Print Usage
- **PDF Headers**: 3cm × 3cm (logo on left)
- **PDF Footers**: 25% opacity watermark (bottom-right)
- **Markdown Reports**: Referenced via `![CORTEX Logo](../.github/branding/cortex-logo.png)`
- **Screenshots**: No watermarking on screenshots (watermark only in exports)

---

## 4. Color System

### Primary Colors

| Color | Hex Code | RGB | Use Case |
|-------|----------|-----|----------|
| **Cyan** | `#0ea5e9` | (14, 165, 233) | Buttons, links, active states, brand accent |
| **Emerald** | `#10b981` | (16, 185, 129) | Success indicators, completed items |
| **Violet** | `#a78bfa` | (167, 139, 250) | AI/intelligence features, accents |
| **Amber** | `#f59e0b` | (245, 158, 11) | Warnings, alerts |
| **Red** | `#ef4444` | (239, 68, 68) | Critical errors, dangers |

### Background Colors

| Element | Color Value | Use Case |
|---------|-------------|----------|
| Header/Cards | `rgba(15, 23, 42, 0.75)` | Primary glassmorphism |
| Secondary | `rgba(30, 41, 59, 0.8)` | Secondary surfaces |
| Tertiary | `rgba(51, 65, 85, 0.6)` | Tertiary backgrounds |
| Hover | `rgba(14, 165, 233, 0.1)` | Interactive hover states |

### Glassmorphism

```css
background: rgba(15, 23, 42, 0.75);
backdrop-filter: blur(16px);
border: 1px solid rgba(255, 255, 255, 0.08);
box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
```

---

## 5. Typography

### Font System

```css
/* Primary Font Stack */
font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;

/* Monospace Stack */
font-family: ui-monospace, 'Courier New', monospace;
```

### Type Scale

| Level | Size | Weight | Use Case |
|-------|------|--------|----------|
| H1 | 2.5rem (40px) | 700 | Page titles |
| H2 | 2rem (32px) | 700 | Section headers |
| H3 | 1.5rem (24px) | 700 | Subsection headers |
| Body | 1rem (16px) | 400 | Regular text |
| Small | 0.875rem (14px) | 400 | Captions, help text |
| Micro | 0.75rem (12px) | 500 | Labels, badges |

### Font Weights
- **Regular**: 400 (body text)
- **Medium**: 500 (labels, buttons)
- **Semibold**: 600 (card titles, badges)
- **Bold**: 700 (headers, emphasis)

---

## 6. Spacing System

**Base Unit**: 4px

### Scale
```
4px   - xs  (0.25rem)
8px   - sm  (0.5rem)
12px  - md  (0.75rem)
16px  - lg  (1rem)      ← Standard padding
24px  - xl  (1.5rem)
32px  - 2xl (2rem)
48px  - 3xl (3rem)
64px  - 4xl (4rem)
96px  - 6xl (6rem)
128px - 8xl (8rem)
```

### Breathing Room
- **Card padding**: 1.5rem (24px)
- **Section margin**: 2rem (32px)
- **Component gap**: 1rem (16px)
- **Grid gap**: 1.5rem (24px)

---

## 7. Icon System

### Icon Library
- **Primary**: Heroicons 2.0 (24px and 32px)
- **Source**: `https://cdn.jsdelivr.net/npm/heroicons@2.0.18/outline/`
- **Usage**: Navigation, actions, status indicators

### Icon Sizing

| Size | Use Case |
|------|----------|
| 16px | Badges, tiny indicators |
| 20px | Button icons |
| 24px | Header icons |
| 32px | Large buttons, primary actions |
| 48px | Hero icons, featured actions |

### Icon Styling

```css
stroke: currentColor;
stroke-width: 2;
fill: none;
```

---

## 8. Animations & Interactions

### Transition Timing
- **Fast**: 200ms (hover effects, state changes)
- **Normal**: 300ms (view transitions, drawer opens)
- **Slow**: 500ms (page transitions, dialogs)

### Animation Examples

```css
/* Glow on hover */
box-shadow: 0 0 20px rgba(14, 165, 233, 0.3);

/* Scale on active */
transform: scale(0.95);

/* Pulse animation */
animation: pulse 2s infinite;

/* Slide animation */
animation: slideInRight 0.3s ease;
```

### Neural Pulse (Brand Animation)
```css
@keyframes pulse-neural {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

animation: pulse-neural 2s infinite;
```

---

## 9. Accessibility

### WCAG 2.1 AA Compliance

- **Color Contrast**: Minimum 4.5:1 for normal text, 3:1 for large text
- **Focus Indicators**: Visible focus ring on all interactive elements
- **Touch Targets**: Minimum 44×44px on mobile
- **Keyboard Navigation**: Full keyboard support, no mouse-only interactions
- **Screen Readers**: ARIA labels on all interactive elements

### Color Accessibility

```css
/* Good contrast */
color: #ffffff;  /* Foreground */
background: #0ea5e9;  /* Background */
/* Contrast ratio: 5.8:1 ✓ */

/* Accessible for color-blind users */
/* Use patterns + color, not color alone */
```

---

## 10. Dark Mode

### Dark Mode Colors

| Element | Light Mode | Dark Mode |
|---------|-----------|-----------|
| Background | `#ffffff` | `#0f172a` (slate-950) |
| Primary Text | `#000000` | `#ffffff` |
| Secondary Text | `rgba(0, 0, 0, 0.6)` | `rgba(255, 255, 255, 0.6)` |
| Borders | `rgba(0, 0, 0, 0.1)` | `rgba(255, 255, 255, 0.08)` |
| Accent | `#0ea5e9` | `#0ea5e9` (unchanged) |

### Dark Mode Toggle

- **Storage**: `localStorage.setItem('cortex-dark-mode', 'true/false')`
- **Class**: Add `.dark-mode` to `<html>` element
- **Logo**: Switch to white variant (`cortex-logo-white.png`)
- **CSS Variable**: `--is-dark-mode: 0 | 1`

---

## 11. Responsive Breakpoints

| Breakpoint | Size | Device | Navigation |
|-----------|------|--------|-----------|
| **Mobile** | 320-479px | Small phones | Hamburger menu |
| **Small Mobile** | 480-639px | Mobile phones | Hamburger menu |
| **Tablet** | 640-767px | Tablets (portrait) | Hamburger menu |
| **Large Tablet** | 768-1023px | Tablets (landscape) | Sidebar collapses |
| **Desktop** | 1024-1535px | Desktops | Full sidebar |
| **Large Desktop** | 1536px+ | Large screens | Full layout |

### Mobile-First Approach
All styles start mobile-optimized, then use `@media (min-width: Xpx)` to enhance for larger screens.

---

## 12. Logo Usage Do's and Don'ts

### ✅ DO

- Use the logo on light backgrounds (primary variant)
- Use white variant on dark backgrounds
- Provide clear spacing around the logo (1rem minimum)
- Maintain aspect ratio (always square 1:1)
- Use in header navigation as a clickable home button
- Include in PDF exports and printed materials
- Use at 48px minimum on web, 32px minimum in small spaces

### ❌ DON'T

- Stretch or distort the logo
- Rotate or skew the logo (except 90° multiples if absolutely necessary)
- Change colors or remove parts of the logo
- Use the logo smaller than 32px on web or in icons
- Place logo on busy or low-contrast backgrounds without a frame
- Use the colored variant on dark backgrounds
- Add drop shadows or effects to the logo (use existing shadow system)
- Use as a repeating pattern or background

---

## 13. Documentation & Assets

### Asset Directory Structure
```
.github/branding/
├── cortex-logo.png           (200x200px, full color)
├── cortex-logo-white.png     (200x200px, white variant)
├── cortex-logo-dark.png      (200x200px, dark variant)
├── cortex-logo-icon.png      (32x32px, icon version)
├── cortex-logo-small.png     (128x128px, sidebar version)
├── cortex-favicon.ico        (32x32px multi-format)
├── BRANDING-GUIDELINES.md    (this file)
├── LOGO-PLACEMENT-GUIDE.md   (logo placement details)
└── COLOR-PALETTE.css         (Tailwind color definitions)
```

### Implementation Files
```
src/dashboard/
├── frontend/
│   ├── assets/
│   │   ├── cortex-logo.png
│   │   ├── cortex-logo-white.png
│   │   └── cortex-favicon.ico
│   ├── js/
│   │   └── components/common/header.js
│   └── css/
│       ├── header.css
│       ├── colors.css
│       └── glassmorphism.css
```

---

## 14. Implementation Checklist

- [ ] Logo files created and placed in `.github/branding/`
- [ ] Header component (`header.js`) created with logo integration
- [ ] Header styles (`header.css`) implemented with glassmorphism
- [ ] Color system defined in CSS variables
- [ ] Dark mode toggle implemented
- [ ] Responsive design tested at all breakpoints
- [ ] Accessibility audit completed (WCAG 2.1 AA)
- [ ] Logo hover effects and animations working
- [ ] Favicon configured in HTML head
- [ ] Dark mode variant tested
- [ ] Export functionality includes branding
- [ ] All documentation updated
- [ ] Screenshots captured for portfolio

---

## 15. Questions & Support

For branding questions or guidance:
1. Review this document (BRANDING-GUIDELINES.md)
2. Check LOGO-PLACEMENT-GUIDE.md for specific placement questions
3. Reference COLOR-PALETTE.css for color values
4. Test locally with `header.js` component

---

**End of Branding Guidelines**  
*Last Updated: January 16, 2026*  
*Version: 2.0 - Production Ready*
