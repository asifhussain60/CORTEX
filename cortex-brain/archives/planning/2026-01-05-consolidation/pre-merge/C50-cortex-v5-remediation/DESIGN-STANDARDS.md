# C50 Epic Design Standards

**Version:** 1.0  
**Date:** January 4, 2026  
**Approved By:** Asif Hussain  
**Status:** ✅ PRODUCTION STANDARD

---

## 🎯 Progressive Disclosure Pattern

### Principle
**Active work items ALWAYS appear at the TOP, completed items ALWAYS appear at the BOTTOM.**

This ensures users focus on what needs attention NOW rather than scrolling past completed work.

---

## 📊 Sorting Priority Specification

### Status Priority Order (Low Number = Higher Position)

```javascript
const PRIORITY_MAP = {
  'in progress': 1,    // Highest priority - actively being worked
  'blocked': 2,        // Needs immediate attention to unblock
  'pending': 3,        // Ready to start next
  'active': 4,         // General active state
  'deferred': 5,       // Postponed but tracked
  'complete': 6,       // Done - pushed to bottom
  'completed': 6       // Done - pushed to bottom
};
```

### Implementation Requirements

**MANDATORY for all C50 child plan viewers:**

1. **Sort Function**: Must implement `sortChildPlansByPriority(plans)` function
2. **Visual Indicators**: High-priority items MUST have colored left border:
   - `data-priority="high"` → Green gradient (In Progress/Blocked)
   - `data-priority="medium"` → Orange gradient (Pending)
   - `data-priority="low"` → No indicator (Deferred/Complete)
3. **Secondary Sort**: Within same priority, sort by plan ID/order
4. **Auto-Refresh**: Sorting must re-apply on every data refresh

---

## 🎨 Visual Design Standards

### Header Design (Approved January 4, 2026)

**Logo:**
- Size: 180px × 180px
- Effect: Purple glow (`drop-shadow(0 4px 12px rgba(109, 40, 217, 0.4))`)
- Position: Left-aligned with title

**Title:**
- Font: 2.8em, weight 700
- Color: White with shadow
- Letter spacing: -0.5px

**Subtitle:**
- Font: 1.2em, weight 400
- Color: `rgba(255, 255, 255, 0.75)`
- Letter spacing: 0.5px

**Metadata Cards:**
- Layout: CSS Grid, auto-fit, min 180px
- Padding: 18px
- Background: `rgba(255, 255, 255, 0.05)` with hover to `0.08`
- Border: 1px solid `rgba(255, 255, 255, 0.1)`
- Hover: `translateY(-2px)` + shadow

### Progress Bars

**Overall Progress:**
- Height: 45px
- Border radius: 25px
- Gradient: `linear-gradient(90deg, var(--accent) 0%, var(--accent-light) 50%, var(--primary-light) 100%)`
- Animation: Shimmer effect (`@keyframes shimmer`)

**Status Badges:**
- Padding: 8px 20px
- Border radius: 25px
- Font: 0.95em, weight 700, uppercase
- Gradients: All badges use gradient backgrounds
- Hover: `scale(1.05)` + enhanced shadow

### Child Plan Cards

**Base Style:**
- Padding: 20px
- Cursor: pointer
- Hover: `translateY(-5px)` + shadow

**Priority Indicators:**
- Left border: 4px width
- High priority (In Progress/Blocked): Green gradient
- Medium priority (Pending): Orange gradient
- Low priority: No indicator

---

## 📱 Responsive Design Requirements

### Breakpoints

**Desktop (>1024px):**
- Metadata: 4-column grid
- Logo: 180px
- Title: 2.8em

**Tablet (768-1024px):**
- Metadata: 2-column grid
- Logo: 140px
- Title: 2.2em

**Mobile (<768px):**
- Metadata: 1-column grid
- Logo: 120px (centered)
- Title: 1.8em
- Header: Centered layout

---

## 🔧 Implementation Checklist

**For ALL C50 child plan viewers:**

- [ ] Implement `sortChildPlansByPriority()` function
- [ ] Add `data-priority` attributes to cards
- [ ] Add CSS for left border indicators (high/medium)
- [ ] Apply sorting BEFORE rendering cards
- [ ] Re-sort on data refresh
- [ ] Test with mixed status scenarios
- [ ] Verify completed items appear at bottom
- [ ] Verify in-progress items appear at top

---

## 📝 Code Template

### JavaScript Sorting Function

```javascript
// Sort child plans by priority (active work at top, completed at bottom)
function sortChildPlansByPriority(plans) {
    const priorityMap = {
        'in progress': 1,
        'blocked': 2,
        'pending': 3,
        'active': 4,
        'deferred': 5,
        'complete': 6,
        'completed': 6
    };

    return plans.sort((a, b) => {
        const aStatus = a.status.toLowerCase();
        const bStatus = b.status.toLowerCase();
        
        // Find priority for each status
        let aPriority = 999;
        let bPriority = 999;
        
        for (const [key, value] of Object.entries(priorityMap)) {
            if (aStatus.includes(key)) aPriority = Math.min(aPriority, value);
            if (bStatus.includes(key)) bPriority = Math.min(bPriority, value);
        }
        
        // If same priority, sort by order/id
        if (aPriority === bPriority) {
            return (a.order || a.id).localeCompare(b.order || b.id);
        }
        
        return aPriority - bPriority;
    });
}
```

### CSS Priority Indicators

```css
/* Priority indicator for active work (visual cue) */
.child-plan[data-priority="high"]::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 4px;
    background: linear-gradient(180deg, var(--accent) 0%, var(--accent-light) 100%);
    border-radius: 12px 0 0 12px;
}

.child-plan[data-priority="medium"]::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 4px;
    background: linear-gradient(180deg, var(--warning) 0%, #F59E0B 100%);
    border-radius: 12px 0 0 12px;
}
```

### Priority Attribute Assignment

```javascript
// Add priority attribute for visual indicator
const status = plan.status.toLowerCase();
if (status.includes('progress') || status.includes('blocked')) {
    card.setAttribute('data-priority', 'high');
} else if (status.includes('pending')) {
    card.setAttribute('data-priority', 'medium');
}
```

---

## 🚀 Rollout Plan

### Phase 1: Standardization (Current)
- ✅ Apply to main C50 epic dashboard (`plan-viewer.html`)
- ✅ Document standards in `DESIGN-STANDARDS.md`
- ✅ Test with actual C50 data

### Phase 2: Child Plan Viewers (Next)
- [ ] Audit all 22 child plan viewers
- [ ] Apply sorting logic to each
- [ ] Add priority indicators
- [ ] Test responsiveness

### Phase 3: Validation (Final)
- [ ] User acceptance testing
- [ ] Performance validation (sorting overhead)
- [ ] Cross-browser testing (Chrome, Safari, Firefox)
- [ ] Mobile device testing (iOS, Android)

---

## 📚 References

**Main Implementation:** `plan-viewer.html` (C50 Epic Dashboard)  
**CSS Framework:** Glassmorphism theme v5.1.0  
**Response Templates:** `cortex-brain/response-templates-v4.yaml`  
**Master Orchestrator:** `cortex-brain/config/master-orchestrator.yaml`

---

## ✅ Approval History

| Date | Approver | Change | Status |
|------|----------|--------|--------|
| 2026-01-04 | Asif Hussain | Initial header design + progressive disclosure | ✅ Approved |
| 2026-01-04 | Asif Hussain | Standardized across C50 epic | ✅ Approved |

---

**Copyright © 2026 Asif Hussain. All rights reserved.**
