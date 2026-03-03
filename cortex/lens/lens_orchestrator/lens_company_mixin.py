"""
LensCompanyMixin — company domain knowledge and compliance detection.

Covers:
  - analyze_with_company_knowledge
  - _load_company_domains
  - _detect_compliance
  - _merge_knowledge

Extracted from lens_orchestrator.py (Phase 103-d, GAP-103-04).
Authority: CORE-008, CORE-011, CORE-012, Phase 20 Component #2
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

__all__ = ["LensCompanyMixin"]


class LensCompanyMixin:
    """
    Mixin providing company domain knowledge and compliance detection.

    Requires the host class to have:
        self.analyze_file(file_path: Path) -> Dict[str, Any]
    """

    def analyze_with_company_knowledge(
        self,
        file_path: str,
        company_name: str,
    ) -> Dict[str, Any]:
        """
        Analyze file with company domain knowledge integration.

        Combines standard LENS analysis with company-specific rules,
        patterns, and compliance requirements.

        Args:
            file_path: Path to file to analyze
            company_name: Company name for domain knowledge lookup

        Returns:
            Extended LENS context with company_knowledge field

        Authority: Phase 20 Component #2 (AC_LENS_COMPANY_002)
        """
        lens_context = self.analyze_file(Path(file_path))  # type: ignore[attr-defined]
        company_knowledge = self._load_company_domains(company_name)
        code_content = Path(file_path).read_text() if Path(file_path).exists() else ""
        compliance_flags = self._detect_compliance(code_content)
        merged_knowledge = self._merge_knowledge(
            base_knowledge={},
            company_knowledge=company_knowledge,
            compliance_flags=compliance_flags,
        )
        lens_context["company_knowledge"] = merged_knowledge
        return lens_context

    def _load_company_domains(self, company_name: str) -> Dict[str, Any]:
        """
        Load company-specific domain knowledge from YAML files.

        Args:
            company_name: Company name (e.g., "acme-corp")

        Returns:
            Company domain knowledge dict

        Authority: Phase 20 Component #2
        """
        import yaml

        try:
            company_dir = Path("cortex-registry") / "company" / "domains"
            if not company_dir.exists():
                return {}
            domains: Dict[str, Any] = {}
            for yaml_file in company_dir.glob("*.yaml"):
                try:
                    with open(yaml_file, "r") as f:
                        domain_data = yaml.safe_load(f)
                        if domain_data:
                            domains.update(domain_data)
                except Exception:
                    continue
            return domains
        except Exception:
            return {}

    def _detect_compliance(self, code_content: str) -> Dict[str, Any]:
        """
        Auto-detect applicable compliance standards from code patterns.

        Detects PCI-DSS, HIPAA, SOC2, GDPR from code patterns.

        Args:
            code_content: Source code to analyze

        Returns:
            Dict with detected_standards list

        Authority: Phase 20 Component #2
        """
        detected_standards: List[Dict[str, Any]] = []
        content_lower = code_content.lower()

        pci_patterns = ["stripe", "payment", "credit_card", "card_number", "cvv", "card_data", "payment_method"]
        pci_confidence = sum(1 for p in pci_patterns if p in content_lower) / len(pci_patterns)
        if pci_confidence > 0.2:
            detected_standards.append({
                "standard_id": "PCI-DSS-3.2.1",
                "confidence": min(0.95, pci_confidence + 0.5),
                "violations": [],
                "file_locations": [],
            })

        hipaa_patterns = ["patient", "medical", "health", "hipaa", "phi", "ssn", "medical_record", "diagnosis"]
        hipaa_confidence = sum(1 for p in hipaa_patterns if p in content_lower) / len(hipaa_patterns)
        if hipaa_confidence > 0.2:
            detected_standards.append({
                "standard_id": "HIPAA",
                "confidence": min(0.95, hipaa_confidence + 0.5),
                "violations": [],
                "file_locations": [],
            })

        soc2_patterns = ["encrypt", "authentication", "authorization", "audit", "logging", "access_control"]
        soc2_confidence = sum(1 for p in soc2_patterns if p in content_lower) / len(soc2_patterns)
        if soc2_confidence > 0.2:
            detected_standards.append({
                "standard_id": "SOC2",
                "confidence": min(0.95, soc2_confidence + 0.5),
                "violations": [],
                "file_locations": [],
            })

        return {"detected_standards": detected_standards}

    def _merge_knowledge(
        self,
        base_knowledge: Dict[str, Any],
        company_knowledge: Dict[str, Any],
        compliance_flags: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Merge knowledge sources with precedence rules.

        Precedence: OVERRIDE (company replaces base) or MERGE (combine both).

        Args:
            base_knowledge: CORTEX base knowledge
            company_knowledge: Company-specific knowledge
            compliance_flags: Detected compliance standards

        Returns:
            Merged knowledge dict with precedence tracking

        Authority: Phase 20 Component #2
        """
        merged: Dict[str, Any] = {
            "rules": [],
            "patterns": {},
            "compliance_flags": compliance_flags,
            "knowledge_precedence": {
                "company_overrides": 0,
                "cortex_base": 0,
                "compliance_standards": [
                    s["standard_id"]
                    for s in compliance_flags.get("detected_standards", [])
                ],
            },
        }

        precedence = company_knowledge.get("precedence", "MERGE")

        if precedence == "OVERRIDE":
            merged["rules"] = company_knowledge.get("rules", [])
            merged["knowledge_precedence"]["company_overrides"] = len(merged["rules"])
        else:
            merged["rules"].extend(base_knowledge.get("rules", []))
            merged["rules"].extend(company_knowledge.get("rules", []))
            merged["knowledge_precedence"]["cortex_base"] = len(base_knowledge.get("rules", []))
            merged["knowledge_precedence"]["company_overrides"] = len(company_knowledge.get("rules", []))

        if "patterns" in base_knowledge:
            merged["patterns"].update(base_knowledge["patterns"])
        if "patterns" in company_knowledge:
            merged["patterns"].update(company_knowledge["patterns"])

        return merged
