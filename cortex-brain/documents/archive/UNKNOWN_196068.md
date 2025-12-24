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
