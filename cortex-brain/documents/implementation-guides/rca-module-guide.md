# CORTEX RCA (Root Cause Analysis) Module - Implementation Guide

**Version:** 3.4.0  
**Status:** ✅ PRODUCTION READY  
**Author:** Asif Hussain  
**Date:** 2024-12-01

---

## 🎯 Overview

The CORTEX RCA Module provides **interactive Root Cause Analysis** with the **5 Whys methodology**, enabling systematic investigation of incidents and generation of executive-ready reports for senior leadership.

### Key Features

✅ **Interactive 5 Whys Engine** - Guided questioning with intelligent suggestions  
✅ **Pattern Learning** - Learns from historical RCAs to improve analysis  
✅ **Confidence Scoring** - Assesses answer quality and causal chain strength  
✅ **Executive Reporting** - Generates leadership-ready RCA reports  
✅ **DOCX Import** - Converts existing RCA documents to CORTEX format  
✅ **Knowledge Graph Integration** - Stores findings for future pattern matching

---

## 📋 Table of Contents

1. [Architecture](#architecture)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Workflows](#workflows)
5. [Command Reference](#command-reference)
6. [Report Structure](#report-structure)
7. [Integration Points](#integration-points)
8. [Configuration](#configuration)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

---

## 🏗️ Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      RCA Agent (Entry Point)                 │
│  - Intent detection                                          │
│  - Natural language routing                                  │
│  - Response formatting                                       │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                  RCA Orchestrator (Core Logic)               │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ Document Processor│  │ 5 Whys Engine    │                │
│  │ - DOCX → Markdown │  │ - Question gen   │                │
│  │ - Metadata extract│  │ - Answer scoring │                │
│  └──────────────────┘  └──────────────────┘                │
│                                                               │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ Report Generator  │  │ Pattern Learner  │                │
│  │ - Executive report│  │ - KG integration │                │
│  │ - 8 sections      │  │ - Suggestion gen │                │
│  └──────────────────┘  └──────────────────┘                │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    Storage (cortex-brain/)                   │
│  documents/investigations/rca/                               │
│    ├── active/       - In-progress analyses                 │
│    ├── completed/    - Finished analyses                    │
│    ├── approved/     - Approved RCA reports                 │
│    └── templates/    - Report templates                     │
└─────────────────────────────────────────────────────────────┘
```

### Data Models

**Core Structures:**
- `IncidentDetails` - Incident metadata (ID, title, severity, dates, impact)
- `WhyQuestion` - Individual Why question with answer, confidence, evidence
- `RootCause` - Identified root cause with category, confidence, why chain
- `CorrectiveAction` - Remediation action with type, owner, priority
- `RCAAnalysis` - Complete analysis container

---

## 🚀 Installation

### Prerequisites

- CORTEX v3.4.0 or later
- Python 3.8+
- `python-docx` library (optional, for DOCX conversion)

### Setup

1. **Install Optional Dependencies** (for DOCX conversion):
   ```powershell
   pip install python-docx
   ```

2. **Verify Installation**:
   ```powershell
   # Check RCA directories exist
   Test-Path cortex-brain\documents\investigations\rca\active
   ```

3. **Agent Registration** (automatic):
   RCA Agent auto-registers with IntentRouter on first use.

---

## ⚡ Quick Start

### Scenario: Import Existing RCA and Complete Analysis

```powershell
# 1. Import RCA document
import rca docs\rca\RCA_RA2_Error.docx

# Output: Analysis ID (e.g., 20241201-140530-ra2-error)

# 2. Start 5 Whys analysis
analyze rca 20241201-140530-ra2-error

# Output: Why 1 question with suggestions

# 3. Answer Why questions (5 iterations)
answer rca 20241201: Service crashed due to memory leak in caching layer

# Continue answering Why 2-5...

# 4. Generate executive report
report rca 20241201-140530-ra2-error

# Output: Report file path in cortex-brain/documents/investigations/rca/approved/
```

---

## 🔄 Workflows

### Workflow 1: Import Existing RCA Document

**Use Case:** Convert DOCX RCA document to CORTEX format

**Steps:**
1. Place DOCX file in `docs/rca/` directory
2. Run: `import rca docs/rca/[filename].docx`
3. CORTEX converts to markdown and extracts metadata
4. Analysis ready in `cortex-brain/documents/investigations/rca/active/`

**Auto-Extracted:**
- Incident title
- Date occurred
- Severity level
- Initial description

---

### Workflow 2: Interactive 5 Whys Analysis

**Use Case:** Systematic root cause identification

**Steps:**

**Phase 1: Discovery (Why 1-2)**
- Focus: Immediate symptoms and direct causes
- Suggestions: System-level issues (config, code, dependencies)

**Phase 2: Analysis (Why 3-4)**
- Focus: Process gaps and human factors
- Suggestions: Testing, documentation, communication

**Phase 3: Synthesis (Why 5)**
- Focus: Organizational and strategic causes
- Suggestions: Culture, priorities, resource allocation

**Confidence Scoring:**
- **90%+** High confidence - Can stop early if root cause clear
- **70-89%** Medium confidence - Continue to Why 5
- **<70%** Low confidence - Request more evidence

---

### Workflow 3: Executive Report Generation

**Use Case:** Create leadership-ready RCA report

**Report Sections:**
1. **Executive Summary** - One-page overview for C-level
2. **Incident Overview** - What happened, when, impact
3. **Detailed Timeline** - Chronological event sequence
4. **Root Cause Analysis** - Full 5 Whys chain with evidence
5. **Impact Assessment** - Business/financial/reputational
6. **Corrective Actions** - Immediate/short-term/long-term
7. **Prevention Strategy** - How to avoid recurrence
8. **Recommendations** - Process/tool/training improvements
9. **Technical Appendix** - Logs, configs, code (optional)

**Output:** Copy-paste ready markdown formatted for senior leadership

---

## 📖 Command Reference

### Import Commands

```powershell
# Import DOCX document
import rca [file_path]
import rca docs/rca/incident-2024.docx

# Auto-converts DOCX → Markdown
# Extracts incident metadata
# Creates analysis file in active/
```

### Analysis Commands

```powershell
# Start 5 Whys analysis
analyze rca [analysis_id]
start rca [analysis_id]
5 whys [analysis_id]

# Answer current Why question
answer rca [analysis_id]: [your answer]
answer rca 20241201: Memory leak in UserSession cache

# Continue to next Why
continue rca [analysis_id]

# Accept early root cause (if confidence >90%)
accept root cause [analysis_id]
```

### Report Commands

```powershell
# Generate executive report
report rca [analysis_id]
generate report [analysis_id]

# Generate with technical appendix
report rca [analysis_id] --appendix

# Approve RCA for distribution
approve rca [analysis_id]
```

### Management Commands

```powershell
# List active analyses
list rcas
show active rcas

# View specific analysis
show rca [analysis_id]

# Get RCA help
rca help
```

---

## 📊 Report Structure

### Executive Summary Example

```markdown
## Executive Summary

**Incident:** RA2 Employer Service API Error
**Date:** 2024-08-05
**Severity:** CRITICAL
**Status:** Completed

### Key Findings

**Root Cause:** Insufficient connection pooling limits in database configuration, compounded by lack of connection timeout monitoring.

**Category:** Technical (with process contributing factors)
**Confidence Level:** 92%

### Impact

Service unavailable for 4 hours affecting 2,500 users and 150 employer accounts. Estimated revenue impact: $45,000.

### Actions Required

3 corrective actions identified
5 preventive measures recommended
```

### 5 Whys Chain Example

```markdown
## Root Cause Analysis

### 5 Whys Methodology

**Why 1:** Why did the RA2 Employer Service API fail?

**Answer:** Database connection pool exhausted, causing all API requests to timeout.

**Supporting Evidence:**
- Application logs showed "Max pool size reached" errors
- Database monitoring showed 100/100 connections in use
- API response time increased from 200ms to 30s+

---

**Why 2:** Why did the connection pool exhaust?

**Answer:** Long-running queries were not releasing connections due to missing timeout configuration.

**Supporting Evidence:**
- 47 connections held for >5 minutes
- Query execution plan showed full table scans
- No connection timeout configured in app.config

---

**Why 3:** Why were long-running queries not handled properly?

**Answer:** Missing query timeout configuration and lack of query performance monitoring.

**Supporting Evidence:**
- No timeout values in EntityFramework configuration
- No slow query alerts configured in monitoring
- Database performance dashboard not reviewed in 2 months

---

**Why 4:** Why was query timeout configuration missing?

**Answer:** Configuration best practices not included in deployment checklist, and code review didn't catch it.

**Supporting Evidence:**
- Deployment checklist v2.1 (used) has 12 items, none for connection/query timeouts
- Pull request #4523 approved without performance review
- No automated performance testing in CI/CD pipeline

---

**Why 5:** Why aren't configuration best practices enforced?

**Answer:** Lack of automated configuration validation and incomplete infrastructure-as-code templates.

**Supporting Evidence:**
- ARM templates missing database connection settings section
- No policy enforcement for configuration compliance
- Training on configuration management last conducted 18 months ago

### Identified Root Cause

**Insufficient connection pooling limits in database configuration, combined with lack of automated configuration validation and performance monitoring.**

**Category:** Technical (with process and organizational contributing factors)
**Confidence:** 92%
```

---

## 🔗 Integration Points

### 1. InvestigationRouter Integration

**Purpose:** Deep investigation capabilities for RCA analyses

**Usage:**
```python
# RCA Orchestrator can invoke InvestigationRouter for:
# - File dependency analysis
# - Code health insights
# - Pattern matching across codebase

investigation_result = await investigation_router.handle_investigation(
    query=f"Investigate why {incident.affected_systems[0]} failed",
    context={'rca_analysis_id': analysis.analysis_id}
)
```

### 2. Knowledge Graph Integration

**Purpose:** Learn from historical RCAs and suggest similar patterns

**Storage:**
```python
# After completing analysis:
# - Root cause patterns stored in Tier 2
# - Causal relationships indexed for future matching
# - Suggestion generation uses historical data

self.knowledge_graph.store_pattern(
    pattern_type='rca_root_cause',
    pattern_data={
        'category': root_cause.category,
        'description': root_cause.description,
        'affected_systems': incident.affected_systems,
        'confidence': root_cause.confidence
    }
)
```

### 3. Health Validator Integration

**Purpose:** Provide context on system health during incident

**Usage:**
```python
# Get health insights for affected components
health_data = await enhanced_validator.analyze_component_health(
    entity=incident.affected_systems[0]
)

# Insights added to RCA findings
analysis.findings.append({
    'type': 'health_analysis',
    'data': health_data,
    'confidence': 0.85
})
```

---

## ⚙️ Configuration

### File Locations

```yaml
cortex-brain/documents/investigations/rca/
  active/         # In-progress analyses
  completed/      # Finished analyses (not yet reported)
  approved/       # Executive reports ready for distribution
  templates/      # Custom report templates (future)
```

### Orchestrator Settings

```python
# RCAOrchestrator initialization
rca_orchestrator = RCAOrchestrator(
    brain_path=Path("cortex-brain"),
    # Auto-creates directory structure
)

# Confidence thresholds
early_completion_threshold = 0.90  # Can stop at Why 3-4 if >90% confidence
minimum_confidence = 0.70          # Warn if confidence <70%

# Suggestion count
max_suggestions_per_why = 5        # Limit to top 5 suggestions
```

### Response Template Integration

Add to `cortex-brain/response-templates.yaml`:

```yaml
rca_analysis:
  template_id: rca_analysis_start
  triggers:
    - "analyze rca"
    - "start rca"
    - "5 whys"
  format: |
    ## 🔍 5 Whys Analysis Started
    
    **Analysis ID:** {analysis_id}
    **Incident:** {incident_title}
    
    ### {question}
    
    **Suggestions (based on similar incidents):**
    {suggestions}
```

---

## 🐛 Troubleshooting

### Issue: DOCX Import Fails

**Symptom:** "Could not convert DOCX file"

**Causes:**
1. `python-docx` library not installed
2. DOCX file corrupted or password-protected
3. File path incorrect

**Solutions:**
```powershell
# Install python-docx
pip install python-docx

# Verify file exists
Test-Path docs\rca\filename.docx

# Try manual conversion fallback
# CORTEX creates placeholder markdown for manual paste
```

---

### Issue: Low Confidence Scores

**Symptom:** All Why answers have <70% confidence

**Causes:**
1. Answers too brief (lack detail)
2. No supporting evidence provided
3. Vague or generic answers

**Solutions:**
```powershell
# Provide detailed answers with specifics:
✅ GOOD: "Memory leak in UserSession cache due to missing Dispose() calls in SessionManager.cs lines 45-67"

❌ BAD: "Memory leak"

# Include evidence:
answer rca 20241201: [answer] --evidence "Log excerpt: OutOfMemoryException at 14:32:05"
```

---

### Issue: Pattern Suggestions Not Appearing

**Symptom:** No intelligent suggestions during Why questions

**Causes:**
1. First RCA analysis (no historical data)
2. Knowledge graph not initialized
3. Affected systems don't match historical patterns

**Solutions:**
```powershell
# Check Knowledge Graph health
cortex healthcheck

# Complete 2-3 RCAs to build pattern library
# Suggestions improve over time with more data

# Manually provide context:
analyze rca [id] --context "Similar to incident INC-2024-003"
```

---

## ✅ Best Practices

### 1. Answer Quality

**DO:**
- ✅ Use specific terms (class names, config keys, error codes)
- ✅ Include timestamps and quantifiable data
- ✅ Reference logs, metrics, or code
- ✅ Explain the causal link clearly

**DON'T:**
- ❌ Give vague answers ("Something broke")
- ❌ Skip evidence ("I think it was X")
- ❌ Assume without verification
- ❌ Stop at symptoms (go deeper)

---

### 2. Evidence Collection

**Before Starting Analysis:**
1. Gather logs from incident time window
2. Collect error messages and stack traces
3. Review monitoring dashboards
4. Interview team members
5. Document timeline of events

**During Analysis:**
- Attach evidence to each Why answer
- Link to specific log entries or metrics
- Reference code commits or config changes

---

### 3. Root Cause Categorization

**Technical:** Code bugs, system failures, infrastructure issues  
**Process:** Missing procedures, inadequate testing, poor review  
**Human:** Training gaps, communication failures, assumptions  
**Organizational:** Resource constraints, priority conflicts, culture

**Most RCAs have multi-category causes** - Document primary + contributing factors

---

### 4. Executive Report Writing

**Executive Summary Rules:**
- ✅ One page maximum
- ✅ Start with business impact
- ✅ Use non-technical language
- ✅ End with clear actions

**Technical Details:**
- ✅ Move to appendix
- ✅ Include for engineers/operators
- ✅ Omit from executive distribution

---

### 5. Follow-Up Actions

**After Report Generation:**
1. Review with incident response team
2. Validate root cause with subject matter experts
3. Get approval from engineering leadership
4. Distribute to stakeholders
5. **Track corrective actions to completion**
6. **Schedule follow-up review (30/60/90 days)**

---

## 📈 Success Metrics

### Analysis Quality Indicators

**High-Quality RCA:**
- ✅ Confidence score >85%
- ✅ Specific root cause identified
- ✅ Evidence attached to each Why
- ✅ Actionable corrective actions defined
- ✅ Clear prevention strategy

**Needs Improvement:**
- ⚠️ Confidence score <70%
- ⚠️ Generic root cause ("user error")
- ⚠️ Missing evidence
- ⚠️ No corrective actions
- ⚠️ Vague recommendations

---

## 🎓 Learning Resources

### Internal Documentation
- `src/orchestrators/rca_orchestrator.py` - Full implementation
- `src/cortex_agents/rca_agent.py` - Agent routing logic
- `src/cortex_agents/investigation_router.py` - Deep investigation capabilities

### External References
- [5 Whys Technique](https://en.wikipedia.org/wiki/Five_whys) - Lean methodology
- [Root Cause Analysis Best Practices](https://www.asq.org/quality-resources/root-cause-analysis)
- [Incident Post-Mortem Template](https://github.com/dastergon/postmortem-templates)

---

## 🚀 Future Enhancements

### Planned (v3.5.0)

1. **Visual Timeline Generator** - Interactive HTML timeline of incident events
2. **Multi-Root Cause Support** - Complex incidents with multiple contributing causes
3. **Automated Action Tracking** - Integration with ADO for corrective action work items
4. **Trend Analysis** - Identify recurring root cause patterns across incidents
5. **AI-Assisted Questioning** - GPT-4 generated follow-up questions based on answers

### Under Consideration

- RCA dashboard with incident metrics
- Slack/Teams notification integration
- Export to PDF for executive distribution
- Video recording support for incident walkthroughs

---

## 📞 Support

**Questions?** Open an issue in the CORTEX repository with the `rca-module` label.

**Bug Reports:** Use `report issue` command with RCA context.

**Feature Requests:** Submit via `feedback` command with enhancement type.

---

**Document Version:** 1.0.0  
**Last Updated:** 2024-12-01  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)
