---
# PHASE-E IMPLEMENTATION EXECUTION GUIDE
# How to implement modules WITHOUT creating stubs
# Version: 1.0
# Date: 2026-01-20

metadata:
  purpose: "Enforce test-driven implementation discipline for Phase E"
  audience: "AI Assistant (GitHub Copilot) executing Phase E"
  key_principle: "RED → GREEN → REFACTOR (never stub)"
  
## WORKFLOW FOR EACH MODULE

per_module_workflow:

  step_1_locate_test_file:
    action: "Find the test file for the module"
    example: |
      Module to implement: cortex/core/orchestrator_decorator.py
      Test file location: tests/unit/core/test_orchestrator_decorator.py
    command: "find tests/ -name '*orchestrator_decorator*' -type f"
    
  step_2_read_complete_test:
    action: "Read the ENTIRE test file"
    why: |
      - Understand full contract
      - See all test methods (not just happy path)
      - Identify edge cases
      - Find fixtures and setup
      - Note dependencies on other classes
    process: |
      1. Open test file completely
      2. Note all test class names
      3. Note all test method names
      4. Identify setup/teardown
      5. Extract expected behavior from assertions
      
  step_3_identify_required_classes:
    action: "Extract exact class/function names from test imports"
    example: |
      Test file imports:
        from cortex.core.orchestrator_decorator import (
            OrchestratorDecorator,
            ExecutionContext,
            DecoratorChain
        )
      
      So module MUST have exactly these (no more, no less):
      - class OrchestratorDecorator
      - class ExecutionContext
      - class DecoratorChain
    
    process: |
      1. Look at "from cortex.X import" statements
      2. List all class/function names
      3. Mark which are most commonly used in tests
      4. Start with most-used first

  step_4_run_test_red_phase:
    action: "Execute test to see it FAIL"
    why: |
      - Proves test actually tests something
      - Shows exact error message
      - Identifies what's missing
      - Prevents implementing wrong thing
    
    commands: |
      # Collect tests only (see what we're dealing with)
      pytest tests/unit/core/test_orchestrator_decorator.py --collect-only
      
      # Run tests (watch them fail - RED phase)
      pytest tests/unit/core/test_orchestrator_decorator.py -v --tb=short
      
    what_to_look_for: |
      ✓ ImportError: No module named
      ✓ ImportError: Cannot import name 'OrchestratorDecorator'
      ✓ AttributeError: module has no attribute
      ✓ TypeError: ... missing required positional argument
      ✓ AssertionError: ... != ...
      
      These errors TELL YOU what to implement.

  step_5_create_stub_file:
    action: "Create empty module file if it doesn't exist"
    when: "Module file doesn't exist yet"
    example: |
      touch cortex/core/orchestrator_decorator.py
    
    content: |
      '''Module: orchestrator_decorator
      Handles decorator chain execution for orchestrators.
      '''
    
    note: "This is just the container - NOT the implementation yet"

  step_6_implement_minimum_for_first_test:
    action: "Look at first test method, implement ONLY what it needs"
    
    process_per_test: |
      1. Pick first test method (test_XXX)
      2. Read test code line by line
      3. Identify what classes/methods it calls
      4. Implement exactly that - nothing more
      5. Run: pytest tests/.../test_file.py::TestClass::test_XXX -v
      6. When it passes, move to next test
    
    implementation_template: |
      class OrchestratorDecorator:
          """Orchestrator execution decorator.
          
          Manages execution context, decorator chain, and 
          callback management for orchestrator methods.
          """
          
          def __init__(self, func=None):
              """Initialize decorator.
              
              Args:
                  func: Optional function to decorate immediately.
              """
              self.func = func
              self.decorators = []
          
          def __call__(self, func):
              """Apply decorator to function.
              
              Args:
                  func: Function to decorate.
              
              Returns:
                  Wrapped function.
              """
              # Implementation based on test assertions
              pass
    
    key_rules: |
      ✅ DO include function signature matching test calls
      ✅ DO include type hints for parameters
      ✅ DO include docstring with Args/Returns
      ✅ DO implement just enough to pass test
      ✅ DO throw NotImplementedError for unrelated features
      
      ❌ DON'T add features not in test
      ❌ DON'T over-engineer
      ❌ DON'T implement edge cases until test requires them
      ❌ DON'T leave bare "pass" statements

  step_7_run_incremental_tests:
    action: "Run tests one at a time, growing implementation"
    
    workflow: |
      Loop for each test method:
      1. Run: pytest tests/...::TestClass::test_method -v
      2. See which assertion fails
      3. Add minimum code to pass that assertion
      4. Go back to step 1
      
    example_run_sequence: |
      pytest tests/unit/core/test_orchestrator_decorator.py::TestDecoratorInitialization::test_init -v
        → FAIL: __init__ not implemented
        → ADD: def __init__(self): pass
        → PASS
      
      pytest tests/unit/core/test_orchestrator_decorator.py::TestDecoratorInitialization::test_init_with_func -v
        → FAIL: func parameter not handled
        → ADD: def __init__(self, func=None): self.func = func
        → PASS
      
      pytest tests/unit/core/test_orchestrator_decorator.py::TestDecoratorChain::test_add_decorator -v
        → FAIL: add_decorator method missing
        → ADD: def add_decorator(self, decorator): ...
        → PASS

  step_8_full_module_test:
    action: "Run ALL tests for module at once"
    command: "pytest tests/unit/core/test_orchestrator_decorator.py -v"
    
    criteria_for_completion: |
      ✅ All tests pass: tests/unit/.../test_orchestrator_decorator.py (50/50 PASSED)
      ✅ No collection errors
      ✅ No import errors
      ✅ Type hints: 100% (all params and returns typed)
      ✅ Docstrings: 100% (all public functions documented)
      ✅ No bare except clauses
      ✅ No functions >500 lines

  step_9_governance_compliance_check:
    action: "Verify CORE rules compliance"
    checks: |
      # Check for bare except
      grep -n "except:" cortex/core/orchestrator_decorator.py
      → Must return 0 (no results)
      
      # Check function lengths
      awk '/^    def /{start=NR; name=$2} NR-start>500 && start>0 {print name": "NR-start" lines"}' cortex/core/orchestrator_decorator.py
      → Must return 0 (no functions >500 lines)
      
      # Check for type hints
      grep -n "def " cortex/core/orchestrator_decorator.py | grep -v " -> "
      → Check parameters have type hints (: Type not just : )
    
    docstring_check: |
      # Verify Google docstrings
      pydoc cortex.core.orchestrator_decorator | head -20
      → Should show:
        Help on module cortex.core.orchestrator_decorator in cortex.core.orchestrator_decorator:
        
        NAME
            cortex.core.orchestrator_decorator
        
        DESCRIPTION
            Module: orchestrator_decorator
            Handles decorator chain execution for orchestrators.

  step_10_type_hints_check:
    action: "Verify mypy passes"
    command: "mypy cortex/core/orchestrator_decorator.py --strict"
    
    expect_output: |
      Success: no issues found in 1 source file
    
    if_errors: |
      Fix type hints immediately:
      - Add missing type annotations
      - Use Optional[] for optional parameters
      - Use Union[] for multiple types
      - Never use Any unless necessary

  step_11_git_commit:
    action: "Commit completed module"
    command: |
      git add cortex/core/orchestrator_decorator.py
      git commit -m "Module: orchestrator_decorator - Implement OrchestratorDecorator, ExecutionContext, DecoratorChain; 50 tests passing"
    
    commit_message_format: |
      Module: {module_name} - Implement {classes}, {N} tests passing
      
      Example:
      Module: orchestrator_decorator - Implement OrchestratorDecorator, ExecutionContext, DecoratorChain; 50/50 tests passing

## PREVENTING STUB CREATION

anti_stub_enforcement:

  enforcement_1_test_first_rule:
    rule: "NEVER write code without seeing test FAIL first"
    how_to_enforce: |
      1. Before creating any class: pytest --co
         → See list of tests expecting the class
      2. Run the test: pytest tests/...::test_X -v
         → See the error (ImportError, AttributeError, etc.)
      3. ONLY THEN create the class
      4. Run test again: should get different error (TypeError, AssertionError)
      5. Implement method: run again
      
      Result: Cannot accidentally create empty stub - test will immediately fail
  
  enforcement_2_no_pass_statements:
    rule: "Every function must have implementation, not just 'pass'"
    detection: |
      # Find bare pass statements (after colon)
      grep -n "pass$" cortex/core/orchestrator_decorator.py
      
      # If you see this:
        def some_method(self):
            pass  # ← WRONG! Will fail tests
      
      # Fix by looking at test assertion and implementing:
        def some_method(self):
            return self.value  # ← Test expects this
    
    validation: |
      When test runs, any bare "pass" will cause:
      - AssertionError: assertion failed
      - TypeError: None is not X
      - AttributeError: NoneType has no attribute Y
      
      Test WILL FAIL, forcing you to implement.

  enforcement_3_required_type_hints:
    rule: "100% type hints prevent stub that passes mypy"
    how_it_works: |
      If you write: def method(self, x): pass
      mypy --strict will fail with: error: Function is missing a return type annotation
      
      So you MUST write: def method(self, x: str) -> str:
      
      And then "pass" won't satisfy the return type, so you implement: return x.upper()
    
    validation: "mypy cortex/ --strict (must show 0 errors)"

  enforcement_4_test_pass_requirement:
    rule: "Module cannot be considered complete until tests pass"
    enforcement: |
      Definition of "done":
      - pytest tests/unit/.../test_module.py -v shows ALL PASS
      - Not just "tests collected" - actually PASSING
      - pytest output shows: "50 passed in 0.34s" ✓
      - NOT: "50 error" ✗
    
    validation: |
      After each module completion:
      pytest tests/unit/.../test_module.py -v | tail -1
      → Must show "NN passed" not "NN error"

  enforcement_5_no_mock_implementations:
    rule: "No return Mock() or MagicMock() in production code"
    detection: |
      grep -r "Mock\|MagicMock" cortex/core/orchestrator_decorator.py
      → If found: WRONG, remove immediately
      
      Mock objects are for tests ONLY, never in production code.
      Tests will catch this - mock won't have required methods.

## WHEN YOU SEE AN ERROR

error_handling_guide:

  error_importerror_no_module:
    error: "ImportError: No module named 'cortex.core.orchestrator_decorator'"
    cause: "Module file doesn't exist yet"
    solution: |
      touch cortex/core/orchestrator_decorator.py
      echo '"""Module stub."""' > cortex/core/orchestrator_decorator.py
      # Then run step_6 (implement)

  error_importerror_cannot_import:
    error: "ImportError: cannot import name 'OrchestratorDecorator'"
    cause: "Module exists but class not defined"
    solution: |
      Add to module:
      class OrchestratorDecorator:
          """Decorator for orchestrators."""
          pass
      # Then run test again - will show next error

  error_typeerror_missing_argument:
    error: "TypeError: __init__() missing 1 required positional argument: 'func'"
    cause: "Method signature doesn't match test call"
    solution: |
      Test calls: OrchestratorDecorator(some_func)
      
      Your code has:
        def __init__(self):  # ← Missing 'func' parameter
      
      Fix to:
        def __init__(self, func):  # ← Matches test call

  error_assertionerror:
    error: "AssertionError: expected X but got Y"
    cause: "Implementation logic is wrong"
    solution: |
      1. Read test assertion: assert result == expected
      2. Understand what test expects: result should be expected
      3. Change implementation to return expected:
         return expected  # or compute it correctly
      4. Run test again

  error_attributeerror:
    error: "AttributeError: object has no attribute 'some_method'"
    cause: "Class missing a method"
    solution: |
      Add the method:
      def some_method(self, param):
          """Implementation."""
          # Add minimum code to pass test
          pass  # Temporary until test shows what it needs
      
      Run test: will show TypeError/AssertionError with real requirement

  error_mypy_error_no_return_type:
    error: "error: Function is missing a return type annotation"
    cause: "Type hints incomplete"
    solution: |
      Current:
        def method(self, x: str):
            return x
      
      Fix:
        def method(self, x: str) -> str:  # ← Add return type
            return x
      
      If multiple return types: use Union[str, int] or Optional[str]

  error_pytest_collection_fails:
    error: "ImportError during collection / SyntaxError"
    cause: "Python syntax error in module"
    solution: |
      1. Check for typos in module
      2. Verify indentation (Python is sensitive)
      3. Ensure all docstrings properly quoted
      4. Check for unclosed parentheses/brackets
      5. Run: python -m py_compile cortex/core/orchestrator_decorator.py
         → Will show exact syntax error

## COMPLETION CHECKLIST PER MODULE

per_module_completion_checklist:

  before_starting:
    - [ ] Located test file
    - [ ] Read entire test file
    - [ ] Identified all required classes/functions
    - [ ] Ran test: pytest tests/.../test_module.py --co (see tests collect)
    - [ ] Ran test: pytest tests/.../test_module.py -v (see RED)

  during_implementation:
    - [ ] Created module file with docstring
    - [ ] Added first class with docstring
    - [ ] Ran test for first test method (RED)
    - [ ] Implemented method to make test pass (GREEN)
    - [ ] Added type hints to all parameters
    - [ ] Added return type hint
    - [ ] Added Google docstring
    - [ ] Ran next test method
    - [ ] Repeated until all tests pass

  after_implementation:
    - [ ] ALL tests pass: pytest tests/.../test_module.py -v
    - [ ] No bare except clauses: grep "except:" cortex/.../module.py
    - [ ] All functions <500 lines
    - [ ] All type hints present: mypy cortex/.../module.py --strict (0 errors)
    - [ ] All docstrings present
    - [ ] No Mock/MagicMock in production code
    - [ ] Git committed with test count in message
    - [ ] Next module ready to start

## BATCH OPERATIONS (After individual modules working)

batch_operations:

  after_phase_e2_5_modules_complete:
    action: "Verify all 5 critical modules together"
    command: |
      pytest tests/unit/core/test_orchestrator_decorator.py \
             tests/unit/core/orchestrator/test_conversation_protocol.py \
             tests/unit/core/interfaces/test_i_orchestrator.py \
             tests/unit/infrastructure/test_database.py \
             tests/unit/infrastructure/test_audit_logger.py \
             -v
    
    expected_output: |
      ✓ 180 passed (50+35+28+42+25)
      ✓ 0 errors
      ✓ Collection: 7480/7547 (76-52 errors fixed = 24 errors resolved = 24 more tests collected)

  after_all_modules_implemented:
    action: "Run full test suite verification"
    command: |
      pytest tests/ --tb=short -v | tail -50
    
    expected_output: |
      ✓ 7400+ passed (≥98%)
      ✓ 0 collection errors
      ✓ 0 failures
      ✓ Tests in X seconds

  quality_gate_final:
    action: "Final governance and type check"
    commands: |
      # Type hints check
      mypy cortex/ --strict
      → 0 errors
      
      # Bare except check
      grep -r "except:" cortex/ | wc -l
      → Should be 0 or small number (only test fixtures)
      
      # Line length check
      find cortex -name "*.py" -exec sh -c 'wc -l "$1" | awk "{if (\$1>500) print \$2 \": \" \$1}" ' _ {} \;
      → Should be 0 or small number

## VELOCITY TARGETS

expected_velocity:

  per_day_targets:
    modules_per_day: "7-10 modules"
    lines_of_code_per_day: "1500-2000 LOC"
    tests_fixed_per_day: "400-600 tests"
    
    day_1: "7 modules × 200-300 LOC = 1400-2100 LOC, 280-420 tests"
    day_2: "8 modules × 200-300 LOC = 1600-2400 LOC, 320-480 tests"
    day_3: "8 modules × 200-300 LOC = 1600-2400 LOC, 320-480 tests"
    day_4: "6 modules × 200-300 LOC = 1200-1800 LOC, 240-360 tests"

  commit_frequency: "1 module per commit (enables rollback, clear history)"

## FINAL VALIDATION

final_validation_per_module:

  test_command: "pytest tests/unit/.../test_module.py -v --tb=short"
  
  pass_criteria: |
    ✓ All tests collected (no ImportError)
    ✓ All tests passed (no FAILED)
    ✓ Test count shown in output (50 passed, 35 passed, etc.)
    ✓ Execution time < 5 seconds per 50 tests
  
  fail_criteria: |
    ✗ Any tests marked FAILED
    ✗ Any ImportError or ModuleNotFoundError
    ✗ TypeError or AttributeError
    ✗ Collection time > 10 seconds (suggests heavy computation in module level)
