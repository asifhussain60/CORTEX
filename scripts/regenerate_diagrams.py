#!/usr/bin/env python3
"""
CORTEX Diagram Regeneration Script
Regenerates all diagram documentation: prompts, narratives, and mermaid diagrams

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import os
import sys
from pathlib import Path
import yaml
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

class DiagramRegenerator:
    """Handles regeneration of all CORTEX diagram documentation"""
    
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.diagrams_path = root_path / "docs" / "diagrams"
        self.prompts_path = self.diagrams_path / "prompts"
        self.narratives_path = self.diagrams_path / "narratives"
        self.mermaid_path = self.diagrams_path / "mermaid"
        self.img_path = self.diagrams_path / "img"
        
        # Diagram definitions
        self.diagrams = [
            {"id": "01", "name": "tier-architecture", "title": "4-Tier Brain Architecture"},
            {"id": "02", "name": "agent-system", "title": "10 Specialized Agents"},
            {"id": "03", "name": "plugin-architecture", "title": "Plugin System Architecture"},
            {"id": "04", "name": "memory-flow", "title": "Memory Flow Pipeline"},
            {"id": "05", "name": "agent-coordination", "title": "Agent Coordination Flow"},
            {"id": "06", "name": "basement-scene", "title": "Basement Meeting Scene"},
            {"id": "07", "name": "cortex-one-pager", "title": "CORTEX One-Pager Overview"},
            {"id": "08", "name": "knowledge-graph", "title": "Knowledge Graph (Tier 2)"},
            {"id": "09", "name": "context-intelligence", "title": "Context Intelligence (Tier 3)"},
            {"id": "10", "name": "feature-planning", "title": "Feature Planning Workflow"},
            {"id": "11", "name": "performance-benchmarks", "title": "Performance Benchmarks"},
            {"id": "12", "name": "token-optimization", "title": "Token Optimization Strategy"},
            {"id": "13", "name": "plugin-system", "title": "Plugin System Details"},
            {"id": "14", "name": "data-flow-complete", "title": "Complete Data Flow"},
            {"id": "15", "name": "before-vs-after", "title": "Before vs After Comparison"},
            {"id": "16", "name": "technical-documentation", "title": "Technical Documentation"},
            {"id": "17", "name": "executive-feature-list", "title": "Executive Feature List"},
        ]
    
    def verify_structure(self) -> dict:
        """Verify all required folders and files exist"""
        status = {
            "folders": {},
            "prompts": {"exists": 0, "missing": []},
            "narratives": {"exists": 0, "missing": []},
            "mermaid": {"exists": 0, "missing": []},
            "images": {"exists": 0, "missing": []}
        }
        
        # Check folders
        for folder_name, folder_path in [
            ("prompts", self.prompts_path),
            ("narratives", self.narratives_path),
            ("mermaid", self.mermaid_path),
            ("img", self.img_path)
        ]:
            status["folders"][folder_name] = folder_path.exists()
            if not folder_path.exists():
                print(f"❌ Missing folder: {folder_path}")
                folder_path.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created folder: {folder_path}")
        
        # Check files
        for diagram in self.diagrams:
            file_id = diagram["id"]
            file_name = diagram["name"]
            
            # Prompts
            prompt_file = self.prompts_path / f"{file_id}-{file_name}.md"
            if prompt_file.exists():
                status["prompts"]["exists"] += 1
            else:
                status["prompts"]["missing"].append(str(prompt_file))
            
            # Narratives
            narrative_file = self.narratives_path / f"{file_id}-{file_name}.md"
            if narrative_file.exists():
                status["narratives"]["exists"] += 1
            else:
                status["narratives"]["missing"].append(str(narrative_file))
            
            # Mermaid
            mermaid_file = self.mermaid_path / f"{file_id}-{file_name}.mmd"
            if mermaid_file.exists():
                status["mermaid"]["exists"] += 1
            else:
                status["mermaid"]["missing"].append(str(mermaid_file))
            
            # Images
            img_file = self.img_path / f"{file_id}-{file_name}.png"
            if img_file.exists():
                status["images"]["exists"] += 1
            else:
                status["images"]["missing"].append(str(img_file))
        
        return status
    
    def generate_report(self) -> str:
        """Generate a comprehensive status report"""
        status = self.verify_structure()
        
        report = [
            "=" * 80,
            "CORTEX DIAGRAM DOCUMENTATION STATUS",
            "=" * 80,
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Diagrams: {len(self.diagrams)}",
            "",
            "FOLDER STRUCTURE:",
            "-" * 80,
        ]
        
        for folder, exists in status["folders"].items():
            status_icon = "✅" if exists else "❌"
            report.append(f"{status_icon} {folder.upper()}: {exists}")
        
        report.extend([
            "",
            "FILE STATUS:",
            "-" * 80,
        ])
        
        for file_type in ["prompts", "narratives", "mermaid", "images"]:
            exists = status[file_type]["exists"]
            total = len(self.diagrams)
            percentage = (exists / total * 100) if total > 0 else 0
            status_icon = "✅" if exists == total else "⚠️"
            
            report.append(f"{status_icon} {file_type.upper()}: {exists}/{total} ({percentage:.1f}%)")
            
            if status[file_type]["missing"]:
                report.append(f"   Missing files:")
                for missing_file in status[file_type]["missing"][:5]:  # Show first 5
                    report.append(f"   - {Path(missing_file).name}")
                if len(status[file_type]["missing"]) > 5:
                    report.append(f"   ... and {len(status[file_type]['missing']) - 5} more")
        
        report.extend([
            "",
            "=" * 80,
            "SUMMARY:",
            "-" * 80,
        ])
        
        total_files = len(self.diagrams) * 4  # prompts, narratives, mermaid, images
        existing_files = (
            status["prompts"]["exists"] +
            status["narratives"]["exists"] +
            status["mermaid"]["exists"] +
            status["images"]["exists"]
        )
        
        report.append(f"Total Files: {existing_files}/{total_files} ({existing_files/total_files*100:.1f}%)")
        
        if existing_files == total_files:
            report.append("✅ All diagram documentation is complete!")
        else:
            missing_count = total_files - existing_files
            report.append(f"⚠️ {missing_count} files need to be created or restored")
        
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_report(self, filename: str = "diagram-status-report.txt"):
        """Save the status report to a file"""
        report = self.generate_report()
        report_path = self.diagrams_path / filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ Report saved to: {report_path}")
        return report_path
    
    def create_index(self):
        """Create an index of all diagrams"""
        index_content = [
            "# CORTEX Diagram Index",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total Diagrams:** {len(self.diagrams)}",
            "",
            "## Diagram List",
            "",
            "| # | Name | Prompt | Narrative | Mermaid | Image |",
            "|---|------|--------|-----------|---------|-------|",
        ]
        
        for diagram in self.diagrams:
            file_id = diagram["id"]
            file_name = diagram["name"]
            title = diagram["title"]
            
            prompt_exists = (self.prompts_path / f"{file_id}-{file_name}.md").exists()
            narrative_exists = (self.narratives_path / f"{file_id}-{file_name}.md").exists()
            mermaid_exists = (self.mermaid_path / f"{file_id}-{file_name}.mmd").exists()
            image_exists = (self.img_path / f"{file_id}-{file_name}.png").exists()
            
            prompt_icon = "✅" if prompt_exists else "❌"
            narrative_icon = "✅" if narrative_exists else "❌"
            mermaid_icon = "✅" if mermaid_exists else "❌"
            image_icon = "✅" if image_exists else "❌"
            
            index_content.append(
                f"| {file_id} | {title} | {prompt_icon} | {narrative_icon} | {mermaid_icon} | {image_icon} |"
            )
        
        index_content.extend([
            "",
            "## Legend",
            "",
            "- ✅ File exists",
            "- ❌ File missing",
            "",
            "## File Paths",
            "",
            f"- **Prompts:** `{self.prompts_path.relative_to(self.root_path)}/`",
            f"- **Narratives:** `{self.narratives_path.relative_to(self.root_path)}/`",
            f"- **Mermaid:** `{self.mermaid_path.relative_to(self.root_path)}/`",
            f"- **Images:** `{self.img_path.relative_to(self.root_path)}/`",
            "",
            "---",
            "",
            "**Author:** Asif Hussain",
            "**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.",
            "**Repository:** github.com/asifhussain60/CORTEX",
        ])
        
        index_path = self.diagrams_path / "DIAGRAM-INDEX.md"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(index_content))
        
        print(f"✅ Index created: {index_path}")
        return index_path


def main():
    """Main entry point"""
    print("🧠 CORTEX Diagram Regeneration System")
    print("=" * 80)
    
    # Get root path from script location (scripts/ -> CORTEX/)
    root_path = Path(__file__).parent.parent
    print(f"Root path: {root_path}")
    regenerator = DiagramRegenerator(root_path)
    
    # Generate and print report
    report = regenerator.generate_report()
    print(report)
    
    # Save report
    regenerator.save_report()
    
    # Create index
    regenerator.create_index()
    
    print("\n✅ Diagram regeneration complete!")


if __name__ == "__main__":
    main()
