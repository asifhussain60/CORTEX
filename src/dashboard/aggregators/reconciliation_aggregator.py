"""
Reconciliation Aggregator

Cross-collector gap analysis and data consistency checks

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class ReconciliationAggregator:
    """Performs cross-collector reconciliation and gap analysis"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
    
    def aggregate(self) -> Dict[str, Any]:
        """Generate reconciliation.json from all collectors"""
        
        # Load all collector data
        health = self._load_json("health-data.json")
        tech = self._load_json("tech-stack.json")
        security = self._load_json("security.json")
        architecture = self._load_json("architecture.json")
        code_org = self._load_json("code-organization.json")
        overview = self._load_json("overview.json")
        
        # Extract key metrics for reconciliation
        reconciled_data = {
            "security_score": security.get("overall_score", 0),
            "quality_score": health.get("metrics", {}).get("code_quality_score", 0),
            "maintainability_score": code_org.get("summary", {}).get("maintainability_score", 0),
            "architecture_score": architecture.get("metrics", {}).get("overall_score", 0),
            "test_coverage": health.get("summary", {}).get("test_coverage", 0),
            "critical_vulnerabilities": sum(1 for v in security.get("vulnerabilities", []) if isinstance(v, dict) and v.get("severity") == "critical"),
            "high_vulnerabilities": sum(1 for v in security.get("vulnerabilities", []) if isinstance(v, dict) and v.get("severity") == "high"),
            "code_smells": code_org.get("summary", {}).get("code_smell_count", 0),
            "cyclomatic_complexity": code_org.get("summary", {}).get("avg_complexity", 0),
            "security_hotspots": len([h for h in code_org.get("hotspots", []) if h.get("risk_level") in ("high", "critical")]),
            "overall_score": overview.get("overall_health", {}).get("score", 0)
        }
        
        # Detect violations (inconsistencies)
        violations = self._detect_violations(reconciled_data)
        
        # Detect anomalies
        anomalies = self._detect_anomalies(reconciled_data, health, security, architecture)
        
        # Build audit trail
        audit_trail = self._build_audit_trail(violations, anomalies)
        
        return {
            "reconciliation_timestamp": datetime.now().isoformat(),
            "reconciliation_version": "1.0.0",
            "repository": self.data_dir.name,
            "execution_time_ms": 0.0,
            "reconciled_data": reconciled_data,
            "violations": violations,
            "anomalies": anomalies,
            "audit_trail": audit_trail,
            "metrics": {
                "total_adjustments": len(violations),
                "total_anomalies": len(anomalies),
                "data_quality_score": 100 - (len(violations) * 5 + len(anomalies) * 3)
            }
        }
    
    def _detect_violations(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect rule violations and inconsistencies"""
        violations = []
        
        # Rule: High complexity inconsistent with high maintainability
        if data["cyclomatic_complexity"] > 20 and data["maintainability_score"] > 80:
            violations.append({
                "rule_id": "R10_MAINTAINABILITY_COMPLEXITY_INVERSE",
                "severity": "medium",
                "category": "maintainability",
                "message": f"High complexity ({data['cyclomatic_complexity']}) inconsistent with high maintainability ({data['maintainability_score']})",
                "original_score": data["maintainability_score"],
                "adjusted_score": max(70, data["maintainability_score"] - data["cyclomatic_complexity"]),
                "adjustment": min(-data["cyclomatic_complexity"], -22),
                "rationale": f"Complexity of {data['cyclomatic_complexity']} indicates maintenance challenges"
            })
        
        # Rule: Both security and quality below threshold
        if data["security_score"] < 50 and data["quality_score"] < 50:
            original = data["overall_score"]
            adjusted = max(50, original - 10)
            violations.append({
                "rule_id": "R8",
                "severity": "high",
                "category": "overall",
                "message": f"Both security ({data['security_score']}) and quality ({data['quality_score']}) are below 50",
                "original_score": original,
                "adjusted_score": adjusted,
                "adjustment": adjusted - original,
                "rationale": "When both security and quality are weak, system is at significant risk"
            })
        
        # Rule: Test coverage below threshold but high quality score
        if data["test_coverage"] < 50 and data["quality_score"] > 80:
            violations.append({
                "rule_id": "R12_QUALITY_TEST_COVERAGE",
                "severity": "medium",
                "category": "quality",
                "message": f"Test coverage ({data['test_coverage']}%) is low despite high quality score ({data['quality_score']})",
                "original_score": data["quality_score"],
                "adjusted_score": max(60, data["quality_score"] - 20),
                "adjustment": -20,
                "rationale": "Quality score should reflect inadequate test coverage"
            })
        
        return violations
    
    def _detect_anomalies(self, data: Dict[str, Any], health: Dict, security: Dict, architecture: Dict) -> List[Dict[str, Any]]:
        """Detect statistical anomalies and inconsistencies"""
        anomalies = []
        
        # Anomaly: High architecture score but low security score
        arch_score = data["architecture_score"]
        sec_score = data["security_score"]
        if arch_score > 80 and sec_score < 50:
            anomalies.append({
                "type": "score_inconsistency",
                "confidence": 0.95,
                "category": "architecture_security",
                "message": f"Architecture score ({arch_score}) is high but security score ({sec_score}) is low",
                "recommendation": "Review architecture for security design patterns (defense in depth, least privilege, etc.)",
                "z_score": None,
                "metadata": {
                    "architecture_score": arch_score,
                    "security_score": sec_score,
                    "gap": arch_score - sec_score
                }
            })
        
        # Anomaly: High vulnerability count but high overall score
        high_vulns = data["high_vulnerabilities"] + data["critical_vulnerabilities"]
        overall = data["overall_score"]
        if high_vulns > 10 and overall > 80:
            anomalies.append({
                "type": "vulnerability_mismatch",
                "confidence": 0.90,
                "category": "security_overall",
                "message": f"{high_vulns} high/critical vulnerabilities found but overall score is {overall}",
                "recommendation": "Address high-severity vulnerabilities immediately to align with overall health assessment",
                "z_score": None,
                "metadata": {
                    "vulnerability_count": high_vulns,
                    "overall_score": overall
                }
            })
        
        # Anomaly: High code smells but high maintainability
        code_smells = data["code_smells"]
        maint_score = data["maintainability_score"]
        if code_smells > 50 and maint_score > 85:
            anomalies.append({
                "type": "maintainability_smell_mismatch",
                "confidence": 0.85,
                "category": "code_quality",
                "message": f"{code_smells} code smells detected but maintainability score is {maint_score}",
                "recommendation": "Refactor code to address smells and improve long-term maintainability",
                "z_score": None,
                "metadata": {
                    "code_smell_count": code_smells,
                    "maintainability_score": maint_score
                }
            })
        
        return anomalies
    
    def _build_audit_trail(self, violations: List[Dict], anomalies: List[Dict]) -> Dict[str, Any]:
        """Build audit trail of changes and detections"""
        
        changes = []
        for violation in violations:
            changes.append({
                "category": violation["category"],
                "field": "score",
                "before": violation["original_score"],
                "after": violation["adjusted_score"],
                "reason": f"{violation['rule_id']}: {violation['message']}",
                "timestamp": datetime.now().isoformat()
            })
        
        return {
            "changes": changes,
            "rules_triggered": len(violations),
            "anomalies_detected": len(anomalies),
            "execution_time_ms": 0.0
        }
    
    def _load_json(self, filename: str) -> Dict[str, Any]:
        """Load JSON file with error handling"""
        file_path = self.data_dir / filename
        if file_path.exists():
            try:
                return json.loads(file_path.read_text())
            except:
                return {}
        return {}


def main():
    """CLI entry point"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python reconciliation_aggregator.py <data_dir>")
        sys.exit(1)
    
    data_dir = Path(sys.argv[1])
    aggregator = ReconciliationAggregator(data_dir)
    result = aggregator.aggregate()
    
    output_path = data_dir / "reconciliation.json"
    output_path.write_text(json.dumps(result, indent=2))
    print(f"Generated: {output_path}")


if __name__ == "__main__":
    main()
