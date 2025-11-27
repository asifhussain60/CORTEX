"""
TestGenerator Agent - Modular Version

Analyzes code and generates pytest-compatible test cases.
Creates comprehensive test suites with fixtures, mocks, and edge cases.
"""

import os
from typing import List, Dict, Any
from datetime import datetime

from ..base_agent import BaseAgent, AgentRequest, AgentResponse
from ..agent_types import IntentType
from ..utils import safe_get

from .analyzers import CodeAnalyzer
from .generators import FunctionTestGenerator, ClassTestGenerator
from .templates import TemplateManager
from .test_counter import TestCounter
from .pattern_learner import PatternLearner


class TestGenerator(BaseAgent):
    """
    Generates pytest-compatible test cases from code analysis.
    
    Features:
    - AST-based code analysis
    - pytest-style test generation
    - Mock/fixture templates
    - Pattern learning from Tier 2
    - Coverage-aware generation
    """
    
    def __init__(self, name: str, tier1_api=None, tier2_kg=None, tier3_context=None):
        """Initialize TestGenerator with tier APIs."""
        super().__init__(name, tier1_api, tier2_kg, tier3_context)
        
        # Initialize components
        self.code_analyzer = CodeAnalyzer()
        self.template_manager = TemplateManager()
        self.function_generator = FunctionTestGenerator(self.template_manager)
        self.class_generator = ClassTestGenerator()
        self.test_counter = TestCounter()
        self.pattern_learner = PatternLearner(tier2_kg)
        
        # Common test fixtures
        self.COMMON_FIXTURES = [
            "mock_tier1",
            "mock_tier2", 
            "mock_tier3",
            "temp_file",
            "temp_directory"
        ]
    
    def can_handle(self, request: AgentRequest) -> bool:
        """Check if this agent can handle the request."""
        valid_intents = [
            IntentType.TEST.value,
            IntentType.TDD.value,
            "generate_tests",
            "create_tests",
            "test_generation"
        ]
        return request.intent.lower() in valid_intents
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """Generate test cases for code."""
        try:
            self.log_request(request)
            self.logger.info("Starting test generation")
            
            # Extract rule context for Phase 3: Summary generation control
            rule_context = request.context.get("rule_context", {})
            skip_summary = rule_context.get("skip_summary_generation", False)
            
            # Get file path or code to test
            file_path = safe_get(request.context, "file_path")
            source_code = safe_get(request.context, "source_code")
            target = safe_get(request.context, "target")  # Optional specific target
            
            if not file_path and not source_code:
                return AgentResponse(
                    success=False,
                    result=None,
                    message="No file_path or source_code provided",
                    agent_name=self.name
                )
            
            # Read source code if file path provided
            if file_path and not source_code:
                if not os.path.exists(file_path):
                    return AgentResponse(
                        success=False,
                        result=None,
                        message=f"File not found: {file_path}",
                        agent_name=self.name
                    )
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    source_code = f.read()
            
            # Analyze code structure
            analysis = self.code_analyzer.analyze(source_code, target)
            
            if not analysis["success"]:
                return AgentResponse(
                    success=False,
                    result=analysis,
                    message=analysis.get("error", "Code analysis failed"),
                    agent_name=self.name
                )
            
            # Search Tier 2 for similar test patterns
            similar_patterns = self.pattern_learner.find_similar_patterns(analysis)
            
            # Generate test code
            test_code = self._generate_test_code(analysis, similar_patterns)
            
            # Count generated tests
            test_count = self.test_counter.count(test_code)
            
            # Log to Tier 1 if available
            if self.tier1 and request.conversation_id:
                self.tier1.process_message(
                    request.conversation_id,
                    "agent",
                    f"TestGenerator: Generated {test_count} tests"
                )
            
            # Store pattern in Tier 2 for learning
            self.pattern_learner.store_pattern(analysis, test_code, test_count)
            
            # Build result - conditionally include summary fields based on rule context
            result = {
                "success": True,
                "test_code": test_code,
                "test_count": test_count,
                "file_path": file_path,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add verbose summary only if NOT suppressed
            if not skip_summary:
                result.update({
                    "scenarios": analysis["scenarios"],
                    "functions": len(analysis["functions"]),
                    "classes": len(analysis["classes"])
                })
            
            # Build response message
            if skip_summary:
                # Concise message for execution intents
                message = f"Generated {test_count} tests"
            else:
                # Detailed message for investigation intents
                message = f"Generated {test_count} tests for {len(analysis['functions'])} functions and {len(analysis['classes'])} classes"
            
            response = AgentResponse(
                success=True,
                result=result,
                message=message,
                agent_name=self.name,
                metadata={
                    "test_count": test_count,
                    "skip_summary": skip_summary
                },
                next_actions=self._suggest_next_actions(result) if not skip_summary else ["Run generated tests"]
            )
            
            self.log_response(response)
            return response
            
        except Exception as e:
            self.logger.error(f"Test generation failed: {str(e)}")
            return AgentResponse(
                success=False,
                result=None,
                message=f"Test generation failed: {str(e)}",
                agent_name=self.name
            )
    
    def _generate_test_code(
        self,
        analysis: Dict[str, Any],
        patterns: List[Dict[str, Any]]
    ) -> str:
        """Generate test code from analysis."""
        test_parts = []
        
        # Generate header with imports
        test_parts.append(self.template_manager.test_header(analysis))
        
        # Generate fixtures if needed
        if analysis.get("classes"):
            fixtures = self.template_manager.fixtures(analysis)
            if fixtures:
                test_parts.append(fixtures)
        
        # Generate tests for functions
        for func in analysis.get("functions", []):
            test_parts.append(self.function_generator.generate(func))
        
        # Generate tests for classes
        for cls in analysis.get("classes", []):
            test_parts.append(self.class_generator.generate(cls))
        
        return "\n\n".join(test_parts)
    
    def _suggest_next_actions(self, result: Dict[str, Any]) -> List[str]:
        """Suggest next actions based on generation result."""
        actions = []
        
        if result.get("success"):
            actions.append("Review generated tests")
            actions.append("Run tests to verify functionality")
            actions.append("Add assertions specific to your logic")
            actions.append("Implement mock objects for dependencies")
            
            if result.get("test_count", 0) > 10:
                actions.append("Consider splitting into multiple test files")
        else:
            actions.append("Fix code issues before generating tests")
            actions.append("Ensure code is syntactically valid")
        
        return actions
