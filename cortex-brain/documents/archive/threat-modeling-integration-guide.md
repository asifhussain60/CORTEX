# Threat Modeling Integration Guide

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Created:** December 8, 2025  
**Status:** ✅ Production Ready

---

## 📋 Overview

Threat modeling is automatically integrated into CORTEX Planning System, providing zero-effort security analysis for every security-sensitive feature. The ThreatModelerAgent analyzes features using the STRIDE framework and OWASP Top 10 2021 mapping, generating comprehensive threat reports with actionable mitigation strategies.

---

## 🎯 Key Features

### Automatic Detection
- **Keyword Matching:** Analyzes feature descriptions for security-sensitive patterns
- **Keywords:** auth, authentication, login, password, token, jwt, oauth, payment, credit card, financial, user, account, api, endpoint, database, sql, data
- **Zero Configuration:** Automatically enabled for matching features

### STRIDE Framework
- **Spoofing:** Identity verification threats
- **Tampering:** Data integrity threats
- **Repudiation:** Audit trail threats
- **Information Disclosure:** Confidentiality threats
- **Denial of Service:** Availability threats
- **Elevation of Privilege:** Authorization threats

### OWASP Top 10 2021 Mapping
- **A01:** Broken Access Control
- **A02:** Cryptographic Failures
- **A03:** Injection
- **A04:** Insecure Design
- **A05:** Security Misconfiguration
- **A06:** Vulnerable and Outdated Components
- **A07:** Identification and Authentication Failures
- **A08:** Software and Data Integrity Failures
- **A09:** Security Logging and Monitoring Failures
- **A10:** Server-Side Request Forgery (SSRF)

### Risk Assessment
- **Risk Ratings:** CRITICAL, HIGH, MEDIUM, LOW
- **Risk Scoring:** 0-10 scale (likelihood × impact)
- **Automatic Prioritization:** Critical/High threats flagged for immediate attention

### Mitigation Strategies
- **Implementation Steps:** Numbered action items
- **Code Examples:** Language-specific implementations
- **Effort Estimates:** Hours required per mitigation
- **Effectiveness Metrics:** Percentage risk reduction
- **Testing Guidance:** How to verify mitigation

---

## 🔧 Integration Points

### Planning Workflow

```
Phase 1: Foundation → Phase 2: Development → Phase 3: Security
    ↓
Threat Analysis (after Phase 3 complete)
    ↓
Format Results → Append to Plan → TDD Injection → Integration Phase
```

### Files Modified

#### PlanningOrchestrator
**File:** `src/orchestrators/planning_orchestrator.py`

**Methods:**
- `_run_threat_analysis()` - Lines 3293-3345
- `_append_threat_analysis_to_plan()` - Lines 3347-3365
- `_format_threat_section()` - Lines 3367-3504
- `_generate_mitigation_progress_bar()` - Lines 1800-1816
- `_format_stride_summary()` - Lines 1818-1847
- `_render_threat_section_for_progress()` - Lines 1849-1874

**Integration:** Lines 951-961 (after Phase 3 completion)

#### Plan Schema
**File:** `cortex-brain/config/plan-schema.yaml`

**Additions:**
- `threat_analysis_enabled` (metadata) - Line 28
- `threat_analysis` section - Lines 241-312

#### Response Templates
**File:** `cortex-brain/response-templates.yaml`

**Templates Updated:**
- `autonomous_execution_progress` - Lines 217-257
- `work_planner_success` - Lines 1947-2018

---

## 💻 Usage

### During Plan Creation

Threat modeling runs automatically for security-sensitive features:

```bash
python -m src.main "plan user authentication with JWT tokens"
```

**Output:**
```markdown
## 🔒 Threat Modeling Analysis

**Security Assessment:** ✅ STRIDE + OWASP Top 10 2021

### STRIDE Categories
- **Spoofing:** 3 threats ⚠️
- **Tampering:** 0 threats ✅
- **Repudiation:** 0 threats ✅
...

### Identified Threats

#### High Severity Threats (3)

**1. [HIGH] Session Hijacking (Spoofing)**
- **OWASP:** A07:2021 - Identification and Authentication Failures
- **Risk Score:** 8/10
- **Attack Scenario:** Attacker intercepts session cookie via XSS
- **Mitigation:** Secure Session Management
  - **Effort:** 1.5h | **Effectiveness:** 90%
  - **Steps:** Enable HttpOnly, Secure, SameSite flags...

[Code example follows]
```

### Programmatic Access

```python
from src.orchestrators.planning_orchestrator import PlanningOrchestrator

po = PlanningOrchestrator(cortex_root='/path/to/CORTEX')

# Run threat analysis
threat_analysis = po._run_threat_analysis(
    feature_description='User authentication with JWT tokens',
    feature_name='user-auth'
)

# Format as markdown
threat_section = po._format_threat_section(threat_analysis)
```

### Disable for Specific Features

Edit plan metadata:

```yaml
metadata:
  threat_analysis_enabled: false
```

---

## 📊 Output Structure

### Plan Document Section

```markdown
---

## 🔒 Threat Modeling Analysis

**Security Assessment:** ✅ STRIDE + OWASP Top 10 2021

### STRIDE Categories
[Category counts with icons]

**Total Threats:** X (Y Critical, Z High, ...)
**Risk Level:** 🔴 HIGH / 🟡 MEDIUM / 🟢 LOW

### OWASP Top 10 Coverage
[OWASP categories with threat counts]

### Identified Threats

#### Critical Severity Threats (X)
[Threat details with mitigations]

#### High Severity Threats (Y)
[Threat details with mitigations]

...

### Recommendations
- [Priority-based recommendations]

**Total Mitigation Effort:** X hours (included in DoD)
```

### Execution Progress

During autonomous execution:

```markdown
### 🔒 Threat Modeling Analysis

**Security Assessment:** ✅ Enabled (STRIDE + OWASP)

**STRIDE Categories:** Spoofing: 3, Tampering: 0, ...
**Threats Identified:** 14 (2 Critical, 5 High, 5 Medium, 2 Low)
**OWASP Coverage:** A01, A02, A03, A07, A09

**Mitigation Status:** [████████░░] 8/14 implemented
```

---

## 🧪 Testing

### Unit Test

```python
def test_threat_analysis_integration():
    """Test threat modeling integration in planning."""
    from src.orchestrators.planning_orchestrator import PlanningOrchestrator
    
    po = PlanningOrchestrator(cortex_root='.')
    
    # Test with auth feature
    result = po._run_threat_analysis(
        'User authentication with JWT tokens',
        'user-auth'
    )
    
    assert result is not None
    assert 'threats' in result
    assert len(result['threats']) > 0
    assert result['risk_level'] in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
```

### Integration Test

```python
def test_full_planning_with_threats():
    """Test complete planning workflow with threat analysis."""
    from src.orchestrators.planning_orchestrator import PlanningOrchestrator
    from pathlib import Path
    
    po = PlanningOrchestrator(cortex_root='.')
    
    # Generate plan
    success, plan_path, message = po.generate_incremental_plan(
        feature_requirements='API authentication with OAuth2',
        output_filename='test-auth-plan.yaml'
    )
    
    assert success
    assert plan_path.exists()
    
    # Verify threat section exists
    content = plan_path.read_text()
    assert '## 🔒 Threat Modeling Analysis' in content
    assert 'STRIDE Categories' in content
    assert 'OWASP' in content
```

---

## 🔒 Security Considerations

### Keyword Coverage
Current keyword list covers:
- **Authentication:** auth, login, password, token, jwt, oauth, mfa
- **Finance:** payment, credit card, billing, financial
- **Data:** database, sql, data, storage
- **Access:** user, account, profile, permission, role, access
- **APIs:** api, endpoint, service, integration

**Expansion:** Add keywords to `_run_threat_analysis()` method (line 3306)

### False Negatives
Features without matching keywords won't trigger analysis. Options:
1. Add more keywords
2. Set `threat_analysis_enabled: true` in plan metadata
3. Run manual analysis post-creation

### False Positives
Non-security features with matching keywords may trigger analysis. This is acceptable - extra analysis is safer than missing threats.

---

## 📈 Metrics & Monitoring

### Analysis Metrics
- **Detection Rate:** Percentage of security-sensitive features analyzed
- **Threat Count:** Average threats per feature
- **Risk Distribution:** Critical/High/Medium/Low breakdown
- **OWASP Coverage:** Which categories most frequently identified
- **Mitigation Effort:** Average hours per feature

### Logging
```python
[ThreatModeler] INFO: Analyzing threats for general feature
[ThreatModeler] INFO: Threat analysis complete: 3 threats, risk=HIGH
[ThreatModeler] INFO: Response SUCCESS - Duration: 2.08ms
```

---

## 🚀 Future Enhancements

### Phase 1 (Current)
- ✅ Automatic threat detection
- ✅ STRIDE + OWASP mapping
- ✅ Mitigation strategies
- ✅ Integration into planning

### Phase 2 (Planned)
- ☐ Threat database (historical threats)
- ☐ Machine learning threat detection
- ☐ Custom threat templates
- ☐ Threat modeling for existing code

### Phase 3 (Future)
- ☐ Automated penetration testing
- ☐ Security regression tracking
- ☐ Compliance mapping (SOC 2, ISO 27001)
- ☐ Threat model visualization

---

## 📚 References

### Documentation
- **STRIDE Framework:** https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats
- **OWASP Top 10 2021:** https://owasp.org/Top10/
- **ThreatModelerAgent:** `src/agents/security/threat_modeler_agent.py`
- **Plan Schema:** `cortex-brain/config/plan-schema.yaml`

### Related Guides
- Planning Orchestrator Guide: `.github/prompts/modules/planning-orchestrator-guide.md`
- Response Format V3: `.github/prompts/modules/response-format-v3.md`
- TDD Mastery Guide: `.github/prompts/modules/tdd-mastery-guide.md`

---

## ❓ Troubleshooting

### Threat Analysis Not Running

**Problem:** Plan created without threat section

**Solutions:**
1. Check feature description contains security keywords
2. Verify `threat_analysis_enabled` not set to `false`
3. Check ThreatModelerAgent initialization (line 81)
4. Review logs for errors

### Empty Threat Results

**Problem:** Analysis runs but no threats identified

**Possible Causes:**
- Feature truly has no threats (rare)
- Keywords matched but context insufficient
- ThreatModelerAgent template issue

**Solutions:**
1. Add more context to feature description
2. Manually specify components in context
3. Review ThreatModelerAgent threat templates

### Formatting Issues

**Problem:** Threat section malformed in output

**Solutions:**
1. Check `_format_threat_section()` method (line 3367)
2. Verify threat_analysis structure matches schema
3. Review markdown escaping for special characters

---

## 📞 Support

**Issues:** https://github.com/asifhussain60/CORTEX/issues  
**Author:** Asif Hussain  
**Email:** Contact via GitHub

---

**Last Updated:** December 8, 2025  
**Document Version:** 1.0.0  
**CORTEX Version:** 3.8.1+
