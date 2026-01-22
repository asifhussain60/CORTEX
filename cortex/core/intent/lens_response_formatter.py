"""LENS Response Formatter.

Formats LENS reflection responses into various output formats (JSON, YAML, Markdown).

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import yaml


class ResponseFormat(Enum):
    """Available response formats."""
    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"
    TEXT = "text"


class SeverityColor(Enum):
    """Severity colors for formatted output."""
    SUCCESS = "green"
    WARNING = "yellow"
    ERROR = "red"
    INFO = "blue"


@dataclass
class FormattedResponse:
    """Formatted response data.
    
    Attributes:
        format_type: The format type used.
        content: The formatted content string.
        metadata: Additional metadata about the formatting.
    """
    format_type: ResponseFormat = ResponseFormat.TEXT
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class LENSResponseFormatter:
    """Formatter for LENS reflection responses.
    
    Converts reflection responses into various output formats for display.
    """
    
    def __init__(self) -> None:
        """Initialize the formatter."""
        self._default_format = ResponseFormat.JSON
    
    def format(
        self,
        response: Any,
        output_format: ResponseFormat = ResponseFormat.JSON,
    ) -> str:
        """Format a response.
        
        Args:
            response: The response object to format.
            output_format: The desired output format.
            
        Returns:
            Formatted string content.
        """
        if output_format == ResponseFormat.JSON:
            result = self._format_json(response)
        elif output_format == ResponseFormat.YAML:
            result = self._format_yaml(response)
        elif output_format == ResponseFormat.MARKDOWN:
            result = self._format_markdown(response)
        else:
            result = self._format_text(response)
        return result.content
    
    def format_response(
        self,
        response: Any,
        output_format: ResponseFormat = ResponseFormat.JSON,
    ) -> FormattedResponse:
        """Format a response and return full FormattedResponse object.
        
        Args:
            response: The response object to format.
            output_format: The desired output format.
            
        Returns:
            FormattedResponse with the formatted content.
        """
        if output_format == ResponseFormat.JSON:
            return self._format_json(response)
        elif output_format == ResponseFormat.YAML:
            return self._format_yaml(response)
        elif output_format == ResponseFormat.MARKDOWN:
            return self._format_markdown(response)
        else:
            return self._format_text(response)
    
    def _format_json(self, response: Any) -> FormattedResponse:
        """Format as JSON."""
        try:
            if hasattr(response, '__dict__'):
                data = self._to_dict(response)
            else:
                data = response
            content = json.dumps(data, indent=2, default=str)
        except (TypeError, ValueError):
            content = str(response)
        
        return FormattedResponse(
            format_type=ResponseFormat.JSON,
            content=content,
        )
    
    def _format_yaml(self, response: Any) -> FormattedResponse:
        """Format as YAML."""
        try:
            if hasattr(response, '__dict__'):
                data = self._to_dict(response)
            else:
                data = response
            content = yaml.safe_dump(data, default_flow_style=False)
        except (TypeError, ValueError):
            content = str(response)
        
        return FormattedResponse(
            format_type=ResponseFormat.YAML,
            content=content,
        )
    
    def _format_markdown(self, response: Any) -> FormattedResponse:
        """Format as Markdown."""
        if hasattr(response, '__dict__'):
            data = self._to_dict(response)
            lines = ["# Response\n"]
            for key, value in data.items():
                lines.append(f"**{key}**: {value}\n")
            content = "\n".join(lines)
        else:
            content = f"# Response\n\n{response}"
        
        return FormattedResponse(
            format_type=ResponseFormat.MARKDOWN,
            content=content,
        )
    
    def _format_text(self, response: Any) -> FormattedResponse:
        """Format as plain text."""
        return FormattedResponse(
            format_type=ResponseFormat.TEXT,
            content=str(response),
        )
    
    def _to_dict(self, obj: Any) -> Dict[str, Any]:
        """Convert object to dictionary."""
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        elif hasattr(obj, '__dict__'):
            result = {}
            for key, value in obj.__dict__.items():
                if not key.startswith('_'):
                    if hasattr(value, '__dict__'):
                        result[key] = self._to_dict(value)
                    elif isinstance(value, Enum):
                        result[key] = value.value
                    else:
                        result[key] = value
            return result
        return {"value": str(obj)}


__all__ = [
    "ResponseFormat",
    "SeverityColor",
    "FormattedResponse",
    "LENSResponseFormatter",
]