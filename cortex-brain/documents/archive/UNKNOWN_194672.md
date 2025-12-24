  Test location violation detected!

  Target: '{target_path}'
  Test Type: '{test_type}'

  ❌ WRONG: Application test being created in CORTEX folder
  - Path: CORTEX/tests/test_user_feature.py
  - Reason: Application tests don't belong in CORTEX
  - Impact: Pollutes CORTEX with application-specific code

  ✅ CORRECT: Application test in user repository
  - Path: /Users/user/myapp/tests/test_user_feature.py
  - Framework: {user's framework} (pytest/jest/xunit/etc.)
  - Conventions: {user's naming patterns}
  - Brain Learning: Test patterns stored in cortex-brain/tier2/

  **CORTEX Tests (stay in CORTEX folder):**
  - Brain protection tests
  - Agent functionality tests
  - Workflow orchestration tests
  - CORTEX infrastructure tests

  **Application Tests (go in user repo):**
  - Business logic tests
  - Feature tests
  - Integration tests
  - E2E tests

  **Knowledge Capture (automatic):**
  - Test framework detection → Tier 2
  - Naming conventions → Tier 2
  - Test patterns → Tier 2
  - Code coverage insights → Tier 1
  - Common failure patterns → Tier 2

rationale: |
  TEST_LOCATION_SEPARATION: Architectural Clarity & Brain Intelligence

  Problem Scenario:
  - User developing "payment processing" feature
  - CORTEX generates test_payment.py in CORTEX/tests/
  - Test contains application-specific logic
  - CORTEX repo polluted with user's business logic
  - User can't find tests in their own repo
  - Tests don't use user's existing framework

  Correct Approach:
  1. **Detect Context:**
     - Working directory: /Users/user/myapp
     - Test framework: pytest (detected from requirements.txt)
     - Convention: tests/ folder with test_*.py pattern

  2. **Generate Tests in User Repo:**
     - Path: /Users/user/myapp/tests/test_payment.py
     - Framework: pytest (user's choice)
     - Style: Matches user's existing tests

  3. **Capture Knowledge for Brain:**
     - Pattern: "Payment tests use mock stripe API"
     - Pattern: "User prefers parametrized fixtures"
     - Insight: "Payment tests fail when DB not seeded"
     - Store: cortex-brain/tier2/knowledge-graph.yaml

  4. **Benefits:**
     - User repo self-contained with its tests
     - CORTEX stays focused on CORTEX functionality
     - Brain learns from user patterns (not polluted with user code)
     - User's test framework honored
     - Proper separation of concerns

  Brain Learning Mechanism:
  - Monitor test execution results
  - Track framework usage patterns
  - Identify common anti-patterns
  - Store generalized insights (not specific code)
  - Use insights to improve future test generation

  Exception:
  Only CORTEX-related tests (brain, agents, workflows) stay in CORTEX folder.
