# Sprint 1: Immediate Visibility Enhancement - Implementation Guide

**Sprint:** 1 of 8  
**Duration:** 1 week  
**Status:** ≡ƒÜº IN PROGRESS  
**Started:** November 28, 2025  
**Target Completion:** December 5, 2025

---

## ≡ƒÄ» Sprint Goal

Make CORTEX Rulebook impossible to miss at every entry point with:
1. Welcome banner with rulebook link
2. Help command governance section
3. First-use acknowledgment flow

---

## ≡ƒôï Deliverables

### 1. Welcome Banner Enhancement

**Location:** `src/cortex_agents/profile_agent.py`  
**Component:** Greeting response template modification

**Changes:**
```python
def _generate_greeting_response(self) -> str:
    """Generate greeting with rulebook link."""
    return """
    Hello! I'm CORTEX, your AI assistant enhancement system.
    
    ≡ƒºá **CORTEX Vision:** Transparent governance where rules guide development.
    
    ≡ƒôû **Important:** Please review the CORTEX Rulebook before starting:
       #file:cortex-brain/governance/CORTEX-RULEBOOK.md
    
    This ensures you understand brain protection rules and development guidelines.
    
    Ready to begin? Say 'help' to see available commands.
    """
```

**Validation:**
- Γ£à Link appears in all greeting responses
- Γ£à File reference uses correct syntax (#file:)
- Γ£à Language uses "vision" not "promise"

### 2. Help Command Enhancement

**Location:** `cortex-brain/response-templates.yaml`  
**Template:** `help_table`

**New Section:**
```yaml
## ≡ƒôû Governance & Rules

**CORTEX Rulebook:** #file:cortex-brain/governance/CORTEX-RULEBOOK.md

Understanding governance rules helps you work effectively with CORTEX:
- Brain Protection Rules (27 rules across 10 layers)
- Development Guidelines
- Quality Standards
- Security Requirements

**Commands:**
- `show rules` - View all governance rules
- `explain rule [name]` - Get detailed rule explanation
- `my compliance` - Check your compliance status
```

**Validation:**
- Γ£à Section appears in help response
- Γ£à Commands functional (Sprint 3 implementation)
- Γ£à Rulebook link navigable

### 3. Pre-Flight Acknowledgment Flow

**Location:** `src/tier1/user_profile_manager.py`

**New Methods:**

```python
def check_rulebook_acknowledgment(self) -> bool:
    """
    Check if user has acknowledged rulebook.
    
    Returns:
        True if acknowledged, False if first-time user
    """
    profile = self.get_profile()
    if not profile:
        return False
    
    return profile.get('rulebook_acknowledged', False)

def record_rulebook_acknowledgment(self) -> bool:
    """
    Record that user has acknowledged rulebook.
    
    Returns:
        True if successfully recorded
    """
    # Store in Tier 3 for persistence
    from src.tier3.development_context import DevelopmentContext
    
    dev_context = DevelopmentContext()
    dev_context.store_pattern(
        namespace="cortex.governance.acknowledgments",
        pattern_type="rulebook_acknowledgment",
        pattern_data={
            "acknowledged_at": datetime.now().isoformat(),
            "version": "3.2.1"
        }
    )
    
    # Update user profile
    return self.update_profile(rulebook_acknowledged=True)
```

**Dialog Flow:**

```python
def show_pre_flight_acknowledgment(self) -> str:
    """
    Show pre-flight acknowledgment dialog for first-time users.
    
    Returns:
        Acknowledgment prompt text
    """
    return """
    ## ≡ƒôû Welcome to CORTEX!
    
    Before we begin, please take a moment to review the CORTEX Rulebook:
    
    **Rulebook:** #file:cortex-brain/governance/CORTEX-RULEBOOK.md
    
    The rulebook explains:
    - How CORTEX protects your brain (knowledge graph)
    - Development guidelines and best practices
    - What CORTEX will and won't do
    
    **This takes ~5 minutes to read.**
    
    ---
    
    Have you reviewed the rulebook?
    - Say "yes" or "I acknowledge" to continue
    - Say "show rulebook" to open it now
    - Say "skip for now" to proceed (will show again)
    
    **Note:** Experienced users with existing profiles skip this step.
    """
```

**Validation:**
- Γ£à Shows only for first-time users
- Γ£à Experienced users (existing profile) skip
- Γ£à Acknowledgment persisted in Tier 3
- Γ£à Can be re-triggered with "show rulebook acknowledgment"

---

## ≡ƒùä∩╕Å Database Schema (Sprint 2 Prep)

**Location:** `cortex-brain/compliance-tracking-schema.sql`

```sql
-- Compliance tracking database for Option B dashboard
-- Created: November 28, 2025
-- Sprint: 2 (prepared in Sprint 1)

CREATE TABLE IF NOT EXISTS compliance_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,  -- 'violation', 'warning', 'acknowledgment'
    rule_id TEXT,              -- SKULL rule identifier (e.g., 'SKULL-01')
    rule_category TEXT,        -- 'brain_protection', 'development', 'quality'
    severity TEXT,             -- 'critical', 'warning', 'info'
    description TEXT NOT NULL,
    context TEXT,              -- JSON: file, line, operation
    user_response TEXT,        -- How user handled event
    timestamp TEXT NOT NULL,
    resolved_at TEXT,
    resolution_notes TEXT
);

CREATE TABLE IF NOT EXISTS rulebook_acknowledgments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,              -- From user profile
    acknowledged_at TEXT NOT NULL,
    cortex_version TEXT NOT NULL,
    rulebook_version TEXT DEFAULT '1.0'
);

CREATE TABLE IF NOT EXISTS rule_views (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL,
    viewed_at TEXT NOT NULL,
    view_context TEXT,         -- 'help', 'violation', 'search', 'dashboard'
    view_duration_seconds INTEGER
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_compliance_timestamp 
    ON compliance_events(timestamp);

CREATE INDEX IF NOT EXISTS idx_compliance_rule 
    ON compliance_events(rule_id);

CREATE INDEX IF NOT EXISTS idx_compliance_severity 
    ON compliance_events(severity);

CREATE INDEX IF NOT EXISTS idx_acknowledgment_user 
    ON rulebook_acknowledgments(user_id);

CREATE INDEX IF NOT EXISTS idx_rule_views_rule 
    ON rule_views(rule_id);
```

**Schema Validation:**
- Γ£à Supports all Sprint 2 dashboard requirements
- Γ£à Indexes optimize query performance (<50ms target)
- Γ£à JSON context field allows flexible data storage
- Γ£à Resolution tracking for violation follow-up

---

## ≡ƒº¬ Testing Requirements

### Unit Tests (15 tests)

**File:** `tests/tier1/test_rulebook_acknowledgment.py`

```python
import pytest
from src.tier1.user_profile_manager import UserProfileManager

def test_welcome_banner_includes_rulebook_link():
    """Verify welcome banner contains rulebook link."""
    from src.cortex_agents.profile_agent import ProfileAgent
    
    agent = ProfileAgent()
    greeting = agent._generate_greeting_response()
    
    assert "#file:cortex-brain/governance/CORTEX-RULEBOOK.md" in greeting
    assert "CORTEX Vision" in greeting
    assert "promise" not in greeting.lower()

def test_help_command_shows_governance_section():
    """Verify help response includes governance section."""
    # Load response template
    import yaml
    with open("cortex-brain/response-templates.yaml") as f:
        templates = yaml.safe_load(f)
    
    help_template = templates['templates']['help_table']
    content = help_template['content']
    
    assert "Governance & Rules" in content
    assert "CORTEX-RULEBOOK.md" in content
    assert "show rules" in content

def test_first_use_acknowledgment_flow_functional():
    """Verify pre-flight acknowledgment shown to first-time users."""
    manager = UserProfileManager()
    
    # Delete profile to simulate first-time user
    manager.delete_profile()
    
    # Check acknowledgment required
    assert manager.check_rulebook_acknowledgment() is False
    
    # Record acknowledgment
    assert manager.record_rulebook_acknowledgment() is True
    
    # Verify persisted
    assert manager.check_rulebook_acknowledgment() is True

def test_acknowledgment_timestamp_persisted_in_tier3():
    """Verify acknowledgment timestamp stored in Tier 3."""
    from src.tier3.development_context import DevelopmentContext
    
    manager = UserProfileManager()
    manager.record_rulebook_acknowledgment()
    
    # Query Tier 3
    dev_context = DevelopmentContext()
    patterns = dev_context.query_patterns(
        namespace="cortex.governance.acknowledgments",
        pattern_type="rulebook_acknowledgment"
    )
    
    assert len(patterns) > 0
    assert "acknowledged_at" in patterns[0]['pattern_data']

def test_experienced_users_skip_acknowledgment():
    """Verify users with existing profiles skip acknowledgment."""
    manager = UserProfileManager()
    
    # Create profile (simulate experienced user)
    manager.create_profile(
        interaction_mode="guided",
        experience_level="senior"
    )
    
    # Mark as acknowledged
    manager.record_rulebook_acknowledgment()
    
    # Verify skip logic
    assert manager.check_rulebook_acknowledgment() is True
```

### Integration Tests (2 tests)

**File:** `tests/integration/test_rulebook_integration.py`

```python
def test_end_to_end_onboarding_with_rulebook_acknowledgment():
    """Test complete onboarding flow with rulebook."""
    # Simulate fresh user activation
    # Verify greeting ΓåÆ acknowledgment ΓåÆ profile creation ΓåÆ ready
    pass

def test_rulebook_link_navigation_from_all_entry_points():
    """Verify rulebook accessible from greeting, help, pre-flight."""
    pass
```

### Manual Validation Checklist

- [ ] Fresh user activation shows acknowledgment flow
- [ ] Existing users see greeting but skip acknowledgment
- [ ] Rulebook link navigates correctly in VS Code
- [ ] Language uses "vision" framing, not "promise" framing
- [ ] All entry points (greeting, help, pre-flight) include rulebook reference

---

## ≡ƒôè Success Criteria

**Sprint 1 Complete When:**

1. Γ£à All activation responses include rulebook link
2. Γ£à Help command shows governance section with 4 commands
3. Γ£à First-use acknowledgment flow functional
4. Γ£à Acknowledgment timestamp persisted in Tier 3
5. Γ£à All 15 unit tests pass (100% pass rate)
6. Γ£à 2 integration tests pass
7. Γ£à Manual validation checklist complete

**Performance Targets:**
- Acknowledgment check: <10ms
- Profile update: <50ms
- Tier 3 storage: <100ms

---

## ≡ƒöä Next Sprint Preview

**Sprint 2: Active Compliance Dashboard**

After Sprint 1, we'll build:
- SQLite compliance tracking database (schema ready)
- HTML dashboard with auto-refresh
- Protection event notifications in Copilot Chat
- WebSocket server for real-time updates

**Dependencies from Sprint 1:**
- Acknowledgment tracking operational
- User profile system integrated
- Database schema validated

---

## ≡ƒôÜ References

- **Option B Plan:** `OPTION-B-COMPREHENSIVE-DASHBOARD-PLAN.yaml`
- **User Profile Guide:** `user-profile-guide.md`
- **Brain Protection Rules:** `cortex-brain/governance/CORTEX-RULEBOOK.md`
- **Response Templates:** `cortex-brain/response-templates.yaml`

---

**Author:** Asif Hussain  
**Copyright:** ┬⌐ 2024-2025 Asif Hussain. All rights reserved.  
**Sprint Status:** ≡ƒÜº IN PROGRESS  
**Next Review:** December 5, 2025
