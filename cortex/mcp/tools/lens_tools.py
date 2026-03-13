"""
LENS MCP Tools — cortex_vision_analyze

MCP tool wrapper for VisionAnalyzer image analysis.
Authority: Phase 81 — LENS Analysis Suite
"""
from typing import Any, Dict, Optional

from cortex.lens.analysis.vision_analyzer import VisionAnalyzer


def cortex_vision_analyze(
    image_data: Optional[str] = None,
    image_url: Optional[str] = None,
    image_type: str = "screenshot",
    analysis_depth: str = "standard",
) -> Dict[str, Any]:
    """Analyze an image via VisionAnalyzer.

    Args:
        image_data: Base64-encoded image data.
        image_url: URL of the image to analyze.
        image_type: Type of image (e.g. "screenshot", "diagram").
        analysis_depth: Depth of analysis ("standard", "thorough", "quick").

    Returns:
        Dict with at minimum a "status" key.
    """
    if not image_data and not image_url:
        return {
            "status": "error",
            "error": "Must provide either image_data (base64) or image_url.",
        }

    analyzer = VisionAnalyzer()

    if image_data:
        result = analyzer.analyze_base64(
            image_data=image_data,
            image_type=image_type,
            analysis_depth=analysis_depth,
        )
    else:
        result = analyzer.analyze_url(
            image_url=image_url,
            image_type=image_type,
            analysis_depth=analysis_depth,
        )

    return result.to_dict()
