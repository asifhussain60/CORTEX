#!/usr/bin/env python3
"""
Markdown to YAML Converter - Converts markdown requirements to YAML

This tool converts markdown-formatted requirements documents to structured
YAML format that can be validated and processed programmatically.

Part of: CORTEX 6.0 Remediation Plan - Phase P0-T3
Author: GitHub Copilot + Asif Hussain
Created: 2026-01-08

Usage:
    # Convert single file
    python -m src.tools.md_to_yaml_converter input.md output.yaml
    
    # Convert with validation
    python -m src.tools.md_to_yaml_converter input.md output.yaml --validate
    
    # Batch convert directory
    python -m src.tools.md_to_yaml_converter --dir docs/requirements --output converted/
    
    # Generate conversion report
    python -m src.tools.md_to_yaml_converter input.md output.yaml --report report.md
"""

import re
import yaml
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from src.tools.yaml_validator import YAMLValidator, SchemaType


@dataclass
class ConversionError:
    """Represents a conversion error or warning."""
    line_number: Optional[int]
    message: str
    severity: str = "ERROR"  # ERROR or WARNING


@dataclass
class ConversionResult:
    """Result of MD→YAML conversion."""
    input_file: Path
    output_data: Dict[str, Any]
    success: bool
    errors: List[ConversionError] = field(default_factory=list)
    warnings: List[ConversionError] = field(default_factory=list)
    validated: bool = False
    requirements_count: int = 0
    
    @property
    def summary(self) -> str:
        """Generate summary string."""
        status = "✅ SUCCESS" if self.success else "❌ FAILED"
        return f"{status} | {self.requirements_count} requirements | {len(self.errors)} errors | {len(self.warnings)} warnings"


class RequirementExtractor:
    """Extracts requirements from markdown text."""
    
    # Patterns for parsing
    REQ_ID_PATTERN = re.compile(r'REQ-\d{3}')
    PRIORITY_PATTERN = re.compile(r'\*\*Priority:\*\*\s*(P[0-3]_(?:CRITICAL|HIGH|MEDIUM|LOW))', re.IGNORECASE)
    STATUS_PATTERN = re.compile(r'\*\*Status:\*\*\s*(NOT_STARTED|IN_PROGRESS|COMPLETE|BLOCKED|DEPRECATED)', re.IGNORECASE)
    ACCEPTANCE_CRITERIA_MARKER = re.compile(r'\*\*Acceptance Criteria:\*\*', re.IGNORECASE)
    DEPENDENCIES_PATTERN = re.compile(r'\*\*Dependencies:\*\*\s*(.+)')
    
    @staticmethod
    def extract_heading(line: str) -> Optional[Tuple[int, str]]:
        """Extract heading level and text."""
        match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if match:
            level = len(match.group(1))
            text = match.group(2).strip()
            return (level, text)
        return None
    
    @staticmethod
    def extract_list_items(lines: List[str], start_idx: int) -> List[str]:
        """Extract list items starting from index."""
        items = []
        for line in lines[start_idx:]:
            line = line.strip()
            if not line:
                break
            if line.startswith('- ') or line.startswith('* '):
                items.append(line[2:].strip())
            elif not line.startswith('#'):
                # Continue previous item
                if items:
                    items[-1] += " " + line
                else:
                    break
            else:
                break
        return items
    
    @classmethod
    def extract_requirement_from_section(cls, lines: List[str], start_idx: int, req_id: str) -> Dict[str, Any]:
        """Extract requirement data from markdown section."""
        req = {
            "requirement_id": req_id,
            "description": "",
            "acceptance_criteria": []
        }
        
        description_lines = []
        in_acceptance_criteria = False
        
        for i, line in enumerate(lines[start_idx:], start=start_idx):
            line_stripped = line.strip()
            
            # Stop at next heading
            if line_stripped.startswith('#'):
                break
            
            # Extract priority
            priority_match = cls.PRIORITY_PATTERN.search(line)
            if priority_match:
                req["priority"] = priority_match.group(1).upper()
            
            # Extract status
            status_match = cls.STATUS_PATTERN.search(line)
            if status_match:
                req["status"] = status_match.group(1).upper()
            
            # Extract dependencies
            deps_match = cls.DEPENDENCIES_PATTERN.search(line)
            if deps_match:
                deps_str = deps_match.group(1)
                req["dependencies"] = [d.strip() for d in re.findall(cls.REQ_ID_PATTERN, deps_str)]
            
            # Check for acceptance criteria marker
            if cls.ACCEPTANCE_CRITERIA_MARKER.search(line):
                in_acceptance_criteria = True
                continue
            
            # Extract acceptance criteria
            if in_acceptance_criteria:
                if line_stripped.startswith('- ') or line_stripped.startswith('* '):
                    req["acceptance_criteria"].append(line_stripped[2:])
                elif line_stripped and not line_stripped.startswith('#'):
                    # Continuation of previous criterion
                    if req["acceptance_criteria"]:
                        req["acceptance_criteria"][-1] += " " + line_stripped
            elif line_stripped and not priority_match and not status_match and not deps_match:
                # Part of description
                description_lines.append(line_stripped)
        
        # Join description
        req["description"] = " ".join(description_lines).strip()
        
        # Remove empty acceptance criteria
        req["acceptance_criteria"] = [ac for ac in req["acceptance_criteria"] if ac]
        
        return req
    
    @classmethod
    def extract_requirements_from_table(cls, lines: List[str], start_idx: int) -> List[Dict[str, Any]]:
        """Extract requirements from markdown table."""
        requirements = []
        
        # Find table header
        header_idx = start_idx
        while header_idx < len(lines) and not lines[header_idx].strip().startswith('|'):
            header_idx += 1
        
        if header_idx >= len(lines):
            return requirements
        
        # Parse header
        header = [cell.strip() for cell in lines[header_idx].split('|')[1:-1]]
        
        # Skip separator line
        separator_idx = header_idx + 1
        
        # Parse rows
        for line in lines[separator_idx + 1:]:
            line = line.strip()
            if not line.startswith('|'):
                break
            
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if len(cells) != len(header):
                continue
            
            # Build requirement
            req = {}
            for col_name, cell_value in zip(header, cells):
                col_lower = col_name.lower()
                
                if 'id' in col_lower:
                    req["requirement_id"] = cell_value
                elif 'description' in col_lower or 'desc' in col_lower:
                    req["description"] = cell_value
                elif 'priority' in col_lower:
                    req["priority"] = cell_value.upper()
                elif 'status' in col_lower:
                    req["status"] = cell_value.upper()
            
            if "requirement_id" in req and "description" in req:
                # Add minimal acceptance_criteria if not present
                if "acceptance_criteria" not in req:
                    req["acceptance_criteria"] = [req["description"]]
                requirements.append(req)
        
        return requirements


class MDToYAMLConverter:
    """Converts markdown requirements to YAML format."""
    
    def __init__(self, schema_validator: Optional[YAMLValidator] = None):
        """Initialize converter with optional validator."""
        self.schema_validator = schema_validator or YAMLValidator()
        self.extractor = RequirementExtractor()
    
    def convert(self, input_file: Path) -> ConversionResult:
        """
        Convert markdown file to YAML structure.
        
        Args:
            input_file: Path to markdown file
            
        Returns:
            ConversionResult with extracted data
        """
        input_file = Path(input_file)
        errors = []
        warnings = []
        
        # Check file exists
        if not input_file.exists():
            errors.append(ConversionError(
                line_number=None,
                message=f"File not found: {input_file}",
                severity="ERROR"
            ))
            return ConversionResult(
                input_file=input_file,
                output_data={},
                success=False,
                errors=errors
            )
        
        # Read file
        try:
            with open(input_file, "r") as f:
                content = f.read()
        except Exception as e:
            errors.append(ConversionError(
                line_number=None,
                message=f"Failed to read file: {e}",
                severity="ERROR"
            ))
            return ConversionResult(
                input_file=input_file,
                output_data={},
                success=False,
                errors=errors
            )
        
        if not content.strip():
            errors.append(ConversionError(
                line_number=1,
                message="Empty file",
                severity="ERROR"
            ))
            return ConversionResult(
                input_file=input_file,
                output_data={},
                success=False,
                errors=errors
            )
        
        # Parse markdown
        lines = content.split('\n')
        requirements = []
        feature_metadata = {}
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Extract heading
            heading = self.extractor.extract_heading(line)
            
            if heading:
                level, text = heading
                
                # Feature title (# Feature: ...)
                if level == 1 and 'feature' in text.lower():
                    feature_metadata["name"] = text.replace("Feature:", "").strip()
                
                # Check for requirement heading with ID
                req_id_match = RequirementExtractor.REQ_ID_PATTERN.search(text)
                if req_id_match:
                    req_id = req_id_match.group(0)
                    req = self.extractor.extract_requirement_from_section(lines, i + 1, req_id)
                    requirements.append(req)
            
            # Check for table
            elif line.startswith('|'):
                table_reqs = self.extractor.extract_requirements_from_table(lines, i)
                requirements.extend(table_reqs)
            
            i += 1
        
        # Validate we extracted something
        if not requirements:
            warnings.append(ConversionError(
                line_number=None,
                message="No requirements extracted from file",
                severity="WARNING"
            ))
        
        # Build output structure
        output_data = requirements if len(requirements) > 0 else []
        
        # Add feature metadata if present
        if feature_metadata and requirements:
            output_data = {
                **feature_metadata,
                "requirements": requirements
            }
        
        return ConversionResult(
            input_file=input_file,
            output_data=output_data,
            success=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            requirements_count=len(requirements)
        )
    
    def validate_output(self, result: ConversionResult) -> bool:
        """Validate output against requirements schema."""
        if not result.success:
            return False
        
        # For now, basic validation (can enhance with schema validator)
        if isinstance(result.output_data, list):
            for req in result.output_data:
                if "requirement_id" not in req or "description" not in req:
                    return False
        elif isinstance(result.output_data, dict):
            if "requirements" in result.output_data:
                for req in result.output_data["requirements"]:
                    if "requirement_id" not in req or "description" not in req:
                        return False
        
        result.validated = True
        return True
    
    def save(self, result: ConversionResult, output_file: Path):
        """Save conversion result to YAML file."""
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, "w") as f:
            yaml.dump(result.output_data, f, default_flow_style=False, sort_keys=False)
    
    def convert_batch(self, input_files: List[Path]) -> List[ConversionResult]:
        """Convert multiple files."""
        return [self.convert(f) for f in input_files]


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert Markdown requirements to YAML format",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        help="Input markdown file"
    )
    
    parser.add_argument(
        "output",
        nargs="?",
        type=Path,
        help="Output YAML file"
    )
    
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate output against schema"
    )
    
    parser.add_argument(
        "--dir",
        type=Path,
        help="Directory to batch convert"
    )
    
    parser.add_argument(
        "--pattern",
        default="*.md",
        help="File pattern for directory mode (default: *.md)"
    )
    
    parser.add_argument(
        "--report",
        type=Path,
        help="Generate conversion report"
    )
    
    args = parser.parse_args()
    
    # Create converter
    converter = MDToYAMLConverter()
    
    results = []
    
    # Directory mode
    if args.dir:
        if not args.output:
            print("❌ Error: --output required for directory mode", file=sys.stderr)
            return 1
        
        input_files = list(args.dir.glob(args.pattern))
        if not input_files:
            print(f"❌ No files matching {args.pattern} in {args.dir}", file=sys.stderr)
            return 1
        
        args.output.mkdir(parents=True, exist_ok=True)
        
        for input_file in input_files:
            result = converter.convert(input_file)
            results.append(result)
            
            if result.success:
                output_file = args.output / f"{input_file.stem}.yaml"
                converter.save(result, output_file)
    
    # Single file mode
    elif args.input and args.output:
        result = converter.convert(args.input)
        results.append(result)
        
        if result.success:
            converter.save(result, args.output)
            
            if args.validate:
                converter.validate_output(result)
    
    else:
        print("❌ Error: Provide input/output files or use --dir", file=sys.stderr)
        parser.print_help()
        return 1
    
    # Print results
    print(f"\n{'='*80}")
    print("MD→YAML Conversion Results")
    print(f"{'='*80}\n")
    
    total_reqs = 0
    success_count = 0
    
    for result in results:
        print(f"📄 {result.input_file.name}")
        print(f"   {result.summary}")
        
        if result.errors:
            for error in result.errors:
                print(f"   ❌ {error.message}")
        
        if result.warnings:
            for warning in result.warnings:
                print(f"   ⚠️  {warning.message}")
        
        print()
        
        total_reqs += result.requirements_count
        if result.success:
            success_count += 1
    
    print(f"{'='*80}")
    print(f"Summary: {success_count}/{len(results)} files converted | {total_reqs} total requirements")
    print(f"{'='*80}\n")
    
    return 0 if success_count == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
