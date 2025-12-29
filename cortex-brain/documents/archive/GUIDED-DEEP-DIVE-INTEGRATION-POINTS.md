# Integration Points - Guided Deep Dive Pattern

## Overview
Maps exactly where the Guided Deep Dive pattern integrates with existing CORTEX 3.0 components.

## 1. Intent Router Integration

### Current State
- **File:** `src/cortex_agents/intent_router.py`
- **Current keywords:** "investigate" routes to ARCHITECTURE intent → Health Validator
- **Pattern matching:** Uses Tier 2 for similar past requests

### Integration Changes
```python
# src/cortex_agents/intent_router.py - Line ~100
INTENT_KEYWORDS = {
    # ... existing keywords ...
    IntentType.ARCHITECTURE: [
        # ... existing architecture keywords ...
        # ADD: Deep dive investigation patterns
        "investigate why", "analyze why", "understand why", 
        "deep dive", "trace through", "follow the path",
        "crawl dependencies", "map relationships"
    ],
    # NEW: Dedicated investigation intent
    IntentType.INVESTIGATE: [
        "investigate", "investigate why", "analyze why", "understand why",
        "deep dive", "crawl through", "trace through", "follow the path",
        "dependency analysis", "impact analysis", "root cause"
    ]
}

# Add routing logic for investigations
def _make_routing_decision(self, intent, similar_patterns, request):
    # ... existing logic ...
    
    # NEW: Route investigations to Health Validator with investigation mode
    if intent == IntentType.INVESTIGATE or "investigate" in request.user_message.lower():
        return {
            "primary_agent": AgentType.HEALTH_VALIDATOR,
            "mode": "investigation",  # NEW: Signals guided deep dive
            "secondary_agents": [AgentType.PATTERN_MATCHER],
            "confidence": self._calculate_confidence(intent, similar_patterns, request)
        }
```

## 2. Health Validator Integration

### Current State  
- **File:** `src/cortex_agents/health_validator/agent.py`
- **Current capability:** System health checks, validation
- **Methods:** `execute()`, `can_handle()`

### Integration Changes
```python
# src/cortex_agents/health_validator/agent.py
class HealthValidator(BaseAgent):
    def __init__(self, name: str, tier1_api=None, tier2_kg=None, tier3_context=None):
        # ... existing initialization ...
        
        # NEW: Add investigation capabilities
        from ..investigation_router import InvestigationRouter
        self.investigation_router = InvestigationRouter(tier2_kg)
    
    def can_handle(self, request: AgentRequest) -> bool:
        # ... existing logic ...
        
        # NEW: Handle investigation requests
        investigation_keywords = ["investigate", "analyze why", "trace", "deep dive"]
        if any(keyword in request.user_message.lower() for keyword in investigation_keywords):
            return True
        
        return request.intent.lower() in valid_intents
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        # ... existing validation logic ...
        
        # NEW: Check if this is an investigation request
        if self._is_investigation_request(request):
            return self._execute_investigation(request)
        else:
            # Existing health check logic
            return self._execute_health_check(request)
    
    def _is_investigation_request(self, request: AgentRequest) -> bool:
        """Determine if request is for guided investigation."""
        investigation_indicators = [
            "investigate why", "analyze why", "understand why",
            "trace through", "deep dive", "crawl dependencies"
        ]
        return any(indicator in request.user_message.lower() 
                  for indicator in investigation_indicators)
    
    def _execute_investigation(self, request: AgentRequest) -> AgentResponse:
        """Execute guided deep dive investigation."""
        return self.investigation_router.conduct_investigation(request)
```

## 3. Pattern Matcher Integration

### Current State
- **File:** `src/cortex_agents/strategic/pattern_matcher.py` (assumed location)
- **Current capability:** Find similar patterns in Tier 2
- **Used by:** Intent Router for routing decisions

### Integration Changes
```python
# src/cortex_agents/strategic/pattern_matcher.py
class PatternMatcher(BaseAgent):
    def find_investigation_patterns(self, target_file: str, investigation_type: str) -> List[Dict]:
        """Find past investigation patterns for similar files/issues."""
        
        # Search for past investigations on similar files
        file_patterns = self.tier2.search_patterns(
            query=f"investigation target:{target_file}",
            pattern_type="investigation_route",
            limit=5
        )
        
        # Search for similar investigation types
        type_patterns = self.tier2.search_patterns(
            query=f"investigation_type:{investigation_type}",
            pattern_type="investigation_route", 
            limit=3
        )
        
        return self._merge_and_rank_patterns(file_patterns, type_patterns)
    
    def suggest_investigation_phases(self, target: str, past_patterns: List[Dict]) -> List[int]:
        """Suggest which phases to execute based on past successful patterns."""
        
        if not past_patterns:
            return [1]  # Default: just immediate context
        
        # Analyze successful past investigations
        successful_patterns = [p for p in past_patterns if p.get('success', False)]
        
        if not successful_patterns:
            return [1, 2]  # Conservative: immediate + related
        
        # Find most common successful phase combinations
        phase_combinations = [p['phases_used'] for p in successful_patterns]
        most_common = max(set(tuple(combo) for combo in phase_combinations), 
                         key=lambda x: phase_combinations.count(list(x)))
        
        return list(most_common)
```

## 4. Knowledge Graph Integration

### Current State
- **File:** `src/tier2/knowledge_graph/knowledge_graph.py`
- **Current capability:** Pattern storage, search, relationships
- **Methods:** `add_pattern()`, `search_patterns()`

### Integration Changes
```python
# src/tier2/knowledge_graph/knowledge_graph.py
class KnowledgeGraph:
    def store_investigation_result(self, request: str, target: str, 
                                 phases_executed: List[int], 
                                 token_usage: int,
                                 success: bool,
                                 findings: List[str]) -> str:
        """Store investigation pattern for future routing optimization."""
        
        pattern_data = {
            "investigation_target": target,
            "original_request": request,
            "phases_executed": phases_executed,
            "token_usage": token_usage,
            "success": success,
            "efficiency_score": self._calculate_efficiency_score(token_usage, len(findings)),
            "findings_summary": findings[:3],  # Top 3 findings
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self.add_pattern(
            pattern_type="investigation_route",
            content=json.dumps(pattern_data),
            metadata={
                "confidence": 0.8 if success else 0.3,
                "investigation_type": self._classify_investigation_type(request),
                "target_type": self._classify_target_type(target)
            }
        )
    
    def get_investigation_recommendations(self, target: str, request: str) -> Dict[str, Any]:
        """Get recommendations for investigation phases based on past patterns."""
        
        # Find similar investigations
        similar = self.search_patterns(
            query=f"investigation_target:{target} OR {request}",
            pattern_type="investigation_route",
            limit=10
        )
        
        if not similar:
            return {"recommended_phases": [1], "confidence": "low"}
        
        # Analyze successful investigations
        successful = [p for p in similar if json.loads(p['content']).get('success')]
        
        if successful:
            avg_phases = self._calculate_average_phases(successful)
            avg_tokens = self._calculate_average_tokens(successful)
            
            return {
                "recommended_phases": avg_phases,
                "estimated_tokens": avg_tokens,
                "confidence": "high" if len(successful) >= 3 else "medium",
                "past_successes": len(successful)
            }
        
        return {"recommended_phases": [1, 2], "confidence": "medium"}
```

## 5. File System Integration

### Current State
- **Dependency tracking:** Planned in CORTEX 2.0 Phase 13 (not implemented)
- **File relationship mapping:** Does not exist currently

### Integration Requirements
```python
# NEW FILE: src/tier2/file_relationships.py
class FileRelationshipMapper:
    """Maps file relationships for investigation scoping."""
    
    def __init__(self, tier2_kg):
        self.tier2 = tier2_kg
        
    def get_related_files(self, file_path: str, max_depth: int = 3) -> List[str]:
        """Get files related to target file within max_depth."""
        
        # Strategy 1: Import analysis (if file is Python)
        if file_path.endswith('.py'):
            return self._analyze_python_imports(file_path, max_depth)
        
        # Strategy 2: Pattern-based relationships from Tier 2
        patterns = self.tier2.search_patterns(
            query=f"file_relationship:{file_path}",
            limit=20
        )
        
        related = []
        for pattern in patterns:
            content = json.loads(pattern['content'])
            if 'related_files' in content:
                related.extend(content['related_files'])
        
        return list(set(related))[:10]  # Limit to 10 files
    
    def _analyze_python_imports(self, file_path: str, max_depth: int) -> List[str]:
        """Analyze Python file imports to find related files."""
        # Implementation would use AST to parse imports
        # This is placeholder for the actual dependency tracking system
        pass
```

## 6. User Interface Integration

### Current State
- **Response formatting:** Uses AgentResponse with structured data
- **User interaction:** Currently limited to command execution

### Integration Changes
```python
# NEW FILE: src/cortex_agents/investigation_ui.py
class InvestigationUI:
    """Handles user interaction during guided investigations."""
    
    @staticmethod
    def format_phase_prompt(phase_info: Dict) -> str:
        """Format phase continuation prompt for user."""
        return f"""
🔍 **Investigation Phase {phase_info['number']}: {phase_info['scope'].title()}**

**What we'll analyze:**
{chr(10).join(f"  • {file}" for file in phase_info['files'][:5])}
{f"  • ... and {len(phase_info['files'])-5} more files" if len(phase_info['files']) > 5 else ""}

**Cost:** {phase_info['estimated_tokens']} tokens ({phase_info['estimated_tokens']/50:.1f}% of budget)
**Confidence:** {phase_info['confidence']} (based on {phase_info.get('past_patterns', 0)} past patterns)

**Continue with this phase? (y/n/skip):**
"""
    
    @staticmethod
    def format_investigation_summary(results: List[Dict]) -> str:
        """Format final investigation results."""
        return f"""
## 🔍 Investigation Complete

**Analysis performed:**
{chr(10).join(f"  ✅ Phase {i+1}: {r['scope']} ({r['files_analyzed']} files)" for i, r in enumerate(results))}

**Total cost:** {sum(r['tokens_used'] for r in results)} tokens

**Key findings:**
{chr(10).join(f"  • {finding}" for result in results for finding in result.get('findings', [])[:2])}

**Next steps:**
{chr(10).join(f"  {i+1}. {step}" for i, step in enumerate(InvestigationUI._generate_next_steps(results)))}
"""
```

## Implementation Order

### Phase 1: Core Integration (Hours 1-3)
1. **Intent Router**: Add investigation keywords and routing logic
2. **Health Validator**: Add investigation mode detection and routing
3. **Basic Investigation Router**: Core phase management without UI

### Phase 2: Pattern Learning (Hours 4-6)  
1. **Knowledge Graph**: Add investigation pattern storage
2. **Pattern Matcher**: Add investigation pattern analysis
3. **File Relationships**: Basic file relationship mapping

### Phase 3: User Experience (Hours 7-8)
1. **Investigation UI**: User prompts and result formatting
2. **Integration testing**: End-to-end investigation workflow
3. **Token budget validation**: Ensure efficiency targets met

## Integration Validation

### Test Cases
1. **"Investigate why UserView loads slowly"** → Routes to Health Validator investigation mode
2. **Phase progression** → User prompted at each phase with token costs
3. **Pattern learning** → Successful investigations stored and retrieved
4. **Token limits** → Investigation stops when budget exceeded
5. **File relationships** → Related files identified within confidence thresholds

This integration map ensures the Guided Deep Dive pattern seamlessly extends CORTEX 3.0's existing architecture without breaking current functionality.