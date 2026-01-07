# Phase 5 Execution Plan: Knowledge File Pages
**Date:** December 28, 2025  
**Status:** IN PROGRESS  
**Target:** 34 individual knowledge file detail pages

---

## 🎯 Objective

Build Level 4 pages in the information hierarchy: individual knowledge file detail pages that deep-dive into specific topics with actionable content.

**Navigation Flow:**
```
Home → Knowledge Library → Category Page → Knowledge File Page
                                           (You are here)
```

---

## 📊 File Inventory

**Total Knowledge Files:** 34 unique YAML files

### By Category

| Category | Files | Knowledge Files |
|----------|-------|----------------|
| **Engineering** | 8 | solid-principles, design-patterns, clean-code, refactoring, code-review, anti-patterns, rest-api-design, graphql-best-practices, api-versioning |
| **Testing** | 4 | tdd-best-practices, testing-pyramid, test-doubles, selenium-to-playwright-migration |
| **Security** | 3 | secure-coding-practices, owasp-top-10, api-security-checklist |
| **DDD** | 3 | bounded-contexts, domain-events, aggregates-entities |
| **Performance** | 3 | caching-strategies, optimization-techniques, profiling-analysis |
| **DevOps** | 3 | cicd-pipelines, monitoring-observability, infrastructure-as-code |
| **RAG Domains** | 4 | domain-rag-integration, retrieval-pipeline, vector-database-guide, embeddings-strategy |
| **Cloud** | 1 | aws-best-practices |
| **Database** | 1 | oracle-best-practices |
| **Microservices** | 1 | resilience-patterns |
| **Frontend** | 1 | react-best-practices |
| **UI-UX** | 1 | ui-ux-best-practices |
| **Mobile** | 1 | TBD (no YAML files found) |
| **Messaging** | 0 | TBD (no YAML files found) |
| **Containers** | 0 | TBD (no YAML files found) |

**TOTAL:** 34 files (3 categories have no knowledge files yet)

---

## 🏗️ Page Structure

Each knowledge file page follows a **4-tab layout**:

### Tab 1: Overview
- **Purpose:** Quick summary and key takeaways
- **Content:** 
  - Title + subtitle
  - Description (2-3 paragraphs)
  - Key concepts list (4-6 items)
  - When to use / When to avoid

### Tab 2: Content
- **Purpose:** Deep-dive into the topic with actionable details
- **Content:**
  - Core principles (5-8 principles)
  - Implementation patterns
  - Best practices
  - Common pitfalls
  - Anti-patterns to avoid

### Tab 3: Examples
- **Purpose:** Concrete code examples and case studies
- **Content:**
  - Code snippets (2-4 examples)
  - Real-world scenarios
  - Before/After comparisons
  - Integration patterns

### Tab 4: CORTEX Usage
- **Purpose:** How CORTEX leverages this knowledge
- **Content:**
  - Implementation examples from CORTEX codebase
  - Related CORTEX components
  - How to query this knowledge
  - Related knowledge files

---

## 🎨 Design Requirements

**CSS Compliance:**
- ✅ Single CSS file: `../assets/css/main.css` ONLY
- ❌ NO inline styles (`style=""` attributes)
- ❌ NO additional CSS files
- ✅ Use CSS variables from theme
- ✅ Dark blue glassmorphism (#0a0e27 → #1a1f3a)

**Theme Variables:**
```css
--bg-primary: #0a0e27
--bg-secondary: #1a1f3a
--glass-bg: rgba(255,255,255,0.05)
--accent-primary: #00d4ff
--accent-secondary: #7b2ff7
```

**HTML Structure:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{File Name} | CORTEX Knowledge</title>
    <link rel="stylesheet" href="../../assets/css/main.css">
</head>
<body>
    <header class="header-glass">
        <!-- Breadcrumb navigation -->
    </header>
    
    <main class="main-content">
        <section class="knowledge-file-hero">
            <!-- Title, subtitle, metadata -->
        </section>
        
        <section class="tab-container">
            <!-- 4-tab layout -->
        </section>
    </main>
    
    <footer class="footer-glass">
        <!-- Footer content -->
    </footer>
</body>
</html>
```

---

## 🚀 Build Order

**Priority 1: Engineering (8 files)**
- Largest category, foundational content
- Start with: `solid-principles.html` (most referenced)

**Priority 2: Testing (4 files)**
- Critical for TDD workflow
- Start with: `tdd-best-practices.html`

**Priority 3: Security (3 files)**
- High-value content
- Start with: `secure-coding-practices.html`

**Priority 4: DDD + Performance + DevOps (9 files)**
- Medium-sized categories
- Build in parallel batches

**Priority 5: RAG Domains (4 files)**
- CORTEX-specific content
- Start with: `domain-rag-integration.html`

**Priority 6: Remaining (6 files)**
- Single-file categories
- Build as final batch

---

## ✅ Quality Criteria

**Per-Page Validation:**
1. HTML syntax valid (DOCTYPE, proper structure)
2. CSS compliance 100% (single main.css, zero inline styles)
3. 4-tab layout functional (JavaScript tab switching)
4. Breadcrumb navigation working
5. Links to parent category page and knowledge library
6. Content sourced from YAML knowledge files

**Phase 5.5 Quality Review:**
- HTML validation: 34/34 pages PASS
- CSS compliance: 34/34 pages 100%
- Compliance matrix report generated
- Master plan updated
- Git commit with validation results

---

## 📁 File Paths

**Knowledge file pages location:**
```
docs/knowledge/files/{category}/{file-name}.html
```

**Examples:**
```
docs/knowledge/files/engineering/solid-principles.html
docs/knowledge/files/testing/tdd-best-practices.html
docs/knowledge/files/security/secure-coding-practices.html
docs/knowledge/files/ddd/bounded-contexts.html
docs/knowledge/files/performance/caching-strategies.html
docs/knowledge/files/devops/cicd-pipelines.html
docs/knowledge/files/rag-domains/domain-rag-integration.html
docs/knowledge/files/cloud/aws-best-practices.html
docs/knowledge/files/database/oracle-best-practices.html
docs/knowledge/files/microservices/resilience-patterns.html
docs/knowledge/files/frontend/react-best-practices.html
docs/knowledge/files/ui-ux/ui-ux-best-practices.html
```

**Source YAML files:**
```
cortex-brain/knowledge/{category}/{file-name}.yaml
```

---

## 📈 Progress Tracking

**Phase 5 Milestones:**
- [ ] Engineering (8 files) - 0/8 = 0%
- [ ] Testing (4 files) - 0/4 = 0%
- [ ] Security (3 files) - 0/3 = 0%
- [ ] DDD (3 files) - 0/3 = 0%
- [ ] Performance (3 files) - 0/3 = 0%
- [ ] DevOps (3 files) - 0/3 = 0%
- [ ] RAG Domains (4 files) - 0/4 = 0%
- [ ] Remaining (6 files) - 0/6 = 0%

**Overall Progress:** 0/34 pages = 0%

**Phase 5.5 Quality Review:** NOT STARTED

---

## 🎓 Next Steps

1. **Create first knowledge file page:** `solid-principles.html`
2. **Read source YAML:** `cortex-brain/knowledge/engineering/solid-principles.yaml`
3. **Build 4-tab layout:** Overview, Content, Examples, CORTEX Usage
4. **Validate CSS compliance:** Run `validate_css_compliance.sh`
5. **Test in browser:** Verify tab switching and navigation
6. **Commit:** Push first knowledge file page
7. **Repeat:** Build next 33 pages following same pattern

---

**Status:** Ready to begin Phase 5 execution  
**First Target:** `docs/knowledge/files/engineering/solid-principles.html`
