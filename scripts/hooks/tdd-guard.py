"""CORTEX TDD Guard Hook — CORE-008 enforcement.

PostToolUse hook: After a Python file in cortex/ is edited, warns if no
corresponding test file exists in tests/.
"""
import json
import pathlib
import sys


def main() -> None:
    data = json.load(sys.stdin)
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    # Only act on file-editing tools
    if tool_name not in ("create_file", "replace_string_in_file", "editFiles"):
        json.dump({"continue": True}, sys.stdout)
        return

    file_path = tool_input.get("filePath", tool_input.get("file_path", ""))
    if not file_path:
        json.dump({"continue": True}, sys.stdout)
        return

    path = pathlib.PurePosixPath(file_path)

    # Only check cortex/**/*.py (not tests, scripts, etc.)
    parts = path.parts
    if "cortex" not in parts or not str(path).endswith(".py"):
        json.dump({"continue": True}, sys.stdout)
        return

    # Skip __init__.py and non-module files
    if path.name.startswith("__"):
        json.dump({"continue": True}, sys.stdout)
        return

    # Build expected test path: cortex/foo/bar.py → tests/foo/test_bar.py
    try:
        cortex_idx = parts.index("cortex")
        relative_parts = parts[cortex_idx + 1 :]
        if not relative_parts:
            json.dump({"continue": True}, sys.stdout)
            return

        test_name = f"test_{relative_parts[-1]}"
        test_path = pathlib.Path("tests", *relative_parts[:-1], test_name)

        if not test_path.exists():
            msg = (
                f"CORE-008 TDD Guard: No test file found at {test_path}. "
                f"Write a failing test before implementing changes."
            )
            json.dump({"continue": True, "systemMessage": msg}, sys.stdout)
            return
    except (ValueError, IndexError):
        pass

    json.dump({"continue": True}, sys.stdout)


if __name__ == "__main__":
    main()
