# Template Enhancement - Test Plan & Validation

**Plan ID:** template-enhancement-20251207  
**Test Phase:** Phase 4  
**Created:** 2025-12-07

---

## Test Strategy

This test plan covers 6 new templates (4 introduction variants, 1 business value, 1 security) with focus on:
1. Template selection (trigger matching)
2. Audience detection (explicit + implicit + default)
3. Format validation (structure, tone, content)
4. Integration (routing priority, conflict resolution)

---

## Manual Validation Checklist

### Template Selection Tests

#### Introduction - Professional (Default)
- [ ] Trigger: "introduce yourself" → `introduction_professional`
- [ ] Trigger: "what is cortex" → `introduction_professional`
- [ ] Trigger: "tell me about cortex" → `introduction_professional`
- [ ] No audience specified → Defaults to professional variant

#### Introduction - Leadership
- [ ] Explicit: "introduce yourself to leadership" → `introduction_leadership`
- [ ] Explicit: "present cortex to executives" → `introduction_leadership`
- [ ] Implicit: Message contains "ROI" + "introduce" → `introduction_leadership`
- [ ] Implicit: Message contains "business value" + "introduce" → `introduction_leadership`

#### Introduction - Product
- [ ] Explicit: "introduce cortex to product" → `introduction_product`
- [ ] Explicit: "present cortex to product owners" → `introduction_product`
- [ ] Implicit: Message contains "sprint" + "introduce" → `introduction_product`
- [ ] Implicit: Message contains "backlog" + "introduce" → `introduction_product`

#### Introduction - Engineering
- [ ] Explicit: "introduce yourself to engineers" → `introduction_engineering`
- [ ] Explicit: "present cortex to developers" → `introduction_engineering`
- [ ] Implicit: Message contains "architecture" + "introduce" → `introduction_engineering`
- [ ] Implicit: Message contains "technical" + "introduce" → `introduction_engineering`

#### Business Value
- [ ] Trigger: "how can cortex help the business" → `business_value`
- [ ] Trigger: "what can cortex do" → `business_value`
- [ ] Trigger: "cortex capabilities" → `business_value`

#### Security Posture
- [ ] Trigger: "cortex security" → `security_posture`
- [ ] Trigger: "how does cortex address security" → `security_posture`
- [ ] Trigger: "is cortex secure" → `security_posture`

---

### Format Validation Tests

#### 5-Section Structure (Introductions)
- [ ] Professional: Has What/Why/Tech/How/Explore sections
- [ ] Leadership: Has What/Why/Tech/How/Explore sections
- [ ] Product: Has What/Why/Tech/How/Explore sections
- [ ] Engineering: Has What/Why/Tech/How/Explore sections

#### Direct Address Format (NOT 5-Part)
- [ ] Professional: NO "My Understanding Of Your Request" section
- [ ] Leadership: NO "Approach & Considerations" section
- [ ] Product: NO "Impact & Changes" section
- [ ] Engineering: NO "Next Steps" (has "Explore Further" instead)
- [ ] Business value: Uses capability-based organization, not 5-part
- [ ] Security: Uses unified narrative, not 5-part

#### Professional Tone
- [ ] Professional: NO enthusiasm markers ("excited!", "amazing!")
- [ ] Leadership: NO enthusiasm markers
- [ ] Product: NO enthusiasm markers
- [ ] Engineering: NO enthusiasm markers
- [ ] Business value: NO enthusiasm markers
- [ ] Security: NO enthusiasm markers

#### Evidence-Based Claims
- [ ] Leadership: Includes 97.2% token reduction metric
- [ ] Leadership: Includes 94% vs 67% TDD success rate
- [ ] Professional: Includes quantitative metrics
- [ ] Engineering: Includes performance numbers (<100ms, 97.2%)
- [ ] Business value: Each capability has evidence/impact statement
- [ ] Security: Claims backed by implementation details

---

### Content Completeness Tests

#### Governance/SKULL Mention
- [ ] Professional: Mentions governance/SKULL in "Why built?" section
- [ ] Leadership: Mentions SKULL rules (2-3 sentences)
- [ ] Product: Mentions governance rules in quality context
- [ ] Engineering: Detailed SKULL explanation (declarative rules)

#### Exploration Questions
- [ ] Professional: Has 4-5 exploration questions
- [ ] Leadership: Has 5 business-focused questions
- [ ] Product: Has 5 product-focused questions
- [ ] Engineering: Has 6 technical deep-dive questions

#### Audience-Appropriate Emphasis
- [ ] Leadership: Emphasizes ROI, velocity, quality metrics
- [ ] Product: Emphasizes feature delivery, DoR/DoD, planning
- [ ] Engineering: Emphasizes architecture, TDD, agent framework
- [ ] Professional: Balanced technical + business value

#### Token Reduction Metric
- [ ] Leadership: Includes 97.2% metric prominently
- [ ] Professional: Mentions metric but less prominent
- [ ] Product: Mentions in cost efficiency context
- [ ] Engineering: Explains mechanism technically
- [ ] Business value: Dedicated cost efficiency section
- [ ] Other templates: Do NOT include (leadership only for emphasis)

---

### Integration Tests

#### Routing Priority
- [ ] "introduce yourself" triggers introduction, NOT greeting
- [ ] "hi cortex" triggers greeting, NOT introduction
- [ ] Introduction templates fire before Planning workflows (Priority 1 > Priority 2)
- [ ] Business value template at Priority 1
- [ ] Security template at Priority 1

#### Conflict Resolution
- [ ] "introduce yourself" → introduction (NOT greeting)
- [ ] "hello" → greeting (NOT introduction)
- [ ] "what can you do" → help OR business value (test priority)
- [ ] Ambiguous audience → Defaults to professional

#### Audience Detection Precedence
- [ ] Explicit phrase beats implicit keywords
- [ ] "introduce to leadership ROI" → leadership (explicit wins)
- [ ] "introduce architecture" → engineering (implicit keyword)
- [ ] "introduce" (no audience clues) → professional (default)

#### YAML Syntax
- [ ] response-templates.yaml parses without errors
- [ ] response-routing-rules.yaml parses without errors
- [ ] No duplicate template names
- [ ] No duplicate trigger keywords across templates

---

## Automated Test Scenarios (If Implementing)

### Test File: `tests/test_introduction_templates.py`

```python
def test_introduction_professional_triggers():
    """Test default introduction triggers route to professional variant"""
    triggers = [
        "introduce yourself",
        "what is cortex",
        "tell me about cortex",
        "present cortex"
    ]
    for trigger in triggers:
        template = route_to_template(trigger)
        assert template == "introduction_professional"

def test_introduction_leadership_explicit():
    """Test explicit leadership audience detection"""
    triggers = [
        "introduce yourself to leadership",
        "present cortex to executives",
        "introduce cortex for leadership"
    ]
    for trigger in triggers:
        template = route_to_template(trigger)
        assert template == "introduction_leadership"

def test_audience_detection_implicit():
    """Test implicit keyword-based audience detection"""
    test_cases = [
        ("introduce yourself, focusing on ROI", "introduction_leadership"),
        ("introduce cortex for our sprint planning", "introduction_product"),
        ("introduce cortex with architecture details", "introduction_engineering")
    ]
    for message, expected_template in test_cases:
        template = route_to_template(message)
        assert template == expected_template

def test_default_fallback():
    """Test fallback to professional when audience ambiguous"""
    ambiguous_messages = [
        "introduce yourself to the team",
        "tell me about cortex for everyone",
        "introduce cortex"
    ]
    for message in ambiguous_messages:
        template = route_to_template(message)
        assert template == "introduction_professional"

def test_conflict_resolution():
    """Test introduction overrides greeting"""
    assert route_to_template("introduce yourself") == "introduction_professional"
    assert route_to_template("hi cortex") == "greeting"
    assert route_to_template("hello") == "greeting"
```

### Test File: `tests/test_template_format_validation.py`

```python
def test_introduction_five_section_structure():
    """Verify all introductions have 5-section structure"""
    templates = [
        "introduction_professional",
        "introduction_leadership",
        "introduction_product",
        "introduction_engineering"
    ]
    required_sections = [
        "What is CORTEX?",
        "Why Was It Built?",
        "Tech Stack & Architecture",
        "How CORTEX Can Help",
        "Explore Further"
    ]
    for template_name in templates:
        template_content = load_template(template_name)
        for section in required_sections:
            assert section in template_content

def test_no_five_part_operational_format():
    """Verify presentation templates don't use 5-part format"""
    presentation_templates = [
        "introduction_professional",
        "introduction_leadership",
        "introduction_product",
        "introduction_engineering",
        "business_value",
        "security_posture"
    ]
    forbidden_sections = [
        "My Understanding Of Your Request",
        "Approach & Considerations",
        "Impact & Changes"
    ]
    for template_name in presentation_templates:
        template_content = load_template(template_name)
        for section in forbidden_sections:
            assert section not in template_content

def test_professional_tone():
    """Verify no enthusiasm markers in any template"""
    all_new_templates = [
        "introduction_professional",
        "introduction_leadership",
        "introduction_product",
        "introduction_engineering",
        "business_value",
        "security_posture"
    ]
    enthusiasm_markers = ["excited!", "amazing!", "awesome!", "perfect!"]
    for template_name in all_new_templates:
        template_content = load_template(template_name)
        content_lower = template_content.lower()
        for marker in enthusiasm_markers:
            assert marker.lower() not in content_lower

def test_evidence_based_claims():
    """Verify metrics present where expected"""
    # Leadership should have 97.2% token reduction
    leadership = load_template("introduction_leadership")
    assert "97.2%" in leadership
    
    # All templates should have some quantitative evidence
    for template_name in ["introduction_professional", "introduction_engineering"]:
        content = load_template(template_name)
        # Check for percentage or numbers
        assert any(char.isdigit() for char in content)
```

### Test File: `tests/test_business_security_templates.py`

```python
def test_business_value_capability_organization():
    """Verify business value template has 4 capability categories"""
    content = load_template("business_value")
    categories = [
        "Planning & Requirements",
        "Development Automation",
        "Quality Assurance",
        "Operations & Maintenance"
    ]
    for category in categories:
        assert category in content

def test_security_unified_narrative():
    """Verify security template covers both CORTEX and app security"""
    content = load_template("security_posture")
    cortex_security_topics = ["Git Isolation", "Privacy Protection", "Code Boundary"]
    app_security_topics = ["TDD Enforcement", "Threat Modeling", "OWASP"]
    
    for topic in cortex_security_topics:
        assert topic in content
    for topic in app_security_topics:
        assert topic in content

def test_business_value_evidence():
    """Verify each capability has evidence/impact statement"""
    content = load_template("business_value")
    capabilities = [
        "Planning System 2.0",
        "TDD Mastery",
        "Convention-Based Validation",
        "Universal Upgrade System"
    ]
    for capability in capabilities:
        # Find capability section
        assert capability in content
        # Verify evidence follows (look for metrics, percentages, outcomes)
        # This would need more sophisticated parsing in real implementation
```

---

## Manual Test Execution Log

**Tester:** [Name]  
**Date:** [Date]  
**Environment:** GitHub Copilot Chat in VS Code

### Test Session 1: Template Selection

| Test | Input | Expected | Actual | Status |
|------|-------|----------|--------|--------|
| IT-1 | "introduce yourself" | introduction_professional | [actual] | [ ] |
| IT-2 | "introduce yourself to leadership" | introduction_leadership | [actual] | [ ] |
| IT-3 | "introduce cortex to product" | introduction_product | [actual] | [ ] |
| IT-4 | "introduce yourself to engineers" | introduction_engineering | [actual] | [ ] |
| BV-1 | "how can cortex help the business" | business_value | [actual] | [ ] |
| SP-1 | "cortex security" | security_posture | [actual] | [ ] |

### Test Session 2: Audience Detection

| Test | Input | Expected | Actual | Status |
|------|-------|----------|--------|--------|
| AD-1 | "introduce, focusing on ROI" | introduction_leadership | [actual] | [ ] |
| AD-2 | "introduce for sprint planning" | introduction_product | [actual] | [ ] |
| AD-3 | "introduce with architecture details" | introduction_engineering | [actual] | [ ] |
| AD-4 | "introduce to the team" | introduction_professional | [actual] | [ ] |

### Test Session 3: Format Validation

| Test | Template | Check | Status |
|------|----------|-------|--------|
| FV-1 | introduction_professional | 5 sections present | [ ] |
| FV-2 | introduction_leadership | NO 5-part format | [ ] |
| FV-3 | business_value | 4 categories present | [ ] |
| FV-4 | security_posture | Unified narrative | [ ] |
| FV-5 | All templates | NO enthusiasm | [ ] |
| FV-6 | All templates | Evidence-based | [ ] |

---

## Issues Found

| ID | Description | Severity | Status |
|----|-------------|----------|--------|
| [Example: ISS-001] | [Example: Leadership template missing ROI metric] | [High/Med/Low] | [Open/Fixed] |

---

## Test Summary

**Total Tests:** [Number]  
**Passed:** [Number]  
**Failed:** [Number]  
**Blocked:** [Number]  
**Success Rate:** [Percentage]

**Recommendation:** [ ] APPROVED FOR DEPLOYMENT / [ ] NEEDS FIXES

---

## Notes

- Template testing in Copilot Chat is qualitative (manual observation)
- Automated tests would require CORTEX orchestrator implementation
- Focus on trigger matching and format compliance
- Document any unexpected behaviors or edge cases
