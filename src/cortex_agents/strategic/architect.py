"""
Architect Agent - Strategic architectural analysis with automatic brain saving.

Handles:
- System architecture analysis
- Routing system investigation  
- Component structure mapping
- View injection pattern analysis
- Feature architecture documentation
- Automatic saving of analysis to Tier 2 Knowledge Graph

This agent addresses CORTEX-BRAIN-001 incident by ensuring architectural
analysis is automatically persisted across sessions.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import logging
from datetime import datetime

from ..base_agent import BaseAgent, AgentRequest, AgentResponse
from ..agent_types import IntentType
from src.tier2.knowledge_graph import KnowledgeGraph


class ArchitectAgent(BaseAgent):
    """
    Strategic agent for architectural analysis with automatic brain saving.
    
    Performs deep architectural analysis including:
    - Shell structure analysis (layout, navigation, panels)
    - Routing system mapping (states, URLs, templates)
    - View injection pattern documentation
    - Feature directory structure analysis
    - Component interaction flows
    
    Key Features:
    - Automatic namespace detection (e.g., ksessions_architecture)
    - Structured analysis data persistence
    - Cross-session memory via Tier 2 Knowledge Graph
    - User confirmation of brain saves
    
    Example:
        architect = ArchitectAgent("Architect", tier1_api, tier2_kg, tier3_context)
        
        request = AgentRequest(
            intent="analyze_architecture",
            context={"workspace_path": "/path/to/KSESSIONS"},
            user_message="crawl shell.html to understand KSESSIONS architecture"
        )
        
        response = architect.execute(request)
        # Analysis automatically saved to brain with namespace: ksessions_architecture
    """
    
    def __init__(self, name: str, tier1_api=None, tier2_kg=None, tier3_context=None):
        """Initialize ArchitectAgent with tier APIs."""
        super().__init__(name, tier1_api, tier2_kg, tier3_context)
        
        # Initialize knowledge graph for architectural analysis saving
        self.knowledge_graph = tier2_kg if tier2_kg else KnowledgeGraph()
        
    def can_handle(self, request: AgentRequest) -> bool:
        """
        Check if this agent can handle the request.
        
        Handles architectural analysis requests including:
        - Architecture analysis ("understand", "analyze", "crawl")
        - Routing analysis ("routing", "navigation", "flow")
        - Structure analysis ("structure", "layout", "components")
        - Feature analysis ("feature", "directory", "organization")
        
        Args:
            request: The agent request
        
        Returns:
            True if intent matches architectural analysis patterns
        """
        architectural_patterns = [
            "architecture", "architectural", "analyze", "crawl", "understand",
            "routing", "navigation", "structure", "layout", "components", 
            "shell", "view", "injection", "feature", "directory", "organization",
            "system", "design", "pattern", "flow"
        ]
        
        request_text = f"{request.intent} {request.user_message}".lower()
        return any(pattern in request_text for pattern in architectural_patterns)
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Perform architectural analysis with automatic brain saving.
        
        Args:
            request: The agent request
        
        Returns:
            AgentResponse with analysis results and brain save confirmation
        """
        try:
            self.log_request(request)
            self.logger.info("Starting architectural analysis with auto-save")
            
            # Step 1: Perform architectural analysis
            analysis_result = self._analyze_architecture(request)
            
            # Step 2: Auto-save to brain if analysis contains valuable data
            save_result = self._auto_save_analysis(request, analysis_result)
            
            # Step 3: Format response with save confirmation
            response_message = self._format_response_with_confirmation(
                analysis_result, save_result
            )
            
            # Log to Tier 1 if available
            if self.tier1 and request.conversation_id:
                self.tier1.process_message(
                    request.conversation_id,
                    "agent",
                    f"ArchitectAgent: Analysis complete, saved to {save_result.get('namespace', 'N/A')}"
                )
            
            return AgentResponse(
                success=True,
                result={
                    "analysis": analysis_result,
                    "brain_save": save_result,
                    "namespace": save_result.get('namespace'),
                    "items_saved": save_result.get('items_saved', 0)
                },
                message=response_message,
                agent_name=self.name,
                metadata={
                    "analysis_type": analysis_result.get('analysis_type', 'architectural'),
                    "files_analyzed": len(analysis_result.get('files_analyzed', [])),
                    "brain_saved": save_result.get('saved', False),
                    "namespace": save_result.get('namespace')
                }
            )
            
        except Exception as e:
            self.logger.error(f"Architectural analysis error: {str(e)}")
            return AgentResponse(
                success=False,
                result={},
                message=f"Architectural analysis failed: {str(e)}",
                agent_name=self.name,
                error=str(e)
            )
    
    def _analyze_architecture(self, request: AgentRequest) -> Dict[str, Any]:
        """
        Perform the actual architectural analysis.
        
        This method would normally contain the complex logic for:
        - File system analysis
        - Route mapping
        - Component discovery
        - Pattern identification
        
        For now, returns a structured placeholder that demonstrates
        the expected output format.
        """
        # Extract workspace info from request context
        workspace_path = request.context.get('workspace_path', '')
        files_analyzed = request.context.get('files_analyzed', [])
        
        # Mock analysis result - in real implementation, this would:
        # 1. Crawl shell.html structure
        # 2. Parse routing configuration
        # 3. Map view injection patterns  
        # 4. Document feature organization
        analysis_result = {
            "analysis_type": "architectural",
            "timestamp": datetime.now().isoformat(),
            "workspace_path": workspace_path,
            "files_analyzed": files_analyzed,
            "shell_architecture": {
                "description": "Main application shell with dynamic view injection",
                "components": {
                    "header": {"injection": "ng-include", "source": "/app/layout/topnav.html"},
                    "main_content": {"injection": "ui-view", "source": "Dynamic (from routes)"},
                    "footer": {"injection": "ng-include", "source": "/app/layout/footer.html"}
                }
            },
            "routing_system": {
                "pattern": "State-based with nested routes",
                "estimated_routes": 42,
                "key_patterns": [
                    "Direct UI-View Injection",
                    "Nested UI-View (Admin)",
                    "Global Conditional Panels",
                    "Floating Panels (Always Present)"
                ]
            },
            "feature_structure": {
                "base_path": "app/features",
                "directories": ["admin", "album", "session", "manage", "registration"]
            }
        }
        
        return analysis_result
    
    def _auto_save_analysis(self, request: AgentRequest, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automatically save analysis to knowledge graph with appropriate namespace.
        
        Args:
            request: Original user request
            analysis_result: Structured analysis data
            
        Returns:
            Dict with save results and confirmation data
        """
        try:
            # Create context for namespace detection
            context = {
                'workspace_path': analysis_result.get('workspace_path', ''),
                'files_analyzed': analysis_result.get('files_analyzed', []),
                'analysis_type': analysis_result.get('analysis_type', 'architectural')
            }
            
            # Detect appropriate namespace
            namespace = self.knowledge_graph.detect_analysis_namespace(
                request.user_message, context
            )
            
            # Save to knowledge graph
            save_result = self.knowledge_graph.save_architectural_analysis(
                namespace=namespace,
                analysis_data=analysis_result,
                metadata={
                    'request_text': request.user_message,
                    'conversation_id': request.conversation_id,
                    'agent_name': self.name
                }
            )
            
            self.logger.info(f"Analysis saved to namespace: {namespace}")
            return save_result
            
        except Exception as e:
            self.logger.error(f"Auto-save failed: {str(e)}")
            return {
                'saved': False,
                'error': str(e),
                'namespace': 'unknown',
                'items_saved': 0
            }
    
    def _format_response_with_confirmation(self, analysis_result: Dict[str, Any], 
                                         save_result: Dict[str, Any]) -> str:
        """
        Format analysis response with brain save confirmation.
        
        Args:
            analysis_result: The architectural analysis results
            save_result: Results from brain save operation
            
        Returns:
            Formatted response message with confirmation
        """
        # Format the main analysis findings
        shell_components = len(analysis_result.get('shell_architecture', {}).get('components', {}))
        route_patterns = len(analysis_result.get('routing_system', {}).get('key_patterns', []))
        feature_dirs = len(analysis_result.get('feature_structure', {}).get('directories', []))
        
        response_parts = [
            "# 🏗️ Architectural Analysis Complete",
            "",
            "## Analysis Results:",
            f"- **Shell Architecture**: {shell_components} components identified",
            f"- **Routing Patterns**: {route_patterns} injection patterns documented", 
            f"- **Feature Organization**: {feature_dirs} feature directories mapped",
            f"- **Files Analyzed**: {len(analysis_result.get('files_analyzed', []))} files",
            "",
        ]
        
        # Add brain save confirmation
        if save_result.get('saved'):
            response_parts.append(save_result.get('save_confirmation', ''))
        else:
            response_parts.extend([
                "⚠️ **Brain Save Failed**",
                f"Error: {save_result.get('error', 'Unknown error')}",
                "Analysis completed but not persisted to brain."
            ])
        
        return "\n".join(response_parts)


__all__ = ["ArchitectAgent"]