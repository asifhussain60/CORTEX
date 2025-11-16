"""
Demo Conversation Module

Demonstrates CORTEX conversation tracking and memory system.

SOLID Principles:
- Single Responsibility: Only handles conversation memory demonstration
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import Dict, Any, Tuple, List
from datetime import datetime
from pathlib import Path

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationStatus,
    OperationPhase
)


class DemoConversationModule(BaseOperationModule):
    """
    Demo module for showcasing conversation tracking.
    
    Responsibilities:
    1. Explain conversation tracking system
    2. Show recent conversations (if any)
    3. Demonstrate /resume workflow
    4. Explain memory persistence
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="demo_conversation",
            name="Demo Conversation Memory",
            description="Explain conversation tracking and demonstrate /resume workflow",
            phase=OperationPhase.PROCESSING,
            priority=3,
            dependencies=["demo_cleanup"],
            optional=True,  # Optional in standard profile
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate prerequisites for conversation demo.
        
        Checks:
        1. Brain directory exists
        2. Conversation database accessible
        """
        issues = []
        
        config = context.get('config', {})
        cortex_root = Path(config.get('cortex_root', Path.cwd()))
        brain_dir = cortex_root / 'cortex-brain'
        
        if not brain_dir.exists():
            issues.append(f"Brain directory not found: {brain_dir}")
        
        # Note: Database may not exist yet (first run), but that's okay
        # We'll just explain the concept
        
        return len(issues) == 0, issues
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute conversation memory demonstration.
        
        Steps:
        1. Explain conversation tracking purpose
        2. Show recent conversations (if any)
        3. Demonstrate /resume command
        4. Explain memory persistence
        """
        start_time = datetime.now()
        
        try:
            self.log_info("")
            self.log_info("=" * 70)
            self.log_info("CONVERSATION MEMORY DEMONSTRATION")
            self.log_info("=" * 70)
            
            # Explain conversation tracking
            self._explain_conversation_tracking()
            
            # Check for existing conversations
            conversation_count = self._check_conversations(context)
            
            # Show /resume workflow
            self._demonstrate_resume(conversation_count)
            
            # Explain memory architecture
            self._explain_memory_system()
            
            self.log_info("")
            self.log_info("=" * 70)
            
            duration_seconds = (datetime.now() - start_time).total_seconds()
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message="Conversation memory demonstration complete",
                data={
                    'conversation_count': conversation_count,
                    'tracking_explained': True
                },
                duration_seconds=duration_seconds
            )
            
        except Exception as e:
            self.log_error(f"Conversation demo failed: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Conversation demo failed: {str(e)}",
                errors=[str(e)],
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )
    
    def _explain_conversation_tracking(self):
        """Explain what conversation tracking does."""
        self.log_info("")
        self.log_info("💬 About Conversation Tracking:")
        self.log_info("")
        self.log_info("GitHub Copilot Chat has no memory between sessions.")
        self.log_info("Each new chat starts from scratch - it's like amnesia!")
        self.log_info("")
        self.log_info("CORTEX solves this with Tier 1 Memory (Working Memory):")
        self.log_info("")
        self.log_info("  • Captures last 20 conversations automatically")
        self.log_info("  • Stores in SQLite database (cortex-brain/)")
        self.log_info("  • Enables /resume command to pick up where you left off")
        self.log_info("  • Tracks context, decisions, and patterns")
        self.log_info("")
        self.log_info("Example: 'Add a purple button' in a new chat will work")
        self.log_info("because CORTEX remembers you were working on the UI!")
        self.log_info("")
    
    def _check_conversations(self, context: Dict[str, Any]) -> int:
        """
        Check for existing conversations.
        
        Args:
            context: Demo context
            
        Returns:
            Number of conversations found
        """
        try:
            config = context.get('config', {})
            cortex_root = Path(config.get('cortex_root', Path.cwd()))
            conversation_db = cortex_root / 'cortex-brain' / 'conversation-history.jsonl'
            
            if conversation_db.exists():
                # Count lines in JSONL file
                with open(conversation_db, 'r', encoding='utf-8') as f:
                    count = sum(1 for _ in f)
                
                self.log_info(f"📊 Found {count} conversation(s) in memory")
                self.log_info("")
                
                if count > 0:
                    self.log_info("You can use /resume to continue from your last session!")
                else:
                    self.log_info("This is your first session - future chats will have memory!")
                
                return count
            else:
                self.log_info("📊 No conversations yet (this is your first session)")
                self.log_info("")
                self.log_info("After this demo, your conversation will be saved for next time!")
                return 0
                
        except Exception as e:
            self.log_warning(f"Could not check conversations: {e}")
            return 0
    
    def _demonstrate_resume(self, conversation_count: int):
        """
        Demonstrate the /resume command.
        
        Args:
            conversation_count: Number of conversations in memory
        """
        self.log_info("")
        self.log_info("🔄 Using /resume:")
        self.log_info("")
        
        if conversation_count > 0:
            self.log_info("Try this in a new chat window:")
            self.log_info("")
            self.log_info("  User:    /resume")
            self.log_info("  CORTEX:  'You were working on [last topic]...'")
            self.log_info("")
            self.log_info("CORTEX will:")
            self.log_info("  ✓ Load your last conversation")
            self.log_info("  ✓ Recall context and decisions")
            self.log_info("  ✓ Continue where you left off")
        else:
            self.log_info("After this demo, try starting a new chat and saying:")
            self.log_info("")
            self.log_info("  User:    /resume")
            self.log_info("  CORTEX:  'You just completed the interactive demo...'")
            self.log_info("")
            self.log_info("This proves CORTEX remembers across sessions!")
        
        self.log_info("")
    
    def _explain_memory_system(self):
        """Explain CORTEX memory architecture."""
        self.log_info("🧠 CORTEX Memory Architecture:")
        self.log_info("")
        self.log_info("CORTEX has a 4-tier brain system:")
        self.log_info("")
        self.log_info("  Tier 0 (Instinct): Immutable governance rules")
        self.log_info("  Tier 1 (Working Memory): Last 20 conversations ← We're here!")
        self.log_info("  Tier 2 (Knowledge Graph): Learned patterns over time")
        self.log_info("  Tier 3 (Context): Git metrics, test coverage, project health")
        self.log_info("")
        self.log_info("This multi-tier system gives CORTEX:")
        self.log_info("  ✓ Short-term memory (Tier 1)")
        self.log_info("  ✓ Long-term learning (Tier 2)")
        self.log_info("  ✓ Project awareness (Tier 3)")
        self.log_info("  ✓ Safety guarantees (Tier 0)")
        self.log_info("")
        self.log_info("💡 Learn more: #file:prompts/shared/story.md")
        self.log_info("")

