"""
Knowledge Cache Builder - Auto-rebuild cache from YAML on git pull

Authority: AC-HYBRID-KNOWLEDGE-003
Version: 1.0
Date: 2026-01-26

Entrypoint for automatic cache rebuilds triggered by:
1. Post-merge hook (after git pull)
2. First import of cortex module
3. Manual trigger via CLI

Usage:
    # Auto-triggered by git post-merge hook
    python -m cortex.brain.knowledge.cache_builder rebuild

    # Manual trigger
    from cortex.brain.knowledge.cache_builder import rebuild_knowledge_cache
    rebuild_knowledge_cache()
"""

import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def rebuild_knowledge_cache() -> bool:
    """
    Rebuild knowledge cache from YAML files.

    Returns:
        True if rebuild successful, False otherwise.
    """
    try:
        from cortex.brain.knowledge.hybrid_loader import get_hybrid_loader

        loader = get_hybrid_loader()
        success = loader.rebuild_cache()

        if success:
            logger.info("✅ Knowledge cache rebuilt successfully")
            return True
        else:
            logger.warning("⚠️  Knowledge cache rebuild completed with issues")
            return False

    except Exception as e:
        logger.error(f"❌ Failed to rebuild knowledge cache: {e}")
        return False


def main():
    """CLI entry point for manual cache rebuild."""
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) > 1 and sys.argv[1] == "rebuild":
        success = rebuild_knowledge_cache()
        sys.exit(0 if success else 1)
    else:
        print("Usage: python -m cortex.brain.knowledge.cache_builder rebuild")
        sys.exit(1)


if __name__ == "__main__":
    main()
