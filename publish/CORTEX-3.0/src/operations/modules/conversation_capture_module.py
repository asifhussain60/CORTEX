"""
Conversation Capture Module

Enables manual conversation capture to Tier 1 Working Memory via natural language commands.

Natural Language Triggers:
- "remember this"
- "capture conversation" 
- "save chat"
- "store this conversation"
- "save context"

SOLID Principles:
- Single Responsibility: Only handles manual conversation capture
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on abstractions (WorkingMemory interface)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import re
from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional
from datetime import datetime
import uuid

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationStatus,
    OperationPhase
)


class ConversationCaptureModule(BaseOperationModule):
    """
    Captures current conversation to Tier 1 Working Memory on user request.
    
    Responsibilities:
    1. Detect natural language capture triggers
    2. Extract conversation history from context
    3. Identify entities (files, classes, methods)
    4. Detect conversation intent (PLAN, EXECUTE, FIX, etc.)
    5. Store to Tier 1 database
    6. Return confirmation with conversation ID
    """
    
    # Natural language patterns that trigger conversation capture
    CAPTURE_PATTERNS = [
        r'\bremember\s+this\b',
        r'\bcapture\s+(this\s+)?conversation\b',
        r'\bsave\s+(this\s+)?chat\b',
        r'\bstore\s+(this\s+)?conversation\b',
        r'\bsave\s+(this\s+)?context\b',
        r'\bkeep\s+this\s+in\s+memory\b',
    ]
    
    # Intent detection patterns
    INTENT_PATTERNS = {
        'PLAN': [r'\bplan\b', r'\bdesign\b', r'\barchitecture\b', r'\bapproach\b'],
        'EXECUTE': [r'\bimplement\b', r'\bcreate\b', r'\bbuild\b', r'\badd\b'],
        'FIX': [r'\bfix\b', r'\bbug\b', r'\berror\b', r'\bissue\b', r'\bdebug\b'],
        'REFACTOR': [r'\brefactor\b', r'\bimprove\b', r'\boptimize\b', r'\bclean\b'],
        'TEST': [r'\btest\b', r'\bvalidate\b', r'\bverify\b'],
        'DOCUMENT': [r'\bdocument\b', r'\bexplain\b', r'\bdescribe\b'],
        'RESEARCH': [r'\bresearch\b', r'\binvestigate\b', r'\banalyze\b', r'\bexplore\b'],
    }
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="conversation_capture",
            name="Conversation Capture",
            description="Capture current conversation to Tier 1 Working Memory",
            phase=OperationPhase.FEATURES,
            priority=30,  # After conversation tracking setup
            dependencies=["brain_initialization"],
            optional=False,  # Core feature for Tier 1 memory
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate prerequisites for conversation capture.
        
        Checks:
        1. Brain initialized (Tier 1 database exists)
        2. User request contains capture trigger
        3. Conversation history available in context
        """
        issues = []
        
        # Check brain initialization
        brain_initialized = context.get('brain_initialized', False)
        if not brain_initialized:
            issues.append("Brain must be initialized before capturing conversations")
            return False, issues
        
        # Check if user request contains capture trigger
        user_request = context.get('user_request', '')
        if not self.should_capture(user_request):
            # This is not an error - just means capture not requested
            return False, []
        
        return True, []
    
    def should_capture(self, user_request: str) -> bool:
        """
        Check if user request contains a capture trigger.
        
        Args:
            user_request: The user's input text
            
        Returns:
            True if capture was requested, False otherwise
        """
        user_request_lower = user_request.lower()
        
        for pattern in self.CAPTURE_PATTERNS:
            if re.search(pattern, user_request_lower):
                return True
        
        return False
    
    def detect_intent(self, conversation_text: str) -> str:
        """
        Detect the primary intent of the conversation.
        
        Args:
            conversation_text: Combined text from all messages
            
        Returns:
            Intent string (PLAN, EXECUTE, FIX, etc.) or 'GENERAL'
        """
        conversation_lower = conversation_text.lower()
        
        # Count matches for each intent
        intent_scores = {}
        for intent, patterns in self.INTENT_PATTERNS.items():
            score = sum(1 for pattern in patterns if re.search(pattern, conversation_lower))
            if score > 0:
                intent_scores[intent] = score
        
        # Return intent with highest score, or GENERAL if none found
        if intent_scores:
            return max(intent_scores.items(), key=lambda x: x[1])[0]
        
        return 'GENERAL'
    
    def extract_entities(self, conversation_text: str) -> Dict[str, List[str]]:
        """
        Extract entities (files, classes, methods) from conversation.
        
        Args:
            conversation_text: Combined text from all messages
            
        Returns:
            Dict with entity categories and lists of entity names
        """
        entities = {
            'files': [],
            'classes': [],
            'methods': [],
            'ui_components': []
        }
        
        # File patterns - common extensions
        file_pattern = r'\b[\w\-./]+\.(?:py|cs|js|ts|jsx|tsx|java|cpp|h|css|html|json|yaml|yml|md|txt)\b'
        entities['files'] = list(set(re.findall(file_pattern, conversation_text)))
        
        # Class patterns - PascalCase
        class_pattern = r'\b[A-Z][a-z]+(?:[A-Z][a-z]*)*\b'
        potential_classes = re.findall(class_pattern, conversation_text)
        # Filter out common words
        common_words = {'The', 'This', 'That', 'These', 'Those', 'Phase', 'Step', 'Test', 'Class', 'Method'}
        entities['classes'] = [c for c in set(potential_classes) if c not in common_words][:10]
        
        # Method patterns - camelCase or method keywords
        method_pattern = r'\b(?:get|set|is|has|create|delete|update|find|load|save|validate|process|handle|execute|format|extract|resolve)[A-Z][a-z]*(?:[A-Z][a-z]*)*\b'
        entities['methods'] = list(set(re.findall(method_pattern, conversation_text)))[:10]
        
        # UI component patterns
        ui_keywords = ['button', 'form', 'input', 'dialog', 'modal', 'dropdown', 'menu', 'navbar']
        ui_pattern = r'\b(?:' + '|'.join(ui_keywords) + r')\b'
        entities['ui_components'] = list(set(re.findall(ui_pattern, conversation_text.lower())))[:5]
        
        return entities
    
    def create_conversation_summary(self, conversation_history: List[Dict[str, str]], max_length: int = 200) -> str:
        """
        Create a concise summary of the conversation.
        
        Args:
            conversation_history: List of message dicts with 'role' and 'content'
            max_length: Maximum summary length in characters
            
        Returns:
            Summary string
        """
        # Get first user message as primary context
        first_user_msg = next((msg['content'] for msg in conversation_history if msg['role'] == 'user'), '')
        
        if len(first_user_msg) <= max_length:
            return first_user_msg
        
        # Truncate with ellipsis
        return first_user_msg[:max_length - 3] + '...'
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute conversation capture.
        
        Steps:
        1. Extract conversation history from context
        2. Generate conversation ID
        3. Extract entities from conversation
        4. Detect conversation intent
        5. Create summary
        6. Store to Tier 1 database
        7. Return confirmation
        """
        start_time = datetime.now()
        
        try:
            # Import WorkingMemory here to avoid circular dependencies
            from src.tier1.working_memory import WorkingMemory
            
            # Get conversation history from context
            conversation_history = context.get('conversation_history', [])
            if not conversation_history:
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="No conversation history available to capture",
                    duration_seconds=(datetime.now() - start_time).total_seconds()
                )
            
            # Generate conversation ID
            conversation_id = f"conv_{uuid.uuid4().hex[:8]}"
            
            # Combine all messages for entity extraction and intent detection
            conversation_text = '\n'.join([msg.get('content', '') for msg in conversation_history])
            
            # Extract entities
            entities = self.extract_entities(conversation_text)
            
            # Detect intent
            intent = self.detect_intent(conversation_text)
            
            # Create summary
            summary = self.create_conversation_summary(conversation_history)
            
            # Initialize Working Memory
            project_root = context.get('project_root', Path.cwd())
            db_path = Path(project_root) / "cortex-brain" / "tier1" / "working_memory.db"
            wm = WorkingMemory(db_path=db_path)
            
            # Store conversation
            conv_id = wm.add_conversation(
                conversation_id=conversation_id,
                title=summary,
                summary=summary,
                tags=[intent] + entities['files'][:3]  # Tag with intent and top 3 files
            )
            
            # Add messages to conversation
            for msg in conversation_history:
                wm.message_store.add_message(
                    conversation_id=conversation_id,
                    role=msg.get('role', 'user'),
                    content=msg.get('content', '')
                )
            
            # Add entities to database
            for entity_type, entity_list in entities.items():
                for entity_name in entity_list:
                    if entity_type == 'files':
                        wm.entity_extractor.add_entity(
                            conversation_id=conversation_id,
                            entity_type='file',
                            entity_name=entity_name,
                            file_path=entity_name
                        )
                    elif entity_type == 'classes':
                        wm.entity_extractor.add_entity(
                            conversation_id=conversation_id,
                            entity_type='class',
                            entity_name=entity_name
                        )
                    elif entity_type == 'methods':
                        wm.entity_extractor.add_entity(
                            conversation_id=conversation_id,
                            entity_type='method',
                            entity_name=entity_name
                        )
                    elif entity_type == 'ui_components':
                        wm.entity_extractor.add_entity(
                            conversation_id=conversation_id,
                            entity_type='ui_component',
                            entity_name=entity_name
                        )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Create success message
            entity_summary = ', '.join([f"{len(v)} {k}" for k, v in entities.items() if v])
            message = f"✅ Conversation captured to Tier 1 Working Memory\n\n"
            message += f"**Conversation ID:** `{conversation_id}`\n"
            message += f"**Intent:** {intent}\n"
            message += f"**Entities Extracted:** {entity_summary}\n"
            message += f"**Messages:** {len(conversation_history)}\n"
            message += f"**Summary:** {summary[:100]}{'...' if len(summary) > 100 else ''}"
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=message,
                data={
                    'conversation_id': conversation_id,
                    'intent': intent,
                    'entities': entities,
                    'message_count': len(conversation_history),
                    'summary': summary
                },
                duration_seconds=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.log_error(f"Failed to capture conversation: {e}")
            
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Failed to capture conversation: {str(e)}",
                duration_seconds=execution_time
            )


def capture_conversation(user_request: str, conversation_history: List[Dict[str, str]], 
                        project_root: Optional[Path] = None) -> Dict[str, Any]:
    """
    Convenience function to capture a conversation.
    
    Args:
        user_request: The user's request (checked for capture trigger)
        conversation_history: List of messages with 'role' and 'content'
        project_root: Project root path (defaults to current directory)
        
    Returns:
        Dict with capture results or None if capture not requested
    """
    module = ConversationCaptureModule()
    
    context = {
        'user_request': user_request,
        'conversation_history': conversation_history,
        'brain_initialized': True,
        'project_root': project_root or Path.cwd()
    }
    
    # Check if capture was requested
    if not module.should_capture(user_request):
        return None
    
    # Validate prerequisites
    valid, issues = module.validate_prerequisites(context)
    if not valid:
        return {
            'success': False,
            'message': f"Cannot capture: {', '.join(issues)}"
        }
    
    # Execute capture
    result = module.execute(context)
    
    return {
        'success': result.success,
        'message': result.message,
        'data': result.data,
        'execution_time_ms': result.duration_seconds * 1000
    }
