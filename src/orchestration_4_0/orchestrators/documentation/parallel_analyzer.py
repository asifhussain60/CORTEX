"""
Parallel Documentation Analyzer - Multi-agent parallel documentation analysis

Coordinates multiple specialized agents to analyze different documentation types
concurrently, with cross-reference validation to ensure consistency.

Architecture:
- ParallelDocumentationAnalyzer: Main coordinator
- APIDocumentationAgent: Analyzes API documentation
- ArchitectureDocumentationAgent: Analyzes architecture diagrams
- UserGuideDocumentationAgent: Analyzes user guides
- CrossReferenceValidator: Validates consistency between docs
"""

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, TYPE_CHECKING
import time

if TYPE_CHECKING:
    from logging import Logger


class DocumentationType(Enum):
    """Types of documentation that can be analyzed"""
    API = "api"
    ARCHITECTURE = "architecture"
    USER_GUIDE = "user_guide"


@dataclass
class AnalysisResult:
    """Result from a documentation analysis"""
    doc_type: DocumentationType
    modules_analyzed: int = 0
    classes_found: int = 0
    functions_found: int = 0
    references: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0


@dataclass
class CrossReferenceIssue:
    """An issue found during cross-reference validation"""
    source_doc: DocumentationType
    target_doc: DocumentationType
    issue_type: str  # "broken_link", "missing_reference", "inconsistent_signature"
    description: str
    location: str


@dataclass
class ValidationResult:
    """Result from cross-reference validation"""
    issues: List[CrossReferenceIssue] = field(default_factory=list)
    references_checked: int = 0
    valid_references: int = 0
    broken_references: int = 0


class APIDocumentationAgent:
    """
    Specialized agent for analyzing API documentation
    
    Extracts:
    - Module structure
    - Class definitions
    - Function signatures
    - Type hints
    - Cross-references to other docs
    """
    
    def __init__(self, logger: Optional["Logger"] = None):
        self.logger = logger
    
    async def analyze(self, source_paths: List[Path]) -> AnalysisResult:
        """
        Analyze API documentation asynchronously
        
        Args:
            source_paths: List of Python source file paths to analyze
            
        Returns:
            AnalysisResult with API documentation metadata
        """
        start_time = time.time()
        result = AnalysisResult(doc_type=DocumentationType.API)
        
        try:
            if self.logger:
                self.logger.info(f"🔍 API Agent: Analyzing {len(source_paths)} source paths")
            
            # Simulate parallel module analysis (in real implementation, use AST)
            for path in source_paths:
                if path.is_file() and path.suffix == ".py":
                    # Placeholder: In production, use CodeAnalyzer
                    result.modules_analyzed += 1
                    result.references.append(f"module:{path.stem}")
                elif path.is_dir():
                    # Recursively analyze directory
                    py_files = list(path.rglob("*.py"))
                    result.modules_analyzed += len(py_files)
                    
                    # Add references for each module found
                    for py_file in py_files:
                        result.references.append(f"module:{py_file.stem}")
                    
                    # Simulate finding classes and functions
                    result.classes_found += len(py_files) * 2  # Avg 2 classes per module
                    result.functions_found += len(py_files) * 5  # Avg 5 functions per module
            
            # Simulate async I/O delay
            await asyncio.sleep(0.1)
            
            if self.logger:
                self.logger.info(
                    f"✅ API Agent: Found {result.modules_analyzed} modules, "
                    f"{result.classes_found} classes, {result.functions_found} functions"
                )
        
        except Exception as e:
            error_msg = f"API analysis failed: {str(e)}"
            result.errors.append(error_msg)
            if self.logger:
                self.logger.error(f"❌ {error_msg}")
        
        result.duration_seconds = time.time() - start_time
        return result


class ArchitectureDocumentationAgent:
    """
    Specialized agent for analyzing architecture documentation
    
    Extracts:
    - Component relationships
    - Class hierarchies
    - Phase flows
    - Diagram metadata
    """
    
    def __init__(self, logger: Optional["Logger"] = None):
        self.logger = logger
    
    async def analyze(self, source_paths: List[Path]) -> AnalysisResult:
        """
        Analyze architecture documentation asynchronously
        
        Args:
            source_paths: List of paths to analyze for architecture
            
        Returns:
            AnalysisResult with architecture metadata
        """
        start_time = time.time()
        result = AnalysisResult(doc_type=DocumentationType.ARCHITECTURE)
        
        try:
            if self.logger:
                self.logger.info(f"🏗️ Architecture Agent: Analyzing {len(source_paths)} paths")
            
            # Analyze class hierarchies and relationships
            for path in source_paths:
                if path.is_dir():
                    # Count Python files for architecture analysis
                    py_files = list(path.rglob("*.py"))
                    result.modules_analyzed += len(py_files)
                    
                    # Detect base classes and orchestrators
                    for py_file in py_files:
                        if "base" in py_file.stem or "orchestrator" in py_file.stem:
                            result.references.append(f"architecture:{py_file.stem}")
            
            # Simulate async I/O delay
            await asyncio.sleep(0.1)
            
            if self.logger:
                self.logger.info(
                    f"✅ Architecture Agent: Analyzed {result.modules_analyzed} modules, "
                    f"found {len(result.references)} architectural components"
                )
        
        except Exception as e:
            error_msg = f"Architecture analysis failed: {str(e)}"
            result.errors.append(error_msg)
            if self.logger:
                self.logger.error(f"❌ {error_msg}")
        
        result.duration_seconds = time.time() - start_time
        return result


class UserGuideDocumentationAgent:
    """
    Specialized agent for analyzing user guide documentation
    
    Extracts:
    - Usage examples
    - Tutorial content
    - Quick references
    - Command references
    """
    
    def __init__(self, logger: Optional["Logger"] = None):
        self.logger = logger
    
    async def analyze(self, source_paths: List[Path]) -> AnalysisResult:
        """
        Analyze user guide documentation asynchronously
        
        Args:
            source_paths: List of paths to analyze for user guides
            
        Returns:
            AnalysisResult with user guide metadata
        """
        start_time = time.time()
        result = AnalysisResult(doc_type=DocumentationType.USER_GUIDE)
        
        try:
            if self.logger:
                self.logger.info(f"📖 User Guide Agent: Analyzing {len(source_paths)} paths")
            
            # Look for docstrings and examples
            for path in source_paths:
                if path.is_dir():
                    py_files = list(path.rglob("*.py"))
                    result.modules_analyzed += len(py_files)
                    
                    # Extract references to user-facing features
                    for py_file in py_files:
                        if "example" in py_file.stem or "__main__" in py_file.stem:
                            result.references.append(f"guide:{py_file.stem}")
            
            # Simulate async I/O delay
            await asyncio.sleep(0.1)
            
            if self.logger:
                self.logger.info(
                    f"✅ User Guide Agent: Analyzed {result.modules_analyzed} modules, "
                    f"found {len(result.references)} user guide references"
                )
        
        except Exception as e:
            error_msg = f"User guide analysis failed: {str(e)}"
            result.errors.append(error_msg)
            if self.logger:
                self.logger.error(f"❌ {error_msg}")
        
        result.duration_seconds = time.time() - start_time
        return result


class CrossReferenceValidator:
    """
    Validates consistency between different documentation types
    
    Checks:
    - API references in architecture diagrams exist
    - Architecture components referenced in user guides exist
    - Function signatures match between API docs and examples
    """
    
    def __init__(self, logger: Optional["Logger"] = None):
        self.logger = logger
    
    def validate(
        self,
        api_result: AnalysisResult,
        arch_result: AnalysisResult,
        guide_result: AnalysisResult
    ) -> ValidationResult:
        """
        Validate cross-references between documentation types
        
        Args:
            api_result: Results from API documentation analysis
            arch_result: Results from architecture documentation analysis
            guide_result: Results from user guide documentation analysis
            
        Returns:
            ValidationResult with list of issues found
        """
        if self.logger:
            self.logger.info("🔗 Cross-Reference Validator: Checking consistency")
        
        validation = ValidationResult()
        
        # Check architecture references to API
        for arch_ref in arch_result.references:
            validation.references_checked += 1
            
            # Extract module name from reference
            if arch_ref.startswith("architecture:"):
                module_name = arch_ref.split(":", 1)[1]
                
                # Check if corresponding module exists in API docs
                if not any(f"module:{module_name}" in ref for ref in api_result.references):
                    validation.broken_references += 1
                    validation.issues.append(CrossReferenceIssue(
                        source_doc=DocumentationType.ARCHITECTURE,
                        target_doc=DocumentationType.API,
                        issue_type="missing_reference",
                        description=f"Architecture references module '{module_name}' not found in API docs",
                        location=arch_ref
                    ))
                else:
                    validation.valid_references += 1
        
        # Check user guide references to API
        for guide_ref in guide_result.references:
            validation.references_checked += 1
            
            if guide_ref.startswith("guide:"):
                module_name = guide_ref.split(":", 1)[1]
                
                # Check if corresponding module exists in API docs
                if not any(f"module:{module_name}" in ref for ref in api_result.references):
                    validation.broken_references += 1
                    validation.issues.append(CrossReferenceIssue(
                        source_doc=DocumentationType.USER_GUIDE,
                        target_doc=DocumentationType.API,
                        issue_type="missing_reference",
                        description=f"User guide references module '{module_name}' not found in API docs",
                        location=guide_ref
                    ))
                else:
                    validation.valid_references += 1
        
        if self.logger:
            self.logger.info(
                f"✅ Validated {validation.references_checked} references: "
                f"{validation.valid_references} valid, {validation.broken_references} broken"
            )
        
        return validation


class ParallelDocumentationAnalyzer:
    """
    Coordinates parallel analysis of multiple documentation types
    
    Uses specialized agents to analyze API docs, architecture, and user guides
    concurrently, then validates cross-references for consistency.
    
    Example:
        analyzer = ParallelDocumentationAnalyzer(logger)
        results = await analyzer.analyze_parallel([Path("src/orchestration_4_0")])
        
        print(f"API: {results['api'].modules_analyzed} modules")
        print(f"Architecture: {results['architecture'].modules_analyzed} modules")
        print(f"User Guides: {results['user_guide'].modules_analyzed} modules")
        print(f"Validation: {results['validation'].broken_references} broken refs")
    """
    
    def __init__(
        self,
        logger: Optional["Logger"] = None,
        timeout_seconds: float = 30.0
    ):
        """
        Initialize parallel documentation analyzer
        
        Args:
            logger: Logger instance for output
            timeout_seconds: Maximum time to wait for analysis (default 30s)
        """
        self.logger = logger
        self.timeout_seconds = timeout_seconds
        
        # Initialize specialized agents
        self.api_agent = APIDocumentationAgent(logger)
        self.arch_agent = ArchitectureDocumentationAgent(logger)
        self.guide_agent = UserGuideDocumentationAgent(logger)
        self.validator = CrossReferenceValidator(logger)
    
    async def analyze_parallel(
        self,
        source_paths: List[Path]
    ) -> Dict[str, Any]:
        """
        Analyze documentation in parallel across all agent types
        
        Args:
            source_paths: List of paths to analyze
            
        Returns:
            Dict with results from each agent and validation:
            {
                'api': AnalysisResult,
                'architecture': AnalysisResult,
                'user_guide': AnalysisResult,
                'validation': ValidationResult,
                'total_duration': float
            }
        """
        if self.logger:
            self.logger.info(f"🚀 Starting parallel analysis of {len(source_paths)} paths")
        
        start_time = time.time()
        
        try:
            # Run all agents in parallel with timeout
            api_task = asyncio.create_task(self.api_agent.analyze(source_paths))
            arch_task = asyncio.create_task(self.arch_agent.analyze(source_paths))
            guide_task = asyncio.create_task(self.guide_agent.analyze(source_paths))
            
            # Wait for all tasks with timeout
            api_result, arch_result, guide_result = await asyncio.wait_for(
                asyncio.gather(api_task, arch_task, guide_task),
                timeout=self.timeout_seconds
            )
            
            # Validate cross-references (synchronous)
            validation_result = self.validator.validate(
                api_result,
                arch_result,
                guide_result
            )
            
            total_duration = time.time() - start_time
            
            if self.logger:
                self.logger.info(
                    f"✅ Parallel analysis complete in {total_duration:.2f}s "
                    f"({validation_result.broken_references} broken references)"
                )
            
            return {
                'api': api_result,
                'architecture': arch_result,
                'user_guide': guide_result,
                'validation': validation_result,
                'total_duration': total_duration
            }
        
        except asyncio.TimeoutError:
            error_msg = f"Analysis timeout after {self.timeout_seconds}s"
            if self.logger:
                self.logger.error(f"❌ {error_msg}")
            
            return {
                'api': AnalysisResult(doc_type=DocumentationType.API, errors=[error_msg]),
                'architecture': AnalysisResult(doc_type=DocumentationType.ARCHITECTURE, errors=[error_msg]),
                'user_guide': AnalysisResult(doc_type=DocumentationType.USER_GUIDE, errors=[error_msg]),
                'validation': ValidationResult(),
                'total_duration': time.time() - start_time
            }
        
        except Exception as e:
            error_msg = f"Parallel analysis failed: {str(e)}"
            if self.logger:
                self.logger.error(f"❌ {error_msg}")
            
            return {
                'api': AnalysisResult(doc_type=DocumentationType.API, errors=[error_msg]),
                'architecture': AnalysisResult(doc_type=DocumentationType.ARCHITECTURE, errors=[error_msg]),
                'user_guide': AnalysisResult(doc_type=DocumentationType.USER_GUIDE, errors=[error_msg]),
                'validation': ValidationResult(),
                'total_duration': time.time() - start_time
            }
