"""
Narrative Generator

Generates business narratives from technical analysis data.
"""

import logging
from pathlib import Path
from typing import Dict, Any
from .base import BaseGenerator

logger = logging.getLogger(__name__)


class NarrativeGenerator(BaseGenerator):
    """
    Generate executive summaries and business narratives
    
    Transforms technical data into business-focused insights.
    """
    
    def generate(
        self,
        data: Dict[str, Any],
        output_path: Path,
        **kwargs
    ) -> Path:
        """
        Generate narrative from analysis data
        
        Args:
            data: Collected analysis data
            output_path: Output path (ignored, returns dict)
            **kwargs: Additional options
            
        Returns:
            Path to narrative file (or dict for now)
        """
        logger.info("Generating narrative...")
        
        # Extract key information
        metadata = data.get('metadata', {})
        classification = data.get('classification', {})
        health = data.get('health', {})
        
        repo_name = metadata.get('repo_name', 'Unknown')
        repo_type = classification.get('primary_type', 'unknown')
        total_files = health.get('total_files', 0)
        total_loc = health.get('total_loc', 0)
        health_score = health.get('health_score', 0)
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            repo_name,
            repo_type,
            total_files,
            total_loc,
            health_score
        )
        
        # Generate key capabilities
        key_capabilities = self._extract_capabilities(data)
        
        # Generate technical highlights
        technical_highlights = self._extract_highlights(data)
        
        narrative = {
            'executive_summary': executive_summary,
            'key_capabilities': key_capabilities,
            'technical_highlights': technical_highlights,
            'recommendations': self._generate_recommendations(data)
        }
        
        logger.info("✅ Narrative generated")
        
        # For now, return the dict directly
        # TODO: Write to markdown file
        return narrative
    
    def _generate_executive_summary(
        self,
        repo_name: str,
        repo_type: str,
        total_files: int,
        total_loc: int,
        health_score: float
    ) -> str:
        """Generate executive summary paragraph"""
        repo_type_names = {
            'fullstack_web': 'Full-Stack Web Application',
            'api_service': 'API Service',
            'database_project': 'Database Project',
            'console_app': 'Console Application',
            'microservices': 'Microservices Architecture',
            'library_package': 'Library/Package'
        }
        
        type_name = repo_type_names.get(repo_type, 'Software Project')
        
        return (
            f"{repo_name} is a {type_name} comprising {total_files:,} files "
            f"and {total_loc:,} lines of code. "
            f"The repository demonstrates a health score of {health_score:.1f}/100, "
            f"indicating {'excellent' if health_score >= 90 else 'good' if health_score >= 70 else 'moderate'} "
            f"code organization and maintainability."
        )
    
    def _extract_capabilities(self, data: Dict[str, Any]) -> list:
        """Extract key capabilities from data"""
        capabilities = []
        
        patterns = data.get('classification', {}).get('detected_patterns', {})
        
        if patterns.get('has_frontend'):
            capabilities.append("User Interface (Web Frontend)")
        if patterns.get('has_backend'):
            capabilities.append("Backend API Services")
        if patterns.get('has_database'):
            capabilities.append("Data Persistence Layer")
        if patterns.get('has_messaging'):
            capabilities.append("Event-Driven Messaging")
        if patterns.get('has_containerization'):
            capabilities.append("Container Orchestration")
        if patterns.get('has_tests'):
            capabilities.append("Automated Testing")
        if patterns.get('has_ci_cd'):
            capabilities.append("CI/CD Pipeline")
        
        return capabilities or ["Core Application Functionality"]
    
    def _extract_highlights(self, data: Dict[str, Any]) -> list:
        """Extract technical highlights"""
        highlights = []
        
        health = data.get('health', {})
        languages = health.get('languages', {})
        
        if languages:
            # Primary language
            primary_lang = max(languages.items(), key=lambda x: x[1].get('percentage', 0))
            highlights.append(
                f"Primary implementation language: {primary_lang[0]} "
                f"({primary_lang[1].get('percentage', 0):.1f}% of codebase)"
            )
        
        # Health score
        health_score = health.get('health_score', 0)
        if health_score >= 80:
            highlights.append(
                f"Strong code health metrics (score: {health_score:.1f}/100)"
            )
        
        return highlights
    
    def _generate_recommendations(self, data: Dict[str, Any]) -> list:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        health = data.get('health', {})
        health_score = health.get('health_score', 0)
        
        if health_score < 70:
            recommendations.append(
                "Consider refactoring to improve code organization and maintainability"
            )
        
        total_loc = health.get('total_loc', 0)
        total_files = health.get('total_files', 0)
        
        if total_files > 0:
            avg_file_size = total_loc // total_files
            if avg_file_size > 500:
                recommendations.append(
                    f"Large average file size ({avg_file_size} LOC) - "
                    "consider breaking down into smaller modules"
                )
        
        return recommendations or ["Repository is in good shape - maintain current practices"]
