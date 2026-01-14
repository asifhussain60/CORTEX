"""
LLM Code Generator - Generate implementation code from AC requirements.

This module provides LLM-powered code generation capabilities:
1. OpenAI/Anthropic integration
2. Context-aware prompts
3. Temperature control
4. Token management
5. Structured output parsing

AC-ID: AC-CODEGEN-001
Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
import logging
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


@dataclass
class CodeGenerationRequest:
    """Request for code generation."""
    ac_id: str
    feature_name: str
    requirements: List[str]
    context: Dict[str, Any]
    target_file: Optional[str] = None
    existing_code: Optional[str] = None
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class CodeGenerationResult:
    """Result of code generation."""
    success: bool
    code: str
    explanation: str
    file_path: Optional[str] = None
    imports: List[str] = None
    tests: Optional[str] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.imports is None:
            self.imports = []


class LLMCodeGenerator:
    """
    LLM-powered code generator.
    
    Generates implementation code from AC requirements using:
    - OpenAI GPT-4 (preferred)
    - Anthropic Claude (fallback)
    
    Acceptance Criteria:
    - AC-CODEGEN-001: LLM integration with context-aware prompts
    - AC-CODEGEN-002: Structured output parsing (code, tests, imports)
    - AC-CODEGEN-003: Token management and error handling
    """
    
    def __init__(
        self,
        provider: LLMProvider = LLMProvider.OPENAI,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ):
        """
        Initialize LLM Code Generator.
        
        Args:
            provider: LLM provider to use
            model: Model name (default: gpt-4 or claude-3-sonnet)
            temperature: Generation temperature (0.0-1.0)
            max_tokens: Maximum tokens in response
        """
        self.logger = logging.getLogger("cortex.tools.llm_code_generator")
        self.provider = provider
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Set default models
        if model:
            self.model = model
        elif provider == LLMProvider.OPENAI:
            self.model = "gpt-4"
        else:
            self.model = "claude-3-sonnet-20240229"
        
        # Initialize client
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize LLM client."""
        if self.provider == LLMProvider.OPENAI:
            if not OPENAI_AVAILABLE:
                raise ImportError("openai package not installed. Run: pip install openai")
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            self.client = openai.OpenAI(api_key=api_key)
            self.logger.info(f"Initialized OpenAI client with model {self.model}")
            
        elif self.provider == LLMProvider.ANTHROPIC:
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("anthropic package not installed. Run: pip install anthropic")
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")
            self.client = anthropic.Anthropic(api_key=api_key)
            self.logger.info(f"Initialized Anthropic client with model {self.model}")
    
    def generate_code(
        self,
        request: CodeGenerationRequest
    ) -> CodeGenerationResult:
        """
        Generate implementation code from AC requirements.
        
        Args:
            request: Code generation request
            
        Returns:
            CodeGenerationResult with generated code
        """
        try:
            # Build prompt
            prompt = self._build_prompt(request)
            
            # Generate via LLM
            if self.provider == LLMProvider.OPENAI:
                response = self._generate_openai(prompt)
            else:
                response = self._generate_anthropic(prompt)
            
            # Parse response
            result = self._parse_response(response, request)
            
            self.logger.info(f"Generated code for {request.ac_id}: {len(result.code)} chars")
            return result
            
        except Exception as e:
            self.logger.error(f"Code generation failed: {e}")
            return CodeGenerationResult(
                success=False,
                code="",
                explanation="",
                error=str(e)
            )
    
    def _build_prompt(self, request: CodeGenerationRequest) -> str:
        """Build context-aware prompt for code generation."""
        lines = [
            "You are an expert Python developer implementing CORTEX 6.0 features.",
            "",
            f"## Task: Implement {request.ac_id}",
            f"Feature: {request.feature_name}",
            "",
            "## Requirements:",
        ]
        
        for i, req in enumerate(request.requirements, 1):
            lines.append(f"{i}. {req}")
        
        lines.extend([
            "",
            "## Context:",
            f"- Target file: {request.target_file or 'New file'}",
        ])
        
        if request.dependencies:
            lines.append("- Dependencies:")
            for dep in request.dependencies:
                lines.append(f"  - {dep}")
        
        if request.existing_code:
            lines.extend([
                "",
                "## Existing Code:",
                "```python",
                request.existing_code,
                "```"
            ])
        
        lines.extend([
            "",
            "## Instructions:",
            "1. Generate production-ready Python code",
            "2. Include comprehensive docstrings",
            "3. Add type hints",
            "4. Follow PEP 8 style",
            "5. Include error handling",
            "6. Generate unit tests",
            "",
            "## Output Format:",
            "Provide your response in this JSON structure:",
            "```json",
            "{",
            '  "code": "# Python implementation code",',
            '  "explanation": "Brief explanation of implementation",',
            '  "imports": ["import statements"],',
            '  "tests": "# Unit test code",',
            '  "file_path": "suggested/file/path.py"',
            "}",
            "```"
        ])
        
        return "\n".join(lines)
    
    def _generate_openai(self, prompt: str) -> str:
        """Generate via OpenAI API."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Python developer. Generate clean, well-documented code."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        return response.choices[0].message.content
    
    def _generate_anthropic(self, prompt: str) -> str:
        """Generate via Anthropic API."""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        return message.content[0].text
    
    def _parse_response(
        self,
        response: str,
        request: CodeGenerationRequest
    ) -> CodeGenerationResult:
        """Parse LLM response into structured result."""
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                # Fallback: treat entire response as code
                return CodeGenerationResult(
                    success=True,
                    code=response,
                    explanation="Generated code (no structured output)",
                    file_path=request.target_file
                )
            
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
            
            return CodeGenerationResult(
                success=True,
                code=data.get("code", ""),
                explanation=data.get("explanation", ""),
                file_path=data.get("file_path") or request.target_file,
                imports=data.get("imports", []),
                tests=data.get("tests")
            )
            
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse JSON response: {e}")
            # Fallback: extract code blocks
            code_blocks = []
            in_code_block = False
            current_block = []
            
            for line in response.split('\n'):
                if line.strip().startswith('```python'):
                    in_code_block = True
                    current_block = []
                elif line.strip() == '```' and in_code_block:
                    in_code_block = False
                    code_blocks.append('\n'.join(current_block))
                elif in_code_block:
                    current_block.append(line)
            
            if code_blocks:
                return CodeGenerationResult(
                    success=True,
                    code=code_blocks[0],
                    explanation="Extracted from markdown code block",
                    file_path=request.target_file,
                    tests=code_blocks[1] if len(code_blocks) > 1 else None
                )
            
            return CodeGenerationResult(
                success=False,
                code="",
                explanation="",
                error=f"Failed to parse response: {e}"
            )
    
    def generate_batch(
        self,
        requests: List[CodeGenerationRequest]
    ) -> List[CodeGenerationResult]:
        """
        Generate code for multiple AC-IDs.
        
        Args:
            requests: List of generation requests
            
        Returns:
            List of generation results
        """
        results = []
        for request in requests:
            result = self.generate_code(request)
            results.append(result)
        return results
