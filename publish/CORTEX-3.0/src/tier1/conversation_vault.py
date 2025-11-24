"""
CORTEX 3.0 - Conversation Vault Manager

Purpose: Manage conversation vault files for manual/automatic capture.
Creates structured markdown files with metadata for easy import to Tier 1.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class ConversationMetadata:
    """Metadata for captured conversation."""
    conversation_id: str
    timestamp: str
    quality_score: int
    quality_level: str
    semantic_elements: Dict
    total_turns: int
    user_topic: str


@dataclass
class ConversationTurn:
    """Single turn in a conversation."""
    turn_number: int
    user_prompt: str
    assistant_response: str
    timestamp: str


class ConversationVaultManager:
    """
    Manages conversation vault files for CORTEX 3.0 hybrid capture.
    
    File Structure:
    ```
    cortex-brain/conversation-vault/
    ├── 2025-11-13-implement-smart-hints.md
    ├── 2025-11-13-design-discussion.md
    └── metadata/
        ├── conv-20251113-143045.json
        └── conv-20251113-145230.json
    ```
    
    Each markdown file contains:
    - Frontmatter with metadata (YAML)
    - Conversation turns (formatted markdown)
    - Quality assessment summary
    - Import instructions
    """
    
    def __init__(self, vault_path: str = "cortex-brain/conversation-vault"):
        """
        Initialize vault manager.
        
        Args:
            vault_path: Path to conversation vault directory
        """
        self.vault_path = Path(vault_path)
        self.metadata_path = self.vault_path / "metadata"
        
        # Create directories if needed
        self.vault_path.mkdir(exist_ok=True, parents=True)
        self.metadata_path.mkdir(exist_ok=True, parents=True)
    
    def create_conversation_file(
        self,
        metadata: ConversationMetadata,
        turns: List[ConversationTurn],
        filename: str
    ) -> Path:
        """
        Create conversation file in vault.
        
        Args:
            metadata: Conversation metadata
            turns: List of conversation turns
            filename: Suggested filename
            
        Returns:
            Path to created file
        """
        filepath = self.vault_path / filename
        
        # Build markdown content
        content = self._build_markdown_content(metadata, turns)
        
        # Write conversation file
        filepath.write_text(content, encoding='utf-8')
        
        # Save metadata separately
        self._save_metadata(metadata)
        
        return filepath
    
    def _build_markdown_content(
        self,
        metadata: ConversationMetadata,
        turns: List[ConversationTurn]
    ) -> str:
        """Build formatted markdown content."""
        lines = []
        
        # Add frontmatter
        lines.append("---")
        lines.append(f"conversation_id: {metadata.conversation_id}")
        lines.append(f"timestamp: {metadata.timestamp}")
        lines.append(f"quality_score: {metadata.quality_score}")
        lines.append(f"quality_level: {metadata.quality_level}")
        lines.append(f"total_turns: {metadata.total_turns}")
        lines.append(f"topic: {metadata.user_topic}")
        lines.append("captured_by: CORTEX Smart Hint System")
        lines.append("status: ready_for_import")
        lines.append("---")
        lines.append("")
        
        # Add header
        lines.append(f"# {metadata.user_topic}")
        lines.append("")
        lines.append(f"**Captured:** {metadata.timestamp}  ")
        lines.append(f"**Quality:** {metadata.quality_level} ({metadata.quality_score}/10)  ")
        lines.append(f"**Conversation ID:** `{metadata.conversation_id}`")
        lines.append("")
        
        # Add quality summary
        lines.append("## Quality Assessment")
        lines.append("")
        lines.append(f"**Score:** {metadata.quality_score}/10")
        lines.append(f"**Level:** {metadata.quality_level}")
        lines.append("")
        lines.append("**Semantic Elements Detected:**")
        for key, value in metadata.semantic_elements.items():
            if value:
                formatted_key = key.replace('_', ' ').title()
                lines.append(f"- ✅ {formatted_key}: {value}")
        lines.append("")
        
        # Add conversation turns
        lines.append("## Conversation")
        lines.append("")
        
        for turn in turns:
            lines.append(f"### Turn {turn.turn_number}")
            lines.append("")
            lines.append(f"**User ({turn.timestamp}):**")
            lines.append("")
            lines.append(turn.user_prompt)
            lines.append("")
            lines.append("**Assistant:**")
            lines.append("")
            lines.append(turn.assistant_response)
            lines.append("")
            lines.append("---")
            lines.append("")
        
        # Add import instructions
        lines.append("## Import to CORTEX Brain")
        lines.append("")
        lines.append("To import this conversation to Tier 1 memory:")
        lines.append("")
        lines.append("```")
        lines.append(f'/import-conversation "{self.vault_path.name}/{metadata.conversation_id}"')
        lines.append("```")
        lines.append("")
        lines.append("Or use natural language:")
        lines.append("")
        lines.append("```")
        lines.append("import this conversation")
        lines.append("```")
        lines.append("")
        
        # Add footer
        lines.append("---")
        lines.append("")
        lines.append("*This conversation was automatically captured by CORTEX 3.0 Smart Hint System*  ")
        lines.append("*© 2024-2025 Asif Hussain. All rights reserved.*")
        
        return "\n".join(lines)
    
    def _save_metadata(self, metadata: ConversationMetadata) -> None:
        """Save metadata as JSON for quick lookup."""
        metadata_file = self.metadata_path / f"{metadata.conversation_id}.json"
        
        metadata_dict = asdict(metadata)
        metadata_dict['saved_at'] = datetime.now().isoformat()
        
        metadata_file.write_text(
            json.dumps(metadata_dict, indent=2),
            encoding='utf-8'
        )
    
    def get_conversation_by_id(self, conv_id: str) -> Optional[Path]:
        """
        Find conversation file by ID.
        
        Args:
            conv_id: Conversation ID
            
        Returns:
            Path to conversation file or None if not found
        """
        # Check metadata first
        metadata_file = self.metadata_path / f"{conv_id}.json"
        if not metadata_file.exists():
            return None
        
        # Find corresponding markdown file
        for filepath in self.vault_path.glob("*.md"):
            content = filepath.read_text(encoding='utf-8')
            if f"conversation_id: {conv_id}" in content:
                return filepath
        
        return None
    
    def list_conversations(
        self,
        quality_filter: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        List captured conversations with optional filtering.
        
        Args:
            quality_filter: Filter by quality level (EXCELLENT, GOOD, etc.)
            limit: Maximum number to return
            
        Returns:
            List of conversation metadata dicts
        """
        conversations = []
        
        for metadata_file in sorted(
            self.metadata_path.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        ):
            try:
                metadata = json.loads(metadata_file.read_text())
                
                # Apply quality filter
                if quality_filter and metadata.get('quality_level') != quality_filter:
                    continue
                
                conversations.append(metadata)
                
                if len(conversations) >= limit:
                    break
                    
            except Exception:
                continue
        
        return conversations
    
    def get_vault_stats(self) -> Dict:
        """Get statistics about conversation vault."""
        conversations = self.list_conversations(limit=1000)
        
        quality_counts = {}
        for conv in conversations:
            level = conv.get('quality_level', 'UNKNOWN')
            quality_counts[level] = quality_counts.get(level, 0) + 1
        
        total_turns = sum(conv.get('total_turns', 0) for conv in conversations)
        avg_quality = sum(conv.get('quality_score', 0) for conv in conversations) / max(len(conversations), 1)
        
        return {
            'total_conversations': len(conversations),
            'quality_distribution': quality_counts,
            'total_turns': total_turns,
            'average_quality_score': round(avg_quality, 2),
            'vault_path': str(self.vault_path),
            'oldest_conversation': conversations[-1]['timestamp'] if conversations else None,
            'newest_conversation': conversations[0]['timestamp'] if conversations else None
        }


def create_vault_manager(config: Dict = None) -> ConversationVaultManager:
    """
    Factory function to create vault manager with config.
    
    Args:
        config: Optional configuration dict with 'vault_path' key
        
    Returns:
        Configured ConversationVaultManager instance
    """
    vault_path = "cortex-brain/conversation-vault"
    
    if config and 'vault_path' in config:
        vault_path = config['vault_path']
    
    return ConversationVaultManager(vault_path=vault_path)
