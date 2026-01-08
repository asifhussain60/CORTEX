"""Tests for Multi-Repo Manager"""
import pytest
from pathlib import Path

class TestMultiRepo:
    def test_manager_init(self):
        from src.mcp.multi_repo_manager import MultiRepoManager
        manager = MultiRepoManager()
        manager.initialize()
        assert len(manager.repos) > 0
