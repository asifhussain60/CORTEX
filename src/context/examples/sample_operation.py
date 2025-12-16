"""
Sample operation demonstrating WorkspaceContext usage.

Shows how to convert Path.cwd()-based operations to context-aware operations.
"""

from pathlib import Path
from typing import Optional
import logging
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.context.workspace_context import WorkspaceContext
from src.context.context_resolver import resolve_context

logger = logging.getLogger(__name__)


# ============================================================================
# BEFORE: Path.cwd() (Ambiguous in workspace environments)
# ============================================================================

def old_operation():
    """Old way: Uses Path.cwd() - AMBIGUOUS!"""
    repo_root = Path.cwd()  # ❌ Could be CORTEX or user repo!
    
    print(f"Operating on: {repo_root}")
    print(f"  .git exists: {(repo_root / '.git').exists()}")
    print(f"  README.md exists: {(repo_root / 'README.md').exists()}")


# ============================================================================
# AFTER: WorkspaceContext (Explicit with graceful degradation)
# ============================================================================

def new_operation(context: Optional[WorkspaceContext] = None):
    """
    New way: Accepts WorkspaceContext with graceful degradation.
    
    Resolution priority:
    1. Explicit context parameter (100% confidence)
    2. GitHub Copilot context (95% confidence)
    3. Environment variable (80% confidence)
    4. Config file (70% confidence)
    5. Path.cwd() fallback (50% confidence, warns)
    
    Args:
        context: Explicit workspace context (optional, highest priority)
    """
    # Resolve context if not provided
    if context is None:
        context = resolve_context()
    
    # Validate before use
    if not context.validate():
        logger.error("Context validation failed!")
        # Could raise or use safer defaults
    
    # Log context quality
    logger.info(f"Context source: {context.source} ({context.confidence:.0%} confidence)")
    if context.warnings:
        for warning in context.warnings:
            logger.warning(warning)
    
    # Use explicit paths
    repo_root = context.repo_root
    cortex_root = context.cortex_root
    
    print(f"\n🎯 Operating on: {repo_root}")
    print(f"   CORTEX at: {cortex_root}")
    print(f"   Source: {context.source} ({context.confidence:.0%} confidence)")
    print(f"   Is CORTEX repo: {context.is_cortex_repo()}")
    print(f"\n📁 Repository contents:")
    print(f"   .git exists: {(repo_root / '.git').exists()}")
    print(f"   README.md exists: {(repo_root / 'README.md').exists()}")
    print(f"   cortex-brain exists: {(repo_root / 'cortex-brain').exists()}")


# ============================================================================
# Usage Examples
# ============================================================================

def demo_all_layers():
    """Demonstrate all 5 resolution layers."""
    
    print("\n" + "="*60)
    print("Layer 1: Explicit Parameters (100% confidence)")
    print("="*60)
    explicit_context = WorkspaceContext(
        repo_root=Path("D:/PROJECTS/NOOR CANVAS"),
        cortex_root=Path("D:/PROJECTS/CORTEX"),
        metadata={'source': 'explicit', 'confidence': 1.0}
    )
    new_operation(context=explicit_context)
    
    print("\n" + "="*60)
    print("Layer 2: GitHub Copilot Context (95% confidence)")
    print("="*60)
    print("(Would use Copilot API - gracefully degrades to next layer in POC)")
    
    print("\n" + "="*60)
    print("Layer 3: Environment Variables (80% confidence)")
    print("="*60)
    print("Set CORTEX_TARGET_REPO env var to use this layer")
    
    print("\n" + "="*60)
    print("Layer 4: Config File (70% confidence)")
    print("="*60)
    print("Add workspace.default_repo to cortex.config.json to use this layer")
    
    print("\n" + "="*60)
    print("Layer 5: Path.cwd() Fallback (50% confidence, RISKY)")
    print("="*60)
    new_operation()  # No context = uses all fallback layers


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    
    demo_all_layers()
