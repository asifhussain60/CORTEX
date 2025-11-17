# Image Prompt: CORTEX Multi-Agent Coordination

**For:** ChatGPT Image Generator (DALL-E 3)

## Prompt

Create a professional sequence diagram with generous margins (10% on all sides) showing multi-agent coordination for feature implementation. The diagram should be centered with clear spacing.

**Visual Style:**
- Modern tech aesthetic with gradient background (dark navy to deep blue)
- Sequence diagram with vertical lifelines and horizontal messages
- Use different colors for different agent types
- Professional typography with perfect spelling
- Clean arrow lines for message flow

**Participants (Left to Right):**
1. "User" (person icon, gray color)
2. "Intent Router" (compass icon, orange color)
3. "Work Planner" (clipboard icon, orange color)
4. "Corpus Callosum" (bridge icon, green color)
5. "Code Executor" (laptop icon, blue color)
6. "Test Generator" (checkmark icon, blue color)
7. "Health Validator" (heart icon, blue color)
8. "Commit Handler" (branch icon, blue color)
9. "Tier 2 (KG)" (puzzle icon, green color)

**Message Flow (Top to Bottom):**

**Phase 1: Planning**
1. User → Intent Router: "Add user authentication"
2. Intent Router → Intent Router: Parse intent (PLAN)
3. Intent Router → Tier 2: Search similar patterns
4. Tier 2 → Intent Router: Found: auth_workflow (0.85 confidence)
5. Intent Router → Work Planner: Route to Work Planner
6. Work Planner → Work Planner: Create 4-phase plan
7. Work Planner → Corpus Callosum: Post plan to queue
8. Corpus Callosum → User: Plan ready for review

**Phase 2: Test Creation**
9. User → Corpus Callosum: "Start Phase 1"
10. Corpus Callosum → Test Generator: Phase 1: Create tests
11. Test Generator → Test Generator: Generate LoginTests.cs
12. Test Generator → Corpus Callosum: Tests created (RED)
13. Corpus Callosum → User: Phase 1 complete (tests failing ✓)

**Phase 3: Implementation**
14. User → Corpus Callosum: "Continue"
15. Corpus Callosum → Code Executor: Phase 2: Implement
16. Code Executor → Code Executor: Create AuthService.cs
17. Code Executor → Test Generator: Run tests
18. Test Generator → Code Executor: Tests pass (GREEN) ✓
19. Code Executor → Corpus Callosum: Implementation complete

**Phase 4: Validation & Commit**
20. Corpus Callosum → Health Validator: Phase 3: Validate
21. Health Validator → Health Validator: Check errors/warnings
22. Health Validator → Health Validator: Run full test suite
23. Health Validator → Corpus Callosum: All checks pass ✓
24. Corpus Callosum → Commit Handler: Phase 4: Commit
25. Commit Handler → Commit Handler: Create semantic message
26. Commit Handler → Commit Handler: Git commit
27. Commit Handler → Corpus Callosum: Committed with tag

**Phase 5: Learning**
28. Corpus Callosum → Tier 2: Store workflow pattern
29. Tier 2 → Tier 2: Update confidence (0.85 → 0.90)
30. Corpus Callosum → User: Feature complete 🎉

**Typography Requirements:**
- All text perfectly spelled
- Participant names: 14pt, bold
- Message text: 12pt, regular
- Phase headers: 16pt, bold, italic
- Notes: 11pt, italic

**Color Palette:**
- User: Gray (#6B7280)
- Right Brain Agents (Router, Planner): Orange (#F59E0B)
- Left Brain Agents (Executor, Generator, Validator, Handler): Blue (#3B82F6)
- Coordination (Corpus Callosum): Green (#10B981)
- Knowledge (Tier 2): Green (#10B981)
- Background: Gradient from #0F172A to #1E3A8A
- Lifelines: Light gray (#D1D5DB)
- Messages: White arrows

**Margin Requirements:**
- Top margin: 10% of canvas height
- Bottom margin: 10% of canvas height
- Left margin: 10% of canvas width
- Right margin: 10% of canvas width

**Additional Elements:**
- "CORTEX Multi-Agent Coordination" title at top
- "Feature Implementation: User Authentication" subtitle
- "5 Phases: Plan → Test → Implement → Validate → Learn" caption
- "© 2024-2025" copyright bottom right

Make it look like a professional system sequence diagram with perfect spelling and clear message flow.
