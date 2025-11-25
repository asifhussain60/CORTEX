"""
CORTEX 2.0 - Conversation Import Plugin

Purpose: Import manually copy-pasted Copilot conversations to enrich CORTEX learning.
Complements ambient daemon with strategic context and decision rationale.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from src.plugins.base_plugin import BasePlugin, PluginMetadata
from src.plugins.command_registry import CommandMetadata


@dataclass
class ConversationTurn:
    """Represents one turn in a Copilot conversation."""
    user: str
    timestamp: datetime
    user_prompt: str
    assistant_response: str
    semantic_elements: Dict[str, Any]
    files_mentioned: List[str]


@dataclass
class ParsedConversation:
    """Parsed conversation with metadata."""
    turns: List[ConversationTurn]
    total_turns: int
    semantic_score: int
    files_referenced: List[str]
    patterns_detected: List[str]


class ConversationImportPlugin(BasePlugin):
    """
    Plugin for importing Copilot conversations to CORTEX brain.
    
    Provides dual-channel learning:
    - Channel 1: Ambient daemon (execution-focused)
    - Channel 2: Manual conversations (strategy-focused)
    """
    
    def _get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="conversation_import",
            name="Conversation Import",
            version="1.0.0",
            description="Import Copilot conversations to enrich CORTEX learning",
            author="Asif Hussain",
            capabilities=[
                "parse_copilot_chat",
                "extract_semantic_elements",
                "store_to_tier1",
                "cross_reference_with_daemon"
            ]
        )
    
    def register_commands(self) -> List[CommandMetadata]:
        """Register slash commands and natural language equivalents."""
        return [
            CommandMetadata(
                command="/import-conversation",
                natural_language_equivalent="import conversation from file",
                plugin_id=self.metadata.plugin_id,
                description="Import a Copilot conversation file to CORTEX brain",
                parameters={
                    "file_path": "Path to conversation markdown file"
                }
            ),
            CommandMetadata(
                command="/analyze-conversation",
                natural_language_equivalent="analyze conversation quality",
                plugin_id=self.metadata.plugin_id,
                description="Analyze conversation file for semantic value",
                parameters={
                    "file_path": "Path to conversation markdown file"
                }
            ),
            CommandMetadata(
                command="/capture-conversation",
                natural_language_equivalent="capture conversation",
                plugin_id=self.metadata.plugin_id,
                description="Capture current conversation to vault for future import",
                parameters={}
            )
        ]
    
    def initialize(self) -> bool:
        """Initialize conversation import plugin."""
        try:
            self.logger.info("Initializing Conversation Import Plugin")
            
            # Initialize storage paths
            self.brain_path = Path(self.get_brain_path())
            self.imported_conversations_dir = self.brain_path / "imported-conversations"
            self.imported_conversations_dir.mkdir(exist_ok=True, parents=True)
            
            # Initialize conversation vault for CORTEX 3.0
            self.vault_dir = self.brain_path / "conversation-vault"
            self.vault_dir.mkdir(exist_ok=True, parents=True)
            
            # Initialize Tier 1 connection
            self.tier1_db = self.brain_path / "tier1" / "conversations.db"
            
            if not self.tier1_db.exists():
                self.logger.warning(f"Tier 1 database not found: {self.tier1_db}")
                return False
            
            self.logger.info("Conversation Import Plugin initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize: {e}")
            return False
    
    def execute(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute conversation import operations.
        
        Args:
            request: User request string
            context: Execution context
            
        Returns:
            Result dictionary with status and data
        """
        try:
            # Parse request intent
            if "capture" in request.lower():
                return self._handle_capture(context)
            elif "import" in request.lower():
                return self._handle_import(context)
            elif "analyze" in request.lower():
                return self._handle_analyze(context)
            else:
                return {
                    "status": "error",
                    "message": "Unknown operation. Use 'capture', 'import', or 'analyze'."
                }
                
        except Exception as e:
            self.logger.error(f"Execution error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _handle_capture(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Capture current conversation to vault using CORTEX 3.0 smart hint system."""
        try:
            # Import smart hint system
            from src.tier1.smart_hint_integration import capture_current_conversation
            
            # Get conversation from context
            user_prompt = context.get("user_prompt", "")
            assistant_response = context.get("assistant_response", "")
            
            if not user_prompt or not assistant_response:
                return {
                    "status": "error",
                    "message": "Missing conversation context. Please provide user_prompt and assistant_response."
                }
            
            # Capture using smart hint system
            confirmation = capture_current_conversation(user_prompt, assistant_response)
            
            return {
                "status": "success",
                "message": confirmation,
                "data": {
                    "vault_path": str(self.vault_dir)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Capture error: {e}")
            return {
                "status": "error",
                "message": f"Failed to capture conversation: {str(e)}"
            }
    
    def _handle_import(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Import conversation file to CORTEX brain."""
        file_path = context.get("file_path")
        
        if not file_path:
            return {
                "status": "error",
                "message": "file_path parameter required"
            }
        
        # Parse conversation
        parsed = self.parse_conversation_file(file_path)
        
        if not parsed:
            return {
                "status": "error",
                "message": "Failed to parse conversation file"
            }
        
        # Store to Tier 1
        success = self.store_to_tier1(parsed)
        
        if success:
            return {
                "status": "success",
                "message": f"Imported {parsed.total_turns} conversation turns",
                "data": {
                    "total_turns": parsed.total_turns,
                    "semantic_score": parsed.semantic_score,
                    "files_referenced": len(parsed.files_referenced),
                    "patterns_detected": parsed.patterns_detected
                }
            }
        else:
            return {
                "status": "error",
                "message": "Failed to store conversation to Tier 1"
            }
    
    def _handle_analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze conversation quality without importing."""
        file_path = context.get("file_path")
        
        if not file_path:
            return {
                "status": "error",
                "message": "file_path parameter required"
            }
        
        # Parse conversation
        parsed = self.parse_conversation_file(file_path)
        
        if not parsed:
            return {
                "status": "error",
                "message": "Failed to parse conversation file"
            }
        
        # Generate analysis report
        report = self._generate_analysis_report(parsed)
        
        return {
            "status": "success",
            "message": "Conversation analysis complete",
            "data": report
        }
    
    def parse_conversation_file(self, file_path: str) -> Optional[ParsedConversation]:
        """
        Parse Copilot conversation markdown file.
        
        Args:
            file_path: Path to conversation file
            
        Returns:
            ParsedConversation or None if parsing fails
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                self.logger.error(f"File not found: {file_path}")
                return None
            
            content = path.read_text(encoding='utf-8')
            
            # Split by user prompts (asifhussain60:)
            conversations = re.split(r'^asifhussain60:', content, flags=re.MULTILINE)
            
            turns = []
            all_files = []
            all_patterns = []
            total_semantic_score = 0
            
            for i, conv_text in enumerate(conversations[1:], 1):
                # Extract timestamp (if present)
                timestamp = datetime.now()
                
                # Split into prompt and response
                parts = re.split(r'^GitHub Copilot:', conv_text, maxsplit=1, flags=re.MULTILINE)
                
                if len(parts) < 2:
                    continue  # No assistant response
                
                user_prompt = parts[0].strip()
                assistant_response = parts[1].strip()
                
                # Extract semantic elements
                semantic = self._extract_semantic_elements(assistant_response)
                total_semantic_score += semantic['score']
                
                # Extract file mentions
                files = self._extract_file_mentions(conv_text)
                all_files.extend(files)
                
                # Detect patterns
                patterns = self._detect_patterns(assistant_response)
                all_patterns.extend(patterns)
                
                # Create turn
                turn = ConversationTurn(
                    user="asifhussain60",
                    timestamp=timestamp,
                    user_prompt=user_prompt,
                    assistant_response=assistant_response,
                    semantic_elements=semantic,
                    files_mentioned=files
                )
                
                turns.append(turn)
            
            # Deduplicate files and patterns
            all_files = list(set(all_files))
            all_patterns = list(set(all_patterns))
            
            return ParsedConversation(
                turns=turns,
                total_turns=len(turns),
                semantic_score=total_semantic_score,
                files_referenced=all_files,
                patterns_detected=all_patterns
            )
            
        except Exception as e:
            self.logger.error(f"Parsing error: {e}")
            return None
    
    def _extract_semantic_elements(self, text: str) -> Dict[str, Any]:
        """Extract semantic elements from assistant response."""
        elements = {
            'has_cortex_template': 'CORTEX' in text,
            'has_challenge': 'Challenge:' in text,
            'has_alternatives': 'Alternative' in text or 'Better solution' in text,
            'has_phase_planning': bool(re.search(r'Phase \d+', text)),
            'has_next_steps': 'Next Steps:' in text,
            'has_design_decision': any(kw in text for kw in ['architecture', 'design', 'approach', 'strategy']),
            'score': 0
        }
        
        # Calculate score
        score = 0
        if elements['has_cortex_template']:
            score += 2
        if elements['has_challenge']:
            score += 3
        if elements['has_alternatives']:
            score += 3
        if elements['has_phase_planning']:
            score += 2
        if elements['has_next_steps']:
            score += 2
        if elements['has_design_decision']:
            score += 1
        
        elements['score'] = score
        
        return elements
    
    def _extract_file_mentions(self, text: str) -> List[str]:
        """Extract file paths mentioned in conversation."""
        # Match file paths in backticks
        file_pattern = r'`([a-zA-Z0-9_\-/.]+\.(py|md|yaml|json|ps1|ts|tsx|cs|sql|sh))`'
        matches = re.findall(file_pattern, text)
        return [m[0] for m in matches]
    
    def _detect_patterns(self, text: str) -> List[str]:
        """Detect conversation patterns."""
        patterns = []
        
        if 'CORTEX' in text:
            patterns.append('cortex_template')
        if 'Challenge' in text and 'Accept' in text:
            patterns.append('challenge_accept_flow')
        if re.search(r'Phase \d+.*?Phase \d+', text, re.DOTALL):
            patterns.append('multi_phase_planning')
        if 'Test' in text and ('pytest' in text or 'test_' in text):
            patterns.append('test_driven')
        
        return patterns
    
    def store_to_tier1(self, parsed: ParsedConversation) -> bool:
        """
        Store parsed conversation to Tier 1 working memory.
        
        Args:
            parsed: ParsedConversation object
            
        Returns:
            True if successful
        """
        try:
            from src.tier1.working_memory import WorkingMemory
            
            wm = WorkingMemory(str(self.tier1_db))
            
            # Create conversation session
            session_id = wm.start_conversation(
                user_id="manual_import",
                metadata={
                    "type": "copilot_conversation_import",
                    "import_date": datetime.now().isoformat(),
                    "total_turns": parsed.total_turns,
                    "semantic_score": parsed.semantic_score,
                    "files_referenced": parsed.files_referenced,
                    "patterns_detected": parsed.patterns_detected
                }
            )
            
            # Store each turn as message pair
            for turn in parsed.turns:
                # User message
                wm.store_message(
                    conversation_id=session_id,
                    message={
                        "role": "user",
                        "content": turn.user_prompt,
                        "timestamp": turn.timestamp.isoformat()
                    }
                )
                
                # Assistant message with semantic metadata
                wm.store_message(
                    conversation_id=session_id,
                    message={
                        "role": "assistant",
                        "content": turn.assistant_response,
                        "timestamp": turn.timestamp.isoformat(),
                        "metadata": {
                            "semantic_elements": turn.semantic_elements,
                            "files_mentioned": turn.files_mentioned
                        }
                    }
                )
            
            self.logger.info(f"Stored {parsed.total_turns} turns to Tier 1 (session: {session_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store to Tier 1: {e}")
            return False
    
    def _generate_analysis_report(self, parsed: ParsedConversation) -> Dict[str, Any]:
        """Generate detailed analysis report."""
        return {
            "total_turns": parsed.total_turns,
            "semantic_score": parsed.semantic_score,
            "average_score_per_turn": parsed.semantic_score / max(1, parsed.total_turns),
            "files_referenced": {
                "count": len(parsed.files_referenced),
                "list": parsed.files_referenced[:10]  # First 10
            },
            "patterns_detected": {
                "count": len(parsed.patterns_detected),
                "list": parsed.patterns_detected
            },
            "quality_assessment": self._assess_quality(parsed)
        }
    
    def _assess_quality(self, parsed: ParsedConversation) -> str:
        """Assess conversation quality."""
        avg_score = parsed.semantic_score / max(1, parsed.total_turns)
        
        if avg_score >= 10:
            return "EXCELLENT - High strategic value with multiple semantic elements"
        elif avg_score >= 6:
            return "GOOD - Moderate strategic context with planning elements"
        elif avg_score >= 3:
            return "FAIR - Some strategic context, mostly execution"
        else:
            return "LOW - Minimal strategic content, primarily execution"
    
    def cleanup(self) -> bool:
        """Cleanup plugin resources."""
        self.logger.info("Conversation Import Plugin cleanup complete")
        return True


def register() -> BasePlugin:
    """Plugin registration function."""
    return ConversationImportPlugin()
