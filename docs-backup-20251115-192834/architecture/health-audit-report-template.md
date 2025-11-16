# CORTEX Health Audit Report Template

**Version:** 1.0  
**Generated:** {{timestamp}}  
**Scan Duration:** {{scan_duration}}  
**CORTEX Version:** {{cortex_version}}

---

# 📊 Executive Summary

## System Health Score: {{health_score}}/100

{{#health_score_badge}}
{{#if (gte health_score 90)}}🟢 **EXCELLENT** - System is operating optimally{{/if}}
{{#if (and (gte health_score 70) (lt health_score 90))}}🟡 **GOOD** - Minor issues detected, system stable{{/if}}
{{#if (and (gte health_score 50) (lt health_score 70))}}🟠 **FAIR** - Several issues need attention{{/if}}
{{#if (lt health_score 50)}}🔴 **POOR** - Critical issues require immediate action{{/if}}
{{/health_score_badge}}

## Issue Overview

| Severity | Count | % of Total | Trend |
|----------|--------|------------|-------|
| 🚨 CRITICAL | {{critical_count}} | {{critical_percentage}}% | {{critical_trend}} |
| 🔴 HIGH | {{high_count}} | {{high_percentage}}% | {{high_trend}} |
| 🟠 MEDIUM | {{medium_count}} | {{medium_percentage}}% | {{medium_trend}} |
| 🟡 LOW | {{low_count}} | {{low_percentage}}% | {{low_trend}} |
| ℹ️ INFO | {{info_count}} | {{info_percentage}}% | {{info_trend}} |
| **TOTAL** | **{{total_issues}}** | **100%** | {{overall_trend}} |

## Top Priority Issues (Fix First)

{{#each top_priority_issues}}
### {{@index}}. {{title}} {{severity_emoji}}

**Category:** {{category}} | **Priority Score:** {{priority_score}}/100 | **Est. Fix Time:** {{estimated_fix_time}}

{{description}}

**Impact:** {{impact_description}}

**Quick Fix:** {{#if quick_fix}}✅ {{quick_fix}}{{else}}❌ Requires detailed analysis{{/if}}

---
{{/each}}

## Health Trends

{{#if has_historical_data}}
- **Improvement Rate:** {{improvement_rate}} issues resolved/week
- **New Issue Rate:** {{new_issue_rate}} issues introduced/week
- **Health Score Change:** {{health_score_change}} ({{health_score_change_period}})
- **Critical Issue Resolution Time:** {{critical_resolution_time}} avg
{{else}}
*No historical data available. This is the baseline health assessment.*
{{/if}}

## Recommended Actions

### 🚨 Immediate (Within 24 hours)
{{#each immediate_actions}}
- [ ] {{description}} ({{estimated_time}})
{{/each}}

### 📅 Short-term (Within 1 week) 
{{#each short_term_actions}}
- [ ] {{description}} ({{estimated_time}})
{{/each}}

### 🎯 Strategic (Within 1 month)
{{#each strategic_actions}}
- [ ] {{description}} ({{estimated_time}})
{{/each}}

---

# 🔍 Detailed Analysis

## By System Component

### 🛡️ Tier 0: Governance & Protection
{{> tier_analysis tier=tier0_analysis}}

### 🧠 Tier 1: Working Memory
{{> tier_analysis tier=tier1_analysis}}

### 📊 Tier 2: Knowledge Graph
{{> tier_analysis tier=tier2_analysis}}

### 🔄 Tier 3: Development Context
{{> tier_analysis tier=tier3_analysis}}

### 🤖 Agent System
{{> agent_analysis agents=agent_analysis}}

### 🔌 Plugin System
{{> plugin_analysis plugins=plugin_analysis}}

### 🧪 Testing & Quality
{{> test_analysis tests=test_analysis}}

### 📚 Documentation
{{> documentation_analysis docs=documentation_analysis}}

### ⚙️ Configuration
{{> configuration_analysis config=configuration_analysis}}

### 🚀 Operations
{{> operations_analysis ops=operations_analysis}}

### 🔒 Security
{{> security_analysis security=security_analysis}}

---

# 📋 Priority Matrix

## Critical Path Analysis

```
High Impact, High Urgency     │ High Impact, Low Urgency
                              │
{{critical_urgent_issues}}    │ {{critical_not_urgent_issues}}
                              │
──────────────────────────────┼──────────────────────────────
                              │
Low Impact, High Urgency      │ Low Impact, Low Urgency
                              │
{{not_critical_urgent_issues}}│ {{not_critical_not_urgent_issues}}
```

## Dependency Analysis

{{#each dependency_clusters}}
### {{cluster_name}}

**Issues in this cluster:** {{issue_count}}  
**Resolution Strategy:** {{strategy}}

{{#each issues}}
- {{title}} → **{{dependent_issues.length}}** dependent issue(s)
{{/each}}

**Recommended Fix Order:**
{{#each fix_order}}
{{@index}}. {{title}} ({{estimated_time}})
{{/each}}

---
{{/each}}

# 🎯 Action Plan

## Phase 1: Critical Issues (Week 1)

{{#each phase1_tasks}}
### Task {{@index}}: {{title}}

**Objective:** {{objective}}  
**Success Criteria:** {{success_criteria}}  
**Estimated Time:** {{estimated_time}}  
**Assigned Component:** {{component}}

**Steps:**
{{#each steps}}
{{@index}}. {{description}}
{{/each}}

**Risk Factors:**
{{#each risks}}
- ⚠️ {{description}} (Mitigation: {{mitigation}})
{{/each}}

**Dependencies:** {{#if dependencies}}{{dependencies}}{{else}}None{{/if}}

---
{{/each}}

## Phase 2: High Priority Issues (Week 2-3)

{{#each phase2_tasks}}
### Task {{@index}}: {{title}}

**Objective:** {{objective}}  
**Estimated Time:** {{estimated_time}}  
**Component:** {{component}}

**Quick Summary:** {{summary}}

---
{{/each}}

## Phase 3: Optimization & Enhancement (Week 4+)

{{#each phase3_tasks}}
### Task {{@index}}: {{title}}

**Objective:** {{objective}}  
**Estimated Time:** {{estimated_time}}  
**Component:** {{component}}
**ROI:** {{roi_description}}

---
{{/each}}

# 📈 Metrics & KPIs

## Current State

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Overall Health Score** | {{health_score}}/100 | 85+ | {{health_status}} |
| **Critical Issues** | {{critical_count}} | 0 | {{critical_status}} |
| **Test Coverage** | {{test_coverage}}% | 90%+ | {{coverage_status}} |
| **Documentation Coverage** | {{doc_coverage}}% | 80%+ | {{doc_status}} |
| **Security Score** | {{security_score}}/100 | 95+ | {{security_status}} |
| **Performance Score** | {{performance_score}}/100 | 80+ | {{perf_status}} |

## Progress Tracking

Copy this checklist to track your progress:

```markdown
## Health Audit Progress Tracker

### Critical Issues ({{critical_count}} total)
{{#each critical_issues}}
- [ ] {{title}} ({{estimated_fix_time}})
{{/each}}

### High Priority Issues ({{high_count}} total)
{{#each high_priority_issues}}
- [ ] {{title}} ({{estimated_fix_time}})
{{/each}}

### Medium Priority Issues ({{medium_count}} total)
- [ ] Review and prioritize medium issues
- [ ] Address blocking medium issues first
- [ ] Schedule remaining for future sprints

### System Health Goals
- [ ] Achieve 85+ health score
- [ ] Zero critical issues
- [ ] 90%+ test coverage
- [ ] 80%+ documentation coverage
- [ ] All security vulnerabilities resolved
```

# 🔧 Technical Details

## Scanner Configuration

{{#each scanners}}
### {{name}} Scanner

**Status:** {{status}}  
**Issues Found:** {{issues_found}}  
**Scan Time:** {{scan_time}}  
**Configuration:**

```yaml
{{configuration}}
```

**Notes:** {{notes}}

---
{{/each}}

## Issue Detection Algorithms

{{#each detection_algorithms}}
### {{category}} Detection

**Method:** {{method}}  
**Accuracy:** {{accuracy}}%  
**False Positive Rate:** {{false_positive_rate}}%  
**Pattern Confidence:** {{confidence}}

---
{{/each}}

# 📚 Appendices

## Appendix A: Full Issue Inventory

{{#each all_issues_by_category}}
### {{category_name}} ({{issues.length}} issues)

{{#each issues}}
#### {{id}}: {{title}} {{severity_emoji}}

**Severity:** {{severity}} | **Type:** {{issue_type}} | **Priority:** {{priority_score}}/100

{{description}}

{{#if file_path}}**Location:** `{{file_path}}`{{#if line_number}}:{{line_number}}{{/if}}{{/if}}

**Suggestions:**
{{#each suggestions}}
- {{.}}
{{/each}}

{{#if related_issues}}**Related Issues:** {{related_issues}}{{/if}}

---
{{/each}}
{{/each}}

## Appendix B: Scanner Details

### Scanner Performance

| Scanner | Runtime | Memory Usage | Issues Found | Accuracy |
|---------|---------|--------------|--------------|----------|
{{#each scanner_performance}}
| {{name}} | {{runtime}} | {{memory}} | {{issues}} | {{accuracy}}% |
{{/each}}

### Configuration Files Analyzed

{{#each config_files}}
- **{{file_path}}** - {{status}} ({{last_modified}})
{{/each}}

## Appendix C: Historical Comparison

{{#if historical_data}}
### Previous Health Reports

| Date | Health Score | Critical Issues | Total Issues | Notes |
|------|--------------|-----------------|--------------|-------|
{{#each historical_reports}}
| {{date}} | {{health_score}}/100 | {{critical_count}} | {{total_issues}} | {{notes}} |
{{/each}}

### Trend Analysis

**Health Score Trend:** {{health_trend_description}}  
**Issue Introduction Rate:** {{issue_introduction_rate}} per week  
**Issue Resolution Rate:** {{issue_resolution_rate}} per week  
**Most Problematic Component:** {{most_problematic_component}}  
**Fastest Improving Component:** {{fastest_improving_component}}
{{else}}
*This is the first health audit. Future reports will include historical comparisons.*
{{/if}}

---

# 🏁 Next Steps

## Recommended Workflow

1. **Immediate Response** (Today)
   - Address all CRITICAL issues
   - Review security vulnerabilities
   - Ensure system stability

2. **Sprint Planning** (This Week)
   - Prioritize HIGH issues for current sprint
   - Plan MEDIUM issues for upcoming sprints
   - Schedule regular health check-ins

3. **Continuous Improvement** (Ongoing)
   - Run weekly health audits
   - Track progress on key metrics
   - Automate issue detection where possible

4. **Prevention** (Process Integration)
   - Add health checks to CI/CD pipeline
   - Create issue prevention guidelines
   - Train team on health audit process

## Tools & Resources

- **Re-run Health Audit:** `{{rerun_command}}`
- **Focus on Specific Component:** `{{component_scan_command}}`
- **Export to Different Format:** `{{export_command}}`
- **Schedule Automated Scans:** `{{schedule_command}}`

## Support & Contact

- **Documentation:** [CORTEX Health Audit Guide]({{docs_link}})
- **Issue Reporting:** [GitHub Issues]({{github_link}})
- **Team Chat:** [Discussion Channel]({{chat_link}})

---

**Generated by CORTEX Health Audit System**  
**Report ID:** {{report_id}}  
**Configuration Hash:** {{config_hash}}  
**Scanner Version:** {{scanner_version}}

*This report contains {{total_issues}} issues across {{categories_scanned}} categories, analyzed by {{scanner_count}} specialized scanners.*

---

# Partials/Templates

## {{> tier_analysis}}

**Health Score:** {{tier.health_score}}/100 {{tier.health_emoji}}

**Issues Found:** {{tier.issue_count}} ({{tier.critical}} critical, {{tier.high}} high, {{tier.medium}} medium, {{tier.low}} low)

{{#if tier.critical_issues}}
### 🚨 Critical Issues
{{#each tier.critical_issues}}
- **{{title}}** - {{description}} ({{estimated_fix_time}})
{{/each}}
{{/if}}

**Top Recommendations:**
{{#each tier.recommendations}}
{{@index}}. {{.}}
{{/each}}

**Component Status:**
{{#each tier.components}}
- {{name}}: {{status}} {{status_emoji}}
{{/each}}

## {{> agent_analysis}}

**Agent System Health:** {{agents.overall_health}}/100 {{agents.health_emoji}}

### Agent Status

| Agent | Status | Issues | Last Active |
|-------|--------|--------|-------------|
{{#each agents.individual_status}}
| {{name}} | {{status}} {{status_emoji}} | {{issue_count}} | {{last_active}} |
{{/each}}

### Communication Health

- **Corpus Callosum Status:** {{agents.corpus_callosum_status}} {{agents.cc_emoji}}
- **Message Success Rate:** {{agents.message_success_rate}}%
- **Average Response Time:** {{agents.avg_response_time}}ms

{{#if agents.workflow_issues}}
### Workflow Issues
{{#each agents.workflow_issues}}
- {{title}} ({{severity}})
{{/each}}
{{/if}}

---

*Report Template Version 1.0 | Generated {{timestamp}}*