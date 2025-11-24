"""
Vision API Setup Module

Activates GitHub Copilot Vision API for screenshot analysis in CORTEX.

SOLID Principles:
- Single Responsibility: Only handles Vision API activation
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import json
from pathlib import Path
from typing import Dict, Any, Tuple, List
from datetime import datetime

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationStatus,
    OperationPhase
)


class VisionAPIModule(BaseOperationModule):
    """
    Setup module for activating Vision API.
    
    Responsibilities:
    1. Verify cortex.config.json exists
    2. Enable vision_api.enabled flag
    3. Configure default settings if not present
    4. Verify Pillow/PIL is installed (optional, for preprocessing)
    5. Update context for downstream modules
    
    Configuration (from YAML):
        config_file: Path to cortex.config.json
        config_path: JSON path to enable (e.g., "vision_api.enabled")
        max_tokens_per_image: Token budget per image
        cache_results: Whether to cache analysis results
        requires_copilot: Whether GitHub Copilot is required
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="vision_api",
            name="Vision API Activation",
            description="Enable GitHub Copilot Vision API for screenshot analysis",
            phase=OperationPhase.FEATURES,
            priority=10,
            dependencies=["python_dependencies"],
            optional=True,  # Optional feature
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate prerequisites for Vision API activation.
        
        Checks:
        1. Project root exists in context
        2. cortex.config.json exists
        3. Config file is valid JSON
        """
        issues = []
        
        # Check project root
        project_root = context.get('project_root')
        if not project_root:
            issues.append("Project root not found in context")
            return False, issues
        
        project_root = Path(project_root)
        
        # Check config file
        config_file = project_root / "cortex.config.json"
        if not config_file.exists():
            issues.append(f"Config file not found: {config_file}")
            return False, issues
        
        # Validate JSON
        try:
            with open(config_file, 'r') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            issues.append(f"Invalid JSON in config file: {e}")
            return False, issues
        except Exception as e:
            issues.append(f"Failed to read config file: {e}")
            return False, issues
        
        return True, []
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute Vision API activation.
        
        Steps:
        1. Load cortex.config.json
        2. Enable vision_api.enabled = true
        3. Set default configuration if missing
        4. Save updated config
        5. Update context
        """
        start_time = datetime.now()
        
        try:
            project_root = Path(context['project_root'])
            config_file = project_root / "cortex.config.json"
            
            self.log_info(f"Loading config from: {config_file}")
            
            # Load current config
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Initialize vision_api section if missing
            if 'vision_api' not in config:
                self.log_info("Creating vision_api configuration section")
                config['vision_api'] = {}
            
            vision_config = config['vision_api']
            
            # Check if already enabled
            was_enabled = vision_config.get('enabled', False)
            
            # Enable Vision API
            vision_config['enabled'] = True
            
            # Set default configurations if missing
            defaults = {
                'max_tokens_per_image': 500,
                'max_image_size_bytes': 2_000_000,
                'downscale_threshold': 1920,
                'jpeg_quality': 85,
                'cache_analysis_results': True,
                'cache_ttl_hours': 24,
                'warn_threshold_tokens': 400
            }
            
            config_updated = False
            for key, default_value in defaults.items():
                if key not in vision_config:
                    vision_config[key] = default_value
                    config_updated = True
                    self.log_info(f"Set default: {key} = {default_value}")
            
            # Save updated config
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Update context for downstream modules
            context['vision_api_enabled'] = True
            context['vision_api_config'] = vision_config
            
            # Check for PIL/Pillow (optional but recommended)
            warnings = []
            try:
                import PIL
                self.log_info("✓ Pillow installed (image preprocessing available)")
            except ImportError:
                warnings.append(
                    "Pillow not installed. Image preprocessing disabled. "
                    "Install with: pip install Pillow"
                )
                self.log_warning(warnings[0])
            
            # Build result message
            if was_enabled and not config_updated:
                message = "Vision API already enabled (no changes needed)"
                status = OperationStatus.SUCCESS
            elif was_enabled and config_updated:
                message = "Vision API configuration updated with defaults"
                status = OperationStatus.SUCCESS
            else:
                message = "Vision API enabled successfully"
                status = OperationStatus.SUCCESS
            
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return OperationResult(
                module_id=self.metadata.module_id,
                status=status,
                message=message,
                details={
                    'config_file': str(config_file),
                    'was_enabled': was_enabled,
                    'config_updated': config_updated,
                    'max_tokens': vision_config['max_tokens_per_image'],
                    'cache_enabled': vision_config['cache_analysis_results'],
                    'pillow_available': 'PIL' in locals()
                },
                warnings=warnings,
                duration_ms=duration_ms
            )
            
        except Exception as e:
            self.log_error(f"Failed to enable Vision API: {e}")
            return OperationResult(
                module_id=self.metadata.module_id,
                status=OperationStatus.FAILED,
                message=f"Vision API activation failed: {str(e)}",
                errors=[str(e)],
                duration_ms=(datetime.now() - start_time).total_seconds() * 1000
            )
    
    def rollback(self, context: Dict[str, Any]) -> bool:
        """
        Rollback Vision API activation.
        
        Disables vision_api.enabled in config.
        """
        try:
            project_root = Path(context['project_root'])
            config_file = project_root / "cortex.config.json"
            
            if not config_file.exists():
                return True
            
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            if 'vision_api' in config:
                config['vision_api']['enabled'] = False
                
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                
                self.log_info("Vision API disabled (rollback)")
            
            return True
            
        except Exception as e:
            self.log_error(f"Rollback failed: {e}")
            return False
    
    def should_run(self, context: Dict[str, Any]) -> bool:
        """
        Determine if Vision API setup should run.
        
        Runs if:
        - User explicitly requested full setup
        - User included 'vision' in setup request
        """
        # Check if explicitly requested
        request = context.get('user_request', '').lower()
        if 'vision' in request or 'screenshot' in request:
            return True
        
        # Check setup profile
        profile = context.get('setup_profile', 'standard')
        if profile == 'full':
            return True
        
        # Otherwise, skip by default (optional feature)
        return False

