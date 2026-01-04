"""
Cross-Session Context Middleware.

Pre-routing enrichment layer that injects lightweight session context
from Tier 1 Working Memory into Master Orchestrator requests.

Part of CORTEX v5 Phase 4.5: Enables continuation across chat sessions
without losing user context.

Architecture:
    User Input → Middleware (continuation detection)
              ↓
          Query Tier 1 (orchestrator sessions OR active projects)
              ↓
          Inject metadata (<200 tokens)
              ↓
          Pass to Master Orchestrator

Option B Enhancement: Supports both orchestrator-level and project-level continuations.
- Orchestrator continuation: "continue" after TDD/Debug/ADO session
- Project continuation: "continue" with active planning project

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import re
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path


class CrossSessionContextMiddleware:
    """
    Middleware for cross-session context injection.
    
    Detects continuation patterns ("continue", "resume", "next phase") and
    enriches routing requests with lightweight session metadata from
    Tier 1 Working Memory.
    
    Token Efficiency: 200 tokens (metadata) vs 50,000 tokens (full conversation)
    = 99.6% reduction
    
    Usage:
        from src.tier1.sessions.session_manager import SessionManager
        
        session_mgr = SessionManager(Path("cortex-brain/tier1/working_memory.db"))
        middleware = CrossSessionContextMiddleware(session_manager=session_mgr)
        
        enriched_context = middleware.enrich_context(
            user_input="continue",
            existing_context={}
        )
        
        master_orch.handle_request(user_input, enriched_context)
    """
    
    # Continuation patterns (aligned with ExecutionModeDetector)
    CONTINUATION_PATTERNS = [
        r'\bcontinue\b',
        r'\bresume\b',
        r'\bkeep going\b',
        r'\bnext phase\b',
        r'\bproceed\b',
        r'\bcontinue with\b',
        r'\bresume execution\b',
        r'\bnext\b'
    ]
    
    def __init__(self, session_manager: Optional[Any] = None, project_tracker: Optional[Any] = None):
        """
        Initialize context middleware.
        
        Args:
            session_manager: Tier 1 SessionManager instance.
                           If None, creates default instance.
            project_tracker: Tier 1 ProjectTracker instance.
                           If None, creates default instance.
        """
        if session_manager is None:
            # Late import to avoid circular dependencies
            from src.tier1.sessions.session_manager import SessionManager
            db_path = Path("cortex-brain/tier1/working_memory.db")
            self.session_manager = SessionManager(db_path)
        else:
            self.session_manager = session_manager
        
        if project_tracker is None:
            # Late import to avoid circular dependencies
            from src.tier1.project_tracker import ProjectTracker
            db_path = Path("cortex-brain/tier1/working_memory.db")
            self.project_tracker = ProjectTracker(db_path)
        else:
            self.project_tracker = project_tracker
        
        # Initialize knowledge graph for file relationships
        try:
            from src.tier2.knowledge_graph import KnowledgeGraph
            kg_path = Path("cortex-brain/tier2/knowledge_graph.db")
            self.knowledge_graph = KnowledgeGraph(db_path=str(kg_path))
        except Exception as e:
            self.logger.warning(f"Knowledge graph not available: {e}")
            self.knowledge_graph = None
        
        self.logger = logging.getLogger("cortex.orchestrators.context_middleware")
        
        # Compile continuation patterns for performance
        self._continuation_regex = re.compile(
            '|'.join(self.CONTINUATION_PATTERNS),
            re.IGNORECASE
        )
        
        # Compile file path pattern for extraction
        self._file_path_regex = re.compile(
            r'(?:^|[\s\'"(])'  # Start or preceded by whitespace/quotes/parens
            r'((?:\./)?'  # Optional ./
            r'[a-zA-Z0-9_\-./]+'  # Path segments
            r'\.py)'  # Must end in .py
            r'(?:$|[\s\'")\],])',  # End or followed by whitespace/quotes/parens/punctuation
            re.MULTILINE
        )
        
        self.logger.info("CrossSessionContextMiddleware initialized with project tracking")
    
    def enrich_context(
        self,
        user_input: str,
        existing_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Enrich routing context with cross-session metadata if continuation detected.
        
        Two-tier fallback:
        1. Check for orchestrator session (TDD, Debug, ADO, etc.)
        2. If none, check for active planning project
        
        Args:
            user_input: User's natural language request
            existing_context: Optional existing context dict
        
        Returns:
            Enriched context dict with 'recent_activity' and/or 'active_project'
            if continuation detected, otherwise returns existing_context unchanged
        
        Example Output (Orchestrator Session):
            {
                "recent_activity": [
                    {
                        "session_id": "session-20260102-101500",
                        "orchestrator": "tdd_master",
                        "intent": "run tests for auth module",
                        "artifacts": ["test_results.json"],
                        "timestamp": "2026-01-02T10:15:00Z"
                    }
                ],
                "continuation_detected": true,
                "continuation_type": "orchestrator_session",
                "context_source": "tier1_working_memory"
            }
        
        Example Output (Project Continuation):
            {
                "active_project": {
                    "project_id": "cortex-v5-holistic-refactor",
                    "plan_name": "CORTEX v5 Holistic Refactor",
                    "current_phase": "Phase 5",
                    "current_task": "Task 5.1",
                    "last_completed": "Phase 5.1a",
                    "progress": 40,
                    "next_action": "/CORTEX Plan ADO Orchestrator v2 Migration",
                    "orchestrator": "planning_v5"
                },
                "continuation_detected": true,
                "continuation_type": "active_project",
                "context_source": "tier1_project_tracker"
            }
        """
        context = existing_context.copy() if existing_context else {}
        
        # PRIORITY 1: Vision Context - Check for image attachments
        context = self._inject_vision_context(context)
        
        # PRIORITY 3: File Relationships - Check for file mentions
        context = self._inject_file_relationships(user_input, context)
        
        # Enforce token budget before continuation check
        context = self._enforce_token_budget(context, max_tokens=500)
        
        # Check if continuation pattern detected
        if not self._is_continuation(user_input):
            self.logger.debug("No continuation pattern detected")
            return context
        
        self.logger.info("Continuation pattern detected, checking session and project context")
        
        # TIER 1: Check for orchestrator session
        try:
            recent_sessions = self.session_manager.get_recent_session_context(limit=3)
        except Exception as e:
            self.logger.error(f"Failed to query Tier 1 for session context: {e}")
            recent_sessions = []
        
        if recent_sessions:
            # Orchestrator session found - inject session context
            context['recent_activity'] = recent_sessions
            context['continuation_detected'] = True
            context['continuation_type'] = 'orchestrator_session'
            context['context_source'] = 'tier1_working_memory'
            
            last_orch = recent_sessions[0]['orchestrator']
            self.logger.info(
                f"Injected {len(recent_sessions)} orchestrator session(s) metadata "
                f"(last orchestrator: {last_orch})"
            )
            return context
        
        # TIER 2: Check for active planning project
        try:
            project_context = self.project_tracker.get_lightweight_project_context()
        except Exception as e:
            self.logger.error(f"Failed to query Tier 1 for project context: {e}")
            project_context = None
        
        if project_context:
            # Active project found - inject project context
            context['active_project'] = project_context
            context['continuation_detected'] = True
            context['continuation_type'] = 'active_project'
            context['context_source'] = 'tier1_project_tracker'
            
            self.logger.info(
                f"Injected active project context: {project_context['project_id']} "
                f"({project_context['progress']}% complete, next: {project_context.get('current_task', 'N/A')})"
            )
            return context
        
        # No continuation context found
        self.logger.warning("Continuation pattern detected but no session or project context found")
        return context
    
    def _is_continuation(self, user_input: str) -> bool:
        """
        Check if user input matches continuation patterns.
        
        Args:
            user_input: User's natural language request
        
        Returns:
            True if continuation pattern detected, False otherwise
        """
        return bool(self._continuation_regex.search(user_input))
    
    def get_last_orchestrator(
        self,
        user_input: str,
        existing_context: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Get last used orchestrator if continuation detected.
        
        Convenience method for Master Orchestrator routing.
        Checks both orchestrator sessions and active projects.
        
        Args:
            user_input: User's natural language request
            existing_context: Optional existing context dict
        
        Returns:
            Orchestrator ID from last session or active project, or None if not continuation
        
        Example:
            middleware.get_last_orchestrator("continue")  # → "planning_v5" (from project)
            middleware.get_last_orchestrator("resume")    # → "tdd_master" (from session)
            middleware.get_last_orchestrator("plan X")    # → None
        """
        enriched = self.enrich_context(user_input, existing_context)
        
        # Check orchestrator session first (higher priority)
        if 'recent_activity' in enriched and enriched['recent_activity']:
            return enriched['recent_activity'][0]['orchestrator']
        
        # Check active project second
        if 'active_project' in enriched and enriched['active_project']:
            return enriched['active_project'].get('orchestrator', 'planning_v5')
        
        return None
    
    def get_context_token_count(self, context: Dict[str, Any]) -> int:
        """
        Estimate token count for injected context.
        
        Used for monitoring token efficiency. Handles both orchestrator
        sessions (recent_activity) and project context (active_project).
        
        Args:
            context: Enriched context dict
        
        Returns:
            Estimated token count (rough approximation: chars / 4)
        """
        import json
        
        # Calculate tokens for orchestrator session context
        session_tokens = 0
        if 'recent_activity' in context:
            context_json = json.dumps(context['recent_activity'])
            session_tokens = len(context_json) // 4
        
        # Calculate tokens for project context
        project_tokens = 0
        if 'active_project' in context:
            project_json = json.dumps(context['active_project'])
            project_tokens = len(project_json) // 4
        
        # Calculate tokens for vision context
        vision_tokens = 0
        if 'vision_context' in context:
            vision_json = json.dumps(context['vision_context'])
            vision_tokens = len(vision_json) // 4
        
        # Calculate tokens for file relationships
        file_rel_tokens = 0
        if 'file_relationships' in context:
            file_rel_json = json.dumps(context['file_relationships'])
            file_rel_tokens = len(file_rel_json) // 4
        
        return session_tokens + project_tokens + vision_tokens + file_rel_tokens
    
    def _inject_vision_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inject Vision API context if images are present in attachments.
        
        Priority 1: Highest priority context source (<100 tokens).
        
        Args:
            context: Context dict (may contain 'attachments')
        
        Returns:
            Context with 'vision_context' added if images detected
        """
        # Check for image attachments
        attachments = context.get('attachments', [])
        if not attachments:
            return context
        
        # Check if any attachment is an image
        has_images = any(
            att.get('type') == 'image' for att in attachments
        )
        
        if not has_images:
            return context
        
        # Mark vision context as available
        context['vision_context_available'] = True
        
        try:
            # Import vision middleware (lazy import to avoid circular deps)
            from src.operations.utilities.vision_context_middleware import VisionContextMiddleware
            
            vision_middleware = VisionContextMiddleware()
            
            # Process context to get vision analysis
            enhanced_context = vision_middleware.process_context(context)
            
            # Extract and trim vision analysis to token budget
            if 'vision_analysis' in enhanced_context:
                vision_data = enhanced_context['vision_analysis']
                
                # Trim to ~100 token budget (400 chars ≈ 100 tokens)
                context['vision_context'] = self._trim_vision_context(vision_data, max_chars=400)
                
                self.logger.info("Vision context injected (<100 tokens)")
            
        except ImportError:
            self.logger.warning("VisionContextMiddleware not available")
        except Exception as e:
            self.logger.error(f"Failed to inject vision context: {e}")
        
        return context
    
    def _trim_vision_context(self, vision_data: Dict[str, Any], max_chars: int = 400) -> Dict[str, Any]:
        """
        Trim vision context to respect token budget.
        
        Args:
            vision_data: Vision analysis data
            max_chars: Maximum characters (~max_chars/4 tokens)
        
        Returns:
            Trimmed vision context
        """
        # Keep only essential fields
        trimmed = {}
        
        if 'description' in vision_data:
            desc = str(vision_data['description'])
            # Trim description if too long
            if len(desc) > 200:
                trimmed['description'] = desc[:197] + "..."
            else:
                trimmed['description'] = desc
        
        if 'confidence' in vision_data:
            trimmed['confidence'] = vision_data['confidence']
        
        if 'ui_elements' in vision_data:
            elements = vision_data['ui_elements']
            # Keep max 10 elements
            if isinstance(elements, list):
                trimmed['ui_elements'] = elements[:10]
            else:
                trimmed['ui_elements'] = elements
        
        if 'objects' in vision_data:
            objects = vision_data['objects']
            # Keep max 8 objects
            if isinstance(objects, list):
                trimmed['objects'] = objects[:8]
            else:
                trimmed['objects'] = objects
        
        return trimmed
    
    def _inject_file_relationships(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inject file relationship context if files are mentioned.
        
        Priority 3: File relationships from knowledge graph (<150 tokens).
        
        Args:
            user_input: User's natural language request
            context: Context dict
        
        Returns:
            Context with 'file_relationships' added if files mentioned
        """
        # Extract file paths from user input
        file_paths = self._extract_file_paths(user_input)
        
        if not file_paths:
            return context
        
        if not self.knowledge_graph:
            self.logger.debug("Knowledge graph not available for file relationships")
            return context
        
        try:
            # Query relationships for first mentioned file
            # (could expand to all files, but limiting for token budget)
            primary_file = file_paths[0]
            
            relationships = self.knowledge_graph.get_file_relationships(
                file_path=primary_file,
                min_strength=0.5  # Filter weak relationships
            )
            
            if relationships:
                # Trim to token budget (~150 tokens = 600 chars)
                trimmed_relationships = self._trim_file_relationships(relationships, max_items=5)
                context['file_relationships'] = trimmed_relationships
                context['mentioned_files'] = file_paths
                
                self.logger.info(
                    f"File relationships injected: {len(trimmed_relationships)} related files "
                    f"for {primary_file}"
                )
        
        except Exception as e:
            self.logger.error(f"Failed to inject file relationships: {e}")
        
        return context
    
    def _extract_file_paths(self, user_input: str) -> List[str]:
        """
        Extract file paths from user input.
        
        Args:
            user_input: User's natural language request
        
        Returns:
            List of extracted file paths
        """
        matches = self._file_path_regex.findall(user_input)
        
        # Clean up matches
        file_paths = []
        for match in matches:
            # Remove leading/trailing whitespace and quotes
            cleaned = match.strip().strip('\'"')
            if cleaned:
                file_paths.append(cleaned)
        
        return file_paths
    
    def _trim_file_relationships(
        self,
        relationships: List[Dict[str, Any]],
        max_items: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Trim file relationships to respect token budget.
        
        Args:
            relationships: List of relationship dicts
            max_items: Maximum number of relationships to keep
        
        Returns:
            Trimmed list of relationships
        """
        # Sort by strength (descending)
        sorted_rels = sorted(relationships, key=lambda r: r.get('strength', 0), reverse=True)
        
        # Keep top N relationships
        trimmed = sorted_rels[:max_items]
        
        # Keep only essential fields
        essential_fields = ['related_file', 'relationship_type', 'strength']
        
        return [
            {k: v for k, v in rel.items() if k in essential_fields}
            for rel in trimmed
        ]
    
    def _enforce_token_budget(self, context: Dict[str, Any], max_tokens: int = 500) -> Dict[str, Any]:
        """
        Enforce overall token budget across all context sources.
        
        Priority order (highest to lowest):
        1. Vision Context (~100 tokens)
        2. Session/Project Context (~100 tokens) 
        3. File Relationships (~150 tokens)
        
        Args:
            context: Context dict with injected data
            max_tokens: Maximum total tokens allowed
        
        Returns:
            Context with trimmed data if needed
        """
        current_tokens = self.get_context_token_count(context)
        
        if current_tokens <= max_tokens:
            return context  # Under budget, no trimming needed
        
        self.logger.warning(
            f"Context token budget exceeded: {current_tokens} > {max_tokens}. "
            f"Trimming lower priority sources."
        )
        
        # Priority 4: Trim file relationships further if over budget
        if 'file_relationships' in context and current_tokens > max_tokens:
            # Reduce file relationships to 3 items
            context['file_relationships'] = context['file_relationships'][:3]
            current_tokens = self.get_context_token_count(context)
        
        # Priority 5: If still over, remove file relationships entirely
        if current_tokens > max_tokens and 'file_relationships' in context:
            del context['file_relationships']
            if 'mentioned_files' in context:
                del context['mentioned_files']
            self.logger.warning("Removed file relationships to meet token budget")
        
        return context
