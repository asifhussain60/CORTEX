"""
E2E Test Prioritizer - Phase 7.5.2
Prioritizes E2E test scenarios using extensible criteria system

8 Criteria:
1. Code Complexity
2. Risk Score (Complexity × Change Frequency)
3. Business Value
4. User Impact
5. Regulatory Compliance (PCI, GDPR, HIPAA, SOX)
6. Data Integrity
7. External Dependency Risk
8. Change Frequency (Regression Risk)

Priority Levels: P0 (Critical) > P1 (High) > P2 (Medium) > P3 (Low)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import re
from typing import Dict, List, Any, Optional


class E2ETestPrioritizer:
    """Prioritizes E2E test scenarios using weighted criteria"""
    
    # Regulatory patterns
    REGULATORY_PATTERNS = {
        'PCI-DSS': r'\b(credit\s*card|card\s*number|cvv|cvc|pan|pci|payment\s*card|cardholder)\b',
        'GDPR': r'\b(gdpr|personal\s*data|data\s*subject|right\s*to\s*erasure|consent|dpo)\b',
        'HIPAA': r'\b(hipaa|phi|protected\s*health|medical\s*record|patient\s*data|ehr)\b',
        'SOX': r'\b(sox|sarbanes|financial\s*report|audit\s*trail|internal\s*control)\b'
    }
    
    # Business value keywords
    BUSINESS_VALUE_KEYWORDS = [
        'payment', 'order', 'checkout', 'invoice', 'transaction', 'billing',
        'purchase', 'cart', 'credit', 'money', 'financial'
    ]
    
    # Data integrity keywords
    DATA_INTEGRITY_KEYWORDS = [
        'transaction', 'financial', 'money', 'balance', 'audit', 'ledger',
        'reconciliation', 'accounting', 'revenue'
    ]
    
    # Default criteria weights
    DEFAULT_CRITERIA_WEIGHTS = {
        'complexity': 30,
        'risk_score': 25,
        'business_value': 20,
        'user_impact': 15,
        'regulatory': 30,  # Can trigger auto-promote
        'data_integrity': 20,
        'dependency_risk': 10,
        'change_frequency': 15
    }
    
    # Default priority thresholds (normalized 0-100)
    DEFAULT_PRIORITY_THRESHOLDS = {
        'p0': 80,
        'p1': 60,
        'p2': 40,
        'p3': 0
    }
    
    def __init__(self, criteria_weights: Optional[Dict[str, int]] = None,
                 priority_thresholds: Optional[Dict[str, float]] = None):
        """Initialize E2E test prioritizer"""
        self.criteria_weights = criteria_weights or self.DEFAULT_CRITERIA_WEIGHTS.copy()
        self.priority_thresholds = priority_thresholds or self.DEFAULT_PRIORITY_THRESHOLDS.copy()
        
        # Calculate total weight for normalization
        self.total_weight = sum(self.criteria_weights.values())
    
    def calculate_priority(self, scenario: Dict[str, Any]) -> str:
        """
        Calculate priority (P0-P3) for a scenario
        
        Args:
            scenario: Scenario dict with criteria data
            
        Returns:
            Priority string (P0, P1, P2, or P3)
        """
        # Check for regulatory auto-promotion
        regulatory = self.detect_regulatory_requirements(scenario)
        if any(regulatory.values()):
            return 'P0'
        
        # Calculate normalized score
        score = self.calculate_normalized_score(scenario)
        
        # Assign priority based on thresholds
        if score >= self.priority_thresholds['p0']:
            return 'P0'
        elif score >= self.priority_thresholds['p1']:
            return 'P1'
        elif score >= self.priority_thresholds['p2']:
            return 'P2'
        else:
            return 'P3'
    
    def calculate_normalized_score(self, scenario: Dict[str, Any]) -> float:
        """
        Calculate normalized score (0-100) from all criteria
        
        Args:
            scenario: Scenario dict with criteria data
            
        Returns:
            Normalized score 0-100
        """
        weighted_score = 0.0
        
        # Evaluate each criterion
        complexity_score = self.evaluate_complexity_criterion(scenario)
        weighted_score += complexity_score * (self.criteria_weights['complexity'] / 100)
        
        risk_score = self.calculate_risk_score(scenario)
        risk_normalized = min(risk_score / 10, 100)  # Normalize risk score
        weighted_score += risk_normalized * (self.criteria_weights['risk_score'] / 100)
        
        business_score = self.evaluate_business_value(scenario)
        weighted_score += business_score * (self.criteria_weights['business_value'] / 100)
        
        user_score = self.evaluate_user_impact(scenario)
        weighted_score += user_score * (self.criteria_weights['user_impact'] / 100)
        
        data_score = self.evaluate_data_integrity(scenario)
        weighted_score += data_score * (self.criteria_weights['data_integrity'] / 100)
        
        dependency_score = self.evaluate_dependency_risk(scenario)
        weighted_score += dependency_score * (self.criteria_weights['dependency_risk'] / 100)
        
        change_score = self.evaluate_change_frequency(scenario)
        weighted_score += change_score * (self.criteria_weights['change_frequency'] / 100)
        
        # Normalize to 0-100
        normalized = (weighted_score / self.total_weight) * 100
        return min(normalized, 100.0)
    
    def evaluate_complexity_criterion(self, scenario: Dict[str, Any]) -> float:
        """Evaluate complexity criterion (0-100)"""
        complexity = scenario.get('complexity', 0)
        
        if complexity >= 20:
            return 100.0  # Critical
        elif complexity >= 15:
            return 80.0   # High
        elif complexity >= 10:
            return 60.0   # Medium
        elif complexity > 0:
            return 40.0   # Low
        else:
            return 0.0
    
    def calculate_risk_score(self, scenario: Dict[str, Any]) -> float:
        """Calculate risk score = complexity × change_frequency"""
        complexity = scenario.get('complexity', 0)
        change_frequency = scenario.get('change_frequency', 0)
        return complexity * change_frequency
    
    def evaluate_business_value(self, scenario: Dict[str, Any]) -> float:
        """Evaluate business value from keywords (0-100)"""
        text = f"{scenario.get('name', '')} {scenario.get('description', '')}".lower()
        
        matches = sum(1 for keyword in self.BUSINESS_VALUE_KEYWORDS if keyword in text)
        
        if matches >= 3:
            return 100.0
        elif matches == 2:
            return 80.0
        elif matches == 1:
            return 60.0
        else:
            return 0.0
    
    def detect_regulatory_requirements(self, scenario: Dict[str, Any]) -> Dict[str, bool]:
        """Detect regulatory compliance requirements"""
        text = f"{scenario.get('name', '')} {scenario.get('description', '')}".lower()
        
        regulatory = {}
        for regulation, pattern in self.REGULATORY_PATTERNS.items():
            regulatory[regulation] = bool(re.search(pattern, text, re.IGNORECASE))
        
        return regulatory
    
    def evaluate_user_impact(self, scenario: Dict[str, Any]) -> float:
        """Evaluate user impact from endpoint traffic (0-100)"""
        endpoint_calls = scenario.get('endpoint_calls', 0)
        
        if endpoint_calls >= 1000:
            return 100.0  # Critical
        elif endpoint_calls >= 500:
            return 80.0   # High
        elif endpoint_calls >= 100:
            return 60.0   # Medium
        elif endpoint_calls > 0:
            return 40.0   # Low
        else:
            return 0.0
    
    def evaluate_data_integrity(self, scenario: Dict[str, Any]) -> float:
        """Evaluate data integrity criticality (0-100)"""
        text = f"{scenario.get('name', '')} {scenario.get('description', '')}".lower()
        
        matches = sum(1 for keyword in self.DATA_INTEGRITY_KEYWORDS if keyword in text)
        
        if matches >= 3:
            return 100.0
        elif matches == 2:
            return 80.0
        elif matches == 1:
            return 60.0
        else:
            return 0.0
    
    def evaluate_dependency_risk(self, scenario: Dict[str, Any]) -> float:
        """Evaluate external dependency risk (0-100)"""
        has_dependencies = scenario.get('has_external_dependencies', False)
        external_services = scenario.get('external_services', [])
        
        if has_dependencies and len(external_services) > 0:
            if len(external_services) >= 3:
                return 100.0
            elif len(external_services) == 2:
                return 70.0
            else:
                return 50.0
        elif has_dependencies:
            return 50.0
        else:
            return 0.0
    
    def evaluate_change_frequency(self, scenario: Dict[str, Any]) -> float:
        """Evaluate change frequency (regression risk) (0-100)"""
        change_frequency = scenario.get('change_frequency', 0)
        
        if change_frequency >= 20:
            return 100.0  # Critical
        elif change_frequency >= 10:
            return 80.0   # High
        elif change_frequency >= 5:
            return 60.0   # Medium
        elif change_frequency > 0:
            return 40.0   # Low
        else:
            return 0.0
    
    def prioritize_scenarios(self, scenarios: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prioritize a list of scenarios
        
        Args:
            scenarios: List of scenario dicts
            
        Returns:
            List of scenarios with priority and score added, sorted by priority
        """
        if not scenarios:
            return []
        
        # Add priority and score to each scenario
        for scenario in scenarios:
            scenario['score'] = self.calculate_normalized_score(scenario)
            scenario['priority'] = self.calculate_priority(scenario)
        
        # Sort by priority (P0 > P1 > P2 > P3), then by score
        priority_order = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
        scenarios.sort(key=lambda s: (priority_order.get(s['priority'], 3), -s['score']))
        
        return scenarios
    
    def generate_recommendations(self, scenarios: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate E2E test recommendations grouped by priority
        
        Args:
            scenarios: List of scenario dicts
            
        Returns:
            Dict with recommendations grouped by priority level
        """
        prioritized = self.prioritize_scenarios(scenarios)
        
        recommendations = {
            'p0_critical': [],
            'p1_high': [],
            'p2_medium': [],
            'p3_low': []
        }
        
        for scenario in prioritized:
            priority = scenario['priority']
            
            recommendation = {
                'scenario': scenario.get('name', 'Unknown'),
                'description': scenario.get('description', ''),
                'priority': priority,
                'score': scenario['score'],
                'rationale': self._generate_rationale(scenario)
            }
            
            if priority == 'P0':
                recommendations['p0_critical'].append(recommendation)
            elif priority == 'P1':
                recommendations['p1_high'].append(recommendation)
            elif priority == 'P2':
                recommendations['p2_medium'].append(recommendation)
            else:
                recommendations['p3_low'].append(recommendation)
        
        return recommendations
    
    def get_scoring_details(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed scoring breakdown for a scenario
        
        Args:
            scenario: Scenario dict
            
        Returns:
            Dict with criteria scores and totals
        """
        criteria_scores = {
            'complexity': self.evaluate_complexity_criterion(scenario),
            'risk_score': min(self.calculate_risk_score(scenario) / 10, 100),
            'business_value': self.evaluate_business_value(scenario),
            'user_impact': self.evaluate_user_impact(scenario),
            'data_integrity': self.evaluate_data_integrity(scenario),
            'dependency_risk': self.evaluate_dependency_risk(scenario),
            'change_frequency': self.evaluate_change_frequency(scenario)
        }
        
        regulatory = self.detect_regulatory_requirements(scenario)
        criteria_scores['regulatory'] = 100.0 if any(regulatory.values()) else 0.0
        
        total_score = self.calculate_normalized_score(scenario)
        priority = self.calculate_priority(scenario)
        
        return {
            'criteria_scores': criteria_scores,
            'total_score': total_score,
            'priority': priority,
            'regulatory_requirements': regulatory
        }
    
    def _generate_rationale(self, scenario: Dict[str, Any]) -> str:
        """Generate rationale for prioritization"""
        reasons = []
        
        # Check regulatory
        regulatory = self.detect_regulatory_requirements(scenario)
        if any(regulatory.values()):
            regs = [k for k, v in regulatory.items() if v]
            reasons.append(f"Regulatory compliance required: {', '.join(regs)}")
        
        # Check complexity
        complexity = scenario.get('complexity', 0)
        if complexity >= 20:
            reasons.append(f"High complexity ({complexity})")
        
        # Check business value
        if self.evaluate_business_value(scenario) >= 80:
            reasons.append("High business value (payment/financial)")
        
        # Check user impact
        calls = scenario.get('endpoint_calls', 0)
        if calls >= 1000:
            reasons.append(f"High user impact ({calls} calls)")
        
        # Check change frequency
        changes = scenario.get('change_frequency', 0)
        if changes >= 20:
            reasons.append(f"High regression risk ({changes} changes)")
        
        if not reasons:
            return "Standard test coverage"
        
        return "; ".join(reasons)
