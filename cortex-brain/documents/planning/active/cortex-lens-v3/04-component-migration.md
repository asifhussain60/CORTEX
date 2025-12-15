# CORTEX Lens v3.0 - Component Migration Checklist

**Version:** 1.0  
**Date:** December 14, 2025  
**Phase:** Phase 0 - Planning & Preparation  
**Status:** Checklist Defined

---

## 🎯 Overview

Tracks migration of 26 production components from Admin Dashboard to CORTEX Lens v3.0.

**Migration Types:**
- **Extract:** Copy from admin with modifications (18 components)
- **Create:** Build new for lens-specific needs (6 components)
- **Adapt:** Heavily modify admin component (2 components)

---

## 📋 Component Migration Matrix

| # | Component | Source | Type | Priority | Status | Dependencies | Sub-Plan |
|---|-----------|--------|------|----------|--------|--------------|----------|
| 1 | LoadingSpinner | Admin | Extract | HIGH | ☐ | variables.css | SP-14 |
| 2 | SkeletonLoader | Admin | Extract | HIGH | ☐ | variables.css, animations.css | SP-14 |
| 3 | ProgressBar | Admin | Extract | MEDIUM | ☐ | variables.css | SP-14 |
| 4 | Modal | Admin | Extract | MEDIUM | ☐ | variables.css, glassmorphism | SP-14 |
| 5 | Tooltip | Admin | Extract | LOW | ☐ | variables.css | SP-14 |
| 6 | Toast | Admin | Extract | LOW | ☐ | variables.css, animations.css | SP-14 |
| 7 | Dropdown | Admin | Extract | MEDIUM | ☐ | variables.css | SP-14 |
| 8 | DatePicker | Admin | Extract | LOW | ☐ | variables.css, dropdown | SP-14 |
| 9 | SearchBox | Admin | Extract | MEDIUM | ☐ | variables.css, dropdown | SP-14 |
| 10 | Pagination | Admin | Extract | MEDIUM | ☐ | variables.css | SP-14 |
| 11 | InfiniteScroll | Admin | Extract | LOW | ☐ | - | SP-14 |
| 12 | VirtualScroll | Admin | Extract | HIGH | ☐ | - | SP-15 |
| 13 | Breadcrumbs | Admin | Extract | LOW | ☐ | variables.css | SP-14 |
| 14 | Stepper | Admin | Extract | LOW | ☐ | variables.css | SP-14 |
| 15 | Accordion | Admin | Extract | LOW | ☐ | variables.css, animations.css | SP-14 |
| 16 | Carousel | Admin | Extract | LOW | ☐ | variables.css, animations.css | SP-14 |
| 17 | Badge | Admin | Extract | MEDIUM | ☐ | variables.css | SP-14 |
| 18 | Avatar | Admin | Extract | LOW | ☐ | variables.css | SP-14 |
| 19 | FileUpload | Admin | Extract | LOW | ☐ | variables.css | SP-14 |
| 20 | CodeBlock | Admin | Extract | LOW | ☐ | variables.css, syntax highlighting | SP-14 |
| 21 | ProgressiveLoader | Admin | Extract | HIGH | ☐ | InfiniteScroll | SP-14 |
| 22 | ExportUtils | Admin | Adapt | HIGH | ☐ | - | SP-14 |
| 23 | AdaptiveVisibility | Admin | Extract | MEDIUM | ☐ | breakpoints | SP-14 |
| 24 | KeyboardNavigation | Admin | Adapt | HIGH | ☐ | - | SP-3 |
| 25 | ThemeToggle | Admin | Extract | LOW | ☐ | variables.css | SP-14 |
| 26 | DataGrid | Admin | Extract | MEDIUM | ☐ | VirtualScroll, Pagination | SP-14 |
| 27 | HealthScoreRing | Lens | Create | HIGH | ☐ | D3.js | SP-5 |
| 28 | TrendIndicator | Lens | Create | MEDIUM | ☐ | Chart.js | SP-5 |
| 29 | SecurityBadge | Lens | Create | MEDIUM | ☐ | Badge | SP-8 |
| 30 | DependencyStatus | Lens | Create | MEDIUM | ☐ | Badge | SP-7 |
| 31 | CoverageBar | Lens | Create | MEDIUM | ☐ | ProgressBar | SP-6 |
| 32 | ComplexityGauge | Lens | Create | MEDIUM | ☐ | D3.js | SP-6 |

---

## 🔄 Migration Workflow Per Component

### Phase 1: Extraction (Day 1)
- [ ] Locate component in admin dashboard
- [ ] Copy HTML structure
- [ ] Copy CSS styles (with glassmorphism)
- [ ] Copy JavaScript logic
- [ ] Document dependencies

### Phase 2: Adaptation (Day 1-2)
- [ ] Apply 125% typography scale
- [ ] Update CSS variables (admin → lens)
- [ ] Remove admin-specific logic
- [ ] Add lens-specific features
- [ ] Vendor external dependencies (if any)

### Phase 3: Testing (Day 2)
- [ ] RED: Write failing unit tests
- [ ] GREEN: Implement component
- [ ] REFACTOR: Clean up code
- [ ] Test accessibility (ARIA, keyboard nav)
- [ ] Test in all target browsers

### Phase 4: Integration (Day 2-3)
- [ ] Add to component library
- [ ] Create usage documentation
- [ ] Add to Storybook-style examples
- [ ] Update master checklist

---

## 📊 Progress Tracking

**Overall:** 0/32 components (0%)

**By Priority:**
- HIGH (8): 0/8 (0%)
- MEDIUM (13): 0/13 (0%)
- LOW (11): 0/11 (0%)

**By Type:**
- Extract (24): 0/24 (0%)
- Create (6): 0/6 (0%)
- Adapt (2): 0/2 (0%)

---

## ✅ Completion Criteria

Component migration complete when:
- [ ] All 32 components implemented
- [ ] All components tested (unit + integration)
- [ ] All components documented with examples
- [ ] All components accessible (WCAG 2.1 AAA)
- [ ] Component library integrated in all 6 templates
- [ ] Zero external dependencies

---

**Next Action:** Begin migration in Phase 6 (Sub-Plan 14)
