# Architecture Enhancement Proposal: Response Rendering Pipeline

**Investigation ID:** INVEST-20260103-150000  
**Author:** Asif Hussain  
**Date:** January 3, 2026  
**Status:** 📋 DESIGN PHASE  
**Approval:** ✅ APPROVED (Option B - Architecture Refactor)

---

## 🎯 Executive Summary

**Problem:** Master Orchestrator lacks mechanism to render OrchestratorResult messages to user-facing markdown  
**Solution:** Create ResponseRenderer + ResponseMiddleware architecture  
**Impact:** Fixes continuation prompt display + 4 similar issues across 9 components  
**Investment:** 8 hours  
**Risk:** Low (backward compatible)  
**ROI:** High (fixes 5 issues, establishes rendering architecture)

---

## 📊 Current State Analysis

### Architecture Gap: No Response Rendering Pipeline

```
CURRENT FLOW (BROKEN):
User Request → Master Orchestrator → Orchestrator → OrchestratorResult
                                                            ↓
                                                     message="Plan created\n\n⚠️ TOKEN WARNING..."
                                                            ↓
                                                    Master Orchestrator
                                                            ↓
                                          return {"message": result.message}
                                                            ↓
                                                    ??? (who displays?)
                                                            ↓
                                                    ❌ USER NEVER SEES IT
```

### Problems with Current Approach

1. **No Standard Rendering:** Each orchestrator formats messages independently
2. **No Template Integration:** response-templates-v4.yaml not used
3. **No Middleware:** System messages (token warnings) appended manually
4. **Fragile:** Easy to forget appending warnings, inconsistent formatting
5. **Not Extensible:** Can't add new message types without modifying each orchestrator

---

## 🏗️ Proposed Architecture

### Enhanced Flow (WITH Response Rendering Pipeline)

```
PROPOSED FLOW (FIXED):
User Request → Master Orchestrator → Orchestrator → OrchestratorResult
                                                            ↓
                                                     message="Plan created"
                                                     metadata={'token_status': {...}}
                                                            ↓
                                        ┌───────────────────┴────────────────────┐
                                        │                                        │
                                        ▼                                        ▼
                            ResponseMiddleware                         ResponseRenderer
                         (inject system messages)                   (format markdown)
                                        │                                        │
                                        │  enriched_result:                     │
                                        │  - message                             │
                                        │  - system_messages: [                  │
                                        │      "⚠️ TOKEN WARNING...",            │
                                        │      "📋 Continuation prompt..."      │
                                        │    ]                                   │
                                        └───────────────────┬────────────────────┘
                                                            ▼
                                                  Formatted Markdown
                                                            ↓
                                               ## 🧠 CORTEX Response
                                               
                                               ✅ Plan created successfully
                                               
                                               ⚠️ **TOKEN WARNING**: ...
                                               📋 **Continuation prompt**: ...
                                               
                                               **Next:** Review plan...
                                                            ↓
                                                    ✅ USER SEES IT
```

---

## 🔧 Component Design

### Component 1: ResponseRenderer

**Purpose:** Convert OrchestratorResult to user-facing markdown using response-templates-v4.yaml

**Responsibilities:**
1. Tier routing (INSTANT → COMPREHENSIVE)
2. Block selection (header, progress, response, changes, next_steps)
3. Template rendering (Jinja2)
4. Markdown composition

**API:**

```python
class ResponseRenderer:
    """
    Unified response rendering for all orchestrators.
    
    Features:
    - Template-driven formatting (response-templates-v4.yaml)
    - Tier routing based on complexity
    - Block composition (LEGO-style)
    - Markdown generation
    - Performance: <10ms per render
    """
    
    def __init__(
        self,
        template_path: str = "cortex-brain/response-templates-v4.yaml",
        cache_templates: bool = True
    ):
        """
        Initialize ResponseRenderer.
        
        Args:
            template_path: Path to response templates YAML
            cache_templates: Cache parsed templates for performance
        """
        self.template_config = self._load_templates(template_path)
        self.template_cache = {} if cache_templates else None
        self.logger = logging.getLogger(__name__)
    
    def render(
        self,
        result: OrchestratorResult,
        tier: str = 'auto',
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Render OrchestratorResult to user-facing markdown.
        
        Args:
            result: Orchestrator execution result
            tier: Response tier (auto|INSTANT|FOCUSED|STRUCTURED|COMPREHENSIVE)
            context: Additional rendering context
        
        Returns:
            Formatted markdown string
        
        Example:
            >>> renderer = ResponseRenderer()
            >>> result = OrchestratorResult(
            ...     status=OrchestratorStatus.COMPLETED,
            ...     message="Plan created successfully",
            ...     metadata={'plan_id': 'user-auth-123'}
            ... )
            >>> markdown = renderer.render(result, tier='FOCUSED')
            >>> print(markdown)
            ## 🧠 CORTEX Response
            
            ✅ Plan created successfully
            
            **Plan ID:** user-auth-123
            
            **Next:** Review plan in `cortex-brain/documents/planning/active/user-auth-123/`
        """
        # Step 1: Determine tier
        tier = self._determine_tier(result, tier, context)
        
        # Step 2: Select blocks
        blocks = self._select_blocks(result, tier, context)
        
        # Step 3: Render blocks
        rendered_blocks = [
            self._render_block(block, result, context)
            for block in blocks
        ]
        
        # Step 4: Compose final markdown
        return self._compose_response(rendered_blocks, tier)
    
    def _determine_tier(
        self,
        result: OrchestratorResult,
        tier: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """
        Determine response tier based on result complexity.
        
        Rules:
        - INSTANT: Simple success/error, <50 tokens
        - FOCUSED: Single concept, 50-200 tokens
        - STRUCTURED: Multi-faceted, 200-600 tokens
        - COMPREHENSIVE: Complex operations, 600+ tokens
        
        Args:
            result: Orchestrator result
            tier: Requested tier ('auto' for automatic)
            context: Additional context
        
        Returns:
            Tier name (INSTANT|FOCUSED|STRUCTURED|COMPREHENSIVE)
        """
        if tier != 'auto':
            return tier
        
        # Heuristic: Estimate complexity
        token_count = len(result.message) // 4  # ~4 chars per token
        
        if result.status == OrchestratorStatus.FAILED:
            return 'FOCUSED'  # Errors always FOCUSED minimum
        
        if token_count < 50:
            return 'INSTANT'
        elif token_count < 200:
            return 'FOCUSED'
        elif token_count < 600:
            return 'STRUCTURED'
        else:
            return 'COMPREHENSIVE'
    
    def _select_blocks(
        self,
        result: OrchestratorResult,
        tier: str,
        context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Select response blocks based on tier and context signals.
        
        Context Signals:
        - operation_type: planning, execution, analysis, etc.
        - response_phase: start, in_progress, complete, error
        - orchestrator_type: planning, vacuum, cleanup, etc.
        - files_modified: bool
        - validation_ran: bool
        - multi_phase_operation: bool
        
        Args:
            result: Orchestrator result
            tier: Response tier
            context: Rendering context
        
        Returns:
            List of blocks to render with priority
        """
        blocks = []
        ctx = context or {}
        
        # Mandatory blocks (always included)
        blocks.append({
            'name': 'cortex_header',
            'priority': 100,
            'config': self.template_config['blocks']['cortex_header']
        })
        
        # Conditional blocks based on context signals
        if ctx.get('multi_phase_operation'):
            blocks.append({
                'name': 'progress_tracker',
                'priority': 90,
                'config': self.template_config['blocks']['progress_tracker']
            })
        
        if result.status == OrchestratorStatus.FAILED:
            blocks.append({
                'name': 'error_details',
                'priority': 85,
                'config': self.template_config['blocks']['error_details']
            })
        
        # Response body (always included)
        blocks.append({
            'name': 'response',
            'priority': 80,
            'config': self.template_config['blocks']['response']
        })
        
        # Changes block (if files modified)
        if ctx.get('files_modified') or result.artifacts:
            blocks.append({
                'name': 'changes',
                'priority': 75,
                'config': self.template_config['blocks']['changes']
            })
        
        # Next steps (mandatory unless complete)
        if result.status != OrchestratorStatus.COMPLETED:
            blocks.append({
                'name': 'next_steps',
                'priority': 70,
                'config': self.template_config['blocks']['next_steps']
            })
        else:
            blocks.append({
                'name': 'completion',
                'priority': 70,
                'config': self.template_config['blocks']['completion']
            })
        
        # Sort by priority (high to low)
        blocks.sort(key=lambda b: b['priority'], reverse=True)
        
        return blocks
    
    def _render_block(
        self,
        block: Dict[str, Any],
        result: OrchestratorResult,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """
        Render individual block to markdown.
        
        Args:
            block: Block configuration
            result: Orchestrator result
            context: Rendering context
        
        Returns:
            Rendered markdown for block
        """
        block_name = block['name']
        config = block['config']
        
        # Get block template
        template_str = config.get('template', '')
        
        # Prepare template context
        template_context = {
            'result': result,
            'context': context or {},
            'status_emoji': self._get_status_emoji(result.status),
            'title': config.get('title', ''),
            'emoji': config.get('emoji', '')
        }
        
        # Render template (simple string substitution for now)
        # Future: Use Jinja2 for more complex templates
        rendered = template_str.format(**template_context)
        
        return rendered
    
    def _compose_response(
        self,
        rendered_blocks: List[str],
        tier: str
    ) -> str:
        """
        Compose final markdown from rendered blocks.
        
        Args:
            rendered_blocks: List of rendered block strings
            tier: Response tier
        
        Returns:
            Final markdown response
        """
        # Join blocks with double newlines
        markdown = '\n\n'.join(block for block in rendered_blocks if block)
        
        # Add tier-specific formatting
        if tier == 'COMPREHENSIVE':
            markdown += '\n\n---\n\n'
        
        return markdown
    
    def _get_status_emoji(self, status: OrchestratorStatus) -> str:
        """Get emoji for orchestrator status."""
        return {
            OrchestratorStatus.COMPLETED: '✅',
            OrchestratorStatus.SUCCESS: '✅',
            OrchestratorStatus.FAILED: '❌',
            OrchestratorStatus.CANCELLED: '🚫',
            OrchestratorStatus.IN_PROGRESS: '⏳'
        }.get(status, '❓')
    
    def _load_templates(self, path: str) -> Dict[str, Any]:
        """Load response templates from YAML file."""
        import yaml
        from pathlib import Path
        
        template_file = Path(path)
        if not template_file.exists():
            raise FileNotFoundError(f"Template file not found: {path}")
        
        with open(template_file, 'r') as f:
            return yaml.safe_load(f)
```

**File:** `/src/orchestrators/response_renderer.py` (300 lines)  
**Tests:** 15 unit tests (200 lines)  
**Performance:** <10ms per render (target)

---

### Component 2: ResponseMiddleware

**Purpose:** Inject system messages into OrchestratorResult before rendering

**Responsibilities:**
1. Token warning injection
2. Security alert injection
3. Deprecation notice injection
4. Success message enrichment
5. Priority ordering

**API:**

```python
class ResponseMiddleware:
    """
    Post-execution middleware for injecting system messages.
    
    Features:
    - Token warnings (from check_token_usage())
    - Security alerts
    - Deprecation notices
    - Success message enrichment
    - Priority-based message ordering
    """
    
    def __init__(
        self,
        token_warning_threshold: int = 80000,
        enable_security_alerts: bool = True,
        enable_deprecation_notices: bool = True
    ):
        """
        Initialize ResponseMiddleware.
        
        Args:
            token_warning_threshold: Token threshold for warnings
            enable_security_alerts: Enable security alert injection
            enable_deprecation_notices: Enable deprecation notice injection
        """
        self.token_warning_threshold = token_warning_threshold
        self.enable_security_alerts = enable_security_alerts
        self.enable_deprecation_notices = enable_deprecation_notices
        self.logger = logging.getLogger(__name__)
    
    def inject_system_messages(
        self,
        result: OrchestratorResult,
        context: Dict[str, Any]
    ) -> OrchestratorResult:
        """
        Inject system messages into orchestrator result.
        
        System Messages:
        - Token warnings (HIGH priority)
        - Security alerts (CRITICAL priority)
        - Deprecation notices (MEDIUM priority)
        - Success enrichment (LOW priority)
        
        Args:
            result: Original orchestrator result
            context: Execution context
        
        Returns:
            Enriched OrchestratorResult with system messages
        
        Example:
            >>> middleware = ResponseMiddleware()
            >>> result = OrchestratorResult(
            ...     status=OrchestratorStatus.COMPLETED,
            ...     message="Plan created successfully",
            ...     metadata={'token_status': {'should_warn': True, ...}}
            ... )
            >>> enriched = middleware.inject_system_messages(result, {})
            >>> print(enriched.message)
            Plan created successfully
            
            ⚠️ **TOKEN WARNING**: Estimated 85,000 tokens (106.2% of 80,000 threshold).
            
            📋 **Continuation prompt updated**: `tracking/CONTINUATION-PROMPT.md`
            💡 **Recommendation**: Consider copying the continuation prompt...
        """
        system_messages = []
        
        # Priority 1: Security alerts (CRITICAL)
        if self.enable_security_alerts:
            security_messages = self._inject_security_alerts(result, context)
            system_messages.extend(security_messages)
        
        # Priority 2: Token warnings (HIGH)
        token_message = self._inject_token_warning(result, context)
        if token_message:
            system_messages.append(token_message)
        
        # Priority 3: Deprecation notices (MEDIUM)
        if self.enable_deprecation_notices:
            deprecation_messages = self._inject_deprecation_notices(result, context)
            system_messages.extend(deprecation_messages)
        
        # Priority 4: Success enrichment (LOW)
        enrichment_messages = self._inject_success_enrichment(result, context)
        system_messages.extend(enrichment_messages)
        
        # Append system messages to result message
        if system_messages:
            enriched_message = result.message + '\n\n' + '\n\n'.join(system_messages)
            
            # Create new OrchestratorResult with enriched message
            return OrchestratorResult(
                status=result.status,
                success=result.success,
                message=enriched_message,
                data=result.data,
                artifacts=result.artifacts,
                errors=result.errors,
                execution_time_seconds=result.execution_time_seconds
            )
        
        return result
    
    def _inject_token_warning(
        self,
        result: OrchestratorResult,
        context: Dict[str, Any]
    ) -> Optional[str]:
        """
        Inject token warning if threshold exceeded.
        
        Reads from result.metadata['token_status'] or result.data['token_status']
        
        Args:
            result: Orchestrator result
            context: Execution context
        
        Returns:
            Token warning message or None
        """
        # Check metadata first
        metadata = getattr(result, 'metadata', None) or result.data or {}
        token_status = metadata.get('token_status')
        
        if not token_status or not token_status.get('should_warn'):
            return None
        
        # Format token warning message
        estimated = token_status.get('estimated_tokens', 0)
        threshold = token_status.get('threshold', self.token_warning_threshold)
        percentage = token_status.get('percentage', 0)
        
        warning = (
            f"⚠️ **TOKEN WARNING**: Estimated {estimated:,} tokens "
            f"({percentage:.1f}% of {threshold:,} threshold).\n\n"
            f"📋 **Continuation prompt updated**: `tracking/CONTINUATION-PROMPT.md`\n"
            f"💡 **Recommendation**: Consider copying the continuation prompt "
            f"for session handoff to maintain context across chat sessions."
        )
        
        self.logger.info(f"Token warning injected: {estimated} tokens")
        
        return warning
    
    def _inject_security_alerts(
        self,
        result: OrchestratorResult,
        context: Dict[str, Any]
    ) -> List[str]:
        """
        Inject security alerts if risks detected.
        
        Args:
            result: Orchestrator result
            context: Execution context
        
        Returns:
            List of security alert messages
        """
        alerts = []
        
        # Check for security risks in metadata
        metadata = getattr(result, 'metadata', None) or result.data or {}
        security_risks = metadata.get('security_risks', [])
        
        for risk in security_risks:
            severity = risk.get('severity', 'MEDIUM')
            message = risk.get('message', 'Security risk detected')
            
            alert = f"🔒 **SECURITY ALERT** ({severity}): {message}"
            alerts.append(alert)
            
            self.logger.warning(f"Security alert injected: {severity} - {message}")
        
        return alerts
    
    def _inject_deprecation_notices(
        self,
        result: OrchestratorResult,
        context: Dict[str, Any]
    ) -> List[str]:
        """
        Inject deprecation notices if deprecated features used.
        
        Args:
            result: Orchestrator result
            context: Execution context
        
        Returns:
            List of deprecation notice messages
        """
        notices = []
        
        # Check for deprecation warnings in metadata
        metadata = getattr(result, 'metadata', None) or result.data or {}
        deprecations = metadata.get('deprecations', [])
        
        for deprecation in deprecations:
            feature = deprecation.get('feature', 'Unknown feature')
            alternative = deprecation.get('alternative', 'See documentation')
            
            notice = (
                f"⚠️ **DEPRECATION NOTICE**: `{feature}` is deprecated. "
                f"Use `{alternative}` instead."
            )
            notices.append(notice)
            
            self.logger.info(f"Deprecation notice injected: {feature}")
        
        return notices
    
    def _inject_success_enrichment(
        self,
        result: OrchestratorResult,
        context: Dict[str, Any]
    ) -> List[str]:
        """
        Inject success message enrichment (metadata, metrics, etc.).
        
        Args:
            result: Orchestrator result
            context: Execution context
        
        Returns:
            List of enrichment messages
        """
        enrichments = []
        
        if result.status != OrchestratorStatus.COMPLETED:
            return enrichments
        
        # Add execution time if available
        if result.execution_time_seconds:
            duration = result.execution_time_seconds
            enrichments.append(f"⏱️ **Duration**: {duration:.1f}s")
        
        # Add artifact count if available
        if result.artifacts:
            count = len(result.artifacts)
            enrichments.append(f"📁 **Artifacts Created**: {count}")
        
        return enrichments
```

**File:** `/src/orchestrators/response_middleware.py` (150 lines)  
**Tests:** 10 unit tests (100 lines)  
**Performance:** <5ms per injection (target)

---

### Component 3: Master Orchestrator Integration

**Changes Required:**

```python
# File: src/orchestrators/master_orchestrator.py

from src.orchestrators.response_renderer import ResponseRenderer
from src.orchestrators.response_middleware import ResponseMiddleware

class MasterOrchestrator:
    """
    Master orchestrator for routing and coordinating all CORTEX orchestrators.
    """
    
    def __init__(
        self,
        config_path: str,
        registry: Optional[OrchestratorRegistry] = None,
        state_manager: Optional[StateManager] = None
    ):
        """Initialize Master Orchestrator."""
        # ...existing initialization...
        
        # NEW: Initialize response rendering components
        self.response_renderer = ResponseRenderer(
            template_path="cortex-brain/response-templates-v4.yaml",
            cache_templates=True
        )
        
        self.response_middleware = ResponseMiddleware(
            token_warning_threshold=80000,
            enable_security_alerts=True,
            enable_deprecation_notices=True
        )
        
        self.logger.info("Response rendering pipeline initialized")
    
    def handle_request(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:  # ✅ CHANGED: Returns str (markdown) instead of dict
        """
        Handle user request by routing to appropriate orchestrator.
        
        Args:
            user_input: User's request
            context: Optional execution context
        
        Returns:
            Formatted markdown response (ready for display)
        
        Raises:
            ValueError: If no matching orchestrator found
            RuntimeError: If execution fails
        """
        ctx = context or {}
        
        # Step 1: Normalize input
        normalized_input = self._normalize_input(user_input)
        
        # Step 2: Route to orchestrator
        match = self.route_request(normalized_input, ctx)
        
        if not match.is_matched:
            # Return formatted error message
            return self._render_error_response(
                "No matching orchestrator found for your request. "
                "Try 'help' to see available commands."
            )
        
        # Step 3: Check for holistic review trigger (if applicable)
        review_config = self._check_review_schedule(match.orchestrator_id, ctx)
        if review_config:
            # Execute review first
            review_result = self.execute_orchestrator(
                "holistic_review_orchestrator",
                params={
                    'review_number': review_config['review_number'],
                    'scope': review_config['scope'],
                    'parent_plan_id': ctx.get('parent_plan_id')
                }
            )
            
            # Inject review insights into context
            if review_result.success:
                insights = review_result.metadata.get('insights', [])
                ctx['review_insights'] = insights
                self.logger.info(f"Review insights injected: {len(insights)} insights")
        
        # Step 4: Execute target orchestrator
        try:
            result = self.execute_orchestrator(
                match.orchestrator_id,
                params={'user_input': user_input, **ctx}
            )
            
            # NEW: Step 5 - Inject system messages (token warnings, etc.)
            enriched_result = self.response_middleware.inject_system_messages(
                result,
                context=ctx
            )
            
            # NEW: Step 6 - Render to user-facing markdown
            markdown_response = self.response_renderer.render(
                enriched_result,
                tier='auto',  # Auto-detect tier based on complexity
                context=ctx
            )
            
            # ✅ Return formatted markdown (ready for display)
            return markdown_response
            
        except Exception as e:
            self.logger.error(f"Orchestrator execution failed: {e}", exc_info=True)
            
            # Return formatted error response
            return self._render_error_response(
                f"Execution failed: {str(e)}"
            )
    
    def _render_error_response(self, error_message: str) -> str:
        """
        Render error message using response renderer.
        
        Args:
            error_message: Error message
        
        Returns:
            Formatted error markdown
        """
        error_result = OrchestratorResult(
            status=OrchestratorStatus.FAILED,
            success=False,
            message=error_message,
            errors=[error_message]
        )
        
        return self.response_renderer.render(
            error_result,
            tier='FOCUSED',
            context={'error': True}
        )
```

**Changes Summary:**
- Add `ResponseRenderer` and `ResponseMiddleware` instantiation in `__init__`
- Modify `handle_request()` to return `str` instead of `dict`
- Add Step 5 (inject system messages)
- Add Step 6 (render to markdown)
- Update error handling to use renderer

**Files Modified:** 1  
**Lines Added:** +50  
**Breaking Changes:** 0 (callers already expect string response)

---

## 🧪 Testing Strategy

### Unit Tests (25 tests, 300 lines)

#### ResponseRenderer Tests (15 tests)
1. `test_render_instant_tier` - Simple success message
2. `test_render_focused_tier` - Single concept response
3. `test_render_structured_tier` - Multi-faceted response
4. `test_render_comprehensive_tier` - Complex operation response
5. `test_auto_tier_detection` - Automatic tier selection
6. `test_block_selection_basic` - Mandatory blocks included
7. `test_block_selection_with_progress` - Progress block when multi-phase
8. `test_block_selection_with_errors` - Error block when failed
9. `test_block_selection_with_artifacts` - Changes block when files modified
10. `test_template_rendering` - Jinja2 template rendering
11. `test_status_emoji_mapping` - Correct emoji for each status
12. `test_invalid_template_path` - Error handling for missing templates
13. `test_empty_result_message` - Handle empty messages gracefully
14. `test_rendering_performance` - <10ms per render
15. `test_template_caching` - Cache hit improves performance

#### ResponseMiddleware Tests (10 tests)
1. `test_inject_token_warning_above_threshold` - Warning injected
2. `test_inject_token_warning_below_threshold` - No warning
3. `test_inject_security_alert_critical` - Security alert formatting
4. `test_inject_deprecation_notice` - Deprecation notice formatting
5. `test_inject_success_enrichment` - Duration and artifact count
6. `test_message_priority_ordering` - Security > Token > Deprecation > Success
7. `test_no_system_messages` - Returns original result unchanged
8. `test_middleware_disabled` - Respects enable flags
9. `test_missing_metadata` - Graceful handling of missing metadata
10. `test_middleware_performance` - <5ms per injection

---

### Integration Tests (8 tests, 100 lines)

#### Master Orchestrator Integration Tests
1. `test_planning_v5_with_token_warning` - Planning orchestrator + token warning display
2. `test_vacuum_v2_with_completion_message` - Vacuum orchestrator + success enrichment
3. `test_error_response_rendering` - Error message formatting
4. `test_holistic_review_auto_trigger` - Review trigger + insights injection + rendering
5. `test_security_alert_display` - Security alert in response
6. `test_deprecation_notice_display` - Deprecation notice in response
7. `test_multi_phase_progress_display` - Progress bar rendering
8. `test_end_to_end_full_workflow` - Complete user request → display flow

---

### Manual Testing Scenarios

#### Scenario 1: Token Warning Display
```
User: "plan user authentication system"
Expected:
  1. Planning v5 executes
  2. Creates plan
  3. Token warning appears in response:
     "⚠️ TOKEN WARNING: Estimated 85,000 tokens (106.2%)..."
  4. Continuation prompt location mentioned
```

#### Scenario 2: Vacuum Completion
```
User: "vacuum /Users/user/project"
Expected:
  1. Vacuum v2 executes
  2. Completes cleanup
  3. Success message with enrichment:
     "✅ Vacuum completed successfully in 12.3s
      📁 Artifacts Created: 3"
```

#### Scenario 3: Error Handling
```
User: "plan" (missing feature name)
Expected:
  1. Planning v5 executes
  2. Returns error
  3. Formatted error message:
     "❌ Planning failed: Feature name required"
```

---

## 📊 Migration Strategy

### Phase 1: Create ResponseRenderer (2h)
**Goal:** Implement core rendering component

**Tasks:**
1. Create `/src/orchestrators/response_renderer.py`
2. Implement tier routing logic
3. Implement block selection logic
4. Implement template rendering
5. Create 15 unit tests
6. Verify 95%+ coverage

**Deliverables:**
- response_renderer.py (300 lines)
- test_response_renderer.py (200 lines)
- Coverage report (95%+)

---

### Phase 2: Create ResponseMiddleware (1h)
**Goal:** Implement message injection component

**Tasks:**
1. Create `/src/orchestrators/response_middleware.py`
2. Implement token warning injection
3. Implement security alert injection
4. Implement deprecation notice injection
5. Implement success enrichment
6. Create 10 unit tests
7. Verify 95%+ coverage

**Deliverables:**
- response_middleware.py (150 lines)
- test_response_middleware.py (100 lines)
- Coverage report (95%+)

---

### Phase 3: Integrate with Master Orchestrator (1h)
**Goal:** Wire components into Master Orchestrator

**Tasks:**
1. Add ResponseRenderer + ResponseMiddleware to `__init__`
2. Modify `handle_request()` to use renderer
3. Update `_render_error_response()` helper
4. Create 8 integration tests
5. Verify 90%+ coverage on integration

**Deliverables:**
- master_orchestrator.py (+50 lines)
- test_master_orchestrator_integration.py (100 lines)
- Coverage report (90%+)

---

### Phase 4: Update Orchestrators (2h)
**Goal:** Remove manual message appending

**Priority 1: Planning v5**
```python
# BEFORE
token_status = self.check_token_usage()
if token_status['should_warn'] and token_status.get('user_message'):
    success_message += token_status['user_message']

# AFTER (remove manual appending)
token_status = self.check_token_usage()
# Middleware handles injection automatically
```

**Priority 2: Vacuum v2**
```python
# BEFORE
final_token_check = self.check_token_usage()
if final_token_check.get('user_message'):
    completion_message += final_token_check['user_message']

# AFTER (remove manual appending)
final_token_check = self.check_token_usage()
# Middleware handles injection automatically
```

**Priority 3: Other Orchestrators (Optional)**
- Cleanup v2, ADO v2, Sanitization v1, etc.
- Optional cleanup (backward compatible)

**Tasks:**
1. Update Planning v5 (remove manual appending)
2. Update Vacuum v2 (remove manual appending)
3. Add `token_status` to metadata for middleware
4. Test each orchestrator individually
5. Verify no regressions

**Deliverables:**
- planning_orchestrator_v5.py (modified)
- vacuum_orchestrator_v2.py (modified)
- Test results (all tests pass)

---

### Phase 5: Testing & Validation (1.5h)
**Goal:** Comprehensive testing

**Tasks:**
1. Run full test suite (33 tests)
2. Generate coverage report (verify 95%+)
3. Manual testing (3 scenarios)
4. Performance testing (<10ms render)
5. Regression testing (all orchestrators)

**Deliverables:**
- Coverage report (HTML)
- Manual test results document
- Performance benchmark results

---

### Phase 6: Documentation (0.5h)
**Goal:** Update all documentation

**Tasks:**
1. Create `docs/architecture/response-rendering-pipeline.md`
2. Create `docs/guides/creating-orchestrator-messages.md`
3. Update `CORTEX.prompt.md` (add rendering architecture)
4. Update `master-orchestrator.md`
5. Update `BaseOrchestrator.md`
6. Create `CHANGELOG.md` entry

**Deliverables:**
- 2 new documents (350 lines total)
- 4 updated documents
- CHANGELOG entry

---

## ✅ Success Criteria

### Functional Requirements
- ✅ Token warnings display in chat responses
- ✅ Error messages display with formatting
- ✅ Success messages include metadata (duration, artifacts)
- ✅ All orchestrators display messages consistently
- ✅ Security alerts display when risks detected
- ✅ Deprecation notices display when deprecated features used

### Quality Requirements
- ✅ 95%+ test coverage on ResponseRenderer
- ✅ 95%+ test coverage on ResponseMiddleware
- ✅ 90%+ test coverage on Master Orchestrator integration
- ✅ Zero breaking changes (backward compatible)
- ✅ Response rendering <10ms (performance target)
- ✅ Middleware injection <5ms (performance target)

### Documentation Requirements
- ✅ Architecture document (response-rendering-pipeline.md)
- ✅ Developer guide (creating-orchestrator-messages.md)
- ✅ Updated system documentation (4 files)
- ✅ CHANGELOG entry

---

## 🔒 Backward Compatibility

### Orchestrators with Manual Appending
**Status:** ✅ Compatible

Orchestrators that manually append token warnings will continue to work:
```python
# Old code (still works)
if token_status['should_warn']:
    message += token_status['user_message']

# Middleware detects manual appending and skips injection
# No duplicate warnings displayed
```

**Detection Logic:**
```python
# In ResponseMiddleware
if 'TOKEN WARNING' in result.message:
    # Already manually appended, skip injection
    return None
```

### Orchestrators Returning OrchestratorResult
**Status:** ✅ Compatible

All orchestrators already return `OrchestratorResult`:
```python
return OrchestratorResult(
    status=OrchestratorStatus.COMPLETED,
    message="Success message",
    data={...}
)
```

No changes required to existing orchestrators (unless removing manual appending).

### Master Orchestrator Return Type
**Status:** ✅ Compatible

**Before:** Returned `dict` (but callers expected string)  
**After:** Returns `str` (formatted markdown)

**Callers:** Already treat return value as string for display, so no breaking change.

---

## 📈 Performance Analysis

### ResponseRenderer Performance

**Target:** <10ms per render

**Optimization Strategies:**
1. **Template Caching:** Cache parsed templates (reduces load time)
2. **Block Precompilation:** Precompile block templates on init
3. **Lazy Loading:** Load templates only when needed
4. **Simple String Formatting:** Use f-strings instead of Jinja2 for simple blocks

**Benchmark Results (Expected):**
- INSTANT tier: <2ms
- FOCUSED tier: <5ms
- STRUCTURED tier: <8ms
- COMPREHENSIVE tier: <10ms

---

### ResponseMiddleware Performance

**Target:** <5ms per injection

**Optimization Strategies:**
1. **Early Exit:** Skip middleware if no system messages
2. **Conditional Checks:** Only check metadata if feature enabled
3. **String Concatenation:** Use list + join instead of += for strings
4. **No External Calls:** All logic in-memory (no file I/O)

**Benchmark Results (Expected):**
- No system messages: <1ms (early exit)
- Token warning only: <2ms
- Multiple messages: <5ms

---

### Total Overhead

**User Request → Response Display:**
- Orchestrator execution: Variable (2s - 30s)
- ResponseMiddleware injection: <5ms
- ResponseRenderer rendering: <10ms
- **Total overhead: <15ms (0.025% - 0.75% of execution time)**

**Verdict:** ✅ Negligible performance impact

---

## 🎓 Lessons Learned & Best Practices

### Architecture Principles

1. **Separation of Concerns**
   - Orchestrators: Business logic only
   - Middleware: System message injection
   - Renderer: Formatting and display

2. **Extensibility**
   - New message types: Add to middleware (no orchestrator changes)
   - New formatting: Update templates (no code changes)
   - New orchestrators: Automatically get rendering pipeline

3. **Backward Compatibility**
   - Always maintain backward compatibility in v5.x
   - Deprecate old patterns, don't break them
   - Provide migration path in documentation

### Development Best Practices

1. **Test-Driven Development**
   - Write tests before implementation
   - Aim for 95%+ coverage
   - Include performance tests

2. **Documentation First**
   - Document architecture before coding
   - Update docs immediately after implementation
   - Provide examples in developer guides

3. **Incremental Rollout**
   - Create components independently
   - Test each component in isolation
   - Integrate step-by-step
   - Validate at each step

---

## 🚀 Implementation Timeline

| Phase | Duration | Deliverable | Status |
|-------|----------|-------------|--------|
| 1. ResponseRenderer | 2h | response_renderer.py (300 lines) + tests | ⏸️ Next |
| 2. ResponseMiddleware | 1h | response_middleware.py (150 lines) + tests | ⏸️ Pending |
| 3. Master Orchestrator Integration | 1h | master_orchestrator.py (+50 lines) + tests | ⏸️ Pending |
| 4. Update Orchestrators | 2h | Planning v5, Vacuum v2 cleanup | ⏸️ Pending |
| 5. Testing & Validation | 1.5h | 33 tests, coverage reports | ⏸️ Pending |
| 6. Documentation | 0.5h | 6 documents (2 new + 4 updated) | ⏸️ Pending |

**Total:** 8 hours  
**Start:** January 3, 2026 (now)  
**Expected Completion:** January 3, 2026 (end of day)

---

## 📁 Files Summary

### Files to Create (4)
1. `/src/orchestrators/response_renderer.py` (300 lines)
2. `/src/orchestrators/response_middleware.py` (150 lines)
3. `/tests/orchestrators/test_response_renderer.py` (200 lines)
4. `/tests/orchestrators/test_response_middleware.py` (100 lines)

### Files to Modify (5)
1. `/src/orchestrators/master_orchestrator.py` (+50 lines)
2. `/src/orchestrators/planning/planning_orchestrator_v5.py` (cleanup)
3. `/src/orchestrators/vacuum/vacuum_orchestrator_v2.py` (cleanup)
4. `/tests/orchestrators/test_master_orchestrator_integration.py` (+100 lines)
5. `.github/prompts/CORTEX.prompt.md` (architecture notes)

### Documentation to Create (2)
1. `/docs/architecture/response-rendering-pipeline.md` (200 lines)
2. `/docs/guides/creating-orchestrator-messages.md` (150 lines)

### Documentation to Update (4)
1. `.github/prompts/CORTEX.prompt.md`
2. `/docs/orchestrators/master-orchestrator.md`
3. `/docs/orchestrators/base-orchestrator.md`
4. `/CHANGELOG.md`

**Total Files:** 15 (4 new + 5 modified code + 2 new docs + 4 updated docs)

---

## ✅ Approval Checklist

- ✅ Root cause identified
- ✅ Architecture enhancement designed
- ✅ Components specified (API, responsibilities)
- ✅ Testing strategy defined
- ✅ Migration strategy planned
- ✅ Backward compatibility ensured
- ✅ Performance targets set
- ✅ Documentation plan created
- ✅ Timeline established
- ⏸️ **Awaiting approval to proceed with Phase 1**

---

**Status:** 📋 DESIGN COMPLETE - Ready for Implementation  
**Next Phase:** Phase 1 - Create ResponseRenderer (2 hours)  
**Approval:** ✅ APPROVED (proceed with implementation)

---

## 🔗 Related Documents

- `root-cause-analysis.md` - Full investigation trail
- `investigation-summary.md` - Executive summary
- `cortex-investigate.prompt.md` - Investigation orchestrator spec
- Response implementation files (will be created in Phase 1-2)
