"""
Mermaid Diagram Validator - CORTEX Lens Quality Assurance

Validates Mermaid diagrams in generated specifications to ensure they render correctly.
Part of the legacy API specification generation quality gates.

Author: CORTEX
Version: 1.0.0
Date: December 15, 2025
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class DiagramValidationError:
    """Represents a validation error in a Mermaid diagram."""
    diagram_type: str  # flowchart, sequenceDiagram, classDiagram
    line_number: int
    error_type: str
    message: str
    context: str  # Surrounding text for debugging


@dataclass
class DiagramValidationResult:
    """Results of diagram validation."""
    is_valid: bool
    errors: List[DiagramValidationError]
    warnings: List[str]
    diagrams_found: int
    diagrams_validated: int


class MermaidDiagramValidator:
    """
    Validates Mermaid diagrams in Markdown files.
    
    Checks for:
    - Syntax errors (unclosed brackets, invalid characters)
    - Truncated text/identifiers
    - Invalid participant names in sequence diagrams
    - Malformed node definitions in flowcharts
    - Invalid class definitions in class diagrams
    """
    
    def __init__(self):
        self.errors: List[DiagramValidationError] = []
        self.warnings: List[str] = []
        
    def validate_markdown_file(self, md_file_path: Path) -> DiagramValidationResult:
        """
        Validate all Mermaid diagrams in a Markdown file.
        
        Args:
            md_file_path: Path to the Markdown file
            
        Returns:
            DiagramValidationResult with validation status and errors
        """
        self.errors = []
        self.warnings = []
        
        if not md_file_path.exists():
            return DiagramValidationResult(
                is_valid=False,
                errors=[DiagramValidationError(
                    diagram_type="file",
                    line_number=0,
                    error_type="FileNotFound",
                    message=f"File not found: {md_file_path}",
                    context=""
                )],
                warnings=[],
                diagrams_found=0,
                diagrams_validated=0
            )
        
        content = md_file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        # Extract all Mermaid code blocks
        diagrams = self._extract_mermaid_diagrams(lines)
        
        # Validate each diagram
        for diagram_type, start_line, diagram_lines in diagrams:
            self._validate_diagram(diagram_type, start_line, diagram_lines)
        
        return DiagramValidationResult(
            is_valid=len(self.errors) == 0,
            errors=self.errors,
            warnings=self.warnings,
            diagrams_found=len(diagrams),
            diagrams_validated=len(diagrams)
        )
    
    def _extract_mermaid_diagrams(self, lines: List[str]) -> List[Tuple[str, int, List[str]]]:
        """
        Extract all Mermaid diagrams from Markdown content.
        
        Returns:
            List of (diagram_type, start_line, diagram_lines)
        """
        diagrams = []
        in_code_block = False
        current_diagram = []
        diagram_type = None
        start_line = 0
        
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('```mermaid'):
                in_code_block = True
                start_line = i
                current_diagram = []
                continue
            elif line.strip() == '```' and in_code_block:
                # End of code block
                if current_diagram:
                    # Detect diagram type from first line
                    first_line = current_diagram[0].strip()
                    if first_line.startswith('flowchart'):
                        diagram_type = 'flowchart'
                    elif first_line.startswith('sequenceDiagram'):
                        diagram_type = 'sequenceDiagram'
                    elif first_line.startswith('classDiagram'):
                        diagram_type = 'classDiagram'
                    else:
                        diagram_type = 'unknown'
                    
                    diagrams.append((diagram_type, start_line, current_diagram))
                
                in_code_block = False
                current_diagram = []
                diagram_type = None
            elif in_code_block:
                current_diagram.append(line)
        
        return diagrams
    
    def _validate_diagram(self, diagram_type: str, start_line: int, lines: List[str]):
        """Validate a single Mermaid diagram."""
        if diagram_type == 'flowchart':
            self._validate_flowchart(start_line, lines)
        elif diagram_type == 'sequenceDiagram':
            self._validate_sequence_diagram(start_line, lines)
        elif diagram_type == 'classDiagram':
            self._validate_class_diagram(start_line, lines)
        else:
            self.warnings.append(f"Line {start_line}: Unknown diagram type: {diagram_type}")
    
    def _validate_flowchart(self, start_line: int, lines: List[str]):
        """Validate flowchart syntax."""
        for i, line in enumerate(lines, start_line):
            # Check for unclosed brackets/braces
            if self._has_unclosed_brackets(line):
                self.errors.append(DiagramValidationError(
                    diagram_type='flowchart',
                    line_number=i,
                    error_type='UnclosedBrackets',
                    message='Line contains unclosed brackets or braces',
                    context=line.strip()
                ))
            
            # Check for truncated text (ends with ... or incomplete word)
            if '...' in line and not line.strip().endswith('...'):
                self.errors.append(DiagramValidationError(
                    diagram_type='flowchart',
                    line_number=i,
                    error_type='TruncatedText',
                    message='Line contains truncated text (...)',
                    context=line.strip()
                ))
            
            # Check for invalid node labels (ending with partial words)
            if '-->' in line or '-->|' in line:
                self._check_node_labels(line, i, 'flowchart')
    
    def _validate_sequence_diagram(self, start_line: int, lines: List[str]):
        """Validate sequence diagram syntax."""
        participants = set()
        
        for i, line in enumerate(lines, start_line):
            stripped = line.strip()
            
            # Extract participant declarations
            if stripped.startswith('participant '):
                participant = stripped.replace('participant ', '').strip()
                if not participant:
                    self.errors.append(DiagramValidationError(
                        diagram_type='sequenceDiagram',
                        line_number=i,
                        error_type='EmptyParticipant',
                        message='Participant declaration is empty',
                        context=line.strip()
                    ))
                else:
                    participants.add(participant)
            
            # Check message arrows
            if '->>' in stripped or '-->>' in stripped or '-->' in stripped:
                # Extract source and target
                arrow_match = re.search(r'(\w+)\s*-+>>?\+?-?\s*(\w+):', stripped)
                if arrow_match:
                    source = arrow_match.group(1)
                    target = arrow_match.group(2)
                    
                    # Check if participants are truncated (common error pattern)
                    if len(source) < 3 or len(target) < 3:
                        self.warnings.append(
                            f"Line {i}: Suspiciously short participant name: {source} or {target}"
                        )
                    
                    # Check for special characters that break Mermaid
                    if re.search(r'[{}[\]()<>"\']', source + target):
                        self.errors.append(DiagramValidationError(
                            diagram_type='sequenceDiagram',
                            line_number=i,
                            error_type='InvalidCharacters',
                            message=f'Participant names contain invalid characters: {source}, {target}',
                            context=line.strip()
                        ))
            
            # Check for unclosed syntax
            if self._has_unclosed_brackets(stripped):
                self.errors.append(DiagramValidationError(
                    diagram_type='sequenceDiagram',
                    line_number=i,
                    error_type='UnclosedBrackets',
                    message='Line contains unclosed brackets',
                    context=line.strip()
                ))
    
    def _validate_class_diagram(self, start_line: int, lines: List[str]):
        """Validate class diagram syntax."""
        for i, line in enumerate(lines, start_line):
            stripped = line.strip()
            
            # Check class declarations
            if stripped.startswith('class '):
                # Check for invalid characters in class names
                class_match = re.search(r'class\s+(\w+)', stripped)
                if class_match:
                    class_name = class_match.group(1)
                    if re.search(r'[{}[\]()<>"\']', class_name):
                        self.errors.append(DiagramValidationError(
                            diagram_type='classDiagram',
                            line_number=i,
                            error_type='InvalidClassName',
                            message=f'Class name contains invalid characters: {class_name}',
                            context=line.strip()
                        ))
            
            # Check for unclosed braces
            if '{' in stripped and '}' not in stripped and not stripped.endswith('{'):
                # Could be start of class definition, which is okay
                pass
            elif self._has_unclosed_brackets(stripped):
                self.errors.append(DiagramValidationError(
                    diagram_type='classDiagram',
                    line_number=i,
                    error_type='UnclosedBrackets',
                    message='Line contains unclosed brackets',
                    context=line.strip()
                ))
    
    def _has_unclosed_brackets(self, line: str) -> bool:
        """Check if a line has unclosed brackets/braces."""
        # Count opening and closing for each type
        brackets = {'(': ')', '[': ']', '{': '}'}
        stack = []
        
        for char in line:
            if char in brackets:
                stack.append(char)
            elif char in brackets.values():
                if not stack:
                    return True
                expected_open = [k for k, v in brackets.items() if v == char][0]
                if stack[-1] != expected_open:
                    return True
                stack.pop()
        
        # Some unclosed brackets are okay in Mermaid (like {text?} in flowcharts)
        # Only flag if it's clearly broken
        return len(stack) > 2
    
    def _check_node_labels(self, line: str, line_num: int, diagram_type: str):
        """Check node labels for truncation or invalid patterns."""
        # Extract labels between [...] or {...}
        labels = re.findall(r'[\[{]([^\]}]+)[\]}]', line)
        
        for label in labels:
            # Check for truncated text
            if label.endswith('...') or len(label.split()[-1]) < 2:
                self.warnings.append(
                    f"Line {line_num}: Potentially truncated label: '{label}'"
                )


def validate_spec_file(spec_file_path: Path) -> DiagramValidationResult:
    """
    Convenience function to validate a specification file.
    
    Args:
        spec_file_path: Path to business-spec.md file
        
    Returns:
        DiagramValidationResult
    """
    validator = MermaidDiagramValidator()
    return validator.validate_markdown_file(spec_file_path)


def print_validation_report(result: DiagramValidationResult, file_path: Path):
    """Print a formatted validation report."""
    print(f"\n{'='*80}")
    print(f"Mermaid Diagram Validation Report")
    print(f"File: {file_path.name}")
    print(f"{'='*80}\n")
    
    print(f"Diagrams Found: {result.diagrams_found}")
    print(f"Diagrams Validated: {result.diagrams_validated}")
    print(f"Status: {'✅ PASS' if result.is_valid else '❌ FAIL'}\n")
    
    if result.errors:
        print(f"❌ Errors ({len(result.errors)}):")
        print(f"{'-'*80}")
        for error in result.errors:
            print(f"  Line {error.line_number} [{error.diagram_type}] {error.error_type}")
            print(f"    {error.message}")
            print(f"    Context: {error.context[:60]}...")
            print()
    
    if result.warnings:
        print(f"⚠️  Warnings ({len(result.warnings)}):")
        print(f"{'-'*80}")
        for warning in result.warnings:
            print(f"  {warning}")
        print()
    
    if result.is_valid and not result.warnings:
        print("✅ All diagrams passed validation with no warnings!\n")
    
    print(f"{'='*80}\n")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python mermaid_diagram_validator.py <path_to_business_spec.md>")
        sys.exit(1)
    
    spec_path = Path(sys.argv[1])
    result = validate_spec_file(spec_path)
    print_validation_report(result, spec_path)
    
    # Exit with error code if validation failed
    sys.exit(0 if result.is_valid else 1)
