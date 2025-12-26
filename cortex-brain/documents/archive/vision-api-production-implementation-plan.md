# Vision API Production Implementation Plan

**Author:** Asif Hussain  
**Date:** December 26, 2025  
**Status:** PLANNING  
**Estimated Time:** 4-6 hours  
**Priority:** MEDIUM (Enhancement)

---

## 🎯 Executive Summary

This document outlines the production implementation of the Vision API orchestrator, transitioning from **mock mode** (architectural validation) to **production mode** (real computer vision). The implementation will enable CORTEX to analyze UI mockups using actual image processing algorithms.

**Current State:** Mock validation complete ✅  
**Target State:** Production-ready computer vision pipeline  
**Use Case:** STS validation app mockup analysis

---

## 📋 Objectives

### Primary Goals
1. Replace mock data generation with real image processing algorithms
2. Implement grid detection using computer vision techniques
3. Extract responsive breakpoints from CSS/design systems
4. Build pattern recognition for layout classification
5. Calculate complexity scores using weighted formulas
6. Validate against STS mockup images

### Success Criteria
- ✅ Analyze real PNG/JPG mockup files (not mock data)
- ✅ Detect grid columns/rows with >90% accuracy
- ✅ Extract color palettes using K-means clustering
- ✅ Identify UI elements (buttons, inputs, cards) with bounding boxes
- ✅ Classify layout patterns (centered-card, grid-with-sidebar, etc.)
- ✅ Calculate complexity scores (LOW/MEDIUM/HIGH)
- ✅ Process images in <2 seconds per mockup
- ✅ Generate actionable recommendations for developers

---

## 🏗️ Architecture

### Technology Stack

**Core Libraries:**
```
opencv-python==4.8.1.78     # Computer vision (edge detection, contours, Hough transforms)
pillow==10.1.0               # Image manipulation (resize, crop, color extraction)
numpy==1.26.2                # Numerical operations (matrices, arrays)
pytesseract==0.3.10          # OCR for text extraction (optional - for CSS detection)
scikit-learn==1.3.2          # K-means clustering for color palette extraction
```

**Optional Enhancements:**
```
tensorflow==2.15.0           # Deep learning for advanced pattern recognition
ultralytics==8.1.0           # YOLOv8 for UI element detection
easyocr==1.7.0               # Better OCR alternative to pytesseract
```

### Pipeline Architecture

```
Input: UI Mockup (PNG/JPG)
    ↓
Phase 1: Preprocessing
    ├─ Resize to standard dimensions (1920x1080)
    ├─ Convert to grayscale for edge detection
    └─ Apply Gaussian blur to reduce noise
    ↓
Phase 2: Layout Analysis
    ├─ Edge detection (Canny algorithm)
    ├─ Line detection (Hough line transform)
    ├─ Grid detection (cluster vertical/horizontal lines)
    └─ Pattern classification (rule-based or ML)
    ↓
Phase 3: Color Extraction
    ├─ K-means clustering (5-6 dominant colors)
    ├─ Color role classification (primary, secondary, accent)
    └─ Contrast ratio calculation (WCAG 2.1 AA)
    ↓
Phase 4: Element Detection
    ├─ Contour detection (find bounding boxes)
    ├─ Template matching (button, input, card shapes)
    ├─ Size/position analysis (classify element types)
    └─ Test ID generation
    ↓
Phase 5: Complexity Scoring
    ├─ Grid dimensions (columns × rows)
    ├─ Element density (elements per 1000px²)
    ├─ Nesting depth (hierarchy detection)
    └─ Weighted formula: (cols × rows × density × depth) / 100
    ↓
Phase 6: Reporting
    ├─ Generate metrics (colors, elements, layouts)
    ├─ Create recommendations (accessibility, testing)
    └─ Export results (JSON, Markdown)
    ↓
Output: VisionAPIMetrics + Recommendations
```

---

## 🧪 Implementation Tasks

### Task 1: Environment Setup (30 minutes)

**Dependencies Installation:**
```bash
# Required packages
pip install opencv-python==4.8.1.78
pip install pillow==10.1.0
pip install numpy==1.26.2
pip install scikit-learn==1.3.2

# Optional (OCR for CSS extraction)
pip install pytesseract==0.3.10
brew install tesseract  # macOS only
```

**Validation:**
```python
import cv2
import PIL
import numpy as np
from sklearn.cluster import KMeans
print("✅ All dependencies installed")
```

**Files to Create:**
- `requirements-vision-api.txt` - Pinned versions
- `src/vision/` - New package for vision utilities

---

### Task 2: Grid Detection Algorithm (1.5 hours)

**Algorithm:** Edge Detection + Hough Line Transform + Line Clustering

**Implementation:**
```python
# File: src/vision/grid_detector.py

import cv2
import numpy as np
from typing import Tuple, List
from dataclasses import dataclass

@dataclass
class GridStructure:
    columns: int
    rows: int
    vertical_lines: List[int]      # X coordinates
    horizontal_lines: List[int]    # Y coordinates
    cell_width: float
    cell_height: float
    confidence: float              # 0.0-1.0

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
        image_path: Path to mockup image
        
    Returns:
        GridStructure with detected columns/rows
    """
    # Load image
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    height, width = gray.shape
    
    # Preprocessing
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Edge detection
    edges = cv2.Canny(blurred, 50, 150, apertureSize=3)
    
    # Hough line transform (detect lines)
    lines = cv2.HoughLinesP(
        edges,
        rho=1,              # Distance resolution (pixels)
        theta=np.pi/180,    # Angle resolution (radians)
        threshold=100,      # Min votes to detect line
        minLineLength=100,  # Min line length
        maxLineGap=10       # Max gap between line segments
    )
    
    if lines is None:
        return GridStructure(1, 1, [], [], width, height, 0.0)
    
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
    
    # Cluster lines (group nearby lines)
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
    confidence = min(detected_lines / max(expected_lines, 1), 1.0)
    
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
    
    Args:
        line_positions: List of line coordinates (X or Y)
        threshold: Max distance between lines to merge
        
    Returns:
        List of cluster centers (representative line positions)
    """
    if not line_positions:
        return []
    
    sorted_positions = sorted(line_positions)
    clusters = []
    current_cluster = [sorted_positions[0]]
    
    for pos in sorted_positions[1:]:
        if pos - current_cluster[-1] <= threshold:
            current_cluster.append(pos)
        else:
            # Finish current cluster, start new one
            clusters.append(int(np.mean(current_cluster)))
            current_cluster = [pos]
    
    # Add last cluster
    clusters.append(int(np.mean(current_cluster)))
    
    return clusters
```

**Test Cases:**
```python
# File: tests/vision/test_grid_detector.py

def test_simple_grid_2x2():
    """Test 2x2 grid detection"""
    result = detect_grid("mockups/grid-2x2.png")
    assert result.columns == 2
    assert result.rows == 2
    assert result.confidence > 0.8

def test_complex_grid_4x6():
    """Test 4x6 dashboard grid"""
    result = detect_grid("mockups/dashboard.png")
    assert result.columns == 4
    assert result.rows == 6
    assert len(result.vertical_lines) == 3
    assert len(result.horizontal_lines) == 5

def test_single_centered_card():
    """Test centered card (1x1 grid)"""
    result = detect_grid("mockups/login-screen.png")
    assert result.columns == 1
    assert result.rows == 1
```

---

### Task 3: Color Palette Extraction (1 hour)

**Algorithm:** K-means Clustering + Color Role Classification

**Implementation:**
```python
# File: src/vision/color_extractor.py

import cv2
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from typing import List, Tuple
from dataclasses import dataclass

@dataclass
class ColorInfo:
    hex: str
    rgb: Tuple[int, int, int]
    role: str               # primary, secondary, accent, neutral, text
    percentage: float       # % of image pixels
    wcag_contrast: float    # Contrast ratio vs white

def extract_color_palette(image_path: str, n_colors: int = 6) -> List[ColorInfo]:
    """
    Extract dominant color palette using K-means clustering.
    
    Args:
        image_path: Path to mockup image
        n_colors: Number of colors to extract (default: 6)
        
    Returns:
        List of ColorInfo objects (sorted by percentage descending)
    """
    # Load image
    img = Image.open(image_path)
    img = img.convert('RGB')
    
    # Resize for performance (K-means on full image is slow)
    img_small = img.resize((150, 150))
    
    # Convert to numpy array and reshape to 2D (pixels × RGB)
    pixels = np.array(img_small).reshape(-1, 3)
    
    # K-means clustering
    kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
    kmeans.fit(pixels)
    
    # Get cluster centers (dominant colors)
    colors = kmeans.cluster_centers_.astype(int)
    
    # Calculate percentage of pixels for each color
    labels = kmeans.labels_
    percentages = np.bincount(labels) / len(labels) * 100
    
    # Sort by percentage (descending)
    sorted_indices = np.argsort(percentages)[::-1]
    
    # Build ColorInfo objects
    palette = []
    for i in sorted_indices:
        rgb = tuple(colors[i])
        hex_color = '#%02x%02x%02x' % rgb
        role = _classify_color_role(rgb, i)
        contrast = _calculate_contrast(rgb, (255, 255, 255))
        
        palette.append(ColorInfo(
            hex=hex_color,
            rgb=rgb,
            role=role,
            percentage=percentages[i],
            wcag_contrast=contrast
        ))
    
    return palette

def _classify_color_role(rgb: Tuple[int, int, int], rank: int) -> str:
    """
    Classify color role based on RGB values and dominance rank.
    
    Heuristics:
    - rank 0 (most dominant) → primary or neutral
    - Dark colors (low brightness) → text or neutral
    - Saturated colors → accent
    - Light colors → secondary or neutral
    """
    r, g, b = rgb
    
    # Calculate brightness (0-255)
    brightness = (r + g + b) / 3
    
    # Calculate saturation (distance from grayscale)
    avg = brightness
    saturation = max(abs(r - avg), abs(g - avg), abs(b - avg))
    
    # Most dominant color
    if rank == 0:
        return 'primary' if saturation > 30 else 'neutral'
    
    # Dark colors
    if brightness < 60:
        return 'text'
    
    # Saturated colors
    if saturation > 50:
        return 'accent'
    
    # Light colors
    if brightness > 200:
        return 'secondary'
    
    return 'neutral'

def _calculate_contrast(rgb1: Tuple[int, int, int], rgb2: Tuple[int, int, int]) -> float:
    """
    Calculate WCAG 2.1 contrast ratio between two colors.
    
    Formula: (L1 + 0.05) / (L2 + 0.05)
    Where L = relative luminance (0.0 - 1.0)
    
    Returns:
        Contrast ratio (1.0 - 21.0)
        WCAG AA requires ≥4.5:1 for normal text
    """
    def _relative_luminance(rgb):
        r, g, b = [x / 255.0 for x in rgb]
        
        # sRGB to linear RGB
        r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
        g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
        b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
        
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    L1 = _relative_luminance(rgb1)
    L2 = _relative_luminance(rgb2)
    
    lighter = max(L1, L2)
    darker = min(L1, L2)
    
    return (lighter + 0.05) / (darker + 0.05)
```

---

### Task 4: Element Detection (1.5 hours)

**Algorithm:** Contour Detection + Template Matching + Size/Position Analysis

**Implementation:**
```python
# File: src/vision/element_detector.py

import cv2
import numpy as np
from typing import List, Tuple
from dataclasses import dataclass

@dataclass
class UIElement:
    type: str               # button, input, card, image, etc.
    bounding_box: Tuple[int, int, int, int]  # (x, y, width, height)
    test_id: str           # Generated test ID
    confidence: float      # 0.0-1.0

def detect_elements(image_path: str) -> List[UIElement]:
    """
    Detect UI elements using contour detection and shape analysis.
    
    Algorithm:
    1. Preprocess image (grayscale, blur, threshold)
    2. Find contours (connected regions)
    3. Filter by size (remove noise)
    4. Classify by shape/aspect ratio
    5. Generate test IDs
    
    Args:
        image_path: Path to mockup image
        
    Returns:
        List of detected UI elements
    """
    # Load image
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Preprocessing
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Threshold (binary image - white elements on black background)
    _, thresh = cv2.threshold(blurred, 240, 255, cv2.THRESH_BINARY_INV)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    elements = []
    element_counts = {}  # Track counts for test ID generation
    
    for contour in contours:
        # Get bounding box
        x, y, w, h = cv2.boundingRect(contour)
        
        # Filter by size (remove noise - too small or too large)
        area = w * h
        if area < 1000 or area > img.shape[0] * img.shape[1] * 0.5:
            continue
        
        # Classify element by shape
        element_type = _classify_element(w, h, area)
        
        # Generate test ID
        element_counts[element_type] = element_counts.get(element_type, 0) + 1
        test_id = f"{element_type}-{element_counts[element_type]}"
        
        # Confidence based on contour properties
        perimeter = cv2.arcLength(contour, True)
        circularity = 4 * np.pi * area / (perimeter ** 2) if perimeter > 0 else 0
        confidence = min(circularity, 1.0)
        
        elements.append(UIElement(
            type=element_type,
            bounding_box=(x, y, w, h),
            test_id=test_id,
            confidence=confidence
        ))
    
    return elements

def _classify_element(width: int, height: int, area: int) -> str:
    """
    Classify UI element type based on dimensions.
    
    Heuristics:
    - Small square/rectangle (100-300px width) → button
    - Wide rectangle (>500px width, thin) → input
    - Large rectangle (>10k area) → card
    - Square (aspect ratio ~1:1) → image/icon
    """
    aspect_ratio = width / height if height > 0 else 1
    
    # Button: small, roughly rectangular
    if 100 <= width <= 300 and 0.3 <= aspect_ratio <= 3:
        return 'button'
    
    # Input: wide, thin
    if width > 300 and aspect_ratio > 4:
        return 'input'
    
    # Card: large rectangle
    if area > 50000:
        return 'card'
    
    # Image/Icon: square-ish
    if 0.8 <= aspect_ratio <= 1.2:
        return 'image'
    
    # Default
    return 'container'
```

---

### Task 5: Pattern Recognition (1 hour)

**Algorithm:** Rule-Based Classification (can be replaced with ML later)

**Implementation:**
```python
# File: src/vision/pattern_classifier.py

from dataclasses import dataclass
from typing import List
from .grid_detector import GridStructure
from .element_detector import UIElement

@dataclass
class LayoutPattern:
    pattern_type: str       # centered-card, grid-with-sidebar, responsive-grid, multi-column
    complexity: str         # LOW, MEDIUM, HIGH
    description: str
    confidence: float       # 0.0-1.0

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
        LayoutPattern with classification
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
        cell_size_variance = np.std([e.bounding_box[2] * e.bounding_box[3] for e in elements])
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
```

---

### Task 6: Complexity Scoring (30 minutes)

**Algorithm:** Weighted Formula

**Implementation:**
```python
# File: src/vision/complexity_scorer.py

from dataclasses import dataclass
from typing import List
from .grid_detector import GridStructure
from .element_detector import UIElement

@dataclass
class ComplexityScore:
    score: int              # 0-100
    level: str              # LOW, MEDIUM, HIGH
    factors: dict           # Breakdown of contributing factors

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
        grid_factor +
        density_factor +
        nesting_factor +
        variety_factor
    ) / 4
    
    Args:
        grid: Detected grid structure
        elements: Detected UI elements
        image_width: Mockup width
        image_height: Mockup height
        
    Returns:
        ComplexityScore with 0-100 score
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
    element_types = len(set(e.type for e in elements))
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
    """
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
```

---

### Task 7: Integration with Orchestrator (1 hour)

**Update Vision API Orchestrator to Use Production Mode:**

```python
# File: src/operations/modules/orchestration/vision_api_validation_orchestrator.py

# Add mode parameter
class VisionAPIValidationOrchestrator:
    def __init__(self, mode: str = 'mock', logger=None):
        """
        Args:
            mode: 'mock' (simulated) or 'production' (real CV)
        """
        self.mode = mode
        ...
    
    def _analyze_phase(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 3: Analyze mockups"""
        
        if self.mode == 'production':
            # Use real computer vision
            from src.vision.grid_detector import detect_grid
            from src.vision.color_extractor import extract_color_palette
            from src.vision.element_detector import detect_elements
            from src.vision.pattern_classifier import classify_layout_pattern
            from src.vision.complexity_scorer import calculate_complexity
            
            for mockup_path in context['mockup_files']:
                # Real analysis
                grid = detect_grid(mockup_path)
                colors = extract_color_palette(mockup_path)
                elements = detect_elements(mockup_path)
                pattern = classify_layout_pattern(grid, elements, 1920, 1080)
                complexity = calculate_complexity(grid, elements, 1920, 1080)
                ...
        else:
            # Use mock data (current implementation)
            ...
```

---

## 🧪 Testing Strategy

### Unit Tests (Per Algorithm)
```python
# tests/vision/test_grid_detector.py
# tests/vision/test_color_extractor.py
# tests/vision/test_element_detector.py
# tests/vision/test_pattern_classifier.py
# tests/vision/test_complexity_scorer.py
```

### Integration Tests (Full Pipeline)
```python
# tests/integration/test_vision_pipeline.py

def test_login_screen_analysis():
    """Test full pipeline on STS login screen"""
    result = analyze_mockup(
        "cortex-sample-apps/sts-validation-app/mockups/login-screen.png"
    )
    
    assert result.grid.columns == 1
    assert result.grid.rows == 1
    assert len(result.colors) == 5-6
    assert len(result.elements) >= 5  # Email, password, button, etc.
    assert result.pattern.pattern_type == 'centered-card'
    assert result.complexity.level == 'LOW'

def test_dashboard_analysis():
    """Test complex dashboard mockup"""
    result = analyze_mockup(
        "cortex-sample-apps/sts-validation-app/mockups/dashboard.png"
    )
    
    assert result.grid.columns >= 3
    assert result.grid.rows >= 3
    assert len(result.elements) >= 20
    assert result.pattern.pattern_type in ['grid-with-sidebar', 'responsive-grid']
    assert result.complexity.level in ['MEDIUM', 'HIGH']
```

### Performance Benchmarks
- **Target:** <2 seconds per mockup (1920x1080)
- **Memory:** <500MB peak usage
- **Accuracy:** >90% for grid detection, >85% for element detection

---

## 📊 Acceptance Criteria

### Functional Requirements
- ✅ Analyze PNG/JPG mockup files (not mock data)
- ✅ Detect grid structure (columns, rows, lines)
- ✅ Extract color palette (5-6 dominant colors with roles)
- ✅ Detect UI elements (buttons, inputs, cards with bounding boxes)
- ✅ Classify layout patterns (4 types: centered-card, grid-with-sidebar, responsive-grid, multi-column)
- ✅ Calculate complexity score (LOW/MEDIUM/HIGH)
- ✅ Generate actionable recommendations

### Non-Functional Requirements
- ✅ Performance: <2s per mockup
- ✅ Accuracy: >85% for all detection algorithms
- ✅ Error handling: Graceful degradation if image invalid
- ✅ Logging: Detailed phase transitions (🎭 pattern)
- ✅ Documentation: Inline comments, docstrings, examples

### Quality Requirements
- ✅ Unit tests: >90% coverage for vision utilities
- ✅ Integration tests: End-to-end pipeline validation
- ✅ Regression tests: Baseline against STS mockups
- ✅ Performance tests: Benchmarks for large images

---

## 🚀 Deployment Plan

### Phase 1: Development (4 hours)
1. Install dependencies (30 min)
2. Implement grid detection (1.5h)
3. Implement color extraction (1h)
4. Implement element detection (1.5h)
5. Implement pattern recognition (1h)
6. Implement complexity scoring (30 min)
7. Integration with orchestrator (1h)

### Phase 2: Testing (1 hour)
1. Unit tests for each algorithm (30 min)
2. Integration tests (20 min)
3. Performance benchmarks (10 min)

### Phase 3: Validation (1 hour)
1. Test against STS mockups (30 min)
2. Compare mock vs production results (15 min)
3. Update documentation (15 min)

### Total Time: 6 hours

---

## 🔄 Rollback Plan

**If production mode has issues:**
1. Revert to mock mode: `VisionAPIValidationOrchestrator(mode='mock')`
2. Architecture validation already complete ✅
3. No impact on other STS capabilities

---

## 📚 References

**Computer Vision:**
- OpenCV Documentation: https://docs.opencv.org/
- Canny Edge Detection: https://docs.opencv.org/4.x/da/d22/tutorial_py_canny.html
- Hough Line Transform: https://docs.opencv.org/4.x/d9/db0/tutorial_hough_lines.html

**Color Theory:**
- K-means Clustering: https://scikit-learn.org/stable/modules/clustering.html#k-means
- WCAG Contrast: https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html

**UI Pattern Recognition:**
- Material Design Grid: https://material.io/design/layout/responsive-layout-grid.html
- Bootstrap Grid System: https://getbootstrap.com/docs/5.3/layout/grid/

---

## ✅ Next Steps

1. **Review and approve this plan** (15 minutes)
2. **Install dependencies** → Task 2
3. **Begin implementation** → Tasks 3-7
4. **Validate against STS mockups** → Task 8
5. **Update STS validation** → Task 9

**Decision Required:** Proceed with implementation (6h) or defer to backlog?
