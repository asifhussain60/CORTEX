"""CORTEX Thin Index Guard Hook — master plan size enforcement.

PostToolUse hook: After cortex-master.yaml is edited, warns if it exceeds
the THIN INDEX CONTRACT limits (alarm at 700, hard limit at 800 lines).
"""
import json
import pathlib
import sys

ALARM_THRESHOLD = 700
HARD_LIMIT = 800
TARGET_FILE = "cortex-registry/cortex-master.yaml"


def main() -> None:
    data = json.load(sys.stdin)
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    if tool_name not in ("create_file", "replace_string_in_file", "editFiles"):
        json.dump({"continue": True}, sys.stdout)
        return

    file_path = tool_input.get("filePath", tool_input.get("file_path", ""))
    if not file_path or not file_path.endswith("cortex-master.yaml"):
        json.dump({"continue": True}, sys.stdout)
        return

    path = pathlib.Path(TARGET_FILE)
    if not path.exists():
        # Try absolute path
        path = pathlib.Path(file_path)
    if not path.exists():
        json.dump({"continue": True}, sys.stdout)
        return

    try:
        line_count = len(path.read_text(encoding="utf-8").splitlines())
    except (OSError, UnicodeDecodeError):
        json.dump({"continue": True}, sys.stdout)
        return

    if line_count > HARD_LIMIT:
        msg = (
            f"THIN INDEX CONTRACT VIOLATION: cortex-master.yaml is {line_count} lines "
            f"(hard limit: {HARD_LIMIT}). Extract phase detail to "
            f"cortex-registry/planning/phases/planned/<phase-id>.yaml."
        )
        json.dump({"continue": True, "systemMessage": msg}, sys.stdout)
    elif line_count > ALARM_THRESHOLD:
        msg = (
            f"THIN INDEX CONTRACT WARNING: cortex-master.yaml is {line_count} lines "
            f"(alarm threshold: {ALARM_THRESHOLD}, hard limit: {HARD_LIMIT}). "
            f"Consider extracting detail to dedicated phase files."
        )
        json.dump({"continue": True, "systemMessage": msg}, sys.stdout)
    else:
        json.dump({"continue": True}, sys.stdout)


if __name__ == "__main__":
    main()
