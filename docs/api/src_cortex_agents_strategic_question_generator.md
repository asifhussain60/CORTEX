# src.cortex_agents.strategic.question_generator

Question Generator Utility (CORTEX 2.1)

Generates high-quality clarifying questions for interactive planning.
Prioritizes questions by importance and adapts to user expertise level.

Part of CORTEX 2.1 Interactive Planning enhancement.

## Functions

### `generate_questions(request, context, max_questions)`

Convenience function to generate questions.

Args:
    request: User's request text
    context: Additional context
    max_questions: Maximum questions to generate

Returns:
    List of Question objects
