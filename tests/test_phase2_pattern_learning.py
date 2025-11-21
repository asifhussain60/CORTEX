"""
Integration tests for Phase 2 - Tier 2 Pattern Store and Pattern Learner

Tests the complete pattern learning and retrieval workflow.

Copyright (c) 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime

from src.cortex_agents.test_generator.tier2_pattern_store import (
    Tier2PatternStore,
    BusinessPattern
)
from src.cortex_agents.test_generator.pattern_learner import (
    PatternLearner,
    ExtractedPattern
)


class TestTier2PatternStore:
    """Test Tier 2 pattern storage"""
    
    @pytest.fixture
    def pattern_store(self):
        """Create temp pattern store for testing"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        store = Tier2PatternStore(db_path)
        yield store
        store.close()
        os.unlink(db_path)
    
    def test_store_pattern(self, pattern_store):
        """Test storing a business pattern"""
        pattern = BusinessPattern(
            pattern_id=None,
            domain='authentication',
            operation='login',
            pattern_type='postcondition',
            description='User should have valid session after login',
            assertion_template='assert session.is_valid()',
            confidence=0.8,
            usage_count=0,
            success_count=0,
            created_at=datetime.now().isoformat(),
            last_used=None,
            metadata={'source': 'auth_tests.py'}
        )
        
        pattern_id = pattern_store.store_pattern(pattern)
        assert pattern_id > 0
    
    def test_search_patterns(self, pattern_store):
        """Test FTS5 pattern search"""
        # Store test patterns
        patterns = [
            BusinessPattern(
                None, 'authentication', 'login', 'postcondition',
                'Valid session after login', 'assert session.is_valid()',
                0.8, 0, 0, datetime.now().isoformat(), None, {}
            ),
            BusinessPattern(
                None, 'authentication', 'logout', 'postcondition',
                'Session invalidated after logout', 'assert not session.is_valid()',
                0.7, 0, 0, datetime.now().isoformat(), None, {}
            ),
            BusinessPattern(
                None, 'validation', 'email', 'precondition',
                'Email format validation', 'assert "@" in email',
                0.9, 0, 0, datetime.now().isoformat(), None, {}
            )
        ]
        
        for p in patterns:
            pattern_store.store_pattern(p)
        
        # Search for login patterns
        results = pattern_store.search_patterns('login', domain='authentication')
        assert len(results) >= 1
        assert results[0].operation == 'login'
    
    def test_get_patterns_by_domain(self, pattern_store):
        """Test domain-based pattern retrieval"""
        # Store patterns in different domains
        auth_pattern = BusinessPattern(
            None, 'authentication', 'login', 'postcondition',
            'Session valid', 'assert session', 0.8, 0, 0,
            datetime.now().isoformat(), None, {}
        )
        val_pattern = BusinessPattern(
            None, 'validation', 'email', 'precondition',
            'Email valid', 'assert email', 0.7, 0, 0,
            datetime.now().isoformat(), None, {}
        )
        
        pattern_store.store_pattern(auth_pattern)
        pattern_store.store_pattern(val_pattern)
        
        # Get auth patterns only
        auth_results = pattern_store.get_patterns_by_domain('authentication')
        assert len(auth_results) >= 1
        assert all(p.domain == 'authentication' for p in auth_results)
    
    def test_update_pattern_usage_success(self, pattern_store):
        """Test pattern usage tracking on success"""
        pattern = BusinessPattern(
            None, 'authentication', 'login', 'postcondition',
            'Session valid', 'assert session', 0.5, 0, 0,
            datetime.now().isoformat(), None, {}
        )
        
        pattern_id = pattern_store.store_pattern(pattern)
        
        # Update with success
        pattern_store.update_pattern_usage(pattern_id, success=True)
        
        # Confidence should increase
        results = pattern_store.search_patterns('login')
        assert len(results) > 0
        assert results[0].confidence > 0.5
        assert results[0].usage_count == 1
        assert results[0].success_count == 1
    
    def test_update_pattern_usage_failure(self, pattern_store):
        """Test pattern usage tracking on failure"""
        pattern = BusinessPattern(
            None, 'authentication', 'login', 'postcondition',
            'Session valid', 'assert session', 0.8, 0, 0,
            datetime.now().isoformat(), None, {}
        )
        
        pattern_id = pattern_store.store_pattern(pattern)
        
        # Update with failure
        pattern_store.update_pattern_usage(pattern_id, success=False)
        
        # Confidence should decrease
        results = pattern_store.search_patterns('login', min_confidence=0.0)  # Lower threshold to find pattern
        assert len(results) > 0
        assert results[0].confidence < 0.8
        assert results[0].usage_count == 1
        assert results[0].success_count == 0
    
    def test_pattern_stats(self, pattern_store):
        """Test pattern statistics"""
        # Store multiple patterns
        for i in range(5):
            pattern = BusinessPattern(
                None, 'authentication', f'operation_{i}', 'postcondition',
                f'Description {i}', f'assert condition_{i}', 0.7 + (i * 0.05),
                0, 0, datetime.now().isoformat(), None, {}
            )
            pattern_store.store_pattern(pattern)
        
        stats = pattern_store.get_pattern_stats()
        assert stats['total_patterns'] >= 5
        assert 'authentication' in stats['patterns_by_domain']
        assert stats['average_confidence'] > 0.0


class TestPatternLearner:
    """Test pattern learning from existing tests"""
    
    @pytest.fixture
    def learner_with_store(self):
        """Create pattern learner with temp storage"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        store = Tier2PatternStore(db_path)
        learner = PatternLearner(pattern_store=store)
        
        yield learner
        
        store.close()
        os.unlink(db_path)
    
    def test_learn_from_test_file(self, learner_with_store):
        """Test extracting patterns from a test file"""
        # Create temp test file
        test_code = '''
import pytest

def test_user_login_success():
    """Test successful user login"""
    user = authenticate('user@example.com', 'password123')
    assert user is not None
    assert user.is_authenticated
    
def test_user_login_invalid_password():
    """Test login with invalid password"""
    with pytest.raises(AuthenticationError):
        authenticate('user@example.com', 'wrong_password')

def test_email_validation():
    """Test email format validation"""
    result = validate_email('test@example.com')
    assert result == True
    assert '@' in 'test@example.com'
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_path = f.name
        
        try:
            patterns = learner_with_store.learn_from_test_file(temp_path)
            assert len(patterns) > 0
            
            # Check domain inference
            domains = {p.domain for p in patterns}
            assert 'authentication' in domains or 'validation' in domains
        finally:
            os.unlink(temp_path)
    
    def test_infer_domain_authentication(self, learner_with_store):
        """Test domain inference for authentication"""
        domain = learner_with_store._infer_domain('test_user_login_success')
        assert domain == 'authentication'
    
    def test_infer_domain_validation(self, learner_with_store):
        """Test domain inference for validation"""
        domain = learner_with_store._infer_domain('test_email_validate_format')
        assert domain == 'validation'
    
    def test_extract_operation(self, learner_with_store):
        """Test operation extraction from test name"""
        operation = learner_with_store._extract_operation('test_user_login_success')
        assert operation == 'login'
        
        operation = learner_with_store._extract_operation('test_calculate_total_with_tax')
        assert operation == 'calculate'
    
    def test_store_learned_patterns(self, learner_with_store):
        """Test storing learned patterns"""
        patterns = [
            ExtractedPattern(
                domain='authentication',
                operation='login',
                pattern_type='equality',
                description='Check user authenticated',
                assertion_template='assert user.is_authenticated',
                source_file='test_auth.py',
                source_function='test_login'
            )
        ]
        
        stored = learner_with_store.store_learned_patterns(patterns)
        assert stored == 1
        
        # Verify stored
        results = learner_with_store.pattern_store.search_patterns('login')
        assert len(results) >= 1


class TestPatternLearningIntegration:
    """Integration tests for complete learning workflow"""
    
    def test_complete_learning_workflow(self):
        """Test end-to-end pattern learning and retrieval"""
        # Create temp database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            # Initialize system
            store = Tier2PatternStore(db_path)
            learner = PatternLearner(pattern_store=store)
            
            # Create temp test file
            test_code = '''
def test_user_authentication():
    user = login('test@example.com', 'password')
    assert user is not None
    assert user.email == 'test@example.com'
'''
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(test_code)
                test_file = f.name
            
            try:
                # Learn patterns
                patterns = learner.learn_from_test_file(test_file)
                stored = learner.store_learned_patterns(patterns)
                
                assert stored > 0
                
                # Search patterns
                results = store.search_patterns('authentication')
                assert len(results) > 0
                
                # Update usage
                store.update_pattern_usage(results[0].pattern_id, success=True)
                
                # Verify confidence increased
                updated = store.search_patterns('authentication')
                assert updated[0].confidence > results[0].confidence
                
            finally:
                os.unlink(test_file)
            
            store.close()
        finally:
            os.unlink(db_path)
    
    def test_performance_search_under_150ms(self):
        """Test that pattern search meets Tier 2 performance target (<150ms)"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            store = Tier2PatternStore(db_path)
            
            # Store 100 patterns
            for i in range(100):
                pattern = BusinessPattern(
                    None, 'domain_' + str(i % 5), f'operation_{i}',
                    'postcondition', f'Description {i}',
                    f'assert condition_{i}', 0.7, 0, 0,
                    datetime.now().isoformat(), None, {}
                )
                store.store_pattern(pattern)
            
            # Measure search time
            import time
            start = time.time()
            results = store.search_patterns('operation', limit=10)
            elapsed_ms = (time.time() - start) * 1000
            
            # Should be under 150ms (Tier 2 target)
            assert elapsed_ms < 150, f"Search took {elapsed_ms:.1f}ms (target: <150ms)"
            assert len(results) > 0
            
            store.close()
        finally:
            os.unlink(db_path)
