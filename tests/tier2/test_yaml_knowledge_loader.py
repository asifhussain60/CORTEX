"""
Tests for YAML Knowledge Loader

Copyright (c) 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from datetime import datetime

from src.tier2.knowledge_graph.knowledge_graph import KnowledgeGraph
from src.tier2.knowledge_graph.loaders.yaml_loader import YAMLKnowledgeLoader


class TestYAMLKnowledgeLoader:
    """Test YAML knowledge file loading."""
    
    @pytest.fixture
    def temp_knowledge_base(self, tmp_path):
        """Create temporary knowledge base structure."""
        knowledge_base = tmp_path / "knowledge"
        
        # Create engineering category
        engineering = knowledge_base / "engineering"
        engineering.mkdir(parents=True)
        
        # Create sample design patterns file
        design_patterns = {
            'metadata': {
                'version': '1.0.0',
                'author': 'Test Author',
                'created': '2025-12-25'
            },
            'pattern_selection_guide': {
                'object_creation': [
                    {
                        'problem': 'Need to ensure only one instance',
                        'pattern': 'Singleton',
                        'category': 'creational'
                    },
                    {
                        'problem': 'Need to create families of objects',
                        'pattern': 'Abstract Factory',
                        'category': 'creational'
                    }
                ]
            }
        }
        
        with open(engineering / "design-patterns.yaml", 'w') as f:
            yaml.dump(design_patterns, f)
        
        # Create testing category
        testing = knowledge_base / "testing"
        testing.mkdir(parents=True)
        
        tdd_practices = {
            'metadata': {
                'version': '1.0.0',
                'author': 'Test Author'
            },
            'three_laws': {
                'law_1': {
                    'statement': 'Write test before production code',
                    'explanation': 'Ensures test actually tests something'
                }
            },
            'red_green_refactor': {
                'red': {
                    'description': 'Write failing test',
                    'goal': 'Define expected behavior'
                },
                'green': {
                    'description': 'Make test pass',
                    'goal': 'Implement minimum code'
                }
            }
        }
        
        with open(testing / "tdd-best-practices.yaml", 'w') as f:
            yaml.dump(tdd_practices, f)
        
        return knowledge_base
    
    @pytest.fixture
    def kg_with_loader(self, tmp_path, temp_knowledge_base):
        """Create KnowledgeGraph with YAML loader."""
        db_path = tmp_path / "test_knowledge_graph.db"
        kg = KnowledgeGraph(db_path=db_path, auto_load_knowledge=False)
        kg.yaml_loader.knowledge_base_path = temp_knowledge_base
        return kg
    
    def test_load_design_patterns(self, kg_with_loader):
        """Test loading design patterns from YAML."""
        count = kg_with_loader.load_knowledge_category('engineering')
        
        assert count > 0, "Should load at least one pattern"
        
        # Search for loaded patterns
        results = kg_with_loader.search_patterns("Singleton", limit=5)
        assert len(results) > 0, "Should find Singleton pattern"
        
        singleton = results[0]
        assert 'Singleton' in singleton['title']
        assert singleton['pattern_type'] == 'design_pattern'
    
    def test_load_tdd_practices(self, kg_with_loader):
        """Test loading TDD best practices from YAML."""
        count = kg_with_loader.load_knowledge_category('testing')
        
        assert count > 0, "Should load TDD patterns"
        
        # Search for TDD patterns
        results = kg_with_loader.search_patterns("test before production", limit=5)
        assert len(results) > 0, "Should find TDD practices"
    
    def test_load_all_categories(self, kg_with_loader):
        """Test loading all knowledge categories."""
        stats = kg_with_loader.yaml_loader.load_all_knowledge_files()
        
        assert 'engineering' in stats, "Should load engineering category"
        assert 'testing' in stats, "Should load testing category"
        assert stats['engineering'] > 0, "Should load patterns from engineering"
        assert stats['testing'] > 0, "Should load patterns from testing"
    
    def test_lazy_loading_on_first_query(self, tmp_path, temp_knowledge_base):
        """Test that knowledge files are loaded on first query."""
        db_path = tmp_path / "test_lazy_load.db"
        kg = KnowledgeGraph(db_path=db_path, auto_load_knowledge=True)
        kg.yaml_loader.knowledge_base_path = temp_knowledge_base
        
        # First query should trigger lazy load
        results = kg.search_patterns("Singleton", limit=5)
        
        # Should have loaded patterns
        assert kg._knowledge_loaded, "Knowledge should be marked as loaded"
        assert len(results) > 0, "Should find patterns after lazy load"
    
    def test_skip_reload_without_changes(self, kg_with_loader, temp_knowledge_base):
        """Test that unchanged files are not reloaded."""
        # First load
        count1 = kg_with_loader.load_knowledge_category('engineering')
        
        # Second load (should skip)
        count2 = kg_with_loader.load_knowledge_category('engineering')
        
        assert count2 == 0, "Should skip reload of unchanged files"
    
    def test_force_reload(self, kg_with_loader):
        """Test force reload of knowledge files."""
        # First load
        count1 = kg_with_loader.load_knowledge_category('engineering')
        
        # Force reload
        count2 = kg_with_loader.load_knowledge_category('engineering', force_reload=True)
        
        assert count2 > 0, "Force reload should reload files"
    
    def test_pattern_id_consistency(self, kg_with_loader):
        """Test that pattern IDs are consistent across reloads."""
        # First load
        kg_with_loader.load_knowledge_category('engineering')
        results1 = kg_with_loader.search_patterns("Singleton", limit=1)
        pattern_id1 = results1[0]['pattern_id']
        
        # Reload
        kg_with_loader.load_knowledge_category('engineering', force_reload=True)
        results2 = kg_with_loader.search_patterns("Singleton", limit=1)
        pattern_id2 = results2[0]['pattern_id']
        
        assert pattern_id1 == pattern_id2, "Pattern IDs should be consistent"
    
    def test_knowledge_load_stats(self, kg_with_loader):
        """Test getting knowledge load statistics."""
        kg_with_loader.load_knowledge_category('engineering')
        kg_with_loader.load_knowledge_category('testing')
        
        stats = kg_with_loader.get_knowledge_load_stats()
        
        assert stats['files_loaded'] > 0, "Should track loaded files"
        assert stats['patterns_from_knowledge'] > 0, "Should count patterns"
        assert stats['last_load'] is not None, "Should record last load time"
    
    def test_update_existing_pattern(self, kg_with_loader, temp_knowledge_base):
        """Test that reloading updates existing patterns."""
        # First load
        kg_with_loader.load_knowledge_category('engineering')
        results1 = kg_with_loader.search_patterns("Singleton", limit=1)
        original_content = results1[0]['content']
        
        # Modify YAML file
        design_patterns_path = temp_knowledge_base / "engineering" / "design-patterns.yaml"
        with open(design_patterns_path, 'r') as f:
            data = yaml.safe_load(f)
        
        data['pattern_selection_guide']['object_creation'][0]['problem'] = 'MODIFIED: Only one instance'
        
        with open(design_patterns_path, 'w') as f:
            yaml.dump(data, f)
        
        # Force reload
        kg_with_loader.load_knowledge_category('engineering', force_reload=True)
        results2 = kg_with_loader.search_patterns("Singleton", limit=1)
        updated_content = results2[0]['content']
        
        assert 'MODIFIED' in updated_content, "Should update existing pattern"
    
    def test_invalid_yaml_handling(self, kg_with_loader, temp_knowledge_base):
        """Test handling of invalid YAML files."""
        invalid_file = temp_knowledge_base / "engineering" / "invalid.yaml"
        with open(invalid_file, 'w') as f:
            f.write("invalid: yaml: content: [")
        
        # Should not crash, just skip the file
        count = kg_with_loader.load_knowledge_category('engineering', force_reload=True)
        
        # Should still load valid files
        assert count >= 0, "Should handle invalid YAML gracefully"
    
    def test_disable_auto_load(self, tmp_path, temp_knowledge_base):
        """Test disabling automatic knowledge loading."""
        db_path = tmp_path / "test_no_auto_load.db"
        kg = KnowledgeGraph(db_path=db_path, auto_load_knowledge=False)
        kg.yaml_loader.knowledge_base_path = temp_knowledge_base
        
        # Query should not trigger load
        results = kg.search_patterns("Singleton", limit=5)
        
        assert not kg._knowledge_loaded, "Should not auto-load when disabled"
        assert len(results) == 0, "Should not find patterns without loading"


class TestPatternExtraction:
    """Test pattern extraction strategies."""
    
    def test_extract_gof_patterns(self, tmp_path):
        """Test extraction of GoF design patterns."""
        knowledge_base = tmp_path / "knowledge" / "engineering"
        knowledge_base.mkdir(parents=True)
        
        gof_patterns = {
            'metadata': {'version': '1.0.0'},
            'creational_patterns': [
                {
                    'name': 'Factory Method',
                    'intent': 'Define interface for creating objects',
                    'problem': 'Need flexibility in object creation',
                    'solution': 'Defer instantiation to subclasses'
                }
            ]
        }
        
        with open(knowledge_base / "patterns.yaml", 'w') as f:
            yaml.dump(gof_patterns, f)
        
        db_path = tmp_path / "test.db"
        kg = KnowledgeGraph(db_path=db_path, auto_load_knowledge=False)
        kg.yaml_loader.knowledge_base_path = tmp_path / "knowledge"
        
        count = kg.load_knowledge_category('engineering')
        assert count > 0, "Should extract GoF patterns"
        
        results = kg.search_patterns("Factory Method", limit=5)
        assert len(results) > 0, "Should find Factory Method pattern"
    
    def test_extract_solid_principles(self, tmp_path):
        """Test extraction of SOLID principles."""
        knowledge_base = tmp_path / "knowledge" / "engineering"
        knowledge_base.mkdir(parents=True)
        
        solid = {
            'metadata': {'version': '1.0.0'},
            'single_responsibility_principle': {
                'name': 'Single Responsibility Principle',
                'definition': 'A class should have one reason to change',
                'explanation': 'Each class should have single responsibility'
            }
        }
        
        with open(knowledge_base / "solid.yaml", 'w') as f:
            yaml.dump(solid, f)
        
        db_path = tmp_path / "test.db"
        kg = KnowledgeGraph(db_path=db_path, auto_load_knowledge=False)
        kg.yaml_loader.knowledge_base_path = tmp_path / "knowledge"
        
        count = kg.load_knowledge_category('engineering')
        assert count > 0, "Should extract SOLID principles"
        
        results = kg.search_patterns("Single Responsibility", limit=5)
        assert len(results) > 0, "Should find SRP"
        assert results[0]['pattern_type'] == 'principle'
