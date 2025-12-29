# CORTEX 3.0 - Feature 1: IDEA Capture System
# 
# Purpose: Ultra-fast capture of fleeting ideas during active work
# Architecture: <5ms capture + async enrichment + natural language interface + smart organization + context linking
# Author: Asif Hussain
# Copyright: © 2024-2025 Asif Hussain. All rights reserved.

from .idea_queue import IdeaQueue, IdeaCapture, create_idea_queue
from .natural_language_interface import (
    IdeaNaturalLanguageInterface,
    IdeaCommand,
    create_idea_interface
)
from .idea_organizer import (
    IdeaCategory,
    IdeaTag,
    IdeaCluster,
    CategoryManager,
    TagSystem,
    PriorityEngine,
    ClusteringEngine,
    IdeaOrganizer,
    create_idea_organizer
)
from .context_linker import (
    IdeaContextLinker,
    ContextLink,
    ConversationContextAnalyzer,
    KnowledgeGraphLinker,
    OperationLinker,
    create_context_linker
)

__all__ = [
    # Core data models
    'IdeaCapture',
    'IdeaCommand',
    'IdeaCategory', 
    'IdeaTag',
    'IdeaCluster',
    'ContextLink',
    
    # Main components
    'IdeaQueue',
    'IdeaNaturalLanguageInterface',
    'IdeaOrganizer',
    'IdeaContextLinker',
    
    # Organization components
    'CategoryManager',
    'TagSystem', 
    'PriorityEngine',
    'ClusteringEngine',
    
    # Context linking components
    'ConversationContextAnalyzer',
    'KnowledgeGraphLinker', 
    'OperationLinker',
    
    # Factory functions
    'create_idea_queue',
    'create_idea_interface',
    'create_idea_organizer',
    'create_context_linker'
]

def create_complete_idea_system(db_path: str = None, cortex_root: str = None):
    """Create a complete IDEA system with all components."""
    queue = create_idea_queue({'db_path': db_path})
    interface = create_idea_interface({'idea_queue': queue})
    organizer = create_idea_organizer(db_path or ':memory:')  # Use in-memory DB if no path provided
    
    # Add context linker if CORTEX root is provided
    context_linker = None
    if cortex_root:
        context_linker = create_context_linker(cortex_root)
    
    return {
        'queue': queue,
        'interface': interface, 
        'organizer': organizer,
        'context_linker': context_linker
    }