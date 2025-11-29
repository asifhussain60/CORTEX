# Scope Approval Gate for SWAGGER/TIMEFRAME Estimation

**Issue:** SWAGGER/TIMEFRAME system generates estimates without user-approved scope  
**Impact:** Critical - Estimates provided based on rough complexity scores without user confirmation  
**Status:** ⏳ PENDING IMPLEMENTATION  
**Priority:** HIGH

---

## 🎯 Problem Statement

### User Complaint (from estimate-issues.md)

> "Why did it estimate based on a rough estimate. This is terrible."

### Current Behavior (BROKEN)

```
User: "estimate authentication system"
    ↓
IntentRouter → IntentType.ESTIMATE
    ↓
PlanningOrchestrator.estimate_timeframe()
    ↓
TimeframeEstimator.estimate_timeframe(complexity=85, scope=None)
    ↓
❌ RESULT: 14-16 week estimate WITHOUT user scope approval
```

**Problems:**
1. ✅ No validation that scope is user-approved before estimation
2. ✅ SWAGGER complexity score treated as "approved scope" when it's just inference
3. ✅ No handoff to planner when scope is unclear/low-confidence
4. ✅ No bidirectional reference between SWAGGER and planner

### Required Behavior (FIX)

```
User: "estimate authentication system"
    ↓
IntentRouter → IntentType.ESTIMATE
    ↓
PlanningOrchestrator.estimate_timeframe()
    ↓
✅ CHECK: Is scope user-approved?
    ├── NO → Hand off to planner
    │         ↓
    │     PlanningOrchestrator.generate_plan()
    │         ↓
    │     User reviews/approves scope
    │         ↓
    │     Return to estimate_timeframe() with approved scope
    │
    └── YES → Continue to TimeframeEstimator
              ↓
          ✅ RESULT: Estimate with validated scope
```

---

## 📋 User Requirements

From conversation:

> "The Entry Point Module should not give estimates unless it has an approved scope from user."

> "If scope is not clear, hand off to planner so user can plan it but keep a link to the swag so that at the end it is handed back to swagger."

**Mandatory Requirements:**
1. **Scope Approval Gate** - Block estimates until user approves scope
2. **Planner Handoff** - When scope unclear, route to planning workflow
3. **Context Preservation** - Keep SWAGGER reference during planner handoff
4. **Bidirectional Return** - Planner hands approved scope back to estimator

---

## 🏗️ Implementation Design

### Component 1: Scope Approval Tracking

**File:** `src/agents/estimation/scope_inference_engine.py`

**Add to ScopeBoundary dataclass:**
```python
@dataclass
class ScopeBoundary:
    """Enhanced with user approval tracking"""
    # Existing fields
    entities: ScopeEntities
    confidence_score: float
    inference_source: str
    ambiguous_references: List[str]
    
    # NEW: User approval tracking
    user_approved: bool = False  # Default: not approved
    approval_timestamp: Optional[datetime] = None
    approval_method: Optional[str] = None  # 'interactive', 'plan', 'explicit'
    swagger_context_id: Optional[str] = None  # Link to SWAGGER analysis
```

**Methods to add:**
```python
def approve_scope(self, method: str = 'interactive') -> None:
    """Mark scope as user-approved"""
    self.user_approved = True
    self.approval_timestamp = datetime.now()
    self.approval_method = method

def is_approval_required(self) -> bool:
    """Check if user approval is needed"""
    return (
        self.confidence_score < 0.8 or  # Low confidence
        len(self.ambiguous_references) > 0 or  # Has ambiguities
        not self.user_approved  # Not yet approved
    )
```

---

### Component 2: Estimation Gate at PlanningOrchestrator

**File:** `src/orchestrators/planning_orchestrator.py`

**Modify estimate_timeframe() method (line 1557):**

```python
def estimate_timeframe(
    self,
    complexity: float,
    scope: Optional[Dict] = None,
    team_size: int = 1,
    velocity: Optional[float] = None,
    include_three_point: bool = False,
    scope_boundary: Optional[ScopeBoundary] = None  # NEW: Accept ScopeBoundary
) -> Dict[str, Any]:
    """
    Generate time estimates from SWAGGER complexity score
    
    ⚠️ CRITICAL: Estimates BLOCKED unless scope is user-approved
    
    Workflow:
    1. Check if scope is user-approved
    2. If NO → Hand off to planner for user clarification
    3. If YES → Proceed with estimation
    """
    from src.agents.estimation.scope_inference_engine import ScopeBoundary
    from src.agents.estimation.timeframe_estimator import TimeframeEstimator
    
    # STEP 1: Validate scope approval
    if scope_boundary is None and scope is not None:
        # Legacy call without ScopeBoundary - create one (treat as unapproved)
        scope_boundary = ScopeBoundary(
            entities=self._dict_to_scope_entities(scope),
            confidence_score=0.5,  # Unknown confidence
            inference_source='legacy',
            ambiguous_references=[],
            user_approved=False  # Default: not approved
        )
    
    # STEP 2: Approval gate
    if scope_boundary and scope_boundary.is_approval_required():
        # Scope NOT approved - hand off to planner
        return self._hand_off_to_planner_for_approval(
            complexity=complexity,
            scope_boundary=scope_boundary,
            team_size=team_size,
            velocity=velocity
        )
    
    # STEP 3: Scope approved - proceed with estimation
    estimator = TimeframeEstimator()
    estimate = estimator.estimate_timeframe(
        complexity=complexity,
        scope=scope or (scope_boundary.entities.__dict__ if scope_boundary else None),
        team_size=team_size,
        velocity=velocity
    )
    
    # ... rest of method (convert to dict, format report, etc.)
```

**New method: _hand_off_to_planner_for_approval:**

```python
def _hand_off_to_planner_for_approval(
    self,
    complexity: float,
    scope_boundary: ScopeBoundary,
    team_size: int,
    velocity: Optional[float]
) -> Dict[str, Any]:
    """
    Hand off to planner when scope requires user approval
    
    Preserves SWAGGER context for return path to estimator
    """
    # Generate unique context ID
    swagger_context_id = f"swagger-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    scope_boundary.swagger_context_id = swagger_context_id
    
    # Store SWAGGER context for later retrieval
    self._store_swagger_context(
        context_id=swagger_context_id,
        complexity=complexity,
        scope_boundary=scope_boundary,
        team_size=team_size,
        velocity=velocity
    )
    
    # Generate clarification prompt for user
    clarification_msg = self._generate_scope_clarification_prompt(
        scope_boundary=scope_boundary,
        confidence=scope_boundary.confidence_score
    )
    
    # Return handoff response (not an estimate)
    return {
        'status': 'scope_approval_required',
        'swagger_context_id': swagger_context_id,
        'confidence': scope_boundary.confidence_score,
        'clarification_prompt': clarification_msg,
        'next_action': 'plan',  # Route to planning workflow
        'message': (
            f"⚠️ **Scope Approval Required**\n\n"
            f"I've analyzed the scope with {scope_boundary.confidence_score:.0%} confidence, "
            f"but need your confirmation before generating time estimates.\n\n"
            f"{clarification_msg}\n\n"
            f"**Options:**\n"
            f"1. Review scope preview and approve: `approve scope {swagger_context_id}`\n"
            f"2. Create detailed plan first: `plan [feature name]`\n"
            f"3. Provide clarifications: Answer the questions above\n\n"
            f"Once scope is approved, I'll return to timeframe estimation."
        )
    }
```

**New method: _store_swagger_context:**

```python
def _store_swagger_context(
    self,
    context_id: str,
    complexity: float,
    scope_boundary: ScopeBoundary,
    team_size: int,
    velocity: Optional[float]
) -> None:
    """Store SWAGGER context for later retrieval (Tier 1 working memory)"""
    if not self.tier1:
        return
    
    context_data = {
        'context_id': context_id,
        'complexity': complexity,
        'scope_boundary': scope_boundary.__dict__,
        'team_size': team_size,
        'velocity': velocity,
        'created_at': datetime.now().isoformat(),
        'status': 'awaiting_approval'
    }
    
    # Store in Tier 1 working memory
    self.tier1.store_swagger_context(context_id, context_data)
```

**New method: _generate_scope_clarification_prompt:**

```python
def _generate_scope_clarification_prompt(
    self,
    scope_boundary: ScopeBoundary,
    confidence: float
) -> str:
    """Generate user-facing clarification prompt"""
    entities = scope_boundary.entities
    ambiguous = scope_boundary.ambiguous_references
    
    prompt_parts = [
        f"**Inferred Scope (Confidence: {confidence:.0%}):**",
        ""
    ]
    
    if entities.tables:
        prompt_parts.append(f"📊 **Database Tables:** {', '.join(entities.tables)}")
    if entities.files:
        prompt_parts.append(f"📁 **Files:** {', '.join(entities.files[:5])}..." if len(entities.files) > 5 else f"📁 **Files:** {', '.join(entities.files)}")
    if entities.services:
        prompt_parts.append(f"⚙️ **Services/APIs:** {', '.join(entities.services)}")
    if entities.dependencies:
        prompt_parts.append(f"🔗 **External Dependencies:** {', '.join(entities.dependencies)}")
    
    if ambiguous:
        prompt_parts.extend([
            "",
            "⚠️ **Ambiguous References (Need Clarification):**"
        ])
        for amb in ambiguous:
            prompt_parts.append(f"  • {amb}")
        prompt_parts.append("")
        prompt_parts.append("**Questions:**")
        prompt_parts.append("1. What exactly do these references mean in your application?")
        prompt_parts.append("2. Are there additional components not listed above?")
        prompt_parts.append("3. Should I analyze the codebase further for better scope accuracy?")
    else:
        prompt_parts.extend([
            "",
            "**Confirm:** Does this scope accurately represent your feature requirements?"
        ])
    
    return "\n".join(prompt_parts)
```

---

### Component 3: Planner Return Path

**New method: resume_estimation_with_approved_scope:**

```python
def resume_estimation_with_approved_scope(
    self,
    swagger_context_id: str,
    approved_scope: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Resume estimation after user approves scope via planning workflow
    
    Called when:
    1. User completes planning workflow
    2. User explicitly approves scope preview
    3. Planner returns to estimator with validated scope
    """
    # Retrieve stored SWAGGER context
    context = self.tier1.retrieve_swagger_context(swagger_context_id)
    if not context:
        return {
            'success': False,
            'error': f"SWAGGER context not found: {swagger_context_id}"
        }
    
    # Update scope if provided (from planning workflow)
    if approved_scope:
        context['scope_boundary']['entities'] = approved_scope
        context['scope_boundary']['user_approved'] = True
        context['scope_boundary']['approval_method'] = 'plan'
        context['scope_boundary']['approval_timestamp'] = datetime.now().isoformat()
    
    # Resume estimation with approved scope
    return self.estimate_timeframe(
        complexity=context['complexity'],
        scope=context['scope_boundary']['entities'],
        team_size=context['team_size'],
        velocity=context['velocity'],
        scope_boundary=ScopeBoundary(**context['scope_boundary'])
    )
```

---

### Component 4: Intent Router Updates

**File:** `src/cortex_agents/intent_router.py`

**Modify INTENT_RULE_CONTEXT for IntentType.ESTIMATE (line 304):**

```python
IntentType.ESTIMATE: {
    'rules_to_consider': ['DEFINITION_OF_READY', 'DOR_ENFORCEMENT', 'SCOPE_APPROVAL_REQUIRED'],  # NEW
    'requires_dor_validation': True,
    'requires_scope_approval': True,  # NEW: Block estimates without approval
    'skip_summary_generation': False,
    'requires_documentation': True,
    'create_persistent_artifact': True,
    'enable_parallel_analysis': True,
    'planner_handoff_on_low_confidence': True  # NEW: Auto-handoff to planner
},
```

---

### Component 5: Tier 1 Working Memory Extensions

**File:** `src/tier1/working_memory.py`

**New methods for SWAGGER context storage:**

```python
def store_swagger_context(self, context_id: str, context_data: Dict) -> bool:
    """Store SWAGGER context for estimation workflow"""
    try:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Ensure swagger_contexts table exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS swagger_contexts (
                context_id TEXT PRIMARY KEY,
                complexity REAL,
                scope_boundary TEXT,
                team_size INTEGER,
                velocity REAL,
                status TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        cursor.execute('''
            INSERT OR REPLACE INTO swagger_contexts 
            (context_id, complexity, scope_boundary, team_size, velocity, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            context_id,
            context_data['complexity'],
            json.dumps(context_data['scope_boundary']),
            context_data['team_size'],
            context_data.get('velocity'),
            context_data['status'],
            context_data['created_at'],
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error storing SWAGGER context: {e}")
        return False

def retrieve_swagger_context(self, context_id: str) -> Optional[Dict]:
    """Retrieve stored SWAGGER context"""
    try:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT complexity, scope_boundary, team_size, velocity, status, created_at, updated_at
            FROM swagger_contexts
            WHERE context_id = ?
        ''', (context_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'context_id': context_id,
                'complexity': row[0],
                'scope_boundary': json.loads(row[1]),
                'team_size': row[2],
                'velocity': row[3],
                'status': row[4],
                'created_at': row[5],
                'updated_at': row[6]
            }
        return None
    except Exception as e:
        print(f"Error retrieving SWAGGER context: {e}")
        return None

def update_swagger_context_status(self, context_id: str, status: str) -> bool:
    """Update SWAGGER context status (awaiting_approval → approved → estimated)"""
    try:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE swagger_contexts
            SET status = ?, updated_at = ?
            WHERE context_id = ?
        ''', (status, datetime.now().isoformat(), context_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating SWAGGER context status: {e}")
        return False
```

---

## 🔄 User Workflow Examples

### Example 1: Low-Confidence Scope → Planner Handoff

```
User: "estimate authentication system"

CORTEX:
   🔍 Analyzing scope...
   
   ⚠️ **Scope Approval Required**
   
   I've analyzed the scope with 65% confidence, but need your confirmation 
   before generating time estimates.
   
   **Inferred Scope (Confidence: 65%):**
   
   📊 **Database Tables:** users, roles, permissions, sessions
   📁 **Files:** auth.py, login.py, session_manager.py, ...
   ⚙️ **Services/APIs:** AuthenticationService, SessionManager
   🔗 **External Dependencies:** bcrypt, JWT
   
   ⚠️ **Ambiguous References (Need Clarification):**
     • "authentication system" - Single sign-on or per-application?
     • Session management - Centralized or distributed?
     • User migration - New system or migrate existing users?
   
   **Questions:**
   1. What exactly do these references mean in your application?
   2. Are there additional components not listed above?
   3. Should I analyze the codebase further for better scope accuracy?
   
   **Options:**
   1. Review scope preview and approve: `approve scope swagger-20251127-143000`
   2. Create detailed plan first: `plan authentication system`
   3. Provide clarifications: Answer the questions above
   
   Once scope is approved, I'll return to timeframe estimation.

User: "plan authentication system"

CORTEX:
   ✅ Routing to Planning Orchestrator...
   📸 Preserving SWAGGER context: swagger-20251127-143000
   
   [... Interactive planning workflow with DoR/DoD ...]
   
   ✅ Plan approved and complete!
   
   🔄 Returning to timeframe estimation with approved scope...
   
   [... Generates estimate with validated scope ...]
```

---

### Example 2: High-Confidence Scope → Direct Approval

```
User: "estimate user login feature"

CORTEX:
   🔍 Analyzing scope...
   
   **Inferred Scope (Confidence: 92%):**
   
   📊 **Database Tables:** users, sessions
   📁 **Files:** login.py, auth.py
   ⚙️ **Services/APIs:** AuthenticationService
   🔗 **External Dependencies:** bcrypt
   
   **Confirm:** Does this scope accurately represent your feature requirements?
   
   **Options:**
   1. Approve and estimate: `yes` or `approve scope`
   2. Refine scope: `plan user login feature`
   3. Modify scope: Describe adjustments

User: "yes"

CORTEX:
   ✅ Scope approved!
   
   📊 Timeframe Estimate:
   
   Story Points: 5
   Hours (Single Developer): 20.0 hours (2.5 days)
   Hours (Team of 2): 12.0 hours (1.5 days)
   Sprints: 0.5 sprints (1 week)
   
   [... Full estimate report ...]
```

---

### Example 3: User Provides Explicit Scope

```
User: "estimate adding payment processing with Stripe integration, 
       3 new database tables (payments, transactions, refunds), 
       and webhook handling"

CORTEX:
   🔍 Analyzing explicit scope...
   
   **Inferred Scope (Confidence: 95%):**
   
   📊 **Database Tables:** payments, transactions, refunds
   ⚙️ **Services/APIs:** PaymentService, StripeWebhookHandler
   🔗 **External Dependencies:** Stripe API, webhook server
   
   ✅ High-confidence scope detected from your explicit description.
   
   **Auto-approving scope** (you provided detailed requirements)
   
   📊 Timeframe Estimate:
   
   [... Generates estimate immediately ...]
```

---

## 📊 Implementation Phases

### Phase 1: Data Model (2 hours)

**Tasks:**
- ✅ Add `user_approved`, `approval_timestamp`, `approval_method`, `swagger_context_id` to ScopeBoundary dataclass
- ✅ Add `is_approval_required()` and `approve_scope()` methods
- ✅ Create Tier 1 database schema for swagger_contexts table
- ✅ Implement store/retrieve/update methods in WorkingMemory

**Testing:**
- Unit tests for ScopeBoundary approval methods
- Database operations (store/retrieve/update)

---

### Phase 2: Estimation Gate (3 hours)

**Tasks:**
- ✅ Modify `estimate_timeframe()` to check scope approval
- ✅ Implement `_hand_off_to_planner_for_approval()` method
- ✅ Implement `_store_swagger_context()` method
- ✅ Implement `_generate_scope_clarification_prompt()` method
- ✅ Add `resume_estimation_with_approved_scope()` method

**Testing:**
- Integration tests: Estimate blocked without approval
- Planner handoff workflow
- Context preservation during handoff

---

### Phase 3: Intent Router Updates (1 hour)

**Tasks:**
- ✅ Update INTENT_RULE_CONTEXT for IntentType.ESTIMATE
- ✅ Add `requires_scope_approval` flag
- ✅ Add `planner_handoff_on_low_confidence` flag

**Testing:**
- Intent classification with scope validation
- Routing decision based on approval status

---

### Phase 4: User Approval Commands (2 hours)

**Tasks:**
- ✅ Add `approve scope [context_id]` command trigger
- ✅ Add template entry for scope approval
- ✅ Implement approval workflow in PlanningOrchestrator

**Testing:**
- Natural language approval commands
- Approval via planning workflow completion
- Approval via explicit confirmation

---

### Phase 5: Documentation & Testing (2 hours)

**Tasks:**
- ✅ Update estimation guide with approval workflow
- ✅ Add examples to response templates
- ✅ End-to-end testing (all 3 examples above)
- ✅ Update CORTEX.prompt.md with new commands

**Testing:**
- Full workflow validation
- User acceptance testing

---

## 📝 Acceptance Criteria

### DoD Checklist

- [ ] Estimates BLOCKED unless scope is user-approved
- [ ] Low-confidence scope (<80%) automatically triggers planner handoff
- [ ] Planner handoff preserves SWAGGER context (complexity, scope, team size)
- [ ] User can approve scope via:
  - [ ] `approve scope [context_id]` command
  - [ ] Completing planning workflow (DoR/DoD validation)
  - [ ] Explicit confirmation ("yes", "looks good")
- [ ] Planner returns to estimator with approved scope automatically
- [ ] SWAGGER context stored in Tier 1 with 7-day retention
- [ ] All 3 workflow examples pass end-to-end tests
- [ ] Documentation updated (estimation guide, CORTEX.prompt.md, response templates)
- [ ] Zero breaking changes to existing estimation API

---

## 🔍 Testing Strategy

### Unit Tests

```python
# test_scope_approval_gate.py

def test_scope_boundary_approval():
    """Test scope approval tracking"""
    scope = ScopeBoundary(
        entities=ScopeEntities(...),
        confidence_score=0.65,
        inference_source='swagger',
        ambiguous_references=['auth system']
    )
    
    assert scope.user_approved == False
    assert scope.is_approval_required() == True
    
    scope.approve_scope(method='interactive')
    
    assert scope.user_approved == True
    assert scope.approval_method == 'interactive'

def test_estimation_gate_blocks_unapproved():
    """Test estimation blocked without approval"""
    orchestrator = PlanningOrchestrator()
    
    scope_boundary = ScopeBoundary(
        entities=ScopeEntities(...),
        confidence_score=0.70,
        inference_source='swagger',
        ambiguous_references=[],
        user_approved=False  # NOT approved
    )
    
    result = orchestrator.estimate_timeframe(
        complexity=75,
        scope_boundary=scope_boundary
    )
    
    assert result['status'] == 'scope_approval_required'
    assert 'swagger_context_id' in result
    assert 'clarification_prompt' in result

def test_estimation_proceeds_with_approval():
    """Test estimation proceeds when approved"""
    orchestrator = PlanningOrchestrator()
    
    scope_boundary = ScopeBoundary(
        entities=ScopeEntities(...),
        confidence_score=0.95,
        inference_source='explicit',
        ambiguous_references=[],
        user_approved=True  # APPROVED
    )
    
    result = orchestrator.estimate_timeframe(
        complexity=75,
        scope_boundary=scope_boundary
    )
    
    assert 'status' not in result  # No blocking
    assert 'story_points' in result
    assert 'hours_single' in result
```

### Integration Tests

```python
# test_planner_handoff_workflow.py

def test_low_confidence_triggers_handoff():
    """Test low-confidence scope triggers planner handoff"""
    orchestrator = PlanningOrchestrator()
    
    # Low confidence (65%) should trigger handoff
    result = orchestrator.estimate_timeframe(
        complexity=85,
        scope_boundary=ScopeBoundary(
            entities=ScopeEntities(...),
            confidence_score=0.65,
            user_approved=False
        )
    )
    
    assert result['status'] == 'scope_approval_required'
    assert result['next_action'] == 'plan'

def test_planner_return_path():
    """Test planner returns to estimator with approved scope"""
    orchestrator = PlanningOrchestrator()
    
    # Initial estimate (blocked)
    result1 = orchestrator.estimate_timeframe(
        complexity=85,
        scope_boundary=ScopeBoundary(
            entities=ScopeEntities(...),
            confidence_score=0.65,
            user_approved=False
        )
    )
    
    context_id = result1['swagger_context_id']
    
    # User completes planning workflow
    approved_scope = {
        'tables': ['users', 'roles', 'permissions'],
        'files': ['auth.py', 'login.py'],
        'services': ['AuthService']
    }
    
    # Resume estimation with approved scope
    result2 = orchestrator.resume_estimation_with_approved_scope(
        swagger_context_id=context_id,
        approved_scope=approved_scope
    )
    
    assert 'story_points' in result2
    assert result2['team_size'] == 1  # Preserved from original context
```

---

## 🚀 Deployment Plan

### Step 1: Schema Migration
- Run Tier 1 schema migration (swagger_contexts table)
- Verify table creation successful
- Test store/retrieve operations

### Step 2: Code Deployment
- Deploy modified PlanningOrchestrator
- Deploy modified IntentRouter
- Deploy modified WorkingMemory

### Step 3: Validation
- Run unit tests (90%+ pass rate)
- Run integration tests (all 3 workflow examples)
- Manual testing with real estimation requests

### Step 4: Documentation
- Update `.github/prompts/modules/timeframe-estimator-guide.md`
- Update `.github/prompts/CORTEX.prompt.md`
- Add examples to response-templates.yaml

---

## 📚 Related Documentation

- **SWAGGER System:** `src/agents/estimation/scope_inference_engine.py`
- **TIMEFRAME Estimator:** `src/agents/estimation/timeframe_estimator.py`
- **Planning Orchestrator:** `src/orchestrators/planning_orchestrator.py`
- **Intent Router:** `src/cortex_agents/intent_router.py`
- **Response Templates:** `cortex-brain/response-templates.yaml`

---

**Author:** Asif Hussain  
**Created:** 2025-11-27  
**Status:** Design Complete, Implementation Pending  
**Estimated Implementation:** 10 hours (2 sprints)
