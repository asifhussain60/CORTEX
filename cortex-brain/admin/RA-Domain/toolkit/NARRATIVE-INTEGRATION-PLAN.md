# Dashboard Narrative Integration Plan

**Purpose:** Identify which OneDrive dashboard pages benefit from descriptive narratives  
**Created:** December 11, 2025  
**Integration Method:** HTML section additions with glass-morphism styling

---

## Narrative Integration Matrix

| Page | Narrative Section | Purpose | Length | Priority |
|------|-------------------|---------|--------|----------|
| **index.html** | Full Executive Narrative | Complete "What This Application Does" | 3,800 words | 🔴 CRITICAL |
| **capability-catalog.html** | Key Capabilities Summary | Explain 14 functional areas | 400 words | 🟠 HIGH |
| **managers/performance-metrics.html** | V2 Architecture Explanation | Why 85% improvement matters | 250 words | 🟠 HIGH |
| **regulatory/compliance-overview.html** | Regulatory Framework Summary | IRS/HIPAA/PCI-DSS context | 300 words | 🟠 HIGH |
| **managers/team-metrics.html** | No narrative | Data speaks for itself | N/A | ⚪ SKIP |
| **managers/technical-debt-roi.html** | ROI Context | Why debt matters to business | 200 words | 🟡 MEDIUM |
| **developers/domain-model.html** | Domain Model Explanation | Entity relationships in context | 300 words | 🟡 MEDIUM |
| **developers/integration-architecture.html** | Integration Ecosystem | Event-driven architecture purpose | 250 words | 🟡 MEDIUM |
| **developers/complexity-heatmap.html** | No narrative | Visual data primary | N/A | ⚪ SKIP |
| **developers/knowledge-ownership.html** | No narrative | Bus factor self-explanatory | N/A | ⚪ SKIP |
| **developers/onboarding-guide.html** | Platform Overview | "Start here" introduction | 400 words | 🟠 HIGH |
| **managers/test-coverage-gaps.html** | No narrative | Gaps table primary | N/A | ⚪ SKIP |
| **managers/test-coverage-roadmap.html** | No narrative | Roadmap visual primary | N/A | ⚪ SKIP |
| **managers/weekly-scorecard.html** | No narrative | Metrics dashboard | N/A | ⚪ SKIP |
| **regulatory/p0-issues-tracker.html** | Compliance Risk Context | Why these P0s matter ($500k-$2M risk) | 250 words | 🟠 HIGH |

---

## Implementation Priority

### Phase 1: Critical (Complete First) - 1 page
1. **index.html** - Full executive narrative (3,800 words)
   - Placement: After header, before KPI grid
   - Styling: Glass card with collapsible sections
   - UX: Show first 500 words, "Read more" expansion

### Phase 2: High Priority - 5 pages
2. **capability-catalog.html** - Key capabilities summary
3. **managers/performance-metrics.html** - V2 architecture explanation
4. **regulatory/compliance-overview.html** - Regulatory framework
5. **developers/onboarding-guide.html** - Platform overview
6. **regulatory/p0-issues-tracker.html** - Compliance risk context

### Phase 3: Medium Priority - 3 pages
7. **managers/technical-debt-roi.html** - ROI business context
8. **developers/domain-model.html** - Entity relationship explanation
9. **developers/integration-architecture.html** - Integration ecosystem

### Phase 4: Skip (Data-Focused, No Narrative Needed) - 6 pages
- team-metrics, complexity-heatmap, knowledge-ownership
- test-coverage-gaps, test-coverage-roadmap, weekly-scorecard

---

## HTML Integration Pattern

**Standard Narrative Section Structure:**

```html
<!-- Executive Narrative Section -->
<section class="glass-card-flat mb-xl">
    <h2 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem; color: var(--text-primary);">
        📖 Understanding This Platform
    </h2>
    
    <!-- Collapsible Narrative Content -->
    <div class="narrative-content">
        <div class="narrative-preview" id="narrative-preview">
            <!-- First 500 words visible by default -->
            <p>The Reimbursement Accounts platform is HealthEquity's enterprise system...</p>
            <!-- ... -->
        </div>
        
        <div class="narrative-full" id="narrative-full" style="display: none;">
            <!-- Full narrative hidden until expanded -->
            <h3>What Is This Application?</h3>
            <p>...</p>
            
            <h3>Who Uses It?</h3>
            <p>...</p>
            
            <!-- ... all sections ... -->
        </div>
        
        <button class="btn-expand" onclick="toggleNarrative()" style="margin-top: 1rem; padding: 0.5rem 1rem; background: var(--primary); color: white; border: none; border-radius: 8px; cursor: pointer;">
            <span id="btn-text">📖 Read Full Story (3,800 words, 15 min read)</span>
        </button>
    </div>
</section>

<script>
function toggleNarrative() {
    const preview = document.getElementById('narrative-preview');
    const full = document.getElementById('narrative-full');
    const btnText = document.getElementById('btn-text');
    
    if (full.style.display === 'none') {
        // Expand
        preview.style.display = 'none';
        full.style.display = 'block';
        btnText.textContent = '📖 Collapse Story';
    } else {
        // Collapse
        preview.style.display = 'block';
        full.style.display = 'none';
        btnText.textContent = '📖 Read Full Story (3,800 words, 15 min read)';
        // Scroll back to section top
        document.querySelector('.narrative-content').scrollIntoView({ behavior: 'smooth' });
    }
}
</script>
```

**Styling Considerations:**
- Use existing glass-morphism card styles
- Narrative text: `font-size: 1rem; line-height: 1.6; color: var(--text-primary)`
- Section headings: `font-size: 1.25rem; font-weight: 600; margin-top: 1.5rem`
- Collapsible UX prevents overwhelming users
- Print-friendly (full narrative expands for PDF generation)

---

## Narrative Content Sources

Each page's narrative will be extracted from the master executive narrative document:

| Page | Extract Sections |
|------|------------------|
| index.html | ALL sections (1-7) |
| capability-catalog.html | Section 3: Key Capabilities |
| performance-metrics.html | Section 6: Technical Architecture (batch processing paragraph) |
| compliance-overview.html | Section 5: Regulatory Compliance |
| onboarding-guide.html | Sections 1-2: What Is This + Who Uses It |
| p0-issues-tracker.html | Section 5: Regulatory Compliance (compliance gaps paragraph) |
| technical-debt-roi.html | Section 6: Technical Architecture (needs NEW synthesis) |
| domain-model.html | Section 1: What Is This (entity model paragraph) |
| integration-architecture.html | Section 7: Integration Ecosystem |

---

## Success Metrics

- [ ] Index page narrative fully integrated (3,800 words collapsible)
- [ ] 5 high-priority pages have contextual narratives (200-400 words each)
- [ ] 3 medium-priority pages have focused narratives (150-250 words each)
- [ ] Collapsible UX prevents information overload
- [ ] Narratives use non-technical language
- [ ] Glass-morphism styling consistent with existing pages
- [ ] Mobile-responsive (narrative readable on phones)
- [ ] Print-friendly (expanded narrative prints correctly)

---

## Next Actions

1. ✅ Create `executive-narrative-what-this-application-does.md` (COMPLETE)
2. 🔄 Update `index.html` with full narrative section (IN PROGRESS)
3. ⏳ Extract subsections for high-priority pages
4. ⏳ Create narrative insertion script (automate HTML updates)
5. ⏳ Test collapsible UX on index page
6. ⏳ Deploy updated files to OneDrive
7. ⏳ Collect stakeholder feedback
8. ⏳ Iterate based on readability metrics

**Estimated Effort:** 4 hours (1 hr index page, 2 hrs high-priority pages, 1 hr medium-priority pages)
