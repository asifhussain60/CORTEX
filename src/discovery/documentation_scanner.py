"""
Documentation Scanner - Convention-Based Discovery

Discovers and validates all CORTEX documentation:
- Parses .github/prompts/CORTEX.prompt.md for module references
- Scans .github/prompts/modules/*.md for feature guides
- Validates #file: references are not broken
- Cross-references orchestrators with documentation

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Set

logger = logging.getLogger(__name__)


class DocumentationScanner:
    """
    Convention-based documentation discovery.
    
    Scans prompts directory for all documentation and validates
    completeness and cross-references.
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize documentation scanner.
        
        Args:
            project_root: Root directory of CORTEX project
        """
        self.project_root = Path(project_root)
        self.prompts_dir = self.project_root / ".github" / "prompts"
        self.main_prompt = self.prompts_dir / "CORTEX.prompt.md"
        self.modules_dir = self.prompts_dir / "modules"
    
    def discover(self) -> Dict[str, Dict[str, Any]]:
        """
        Discover all documentation files.
        
        Returns:
            Dict mapping documentation file to metadata:
            {
                "CORTEX.prompt.md": {
                    "path": Path(...),
                    "type": "main",
                    "file_references": ["modules/tdd-guide.md", ...],
                    "broken_references": [],
                    "features_documented": ["TDD Workflow", ...]
                },
                "modules/tdd-guide.md": {
                    "path": Path(...),
                    "type": "module",
                    "references_from_main": True
                }
            }
        """
        docs = {}
        
        # Scan main prompt
        if self.main_prompt.exists():
            docs["CORTEX.prompt.md"] = self._scan_main_prompt()
        
        # Scan module documentation
        if self.modules_dir.exists():
            for doc_file in self.modules_dir.glob("*.md"):
                rel_path = doc_file.relative_to(self.prompts_dir)
                docs[str(rel_path)] = self._scan_module_doc(doc_file)
        
        logger.info(f"Discovered {len(docs)} documentation files")
        return docs
    
    def _scan_main_prompt(self) -> Dict[str, Any]:
        """
        Scan main CORTEX.prompt.md file.
        
        Returns:
            Metadata dictionary
        """
        try:
            with open(self.main_prompt, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Extract #file: references
            file_refs = re.findall(r'#file:([^\s\)]+)', content)
            
            # Check for broken references
            broken_refs = []
            for ref in file_refs:
                ref_path = self.prompts_dir / ref
                if not ref_path.exists():
                    broken_refs.append(ref)
            
            # Extract feature sections (## headers)
            features = re.findall(r'^## (.+)$', content, re.MULTILINE)
            
            return {
                "path": self.main_prompt,
                "type": "main",
                "file_references": file_refs,
                "broken_references": broken_refs,
                "features_documented": features
            }
        
        except Exception as e:
            logger.error(f"Failed to scan main prompt: {e}")
            return {"error": str(e)}
    
    def _scan_module_doc(self, doc_path: Path) -> Dict[str, Any]:
        """
        Scan module documentation file.
        
        Args:
            doc_path: Path to module documentation
        
        Returns:
            Metadata dictionary
        """
        return {
            "path": doc_path,
            "type": "module",
            "size_bytes": doc_path.stat().st_size
        }
    
    def validate_orchestrator_coverage(
        self,
        discovered_orchestrators: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """
        Validate all orchestrators have documentation.
        
        Args:
            discovered_orchestrators: Dict of discovered orchestrators
        
        Returns:
            List of undocumented orchestrator names
        """
        docs = self.discover()
        main_doc = docs.get("CORTEX.prompt.md", {})
        features_documented = main_doc.get("features_documented", [])
        
        # Convert to lowercase for matching
        documented_lower = {f.lower() for f in features_documented}
        
        undocumented = []
        for orchestrator_name in discovered_orchestrators.keys():
            # Skip admin-only orchestrators
            if "admin" in orchestrator_name.lower():
                continue
            
            # Check if mentioned in documentation
            name_parts = re.findall(r'[A-Z][a-z]+', orchestrator_name)
            
            found = any(
                part.lower() in documented_lower
                for part in name_parts
            )
            
            if not found:
                undocumented.append(orchestrator_name)
        
        return undocumented
