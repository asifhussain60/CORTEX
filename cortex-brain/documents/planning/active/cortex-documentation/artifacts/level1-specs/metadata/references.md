# References - Level 1 Specification

**Document:** Level1-spec.md v4.0.0  
**Last Updated:** January 2, 2026

---

## 📚 Internal Documentation References

### Core CORTEX Documentation
- **Main Site:** `docs/index.html` (Level 0 home page)
- **Glassmorphism Standard:** `glassmorphism-design-standard.md`
- **Main CSS:** `docs/assets/css/main.css`
- **HTML Templates:** `templates/level1-detail-page.html`

### Related Specifications
- **Planning System Manifest:** `cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml`
- **Response Templates:** `cortex-brain/response-templates-v4.yaml`
- **Brain Protection Rules:** `cortex-brain/brain-protection-rules.yaml`

### Implementation Guides
- **Page Creation:** `level1-specs/implementation/page-creation-guide.md` (planned v4.1.0)
- **Visualization Guide:** `level1-specs/implementation/visualization-guide.md` (planned v4.1.0)
- **CSS Integration:** `level1-specs/implementation/css-integration-guide.md` (planned v4.1.0)

---

## 🔗 External References

### Design & UX
- **Glassmorphism:** https://glassmorphism.com/
- **Material Design:** https://material.io/design
- **Apple Human Interface Guidelines:** https://developer.apple.com/design/human-interface-guidelines/
- **Web Content Accessibility Guidelines (WCAG 2.1):** https://www.w3.org/WAI/WCAG21/quickref/

### Visualization Libraries
- **Mermaid.js:** https://mermaid.js.org/
  - Version: 10.x
  - CDN: `https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js`
- **D3.js:** https://d3js.org/
  - Version: 7.x
  - CDN: `https://d3js.org/d3.v7.min.js`

### CSS & Styling
- **CSS Variables Guide:** https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties
- **CSS Grid Layout:** https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout
- **Flexbox Guide:** https://css-tricks.com/snippets/css/a-guide-to-flexbox/

### Security Standards
- **OWASP Top 10 (2021):** https://owasp.org/Top10/
- **STRIDE Threat Modeling:** https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats
- **MITRE ATT&CK Framework:** https://attack.mitre.org/
- **CVE Database:** https://cve.mitre.org/
- **CVSS Scoring:** https://www.first.org/cvss/

### Compliance Frameworks
- **GDPR:** https://gdpr.eu/
- **SOC 2:** https://www.aicpa.org/interestareas/frc/assuranceadvisoryservices/sorhome.html
- **ISO 27001:** https://www.iso.org/isoiec-27001-information-security.html
- **HIPAA:** https://www.hhs.gov/hipaa/index.html
- **PCI-DSS:** https://www.pcisecuritystandards.org/

### Performance & Optimization
- **Web Vitals:** https://web.dev/vitals/
- **Lighthouse:** https://developers.google.com/web/tools/lighthouse
- **PageSpeed Insights:** https://pagespeed.web.dev/

### Development Tools
- **Font Awesome (Icons):** https://fontawesome.com/
  - Version: 6.4.0
  - CDN: `https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css`

---

## 🛠️ Development Tools & Validation

### Validation Scripts
- **Decomposition Validator:** `cortex-toolkit/scripts/validate_decomposition.ps1`
- **Documentation Validator:** `validate_docs.ps1` (see validation-checklist.md)
- **Inline Styles Checker:** `grep -r 'style="' docs/**/*.html`

### Browser DevTools
- **Chrome DevTools:** https://developer.chrome.com/docs/devtools/
- **Firefox Developer Tools:** https://firefox-source-docs.mozilla.org/devtools-user/
- **Safari Web Inspector:** https://developer.apple.com/safari/tools/

### Testing Tools
- **Link Checker:** https://validator.w3.org/checklink
- **HTML Validator:** https://validator.w3.org/
- **CSS Validator:** https://jigsaw.w3.org/css-validator/

---

## 📊 Data Sources

### Complexity Scoring Methodology
Complexity score calculated based on:
1. **Number of sections** (×1 point each)
2. **Mermaid diagrams** (×5 points each)
3. **D3.js visualizations** (×10 points each)
4. **Interactive elements** (×3 points each)
5. **Code examples** (×2 points each)

**Formula:**
```
Complexity = (Sections × 1) + (Mermaid × 5) + (D3 × 10) + (Interactive × 3) + (Code × 2)
```

**Thresholds:**
- **Level 1:** Complexity < 100 (single page)
- **Level 2:** Complexity ≥ 100 (requires decomposition)

### File Size Analysis
- **Source:** PowerShell `Get-Item` command
- **Measurement:** Bytes, converted to KB
- **Baseline:** January 1, 2026 file scan

---

## 🔄 Related Projects

### CORTEX Ecosystem
- **CORTEX Main Repository:** https://github.com/asifhussain60/CORTEX
- **CORTEX Documentation Site:** https://asifhussain60.github.io/CORTEX/
- **Toolkit Manager:** `cortex-toolkit/`
- **Planning System:** `src/orchestrators/planning_orchestrator.py`

### Dependencies
- **Python:** 3.11+
- **PowerShell:** 7.0+
- **Node.js:** 18+ (for build tools)

---

## 📧 Contact & Support

### Maintainer
- **Name:** Asif Hussain
- **Website:** https://asifhussain60.github.io/CORTEX/
- **Repository:** https://github.com/asifhussain60/CORTEX

### Documentation Issues
For issues with this specification or related documentation:
1. Check version history for updates
2. Review validation checklist
3. Consult related specifications
4. Create issue with [DOC] prefix

---

## 📝 Document Standards

### Markdown Conventions
- **Headers:** ATX-style (`#`, `##`, etc.)
- **Code Blocks:** Fenced with language identifier
- **Tables:** GitHub-flavored Markdown
- **Links:** Reference-style for repeated URLs
- **Emoji:** Used sparingly for visual hierarchy

### File Naming Conventions
- **Specs:** `{name}-spec.md`
- **Guides:** `{name}-guide.md`
- **Standards:** `{name}-standard.md`
- **Checklists:** `{name}-checklist.md`
- **History:** `version-history.md`
- **References:** `references.md`

---

**Last Verified:** January 2, 2026  
**Next Review:** March 2026 (quarterly)
