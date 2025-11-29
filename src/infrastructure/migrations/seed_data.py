"""
Database seed data for testing
"""

from datetime import datetime, timedelta
from typing import List
import random

from ..repositories.conversation_repository import Conversation
from ..repositories.pattern_repository import Pattern
from ..repositories.context_repository import ContextItem


def generate_test_conversations(count: int = 10) -> List[Conversation]:
    """
    Generate test conversations.
    
    Args:
        count: Number of conversations to generate
        
    Returns:
        List of test conversations
    """
    conversations = []
    namespaces = ["engineering", "product", "design", "general"]
    
    for i in range(count):
        conversation = Conversation(
            conversation_id=f"conv_{i+1:03d}",
            title=f"Test Conversation {i+1}",
            content=f"This is test conversation content for conversation {i+1}. " * 5,
            quality=round(random.uniform(0.5, 1.0), 2),
            participant_count=random.randint(1, 5),
            entity_count=random.randint(5, 20),
            captured_at=datetime.now() - timedelta(days=random.randint(0, 30)),
            namespace=random.choice(namespaces)
        )
        conversations.append(conversation)
    
    return conversations


def generate_test_patterns(count: int = 10) -> List[Pattern]:
    """
    Generate test patterns.
    
    Args:
        count: Number of patterns to generate
        
    Returns:
        List of test patterns
    """
    patterns = []
    pattern_types = ["code_pattern", "design_pattern", "communication_pattern", "workflow_pattern"]
    namespaces = ["engineering", "product", "design", "general"]
    
    for i in range(count):
        pattern = Pattern(
            pattern_id=f"pattern_{i+1:03d}",
            name=f"Test Pattern {i+1}",
            pattern_type=random.choice(pattern_types),
            context=f"Context for test pattern {i+1}",
            confidence=round(random.uniform(0.6, 1.0), 2),
            namespace=random.choice(namespaces),
            examples=[
                f"Example 1 for pattern {i+1}",
                f"Example 2 for pattern {i+1}"
            ],
            related_patterns=[f"pattern_{j:03d}" for j in range(max(1, i-2), i) if j > 0]
        )
        patterns.append(pattern)
    
    return patterns


def generate_test_context_items(count: int = 15) -> List[ContextItem]:
    """
    Generate test context items.
    
    Args:
        count: Number of context items to generate
        
    Returns:
        List of test context items
    """
    context_items = []
    namespaces = ["engineering", "product", "design", "general"]
    tiers = [1, 2, 3]
    
    for i in range(count):
        context_item = ContextItem(
            context_id=f"context_{i+1:03d}",
            content=f"Test context item {i+1} with relevant information.",
            relevance_score=round(random.uniform(0.5, 1.0), 2),
            namespace=random.choice(namespaces),
            tier=random.choice(tiers),
            source_id=f"source_{random.randint(1, 10):03d}" if random.random() > 0.5 else None
        )
        context_items.append(context_item)
    
    return context_items


async def seed_database(db_context) -> dict:
    """
    Seed database with test data.
    
    Args:
        db_context: Database context
        
    Returns:
        Dictionary with counts of seeded data
    """
    from ..repositories.conversation_repository import ConversationRepository
    from ..repositories.pattern_repository import PatternRepository
    from ..repositories.context_repository import ContextRepository
    
    # Generate test data
    conversations = generate_test_conversations(10)
    patterns = generate_test_patterns(10)
    context_items = generate_test_context_items(15)
    
    # Create repositories
    conv_repo = ConversationRepository(db_context)
    pattern_repo = PatternRepository(db_context)
    context_repo = ContextRepository(db_context)
    
    # Begin transaction
    await db_context.begin()
    
    try:
        # Seed conversations
        for conversation in conversations:
            await conv_repo.add(conversation)
        
        # Seed patterns
        for pattern in patterns:
            await pattern_repo.add(pattern)
        
        # Seed context items
        for context_item in context_items:
            await context_repo.add(context_item)
        
        # Commit transaction
        await db_context.commit()
        
        return {
            'conversations': len(conversations),
            'patterns': len(patterns),
            'context_items': len(context_items)
        }
    
    except Exception as ex:
        await db_context.rollback()
        raise Exception(f"Failed to seed database: {str(ex)}") from ex
