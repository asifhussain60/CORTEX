# Application Health Dashboard - User Guide

**Version:** 1.0 (Option B Foundation)  
**Status:** Beta - Feedback Collection Phase  
**Last Updated:** November 29, 2025

---

## 🚀 Quick Start

### Basic Usage

```
1. Open CORTEX in your project directory
2. Say: "show health dashboard"
3. Wait 2-5 minutes for analysis
4. Review generated report in cortex-brain/documents/reports/
```

### Advanced Usage

**Scan Levels:**
```
"analyze application with overview scan"     → Fast (30 sec, file counts only)
"analyze application with standard scan"     → Balanced (2-5 min) [DEFAULT]
"analyze application with deep scan"         → Complete (5-10 min, all metrics)
```

**Specific Directory:**
```
"scan application in C:\Projects\MyApp"      → Analyze different project
```

---

## 📊 Understanding Your Report

### Summary Section

**Total Files:** Number of files analyzed (excluding .git, cache, etc.)  
**Languages Detected:** Programming languages found in your project  
**Duration:** Analysis time (varies by project size and scan level)

### File Types Breakdown

Shows distribution of file extensions. Useful for:
- Identifying project composition
- Finding unexpected file types
- Spotting configuration sprawl

### Language Breakdown

**Per-Language Metrics:**
- **Files:** Count of files in this language
- **Total Lines:** Combined line count (currently 0 - not yet implemented)
- **Functions:** Detected functions/methods
- **Classes:** Detected classes/types
- **Avg Lines/File:** Average file size

**What's Counted:**
- **Python:** AST-based analysis (accurate function/class detection)
- **C#:** Regex patterns for methods/classes
- **JavaScript/TypeScript:** Combined analysis, React/Angular patterns
- **ColdFusion:** Tag parsing, component detection
- **Other:** Generic fallback (line counting only)

---

## 🎯 Use Cases

### 1. New Project Onboarding

**Scenario:** Just joined a team, need to understand codebase structure

**Command:** `show health dashboard`

**What to look for:**
- Language distribution (primary tech stack)
- File count (project size estimate)
- Function/class counts (complexity indicator)
- File type diversity (monolithic vs modular)

### 2. Refactoring Planning

**Scenario:** Planning major refactor, need baseline metrics

**Command:** `analyze application with deep scan`

**What to look for:**
- Large files (candidates for splitting)
- Language mixing (potential cleanup targets)
- Function counts per file (complexity hotspots)

### 3. Tech Debt Assessment

**Scenario:** Quarterly review, measuring code health trends

**Command:** `show health dashboard` (run monthly)

**Track over time:**
- Total file count growth
- Average lines per file
- Function/class ratio changes
- Language distribution shifts

### 4. Migration Planning

**Scenario:** Planning Python 2 → 3 or .NET Framework → Core migration

**Command:** `scan application in C:\LegacyProject`

**What to look for:**
- Scope of work (file counts)
- Mixed language dependencies
- Configuration file locations

---

## 📈 Sample Reports Explained

### Small Project (< 1,000 files)

```
Total Files: 487
Languages Detected: 3
Duration: 12.3s

Python: 312 files, 1,245 functions, 203 classes
JavaScript: 98 files, 567 functions, 45 classes
CSS: 77 files
```

**Interpretation:**
- Primarily Python backend (64%)
- JavaScript frontend (20%)
- Styling (16%)
- Low complexity (avg 4 functions/file)

### Medium Project (1,000-10,000 files)

```
Total Files: 4,826
Languages Detected: 7
Duration: 75.72s

Python: 2,628 files, 24,652 functions, 5,070 classes
JavaScript: 6 files, 29 functions, 2 classes
Markdown: 978 files (documentation)
```

**Interpretation:**
- Python-heavy (54%)
- Well-documented (20% markdown)
- High complexity (avg 9.4 functions/file)
- Mature codebase (5K+ classes)

### Large Project (10,000+ files)

```
Total Files: 23,401
Languages Detected: 12
Duration: 234.56s (overview scan)

C#: 12,034 files, 89,234 functions, 8,901 classes
TypeScript: 7,234 files, 45,678 functions, 2,345 classes
SQL: 1,234 files
```

**Interpretation:**
- Enterprise-scale (.NET + TypeScript)
- Database-heavy (SQL files)
- Consider deep scan for full analysis
- Multi-threading active (234s for 23K files)

---

## ⚙️ Performance Expectations

**Scan Speed Factors:**
- **Project Size:** ~64 files/second (varies by file size)
- **Scan Level:** Overview 3x faster than deep
- **File Types:** Python (AST parsing) slower than simple text files
- **System:** Multi-core CPUs see 50-80% speed improvement

**Typical Scan Times:**

| Project Size | Overview | Standard | Deep |
|--------------|----------|----------|------|
| < 500 files  | 10s      | 30s      | 60s  |
| 1K-5K files  | 30s      | 2 min    | 5 min |
| 5K-10K files | 60s      | 5 min    | 10 min |
| 10K+ files   | 2 min    | 10 min   | 20 min |

**Optimization Tips:**
- Start with overview scan for quick feedback
- Use standard scan for regular monitoring
- Reserve deep scan for thorough audits
- Exclude build outputs (already ignored: node_modules, .git, etc.)

---

## 🐛 Known Limitations (Beta)

### Currently Not Implemented

1. **Line of Code Counting:** Shows 0 for all files (functions/classes work)
2. **Complexity Metrics:** Cyclomatic/cognitive complexity not calculated
3. **Code Smells:** No pattern detection yet
4. **Security Scanning:** OWASP patterns not analyzed
5. **Interactive Dashboard:** Text reports only (no D3.js visualization)
6. **Framework Detection:** No auto-detection of React/Angular/Vue/.NET versions
7. **Dependency Analysis:** No package.json/requirements.txt parsing
8. **Test Coverage Integration:** No pytest/jest coverage imports

### Planned Features (Phases 3-7)

**Phase 3: Metrics & Quality**
- Complexity calculators
- Code smell detection (7 patterns)
- OWASP security patterns
- Maintainability index

**Phase 4: Interactive Dashboard**
- D3.js visualization
- Dependency graphs
- Quality breakdown charts
- Export to PDF/PNG/PPTX

**Phase 5: Framework Detection**
- Auto-detect frameworks/versions
- Framework-specific best practices
- Version compatibility warnings

---

## 🔧 Troubleshooting

### "GenericAnalyzer.analyze() missing 1 required positional argument"

**Status:** Fixed in latest version  
**If you see this:** Update CORTEX to latest version

### "Scan taking too long"

**Solutions:**
1. Use overview scan: `analyze application with overview scan`
2. Exclude large directories (already auto-excluded: node_modules, .git)
3. Check system resources (CPU/memory usage)

### "Report shows 0 lines of code"

**Status:** Known limitation  
**Workaround:** Focus on function/class counts (these are accurate)  
**Fix:** Planned for Phase 3

### "Language not detected correctly"

**Current Support:**
- ✅ Python (.py)
- ✅ C# (.cs)
- ✅ JavaScript (.js) / TypeScript (.ts)
- ✅ ColdFusion (.cfm, .cfc)
- ⚠️ Java, Ruby, PHP, Go → Generic fallback

**Request Support:** Use feedback system to request your language

---

## 📢 Providing Feedback

### What We Need

**Positive Feedback:**
- Which metrics are most valuable?
- What insights did you gain?
- How does scan speed compare to expectations?
- Would you use this regularly?

**Improvement Suggestions:**
- What's confusing or unclear?
- Which metrics are you missing?
- What visualizations would help?
- Which languages/frameworks need support?

### How to Share

**Method 1: CORTEX Feedback Command**
```
Say: "feedback"
Fill out structured form
Auto-submits to GitHub Gist (with privacy protection)
```

**Method 2: GitHub Issues**
```
Visit: github.com/asifhussain60/CORTEX/issues
Title: [Dashboard Feedback] Your topic
Include: Project size, scan level, specific suggestions
```

**Method 3: Include in Report**
```
Edit generated report markdown
Add your comments under "Feedback Welcome" section
Share with team or CORTEX maintainers
```

---

## 📊 Beta Testing Checklist

**Help us validate the foundation by testing:**

- [ ] Run on small project (< 1K files)
- [ ] Run on medium project (1K-10K files)
- [ ] Run on large project (10K+ files) - if available
- [ ] Test all scan levels (overview, standard, deep)
- [ ] Verify language detection accuracy
- [ ] Check function/class counts against manual inspection
- [ ] Time each scan level
- [ ] Review report clarity and usefulness
- [ ] Identify missing metrics
- [ ] Suggest visualization priorities

**Share Results:**
- Project size & composition
- Scan times for each level
- Accuracy assessment
- Feature priorities (Phases 3-7)

---

## 🎯 Next Steps

**For End Users:**
1. Run dashboard on your project
2. Review generated report
3. Share feedback (3 methods above)
4. Vote on Phase 3-7 priorities

**For CORTEX Team:**
1. Collect feedback for 2 weeks
2. Analyze common requests
3. Prioritize Phase 3-7 features
4. Plan next development sprint

---

## 📚 Related Documentation

- **Planning Document:** `cortex-brain/documents/planning/features/active/PLAN-2025-11-29-APPLICATION-HEALTH-DASHBOARD-COMPREHENSIVE.md`
- **Implementation Report:** `cortex-brain/documents/reports/APPLICATION-HEALTH-DASHBOARD-OPTION-B-COMPLETE.md`
- **Progress Report:** `cortex-brain/documents/reports/APPLICATION-HEALTH-DASHBOARD-PROGRESS-REPORT.md`
- **Response Template:** `cortex-brain/response-templates.yaml` (search: `application_health`)

---

**User Guide Version:** 1.0  
**Report Generated:** November 29, 2025  
**Next Review:** After 2-week beta testing period  
**Contact:** GitHub Issues or CORTEX feedback command
