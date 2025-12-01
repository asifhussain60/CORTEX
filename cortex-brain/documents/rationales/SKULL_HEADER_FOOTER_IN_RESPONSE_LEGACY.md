SKULL-006: Header/Footer in Copilot Response

Real incident (2025-11-11):
- User: "why is header not being displayed?"
- Headers printing to terminal (stdout) correctly
- But GitHub Copilot Chat response had NO header
- ResponseFormatter suppressing headers after first operation
- User specified they want header "in the copilot response in the chat window"

Root Cause:
1. Orchestrators print headers to stdout (terminal visibility)
2. But stdout doesn't reach Copilot Chat window
3. ResponseFormatter has _first_operation_shown flag (header suppression)
4. User sees execution in terminal, but Chat response lacks context

Why This Matters:
- Copyright attribution must be visible to user
- Purpose/profile provides context for what operation did
- Accomplishments show value delivered
- Headers make operations feel professional and informative
- Chat is primary interface (terminal is secondary)

Solution:
1. Orchestrators generate formatted headers/footers
2. Store in OperationResult.formatted_header/footer
3. ResponseFormatter checks for stored headers (priority)
4. Wraps headers in code blocks for proper display
5. Also prints to terminal for immediate visibility

SKULL-006 enforces this by:
- Requiring formatted_header/footer in OperationResult
- Integration tests verify headers in formatted response
- Blocking completion if headers missing from Chat output
- Ensuring copyright/attribution always visible

Implementation:
```python
# In orchestrator execute():
formatted_header = format_minimalist_header(...)
print(formatted_header)  # Terminal visibility

# ... operation logic ...

formatted_footer = format_completion_footer(...)
print(formatted_footer)  # Terminal visibility

return OperationResult(
    success=True,
    formatted_header=formatted_header,  # For Copilot Chat
    formatted_footer=formatted_footer   # For Copilot Chat
)
```
