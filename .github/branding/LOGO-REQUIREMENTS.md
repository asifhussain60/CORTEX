# CORTEX Logo Requirements

## DO-001-01: Logo Integration in Header

### Asset Specifications

**Primary Logo (Light Mode)**
- **File**: `cortex-logo.png`
- **Size**: 200x200px (square)
- **Format**: PNG with transparency
- **Color scheme**: Cyan (#0ea5e9) and gradient accents
- **Usage**: Default logo displayed in light mode
- **Location**: `src/dashboard/frontend/assets/cortex-logo.png`

**Dark Mode Variant**
- **File**: `cortex-logo-white.png`
- **Size**: 200x200px (square)
- **Format**: PNG with transparency
- **Color scheme**: White/light colors for dark backgrounds
- **Usage**: Logo variant for dark mode
- **Location**: `src/dashboard/frontend/assets/cortex-logo-white.png`

### Design Guidelines

**Visual Identity**
- Logo should incorporate neural network or brain-inspired elements
- Primary color: Cyan (#0ea5e9) - represents intelligence and technology
- Secondary accents: Emerald (#10b981) for growth, Violet (#a78bfa) for AI
- Modern, clean, professional aesthetic
- Scalable design (must remain legible at 96px mobile size)

**Responsive Behavior**
- Desktop (≥1024px): 200px × 200px - Full size
- Tablet (768-1023px): 128px × 128px - Scaled
- Mobile (320-767px): 96px × 96px - Compact

**Interactive Elements**
- Hover effect: Scale 1.05x with subtle glow
- Click action: Navigate to dashboard home (`/`)
- Tooltip: "CORTEX v2.0" on hover
- Transition: 200ms ease-in-out

### Technical Requirements

**File Optimization**
- PNG compression: Use pngquant or similar (target <50KB per file)
- Transparency: Alpha channel required for glassmorphism backgrounds
- Resolution: @2x retina assets optional but recommended

**Accessibility**
- Alt text: "CORTEX Neural Observatory Logo"
- ARIA label: "CORTEX Dashboard - Return to Home"
- Focus indicator: 2px cyan outline on keyboard focus
- Minimum contrast: WCAG AA compliant (4.5:1 text, 3:1 UI)

### Implementation Checklist

- [ ] Create/source `cortex-logo.png` (200x200px)
- [ ] Create/source `cortex-logo-white.png` (200x200px)
- [ ] Optimize PNG files (<50KB each)
- [ ] Implement header.js logo component
- [ ] Add responsive CSS scaling
- [ ] Add hover/focus effects
- [ ] Implement dark mode variant switching
- [ ] Add click handler (navigate to `/`)
- [ ] Create tooltip ("CORTEX v2.0")
- [ ] Write 6 acceptance tests
- [ ] Verify WCAG AA compliance

### Testing Criteria

**Unit Tests** (`tests/unit/dashboard/components/test_header_logo.py`)
1. `test_logo_displays_200px_desktop()` - Logo renders at 200px on desktop
2. `test_logo_scales_128px_tablet()` - Logo scales to 128px at 768px breakpoint
3. `test_logo_scales_96px_mobile()` - Logo scales to 96px at 320px viewport
4. `test_logo_click_navigates_home()` - Click handler navigates to `/`
5. `test_logo_hover_effects()` - Hover triggers scale 1.05x and glow
6. `test_dark_mode_variant_loads()` - Dark mode switches to white logo variant

**Manual Testing**
- Visual inspection at all breakpoints (320px, 768px, 1024px, 1920px)
- Keyboard navigation (Tab to logo, Enter to activate)
- Screen reader announcement test
- Dark mode toggle test
- Browser compatibility (Chrome, Firefox, Safari, Edge)

### Notes

**Placeholder Assets**
Until final logo assets are provided, use:
- SVG placeholder with "CORTEX" text and neural network icon
- Generated via: https://placeholder.com/200x200/0ea5e9/FFFFFF?text=CORTEX
- Replace with production assets before phase lock

**Source Assets**
If CORTEX branding exists in other branches:
```bash
# Check for existing logos
git log --all --full-history -- "*logo*" "*branding*"
```

---
**AC-ID**: DO-001-01  
**Phase**: PHASE-15-DASHBOARD-ENHANCEMENT  
**Priority**: CRITICAL  
**Estimated**: 2 hours  
**Status**: PENDING (awaiting logo assets)
