# 🔍 CORTEX 4.0 Detailed Gap Analysis

**Version:** 1.0.0 | **Author:** Asif Hussain | **Date:** December 30, 2025  
**Parent:** [00-EXECUTIVE-SUMMARY.md](./00-EXECUTIVE-SUMMARY.md)

---

## 📋 Table of Contents

1. [Gap 1: Intent Router - LLM Integration](#gap-1)
2. [Gap 2: Auto-Engagement Engine](#gap-2)
3. [Gap 3: Interactive AST Context Building](#gap-3)
4. [Gap 4: Knowledge Library Consultation](#gap-4)
5. [Gap 5: End-to-End LLM Architecture](#gap-5)
6. [Test Strategy](#test-strategy)
7. [Implementation Roadmap](#implementation-roadmap)

---

<a name="gap-1"></a>
## 🚨 GAP 1: Intent Router - LLM Integration

### Current Implementation Analysis

**File:** `src/cortex_agents/intent_router.py` (1,130 LOC)

**Problem Areas:**

1. **Keyword-Based Classification (Lines 694-730)**
```python
# CURRENT (WRONG): Simple substring matching
intent_scores = {}
for intent_type, keywords in self.INTENT_KEYWORDS.items():
    score = 0
    matched_keywords = []
    for keyword in keywords:
        if keyword in message_lower:  # ❌ Brittle matching
            word_count = len(keyword.split())
            score += word_count
            matched_keywords.append(keyword)
```

**Impact:**
- Misses semantic variations ("design architecture" vs "plan system design")
- Cannot handle typos or informal language
- Requires 140+ hardcoded trigger patterns

2. **LLM Only Used for Complexity, Not Intent**
```python
# src/operations/modules/routing/tiered_router.py (lines 245-280)
# LLM correctly used here for Tier 1-4 classification
def _llm_classify(self, operation: str, context: Dict) -> tuple:
    prompt = self.TIER_CLASSIFICATION_PROMPT + f"\n\nOperation: {operation}"
    response = self.llm_client.generate(prompt)
    # ✅ THIS WORKS - should apply to intent classification too
```

### Target Architecture

**REQUIRED: LLM-Based Intent Classification**

```python
# PROPOSED FIX: src/cortex_agents/intent_router_v2.py

class LLMIntentClassifier:
    """
    LLM-powered intent classifier using GPT-4/Claude.
    
    Features:
    - Semantic understanding (handles synonyms, context)
    - Few-shot learning from historical patterns
    - Confidence scoring with explainability
    - Fallback to regex for offline mode
    """
    
    INTENT_CLASSIFICATION_PROMPT = """
You are CORTEX, an AI assistant analyzing user requests to determine intent.

Available Intents:
1. PLAN - User wants to create a structured plan (keywords: plan, design, architect, strategy)
2. CODE - User wants to write/modify code (keywords: implement, build, create, code)
3. DEBUG - User wants to fix issues (keywords: debug, fix, troubleshoot, investigate)
4. TEST - User wants to write tests (keywords: test, TDD, validation, coverage)
5. REFINE - User wants to improve existing code (keywords: refactor, optimize, improve)
6. REVIEW - User wants code review (keywords: review, analyze, assess, audit)
7. SANITIZE - User wants to remove sensitive data (keywords: sanitize, anonymize, clean)
8. MAINTAIN - User wants system health checks (keywords: maintenance, health, monitor)

User Request: "{user_message}"

Respond with JSON:
{{
  "intent": "PLAN|CODE|DEBUG|TEST|REFINE|REVIEW|SANITIZE|MAINTAIN",
  "confidence": 0.0-1.0,
  "reasoning": "why this intent was chosen",
  "secondary_intents": ["optional", "list"]
}}
"""
    
    def classify(self, user_message: str) -> IntentClassificationResult:
        """Classify user message using LLM."""
        prompt = self.INTENT_CLASSIFICATION_PROMPT.format(
            user_message=user_message
        )
        
        try:
            # LLM API call
            response = self.llm_client.generate(
                prompt=prompt,
                temperature=0.2,  # Low temp for consistency
                max_tokens=200
            )
            
            result = json.loads(response)
            
            return IntentClassificationResult(
                intent=IntentType[result["intent"]],
                confidence=result["confidence"],
                rule_context={"reasoning": result["reasoning"]},
                metadata={"secondary_intents": result.get("secondary_intents", [])}
            )
        except Exception as e:
            # Fallback to regex
            logger.warning(f"LLM classification failed, using regex: {e}")
            return self._regex_fallback(user_message)
```

### Test Strategy for Gap 1

**New Tests Required (15 tests):**

```python
# tests/cortex_agents/test_llm_intent_classifier.py

class TestLLMIntentClassification:
    """Test LLM-based intent classification."""
    
    def test_semantic_understanding_synonyms(self):
        """LLM understands synonyms (design = plan = architect)."""
        classifier = LLMIntentClassifier(llm_client=mock_llm)
        
        synonyms = ["design this system", "architect the solution", "plan the feature"]
        for phrase in synonyms:
            result = classifier.classify(phrase)
            assert result.intent == IntentType.PLAN
            assert result.confidence >= 0.8
    
    def test_contextual_disambiguation(self):
        """LLM uses context to disambiguate intent."""
        # "implement tests" = TEST intent, not CODE
        result = classifier.classify("implement tests for authentication")
        assert result.intent == IntentType.TEST
        
        # "implement feature" = CODE intent
        result = classifier.classify("implement authentication feature")
        assert result.intent == IntentType.CODE
    
    def test_multi_intent_detection(self):
        """LLM detects secondary intents."""
        result = classifier.classify("plan and implement user authentication")
        assert result.intent == IntentType.PLAN  # Primary
        assert IntentType.CODE in result.metadata["secondary_intents"]
    
    def test_confidence_scoring(self):
        """LLM provides calibrated confidence scores."""
        clear_intent = classifier.classify("create a plan")
        ambiguous_intent = classifier.classify("do something with code")
        
        assert clear_intent.confidence > ambiguous_intent.confidence
    
    def test_fallback_to_regex_on_llm_failure(self):
        """System falls back to regex when LLM unavailable."""
        classifier = LLMIntentClassifier(llm_client=None)  # Simulate failure
        result = classifier.classify("plan a feature")
        
        assert result.intent == IntentType.PLAN  # Regex worked
        assert result.metadata["classification_method"] == "regex_fallback"
```

**Validation Criteria:**
- ✅ LLM classification accuracy ≥ 95% on test set (100 samples)
- ✅ Regex fallback coverage ≥ 90% (for offline mode)
- ✅ Average response time ≤ 300ms (with caching)
- ✅ Zero false positives on critical intents (SANITIZE, DEBUG)

---

<a name="gap-2"></a>
## 🚨 GAP 2: Auto-Engagement Engine

### Current Implementation Analysis

**Problem:** Planning requires explicit commands (`/CORTEX Plan`, `create a plan`)

**Evidence:**
- CORTEX.prompt.md (lines 24-48): Manual trigger detection
- 140+ hardcoded patterns in `planning.yaml`
- No complexity analysis → auto-planning

### Target Architecture

**REQUIRED: Automatic Complexity-Based Engagement**

```python
# PROPOSED: src/orchestrators/planning/auto_engagement_engine.py

class AutoEngagementEngine:
    """
    Automatically determines if user request requires planning.
    
    Decision Factors:
    1. Request complexity (LOC estimate, dependencies, domains)
    2. Risk level (security, data, architecture changes)
    3. User history (past failures without planning)
    4. Domain knowledge (complex domains = auto-plan)
    """
    
    COMPLEXITY_THRESHOLDS = {
        PlanComplexity.LOW: 0.3,      # ≤30% = inline implementation
        PlanComplexity.MEDIUM: 0.6,   # 30-60% = conditional plan
        PlanComplexity.HIGH: 0.85,    # 60-85% = incremental plan
        PlanComplexity.CRITICAL: 1.0  # >85% = mandatory planning
    }
    
    def should_auto_engage_planning(
        self, 
        user_message: str,
        context: Dict[str, Any]
    ) -> tuple[bool, PlanComplexity, str]:
        """
        Determine if planning should auto-engage.
        
        Returns:
            (should_plan, complexity_level, reasoning)
        """
        # Step 1: Analyze request complexity
        complexity_score = self._analyze_complexity(user_message, context)
        
        # Step 2: Map score to plan complexity
        plan_complexity = self._map_to_plan_complexity(complexity_score)
        
        # Step 3: Decision threshold
        should_plan = complexity_score >= self.COMPLEXITY_THRESHOLDS[PlanComplexity.MEDIUM]
        
        # Step 4: Generate reasoning
        reasoning = self._generate_reasoning(
            complexity_score, 
            plan_complexity, 
            should_plan
        )
        
        return should_plan, plan_complexity, reasoning
    
    def _analyze_complexity(
        self, 
        user_message: str, 
        context: Dict[str, Any]
    ) -> float:
        """
        Calculate complexity score (0.0-1.0) using multiple factors.
        
        Factors:
        - Estimated LOC (from keywords)
        - Number of domains involved
        - Security/data sensitivity
        - Architectural changes
        - Historical failure rate
        """
        score = 0.0
        factors = []
        
        # Factor 1: Estimated LOC (30% weight)
        estimated_loc = self._estimate_loc(user_message)
        if estimated_loc > 500:
            score += 0.30
            factors.append(f"LOC > 500 ({estimated_loc})")
        elif estimated_loc > 200:
            score += 0.15
            factors.append(f"LOC > 200 ({estimated_loc})")
        
        # Factor 2: Multi-domain (25% weight)
        domains = self._detect_domains(user_message)
        if len(domains) > 2:
            score += 0.25
            factors.append(f"Multi-domain ({domains})")
        elif len(domains) == 2:
            score += 0.12
        
        # Factor 3: Security/Data (20% weight)
        if self._has_security_implications(user_message):
            score += 0.20
            factors.append("Security implications")
        
        # Factor 4: Architecture changes (15% weight)
        if self._involves_architecture_change(user_message):
            score += 0.15
            factors.append("Architecture change")
        
        # Factor 5: Historical failure (10% weight)
        if self._has_past_failures_without_planning(context):
            score += 0.10
            factors.append("Past failures without planning")
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _estimate_loc(self, user_message: str) -> int:
        """Estimate lines of code using LLM."""
        # Use LLM to estimate: "User wants to: {message}. Estimated LOC?"
        # Parse response: "50-100 lines" → 75
        pass
    
    def _detect_domains(self, user_message: str) -> List[str]:
        """Detect technical domains (auth, database, frontend, etc.)."""
        domains = []
        domain_keywords = {
            "auth": ["authentication", "login", "oauth", "jwt"],
            "database": ["database", "sql", "orm", "migration"],
            "frontend": ["frontend", "ui", "react", "component"],
            "backend": ["backend", "api", "endpoint", "service"],
            "security": ["security", "encryption", "firewall"],
        }
        
        message_lower = user_message.lower()
        for domain, keywords in domain_keywords.items():
            if any(kw in message_lower for kw in keywords):
                domains.append(domain)
        
        return domains
```

### Test Strategy for Gap 2

**New Tests Required (12 tests):**

```python
# tests/orchestrators/planning/test_auto_engagement_engine.py

class TestAutoEngagement:
    """Test automatic planning engagement."""
    
    def test_simple_request_no_auto_engagement(self):
        """Simple requests don't trigger planning."""
        engine = AutoEngagementEngine()
        
        should_plan, complexity, reason = engine.should_auto_engage_planning(
            user_message="fix typo in README",
            context={}
        )
        
        assert should_plan is False
        assert complexity == PlanComplexity.LOW
    
    def test_complex_request_triggers_planning(self):
        """Complex requests auto-trigger planning."""
        should_plan, complexity, reason = engine.should_auto_engage_planning(
            user_message="implement microservices authentication with OAuth2, JWT, and role-based access control",
            context={}
        )
        
        assert should_plan is True
        assert complexity in [PlanComplexity.HIGH, PlanComplexity.CRITICAL]
        assert "Multi-domain" in reason or "Security" in reason
    
    def test_multi_domain_triggers_planning(self):
        """Multi-domain requests trigger planning."""
        should_plan, _, _ = engine.should_auto_engage_planning(
            user_message="build API endpoint with database migration and frontend component",
            context={}
        )
        
        assert should_plan is True
    
    def test_security_triggers_planning(self):
        """Security-related requests trigger planning."""
        should_plan, _, reason = engine.should_auto_engage_planning(
            user_message="implement encryption for user data",
            context={}
        )
        
        assert should_plan is True
        assert "Security implications" in reason
    
    def test_historical_failure_increases_engagement(self):
        """Past failures without planning trigger engagement."""
        context = {
            "past_failures": [
                {"task": "similar feature", "had_plan": False, "failed": True}
            ]
        }
        
        should_plan, _, reason = engine.should_auto_engage_planning(
            user_message="implement user dashboard",
            context=context
        )
        
        assert should_plan is True
        assert "Past failures" in reason
```

**Validation Criteria:**
- ✅ Correctly identifies 90%+ of requests needing planning (test set: 200 requests)
- ✅ False positive rate ≤ 5% (don't over-engage)
- ✅ Complexity score calibration: HIGH complexity = 80%+ accuracy
- ✅ User can override: "implement without planning" respected

---

<a name="gap-3"></a>
## 🚨 GAP 3: Interactive AST Context Building

### Current Implementation Analysis

**Problem:** AST context is gathered ONCE, not incrementally

**Evidence:**
```python
# src/orchestrators/planning/interactive_session.py (lines 138-148)
def discover_context(self) -> Dict[str, Any]:
    if not self.discovered_context:  # ❌ Only runs once
        engine = DiscoveryEngine(cortex_root=Path.cwd())
        self.discovered_context = engine.discover_context(...)
    return self.discovered_context  # Cached result
```

### Target Architecture

**REQUIRED: Incremental AST Context Building**

```python
# PROPOSED: src/orchestrators/planning/incremental_ast_builder.py

class IncrementalASTBuilder:
    """
    Builds AST context incrementally across conversation turns.
    
    Features:
    - Turn-by-turn refinement
    - Expanding search radius
    - Dependency discovery
    - Code graph updates
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.discovered_modules = set()
        self.ast_cache = {}
        self.dependency_graph = {}
        self.turn_history = []
    
    def update_context_from_turn(
        self,
        turn_number: int,
        user_input: str,
        current_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update AST context based on new conversation turn.
        
        Process:
        1. Extract new entities (classes, functions, modules)
        2. Expand search radius (find dependencies)
        3. Update code graph
        4. Return enriched context
        """
        # Step 1: Extract entities from user input
        new_entities = self._extract_entities(user_input)
        
        # Step 2: Discover related code
        for entity in new_entities:
            if entity not in self.discovered_modules:
                ast_data = self._parse_ast(entity)
                self.ast_cache[entity] = ast_data
                self.discovered_modules.add(entity)
                
                # Discover dependencies
                dependencies = self._discover_dependencies(ast_data)
                self.dependency_graph[entity] = dependencies
        
        # Step 3: Expand search radius (breadth-first)
        expanded_modules = self._expand_search_radius(
            current_context.get("target_modules", [])
        )
        
        # Step 4: Build enriched context
        enriched_context = {
            "turn_number": turn_number,
            "discovered_modules": list(self.discovered_modules),
            "ast_data": self.ast_cache,
            "dependency_graph": self.dependency_graph,
            "search_radius": len(expanded_modules),
            "new_entities": new_entities
        }
        
        self.turn_history.append({
            "turn": turn_number,
            "user_input": user_input,
            "entities_discovered": len(new_entities),
            "total_modules": len(self.discovered_modules)
        })
        
        return enriched_context
    
    def _extract_entities(self, user_input: str) -> List[str]:
        """Extract code entities (classes, functions, modules) from user input."""
        # Use LLM to extract: "User mentioned: UserService, AuthController, login()"
        pass
    
    def _expand_search_radius(self, current_modules: List[str]) -> List[str]:
        """Expand search to dependencies and dependents."""
        expanded = set(current_modules)
        
        for module in current_modules:
            # Add dependencies
            expanded.update(self.dependency_graph.get(module, []))
            
            # Add dependents (reverse lookup)
            for mod, deps in self.dependency_graph.items():
                if module in deps:
                    expanded.add(mod)
        
        return list(expanded)
```

### Integration with PlanningOrchestrator

```python
# UPDATED: src/orchestrators/planning/interactive_session.py

class PlanningSession:
    """Enhanced with incremental AST building."""
    
    def __init__(self, plan_name: str):
        self.plan_name = plan_name
        self.ast_builder = IncrementalASTBuilder(project_root=Path.cwd())
        self.discovered_context = {}  # Continuously updated
        self.turn_number = 0
    
    def process_user_turn(self, user_input: str) -> Dict[str, Any]:
        """Process user turn and update AST context."""
        self.turn_number += 1
        
        # Update AST context based on new turn
        self.discovered_context = self.ast_builder.update_context_from_turn(
            turn_number=self.turn_number,
            user_input=user_input,
            current_context=self.discovered_context
        )
        
        return {
            "turn": self.turn_number,
            "context_updated": True,
            "modules_discovered": len(self.discovered_context["discovered_modules"]),
            "search_radius": self.discovered_context["search_radius"]
        }
```

### Test Strategy for Gap 3

**New Tests Required (10 tests):**

```python
# tests/orchestrators/planning/test_incremental_ast_builder.py

class TestIncrementalASTBuilder:
    """Test incremental AST context building."""
    
    def test_turn_1_discovers_initial_entities(self):
        """First turn discovers initial entities."""
        builder = IncrementalASTBuilder(project_root=Path("test_project"))
        
        context = builder.update_context_from_turn(
            turn_number=1,
            user_input="I want to modify the UserService class",
            current_context={}
        )
        
        assert "UserService" in context["discovered_modules"]
        assert context["turn_number"] == 1
    
    def test_turn_2_expands_dependencies(self):
        """Second turn expands to dependencies."""
        builder = IncrementalASTBuilder(project_root=Path("test_project"))
        
        # Turn 1: Discover UserService
        context1 = builder.update_context_from_turn(1, "UserService", {})
        
        # Turn 2: User asks about related code
        context2 = builder.update_context_from_turn(
            turn_number=2,
            user_input="What does UserService depend on?",
            current_context=context1
        )
        
        # Should discover dependencies (e.g., DatabaseService, Logger)
        assert len(context2["discovered_modules"]) > len(context1["discovered_modules"])
        assert context2["search_radius"] > 1
    
    def test_turn_3_refines_understanding(self):
        """Third turn refines understanding with new details."""
        builder = IncrementalASTBuilder(project_root=Path("test_project"))
        
        context1 = builder.update_context_from_turn(1, "UserService", {})
        context2 = builder.update_context_from_turn(2, "dependencies", context1)
        context3 = builder.update_context_from_turn(
            turn_number=3,
            user_input="Also need to update the authentication logic",
            current_context=context2
        )
        
        # Should discover AuthService
        assert "AuthService" in context3["discovered_modules"]
    
    def test_context_preserved_across_turns(self):
        """Context from previous turns is preserved."""
        builder = IncrementalASTBuilder(project_root=Path("test_project"))
        
        context1 = builder.update_context_from_turn(1, "UserService", {})
        context2 = builder.update_context_from_turn(2, "AuthService", context1)
        
        # Both modules should be in context
        assert "UserService" in context2["discovered_modules"]
        assert "AuthService" in context2["discovered_modules"]
```

**Validation Criteria:**
- ✅ Context grows with each turn (no information loss)
- ✅ Dependencies discovered within 2 turns of initial mention
- ✅ Search radius expands correctly (BFS algorithm)
- ✅ AST cache prevents redundant parsing

---

<a name="gap-4"></a>
## 🚨 GAP 4: Knowledge Library Consultation

### Current Implementation Analysis

**Problem:** Knowledge library exists but orchestrators don't consult it

**Evidence:**
- 35+ YAML files in `cortex-brain/knowledge/`
- 525+ best practice rules
- ZERO active consultation in orchestrator workflows

### Target Architecture

**REQUIRED: Active Knowledge Library Integration**

```python
# PROPOSED: src/orchestrators/base/knowledge_consultant.py

class KnowledgeConsultant:
    """
    Consults knowledge library before code generation.
    
    Process:
    1. Detect relevant domains (auth, database, api, etc.)
    2. Load applicable YAML best practices
    3. Inject guidelines into LLM context
    4. Validate generated code against guidelines
    """
    
    def __init__(self, knowledge_root: Path):
        self.knowledge_root = knowledge_root
        self.cache = {}
    
    def consult_best_practices(
        self,
        operation: str,
        domains: List[str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Retrieve relevant best practices for operation.
        
        Returns:
            {
                "guidelines": [list of rules],
                "examples": [code examples],
                "anti_patterns": [what to avoid],
                "security_rules": [critical security rules]
            }
        """
        guidelines = []
        examples = []
        anti_patterns = []
        security_rules = []
        
        # Load relevant knowledge files
        for domain in domains:
            yaml_file = self._find_knowledge_file(domain)
            if yaml_file:
                knowledge = self._load_yaml(yaml_file)
                
                guidelines.extend(knowledge.get("guidelines", []))
                examples.extend(knowledge.get("examples", []))
                anti_patterns.extend(knowledge.get("anti_patterns", []))
                
                # Extract security rules (CRITICAL priority)
                security_rules.extend([
                    rule for rule in knowledge.get("rules", [])
                    if rule.get("severity") == "CRITICAL"
                ])
        
        return {
            "guidelines": guidelines,
            "examples": examples,
            "anti_patterns": anti_patterns,
            "security_rules": security_rules,
            "total_rules": len(guidelines) + len(security_rules)
        }
    
    def inject_into_llm_context(
        self,
        base_prompt: str,
        best_practices: Dict[str, Any]
    ) -> str:
        """
        Inject best practices into LLM prompt.
        
        Format:
        {base_prompt}
        
        KNOWLEDGE LIBRARY GUIDELINES:
        - [guideline 1]
        - [guideline 2]
        
        ANTI-PATTERNS TO AVOID:
        - [anti-pattern 1]
        
        CRITICAL SECURITY RULES:
        - [security rule 1] ⚠️
        """
        if not best_practices["guidelines"]:
            return base_prompt  # No guidelines, return original
        
        enhanced_prompt = f"{base_prompt}\n\n"
        enhanced_prompt += "## 📚 KNOWLEDGE LIBRARY GUIDELINES\n\n"
        
        for guideline in best_practices["guidelines"][:10]:  # Top 10
            enhanced_prompt += f"- {guideline}\n"
        
        if best_practices["anti_patterns"]:
            enhanced_prompt += "\n## ⚠️ ANTI-PATTERNS TO AVOID\n\n"
            for ap in best_practices["anti_patterns"][:5]:
                enhanced_prompt += f"- ❌ {ap}\n"
        
        if best_practices["security_rules"]:
            enhanced_prompt += "\n## 🔒 CRITICAL SECURITY RULES\n\n"
            for rule in best_practices["security_rules"]:
                enhanced_prompt += f"- 🚨 {rule}\n"
        
        return enhanced_prompt
```

### Integration into Orchestrators

```python
# UPDATED: src/orchestrators/planning/planning_orchestrator.py

class PlanningOrchestrator(BaseOrchestrator):
    """Enhanced with knowledge consultation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.knowledge_consultant = KnowledgeConsultant(
            knowledge_root=self.cortex_root / "cortex-brain" / "knowledge"
        )
    
    def _generate_plan(self, context: Dict[str, Any]) -> PlanData:
        """Generate plan WITH knowledge consultation."""
        
        # Step 1: Detect domains
        domains = self._detect_domains_from_context(context)
        
        # Step 2: Consult knowledge library
        best_practices = self.knowledge_consultant.consult_best_practices(
            operation="plan_generation",
            domains=domains,
            context=context
        )
        
        logger.info(f"📚 Consulted knowledge library: {best_practices['total_rules']} rules")
        
        # Step 3: Inject into LLM prompt (if using LLM)
        if self.llm_client:
            enhanced_prompt = self.knowledge_consultant.inject_into_llm_context(
                base_prompt=self._get_base_planning_prompt(context),
                best_practices=best_practices
            )
            plan_text = self.llm_client.generate(enhanced_prompt)
        
        # Step 4: Validate against best practices
        validation_result = self._validate_against_knowledge(
            plan_data=plan_text,
            best_practices=best_practices
        )
        
        return plan_data
```

### Test Strategy for Gap 4

**New Tests Required (8 tests):**

```python
# tests/orchestrators/base/test_knowledge_consultant.py

class TestKnowledgeConsultant:
    """Test knowledge library consultation."""
    
    def test_loads_relevant_guidelines(self):
        """Consultant loads relevant domain guidelines."""
        consultant = KnowledgeConsultant(
            knowledge_root=Path("cortex-brain/knowledge")
        )
        
        best_practices = consultant.consult_best_practices(
            operation="code_generation",
            domains=["auth", "database"],
            context={}
        )
        
        assert len(best_practices["guidelines"]) > 0
        assert any("authentication" in g.lower() for g in best_practices["guidelines"])
    
    def test_extracts_security_rules(self):
        """Consultant extracts CRITICAL security rules."""
        best_practices = consultant.consult_best_practices(
            operation="code_generation",
            domains=["security"],
            context={}
        )
        
        assert len(best_practices["security_rules"]) > 0
        # All security rules should be CRITICAL
        for rule in best_practices["security_rules"]:
            assert "CRITICAL" in str(rule) or rule.get("severity") == "CRITICAL"
    
    def test_injects_guidelines_into_prompt(self):
        """Guidelines correctly injected into LLM prompt."""
        best_practices = {
            "guidelines": ["Use bind variables", "Close connections"],
            "anti_patterns": ["Never use string concatenation for SQL"],
            "security_rules": ["Always validate input"]
        }
        
        base_prompt = "Generate code for user authentication."
        enhanced_prompt = consultant.inject_into_llm_context(
            base_prompt, best_practices
        )
        
        assert "Use bind variables" in enhanced_prompt
        assert "Never use string concatenation" in enhanced_prompt
        assert "Always validate input" in enhanced_prompt
    
    def test_orchestrator_consults_before_generation(self):
        """Planning orchestrator consults knowledge library."""
        orchestrator = PlanningOrchestrator(config=test_config)
        
        with patch.object(orchestrator.knowledge_consultant, 'consult_best_practices') as mock_consult:
            mock_consult.return_value = {"guidelines": [], "examples": []}
            
            orchestrator._generate_plan(context={"domains": ["auth"]})
            
            # Verify consultation happened
            mock_consult.assert_called_once()
```

**Validation Criteria:**
- ✅ All orchestrators consult knowledge library before generation
- ✅ CRITICAL security rules ALWAYS injected
- ✅ Knowledge consultation adds ≤ 100ms latency
- ✅ Cache hit rate ≥ 80% for repeated domains

---

<a name="gap-5"></a>
## 🚨 GAP 5: End-to-End LLM Architecture

### Summary

This gap combines Gaps 1-4 into a unified LLM architecture:

1. **LLM Intent Classification** (Gap 1)
2. **LLM Complexity Analysis → Auto-Engagement** (Gap 2)
3. **LLM-Powered AST Context Extraction** (Gap 3)
4. **LLM Consultation of Knowledge Library** (Gap 4)

**Target:** Single coherent LLM pipeline handling all intelligence tasks

---

<a name="test-strategy"></a>
## ✅ Comprehensive Test Strategy

### Test Coverage Summary

| Gap | Area | New Tests | Updated Tests | Total |
|-----|------|-----------|---------------|-------|
| 1 | Intent Router | 15 | 32 | 47 |
| 2 | Auto-Engagement | 12 | 0 | 12 |
| 3 | AST Context | 10 | 18 | 28 |
| 4 | Knowledge Library | 8 | 15 | 23 |
| 5 | E2E LLM | 5 | 30 | 35 |
| **TOTAL** | - | **50** | **95** | **145** |

### Integration Test Suite

```python
# tests/integration/test_cortex_autonomous_behavior.py

class TestAutonomousBehavior:
    """End-to-end tests for autonomous CORTEX behavior."""
    
    def test_e2e_auto_planning_workflow(self):
        """
        E2E: Complex request → LLM intent → Auto-engagement → AST context → Knowledge consultation → Plan
        
        User says: "implement OAuth2 authentication with role-based access control"
        
        Expected Flow:
        1. LLM classifies intent: PLAN (confidence 0.95)
        2. Complexity analyzer: HIGH (OAuth + RBAC + multi-domain)
        3. Auto-engage planning (no user command needed)
        4. Incremental AST: Discover AuthService, UserService, RoleService
        5. Knowledge consultation: Load security/auth best practices
        6. Generate plan with 8 phases, DoR/DoD, TDD requirements
        """
        cortex = CORTEXOrchestrator(config=test_config)
        
        result = cortex.process_request(
            user_message="implement OAuth2 authentication with role-based access control",
            context={}
        )
        
        # Verify autonomous behavior
        assert result["intent_classification"]["method"] == "llm"
        assert result["auto_engagement"]["engaged"] is True
        assert result["auto_engagement"]["complexity"] == PlanComplexity.HIGH
        assert result["ast_context"]["turn_count"] >= 1
        assert result["knowledge_consulted"]["total_rules"] > 0
        assert result["plan_generated"] is True
        assert len(result["plan"]["phases"]) >= 8
```

**Test Execution Plan:**
1. **Week 1:** Implement + test Gap 1 (LLM Intent)
2. **Week 2:** Implement + test Gap 2 (Auto-Engagement)
3. **Week 3:** Implement + test Gap 3 (AST Context)
4. **Week 4:** Implement + test Gap 4 (Knowledge Library)
5. **Week 5:** Integration tests (E2E)
6. **Week 6:** Regression testing + validation

---

<a name="implementation-roadmap"></a>
## 🛠️ Implementation Roadmap

### Phase 1: LLM Intent Classification (Week 1)
- **Deliverables:**
  - `LLMIntentClassifier` class
  - Integration with existing `IntentRouter`
  - 15 new tests
  - Regex fallback mechanism
- **Success Criteria:** 95%+ accuracy on test set

### Phase 2: Auto-Engagement Engine (Week 2)
- **Deliverables:**
  - `AutoEngagementEngine` class
  - Complexity scoring algorithm
  - Integration with `PlanningOrchestrator`
  - 12 new tests
- **Success Criteria:** 90%+ correct engagement decisions

### Phase 3: Incremental AST Context (Week 3)
- **Deliverables:**
  - `IncrementalASTBuilder` class
  - Turn-by-turn context updates
  - Integration with `PlanningSession`
  - 10 new tests
- **Success Criteria:** Context grows correctly across 5+ turns

### Phase 4: Knowledge Library Integration (Week 4)
- **Deliverables:**
  - `KnowledgeConsultant` class
  - Integration with all orchestrators
  - Prompt injection mechanism
  - 8 new tests
- **Success Criteria:** All orchestrators consult knowledge library

### Phase 5: Integration + Validation (Weeks 5-6)
- **Deliverables:**
  - E2E integration tests
  - Regression test suite
  - Performance benchmarks
  - Documentation updates
- **Success Criteria:** Zero regression, 145/145 tests passing

---

**Document Status:** ✅ COMPLETE  
**Next:** [00-REMEDIATION-PLAN.md](./00-REMEDIATION-PLAN.md)  
**GitHub:** github.com/asifhussain60/CORTEX
