---
applyTo: "cortex/**/*.py"
---

# CORTEX Python Source Rules

**These rules apply automatically when editing any Python file under `cortex/`.**

## Type Safety (CORE-011)
- ALL functions MUST have type hints on every parameter and return type
- Use `Optional[X]` for nullable parameters, not `X | None` (compatibility)
- Use `list[str]` not `List[str]` (Python 3.9+)

## Documentation (CORE-012)
- ALL public classes and methods MUST have docstrings
- Use Google-style docstring format: `Args:`, `Returns:`, `Raises:`
- Private methods (`_name`) require docstrings only if logic is non-obvious

## Naming (CORE-028)
- File names: `snake_case.py` only — never camelCase or PascalCase
- Class names: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`

## Imports
- ALL imports use `cortex.*` package path — never `cortex_intelligence`, `cortex_lens`, or `cortex.brain`
- Never import from dissolved packages: `cortex_brain`, `cortex_intelligence`, `cortex_lens`
- Use `from pathlib import Path` — never `os.path` for path operations
- Guard `validate_orchestrator_context` calls:
  ```python
  if orchestrator_context is not None:
      validate_orchestrator_context(orchestrator_context)
  ```

## No Duplicates (CORE-035)
- Single canonical implementation per class — never define the same class in two files
- If a class already exists elsewhere in `cortex/`, import it — do not redefine

## V2 Conventions
- Prefer canonical implementations over temporary compatibility shims; remove expired shims during consolidation phases
- Keep imports and class ownership consistent with consolidated orchestrator/skill surfaces

## AC Markers
- Every public orchestrator method MUST emit `AC_START` at entry and `AC_COMPLETE` at exit
- Format: `AC-{DOMAIN}-{SEQUENCE}` (e.g. `AC-P89-001`)
- No orphaned `AC_START` without matching `AC_COMPLETE`
