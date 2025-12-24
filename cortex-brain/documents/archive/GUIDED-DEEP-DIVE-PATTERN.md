# Guided Deep Dive Pattern - CORTEX 3.0 Investigation Architecture

## Overview
Implements phased investigation for commands like "Investigate why this view..." with intelligent scoping, token budgets, and user control.

## Architecture Components

### 1. Investigation Router (New Component)
```python
# src/cortex_agents/investigation_router.py
class InvestigationRouter:
    """Routes investigation requests through guided phases with token budgets."""
    
    def __init__(self, tier2_kg, max_tokens=5000):
        self.tier2 = tier2_kg
        self.max_tokens = max_tokens
        self.current_phase = 1
        self.context_accumulated = []
        self.token_usage = 0
    
    def analyze_request(self, request: str, file_context: str) -> InvestigationPlan:
        """Create phased investigation plan with token budgets."""
        
        # Phase 1: Immediate Context (Always included)
        phase1 = {
            "scope": "immediate",
            "files": [file_context],
            "estimated_tokens": 800,
            "confidence": "high"
        }
        
        # Phase 2: Related Components (Conditional)
        phase2 = self._analyze_relationships(file_context)
        
        # Phase 3: Infrastructure (If needed)
        phase3 = self._analyze_infrastructure_need(request, file_context)
        
        return InvestigationPlan(phases=[phase1, phase2, phase3])
    
    def _analyze_relationships(self, file_path: str) -> Dict:
        """Use Tier 2 patterns to determine related files."""
        # Check if file_path has known relationship patterns
        patterns = self.tier2.search_patterns(
            query=f"file:{file_path} related_to",
            limit=5
        )
        
        confidence = "high" if len(patterns) > 2 else "medium"
        
        return {
            "scope": "related",
            "files": self._extract_related_files(patterns),
            "estimated_tokens": len(patterns) * 300,
            "confidence": confidence
        }
```

### 2. Token Budget Manager
```python
class TokenBudgetManager:
    """Manages token allocation across investigation phases."""
    
    def __init__(self, max_budget=5000):
        self.max_budget = max_budget
        self.used_tokens = 0
        self.phase_budgets = {
            1: 1500,  # Immediate context
            2: 2000,  # Related components  
            3: 1500   # Infrastructure
        }
    
    def can_proceed_to_phase(self, phase: int, estimated_tokens: int) -> bool:
        """Check if phase can proceed within budget."""
        return (self.used_tokens + estimated_tokens) <= self.max_budget
    
    def allocate_tokens(self, phase: int, actual_tokens: int):
        """Record token usage for phase."""
        self.used_tokens += actual_tokens
        self.logger.info(f"Phase {phase}: Used {actual_tokens} tokens, Total: {self.used_tokens}/{self.max_budget}")
```

### 3. Enhanced Health Validator Integration
```python
# Update to existing HealthValidator
class HealthValidator(BaseAgent):
    def __init__(self, ...):
        # ... existing code ...
        self.investigation_router = InvestigationRouter(tier2_kg)
    
    def investigate_architecture(self, request: AgentRequest) -> AgentResponse:
        """Perform guided deep dive investigation."""
        
        # Extract target from request
        target = self._extract_investigation_target(request.user_message)
        
        # Create investigation plan
        plan = self.investigation_router.analyze_request(
            request.user_message, 
            target
        )
        
        # Execute phases with user guidance
        results = []
        for phase in plan.phases:
            
            # Ask user before proceeding (except Phase 1)
            if phase.number > 1:
                user_choice = self._prompt_user_for_phase(phase)
                if not user_choice:
                    break
            
            # Execute phase
            phase_result = self._execute_investigation_phase(phase)
            results.append(phase_result)
            
            # Check token budget
            if not self.investigation_router.budget_manager.can_proceed_to_next():
                self._notify_token_limit_reached()
                break
        
        return self._format_investigation_results(results)
    
    def _prompt_user_for_phase(self, phase: Dict) -> bool:
        """Prompt user to continue to next phase."""
        return f"""
        Phase {phase['number']}: {phase['scope']} analysis
        Estimated tokens: {phase['estimated_tokens']}
        Files to analyze: {len(phase['files'])}
        Confidence: {phase['confidence']}
        
        Continue? (y/n):
        """
```

### 4. User Guidance Prompts
```python
class InvestigationPrompts:
    """Standardized prompts for user guidance during investigations."""
    
    @staticmethod
    def phase_continuation_prompt(phase: Dict) -> str:
        return f"""
        🔍 **Investigation Phase {phase['number']}: {phase['scope'].title()}**
        
        **Scope:** {phase['description']}
        **Files to analyze:** {len(phase['files'])} files
        **Estimated tokens:** {phase['estimated_tokens']}
        **Confidence level:** {phase['confidence']}
        
        **Next Steps:**
        1. ✅ Continue with this phase
        2. ⏭️  Skip to next phase  
        3. 🛑 Stop investigation here
        
        **Current token usage:** {current_usage}/{max_budget}
        """
    
    @staticmethod
    def investigation_summary(results: List[Dict]) -> str:
        return f"""
        ## 🔍 Investigation Summary
        
        **Total phases executed:** {len(results)}
        **Files analyzed:** {sum(len(r['files']) for r in results)}
        **Token usage:** {sum(r['tokens_used'] for r in results)}
        
        **Key findings:**
        {InvestigationPrompts._format_findings(results)}
        
        **Recommendations:**
        {InvestigationPrompts._format_recommendations(results)}
        """
```

## Integration with Existing CORTEX Architecture

### Intent Router Updates
```python
# Add to IntentRouter.INTENT_KEYWORDS
IntentType.INVESTIGATE: [
    "investigate", "investigate why", "analyze why", "understand why",
    "deep dive", "crawl through", "trace through", "follow the path"
]
```

### Knowledge Graph Integration
```python
# Add to KnowledgeGraph
def store_investigation_pattern(self, request: str, target: str, 
                              phases_executed: List[int], success: bool):
    """Store investigation pattern for future routing decisions."""
    
    pattern_data = {
        "request_type": "investigation",
        "target": target,
        "phases_used": phases_executed,
        "success": success,
        "token_efficiency": self._calculate_efficiency_score()
    }
    
    self.add_pattern(
        pattern_type="investigation_route",
        content=pattern_data,
        metadata={"confidence": 0.8}
    )
```

## Token Budget Strategy

### Phase Allocation
- **Phase 1 (Immediate):** 1,500 tokens - Always executed
- **Phase 2 (Related):** 2,000 tokens - High confidence relationships
- **Phase 3 (Infrastructure):** 1,500 tokens - Only if previous phases indicate need

### Efficiency Controls
- **Relationship confidence threshold:** 70% minimum to proceed to Phase 2
- **Auto-stop triggers:** Circular references, dependency depth > 5 levels
- **User checkpoints:** Before each phase with token impact preview

### Token Calculation
```python
def estimate_tokens(files: List[str]) -> int:
    """Estimate token usage for file analysis."""
    base_tokens_per_file = 300
    context_overhead = 200
    return (len(files) * base_tokens_per_file) + context_overhead
```

## Success Metrics

### Efficiency Targets
- **95% accuracy** in Phase 1 (immediate context should solve 95% of issues)
- **80% user satisfaction** with guided progression
- **Token reduction** of 85% vs exhaustive crawling
- **Investigation completion** in <3 phases for 90% of requests

### User Experience Goals
- **Clear phase boundaries** with explicit user choice points
- **Token transparency** showing usage and remaining budget
- **Escape hatches** to stop or skip phases at any point
- **Pattern learning** to improve future investigation routing

## Implementation Priority

1. **Phase 1: Investigation Router** (Core logic, token budgets)
2. **Phase 2: Health Validator Integration** (Hook into existing analysis)  
3. **Phase 3: User Guidance System** (Prompts, choice points)
4. **Phase 4: Pattern Learning** (Store investigation patterns in Tier 2)

This design balances the accuracy benefits of deep analysis with efficiency controls, while maintaining user agency through guided choices.