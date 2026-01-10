"""
Generic Cleanup Intelligence - Learnings from CORTEX Repository Cleanup

This module encapsulates the cleanup patterns and intelligence derived from
the comprehensive CORTEX v6.0 repository cleanup operation documented in
cortex-brain/documents/cleanup-reports/chat01.md.

Cleanup Categories:
1. Brain Structure Cleanup - Core architecture enforcement
2. Documents Folder Cleanup - Historical vs essential content
3. Root Cortex-* Cleanup - Tool/sample/output folder removal
4. Gitignored Cache Cleanup - Build artifacts and temp data
5. Root Config Files Cleanup - Obsolete configuration removal
6. GitHub Configuration Cleanup - CI/CD and workflow pruning

Each category includes:
- Detection patterns (what to identify)
- Preservation rules (what to keep)
- Deletion criteria (what to remove)
- Safety validations (what to protect)

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


logger = logging.getLogger(__name__)


class CleanupCategory(Enum):
    """Cleanup categories from CORTEX v6.0 rebuild."""
    BRAIN_STRUCTURE = "brain_structure"
    DOCUMENTS_FOLDER = "documents_folder"
    ROOT_CORTEX_ITEMS = "root_cortex_items"
    GITIGNORED_CACHE = "gitignored_cache"
    ROOT_CONFIG_FILES = "root_config_files"
    GITHUB_CONFIG = "github_config"


@dataclass
class CleanupRule:
    """
    Represents a cleanup rule with detection and preservation criteria.
    
    Attributes:
        category: Cleanup category
        name: Rule name
        description: Human-readable description
        detection_patterns: File/folder patterns to detect
        preserve_patterns: Patterns to preserve (exclusions)
        deletion_criteria: Lambda function returning True if should delete
        safety_level: Risk level (LOW, MEDIUM, HIGH, CRITICAL)
        impact_description: Description of impact if deleted
    """
    category: CleanupCategory
    name: str
    description: str
    detection_patterns: List[str]
    preserve_patterns: List[str]
    deletion_criteria: callable
    safety_level: str
    impact_description: str


class GenericCleanupIntelligence:
    """
    Generic cleanup intelligence engine based on CORTEX v6.0 cleanup patterns.
    
    This class encapsulates cleanup logic that can be applied to any Python
    project with similar structure. Rules are derived from actual cleanup
    operations that freed ~140 MB and removed 22,400+ files.
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize cleanup intelligence engine.
        
        Args:
            project_root: Root directory of project to clean
        """
        self.project_root = project_root
        self.rules = self._initialize_rules()
        logger.info(f"Initialized Generic Cleanup Intelligence for {project_root}")
    
    def _initialize_rules(self) -> List[CleanupRule]:
        """
        Initialize cleanup rules from CORTEX v6.0 cleanup operation.
        
        Returns:
            List of CleanupRule instances
        """
        rules = []
        
        # ===== 1. Brain Structure Cleanup =====
        rules.append(CleanupRule(
            category=CleanupCategory.BRAIN_STRUCTURE,
            name="obsolete_brain_folders",
            description="Remove obsolete cortex-brain folders not in v6.0 architecture",
            detection_patterns=[
                "cortex-brain/cognitive-framework",
                "cortex-brain/components",
                "cortex-brain/conversation-captures",
                "cortex-brain/dashboards",
                "cortex-brain/database",
                "cortex-brain/discovery",
                "cortex-brain/domains",
                "cortex-brain/exports",
                "cortex-brain/feedback",
                "cortex-brain/imported-conversations",
                "cortex-brain/inventory-v1",
                "cortex-brain/knowledge",
                "cortex-brain/knowledge-library",
                "cortex-brain/learning",
                "cortex-brain/metadata",
                "cortex-brain/metrics",
                "cortex-brain/metrics-history",
                "cortex-brain/migrations",
                "cortex-brain/operations",
                "cortex-brain/platform-classic-migration",
                "cortex-brain/protection-layers",
                "cortex-brain/reference",
                "cortex-brain/registry",
                "cortex-brain/response-templates",
                "cortex-brain/schemas",
                "cortex-brain/setup-reports",
                "cortex-brain/specifications",
                "cortex-brain/state",
                "cortex-brain/sts-results",
                "cortex-brain/templates",
                "cortex-brain/test-snapshots",
                "cortex-brain/training"
            ],
            preserve_patterns=[
                "cortex-brain/tier0",
                "cortex-brain/tier1",
                "cortex-brain/tier2",
                "cortex-brain/tier3",
                "cortex-brain/manifests",
                "cortex-brain/config",
                "cortex-brain/documents"
            ],
            deletion_criteria=lambda path: path.is_dir() and "cortex-brain" in str(path),
            safety_level="MEDIUM",
            impact_description="Removes obsolete brain folders (v5.x structure)"
        ))
        
        rules.append(CleanupRule(
            category=CleanupCategory.BRAIN_STRUCTURE,
            name="obsolete_brain_root_files",
            description="Remove obsolete cortex-brain root-level config files",
            detection_patterns=[
                "cortex-brain/brain-protection-rules.yaml",
                "cortex-brain/capabilities.yaml",
                "cortex-brain/cleanup-rules.yaml",
                "cortex-brain/compliance-tracking-schema.sql",
                "cortex-brain/doc-generation-rules.yaml",
                "cortex-brain/file-relationships.yaml",
                "cortex-brain/git-checkpoint-rules.yaml",
                "cortex-brain/governance-schema.sql",
                "cortex-brain/hybrid-capture-simulation-results.json",
                "cortex-brain/lessons-learned.yaml",
                "cortex-brain/migrate_brain_db.py",
                "cortex-brain/module-definitions.yaml",
                "cortex-brain/multilingual-templates.yaml",
                "cortex-brain/obsolete-tests-manifest.json",
                "cortex-brain/operations-config.yaml",
                "cortex-brain/publish-config.yaml",
                "cortex-brain/refactoring-rules.yaml",
                "cortex-brain/schema.sql",
                "cortex-brain/self-review-checklist.yaml",
                "cortex-brain/sts-baseline.json",
                "cortex-brain/token-optimization-rules.yaml",
                "cortex-brain/track-integration-plan.json",
                "cortex-brain/user-dictionary.yaml"
            ],
            preserve_patterns=[
                "cortex-brain/response-templates-v4.yaml",
                "cortex-brain/TRUTH-SOURCES.yaml"
            ],
            deletion_criteria=lambda path: path.is_file() and path.parent.name == "cortex-brain",
            safety_level="LOW",
            impact_description="Removes obsolete config files (replaced by tier0/config structure)"
        ))
        
        # ===== 2. Documents Folder Cleanup =====
        rules.append(CleanupRule(
            category=CleanupCategory.DOCUMENTS_FOLDER,
            name="historical_documents",
            description="Remove historical/obsolete documents folders",
            detection_patterns=[
                "cortex-brain/documents/analysis",
                "cortex-brain/documents/archive",
                "cortex-brain/documents/implementation-guides",
                "cortex-brain/documents/planning",
                "cortex-brain/documents/reports",
                "cortex-brain/documents/investigations",
                "cortex-brain/documents/summaries",
                "cortex-brain/documents/learning-library",
                "cortex-brain/documents/legacy",
                "cortex-brain/documents/library",
                "cortex-brain/documents/learning",
                "cortex-brain/documents/learning-paths",
                "cortex-brain/documents/limitations",
                "cortex-brain/documents/features",
                "cortex-brain/documents/fixes",
                "cortex-brain/documents/implementations",
                "cortex-brain/documents/integration-guides",
                "cortex-brain/documents/reviews",
                "cortex-brain/documents/updates",
                "cortex-brain/documents/refinement",
                "cortex-brain/documents/remediation",
                "cortex-brain/documents/implementation-reports"
            ],
            preserve_patterns=[
                "cortex-brain/documents/architecture",
                "cortex-brain/documents/diagrams",
                "cortex-brain/documents/governance",
                "cortex-brain/documents/images",
                "cortex-brain/documents/orchestrators",
                "cortex-brain/documents/requirements",  # ACTIVELY WORKING
                "cortex-brain/documents/standards",
                "cortex-brain/documents/upgrades"
            ],
            deletion_criteria=lambda path: path.is_dir() and "cortex-brain/documents" in str(path),
            safety_level="HIGH",
            impact_description="Removes ~970 historical documents (analysis, planning, reports, etc.)"
        ))
        
        # ===== 3. Root Cortex-* Cleanup =====
        rules.append(CleanupRule(
            category=CleanupCategory.ROOT_CORTEX_ITEMS,
            name="cortex_tool_folders",
            description="Remove cortex-* tool/sample/output folders",
            detection_patterns=[
                "cortex-lens-output",
                "cortex-sample-apps",
                "cortex-toolkit"
            ],
            preserve_patterns=[
                "cortex-brain"
            ],
            deletion_criteria=lambda path: path.is_dir() and path.name.startswith("cortex-") and path.parent == self.project_root,
            safety_level="MEDIUM",
            impact_description="Removes tool folders (~115 MB, 21,400 files)"
        ))
        
        rules.append(CleanupRule(
            category=CleanupCategory.ROOT_CORTEX_ITEMS,
            name="cortex_script_files",
            description="Remove cortex-* root-level script files",
            detection_patterns=[
                "cortex-cleanup.ps1",
                "cortex-operations.yaml",
                "cortex-upgrade-plan.py",
                "cortex-upgrade.ps1",
                "cortex-upgrade.sh",
                ".cortex-initialized",
                ".cortex-installed",
                ".cortexignore"
            ],
            preserve_patterns=[],
            deletion_criteria=lambda path: path.is_file() and (path.name.startswith("cortex-") or path.name.startswith(".cortex")),
            safety_level="LOW",
            impact_description="Removes obsolete cortex-* scripts and markers"
        ))
        
        # ===== 4. Gitignored Cache Cleanup =====
        rules.append(CleanupRule(
            category=CleanupCategory.GITIGNORED_CACHE,
            name="build_and_cache_folders",
            description="Remove gitignored build artifacts and cache folders",
            detection_patterns=[
                ".githooks",
                ".pytest_cache",
                ".upgrades",
                ".vacuum_backup",
                "build",
                "htmlcov",
                "logs"
            ],
            preserve_patterns=[
                ".git",
                ".venv",
                ".github"
            ],
            deletion_criteria=lambda path: path.is_dir() and path.name in [
                ".githooks", ".pytest_cache", ".upgrades", ".vacuum_backup",
                "build", "htmlcov", "logs"
            ],
            safety_level="LOW",
            impact_description="Removes build artifacts and cache (regenerated automatically)"
        ))
        
        # ===== 5. Root Config Files Cleanup =====
        rules.append(CleanupRule(
            category=CleanupCategory.ROOT_CONFIG_FILES,
            name="obsolete_root_configs",
            description="Remove obsolete root-level configuration files",
            detection_patterns=[
                ".coverage",
                ".favorites.json",
                ".flake8",
                ".pre-commit-config.yaml",
                "mypy.ini",
                "pytest.ini",
                "cortex.config.json"
            ],
            preserve_patterns=[
                ".env",
                ".gitattributes",
                ".gitignore",
                "LICENSE",
                "README.md",
                "requirements.txt"
            ],
            deletion_criteria=lambda path: path.is_file() and path.name in [
                ".coverage", ".favorites.json", ".flake8", ".pre-commit-config.yaml",
                "mypy.ini", "pytest.ini", "cortex.config.json"
            ],
            safety_level="LOW",
            impact_description="Removes obsolete linter/test configs (v4.0 structure)"
        ))
        
        # ===== 6. GitHub Configuration Cleanup =====
        rules.append(CleanupRule(
            category=CleanupCategory.GITHUB_CONFIG,
            name="obsolete_github_content",
            description="Remove obsolete .github workflows and prompts",
            detection_patterns=[
                ".github/copilot",
                ".github/light-bulbs.md",
                ".github/workflows",
                ".github/USER-COPILOT-INTEGRATION.md",
                ".github/prompts/cortex-migrate.prompt.md",
                ".github/prompts/cortex-vacuum.prompt.md"
            ],
            preserve_patterns=[
                ".github/.prompt-preserve",
                ".github/copilot-instructions.md",
                ".github/prompts/CORTEX.prompt.md"
            ],
            deletion_criteria=lambda path: ".github" in str(path) and path.name not in [
                ".prompt-preserve", "copilot-instructions.md", "CORTEX.prompt.md"
            ],
            safety_level="MEDIUM",
            impact_description="Removes obsolete CI/CD workflows and prompts (~50 KB)"
        ))
        
        return rules
    
    def analyze_project(self) -> Dict[str, Any]:
        """
        Analyze project and identify cleanup opportunities.
        
        Returns:
            Dictionary with:
                - total_files: Number of files to clean
                - total_size_mb: Space to recover (MB)
                - categories: Breakdown by category
                - recommendations: Cleanup recommendations
        """
        logger.info("Analyzing project for cleanup opportunities...")
        
        results = {
            'total_files': 0,
            'total_size_mb': 0.0,
            'categories': {},
            'recommendations': []
        }
        
        for rule in self.rules:
            category_name = rule.category.value
            if category_name not in results['categories']:
                results['categories'][category_name] = {
                    'files': 0,
                    'size_mb': 0.0,
                    'items': []
                }
            
            # Check each detection pattern
            for pattern in rule.detection_patterns:
                full_path = self.project_root / pattern
                
                if full_path.exists():
                    # Check if should be preserved
                    should_preserve = False
                    for preserve_pattern in rule.preserve_patterns:
                        if preserve_pattern in str(full_path):
                            should_preserve = True
                            break
                    
                    if not should_preserve and rule.deletion_criteria(full_path):
                        # Calculate size
                        if full_path.is_file():
                            size_bytes = full_path.stat().st_size
                            file_count = 1
                        else:
                            file_count = sum(1 for _ in full_path.rglob("*") if _.is_file())
                            size_bytes = sum(
                                f.stat().st_size
                                for f in full_path.rglob("*")
                                if f.is_file()
                            )
                        
                        size_mb = size_bytes / (1024 * 1024)
                        
                        results['categories'][category_name]['files'] += file_count
                        results['categories'][category_name]['size_mb'] += size_mb
                        results['categories'][category_name]['items'].append({
                            'path': str(full_path.relative_to(self.project_root)),
                            'type': 'folder' if full_path.is_dir() else 'file',
                            'files': file_count,
                            'size_mb': round(size_mb, 2),
                            'safety_level': rule.safety_level,
                            'impact': rule.impact_description
                        })
                        
                        results['total_files'] += file_count
                        results['total_size_mb'] += size_mb
        
        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(results)
        
        logger.info(
            f"Analysis complete: {results['total_files']} files, "
            f"{results['total_size_mb']:.1f} MB cleanup opportunity"
        )
        
        return results
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """
        Generate cleanup recommendations based on analysis.
        
        Args:
            analysis: Analysis results
        
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Check each category
        for category_name, data in analysis['categories'].items():
            if data['files'] > 0:
                recommendations.append(
                    f"**{category_name.replace('_', ' ').title()}**: "
                    f"{data['files']} files ({data['size_mb']:.1f} MB) can be cleaned"
                )
        
        # Priority recommendations
        if analysis['total_size_mb'] > 100:
            recommendations.insert(0, "⚠️ **HIGH PRIORITY**: Over 100 MB can be freed")
        
        if analysis['total_files'] > 10000:
            recommendations.insert(0, "⚠️ **HIGH PRIORITY**: Over 10,000 files can be cleaned")
        
        return recommendations
    
    def get_cleanup_plan(
        self,
        categories: Optional[List[CleanupCategory]] = None,
        safety_level: Optional[str] = None
    ) -> Dict[str, List[Path]]:
        """
        Generate cleanup plan filtered by categories and safety level.
        
        Args:
            categories: List of CleanupCategory enums to include (None = all)
            safety_level: Maximum safety level (LOW, MEDIUM, HIGH, CRITICAL)
        
        Returns:
            Dictionary mapping category to list of paths to delete
        """
        plan = {}
        
        safety_order = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        max_safety_index = safety_order.index(safety_level) if safety_level else 3
        
        for rule in self.rules:
            # Filter by category
            if categories and rule.category not in categories:
                continue
            
            # Filter by safety level
            if safety_order.index(rule.safety_level) > max_safety_index:
                continue
            
            category_name = rule.category.value
            if category_name not in plan:
                plan[category_name] = []
            
            # Collect paths for this rule
            for pattern in rule.detection_patterns:
                full_path = self.project_root / pattern
                
                if full_path.exists():
                    # Check preservation rules
                    should_preserve = False
                    for preserve_pattern in rule.preserve_patterns:
                        if preserve_pattern in str(full_path):
                            should_preserve = True
                            break
                    
                    if not should_preserve and rule.deletion_criteria(full_path):
                        plan[category_name].append(full_path)
        
        return plan
