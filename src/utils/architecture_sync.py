#!/usr/bin/env python3
"""
Architecture Synchronization Utility

Auto-updates ARCHITECTURE.md with current system state during deployments.
Part of Phase 2 Deliverable 2.1 - Deploy-Triggered Architecture Updates

This module:
1. Scans src/ for agents and orchestrators
2. Updates ARCHITECTURE.md with current counts
3. Synchronizes capabilities from capabilities.yaml
4. Updates version and timestamp
5. Validates diagram references

Usage:
    from src.utils.architecture_sync import ArchitectureSync
    
    sync = ArchitectureSync()
    sync.update_architecture_doc()

Author: Asif Hussain
License: Source-Available (Use Allowed, No Contributions)
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import yaml


class ArchitectureSync:
    """Synchronizes ARCHITECTURE.md with current codebase state."""
    
    def __init__(self, cortex_root: Path = None):
        """
        Initialize architecture sync.
        
        Args:
            cortex_root: Root directory of CORTEX project
        """
        if cortex_root is None:
            # Auto-detect: this file is in src/utils/
            cortex_root = Path(__file__).parent.parent.parent
        
        self.cortex_root = cortex_root
        self.architecture_doc = cortex_root / "docs" / "ARCHITECTURE.md"
        self.capabilities_file = cortex_root / "cortex-brain" / "capabilities.yaml"
        self.version_file = cortex_root / "VERSION"
    
    def count_agents(self) -> int:
        """Count total number of agent files in src/cortex_agents/."""
        agents_dir = self.cortex_root / "src" / "cortex_agents"
        if not agents_dir.exists():
            return 0
        
        # Count Python files excluding __init__.py and base classes
        agent_files = [
            f for f in agents_dir.rglob("*.py")
            if f.name not in ["__init__.py", "base_agent.py", "agent_types.py"]
        ]
        return len(agent_files)
    
    def count_orchestrators(self) -> int:
        """Count total number of orchestrator files in src/orchestrators/."""
        orchestrators_dir = self.cortex_root / "src" / "orchestrators"
        if not orchestrators_dir.exists():
            return 0
        
        # Count Python files excluding __init__.py
        orchestrator_files = [
            f for f in orchestrators_dir.rglob("*.py")
            if f.name not in ["__init__.py"]
        ]
        return len(orchestrator_files)
    
    def get_version(self) -> str:
        """Get current CORTEX version from VERSION file."""
        if not self.version_file.exists():
            return "3.2.0"  # Default fallback
        
        try:
            with open(self.version_file, 'r') as f:
                content = f.read().strip()
                # Extract version number (first line, format: "CORTEX Version: X.Y.Z")
                match = re.search(r'(\d+\.\d+\.\d+)', content)
                if match:
                    return match.group(1)
                return "3.2.0"
        except Exception:
            return "3.2.0"
    
    def get_capabilities_count(self) -> int:
        """Count capabilities from capabilities.yaml."""
        if not self.capabilities_file.exists():
            return 0
        
        try:
            with open(self.capabilities_file, 'r') as f:
                data = yaml.safe_load(f)
                if isinstance(data, dict) and 'capabilities' in data:
                    return len(data['capabilities'])
                return 0
        except Exception:
            return 0
    
    def analyze_tier_databases(self) -> Dict[str, str]:
        """Analyze tier databases and return their status."""
        tier_dbs = {
            'tier1': self.cortex_root / "cortex-brain" / "tier1-working-memory.db",
            'tier2': self.cortex_root / "cortex-brain" / "tier2-knowledge-graph.db",
            'tier3': self.cortex_root / "cortex-brain" / "tier3-development-context.db",
        }
        
        status = {}
        for tier, db_path in tier_dbs.items():
            if db_path.exists():
                size_mb = db_path.stat().st_size / (1024 * 1024)
                status[tier] = f"✅ Active ({size_mb:.2f} MB)"
            else:
                status[tier] = "⚠️ Not initialized"
        
        return status
    
    def update_architecture_doc(self) -> Tuple[bool, str]:
        """
        Update ARCHITECTURE.md with current system state.
        
        Returns:
            Tuple of (success, message)
        """
        if not self.architecture_doc.exists():
            return False, f"ARCHITECTURE.md not found at {self.architecture_doc}"
        
        try:
            # Read current document
            with open(self.architecture_doc, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Collect current system stats
            agent_count = self.count_agents()
            orchestrator_count = self.count_orchestrators()
            version = self.get_version()
            capabilities_count = self.get_capabilities_count()
            tier_status = self.analyze_tier_databases()
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            # Update version number
            content = re.sub(
                r'\*\*Version:\*\* \d+\.\d+\.\d+',
                f'**Version:** {version}',
                content
            )
            
            # Update date in frontmatter
            content = re.sub(
                r'date: \d{4}-\d{2}-\d{2}',
                f'date: {current_date}',
                content
            )
            
            # Update system overview agent count
            content = re.sub(
                r'\*\*\d+-agent intelligent routing system\*\*',
                f'**{agent_count}-agent intelligent routing system**',
                content
            )
            
            # Update system overview orchestrator count
            content = re.sub(
                r'\*\*\d+-orchestrator workflow system\*\*',
                f'**{orchestrator_count}-orchestrator workflow system**',
                content
            )
            
            # Update agent system section
            content = re.sub(
                r'CORTEX uses \d+ specialized agents',
                f'CORTEX uses {agent_count} specialized agents',
                content
            )
            
            # Update orchestrator system section
            content = re.sub(
                r'CORTEX implements \d+ orchestrators',
                f'CORTEX implements {orchestrator_count} orchestrators',
                content
            )
            
            # Add synchronization timestamp comment at top of file
            sync_marker = f"<!-- Architecture synchronized: {datetime.now().isoformat()} -->\n"
            if "<!-- Architecture synchronized:" not in content:
                # Add after frontmatter
                frontmatter_end = content.find('---\n', 3)
                if frontmatter_end != -1:
                    content = content[:frontmatter_end + 4] + sync_marker + content[frontmatter_end + 4:]
            else:
                # Update existing marker
                content = re.sub(
                    r'<!-- Architecture synchronized: .* -->',
                    sync_marker.strip(),
                    content
                )
            
            # Write updated document
            with open(self.architecture_doc, 'w', encoding='utf-8') as f:
                f.write(content)
            
            message = f"""Architecture document synchronized:
  - Version: {version}
  - Date: {current_date}
  - Agents: {agent_count}
  - Orchestrators: {orchestrator_count}
  - Capabilities: {capabilities_count}
  - Tier 1 DB: {tier_status.get('tier1', 'Unknown')}
  - Tier 2 DB: {tier_status.get('tier2', 'Unknown')}
  - Tier 3 DB: {tier_status.get('tier3', 'Unknown')}
"""
            
            return True, message
        
        except Exception as e:
            return False, f"Error updating ARCHITECTURE.md: {e}"
    
    def validate_diagram_references(self) -> List[str]:
        """
        Validate that all diagram references in ARCHITECTURE.md exist.
        
        Returns:
            List of missing diagram files
        """
        if not self.architecture_doc.exists():
            return ["ARCHITECTURE.md not found"]
        
        missing = []
        
        try:
            with open(self.architecture_doc, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all diagram references (Mermaid and DALL-E prompts)
            mermaid_refs = re.findall(r'diagrams/mermaid/([^\s\)]+\.mmd)', content)
            dalle_refs = re.findall(r'diagrams/prompts/([^\s\)]+\.md)', content)
            
            # Check Mermaid files
            for ref in mermaid_refs:
                diagram_path = self.cortex_root / "diagrams" / "mermaid" / ref
                if not diagram_path.exists():
                    missing.append(f"diagrams/mermaid/{ref}")
            
            # Check DALL-E prompt files
            for ref in dalle_refs:
                prompt_path = self.cortex_root / "diagrams" / "prompts" / ref
                if not prompt_path.exists():
                    missing.append(f"diagrams/prompts/{ref}")
        
        except Exception as e:
            missing.append(f"Error validating references: {e}")
        
        return missing


def main():
    """CLI entry point for architecture synchronization."""
    import sys
    
    print("🔄 CORTEX Architecture Synchronization")
    print("=" * 70)
    
    sync = ArchitectureSync()
    
    # Update architecture document
    print("\n📝 Updating ARCHITECTURE.md...")
    success, message = sync.update_architecture_doc()
    
    if success:
        print("✅ Success!")
        print(message)
    else:
        print(f"❌ Failed: {message}")
        sys.exit(1)
    
    # Validate diagram references
    print("\n🔍 Validating diagram references...")
    missing = sync.validate_diagram_references()
    
    if missing:
        print(f"⚠️  Warning: {len(missing)} diagram reference(s) not found:")
        for ref in missing:
            print(f"  - {ref}")
    else:
        print("✅ All diagram references valid")
    
    print("\n" + "=" * 70)
    print("✅ Architecture synchronization complete!")
    sys.exit(0)


if __name__ == "__main__":
    main()
