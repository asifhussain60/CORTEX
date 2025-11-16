"""
CORTEX Conversation Pipeline Comprehensive Test Harness

Tests 20 diverse conversations through the complete save/retrieve pipeline to ensure:
1. Conversations are saved correctly to SQLite
2. Conversations can be retrieved accurately
3. Quality analysis works across all conversation types
4. Cross-session persistence works (database commits properly)
5. Edge cases are handled gracefully

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import sqlite3
from pathlib import Path
from datetime import datetime
from src.tier1.working_memory import WorkingMemory


class TestConversationPipelineHarness:
    """Comprehensive test harness with 20 diverse conversations."""
    
    @pytest.fixture
    def fresh_db(self, tmp_path):
        """Create fresh database for comprehensive testing."""
        db_path = tmp_path / "pipeline_test.db"
        wm = WorkingMemory(db_path)
        
        # Apply migration for import functionality
        from src.tier1.migration_add_conversation_import import migrate_add_conversation_import
        migrate_add_conversation_import(str(db_path))
        
        return wm, db_path
    
    def _import_and_validate(self, wm, conversation_data, test_name):
        """
        Helper to import conversation and validate it was saved correctly.
        
        Args:
            wm: WorkingMemory instance
            conversation_data: Dict with 'turns', 'expected_quality', 'description'
            test_name: Name of test for error reporting
        
        Returns:
            Dict with import result
        """
        result = wm.import_conversation(
            conversation_turns=conversation_data['turns'],
            import_source=f"test-{test_name}.md",
            workspace_path="/test/project"
        )
        
        # Validate conversation was saved
        assert result['conversation_id'] is not None, f"{test_name}: No conversation_id returned"
        assert result['turns_imported'] == len(conversation_data['turns']), \
            f"{test_name}: Turn count mismatch"
        
        # Validate quality analysis ran
        assert 'quality_score' in result, f"{test_name}: Missing quality_score"
        assert 'quality_level' in result, f"{test_name}: Missing quality_level"
        assert result['quality_level'] in ['EXCELLENT', 'GOOD', 'FAIR', 'LOW'], \
            f"{test_name}: Invalid quality_level: {result['quality_level']}"
        
        # Check expected quality if provided
        if 'expected_quality' in conversation_data:
            expected = conversation_data['expected_quality']
            if isinstance(expected, list):
                assert result['quality_level'] in expected, \
                    f"{test_name}: Expected quality {expected}, got {result['quality_level']}"
            else:
                assert result['quality_level'] == expected, \
                    f"{test_name}: Expected quality {expected}, got {result['quality_level']}"
        
        return result
    
    def test_01_single_turn_question(self, fresh_db):
        """Test 1: Simple single-turn Q&A."""
        wm, db_path = fresh_db
        
        conversation = {
            'turns': [
                {
                    'user': 'What is CORTEX?',
                    'assistant': 'CORTEX is a cognitive framework that gives AI assistants long-term memory and learning capabilities.'
                }
            ],
            'expected_quality': ['FAIR', 'LOW'],  # Single turn usually low quality
            'description': 'Simple factual question'
        }
        
        result = self._import_and_validate(wm, conversation, "single_turn_question")
        
        # Verify can retrieve it
        messages = wm.get_messages(result['conversation_id'])
        assert len(messages) == 2  # User + assistant
        assert 'What is CORTEX' in messages[0]['content']
    
    def test_02_multi_turn_implementation(self, fresh_db):
        """Test 2: Multi-turn implementation conversation."""
        wm, db_path = fresh_db
        
        conversation = {
            'turns': [
                {
                    'user': 'I need to add user authentication to my dashboard',
                    'assistant': 'I\'ll help you implement authentication. Let\'s start with the login UI component.'
                },
                {
                    'user': 'Should I use JWT tokens or session cookies?',
                    'assistant': 'JWT tokens are better for APIs. I\'ll create a token service for you.'
                },
                {
                    'user': 'How do I protect the dashboard routes?',
                    'assistant': 'Use route guards. I\'ll add middleware to check authentication before rendering.'
                }
            ],
            'expected_quality': ['GOOD', 'FAIR'],
            'description': 'Multi-turn implementation planning'
        }
        
        result = self._import_and_validate(wm, conversation, "multi_turn_implementation")
        
        # Verify all 6 messages saved (3 turns × 2 messages)
        messages = wm.get_messages(result['conversation_id'])
        assert len(messages) == 6
    
    def test_03_strategic_planning_conversation(self, fresh_db):
        """Test 3: High-quality strategic planning (CORTEX format)."""
        wm, db_path = fresh_db
        
        conversation = {
            'turns': [
                {
                    'user': 'Let\'s plan the complete authentication system architecture',
                    'assistant': '''
                    🧠 CORTEX Architecture Planning
                    
                    🎯 My Understanding: You want to design a complete authentication system
                    
                    ⚠️ **Challenge:** ✓ **Accept** - Comprehensive approach is sound
                    
                    💬 Response: I recommend a 4-phase implementation:
                    
                    Phase 1: Core Authentication (Login UI, JWT service, user validation)
                    Phase 2: Route Protection (Middleware, guards, redirect logic)
                    Phase 3: Session Management (Token refresh, logout, expiration)
                    Phase 4: Security Hardening (HTTPS, CSRF protection, rate limiting)
                    
                    This architecture provides strong security with incremental delivery.
                    
                    📝 Your Request: Design authentication system architecture
                    
                    🔍 Next Steps:
                       1. Review Phase 1 implementation details
                       2. Set up development environment for authentication
                       3. Create comprehensive test suite for security validation
                    '''
                }
            ],
            'expected_quality': ['EXCELLENT', 'GOOD'],
            'description': 'Strategic planning with CORTEX format'
        }
        
        result = self._import_and_validate(wm, conversation, "strategic_planning")
        
        # High-quality conversations should have high scores
        assert result['quality_score'] >= 6, \
            f"Strategic planning should score ≥6, got {result['quality_score']}"
        
        # Should detect multi-phase planning
        semantic = result['semantic_elements']
        assert semantic.get('multi_phase_planning') == True, \
            "Should detect multi-phase planning pattern"
        assert semantic.get('phase_count', 0) >= 4, \
            f"Should detect 4 phases, got {semantic.get('phase_count')}"
    
    def test_04_debugging_conversation(self, fresh_db):
        """Test 4: Debugging/troubleshooting conversation."""
        wm, db_path = fresh_db
        
        conversation = {
            'turns': [
                {
                    'user': 'My authentication keeps failing with 401 errors',
                    'assistant': 'Let\'s debug systematically. First, check if JWT token is being sent in headers.'
                },
                {
                    'user': 'Token is there but server rejects it',
                    'assistant': 'Check token expiration. Tokens expire after 1 hour by default.'
                },
                {
                    'user': 'Token is valid but still rejected',
                    'assistant': 'Verify token signature. Server needs correct secret key to validate.'
                }
            ],
            'expected_quality': ['GOOD', 'FAIR'],
            'description': 'Systematic debugging session'
        }
        
        result = self._import_and_validate(wm, conversation, "debugging")
        
        # Verify all messages preserved
        messages = wm.get_messages(result['conversation_id'])
        assert len(messages) == 6
        assert '401 errors' in messages[0]['content']
    
    def test_05_code_review_conversation(self, fresh_db):
        """Test 5: Code review with recommendations."""
        wm, db_path = fresh_db
        
        conversation = {
            'turns': [
                {
                    'user': 'Review this authentication code: `if user.password == input_password: login()`',
                    'assistant': 'SECURITY ISSUE: Never compare passwords directly. Use bcrypt hashing instead.'
                },
                {
                    'user': 'How do I implement bcrypt properly?',
                    'assistant': 'Use `bcrypt.hashpw()` to hash passwords on signup, `bcrypt.checkpw()` for validation.'
                }
            ],
            'expected_quality': ['GOOD', 'FAIR'],
            'description': 'Security-focused code review'
        }
        
        result = self._import_and_validate(wm, conversation, "code_review")
    
    def test_06_long_conversation(self, fresh_db):
        """Test 6: Long conversation with many turns."""
        wm, db_path = fresh_db
        
        # Generate 10-turn conversation
        turns = []
        for i in range(10):
            turns.append({
                'user': f'Step {i+1}: What should I do for authentication phase {i+1}?',
                'assistant': f'For phase {i+1}, implement the following components and test thoroughly.'
            })
        
        conversation = {
            'turns': turns,
            'expected_quality': ['GOOD', 'FAIR'],  # Multi-turn increases quality
            'description': 'Long 10-turn conversation'
        }
        
        result = self._import_and_validate(wm, conversation, "long_conversation")
        
        # Verify all 20 messages saved
        messages = wm.get_messages(result['conversation_id'])
        assert len(messages) == 20
    
    def test_07_empty_conversation(self, fresh_db):
        """Test 7: Edge case - empty conversation."""
        wm, db_path = fresh_db
        
        conversation = {
            'turns': [],
            'description': 'Empty conversation edge case'
        }
        
        result = wm.import_conversation(
            conversation_turns=[],
            import_source="test-empty.md",
            workspace_path="/test/project"
        )
        
        # Should handle gracefully
        assert result['turns_imported'] == 0
        assert result['conversation_id'] is not None
    
    def test_08_incomplete_turn(self, fresh_db):
        """Test 8: Edge case - turn with only user message."""
        wm, db_path = fresh_db
        
        conversation = {
            'turns': [
                {'user': 'How do I implement authentication?'}
                # No assistant response
            ],
            'expected_quality': ['LOW', 'FAIR'],
            'description': 'Incomplete turn (user only)'
        }
        
        result = self._import_and_validate(wm, conversation, "incomplete_turn")
        
        # Should save user message even without assistant response
        messages = wm.get_messages(result['conversation_id'])
        assert len(messages) >= 1
    
    def test_09_markdown_with_code_blocks(self, fresh_db):
        """Test 9: Conversation with code blocks in responses."""
        wm, db_path = fresh_db
        
        conversation = {
            'turns': [
                {
                    'user': 'Show me JWT authentication code',
                    'assistant': '''Here's the implementation:
                    
```python
import jwt
from datetime import datetime, timedelta

def create_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
```
'''
                }
            ],
            'expected_quality': ['GOOD', 'FAIR'],
            'description': 'Code block formatting'
        }
        
        result = self._import_and_validate(wm, conversation, "code_blocks")
        
        # Verify code preserved
        messages = wm.get_messages(result['conversation_id'])
        assert 'jwt.encode' in messages[1]['content']
    
    def test_10_conversation_with_file_references(self, fresh_db):
        """Test 10: Conversation mentioning specific files."""
        wm, db_path = fresh_db
        
        conversation = {
            'turns': [
                {
                    'user': 'Fix authentication in auth_service.py',
                    'assistant': 'I\'ll update auth_service.py line 45 to use bcrypt instead of plaintext comparison.'
                },
                {
                    'user': 'Also update user_controller.py',
                    'assistant': 'Done. Modified user_controller.py to call the updated auth service.'
                }
            ],
            'expected_quality': ['GOOD', 'FAIR'],
            'description': 'File references'
        }
        
        result = self._import_and_validate(wm, conversation, "file_references")
        
        # Should detect file references in semantic elements
        semantic = result['semantic_elements']
        assert 'file_references' in semantic, "Should detect file references"
    
    def test_11_very_short_messages(self, fresh_db):
        """Test 11: Very short messages."""
        wm, db_path = fresh_db
        
        conversation = {
            'turns': [
                {'user': 'Fix it', 'assistant': 'Done'},
                {'user': 'Test it', 'assistant': 'OK'},
                {'user': 'Ship it', 'assistant': 'Deployed'}
            ],
            'expected_quality': ['LOW', 'FAIR'],
            'description': 'Very short messages'
        }
        
        result = self._import_and_validate(wm, conversation, "short_messages")
    
    def test_12_very_long_response(self, fresh_db):
        """Test 12: Very long detailed response."""
        wm, db_path = fresh_db
        
        long_response = """
        I'll create a comprehensive authentication system for you. Here's the complete plan:
        
        """ + "\n".join([f"Step {i}: Implement feature {i} with detailed explanation and code examples." for i in range(50)])
        
        conversation = {
            'turns': [
                {'user': 'Design complete authentication', 'assistant': long_response}
            ],
            'expected_quality': ['GOOD', 'FAIR'],
            'description': 'Very long response'
        }
        
        result = self._import_and_validate(wm, conversation, "long_response")
    
    def test_13_cross_session_persistence(self, fresh_db):
        """Test 13: Verify conversations persist across Python sessions."""
        wm, db_path = fresh_db
        
        # Import conversation
        result1 = wm.import_conversation(
            conversation_turns=[
                {'user': 'Test persistence', 'assistant': 'This should persist'}
            ],
            import_source="test-persistence.md",
            workspace_path="/test/project"
        )
        
        conv_id = result1['conversation_id']
        
        # Close first session
        del wm
        
        # Open new session with same database
        wm2 = WorkingMemory(db_path)
        
        # Should be able to retrieve conversation
        messages = wm2.get_messages(conv_id)
        assert len(messages) == 2
        assert 'Test persistence' in messages[0]['content']
    
    def test_14_special_characters(self, fresh_db):
        """Test 14: Special characters and unicode."""
        wm, db_path = fresh_db
        
        conversation = {
            'turns': [
                {
                    'user': 'Add émojis 🎯 and spéciäl çhars',
                    'assistant': 'Sure! I\'ll add unicode support: 中文, العربية, 한국어 ✅'
                }
            ],
            'expected_quality': ['LOW', 'FAIR'],
            'description': 'Special characters and unicode'
        }
        
        result = self._import_and_validate(wm, conversation, "special_chars")
        
        # Verify unicode preserved
        messages = wm.get_messages(result['conversation_id'])
        assert '🎯' in messages[0]['content']
        assert '✅' in messages[1]['content']
    
    def test_15_concurrent_imports(self, fresh_db):
        """Test 15: Multiple conversations imported in sequence."""
        wm, db_path = fresh_db
        
        # Import 5 conversations rapidly
        results = []
        for i in range(5):
            result = wm.import_conversation(
                conversation_turns=[
                    {'user': f'Question {i}', 'assistant': f'Answer {i}'}
                ],
                import_source=f"test-concurrent-{i}.md",
                workspace_path="/test/project"
            )
            results.append(result)
        
        # All should have unique IDs
        conv_ids = [r['conversation_id'] for r in results]
        assert len(set(conv_ids)) == 5, "All conversation IDs should be unique"
        
        # All should be retrievable
        for conv_id in conv_ids:
            messages = wm.get_messages(conv_id)
            assert len(messages) == 2
    
    def test_16_quality_score_accuracy(self, fresh_db):
        """Test 16: Verify quality scoring is consistent."""
        wm, db_path = fresh_db
        
        # Low quality: single short turn
        low_result = wm.import_conversation(
            conversation_turns=[{'user': 'Hi', 'assistant': 'Hello'}],
            import_source="test-low.md"
        )
        
        # High quality: strategic CORTEX-format conversation
        high_result = wm.import_conversation(
            conversation_turns=[{
                'user': 'Let\'s plan a complete system architecture',
                'assistant': '''
                🧠 CORTEX Architecture Planning
                
                🎯 My Understanding: Complete system design
                
                ⚠️ **Challenge:** ✓ **Accept**
                
                💬 Response: 
                Phase 1: Core components
                Phase 2: Integration layer
                Phase 3: Testing strategy
                Phase 4: Deployment pipeline
                
                📝 Your Request: System architecture planning
                
                🔍 Next Steps:
                   1. Phase 1 implementation
                   2. Phase 2 integration
                   3. Phase 3 testing
                '''
            }],
            import_source="test-high.md"
        )
        
        # Verify quality scores make sense
        assert low_result['quality_score'] < high_result['quality_score'], \
            f"High quality ({high_result['quality_score']}) should score higher than low quality ({low_result['quality_score']})"
    
    def test_17_retrieve_by_quality_filter(self, fresh_db):
        """Test 17: Filter conversations by quality level."""
        wm, db_path = fresh_db
        
        # Import conversations of varying quality
        low_conv = wm.import_conversation(
            conversation_turns=[{'user': 'Hi', 'assistant': 'Hi'}],
            import_source="low.md"
        )
        
        good_conv = wm.import_conversation(
            conversation_turns=[{
                'user': 'Design authentication system',
                'assistant': '''I'll create a comprehensive plan:
                Phase 1: Login UI
                Phase 2: JWT service
                Phase 3: Route guards'''
            }],
            import_source="good.md"
        )
        
        # Query database for quality levels
        conn = sqlite3.connect(wm.db_path)
        cursor = conn.cursor()
        
        # Should be able to filter by quality_score
        cursor.execute("SELECT conversation_id, quality_score FROM conversations WHERE quality_score >= 6")
        high_quality = cursor.fetchall()
        
        conn.close()
        
        # Good conversation should appear in high quality results
        high_quality_ids = [row[0] for row in high_quality]
        assert good_conv['conversation_id'] in high_quality_ids
    
    def test_18_entity_extraction(self, fresh_db):
        """Test 18: Verify entity extraction works on imported conversations."""
        wm, db_path = fresh_db
        
        result = wm.import_conversation(
            conversation_turns=[{
                'user': 'Add JWT authentication to `auth_service.py` using bcrypt',
                'assistant': 'I\'ll implement JWT in `auth_service.py` with bcrypt hashing'
            }],
            import_source="test-entities.md"
        )
        
        # Extract entities
        entities = wm.extract_entities(result['conversation_id'])
        
        # Should extract file references and technologies
        entity_texts = [e.entity_name.lower() for e in entities]
        assert any('auth_service.py' in text for text in entity_texts), \
            "Should extract file reference"
    
    def test_19_session_linking(self, fresh_db):
        """Test 19: Conversations link to sessions correctly."""
        wm, db_path = fresh_db
        
        workspace = "/test/myproject"
        
        # Import conversation with workspace
        result = wm.import_conversation(
            conversation_turns=[{
                'user': 'Setup authentication',
                'assistant': 'I\'ll configure auth for your project'
            }],
            import_source="test-session.md",
            workspace_path=workspace
        )
        
        # Should have session_id
        assert result['session_id'] is not None
        
        # Session should exist in database
        session = wm.session_manager.get_active_session(workspace)
        assert session is not None
        assert session.session_id == result['session_id']
    
    def test_20_complete_pipeline_validation(self, fresh_db):
        """Test 20: End-to-end pipeline validation with all features."""
        wm, db_path = fresh_db
        
        # Complex realistic conversation
        conversation_turns = [
            {
                'user': 'I need to implement OAuth2 authentication for my React dashboard',
                'assistant': '''
                🧠 CORTEX Feature Implementation
                
                🎯 My Understanding: OAuth2 authentication for React SPA
                
                ⚠️ **Challenge:** ✓ **Accept** - OAuth2 is the right choice for modern SPAs
                
                💬 Response:
                I'll help implement OAuth2 authentication. Here's the plan:
                
                Phase 1: Backend Setup
                - Configure OAuth2 provider (Google/GitHub)
                - Implement token exchange endpoint
                - Setup JWT token generation
                
                Phase 2: Frontend Integration
                - Add OAuth2 redirect flow in React
                - Store tokens securely (httpOnly cookies)
                - Implement token refresh logic
                
                Phase 3: Protected Routes
                - Create AuthContext provider
                - Add route guards for protected pages
                - Handle authentication errors
                
                📝 Your Request: Implement OAuth2 authentication
                
                🔍 Next Steps:
                   1. Choose OAuth2 provider (Google/GitHub/Auth0)
                   2. Implement Phase 1 backend
                   3. Test token flow before moving to Phase 2
                '''
            },
            {
                'user': 'Let\'s use GitHub OAuth. Show me the backend code',
                'assistant': '''Here's the implementation:

```python
from flask import Flask, redirect, request
import requests

app = Flask(__name__)

GITHUB_CLIENT_ID = 'your_client_id'
GITHUB_CLIENT_SECRET = 'your_secret'

@app.route('/oauth/github')
def github_oauth():
    # Redirect to GitHub authorization
    return redirect(f'https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}')

@app.route('/oauth/callback')
def github_callback():
    code = request.args.get('code')
    
    # Exchange code for access token
    token_response = requests.post('https://github.com/login/oauth/access_token', {
        'client_id': GITHUB_CLIENT_ID,
        'client_secret': GITHUB_CLIENT_SECRET,
        'code': code
    })
    
    # Generate JWT and return to frontend
    # ... JWT generation code ...
```
'''
            },
            {
                'user': 'Perfect! Now show me the React integration',
                'assistant': '''Here's the React OAuth flow:

```javascript
import { useEffect } from 'react';

function LoginPage() {
  const handleGitHubLogin = () => {
    window.location.href = '/oauth/github';
  };
  
  useEffect(() => {
    // Handle OAuth callback
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');
    
    if (token) {
      localStorage.setItem('jwt_token', token);
      // Redirect to dashboard
    }
  }, []);
  
  return (
    <button onClick={handleGitHubLogin}>
      Login with GitHub
    </button>
  );
}
```
'''
            }
        ]
        
        # Import complex conversation
        result = wm.import_conversation(
            conversation_turns=conversation_turns,
            import_source="CopilotChats-OAuth-2025-11-15.md",
            workspace_path="/projects/react-dashboard"
        )
        
        # Validate all aspects
        assert result['conversation_id'] is not None
        assert result['session_id'] is not None
        assert result['turns_imported'] == 3
        assert result['quality_level'] in ['EXCELLENT', 'GOOD']
        assert result['quality_score'] >= 6
        
        # Validate semantic analysis
        semantic = result['semantic_elements']
        assert semantic['multi_phase_planning'] == True
        assert semantic['phase_count'] >= 3
        assert semantic['code_blocks'] >= 2  # Two code examples
        
        # Validate messages stored correctly
        messages = wm.get_messages(result['conversation_id'])
        assert len(messages) == 6  # 3 turns × 2 messages
        
        # Validate code blocks preserved
        assert 'github.com/login/oauth' in messages[3]['content']
        assert 'localStorage.setItem' in messages[5]['content']
        
        # Validate can retrieve from new session
        conv_id = result['conversation_id']
        del wm
        wm2 = WorkingMemory(db_path)
        messages_after = wm2.get_messages(conv_id)
        assert len(messages_after) == 6
        
        print(f"\n✅ Test 20 Complete: Full pipeline validated")
        print(f"   - Conversation ID: {result['conversation_id']}")
        print(f"   - Quality: {result['quality_level']} ({result['quality_score']}/10)")
        print(f"   - Turns: {result['turns_imported']}")
        print(f"   - Messages: {len(messages)}")
        print(f"   - Cross-session: ✅ Passed")
        print(f"   - Code preservation: ✅ Passed")
        print(f"   - Semantic analysis: ✅ Passed")

    # ========== Priority Level Entity Extraction Tests ==========

    def test_p1_entity_extraction_basic(self, fresh_db):
        """Priority 1: Basic entity extraction test with simple file references."""
        wm, db_path = fresh_db
        
        result = wm.import_conversation(
            conversation_turns=[{
                'user': 'Please update `main.py` to include the new `Config` class',
                'assistant': 'I\'ll update `main.py` to include the `Config` class definition'
            }],
            import_source="p1-entity-test.md"
        )
        
        # Extract entities
        entities = wm.extract_entities(result['conversation_id'])
        entity_names = [e.entity_name.lower() for e in entities]
        
        # Should extract file and class entities
        assert any('main.py' in name for name in entity_names), \
            "P1: Should extract file reference 'main.py'"
        assert any('config' in name for name in entity_names), \
            "P1: Should extract class reference 'Config'"
        
        # Should have at least 2 entities
        assert len(entities) >= 2, f"P1: Expected at least 2 entities, got {len(entities)}"
    
    def test_p2_entity_extraction_multiple_types(self, fresh_db):
        """Priority 2: Medium complexity with multiple entity types."""
        wm, db_path = fresh_db
        
        result = wm.import_conversation(
            conversation_turns=[{
                'user': 'Add the `authenticate()` method to `UserService` in `auth/user_service.py`',
                'assistant': 'I\'ll add the `authenticate()` method to the `UserService` class in `auth/user_service.py`'
            }],
            import_source="p2-entity-test.md"
        )
        
        # Extract entities
        entities = wm.extract_entities(result['conversation_id'])
        entity_names = [e.entity_name.lower() for e in entities]
        entity_types = [e.entity_type.value for e in entities]
        
        # Should extract file, class, and method entities
        assert any('user_service.py' in name for name in entity_names), \
            "P2: Should extract file reference 'user_service.py'"
        assert any('userservice' in name for name in entity_names), \
            "P2: Should extract class reference 'UserService'"
        assert any('authenticate()' in name or 'authenticate' in name for name in entity_names), \
            "P2: Should extract method reference 'authenticate()'"
        
        # Should have multiple entity types
        assert 'file' in entity_types, "P2: Should have file entity type"
        assert 'class' in entity_types, "P2: Should have class entity type" 
        assert 'method' in entity_types, "P2: Should have method entity type"
        
        # Should have at least 3 entities
        assert len(entities) >= 3, f"P2: Expected at least 3 entities, got {len(entities)}"
    
    def test_p3_entity_extraction_complex_scenario(self, fresh_db):
        """Priority 3: Complex scenario with nested files, classes, and technologies."""
        wm, db_path = fresh_db
        
        result = wm.import_conversation(
            conversation_turns=[{
                'user': 'Implement JWT authentication in `AuthController` class within `api/auth/auth_controller.py` using `bcrypt` for password hashing and integrate with the existing `UserRepository` from `data/user_repository.py`',
                'assistant': 'I\'ll implement JWT authentication in the `AuthController` class in `api/auth/auth_controller.py`. I\'ll use `bcrypt` for secure password hashing and integrate it with the existing `UserRepository` from `data/user_repository.py`. The implementation will include token generation and validation.'
            }],
            import_source="p3-entity-test.md"
        )
        
        # Extract entities
        entities = wm.extract_entities(result['conversation_id'])
        entity_names = [e.entity_name.lower() for e in entities]
        entity_types = [e.entity_type.value for e in entities]
        
        # Should extract multiple files
        assert any('auth_controller.py' in name for name in entity_names), \
            "P3: Should extract file reference 'auth_controller.py'"
        assert any('user_repository.py' in name for name in entity_names), \
            "P3: Should extract file reference 'user_repository.py'"
        
        # Should extract multiple classes
        assert any('authcontroller' in name for name in entity_names), \
            "P3: Should extract class reference 'AuthController'"
        assert any('userrepository' in name for name in entity_names), \
            "P3: Should extract class reference 'UserRepository'"
        
        # Should have diverse entity types
        file_entities = [e for e in entities if e.entity_type.value == 'file']
        class_entities = [e for e in entities if e.entity_type.value == 'class']
        
        assert len(file_entities) >= 2, f"P3: Expected at least 2 file entities, got {len(file_entities)}"
        assert len(class_entities) >= 2, f"P3: Expected at least 2 class entities, got {len(class_entities)}"
        
        # Should have substantial number of entities due to complexity
        assert len(entities) >= 4, f"P3: Expected at least 4 entities, got {len(entities)}"
        
        # Debug output for complex scenario
        print(f"\nP3 DEBUG: Found {len(entities)} entities:")
        for entity in entities:
            print(f"  - {entity.entity_type.value}: '{entity.entity_name}'")

    # ========== End Priority Level Tests ==========


class TestSQLiteDatabaseValidation:
    """CRITICAL: Comprehensive SQLite database validation tests.
    
    These tests ensure conversation recording pipeline is bulletproof:
    1. Database initialization and schema validation
    2. Record insertion and data integrity
    3. Cross-session persistence
    4. Recovery from corruption
    5. ACID transaction compliance
    """
    
    @pytest.fixture
    def db_harness(self, tmp_path):
        """Create database test harness with direct SQLite access."""
        db_path = tmp_path / "db_validation_test.db"
        wm = WorkingMemory(db_path)
        
        # Apply migration for import functionality
        from src.tier1.migration_add_conversation_import import migrate_add_conversation_import
        migrate_add_conversation_import(str(db_path))
        
        return wm, db_path
    
    def _direct_db_query(self, db_path: Path, query: str, params: tuple = ()):
        """Execute direct database query and return results."""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results
    
    def _verify_table_exists(self, db_path: Path, table_name: str):
        """Verify table exists with proper schema."""
        results = self._direct_db_query(
            db_path, 
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", 
            (table_name,)
        )
        assert len(results) == 1, f"Table {table_name} does not exist"
    
    def test_database_initialization_complete(self, db_harness):
        """CRITICAL: Verify database is properly initialized with all required tables."""
        wm, db_path = db_harness
        
        # Required tables for conversation storage
        required_tables = [
            'conversations',
            'messages', 
            'entities',
            'conversation_entities',
            'eviction_log'
        ]
        
        for table in required_tables:
            self._verify_table_exists(db_path, table)
    
    def test_conversation_record_insertion(self, db_harness):
        """CRITICAL: Verify conversation records are inserted correctly."""
        wm, db_path = db_harness
        
        # Import test conversation
        result = wm.import_conversation(
            conversation_turns=[{
                'user': 'Test database insertion',
                'assistant': 'Recording this conversation to verify SQLite storage'
            }],
            import_source="db-test.md",
            workspace_path="/test/db"
        )
        
        conversation_id = result['conversation_id']
        
        # Verify conversation record exists in database
        conv_records = self._direct_db_query(
            db_path,
            "SELECT conversation_id, title, message_count, import_source FROM conversations WHERE conversation_id = ?",
            (conversation_id,)
        )
        
        assert len(conv_records) == 1, "Conversation record not inserted"
        record = conv_records[0]
        assert record[0] == conversation_id, "Conversation ID mismatch"
        assert record[1] is not None, "Title not set"
        assert record[2] == 2, f"Expected 2 messages, got {record[2]}"
        assert record[3] == "db-test.md", "Import source not recorded"
        
    def test_message_records_insertion(self, db_harness):
        """CRITICAL: Verify all messages are stored correctly."""
        wm, db_path = db_harness
        
        # Multi-turn conversation
        turns = [
            {'user': 'First message', 'assistant': 'First response'},
            {'user': 'Second message', 'assistant': 'Second response'},
            {'user': 'Third message', 'assistant': 'Third response'}
        ]
        
        result = wm.import_conversation(
            conversation_turns=turns,
            import_source="msg-test.md"
        )
        
        conversation_id = result['conversation_id']
        
        # Verify message records - CORRECTED QUERY: role, content, timestamp order
        msg_records = self._direct_db_query(
            db_path,
            "SELECT role, content, timestamp FROM messages WHERE conversation_id = ? ORDER BY timestamp",
            (conversation_id,)
        )
        
        assert len(msg_records) == 6, f"Expected 6 messages, got {len(msg_records)}"
        
        # Verify message alternation (user, assistant, user, assistant...)
        expected_roles = ['user', 'assistant', 'user', 'assistant', 'user', 'assistant']
        actual_roles = [record[0] for record in msg_records]
        assert actual_roles == expected_roles, f"Message roles incorrect: {actual_roles}"
        
        # Verify content preservation - CORRECTED: content is index 1, not 2
        assert 'First message' in msg_records[0][1], "User message content not preserved"
        assert 'First response' in msg_records[1][1], "Assistant message content not preserved"
        
        # Verify timestamps are sequential - timestamps are index 2
        timestamps = [record[2] for record in msg_records]
        for i in range(1, len(timestamps)):
            assert timestamps[i] >= timestamps[i-1], "Timestamps not sequential"
    
    def test_entity_extraction_persistence(self, db_harness):
        """CRITICAL: Verify entities are extracted and persisted."""
        wm, db_path = db_harness
        
        # Conversation with explicit entities
        result = wm.import_conversation(
            conversation_turns=[{
                'user': 'Modify the `auth_service.py` file to use JWT authentication',
                'assistant': 'I\'ll update `auth_service.py` and add JWT functionality to the `AuthController` class'
            }],
            import_source="entity-test.md"
        )
        
        conversation_id = result['conversation_id']
        
        # Extract entities
        entities = wm.extract_entities(conversation_id)
        assert len(entities) > 0, "No entities extracted"
        
        # Verify entities are in database
        entity_records = self._direct_db_query(
            db_path,
            "SELECT entity_type, entity_name, access_count FROM entities"
        )
        
        assert len(entity_records) > 0, "Entities not persisted to database"
        
        # Verify conversation-entity relationships
        relationship_records = self._direct_db_query(
            db_path,
            "SELECT conversation_id, entity_id, relevance_score FROM conversation_entities WHERE conversation_id = ?",
            (conversation_id,)
        )
        
        assert len(relationship_records) > 0, "Entity relationships not recorded"
        assert all(r[2] > 0.0 for r in relationship_records), "Invalid relevance scores"
    
    def test_cross_session_persistence(self, db_harness):
        """CRITICAL: Verify data persists across WorkingMemory instances."""
        wm1, db_path = db_harness
        
        # Store conversation in first instance
        result = wm1.import_conversation(
            conversation_turns=[{
                'user': 'Test persistence across sessions',
                'assistant': 'This should be retrievable later'
            }],
            import_source="persistence-test.md"
        )
        
        conversation_id = result['conversation_id']
        
        # Create new WorkingMemory instance (simulates restart)
        wm2 = WorkingMemory(db_path)
        
        # Verify conversation is retrievable
        retrieved_conversation = wm2.conversation_manager.get_conversation(conversation_id)
        assert retrieved_conversation is not None, "Conversation not persistent across sessions"
        assert retrieved_conversation.conversation_id == conversation_id
        
        # Verify messages are retrievable
        messages = wm2.get_messages(conversation_id)
        assert len(messages) == 2, "Messages not persistent across sessions"
        assert 'Test persistence' in messages[0]['content']
    
    def test_database_transaction_integrity(self, db_harness):
        """CRITICAL: Verify ACID compliance and transaction rollback."""
        wm, db_path = db_harness
        
        # Record initial state
        initial_conversations = self._direct_db_query(db_path, "SELECT COUNT(*) FROM conversations")[0][0]
        initial_messages = self._direct_db_query(db_path, "SELECT COUNT(*) FROM messages")[0][0]
        
        # Try to import malformed conversation (should fail gracefully)
        try:
            wm.import_conversation(
                conversation_turns=[{
                    'user': None,  # Invalid data
                    'assistant': 'This should fail'
                }],
                import_source="invalid-test.md"
            )
            # If we get here, it didn't fail as expected
            assert False, "Invalid conversation should have failed"
        except Exception:
            # Expected failure - verify no partial data inserted
            pass
        
        # Verify database state unchanged (transaction rollback worked)
        final_conversations = self._direct_db_query(db_path, "SELECT COUNT(*) FROM conversations")[0][0]
        final_messages = self._direct_db_query(db_path, "SELECT COUNT(*) FROM messages")[0][0]
        
        assert final_conversations == initial_conversations, "Transaction rollback failed - conversations leaked"
        assert final_messages == initial_messages, "Transaction rollback failed - messages leaked"
    
    def test_quality_score_calculation_storage(self, db_harness):
        """CRITICAL: Verify quality scores are calculated and stored."""
        wm, db_path = db_harness
        
        # High-quality conversation (strategic planning)
        high_quality_result = wm.import_conversation(
            conversation_turns=[{
                'user': 'Design a comprehensive authentication system architecture',
                'assistant': '''🧠 CORTEX Architecture Planning
                
                🎯 Understanding: You need complete auth system design
                
                ⚠️ Challenge: ✓ Accept - Strategic approach is sound
                
                💬 Response: I recommend a 4-phase implementation:
                Phase 1: Core Authentication (Login UI, JWT service)
                Phase 2: Route Protection (Middleware, guards) 
                Phase 3: Session Management (Token refresh, logout)
                Phase 4: Security Hardening (HTTPS, CSRF, rate limiting)
                
                📝 Request: Design authentication system architecture
                
                🔍 Next Steps:
                   1. Review Phase 1 implementation details
                   2. Set up development environment 
                   3. Create comprehensive test suite
                '''
            }],
            import_source="high-quality-test.md"
        )
        
        # Verify quality score stored in database
        quality_records = self._direct_db_query(
            db_path,
            "SELECT quality_score, semantic_elements FROM conversations WHERE conversation_id = ?",
            (high_quality_result['conversation_id'],)
        )
        
        assert len(quality_records) == 1, "Quality record not found"
        stored_quality = quality_records[0][0]
        stored_semantic = quality_records[0][1]
        
        assert stored_quality >= 6.0, f"High-quality conversation should score >=6, got {stored_quality}"
        assert stored_semantic is not None, "Semantic elements not stored"
        
        # Verify semantic elements are valid JSON
        import json
        semantic_data = json.loads(stored_semantic)
        assert isinstance(semantic_data, dict), "Semantic elements should be JSON object"
    
    def test_fifo_queue_database_consistency(self, db_harness):
        """CRITICAL: Verify FIFO queue maintains database consistency."""
        wm, db_path = db_harness
        
        # Import conversations up to limit (20) + 1 to trigger FIFO
        conversation_ids = []
        for i in range(21):
            result = wm.import_conversation(
                conversation_turns=[{
                    'user': f'Test conversation {i}',
                    'assistant': f'Response {i}'
                }],
                import_source=f"fifo-test-{i}.md"
            )
            conversation_ids.append(result['conversation_id'])
        
        # Verify only 20 conversations remain in database
        conv_count = self._direct_db_query(db_path, "SELECT COUNT(*) FROM conversations")[0][0]
        assert conv_count <= 20, f"FIFO failed: {conv_count} conversations in DB (should be ≤20)"
        
        # Verify oldest conversation was removed
        remaining_ids = [
            row[0] for row in self._direct_db_query(db_path, "SELECT conversation_id FROM conversations")
        ]
        oldest_id = conversation_ids[0]
        assert oldest_id not in remaining_ids, "Oldest conversation not evicted by FIFO"
        
        # Verify newest conversation remains
        newest_id = conversation_ids[-1]
        assert newest_id in remaining_ids, "Newest conversation incorrectly evicted"
        
        # Verify eviction is logged
        eviction_records = self._direct_db_query(
            db_path,
            "SELECT conversation_id, event_type FROM eviction_log WHERE conversation_id = ?",
            (oldest_id,)
        )
        assert len(eviction_records) > 0, "FIFO eviction not logged"
        assert eviction_records[0][1] in ['evicted', 'archived'], "Invalid eviction event type"
    
    def test_concurrent_access_safety(self, db_harness):
        """CRITICAL: Verify database handles concurrent access safely."""
        wm1, db_path = db_harness
        
        # Create second WorkingMemory instance (simulates concurrent access)
        wm2 = WorkingMemory(db_path)
        
        # Import conversations from both instances simultaneously
        result1 = wm1.import_conversation(
            conversation_turns=[{
                'user': 'Concurrent access test 1',
                'assistant': 'Response from instance 1'
            }],
            import_source="concurrent-1.md"
        )
        
        result2 = wm2.import_conversation(
            conversation_turns=[{
                'user': 'Concurrent access test 2', 
                'assistant': 'Response from instance 2'
            }],
            import_source="concurrent-2.md"
        )
        
        # Verify both conversations saved without corruption
        conv1 = wm1.conversation_manager.get_conversation(result1['conversation_id'])
        conv2 = wm2.conversation_manager.get_conversation(result2['conversation_id'])
        
        assert conv1 is not None, "Concurrent access corrupted conversation 1"
        assert conv2 is not None, "Concurrent access corrupted conversation 2"
        assert conv1.conversation_id != conv2.conversation_id, "Concurrent access caused ID collision"
        
        # Verify messages accessible from both instances
        messages1_from_wm1 = wm1.get_messages(result1['conversation_id'])
        messages1_from_wm2 = wm2.get_messages(result1['conversation_id'])
        
        assert len(messages1_from_wm1) == len(messages1_from_wm2), "Concurrent access caused message inconsistency"


class TestPipelineBrokenComponentsCheck:
    """Check for other broken pipelines similar to conversation persistence."""
    
    def test_knowledge_graph_updates(self):
        """Verify knowledge graph update pipeline works."""
        # TODO: Add test for knowledge graph pattern learning
        pytest.skip("Knowledge graph update pipeline test - to be implemented")
    
    def test_session_correlation(self):
        """Verify session-conversation correlation works."""
        # TODO: Add test for session correlation
        pytest.skip("Session correlation test - to be implemented")
