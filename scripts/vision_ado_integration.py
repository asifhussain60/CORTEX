"""
Integration module: Vision Analyzer + ADO Manager

Provides seamless integration between vision analysis and ADO work item creation.
Automatically extracts requirements from screenshots and creates ADO items.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import our modules
from ado_manager import ADOManager, ADOType, ADOPriority
from vision_analyzer import VisionAnalyzer, ImageType, ConfidenceLevel


class VisionADOIntegration:
    """
    Integrates Vision Analyzer with ADO Manager.
    
    Provides high-level methods for screenshot-driven ADO planning:
    - analyze_and_create_ado: One-step analysis + creation
    - batch_analyze: Process multiple screenshots
    - suggest_ado_fields: Get field suggestions from vision analysis
    """
    
    def __init__(
        self,
        ado_manager: Optional[ADOManager] = None,
        vision_analyzer: Optional[VisionAnalyzer] = None
    ):
        """
        Initialize integration module.
        
        Args:
            ado_manager: Optional ADO Manager instance (creates if None)
            vision_analyzer: Optional Vision Analyzer instance (creates if None)
        """
        self.ado_manager = ado_manager or ADOManager()
        self.vision_analyzer = vision_analyzer or VisionAnalyzer()
        
    def analyze_and_create_ado(
        self,
        image_path: str,
        ado_number: str,
        template_file_path: str,
        expected_type: Optional[ImageType] = None,
        additional_fields: Optional[Dict[str, Any]] = None
    ) -> tuple[str, Dict[str, Any]]:
        """
        Analyze screenshot and create ADO work item in one step.
        
        Args:
            image_path: Path to screenshot
            ado_number: ADO number (e.g., "ADO-12345")
            template_file_path: Path to template markdown file
            expected_type: Expected image type (auto-detect if None)
            additional_fields: Optional fields to override extracted data
            
        Returns:
            Tuple of (ado_number, extraction_result_dict)
        """
        # Analyze image
        analysis_result = self.vision_analyzer.analyze_image(
            image_path,
            expected_type
        )
        
        # Extract template data
        template_data = self.vision_analyzer.extract_for_ado_template(
            image_path
        )
        
        # Merge with additional fields (user overrides)
        if additional_fields:
            template_data.update(additional_fields)
        
        # Determine ADO type from image type
        ado_type = self._map_image_type_to_ado_type(analysis_result.image_type)
        
        # Determine priority
        priority = template_data.get("priority", "Medium")
        
        # Build tags
        tags = template_data.get("tags", [])
        tags.append(f"vision-extracted-{analysis_result.confidence.value}")
        
        # Create ADO work item
        created_ado = self.ado_manager.create_ado(
            ado_number=ado_number,
            ado_type=ado_type,
            title=template_data.get("title", f"Vision Extracted: {Path(image_path).stem}"),
            template_file_path=template_file_path,
            status="planning",
            priority=priority,
            tags=tags,
            dor_completed=0,
            dod_completed=0,
            conversation_ids=[],
            related_file_paths=template_data.get("related_file_paths", []),
            commit_shas=[]
        )
        
        # Return ADO number and analysis summary
        return created_ado, {
            "image_type": analysis_result.image_type.value,
            "confidence": analysis_result.confidence.value,
            "suggestions": analysis_result.suggestions,
            "warnings": analysis_result.warnings,
            "extracted_data": template_data
        }
    
    def suggest_ado_fields(
        self,
        image_path: str,
        expected_type: Optional[ImageType] = None
    ) -> Dict[str, Any]:
        """
        Analyze screenshot and return suggested ADO fields without creating item.
        
        Useful for interactive planning where user reviews before creating.
        
        Args:
            image_path: Path to screenshot
            expected_type: Expected image type (auto-detect if None)
            
        Returns:
            Dict of suggested ADO fields
        """
        # Analyze image
        analysis_result = self.vision_analyzer.analyze_image(
            image_path,
            expected_type
        )
        
        # Extract template data
        template_data = self.vision_analyzer.extract_for_ado_template(
            image_path
        )
        
        # Add metadata
        template_data.update({
            "image_type": analysis_result.image_type.value,
            "confidence": analysis_result.confidence.value,
            "suggestions": analysis_result.suggestions,
            "warnings": analysis_result.warnings,
            "ado_type": self._map_image_type_to_ado_type(analysis_result.image_type)
        })
        
        return template_data
    
    def batch_analyze(
        self,
        image_paths: List[str],
        output_file: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple screenshots and return suggestions for each.
        
        Args:
            image_paths: List of image paths
            output_file: Optional file to save results (JSON)
            
        Returns:
            List of suggestion dicts
        """
        results = []
        
        for image_path in image_paths:
            try:
                suggestions = self.suggest_ado_fields(image_path)
                suggestions["image_path"] = image_path
                suggestions["processed_at"] = datetime.now().isoformat()
                results.append(suggestions)
            except Exception as e:
                results.append({
                    "image_path": image_path,
                    "error": str(e),
                    "processed_at": datetime.now().isoformat()
                })
        
        # Save to file if requested
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
        
        return results
    
    def _map_image_type_to_ado_type(self, image_type: ImageType) -> str:
        """
        Map ImageType to ADO work item type.
        
        Args:
            image_type: Image type from vision analysis
            
        Returns:
            ADO type string (Bug, Feature, Task, etc.)
        """
        mapping = {
            ImageType.UI_MOCKUP: "Feature",
            ImageType.ERROR_SCREEN: "Bug",
            ImageType.ADO_WORK_ITEM: "Task",  # Default, can be overridden
            ImageType.ARCHITECTURE_DIAGRAM: "Epic",
            ImageType.UNKNOWN: "Task"
        }
        
        return mapping.get(image_type, "Task")
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """
        Get statistics about vision-driven ADO creation.
        
        Returns:
            Dict with stats (total items, by type, by confidence, etc.)
        """
        # Get all ADO items with vision-extracted tag
        all_items, total = self.ado_manager.list_ado(limit=1000)
        
        vision_items = [
            item for item in all_items
            if any("vision-extracted" in tag for tag in item.get("tags", []))
        ]
        
        # Group by confidence level
        by_confidence = {}
        for item in vision_items:
            for tag in item.get("tags", []):
                if "vision-extracted-" in tag:
                    confidence = tag.replace("vision-extracted-", "")
                    by_confidence[confidence] = by_confidence.get(confidence, 0) + 1
        
        # Group by type
        by_type = {}
        for item in vision_items:
            item_type = item.get("type")
            by_type[item_type] = by_type.get(item_type, 0) + 1
        
        return {
            "total_vision_items": len(vision_items),
            "by_confidence": by_confidence,
            "by_type": by_type,
            "high_confidence_percentage": (
                by_confidence.get("high", 0) / len(vision_items) * 100
                if vision_items else 0
            )
        }


# Example usage
if __name__ == "__main__":
    print("=" * 80)
    print("CORTEX Vision + ADO Integration - Example Usage")
    print("=" * 80)
    print()
    
    # Initialize integration
    integration = VisionADOIntegration()
    print("✅ Integration initialized")
    print()
    
    # Example 1: Get suggestions from UI mockup (no creation)
    print("📸 Example 1: Get Suggestions from UI Mockup")
    print("-" * 80)
    suggestions = integration.suggest_ado_fields(
        "login-mockup.png",
        ImageType.UI_MOCKUP
    )
    
    print(f"Image Type: {suggestions['image_type']}")
    print(f"Confidence: {suggestions['confidence']}")
    print(f"Suggested ADO Type: {suggestions['ado_type']}")
    print(f"Suggested Title: {suggestions['title']}")
    print(f"\nAcceptance Criteria ({len(suggestions.get('acceptance_criteria', []))}):")
    for i, ac in enumerate(suggestions.get('acceptance_criteria', []), 1):
        print(f"  {i}. {ac}")
    print(f"\nSuggested Tags: {', '.join(suggestions.get('tags', []))}")
    print()
    
    # Example 2: Analyze and create ADO from error screenshot
    print("🐛 Example 2: Create ADO from Error Screenshot")
    print("-" * 80)
    
    import random
    test_ado_num = f"ADO-{random.randint(70000, 79999)}"
    template_path = f"templates/{test_ado_num}-bug-fix.md"
    
    ado_number, result = integration.analyze_and_create_ado(
        image_path="error-screenshot.png",
        ado_number=test_ado_num,
        template_file_path=template_path,
        expected_type=ImageType.ERROR_SCREEN
    )
    
    print(f"✅ Created ADO: {ado_number}")
    print(f"Image Type: {result['image_type']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Title: {result['extracted_data']['title']}")
    print(f"Priority: {result['extracted_data'].get('priority', 'N/A')}")
    print(f"\nSuggestions:")
    for suggestion in result['suggestions'][:3]:
        print(f"  • {suggestion}")
    print()
    
    # Example 3: Batch analyze multiple screenshots
    print("📦 Example 3: Batch Analyze Multiple Screenshots")
    print("-" * 80)
    
    batch_results = integration.batch_analyze([
        "login-mockup.png",
        "error-screenshot.png",
        "ado-screenshot.png"
    ])
    
    print(f"Analyzed {len(batch_results)} screenshots:")
    for i, result in enumerate(batch_results, 1):
        print(f"\n{i}. {Path(result['image_path']).name}")
        print(f"   Type: {result.get('image_type', 'N/A')}")
        print(f"   Confidence: {result.get('confidence', 'N/A')}")
        print(f"   Title: {result.get('title', 'N/A')}")
    print()
    
    # Example 4: Get integration statistics
    print("📊 Example 4: Vision Integration Statistics")
    print("-" * 80)
    
    stats = integration.get_integration_stats()
    print(f"Total Vision-Extracted ADOs: {stats['total_vision_items']}")
    print(f"High Confidence: {stats['high_confidence_percentage']:.1f}%")
    print(f"\nBy Confidence Level:")
    for level, count in stats['by_confidence'].items():
        print(f"  {level}: {count}")
    print(f"\nBy Type:")
    for ado_type, count in stats['by_type'].items():
        print(f"  {ado_type}: {count}")
    print()
    
    print("=" * 80)
    print("✅ Integration demo complete!")
    print("=" * 80)
