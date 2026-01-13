"""
AC-CHALLENGE-001: Challenge Detection Engine
Detect requests contradicting governance (CORE-025) with pattern matching
"""

from pathlib import Path
from typing import Dict, List, Optional
import re
import yaml


class ChallengeDetectionEngine:
    """
    Detects when user requests contradict governance rules or best practices.
    Part of CORE-025 intelligent challenge protocol.
    """
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.anti_patterns = self._load_anti_patterns()
        self.governance_rules = self._load_governance_rules()
    
    def _load_anti_patterns(self) -> Dict[str, List[str]]:
        """Load anti-pattern definitions from governance."""
        patterns = {
            'direct_coding': [
                r'create.*\.py',
                r'write code for',
                r'implement.*without.*test',
            ],
            'summary_files': [
                r'create.*summary',
                r'generate.*overview\.md',
                r'write.*summary\.yaml',
            ],
            'hardcoded_paths': [
                r'/Users/',
                r'C:\\\\',
                r'D:\\\\',
            ],
            'governance_bypass': [
                r'skip.*test',
                r'bypass.*governance',
                r'ignore.*CORE',
            ],
            'root_level_plans': [
                r'create.*plan.*\.md$',
                r'save.*plan.*in root',
            ]
        }
        return patterns
    
    def _load_governance_rules(self) -> Dict:
        """Load CORE rules from tier0."""
        core_rules_path = self.workspace_root / 'cortex-brain/tier0/governance/core-rules.yaml'
        if core_rules_path.exists():
            return yaml.safe_load(core_rules_path.read_text())
        return {}
    
    def detect_violations(self, user_request: str) -> List[Dict]:
        """
        Detect governance violations in user request.
        
        Returns:
            List of detected violations with rule IDs and severity
        """
        violations = []
        
        # Check anti-patterns
        for pattern_type, patterns in self.anti_patterns.items():
            for pattern in patterns:
                if re.search(pattern, user_request, re.IGNORECASE):
                    violations.append({
                        'type': 'anti_pattern',
                        'category': pattern_type,
                        'pattern': pattern,
                        'severity': 'HIGH',
                        'rule_id': self._map_pattern_to_rule(pattern_type)
                    })
        
        return violations
    
    def _map_pattern_to_rule(self, pattern_type: str) -> str:
        """Map anti-pattern type to CORE rule ID."""
        mapping = {
            'direct_coding': 'CORE-019',
            'summary_files': 'CORE-002',
            'hardcoded_paths': 'CORE-005',
            'governance_bypass': 'CORE-017',
            'root_level_plans': 'CORE-009'
        }
        return mapping.get(pattern_type, 'CORE-017')
    
    def calculate_risk_score(self, violations: List[Dict]) -> float:
        """
        Calculate risk score (0-100) based on violations.
        
        Higher score = more severe violations
        """
        if not violations:
            return 0.0
        
        severity_weights = {
            'CRITICAL': 40,
            'HIGH': 25,
            'MEDIUM': 15,
            'LOW': 5
        }
        
        total_score = sum(
            severity_weights.get(v['severity'], 10)
            for v in violations
        )
        
        # Cap at 100
        return min(total_score, 100.0)
    
    def should_challenge(self, user_request: str) -> tuple[bool, List[Dict], float]:
        """
        Determine if request should be challenged.
        
        Returns:
            (should_challenge, violations, risk_score)
        """
        violations = self.detect_violations(user_request)
        risk_score = self.calculate_risk_score(violations)
        
        # Challenge if risk score >= 25 (HIGH severity or multiple violations)
        should_challenge = risk_score >= 25
        
        return should_challenge, violations, risk_score
