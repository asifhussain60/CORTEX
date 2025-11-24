"""
Domain repository interfaces.

This package contains repository interfaces that define contracts for data access.
These interfaces are part of the domain layer and should not depend on infrastructure.
"""

from .i_repository import IRepository
from .i_unit_of_work import IUnitOfWork
from .i_conversation_repository import IConversationRepository
from .i_pattern_repository import IPatternRepository
from .i_session_repository import ISessionRepository

__all__ = [
    'IRepository',
    'IUnitOfWork',
    'IConversationRepository',
    'IPatternRepository',
    'ISessionRepository',
]
