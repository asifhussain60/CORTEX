"""
CORTEX Documentation Freshness Tests

Validates documentation reflects current codebase state with no stale references.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
import re
import yaml


class TestStalenessDetection:
    """Test suite for stale content detection"""
    
    @pytest.fixture
    def docs_dir(self):
        """Get docs directory path"""
        return Path(__file__).parent.parent.parent / "docs"
    
    @pytest.fixture
    def cortex_brain_dir(self):
        """Get cortex-brain directory path"""
        return Path(__file__).parent.parent.parent / "cortex-brain"
    
    @pytest.fixture
    def src_dir(self):
        """Get src directory path"""
        return Path(__file__).parent.parent.parent / "src"
    
    def test_no_deprecated_feature_references(self, docs_dir):
        """Documentation should not reference deprecated features"""
        deprecated_markers = [
            r'\bDEPRECATED\b',
            r'\bOBSOLETE\b',
            r'\bREMOVED\b',
            r'\bNO LONGER SUPPORTED\b',
        ]
        
        violations = []
        
        for md_file in docs_dir.rglob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            
            for pattern in deprecated_markers:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    violations.append(f"{md_file.name}: Found deprecated marker '{matches[0]}'")
        
        assert len(violations) == 0, \
            f"Found deprecated feature references:\n" + "\n".join(violations)
    
    def test_no_todo_placeholders(self, docs_dir):
        """Production docs should not contain TODO placeholders"""
        todo_patterns = [
            r'\bTODO\b',
            r'\bTBD\b',
            r'\bFIXME\b',
            r'\[Coming Soon\]',
            r'\[Under Development\]',
        ]
        
        violations = []
        
        for md_file in docs_dir.rglob("*.md"):
            # Skip known planning/draft documents
            if "planning" in str(md_file) or "draft" in md_file.name.lower():
                continue
            
            content = md_file.read_text(encoding='utf-8')
            
            for pattern in todo_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    violations.append(f"{md_file.name}: Found TODO placeholder '{matches[0]}'")
        
        assert len(violations) == 0, \
            f"Found TODO placeholders in production docs:\n" + "\n".join(violations)
    
    def test_module_references_valid(self, docs_dir, cortex_brain_dir):
        """Referenced modules should exist in cortex-operations.yaml"""
        operations_file = cortex_brain_dir / "cortex-operations.yaml"
        
        if not operations_file.exists():
            pytest.skip("cortex-operations.yaml not found")
        
        with open(operations_file, 'r', encoding='utf-8') as f:
            operations = yaml.safe_load(f)
        
        # Extract valid operation names
        valid_operations = set(operations.get('operations', {}).keys())
        
        # Scan documentation for operation references
        violations = []
        operation_pattern = re.compile(r'`([a-z_]+)`\s+operation', re.IGNORECASE)
        
        for md_file in docs_dir.rglob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            
            referenced_ops = operation_pattern.findall(content)
            for op in referenced_ops:
                if op not in valid_operations:
                    violations.append(f"{md_file.name}: References non-existent operation '{op}'")
        
        assert len(violations) == 0, \
            f"Found invalid operation references:\n" + "\n".join(violations)
    
    def test_file_path_references_valid(self, docs_dir, src_dir, cortex_brain_dir):
        """Referenced file paths should exist"""
        violations = []
        
        # Pattern to match file paths in code blocks or inline code
        file_path_pattern = re.compile(r'`([a-zA-Z0-9_/.-]+\.(py|yaml|md|json))`')
        
        for md_file in docs_dir.rglob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            
            referenced_files = file_path_pattern.findall(content)
            for file_path, _ in referenced_files:
                # Normalize path
                file_path = file_path.replace('/', '\\')
                
                # Check multiple possible locations
                possible_paths = [
                    Path(__file__).parent.parent.parent / file_path,
                    src_dir / file_path,
                    cortex_brain_dir / file_path,
                ]
                
                exists = any(p.exists() for p in possible_paths)
                
                if not exists and not self._is_example_path(file_path):
                    violations.append(f"{md_file.name}: References non-existent file '{file_path}'")
        
        assert len(violations) == 0, \
            f"Found invalid file path references:\n" + "\n".join(violations)
    
    def _is_example_path(self, path):
        """Check if path is an example/placeholder"""
        example_markers = [
            'example',
            'sample',
            'your-',
            '<',
            '>',
            'path/to/',
        ]
        return any(marker in path.lower() for marker in example_markers)


class TestFreshnessScore:
    """Calculate documentation freshness score"""
    
    def test_freshness_score_target(self):
        """Freshness score should be ≥95%"""
        # This would integrate with the actual freshness analysis from Phase 0
        # For now, this is a placeholder
        pytest.skip("Freshness score calculation requires Phase 0 implementation")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
