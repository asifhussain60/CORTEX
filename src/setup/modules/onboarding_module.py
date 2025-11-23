"""
Onboarding Module - Analyzes user's application and suggests improvements

Responsibilities:
1. Crawl user's codebase (triggered after setup completes)
2. Analyze project structure, tech stack, testing infrastructure
3. Generate onboarding analysis document
4. Ask intelligent improvement questions
5. Store analysis in CORTEX brain for future reference

This module brings the "onboard application" workflow into automated setup.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime

from ..base_setup_module import (
    BaseSetupModule,
    SetupModuleMetadata,
    SetupResult,
    SetupStatus,
    SetupPhase
)


class OnboardingModule(BaseSetupModule):
    """
    Automatically onboard user's application after CORTEX setup.
    
    This module replicates the manual "onboard application" workflow
    by analyzing the codebase and generating actionable insights.
    
    Workflow:
    1. Detect project structure (solution files, package.json, etc.)
    2. Analyze tech stack (languages, frameworks, tools)
    3. Scan testing infrastructure (test directories, coverage tools)
    4. Identify improvement opportunities
    5. Generate onboarding analysis document
    6. Store findings in CORTEX brain
    
    Output:
    - Markdown analysis document in cortex-brain/documents/analysis/
    - Quick wins, testing recommendations, documentation gaps
    - Actionable improvement phases
    """
    
    def get_metadata(self) -> SetupModuleMetadata:
        """Return module metadata."""
        return SetupModuleMetadata(
            module_id="onboarding",
            name="Application Onboarding",
            description="Analyze user's application and generate improvement recommendations",
            phase=SetupPhase.POST_SETUP,
            priority=10,  # Run early in post-setup
            dependencies=["brain_initialization"],
            optional=True,  # Can skip if brain not initialized
            enabled_by_default=True
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate prerequisites for onboarding.
        
        Args:
            context: Must contain 'project_root', 'user_project_root', 'brain_initialized'
        
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        # Check user project root exists
        user_root = context.get('user_project_root')
        if not user_root:
            issues.append("user_project_root not found in context")
        elif not Path(user_root).exists():
            issues.append(f"User project root does not exist: {user_root}")
        
        # Check brain is initialized
        if not context.get('brain_initialized'):
            issues.append("CORTEX brain not initialized - cannot store onboarding data")
        
        # Check documents directory exists
        project_root = context.get('project_root')
        if project_root:
            docs_path = Path(project_root) / 'cortex-brain' / 'documents' / 'analysis'
            if not docs_path.exists():
                try:
                    docs_path.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    issues.append(f"Cannot create analysis directory: {e}")
        
        return len(issues) == 0, issues
    
    def execute(self, context: Dict[str, Any]) -> SetupResult:
        """
        Execute onboarding analysis.
        
        Args:
            context: Shared context with paths and setup results
        
        Returns:
            SetupResult with analysis details
        """
        try:
            user_root = Path(context.get('user_project_root', context['project_root']))
            project_root = Path(context['project_root'])
            
            self.log_info(f"Starting onboarding analysis for: {user_root.name}")
            
            # Step 1: Detect project structure
            project_info = self._detect_project_structure(user_root)
            self.log_info(f"Detected project type: {project_info.get('project_type', 'unknown')}")
            
            # Step 2: Analyze tech stack
            tech_stack = self._analyze_tech_stack(user_root, project_info)
            self.log_info(f"Tech stack: {', '.join(tech_stack.get('languages', []))}")
            
            # Step 3: Scan testing infrastructure
            testing_info = self._analyze_testing_infrastructure(user_root, project_info)
            self.log_info(f"Testing infrastructure: {testing_info.get('status', 'unknown')}")
            
            # Step 4: Identify improvement opportunities
            improvements = self._identify_improvements(user_root, project_info, tech_stack, testing_info)
            self.log_info(f"Found {len(improvements)} improvement opportunities")
            
            # Step 5: Generate onboarding document
            analysis_path = self._generate_onboarding_document(
                project_root, user_root, project_info, tech_stack, testing_info, improvements
            )
            self.log_info(f"Generated onboarding analysis: {analysis_path}")
            
            # Step 6: Store in context for other modules
            context['onboarding_complete'] = True
            context['onboarding_analysis_path'] = str(analysis_path)
            context['improvement_count'] = len(improvements)
            
            return SetupResult(
                module_id=self.metadata.module_id,
                status=SetupStatus.SUCCESS,
                message=f"Onboarding complete - {len(improvements)} improvement opportunities identified",
                details={
                    'analysis_path': str(analysis_path),
                    'project_name': user_root.name,
                    'project_type': project_info.get('project_type'),
                    'languages': tech_stack.get('languages', []),
                    'improvement_count': len(improvements)
                }
            )
        
        except Exception as e:
            self.log_error(f"Onboarding failed: {e}")
            return SetupResult(
                module_id=self.metadata.module_id,
                status=SetupStatus.FAILED,
                message=f"Onboarding analysis failed: {str(e)}",
                errors=[str(e)]
            )
    
    def _detect_project_structure(self, user_root: Path) -> Dict[str, Any]:
        """
        Detect project structure and type.
        
        Args:
            user_root: User's project root
        
        Returns:
            Dictionary with project info
        """
        info = {
            'project_name': user_root.name,
            'project_type': 'unknown',
            'entry_points': [],
            'config_files': []
        }
        
        # Check for .NET solution
        sln_files = list(user_root.glob('*.sln'))
        if sln_files:
            info['project_type'] = 'dotnet'
            info['entry_points'].extend([str(f.relative_to(user_root)) for f in sln_files])
        
        # Check for Node.js project
        if (user_root / 'package.json').exists():
            info['project_type'] = 'nodejs' if info['project_type'] == 'unknown' else 'dotnet+nodejs'
            info['config_files'].append('package.json')
        
        # Check for Python project
        if (user_root / 'requirements.txt').exists() or (user_root / 'setup.py').exists():
            info['project_type'] = 'python' if info['project_type'] == 'unknown' else f"{info['project_type']}+python"
            if (user_root / 'requirements.txt').exists():
                info['config_files'].append('requirements.txt')
        
        return info
    
    def _analyze_tech_stack(self, user_root: Path, project_info: Dict) -> Dict[str, Any]:
        """
        Analyze technology stack.
        
        Args:
            user_root: User's project root
            project_info: Project structure info
        
        Returns:
            Dictionary with tech stack details
        """
        tech_stack = {
            'languages': [],
            'frameworks': [],
            'tools': []
        }
        
        # Detect languages
        if project_info['project_type'] in ['dotnet', 'dotnet+nodejs']:
            tech_stack['languages'].append('C#')
            tech_stack['frameworks'].append('ASP.NET Core')
        
        if 'nodejs' in project_info['project_type']:
            tech_stack['languages'].append('TypeScript/JavaScript')
            
            # Check package.json for frameworks
            package_json = user_root / 'package.json'
            if package_json.exists():
                try:
                    pkg_data = json.loads(package_json.read_text())
                    deps = {**pkg_data.get('dependencies', {}), **pkg_data.get('devDependencies', {})}
                    
                    if 'react' in deps:
                        tech_stack['frameworks'].append('React')
                    if 'vue' in deps:
                        tech_stack['frameworks'].append('Vue')
                    if 'angular' in deps:
                        tech_stack['frameworks'].append('Angular')
                    if 'next' in deps:
                        tech_stack['frameworks'].append('Next.js')
                except Exception:
                    pass
        
        if 'python' in project_info['project_type']:
            tech_stack['languages'].append('Python')
        
        # Detect tools
        if (user_root / '.editorconfig').exists():
            tech_stack['tools'].append('EditorConfig')
        if (user_root / '.eslintrc.js').exists() or (user_root / 'eslint.config.mjs').exists():
            tech_stack['tools'].append('ESLint')
        if (user_root / '.prettierrc').exists():
            tech_stack['tools'].append('Prettier')
        
        return tech_stack
    
    def _analyze_testing_infrastructure(self, user_root: Path, project_info: Dict) -> Dict[str, Any]:
        """
        Analyze testing infrastructure.
        
        Args:
            user_root: User's project root
            project_info: Project structure info
        
        Returns:
            Dictionary with testing info
        """
        testing = {
            'status': 'unknown',
            'test_frameworks': [],
            'test_directories': [],
            'coverage_tools': []
        }
        
        # Find test directories
        test_dirs = []
        for pattern in ['**/Tests/**', '**/test/**', '**/tests/**', '**/__tests__/**']:
            test_dirs.extend(user_root.glob(pattern))
        
        testing['test_directories'] = [str(d.relative_to(user_root)) for d in test_dirs[:10]]  # Limit to 10
        
        if test_dirs:
            testing['status'] = 'present'
        else:
            testing['status'] = 'missing'
            return testing
        
        # Detect test frameworks
        if project_info['project_type'] in ['dotnet', 'dotnet+nodejs']:
            # Check for C# test projects
            for test_dir in test_dirs:
                csproj_files = list(test_dir.glob('*.csproj'))
                for csproj in csproj_files:
                    content = csproj.read_text()
                    if 'xunit' in content.lower():
                        testing['test_frameworks'].append('xUnit')
                    elif 'nunit' in content.lower():
                        testing['test_frameworks'].append('NUnit')
                    elif 'mstest' in content.lower():
                        testing['test_frameworks'].append('MSTest')
        
        # Check package.json for JS/TS test frameworks
        package_json = user_root / 'package.json'
        if package_json.exists():
            try:
                pkg_data = json.loads(package_json.read_text())
                deps = {**pkg_data.get('dependencies', {}), **pkg_data.get('devDependencies', {})}
                
                if 'jest' in deps:
                    testing['test_frameworks'].append('Jest')
                if 'vitest' in deps:
                    testing['test_frameworks'].append('Vitest')
                if 'playwright' in deps or '@playwright/test' in deps:
                    testing['test_frameworks'].append('Playwright')
                
                # Coverage tools
                if 'coverage' in str(pkg_data.get('scripts', {})):
                    testing['coverage_tools'].append('Jest Coverage')
            except Exception:
                pass
        
        testing['test_frameworks'] = list(set(testing['test_frameworks']))
        return testing
    
    def _identify_improvements(
        self, user_root: Path, project_info: Dict, tech_stack: Dict, testing: Dict
    ) -> List[Dict[str, Any]]:
        """
        Identify improvement opportunities.
        
        Args:
            user_root: User's project root
            project_info: Project structure
            tech_stack: Tech stack details
            testing: Testing infrastructure
        
        Returns:
            List of improvement recommendations
        """
        improvements = []
        
        # Code quality improvements
        if '.editorconfig' not in [f for f in project_info.get('config_files', [])]:
            improvements.append({
                'category': 'Code Quality',
                'title': 'Add .editorconfig',
                'description': 'Create .editorconfig for consistent formatting across team',
                'effort': 'low',
                'impact': 'medium'
            })
        
        if 'ESLint' not in tech_stack.get('tools', []) and 'TypeScript/JavaScript' in tech_stack.get('languages', []):
            improvements.append({
                'category': 'Code Quality',
                'title': 'Add ESLint',
                'description': 'Configure ESLint for TypeScript/JavaScript code quality',
                'effort': 'low',
                'impact': 'high'
            })
        
        # Testing improvements
        if testing['status'] == 'missing':
            improvements.append({
                'category': 'Testing',
                'title': 'Add Test Infrastructure',
                'description': 'No test directories found - set up testing framework',
                'effort': 'high',
                'impact': 'critical'
            })
        elif not testing.get('coverage_tools'):
            improvements.append({
                'category': 'Testing',
                'title': 'Add Code Coverage',
                'description': 'Enable code coverage collection and reporting',
                'effort': 'low',
                'impact': 'high'
            })
        
        # Documentation improvements
        readme_exists = (user_root / 'README.md').exists()
        if not readme_exists:
            improvements.append({
                'category': 'Documentation',
                'title': 'Add README.md',
                'description': 'Create README with project overview and setup instructions',
                'effort': 'medium',
                'impact': 'high'
            })
        
        return improvements
    
    def _generate_onboarding_document(
        self,
        project_root: Path,
        user_root: Path,
        project_info: Dict,
        tech_stack: Dict,
        testing: Dict,
        improvements: List[Dict]
    ) -> Path:
        """
        Generate onboarding analysis markdown document.
        
        Args:
            project_root: CORTEX project root
            user_root: User's project root
            project_info: Project structure
            tech_stack: Tech stack details
            testing: Testing infrastructure
            improvements: Improvement recommendations
        
        Returns:
            Path to generated document
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{user_root.name}-onboarding-analysis-{timestamp}.md"
        analysis_path = project_root / 'cortex-brain' / 'documents' / 'analysis' / filename
        
        # Generate markdown content
        content = f"""# CORTEX Onboarding Analysis: {user_root.name}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Project Type:** {project_info.get('project_type', 'Unknown')}  
**CORTEX Module:** Automatic Onboarding

---

## 📊 Project Overview

**Project Name:** {user_root.name}  
**Project Type:** {project_info.get('project_type', 'Unknown')}  
**Languages:** {', '.join(tech_stack.get('languages', ['None detected']))}  
**Frameworks:** {', '.join(tech_stack.get('frameworks', ['None detected']))}

---

## 🔍 Analysis Summary

### Tech Stack
{self._format_tech_stack(tech_stack)}

### Testing Infrastructure
{self._format_testing_info(testing)}

### Code Quality Tools
{self._format_tools(tech_stack.get('tools', []))}

---

## ✅ Improvement Opportunities

Found **{len(improvements)}** improvement opportunities:

"""
        
        # Group improvements by category
        by_category = {}
        for imp in improvements:
            category = imp['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(imp)
        
        for category, items in by_category.items():
            content += f"\n### {category}\n\n"
            for item in items:
                content += f"**{item['title']}**  \n"
                content += f"{item['description']}  \n"
                content += f"*Effort: {item['effort']} | Impact: {item['impact']}*\n\n"
        
        content += """
---

## 🚀 Next Steps

CORTEX can help implement these improvements. Just ask:

- "Create .editorconfig for this project"
- "Set up Jest with React Testing Library"
- "Add ESLint configuration"
- "Generate README.md"

Or say **"let's plan a feature"** to start structured development with DoR/DoD enforcement.

---

**Author:** CORTEX Onboarding Module  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.
"""
        
        analysis_path.write_text(content, encoding='utf-8')
        return analysis_path
    
    def _format_tech_stack(self, tech_stack: Dict) -> str:
        """Format tech stack for markdown."""
        lines = []
        if tech_stack.get('languages'):
            lines.append(f"- **Languages:** {', '.join(tech_stack['languages'])}")
        if tech_stack.get('frameworks'):
            lines.append(f"- **Frameworks:** {', '.join(tech_stack['frameworks'])}")
        return '\n'.join(lines) if lines else "- No tech stack detected"
    
    def _format_testing_info(self, testing: Dict) -> str:
        """Format testing info for markdown."""
        status = testing.get('status', 'unknown')
        if status == 'missing':
            return "- ⚠️ **No test infrastructure found**"
        
        lines = [f"- **Status:** {status.capitalize()}"]
        if testing.get('test_frameworks'):
            lines.append(f"- **Frameworks:** {', '.join(testing['test_frameworks'])}")
        if testing.get('test_directories'):
            lines.append(f"- **Test Directories:** {len(testing['test_directories'])} found")
        if testing.get('coverage_tools'):
            lines.append(f"- **Coverage:** {', '.join(testing['coverage_tools'])}")
        else:
            lines.append("- ⚠️ **Coverage:** Not configured")
        
        return '\n'.join(lines)
    
    def _format_tools(self, tools: List[str]) -> str:
        """Format tools for markdown."""
        if not tools:
            return "- No code quality tools detected"
        return '\n'.join([f"- {tool}" for tool in tools])
    
    def rollback(self, context: Dict[str, Any]) -> bool:
        """
        Rollback onboarding (delete analysis document).
        
        Returns:
            True if rollback successful
        """
        analysis_path = context.get('onboarding_analysis_path')
        if analysis_path and Path(analysis_path).exists():
            try:
                Path(analysis_path).unlink()
                self.log_info(f"Deleted onboarding analysis: {analysis_path}")
            except Exception as e:
                self.log_warning(f"Could not delete analysis document: {e}")
        
        return True
