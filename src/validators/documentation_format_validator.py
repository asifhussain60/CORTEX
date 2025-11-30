"""
Documentation Format Validator

Validates CORTEX admin documentation outputs against the v1.0 format specification.

Copyright ┬⌐ 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from html.parser import HTMLParser
import hashlib


@dataclass
class ValidationError:
    """Represents a validation error (blocker)"""
    category: str
    message: str
    severity: str = "error"
    location: Optional[str] = None
    fix_suggestion: Optional[str] = None


@dataclass
class ValidationWarning:
    """Represents a validation warning (non-blocker)"""
    category: str
    message: str
    severity: str = "warning"
    location: Optional[str] = None


@dataclass
class ValidationResult:
    """Results from documentation format validation"""
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationWarning] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    # Detailed results
    layer_count: int = 0
    viz_count: int = 0
    load_time: float = 0.0
    file_size: int = 0
    
    def __str__(self) -> str:
        """String representation of validation result"""
        status = "Γ£à VALID" if self.is_valid else "Γ¥î INVALID"
        return (
            f"{status}\n"
            f"Errors: {len(self.errors)}\n"
            f"Warnings: {len(self.warnings)}\n"
            f"Layers: {self.layer_count}\n"
            f"Visualizations: {self.viz_count}\n"
            f"File Size: {self.file_size / 1024:.1f} KB"
        )


class DashboardHTMLParser(HTMLParser):
    """Custom HTML parser to extract dashboard structure"""
    
    def __init__(self):
        super().__init__()
        self.structure = {
            'doctype': None,
            'has_d3js': False,
            'has_html2canvas': False,
            'has_jspdf': False,
            'has_csp': False,
            'csp_content': None,
            'layers': [],
            'visualizations': [],
            'inline_handlers': [],
            'script_tags': [],
            'style_tags': [],
            'current_layer': None,
            'tab_buttons': [],
            'export_buttons': []
        }
        self.in_script = False
        self.in_style = False
        self.current_tag_attrs = {}
    
    def handle_decl(self, decl):
        """Handle DOCTYPE declaration"""
        if 'DOCTYPE' in decl.upper():
            self.structure['doctype'] = f"<!{decl}>"
    
    def handle_starttag(self, tag, attrs):
        """Handle opening tags"""
        attrs_dict = dict(attrs)
        self.current_tag_attrs = attrs_dict
        
        # Check for inline event handlers
        for attr_name, attr_value in attrs:
            if attr_name.startswith('on') and attr_name.lower() in [
                'onclick', 'onload', 'onmouseover', 'onmouseout', 
                'onchange', 'onsubmit', 'onerror'
            ]:
                self.structure['inline_handlers'].append({
                    'tag': tag,
                    'event': attr_name,
                    'handler': attr_value
                })
        
        # Track script tags
        if tag == 'script':
            self.in_script = True
            src = attrs_dict.get('src', '')
            if 'd3js.org' in src or 'd3.v7' in src:
                self.structure['has_d3js'] = True
            if 'html2canvas' in src:
                self.structure['has_html2canvas'] = True
            if 'jspdf' in src:
                self.structure['has_jspdf'] = True
            self.structure['script_tags'].append({
                'src': src,
                'attrs': attrs_dict
            })
        
        # Track style tags
        if tag == 'style':
            self.in_style = True
            self.structure['style_tags'].append(attrs_dict)
        
        # Check for CSP meta tag
        if tag == 'meta':
            http_equiv = attrs_dict.get('http-equiv', '').lower()
            if http_equiv == 'content-security-policy':
                self.structure['has_csp'] = True
                self.structure['csp_content'] = attrs_dict.get('content', '')
        
        # Track layers (tab content)
        if tag == 'div':
            div_id = attrs_dict.get('id', '')
            div_class = attrs_dict.get('class', '')
            
            if div_id.startswith('layer-'):
                self.structure['layers'].append({
                    'id': div_id,
                    'class': div_class,
                    'elements': []
                })
                self.current_layer = self.structure['layers'][-1]
        
        # Track SVG elements (visualizations)
        if tag == 'svg':
            svg_id = attrs_dict.get('id', '')
            if svg_id:
                self.structure['visualizations'].append({
                    'id': svg_id,
                    'attrs': attrs_dict
                })
        
        # Track tab buttons
        if tag == 'button':
            button_class = attrs_dict.get('class', '')
            if 'tab-button' in button_class:
                self.structure['tab_buttons'].append(attrs_dict)
        
        # Track export buttons
        if tag == 'button':
            button_text = attrs_dict.get('onclick', '')
            if 'export' in button_text.lower():
                self.structure['export_buttons'].append(attrs_dict)
    
    def handle_endtag(self, tag):
        """Handle closing tags"""
        if tag == 'script':
            self.in_script = False
        if tag == 'style':
            self.in_style = False
        if tag == 'div' and hasattr(self, 'current_layer') and self.current_layer:
            self.current_layer = None


class DocumentationFormatValidator:
    """
    Validates CORTEX admin documentation outputs against format specification v1.0
    
    Validation Categories:
    - Structure: HTML structure, DOCTYPE, libraries, tabs
    - Content: Layers, headings, required elements
    - Visualizations: D3.js charts, interactivity, accessibility
    - Security: CSP, XSS prevention, inline handlers
    - Performance: File size, load time estimates
    - Export: PDF/PNG/PPTX functionality
    - Accessibility: ARIA labels, keyboard navigation
    
    Usage:
        validator = DocumentationFormatValidator()
        result = validator.validate("path/to/dashboard.html")
        
        if result.is_valid:
            print("Γ£à Dashboard is compliant")
        else:
            for error in result.errors:
                print(f"Γ¥î {error.message}")
    """
    
    # Required libraries with minimum versions
    REQUIRED_LIBRARIES = {
        'd3js': {
            'pattern': r'd3\.v7\.(8\.[5-9]|9\.\d+|\d{2,}\.\d+)',
            'url_pattern': r'https://d3js\.org/d3\.v7\.min\.js',
            'min_version': '7.8.5'
        },
        'html2canvas': {
            'pattern': r'html2canvas',
            'url_pattern': r'html2canvas/1\.[4-9]\.',
            'min_version': '1.4.1'
        },
        'jspdf': {
            'pattern': r'jspdf',
            'url_pattern': r'jspdf/2\.[5-9]\.',
            'min_version': '2.5.1'
        }
    }
    
    # Required layers
    REQUIRED_LAYERS = [
        'layer-executive',
        'layer-analysis',
        'layer-issues',
        'layer-technical',
        'layer-export'
    ]
    
    # Required CSP directives
    REQUIRED_CSP_DIRECTIVES = [
        "default-src 'self'",
        "script-src",
        "style-src"
    ]
    
    # CORTEX color palette
    CORTEX_COLORS = {
        'primary': '#2c3e50',
        'secondary': '#3498db',
        'accent': '#e74c3c',
        'success': '#27ae60',
        'warning': '#f39c12',
        'error': '#e74c3c'
    }
    
    def __init__(self, schema_path: Optional[Path] = None):
        """
        Initialize validator
        
        Args:
            schema_path: Optional path to validation schema JSON
        """
        self.schema = self._load_schema(schema_path)
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationWarning] = []
        self.metrics: Dict[str, Any] = {}
    
    def _load_schema(self, schema_path: Optional[Path]) -> Dict[str, Any]:
        """Load validation schema from JSON file"""
        if schema_path is None:
            # Default schema path
            schema_path = Path(__file__).parent.parent.parent / 'cortex-brain' / 'documents' / 'standards' / 'format-validation-schema.json'
        
        if schema_path.exists():
            with open(schema_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Return minimal schema if file not found
            return {"version": "1.0.0"}
    
    def validate(self, file_path: str) -> ValidationResult:
        """
        Validate a dashboard HTML file
        
        Args:
            file_path: Path to HTML file
            
        Returns:
            ValidationResult with detailed validation information
        """
        self.errors = []
        self.warnings = []
        self.metrics = {}
        
        file_path = Path(file_path)
        
        # Check file exists
        if not file_path.exists():
            self.errors.append(ValidationError(
                category="file",
                message=f"File not found: {file_path}",
                fix_suggestion="Verify the file path is correct"
            ))
            return self._build_result(False)
        
        # Check file extension
        if file_path.suffix.lower() != '.html':
            self.errors.append(ValidationError(
                category="file",
                message=f"Invalid file extension: {file_path.suffix} (expected .html)",
                fix_suggestion="Dashboard files must have .html extension"
            ))
            return self._build_result(False)
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.errors.append(ValidationError(
                category="file",
                message=f"Failed to read file: {str(e)}",
                fix_suggestion="Check file permissions and encoding"
            ))
            return self._build_result(False)
        
        # Get file size
        file_size = file_path.stat().st_size
        self.metrics['file_size'] = file_size
        
        # Check file size (max 2 MB)
        if file_size > 2 * 1024 * 1024:
            self.warnings.append(ValidationWarning(
                category="performance",
                message=f"File size exceeds recommendation: {file_size / 1024 / 1024:.2f} MB (max 2 MB)",
                location=str(file_path)
            ))
        
        # Parse HTML
        parser = DashboardHTMLParser()
        try:
            parser.feed(content)
        except Exception as e:
            self.errors.append(ValidationError(
                category="structure",
                message=f"HTML parsing failed: {str(e)}",
                fix_suggestion="Validate HTML syntax"
            ))
            return self._build_result(False)
        
        structure = parser.structure
        
        # Run validation checks
        self._validate_structure(structure, content)
        self._validate_libraries(structure)
        self._validate_csp(structure)
        self._validate_layers(structure)
        self._validate_visualizations(structure)
        self._validate_security(structure, content)
        self._validate_export(structure, content)
        self._validate_accessibility(structure, content)
        self._validate_styling(content)
        
        # Build result
        is_valid = len(self.errors) == 0
        return self._build_result(is_valid, structure)
    
    def _validate_structure(self, structure: Dict, content: str):
        """Validate HTML structure"""
        # Check DOCTYPE
        if not structure['doctype']:
            self.errors.append(ValidationError(
                category="structure",
                message="Missing DOCTYPE declaration",
                fix_suggestion="Add <!DOCTYPE html> at the beginning of the file"
            ))
        elif structure['doctype'] != "<!DOCTYPE html>":
            self.errors.append(ValidationError(
                category="structure",
                message=f"Invalid DOCTYPE: {structure['doctype']} (expected <!DOCTYPE html>)",
                fix_suggestion="Use HTML5 DOCTYPE: <!DOCTYPE html>"
            ))
        
        # Check for required HTML structure
        if '<html' not in content.lower():
            self.errors.append(ValidationError(
                category="structure",
                message="Missing <html> tag",
                fix_suggestion="Wrap content in <html> tags"
            ))
        
        if '<head>' not in content.lower():
            self.errors.append(ValidationError(
                category="structure",
                message="Missing <head> section",
                fix_suggestion="Add <head> section with meta tags and scripts"
            ))
        
        if '<body>' not in content.lower():
            self.errors.append(ValidationError(
                category="structure",
                message="Missing <body> section",
                fix_suggestion="Add <body> section with dashboard content"
            ))
        
        # Check for author attribution
        if 'Asif Hussain' not in content:
            self.warnings.append(ValidationWarning(
                category="metadata",
                message="Missing author attribution",
                location="header"
            ))
        
        # Check for GitHub link
        if 'github.com/asifhussain60/CORTEX' not in content:
            self.warnings.append(ValidationWarning(
                category="metadata",
                message="Missing GitHub repository link",
                location="header"
            ))
    
    def _validate_libraries(self, structure: Dict):
        """Validate required external libraries"""
        if not structure['has_d3js']:
            self.errors.append(ValidationError(
                category="libraries",
                message="Missing D3.js library",
                fix_suggestion="Add D3.js v7.8.5+ script tag: <script src=\"https://d3js.org/d3.v7.min.js\"></script>"
            ))
        
        if not structure['has_html2canvas']:
            self.errors.append(ValidationError(
                category="libraries",
                message="Missing html2canvas library (required for export)",
                fix_suggestion="Add html2canvas script tag for PNG export functionality"
            ))
        
        if not structure['has_jspdf']:
            self.errors.append(ValidationError(
                category="libraries",
                message="Missing jsPDF library (required for export)",
                fix_suggestion="Add jsPDF script tag for PDF export functionality"
            ))
    
    def _validate_csp(self, structure: Dict):
        """Validate Content Security Policy"""
        if not structure['has_csp']:
            self.errors.append(ValidationError(
                category="security",
                message="Missing Content-Security-Policy header",
                fix_suggestion="Add CSP meta tag to <head> section"
            ))
            return
        
        csp_content = structure['csp_content'] or ''
        
        # Check required directives
        for directive in self.REQUIRED_CSP_DIRECTIVES:
            if directive.lower() not in csp_content.lower():
                self.errors.append(ValidationError(
                    category="security",
                    message=f"Missing CSP directive: {directive}",
                    fix_suggestion=f"Add '{directive}' to Content-Security-Policy"
                ))
    
    def _validate_layers(self, structure: Dict):
        """Validate dashboard layers (5-layer structure)"""
        layers = structure['layers']
        layer_ids = [layer['id'] for layer in layers]
        
        self.metrics['layer_count'] = len(layers)
        
        # Check minimum layer count
        if len(layers) < 5:
            self.errors.append(ValidationError(
                category="content",
                message=f"Insufficient layers: {len(layers)} (minimum 5 required)",
                fix_suggestion="Add missing layers: Executive Summary, Detailed Analysis, Issues, Technical Details, Export"
            ))
        
        # Check for required layers
        for required_layer in self.REQUIRED_LAYERS:
            if required_layer not in layer_ids:
                self.errors.append(ValidationError(
                    category="content",
                    message=f"Missing required layer: {required_layer}",
                    fix_suggestion=f"Add <div id=\"{required_layer}\" class=\"tab-content\">...</div>"
                ))
        
        # Check tab buttons
        if len(structure['tab_buttons']) < 5:
            self.errors.append(ValidationError(
                category="structure",
                message=f"Insufficient tab buttons: {len(structure['tab_buttons'])} (minimum 5 required)",
                fix_suggestion="Add tab navigation buttons for each layer"
            ))
    
    def _validate_visualizations(self, structure: Dict):
        """Validate D3.js visualizations"""
        visualizations = structure['visualizations']
        
        self.metrics['viz_count'] = len(visualizations)
        
        # Check minimum visualization count (5 minimum, one per layer)
        if len(visualizations) < 5:
            self.errors.append(ValidationError(
                category="visualizations",
                message=f"Insufficient visualizations: {len(visualizations)} (minimum 5 required)",
                fix_suggestion="Add at least one D3.js visualization per layer"
            ))
    
    def _validate_security(self, structure: Dict, content: str):
        """Validate security measures"""
        # Check for inline event handlers (forbidden)
        inline_handlers = structure['inline_handlers']
        if inline_handlers:
            for handler in inline_handlers[:3]:  # Show first 3
                self.errors.append(ValidationError(
                    category="security",
                    message=f"Inline event handler detected: {handler['tag']}.{handler['event']}",
                    location=f"{handler['tag']} tag",
                    fix_suggestion="Use addEventListener() in <script> block instead of inline handlers"
                ))
            
            if len(inline_handlers) > 3:
                self.errors.append(ValidationError(
                    category="security",
                    message=f"Total inline handlers: {len(inline_handlers)}",
                    fix_suggestion="Remove ALL inline event handlers"
                ))
        
        # Check for potential XSS vulnerabilities
        xss_patterns = [
            r'\.innerHTML\s*=\s*[^;]+(?!sanitize)',  # innerHTML without sanitization
            r'document\.write\(',  # document.write
            r'eval\(',  # eval()
        ]
        
        for pattern in xss_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                self.warnings.append(ValidationWarning(
                    category="security",
                    message=f"Potential XSS risk: {pattern} found {len(matches)} time(s)",
                    location="JavaScript code"
                ))
    
    def _validate_export(self, structure: Dict, content: str):
        """Validate export functionality"""
        # Check for export buttons
        export_buttons = structure['export_buttons']
        if len(export_buttons) < 3:
            self.warnings.append(ValidationWarning(
                category="export",
                message=f"Missing export buttons: {len(export_buttons)} found (3 expected: PDF, PNG, PPTX)",
                location="Export & Actions layer"
            ))
        
        # Check for export functions
        export_functions = ['exportPDF', 'exportPNG', 'exportPPTX']
        for func in export_functions:
            if func not in content:
                self.warnings.append(ValidationWarning(
                    category="export",
                    message=f"Missing export function: {func}()",
                    location="JavaScript code"
                ))
    
    def _validate_accessibility(self, structure: Dict, content: str):
        """Validate accessibility features (WCAG AA)"""
        # Check for ARIA labels on visualizations
        visualizations = structure['visualizations']
        for viz in visualizations:
            viz_id = viz['id']
            # Check if there's a <title> tag for this visualization
            title_pattern = f'<title>[^<]+</title>'
            if not re.search(title_pattern, content, re.IGNORECASE):
                self.warnings.append(ValidationWarning(
                    category="accessibility",
                    message=f"Missing <title> tag for visualization: {viz_id}",
                    location=viz_id
                ))
        
        # Check for alt text on images (if any)
        img_pattern = r'<img(?![^>]*alt=)[^>]*>'
        imgs_without_alt = re.findall(img_pattern, content, re.IGNORECASE)
        if imgs_without_alt:
            self.warnings.append(ValidationWarning(
                category="accessibility",
                message=f"Images without alt text: {len(imgs_without_alt)}",
                location="img tags"
            ))
    
    def _validate_styling(self, content: str):
        """Validate CORTEX color palette compliance"""
        # Check for CORTEX primary color
        if self.CORTEX_COLORS['primary'] not in content:
            self.warnings.append(ValidationWarning(
                category="styling",
                message=f"CORTEX primary color not found: {self.CORTEX_COLORS['primary']}",
                location="CSS styles"
            ))
        
        # Check for font family
        font_patterns = [
            '-apple-system',
            'BlinkMacSystemFont',
            'Segoe UI',
            'Roboto'
        ]
        has_system_font = any(font in content for font in font_patterns)
        if not has_system_font:
            self.warnings.append(ValidationWarning(
                category="styling",
                message="System font stack not found",
                location="CSS typography"
            ))
    
    def _build_result(self, is_valid: bool, structure: Optional[Dict] = None) -> ValidationResult:
        """Build validation result"""
        result = ValidationResult(
            is_valid=is_valid,
            errors=self.errors,
            warnings=self.warnings,
            metrics=self.metrics,
            layer_count=self.metrics.get('layer_count', 0),
            viz_count=self.metrics.get('viz_count', 0),
            file_size=self.metrics.get('file_size', 0)
        )
        
        # Estimate load time based on file size (rough approximation)
        # 1 MB = ~0.5s load time on average connection
        if result.file_size > 0:
            result.load_time = (result.file_size / 1024 / 1024) * 0.5
        
        return result
    
    def validate_batch(self, file_paths: List[str]) -> Dict[str, ValidationResult]:
        """
        Validate multiple dashboard files
        
        Args:
            file_paths: List of file paths to validate
            
        Returns:
            Dictionary mapping file paths to validation results
        """
        results = {}
        for file_path in file_paths:
            results[file_path] = self.validate(file_path)
        return results
    
    def generate_report(self, result: ValidationResult, output_path: Optional[str] = None) -> str:
        """
        Generate detailed validation report
        
        Args:
            result: Validation result
            output_path: Optional path to save report (markdown format)
            
        Returns:
            Report content as string
        """
        timestamp = datetime.now().isoformat()
        
        report_lines = [
            "# CORTEX Documentation Format Validation Report",
            "",
            f"**Generated:** {timestamp}",
            f"**Status:** {'Γ£à VALID' if result.is_valid else 'Γ¥î INVALID'}",
            "",
            "---",
            "",
            "## Summary",
            "",
            f"- **Layers:** {result.layer_count} (minimum 5)",
            f"- **Visualizations:** {result.viz_count} (minimum 5)",
            f"- **File Size:** {result.file_size / 1024:.1f} KB (max 2048 KB)",
            f"- **Estimated Load Time:** {result.load_time:.2f}s (max 2.0s)",
            f"- **Errors:** {len(result.errors)}",
            f"- **Warnings:** {len(result.warnings)}",
            "",
        ]
        
        # Add errors
        if result.errors:
            report_lines.extend([
                "## Γ¥î Errors (Must Fix)",
                ""
            ])
            for i, error in enumerate(result.errors, 1):
                report_lines.append(f"### {i}. {error.message}")
                report_lines.append(f"**Category:** {error.category}")
                if error.location:
                    report_lines.append(f"**Location:** {error.location}")
                if error.fix_suggestion:
                    report_lines.append(f"**Fix:** {error.fix_suggestion}")
                report_lines.append("")
        
        # Add warnings
        if result.warnings:
            report_lines.extend([
                "## ΓÜá∩╕Å Warnings (Recommended Fixes)",
                ""
            ])
            for i, warning in enumerate(result.warnings, 1):
                report_lines.append(f"### {i}. {warning.message}")
                report_lines.append(f"**Category:** {warning.category}")
                if warning.location:
                    report_lines.append(f"**Location:** {warning.location}")
                report_lines.append("")
        
        # Success message
        if result.is_valid:
            report_lines.extend([
                "## Γ£à Validation Successful",
                "",
                "Dashboard complies with CORTEX Documentation Format Specification v1.0",
                ""
            ])
        
        report_content = "\n".join(report_lines)
        
        # Save report if output path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
        
        return report_content
