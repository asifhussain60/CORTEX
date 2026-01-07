"""
CORTEX 6.0 - Routing Module

High-performance intent routing for orchestrator dispatch.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from .trie_router import (
    TrieRouter,
    TrieNode,
    RouteConfig,
    RouteMatch,
    MatchType,
    get_trie_router,
    set_trie_router,
)

__all__ = [
    'TrieRouter',
    'TrieNode',
    'RouteConfig',
    'RouteMatch',
    'MatchType',
    'get_trie_router',
    'set_trie_router',
]
