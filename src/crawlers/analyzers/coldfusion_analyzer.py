"""
ColdFusion Language Analyzer

Analyzes ColdFusion (.cfm, .cfc) files for components, functions, queries,
and security patterns (SQL injection risks).

Author: CORTEX Application Health Dashboard
"""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ColdFusionAnalysisResult:
    """Analysis result for ColdFusion files"""
    file_path: str
    language: str = "coldfusion"
    lines_of_code: int = 0
    components: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    queries: int = 0
    security_issues: List[Dict[str, Any]] = field(default_factory=list)
    cfml_tags: List[str] = field(default_factory=list)
    raw_metrics: Dict[str, Any] = field(default_factory=dict)


class ColdFusionAnalyzer:
    """Analyzer for ColdFusion files using tag-based parsing"""
    
    # Regex patterns for ColdFusion constructs
    COMPONENT_PATTERN = re.compile(
        r'<cfcomponent\s+([^>]*)>',
        re.IGNORECASE | re.DOTALL
    )
    
    FUNCTION_PATTERN = re.compile(
        r'<cffunction\s+name="([^"]+)"',
        re.IGNORECASE
    )
    
    QUERY_PATTERN = re.compile(
        r'<cfquery\s+([^>]*)>',
        re.IGNORECASE
    )
    
    # SQL injection risk patterns (unparameterized queries)
    SQL_INJECTION_PATTERN = re.compile(
        r'<cfquery[^>]*>.*?#[^#]+#.*?</cfquery>',
        re.IGNORECASE | re.DOTALL
    )
    
    # Common CFML tags
    CFML_TAG_PATTERN = re.compile(
        r'<(cf\w+)',
        re.IGNORECASE
    )
    
    def __init__(self):
        """Initialize ColdFusion analyzer"""
        pass
    
    def analyze(self, file_path: str, content: str) -> ColdFusionAnalysisResult:
        """
        Analyze ColdFusion file content
        
        Args:
            file_path: Path to the file
            content: File content as string
            
        Returns:
            ColdFusionAnalysisResult with analysis data
        """
        result = ColdFusionAnalysisResult(file_path=file_path)
        
        # Count lines of code (non-empty lines)
        lines = content.split('\n')
        result.lines_of_code = sum(1 for line in lines if line.strip())
        
        # Extract components
        component_matches = self.COMPONENT_PATTERN.findall(content)
        if component_matches:
            # Extract component name from attributes
            for attrs in component_matches:
                name_match = re.search(r'name="([^"]+)"', attrs, re.IGNORECASE)
                if name_match:
                    result.components.append(name_match.group(1))
                else:
                    result.components.append("UnnamedComponent")
        
        # Extract functions
        function_matches = self.FUNCTION_PATTERN.findall(content)
        result.functions = function_matches
        
        # Count queries
        query_matches = self.QUERY_PATTERN.findall(content)
        result.queries = len(query_matches)
        
        # Detect SQL injection risks
        sql_injection_matches = self.SQL_INJECTION_PATTERN.finditer(content)
        for match in sql_injection_matches:
            issue_text = match.group(0)
            line_number = content[:match.start()].count('\n') + 1
            
            result.security_issues.append({
                'type': 'sql_injection_risk',
                'severity': 'high',
                'line': line_number,
                'description': 'Potential SQL injection - unparameterized query with variable interpolation',
                'snippet': issue_text[:100] + '...' if len(issue_text) > 100 else issue_text
            })
        
        # Extract all CFML tags used
        tag_matches = self.CFML_TAG_PATTERN.findall(content)
        result.cfml_tags = list(set(tag.lower() for tag in tag_matches))
        
        # Store raw metrics
        result.raw_metrics = {
            'component_count': len(result.components),
            'function_count': len(result.functions),
            'query_count': result.queries,
            'security_issue_count': len(result.security_issues),
            'unique_cfml_tags': len(result.cfml_tags)
        }
        
        return result
    
    def can_analyze(self, file_path: str) -> bool:
        """
        Check if this analyzer can handle the file
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file has .cfm or .cfc extension
        """
        return file_path.lower().endswith(('.cfm', '.cfc'))
