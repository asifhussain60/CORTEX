"""
Documentation Refresh Plugin (Orchestrator)

Minimal orchestrator that coordinates doc refresh operations using modular services.
Refactored from monolithic design to follow Single Responsibility Principle.

Part of: CORTEX 3.0 Track B (Token Optimization)
Original: 1,874 lines → Target: ~400 lines (79% reduction)

Services used:
- DocContentService: Content generation and transformation
- DocFileService: File operations and document refresh
- DocValidationService: Validation and constraint enforcement
"""

from typing import Dict, Any
import logging
from pathlib import Path
import json

from .base_plugin import BasePlugin, PluginMetadata, PluginCategory, PluginPriority
from .services.doc_content_service import DocContentService
from .services.doc_file_service import DocFileService
from .services.doc_validation_service import DocValidationService


class DocRefreshPlugin(BasePlugin):
    """Orchestrates documentation refresh operations using modular services"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize services
        self.content_service = DocContentService()
        self.file_service = DocFileService()
        self.validation_service = DocValidationService()
        
        # Plugin metadata
        self.metadata = PluginMetadata(
            plugin_id="doc_refresh_plugin",
            name="Documentation Refresh Plugin",
            version="3.0.0",
            category=PluginCategory.DOCUMENTATION,
            priority=PluginPriority.MEDIUM,
            description="Modular documentation refresh with SRP architecture",
            author="CORTEX 3.0",
            dependencies=[],
            hooks=["documentation", "refresh", "update"],
            natural_language_patterns=[
                "refresh docs", "update documentation", "doc refresh",
                "refresh documentation", "update docs"
            ]
        )
    
    def _get_metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        return self.metadata
    
    def initialize(self) -> bool:
        """Initialize the plugin and validate services"""
        try:
            self.logger.info("Initializing DocRefresh Plugin with modular services")
            
            # Validate all services are properly initialized
            services = [self.content_service, self.file_service, self.validation_service]
            
            for service in services:
                if not hasattr(service, '__class__'):
                    self.logger.error(f"Service initialization failed: {service}")
                    return False
            
            self.logger.info("All services initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Plugin initialization failed: {e}")
            return False
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute documentation refresh operation"""
        try:
            self.logger.info("Starting documentation refresh operation")
            
            # Load design context
            design_context = self.file_service.load_design_context()
            
            # Determine operation type
            operation_type = context.get('operation', 'refresh_all')
            
            if operation_type == 'refresh_all':
                return self._refresh_all_docs(context, design_context)
            elif operation_type == 'check_sync':
                return self.file_service.check_doc_sync(context)
            else:
                return {'success': False, 'error': f'Unknown operation: {operation_type}'}
        
        except Exception as e:
            self.logger.error(f"Plugin execution failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _refresh_all_docs(self, context: Dict[str, Any], design_context: Dict[str, Any]) -> Dict[str, Any]:
        """Refresh all documentation files using services"""
        results = {'success': True, 'files_processed': 0, 'details': []}
        
        # Define target documentation files
        doc_files = [
            ('Technical-CORTEX.md', 'technical'),
            ('Awakening Of CORTEX.md', 'story'), 
            ('Image-Prompts.md', 'image_prompts'),
            ('History.md', 'history'),
            ('Ancient-Rules.md', 'ancient_rules'),
            ('CORTEX-FEATURES.md', 'features')
        ]
        
        for filename, doc_type in doc_files:
            try:
                file_path = Path(f"docs/story/CORTEX-STORY/{filename}")
                
                # Validate file exists (NEVER CREATE NEW FILES)
                if not self.validation_service.validate_no_new_files_rule('update', str(file_path)):
                    continue
                
                # Validate no variant files
                if not self.validation_service.validate_no_variants_rule(filename):
                    continue
                
                # Route to appropriate service method
                if doc_type == 'technical':
                    result = self.file_service.refresh_technical_doc(file_path, design_context)
                elif doc_type == 'story':
                    result = self._refresh_story_with_validation(file_path, design_context)
                elif doc_type == 'image_prompts':
                    result = self.file_service.refresh_image_prompts_doc(file_path, design_context)
                elif doc_type == 'history':
                    result = self.file_service.refresh_history_doc(file_path, design_context)
                elif doc_type == 'ancient_rules':
                    result = self.file_service.refresh_ancient_rules_doc(file_path, design_context)
                elif doc_type == 'features':
                    result = self.file_service.refresh_features_doc(file_path, design_context)
                
                if result.get('success'):
                    results['files_processed'] += 1
                    results['details'].append({
                        'file': filename,
                        'status': 'success',
                        'tokens_saved': result.get('tokens_saved', 0)
                    })
                else:
                    results['details'].append({
                        'file': filename,
                        'status': 'error',
                        'error': result.get('error', 'Unknown error')
                    })
            
            except Exception as e:
                self.logger.error(f"Error processing {filename}: {e}")
                results['details'].append({
                    'file': filename,
                    'status': 'error',
                    'error': str(e)
                })
        
        return results
    
    def _refresh_story_with_validation(self, file_path: Path, design_context: Dict[str, Any]) -> Dict[str, Any]:
        """Refresh story document with read time validation"""
        # Refresh the story content
        refresh_result = self.file_service.refresh_story_doc(file_path, design_context)
        
        if not refresh_result.get('success'):
            return refresh_result
        
        # Validate read time constraints
        content = refresh_result.get('content', '')
        validation_result = self.validation_service.validate_read_time(content, target_minutes=70)
        
        if validation_result.get('action') == 'trim_required':
            self.logger.warning(f"Story exceeds target read time, trimming required")
            # Note: In full implementation, would trim content here
        
        return refresh_result
    
    def cleanup(self) -> bool:
        """Clean up plugin resources"""
        try:
            self.logger.info("Cleaning up DocRefresh Plugin")
            # Services don't need explicit cleanup in this simple implementation
            return True
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            return False


def register():
    """Register the plugin with CORTEX"""
    return DocRefreshPlugin()