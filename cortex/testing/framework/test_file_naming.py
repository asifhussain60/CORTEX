"""
CORTEX Test File Naming Adapter — FileFactory integration for test files.

All CORTEX test filenames are generated and validated through the canonical
FileFactory (cortex/core/file_factory.py) per CORE-028.

Rules enforced:
  ✅ Prefix: test_
  ✅ Case: snake_case (all lowercase, underscores only)
  ✅ Extension: .py
  ❌ No CamelCase, no kebab-case, no missing prefix

Authority: CORE-008 | CORE-011 | CORE-012 | CORE-028
AC-ID: AC-TEST-PARALLEL-001
"""

from __future__ import annotations

import re
from typing import Optional

from cortex.core.file_factory import FileFactory, NamingResult, FileFactoryConfig


def _camel_to_snake(name: str) -> str:
    """Convert CamelCase or PascalCase to snake_case.

    Args:
        name: Input string in any case format.

    Returns:
        Lowercase snake_case string.
    """
    # Insert underscore before uppercase letters that follow lowercase/digits
    s1 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    # Handle sequences like 'MCPTool' → 'MCP_Tool'
    s2 = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", s1)
    return s2.lower()


class TestFileNamingAdapter:
    """Adapts FileFactory for CORTEX test file naming conventions.

    Wraps ``FileFactory.python_test()`` with CamelCase→snake_case
    conversion so orchestrators and the runner can generate correct
    test filenames from class names or subject nouns.

    Example::

        adapter = TestFileNamingAdapter()
        result = adapter.generate("ParallelRunner")
        # result.filename → "test_parallel_runner.py"
        # result.is_valid → True
    """

    def __init__(self, factory: Optional[FileFactory] = None) -> None:
        """Initialise with optional FileFactory instance.

        Args:
            factory: Existing FileFactory instance (default: new instance).
        """
        self.factory: FileFactory = factory or FileFactory()

    def generate(self, subject: str, context: str = "") -> NamingResult:
        """Generate a validated test filename for the given subject.

        Converts CamelCase subjects to snake_case before delegating
        to FileFactory.python_test().

        Args:
            subject: Module/class name to generate test filename for.
                     Accepts CamelCase (``BatchProgressReporter``) or
                     snake_case (``batch_progress_reporter``).
            context: Optional context prefix (e.g. ``"parallel"``).

        Returns:
            NamingResult with filename and validation info.
        """
        # Normalise to snake_case
        snake_subject = _camel_to_snake(subject.strip())
        # Strip leading underscores that might arise from leading caps
        snake_subject = snake_subject.lstrip("_")

        if context:
            snake_context = _camel_to_snake(context.strip()).lstrip("_")
            return self.factory.python_test(noun=snake_subject, context=snake_context)

        return self.factory.python_test(noun=snake_subject)

    def validate(self, filename: str) -> NamingResult:
        """Validate an existing test filename against CORE-028 rules.

        Adds an explicit check that the filename starts with ``test_``.

        Args:
            filename: Filename to validate (e.g. ``"test_runner.py"``).

        Returns:
            NamingResult with is_valid flag and any violations.
        """
        result = self.factory.validate(filename)

        # Enforce test_ prefix (FileFactory may not check this specifically)
        if not filename.startswith("test_"):
            result.is_valid = False
            result.violations.append(
                "Test filenames must start with 'test_' (CORE-028)"
            )
            if result.suggestion is None:
                name_no_ext = filename.rsplit(".", 1)[0]
                result.suggestion = f"test_{name_no_ext}.py"

        return result
