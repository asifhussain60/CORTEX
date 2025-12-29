"""
Complexity Scoring Algorithm

Calculates layout complexity using weighted formula combining multiple factors.

Factors:
- Grid dimensions (columns × rows)
- Element density (elements per 1000px²)
- Nesting depth (hierarchy levels)
- Element variety (number of different types)

Author: Asif Hussain
Date: December 26, 2025
"""

from dataclasses import dataclass
from typing import List, Dict

# Import from sibling modules
from .grid_detector import GridStructure
from .element_detector import UIElement


@dataclass
class ComplexityScore:
    """
    Layout complexity score with factor breakdown.
    
    Attributes:
        score: Overall complexity score (0-100)
        level: Complexity level (LOW, MEDIUM, HIGH)
        factors: Dictionary of contributing factors
    """
    score: int
    level: str
    factors: Dict[str, float]


def calculate_complexity(
    grid: GridStructure,
    elements: List[UIElement],
    image_width: int,
    image_height: int
) -> ComplexityScore:
    """
    Calculate layout complexity using weighted formula.
    
    Formula:
    complexity = (
        grid_factor * 0.3 +
        density_factor * 0.3 +
        nesting_factor * 0.2 +
        variety_factor * 0.2
    )
    
    Args:
        grid: Detected grid structure
        elements: Detected UI elements
        image_width: Mockup width in pixels
        image_height: Mockup height in pixels
        
    Returns:
        ComplexityScore with 0-100 score and factor breakdown
        
    Example:
        >>> score = calculate_complexity(grid, elements, 1920, 1080)
        >>> print(f"Complexity: {score.level} ({score.score}/100)")
        Complexity: MEDIUM (45/100)
    """
    # Factor 1: Grid dimensions (0-100)
    grid_factor = min((grid.columns * grid.rows) * 2, 100)
    
    # Factor 2: Element density (0-100)
    # Elements per 1000px²
    area = image_width * image_height
    density = len(elements) / (area / 1000000) * 10
    density_factor = min(density, 100)
    
    # Factor 3: Nesting depth (0-100)
    # Estimate based on element overlaps
    nesting_depth = _estimate_nesting_depth(elements)
    nesting_factor = min(nesting_depth * 20, 100)
    
    # Factor 4: Element variety (0-100)
    # More element types = more complex
    element_types = len(set(e.type for e in elements)) if elements else 1
    variety_factor = min(element_types * 15, 100)
    
    # Weighted average
    score = int((
        grid_factor * 0.3 +
        density_factor * 0.3 +
        nesting_factor * 0.2 +
        variety_factor * 0.2
    ))
    
    # Classify level
    if score < 30:
        level = 'LOW'
    elif score < 60:
        level = 'MEDIUM'
    else:
        level = 'HIGH'
    
    return ComplexityScore(
        score=score,
        level=level,
        factors={
            'grid': grid_factor,
            'density': density_factor,
            'nesting': nesting_factor,
            'variety': variety_factor
        }
    )


def _estimate_nesting_depth(elements: List[UIElement]) -> int:
    """
    Estimate UI nesting depth based on element containment.
    
    Heuristic: Count how many elements are fully contained within others.
    Higher nesting = more complex hierarchy.
    
    Args:
        elements: List of detected UI elements
        
    Returns:
        Maximum nesting depth (1 = flat, 5+ = deeply nested)
    """
    if not elements:
        return 1
    
    max_depth = 1
    
    for i, elem1 in enumerate(elements):
        depth = 1
        x1, y1, w1, h1 = elem1.bounding_box
        
        for elem2 in elements[:i] + elements[i+1:]:
            x2, y2, w2, h2 = elem2.bounding_box
            
            # Check if elem1 is fully contained in elem2
            if (x2 <= x1 and y2 <= y1 and
                x2 + w2 >= x1 + w1 and y2 + h2 >= y1 + h1):
                depth += 1
        
        max_depth = max(max_depth, depth)
    
    return max_depth


# Example usage
if __name__ == "__main__":
    import sys
    from .grid_detector import detect_grid
    from .element_detector import detect_elements
    
    if len(sys.argv) < 2:
        print("Usage: python complexity_scorer.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    try:
        # Detect grid and elements
        grid = detect_grid(image_path)
        elements = detect_elements(image_path)
        
        # Calculate complexity
        score = calculate_complexity(grid, elements, 1920, 1080)
        
        print(f"✅ Complexity Score Results:")
        print(f"   Overall: {score.score}/100 ({score.level})")
        print()
        print(f"   Factor Breakdown:")
        print(f"      Grid: {score.factors['grid']:.1f}/100")
        print(f"      Density: {score.factors['density']:.1f}/100")
        print(f"      Nesting: {score.factors['nesting']:.1f}/100")
        print(f"      Variety: {score.factors['variety']:.1f}/100")
        print()
        print(f"   Grid: {grid.columns}x{grid.rows}")
        print(f"   Elements: {len(elements)}")
        
        # Complexity interpretation
        if score.level == 'LOW':
            print(f"\n   💡 Simple layout - easy to implement and test")
        elif score.level == 'MEDIUM':
            print(f"\n   💡 Moderate complexity - consider component breakdown")
        else:
            print(f"\n   💡 High complexity - requires careful architecture")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
