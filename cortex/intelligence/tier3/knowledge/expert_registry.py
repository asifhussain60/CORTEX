"""ExpertRegistry — domain expert registry (KN-003-02)."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


_REGISTRY_PATH = (
    Path(__file__).parent.parent.parent.parent.parent.parent
    / "cortex_intelligence" / "tier3" / "knowledge" / "expert-registry.yaml"
)


@dataclass
class Expert:
    id: str
    name: str
    domains: List[str]
    expertise_level: str
    validation_workflow: str = "peer_review"
    contact: Optional[str] = None


class ExpertRegistry:
    """Registry of domain experts with expertise area mapping."""

    def __init__(self, registry_path: Optional[str] = None) -> None:
        self._path = Path(registry_path) if registry_path else _REGISTRY_PATH
        self._experts: Optional[List[Expert]] = None

    def _load(self) -> List[Expert]:
        if self._experts is None:
            if self._path.exists():
                data = yaml.safe_load(self._path.read_text()) or {}
                self._experts = [
                    Expert(
                        id=e.get("id", ""),
                        name=e.get("name", ""),
                        domains=e.get("domains", []),
                        expertise_level=e.get("expertise_level", "senior"),
                        validation_workflow=e.get("validation_workflow", "peer_review"),
                    )
                    for e in data.get("experts", [])
                ]
            else:
                self._experts = []
        return self._experts

    def get_all_experts(self) -> List[Expert]:
        return self._load()

    def find_by_domain(self, domain: str) -> List[Expert]:
        return [e for e in self._load() if domain in e.domains]

    def get_expert(self, expert_id: str) -> Optional[Expert]:
        for e in self._load():
            if e.id == expert_id:
                return e
        return None

    def register(self, expert: Expert) -> bool:
        experts = self._load()
        experts.append(expert)
        self._experts = experts
        if self._path.parent.exists():
            data = yaml.safe_load(self._path.read_text()) if self._path.exists() else {}
            data.setdefault("experts", []).append({
                "id": expert.id,
                "name": expert.name,
                "domains": expert.domains,
                "expertise_level": expert.expertise_level,
                "validation_workflow": expert.validation_workflow,
            })
            self._path.write_text(yaml.dump(data, allow_unicode=True))
        return True

    def get_validation_workflow(self, expert_id: str) -> Optional[str]:
        expert = self.get_expert(expert_id)
        return expert.validation_workflow if expert else None
