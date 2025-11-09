"""
Response Formatter for CORTEX Entry Point

Formats agent responses into user-friendly output with structured
metadata, success/error messages, and actionable context.

Supports 3 verbosity levels:
- concise: 50-150 words (default)
- detailed: 200-400 words
- expert: Full detail, no limit
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json
import re

from src.cortex_agents.base_agent import AgentResponse


class ResponseFormatter:
    """
    Formats agent responses for user consumption with verbosity control.
    
    The ResponseFormatter transforms AgentResponse objects into
    human-readable formats with:
    - Clear success/error messages
    - Structured metadata
    - Result data presentation
    - Action summaries
    - Recommendations and next steps
    - Configurable verbosity levels
    
    Verbosity Levels:
        - concise: Quick summary (50-150 words) - DEFAULT
        - detailed: Structured breakdown (200-400 words)
        - expert: Full technical detail (no limit)
    
    Example:
        formatter = ResponseFormatter(default_verbosity="concise")
        
        response = AgentResponse(
            success=True,
            result={"files": ["src/auth.py"]},
            message="Task completed successfully",
            agent_name="CodeExecutor"
        )
        
        # Concise by default
        formatted = formatter.format(response)
        
        # Override per call
        detailed = formatter.format(response, verbosity="detailed")
    """
    
    def __init__(self, default_verbosity: str = "concise"):
        """
        Initialize formatter.
        
        Args:
            default_verbosity: "concise" | "detailed" | "expert"
        """
        self.default_verbosity = default_verbosity
        self.word_limits = {
            "concise": 150,
            "detailed": 400,
            "expert": None  # No limit
        }
    
    def format(
        self,
        response: AgentResponse,
        verbosity: Optional[str] = None,
        include_metadata: bool = None,
        include_recommendations: bool = None,
        format_type: str = "text"
    ) -> str:
        """
        Format agent response into readable output with verbosity control.
        
        Args:
            response: The AgentResponse to format
            verbosity: Override default verbosity ("concise"|"detailed"|"expert")
            include_metadata: Whether to include metadata (auto-set if None)
            include_recommendations: Whether to include recommendations (auto-set if None)
            format_type: Output format ("text", "json", "markdown")
            
        Returns:
            Formatted response string
        """
        verbosity = verbosity or self.default_verbosity
        
        # Auto-adjust metadata/recommendations based on verbosity
        if include_metadata is None:
            include_metadata = verbosity in ["detailed", "expert"]
        
        if include_recommendations is None:
            include_recommendations = verbosity in ["concise", "detailed"]
        
        # Format based on type
        if format_type == "json":
            formatted = self._format_json(response)
        elif format_type == "markdown":
            formatted = self._format_markdown(
                response, verbosity, include_metadata, include_recommendations
            )
        else:
            formatted = self._format_text(
                response, verbosity, include_metadata, include_recommendations
            )
        
        # Apply word limit for concise/detailed
        word_limit = self.word_limits.get(verbosity)
        if word_limit:
            formatted = self._truncate_to_limit(formatted, word_limit, verbosity)
        
        return formatted
    
    def _format_text(
        self,
        response: AgentResponse,
        verbosity: str,
        include_metadata: bool,
        include_recommendations: bool
    ) -> str:
        """Format response as plain text with verbosity control."""
        if verbosity == "concise":
            return self._format_text_concise(response)
        elif verbosity == "detailed":
            return self._format_text_detailed(response, include_metadata, include_recommendations)
        else:  # expert
            return self._format_text_expert(response, include_metadata, include_recommendations)
    
    def _format_text_concise(self, response: AgentResponse) -> str:
        """Format concise text (50-150 words)."""
        lines = []
        
        # Status (always)
        symbol = "✓" if response.success else "✗"
        status = "SUCCESS" if response.success else "FAILURE"
        lines.append(f"{symbol} **{status}**")
        
        # Message (truncated if long)
        if response.message:
            msg = response.message
            words = msg.split()
            if len(words) > 40:
                msg = " ".join(words[:40]) + "..."
            lines.append(f"\n{msg}")
        
        # Key result (summary only)
        if response.result:
            key_info = self._extract_key_info(response.result)
            if key_info:
                lines.append(f"\n**{key_info}**")
        
        # Top recommendation only
        if response.next_actions and len(response.next_actions) > 0:
            lines.append(f"\n**Next:** {response.next_actions[0]}")
        
        # Expansion hint
        lines.append(f"\n_Say 'show details' for more info_")
        
        return "\n".join(lines)
    
    def _format_text_detailed(
        self,
        response: AgentResponse,
        include_metadata: bool,
        include_recommendations: bool
    ) -> str:
        """Format detailed text (200-400 words)."""
        lines = []
        
        # Status line
        symbol = "✓" if response.success else "✗"
        status = "SUCCESS" if response.success else "FAILURE"
        lines.append(f"{symbol} {status}")
        
        # Agent name if available
        if response.agent_name:
            lines.append(f"Agent: {response.agent_name}")
        
        # Main message
        if response.message:
            lines.append(f"\n{response.message}")
        
        # Result section (abbreviated)
        if response.result:
            lines.append("\nResult:")
            lines.extend(self._format_result(response.result, max_items=5))
        
        # Duration
        if response.duration_ms > 0:
            lines.append(f"\nDuration: {response.duration_ms}ms")
        
        # Metadata (limited)
        if include_metadata and response.metadata:
            lines.append("\nMetadata:")
            lines.extend(self._format_metadata(response.metadata, max_items=3))
        
        # Top 3 recommendations
        if include_recommendations:
            recs = self._extract_recommendations(response)
            if recs:
                lines.append("\nRecommendations:")
                for rec in recs[:3]:
                    lines.append(f"  - {rec}")
        
        return "\n".join(lines)
    
    def _format_text_expert(
        self,
        response: AgentResponse,
        include_metadata: bool,
        include_recommendations: bool
    ) -> str:
        """Format expert text (full detail, no limit)."""
        lines = []
        
        # Status line
        symbol = "✓" if response.success else "✗"
        status = "SUCCESS" if response.success else "FAILURE"
        lines.append(f"{symbol} {status}")
        
        # Agent name if available
        if response.agent_name:
            lines.append(f"Agent: {response.agent_name}")
        
        # Main message
        if response.message:
            lines.append(f"\n{response.message}")
        
        # Result section
        if response.result:
            lines.append("\nResult:")
            lines.extend(self._format_result(response.result))
        
        # Duration
        if response.duration_ms > 0:
            lines.append(f"\nDuration: {response.duration_ms}ms")
        
        # Metadata
        if include_metadata and response.metadata:
            lines.append("\nMetadata:")
            lines.extend(self._format_metadata(response.metadata))
        
        # Recommendations
        if include_recommendations:
            recs = self._extract_recommendations(response)
            if recs:
                lines.append("\nRecommendations:")
                for rec in recs:
                    lines.append(f"  - {rec}")
        
        return "\n".join(lines)
    
    def _format_markdown(
        self,
        response: AgentResponse,
        verbosity: str,
        include_metadata: bool,
        include_recommendations: bool
    ) -> str:
        """Format response as Markdown with verbosity control."""
        lines = []
        
        # Header with status
        symbol = "✓" if response.success else "✗"
        status = "SUCCESS" if response.success else "FAILURE"
        lines.append(f"## {symbol} {status}\n")
        
        # Agent name
        if response.agent_name:
            lines.append(f"**Agent:** {response.agent_name}\n")
        
        # Main message (truncate in concise mode)
        if response.message:
            msg = response.message
            if verbosity == "concise" and len(msg.split()) > 40:
                msg = " ".join(msg.split()[:40]) + "..."
            lines.append(msg + "\n")
        
        # Result section
        if response.result:
            lines.append("### Result\n")
            if isinstance(response.result, dict):
                max_items = 3 if verbosity == "concise" else (5 if verbosity == "detailed" else None)
                item_count = 0
                for key, value in response.result.items():
                    if max_items and item_count >= max_items:
                        lines.append(f"_...and {len(response.result) - max_items} more items_")
                        break
                    if isinstance(value, list):
                        lines.append(f"**{key}:**")
                        for item in value[:3 if verbosity == "concise" else None]:
                            lines.append(f"  - {item}")
                        if verbosity == "concise" and len(value) > 3:
                            lines.append(f"  _...and {len(value) - 3} more_")
                    else:
                        lines.append(f"**{key}:** {value}")
                    item_count += 1
            else:
                lines.append(str(response.result))
            lines.append("")
        
        # Duration
        if response.duration_ms > 0 and verbosity != "concise":
            lines.append(f"**Duration:** {response.duration_ms}ms\n")
        
        # Metadata (only in detailed/expert)
        if include_metadata and response.metadata and verbosity != "concise":
            lines.append("### Metadata\n")
            max_meta = 3 if verbosity == "detailed" else None
            for idx, (key, value) in enumerate(response.metadata.items()):
                if max_meta and idx >= max_meta:
                    break
                lines.append(f"- **{key}:** {value}")
            lines.append("")
        
        # Recommendations
        if include_recommendations:
            recs = self._extract_recommendations(response)
            if recs:
                lines.append("### Recommendations\n")
                max_recs = 1 if verbosity == "concise" else (3 if verbosity == "detailed" else None)
                for rec in recs[:max_recs]:
                    lines.append(f"- {rec}")
                if verbosity == "concise":
                    lines.append(f"\n_Say 'show details' for more info_")
        
        return "\n".join(lines)
    
    def _format_json(self, response: AgentResponse) -> str:
        """Format response as JSON."""
        data = {
            "success": response.success,
            "result": response.result,
            "message": response.message,
            "agent_name": response.agent_name,
            "duration_ms": response.duration_ms,
            "metadata": response.metadata,
            "next_actions": response.next_actions,
            "timestamp": response.timestamp.isoformat() if response.timestamp else None,
        }
        return json.dumps(data, indent=2, default=str)
    
    def _format_result(self, result: Any, max_items: Optional[int] = None) -> List[str]:
        """Format result data into readable lines with optional limit."""
        lines = []
        
        if isinstance(result, dict):
            item_count = 0
            for key, value in result.items():
                if max_items and item_count >= max_items:
                    lines.append(f"  _...and {len(result) - max_items} more items_")
                    break
                
                if isinstance(value, list):
                    lines.append(f"  {key}:")
                    list_limit = 3 if max_items else None
                    for idx, item in enumerate(value):
                        if list_limit and idx >= list_limit:
                            lines.append(f"    _...and {len(value) - list_limit} more_")
                            break
                        lines.append(f"    - {item}")
                elif isinstance(value, dict):
                    lines.append(f"  {key}:")
                    for subkey, subvalue in value.items():
                        lines.append(f"    {subkey}: {subvalue}")
                else:
                    lines.append(f"  {key}: {value}")
                
                item_count += 1
        elif isinstance(result, list):
            for idx, item in enumerate(result):
                if max_items and idx >= max_items:
                    lines.append(f"  _...and {len(result) - max_items} more items_")
                    break
                lines.append(f"  - {item}")
        else:
            lines.append(f"  {result}")
        
        return lines
    
    def _format_metadata(self, metadata: Dict[str, Any], max_items: Optional[int] = None) -> List[str]:
        """Format metadata dictionary with optional limit."""
        lines = []
        item_count = 0
        
        for key, value in metadata.items():
            # Skip internal metadata
            if key.startswith("_"):
                continue
            
            if max_items and item_count >= max_items:
                lines.append(f"  _...and {len(metadata) - max_items} more metadata items_")
                break
            
            lines.append(f"  {key}: {value}")
            item_count += 1
        
        return lines
    
    def _extract_recommendations(self, response: AgentResponse) -> List[str]:
        """Extract recommendations from response."""
        recommendations = []
        
        # Check next_actions first
        if response.next_actions:
            recommendations.extend(response.next_actions)
        
        # Check result for recommendations
        if isinstance(response.result, dict) and "recommendations" in response.result:
            recs = response.result["recommendations"]
            if isinstance(recs, list):
                recommendations.extend(recs)
            elif isinstance(recs, str):
                recommendations.append(recs)
        
        # Check metadata for next steps
        if response.metadata and "next_steps" in response.metadata:
            steps = response.metadata["next_steps"]
            if isinstance(steps, list):
                recommendations.extend(steps)
            elif isinstance(steps, str):
                recommendations.append(steps)
        
        # Generate default recommendations if none found
        if not recommendations:
            recommendations.extend(self._default_recommendations(response))
        
        return recommendations
    
    def _default_recommendations(self, response: AgentResponse) -> List[str]:
        """Generate default recommendations based on response."""
        recs = []
        
        if response.success:
            if isinstance(response.result, dict) and "files" in response.result:
                recs.append("Review the modified files")
            recs.append("Run tests to verify changes")
        else:
            recs.append("Check the error message for details")
            recs.append("Verify input parameters and try again")
        
        return recs
    
    def _extract_key_info(self, result: Dict) -> str:
        """Extract most important info from result dict for concise display."""
        # Prioritize: status, count, files, errors, summary
        priority_keys = ["status", "count", "files_changed", "files", "errors", "summary", "message"]
        
        for key in priority_keys:
            if key in result:
                val = result[key]
                if isinstance(val, list):
                    count = len(val)
                    if count > 0:
                        return f"{count} {key}"
                elif val:
                    return f"{key}: {str(val)[:50]}"
        
        # Fallback: first non-empty item
        for key, val in result.items():
            if val:
                if isinstance(val, list):
                    return f"{len(val)} {key}"
                else:
                    return f"{key}: {str(val)[:50]}"
        
        return "Result available"
    
    def _truncate_to_limit(self, text: str, word_limit: int, verbosity: str) -> str:
        """Truncate text to word limit preserving structure."""
        words = text.split()
        if len(words) <= word_limit:
            return text
        
        # Truncate and add expansion hint
        truncated = " ".join(words[:word_limit])
        
        # Add appropriate hint based on verbosity
        if verbosity == "concise":
            hint = "\n\n_Response truncated. Say 'show details' or 'show more' for full info_"
        else:  # detailed
            hint = "\n\n_Response truncated. Say 'explain fully' or 'show everything' for complete details_"
        
        return f"{truncated}...{hint}"
    
    def format_batch(
        self,
        responses: List[AgentResponse],
        include_summary: bool = True,
        format_type: str = "text"
    ) -> str:
        """
        Format multiple responses.
        
        Args:
            responses: List of responses to format
            include_summary: Whether to include summary section
            format_type: Output format
            
        Returns:
            Formatted batch output
        """
        if not responses:
            return "No responses to format"
        
        lines = []
        
        # Summary
        if include_summary:
            total = len(responses)
            successful = sum(1 for r in responses if r.success)
            lines.append(f"Batch Results: {successful}/{total} successful\n")
        
        # Individual responses
        for i, response in enumerate(responses, 1):
            if format_type == "markdown":
                lines.append(f"### Response {i}\n")
            else:
                lines.append(f"\n--- Response {i} ---")
            
            formatted = self.format(
                response,
                include_metadata=False,
                include_recommendations=False,
                format_type=format_type
            )
            lines.append(formatted)
        
        return "\n".join(lines)
    
    def format_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Format an error into a user-friendly message.
        
        Args:
            error: The exception that occurred
            context: Optional context about the error
            
        Returns:
            Formatted error message
        """
        lines = [
            f"✗ ERROR: {type(error).__name__}",
            f"\n{str(error)}"
        ]
        
        if context:
            lines.append("\nContext:")
            for key, value in context.items():
                lines.append(f"  {key}: {value}")
        
        lines.append("\nPlease check the error details and try again.")
        
        return "\n".join(lines)
    
    def format_progress(
        self,
        current: int,
        total: int,
        message: str = ""
    ) -> str:
        """
        Format progress indicator.
        
        Args:
            current: Current step
            total: Total steps
            message: Optional progress message
            
        Returns:
            Formatted progress string
        """
        percentage = int((current / total) * 100) if total > 0 else 0
        bar_length = 20
        filled = int((bar_length * current) / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_length - filled)
        
        result = f"[{bar}] {percentage}% ({current}/{total})"
        if message:
            result += f" - {message}"
        
        return result
