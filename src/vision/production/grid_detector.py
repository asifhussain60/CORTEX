"""
Grid Detection Algorithm for UI Mockups

Uses edge detection and Hough line transform to detect grid structures in UI layouts.

Algorithm:
1. Load image and convert to grayscale
2. Apply Gaussian blur to reduce noise
3. Edge detection using Canny algorithm
4. Line detection using Hough line transform
5. Cluster lines into columns/rows
6. Calculate grid dimensions and confidence

Author: Asif Hussain
Date: December 26, 2025
"""

import cv2
import numpy as np
from typing import List, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GridStructure:
    """
    Detected grid structure in UI mockup.
    
    Attributes:
        columns: Number of columns detected
        rows: Number of rows detected
        vertical_lines: X coordinates of vertical grid lines
        horizontal_lines: Y coordinates of horizontal grid lines
        cell_width: Average cell width in pixels
        cell_height: Average cell height in pixels
        confidence: Detection confidence (0.0-1.0)
    """
    columns: int
    rows: int
    vertical_lines: List[int]
    horizontal_lines: List[int]
    cell_width: float
    cell_height: float
    confidence: float


def detect_grid(image_path: str) -> GridStructure:
    """
    Detect grid structure in UI mockup using edge detection.
    
    Algorithm:
    1. Load image and convert to grayscale
    2. Apply Gaussian blur to reduce noise
    3. Edge detection using Canny algorithm
    4. Line detection using Hough line transform
    5. Cluster lines into columns/rows
    6. Calculate grid dimensions
    
    Args:
        image_path: Path to mockup image (PNG/JPG)
        
    Returns:
        GridStructure with detected columns, rows, and confidence
        
    Example:
        >>> grid = detect_grid("mockups/dashboard.png")
        >>> print(f"Grid: {grid.columns}x{grid.rows}")
        Grid: 4x6
    """
    # Validate path
    if not Path(image_path).exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Failed to load image: {image_path}")
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    height, width = gray.shape
    
    # Preprocessing - blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Edge detection - Canny algorithm
    edges = cv2.Canny(blurred, 50, 150, apertureSize=3)
    
    # Hough line transform - detect lines in image
    lines = cv2.HoughLinesP(
        edges,
        rho=1,              # Distance resolution (pixels)
        theta=np.pi/180,    # Angle resolution (radians)
        threshold=100,      # Min votes to detect line
        minLineLength=100,  # Min line length
        maxLineGap=10       # Max gap between line segments
    )
    
    # Handle case with no lines detected
    if lines is None:
        return GridStructure(
            columns=1,
            rows=1,
            vertical_lines=[],
            horizontal_lines=[],
            cell_width=float(width),
            cell_height=float(height),
            confidence=0.0
        )
    
    # Separate vertical and horizontal lines
    vertical_lines = []
    horizontal_lines = []
    
    for line in lines:
        x1, y1, x2, y2 = line[0]
        
        # Calculate angle
        angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
        
        # Vertical line (angle close to 90°)
        if 85 <= angle <= 95:
            vertical_lines.append(x1)
        
        # Horizontal line (angle close to 0° or 180°)
        elif angle < 5 or angle > 175:
            horizontal_lines.append(y1)
    
    # Cluster lines (group nearby lines into single representative line)
    v_clusters = _cluster_lines(vertical_lines, threshold=50)
    h_clusters = _cluster_lines(horizontal_lines, threshold=50)
    
    # Calculate grid dimensions
    columns = len(v_clusters) + 1 if v_clusters else 1
    rows = len(h_clusters) + 1 if h_clusters else 1
    
    cell_width = width / columns
    cell_height = height / rows
    
    # Confidence: ratio of detected lines to expected grid lines
    expected_lines = (columns - 1) + (rows - 1)
    detected_lines = len(v_clusters) + len(h_clusters)
    confidence = min(detected_lines / max(expected_lines, 1), 1.0) if expected_lines > 0 else 0.0
    
    return GridStructure(
        columns=columns,
        rows=rows,
        vertical_lines=sorted(v_clusters),
        horizontal_lines=sorted(h_clusters),
        cell_width=cell_width,
        cell_height=cell_height,
        confidence=confidence
    )


def _cluster_lines(line_positions: List[int], threshold: int = 50) -> List[int]:
    """
    Cluster nearby lines (merge lines within threshold distance).
    
    This function groups lines that are close together, assuming they represent
    the same visual grid line. Returns the average position of each cluster.
    
    Args:
        line_positions: List of line coordinates (X or Y positions)
        threshold: Max distance between lines to merge (default: 50 pixels)
        
    Returns:
        List of cluster centers (representative line positions)
        
    Example:
        >>> positions = [100, 105, 102, 300, 305]
        >>> _cluster_lines(positions, threshold=10)
        [102, 302]  # Two clusters with average positions
    """
    if not line_positions:
        return []
    
    sorted_positions = sorted(line_positions)
    clusters = []
    current_cluster = [sorted_positions[0]]
    
    for pos in sorted_positions[1:]:
        if pos - current_cluster[-1] <= threshold:
            # Add to current cluster
            current_cluster.append(pos)
        else:
            # Finish current cluster, start new one
            clusters.append(int(np.mean(current_cluster)))
            current_cluster = [pos]
    
    # Add last cluster
    clusters.append(int(np.mean(current_cluster)))
    
    return clusters


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python grid_detector.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    try:
        grid = detect_grid(image_path)
        print(f"✅ Grid Detection Results:")
        print(f"   Columns: {grid.columns}")
        print(f"   Rows: {grid.rows}")
        print(f"   Cell Size: {grid.cell_width:.1f}x{grid.cell_height:.1f} pixels")
        print(f"   Confidence: {grid.confidence:.2%}")
        print(f"   Vertical Lines: {grid.vertical_lines}")
        print(f"   Horizontal Lines: {grid.horizontal_lines}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
