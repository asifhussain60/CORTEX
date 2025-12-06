"""
Educational Comment Generator

Generates inline educational comments for code based on user's experience level.
Provides context-specific explanations with links to learning paths.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import Dict, List, Optional
from pathlib import Path


class EducationalCommentGenerator:
    """
    Generates educational inline comments for junior/mid-level developers.
    
    Features:
    - Context-specific explanations
    - Links to learning path documents
    - Pattern recognition (SOLID, DI, TDD, etc.)
    - Concise but informative
    
    Usage:
        generator = EducationalCommentGenerator()
        
        # Generate comment for specific pattern
        comment = generator.generate_comment(
            pattern="dependency_injection",
            context={"class_name": "ProfileAgent", "params": ["db_path", "tier1_api"]}
        )
        
        # Result:
        # ProfileAgent - Handles user profile updates (experience level, tech stack)
        # Why: Centralizes profile logic per Single Responsibility Principle
        # Dependencies: db_path (config), tier1_api (brain tier) injected via constructor
        # Reference: cortex-brain/documents/learning-paths/dependency-injection.md
    """
    
    def __init__(self, learning_paths_base: str = "cortex-brain/documents/learning-paths"):
        """
        Initialize generator.
        
        Args:
            learning_paths_base: Base path to learning path documents
        """
        self.learning_paths_base = learning_paths_base
        
        # Pattern templates
        self.patterns = {
            "dependency_injection": {
                "template": "# {class_name} - {purpose}\n# Why: {reason}\n# Dependencies: {dependencies} injected via constructor\n# Reference: {reference}",
                "reference": "dependency-injection.md"
            },
            "single_responsibility": {
                "template": "# {class_name} - {purpose}\n# Why: Centralizes {domain} logic per Single Responsibility Principle\n# Reference: {reference}",
                "reference": "solid-principles.md"
            },
            "factory_pattern": {
                "template": "# {method_name} - Creates {product} instances\n# Why: Encapsulates object creation logic (Factory Pattern)\n# Reference: {reference}",
                "reference": "solid-principles.md#open-closed-principle"
            },
            "async_pattern": {
                "template": "# {method_name} - Asynchronous {operation}\n# Why: Non-blocking operation for better performance\n# Note: Use 'await' when calling this method\n# Reference: {reference}",
                "reference": "async-patterns.md"
            },
            "test_structure": {
                "template": "# Test: {test_name}\n# Arrange: {arrange_desc}\n# Act: {act_desc}\n# Assert: {assert_desc}\n# Reference: {reference}",
                "reference": "tdd-workflow.md"
            }
        }
    
    def generate_comment(
        self, 
        pattern: str, 
        context: Dict[str, str],
        experience_level: str = "junior"
    ) -> str:
        """
        Generate educational comment for specific pattern.
        
        Args:
            pattern: Pattern name (dependency_injection, single_responsibility, etc.)
            context: Context-specific data (class_name, purpose, etc.)
            experience_level: User's experience level (junior/mid/senior/expert)
        
        Returns:
            Formatted inline comment
        """
        if experience_level in ["senior", "expert"]:
            # Senior/expert developers don't need educational comments
            return ""
        
        if pattern not in self.patterns:
            return ""
        
        pattern_config = self.patterns[pattern]
        
        # Build reference path
        reference_path = f"{self.learning_paths_base}/{pattern_config['reference']}"
        context["reference"] = reference_path
        
        # Format template
        try:
            comment = pattern_config["template"].format(**context)
            return comment
        except KeyError as e:
            # Missing required context key
            return f"# {context.get('class_name', 'Class')} - See {reference_path} for details"
    
    def generate_class_comment(
        self,
        class_name: str,
        purpose: str,
        patterns: List[str],
        experience_level: str = "junior"
    ) -> str:
        """
        Generate comprehensive class-level comment.
        
        Args:
            class_name: Name of the class
            purpose: What the class does
            patterns: List of patterns used (e.g., ["dependency_injection", "single_responsibility"])
            experience_level: User's experience level
        
        Returns:
            Multi-line docstring with educational content
        """
        if experience_level in ["senior", "expert"]:
            return f'"""{class_name} - {purpose}"""'
        
        lines = [
            f'"""',
            f'{class_name} - {purpose}',
            '',
            'Patterns Used:'
        ]
        
        pattern_descriptions = {
            "dependency_injection": "Dependency Injection (DI) - Dependencies passed via constructor",
            "single_responsibility": "Single Responsibility (SRP) - One job per class",
            "open_closed": "Open/Closed (OCP) - Extend without modifying",
            "interface_segregation": "Interface Segregation (ISP) - Focused interfaces",
            "dependency_inversion": "Dependency Inversion (DIP) - Depend on abstractions"
        }
        
        for pattern in patterns:
            if pattern in pattern_descriptions:
                lines.append(f'- {pattern_descriptions[pattern]}')
        
        lines.append('')
        lines.append('Learn More:')
        
        # Add relevant learning path links
        if any(p in patterns for p in ["dependency_injection", "single_responsibility", "open_closed"]):
            lines.append(f'- SOLID Principles: {self.learning_paths_base}/solid-principles.md')
        
        if "dependency_injection" in patterns or "dependency_inversion" in patterns:
            lines.append(f'- Dependency Injection: {self.learning_paths_base}/dependency-injection.md')
        
        lines.append('"""')
        
        return '\n'.join(lines)
    
    def generate_method_comment(
        self,
        method_name: str,
        purpose: str,
        parameters: List[Dict[str, str]],
        returns: str,
        experience_level: str = "junior"
    ) -> str:
        """
        Generate educational method comment.
        
        Args:
            method_name: Name of the method
            purpose: What the method does
            parameters: List of {name, description} dicts
            returns: Return value description
            experience_level: User's experience level
        
        Returns:
            Formatted docstring
        """
        if experience_level in ["senior", "expert"]:
            # Minimal docstring for senior/expert
            return f'"""{purpose}"""'
        
        lines = [
            f'"""',
            f'{purpose}',
            ''
        ]
        
        if parameters:
            lines.append('Args:')
            for param in parameters:
                lines.append(f'    {param["name"]}: {param["description"]}')
            lines.append('')
        
        if returns:
            lines.append('Returns:')
            lines.append(f'    {returns}')
            lines.append('')
        
        lines.append('Example:')
        lines.append(f'    result = {method_name}(...)')
        lines.append('"""')
        
        return '\n    '.join(lines)
    
    def get_learning_path_link(self, topic: str) -> str:
        """
        Get direct link to learning path for specific topic.
        
        Args:
            topic: Topic name (solid, dependency_injection, tdd, async, testing)
        
        Returns:
            Path to learning document
        """
        topic_map = {
            "solid": "solid-principles.md",
            "dependency_injection": "dependency-injection.md",
            "di": "dependency-injection.md",
            "tdd": "tdd-workflow.md",
            "testing": "testing-strategies.md",
            "async": "async-patterns.md"
        }
        
        filename = topic_map.get(topic.lower(), "INDEX.md")
        return f"{self.learning_paths_base}/{filename}"
    
    def generate_response_addon(
        self,
        experience_level: str,
        topics_used: List[str]
    ) -> str:
        """
        Generate educational addon for response templates.
        
        Args:
            experience_level: User's experience level
            topics_used: List of topics/patterns used in generated code
        
        Returns:
            Formatted addon text for response template
        """
        if experience_level not in ["junior", "mid"]:
            return ""
        
        lines = [
            f"\n\n💡 **Learning Mode Enabled:** As a {experience_level} developer, I've added explanations to the code.",
            "",
            "**What you'll find:**",
            "- Inline comments explaining key concepts",
            "- Links to detailed learning paths",
            "- Pattern names (SOLID, DI, TDD, etc.)",
            ""
        ]
        
        if topics_used:
            lines.append("📚 **Relevant Learning Paths:**")
            
            topic_set = set(topics_used)  # Remove duplicates
            
            for topic in topic_set:
                link = self.get_learning_path_link(topic)
                topic_display = topic.replace("_", " ").title()
                lines.append(f"- [{topic_display}](file:///{link})")
            
            lines.append("")
        
        lines.extend([
            "🎥 **Quick Videos:** See links in learning path documents",
            "",
            f"Toggle off anytime: `update profile experience level senior`"
        ])
        
        return '\n'.join(lines)


def get_generator() -> EducationalCommentGenerator:
    """
    Get singleton instance of comment generator.
    
    Returns:
        EducationalCommentGenerator instance
    """
    return EducationalCommentGenerator()
