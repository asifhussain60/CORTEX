"""
Simple Response Formatter
Purpose: One function to format clear, scannable orchestrator responses
Authority: chat01.md clarity standards (Phase 53 simplification)
"""

from typing import Dict, List, Optional, Any


def format_response(
    title: str,
    status: str = "COMPLETE",
    sections: Optional[List[Dict[str, Any]]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    next_steps: Optional[List[str]] = None,
    business_wisdom: Optional[str] = None,
) -> str:
    """
    Format a clear, scannable response using chat01.md standards.
    
    Args:
        title: Response title (e.g., "WAVE-1: Foundation Complete")
        status: Status emoji (COMPLETE ✅, IN_PROGRESS 🔵, BLOCKED 🔴, WARNING 🟡)
        sections: List of content sections, each with 'title' and 'content' or 'items'
        metrics: Optional metrics dict (e.g., {"Tests": "90/90", "Coverage": "95%"})
        next_steps: Optional list of next step strings
        business_wisdom: Optional formatted book references (from BusinessWisdomFormatter)
    
    Returns:
        Formatted markdown response string
    
    Example:
        >>> response = format_response(
        ...     title="WAVE-1: Foundation Complete",
        ...     status="COMPLETE",
        ...     sections=[
        ...         {"title": "Work Done", "items": ["Registry sync", "Test intelligence"]},
        ...         {"title": "Results", "content": "All 90 tests passing"}
        ...     ],
        ...     metrics={"Tests": "90/90", "Duration": "3h"},
        ...     next_steps=["Start WAVE-2"],
        ...     business_wisdom="### 📚 Business Wisdom\\n- **TDD** → CORE-008 (Kent Beck)"
        ... )
    
    AC-ID: AC-PHASE-06-S3-001
    Phase: 6 (Business Wisdom Display Enhancement - Stage 3)
    """
    sections = sections or []
    
    # Status emoji mapping
    status_icons = {
        "COMPLETE": "✅",
        "IN_PROGRESS": "🔵",
        "BLOCKED": "🔴",
        "WARNING": "🟡",
        "PLANNED": "⚪"
    }
    icon = status_icons.get(status.upper(), "📋")
    
    lines = []
    
    # Header with separator
    lines.append("----------------------------------------")
    lines.append(f"{icon} {title}")
    lines.append("----------------------------------------")
    lines.append("")
    
    # Business Wisdom section (if provided) - appears after header
    if business_wisdom:
        lines.append(business_wisdom)
        lines.append("")
    
    # Progress bar if metrics include percentage
    if metrics and "Progress" in metrics:
        progress = metrics["Progress"]
        if isinstance(progress, (int, float)):
            bar = _render_progress_bar(progress)
            lines.append(bar)
            lines.append("")
    
    # Sections
    for section in sections:
        section_title = section.get("title", "")
        lines.append(f"## {section_title}")
        lines.append("")
        
        # Section content (prose)
        if "content" in section:
            lines.append(section["content"])
            lines.append("")
        
        # Section items (bulleted list)
        if "items" in section:
            for item in section["items"]:
                lines.append(f"- {item}")
            lines.append("")
        
        # Section table data
        if "table" in section:
            lines.append(_render_table(section["table"]))
            lines.append("")
    
    # Metrics table (if provided)
    if metrics:
        lines.append("## Metrics")
        lines.append("")
        for key, value in metrics.items():
            if key != "Progress":  # Skip progress (already shown in bar)
                lines.append(f"**{key}:** {value}")
        lines.append("")
    
    # Next steps (if provided)
    if next_steps:
        lines.append("## Next Steps")
        lines.append("")
        for i, step in enumerate(next_steps, 1):
            lines.append(f"{i}. {step}")
        lines.append("")
    
    # Footer separator
    lines.append("----------------------------------------")
    
    return "\n".join(lines)


def _render_progress_bar(percentage: float, width: int = 10) -> str:
    """Render ASCII progress bar: [██████░░░░] 60%"""
    filled = int(width * (percentage / 100))
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {percentage}%"


def _render_table(table_data: Dict[str, List[str]]) -> str:
    """
    Render markdown table from dict.
    
    Args:
        table_data: {"headers": ["Col1", "Col2"], "rows": [["val1", "val2"], ...]}
    
    Returns:
        Markdown table string
    """
    headers = table_data.get("headers", [])
    rows = table_data.get("rows", [])
    
    if not headers or not rows:
        return ""
    
    lines = []
    
    # Header row
    lines.append("| " + " | ".join(headers) + " |")
    
    # Separator row
    lines.append("|" + "|".join(["---"] * len(headers)) + "|")
    
    # Data rows
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    
    return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    # Example from chat01.md style
    response = format_response(
        title="WAVE-1: Foundation & Intelligence Bootstrap",
        status="COMPLETE",
        sections=[
            {
                "title": "Work Completed",
                "items": [
                    "Registry sync - WAVE-O marked complete",
                    "Test intelligence layers - 59/59 tests passing",
                    "Quality validator - 20 brittleness patterns"
                ]
            },
            {
                "title": "Test Results",
                "table": {
                    "headers": ["Component", "Tests", "Status"],
                    "rows": [
                        ["Demand Generator", "16/16", "✅ Pass"],
                        ["Test Composer", "21/21", "✅ Pass"],
                        ["Quality Validator", "22/22", "✅ Pass"]
                    ]
                }
            }
        ],
        metrics={
            "Progress": 100,
            "Tests": "59/59",
            "Duration": "3 hours",
            "Coverage": "95%"
        },
        next_steps=[
            "Review wave completion",
            "Proceed with WAVE-2 scaffolder integration"
        ]
    )
    
    print(response)
