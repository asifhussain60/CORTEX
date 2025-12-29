# Phase 13B Capability 9: Vision API / Screenshot Analysis Validation Plan

**Capability:** Vision API - UI Mockup Analysis & Requirements Extraction  
**Status:** ⏳ READY FOR VALIDATION  
**Date:** December 26, 2025  
**Duration:** 5 hours estimated

---

## 🎯 Validation Objective

Validate Vision API's ability to analyze UI mockups and extract actionable requirements:

1. **Color Palette Extraction:** Extract 4-6 dominant colors per mockup
2. **Element Detection:** Identify UI components (buttons, forms, navigation)
3. **Layout Analysis:** Detect layout patterns (grid, flex, absolute)
4. **Test ID Suggestions:** Generate data-testid attributes for testing
5. **Accessibility Checks:** Identify WCAG 2.1 violations
6. **Requirements Extraction:** Generate user stories from visual designs

**Target:** 4/4 mockups analyzed, <500 tokens/image, <2s/analysis, 100% accuracy

---

## 📊 Input: UI Mockups (4 Designs)

### Mockup Set

| Mockup | Description | Elements | Complexity |
|--------|-------------|----------|------------|
| **login-screen.png** | Login form with branding | 8 elements | LOW |
| **dashboard.png** | Analytics dashboard | 24 elements | HIGH |
| **product-grid.png** | E-commerce product listing | 16 elements | MEDIUM |
| **checkout-flow.png** | Multi-step checkout | 20 elements | HIGH |

**Total:** 4 mockups, 68 UI elements, 3 complexity levels

---

### Expected Analysis Results

| Analysis Type | Expected Output | Validation |
|---------------|-----------------|------------|
| **Color Palette** | 18-24 colors total (4-6 per mockup) | RGB/Hex accuracy |
| **Elements** | 68 detected (buttons, inputs, cards, etc.) | Component classification |
| **Layouts** | 4 patterns (grid, flex, split, multi-step) | Layout type accuracy |
| **Test IDs** | 68 generated (kebab-case naming) | Naming convention |
| **Accessibility** | 12 violations (contrast, alt text, labels) | WCAG 2.1 compliance |
| **Requirements** | 16 user stories (4 per mockup) | Acceptance criteria quality |

---

## 🔍 Analysis Algorithms

### 1. Color Palette Extraction

**Algorithm:** K-means clustering with perceptual color space

```python
import cv2
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image

def extract_color_palette(image_path, num_colors=6):
    """
    Extract dominant color palette using K-means clustering.
    
    Args:
        image_path: Path to UI mockup image
        num_colors: Number of dominant colors to extract
    
    Returns:
        Color palette with RGB/Hex values and usage percentages
    """
    
    # Load image
    image = Image.open(image_path)
    image_rgb = image.convert('RGB')
    
    # Resize for faster processing (maintain aspect ratio)
    max_dimension = 800
    image_rgb.thumbnail((max_dimension, max_dimension))
    
    # Convert to numpy array
    pixels = np.array(image_rgb)
    pixels = pixels.reshape(-1, 3)
    
    # Remove extreme values (pure white/black often from artifacts)
    # Keep pixels where R,G,B are in [10, 245] range
    valid_pixels = pixels[
        (pixels[:, 0] > 10) & (pixels[:, 0] < 245) &
        (pixels[:, 1] > 10) & (pixels[:, 1] < 245) &
        (pixels[:, 2] > 10) & (pixels[:, 2] < 245)
    ]
    
    # Apply K-means clustering
    kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
    kmeans.fit(valid_pixels)
    
    # Get cluster centers (dominant colors)
    colors = kmeans.cluster_centers_.astype(int)
    
    # Calculate color usage percentages
    labels = kmeans.labels_
    counts = np.bincount(labels)
    percentages = (counts / len(labels)) * 100
    
    # Sort by usage (most common first)
    sorted_indices = np.argsort(percentages)[::-1]
    colors = colors[sorted_indices]
    percentages = percentages[sorted_indices]
    
    # Build palette
    palette = []
    for i, (color, percentage) in enumerate(zip(colors, percentages)):
        r, g, b = color
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        
        # Classify color role
        role = classify_color_role(color, i)
        
        palette.append({
            'index': i + 1,
            'rgb': f"rgb({r}, {g}, {b})",
            'hex': hex_color,
            'percentage': round(percentage, 2),
            'role': role,
            'css_var': f"--color-{role.lower().replace(' ', '-')}"
        })
    
    return {
        'palette': palette,
        'count': len(palette),
        'dominant_color': palette[0],
        'suggestions': generate_color_suggestions(palette)
    }


def classify_color_role(rgb, index):
    """Classify color based on hue/saturation/value."""
    
    r, g, b = rgb
    
    # Convert to HSV
    hsv = cv2.cvtColor(np.uint8([[rgb]]), cv2.COLOR_RGB2HSV)[0][0]
    h, s, v = hsv
    
    # Primary/Brand color (first, high saturation)
    if index == 0 and s > 100:
        return "Primary"
    
    # Accent color (high saturation, not first)
    if s > 150:
        return "Accent"
    
    # Background (low saturation, high value)
    if s < 30 and v > 200:
        return "Background"
    
    # Text (low saturation, low value)
    if s < 30 and v < 100:
        return "Text"
    
    # Neutral
    if s < 50:
        return "Neutral"
    
    return "Secondary"


def generate_color_suggestions(palette):
    """Generate accessibility and design suggestions."""
    
    suggestions = []
    
    # Check contrast ratios
    bg_colors = [c for c in palette if c['role'] in ['Background', 'Neutral']]
    text_colors = [c for c in palette if c['role'] == 'Text']
    
    for bg in bg_colors:
        for text in text_colors:
            contrast = calculate_contrast_ratio(bg['rgb'], text['rgb'])
            if contrast < 4.5:  # WCAG AA standard
                suggestions.append({
                    'issue': 'Low contrast ratio',
                    'background': bg['hex'],
                    'text': text['hex'],
                    'contrast_ratio': contrast,
                    'recommendation': 'Increase contrast to 4.5:1 minimum (WCAG AA)',
                    'severity': 'HIGH'
                })
    
    # Check for sufficient color variety
    if len(palette) < 4:
        suggestions.append({
            'issue': 'Limited color palette',
            'recommendation': 'Consider adding more neutral colors for hierarchy',
            'severity': 'MEDIUM'
        })
    
    return suggestions
```

**Expected Results for login-screen.png:**
```json
{
  "palette": [
    {"index": 1, "hex": "#2563eb", "rgb": "rgb(37, 99, 235)", "percentage": 28.5, "role": "Primary", "css_var": "--color-primary"},
    {"index": 2, "hex": "#f8fafc", "rgb": "rgb(248, 250, 252)", "percentage": 45.2, "role": "Background", "css_var": "--color-background"},
    {"index": 3, "hex": "#1e293b", "rgb": "rgb(30, 41, 59)", "percentage": 12.3, "role": "Text", "css_var": "--color-text"},
    {"index": 4, "hex": "#64748b", "rgb": "rgb(100, 116, 139)", "percentage": 8.7, "role": "Neutral", "css_var": "--color-neutral"},
    {"index": 5, "hex": "#10b981", "rgb": "rgb(16, 185, 129)", "percentage": 3.8, "role": "Accent", "css_var": "--color-accent"},
    {"index": 6, "hex": "#ef4444", "rgb": "rgb(239, 68, 68)", "percentage": 1.5, "role": "Accent", "css_var": "--color-accent-2"}
  ],
  "suggestions": [
    {
      "issue": "Low contrast ratio",
      "background": "#f8fafc",
      "text": "#64748b",
      "contrast_ratio": 3.2,
      "recommendation": "Increase contrast to 4.5:1 minimum (WCAG AA)",
      "severity": "HIGH"
    }
  ]
}
```

---

### 2. Element Detection

**Algorithm:** Template matching + OCR + Geometric analysis

```python
import pytesseract
import cv2
from ultralytics import YOLO  # Optional: Use pre-trained UI component model

def detect_ui_elements(image_path):
    """
    Detect UI components using computer vision + OCR.
    
    Returns:
        List of detected UI elements with types, positions, and properties
    """
    
    # Load image
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    elements = []
    
    # Step 1: Detect text elements (labels, headings, paragraphs)
    text_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    
    for i in range(len(text_data['text'])):
        if int(text_data['conf'][i]) > 60:  # Confidence threshold
            text = text_data['text'][i].strip()
            if text:
                x, y, w, h = (
                    text_data['left'][i],
                    text_data['top'][i],
                    text_data['width'][i],
                    text_data['height'][i]
                )
                
                # Classify text type
                element_type = classify_text_element(text, h)
                
                elements.append({
                    'type': element_type,
                    'text': text,
                    'bbox': {'x': x, 'y': y, 'width': w, 'height': h},
                    'confidence': text_data['conf'][i]
                })
    
    # Step 2: Detect interactive elements (buttons, inputs)
    # Use edge detection + contour analysis
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        
        # Filter by size (ignore very small/large elements)
        if 20 < w < 400 and 15 < h < 100:
            aspect_ratio = w / h
            
            # Button detection (rectangular, moderate aspect ratio)
            if 1.5 < aspect_ratio < 8 and 30 < h < 60:
                elements.append({
                    'type': 'button',
                    'text': extract_text_from_region(image, x, y, w, h),
                    'bbox': {'x': x, 'y': y, 'width': w, 'height': h},
                    'confidence': 85
                })
            
            # Input field detection (rectangular, wide aspect ratio)
            elif aspect_ratio > 4 and 25 < h < 50:
                elements.append({
                    'type': 'input',
                    'placeholder': extract_text_from_region(image, x, y, w, h),
                    'bbox': {'x': x, 'y': y, 'width': w, 'height': h},
                    'confidence': 80
                })
    
    # Step 3: Detect structural elements (cards, panels, sections)
    # Use YOLO or template matching for common UI patterns
    structural_elements = detect_structural_elements(image)
    elements.extend(structural_elements)
    
    # Step 4: Group elements into hierarchies
    grouped_elements = build_element_hierarchy(elements, image.shape)
    
    return {
        'elements': grouped_elements,
        'count': len(grouped_elements),
        'by_type': count_by_type(grouped_elements),
        'layout': infer_layout_pattern(grouped_elements, image.shape)
    }


def classify_text_element(text, height):
    """Classify text element based on content and size."""
    
    if height > 30:
        return 'heading'
    elif len(text) > 50:
        return 'paragraph'
    elif ':' in text or 'label' in text.lower():
        return 'label'
    else:
        return 'text'


def build_element_hierarchy(elements, image_shape):
    """Group elements into parent-child relationships."""
    
    height, width = image_shape[:2]
    
    # Sort by Y-coordinate (top to bottom)
    elements.sort(key=lambda e: e['bbox']['y'])
    
    hierarchy = []
    current_group = None
    
    for element in elements:
        bbox = element['bbox']
        
        # Start new group if element is at left edge
        if bbox['x'] < width * 0.1:
            if current_group:
                hierarchy.append(current_group)
            current_group = {
                'type': 'group',
                'children': [element],
                'bbox': bbox.copy()
            }
        else:
            if current_group:
                current_group['children'].append(element)
                # Expand group bbox
                current_group['bbox'] = merge_bboxes(current_group['bbox'], bbox)
    
    if current_group:
        hierarchy.append(current_group)
    
    return hierarchy
```

**Expected Results for login-screen.png:**
```json
{
  "elements": [
    {"type": "heading", "text": "Welcome Back", "bbox": {"x": 120, "y": 80, "width": 280, "height": 42}},
    {"type": "label", "text": "Email Address", "bbox": {"x": 120, "y": 150, "width": 140, "height": 18}},
    {"type": "input", "placeholder": "you@example.com", "bbox": {"x": 120, "y": 175, "width": 360, "height": 44}},
    {"type": "label", "text": "Password", "bbox": {"x": 120, "y": 235, "width": 100, "height": 18}},
    {"type": "input", "placeholder": "••••••••", "bbox": {"x": 120, "y": 260, "width": 360, "height": 44}},
    {"type": "button", "text": "Sign In", "bbox": {"x": 120, "y": 330, "width": 360, "height": 48}},
    {"type": "link", "text": "Forgot password?", "bbox": {"x": 360, "y": 395, "width": 120, "height": 20}},
    {"type": "text", "text": "Don't have an account? Sign up", "bbox": {"x": 140, "y": 450, "width": 280, "height": 20}}
  ],
  "count": 8,
  "by_type": {"heading": 1, "label": 2, "input": 2, "button": 1, "link": 1, "text": 1},
  "layout": "centered-form"
}
```

---

### 3. Test ID Generation

**Algorithm:** Semantic naming based on element context

```python
def generate_test_ids(elements, page_name):
    """
    Generate data-testid attributes for UI testing.
    
    Args:
        elements: Detected UI elements
        page_name: Page identifier (e.g., 'login', 'dashboard')
    
    Returns:
        Elements with assigned test IDs
    """
    
    # Counter for duplicate types
    type_counters = {}
    
    for element in elements:
        element_type = element['type']
        
        # Generate semantic base name
        if 'text' in element and element['text']:
            # Use text content for semantic naming
            base_name = slugify(element['text'])
            
            # Truncate long names
            if len(base_name) > 30:
                base_name = base_name[:30]
            
            test_id = f"{page_name}-{element_type}-{base_name}"
        else:
            # Fallback: use type + counter
            if element_type not in type_counters:
                type_counters[element_type] = 0
            type_counters[element_type] += 1
            
            test_id = f"{page_name}-{element_type}-{type_counters[element_type]}"
        
        # Ensure uniqueness
        test_id = ensure_unique_test_id(test_id, elements)
        
        element['testid'] = test_id
        element['html_attribute'] = f'data-testid="{test_id}"'
    
    return elements


def slugify(text):
    """Convert text to kebab-case slug."""
    
    # Lowercase
    slug = text.lower()
    
    # Replace spaces and special chars with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    return slug
```

**Expected Results for login-screen.png:**
```json
{
  "test_ids": [
    {"element": "heading", "text": "Welcome Back", "testid": "login-heading-welcome-back"},
    {"element": "label", "text": "Email Address", "testid": "login-label-email-address"},
    {"element": "input", "placeholder": "you@example.com", "testid": "login-input-email"},
    {"element": "label", "text": "Password", "testid": "login-label-password"},
    {"element": "input", "placeholder": "••••••••", "testid": "login-input-password"},
    {"element": "button", "text": "Sign In", "testid": "login-button-sign-in"},
    {"element": "link", "text": "Forgot password?", "testid": "login-link-forgot-password"},
    {"element": "text", "text": "Sign up", "testid": "login-link-sign-up"}
  ],
  "count": 8,
  "convention": "kebab-case",
  "prefix": "login"
}
```

---

### 4. Accessibility Analysis

**Algorithm:** WCAG 2.1 compliance checking

```python
def analyze_accessibility(image_path, elements, color_palette):
    """
    Check WCAG 2.1 Level AA compliance.
    
    Returns:
        List of accessibility violations with severity and recommendations
    """
    
    violations = []
    
    # Check 1: Color contrast (1.4.3 Contrast Minimum)
    for element in elements:
        if element['type'] in ['text', 'label', 'heading']:
            # Estimate text color from element region
            text_color = extract_dominant_color(image_path, element['bbox'])
            bg_color = estimate_background_color(image_path, element['bbox'])
            
            contrast = calculate_contrast_ratio(text_color, bg_color)
            
            # WCAG AA: 4.5:1 for normal text, 3:1 for large text
            threshold = 3.0 if element['type'] == 'heading' else 4.5
            
            if contrast < threshold:
                violations.append({
                    'guideline': 'WCAG 2.1 - 1.4.3 Contrast (Minimum)',
                    'element': element['text'],
                    'type': element['type'],
                    'issue': f'Insufficient contrast ratio: {contrast:.2f}:1 (minimum {threshold}:1)',
                    'severity': 'HIGH',
                    'recommendation': f'Increase contrast to {threshold}:1 or higher'
                })
    
    # Check 2: Missing alt text for images (1.1.1 Non-text Content)
    image_elements = [e for e in elements if e['type'] in ['image', 'icon']]
    if image_elements:
        violations.append({
            'guideline': 'WCAG 2.1 - 1.1.1 Non-text Content',
            'element': 'Images/Icons',
            'issue': f'{len(image_elements)} images without alt text detected',
            'severity': 'HIGH',
            'recommendation': 'Add descriptive alt text to all images'
        })
    
    # Check 3: Missing form labels (3.3.2 Labels or Instructions)
    inputs = [e for e in elements if e['type'] == 'input']
    labels = [e for e in elements if e['type'] == 'label']
    
    if len(inputs) > len(labels):
        violations.append({
            'guideline': 'WCAG 2.1 - 3.3.2 Labels or Instructions',
            'element': 'Form inputs',
            'issue': f'{len(inputs) - len(labels)} inputs without visible labels',
            'severity': 'HIGH',
            'recommendation': 'Add <label> elements with for attribute'
        })
    
    # Check 4: Touch target size (2.5.5 Target Size - Level AAA but recommended)
    for element in elements:
        if element['type'] in ['button', 'link']:
            width = element['bbox']['width']
            height = element['bbox']['height']
            
            if width < 44 or height < 44:  # 44x44 CSS pixels minimum
                violations.append({
                    'guideline': 'WCAG 2.1 - 2.5.5 Target Size',
                    'element': element.get('text', element['type']),
                    'issue': f'Touch target too small: {width}x{height}px (minimum 44x44px)',
                    'severity': 'MEDIUM',
                    'recommendation': 'Increase button/link size to 44x44px minimum'
                })
    
    # Check 5: Focus indicators (2.4.7 Focus Visible)
    # Note: Can't detect from static image, add as reminder
    violations.append({
        'guideline': 'WCAG 2.1 - 2.4.7 Focus Visible',
        'element': 'Interactive elements',
        'issue': 'Focus indicators not visible in static mockup',
        'severity': 'MEDIUM',
        'recommendation': 'Ensure visible focus indicators (outline/ring) on all interactive elements',
        'note': 'Verify in live implementation'
    })
    
    return {
        'violations': violations,
        'count': len(violations),
        'by_severity': {
            'HIGH': len([v for v in violations if v['severity'] == 'HIGH']),
            'MEDIUM': len([v for v in violations if v['severity'] == 'MEDIUM']),
            'LOW': len([v for v in violations if v['severity'] == 'LOW'])
        },
        'compliance_score': calculate_compliance_score(violations)
    }


def calculate_contrast_ratio(color1, color2):
    """Calculate WCAG contrast ratio between two colors."""
    
    def relative_luminance(rgb):
        """Calculate relative luminance."""
        r, g, b = [x / 255.0 for x in rgb]
        
        # Apply gamma correction
        r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
        g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
        b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
        
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    l1 = relative_luminance(color1)
    l2 = relative_luminance(color2)
    
    lighter = max(l1, l2)
    darker = min(l1, l2)
    
    return (lighter + 0.05) / (darker + 0.05)
```

**Expected Results for login-screen.png:**
```json
{
  "violations": [
    {
      "guideline": "WCAG 2.1 - 1.4.3 Contrast (Minimum)",
      "element": "Forgot password?",
      "type": "link",
      "issue": "Insufficient contrast ratio: 3.2:1 (minimum 4.5:1)",
      "severity": "HIGH",
      "recommendation": "Increase contrast to 4.5:1 or higher"
    },
    {
      "guideline": "WCAG 2.1 - 2.5.5 Target Size",
      "element": "Forgot password?",
      "issue": "Touch target too small: 120x20px (minimum 44x44px)",
      "severity": "MEDIUM",
      "recommendation": "Increase button/link size to 44x44px minimum"
    },
    {
      "guideline": "WCAG 2.1 - 2.4.7 Focus Visible",
      "element": "Interactive elements",
      "issue": "Focus indicators not visible in static mockup",
      "severity": "MEDIUM",
      "recommendation": "Ensure visible focus indicators on all interactive elements"
    }
  ],
  "count": 3,
  "by_severity": {"HIGH": 1, "MEDIUM": 2, "LOW": 0},
  "compliance_score": 75
}
```

---

### 5. Requirements Extraction

**Algorithm:** Template-based user story generation

```python
def extract_requirements(mockup_name, elements, layout, color_palette):
    """
    Generate user stories from UI mockup analysis.
    
    Returns:
        List of user stories with acceptance criteria
    """
    
    user_stories = []
    
    # Story 1: Authentication (if login elements detected)
    if any(e['type'] == 'input' and 'email' in e.get('text', '').lower() for e in elements):
        user_stories.append({
            'id': 'US-001',
            'title': 'User Login',
            'as_a': 'registered user',
            'i_want': 'to log in with my email and password',
            'so_that': 'I can access my account',
            'acceptance_criteria': [
                'GIVEN I am on the login page',
                'WHEN I enter valid email and password',
                'THEN I am redirected to the dashboard',
                'AND my session is established'
            ],
            'elements': ['email input', 'password input', 'sign in button'],
            'priority': 'HIGH'
        })
    
    # Story 2: Password recovery
    if any('forgot' in e.get('text', '').lower() for e in elements):
        user_stories.append({
            'id': 'US-002',
            'title': 'Password Recovery',
            'as_a': 'user who forgot my password',
            'i_want': 'to reset my password via email',
            'so_that': 'I can regain access to my account',
            'acceptance_criteria': [
                'GIVEN I am on the login page',
                'WHEN I click "Forgot password?"',
                'THEN I am taken to password reset page',
                'AND I can enter my email to receive reset link'
            ],
            'elements': ['forgot password link'],
            'priority': 'MEDIUM'
        })
    
    # Story 3: User registration
    if any('sign up' in e.get('text', '').lower() for e in elements):
        user_stories.append({
            'id': 'US-003',
            'title': 'User Registration',
            'as_a': 'new user',
            'i_want': 'to create an account',
            'so_that': 'I can access the platform',
            'acceptance_criteria': [
                'GIVEN I am on the login page',
                'WHEN I click "Sign up"',
                'THEN I am taken to registration page',
                'AND I can create a new account'
            ],
            'elements': ['sign up link'],
            'priority': 'HIGH'
        })
    
    # Story 4: Responsive design
    user_stories.append({
        'id': 'US-004',
        'title': 'Responsive Login Page',
        'as_a': 'mobile user',
        'i_want': 'the login page to work on mobile devices',
        'so_that': 'I can log in from anywhere',
        'acceptance_criteria': [
            f'GIVEN the page uses {layout} layout',
            'WHEN I access the page on mobile (320px-768px)',
            'THEN all elements are readable and accessible',
            'AND touch targets are minimum 44x44px'
        ],
        'elements': ['all page elements'],
        'priority': 'HIGH'
    })
    
    return {
        'stories': user_stories,
        'count': len(user_stories),
        'total_acceptance_criteria': sum(len(s['acceptance_criteria']) for s in user_stories)
    }
```

---

## ✅ Success Criteria

| Criterion | Target | Validation |
|-----------|--------|------------|
| **Mockups Analyzed** | 4/4 | All mockups processed |
| **Color Extraction** | 100% | 18-24 colors detected |
| **Element Detection** | 100% | 68 elements identified |
| **Test ID Generation** | 100% | 68 unique test IDs |
| **Accessibility Checks** | 100% | 12 violations detected |
| **Requirements** | 16 stories | 4 per mockup with criteria |
| **Token Efficiency** | <500 tokens/image | API cost optimization |
| **Analysis Time** | <2s/image | Performance target |

---

## 🎯 Validation Execution

### Phase 1: Image Analysis (120 minutes)

1. **Color Palette Extraction (30 min):** Process 4 mockups with K-means
2. **Element Detection (40 min):** Run OCR + contour detection
3. **Test ID Generation (20 min):** Generate semantic test IDs
4. **Accessibility Analysis (30 min):** WCAG 2.1 compliance checks

### Phase 2: Requirements Generation (90 minutes)

1. **User Story Extraction (40 min):** Generate 16 stories
2. **Acceptance Criteria (30 min):** GIVEN-WHEN-THEN format
3. **Priority Assignment (20 min):** Classify HIGH/MEDIUM/LOW

### Phase 3: Validation (90 minutes)

1. **Manual Verification (40 min):** Spot-check analysis accuracy
2. **Token Counting (20 min):** Measure API token usage
3. **Performance Benchmarking (15 min):** Measure analysis time
4. **Accuracy Assessment (15 min):** Compare with ground truth

---

## 📝 Validation Report Template

```markdown
# Vision API Validation Report

## Executive Summary
- **Mockups Analyzed:** 4/4
- **Total Elements:** 68 detected
- **Analysis Time:** 7.2 seconds (1.8s/mockup)
- **Token Usage:** 1,840 tokens (460 avg/mockup)

## Results

### Color Palette Extraction ✅
- **Colors Detected:** 22 (4-6 per mockup)
- **Accuracy:** 100% (RGB/Hex validation)
- **Suggestions:** 8 contrast issues identified

### Element Detection ✅
- **Elements Detected:** 68/68 (100%)
- **By Type:** Buttons 12, Inputs 18, Labels 16, Headings 8, Links 6, Others 8
- **Accuracy:** 100% (manual verification)

### Test ID Generation ✅
- **Test IDs Generated:** 68 unique IDs
- **Convention:** kebab-case ✅
- **Uniqueness:** 100% ✅
- **Semantic Naming:** 100% ✅

### Accessibility Analysis ✅
- **Violations Detected:** 12 (expected: 12)
  - HIGH: 5 (contrast, missing labels)
  - MEDIUM: 7 (touch targets, focus indicators)
- **WCAG Compliance:** 75% (before fixes)

### Requirements Extraction ✅
- **User Stories:** 16 generated (4 per mockup)
- **Acceptance Criteria:** 64 total (4 per story)
- **Format:** GIVEN-WHEN-THEN ✅
- **Priority:** All stories prioritized ✅

**Verdict:** ✅ **VISION API VALIDATED** (4/4 mockups, 1.8s/image, 460 tokens/image)
```

---

**Plan Created:** December 26, 2025  
**Status:** ⏳ READY FOR VALIDATION  
**Duration:** 5 hours estimated  
**Target:** 4 mockups, <2s/image, 100% accuracy, <500 tokens/image

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX
