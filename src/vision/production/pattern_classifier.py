"""
Layout Pattern Classification

Classifies UI mockup layouts into common patterns using rule-based heuristics.

Patterns:
- centered-card: Single centered element (login, signup)
- grid-with-sidebar: Sidebar navigation + grid content
- responsive-grid: Uniform grid layout (products, gallery)
- multi-column: 2-3 columns with mixed content

Author: Asif Hussain
Date: December 26, 2025
"""

import numpy as np
from dataclasses import dataclass
from typing import List

# Import from sibling modules
from .grid_detector import GridStructure
from .element_detector import UIElement


@dataclass
class LayoutPattern:
    """
    Classified layout pattern with metadata.
    
    Attributes:
        pattern_type: Pattern name (centered-card, grid-with-sidebar, etc.)
        complexity: Complexity level (LOW, MEDIUM, HIGH)
        description: Human-readable description
        confidence: Classification confidence (0.0-1.0)
    """
    pattern_type: str
    complexity: str
    description: str
    confidence: float


def classify_layout_pattern(
    grid: GridStructure,
    elements: List[UIElement],
    image_width: int,
    image_height: int
) -> LayoutPattern:
    """
    Classify layout pattern based on grid structure and elements.
    
    Patterns:
    - centered-card: 1x1 grid, single centered element
    - grid-with-sidebar: Vertical bar on left/right + grid
    - responsive-grid: NxN uniform grid
    - multi-column: 2-3 columns with different content types
    
    Args:
        grid: Detected grid structure
        elements: Detected UI elements
        image_width: Mockup width in pixels
        image_height: Mockup height in pixels
        
    Returns:
        LayoutPattern with classification and confidence
        
    Example:
        >>> pattern = classify_layout_pattern(grid, elements, 1920, 1080)
        >>> print(f"{pattern.pattern_type} ({pattern.complexity})")
        grid-with-sidebar (HIGH)
    """
    # Calculate complexity
    complexity_score = (grid.columns * grid.rows * len(elements)) / 10
    
    if complexity_score < 10:
        complexity = 'LOW'
    elif complexity_score < 50:
        complexity = 'MEDIUM'
    else:
        complexity = 'HIGH'
    
    # Classify pattern (rule-based)
    
    # Pattern 1: Centered Card
    if grid.columns == 1 and grid.rows == 1 and len(elements) < 10:
        return LayoutPattern(
            pattern_type='centered-card',
            complexity='LOW',
            description='Single centered card with vertical form layout',
            confidence=0.95
        )
    
    # Pattern 2: Grid with Sidebar
    # Heuristic: First column is narrow (sidebar), rest is grid
    if grid.columns >= 3 and grid.cell_width < image_width / 6:
        return LayoutPattern(
            pattern_type='grid-with-sidebar',
            complexity='HIGH',
            description='Left sidebar navigation with multi-column grid',
            confidence=0.85
        )
    
    # Pattern 3: Responsive Grid (uniform cells)
    if grid.columns >= 3 and grid.rows >= 3:
        # Check if cells are roughly equal size (uniform grid)
        if elements:
            element_areas = [e.bounding_box[2] * e.bounding_box[3] for e in elements]
            cell_size_variance = np.std(element_areas)
            
            if cell_size_variance < 10000:  # Low variance = uniform
                return LayoutPattern(
                    pattern_type='responsive-grid',
                    complexity=complexity,
                    description=f'{grid.columns}x{grid.rows} uniform grid layout',
                    confidence=0.90
                )
    
    # Pattern 4: Multi-Column (2-3 columns, different content types)
    if 2 <= grid.columns <= 3:
        return LayoutPattern(
            pattern_type='multi-column',
            complexity=complexity,
            description=f'{grid.columns}-column layout with mixed content',
            confidence=0.80
        )
    
    # Default: Unknown pattern
    return LayoutPattern(
        pattern_type='custom',
        complexity=complexity,
        description='Custom layout pattern (not classified)',
        confidence=0.50
    )


# Example usage
if __name__ == "__main__":
    import sys
    from .grid_detector import detect_grid
    from .element_detector import detect_elements
    
    if len(sys.argv) < 2:
        print("Usage: python pattern_classifier.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    try:
        # Detect grid and elements
        grid = detect_grid(image_path)
        elements = detect_elements(image_path)
        
        # Classify pattern
        # Assume standard dimensions (can be extracted from image)
        pattern = classify_layout_pattern(grid, elements, 1920, 1080)
        
        print(f"✅ Layout Pattern Classification:")
        print(f"   Pattern: {pattern.pattern_type}")
        print(f"   Complexity: {pattern.complexity}")
        print(f"   Description: {pattern.description}")
        print(f"   Confidence: {pattern.confidence:.2%}")
        print()
        print(f"   Grid: {grid.columns}x{grid.rows}")
        print(f"   Elements: {len(elements)}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
