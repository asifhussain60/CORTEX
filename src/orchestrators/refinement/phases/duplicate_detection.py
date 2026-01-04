"""
Phase 2: Duplicate Detection

AST-based duplicate code detection and consolidation suggestions.

Author: Asif Hussain
Created: January 3, 2026
"""

import ast
import hashlib
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)


class DuplicateDetectionPhase:
    """Phase 2: Detect duplicate code blocks."""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.target_path = orchestrator.target_path
        self.min_similarity = 0.8  # 80% similarity threshold
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute duplicate detection.
        
        Returns:
            Dictionary containing duplicate blocks and consolidation suggestions
        """
        logger.info("Phase 2: Starting duplicate detection")
        
        results = {
            "duplicates_found": 0,
            "duplicate_groups": [],
            "consolidation_suggestions": [],
            "estimated_savings": {"lines": 0, "files": 0}
        }
        
        try:
            files = self._get_python_files()
            
            # Extract code blocks from all files
            all_blocks = []
            for file_path in files:
                blocks = self._extract_code_blocks(file_path)
                all_blocks.extend(blocks)
            
            # Find duplicates
            duplicate_groups = self._find_duplicates(all_blocks)
            results["duplicate_groups"] = duplicate_groups
            results["duplicates_found"] = len(duplicate_groups)
            
            # Generate consolidation suggestions
            for group in duplicate_groups:
                suggestion = self._generate_consolidation_suggestion(group)
                results["consolidation_suggestions"].append(suggestion)
            
            # Calculate savings
            results["estimated_savings"] = self._calculate_savings(duplicate_groups)
            
            logger.info(f"Duplicate detection complete: {results['duplicates_found']} "
                       f"duplicate groups found")
            
        except Exception as e:
            logger.error(f"Duplicate detection failed: {e}", exc_info=True)
            results["error"] = str(e)
        
        return results
    
    def _get_python_files(self) -> List[Path]:
        """Get list of Python files to analyze."""
        if self.target_path.is_file():
            return [self.target_path]
        
        python_files = list(self.target_path.rglob("*.py"))
        excluded = ["__pycache__", ".venv", "venv", "migrations", ".git"]
        return [f for f in python_files if not any(ex in str(f) for ex in excluded)]
    
    def _extract_code_blocks(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract significant code blocks from a file."""
        blocks = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Extract functions
                if isinstance(node, ast.FunctionDef):
                    block = {
                        "type": "function",
                        "name": node.name,
                        "file": str(file_path),
                        "line": node.lineno,
                        "code": ast.get_source_segment(content, node),
                        "hash": self._hash_node(node),
                        "size": len(node.body)
                    }
                    blocks.append(block)
                
                # Extract classes
                elif isinstance(node, ast.ClassDef):
                    block = {
                        "type": "class",
                        "name": node.name,
                        "file": str(file_path),
                        "line": node.lineno,
                        "code": ast.get_source_segment(content, node),
                        "hash": self._hash_node(node),
                        "size": len(node.body)
                    }
                    blocks.append(block)
        
        except Exception as e:
            logger.debug(f"Failed to extract blocks from {file_path}: {e}")
        
        return blocks
    
    def _hash_node(self, node: ast.AST) -> str:
        """Generate hash of AST node structure (ignoring variable names)."""
        # Simplified hash based on node types
        node_types = []
        for n in ast.walk(node):
            node_types.append(type(n).__name__)
        
        structure = "-".join(node_types)
        return hashlib.md5(structure.encode()).hexdigest()
    
    def _find_duplicates(self, blocks: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Find duplicate code blocks."""
        # Group blocks by hash
        hash_groups = defaultdict(list)
        for block in blocks:
            if block["size"] >= 3:  # Minimum size threshold
                hash_groups[block["hash"]].append(block)
        
        # Filter to groups with duplicates
        duplicate_groups = [
            group for group in hash_groups.values()
            if len(group) > 1
        ]
        
        return duplicate_groups
    
    def _generate_consolidation_suggestion(self, group: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate suggestion for consolidating duplicate code."""
        first_block = group[0]
        
        # Determine best location for consolidated function
        files = [block["file"] for block in group]
        file_counts = defaultdict(int)
        for f in files:
            file_counts[f] += 1
        
        suggested_location = max(file_counts.items(), key=lambda x: x[1])[0]
        
        suggestion = {
            "duplicate_count": len(group),
            "block_type": first_block["type"],
            "suggested_name": f"consolidated_{first_block['name']}",
            "suggested_location": suggested_location,
            "occurrences": [
                {"file": block["file"], "line": block["line"]}
                for block in group
            ],
            "refactoring_steps": [
                f"1. Create consolidated function in {suggested_location}",
                f"2. Replace {len(group)} occurrences with function call",
                "3. Add tests for consolidated function",
                "4. Validate all call sites work correctly"
            ]
        }
        
        return suggestion
    
    def _calculate_savings(self, duplicate_groups: List[List[Dict[str, Any]]]) -> Dict[str, int]:
        """Calculate estimated code savings from removing duplicates."""
        total_lines = 0
        affected_files = set()
        
        for group in duplicate_groups:
            # Estimate lines saved (all but one instance)
            avg_size = sum(block["size"] for block in group) / len(group)
            total_lines += int(avg_size * (len(group) - 1))
            
            # Track files
            for block in group:
                affected_files.add(block["file"])
        
        return {
            "lines": total_lines,
            "files": len(affected_files)
        }
