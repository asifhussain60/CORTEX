"""
ContextResolver: Tiered context resolution with graceful degradation.

Resolution layers (highest to lowest priority):
1. Explicit parameters
2. GitHub Copilot context
3. Environment variables
4. Config file
5. Path.cwd() fallback
"""

from pathlib import Path
from typing import Optional
import os
import json
import logging

from .workspace_context import WorkspaceContext
from .copilot_integration import CopilotIntegration

logger = logging.getLogger(__name__)


class ContextResolver:
    """
    Resolve workspace context with 5-layer fallback strategy.
    
    Principles:
    - CORTEX-first (works standalone)
    - Copilot-enhanced (better when available)
    - Explicit wins (user parameters highest priority)
    - Graceful degradation (always returns valid context)
    """
    
    def __init__(self):
        self.copilot = CopilotIntegration()
    
    def resolve(
        self,
        repo_root: Optional[Path] = None,
        cortex_root: Optional[Path] = None,
    ) -> WorkspaceContext:
        """
        Resolve workspace context with graceful degradation.
        
        Args:
            repo_root: Explicit target repository root (highest priority)
            cortex_root: Explicit CORTEX root (highest priority)
        
        Returns:
            WorkspaceContext with resolved paths
        """
        metadata = {
            'source': 'unknown',
            'confidence': 0.0,
            'warnings': [],
        }
        
        # Layer 1: Explicit parameters (100% confidence)
        if repo_root and cortex_root:
            metadata['source'] = 'explicit'
            metadata['confidence'] = 1.0
            logger.info("✅ Context from explicit parameters (100% confidence)")
            return WorkspaceContext(
                repo_root=repo_root,
                cortex_root=cortex_root,
                metadata=metadata
            )
        
        # Layer 2: GitHub Copilot context (95% confidence)
        copilot_context = self.copilot.get_context()
        if copilot_context:
            resolved_repo = repo_root or copilot_context.get('repo_root')
            resolved_cortex = cortex_root or copilot_context.get('cortex_root')
            
            if resolved_repo and resolved_cortex:
                metadata['source'] = 'copilot'
                metadata['confidence'] = 0.95
                metadata['copilot_available'] = True
                logger.info("✅ Context from GitHub Copilot (95% confidence)")
                return WorkspaceContext(
                    repo_root=Path(resolved_repo),
                    cortex_root=Path(resolved_cortex),
                    metadata=metadata
                )
        
        # Layer 3: Environment variables (80% confidence)
        env_repo = os.getenv('CORTEX_TARGET_REPO')
        env_cortex = os.getenv('CORTEX_ROOT')
        
        if env_repo or env_cortex:
            resolved_repo = repo_root or (Path(env_repo) if env_repo else None)
            resolved_cortex = cortex_root or (Path(env_cortex) if env_cortex else None)
            
            if resolved_repo and resolved_cortex:
                metadata['source'] = 'environment'
                metadata['confidence'] = 0.80
                metadata['warnings'].append(
                    "Using environment variables. Consider using explicit parameters."
                )
                logger.info("⚠️  Context from environment variables (80% confidence)")
                return WorkspaceContext(
                    repo_root=resolved_repo,
                    cortex_root=resolved_cortex,
                    metadata=metadata
                )
        
        # Layer 4: Config file (70% confidence)
        config_context = self._load_config()
        if config_context:
            resolved_repo = repo_root or config_context.get('repo_root')
            resolved_cortex = cortex_root or config_context.get('cortex_root')
            
            if resolved_repo and resolved_cortex:
                metadata['source'] = 'config'
                metadata['confidence'] = 0.70
                metadata['warnings'].append(
                    "Using config file. Consider using explicit parameters for clarity."
                )
                logger.info("⚠️  Context from config file (70% confidence)")
                return WorkspaceContext(
                    repo_root=Path(resolved_repo),
                    cortex_root=Path(resolved_cortex),
                    metadata=metadata
                )
        
        # Layer 5: Path.cwd() fallback (50% confidence, RISKY)
        cwd = Path.cwd()
        cortex_from_module = Path(__file__).parent.parent.parent  # src/context -> CORTEX
        
        metadata['source'] = 'cwd_fallback'
        metadata['confidence'] = 0.50
        metadata['warnings'].append(
            f"⚠️  FALLBACK: Using Path.cwd()={cwd}. This may be incorrect in workspace environments!"
        )
        metadata['warnings'].append(
            "RECOMMENDATION: Provide explicit repo_root parameter or set CORTEX_TARGET_REPO env var."
        )
        
        logger.warning("❌ Context from Path.cwd() fallback (50% confidence, RISKY)")
        for warning in metadata['warnings']:
            logger.warning(warning)
        
        return WorkspaceContext(
            repo_root=cwd,
            cortex_root=cortex_from_module,
            metadata=metadata
        )
    
    def _load_config(self) -> Optional[dict]:
        """
        Load context from cortex.config.json.
        
        Returns:
            Dict with repo_root and cortex_root, or None if unavailable
        """
        try:
            cortex_root = Path(__file__).parent.parent.parent
            config_path = cortex_root / "cortex.config.json"
            
            if not config_path.exists():
                return None
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            workspace_config = config.get('workspace', {})
            default_repo = workspace_config.get('default_repo')
            
            if not default_repo:
                return None
            
            return {
                'repo_root': Path(default_repo),
                'cortex_root': cortex_root,
            }
        
        except Exception as e:
            logger.debug(f"Failed to load config: {e}")
            return None


# Convenience function for quick resolution
def resolve_context(
    repo_root: Optional[Path] = None,
    cortex_root: Optional[Path] = None,
) -> WorkspaceContext:
    """
    Quick context resolution with graceful degradation.
    
    Args:
        repo_root: Explicit target repository root
        cortex_root: Explicit CORTEX root
    
    Returns:
        WorkspaceContext with resolved paths
    """
    resolver = ContextResolver()
    return resolver.resolve(repo_root=repo_root, cortex_root=cortex_root)
