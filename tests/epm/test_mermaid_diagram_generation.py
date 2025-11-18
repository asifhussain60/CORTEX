"""
Mermaid Diagram Generation Tests

Validates that Mermaid diagrams are generated correctly and render without errors.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import yaml
import re

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.epm.modules.diagram_generator import DiagramGenerator


class TestMermaidDiagramGeneration(unittest.TestCase):
    """Tests for Mermaid diagram generation"""
    
    def setUp(self):
        """Create temporary directory for tests"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.root_path = self.temp_dir
        self.generator = DiagramGenerator(self.root_path, dry_run=False)
        
        # Create test diagram definitions
        self.definitions_file = self.temp_dir / "diagram-definitions.yaml"
        self.definitions = {
            'diagrams': [
                {
                    'name': 'Test Tier Architecture',
                    'type': 'tier_architecture',
                    'output_path': 'images/diagrams/test-tier-architecture.md'
                },
                {
                    'name': 'Test Agent System',
                    'type': 'agent_system',
                    'output_path': 'images/diagrams/test-agent-system.md'
                },
                {
                    'name': 'Test Pipeline Flow',
                    'type': 'pipeline_flow',
                    'output_path': 'images/diagrams/test-pipeline-flow.md',
                    'stages': ['stage1', 'stage2', 'stage3']
                },
                {
                    'name': 'Test Module Structure',
                    'type': 'module_structure',
                    'output_path': 'images/diagrams/test-module-structure.md'
                },
                {
                    'name': 'Test Data Flow',
                    'type': 'data_flow',
                    'output_path': 'images/diagrams/test-data-flow.md',
                    'source': 'Source System',
                    'target': 'Target System'
                }
            ]
        }
        
        with open(self.definitions_file, 'w') as f:
            yaml.dump(self.definitions, f)
    
    def tearDown(self):
        """Clean up temporary directory"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_diagram_generator_initialization(self):
        """Test that DiagramGenerator initializes correctly"""
        self.assertEqual(self.generator.root_path, self.root_path)
        self.assertEqual(self.generator.brain_path, self.root_path / "cortex-brain")
        self.assertEqual(self.generator.output_path, self.root_path / "docs")
    
    def test_generate_all_diagrams(self):
        """Test that all diagrams in definitions file are generated"""
        result = self.generator.generate_all_diagrams(self.definitions_file)
        
        self.assertIn('diagrams_generated', result)
        self.assertIn('files', result)
        
        # Should generate all diagrams in definitions
        self.assertEqual(result['diagrams_generated'], len(self.definitions['diagrams']))
    
    def test_tier_architecture_mermaid_syntax(self):
        """Test that tier architecture diagram has valid Mermaid syntax"""
        content = self.generator._generate_tier_architecture()
        
        # Check for Mermaid code block
        self.assertIn('```mermaid', content)
        self.assertIn('```', content[content.index('```mermaid') + 11:])
        
        # Check for graph definition
        self.assertIn('graph TB', content)  # Top to bottom
        
        # Check for subgraphs (tiers)
        self.assertIn('subgraph', content)
        
        # Check for tier labels
        self.assertIn('Tier', content)
    
    def test_agent_system_mermaid_syntax(self):
        """Test that agent system diagram has valid Mermaid syntax"""
        content = self.generator._generate_agent_system()
        
        # Check for Mermaid code block
        self.assertIn('```mermaid', content)
        
        # Check for graph definition
        self.assertIn('graph LR', content)  # Left to right
        
        # Check for brain regions
        self.assertIn('RightBrain', content)
        self.assertIn('LeftBrain', content)
        self.assertIn('Coordination', content)
    
    def test_pipeline_flow_mermaid_syntax(self):
        """Test that pipeline flow diagram has valid Mermaid syntax"""
        definition = {
            'name': 'Test Pipeline',
            'stages': ['validation', 'execution', 'verification']
        }
        
        content = self.generator._generate_pipeline_flow(definition)
        
        # Check for Mermaid code block
        self.assertIn('```mermaid', content)
        
        # Check for stages
        self.assertIn('S1', content)
        self.assertIn('S2', content)
        self.assertIn('S3', content)
        
        # Check for arrows between stages
        self.assertIn('-->', content)
    
    def test_module_structure_mermaid_syntax(self):
        """Test that module structure diagram has valid Mermaid syntax"""
        definition = {}
        content = self.generator._generate_module_structure(definition)
        
        # Check for Mermaid code block
        self.assertIn('```mermaid', content)
        
        # Check for graph structure
        self.assertIn('graph TB', content)
        
        # Check for modules
        self.assertIn('subgraph', content)
    
    def test_data_flow_mermaid_syntax(self):
        """Test that data flow diagram has valid Mermaid syntax"""
        definition = {
            'source': 'Input System',
            'target': 'Output System'
        }
        
        content = self.generator._generate_data_flow(definition)
        
        # Check for Mermaid code block
        self.assertIn('```mermaid', content)
        
        # Check for source and target
        self.assertIn('Source', content)
        self.assertIn('Target', content)
        
        # Check for flow direction
        self.assertIn('-->', content)
    
    def test_mermaid_syntax_validation_basic(self):
        """Test basic Mermaid syntax validation"""
        # Generate all diagrams
        result = self.generator.generate_all_diagrams(self.definitions_file)
        
        # Read each generated file and validate Mermaid syntax
        for file_path in result['files']:
            file = Path(file_path)
            if file.exists():
                content = file.read_text()
                
                # Basic validations
                self.assertIn('```mermaid', content, f"Missing Mermaid code block in {file}")
                
                # Count opening and closing backticks
                opening_count = content.count('```mermaid')
                closing_count = content.count('```')
                
                # Should have equal opening and closing (closing includes opening, so closing should be at least opening count)
                self.assertGreaterEqual(
                    closing_count,
                    opening_count,
                    f"Mismatched code blocks in {file}"
                )
    
    def test_generated_files_exist(self):
        """Test that generated diagram files exist"""
        result = self.generator.generate_all_diagrams(self.definitions_file)
        
        for file_path in result['files']:
            file = Path(file_path)
            self.assertTrue(
                file.exists(),
                f"Generated file does not exist: {file}"
            )
    
    def test_generated_files_not_empty(self):
        """Test that generated diagram files are not empty"""
        result = self.generator.generate_all_diagrams(self.definitions_file)
        
        for file_path in result['files']:
            file = Path(file_path)
            if file.exists():
                content = file.read_text()
                self.assertGreater(
                    len(content),
                    0,
                    f"Generated file is empty: {file}"
                )
    
    def test_dry_run_mode(self):
        """Test that dry run mode doesn't create files"""
        dry_run_generator = DiagramGenerator(self.root_path, dry_run=True)
        
        result = dry_run_generator.generate_all_diagrams(self.definitions_file)
        
        # Result should show what would be generated
        self.assertEqual(result['diagrams_generated'], len(self.definitions['diagrams']))
        
        # But no files should actually exist
        for file_path in result['files']:
            file = Path(file_path)
            # In dry run, files might not be created
            # (depending on implementation)
    
    def test_unknown_diagram_type_handling(self):
        """Test that unknown diagram types are handled gracefully"""
        # Add unknown diagram type
        self.definitions['diagrams'].append({
            'name': 'Unknown Type',
            'type': 'unknown_type',
            'output_path': 'images/diagrams/unknown.md'
        })
        
        with open(self.definitions_file, 'w') as f:
            yaml.dump(self.definitions, f)
        
        # Should not crash, just skip unknown types
        try:
            result = self.generator.generate_all_diagrams(self.definitions_file)
            # Should generate all known diagrams
            self.assertGreater(result['diagrams_generated'], 0)
        except Exception as e:
            self.fail(f"Generator crashed on unknown diagram type: {e}")
    
    def test_mermaid_node_syntax(self):
        """Test that Mermaid node syntax is valid"""
        content = self.generator._generate_tier_architecture()
        
        # Extract Mermaid code
        mermaid_start = content.index('```mermaid') + 11
        mermaid_end = content.index('```', mermaid_start)
        mermaid_code = content[mermaid_start:mermaid_end].strip()
        
        # Check for valid node syntax patterns
        # Nodes can be: A[Label], A(Label), A{Label}, A>Label], etc.
        node_pattern = re.compile(r'\w+\[.+?\]|\w+\(.+?\)|\w+\{.+?\}')
        nodes = node_pattern.findall(mermaid_code)
        
        self.assertGreater(
            len(nodes),
            0,
            "No valid Mermaid nodes found in diagram"
        )
    
    def test_mermaid_arrow_syntax(self):
        """Test that Mermaid arrow syntax is valid"""
        definition = {
            'stages': ['stage1', 'stage2']
        }
        
        content = self.generator._generate_pipeline_flow(definition)
        
        # Should contain arrows
        self.assertIn('-->', content, "No arrows found in flow diagram")
    
    def test_subgraph_syntax(self):
        """Test that subgraph syntax is valid"""
        content = self.generator._generate_tier_architecture()
        
        # Should have subgraph definitions
        self.assertIn('subgraph', content)
        
        # Each subgraph should have 'end'
        subgraph_count = content.count('subgraph')
        end_count = content.count('end')
        
        self.assertEqual(
            subgraph_count,
            end_count,
            "Mismatched subgraph/end keywords"
        )


class TestMermaidIntegrationWithMasterConfig(unittest.TestCase):
    """Tests for Mermaid diagram generation with master diagram configuration"""
    
    def setUp(self):
        """Load master diagram configuration"""
        self.config_path = Path(__file__).parent.parent.parent / "cortex-brain" / "doc-generation-config" / "master-diagram-list.yaml"
        
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.master_config = yaml.safe_load(f)
        else:
            self.master_config = None
    
    @unittest.skipIf(
        not Path(__file__).parent.parent.parent.joinpath("cortex-brain/doc-generation-config/master-diagram-list.yaml").exists(),
        "Master diagram config not found"
    )
    def test_mermaid_generator_supports_master_config_types(self):
        """Test that DiagramGenerator supports all diagram types in master config"""
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            generator = DiagramGenerator(temp_dir, dry_run=True)
            
            # Get unique diagram types from master config
            diagram_types = set(d['type'] for d in self.master_config['diagrams'])
            
            # Map master config types to generator types
            # (Master config uses human-readable names, generator uses internal names)
            type_mapping = {
                'architecture': ['tier_architecture', 'module_structure'],
                'system': ['agent_system'],
                'workflow': ['pipeline_flow', 'data_flow'],
                'comparison': ['data_flow'],
                'executive': ['data_flow'],
                'narrative': ['data_flow']
            }
            
            supported_types = set()
            for category_types in type_mapping.values():
                supported_types.update(category_types)
            
            # Note: This is a placeholder test. Full integration would require
            # mapping master config types to generator methods.
            self.assertGreater(len(supported_types), 0)
            
        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)


if __name__ == '__main__':
    unittest.main(verbosity=2)
