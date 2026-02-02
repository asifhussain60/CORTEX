"""
Business Language Orchestrator for Repository Analysis.

Generates comprehensive business narratives, use cases, and descriptions
from repository analysis with confidence scoring.

Authority: cortex-architect.prompt.md v8.0
Author: Asif Hussain
AC-ID: AC-UNIVERSAL-ONBOARD-003
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class ConfidenceScore:
    """
    Confidence score with evidence tracking.
    
    Attributes:
        score: 0-100 confidence percentage
        level: 'high', 'medium', 'low'
        evidence: List of evidence sources
        assumptions: List of assumptions made
    """
    score: int
    level: str
    evidence: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    
    @classmethod
    def from_evidence(cls, evidence_count: int, assumption_count: int) -> 'ConfidenceScore':
        """Calculate confidence from evidence vs assumptions."""
        if evidence_count == 0 and assumption_count == 0:
            return cls(score=0, level='low', evidence=[], assumptions=['No data available'])
        
        total = evidence_count + assumption_count
        score = int((evidence_count / total) * 100) if total > 0 else 0
        
        if score >= 70:
            level = 'high'
        elif score >= 40:
            level = 'medium'
        else:
            level = 'low'
        
        return cls(score=score, level=level)


@dataclass
class UseCase:
    """
    Business use case extracted from repository.
    
    Attributes:
        title: Use case name
        description: Detailed description
        actors: Users/systems involved
        icon: Emoji icon
        evidence_files: Files supporting this use case
        confidence: Confidence score
    """
    title: str
    description: str
    actors: List[str] = field(default_factory=list)
    icon: str = "📋"
    evidence_files: List[str] = field(default_factory=list)
    confidence: ConfidenceScore = field(default_factory=lambda: ConfidenceScore(0, 'low'))


@dataclass
class BusinessNarrative:
    """
    Complete business narrative for a repository.
    
    Attributes:
        name: Repository/project name
        title: Display title
        tagline: Short tagline
        description: Comprehensive description
        use_cases: Primary use cases
        tech_stack: Technologies detected
        architecture_summary: Architecture overview
        target_users: Primary users
        confidence: Overall confidence
        evidence_map: Map of claims to evidence
    """
    name: str
    title: str
    tagline: str
    description: str
    use_cases: List[UseCase] = field(default_factory=list)
    tech_stack: List[Dict[str, Any]] = field(default_factory=list)
    architecture_summary: str = ""
    target_users: List[str] = field(default_factory=list)
    confidence: ConfidenceScore = field(default_factory=lambda: ConfidenceScore(0, 'low'))
    evidence_map: Dict[str, List[str]] = field(default_factory=dict)


class BusinessLanguageOrchestrator:
    """
    Generate comprehensive business narratives from repository analysis.
    
    Features:
    - Intelligent narrative generation from code analysis
    - Use case extraction from features/APIs
    - Confidence scoring with evidence tracking
    - Collapsible file references for transparency
    
    Example:
        >>> orchestrator = BusinessLanguageOrchestrator()
        >>> narrative = orchestrator.generate_narrative(repo_path, analysis_data)
        >>> print(f"Title: {narrative.title}")
        >>> print(f"Confidence: {narrative.confidence.score}%")
    """
    
    # Technology detection patterns
    TECH_PATTERNS = {
        "ASP.NET": {
            "patterns": [r"\.aspx$", r"\.ascx$", r"Web\.config", r"System\.Web"],
            "icon": "🔷",
            "category": "framework",
        },
        "ASP.NET MVC": {
            "patterns": [r"Controller\.cs$", r"Views/", r"RouteConfig"],
            "icon": "🔷",
            "category": "framework",
        },
        "ASP.NET Core": {
            "patterns": [r"appsettings\.json", r"Startup\.cs", r"Program\.cs.*WebApplication"],
            "icon": "🔷",
            "category": "framework",
        },
        "VB.NET": {
            "patterns": [r"\.vb$", r"\.vbproj$"],
            "icon": "🟦",
            "category": "language",
        },
        "C#": {
            "patterns": [r"\.cs$", r"\.csproj$"],
            "icon": "🟪",
            "category": "language",
        },
        "SQL Server": {
            "patterns": [r"\.sql$", r"SqlConnection", r"SqlCommand", r"Data Source="],
            "icon": "🗄️",
            "category": "database",
        },
        "Entity Framework": {
            "patterns": [r"DbContext", r"DbSet", r"\.edmx$"],
            "icon": "📊",
            "category": "orm",
        },
        "jQuery": {
            "patterns": [r"jquery", r"\$\(", r"\.ajax\("],
            "icon": "📜",
            "category": "frontend",
        },
        "Bootstrap": {
            "patterns": [r"bootstrap", r"class=\".*btn.*\"", r"class=\".*container.*\""],
            "icon": "🎨",
            "category": "frontend",
        },
        "Python": {
            "patterns": [r"\.py$", r"requirements\.txt", r"setup\.py"],
            "icon": "🐍",
            "category": "language",
        },
        "FastAPI": {
            "patterns": [r"from fastapi", r"FastAPI\(\)", r"@app\.get"],
            "icon": "⚡",
            "category": "framework",
        },
        "Django": {
            "patterns": [r"from django", r"INSTALLED_APPS", r"urlpatterns"],
            "icon": "🎸",
            "category": "framework",
        },
        "React": {
            "patterns": [r"from ['\"]react['\"]", r"useState", r"useEffect"],
            "icon": "⚛️",
            "category": "frontend",
        },
        "Node.js": {
            "patterns": [r"package\.json", r"require\(", r"module\.exports"],
            "icon": "🟢",
            "category": "runtime",
        },
    }
    
    # Use case extraction patterns
    USE_CASE_PATTERNS = {
        "authentication": {
            "patterns": [r"login", r"logout", r"auth", r"password", r"signin", r"signup"],
            "title": "User Authentication",
            "icon": "🔐",
            "description_template": "Secure user authentication with {features}",
        },
        "crud": {
            "patterns": [r"create", r"update", r"delete", r"edit", r"add", r"remove"],
            "title": "Data Management",
            "icon": "📝",
            "description_template": "CRUD operations for {entities}",
        },
        "search": {
            "patterns": [r"search", r"find", r"query", r"filter", r"browse"],
            "title": "Search & Discovery",
            "icon": "🔍",
            "description_template": "Search functionality for {entities}",
        },
        "reporting": {
            "patterns": [r"report", r"dashboard", r"analytics", r"statistics", r"metrics"],
            "title": "Reporting & Analytics",
            "icon": "📊",
            "description_template": "Analytics and reporting for {metrics}",
        },
        "notification": {
            "patterns": [r"email", r"notification", r"alert", r"message", r"notify"],
            "title": "Notifications",
            "icon": "🔔",
            "description_template": "Notification system via {channels}",
        },
        "file_management": {
            "patterns": [r"upload", r"download", r"file", r"document", r"attachment"],
            "title": "File Management",
            "icon": "📁",
            "description_template": "File upload and management for {types}",
        },
        "scheduling": {
            "patterns": [r"calendar", r"schedule", r"event", r"booking", r"appointment"],
            "title": "Scheduling",
            "icon": "📅",
            "description_template": "Scheduling and calendar management",
        },
        "api": {
            "patterns": [r"api/", r"endpoint", r"rest", r"graphql", r"webservice"],
            "title": "API Services",
            "icon": "🔌",
            "description_template": "API endpoints for {services}",
        },
    }
    
    def __init__(self):
        """Initialize Business Language Orchestrator."""
        self.logger = logging.getLogger(__name__)
    
    def generate_narrative(
        self,
        repo_path: Path,
        analysis_data: Dict[str, Any],
    ) -> BusinessNarrative:
        """
        Generate comprehensive business narrative from analysis data.
        
        Args:
            repo_path: Path to repository
            analysis_data: Data from LENS analysis
            
        Returns:
            BusinessNarrative with use cases and confidence scores
        """
        self.logger.info(f"Generating narrative for: {repo_path}")
        
        # Gather evidence
        files = self._scan_repository_files(repo_path)
        readme_content = self._read_readme(repo_path)
        config_data = analysis_data.get("config_analysis", {})
        code_data = analysis_data.get("code_analysis", {})
        
        # Detect technology stack
        tech_stack = self._detect_tech_stack(repo_path, files)
        
        # Extract use cases
        use_cases = self._extract_use_cases(repo_path, files, analysis_data)
        
        # Generate project description
        project_name = repo_path.name
        description, desc_confidence = self._generate_description(
            project_name, readme_content, tech_stack, use_cases, files
        )
        
        # Generate tagline
        tagline = self._generate_tagline(project_name, tech_stack, use_cases)
        
        # Generate architecture summary
        arch_summary = self._generate_architecture_summary(
            repo_path, files, tech_stack, analysis_data
        )
        
        # Identify target users
        target_users = self._identify_target_users(use_cases, readme_content)
        
        # Calculate overall confidence
        evidence_count = len([uc for uc in use_cases if uc.confidence.level == 'high'])
        assumption_count = len([uc for uc in use_cases if uc.confidence.level == 'low'])
        overall_confidence = ConfidenceScore.from_evidence(evidence_count, assumption_count)
        overall_confidence.evidence = [f"Analyzed {len(files)} files"]
        if readme_content:
            overall_confidence.evidence.append("README.md found")
            overall_confidence.score = min(100, overall_confidence.score + 10)
        
        # Build evidence map
        evidence_map = self._build_evidence_map(use_cases, tech_stack)
        
        return BusinessNarrative(
            name=project_name,
            title=project_name.upper(),
            tagline=tagline,
            description=description,
            use_cases=use_cases,
            tech_stack=tech_stack,
            architecture_summary=arch_summary,
            target_users=target_users,
            confidence=overall_confidence,
            evidence_map=evidence_map,
        )
    
    def _scan_repository_files(self, repo_path: Path) -> List[Path]:
        """Scan repository for relevant files."""
        files = []
        try:
            for pattern in ["**/*.cs", "**/*.vb", "**/*.py", "**/*.js", "**/*.aspx", 
                          "**/*.config", "**/*.json", "**/*.xml", "**/*.sql"]:
                files.extend(repo_path.glob(pattern))
        except Exception as e:
            self.logger.warning(f"File scan error: {e}")
        return files[:500]  # Limit for performance
    
    def _read_readme(self, repo_path: Path) -> str:
        """Read README file content."""
        for name in ["README.md", "readme.md", "README.txt", "README"]:
            readme_path = repo_path / name
            if readme_path.exists():
                try:
                    return readme_path.read_text(encoding='utf-8', errors='ignore')[:5000]
                except (OSError, IOError, UnicodeDecodeError):
                    pass
        return ""
    
    def _detect_tech_stack(
        self,
        repo_path: Path,
        files: List[Path],
    ) -> List[Dict[str, Any]]:
        """Detect technology stack from files."""
        detected = []
        file_contents_cache = {}
        
        for tech_name, tech_info in self.TECH_PATTERNS.items():
            evidence_files = []
            
            for file_path in files:
                rel_path = str(file_path.relative_to(repo_path))
                
                for pattern in tech_info["patterns"]:
                    # Check filename
                    if re.search(pattern, rel_path, re.IGNORECASE):
                        evidence_files.append(rel_path)
                        break
                    
                    # Check file content for small files
                    if file_path.suffix in ['.cs', '.vb', '.py', '.js', '.config', '.json']:
                        if rel_path not in file_contents_cache:
                            try:
                                content = file_path.read_text(encoding='utf-8', errors='ignore')[:2000]
                                file_contents_cache[rel_path] = content
                            except (OSError, IOError, UnicodeDecodeError):
                                file_contents_cache[rel_path] = ""
                        
                        if re.search(pattern, file_contents_cache[rel_path], re.IGNORECASE):
                            evidence_files.append(rel_path)
                            break
            
            if evidence_files:
                detected.append({
                    "name": tech_name,
                    "icon": tech_info["icon"],
                    "category": tech_info["category"],
                    "evidence_count": len(set(evidence_files)),
                    "evidence_files": list(set(evidence_files))[:5],
                    "confidence": "high" if len(set(evidence_files)) >= 3 else "medium",
                })
        
        # Sort by evidence count
        detected.sort(key=lambda x: x["evidence_count"], reverse=True)
        return detected
    
    def _extract_use_cases(
        self,
        repo_path: Path,
        files: List[Path],
        analysis_data: Dict[str, Any],
    ) -> List[UseCase]:
        """Extract business use cases from repository."""
        use_cases = []
        
        for uc_key, uc_info in self.USE_CASE_PATTERNS.items():
            evidence_files = []
            features_found = []
            
            for file_path in files:
                rel_path = str(file_path.relative_to(repo_path))
                file_name = file_path.stem.lower()
                
                for pattern in uc_info["patterns"]:
                    if re.search(pattern, file_name, re.IGNORECASE):
                        evidence_files.append(rel_path)
                        features_found.append(pattern)
                        break
                    
                    if re.search(pattern, rel_path, re.IGNORECASE):
                        evidence_files.append(rel_path)
                        features_found.append(pattern)
                        break
            
            if evidence_files:
                # Generate description
                features_str = ", ".join(list(set(features_found))[:3])
                description = uc_info["description_template"].format(
                    features=features_str,
                    entities="data",
                    metrics="key indicators",
                    channels="email",
                    types="documents",
                    services="backend"
                )
                
                confidence = ConfidenceScore(
                    score=min(100, len(evidence_files) * 20),
                    level="high" if len(evidence_files) >= 5 else "medium" if len(evidence_files) >= 2 else "low",
                    evidence=evidence_files[:5],
                    assumptions=[] if len(evidence_files) >= 2 else ["Limited evidence"],
                )
                
                use_cases.append(UseCase(
                    title=uc_info["title"],
                    description=description,
                    actors=["Users", "System"],
                    icon=uc_info["icon"],
                    evidence_files=evidence_files[:10],
                    confidence=confidence,
                ))
        
        # Sort by confidence
        use_cases.sort(key=lambda x: x.confidence.score, reverse=True)
        return use_cases[:8]  # Top 8 use cases
    
    def _generate_description(
        self,
        project_name: str,
        readme_content: str,
        tech_stack: List[Dict[str, Any]],
        use_cases: List[UseCase],
        files: List[Path],
    ) -> Tuple[str, ConfidenceScore]:
        """Generate comprehensive project description."""
        evidence = []
        assumptions = []
        
        # Start with README if available
        if readme_content:
            # Extract first paragraph or description
            lines = readme_content.split('\n')
            desc_lines = []
            in_desc = False
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    if desc_lines:
                        break
                    continue
                if not line.startswith('[') and not line.startswith('!'):
                    desc_lines.append(line)
                    in_desc = True
                    if len(desc_lines) >= 3:
                        break
            
            if desc_lines:
                base_description = ' '.join(desc_lines)
                evidence.append("README.md")
            else:
                base_description = f"{project_name.upper()} is a software application"
                assumptions.append("No description in README")
        else:
            base_description = f"{project_name.upper()} is a software application"
            assumptions.append("No README found")
        
        # Enhance with tech stack
        if tech_stack:
            primary_tech = [t["name"] for t in tech_stack[:3]]
            tech_str = ", ".join(primary_tech)
            base_description += f" built with {tech_str}."
            evidence.append(f"Tech stack detected: {tech_str}")
        
        # Add use case summary
        if use_cases:
            uc_names = [uc.title for uc in use_cases[:3]]
            base_description += f" The application provides {', '.join(uc_names).lower()}."
            evidence.append(f"Use cases detected: {len(use_cases)}")
        
        # Calculate file age
        oldest_file = None
        for f in files[:50]:
            try:
                mtime = f.stat().st_mtime
                if oldest_file is None or mtime < oldest_file:
                    oldest_file = mtime
            except (OSError, IOError):
                pass
        
        if oldest_file:
            from datetime import datetime
            age_years = (datetime.now().timestamp() - oldest_file) / (365.25 * 24 * 3600)
            if age_years >= 1:
                base_description += f" Originally developed approximately {int(age_years)} years ago."
                evidence.append("File timestamps analyzed")
        
        confidence = ConfidenceScore.from_evidence(len(evidence), len(assumptions))
        confidence.evidence = evidence
        confidence.assumptions = assumptions
        
        return base_description, confidence
    
    def _generate_tagline(
        self,
        project_name: str,
        tech_stack: List[Dict[str, Any]],
        use_cases: List[UseCase],
    ) -> str:
        """Generate short tagline for project."""
        if use_cases:
            primary_uc = use_cases[0].title.lower()
            if tech_stack:
                primary_tech = tech_stack[0]["name"]
                return f"{primary_uc.title()} platform built with {primary_tech}"
            return f"{primary_uc.title()} platform"
        
        if tech_stack:
            return f"Application built with {tech_stack[0]['name']}"
        
        return "Software application"
    
    def _generate_architecture_summary(
        self,
        repo_path: Path,
        files: List[Path],
        tech_stack: List[Dict[str, Any]],
        analysis_data: Dict[str, Any],
    ) -> str:
        """Generate architecture overview."""
        layers = []
        
        # Check for common architectural patterns
        has_web = any(t["name"] in ["ASP.NET", "ASP.NET MVC", "ASP.NET Core", "FastAPI", "Django", "React"] for t in tech_stack)
        has_db = any(t["name"] in ["SQL Server", "Entity Framework", "PostgreSQL", "MongoDB"] for t in tech_stack)
        has_api = any(f for f in files if "api" in str(f).lower() or "controller" in str(f).lower())
        
        if has_web:
            layers.append("**Presentation Layer:** Web-based user interface")
        if has_api:
            layers.append("**API Layer:** RESTful services for data access")
        if has_db:
            layers.append("**Data Layer:** Persistent storage with database")
        
        if layers:
            return " → ".join([l.split(':')[0].replace('**', '') for l in layers])
        
        return "Standard application architecture"
    
    def _identify_target_users(
        self,
        use_cases: List[UseCase],
        readme_content: str,
    ) -> List[str]:
        """Identify target user personas."""
        users = set()
        
        # Common user patterns
        user_patterns = {
            r"admin": "Administrators",
            r"user": "End Users",
            r"customer": "Customers",
            r"manager": "Managers",
            r"developer": "Developers",
            r"student": "Students",
            r"teacher": "Teachers/Instructors",
        }
        
        search_text = readme_content.lower() + " " + " ".join([uc.title.lower() for uc in use_cases])
        
        for pattern, user_name in user_patterns.items():
            if re.search(pattern, search_text):
                users.add(user_name)
        
        if not users:
            users.add("General Users")
        
        return list(users)[:5]
    
    def _build_evidence_map(
        self,
        use_cases: List[UseCase],
        tech_stack: List[Dict[str, Any]],
    ) -> Dict[str, List[str]]:
        """Build map of claims to evidence files."""
        evidence_map = {}
        
        for uc in use_cases:
            evidence_map[uc.title] = uc.evidence_files[:5]
        
        for tech in tech_stack:
            evidence_map[f"Tech: {tech['name']}"] = tech.get("evidence_files", [])[:5]
        
        return evidence_map


# Singleton instance
_business_language_orchestrator = None


def get_business_language_orchestrator() -> BusinessLanguageOrchestrator:
    """Get or create singleton BusinessLanguageOrchestrator."""
    global _business_language_orchestrator
    if _business_language_orchestrator is None:
        _business_language_orchestrator = BusinessLanguageOrchestrator()
    return _business_language_orchestrator
