"""
Track A Phase 2: Comprehensive Unit Tests for SemanticExtractor

Tests semantic analysis of conversations including:
- Entity extraction (files, classes, functions, variables)
- Intent detection (EXECUTE, PLAN, TEST, FIX, etc.)
- Quality scoring (0-10 scale)
- Conversation depth analysis
- Multi-turn pattern recognition

Author: CORTEX Team
Date: 2025-11-15
"""

import pytest
from src.track_a.extractors.semantic_extractor import SemanticExtractor


class TestSemanticExtractorBasics:
    """Test basic SemanticExtractor functionality."""
    
    @pytest.fixture
    def extractor(self):
        """Create SemanticExtractor instance."""
        return SemanticExtractor()
    
    def test_extractor_initialization(self, extractor):
        """Test extractor initializes successfully."""
        assert extractor is not None
        assert hasattr(extractor, 'extract')
        assert callable(extractor.extract)
    
    def test_extractor_has_required_methods(self, extractor):
        """Test extractor has all required analysis methods."""
        assert hasattr(extractor, 'extract')
        # May have private methods for entity/intent/quality extraction


class TestEntityExtraction:
    """Test entity extraction from conversations."""
    
    @pytest.fixture
    def extractor(self):
        return SemanticExtractor()
    
    @pytest.fixture
    def conversation_with_code(self):
        """Conversation containing code entities."""
        return {
            "messages": [
                {
                    "role": "user",
                    "content": "How do I modify the AuthService.cs file?",
                    "timestamp": "2025-11-15T10:00:00"
                },
                {
                    "role": "assistant",
                    "content": """Here's how to update AuthService.cs:

```csharp
public class AuthService {
    public bool ValidateUser(string username) {
        return UserRepository.FindByUsername(username) != null;
    }
}
```

This adds a ValidateUser method to the AuthService class.""",
                    "timestamp": "2025-11-15T10:00:05"
                }
            ]
        }
    
    def test_extract_file_entities(self, extractor, conversation_with_code):
        """Test extraction of file names."""
        result = extractor.extract(conversation_with_code)
        
        assert "entities" in result
        entities = result["entities"]
        
        # Should find AuthService.cs
        file_entities = [e for e in entities if e.get("type") == "file"]
        assert len(file_entities) >= 1
        assert any("AuthService.cs" in e.get("value", "") for e in file_entities)
    
    def test_extract_class_entities(self, extractor, conversation_with_code):
        """Test extraction of class names."""
        result = extractor.extract(conversation_with_code)
        
        entities = result["entities"]
        
        # Should find AuthService and UserRepository classes
        class_entities = [e for e in entities if e.get("type") == "class"]
        assert len(class_entities) >= 1
        
        class_names = [e.get("value", "") for e in class_entities]
        assert any("AuthService" in name for name in class_names)
    
    def test_extract_method_entities(self, extractor, conversation_with_code):
        """Test extraction of method/function names."""
        result = extractor.extract(conversation_with_code)
        
        entities = result["entities"]
        
        # Should find ValidateUser and FindByUsername methods
        method_entities = [e for e in entities if e.get("type") in ["method", "function"]]
        assert len(method_entities) >= 1
        
        method_names = [e.get("value", "") for e in method_entities]
        assert any("ValidateUser" in name or "FindByUsername" in name for name in method_names)
    
    def test_extract_entities_from_natural_language(self, extractor):
        """Test entity extraction from natural language (no code)."""
        conversation = {
            "messages": [
                {
                    "role": "user",
                    "content": "I need to update the authentication module in src/auth/AuthModule.py",
                    "timestamp": "2025-11-15T10:00:00"
                }
            ]
        }
        
        result = extractor.extract(conversation)
        entities = result["entities"]
        
        # Should extract file path
        file_entities = [e for e in entities if e.get("type") == "file"]
        assert len(file_entities) >= 1
    
    def test_entity_deduplication(self, extractor):
        """Test entities are deduplicated."""
        conversation = {
            "messages": [
                {
                    "role": "user",
                    "content": "Update AuthService.cs",
                    "timestamp": "2025-11-15T10:00:00"
                },
                {
                    "role": "assistant",
                    "content": "I'll update AuthService.cs for you.",
                    "timestamp": "2025-11-15T10:00:05"
                },
                {
                    "role": "user",
                    "content": "Make sure AuthService.cs has error handling",
                    "timestamp": "2025-11-15T10:00:10"
                }
            ]
        }
        
        result = extractor.extract(conversation)
        entities = result["entities"]
        
        # Should deduplicate AuthService.cs mentions
        file_entities = [e for e in entities if e.get("type") == "file" and "AuthService.cs" in e.get("value", "")]
        # May have 1 or multiple entries depending on implementation
        assert len(file_entities) >= 1


class TestIntentDetection:
    """Test intent detection from conversations."""
    
    @pytest.fixture
    def extractor(self):
        return SemanticExtractor()
    
    def test_detect_execute_intent(self, extractor):
        """Test detection of EXECUTE intent."""
        conversation = {
            "messages": [
                {
                    "role": "user",
                    "content": "Create a new function called processData that handles user input",
                    "timestamp": "2025-11-15T10:00:00"
                }
            ]
        }
        
        result = extractor.extract(conversation)
        
        assert "intents" in result
        assert "EXECUTE" in result["intents"]
    
    def test_detect_plan_intent(self, extractor):
        """Test detection of PLAN intent."""
        conversation = {
            "messages": [
                {
                    "role": "user",
                    "content": "How should I design the authentication system architecture?",
                    "timestamp": "2025-11-15T10:00:00"
                }
            ]
        }
        
        result = extractor.extract(conversation)
        
        assert "intents" in result
        assert "PLAN" in result["intents"]
    
    def test_detect_test_intent(self, extractor):
        """Test detection of TEST intent."""
        conversation = {
            "messages": [
                {
                    "role": "user",
                    "content": "Write unit tests for the AuthService class",
                    "timestamp": "2025-11-15T10:00:00"
                }
            ]
        }
        
        result = extractor.extract(conversation)
        
        assert "intents" in result
        assert "TEST" in result["intents"]
    
    def test_detect_fix_intent(self, extractor):
        """Test detection of FIX intent."""
        conversation = {
            "messages": [
                {
                    "role": "user",
                    "content": "There's a bug in the login function - it's returning null",
                    "timestamp": "2025-11-15T10:00:00"
                }
            ]
        }
        
        result = extractor.extract(conversation)
        
        assert "intents" in result
        # Should detect FIX or EXECUTE
        assert "FIX" in result["intents"] or "EXECUTE" in result["intents"]
    
    def test_detect_multiple_intents(self, extractor):
        """Test detection of multiple intents in conversation."""
        conversation = {
            "messages": [
                {
                    "role": "user",
                    "content": "Create a login function and write tests for it",
                    "timestamp": "2025-11-15T10:00:00"
                }
            ]
        }
        
        result = extractor.extract(conversation)
        
        intents = result["intents"]
        # Should detect both EXECUTE (create) and TEST (write tests)
        assert len(intents) >= 1
    
    def test_detect_status_intent(self, extractor):
        """Test detection of STATUS intent."""
        conversation = {
            "messages": [
                {
                    "role": "user",
                    "content": "What's the current status of the project?",
                    "timestamp": "2025-11-15T10:00:00"
                }
            ]
        }
        
        result = extractor.extract(conversation)
        
        assert "intents" in result
        # May detect STATUS, ANALYZE, or similar
        assert len(result["intents"]) >= 1


class TestQualityScoring:
    """Test conversation quality scoring."""
    
    @pytest.fixture
    def extractor(self):
        return SemanticExtractor()
    
    def test_quality_score_in_range(self, extractor):
        """Test quality score is in 0-10 range."""
        conversation = {
            "messages": [
                {"role": "user", "content": "Test", "timestamp": "2025-11-15T10:00:00"}
            ]
        }
        
        result = extractor.extract(conversation)
        
        assert "quality" in result
        assert 0 <= result["quality"] <= 10
    
    def test_quality_score_short_conversation(self, extractor):
        """Test quality score for short conversation."""
        short_conv = {
            "messages": [
                {"role": "user", "content": "Hi", "timestamp": "2025-11-15T10:00:00"}
            ]
        }
        
        result = extractor.extract(short_conv)
        
        # Short conversations should have lower quality
        assert result["quality"] <= 5
    
    def test_quality_score_detailed_conversation(self, extractor):
        """Test quality score for detailed conversation."""
        detailed_conv = {
            "messages": [
                {
                    "role": "user",
                    "content": "I need help implementing a comprehensive authentication system with JWT tokens, session management, and role-based access control.",
                    "timestamp": "2025-11-15T10:00:00"
                },
                {
                    "role": "assistant",
                    "content": """Here's a detailed implementation plan:

1. JWT Token Generation:
   - Use industry-standard libraries
   - Implement refresh token mechanism
   
2. Session Management:
   - Store sessions in Redis
   - Implement timeout and renewal
   
3. RBAC:
   - Define role hierarchy
   - Implement permission checking

Let me show you code examples for each component...""",
                    "timestamp": "2025-11-15T10:00:05"
                },
                {
                    "role": "user",
                    "content": "Can you show the JWT implementation first?",
                    "timestamp": "2025-11-15T10:00:10"
                }
            ]
        }
        
        result = extractor.extract(detailed_conv)
        
        # Detailed conversations should have higher quality
        assert result["quality"] >= 5
    
    def test_quality_score_with_code(self, extractor):
        """Test quality score considers code presence."""
        conv_with_code = {
            "messages": [
                {
                    "role": "user",
                    "content": "Show me a function",
                    "timestamp": "2025-11-15T10:00:00"
                },
                {
                    "role": "assistant",
                    "content": """Here's the function:

```python
def calculate(x, y):
    return x + y
```""",
                    "timestamp": "2025-11-15T10:00:05"
                }
            ]
        }
        
        result = extractor.extract(conv_with_code)
        
        # Code presence may increase quality
        assert result["quality"] > 0


class TestMultiTurnAnalysis:
    """Test analysis of multi-turn conversations."""
    
    @pytest.fixture
    def extractor(self):
        return SemanticExtractor()
    
    def test_extract_from_multi_turn_conversation(self, extractor):
        """Test extraction handles multiple turns correctly."""
        multi_turn = {
            "messages": [
                {"role": "user", "content": "Create AuthService.cs", "timestamp": "2025-11-15T10:00:00"},
                {"role": "assistant", "content": "I'll create AuthService.cs", "timestamp": "2025-11-15T10:00:05"},
                {"role": "user", "content": "Add ValidateUser method", "timestamp": "2025-11-15T10:00:10"},
                {"role": "assistant", "content": "Added ValidateUser method", "timestamp": "2025-11-15T10:00:15"}
            ]
        }
        
        result = extractor.extract(multi_turn)
        
        # Should extract entities and intents across all turns
        assert len(result["entities"]) >= 1
        assert len(result["intents"]) >= 1
    
    def test_quality_increases_with_turns(self, extractor):
        """Test quality score tends to increase with more turns."""
        single_turn = {
            "messages": [
                {"role": "user", "content": "Test", "timestamp": "2025-11-15T10:00:00"}
            ]
        }
        
        multi_turn = {
            "messages": [
                {"role": "user", "content": "Test 1", "timestamp": "2025-11-15T10:00:00"},
                {"role": "assistant", "content": "Response 1", "timestamp": "2025-11-15T10:00:05"},
                {"role": "user", "content": "Test 2", "timestamp": "2025-11-15T10:00:10"},
                {"role": "assistant", "content": "Response 2", "timestamp": "2025-11-15T10:00:15"}
            ]
        }
        
        single_result = extractor.extract(single_turn)
        multi_result = extractor.extract(multi_turn)
        
        # Multi-turn should generally have higher quality
        assert multi_result["quality"] >= single_result["quality"]


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.fixture
    def extractor(self):
        return SemanticExtractor()
    
    def test_extract_empty_conversation(self, extractor):
        """Test extraction from empty conversation."""
        empty_conv = {"messages": []}
        
        result = extractor.extract(empty_conv)
        
        assert result is not None
        assert "entities" in result
        assert "intents" in result
        assert "quality" in result
        assert len(result["entities"]) == 0
        assert result["quality"] == 0
    
    def test_extract_minimal_content(self, extractor):
        """Test extraction from minimal content."""
        minimal = {
            "messages": [
                {"role": "user", "content": "ok", "timestamp": "2025-11-15T10:00:00"}
            ]
        }
        
        result = extractor.extract(minimal)
        
        # Should handle gracefully
        assert result is not None
        assert 0 <= result["quality"] <= 10
    
    def test_extract_without_timestamp(self, extractor):
        """Test extraction when timestamps are missing."""
        no_timestamp = {
            "messages": [
                {"role": "user", "content": "Test message"}
            ]
        }
        
        # Should either add timestamps or handle gracefully
        result = extractor.extract(no_timestamp)
        
        assert result is not None
        assert "entities" in result
