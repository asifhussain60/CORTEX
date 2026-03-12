"""CORTEX Snake Case Guard Hook — CORE-028 enforcement.

PostToolUse hook: After a file is created in cortex/ or tests/, warns if the
filename is not snake_case.
"""
import json
import pathlib
import re
import sys

SNAKE_CASE = re.compile(r"^[a-z][a-z0-9_]*\.py$")


def main() -> None:
    data = json.load(sys.stdin)
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    # Only act on file creation
    if tool_name != "create_file":
        json.dump({"continue": True}, sys.stdout)
        return

    file_path = tool_input.get("filePath", tool_input.get("file_path", ""))
    if not file_path or not file_path.endswith(".py"):
        json.dump({"continue": True}, sys.stdout)
        return

    path = pathlib.PurePosixPath(file_path)
    parts = path.parts

    # Only check cortex/ and tests/ directories
    if "cortex" not in parts and "tests" not in parts:
        json.dump({"continue": True}, sys.stdout)
        return

    filename = path.name

    # Skip dunder files
    if filename.startswith("__"):
        json.dump({"continue": True}, sys.stdout)
        return

    if not SNAKE_CASE.match(filename):
        msg = (
            f"CORE-028 Snake Case Guard: '{filename}' is not snake_case. "
            f"Rename to a lowercase_with_underscores.py format."
        )
        json.dump({"continue": True, "systemMessage": msg}, sys.stdout)
    else:
        json.dump({"continue": True}, sys.stdout)


if __name__ == "__main__":
    main()
