"""ExpertRegistry - domain expert registry (KN-003-02)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


_REPO_ROOT = Path(__file__).resolve().parents[4]
_REGISTRY_PATH = (
    _REPO_ROOT
    / "tests"
    / "cortex.intelligence"
    / "tier3"
    / "knowledge"
    / "expert-registry.yaml"
)
_VALID_DOMAINS = [
    "GOVERNANCE",
    "INTENT-ROUTING",
    "HALLUCINATION-PREVENTION",
    "EXECUTION-ORCHESTRATION",
    "DATA-MANAGEMENT",
    "OBSERVABILITY",
    "SECURITY",
    "API-DESIGN",
    "ML-MODELS",
    "KNOWLEDGE-CURATION",
    "TESTING-VALIDATION",
    "DEPLOYMENT",
    "DOCUMENTATION",
    "PERFORMANCE",
    "ARCHITECTURE",
    "ERROR-HANDLING",
]
_EXPERTISE_LEVELS = ["expert", "advanced", "intermediate"]


@dataclass
class Expert:
    """Domain expert profile for knowledge validation workflows.

    Args:
        expert_id: Stable expert identifier.
        name: Display name.
        email: Contact email.
        domains: Domains the expert can validate.
        expertise_level: Expertise classification.
        active: Whether the expert is active.
    """

    expert_id: str
    name: str
    email: str
    domains: List[str]
    expertise_level: str
    active: bool = True


_DEFAULT_EXPERTS = [
    Expert("EXPERT-001", "Governance Lead", "governance@cortex.local", ["GOVERNANCE"], "expert"),
    Expert("EXPERT-002", "Routing Architect", "routing@cortex.local", ["INTENT-ROUTING"], "expert"),
    Expert("EXPERT-003", "Safety Analyst", "safety@cortex.local", ["HALLUCINATION-PREVENTION"], "advanced"),
    Expert("EXPERT-004", "Execution Coordinator", "execution@cortex.local", ["EXECUTION-ORCHESTRATION"], "expert"),
    Expert("EXPERT-005", "Data Steward", "data@cortex.local", ["DATA-MANAGEMENT"], "advanced"),
    Expert("EXPERT-006", "Observability Engineer", "observability@cortex.local", ["OBSERVABILITY"], "expert"),
    Expert("EXPERT-007", "Security Reviewer", "security@cortex.local", ["SECURITY"], "expert"),
    Expert("EXPERT-008", "API Designer", "api@cortex.local", ["API-DESIGN"], "advanced"),
    Expert("EXPERT-009", "ML Reviewer", "ml@cortex.local", ["ML-MODELS"], "advanced"),
    Expert("EXPERT-010", "Knowledge Curator", "knowledge@cortex.local", ["KNOWLEDGE-CURATION"], "expert"),
    Expert("EXPERT-011", "Test Strategist", "testing@cortex.local", ["TESTING-VALIDATION"], "expert"),
    Expert("EXPERT-012", "Release Engineer", "deployment@cortex.local", ["DEPLOYMENT"], "advanced"),
    Expert("EXPERT-013", "Documentation Editor", "docs@cortex.local", ["DOCUMENTATION"], "advanced"),
    Expert("EXPERT-014", "Performance Analyst", "performance@cortex.local", ["PERFORMANCE"], "expert"),
    Expert("EXPERT-015", "Systems Architect", "architecture@cortex.local", ["ARCHITECTURE"], "expert"),
    Expert("EXPERT-016", "Resilience Engineer", "errors@cortex.local", ["ERROR-HANDLING"], "advanced"),
]


class ExpertRegistry:
    """Registry of domain experts with compatibility APIs for KN-003-02."""

    ac_id = "KN-003-02"

    def __init__(self, registry_path: Optional[str] = None) -> None:
        """Initialise expert registry from YAML file.

        Args:
            registry_path: Optional explicit registry path.
        """
        self._path = Path(registry_path) if registry_path else _REGISTRY_PATH
        self._experts: Optional[List[Expert]] = None
        self._validation_log: List[Dict[str, Any]] = []
        self._ensure_registry_file()

    def _ensure_registry_file(self) -> None:
        """Create the default registry YAML when it is missing."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if self._path.exists():
            return

        payload = {
            "metadata": {
                "ac_id": self.ac_id,
                "version": "1.0",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            },
            "experts": [self._serialize_expert(expert) for expert in _DEFAULT_EXPERTS],
        }
        self._path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    def _load(self) -> List[Expert]:
        """Load experts from the registry file.

        Returns:
            Parsed list of experts.
        """
        if self._experts is None:
            data = yaml.safe_load(self._path.read_text(encoding="utf-8")) or {}
            self._experts = [self._hydrate_expert(item) for item in data.get("experts", [])]
        return self._experts

    def _hydrate_expert(self, payload: Dict[str, Any]) -> Expert:
        """Convert YAML payload into an Expert model.

        Args:
            payload: Expert dictionary from YAML.

        Returns:
            Hydrated expert instance.
        """
        return Expert(
            expert_id=str(payload.get("expert_id") or payload.get("id") or ""),
            name=str(payload.get("name", "")),
            email=str(payload.get("email") or payload.get("contact") or ""),
            domains=list(payload.get("domains", [])),
            expertise_level=str(payload.get("expertise_level", "intermediate")),
            active=bool(payload.get("active", True)),
        )

    def _serialize_expert(self, expert: Expert) -> Dict[str, Any]:
        """Convert an Expert model into YAML-safe data.

        Args:
            expert: Expert to serialize.

        Returns:
            Serialized expert dictionary.
        """
        return {
            "expert_id": expert.expert_id,
            "name": expert.name,
            "email": expert.email,
            "domains": expert.domains,
            "expertise_level": expert.expertise_level,
            "active": expert.active,
        }

    def _persist(self) -> None:
        """Persist the current expert set and metadata back to YAML."""
        payload = {
            "metadata": {
                "ac_id": self.ac_id,
                "version": "1.0",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            },
            "experts": [self._serialize_expert(expert) for expert in self._load()],
        }
        self._path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    def get_all_experts(self) -> List[Expert]:
        """Return all registered experts.

        Returns:
            All experts from the registry.
        """
        return list(self._load())

    def get_expert(self, expert_id: str) -> Optional[Expert]:
        """Retrieve a single expert by ID.

        Args:
            expert_id: Expert identifier.

        Returns:
            Matching expert when found, otherwise None.
        """
        for expert in self._load():
            if expert.expert_id == expert_id:
                return expert
        return None

    def get_experts_by_domain(self, domain: str) -> List[Expert]:
        """Return experts that cover a given domain.

        Args:
            domain: Canonical domain name.

        Returns:
            Experts assigned to the domain.
        """
        return [expert for expert in self._load() if domain in expert.domains and expert.active]

    def find_by_domain(self, domain: str) -> List[Expert]:
        """Backward-compatible alias for domain expert lookup.

        Args:
            domain: Canonical domain name.

        Returns:
            Experts assigned to the domain.
        """
        return self.get_experts_by_domain(domain)

    def add_expert(self, expert: Expert) -> bool:
        """Add a new expert to the registry.

        Args:
            expert: Expert to register.

        Returns:
            True when the expert is persisted.
        """
        if expert.expertise_level not in _EXPERTISE_LEVELS:
            raise ValueError(f"Invalid expertise level: {expert.expertise_level}")
        for domain in expert.domains:
            if domain not in _VALID_DOMAINS:
                raise ValueError(f"Invalid domain: {domain}")
        experts = self._load()
        experts.append(expert)
        self._experts = experts
        self._persist()
        return True

    def register(self, expert: Expert) -> bool:
        """Backward-compatible alias for adding experts.

        Args:
            expert: Expert to register.

        Returns:
            True when the expert is persisted.
        """
        return self.add_expert(expert)

    def is_expert_for_domain(self, expert_id: str, domain: str) -> bool:
        """Return whether an expert covers a domain.

        Args:
            expert_id: Expert identifier.
            domain: Canonical domain name.

        Returns:
            True when the expert can validate the domain.
        """
        expert = self.get_expert(expert_id)
        return bool(expert and expert.active and domain in expert.domains)

    def can_validate_entry(self, expert_id: str, domain: str) -> bool:
        """Return whether an expert can validate a knowledge entry.

        Args:
            expert_id: Expert identifier.
            domain: Canonical domain name.

        Returns:
            True when validation is allowed.
        """
        return self.is_expert_for_domain(expert_id, domain)

    def log_validation(
        self,
        expert_id: str,
        entry_id: str,
        domain: str,
        result: str = "approved",
    ) -> bool:
        """Append a validation event to the in-memory log.

        Args:
            expert_id: Expert performing the validation.
            entry_id: Knowledge entry identifier.
            domain: Domain validated.
            result: Validation outcome.

        Returns:
            True when the log entry is recorded.
        """
        self._validation_log.append(
            {
                "expert_id": expert_id,
                "entry_id": entry_id,
                "domain": domain,
                "result": result,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        return True

    def get_validation_log(self) -> List[Dict[str, Any]]:
        """Return the validation log.

        Returns:
            Recorded validation events.
        """
        return list(self._validation_log)

    def validate_entry_with_expert(self, expert_id: str, entry_id: str, domain: str) -> bool:
        """Validate an entry with an expert and log the outcome.

        Args:
            expert_id: Expert identifier.
            entry_id: Knowledge entry identifier.
            domain: Domain being validated.

        Returns:
            True when validation succeeds.
        """
        allowed = self.can_validate_entry(expert_id, domain)
        self.log_validation(
            expert_id=expert_id,
            entry_id=entry_id,
            domain=domain,
            result="approved" if allowed else "rejected",
        )
        return allowed

    def get_validation_workflow(self, expert_id: str) -> Optional[str]:
        """Return the validation workflow for an expert.

        Args:
            expert_id: Expert identifier.

        Returns:
            Static workflow name for active experts, otherwise None.
        """
        return "peer_review" if self.get_expert(expert_id) else None
