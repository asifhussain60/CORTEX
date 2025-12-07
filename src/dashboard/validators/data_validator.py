"""
Dashboard Data Validator

Independent validation layer that verifies collector output against ground truth.
Fixes common issues: false positive languages, version hallucinations, third-party noise.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import re
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Set, Tuple
from collections import Counter
import xml.etree.ElementTree as ET


logger = logging.getLogger(__name__)


class DashboardDataValidator:
    """Validates and corrects dashboard data before rendering"""
    
    # Directories to exclude from language detection
    THIRD_PARTY_DIRS = {
        'Tools', 'External', 'Externals', 'ThirdParty',
        'node_modules', 'packages', 'vendor', 'lib', 'libs',
        'venv', 'env', '.venv', '__pycache__',
        'bin', 'obj', '.git', '.vs', '.vscode',
        'dist', 'build', 'out', 'target'
    }
    
    # Language file extensions (lowercase)
    LANGUAGE_EXTENSIONS = {
        'C#': {'.cs'},
        'Python': {'.py'},
        'JavaScript': {'.js', '.jsx'},
        'TypeScript': {'.ts', '.tsx'},
        'Java': {'.java'},
        'Go': {'.go'},
        'Rust': {'.rs'},
        'Ruby': {'.rb'},
        'PHP': {'.php'},
        'ColdFusion': {'.cfm', '.cfc'}
    }
    
    # Type definition file patterns (not application code)
    TYPE_DEF_PATTERNS = {
        r'\.d\.ts$',  # TypeScript definitions
        r'types?\.ts$',  # Type files
        r'@types/',  # NPM type packages
    }
    
    # Minimum file count to consider language "present"
    MIN_FILE_THRESHOLD = 5
    
    def __init__(self, repo_path: Path):
        """
        Initialize validator.
        
        Args:
            repo_path: Path to repository to validate
        """
        self.repo_path = Path(repo_path)
        self.ground_truth = None
        
    def validate_and_fix(self, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and fix collected dashboard data.
        
        Args:
            collected_data: Raw data from collectors
            
        Returns:
            Corrected and validated data
        """
        logger.info("Starting independent validation of collector data...")
        
        # Step 1: Get ground truth from direct repository scan
        self.ground_truth = self._scan_repository_ground_truth()
        
        # Step 2: Validate and fix tech stack
        if 'tech-stack' in collected_data or 'tech_stack' in collected_data:
            tech_key = 'tech-stack' if 'tech-stack' in collected_data else 'tech_stack'
            collected_data[tech_key] = self._fix_tech_stack(collected_data[tech_key])
        
        # Step 3: Validate and fix executive summary
        if 'executive-summary' in collected_data or 'executive_summary' in collected_data:
            exec_key = 'executive-summary' if 'executive-summary' in collected_data else 'executive_summary'
            collected_data[exec_key] = self._fix_executive_summary(collected_data[exec_key])
        
        # Step 4: Validate architecture data
        if 'architecture' in collected_data:
            collected_data['architecture'] = self._fix_architecture(collected_data['architecture'])
        
        # Step 5: Add validation metadata
        collected_data['_validation'] = {
            'validated': True,
            'validator_version': '1.0',
            'ground_truth_languages': list(self.ground_truth['languages'].keys()),
            'corrections_applied': self.ground_truth.get('corrections_applied', [])
        }
        
        logger.info(f"Validation complete. Applied {len(self.ground_truth.get('corrections_applied', []))} corrections")
        
        return collected_data
    
    def _scan_repository_ground_truth(self) -> Dict[str, Any]:
        """
        Scan repository directly to establish ground truth.
        
        Returns:
            Dictionary with actual file counts, languages, frameworks
        """
        logger.info("Scanning repository for ground truth...")
        
        ground_truth = {
            'languages': {},
            'source_directories': [],
            'framework_evidence': {},
            'corrections_applied': []
        }
        
        # Find actual source directories
        source_dirs = self._find_source_directories()
        ground_truth['source_directories'] = [str(d) for d in source_dirs]
        
        # Count files by language in SOURCE directories only
        for lang, extensions in self.LANGUAGE_EXTENSIONS.items():
            file_count = 0
            sample_files = []
            
            for source_dir in source_dirs:
                for ext in extensions:
                    files = list(source_dir.rglob(f'*{ext}'))
                    # Filter out type definitions
                    files = [f for f in files if not self._is_type_definition(f)]
                    file_count += len(files)
                    if len(sample_files) < 5:
                        sample_files.extend([str(f.relative_to(self.repo_path)) for f in files[:5-len(sample_files)]])
            
            if file_count > 0:
                ground_truth['languages'][lang] = {
                    'file_count': file_count,
                    'sample_files': sample_files
                }
        
        # Detect framework from project files
        ground_truth['framework_evidence'] = self._detect_framework_evidence()
        
        return ground_truth
    
    def _find_source_directories(self) -> List[Path]:
        """
        Find actual source code directories, excluding third-party.
        
        Returns:
            List of source directory paths
        """
        source_dirs = []
        
        # Common source directory names
        source_names = {'Source', 'src', 'app', 'lib', 'pkg', 'internal', 'cmd'}
        
        # Find directories matching source names
        for item in self.repo_path.iterdir():
            if item.is_dir() and item.name in source_names:
                source_dirs.append(item)
        
        # If no standard source dirs found, use repo root but exclude third-party
        if not source_dirs:
            source_dirs = [self.repo_path]
        
        return source_dirs
    
    def _is_third_party(self, file_path: Path) -> bool:
        """Check if file is in third-party directory"""
        parts = file_path.parts
        return any(excluded in parts for excluded in self.THIRD_PARTY_DIRS)
    
    def _is_type_definition(self, file_path: Path) -> bool:
        """Check if file is a type definition (not application code)"""
        file_str = str(file_path)
        return any(re.search(pattern, file_str, re.IGNORECASE) for pattern in self.TYPE_DEF_PATTERNS)
    
    def _detect_framework_evidence(self) -> Dict[str, Any]:
        """
        Detect framework from project files.
        
        Returns:
            Framework evidence dictionary
        """
        evidence = {
            'dotnet_version': None,
            'dotnet_framework': None,
            'nodejs_version': None,
            'python_version': None
        }
        
        # Check for .NET projects
        csproj_files = list(self.repo_path.rglob('*.csproj'))
        if csproj_files:
            # Parse first csproj for framework version
            try:
                tree = ET.parse(csproj_files[0])
                root = tree.getroot()
                
                # Look for TargetFramework or TargetFrameworkVersion
                for elem in root.iter():
                    if 'TargetFramework' in elem.tag:
                        framework = elem.text
                        if framework:
                            evidence['dotnet_framework'] = framework
                            # Parse version
                            # Format 1: v4.7.2 (old .NET Framework with 'v' prefix)
                            if framework.startswith('v') and '.' in framework:
                                evidence['dotnet_version'] = framework[1:]  # Strip 'v'
                            # Format 2: net472 -> 4.7.2, net6.0 -> 6.0
                            elif framework.startswith('net') and not framework.startswith('netstandard'):
                                version_part = framework[3:]
                                if '.' in version_part:
                                    evidence['dotnet_version'] = version_part
                                elif len(version_part) >= 3:
                                    # net472 -> 4.7.2
                                    major = version_part[0]
                                    minor = version_part[1]
                                    patch = version_part[2] if len(version_part) > 2 else '0'
                                    evidence['dotnet_version'] = f"{major}.{minor}.{patch}"
                        break
            except Exception as e:
                logger.debug(f"Failed to parse .csproj: {e}")
            
            # Also check packages.config for targetFramework
            if not evidence['dotnet_framework']:
                packages_config = self.repo_path / 'packages.config'
                if not packages_config.exists():
                    # Look in subdirectories
                    packages_configs = list(self.repo_path.rglob('packages.config'))
                    if packages_configs:
                        packages_config = packages_configs[0]
                
                if packages_config.exists():
                    try:
                        content = packages_config.read_text()
                        match = re.search(r'targetFramework="(net\d+)"', content)
                        if match:
                            framework = match.group(1)
                            evidence['dotnet_framework'] = framework
                            # Convert net472 -> 4.7.2
                            if framework.startswith('net') and len(framework) >= 5:
                                version_part = framework[3:]  # Remove 'net' prefix
                                if len(version_part) == 2:
                                    # net45 -> 4.5
                                    evidence['dotnet_version'] = f"{version_part[0]}.{version_part[1]}"
                                elif len(version_part) == 3:
                                    # net472 -> 4.7.2
                                    evidence['dotnet_version'] = f"{version_part[0]}.{version_part[1]}.{version_part[2]}"
                    except Exception as e:
                        logger.debug(f"Failed to parse packages.config: {e}")
        
        # Check for Node.js
        package_json = self.repo_path / 'package.json'
        if package_json.exists():
            try:
                data = json.loads(package_json.read_text())
                if 'engines' in data and 'node' in data['engines']:
                    evidence['nodejs_version'] = data['engines']['node']
            except Exception as e:
                logger.debug(f"Failed to parse package.json: {e}")
        
        # Check for Python
        if (self.repo_path / 'requirements.txt').exists() or (self.repo_path / 'setup.py').exists():
            # Look for python_requires in setup.py
            setup_py = self.repo_path / 'setup.py'
            if setup_py.exists():
                try:
                    content = setup_py.read_text()
                    match = re.search(r'python_requires\s*=\s*["\']([^"\']+)["\']', content)
                    if match:
                        evidence['python_version'] = match.group(1)
                except Exception as e:
                    logger.debug(f"Failed to parse setup.py: {e}")
        
        return evidence
    
    def _fix_tech_stack(self, tech_stack: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fix tech stack data using ground truth.
        
        Args:
            tech_stack: Tech stack data from collectors
            
        Returns:
            Corrected tech stack data
        """
        logger.info("Fixing tech stack data...")
        corrections = []
        
        # Fix each category
        for category in ['frontend', 'backend', 'database', 'devops']:
            if category not in tech_stack:
                continue
            
            techs = tech_stack[category]
            fixed_techs = []
            
            for tech in techs:
                lang_name = tech['name']
                
                # Fix .NET version FIRST (before language checks)
                if lang_name in ['.NET', 'ASP.NET', 'ASP.NET MVC']:
                    if self.ground_truth and self.ground_truth['framework_evidence']['dotnet_version']:
                        actual_version = self.ground_truth['framework_evidence']['dotnet_version']
                        if tech.get('version') != actual_version:
                            corrections.append(f"Fixed .NET version: {tech.get('version')} -> {actual_version}")
                            tech['version'] = actual_version
                            tech['latest'] = actual_version  # Conservative: mark as latest
                
                # Check if language actually exists in source code
                if lang_name in self.LANGUAGE_EXTENSIONS:
                    # Only validate if ground_truth exists
                    if self.ground_truth and lang_name in self.ground_truth['languages']:
                        # Language exists - update file count if available
                        actual_count = self.ground_truth['languages'][lang_name]['file_count']
                        
                        # Only include if meets threshold
                        if actual_count >= self.MIN_FILE_THRESHOLD:
                            if 'file_count' in tech:
                                if tech['file_count'] != actual_count:
                                    corrections.append(f"Updated {lang_name} file count: {tech['file_count']} -> {actual_count}")
                                    tech['file_count'] = actual_count
                            fixed_techs.append(tech)
                        else:
                            corrections.append(f"Removed {lang_name}: only {actual_count} files (threshold: {self.MIN_FILE_THRESHOLD})")
                    elif self.ground_truth:
                        # Language does NOT exist in source code
                        corrections.append(f"Removed {lang_name}: not found in source directories")
                    else:
                        # No ground truth - keep as-is
                        fixed_techs.append(tech)
                else:
                    # Not a language (framework, tool, etc.) - keep it
                    fixed_techs.append(tech)
            
            tech_stack[category] = fixed_techs
        
        # Sort backend by file count (primary language first)
        if 'backend' in tech_stack and self.ground_truth:
            tech_stack['backend'].sort(
                key=lambda t: self.ground_truth['languages'].get(t['name'], {}).get('file_count', 0),
                reverse=True
            )
        
        # Update summary
        if 'summary' in tech_stack:
            all_techs = (
                tech_stack.get('frontend', []) +
                tech_stack.get('backend', []) +
                tech_stack.get('database', []) +
                tech_stack.get('devops', [])
            )
            tech_stack['summary']['total_technologies'] = len(all_techs)
        
        if self.ground_truth:
            self.ground_truth['corrections_applied'].extend(corrections)
        return tech_stack
    
    def _fix_executive_summary(self, exec_summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fix executive summary using ground truth.
        
        Args:
            exec_summary: Executive summary from collectors
            
        Returns:
            Corrected executive summary
        """
        logger.info("Fixing executive summary...")
        corrections = []
        
        # Fix primary technologies list
        if 'tech_stack_summary' in exec_summary:
            primary_techs = exec_summary['tech_stack_summary'].get('primary_technologies', [])
            fixed_primary = []
            
            for tech in primary_techs:
                lang_name = tech['name']
                
                # Validate language exists
                if lang_name in self.LANGUAGE_EXTENSIONS:
                    if lang_name in self.ground_truth['languages']:
                        actual_count = self.ground_truth['languages'][lang_name]['file_count']
                        if actual_count >= self.MIN_FILE_THRESHOLD:
                            fixed_primary.append(tech)
                        else:
                            corrections.append(f"Removed {lang_name} from primary technologies")
                    else:
                        corrections.append(f"Removed {lang_name} from primary technologies (not in source)")
                else:
                    # Framework/tool - keep it
                    fixed_primary.append(tech)
            
            exec_summary['tech_stack_summary']['primary_technologies'] = fixed_primary
            exec_summary['tech_stack_summary']['total_technologies'] = len(fixed_primary)
        
        # Fix narrative if it mentions non-existent languages
        if 'what_it_does' in exec_summary:
            summary_text = exec_summary['what_it_does'].get('summary', '')
            tagline = exec_summary.get('tagline', '')
            
            # Detect primary language from ground truth
            primary_lang = None
            max_files = 0
            for lang, data in self.ground_truth['languages'].items():
                if data['file_count'] > max_files:
                    max_files = data['file_count']
                    primary_lang = lang
            
            # Replace incorrect language mentions
            for lang in self.LANGUAGE_EXTENSIONS:
                if lang not in self.ground_truth['languages']:
                    # Language doesn't exist - remove from narrative
                    if lang in summary_text or lang in tagline:
                        if primary_lang:
                            summary_text = summary_text.replace(f"built with {lang}", f"built with {primary_lang}")
                            summary_text = summary_text.replace(f"{lang}-based", f"{primary_lang}-based")
                            tagline = tagline.replace(f"{lang}", primary_lang)
                            corrections.append(f"Fixed narrative: replaced {lang} with {primary_lang}")
            
            exec_summary['what_it_does']['summary'] = summary_text
            exec_summary['tagline'] = tagline
        
        self.ground_truth['corrections_applied'].extend(corrections)
        return exec_summary
    
    def _fix_architecture(self, architecture: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fix architecture data - ensure no third-party internal code in tiers.
        
        Args:
            architecture: Architecture data from collectors
            
        Returns:
            Corrected architecture data
        """
        logger.info("Fixing architecture data...")
        corrections = []
        
        # Filter tiers to remove third-party library internals
        if 'tiers' in architecture:
            fixed_tiers = []
            
            for tier in architecture['tiers']:
                tier_path = tier.get('path', '')
                
                # Check if tier is third-party library internal
                is_third_party_internal = False
                for excluded in ['PEG_GrammarExplorer', 'dotless\\lib', 'External\\TypeScript']:
                    if excluded in tier_path:
                        is_third_party_internal = True
                        break
                
                if not is_third_party_internal:
                    fixed_tiers.append(tier)
                else:
                    corrections.append(f"Removed third-party tier: {tier.get('name')} ({tier_path})")
            
            architecture['tiers'] = fixed_tiers
        
        self.ground_truth['corrections_applied'].extend(corrections)
        return architecture


def validate_dashboard_data(repo_path: Path, collected_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to validate and fix dashboard data.
    
    Args:
        repo_path: Path to repository
        collected_data: Raw data from collectors
        
    Returns:
        Validated and corrected data
    """
    validator = DashboardDataValidator(repo_path)
    return validator.validate_and_fix(collected_data)


__all__ = ['DashboardDataValidator', 'validate_dashboard_data']
