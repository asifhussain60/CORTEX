"""
Tests for Domain Glossary Generator

Validates domain glossary generation with entities, relationships, and lifecycle tracking.

Author: CORTEX Architect
Phase: Phase 66 S3
"""

import pytest
from pathlib import Path
from typing import List, Dict, Any


class TestGlossaryGenerator:
    """Test suite for domain glossary generation"""
    
    def test_entity_extraction_from_classes(self):
        """Test extracting entities from class definitions"""
        from cortex_lens.domain_inference.glossary_generator import GlossaryGenerator
        
        code = '''
class User(BaseModel):
    """Represents a system user"""
    id: int
    name: str
    email: str
    
class Order(BaseModel):
    """Customer order"""
    id: int
    user_id: int
    total: float
'''
        
        generator = GlossaryGenerator()
        entities = generator.extract_entities(code)
        
        assert len(entities) >= 2
        
        # Check User entity
        user_entity = next(e for e in entities if e["name"] == "User")
        assert "user" in user_entity["description"].lower()
        assert len(user_entity["attributes"]) >= 3
        
        # Check Order entity
        order_entity = next(e for e in entities if e["name"] == "Order")
        assert "order" in order_entity["description"].lower()
    
    def test_relationship_detection(self):
        """Test detecting relationships between entities"""
        from cortex_lens.domain_inference.glossary_generator import GlossaryGenerator
        
        code = '''
class Order(BaseModel):
    user_id: int  # FK to User
    items: List[OrderItem]
'''
        
        generator = GlossaryGenerator()
        relationships = generator.detect_relationships(code)
        
        assert len(relationships) >= 1
        
        # Check for User relationship
        user_rel = next((r for r in relationships if "User" in r["target"]), None)
        assert user_rel is not None
        assert user_rel["type"] in ["has_one", "belongs_to", "references"]
    
    def test_verb_extraction_from_methods(self):
        """Test extracting domain verbs (use cases) from methods"""
        from cortex_lens.domain_inference.glossary_generator import GlossaryGenerator
        
        code = '''
class UserService:
    def create_user(self, data):
        """Create a new user"""
        pass
    
    def authenticate_user(self, credentials):
        """Authenticate user credentials"""
        pass
    
    def deactivate_user(self, user_id):
        """Deactivate user account"""
        pass
'''
        
        generator = GlossaryGenerator()
        verbs = generator.extract_verbs(code)
        
        assert len(verbs) >= 3
        assert any("create" in v["name"].lower() for v in verbs)
        assert any("authenticate" in v["name"].lower() for v in verbs)
        assert any("deactivate" in v["name"].lower() for v in verbs)
    
    def test_lifecycle_stages_detection(self):
        """Test detecting entity lifecycle stages"""
        from cortex_lens.domain_inference.glossary_generator import GlossaryGenerator
        
        # Code with state transitions
        code = '''
class Phase(BaseModel):
    status: PhaseStatus  # planned -> active -> completed
'''
        
        transitions = [
            {"from": "planned", "to": "active"},
            {"from": "active", "to": "completed"}
        ]
        
        generator = GlossaryGenerator()
        lifecycle = generator.build_lifecycle("Phase", transitions)
        
        assert lifecycle["entity"] == "Phase"
        assert len(lifecycle["stages"]) >= 2
        assert "planned" in [s.lower() for s in lifecycle["stages"]]
        assert "completed" in [s.lower() for s in lifecycle["stages"]]
    
    def test_glossary_generation(self):
        """Test generating complete domain glossary"""
        from cortex_lens.domain_inference.glossary_generator import GlossaryGenerator
        
        entities = [
            {"name": "User", "description": "System user", "attributes": ["id", "name"]},
            {"name": "Order", "description": "Customer order", "attributes": ["id", "total"]}
        ]
        
        verbs = [
            {"name": "create_user", "description": "Create new user"},
            {"name": "place_order", "description": "Place new order"}
        ]
        
        rules = [
            {"field": "email", "description": "Must contain @"}
        ]
        
        generator = GlossaryGenerator()
        glossary = generator.generate_glossary(entities, verbs, rules)
        
        assert "entities" in glossary
        assert "verbs" in glossary
        assert "rules" in glossary
        assert len(glossary["entities"]) == 2
        assert len(glossary["verbs"]) == 2
        assert len(glossary["rules"]) == 1
    
    def test_confidence_scoring(self):
        """Test confidence scoring for glossary entries"""
        from cortex_lens.domain_inference.glossary_generator import GlossaryGenerator
        
        # Strong signals: documented, has attributes, has relationships
        strong_entity = {
            "has_docstring": True,
            "attribute_count": 5,
            "relationship_count": 2,
            "has_methods": True
        }
        
        generator = GlossaryGenerator()
        confidence = generator.calculate_confidence(strong_entity)
        
        assert confidence >= 0.8
        
        # Weak signals: no docs, few attributes
        weak_entity = {
            "has_docstring": False,
            "attribute_count": 1,
            "relationship_count": 0,
            "has_methods": False
        }
        
        confidence_weak = generator.calculate_confidence(weak_entity)
        assert confidence_weak < 0.6


class TestGlossaryGeneratorIntegration:
    """Integration tests for glossary generation"""
    
    def test_cortex_glossary_generation(self):
        """Test generating glossary for CORTEX domain"""
        from cortex_lens.domain_inference.glossary_generator import GlossaryGenerator
        from pathlib import Path
        
        generator = GlossaryGenerator()
        
        # Analyze CORTEX models
        models_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex/models")
        if models_path.exists():
            entities_found = []
            
            for py_file in models_path.glob("*.py"):
                content = py_file.read_text()
                entities = generator.extract_entities(content)
                entities_found.extend(entities)
            
            # CORTEX should have identifiable entities
            if entities_found:
                assert len(entities_found) > 0
                # Check for Phase entity (known CORTEX concept)
                assert any("phase" in e["name"].lower() for e in entities_found)
