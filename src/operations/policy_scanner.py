"""
Policy Scanner - Multi-format policy document detection and parsing

**Purpose:** Detect and parse policy documents from common locations in user repositories
**Supports:** YAML, JSON, Markdown formats
**Graceful Handling:** Works whether policies exist or not

**Author:** Asif Hussain
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.
**License:** Source-Available (Use Allowed, No Contributions)
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Optional: Document converter for Word/PDF support
try:
    from src.utils.document_converter import DocumentConverter
    CONVERTER_AVAILABLE = True
except ImportError:
    CONVERTER_AVAILABLE = False


class PolicyFormat(Enum):
    """Supported policy document formats"""
    YAML = "yaml"
    JSON = "json"
    MARKDOWN = "markdown"
    UNKNOWN = "unknown"


@dataclass
class PolicyDocument:
    """Represents a detected policy document"""
    path: Path
    format: PolicyFormat
    content: Dict[str, Any]
    categories: List[str]  # naming, security, standards, architecture
    
    def __post_init__(self):
        """Validate policy document structure"""
        if not self.path.exists():
            raise ValueError(f"Policy document does not exist: {self.path}")


class PolicyScanner:
    """
    Scans repository for policy documents in multiple formats
    
    **Search Locations:**
    1. .github/policies/ (GitHub convention)
    2. docs/policies/ (Documentation folder)
    3. policies/ (Root policies folder)
    4. POLICIES.md / POLICIES.yaml / POLICIES.json (Root files)
    
    **Supported Formats:**
    - YAML (.yaml, .yml)
    - JSON (.json)
    - Markdown (.md) - Parses structured sections
    """
    
    def __init__(self, repo_root: Path):
        """
        Initialize policy scanner
        
        Args:
            repo_root: Root directory of user repository
        """
        self.repo_root = Path(repo_root)
        
        # Initialize document converter if available
        self.converter = DocumentConverter() if CONVERTER_AVAILABLE else None
        
        # Policy file locations (supports YAML, JSON, Markdown, Word, PDF)
        self.policy_locations = [
            self.repo_root / ".github" / "policies",
            self.repo_root / "docs" / "policies",
            self.repo_root / "policies",
            self.repo_root / "POLICIES.yaml",
            self.repo_root / "POLICIES.yml",
            self.repo_root / "POLICIES.json",
            self.repo_root / "POLICIES.md",
            # Word/PDF support (if converter available)
            self.repo_root / "POLICIES.docx",
            self.repo_root / "POLICIES.doc",
            self.repo_root / "POLICIES.pdf"
        ]
    
    def scan_for_policies(self) -> List[PolicyDocument]:
        """
        Scan all common locations for policy documents
        
        Returns:
            List of detected PolicyDocument objects (empty if none found)
        """
        detected_policies = []
        
        for location in self.policy_locations:
            if not location.exists():
                continue
            
            if location.is_file():
                # Single policy file
                policy = self._parse_policy_file(location)
                if policy:
                    detected_policies.append(policy)
            elif location.is_dir():
                # Directory of policy files
                for policy_file in location.glob("*"):
                    if policy_file.is_file() and self._is_policy_file(policy_file):
                        policy = self._parse_policy_file(policy_file)
                        if policy:
                            detected_policies.append(policy)
        
        return detected_policies
    
    def _is_policy_file(self, path: Path) -> bool:
        """Check if file is a supported policy format"""
        supported_formats = ['.yaml', '.yml', '.json', '.md']
        
        # Add Word/PDF if converter available
        if self.converter:
            supported_formats.extend(['.docx', '.doc', '.pdf'])
        
        return path.suffix.lower() in supported_formats
    
    def _parse_policy_file(self, path: Path) -> Optional[PolicyDocument]:
        """
        Parse policy file based on format
        
        Args:
            path: Path to policy file
            
        Returns:
            PolicyDocument if parsing succeeds, None if fails
        """
        try:
            # Convert Word/PDF to Markdown first if needed
            if path.suffix.lower() in ['.docx', '.doc', '.pdf']:
                if not self.converter:
                    print(f"⚠️  Word/PDF converter not available for {path}")
                    print("   Install: pip install python-docx PyPDF2")
                    print("   Optional: Install pandoc for best quality")
                    return None
                
                result = self.converter.convert_to_markdown(path)
                if not result.success:
                    print(f"⚠️  Failed to convert {path}: {result.error_message}")
                    return None
                
                # Use converted markdown file
                path = result.markdown_path
                format_type = PolicyFormat.MARKDOWN
            else:
                format_type = self._detect_format(path)
            
            if format_type == PolicyFormat.YAML:
                content = self._parse_yaml(path)
            elif format_type == PolicyFormat.JSON:
                content = self._parse_json(path)
            elif format_type == PolicyFormat.MARKDOWN:
                content = self._parse_markdown(path)
            else:
                return None
            
            if not content:
                return None
            
            categories = self._extract_categories(content)
            
            return PolicyDocument(
                path=path,
                format=format_type,
                content=content,
                categories=categories
            )
        except Exception as e:
            print(f"⚠️  Failed to parse policy file {path}: {e}")
            return None
    
    def _detect_format(self, path: Path) -> PolicyFormat:
        """Detect policy file format from extension"""
        suffix = path.suffix.lower()
        
        if suffix in ['.yaml', '.yml']:
            return PolicyFormat.YAML
        elif suffix == '.json':
            return PolicyFormat.JSON
        elif suffix == '.md':
            return PolicyFormat.MARKDOWN
        else:
            return PolicyFormat.UNKNOWN
    
    def _parse_yaml(self, path: Path) -> Dict[str, Any]:
        """Parse YAML policy file"""
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _parse_json(self, path: Path) -> Dict[str, Any]:
        """Parse JSON policy file"""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _parse_markdown(self, path: Path) -> Dict[str, Any]:
        """
        Parse Markdown policy file into structured format
        
        Converts markdown sections into dictionary:
        ## Naming Conventions → {"naming_conventions": [...]}
        """
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        policies = {}
        current_section = None
        current_rules = []
        
        for line in content.split('\n'):
            line = line.strip()
            
            if line.startswith('## '):
                # New section
                if current_section:
                    policies[current_section] = current_rules
                
                current_section = line[3:].strip().lower().replace(' ', '_')
                current_rules = []
            elif line.startswith('- ') and current_section:
                # Rule item
                current_rules.append(line[2:].strip())
        
        # Add last section
        if current_section and current_rules:
            policies[current_section] = current_rules
        
        return policies
    
    def _extract_categories(self, content: Dict[str, Any]) -> List[str]:
        """
        Extract policy categories from content
        
        Categories:
        - naming: Naming conventions
        - security: Security rules
        - standards: Code standards
        - architecture: Architecture patterns
        """
        categories = []
        
        # Check for naming-related keys
        naming_keys = ['naming', 'naming_conventions', 'file_naming', 'class_naming']
        if any(key in content for key in naming_keys):
            categories.append('naming')
        
        # Check for security-related keys
        security_keys = ['security', 'security_rules', 'authentication', 'authorization']
        if any(key in content for key in security_keys):
            categories.append('security')
        
        # Check for standards-related keys
        standards_keys = ['standards', 'code_standards', 'formatting', 'documentation']
        if any(key in content for key in standards_keys):
            categories.append('standards')
        
        # Check for architecture-related keys
        architecture_keys = ['architecture', 'patterns', 'design_patterns', 'layering']
        if any(key in content for key in architecture_keys):
            categories.append('architecture')
        
        return categories
    
    def has_policies(self) -> bool:
        """Quick check if any policies exist"""
        return len(self.scan_for_policies()) > 0
    
    def create_starter_policies(self, output_path: Optional[Path] = None) -> Path:
        """
        Create starter policy template for users without policies
        
        Args:
            output_path: Where to save template (default: repo_root/.github/policies/starter-policies.yaml)
            
        Returns:
            Path to created policy file
        """
        if output_path is None:
            output_path = self.repo_root / ".github" / "policies" / "starter-policies.yaml"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load template from cortex-brain
        cortex_root = self._find_cortex_root()
        template_path = cortex_root / "cortex-brain" / "templates" / "starter-policies.yaml"
        
        if template_path.exists():
            # Copy template
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
        else:
            # Create minimal template
            minimal_template = """# Starter Policy Template
# Generated by CORTEX Setup

naming_conventions:
  descriptive_names: Use descriptive variable names (min 3 characters)
  classes_pascal_case: Class names use PascalCase
  functions_snake_case: Function names use snake_case
  constants_upper_case: Constants use UPPER_CASE

security_rules:
  no_hardcoded_credentials: No hardcoded credentials
  use_environment_variables: Use environment variables for secrets
  validate_all_inputs: Validate all user inputs

code_standards:
  require_docstrings: Include docstrings for all public functions
  test_coverage_minimum: Maintain test coverage above 70%
  run_linter: Run linter before committing

architecture_patterns:
  separation_of_concerns: Follow separation of concerns
  dependency_injection: Use dependency injection
  max_function_length: Keep functions under 50 lines
"""
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(minimal_template)
        
        return output_path
    
    def _find_cortex_root(self) -> Path:
        """Find CORTEX root directory"""
        # Check if embedded
        if (self.repo_root / "CORTEX" / "cortex-brain").exists():
            return self.repo_root / "CORTEX"
        
        # Check if standalone
        if (self.repo_root / "cortex-brain").exists():
            return self.repo_root
        
        # Check common locations
        common_locations = [
            Path.home() / "PROJECTS" / "CORTEX",
            Path(__file__).parent.parent.parent  # 3 levels up from this file
        ]
        
        for location in common_locations:
            if (location / "cortex-brain").exists():
                return location
        
        raise ValueError("CORTEX installation not found")


# CLI for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python policy_scanner.py <repo_root>")
        sys.exit(1)
    
    repo_root = Path(sys.argv[1])
    scanner = PolicyScanner(repo_root)
    
    print(f"🔍 Scanning for policies in: {repo_root}")
    print(f"   Search locations: {len(scanner.policy_locations)}")
    
    policies = scanner.scan_for_policies()
    
    if policies:
        print(f"\n✅ Found {len(policies)} policy document(s):")
        for i, policy in enumerate(policies, 1):
            print(f"\n{i}. {policy.path.name}")
            print(f"   Format: {policy.format.value}")
            print(f"   Categories: {', '.join(policy.categories)}")
            print(f"   Rules: {len(policy.content)} sections")
    else:
        print("\n⚠️  No policy documents found")
        print("\nWould you like to create a starter policy template? (y/n): ", end="")
        
        if input().lower() == 'y':
            output_path = scanner.create_starter_policies()
            print(f"\n✅ Created starter policy template: {output_path}")
