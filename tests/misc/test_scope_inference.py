"""
CORTEX Phase 3.2 - Scope Inference Engine Tests (TDD RED Phase)

Purpose: Validate scope extraction from Planning DoR Q3 (functional scope) and Q6 (technical dependencies)
Target: <5s execution time, >70% confidence threshold for auto-proceed
Status: RED - Tests should fail until implementation complete

Test Coverage:
- Entity extraction (tables, files, services, dependencies)
- Confidence scoring (>70% high, 30-70% medium, <30% low)
- Scope boundary generation (max 50 tables, 100 files, 2-hop depth)
- Edge cases (vague requirements, missing data, enterprise scale)
"""

import pytest
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime

# Module under test (doesn't exist yet - TDD RED)
from src.agents.estimation.scope_inference_engine import (
    ScopeInferenceEngine,
    ScopeEntities,
    ScopeBoundary
)


class TestScopeEntityExtraction:
    """Test entity detection from requirements text"""
    
    def test_extract_database_tables_from_explicit_mentions(self):
        """Should detect explicitly named tables"""
        engine = ScopeInferenceEngine()
        requirements = """
        This feature will modify the Users table, UserProfiles table, and Sessions table.
        We need to add authentication fields to user_accounts.
        """
        
        entities = engine.extract_entities(requirements)
        
        assert "Users" in entities.tables
        assert "UserProfiles" in entities.tables
        assert "Sessions" in entities.tables
        assert "user_accounts" in entities.tables
        assert len(entities.tables) == 4
    
    def test_extract_files_from_class_mentions(self):
        """Should detect file/class references"""
        engine = ScopeInferenceEngine()
        requirements = """
        We'll need to update UserService.cs, AuthController.cs, and authentication.py.
        The LoginViewModel will also need changes.
        """
        
        entities = engine.extract_entities(requirements)
        
        assert "UserService.cs" in entities.files
        assert "AuthController.cs" in entities.files
        assert "authentication.py" in entities.files
        assert "LoginViewModel" in entities.files
        assert len(entities.files) == 4
    
    def test_extract_external_services(self):
        """Should detect external service dependencies"""
        engine = ScopeInferenceEngine()
        requirements = """
        This integrates with Azure AD for authentication, SendGrid for emails,
        and Twilio for SMS notifications.
        """
        
        entities = engine.extract_entities(requirements)
        
        assert "Azure AD" in entities.services
        assert "SendGrid" in entities.services
        assert "Twilio" in entities.services
        assert len(entities.services) == 3
    
    def test_extract_technical_dependencies(self):
        """Should detect technical dependencies (OAuth, JWT, etc.)"""
        engine = ScopeInferenceEngine()
        requirements = """
        Requires OAuth 2.0 implementation, JWT token handling,
        and SMTP configuration for password resets.
        """
        
        entities = engine.extract_entities(requirements)
        
        assert "OAuth" in entities.dependencies or "OAuth 2.0" in entities.dependencies
        assert "JWT" in entities.dependencies
        assert "SMTP" in entities.dependencies
    
    def test_extract_from_dor_q3_functional_scope(self):
        """Should parse DoR Question 3 (functional scope) format"""
        engine = ScopeInferenceEngine()
        dor_q3 = """
        **Functional Scope:**
        - User authentication with email/password
        - Password reset via email
        - Session management with 30-minute timeout
        
        **Database Changes:**
        - Users table (add password_hash, salt columns)
        - Sessions table (new table for active sessions)
        - PasswordResets table (new table for reset tokens)
        """
        
        entities = engine.extract_entities(dor_q3)
        
        assert "Users" in entities.tables
        assert "Sessions" in entities.tables
        assert "PasswordResets" in entities.tables
        assert len(entities.tables) >= 3
    
    def test_extract_from_dor_q6_technical_dependencies(self):
        """Should parse DoR Question 6 (technical dependencies) format"""
        engine = ScopeInferenceEngine()
        dor_q6 = """
        **Technical Dependencies:**
        - Azure AD B2C for social login
        - SendGrid API for email delivery
        - Redis for session caching
        
        **Integration Points:**
        - UserService (add authentication methods)
        - EmailService (password reset emails)
        - CacheService (session storage)
        """
        
        entities = engine.extract_entities(dor_q6)
        
        assert "Azure AD" in entities.services or "Azure AD B2C" in entities.services
        assert "SendGrid" in entities.services
        assert "Redis" in entities.services
        assert "UserService" in entities.files
        assert "EmailService" in entities.files
        assert "CacheService" in entities.files


class TestConfidenceScoring:
    """Test confidence calculation for scope inference"""
    
    def test_high_confidence_with_explicit_entities(self):
        """Clear entity names should produce >70% confidence"""
        engine = ScopeInferenceEngine()
        entities = ScopeEntities(
            tables=["Users", "UserProfiles", "Sessions"],
            files=["UserService.cs", "AuthController.cs"],
            services=["Azure AD", "SendGrid"],
            dependencies=["OAuth", "JWT"],
            confidence_scores={}
        )
        
        confidence = engine.calculate_confidence(entities)
        
        assert confidence > 0.70, "Explicit entities should have high confidence"
    
    def test_medium_confidence_with_mixed_clarity(self):
        """Mix of clear and vague entities should be 30-70% confidence"""
        engine = ScopeInferenceEngine()
        requirements = """
        We need to update some user tables and a few authentication files.
        Maybe integrate with an email service.
        """
        
        entities = engine.extract_entities(requirements)
        confidence = engine.calculate_confidence(entities, requirements)
        
        assert 0.30 <= confidence <= 0.70, "Vague references should have medium confidence"
    
    def test_low_confidence_with_vague_scope(self):
        """Vague requirements should produce <30% confidence"""
        engine = ScopeInferenceEngine()
        requirements = """
        Add authentication to the system. Make it secure.
        """
        
        entities = engine.extract_entities(requirements)
        confidence = engine.calculate_confidence(entities, requirements)
        
        assert confidence < 0.30, "Vague requirements should have low confidence"
    
    def test_confidence_increases_with_quantified_scope(self):
        """Quantified scope ("15 tables") should boost confidence"""
        engine = ScopeInferenceEngine()
        requirements_vague = "Update user tables"
        requirements_quantified = "Update 15 user-related tables: Users, UserProfiles, ..."
        
        entities_vague = engine.extract_entities(requirements_vague)
        entities_quantified = engine.extract_entities(requirements_quantified)
        
        confidence_vague = engine.calculate_confidence(entities_vague)
        confidence_quantified = engine.calculate_confidence(entities_quantified)
        
        assert confidence_quantified > confidence_vague, "Quantified scope should have higher confidence"


class TestScopeBoundaryGeneration:
    """Test scope boundary creation with safety limits"""
    
    def test_generate_boundary_with_valid_entities(self):
        """Should create boundary with entity counts"""
        engine = ScopeInferenceEngine()
        entities = ScopeEntities(
            tables=["Users", "UserProfiles", "Sessions"],
            files=["UserService.cs", "AuthController.cs"],
            services=["Azure AD"],
            dependencies=["OAuth"],
            confidence_scores={}
        )
        
        boundary = engine.generate_scope_boundary(entities, confidence=0.85)
        
        assert boundary.table_count == 3
        assert boundary.file_count == 2
        assert boundary.service_count == 1
        assert boundary.dependency_depth <= 2
        assert boundary.confidence == 0.85
    
    def test_boundary_enforces_50_table_limit(self):
        """Should cap at 50 tables (enterprise monolith protection)"""
        engine = ScopeInferenceEngine()
        # Simulate 100 tables detected
        entities = ScopeEntities(
            tables=[f"Table{i}" for i in range(100)],
            files=[],
            services=[],
            dependencies=[],
            confidence_scores={}
        )
        
        boundary = engine.generate_scope_boundary(entities, confidence=0.80)
        
        assert boundary.table_count <= 50, "Should enforce 50 table maximum"
        assert len(boundary.gaps) > 0, "Should flag scope overflow in gaps"
    
    def test_boundary_enforces_100_file_limit(self):
        """Should cap at 100 files"""
        engine = ScopeInferenceEngine()
        entities = ScopeEntities(
            tables=[],
            files=[f"File{i}.cs" for i in range(150)],
            services=[],
            dependencies=[],
            confidence_scores={}
        )
        
        boundary = engine.generate_scope_boundary(entities, confidence=0.75)
        
        assert boundary.file_count <= 100, "Should enforce 100 file maximum"
    
    def test_boundary_calculates_estimated_complexity(self):
        """Should estimate complexity (0-100 scale)"""
        engine = ScopeInferenceEngine()
        # Small scope
        entities_small = ScopeEntities(
            tables=["Users"],
            files=["UserService.cs"],
            services=[],
            dependencies=[],
            confidence_scores={}
        )
        # Large scope
        entities_large = ScopeEntities(
            tables=[f"Table{i}" for i in range(20)],
            files=[f"File{i}.cs" for i in range(30)],
            services=["Azure AD", "SendGrid", "Twilio"],
            dependencies=["OAuth", "JWT", "SMTP", "Redis"],
            confidence_scores={}
        )
        
        boundary_small = engine.generate_scope_boundary(entities_small, confidence=0.90)
        boundary_large = engine.generate_scope_boundary(entities_large, confidence=0.80)
        
        assert 0 <= boundary_small.estimated_complexity <= 100
        assert 0 <= boundary_large.estimated_complexity <= 100
        assert boundary_large.estimated_complexity > boundary_small.estimated_complexity
    
    def test_boundary_identifies_gaps_for_clarification(self):
        """Should list missing information for clarification"""
        engine = ScopeInferenceEngine()
        entities = ScopeEntities(
            tables=[],  # No tables mentioned
            files=["UserService.cs"],
            services=[],
            dependencies=["OAuth"],  # Vague dependency
            confidence_scores={}
        )
        
        boundary = engine.generate_scope_boundary(entities, confidence=0.25)
        
        assert len(boundary.gaps) > 0, "Should identify gaps for low confidence"
        assert any("table" in gap.lower() for gap in boundary.gaps), "Should flag missing tables"


class TestPerformance:
    """Test execution time targets"""
    
    def test_scope_inference_completes_under_5_seconds(self):
        """Entire scope inference should complete in <5 seconds"""
        engine = ScopeInferenceEngine()
        # Large realistic requirements
        requirements = """
        This feature implements user authentication with the following scope:
        
        Database Changes:
        - Users table (add password_hash, salt, last_login, failed_attempts)
        - UserProfiles table (link to Users)
        - Sessions table (new - store active sessions)
        - PasswordResets table (new - reset tokens)
        - AuditLog table (track login attempts)
        
        Code Changes:
        - UserService.cs (authentication methods)
        - AuthController.cs (login/logout endpoints)
        - SessionManager.cs (session handling)
        - PasswordResetService.cs (email reset flow)
        - AuthMiddleware.cs (request authentication)
        
        External Services:
        - Azure AD B2C (social login)
        - SendGrid (email delivery)
        - Redis (session caching)
        
        Dependencies:
        - OAuth 2.0, JWT, SMTP, bcrypt
        """
        
        start = datetime.now()
        entities = engine.extract_entities(requirements)
        confidence = engine.calculate_confidence(entities)
        boundary = engine.generate_scope_boundary(entities, confidence)
        duration = (datetime.now() - start).total_seconds()
        
        assert duration < 5.0, f"Scope inference took {duration}s (target: <5s)"


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_requirements_returns_empty_entities(self):
        """Should handle empty requirements gracefully"""
        engine = ScopeInferenceEngine()
        entities = engine.extract_entities("")
        
        assert len(entities.tables) == 0
        assert len(entities.files) == 0
        assert len(entities.services) == 0
        assert len(entities.dependencies) == 0
    
    def test_handles_mixed_case_entity_names(self):
        """Should normalize entity names (case-insensitive)"""
        engine = ScopeInferenceEngine()
        requirements = "Update users table, USERS table, and Users table"
        
        entities = engine.extract_entities(requirements)
        
        # Should deduplicate case variations
        assert len([t for t in entities.tables if t.lower() == "users"]) == 1
    
    def test_handles_special_characters_in_entity_names(self):
        """Should parse entities with underscores, hyphens, dots"""
        engine = ScopeInferenceEngine()
        requirements = """
        Tables: user_accounts, user-profiles, sys.Users
        Files: User.Service.cs, Auth_Controller.py
        """
        
        entities = engine.extract_entities(requirements)
        
        assert "user_accounts" in entities.tables
        assert "user-profiles" in entities.tables or "user_profiles" in entities.tables
        assert any("User" in f and "Service" in f for f in entities.files)
    
    def test_handles_duplicate_entities(self):
        """Should deduplicate repeated entity mentions"""
        engine = ScopeInferenceEngine()
        requirements = """
        Update Users table. The Users table needs authentication.
        UserService.cs handles Users table operations.
        """
        
        entities = engine.extract_entities(requirements)
        
        # Should only list Users once
        assert entities.tables.count("Users") == 1


class TestParseDorAnswers:
    """Test DoR response parsing"""
    
    def test_parse_combined_dor_q3_and_q6(self):
        """Should combine Q3 and Q6 for complete scope picture"""
        engine = ScopeInferenceEngine()
        dor_responses = {
            'Q3': """
            Functional Scope:
            - User authentication with email/password
            - Password reset flow
            
            Database: Users, Sessions, PasswordResets tables
            """,
            'Q6': """
            Technical Dependencies:
            - Azure AD for SSO
            - SendGrid for emails
            
            Code: UserService.cs, AuthController.cs
            """
        }
        
        combined_text = engine.parse_dor_answers(dor_responses)
        
        assert "Users" in combined_text
        assert "Azure AD" in combined_text
        assert "UserService.cs" in combined_text
    
    def test_parse_handles_missing_questions(self):
        """Should handle missing Q3 or Q6 gracefully"""
        engine = ScopeInferenceEngine()
        dor_responses_q3_only = {'Q3': 'Update Users table'}
        dor_responses_q6_only = {'Q6': 'Integrate Azure AD'}
        
        text_q3 = engine.parse_dor_answers(dor_responses_q3_only)
        text_q6 = engine.parse_dor_answers(dor_responses_q6_only)
        
        assert "Users" in text_q3
        assert "Azure AD" in text_q6


if __name__ == "__main__":
    # Run tests to verify RED phase (should fail)
    pytest.main([__file__, "-v", "--tb=short"])
