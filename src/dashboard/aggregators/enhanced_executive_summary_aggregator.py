"""
Enhanced Executive Summary Aggregator

Integrates 5 intelligence sources for high-quality executive summaries:
1. Git commit patterns (narrative, velocity, themes)
2. README deep-parsing (purpose, features, capabilities)
3. Docstring mining (code documentation quality)
4. Business domain inference (domains from code structure)
5. Tech stack analysis (existing functionality)

Quality Improvement: 3/10 → 8/10 target

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass

from src.intelligence.git_commit_analyzer import GitCommitAnalyzer
from src.intelligence.readme_parser import ReadmeParser
from src.intelligence.multi_language_docstring_orchestrator import MultiLanguageDocstringOrchestrator
from src.intelligence.business_domain_inference import BusinessDomainInferenceEngine


class IntelligenceSource(Enum):
    """Available intelligence sources for executive summaries."""
    GIT_COMMITS = "git_commits"
    README = "readme"
    DOCSTRINGS = "docstrings"
    BUSINESS_DOMAINS = "business_domains"
    TECH_STACK = "tech_stack"


@dataclass
class SourcePriority:
    """Priority ranking for intelligence sources."""
    source: IntelligenceSource
    weight: float
    available: bool


class EnhancedExecutiveSummaryAggregator:
    """Enhanced aggregator with 5 intelligence sources."""
    
    def __init__(self, data_dir: Path, repo_path: Path = None):
        """
        Initialize enhanced aggregator.
        
        Args:
            data_dir: Directory containing dashboard data files
            repo_path: Path to repository for code analysis
        """
        self.data_dir = Path(data_dir)
        self.repo_path = Path(repo_path) if repo_path else Path(f"C:/PROJECTS/{data_dir.name}")
        
        # Initialize intelligence analyzers
        self.git_analyzer = None
        self.readme_parser = ReadmeParser()
        self.docstring_orchestrator = MultiLanguageDocstringOrchestrator()
        self.domain_engine = BusinessDomainInferenceEngine()
        
        # Initialize git analyzer if repo exists
        if self.repo_path.exists() and (self.repo_path / ".git").exists():
            try:
                self.git_analyzer = GitCommitAnalyzer(self.repo_path)
            except:
                pass
    
    def get_available_sources(self) -> List[IntelligenceSource]:
        """Get list of available intelligence sources."""
        sources = [IntelligenceSource.TECH_STACK]  # Always available
        
        if self.git_analyzer:
            sources.append(IntelligenceSource.GIT_COMMITS)
        
        # Check for README
        for readme_name in ["README.md", "readme.md", "README.txt"]:
            if (self.repo_path / readme_name).exists():
                sources.append(IntelligenceSource.README)
                break
        
        # Docstrings and domains available if repo exists
        if self.repo_path.exists():
            sources.append(IntelligenceSource.DOCSTRINGS)
            sources.append(IntelligenceSource.BUSINESS_DOMAINS)
        
        return sources
    
    def aggregate(self) -> Dict[str, Any]:
        """
        Generate enhanced executive summary from all sources.
        
        Returns:
            Complete executive summary with intelligence from all sources
        """
        # Load base data
        tech = self._load_json("tech-stack.json")
        architecture = self._load_json("architecture.json")
        health = self._load_json("health-data.json")
        security = self._load_json("security.json")
        code_org = self._load_json("code-organization.json")
        
        # Extract intelligence from all sources
        git_insights = self._extract_git_insights()
        readme_insights = self._extract_readme_insights()
        docstring_insights = self._extract_docstring_insights()
        domain_insights = self._extract_domain_insights()
        
        # Determine source priority
        source_priority = self._determine_source_priority(
            readme_insights, git_insights, docstring_insights, domain_insights
        )
        
        # Generate enhanced summary
        what_it_does = self._generate_enhanced_what_it_does(
            tech, architecture,
            git_insights, readme_insights, docstring_insights, domain_insights,
            source_priority
        )
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(
            what_it_does, git_insights, readme_insights, docstring_insights, domain_insights
        )
        
        # Build complete summary
        return {
            "project_name": self._extract_project_name(),
            "tagline": self._generate_tagline(tech, readme_insights),
            "what_it_does": what_it_does,
            "recent_activity": git_insights.get("recent_commits", []) if git_insights else [],
            "composition": self._build_composition(tech, architecture),
            "tech_stack_summary": self._build_tech_summary(tech),
            "health_indicators": self._build_health_indicators(health, security, code_org),
            "quality_score": quality_score,
            "intelligence_sources_used": [s.value for s in self.get_available_sources()]
        }
    
    def _extract_git_insights(self) -> Optional[Dict[str, Any]]:
        """Extract insights from git commit history."""
        if not self.git_analyzer:
            return None
        
        try:
            narrative = self.git_analyzer.analyze(days=90, limit=100)
            
            return {
                "narrative": narrative.summary,
                "velocity": narrative.velocity_metrics,
                "top_themes": [{"theme": t.theme, "count": t.count, "percentage": t.percentage} 
                               for t in narrative.top_themes],
                "active_areas": narrative.active_areas,
                "recent_commits": []  # Populated separately if needed
            }
        except Exception as e:
            print(f"Warning: Git analysis failed: {e}")
            return None
    
    def _extract_readme_insights(self) -> Optional[Dict[str, Any]]:
        """Extract insights from README file."""
        for readme_name in ["README.md", "readme.md", "README.txt"]:
            readme_path = self.repo_path / readme_name
            if readme_path.exists():
                try:
                    metadata = self.readme_parser.parse_file(readme_path)
                    
                    return {
                        "purpose": metadata.purpose,
                        "description": metadata.description,
                        "capabilities": metadata.features[:10],
                        "title": metadata.title,
                        "sections_count": len(metadata.sections),
                        "has_installation": len(metadata.installation_steps) > 0
                    }
                except Exception as e:
                    print(f"Warning: README parsing failed: {e}")
                    return None
        
        return None
    
    def _extract_docstring_insights(self) -> Optional[Dict[str, Any]]:
        """Extract insights from code docstrings."""
        if not self.repo_path.exists():
            return None
        
        try:
            # Find Python files (primary target for docstrings)
            python_files = list(self.repo_path.rglob("*.py"))
            if not python_files:
                return None
            
            # Limit to first 10 files for performance (<30s target)
            # For large repos, prioritize src/ and app/ directories
            if len(python_files) > 10:
                priority_files = [f for f in python_files if '/src/' in str(f) or '/app/' in str(f)]
                if priority_files:
                    python_files = priority_files[:10]
                else:
                    python_files = python_files[:10]
            python_files = python_files[:10]
            
            # Extract docstrings
            results = self.docstring_orchestrator.extract_from_files(
                python_files,
                limit_per_file=10,
                parallel=True
            )
            
            # Calculate quality score from all_docstrings
            all_docstrings = results.get('all_docstrings', [])
            total_docstrings = len(all_docstrings)
            
            if total_docstrings == 0:
                quality_score = 0
            else:
                # Simple heuristic: weighted by informativeness
                informative = len([d for d in all_docstrings 
                                 if d.informativeness_score > 5])
                quality_score = int((informative / total_docstrings) * 100)
            
            # Get top documented modules
            top_modules = []
            for doc in all_docstrings[:5]:
                module = Path(doc.source_file).stem
                top_modules.append(module)
            
            # Get languages from by_language keys
            languages_analyzed = list(results.get('by_language', {}).keys())
            
            return {
                "quality_score": quality_score,
                "total_docstrings": total_docstrings,
                "top_modules": top_modules,
                "languages_analyzed": languages_analyzed
            }
        except Exception as e:
            print(f"Warning: Docstring analysis failed: {e}")
            return None
    
    def _extract_domain_insights(self) -> Optional[Dict[str, Any]]:
        """Extract business domain insights from code structure."""
        if not self.repo_path.exists():
            return None
        
        try:
            # NOTE: Business domain inference can be slow on large repos
            # For executive summary, we only need top domains
            # Skip if repo is too large (>500 files) to stay under 30s target
            code_files = list(self.repo_path.rglob("*.py")) + list(self.repo_path.rglob("*.cs")) + list(self.repo_path.rglob("*.js"))
            if len(code_files) > 500:
                print(f"   ⚠️  Skipping domain analysis ({len(code_files)} files, >500 limit for performance)")
                return None
            
            # analyze_repository returns List[DomainEntity]
            domain_entities = self.domain_engine.analyze_repository(self.repo_path)
            
            # Convert to serializable format
            domains = []
            for domain in domain_entities[:10]:
                domains.append({
                    "name": domain.name,
                    "confidence": domain.confidence,
                    "frequency": domain.frequency,
                    "sources": domain.sources
                })
            
            return {
                "domains": domains,
                "total_domains": len(domain_entities),
                "high_confidence_count": len([d for d in domains if d['confidence'] == 'high'])
            }
        except Exception as e:
            print(f"Warning: Domain analysis failed: {e}")
            return None
    
    def _determine_source_priority(
        self,
        readme: Optional[Dict],
        git: Optional[Dict],
        docstrings: Optional[Dict],
        domains: Optional[Dict]
    ) -> List[str]:
        """
        Determine priority order for intelligence sources.
        
        Priority logic:
        1. README if detailed (>200 chars purpose/description)
        2. Business domains if high confidence domains exist
        3. Docstrings if good quality (>50% score)
        4. Git commits if active (>10 commits in 90 days)
        5. Tech stack (fallback)
        """
        priorities = []
        
        # README priority (highest - explicit documentation)
        if readme and isinstance(readme, dict):
            purpose_len = len(readme.get('purpose') or '')
            desc_len = len(readme.get('description') or '')
            # Detailed README: purpose>50 OR description>50 (lowered for shorter READMEs)
            # Rationale: Any README content is better than tech-only fallback
            if purpose_len > 50 or desc_len > 50:
                priorities.append("readme")
        
        # Domains priority (business context)
        if domains and domains.get('high_confidence_count', 0) > 0:
            priorities.append("domains")
        
        # Docstrings priority (code-level documentation)
        if docstrings and docstrings.get('quality_score', 0) > 50:
            priorities.append("docstrings")
        
        # Git priority (historical narrative)
        if git and git['velocity'].get('total_commits', 0) > 10:
            priorities.append("git")
        
        # Tech stack always available as fallback
        priorities.append("tech_stack")
        
        # Add remaining sources that exist but lower priority
        if readme and "readme" not in priorities:
            priorities.append("readme")
        if domains and "domains" not in priorities:
            priorities.append("domains")
        if docstrings and "docstrings" not in priorities:
            priorities.append("docstrings")
        if git and "git" not in priorities:
            priorities.append("git")
        
        return priorities
    
    def _generate_enhanced_what_it_does(
        self,
        tech: Dict,
        architecture: Dict,
        git_insights: Optional[Dict],
        readme_insights: Optional[Dict],
        docstring_insights: Optional[Dict],
        domain_insights: Optional[Dict],
        source_priority: List[str]
    ) -> Dict[str, Any]:
        """Generate enhanced what_it_does section using all sources."""
        
        # Start with highest priority source
        summary = None
        key_points = []
        
        # Use README if top priority and available
        if "readme" in source_priority[:2] and readme_insights:
            if readme_insights.get('purpose'):
                summary = readme_insights['purpose']
            elif readme_insights.get('description'):
                summary = readme_insights['description'][:500]
            
            # Extend summary if too short
            if summary and len(summary) < 200:
                # Add description to purpose
                if readme_insights.get('description') and readme_insights.get('purpose'):
                    summary += " " + readme_insights['description'][:300]
                elif readme_insights.get('description'):
                    summary = readme_insights['description'][:500]
                
                # If still short, add capabilities
                if len(summary) < 200 and readme_insights.get('capabilities'):
                    caps = readme_insights['capabilities'][:5]
                    if len(caps) >= 2:
                        summary += f" Key capabilities: {caps[0]}, {caps[1]}"
                        if len(caps) > 2:
                            summary += f", {caps[2]}"
                        summary += "."
                
                # If STILL short, add domain context
                if len(summary) < 200 and domain_insights and domain_insights.get('domains'):
                    top_domains = [d['name'] for d in domain_insights['domains'][:2]]
                    if top_domains:
                        summary += f" Operates in {', '.join(top_domains)} domains."
            
            # Add capabilities as key points
            if readme_insights.get('capabilities'):
                key_points.extend(readme_insights['capabilities'][:5])
        
        # Enhance with git insights
        if git_insights and git_insights.get('narrative'):
            if not summary:
                summary = git_insights['narrative']
            else:
                # Add git narrative as context
                key_points.append(f"Development focus: {git_insights['narrative'][:100]}")
        
        # Enhance with domain insights
        if domain_insights and domain_insights.get('domains'):
            high_conf_domains = [d['name'] for d in domain_insights['domains'] 
                                if d['confidence'] == 'high']
            if high_conf_domains:
                key_points.append(f"Key business domains: {', '.join(high_conf_domains[:5])}")
        
        # Fallback to tech stack if no summary yet
        if not summary:
            backend_techs = tech.get('backend', [])
            frontend_techs = tech.get('frontend', [])
            primary_tech = backend_techs[0].get('name', 'modern technologies') if backend_techs else 'modern technologies'
            frontend_tech = frontend_techs[0].get('name', '') if frontend_techs else ''
            total_loc = architecture.get('summary', {}).get('total_loc', 0)
            
            summary = f"A software application built with {primary_tech}"
            if frontend_tech:
                summary += f" and {frontend_tech}"
            summary += f", encompassing {total_loc:,} lines of code. "
            summary += "This system provides core business functionality with data persistence, API services, and user interfaces. "
            
            # Add architecture style if available
            arch_style = architecture.get('style', {}).get('name', '')
            if arch_style and 'unknown' not in arch_style.lower():
                summary += f"Architecture follows {arch_style} pattern for modularity and maintainability."
        
        # Ensure key_points has content
        if not key_points:
            # Generate from architecture
            endpoint_count = len(architecture.get('endpoints', []))
            if endpoint_count > 0:
                key_points.append(f"{endpoint_count} API endpoints")
            
            component_count = architecture.get('summary', {}).get('total_components', 0)
            if component_count > 0:
                key_points.append(f"{component_count} architectural components")
        
        return {
            "summary": summary,
            "key_points": key_points[:8],  # Limit to 8
            "source_priority": source_priority,
            "git_insights": git_insights,
            "readme_insights": readme_insights,
            "docstring_insights": docstring_insights,
            "domain_insights": domain_insights
        }
    
    def _calculate_quality_score(
        self,
        what_it_does: Dict,
        git_insights: Optional[Dict],
        readme_insights: Optional[Dict],
        docstring_insights: Optional[Dict],
        domain_insights: Optional[Dict]
    ) -> int:
        """
        Calculate executive summary quality score (0-10).
        
        Scoring:
        - Summary specificity (0-2): Not generic, >200 chars
        - Key points quality (0-2): >3 specific points
        - Multi-source integration (0-2): Uses 3+ sources
        - Git narrative quality (0-1): Has meaningful git insights
        - README depth (0-1): Has detailed README
        - Domain clarity (0-1): Has high-confidence domains
        - Documentation quality (0-1): Good docstring coverage
        """
        score = 0
        
        # Summary specificity (0-2 points)
        summary = what_it_does.get('summary', '')
        is_generic = 'software application' in summary.lower() or 'modern technologies' in summary.lower()
        
        if len(summary) > 200 and not is_generic:
            score += 2
        elif len(summary) > 200 and is_generic:
            score += 1  # Long but generic
        elif len(summary) > 100:
            score += 1
        
        # Key points quality
        key_points = what_it_does.get('key_points', [])
        if len(key_points) >= 5:
            score += 2
        elif len(key_points) >= 3:
            score += 1
        
        # Multi-source integration
        sources_used = sum([
            git_insights is not None,
            readme_insights is not None,
            docstring_insights is not None,
            domain_insights is not None
        ])
        if sources_used >= 3:
            score += 2
        elif sources_used >= 2:
            score += 1
        
        # Git narrative (0-1 point)
        if git_insights and git_insights.get('velocity', {}).get('total_commits', 0) > 10:
            score += 1
        
        # README depth (0-2 points) - weighted higher
        if readme_insights and isinstance(readme_insights, dict):
            purpose_len = len(readme_insights.get('purpose') or '')
            if purpose_len > 200:
                score += 2
            elif purpose_len > 100:
                score += 1
        
        # Domain clarity (0-1 point)
        if domain_insights and domain_insights.get('high_confidence_count', 0) > 0:
            score += 1
        
        # Documentation quality (0-1 point)
        if docstring_insights and docstring_insights.get('quality_score', 0) > 50:
            score += 1
        
        return min(score, 10)  # Cap at 10
    
    def _extract_project_name(self) -> str:
        """Extract project name from various sources."""
        # Try README first
        for readme_name in ["README.md", "readme.md"]:
            readme_path = self.repo_path / readme_name
            if readme_path.exists():
                try:
                    metadata = self.readme_parser.parse_file(readme_path)
                    if metadata.title:
                        return metadata.title
                except:
                    pass
        
        # Fallback to directory name
        return self.repo_path.name.replace("-", " ").replace("_", " ").title()
    
    def _generate_tagline(self, tech: Dict, readme: Optional[Dict]) -> str:
        """Generate project tagline."""
        # Use README description if available
        if readme and readme.get('description'):
            desc = readme['description']
            # Take first sentence
            first_sentence = desc.split('.')[0] + '.'
            if len(first_sentence) < 150:
                return first_sentence
        
        # Fallback to tech-based tagline
        backend_techs = tech.get('backend', [])
        primary_tech = backend_techs[0].get('name', 'modern technologies') if backend_techs else 'modern technologies'
        return f"Application built with {primary_tech}"
    
    def _build_composition(self, tech: Dict, architecture: Dict) -> Dict[str, Any]:
        """Build composition section."""
        arch_style = architecture.get("style", {})
        
        components = []
        for tier in architecture.get("tiers", [])[:6]:
            components.append({
                "name": tier.get("name", "Component"),
                "technology": ", ".join(tier.get("technologies", [])[:3]),
                "purpose": tier.get("description", ""),
                "files_count": tier.get("file_count", 0)
            })
        
        return {
            "architecture_style": arch_style.get("name", "Application Architecture"),
            "components": components,
            "relationships": arch_style.get("characteristics", [])[:5]
        }
    
    def _build_tech_summary(self, tech: Dict) -> Dict[str, Any]:
        """Build tech stack summary."""
        summary = tech.get("summary", {})
        
        all_techs = []
        for category in ["frontend", "backend", "database", "devops"]:
            all_techs.extend(tech.get(category, []))
        
        top_techs = [
            {
                "name": t.get("name", ""),
                "version": t.get("version", "unknown"),
                "category": t.get("category", "unknown")
            }
            for t in all_techs[:5]
        ]
        
        return {
            "total_technologies": summary.get("total_technologies", 0),
            "primary_technologies": top_techs,
            "outdated_count": summary.get("outdated_count", 0),
            "critical_updates_needed": summary.get("critical_cves", 0)
        }
    
    def _build_health_indicators(self, health: Dict, security: Dict, code_org: Dict) -> List[Dict[str, Any]]:
        """Build health indicators."""
        indicators = []
        
        quality_score = health.get("metrics", {}).get("code_quality_score", 75)
        indicators.append({
            "name": "Code Quality",
            "value": f"{quality_score}%",
            "status": "healthy" if quality_score >= 70 else "warning",
            "trend": "stable"
        })
        
        security_score = security.get("overall_score", 100)
        indicators.append({
            "name": "Security",
            "value": f"{security_score}%",
            "status": "healthy" if security_score >= 90 else "warning",
            "trend": "stable"
        })
        
        tech_debt = code_org.get("summary", {}).get("technical_debt_hours", 0)
        indicators.append({
            "name": "Technical Debt",
            "value": f"{tech_debt:.1f}h",
            "status": "healthy" if tech_debt < 50 else "warning",
            "trend": "stable"
        })
        
        return indicators
    
    def _load_json(self, filename: str) -> Dict[str, Any]:
        """Load JSON file with error handling."""
        file_path = self.data_dir / filename
        if file_path.exists():
            try:
                return json.loads(file_path.read_text())
            except:
                return {}
        return {}
