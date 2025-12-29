# Task 6.10: Post-Phase 5 TDD v4.0 Enhancement

**Version:** 1.0  
**Author:** Asif Hussain  
**Created:** December 21, 2025  
**Status:** 📋 PLANNED  
**Execution Mode:** 👤 Supervised

---

## 📋 Executive Summary

**Goal:** Enhance TDDOrchestrator from 57% agentic alignment to 95% by integrating Phase 5 agentic AI patterns

**Current State:** TDDOrchestrator (791 LOC) with excellent learning engine and adaptive execution

**Target State:** TDDOrchestrator Enhanced (1,100+ LOC) with:
- Multi-agent collaboration (parallel test execution)
- LLM-as-judge test quality evaluation  
- Enhanced guardrails (code safety classifier)
- Full MCP integration
- Adaptive execution mode integration

**Timeline:** 1 week (5 days)  
**Effort:** 40 hours  
**Dependencies:** Phase 5 Packages 1, 3, 5, 6 complete

---

## 🎯 Enhancement Packages

### Package 1: Multi-Agent Collaboration (30% → 90%)

**Current:** Sequential RED→GREEN→REFACTOR with strategy pattern  
**Target:** Parallel test execution with async support

**Implementation:**

```python
class ParallelTestRunner:
    """Run multiple test suites in parallel"""
    
    async def run_tests_parallel(
        self,
        test_suites: List[Path],
        timeout: int = 300
    ) -> List[TestResult]:
        """Execute test suites concurrently"""
        tasks = [
            self._run_test_suite(suite, timeout) 
            for suite in test_suites
        ]
        
        # Gather with exception handling
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        return [
            result if isinstance(result, TestResult) 
            else TestResult(success=False, error=str(result))
            for result in results
        ]
    
    async def _run_test_suite(
        self,
        suite: Path,
        timeout: int
    ) -> TestResult:
        """Run single test suite with timeout"""
        try:
            async with asyncio.timeout(timeout):
                proc = await asyncio.create_subprocess_exec(
                    'pytest', str(suite), '-v',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await proc.communicate()
                
                return self._parse_test_output(
                    stdout.decode(), 
                    stderr.decode(),
                    proc.returncode
                )
        except asyncio.TimeoutError:
            return TestResult(
                success=False,
                error=f"Test suite timed out after {timeout}s"
            )
```

**Integration Points:**
- RED phase: Parallel test discovery
- GREEN phase: Parallel test execution
- REFACTOR phase: Parallel linting/formatting

**Tests:** 10 tests covering parallel execution, timeout handling, result aggregation

---

### Package 3: Agent Evaluation (30% → 90%)

**Current:** Clean code quality scoring (0-10)  
**Target:** LLM-as-judge test quality evaluation

**Implementation:**

```python
class TestQualityEvaluator:
    """Evaluate test generation reasoning using LLM"""
    
    def __init__(self, llm_client: Any):
        self.llm = llm_client
        self.criteria = {
            'coverage_completeness': 'Tests cover all requirements',
            'edge_case_handling': 'Edge cases and error scenarios tested',
            'assertion_quality': 'Assertions are specific and meaningful',
            'maintainability': 'Tests are readable and well-structured',
            'independence': 'Tests are isolated and repeatable'
        }
    
    async def evaluate_test_quality(
        self,
        test_code: str,
        implementation: str,
        acceptance_criteria: List[str]
    ) -> Dict[str, float]:
        """Use LLM to judge test quality (1-10 per criterion)"""
        prompt = self._build_evaluation_prompt(
            test_code,
            implementation,
            acceptance_criteria
        )
        
        response = await self.llm.complete(prompt)
        scores = self._parse_scores(response)
        
        # Calculate weighted average
        scores['overall'] = sum(scores.values()) / len(scores)
        
        return scores
    
    def _build_evaluation_prompt(
        self,
        test_code: str,
        implementation: str,
        acceptance_criteria: List[str]
    ) -> str:
        """Build evaluation prompt"""
        return f"""
        Evaluate this test suite quality (1-10 per criterion):
        
        ## Implementation
        ```
        {implementation}
        ```
        
        ## Test Suite
        ```
        {test_code}
        ```
        
        ## Acceptance Criteria
        {chr(10).join(f'- {c}' for c in acceptance_criteria)}
        
        ## Evaluation Criteria
        {chr(10).join(f'- {k}: {v}' for k, v in self.criteria.items())}
        
        Provide scores in JSON format:
        {{
            "coverage_completeness": <1-10>,
            "edge_case_handling": <1-10>,
            "assertion_quality": <1-10>,
            "maintainability": <1-10>,
            "independence": <1-10>,
            "reasoning": "<brief explanation>"
        }}
        """
    
    def _parse_scores(self, response: str) -> Dict[str, float]:
        """Parse LLM response into scores"""
        try:
            data = json.loads(response)
            return {
                k: float(v) 
                for k, v in data.items() 
                if k != 'reasoning'
            }
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse LLM scores: {e}")
            return {k: 5.0 for k in self.criteria.keys()}  # Default to neutral
```

**Integration Points:**
- RED phase: Evaluate test design before implementation
- GREEN phase: Evaluate test quality after implementation
- REFACTOR phase: Evaluate test maintainability

**Tests:** 8 tests covering LLM evaluation, score parsing, error handling

---

### Package 5: Adaptive Execution Modes (0% → 100%)

**Current:** Single execution mode  
**Target:** Integration with ExecutionModeManager

**Implementation:**

```python
from src.orchestration_4_0.execution import ExecutionMode, ExecutionModeManager

class TDDOrchestratorEnhanced:
    """TDD Orchestrator with adaptive execution modes"""
    
    def __init__(self, config: Dict[str, Any], cortex_root: Path):
        self.config = config
        self.cortex_root = cortex_root
        
        # Initialize execution mode manager
        self.mode_manager = ExecutionModeManager(
            config=config,
            user_profile=self._load_user_profile()
        )
        
        # Existing initialization
        self.tech_discovery = TechnologyDiscoveryEngine(cortex_root)
        self.clean_code_enforcer = CleanCodeEnforcer()
    
    async def execute(
        self,
        context: Dict[str, Any],
        mode: Optional[ExecutionMode] = None
    ) -> Dict[str, Any]:
        """Execute TDD workflow with adaptive mode"""
        # Select execution mode
        if mode is None:
            task = self._extract_task(context)
            mode = self.mode_manager.select_mode(task)
        
        logger.info(f"🎭 Executing TDD workflow in {mode.value} mode")
        
        # Adapt behavior based on mode
        if mode == ExecutionMode.AUTONOMOUS:
            return await self._execute_autonomous(context)
        elif mode == ExecutionMode.SUPERVISED:
            return await self._execute_supervised(context)
        elif mode == ExecutionMode.MANUAL:
            return await self._execute_manual(context)
        else:
            raise ValueError(f"Unsupported execution mode: {mode}")
    
    async def _execute_autonomous(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fully autonomous RED→GREEN→REFACTOR"""
        # RED: Generate tests autonomously
        red_result = await self._red_phase_autonomous(context)
        if not red_result['success']:
            return red_result
        
        # GREEN: Implement autonomously
        green_result = await self._green_phase_autonomous(red_result)
        if not green_result['success']:
            return green_result
        
        # REFACTOR: Auto-refactor
        refactor_result = await self._refactor_phase_autonomous(green_result)
        
        return refactor_result
    
    async def _execute_supervised(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Supervised mode with approval gates"""
        # RED: Generate tests, await approval
        red_result = await self._red_phase_supervised(context)
        if not red_result.get('user_approved'):
            return {'success': False, 'reason': 'User rejected RED phase'}
        
        # GREEN: Implement, await approval
        green_result = await self._green_phase_supervised(red_result)
        if not green_result.get('user_approved'):
            return {'success': False, 'reason': 'User rejected GREEN phase'}
        
        # REFACTOR: Refactor, await approval
        refactor_result = await self._refactor_phase_supervised(green_result)
        
        return refactor_result
```

**Integration Points:**
- Orchestrator initialization: Load ExecutionModeManager
- Phase execution: Adapt to selected mode
- User feedback: Learn from mode effectiveness

**Tests:** 12 tests covering mode selection, autonomous execution, supervised execution

---

### Package 6: Enhanced Guardrails (0% → 100%)

**Current:** No security checks  
**Target:** Code safety classifier for generated code

**Implementation:**

```python
class CodeSafetyGuardrail:
    """Detect security issues in generated code"""
    
    def __init__(self):
        self.patterns = self._load_vulnerability_patterns()
        self.severity_levels = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
    
    def check_safety(
        self,
        code: str,
        language: str
    ) -> List[SecurityViolation]:
        """Scan for security vulnerabilities"""
        violations = []
        
        # Language-specific checks
        if language == 'Python':
            violations.extend(self._check_python_safety(code))
        elif language == 'JavaScript':
            violations.extend(self._check_javascript_safety(code))
        elif language == 'C#':
            violations.extend(self._check_csharp_safety(code))
        
        # Generic checks
        violations.extend(self._check_generic_safety(code))
        
        return violations
    
    def _check_python_safety(self, code: str) -> List[SecurityViolation]:
        """Python-specific security checks"""
        violations = []
        
        # Dangerous functions
        if 'eval(' in code or 'exec(' in code:
            violations.append(SecurityViolation(
                severity='CRITICAL',
                category='CWE-95',
                message='Dangerous eval/exec usage detected',
                line=self._find_line(code, 'eval(') or self._find_line(code, 'exec('),
                recommendation='Use ast.literal_eval() for safe parsing'
            ))
        
        # Unsafe deserialization
        if 'pickle.loads' in code:
            violations.append(SecurityViolation(
                severity='HIGH',
                category='CWE-502',
                message='Unsafe pickle deserialization',
                line=self._find_line(code, 'pickle.loads'),
                recommendation='Use JSON or msgpack for data serialization'
            ))
        
        # SQL injection risk
        if re.search(r'execute\([\'"].*?%s', code):
            violations.append(SecurityViolation(
                severity='HIGH',
                category='CWE-89',
                message='Potential SQL injection via string formatting',
                line=self._find_line(code, 'execute'),
                recommendation='Use parameterized queries with placeholders'
            ))
        
        # Hardcoded credentials
        if re.search(r'(password|api[_-]?key|token)\s*=\s*["\'][^"\']+["\']', code):
            violations.append(SecurityViolation(
                severity='CRITICAL',
                category='CWE-798',
                message='Hardcoded credentials detected',
                line=self._find_line(code, 'password') or self._find_line(code, 'api'),
                recommendation='Use environment variables or secret management'
            ))
        
        return violations
    
    def _check_generic_safety(self, code: str) -> List[SecurityViolation]:
        """Generic security checks"""
        violations = []
        
        # TODO/FIXME in production
        if 'TODO:' in code or 'FIXME:' in code:
            violations.append(SecurityViolation(
                severity='MEDIUM',
                category='CWE-1127',
                message='TODO/FIXME comments in production code',
                line=self._find_line(code, 'TODO') or self._find_line(code, 'FIXME'),
                recommendation='Resolve all TODOs before production deployment'
            ))
        
        return violations
    
    def _find_line(self, code: str, pattern: str) -> Optional[int]:
        """Find line number of pattern"""
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            if pattern in line:
                return i
        return None

@dataclass
class SecurityViolation:
    """Security violation detected by guardrail"""
    severity: str
    category: str  # CWE code
    message: str
    line: Optional[int]
    recommendation: str
```

**Integration Points:**
- GREEN phase: Scan implementation code
- REFACTOR phase: Scan refactored code
- Validation: Block commit if CRITICAL violations found

**Tests:** 15 tests covering Python/JS/C# safety checks, violation detection

---

## 📊 Implementation Plan

### Day 1: Multi-Agent Collaboration (8 hours)
- [ ] Implement ParallelTestRunner
- [ ] Add async test execution
- [ ] Integrate with RED/GREEN/REFACTOR phases
- [ ] Write 10 tests
- [ ] Git checkpoint

### Day 2: Agent Evaluation (8 hours)
- [ ] Implement TestQualityEvaluator
- [ ] Build evaluation prompts
- [ ] Add LLM integration
- [ ] Write 8 tests
- [ ] Git checkpoint

### Day 3: Adaptive Execution Modes (8 hours)
- [ ] Integrate ExecutionModeManager
- [ ] Implement autonomous execution
- [ ] Implement supervised execution
- [ ] Write 12 tests
- [ ] Git checkpoint

### Day 4: Enhanced Guardrails (8 hours)
- [ ] Implement CodeSafetyGuardrail
- [ ] Add Python/JS/C# safety checks
- [ ] Integrate with phases
- [ ] Write 15 tests
- [ ] Git checkpoint

### Day 5: Integration & Testing (8 hours)
- [ ] End-to-end integration testing
- [ ] Performance benchmarking
- [ ] Documentation updates
- [ ] Final validation
- [ ] Deployment

---

## ✅ Success Criteria

1. **Multi-Agent Collaboration:** Parallel test execution <50% faster
2. **Agent Evaluation:** LLM-as-judge scores correlate with human ratings (>80%)
3. **Adaptive Execution:** ExecutionModeManager integrated, all 3 modes working
4. **Enhanced Guardrails:** 95%+ security vulnerability detection
5. **Tests:** 55/55 tests passing (85%+ coverage)
6. **Performance:** <10% overhead vs current TDD v4.0
7. **Agentic Alignment:** 57% → 95% (38% improvement)

---

## 📁 Files Modified/Created

**Modified:**
- `src/orchestrators/tdd/tdd_orchestrator.py` (791 → 1,100 LOC)
- `src/orchestrators/tdd/strategies/red_strategy.py` (parallel test execution)
- `src/orchestrators/tdd/strategies/green_strategy.py` (safety guardrails)

**Created:**
- `src/orchestrators/tdd/parallel_test_runner.py` (150 LOC)
- `src/orchestrators/tdd/test_quality_evaluator.py` (200 LOC)
- `src/orchestrators/tdd/code_safety_guardrail.py` (250 LOC)
- `tests/orchestrators/test_tdd_v4_post_phase5.py` (55 tests, 400 LOC)
- `cortex-brain/documents/implementation-guides/tdd-v4-post-phase5-guide.md`

**Total:** +600 LOC implementation, +400 LOC tests, +300 LOC documentation

---

## 🔗 References

- **COMPLETED-ORCHESTRATORS-AGENTIC-ALIGNMENT-REVIEW.md** - Gap analysis and enhancement opportunities
- **phase-05-brain-agentic-ai.md** - Phase 5 agentic AI patterns
- **TDDOrchestrator:** `src/orchestrators/tdd/tdd_orchestrator.py`
- **ExecutionModeManager:** `src/orchestration_4_0/execution/execution_mode_manager.py`

---

**Status:** 📋 PLANNED - Ready for execution after Phase 5 completion  
**Next Action:** Await Phase 5 Packages 1, 3, 5, 6 completion
