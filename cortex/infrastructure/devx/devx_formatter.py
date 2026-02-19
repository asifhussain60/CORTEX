"""DevX Formatter for code and output formatting."""

import json
from typing import Any, Dict, List


class DevxFormatter:
    """Formats code, output, and logs."""

    def __init__(self) -> None:
        """Initialize formatter."""
        pass

    def format_code(self, code: str) -> str:
        """Format Python code.

        Args:
            code: Code string

        Returns:
            Formatted code
        """
        # Simple formatting: add spaces around operators
        formatted = code.replace("=", " = ").replace("+", " + ")
        return formatted

    def format_output(self, data: Any) -> str:
        """Format output for display.

        Args:
            data: Data to format

        Returns:
            Formatted output string
        """
        if isinstance(data, dict):
            # Convert any objects with to_dict method
            converted_data: Dict[str, Any] = {}
            for k, v in data.items():
                if hasattr(v, "to_dict"):
                    converted_data[k] = v.to_dict()
                else:
                    converted_data[k] = v
            return json.dumps(converted_data, indent=2, default=str)
        return str(data)

    def format_logs(self, logs: List[str]) -> str:
        """Format log entries.

        Args:
            logs: List of log entries

        Returns:
            Formatted logs
        """
        return "\n".join(logs)
