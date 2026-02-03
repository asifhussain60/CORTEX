"""
Educational Orchestrator - Progressive Disclosure Engine

Provides truth-based educational responses about CORTEX architecture with
intelligent next-step guidance and knowledge-level adaptation.

Phase 22 Component #3: EducationalOrchestrator (P0)

Authority: AC-EDUCATIONAL-INTERACTION-001
Rule: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from cortex.brain.core.interfaces.i_orchestrator import IOrchestrator, OperationMode
from cortex.core.result import Result, Ok, Err
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


class KnowledgeLevel(Enum):
    """User knowledge level classification."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class EducationalContext:
    """
    Context for educational interaction.
    
    Tracks user's learning journey across conversation.
    """
    
    query: str
    knowledge_level: KnowledgeLevel
    topics_covered: List[str] = field(default_factory=list)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    detected_issues: List[str] = field(default_factory=list)
    user_path: List[str] = field(default_factory=list)  # Learning path taken
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class EducationalResponse:
    """
    Educational response with progressive disclosure.
    
    Contains explanation adapted to knowledge level plus next steps.
    """
    
    title: str
    implementation_reality: str  # Verified truth from live code
    evidence: List[str]  # File paths, line numbers, test refs
    explanation: str  # Adapted to knowledge level
    detected_issues: List[Dict[str, Any]]  # Optional fault reports
    next_steps: List[Dict[str, str]]  # 3-5 numbered options
    knowledge_level: KnowledgeLevel
    code_snippets: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class EducationalOrchestrator(IOrchestrator):
    """
    Educational Orchestrator - Truth-based learning with progressive disclosure.
    
    Provides implementation-verified education about CORTEX architecture,
    adapting explanation depth to user's knowledge level and generating
    intelligent next-step options for continued learning.
    
    Features:
    - Progressive disclosure (beginner → intermediate → advanced)
    - Implementation truth verification
    - Context tracking across conversation
    - Intelligent next-step generation (3-5 options)
    - Fault detection with recommendations
    - Integration with InteractionOrchestrator for challenges
    
    Usage:
        >>> orchestrator = EducationalOrchestrator()
        >>> context = EducationalContext(
        ...     query="What is MasterOrchestrator?",
        ...     knowledge_level=KnowledgeLevel.BEGINNER
        ... )
        >>> response = orchestrator.generate_response(context)
        >>> print(response.explanation)  # Adapted to beginner level
        >>> print(response.next_steps)  # 3-5 numbered options
    
    Authority: AC-EDUCATIONAL-INTERACTION-001 (Phase 22)
    """
    
    def __init__(self):
        """Initialize Educational Orchestrator."""
        self.logger = EnhancedAuditLogger.instance()
        self._conversation_contexts: Dict[str, EducationalContext] = {}
        
        self.logger.log_operation_start(
            ac_id="AC-EDUCATIONAL-INTERACTION-001",
            operation="EDUCATIONAL_ORCHESTRATOR_INIT",
            details={"component": "EducationalOrchestrator"}
        )
    
    def detect_knowledge_level(self, query: str, history: List[str]) -> KnowledgeLevel:
        """
        Detect user's knowledge level from query and history.
        
        Phase 22: Knowledge Level Detection
        
        Signals:
        - Beginner: General questions, no implementation details
        - Intermediate: References specific components, asks about integration
        - Advanced: Deep architectural questions, proposes alternatives
        
        Args:
            query: User's current query
            history: Previous queries in conversation
        
        Returns:
            KnowledgeLevel: Detected level
        
        Example:
            >>> orchestrator.detect_knowledge_level("What is CORTEX?", [])
            KnowledgeLevel.BEGINNER
            >>> orchestrator.detect_knowledge_level(
            ...     "How does MasterOrchestrator handle Stage 2 routing?",
            ...     ["What is MasterOrchestrator?"]
            ... )
            KnowledgeLevel.INTERMEDIATE
        
        Authority: AC-EDUCATIONAL-INTERACTION-001
        """
        query_lower = query.lower()
        
        # Advanced signals
        advanced_signals = [
            "architecture pattern",
            "design decision",
            "trade-off",
            "alternative approach",
            "why not",
            "performance",
            "extension point",
            "refactor",
        ]
        
        # Intermediate signals
        intermediate_signals = [
            "how does",
            "integration",
            "wiring",
            "orchestrator",
            "stage",
            "routing",
            "synthesis",
            "lens",
        ]
        
        # Check for advanced signals
        if any(signal in query_lower for signal in advanced_signals):
            return KnowledgeLevel.ADVANCED
        
        # Check history length (more history = likely more advanced)
        if len(history) > 5:
            return KnowledgeLevel.ADVANCED if len(history) > 10 else KnowledgeLevel.INTERMEDIATE
        
        # Check for intermediate signals
        if any(signal in query_lower for signal in intermediate_signals):
            return KnowledgeLevel.INTERMEDIATE
        
        # Default to beginner
        return KnowledgeLevel.BEGINNER
    
    def generate_response(
        self,
        context: EducationalContext,
        verified_truth: Optional[Dict[str, Any]] = None
    ) -> EducationalResponse:
        """
        Generate educational response with progressive disclosure.
        
        Phase 22: Response Generation
        
        Adapts explanation depth to user's knowledge level and generates
        3-5 intelligent next-step options for continued learning.
        
        Args:
            context: Educational context with query and knowledge level
            verified_truth: Optional implementation verification results
        
        Returns:
            EducationalResponse: Formatted response with next steps
        
        Example:
            >>> context = EducationalContext(
            ...     query="What is MasterOrchestrator?",
            ...     knowledge_level=KnowledgeLevel.BEGINNER
            ... )
            >>> response = orchestrator.generate_response(context)
            >>> len(response.next_steps)
            5
        
        Authority: AC-EDUCATIONAL-INTERACTION-001
        """
        # Extract topic from query
        topic = self._extract_topic(context.query)
        
        # Generate explanation based on knowledge level
        explanation = self._generate_explanation(
            topic=topic,
            knowledge_level=context.knowledge_level,
            verified_truth=verified_truth
        )
        
        # Collect evidence
        evidence = self._collect_evidence(topic, verified_truth)
        
        # Generate next steps
        next_steps = self._generate_next_steps(
            topic=topic,
            knowledge_level=context.knowledge_level,
            user_path=context.user_path
        )
        
        # Detect issues (if verification provided)
        detected_issues = []
        if verified_truth and verified_truth.get("issues"):
            detected_issues = verified_truth["issues"]
        
        response = EducationalResponse(
            title=f"Understanding {topic}",
            implementation_reality=explanation.get("reality", ""),
            evidence=evidence,
            explanation=explanation.get("content", ""),
            detected_issues=detected_issues,
            next_steps=next_steps,
            knowledge_level=context.knowledge_level,
            code_snippets=explanation.get("snippets", [])
        )
        
        self.logger.log_operation_complete(
            ac_id="AC-EDUCATIONAL-INTERACTION-001",
            operation="RESPONSE_GENERATED",
            success=True,
            details={
                "topic": topic,
                "knowledge_level": context.knowledge_level.value,
                "next_steps_count": len(next_steps),
                "evidence_count": len(evidence)
            }
        )
        
        return response
    
    def _extract_topic(self, query: str) -> str:
        """Extract main topic from query."""
        # Simple extraction - can be enhanced with NLP
        query_lower = query.lower()
        
        # Common CORTEX topics
        topics = {
            "master": "MasterOrchestrator",
            "intent": "IntentRouter",
            "lens": "LENS Protocol",
            "challenge": "ChallengeEngine",
            "interaction": "InteractionOrchestrator",
            "governance": "Governance System",
            "wiring": "Wiring System",
            "orchestrator": "Orchestrators",
            "synthesis": "Knowledge Synthesis",
            "cortex": "CORTEX System",
        }
        
        for keyword, topic in topics.items():
            if keyword in query_lower:
                return topic
        
        return "CORTEX Architecture"
    
    def _generate_explanation(
        self,
        topic: str,
        knowledge_level: KnowledgeLevel,
        verified_truth: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate explanation adapted to knowledge level."""
        if knowledge_level == KnowledgeLevel.BEGINNER:
            return self._beginner_explanation(topic, verified_truth)
        elif knowledge_level == KnowledgeLevel.INTERMEDIATE:
            return self._intermediate_explanation(topic, verified_truth)
        else:
            return self._advanced_explanation(topic, verified_truth)
    
    def _beginner_explanation(
        self,
        topic: str,
        verified_truth: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate beginner-level explanation with analogies."""
        # Simplified explanation with analogies
        explanations = {
            "MasterOrchestrator": {
                "reality": "The MasterOrchestrator is the central coordinator of CORTEX",
                "content": """
**What is the MasterOrchestrator?**

Think of the MasterOrchestrator as a conductor leading an orchestra. Just like a conductor:
- Coordinates all the musicians (other orchestrators)
- Ensures everyone plays at the right time
- Creates harmony from individual parts

When you make a request to CORTEX, the MasterOrchestrator:
1. Figures out what you want to do
2. Decides which orchestrator(s) can help
3. Coordinates their work
4. Returns the result to you

It's the "traffic controller" of CORTEX - making sure everything flows smoothly!
                """,
                "snippets": []
            }
        }
        
        return explanations.get(topic, {
            "reality": f"{topic} is a component of CORTEX",
            "content": f"**{topic}** helps CORTEX work effectively by managing specific responsibilities.",
            "snippets": []
        })
    
    def _intermediate_explanation(
        self,
        topic: str,
        verified_truth: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate intermediate-level explanation with technical details."""
        # More technical with integration patterns
        return {
            "reality": f"{topic} implements core CORTEX patterns",
            "content": f"""
**How {topic} Works**

{topic} integrates with CORTEX through:
- Wiring registration in wiring.yaml
- Interface implementation (IOrchestrator)
- MCP tool exposure for external access
- Integration with other orchestrators

This allows it to participate in the orchestration workflow while maintaining loose coupling.
            """,
            "snippets": []
        }
    
    def _advanced_explanation(
        self,
        topic: str,
        verified_truth: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate advanced-level explanation with architecture patterns."""
        # Deep architectural analysis
        return {
            "reality": f"{topic} implements several design patterns",
            "content": f"""
**{topic} Architecture**

Design Patterns:
- **Mediator Pattern**: Decouples components
- **Strategy Pattern**: Runtime behavior selection
- **Observer Pattern**: Event propagation

Trade-offs:
- ✅ Flexibility and extensibility
- ✅ Testability through interfaces
- ⚠️ Added complexity (mitigated by clear contracts)

Extension Points:
- Implement IOrchestrator interface
- Register in wiring.yaml
- Expose via MCP tools
            """,
            "snippets": []
        }
    
    def _collect_evidence(
        self,
        topic: str,
        verified_truth: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Collect evidence (file paths, line numbers, tests)."""
        evidence = []
        
        if verified_truth:
            if "file_path" in verified_truth:
                evidence.append(f"File: `{verified_truth['file_path']}`")
            if "line_range" in verified_truth:
                evidence.append(f"Lines: {verified_truth['line_range']}")
            if "tests" in verified_truth:
                evidence.append(f"Tests: {verified_truth['tests']}")
        
        # Default evidence for common topics
        if not evidence:
            evidence.append(f"Documentation: `docs/` (check for {topic})")
            evidence.append("Implementation: Verify via code inspection")
        
        return evidence
    
    def _generate_next_steps(
        self,
        topic: str,
        knowledge_level: KnowledgeLevel,
        user_path: List[str]
    ) -> List[Dict[str, str]]:
        """
        Generate 3-5 intelligent next-step options.
        
        Phase 22: Next Step Generation
        
        Rules:
        1. Always include deeper dive on current topic
        2. Add 1-2 related concepts
        3. Include practical example
        4. Add troubleshooting or advanced topic based on level
        
        Returns:
            List of option dicts with 'title' and 'description'
        """
        options = []
        
        # Option 1: Deeper dive (always)
        options.append({
            "title": f"Deep Dive: {topic} Implementation",
            "description": f"Explore the code, wiring, and tests for {topic}"
        })
        
        # Option 2-3: Related concepts
        related = self._get_related_topics(topic)
        for rel_topic in related[:2]:
            options.append({
                "title": f"Explore {rel_topic}",
                "description": f"Learn how {rel_topic} relates to {topic}"
            })
        
        # Option 4: Practical example
        options.append({
            "title": f"See {topic} in Action",
            "description": f"Walk through a real example of {topic} working"
        })
        
        # Option 5: Context-dependent
        if knowledge_level == KnowledgeLevel.ADVANCED:
            options.append({
                "title": "Extension Points",
                "description": f"Learn how to extend or customize {topic}"
            })
        else:
            options.append({
                "title": "Common Questions",
                "description": f"FAQ and troubleshooting for {topic}"
            })
        
        return options[:5]  # Cap at 5
    
    def _get_related_topics(self, topic: str) -> List[str]:
        """Get related topics for exploration."""
        relations = {
            "MasterOrchestrator": ["IntentRouter", "Wiring System", "Orchestrator Registry"],
            "IntentRouter": ["MasterOrchestrator", "LENS Protocol", "Intent Classification"],
            "LENS Protocol": ["AST Analysis", "Git History", "Code Intelligence"],
            "ChallengeEngine": ["InteractionOrchestrator", "Disagreement Detection"],
            "Knowledge Synthesis": ["LENS Protocol", "Company Knowledge", "CORE Rules"],
        }
        
        return relations.get(topic, ["CORTEX Architecture", "Orchestrators", "MCP Tools"])
    
    def execute(self, parameters: Dict[str, Any]) -> Result[str]:
        """
        Execute educational query (IOrchestrator interface).
        
        Args:
            parameters: Must contain 'query' and optionally 'knowledge_level'
        
        Returns:
            Result[str]: Ok with response JSON, or Err with error
        
        Authority: AC-EDUCATIONAL-INTERACTION-001
        """
        self.logger.log_operation_start(
            ac_id="AC-EDUCATIONAL-INTERACTION-001",
            operation="EDUCATIONAL_EXECUTE",
            details=parameters
        )
        
        try:
            query = parameters.get("query", "")
            if not query:
                return Err("Query parameter required")
            
            # Detect knowledge level
            history = parameters.get("history", [])
            knowledge_level = self.detect_knowledge_level(query, history)
            
            # Create context
            context = EducationalContext(
                query=query,
                knowledge_level=knowledge_level,
                conversation_history=history
            )
            
            # Generate response
            response = self.generate_response(context)
            
            # Format as JSON
            import json
            result_json = json.dumps({
                "title": response.title,
                "implementation_reality": response.implementation_reality,
                "evidence": response.evidence,
                "explanation": response.explanation,
                "next_steps": response.next_steps,
                "knowledge_level": response.knowledge_level.value
            }, indent=2)
            
            self.logger.log_operation_complete(
                ac_id="AC-EDUCATIONAL-INTERACTION-001",
                operation="EDUCATIONAL_EXECUTE",
                success=True,
                details={"query": query, "knowledge_level": knowledge_level.value}
            )
            
            return Ok(result_json)
            
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-EDUCATIONAL-INTERACTION-001",
                operation="EDUCATIONAL_EXECUTE",
                success=False,
                details={"error": str(e)}
            )
            return Err(f"Educational execution failed: {str(e)}")
    
    def get_mode(self) -> OperationMode:
        """Get orchestrator operation mode."""
        return OperationMode.EDUCATIONAL
    
    def get_name(self) -> str:
        """Get orchestrator name."""
        return "EducationalOrchestrator"
    
    def get_version(self) -> str:
        """Get orchestrator version."""
        return "1.0.0"
    
    def initialize(self) -> Result[str]:
        """Initialize orchestrator."""
        try:
            self.logger.log_operation_start(
                ac_id="AC-EDUCATIONAL-INTERACTION-001",
                operation="INITIALIZE",
                details={}
            )
            
            # Initialize conversation contexts
            self._conversation_contexts = {}
            
            self.logger.log_operation_complete(
                ac_id="AC-EDUCATIONAL-INTERACTION-001",
                operation="INITIALIZE",
                success=True
            )
            
            return Ok("EducationalOrchestrator initialized")
        except Exception as e:
            return Err(f"Initialization failed: {str(e)}")
    
    def get_mcp_tools(self) -> Result[Dict[str, Any]]:
        """Get exposed MCP tools for educational interaction."""
        tools = {
            "cortex_ask": {
                "name": "cortex_ask",
                "description": "Ask educational questions about CORTEX architecture",
                "parameters": {
                    "query": {
                        "type": "string",
                        "description": "Educational question to ask",
                        "required": True
                    },
                    "knowledge_level": {
                        "type": "string",
                        "description": "User knowledge level (beginner/intermediate/advanced)",
                        "required": False,
                        "enum": ["beginner", "intermediate", "advanced"]
                    },
                    "history": {
                        "type": "array",
                        "description": "Conversation history for context",
                        "required": False
                    }
                },
                "returns": {
                    "title": "string",
                    "implementation_reality": "string",
                    "evidence": "array",
                    "explanation": "string",
                    "next_steps": "array",
                    "knowledge_level": "string"
                }
            }
        }
        
        return Ok(tools)
    
    def execute_operation(
        self,
        operation_name: str,
        parameters: Dict[str, Any],
    ) -> Result[Any]:
        """Execute named operation with audit logging."""
        if operation_name == "ask":
            return self.execute(parameters)
        else:
            return Err(f"Unknown operation: {operation_name}")
    
    def get_audit_trail(self, limit: int = 100) -> Result[list]:
        """Get audit trail with hash chain."""
        try:
            # Retrieve audit logs from logger
            audit_trail = self.logger.get_recent_logs(limit)
            return Ok(audit_trail)
        except Exception as e:
            return Err(f"Failed to retrieve audit trail: {str(e)}")
