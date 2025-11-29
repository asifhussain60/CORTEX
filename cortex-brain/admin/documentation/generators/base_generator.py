"""
Base Documentation Generator

Extensible base class for all CORTEX documentation generation components.
Provides common infrastructure for diagrams, MkDocs, feature lists, and future components.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import logging
import json
import yaml
from datetime import datetime


logger = logging.getLogger(__name__)


class GeneratorType(Enum):
    """Documentation component types"""
    DIAGRAMS = "diagrams"
    MKDOCS = "mkdocs"
    FEATURE_LIST = "feature-list"
    EXECUTIVE_SUMMARY = "executive-summary"
    PUBLISH = "publish"
    API_REFERENCE = "api-reference"
    ARCHITECTURE = "architecture"
    GUIDES = "guides"
    ALL = "all"


class GenerationProfile(Enum):
    """Generation depth profiles"""
    MINIMAL = "minimal"        # Core essentials only
    STANDARD = "standard"      # Standard documentation
    COMPREHENSIVE = "comprehensive"  # Full documentation
    CUSTOM = "custom"          # Custom selection


@dataclass
class GenerationConfig:
    """Configuration for documentation generation"""
    generator_type: GeneratorType
    profile: GenerationProfile
    output_path: Path
    force_regenerate: bool = False
    include_timestamps: bool = True
    validate_output: bool = True
    custom_components: Optional[Set[str]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class GenerationResult:
    """Result of documentation generation"""
    success: bool
    generator_type: GeneratorType
    files_generated: List[Path]
    files_updated: List[Path]
    errors: List[str]
    warnings: List[str]
    duration_seconds: float
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting"""
        return {
            "success": self.success,
            "generator_type": self.generator_type.value,
            "files_generated": [str(p) for p in self.files_generated],
            "files_updated": [str(p) for p in self.files_updated],
            "errors": self.errors,
            "warnings": self.warnings,
            "duration_seconds": self.duration_seconds,
            "metadata": self.metadata or {}
        }


class BaseDocumentationGenerator(ABC):
    """
    Abstract base class for all documentation generators.
    
    All component generators (Diagrams, MkDocs, Feature List, etc.) 
    must inherit from this class and implement required methods.
    """
    
    def __init__(self, config: GenerationConfig, workspace_root: Optional[Path] = None):
        """
        Initialize generator.
        
        Args:
            config: Generation configuration
            workspace_root: Root path of CORTEX workspace
        """
        self.config = config
        self.workspace_root = workspace_root or self._detect_workspace_root()
        self.admin_path = self.workspace_root / "cortex-brain" / "admin" / "documentation"
        self.config_path = self.admin_path / "config"
        self.output_path = config.output_path
        
        # Ensure admin structure exists
        self.admin_path.mkdir(parents=True, exist_ok=True)
        self.config_path.mkdir(parents=True, exist_ok=True)
        
        # Statistics
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.files_generated: List[Path] = []
        self.files_updated: List[Path] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def _detect_workspace_root(self) -> Path:
        """Detect CORTEX workspace root from current file location"""
        current = Path(__file__).resolve()
        while current.parent != current:
            if (current / "cortex-brain").exists():
                return current
            current = current.parent
        raise RuntimeError("Could not detect CORTEX workspace root")
    
    @abstractmethod
    def generate(self) -> GenerationResult:
        """
        Generate documentation for this component.
        
        Must be implemented by each concrete generator.
        
        Returns:
            GenerationResult with files created, errors, warnings
        """
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """
        Validate generated documentation.
        
        Must be implemented by each concrete generator.
        
        Returns:
            True if validation passes, False otherwise
        """
        pass
    
    @abstractmethod
    def get_component_name(self) -> str:
        """
        Get human-readable component name.
        
        Returns:
            Component name (e.g., "Mermaid Diagrams", "MkDocs Site")
        """
        pass
    
    def collect_data(self) -> Dict[str, Any]:
        """
        Collect data needed for documentation generation.
        
        Override in subclasses to provide component-specific data.
        
        Returns:
            Dictionary of collected data
        """
        return {}
    
    def pre_generation_checks(self) -> bool:
        """
        Run pre-generation validation checks.
        
        Override in subclasses for component-specific checks.
        
        Returns:
            True if checks pass, False otherwise
        """
        # Ensure output path exists
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Check write permissions
        if not self.output_path.exists() or not self.output_path.is_dir():
            self.errors.append(f"Output path not accessible: {self.output_path}")
            return False
        
        return True
    
    def post_generation_cleanup(self):
        """
        Cleanup after generation completes.
        
        Override in subclasses for component-specific cleanup.
        """
        pass
    
    def record_file_generated(self, file_path: Path):
        """Record that a file was generated"""
        self.files_generated.append(file_path)
        logger.info(f"Generated: {file_path}")
    
    def record_file_updated(self, file_path: Path):
        """Record that a file was updated"""
        self.files_updated.append(file_path)
        logger.info(f"Updated: {file_path}")
    
    def record_error(self, error: str):
        """Record an error"""
        self.errors.append(error)
        logger.error(error)
    
    def record_warning(self, warning: str):
        """Record a warning"""
        self.warnings.append(warning)
        logger.warning(warning)
    
    def execute(self) -> GenerationResult:
        """
        Execute complete generation workflow.
        
        This is the main entry point that orchestrates the generation process.
        
        Returns:
            GenerationResult with complete generation status
        """
        logger.info(f"Starting {self.get_component_name()} generation")
        self.start_time = datetime.now()
        
        try:
            # Pre-generation checks
            if not self.pre_generation_checks():
                return self._create_failed_result("Pre-generation checks failed")
            
            # Collect data
            logger.info("Collecting data...")
            data = self.collect_data()
            
            # Generate documentation
            logger.info("Generating documentation...")
            result = self.generate()
            
            # Validate if configured
            if self.config.validate_output:
                logger.info("Validating documentation...")
                if not self.validate():
                    self.record_warning("Validation failed but generation completed")
            
            # Post-generation cleanup
            self.post_generation_cleanup()
            
            self.end_time = datetime.now()
            
            # Add timing to result
            if result:
                result.duration_seconds = (self.end_time - self.start_time).total_seconds()
            
            logger.info(f"Completed {self.get_component_name()} generation in {result.duration_seconds:.2f}s")
            return result
            
        except Exception as e:
            logger.exception(f"Error during {self.get_component_name()} generation")
            self.record_error(str(e))
            return self._create_failed_result(f"Generation failed: {e}")
    
    def _create_failed_result(self, error: str) -> GenerationResult:
        """Create a failed GenerationResult"""
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds() if self.start_time else 0.0
        
        return GenerationResult(
            success=False,
            generator_type=self.config.generator_type,
            files_generated=self.files_generated,
            files_updated=self.files_updated,
            errors=self.errors + [error],
            warnings=self.warnings,
            duration_seconds=duration
        )
    
    def _create_success_result(self, metadata: Optional[Dict[str, Any]] = None) -> GenerationResult:
        """Create a successful GenerationResult"""
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds() if self.start_time else 0.0
        
        return GenerationResult(
            success=True,
            generator_type=self.config.generator_type,
            files_generated=self.files_generated,
            files_updated=self.files_updated,
            errors=self.errors,
            warnings=self.warnings,
            duration_seconds=duration,
            metadata=metadata
        )
    
    def load_config_file(self, config_name: str) -> Optional[Dict[str, Any]]:
        """
        Load a YAML config file, preferring admin/documentation/config/ with fallbacks.

        Search order:
        1) cortex-brain/admin/documentation/config/{config_name}
        2) workspace root: {config_name}
        3) cortex-brain/{config_name}
        
        Args:
            config_name: Config file name (e.g., "diagrams-config.yaml")
        
        Returns:
            Parsed config dictionary or None if not found
        """
        candidates = [
            self.config_path / config_name,
            self.workspace_root / config_name,
            self.workspace_root / "cortex-brain" / config_name,
        ]

        for config_file in candidates:
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        return yaml.safe_load(f)
                except Exception as e:
                    self.record_error(f"Failed to load config {config_name} from {config_file}: {e}")
                    return None

        self.record_warning(f"Config file not found in known locations: {config_name}")
        return None
    
    def save_metadata(self, filename: str, metadata: Dict[str, Any]):
        """
        Save generation metadata to admin folder.
        
        Args:
            filename: Metadata filename (e.g., "diagrams-metadata.json")
            metadata: Metadata dictionary
        """
        metadata_file = self.admin_path / filename
        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, default=str)
            logger.info(f"Saved metadata: {metadata_file}")
        except Exception as e:
            self.record_error(f"Failed to save metadata {filename}: {e}")
