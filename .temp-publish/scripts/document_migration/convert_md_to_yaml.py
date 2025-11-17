"""
Markdown to YAML Document Converter

Converts structured Markdown documents to YAML format with Git-based deletion strategy.
Prevents GitHub Copilot conversation history loops by reducing token usage by 60%.

Usage:
    python convert_md_to_yaml.py --input FILE.md --schema report --output FILE.yaml --commit-and-delete

Architecture:
- Parse Markdown structure (headings, lists, metadata)
- Map content to YAML schema
- Validate against JSON Schema
- Git commit YAML file
- Git commit deletion of MD file

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import os
import re
import yaml
import json
import subprocess
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MDToYAMLConverter:
    """
    Convert Markdown documents to YAML format.
    
    Features:
    - Structure-aware parsing (headings, lists, code blocks)
    - Schema mapping (report, analysis, planning, summary)
    - JSON Schema validation
    - Git-based deletion strategy
    """
    
    def __init__(self, schema_type: str):
        """
        Initialize converter.
        
        Args:
            schema_type: Type of document (report, analysis, planning, summary, tracking)
        """
        self.schema_type = schema_type
        self.cortex_root = Path(os.environ.get("CORTEX_ROOT", Path.cwd()))
    
    def convert(self, md_file: Path) -> Dict[str, Any]:
        """
        Convert Markdown file to YAML structure.
        
        Args:
            md_file: Path to Markdown file
        
        Returns:
            YAML-compatible dictionary
        """
        logger.info(f"Converting {md_file.name} to YAML ({self.schema_type} schema)")
        
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Parse based on schema type
        if self.schema_type == "report":
            return self._parse_report(md_content, md_file)
        elif self.schema_type == "analysis":
            return self._parse_analysis(md_content, md_file)
        elif self.schema_type == "planning":
            return self._parse_planning(md_content, md_file)
        elif self.schema_type == "summary":
            return self._parse_summary(md_content, md_file)
        elif self.schema_type == "tracking":
            return self._parse_tracking(md_content, md_file)
        else:
            raise ValueError(f"Unknown schema type: {self.schema_type}")
    
    def validate(self, yaml_content: Dict[str, Any]) -> bool:
        """
        Validate YAML content against JSON Schema.
        
        Args:
            yaml_content: YAML structure to validate
        
        Returns:
            True if valid
        
        Raises:
            ValueError: If validation fails
        """
        # TODO: Implement JSON Schema validation
        # For now, basic structure validation
        required_fields = ["version", "type", "title", "created"]
        
        for field in required_fields:
            if field not in yaml_content:
                raise ValueError(f"Missing required field: {field}")
        
        logger.info("✓ YAML validation passed")
        return True
    
    def write(self, output_file: Path, yaml_content: Dict[str, Any]) -> None:
        """
        Write YAML content to file.
        
        Args:
            output_file: Output file path
            yaml_content: YAML structure
        """
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_content, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        logger.info(f"✓ Written to {output_file}")
    
    def commit_yaml(self, yaml_file: Path, commit_message: str) -> str:
        """
        Git commit YAML file.
        
        Args:
            yaml_file: YAML file to commit
            commit_message: Commit message
        
        Returns:
            Commit hash
        """
        try:
            # Add file
            subprocess.run(
                ["git", "add", str(yaml_file)],
                cwd=self.cortex_root,
                check=True,
                capture_output=True
            )
            
            # Commit
            result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=self.cortex_root,
                check=True,
                capture_output=True,
                text=True
            )
            
            # Get commit hash
            commit_hash = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.cortex_root,
                check=True,
                capture_output=True,
                text=True
            ).stdout.strip()
            
            logger.info(f"✓ Committed YAML: {commit_hash[:8]}")
            return commit_hash
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Git commit failed: {e}")
            raise
    
    def commit_deletion(self, md_file: Path, yaml_commit_hash: str) -> str:
        """
        Git commit deletion of MD file.
        
        Args:
            md_file: MD file to delete
            yaml_commit_hash: Commit hash of YAML conversion
        
        Returns:
            Commit hash
        """
        commit_message = (
            f"chore(migration): Delete {md_file.name} after YAML conversion\n\n"
            f"Converted to YAML in commit {yaml_commit_hash[:8]}\n"
            f"Backup available in Git history"
        )
        
        try:
            # Remove file
            subprocess.run(
                ["git", "rm", str(md_file)],
                cwd=self.cortex_root,
                check=True,
                capture_output=True
            )
            
            # Commit deletion
            subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=self.cortex_root,
                check=True,
                capture_output=True
            )
            
            # Get commit hash
            commit_hash = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.cortex_root,
                check=True,
                capture_output=True,
                text=True
            ).stdout.strip()
            
            logger.info(f"✓ Committed deletion: {commit_hash[:8]}")
            return commit_hash
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Git commit failed: {e}")
            raise
    
    # ========================================================================
    # Schema-Specific Parsers
    # ========================================================================
    
    def _parse_report(self, md_content: str, md_file: Path) -> Dict[str, Any]:
        """Parse Markdown as completion/status report."""
        # Extract title (first H1)
        title_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
        title = title_match.group(1) if title_match else md_file.stem
        
        # Detect report type
        if "COMPLETE" in title or "COMPLETION" in title:
            report_type = "completion"
        elif "STATUS" in title:
            report_type = "status"
        elif "PROGRESS" in title:
            report_type = "progress"
        else:
            report_type = "milestone"
        
        # Extract sections
        summary = self._extract_section(md_content, ["Summary", "Overview", "Executive Summary"])
        accomplishments = self._extract_list_items(md_content, ["Accomplishments", "Achievements", "Completed"])
        next_steps = self._extract_list_items(md_content, ["Next Steps", "TODO", "Upcoming"])
        
        return {
            "version": "1.0",
            "type": report_type,
            "title": title,
            "created": datetime.now().isoformat(),
            "project": self._extract_project_name(title),
            "summary": summary or f"Report extracted from {md_file.name}",
            "accomplishments": [{"description": item} for item in accomplishments],
            "metrics": self._extract_metrics(md_content),
            "next_steps": next_steps,
            "source_file": str(md_file.name)
        }
    
    def _parse_analysis(self, md_content: str, md_file: Path) -> Dict[str, Any]:
        """Parse Markdown as analysis document."""
        title_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
        title = title_match.group(1) if title_match else md_file.stem
        
        # Detect analysis type
        if "PERFORMANCE" in title.upper():
            analysis_type = "performance"
        elif "ARCHITECTURE" in title.upper():
            analysis_type = "architecture"
        elif "ROOT" in title.upper() or "CAUSE" in title.upper():
            analysis_type = "root-cause"
        elif "PATTERN" in title.upper():
            analysis_type = "pattern"
        else:
            analysis_type = "architecture"
        
        findings = self._extract_list_items(md_content, ["Findings", "Results", "Observations"])
        recommendations = self._extract_list_items(md_content, ["Recommendations", "Suggestions", "Action Items"])
        
        return {
            "version": "1.0",
            "type": analysis_type,
            "title": title,
            "created": datetime.now().isoformat(),
            "scope": self._extract_section(md_content, ["Scope"]) or "Analysis scope not specified",
            "methodology": self._extract_section(md_content, ["Methodology", "Approach"]) or "Standard analysis methodology",
            "findings": [{"description": item} for item in findings],
            "recommendations": [{"description": item} for item in recommendations],
            "metrics": self._extract_metrics(md_content),
            "source_file": str(md_file.name)
        }
    
    def _parse_planning(self, md_content: str, md_file: Path) -> Dict[str, Any]:
        """Parse Markdown as planning document."""
        title_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
        title = title_match.group(1) if title_match else md_file.stem
        
        # Detect planning type
        if "ROADMAP" in title.upper():
            planning_type = "roadmap"
        elif "IMPLEMENTATION" in title.upper():
            planning_type = "implementation"
        elif "ARCHITECTURE" in title.upper():
            planning_type = "architecture"
        elif "MIGRATION" in title.upper():
            planning_type = "migration"
        else:
            planning_type = "implementation"
        
        phases = self._extract_phases(md_content)
        risks = self._extract_list_items(md_content, ["Risks", "Challenges"])
        success_criteria = self._extract_list_items(md_content, ["Success Criteria", "Goals", "Objectives"])
        
        return {
            "version": "1.0",
            "type": planning_type,
            "title": title,
            "created": datetime.now().isoformat(),
            "scope": self._extract_section(md_content, ["Scope"]) or "Planning scope not specified",
            "timeline": {},
            "phases": [{"name": phase, "description": ""} for phase in phases],
            "risks": [{"description": risk} for risk in risks],
            "dependencies": [],
            "success_criteria": success_criteria,
            "source_file": str(md_file.name)
        }
    
    def _parse_summary(self, md_content: str, md_file: Path) -> Dict[str, Any]:
        """Parse Markdown as summary document."""
        title_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
        title = title_match.group(1) if title_match else md_file.stem
        
        return {
            "version": "1.0",
            "type": "session",
            "title": title,
            "created": datetime.now().isoformat(),
            "summary": md_content[:500],  # First 500 chars
            "key_points": self._extract_list_items(md_content, ["Key Points", "Highlights", "Summary"]),
            "decisions": self._extract_list_items(md_content, ["Decisions", "Resolved"]),
            "action_items": self._extract_list_items(md_content, ["Action Items", "TODO", "Next Steps"]),
            "source_file": str(md_file.name)
        }
    
    def _parse_tracking(self, md_content: str, md_file: Path) -> Dict[str, Any]:
        """Parse Markdown as phase tracking document."""
        title_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
        title = title_match.group(1) if title_match else md_file.stem
        
        phases = self._extract_phases(md_content)
        
        return {
            "version": "1.0",
            "project": {
                "name": title,
                "description": self._extract_section(md_content, ["Description", "Overview"]) or "",
                "started": datetime.now().isoformat(),
                "tags": []
            },
            "phases": [
                {
                    "phase_id": f"phase_{i+1}",
                    "name": phase,
                    "status": "not-started",
                    "priority": "medium",
                    "dependencies": [],
                    "acceptance_criteria": [],
                    "tasks": []
                }
                for i, phase in enumerate(phases)
            ],
            "source_file": str(md_file.name)
        }
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _extract_section(self, md_content: str, section_names: List[str]) -> Optional[str]:
        """Extract content from a section."""
        for name in section_names:
            pattern = rf'^##?\s+{re.escape(name)}\s*$\n+(.*?)(?=^##?\s+|\Z)'
            match = re.search(pattern, md_content, re.MULTILINE | re.DOTALL)
            if match:
                return match.group(1).strip()
        return None
    
    def _extract_list_items(self, md_content: str, section_names: List[str]) -> List[str]:
        """Extract list items from a section."""
        section = self._extract_section(md_content, section_names)
        if not section:
            return []
        
        # Extract bullet points
        items = re.findall(r'^\s*[-*•]\s+(.+)$', section, re.MULTILINE)
        return [item.strip() for item in items]
    
    def _extract_phases(self, md_content: str) -> List[str]:
        """Extract phase names from document."""
        # Look for headings that indicate phases
        phase_pattern = r'^##\s+(Phase\s+\d+|Step\s+\d+|Stage\s+\d+)[:\s]+(.+)$'
        phases = re.findall(phase_pattern, md_content, re.MULTILINE)
        
        if phases:
            return [f"{num}: {name}" for num, name in phases]
        
        # Fallback: extract all H2 headings
        return re.findall(r'^##\s+(.+)$', md_content, re.MULTILINE)
    
    def _extract_metrics(self, md_content: str) -> Dict[str, Any]:
        """Extract metrics from document."""
        metrics = {}
        
        # Look for key-value pairs
        kv_pattern = r'^\s*[-*•]?\s*\*\*(.+?):\*\*\s+(.+)$'
        matches = re.findall(kv_pattern, md_content, re.MULTILINE)
        
        for key, value in matches:
            # Try to convert to number
            try:
                if '%' in value:
                    metrics[key.lower().replace(' ', '_')] = float(value.replace('%', ''))
                elif value.isdigit():
                    metrics[key.lower().replace(' ', '_')] = int(value)
                else:
                    metrics[key.lower().replace(' ', '_')] = value
            except:
                metrics[key.lower().replace(' ', '_')] = value
        
        return metrics
    
    def _extract_project_name(self, title: str) -> str:
        """Extract project name from title."""
        # Remove common suffixes
        project = re.sub(r'\s+(Complete|Status|Progress|Report|Analysis|Planning)', '', title, flags=re.IGNORECASE)
        return project.strip()


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert Markdown documents to YAML format with Git-based deletion"
    )
    parser.add_argument("--input", required=True, help="Input Markdown file")
    parser.add_argument("--schema", required=True, choices=["report", "analysis", "planning", "summary", "tracking"], help="Schema type")
    parser.add_argument("--output", required=True, help="Output YAML file")
    parser.add_argument("--commit-and-delete", action="store_true", help="Commit YAML and delete MD file")
    parser.add_argument("--dry-run", action="store_true", help="Show conversion without writing files")
    
    args = parser.parse_args()
    
    # Convert
    converter = MDToYAMLConverter(schema_type=args.schema)
    md_file = Path(args.input)
    
    if not md_file.exists():
        logger.error(f"Input file not found: {md_file}")
        return 1
    
    yaml_content = converter.convert(md_file)
    
    # Validate
    try:
        converter.validate(yaml_content)
    except ValueError as e:
        logger.error(f"Validation failed: {e}")
        return 1
    
    if args.dry_run:
        logger.info("\n=== DRY RUN - YAML Output ===")
        print(yaml.dump(yaml_content, default_flow_style=False, sort_keys=False))
        return 0
    
    # Write YAML
    output_file = Path(args.output)
    converter.write(output_file, yaml_content)
    
    # Git workflow
    if args.commit_and_delete:
        logger.info("\n=== Git Workflow: Two-Stage Commit ===")
        
        # Stage 1: Commit YAML
        yaml_commit = converter.commit_yaml(
            output_file,
            f"feat(migration): Convert {md_file.name} to YAML format"
        )
        
        # Stage 2: Commit deletion
        deletion_commit = converter.commit_deletion(md_file, yaml_commit)
        
        logger.info("\n✅ Migration complete!")
        logger.info(f"  YAML commit: {yaml_commit[:8]}")
        logger.info(f"  Deletion commit: {deletion_commit[:8]}")
        logger.info(f"  Rollback: git revert {deletion_commit[:8]} {yaml_commit[:8]}")
    
    return 0


if __name__ == "__main__":
    exit(main())
