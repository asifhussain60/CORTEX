"""
LensVisionMixin — image and combined LENS+Vision analysis.

Covers:
  - analyze_image
  - analyze_with_vision

Extracted from lens_orchestrator.py (Phase 103-d, GAP-103-04).
Authority: CORE-008, CORE-011, CORE-012, LENS-003
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

__all__ = ["LensVisionMixin"]


class LensVisionMixin:
    """
    Mixin providing image and combined LENS+Vision analysis.

    Requires the host class to have:
        self.analyze_file(file_path: Path) -> Dict[str, Any]
    """

    def analyze_image(
        self,
        image_data: Optional[str] = None,
        image_url: Optional[str] = None,
        image_path: Optional[Path] = None,
        image_type: str = "unknown",
        analysis_depth: str = "standard",
    ) -> Dict[str, Any]:
        """
        Analyze an image using VisionAnalyzer.

        Extracts UI elements, URLs, issues, and structural information
        from screenshots, diagrams, mockups, and error messages.

        Args:
            image_data: Base64-encoded image data
            image_url: URL to image
            image_path: Path to image file
            image_type: Type of image (screenshot/diagram/mockup/error/unknown)
            analysis_depth: Depth of analysis (quick/standard/thorough)

        Returns:
            Dict with urls, ui_elements, issues, text_content, structural_map
        """
        from cortex.lens.analysis.vision_analyzer import AnalysisDepth, ImageType

        try:
            from cortex.lens.analysis.vision_analyzer import VisionAnalyzer
            analyzer = VisionAnalyzer()

            try:
                img_type = ImageType(image_type.lower())
            except ValueError:
                img_type = ImageType.UNKNOWN

            try:
                depth = AnalysisDepth(analysis_depth.lower())
            except ValueError:
                depth = AnalysisDepth.STANDARD

            if image_path and image_path.exists():
                result = analyzer.analyze_file(
                    file_path=image_path,
                    image_type=img_type,
                    depth=depth,
                )
            elif image_data:
                result = analyzer.analyze_base64(
                    image_data=image_data,
                    image_type=img_type,
                    depth=depth,
                )
            elif image_url:
                result = analyzer.analyze_url(
                    image_url=image_url,
                    image_type=img_type,
                    depth=depth,
                )
            else:
                return {
                    "status": "error",
                    "error": "Must provide image_data, image_url, or image_path",
                }

            return result.to_dict()

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def analyze_with_vision(
        self,
        file_path: Optional[Path] = None,
        image_data: Optional[str] = None,
        image_url: Optional[str] = None,
        image_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """
        Combined LENS + Vision analysis.

        Performs standard LENS analysis on a code file (if provided)
        AND Vision analysis on an image (if provided).

        Args:
            file_path: Path to code file for LENS analysis
            image_data: Base64-encoded image for Vision analysis
            image_url: URL to image for Vision analysis
            image_path: Path to image file for Vision analysis

        Returns:
            Dict with git_analysis, ast_analysis, comment_analysis, vision_analysis
        """
        result: Dict[str, Any] = {
            "git_analysis": {},
            "ast_analysis": {},
            "comment_analysis": {},
            "vision_analysis": {},
            "_metadata": {"analyzers_run": []},
        }

        if file_path and file_path.exists():
            lens_result = self.analyze_file(file_path)  # type: ignore[attr-defined]
            result["git_analysis"] = lens_result.get("git_analysis", {})
            result["ast_analysis"] = lens_result.get("ast_analysis", {})
            result["comment_analysis"] = lens_result.get("comment_analysis", {})
            result["_metadata"]["analyzers_run"].extend(["git", "ast", "comment"])

        if image_data or image_url or image_path:
            vision_result = self.analyze_image(
                image_data=image_data,
                image_url=image_url,
                image_path=image_path,
            )
            result["vision_analysis"] = vision_result
            result["_metadata"]["analyzers_run"].append("vision")

        return result
