"""
Phase 66-A RED tests — GAP-66-005: KnowledgeIndexerDocGenBridge.

TDD-66-A-005: KnowledgeIndexerDocGenBridge.sync() must bridge KnowledgeIndexer
to DocGen pipeline, returning a list of YAML paths synced.

Author: Asif Hussain
Phase: 66-A
Sweep: SWEEP-66-INTELLIGENCE-MATRIX
"""

import pytest
from pathlib import Path
from typing import List
from unittest.mock import MagicMock, patch

# AC_START: AC-66-A-005-KNOWLEDGE-INDEXER-DOCGEN-BRIDGE-20260224T000000Z


class TestKnowledgeIndexerDocGenBridgeExists:
    """GAP-66-005: KnowledgeIndexerDocGenBridge must exist with sync() method."""

    def test_bridge_module_importable(self) -> None:
        """cortex.intelligence.tier3.knowledge.knowledge_indexer_docgen_bridge must import."""
        from cortex.intelligence.tier3.knowledge.knowledge_indexer_docgen_bridge import (
            KnowledgeIndexerDocGenBridge,
        )  # noqa: F401

    def test_bridge_class_has_sync_method(self) -> None:
        """KnowledgeIndexerDocGenBridge must have sync() method."""
        from cortex.intelligence.tier3.knowledge.knowledge_indexer_docgen_bridge import (
            KnowledgeIndexerDocGenBridge,
        )
        assert hasattr(KnowledgeIndexerDocGenBridge, "sync"), (
            "KnowledgeIndexerDocGenBridge must have sync() method (GAP-66-005)"
        )

    def test_sync_returns_list_of_strings(self) -> None:
        """sync() must return List[str] of YAML paths synced."""
        from cortex.intelligence.tier3.knowledge.knowledge_indexer_docgen_bridge import (
            KnowledgeIndexerDocGenBridge,
        )

        bridge = KnowledgeIndexerDocGenBridge()
        result = bridge.sync()

        assert isinstance(result, list), (
            f"sync() must return list, got {type(result)}"
        )
        assert len(result) >= 1, (
            "sync() must return at least 1 YAML path (GAP-66-005 acceptance criterion)"
        )
        for item in result:
            assert isinstance(item, str), (
                f"sync() items must be strings (YAML paths), got {type(item)}"
            )

    def test_sync_calls_indexer_index_entry(self) -> None:
        """sync() must call KnowledgeIndexer.index_entry() for each docgen artifact."""
        from cortex.intelligence.tier3.knowledge.knowledge_indexer_docgen_bridge import (
            KnowledgeIndexerDocGenBridge,
        )
        from cortex.intelligence.tier3.knowledge.knowledge_indexer import KnowledgeIndexer

        mock_indexer = MagicMock(spec=KnowledgeIndexer)
        bridge = KnowledgeIndexerDocGenBridge(indexer=mock_indexer)
        bridge.sync()

        assert mock_indexer.index_entry.called, (
            "sync() must call indexer.index_entry() to register docgen artifacts (GAP-66-005)"
        )

    def test_bridge_has_type_hints(self) -> None:
        """sync() must have proper type annotations (CORE-011)."""
        from cortex.intelligence.tier3.knowledge.knowledge_indexer_docgen_bridge import (
            KnowledgeIndexerDocGenBridge,
        )
        import inspect

        sig = inspect.signature(KnowledgeIndexerDocGenBridge.sync)
        assert sig.return_annotation is not inspect.Parameter.empty, (
            "sync() must have return type annotation (CORE-011)"
        )


class TestKnowledgeIndexerHasInventory:
    """GAP-66-005: KnowledgeIndexer must gain inventory() method."""

    def test_knowledge_indexer_has_inventory_method(self) -> None:
        """KnowledgeIndexer must have an inventory() method returning list."""
        from cortex.intelligence.tier3.knowledge.knowledge_indexer import KnowledgeIndexer

        assert hasattr(KnowledgeIndexer, "inventory"), (
            "KnowledgeIndexer must have inventory() method (GAP-66-005 dependency). "
            "Add it to cortex/intelligence/tier3/knowledge/knowledge_indexer.py."
        )

    def test_inventory_returns_list(self) -> None:
        """KnowledgeIndexer.inventory() must return List[str]."""
        from cortex.intelligence.tier3.knowledge.knowledge_indexer import KnowledgeIndexer

        indexer = KnowledgeIndexer()
        result = indexer.inventory()
        assert isinstance(result, list), (
            f"inventory() must return list, got {type(result)}"
        )


# AC_COMPLETE: AC-66-A-005-KNOWLEDGE-INDEXER-DOCGEN-BRIDGE-20260224T000000Z ✅
