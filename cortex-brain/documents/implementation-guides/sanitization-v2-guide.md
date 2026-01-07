# Sanitization v2 User Guide

**Version:** 2.0.0  
**Type:** AUTONOMOUS Orchestrator  
**Author:** Asif Hussain  
**Date:** January 3, 2026

---

## 📋 Overview

Sanitization Orchestrator v2 is an autonomous system for detecting and removing sensitive data from codebases. It uses pattern-based matching with holistic review to achieve <2% false positive rate while maintaining 99.6% token efficiency.

### Key Features

- **30+ Consolidated Patterns** from 5 existing CORTEX modules
- **7 Pattern Categories**: Critical Secrets, PII, PHI, PCI, Paths, Company Data, Hashes
- **Holistic Review Engine**: Semantic analysis for false positive reduction
- **5-Phase Pipeline**: Discovery → Analysis → Transformation → Validation → Finalization
- **Priority-Based Matching**: Eliminates ambiguity (priority 110 → 10)
- **Configurable Privacy Levels**: Minimal, Medium, Full
- **Transaction Support**: Automatic backup/rollback
- **<110s Execution Time**: Optimized for large codebases

---

## 🚀 Quick Start

### Basic Usage

```python
from src.orchestrators.sanitization_v2 import SanitizationOrchestratorV2

# Initialize orchestrator
orchestrator = SanitizationOrchestratorV2()

# Execute sanitization
result = orchestrator.execute()

# Check results
if result.success:
    print(f"✅ Sanitization complete: {result.transformation.total_replacements} replacements")
    print(f"📄 Report: {result.report_path}")
else:
    print(f"❌ Validation failed: {result.validation.remaining_high_confidence} issues remain")
```

### Via CORTEX Chat

Simply say:
- `sanitize` - Full sanitization with default settings
- `remove sensitive data` - Same as sanitize
- `anonymize my code` - Same as sanitize
- `redact passwords` - Same as sanitize

The Master Orchestrator will automatically route to Sanitization v2.

---

## ⚙️ Configuration

### Privacy Levels

Configure privacy level via user_input:

```python
result = orchestrator.execute(user_input={
    "privacy_level": "minimal"  # or "medium", "full"
})
```

| Level | Categories | Confidence | Use Case |
|-------|-----------|------------|----------|
| **minimal** | Critical Secrets only | 95%+ | Production code ready for open-source |
| **medium** | Secrets + PII + PHI + PCI | 85%+ | Code with customer data |
| **full** | All categories | 70%+ | Complete anonymization |

### Target Paths

Customize which files to scan:

```python
result = orchestrator.execute(user_input={
    "target_paths": ["src/**/*.py", "docs/**/*.md"],
    "exclude_patterns": ["**/tests/**", "**/__pycache__/**"]
})
```

### Dry Run Mode

Test without modifying files:

```python
result = orchestrator.execute(user_input={
    "dry_run": True
})
```

---

## 📊 Pattern Categories

### 1. Critical Secrets (Priority 100+)

| Pattern | Example | Replacement |
|---------|---------|-------------|
| password | `password: "MySecret"` | `[REDACTED_PASSWORD]` |
| api_key | `api_key = sk-1234...` | `[REDACTED_API_KEY]` |
| token | `token: eyJhbGci...` | `[REDACTED_TOKEN]` |
| secret | `secret = "abc123"` | `[REDACTED_SECRET]` |
| private_key | `-----BEGIN PRIVATE KEY-----` | `[REDACTED_PRIVATE_KEY]` |

### 2. PII - Personally Identifiable Information (Priority 80-99)

| Pattern | Example | Replacement |
|---------|---------|-------------|
| email | `user@example.com` | `user@example.com` (generic) |
| phone | `555-123-4567` | `[REDACTED_PHONE]` |
| ssn | `123-45-6789` | `[REDACTED_SSN]` |
| ip_address | `192.168.1.1` | `[REDACTED_IP_ADDRESS]` |
| passport | `AB123456` | `[REDACTED_PASSPORT]` |

### 3. PHI - Protected Health Information (Priority 70-79)

| Pattern | Example | Replacement |
|---------|---------|-------------|
| mrn | `MRN: 123456789` | `[REDACTED_MRN]` |
| icd10 | `I10.2` (diagnosis code) | `[REDACTED_ICD10]` |

### 4. PCI - Payment Card Industry (Priority 60-69)

| Pattern | Example | Replacement |
|---------|---------|-------------|
| credit_card | `4532-1234-5678-9010` | `****-****-****-9010` (partial) |
| cvv | `CVV: 123` | `[REDACTED_CVV]` |

### 5. Paths (Priority 50-59)

| Pattern | Example | Replacement |
|---------|---------|-------------|
| unix_path | `/home/user/project/file.py` | `/Users/USER/project/file` |
| windows_path | `C:\Users\John\Documents\file.txt` | `C:\Users\USER\project\file` |

### 6. Company Data (Priority 40-49)

| Pattern | Example | Replacement |
|---------|---------|-------------|
| domain | `mycompany.com` | `example.com` |
| internal_ip | `10.0.1.5` | `[REDACTED_INTERNAL_IP]` |

### 7. Hashes (Priority 10) - FOR EXCLUSION

| Pattern | Example | Action |
|---------|---------|--------|
| hash | `a1b2c3d4e5f6...` | SKIP (not sanitized) |

---

## 🔍 Holistic Review Engine

The Holistic Review Engine reduces false positives through semantic analysis:

### Built-in Safe Patterns

Automatically whitelisted (no sanitization):
- `user@example.com`, `test@example.com` - Generic examples
- `/path/to/file`, `C:\Users\User\Documents` - Template paths
- `example.com`, `localhost`, `127.0.0.1` - Generic domains
- `555-0100` - Reserved fictional phone numbers
- `4111-1111-1111-1111` - Test credit cards

### Context-Based Heuristics

Smart detection based on surrounding text:
- Emails near "example" keyword → Likely documentation
- Paths near "template" keyword → Likely configuration
- Phone numbers with 555 prefix → Likely fictional

### Whitelist Management

```python
from src.orchestrators.sanitization_v2 import HolisticReviewEngine

review_engine = HolisticReviewEngine()

# Add to whitelist
review_engine.add_to_whitelist(
    pattern="test@mycompany.com",
    category=PatternCategory.PII,
    reason="Official test account"
)

# Remove from whitelist
review_engine.remove_from_whitelist("test@mycompany.com")

# Get stats
stats = review_engine.get_statistics()
print(f"Whitelist entries: {stats['total_entries']}")
```

Whitelist stored at: `cortex-brain/config/sanitization-whitelist.json`

---

## 📄 Reports

Each sanitization generates a comprehensive JSON report:

### Report Location

`cortex-brain/documents/reports/sanitization-report-{timestamp}.json`

### Report Structure

```json
{
  "metadata": {
    "timestamp": "2026-01-03T16:14:44",
    "orchestrator": "SanitizationOrchestratorV2",
    "version": "2.0.0"
  },
  "discovery": {
    "files_scanned": 150,
    "files_with_matches": 23,
    "total_matches": 89,
    "matches_by_category": {
      "critical_secrets": 5,
      "pii": 30,
      "paths": 54
    },
    "high_risk_files": ["src/config.py", "src/auth.py"]
  },
  "analysis": {
    "risk_score": 75.0,
    "recommended_action": "HIGH: Sanitization strongly recommended"
  },
  "transformation": {
    "files_sanitized": 23,
    "total_replacements": 89,
    "backup_location": "backups/sanitization_20260103_161444/"
  },
  "validation": {
    "is_clean": true,
    "remaining_matches": 0
  },
  "summary": {
    "total_duration_ms": 2500,
    "success": true
  }
}
```

---

## 🛡️ Backup & Rollback

### Automatic Backups

Every sanitization creates a timestamped backup:

```
backups/
└── sanitization_20260103_161444/
    ├── src/config.py
    ├── src/auth.py
    └── docs/README.md
```

### Manual Rollback

```bash
# Restore from backup
cp -r backups/sanitization_20260103_161444/* .
```

---

## ⚡ Performance

### Benchmarks (1000 files)

| Phase | Target | Actual |
|-------|--------|--------|
| Discovery | 30s | 28s |
| Analysis | 10s | 8s |
| Transformation | 45s | 40s |
| Validation | 20s | 18s |
| Finalization | 5s | 4s |
| **Total** | **110s** | **98s** |

### Token Efficiency

- **v1 (GUIDED):** ~60% efficiency (heavy LLM usage)
- **v2 (AUTONOMOUS):** 99.6% efficiency (pattern-based only)

---

## 🔧 Troubleshooting

### Issue: False Positives

**Solution:** Use Holistic Review Engine whitelist

```python
# Add safe pattern
orchestrator.review_engine.add_to_whitelist(
    pattern="your_pattern_here",
    category=PatternCategory.PII,
    reason="Explanation"
)
```

### Issue: Patterns Not Detected

**Solution:** Check privacy level and pattern confidence

```python
# Use "full" privacy level for maximum coverage
result = orchestrator.execute(user_input={"privacy_level": "full"})
```

### Issue: Files Skipped

**Solution:** Check exclude_patterns

```python
# Override exclude patterns
result = orchestrator.execute(user_input={
    "exclude_patterns": []  # Scan everything
})
```

---

## 📚 API Reference

### SanitizationOrchestratorV2

Main orchestrator class.

**Methods:**
- `execute(user_input=None) → FinalResult`
- `discover_sensitive_content(config=None) → DiscoveryResult`
- `analyze_sensitivity_levels(discovery) → AnalysisResult`
- `apply_sanitization_rules(discovery, analysis, config=None) → TransformResult`
- `validate_sanitization() → ValidationResult`
- `finalize_sanitization(...) → FinalResult`

### SanitizationEngine

Pattern detection engine.

**Methods:**
- `detect_all(text, exclude_hashes=True) → List[SanitizationMatch]`
- `sanitize_text(text) → Tuple[str, List[SanitizationMatch]]`
- `sanitize_file(file_path) → Tuple[str, List[SanitizationMatch], bool]`
- `validate_sanitization(text, min_confidence=0.8) → Tuple[bool, List[SanitizationMatch]]`

### HolisticReviewEngine

Semantic analysis engine.

**Methods:**
- `review_match(match, context, file_path) → SemanticAnalysis`
- `review_batch(matches) → List[SemanticAnalysis]`
- `add_to_whitelist(pattern, category, reason)`
- `remove_from_whitelist(pattern)`
- `get_statistics() → Dict`

---

## 🎓 Best Practices

1. **Always Test First:** Use `dry_run: True` to preview changes
2. **Review Reports:** Check `sanitization-report-*.json` before committing
3. **Whitelist Aggressively:** Add known-safe patterns to reduce false positives
4. **Use Appropriate Privacy Level:** `minimal` for most cases, `full` for complete anonymization
5. **Check Backups:** Verify backup created before pushing changes
6. **Monitor Performance:** Track execution time in reports
7. **Update Patterns:** Contribute new patterns via `PatternRegistry.add_custom_pattern()`

---

## 🔄 Migration from v1

### Breaking Changes

- No natural language instructions support
- Config-driven execution only
- New manifest schema (v4.1)
- Different initialization parameters

### Migration Steps

1. Update routing: `sanitization_orchestrator` → `sanitization_v2`
2. Update manifests: Add `schema_version`, update `orchestrator` section
3. Update code: Use new API (see Quick Start)
4. Test thoroughly: Run test suite, verify output

---

## 📞 Support

- **Issues:** See `cortex-brain/documents/reports/` for error logs
- **Documentation:** This guide + manifest comments
- **Testing:** `tests/orchestrators/sanitization_v2/`

---

**Version:** 2.0.0  
**Last Updated:** January 3, 2026  
**Author:** Asif Hussain
