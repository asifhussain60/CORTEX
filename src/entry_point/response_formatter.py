"""
Response Formatter for CORTEX Entry Point

Formats agent responses into user-friendly output with structured
metadata, success/error messages, and actionable context.
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json

from ..cortex_agents.base_agent import AgentResponse


class ResponseFormatter:
    """
    Formats agent responses for user consumption.
    
    The ResponseFormatter transforms AgentResponse objects into
    human-readable formats with:
    - Clear success/error messages
    - Structured metadata
    - Result data presentation
    - Action summaries
    - Recommendations and next steps
    
    Example:
        formatter = ResponseFormatter()
        
        response = AgentResponse(
            success=True,
            result={"files": ["src/auth.py"]},
            message="Task completed successfully",
            agent_name="CodeExecutor"
        )
        
        formatted = formatter.format(response)
        # Returns formatted string with status, message, and details
    """
    
    def format(
        self,
        response: AgentResponse,
        include_metadata: bool = True,
        include_recommendations: bool = True,
        format_type: str = "text"
    ) -> str:
        """
        Format agent response into readable output.
        
        Args:
            response: The AgentResponse to format
            include_metadata: Whether to include metadata section
            include_recommendations: Whether to include recommendations
            format_type: Output format ("text", "json", "markdown")
            
        Returns:
            Formatted response string
        """
        if format_type == "json":
            return self._format_json(response)
        elif format_type == "markdown":
            return self._format_markdown(response, include_metadata, include_recommendations)
        else:
            return self._format_text(response, include_metadata, include_recommendations)
    
    def _format_text(
        self,
        response: AgentResponse,
        include_metadata: bool,
        include_recommendations: bool
    ) -> str:
        """Format response as plain text."""
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
        include_metadata: bool,
        include_recommendations: bool
    ) -> str:
        """Format response as Markdown."""
        lines = []
        
        # Header with status
        symbol = "✓" if response.success else "✗"
        status = "SUCCESS" if response.success else "FAILURE"
        lines.append(f"## {symbol} {status}\n")
        
        # Agent name
        if response.agent_name:
            lines.append(f"**Agent:** {response.agent_name}\n")
        
        # Main message
        if response.message:
            lines.append(response.message + "\n")
        
        # Result section
        if response.result:
            lines.append("### Result\n")
            if isinstance(response.result, dict):
                for key, value in response.result.items():
                    if isinstance(value, list):
                        lines.append(f"**{key}:**")
                        for item in value:
                            lines.append(f"  - {item}")
                    else:
                        lines.append(f"**{key}:** {value}")
            else:
                lines.append(str(response.result))
            lines.append("")
        
        # Duration
        if response.duration_ms > 0:
            lines.append(f"**Duration:** {response.duration_ms}ms\n")
        
        # Metadata
        if include_metadata and response.metadata:
            lines.append("### Metadata\n")
            for key, value in response.metadata.items():
                lines.append(f"- **{key}:** {value}")
            lines.append("")
        
        # Recommendations
        if include_recommendations:
            recs = self._extract_recommendations(response)
            if recs:
                lines.append("### Recommendations\n")
                for rec in recs:
                    lines.append(f"- {rec}")
        
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
    
    def _format_result(self, result: Any) -> List[str]:
        """Format result data into readable lines."""
        lines = []
        
        if isinstance(result, dict):
            for key, value in result.items():
                if isinstance(value, list):
                    lines.append(f"  {key}:")
                    for item in value:
                        lines.append(f"    - {item}")
                elif isinstance(value, dict):
                    lines.append(f"  {key}:")
                    for subkey, subvalue in value.items():
                        lines.append(f"    {subkey}: {subvalue}")
                else:
                    lines.append(f"  {key}: {value}")
        elif isinstance(result, list):
            for item in result:
                lines.append(f"  - {item}")
        else:
            lines.append(f"  {result}")
        
        return lines
    
    def _format_metadata(self, metadata: Dict[str, Any]) -> List[str]:
        """Format metadata dictionary."""
        lines = []
        for key, value in metadata.items():
            # Skip internal metadata
            if key.startswith("_"):
                continue
            lines.append(f"  {key}: {value}")
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
