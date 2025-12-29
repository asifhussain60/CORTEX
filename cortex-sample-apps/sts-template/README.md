# STS Template Application

**Version:** 1.0  
**Purpose:** CORTEX 4.0 Capability Validation (Sharpen The Saw)  
**Status:** 🏗️ UNDER CONSTRUCTION

---

## Overview

This is a deliberately flawed e-commerce application designed to validate CORTEX 4.0's critical capabilities. The application contains **40 documented flaws** across 6 categories, providing a realistic testbed for deployment, end-to-end workflows, upgrade paths, and multi-IDE support validation.

**DO NOT use this code in production.** It is intentionally insecure and poorly designed for testing purposes only.

---

## Quick Start

### Instantiation (< 30 minutes)

```bash
# 1. Clone template to working directory
cp -r cortex-sample-apps/sts-template /tmp/sts-app-$(date +%Y%m%d)
cd /tmp/sts-app-$(date +%Y%m%d)

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run application (for testing only)
python src/app.py

# 5. Run CORTEX validation
cd /path/to/CORTEX
python scripts/run_sts_validation.py --app-path /tmp/sts-app-$(date +%Y%m%d)
```

---

## Architecture

### Layer Structure

```
src/
├── api/           # REST API endpoints (security, validation issues)
├── business/      # Business logic (SOLID violations, duplication)
├── data/          # Data access (SQL injection, connection issues)
└── utils/         # Utilities (god objects, complexity)
```

### Intentional Flaws (40 total)

**See `STS-MANIFEST.json` for complete catalog.**

**Category Breakdown:**
- Security Issues: 10 flaws (hardcoded secrets, SQL injection, weak auth)
- SOLID Violations: 8 flaws (god classes, tight coupling, no interfaces)
- Code Quality: 10 flaws (high complexity, duplication, dead code)
- Performance: 6 flaws (N+1 queries, no caching, memory leaks)
- Testing Gaps: 4 flaws (placeholder tests, missing files)
- Documentation: 2 flaws (outdated, incomplete)

---

## Usage

### Validation Capabilities

This template validates **8 critical CORTEX capabilities**:

1. **Deployment Pipeline** - Build, install, publish, first-run
2. **Multi-Workspace** - VSCode, Visual Studio, GitHub Copilot detection
3. **Upgrade Path** - 3.0→4.0 migration with rollback
4. **End-to-End Workflows** - Multi-orchestrator chains
5. **Brain Persistence** - Failure recovery, integrity
6. **Agent Collaboration** - Handoffs, context preservation
7. **Performance Baseline** - Scale, latency, memory
8. **Regression Detection** - Baseline comparison, CI/CD

### Baseline Metrics

**Before CORTEX transformation:**
- Security Score: 2/10 (10 vulnerabilities)
- SOLID Compliance: 3/10 (8 violations)
- Code Quality: 3/10 (complexity avg 55)
- Test Coverage: 15%
- Documentation: D grade

**After CORTEX transformation (target):**
- Security Score: 9/10 (0 critical vulnerabilities)
- SOLID Compliance: 8/10 (0 violations)
- Code Quality: 8/10 (complexity avg <20)
- Test Coverage: 85%+
- Documentation: B+ grade

---

## Maintenance

### Update Frequency

- **Major Updates:** 1-2x per year (align with CORTEX architecture changes)
- **Minor Updates:** As needed (add new flaw types)
- **Baseline Refresh:** After major updates

### Versioning

- v1.0 - Initial template (40 flaws, 6 categories)
- Future versions will add complexity as CORTEX capabilities expand

---

## Related Documentation

- **STS Plan:** `cortex-brain/documents/planning/active/CORTEX-3.0-4.0/phase-13-sharpen-the-saw-plan.md`
- **Value Analysis:** `cortex-brain/documents/analysis/phase-13b-sts-value-analysis.md`
- **Usage Guide:** `cortex-brain/documents/guides/STS-USAGE.md` (coming soon)
- **Certification Guide:** `cortex-brain/documents/guides/STS-CERTIFICATION.md` (coming soon)

---

## Status

**Current Phase:** Week 1 Day 1 - Template Creation  
**Completion:** 10% (structure created, implementation pending)  
**Next:** Implement Flask application with 40 documented flaws
