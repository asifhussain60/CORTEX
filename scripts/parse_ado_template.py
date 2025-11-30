#!/usr/bin/env python3
"""
ADO Template Parser - Extract DoR/DoD completion, acceptance criteria, and metadata

This module parses ADO markdown templates to extract:
- Definition of Ready (DoR) checkboxes and completion percentage
- Definition of Done (DoD) checkboxes and completion percentage
- Acceptance criteria in Given/When/Then format
- Metadata fields (ADO#, title, priority, etc.)
- Risk analysis and mitigation strategies
- Dependencies and related links

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain
License: Proprietary
Repository: https://github.com/asifhussain60/CORTEX
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CheckboxItem:
    """Represents a checkbox item in the template"""
    text: str
    checked: bool
    section: str  # 'dor', 'dod', 'acceptance_criteria'
    line_number: int


@dataclass
class AcceptanceCriterion:
    """Represents a single acceptance criterion"""
    given: str
    when: str
    then: str
    priority: str = "medium"  # high, medium, low


@dataclass
class ParsedTemplate:
    """Complete parsed template data"""
    # Metadata
    ado_number: Optional[str] = None
    title: Optional[str] = None
    work_item_type: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    
    # DoR/DoD
    dor_items: List[CheckboxItem] = field(default_factory=list)
    dod_items: List[CheckboxItem] = field(default_factory=list)
    dor_completed: int = 0
    dod_completed: int = 0
    
    # Acceptance Criteria
    acceptance_criteria: List[AcceptanceCriterion] = field(default_factory=list)
    
    # Additional fields
    description: Optional[str] = None
    technical_notes: Optional[str] = None
    risks: List[Dict[str, str]] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    related_links: List[str] = field(default_factory=list)
    
    # Files and commits
    files_to_modify: List[str] = field(default_factory=list)
    related_commits: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ADOTemplateParser:
    """Parser for ADO markdown templates"""
    
    # Regex patterns
    METADATA_PATTERN = r'\*\*(.+?):\*\*\s*(.+?)(?:\n|$)'
    CHECKBOX_PATTERN = r'^[\s]*[-*]\s*\[([xX\s])\]\s*(.+?)$'
    GIVEN_WHEN_THEN_PATTERN = r'\*\*Given:\*\*\s*(.+?)\n\s*\*\*When:\*\*\s*(.+?)\n\s*\*\*Then:\*\*\s*(.+?)(?:\n|$)'
    RISK_PATTERN = r'\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|'
    
    def __init__(self):
        self.current_section = None
        
    def parse_file(self, file_path: str) -> ParsedTemplate:
        """Parse an ADO template markdown file"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Template file not found: {file_path}")
            
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        return self.parse_content(content)
    
    def parse_content(self, content: str) -> ParsedTemplate:
        """Parse template content and extract all data"""
        template = ParsedTemplate()
        lines = content.split('\n')
        
        for i, line in enumerate(lines, start=1):
            # Track current section
            self._update_section(line)
            
            # Extract metadata
            if match := re.search(self.METADATA_PATTERN, line):
                self._extract_metadata(match, template)
            
            # Extract checkboxes
            if match := re.search(self.CHECKBOX_PATTERN, line):
                self._extract_checkbox(match, i, template)
            
            # Extract risks from table rows
            if '|' in line and self.current_section == 'risks':
                self._extract_risk(line, template)
        
        # Extract multi-line sections
        self._extract_acceptance_criteria(content, template)
        self._extract_description(content, template)
        self._extract_technical_notes(content, template)
        self._extract_dependencies(content, template)
        self._extract_files_and_commits(content, template)
        
        # Calculate completion percentages
        template.dor_completed = self._calculate_completion(template.dor_items)
        template.dod_completed = self._calculate_completion(template.dod_items)
        
        return template
    
    def _update_section(self, line: str):
        """Track which section we're currently parsing"""
        line_lower = line.lower()
        if '## definition of ready' in line_lower or '### definition of ready' in line_lower:
            self.current_section = 'dor'
        elif '## definition of done' in line_lower or '### definition of done' in line_lower:
            self.current_section = 'dod'
        elif '## acceptance criteria' in line_lower or '### acceptance criteria' in line_lower:
            self.current_section = 'acceptance_criteria'
        elif '## risk analysis' in line_lower or '### risk analysis' in line_lower:
            self.current_section = 'risks'
        elif line.startswith('## ') or line.startswith('### '):
            self.current_section = 'other'
    
    def _extract_metadata(self, match: re.Match, template: ParsedTemplate):
        """Extract metadata fields"""
        key = match.group(1).strip()
        value = match.group(2).strip()
        
        key_lower = key.lower()
        if 'ado' in key_lower or 'work item' in key_lower:
            template.ado_number = value
        elif 'title' in key_lower:
            template.title = value
        elif 'type' in key_lower:
            template.work_item_type = value
        elif 'priority' in key_lower:
            template.priority = value
        elif 'status' in key_lower:
            template.status = value
        elif 'created' in key_lower:
            template.created_at = value
        elif 'updated' in key_lower:
            template.updated_at = value
    
    def _extract_checkbox(self, match: re.Match, line_number: int, template: ParsedTemplate):
        """Extract checkbox items"""
        checked_char = match.group(1).strip()
        text = match.group(2).strip()
        checked = checked_char.lower() == 'x'
        
        checkbox = CheckboxItem(
            text=text,
            checked=checked,
            section=self.current_section or 'unknown',
            line_number=line_number
        )
        
        if self.current_section == 'dor':
            template.dor_items.append(checkbox)
        elif self.current_section == 'dod':
            template.dod_items.append(checkbox)
    
    def _extract_acceptance_criteria(self, content: str, template: ParsedTemplate):
        """Extract Given/When/Then acceptance criteria"""
        # Find acceptance criteria section
        ac_section = re.search(
            r'## Acceptance Criteria\s*(.+?)(?=\n##|\Z)',
            content,
            re.DOTALL | re.IGNORECASE
        )
        
        if not ac_section:
            return
        
        ac_content = ac_section.group(1)
        
        # Find all Given/When/Then blocks
        matches = re.finditer(
            r'\*\*Given:\*\*\s*(.+?)\s*\*\*When:\*\*\s*(.+?)\s*\*\*Then:\*\*\s*(.+?)(?=\n\n|\*\*Given:|\Z)',
            ac_content,
            re.DOTALL
        )
        
        for match in matches:
            criterion = AcceptanceCriterion(
                given=match.group(1).strip(),
                when=match.group(2).strip(),
                then=match.group(3).strip()
            )
            template.acceptance_criteria.append(criterion)
    
    def _extract_description(self, content: str, template: ParsedTemplate):
        """Extract description section"""
        desc_match = re.search(
            r'## Description\s*(.+?)(?=\n##|\Z)',
            content,
            re.DOTALL | re.IGNORECASE
        )
        if desc_match:
            template.description = desc_match.group(1).strip()
    
    def _extract_technical_notes(self, content: str, template: ParsedTemplate):
        """Extract technical notes section"""
        notes_match = re.search(
            r'## Technical Notes\s*(.+?)(?=\n##|\Z)',
            content,
            re.DOTALL | re.IGNORECASE
        )
        if notes_match:
            template.technical_notes = notes_match.group(1).strip()
    
    def _extract_dependencies(self, content: str, template: ParsedTemplate):
        """Extract dependencies and related links"""
        # Dependencies
        deps_match = re.search(
            r'## Dependencies\s*(.+?)(?=\n##|\Z)',
            content,
            re.DOTALL | re.IGNORECASE
        )
        if deps_match:
            deps_text = deps_match.group(1)
            # Extract items from bullet points
            template.dependencies = [
                line.strip('- ').strip()
                for line in deps_text.split('\n')
                if line.strip().startswith('-')
            ]
        
        # Related Links
        links_match = re.search(
            r'## Related Links\s*(.+?)(?=\n##|\Z)',
            content,
            re.DOTALL | re.IGNORECASE
        )
        if links_match:
            links_text = links_match.group(1)
            template.related_links = [
                line.strip('- ').strip()
                for line in links_text.split('\n')
                if line.strip().startswith('-')
            ]
    
    def _extract_files_and_commits(self, content: str, template: ParsedTemplate):
        """Extract files to modify and related commits"""
        # Files to modify
        files_match = re.search(
            r'## Files to Modify\s*(.+?)(?=\n##|\Z)',
            content,
            re.DOTALL | re.IGNORECASE
        )
        if files_match:
            files_text = files_match.group(1)
            template.files_to_modify = [
                line.strip('- ').strip().strip('`')
                for line in files_text.split('\n')
                if line.strip().startswith('-')
            ]
        
        # Related commits
        commits_match = re.search(
            r'## Related Commits\s*(.+?)(?=\n##|\Z)',
            content,
            re.DOTALL | re.IGNORECASE
        )
        if commits_match:
            commits_text = commits_match.group(1)
            template.related_commits = [
                line.strip('- ').strip()
                for line in commits_text.split('\n')
                if line.strip().startswith('-')
            ]
    
    def _extract_risk(self, line: str, template: ParsedTemplate):
        """Extract risk from table row"""
        if match := re.search(self.RISK_PATTERN, line):
            risk_name = match.group(1).strip()
            impact = match.group(2).strip()
            mitigation = match.group(3).strip()
            
            # Skip header row
            if risk_name.lower() != 'risk' and '---' not in risk_name:
                template.risks.append({
                    'name': risk_name,
                    'impact': impact,
                    'mitigation': mitigation
                })
    
    def _calculate_completion(self, items: List[CheckboxItem]) -> int:
        """Calculate completion percentage for checkbox items"""
        if not items:
            return 0
        checked_count = sum(1 for item in items if item.checked)
        return int((checked_count / len(items)) * 100)
    
    def to_dict(self, template: ParsedTemplate) -> Dict:
        """Convert parsed template to dictionary for database storage"""
        return {
            'ado_number': template.ado_number,
            'title': template.title,
            'work_item_type': template.work_item_type,
            'priority': template.priority,
            'status': template.status,
            'description': template.description,
            'technical_notes': template.technical_notes,
            'dor_completed': template.dor_completed,
            'dod_completed': template.dod_completed,
            'dor_items': [
                {'text': item.text, 'checked': item.checked}
                for item in template.dor_items
            ],
            'dod_items': [
                {'text': item.text, 'checked': item.checked}
                for item in template.dod_items
            ],
            'acceptance_criteria': [
                {'given': ac.given, 'when': ac.when, 'then': ac.then, 'priority': ac.priority}
                for ac in template.acceptance_criteria
            ],
            'risks': template.risks,
            'dependencies': template.dependencies,
            'related_links': template.related_links,
            'files_to_modify': template.files_to_modify,
            'related_commits': template.related_commits,
            'created_at': template.created_at,
            'updated_at': template.updated_at
        }
    
    def generate_summary(self, template: ParsedTemplate) -> str:
        """Generate a human-readable summary of the parsed template"""
        lines = [
            f"📋 ADO Template Summary",
            f"{'=' * 50}",
            f"",
            f"ADO Number: {template.ado_number or 'N/A'}",
            f"Title: {template.title or 'N/A'}",
            f"Type: {template.work_item_type or 'N/A'}",
            f"Priority: {template.priority or 'N/A'}",
            f"Status: {template.status or 'N/A'}",
            f"",
            f"📊 Progress:",
            f"  DoR: {template.dor_completed}% complete ({sum(1 for i in template.dor_items if i.checked)}/{len(template.dor_items)} items)",
            f"  DoD: {template.dod_completed}% complete ({sum(1 for i in template.dod_items if i.checked)}/{len(template.dod_items)} items)",
            f"",
            f"✅ Acceptance Criteria: {len(template.acceptance_criteria)} defined",
            f"⚠️  Risks: {len(template.risks)} identified",
            f"🔗 Dependencies: {len(template.dependencies)}",
            f"📁 Files to Modify: {len(template.files_to_modify)}",
        ]
        
        return '\n'.join(lines)


# Integration with ADO Manager
def update_ado_from_template(template_path: str, ado_manager) -> bool:
    """Parse template and update ADO item in database"""
    parser = ADOTemplateParser()
    
    try:
        # Parse the template
        parsed = parser.parse_file(template_path)
        
        if not parsed.ado_number:
            print("❌ Error: No ADO number found in template")
            return False
        
        # Convert to dict for database update
        data = parser.to_dict(parsed)
        
        # Update the ADO item
        success = ado_manager.update_ado(
            ado_number=parsed.ado_number,
            dor_completed=parsed.dor_completed,
            dod_completed=parsed.dod_completed,
            status=parsed.status,
            priority=parsed.priority,
            # Store structured data as JSON
            acceptance_criteria=json.dumps(data['acceptance_criteria']),
            technical_notes=parsed.technical_notes
        )
        
        if success:
            print(f"✅ Updated ADO {parsed.ado_number}")
            print(f"   DoR: {parsed.dor_completed}% | DoD: {parsed.dod_completed}%")
            return True
        else:
            print(f"❌ Failed to update ADO {parsed.ado_number}")
            return False
            
    except Exception as e:
        print(f"❌ Error parsing template: {e}")
        return False


# CLI interface
def main():
    """Test the parser with a sample template"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python parse_ado_template.py <template_file>")
        print("\nExample: python parse_ado_template.py cortex-brain/templates/ado/base-template.md")
        return
    
    template_file = sys.argv[1]
    parser = ADOTemplateParser()
    
    try:
        # Parse the template
        parsed = parser.parse_file(template_file)
        
        # Display summary
        print(parser.generate_summary(parsed))
        
        # Show detailed breakdown
        print("\n📋 Definition of Ready:")
        for item in parsed.dor_items:
            status = "✅" if item.checked else "☐"
            print(f"  {status} {item.text}")
        
        print("\n📋 Definition of Done:")
        for item in parsed.dod_items:
            status = "✅" if item.checked else "☐"
            print(f"  {status} {item.text}")
        
        if parsed.acceptance_criteria:
            print("\n✅ Acceptance Criteria:")
            for i, ac in enumerate(parsed.acceptance_criteria, 1):
                print(f"  {i}. Given: {ac.given}")
                print(f"     When: {ac.when}")
                print(f"     Then: {ac.then}")
        
        if parsed.risks:
            print("\n⚠️  Risks:")
            for risk in parsed.risks:
                print(f"  • {risk['name']}")
                print(f"    Impact: {risk['impact']}")
                print(f"    Mitigation: {risk['mitigation']}")
        
        print(f"\n✅ Template parsed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
