"""Tests for InquiryOrchestrator - Main entry point.

AC-ID: INQUIRY-014
Purpose: Test complete inquiry pipeline
Author: Asif Hussain
Date: 2026-01-27
"""

from pathlib import Path

import pytest

from cortex.orchestrators.domain.inquiry_orchestrator import InquiryOrchestrator


class TestInquiryOrchestratorInitialization:
    """Test orchestrator initialization."""
    
    def test_create_orchestrator(self) -> None:
        """Test creating InquiryOrchestrator."""
        orchestrator = InquiryOrchestrator()
        
        assert orchestrator is not None
        assert hasattr(orchestrator, "ask")


class TestInquiryPipelineExecution:
    """Test complete pipeline execution."""
    
    def test_ask_question_complete_pipeline(self, tmp_path: Path) -> None:
        """Test asking question through complete pipeline."""
        orchestrator = InquiryOrchestrator(repo_path=tmp_path)
        
        response = orchestrator.ask("How does authentication work?")
        
        assert isinstance(response, dict)
        assert "answer" in response
        assert "evidence" in response
        assert "confidence" in response
        assert "repo_type" in response
        assert "category" in response
    
    def test_ask_returns_all_required_fields(self, tmp_path: Path) -> None:
        """Test response contains all required fields."""
        orchestrator = InquiryOrchestrator(repo_path=tmp_path)
        
        response = orchestrator.ask("Test question")
        
        required_fields = [
            "answer",
            "evidence",
            "confidence",
            "repo_type",
            "repo_name",
            "category",
            "cache_hit",
        ]
        
        for field in required_fields:
            assert field in response
    
    def test_ask_with_category_hint(self, tmp_path: Path) -> None:
        """Test asking with category hint."""
        from cortex.models.inquiry_models import InquiryCategory
        
        orchestrator = InquiryOrchestrator(repo_path=tmp_path)
        
        response = orchestrator.ask(
            "How is the system designed?",
            category_hint=InquiryCategory.ARCHITECTURE,
        )
        
        assert response["category"] == "architecture"
    
    def test_ask_with_file_paths(self, tmp_path: Path) -> None:
        """Test asking with file path hints."""
        orchestrator = InquiryOrchestrator(repo_path=tmp_path)
        
        response = orchestrator.ask(
            "What does this file do?",
            file_paths=["src/main.py"],
        )
        
        assert isinstance(response, dict)


class TestCacheIntegration:
    """Test cache integration in pipeline."""
    
    def test_second_ask_uses_cache(self, tmp_path: Path) -> None:
        """Test second identical question uses cache."""
        orchestrator = InquiryOrchestrator(repo_path=tmp_path)
        
        question = "How does feature X work?"
        
        # First ask - cache miss
        response1 = orchestrator.ask(question)
        
        # Second ask - should hit cache
        response2 = orchestrator.ask(question)
        
        # Both should return valid responses
        assert "answer" in response1
        assert "answer" in response2
