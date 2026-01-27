"""InquiryOrchestrator - Main entry point for inquiry system.

AC-ID: INQUIRY-014
Purpose: Orchestrate the complete inquiry pipeline
Author: Asif Hussain
Date: 2026-01-27

Pipeline:
1. Detect repository type (CORTEX vs. user)
2. Assemble context (evidence + knowledge)
3. Route to appropriate handler
4. Return formatted response
"""

from pathlib import Path
from typing import Any, Dict, Optional

from cortex.models.inquiry_models import InquiryCategory, RepoContext
from cortex.orchestrators.support.repo_detection_orchestrator import (
    RepoDetectionOrchestrator,
)
from cortex.orchestrators.support.context_assembly_orchestrator import (
    ContextAssemblyOrchestrator,
)
from cortex.orchestrators.domain.inquiry.inquiry_router import InquiryRouter


class InquiryOrchestrator:
    """Main orchestrator for inquiry system.
    
    Coordinates repo detection, context assembly, and handler routing
    to answer questions about CORTEX or user repositories.
    """
    
    def __init__(
        self,
        repo_path: Optional[Path] = None,
        cache_path: Optional[Path] = None,
    ) -> None:
        """Initialize inquiry orchestrator.
        
        Args:
            repo_path: Repository path (defaults to cwd)
            cache_path: Cache database path
        """
        self.repo_path = repo_path or Path.cwd()
        
        # Initialize components
        self.repo_detector = RepoDetectionOrchestrator()
        self.context_assembler = ContextAssemblyOrchestrator(cache_path=cache_path)
        self.router = InquiryRouter()
    
    def ask(
        self,
        question: str,
        category_hint: Optional[InquiryCategory] = None,
        file_paths: Optional[list[str]] = None,
    ) -> Dict[str, Any]:
        """Ask a question about the codebase.
        
        Main entry point for inquiry system. Handles the complete pipeline:
        1. Detect repository type
        2. Assemble context
        3. Route to handler
        4. Return response
        
        Args:
            question: Natural language question
            category_hint: Optional category hint for optimization
            file_paths: Optional file paths for evidence
            
        Returns:
            Response dictionary with answer, evidence, confidence
        """
        # Step 1: Detect repository type
        repo_context = self.repo_detector.detect_repository(
            question=question,
            current_directory=self.repo_path,
            file_paths=file_paths,
        )
        
        # Step 2: Assemble context
        assembled_context = self.context_assembler.assemble_context(
            question=question,
            repo_context=repo_context,
            category=category_hint,
        )
        
        # Step 3: Route to appropriate handler
        handler = self.router.route(assembled_context)
        
        # Step 4: Execute handler and return response
        response = handler.handle(assembled_context)
        
        # Add metadata
        response["repo_type"] = repo_context.repo_type.value
        response["repo_name"] = repo_context.repo_name
        response["category"] = assembled_context.category.value
        response["cache_hit"] = assembled_context.cache_hit
        
        return response
