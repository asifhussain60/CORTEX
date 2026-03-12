"""CORTEX Import Guard Hook — dissolved package detection.

PostToolUse hook: After any Python file is edited, checks for imports from
dissolved packages (cortex_intelligence, cortex_lens, cortex.brain, cortex_brain).
"""
import json
import pathlib
import sys

DISSOLVED = [
    "cortex_intelligence",
    "cortex_lens",
    "cortex.brain",
    "cortex_brain",
]


def main() -> None:
    data = json.load(sys.stdin)
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    if tool_name not in ("create_file", "replace_string_in_file", "editFiles"):
        json.dump({"continue": True}, sys.stdout)
        return

    file_path = tool_input.get("filePath", tool_input.get("file_path", ""))
    if not file_path or not file_path.endswith(".py"):
        json.dump({"continue": True}, sys.stdout)
        return

    path = pathlib.Path(file_path)
    if not path.exists():
        json.dump({"continue": True}, sys.stdout)
        return

    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        json.dump({"continue": True}, sys.stdout)
        return

    violations = []
    for line_num, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if not (stripped.startswith("import ") or stripped.startswith("from ")):
            continue
        for pkg in DISSOLVED:
            if pkg in stripped:
                violations.append(f"  L{line_num}: {stripped}")
                break

    if violations:
        detail = "\n".join(violations[:5])
        msg = (
            f"Import Guard: Dissolved package import(s) detected in {path.name}:\n"
            f"{detail}\n"
            f"Use cortex.intelligence, cortex.lens instead."
        )
        json.dump({"continue": True, "systemMessage": msg}, sys.stdout)
    else:
        json.dump({"continue": True}, sys.stdout)


if __name__ == "__main__":
    main()
