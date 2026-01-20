"""Multi-Repo Context Switching System"""
from typing import Dict, Optional


class RepositoryContext:
    """Repository context with credentials.
    
    Args:
        name: Repository name
        credentials: Authentication credentials
    """
    def __init__(self, name: str, credentials: str):
        self.name = name
        self.credentials = credentials
        self.active = False


class ContextManager:
    """Manages multiple repository contexts."""
    
    def __init__(self):
        self.contexts: Dict[str, RepositoryContext] = {}
        self.current_context: Optional[RepositoryContext] = None
    
    def add_context(self, name: str, credentials: str) -> bool:
        if name in self.contexts:
            return False
        self.contexts[name] = RepositoryContext(name, credentials)
        return True
    
    def switch_context(self, name: str) -> bool:
        if name not in self.contexts:
            return False
        if self.current_context:
            self.current_context.active = False
        context = self.contexts[name]
        context.active = True
        self.current_context = context
        return True
    
    def get_current_context(self) -> Optional[RepositoryContext]:
        return self.current_context
    
    def list_contexts(self) -> list:
        return list(self.contexts.keys())
    
    def remove_context(self, name: str) -> bool:
        if name in self.contexts:
            del self.contexts[name]
            return True
        return False
