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
                'user': 'Add JWT authentication to auth_service.py using bcrypt',
                'assistant': 'I\'ll implement JWT in auth_service.py with bcrypt hashing'
            }],
            import_source="test-entities.md"
        )
        
        # Extract entities
        entities = wm.extract_entities(result['conversation_id'])
        
        # Should extract file references and technologies
        entity_texts = [e.text.lower() for e in entities]
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


class TestPipelineBrokenComponentsCheck:
    """Check for other broken pipelines similar to conversation persistence."""
    
    def test_knowledge_graph_updates(self):
        """Verify knowledge graph update pipeline works."""
        # TODO: Add test for knowledge graph pattern learning
        pytest.skip("Knowledge graph update pipeline test - to be implemented")
    
    def test_entity_extraction_persistence(self):
        """Verify extracted entities persist correctly."""
        # TODO: Add test for entity extraction and storage
        pytest.skip("Entity extraction persistence test - to be implemented")
    
    def test_session_correlation(self):
        """Verify session-conversation correlation works."""
        # TODO: Add test for session correlation
        pytest.skip("Session correlation test - to be implemented")
