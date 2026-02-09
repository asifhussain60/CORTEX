"""
CopilotMerger - Intelligent copilot instructions merger.

Merges CORTEX governance intelligence with existing repo copilot instructions,
respecting user-defined sections while updating CORTEX-managed content.

AC-ID: AC-MCP-042
"""

from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, field
import re
import shutil
from datetime import datetime
import yaml


@dataclass
class MergeResult:
    """Result of a merge operation."""
    success: bool
    merged_path: Optional[Path] = None
    backup_path: Optional[Path] = None
    preserved_sections: List[str] = field(default_factory=list)
    updated_sections: List[str] = field(default_factory=list)
    error: Optional[str] = None


@dataclass
class Conflict:
    """Represents a conflict between instructions."""
    topic: str
    existing: str
    cortex: str
    severity: str = "warning"


class CopilotMerger:
    """
    Intelligent merger for copilot instructions.
    
    Respects existing repo instructions while adding CORTEX governance intelligence.
    Follows CORE-008 (TDD) and CORE-011 (type hints).
    """
    
    # Known CORTEX-managed section names
    CORTEX_SECTIONS = {
        "CORTEX Governance",
        "TIER 0 Rules",
        "TIER 0 Governance",
        "Architecture Summary",
        "AC-ID Driven Development",
        "Response Header",
        "Response Format Standards",
        "Audit-First Pattern",
        "Key Implementation Principles",
        "CORTEX Instructions",
        "Governance Rules",
        "File Output Rules"
    }
    
    # Keywords that indicate CORTEX-generated content
    CORTEX_KEYWORDS = {
        "CORTEX", "TIER 0", "AC-ID", "governance-first",
        "audit trail", "SKULL rules", "CORE-", "AC-"
    }
    
    # Conflict detection patterns
    CONFLICT_PATTERNS = {
        "indentation": [
            (r"use\s+(?:tabs|spaces))", "indentation style"),
            (r"indent(?:ation)?\s*(?:with|using))?\s*(?:\d+\s*)?(?:tabs|spaces))", "indentation")
        ],
        "line_length": [
            (r"max(?:imum)?\s*(?:line)?\s*(?:length|chars)?|characters?)\s*(?:of|:)?\s*\d+", "line length"),
            (r"\d+\s*(?:chars?|characters?)\s*(?:per|max))", "line length")
        ],
        "testing": [
            (r"use\s+(?:pytest|unittest)|nose)", "testing framework"),
        ]
    }
    
    def __init__(self, audit_enabled: bool = False):
        """
        Initialize CopilotMerger.
        
        Args:
            audit_enabled: Whether to log operations to audit trail.
        """
        self.audit_enabled = audit_enabled
        self._audit = None
        
        if audit_enabled:
            try:
                from cortex.orchestrators.shared_audit_trail import SharedAuditTrail
                self._audit = SharedAuditTrail()
            except ImportError:
                pass
    
    def find_existing_instructions(self, repo_path: Path) -> Optional[Dict[str, Any]]:
        """
        Find existing copilot instructions in a repository.
        
        Searches in order:
        1. .github/copilot-instruction.md
        2. .github/prompts/copilot-instruction.md
        
        Args:
            repo_path: Path to the repository root.
            
        Returns:
            Dict with path and content if found, None otherwise.
        """
        search_paths = [
            repo_path / ".github" / "copilot-instruction.md",
            repo_path / ".github" / "prompts" / "copilot-instruction.md",
        ]
        
        for path in search_paths:
            if path.exists():
                return {
                    "path": path,
                    "content": path.read_text(encoding="utf-8")
                }
        
        return None
    
    def find_cortex_prompt(self, repo_path: Path) -> Optional[Dict[str, Any]]:
        """
        Find existing CORTEX.prompt.md in a repository.
        
        Args:
            repo_path: Path to the repository root.
            
        Returns:
            Dict with path and content if found, None otherwise.
        """
        search_paths = [
            repo_path / ".github" / "prompts" / "CORTEX.prompt.md",
            repo_path / ".github" / "CORTEX.prompt.md",
        ]
        
        for path in search_paths:
            if path.exists():
                return {
                    "path": path,
                    "content": path.read_text(encoding="utf-8")
                }
        
        return None
    
    def parse_sections(self, content: str) -> Dict[str, str]:
        """
        Parse markdown content into sections by headers.
        
        Args:
            content: Markdown content to parse.
            
        Returns:
            Dict mapping section names to their content.
        """
        sections = {}
        current_section = None
        current_content = []
        
        for line in content.split('\n'):
            # Match ## headers (level 2)
            header_match = re.match(r'^##\s+(.+)$', line)
            if header_match:
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                current_section = header_match.group(1).strip()
                current_content = []
            elif current_section:
                current_content.append(line)
        
        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def extract_project_rules(self, content: str) -> List[str]:
        """
        Extract project-specific rules from instructions content.
        
        Args:
            content: Instruction content to parse.
            
        Returns:
            List of extracted rules.
        """
        rules = []
        
        # Match list items
        list_pattern = r'^[-*]\s+(.+)$'
        for line in content.split('\n'):
            match = re.match(list_pattern, line.strip())
            if match:
                rules.append(match.group(1).strip())
        
        return rules
    
    def identify_section_origins(self, content: str) -> Tuple[List[str], List[str]]:
        """
        Identify which sections originated from CORTEX vs user-defined.
        
        Args:
            content: Full instruction content.
            
        Returns:
            Tuple of (cortex_sections, user_sections).
        """
        sections = self.parse_sections(content)
        cortex_sections = []
        user_sections = []
        
        for section_name, section_content in sections.items():
            is_cortex = False
            
            # Check if section name is known CORTEX section
            if section_name in self.CORTEX_SECTIONS:
                is_cortex = True
            
            # Check for CORTEX keywords in content
            if not is_cortex:
                for keyword in self.CORTEX_KEYWORDS:
                    if keyword.lower() in section_name.lower() or \
                       keyword.lower() in section_content.lower():
                        is_cortex = True
                        break
            
            if is_cortex:
                cortex_sections.append(section_name)
            else:
                user_sections.append(section_name)
        
        return cortex_sections, user_sections
    
    def merge_instructions(
        self,
        existing_content: Optional[str],
        cortex_content: str
    ) -> str:
        """
        Merge existing instructions with CORTEX template.
        
        Preserves user-defined sections while updating CORTEX-managed sections.
        
        Args:
            existing_content: Existing instruction content (may be None).
            cortex_content: CORTEX template content.
            
        Returns:
            Merged instruction content.
        """
        if not existing_content:
            # No existing content, use CORTEX template directly
            return self._add_version_header(cortex_content)
        
        # Parse sections from both
        existing_sections = self.parse_sections(existing_content)
        cortex_sections = self.parse_sections(cortex_content)
        
        # Identify origins
        cortex_section_names, user_section_names = self.identify_section_origins(existing_content)
        
        # Build merged content
        merged_parts = []
        
        # Add CORTEX header
        merged_parts.append(self._generate_header())
        
        # Add CORTEX sections (updated from template)
        for section_name in cortex_sections:
            merged_parts.append(f"\n## {section_name}\n")
            merged_parts.append(cortex_sections[section_name])
        
        # Add user sections (preserved from existing)
        for section_name in user_section_names:
            if section_name in existing_sections:
                merged_parts.append(f"\n## {section_name}\n")
                merged_parts.append(existing_sections[section_name])
        
        return '\n'.join(merged_parts)
    
    def _generate_header(self) -> str:
        """Generate CORTEX instruction header."""
        timestamp = datetime.now().strftime("%Y-%m-%d")
        return f"""# CORTEX Managed Instructions
**Version:** 7.0 | **Updated:** {timestamp} | **Managed By:** CORTEX CopilotMerger

> **Note:** Sections marked with CORTEX are automatically managed.
> Your custom sections are preserved during updates.

---"""
    
    def _add_version_header(self, content: str) -> str:
        """Add version header to content."""
        header = self._generate_header()
        return f"{header}\n\n{content}"
    
    def detect_conflicts(self, existing: str, cortex: str) -> List[Dict[str, Any]]:
        """
        Detect conflicts between existing and CORTEX instructions.
        
        Args:
            existing: Existing instruction content.
            cortex: CORTEX template content.
            
        Returns:
            List of detected conflicts.
        """
        conflicts = []
        
        for topic, patterns in self.CONFLICT_PATTERNS.items():
            existing_matches = []
            cortex_matches = []
            
            for pattern, description in patterns:
                existing_found = re.findall(pattern, existing.lower())
                cortex_found = re.findall(pattern, cortex.lower())
                
                existing_matches.extend(existing_found)
                cortex_matches.extend(cortex_found)
            
            # Check for actual conflicts (different values found)
            if existing_matches and cortex_matches:
                if set(existing_matches) != set(cortex_matches):
                    conflicts.append({
                        "topic": topic,
                        "existing": ", ".join(existing_matches),
                        "cortex": ", ".join(cortex_matches)
                    })
        
        return conflicts
    
    def get_resolution_strategies(self, conflicts: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Get resolution strategies for detected conflicts.
        
        Args:
            conflicts: List of detected conflicts.
            
        Returns:
            List of resolution strategies.
        """
        strategies = []
        
        for conflict in conflicts:
            topic = conflict["topic"]
            
            if topic == "indentation":
                strategy = {
                    "topic": topic,
                    "strategy": "preserve_existing",
                    "reason": "Indentation style is project-specific, preserving existing."
                }
            elif topic == "line_length":
                strategy = {
                    "topic": topic,
                    "strategy": "preserve_existing",
                    "reason": "Line length is project-specific, preserving existing."
                }
            elif topic == "testing":
                strategy = {
                    "topic": topic,
                    "strategy": "preserve_existing",
                    "reason": "Testing framework is project-specific, preserving existing."
                }
            else:
                strategy = {
                    "topic": topic,
                    "strategy": "manual_review",
                    "reason": "Conflict requires manual review."
                }
            
            strategies.append(strategy)
        
        return strategies
    
    def generate_merged_file(
        self,
        repo_path: Path,
        cortex_template: str,
        backup: bool = True
    ) -> Dict[str, Any]:
        """
        Generate merged instruction file for a repository.
        
        Args:
            repo_path: Path to the repository.
            cortex_template: CORTEX template content.
            backup: Whether to create backup of existing file.
            
        Returns:
            Result dictionary with success status and paths.
        """
        result = {
            "success": False,
            "merged_path": None,
            "backup_path": None,
            "preserved_sections": [],
            "error": None
        }
        
        try:
            # Find existing instructions
            existing = self.find_existing_instructions(repo_path)
            existing_content = existing["content"] if existing else None
            
            # Identify preserved sections
            if existing_content:
                _, user_sections = self.identify_section_origins(existing_content)
                result["preserved_sections"] = user_sections
            
            # Create backup if requested and file exists
            if backup and existing:
                backup_path = existing["path"].with_suffix(".md.backup")
                shutil.copy2(existing["path"], backup_path)
                result["backup_path"] = backup_path
            
            # Merge content
            merged_content = self.merge_instructions(existing_content, cortex_template)
            
            # Ensure .github directory exists
            github_dir = repo_path / ".github"
            github_dir.mkdir(parents=True, exist_ok=True)
            
            # Write merged file
            output_path = github_dir / "copilot-instruction.md"
            output_path.write_text(merged_content, encoding="utf-8")
            
            result["success"] = True
            result["merged_path"] = output_path
            
            # Log to audit if enabled
            if self._audit:
                self._audit.log_operation(
                    project_name=repo_path.name,
                    operation="copilot_merge",
                    details={
                        "preserved_sections": result["preserved_sections"],
                        "backup_created": backup and existing is not None
                    }
                )
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def generate_cortex_prompt(
        self,
        repo_path: Path,
        project_type: str = "general",
        regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        Generate CORTEX.prompt.md file for a repository.
        
        Args:
            repo_path: Path to the repository.
            project_type: Type of project for customization.
            regenerate: Whether to delete and regenerate existing file.
            
        Returns:
            Result dictionary with success status and paths.
        """
        result = {
            "success": False,
            "prompt_path": None,
            "error": None
        }
        
        try:
            # Ensure prompts directory exists
            prompts_dir = repo_path / ".github" / "prompts"
            prompts_dir.mkdir(parents=True, exist_ok=True)
            
            prompt_path = prompts_dir / "CORTEX.prompt.md"
            
            # Delete existing if regenerating
            if regenerate and prompt_path.exists():
                prompt_path.unlink()
            
            # Generate template based on project type
            content = self._generate_prompt_template(project_type)
            
            # Write file
            prompt_path.write_text(content, encoding="utf-8")
            
            result["success"] = True
            result["prompt_path"] = prompt_path
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _generate_prompt_template(self, project_type: str) -> str:
        """Generate CORTEX.prompt.md template for project type."""
        timestamp = datetime.now().strftime("%Y-%m-%d")
        
        domain_section = self._get_domain_section(project_type)
        
        return f"""# CORTEX Master Orchestrator System Prompt
**Version:** 7.0 | **Generated:** {timestamp} | **Project Type:** {project_type}

---

## Identity

You are the **CORTEX System Agent** operating with governance-aware intelligence.

**Your Mission:** Execute governance-compliant development with audit-first patterns.

---

## TIER 0 Governance (Immutable)

These rules are IMMUTABLE and must be followed at all times:

| Rule | Requirement |
|------|-------------|
| **CORE-001** | Incremental execution <500 lines |
| **CORE-005** | No hardcoded paths |
| **CORE-008** | TDD (tests before code) |
| **CORE-011** | Type hints on all functions |
| **CORE-012** | Docstrings (Google format) |
| **CORE-029** | Response headers required |

---

{domain_section}

## Audit-First Pattern

Every operation MUST follow:
```
AC_START (log intent) → EXECUTE → AC_COMPLETE (log result) → Verify hash chain
```

---

## Response Format

Begin every response with:
```markdown
## 🧠 CORTEX {{operation}}
**Author:** {{author}} | **Phase:** {{phase}} | **Orchestrator:** {{orchestrator}} ✅
```

---

*Generated by CORTEX CopilotMerger*
"""
    
    def _get_domain_section(self, project_type: str) -> str:
        """Get domain-specific section for project type."""
        domain_sections = {
            "finops": """## Domain: FinOps

**Focus Areas:**
- Cost optimization and allocation
- Cloud spend analysis
- Budget compliance
- Resource utilization

**Key Patterns:**
- Use decimal for currency calculations
- Audit all cost-related changes
- Include cost impact in PRs
""",
            "auth": """## Domain: Authentication & Security

**Focus Areas:**
- Identity management
- Access control
- Session handling
- Security compliance

**Key Patterns:**
- Never log sensitive data
- Use secure defaults
- Validate all inputs
- Audit authentication events
""",
            "ml": """## Domain: Machine Learning

**Focus Areas:**
- Model development
- Data pipelines
- Experiment tracking
- Model deployment

**Key Patterns:**
- Version all models
- Track experiments
- Document hyperparameters
- Validate data quality
""",
            "devops": """## Domain: DevOps & Infrastructure

**Focus Areas:**
- CI/CD pipelines
- Infrastructure as code
- Deployment automation
- Monitoring

**Key Patterns:**
- Infrastructure as code
- Immutable deployments
- Comprehensive logging
- Automated testing
""",
            "healthcare": """## Domain: Healthcare

**Focus Areas:**
- HIPAA compliance
- Patient data protection
- Clinical workflows
- Audit requirements

**Key Patterns:**
- PHI protection required
- Comprehensive audit trails
- Access logging mandatory
- Data encryption required
""",
            "legal": """## Domain: Legal & Compliance

**Focus Areas:**
- Regulatory compliance
- Document management
- Retention policies
- Audit requirements

**Key Patterns:**
- Document versioning required
- Retention policy enforcement
- Access audit trails
- Compliance reporting
"""
        }
        
        return domain_sections.get(project_type, """## Domain: General

**Focus Areas:**
- Code quality
- Documentation
- Testing
- Maintainability

**Key Patterns:**
- Follow SOLID principles
- Write comprehensive tests
- Document public APIs
- Keep functions focused
""")
    
    def load_repo_overrides(self, repo_path: Path) -> Dict[str, Any]:
        """
        Load repository-specific override configuration.
        
        Args:
            repo_path: Path to the repository.
            
        Returns:
            Override configuration dictionary.
        """
        override_paths = [
            repo_path / ".github" / "cortex-override.yaml",
            repo_path / ".github" / "cortex-override.yml",
        ]
        
        for path in override_paths:
            if path.exists():
                with open(path, encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
        
        return {}
    
    def process_repos(
        self,
        repos: List[Path],
        cortex_template: str
    ) -> List[Dict[str, Any]]:
        """
        Process multiple repositories with copilot instruction merging.
        
        Args:
            repos: List of repository paths.
            cortex_template: CORTEX template to merge.
            
        Returns:
            List of results for each repository.
        """
        results = []
        
        for repo_path in repos:
            result = self.generate_merged_file(repo_path, cortex_template)
            result["repo"] = repo_path.name
            results.append(result)
        
        return results
