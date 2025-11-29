"""
Evaluate CORTEX Architecture Module - Story Refresh Operation

This module evaluates the current CORTEX architecture state by loading
CORTEX-UNIFIED-ARCHITECTURE.yaml and extracting feature inventory,
implementation status, and architecture patterns.

Author: Asif Hussain
Version: 1.0
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationPhase,
    OperationStatus
)

logger = logging.getLogger(__name__)


class EvaluateCortexArchitectureModule(BaseOperationModule):
    """
    Evaluate current CORTEX architecture from CORTEX-UNIFIED-ARCHITECTURE.yaml.
    
    This module loads the unified architecture document and extracts:
    - Feature inventory (all components, agents, operations, plugins)
    - Implementation status (completion %, tests passing, metrics)
    - Architecture patterns (SOLID, plugin system, etc.)
    - Changes since last refresh (if timestamp provided)
    
    What it does:
        1. Loads CORTEX-UNIFIED-ARCHITECTURE.yaml
        2. Extracts core components (tiers, agents, operations, plugins)
        3. Extracts implementation status (progress, tests, metrics)
        4. Extracts architecture patterns
        5. Compares with last refresh timestamp (optional)
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="evaluate_cortex_architecture",
            name="Evaluate CORTEX Architecture",
            description="Extract current architecture state from CORTEX-UNIFIED-ARCHITECTURE.yaml",
            phase=OperationPhase.PREPARATION,
            priority=100,
            dependencies=[],
            optional=False,
            version="1.0",
            tags=["story", "architecture", "evaluation"]
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate prerequisites."""
        issues = []
        
        if 'project_root' not in context:
            issues.append("project_root not set in context")
            return False, issues
        
        project_root = Path(context['project_root'])
        
        # Check CORTEX-UNIFIED-ARCHITECTURE.yaml exists
        arch_file = project_root / "cortex-brain" / "CORTEX-UNIFIED-ARCHITECTURE.yaml"
        if not arch_file.exists():
            issues.append(f"Architecture file not found: {arch_file}")
        
        return len(issues) == 0, issues
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Evaluate CORTEX architecture with mode detection.
        
        Args:
            context: Shared context dictionary
                - Input: project_root (Path), last_refresh_timestamp (optional datetime)
                  refresh_mode (optional: 'auto' | 'generate-from-scratch' | 'update-in-place')
                  change_magnitude_threshold (optional: float, default 0.20)
                - Output: feature_inventory, implementation_status, architecture_patterns, 
                  changes_since_last_refresh, recommended_mode, change_magnitude, mode_rationale
        
        Returns:
            OperationResult with architecture evaluation and mode recommendation
        """
        try:
            project_root = Path(context['project_root'])
            arch_file = project_root / "cortex-brain" / "CORTEX-UNIFIED-ARCHITECTURE.yaml"
            last_refresh = context.get('last_refresh_timestamp')
            refresh_mode = context.get('refresh_mode', 'generate-from-scratch')  # DEFAULT to generate-from-scratch
            threshold = context.get('change_magnitude_threshold', 0.20)
            
            logger.info(f"Loading architecture from: {arch_file}")
            
            # Load YAML
            with open(arch_file, 'r', encoding='utf-8') as f:
                architecture = yaml.safe_load(f)
            
            logger.info("Architecture loaded successfully")
            
            # Extract feature inventory
            feature_inventory = self._extract_feature_inventory(architecture)
            logger.info(f"Extracted {len(feature_inventory['features'])} features")
            
            # Extract implementation status
            implementation_status = self._extract_implementation_status(architecture)
            logger.info(f"Implementation: {implementation_status['overall_progress']}")
            
            # Extract architecture patterns
            architecture_patterns = self._extract_architecture_patterns(architecture)
            logger.info(f"Extracted {len(architecture_patterns)} architecture patterns")
            
            # Detect changes since last refresh (if provided)
            changes = []
            if last_refresh:
                changes = self._detect_changes_since(architecture, last_refresh)
                logger.info(f"Detected {len(changes)} changes since last refresh")
            
            # Calculate change magnitude and recommend mode
            change_magnitude = self._calculate_change_magnitude(changes, feature_inventory)
            recommended_mode, rationale = self._determine_refresh_mode(
                refresh_mode,
                change_magnitude,
                threshold,
                feature_inventory,
                changes
            )
            
            logger.info(f"Change magnitude: {change_magnitude:.1%}")
            logger.info(f"Recommended mode: {recommended_mode}")
            logger.info(f"Rationale: {rationale}")
            
            # Store in context
            context['feature_inventory'] = feature_inventory
            context['implementation_status'] = implementation_status
            context['architecture_patterns'] = architecture_patterns
            context['changes_since_last_refresh'] = changes
            context['architecture_data'] = architecture
            context['recommended_mode'] = recommended_mode
            context['change_magnitude'] = change_magnitude
            context['mode_rationale'] = rationale
            
            return OperationResult(
                success=True,
                status=OperationStatus.COMPLETED,
                message=f"Architecture evaluated: {len(feature_inventory['features'])} features, mode: {recommended_mode}",
                data={
                    "feature_inventory": feature_inventory,
                    "implementation_status": implementation_status,
                    "architecture_patterns": architecture_patterns,
                    "changes_count": len(changes),
                    "changes": changes,
                    "recommended_mode": recommended_mode,
                    "change_magnitude": change_magnitude,
                    "mode_rationale": rationale
                }
            )
            
        except FileNotFoundError as e:
            logger.error(f"Architecture file not found: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Architecture file not found: {e}"
            )
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"YAML parsing error: {e}"
            )
        except Exception as e:
            logger.error(f"Failed to evaluate architecture: {e}", exc_info=True)
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Architecture evaluation failed: {e}"
            )
    
    def rollback(self, context: Dict[str, Any]) -> OperationResult:
        """Rollback architecture evaluation (no-op)."""
        logger.debug("Rollback called for architecture evaluation (no-op)")
        return OperationResult(
            success=True,
            status=OperationStatus.COMPLETED,
            message="Rollback complete (no-op for evaluation)"
        )
    
    def _extract_feature_inventory(self, architecture: Dict[str, Any]) -> Dict[str, Any]:
        """Extract comprehensive feature inventory from architecture."""
        features = []
        
        # Extract brain architecture features (Tier 0-3)
        core_components = architecture.get('core_components', {})
        brain_arch = core_components.get('brain_architecture', {})
        
        # Tier 0 - Instinct
        tier0 = brain_arch.get('tier0_instinct', {})
        if tier0:
            features.append({
                "name": "Tier 0 - Instinct Layer",
                "category": "brain_architecture",
                "description": tier0.get('purpose', ''),
                "status": tier0.get('implementation_status', {}).get('status', 'unknown'),
                "details": {
                    "location": tier0.get('location', ''),
                    "characteristics": tier0.get('characteristics', []),
                    "skull_rules": len(tier0.get('skull_protection_rules', {}))
                }
            })
        
        # Tier 1 - Working Memory
        tier1 = brain_arch.get('tier1_working_memory', {})
        if tier1:
            features.append({
                "name": "Tier 1 - Working Memory",
                "category": "brain_architecture",
                "description": tier1.get('purpose', ''),
                "status": tier1.get('implementation_status', {}).get('status', 'unknown'),
                "details": {
                    "location": tier1.get('location', ''),
                    "capacity": tier1.get('characteristics', {}).get('capacity', ''),
                    "tests_passing": tier1.get('implementation_status', {}).get('tests_passing', 0)
                }
            })
        
        # Tier 2 - Knowledge Graph
        tier2 = brain_arch.get('tier2_knowledge_graph', {})
        if tier2:
            features.append({
                "name": "Tier 2 - Knowledge Graph",
                "category": "brain_architecture",
                "description": tier2.get('purpose', ''),
                "status": tier2.get('implementation_status', {}).get('status', 'unknown'),
                "details": {
                    "location": tier2.get('location', ''),
                    "knowledge_types": list(tier2.get('knowledge_types', {}).keys()),
                    "tests_passing": tier2.get('implementation_status', {}).get('tests_passing', 0)
                }
            })
        
        # Tier 3 - Context Intelligence
        tier3 = brain_arch.get('tier3_context_intelligence', {})
        if tier3:
            features.append({
                "name": "Tier 3 - Context Intelligence",
                "category": "brain_architecture",
                "description": tier3.get('purpose', ''),
                "status": tier3.get('implementation_status', {}).get('status', 'unknown'),
                "details": {
                    "location": tier3.get('location', ''),
                    "context_sources": list(tier3.get('context_sources', {}).keys()),
                    "tests_passing": tier3.get('implementation_status', {}).get('tests_passing', 0)
                }
            })
        
        # Extract agent system features
        agent_system = core_components.get('agent_system', {})
        
        # Left brain agents
        left_brain = agent_system.get('left_brain_tactical', {})
        for agent_id, agent_data in left_brain.get('agents', {}).items():
            features.append({
                "name": agent_data.get('name', agent_id),
                "category": "agent_left_brain",
                "description": agent_data.get('responsibility', ''),
                "status": "complete",
                "details": {
                    "triggers": agent_data.get('triggers', []),
                    "capabilities": list(agent_data.get('capabilities', {}).keys()),
                    "location": agent_data.get('location', '')
                }
            })
        
        # Right brain agents
        right_brain = agent_system.get('right_brain_strategic', {})
        for agent_id, agent_data in right_brain.get('agents', {}).items():
            features.append({
                "name": agent_data.get('name', agent_id),
                "category": "agent_right_brain",
                "description": agent_data.get('responsibility', ''),
                "status": "complete",
                "details": {
                    "triggers": agent_data.get('triggers', []),
                    "capabilities": list(agent_data.get('capabilities', {}).keys()),
                    "location": agent_data.get('location', '')
                }
            })
        
        # Extract operations system features
        operations = core_components.get('operations_system', {})
        ops_v2 = operations.get('operations_v2_0', {})
        for op_id, op_data in ops_v2.items():
            if isinstance(op_data, dict):
                features.append({
                    "name": op_id.replace('_', ' ').title(),
                    "category": "operation",
                    "description": op_data.get('description', ''),
                    "status": op_data.get('status', 'unknown'),
                    "details": {
                        "natural_language": op_data.get('natural_language', ''),
                        "modules_implemented": op_data.get('modules_implemented', []),
                        "modules_pending": op_data.get('modules_pending', [])
                    }
                })
        
        # Extract plugin system features
        plugin_system = core_components.get('plugin_system', {})
        implemented_plugins = plugin_system.get('implemented_plugins', {})
        for plugin_id, plugin_data in implemented_plugins.items():
            features.append({
                "name": plugin_data.get('name', plugin_id),
                "category": "plugin",
                "description": plugin_data.get('description', ''),
                "status": plugin_data.get('status', 'unknown'),
                "details": {
                    "location": plugin_data.get('location', ''),
                    "tests": plugin_data.get('tests', 0),
                    "commands": plugin_data.get('commands', [])
                }
            })
        
        return {
            "features": features,
            "count": len(features),
            "categories": self._categorize_features(features)
        }
    
    def _extract_implementation_status(self, architecture: Dict[str, Any]) -> Dict[str, Any]:
        """Extract implementation status metrics."""
        impl_status = architecture.get('implementation_status', {})
        overview = impl_status.get('overview', {})
        
        return {
            "overall_progress": overview.get('overall_progress', 'unknown'),
            "phase_completed": overview.get('phase_completed', 0),
            "phases_remaining": overview.get('phases_remaining', 0),
            "velocity": overview.get('velocity', 'unknown'),
            "test_metrics": impl_status.get('test_metrics', {}),
            "quality_metrics": impl_status.get('quality_metrics', {}),
            "performance_metrics": impl_status.get('performance_metrics', {}),
            "phase_breakdown": impl_status.get('phase_breakdown', {})
        }
    
    def _extract_architecture_patterns(self, architecture: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract architecture patterns."""
        patterns_data = architecture.get('architecture_patterns', {})
        patterns = []
        
        # Design principles
        for principle in patterns_data.get('design_principles', []):
            patterns.append({
                "type": "design_principle",
                "name": principle.get('name', ''),
                "description": principle.get('description', ''),
                "application": principle.get('application', '')
            })
        
        # Structural patterns
        structural = patterns_data.get('structural_patterns', {})
        for pattern_id, pattern_data in structural.items():
            patterns.append({
                "type": "structural_pattern",
                "name": pattern_id.replace('_', ' ').title(),
                "pattern": pattern_data.get('pattern', ''),
                "rationale": pattern_data.get('rationale', ''),
                "benefits": pattern_data.get('benefits', [])
            })
        
        # Integration patterns
        integration = patterns_data.get('integration_patterns', {})
        for pattern_id, pattern_data in integration.items():
            patterns.append({
                "type": "integration_pattern",
                "name": pattern_id.replace('_', ' ').title(),
                "pattern": pattern_data.get('pattern', ''),
                "rationale": pattern_data.get('rationale', ''),
                "implementation": pattern_data.get('implementation', '')
            })
        
        return patterns
    
    def _detect_changes_since(self, architecture: Dict[str, Any], last_refresh: datetime) -> List[Dict[str, Any]]:
        """Detect changes since last refresh timestamp."""
        changes = []
        
        # Check metadata last_updated
        metadata = architecture.get('metadata', {})
        last_updated_str = metadata.get('last_updated', '')
        
        if last_updated_str:
            try:
                last_updated = datetime.fromisoformat(last_updated_str)
                if last_updated > last_refresh:
                    changes.append({
                        "type": "architecture_update",
                        "timestamp": last_updated_str,
                        "description": "Architecture document updated"
                    })
            except ValueError:
                logger.warning(f"Invalid timestamp format: {last_updated_str}")
        
        # Check implementation status changes
        impl_status = architecture.get('implementation_status', {})
        overview = impl_status.get('overview', {})
        
        changes.append({
            "type": "implementation_progress",
            "current_progress": overview.get('overall_progress', 'unknown'),
            "phase_completed": overview.get('phase_completed', 0),
            "description": f"Current implementation: {overview.get('overall_progress', 'unknown')}"
        })
        
        return changes
    
    def _categorize_features(self, features: List[Dict[str, Any]]) -> Dict[str, int]:
        """Categorize features by type."""
        categories = {}
        for feature in features:
            category = feature.get('category', 'unknown')
            categories[category] = categories.get(category, 0) + 1
        return categories
    
    def _calculate_change_magnitude(self, changes: List[Dict[str, Any]], feature_inventory: Dict[str, Any]) -> float:
        """
        Calculate change magnitude as percentage of system affected.
        
        Weights:
        - New tier: 30% impact
        - New agent: 10% impact per agent
        - New plugin: 5% impact per plugin
        - New operation: 5% impact per operation
        - Test progress: 1% impact per 100 tests
        - Module progress: Captured in implementation_progress
        """
        magnitude = 0.0
        
        for change in changes:
            change_type = change.get('type', '')
            
            if change_type == 'new_tier':
                magnitude += 0.30
            elif change_type == 'new_agent':
                magnitude += 0.10
            elif change_type == 'new_plugin':
                magnitude += 0.05
            elif change_type == 'new_operation':
                magnitude += 0.05
            elif change_type == 'test_progress':
                test_count = change.get('test_count', 0)
                magnitude += (test_count / 100) * 0.01
            elif change_type == 'implementation_progress':
                # Already factored into overall progress
                pass
        
        # Cap at 100%
        return min(magnitude, 1.0)
    
    def _determine_refresh_mode(
        self,
        requested_mode: str,
        change_magnitude: float,
        threshold: float,
        feature_inventory: Dict[str, Any],
        changes: List[Dict[str, Any]]
    ) -> tuple[str, str]:
        """
        Determine refresh mode based on requested mode, change magnitude, and changes.
        
        Returns: (mode, rationale)
        """
        # If user explicitly specified mode (not 'auto'), use it
        if requested_mode in ('generate-from-scratch', 'update-in-place'):
            if requested_mode == 'generate-from-scratch':
                rationale = "User requested full regeneration (default mode)"
            else:
                rationale = "User requested incremental update"
            return requested_mode, rationale
        
        # Auto-detect mode based on change magnitude
        if change_magnitude >= threshold:
            rationale = f"Major changes detected ({change_magnitude:.1%} >= {threshold:.1%} threshold)"
            if any(c.get('type') == 'new_tier' for c in changes):
                rationale += " - New brain tier added"
            elif sum(1 for c in changes if c.get('type') == 'new_agent') >= 3:
                rationale += " - Multiple new agents added"
            return 'generate-from-scratch', rationale
        else:
            rationale = f"Minor changes detected ({change_magnitude:.1%} < {threshold:.1%} threshold)"
            if any(c.get('type') == 'test_progress' for c in changes):
                rationale += " - Implementation progress only"
            return 'update-in-place', rationale


def register() -> BaseOperationModule:
    """Register module with operation system."""
    return EvaluateCortexArchitectureModule()
