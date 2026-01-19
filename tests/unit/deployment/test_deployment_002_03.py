"""Tests for AC-DEPLOY-002-03: Multi-Repo Context Switching"""
import pytest
from typing import Dict, Optional


class RepositoryContext:
    def __init__(self, name: str, credentials: str):
        self.name = name
        self.credentials = credentials
        self.active = False


class ContextManager:
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


class TestMultiRepoContextSwitching:
    def test_add_context(self):
        manager = ContextManager()
        result = manager.add_context("repo1", "creds1")
        assert result is True
    
    def test_switch_context(self):
        manager = ContextManager()
        manager.add_context("repo1", "creds1")
        result = manager.switch_context("repo1")
        assert result is True
        assert manager.get_current_context().name == "repo1"
    
    def test_switch_nonexistent(self):
        manager = ContextManager()
        result = manager.switch_context("nonexistent")
        assert result is False
    
    def test_multiple_contexts(self):
        manager = ContextManager()
        for i in range(3):
            manager.add_context(f"repo{i}", f"creds{i}")
        assert len(manager.list_contexts()) == 3
    
    def test_context_isolation(self):
        manager = ContextManager()
        manager.add_context("repo1", "creds1")
        manager.add_context("repo2", "creds2")
        manager.switch_context("repo1")
        assert manager.get_current_context().credentials == "creds1"
        manager.switch_context("repo2")
        assert manager.get_current_context().credentials == "creds2"
    
    def test_context_active_state(self):
        manager = ContextManager()
        manager.add_context("repo1", "creds1")
        manager.add_context("repo2", "creds2")
        manager.switch_context("repo1")
        assert manager.contexts["repo1"].active is True
        manager.switch_context("repo2")
        assert manager.contexts["repo1"].active is False
        assert manager.contexts["repo2"].active is True
    
    def test_duplicate_context(self):
        manager = ContextManager()
        manager.add_context("repo", "creds")
        result = manager.add_context("repo", "other_creds")
        assert result is False
    
    def test_remove_context(self):
        manager = ContextManager()
        manager.add_context("repo", "creds")
        result = manager.remove_context("repo")
        assert result is True
        assert "repo" not in manager.list_contexts()
    
    def test_list_contexts(self):
        manager = ContextManager()
        for i in range(3):
            manager.add_context(f"r{i}", f"c{i}")
        contexts = manager.list_contexts()
        assert len(contexts) == 3
    
    def test_credentials_stored(self):
        manager = ContextManager()
        manager.add_context("repo", "secret123")
        manager.switch_context("repo")
        assert manager.get_current_context().credentials == "secret123"
