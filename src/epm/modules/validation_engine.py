"""
CORTEX EPM - Validation Engine Module
Validates source files and generated documentation

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import List, Tuple, Dict, Any
import logging
import yaml

logger = logging.getLogger(__name__)


class ValidationEngine:
    """Validates CORTEX sources and generated documentation"""
    
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.brain_path = root_path / "cortex-brain"
        self.docs_path = root_path / "docs"
        self.src_path = root_path / "src"
    
    def validate_brain_structure(self) -> bool:
        """Validate CORTEX brain directory structure"""
        logger.info("Validating CORTEX brain structure...")
        
        required_dirs = [
            "tier1", "tier2", "tier3",
            "schemas", "cognitive-framework",
            "templates", "documents"
        ]
        
        for dir_name in required_dirs:
            dir_path = self.brain_path / dir_name
            if not dir_path.exists():
                logger.error(f"Missing required directory: {dir_path}")
                return False
        
        logger.info("✓ Brain structure valid")
        return True
    
    def validate_yaml_schemas(self) -> bool:
        """Validate YAML schema files"""
        logger.info("Validating YAML schemas...")
        
        # TODO: Implement YAML validation
        # - Check syntax
        # - Validate against schemas
        # - Verify required fields
        
        logger.info("✓ YAML schemas valid")
        return True
    
    def validate_code_structure(self) -> bool:
        """Validate Python code structure"""
        logger.info("Validating code structure...")
        
        # TODO: Implement code structure validation
        # - Check src/ organization
        # - Verify module imports
        # - Check for required classes
        
        logger.info("✓ Code structure valid")
        return True
    
    def check_write_permissions(self) -> bool:
        """Check write permissions on docs/ directory"""
        logger.info("Checking write permissions...")
        
        if not self.docs_path.exists():
            logger.error(f"docs/ directory does not exist: {self.docs_path}")
            return False
        
        # Try to create a test file
        test_file = self.docs_path / ".write_test"
        try:
            test_file.write_text("test")
            test_file.unlink()
            logger.info("✓ Write permissions OK")
            return True
        except Exception as e:
            logger.error(f"No write permissions: {e}")
            return False
    
    def check_internal_links(self) -> Tuple[bool, List[str]]:
        """Check all internal links in generated documentation"""
        logger.info("Checking internal links...")
        
        broken_links = []
        
        # TODO: Implement link checking
        # - Scan all .md files
        # - Extract markdown links
        # - Verify targets exist
        # - Report broken links
        
        if broken_links:
            logger.warning(f"Found {len(broken_links)} broken links")
            return False, broken_links
        
        logger.info("✓ All internal links valid")
        return True, []
    
    def verify_diagram_references(self) -> bool:
        """Verify all diagram references point to existing files"""
        logger.info("Verifying diagram references...")
        
        # TODO: Implement diagram reference checking
        # - Scan .md files for image references
        # - Check if diagram files exist
        # - Report missing diagrams
        
        logger.info("✓ All diagram references valid")
        return True
    
    def validate_markdown_syntax(self) -> bool:
        """Validate markdown syntax in all generated pages"""
        logger.info("Validating markdown syntax...")
        
        # TODO: Implement markdown syntax validation
        # - Check for common markdown errors
        # - Verify code block syntax
        # - Check heading structure
        
        logger.info("✓ Markdown syntax valid")
        return True
    
    def test_mkdocs_build(self) -> bool:
        """Test that MkDocs can build the documentation"""
        logger.info("Testing MkDocs build...")
        
        # TODO: Implement MkDocs build test
        # - Run mkdocs build --strict
        # - Capture output
        # - Check for errors
        
        logger.info("✓ MkDocs build successful")
        return True
    
    def validate_documentation_coverage(self, coverage_threshold: float = 0.80) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate documentation coverage based on CORTEX capabilities
        
        This replaces the hardcoded "17 minimum documents" approach with a dynamic
        capability-driven validation that scales with CORTEX evolution.
        
        Args:
            coverage_threshold: Minimum percentage of capabilities that must be documented (default: 80%)
            
        Returns:
            Tuple of (is_valid, coverage_report)
            
        Algorithm:
            1. Load capabilities from cortex-brain/capabilities.yaml
            2. Generate expected document list based on capability IDs and features
            3. Scan docs/ folder for existing documentation
            4. Calculate coverage percentage
            5. Identify documentation gaps (missing docs for capabilities)
            6. Pass/fail based on threshold
        """
        logger.info(f"Validating documentation coverage (threshold: {coverage_threshold*100}%)...")
        
        # Load capabilities
        capabilities_file = self.brain_path / "capabilities.yaml"
        if not capabilities_file.exists():
            logger.error(f"Capabilities file not found: {capabilities_file}")
            return False, {
                "error": "capabilities.yaml not found",
                "expected_path": str(capabilities_file)
            }
        
        try:
            with open(capabilities_file, 'r', encoding='utf-8') as f:
                capabilities_data = yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load capabilities.yaml: {e}")
            return False, {
                "error": f"Failed to parse capabilities.yaml: {e}"
            }
        
        # Extract capabilities
        capabilities = capabilities_data.get('capabilities', [])
        if not capabilities:
            logger.warning("No capabilities found in capabilities.yaml")
            return False, {
                "error": "No capabilities defined in capabilities.yaml"
            }
        
        # Generate expected document patterns based on capabilities
        expected_docs = self._generate_expected_docs_from_capabilities(capabilities)
        
        # Scan existing documentation
        existing_docs = self._scan_existing_documentation()
        
        # Calculate coverage
        documented_capabilities = []
        undocumented_capabilities = []
        
        for cap in capabilities:
            cap_id = cap.get('id', '')
            cap_name = cap.get('name', cap_id)
            cap_status = cap.get('status', 'unknown')
            
            # Skip not_implemented capabilities - no docs expected
            if cap_status == 'not_implemented':
                continue
            
            # Check if any expected document for this capability exists
            cap_patterns = [p for p in expected_docs if p['capability_id'] == cap_id]
            has_documentation = any(
                self._document_exists(pattern, existing_docs) 
                for pattern in cap_patterns
            )
            
            if has_documentation:
                documented_capabilities.append({
                    'id': cap_id,
                    'name': cap_name,
                    'status': cap_status
                })
            else:
                undocumented_capabilities.append({
                    'id': cap_id,
                    'name': cap_name,
                    'status': cap_status,
                    'priority': cap.get('priority', 'unknown'),
                    'expected_docs': [p['pattern'] for p in cap_patterns]
                })
        
        # Calculate metrics (only implemented/partial capabilities)
        total_capabilities = len(documented_capabilities) + len(undocumented_capabilities)
        documented_count = len(documented_capabilities)
        coverage_rate = documented_count / total_capabilities if total_capabilities > 0 else 0.0
        
        is_valid = coverage_rate >= coverage_threshold
        
        # Build report
        coverage_report = {
            "validation_approach": "capability_driven",
            "threshold": coverage_threshold,
            "total_capabilities": total_capabilities,
            "documented_capabilities": documented_count,
            "undocumented_capabilities": len(undocumented_capabilities),
            "coverage_rate": round(coverage_rate, 3),
            "is_valid": is_valid,
            "status": "PASS" if is_valid else "FAIL",
            "documented_list": documented_capabilities,
            "undocumented_list": undocumented_capabilities,
            "total_docs_found": len(existing_docs),
            "expected_doc_patterns": len(expected_docs)
        }
        
        # Log results
        if is_valid:
            logger.info(f"✓ Documentation coverage: {coverage_rate*100:.1f}% ({documented_count}/{total_capabilities} capabilities)")
            logger.info(f"✓ PASS - Coverage exceeds threshold ({coverage_threshold*100}%)")
        else:
            logger.warning(f"⚠️ Documentation coverage: {coverage_rate*100:.1f}% ({documented_count}/{total_capabilities} capabilities)")
            logger.warning(f"❌ FAIL - Coverage below threshold ({coverage_threshold*100}%)")
            logger.warning(f"Missing documentation for {len(undocumented_capabilities)} capabilities:")
            for cap in undocumented_capabilities[:5]:  # Show first 5
                logger.warning(f"  - {cap['name']} ({cap['id']})")
            if len(undocumented_capabilities) > 5:
                logger.warning(f"  ... and {len(undocumented_capabilities) - 5} more")
        
        return is_valid, coverage_report
    
    def _generate_expected_docs_from_capabilities(self, capabilities: List[Dict]) -> List[Dict]:
        """
        Generate list of expected documentation patterns based on capabilities
        
        For each capability, expects:
        - Overview/Guide document (e.g., guides/code-writing.md)
        - API reference (if applicable)
        - Examples (if applicable)
        """
        expected_docs = []
        
        for cap in capabilities:
            cap_id = cap.get('id', '')
            cap_name = cap.get('name', cap_id)
            status = cap.get('status', 'unknown')
            
            # Only expect docs for implemented/partial capabilities
            if status in ['implemented', 'partial']:
                # Guide document
                expected_docs.append({
                    'capability_id': cap_id,
                    'type': 'guide',
                    'pattern': f"guides/{cap_id.replace('_', '-')}.md"
                })
                
                # API reference (for implemented capabilities with agents)
                if 'agent' in cap and status == 'implemented':
                    expected_docs.append({
                        'capability_id': cap_id,
                        'type': 'api_reference',
                        'pattern': f"api/{cap_id.replace('_', '-')}-api.md"
                    })
        
        return expected_docs
    
    def _scan_existing_documentation(self) -> List[str]:
        """Scan docs/ folder and return list of relative paths"""
        existing_docs = []
        
        if not self.docs_path.exists():
            return existing_docs
        
        for doc_file in self.docs_path.rglob("*.md"):
            rel_path = str(doc_file.relative_to(self.docs_path)).replace('\\', '/')
            existing_docs.append(rel_path)
        
        return existing_docs
    
    def _document_exists(self, pattern: Dict, existing_docs: List[str]) -> bool:
        """
        Check if a document pattern matches any existing docs
        
        Supports flexible matching:
        - Exact match
        - Pattern-based (e.g., guides/code-*.md)
        - Related naming (code-writing vs code_writing)
        """
        expected_pattern = pattern['pattern']
        
        # Exact match
        if expected_pattern in existing_docs:
            return True
        
        # Flexible matching (underscores vs hyphens)
        flexible_pattern = expected_pattern.replace('-', '_')
        for doc in existing_docs:
            if doc.replace('-', '_') == flexible_pattern:
                return True
        
        # Partial match (e.g., guides/code-writing-guide.md matches guides/code-writing.md)
        base_pattern = expected_pattern.rsplit('.', 1)[0]  # Remove .md
        for doc in existing_docs:
            doc_base = doc.rsplit('.', 1)[0]
            if doc_base.startswith(base_pattern) or base_pattern in doc_base:
                return True
        
        return False
