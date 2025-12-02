"""
Template Composer (Phase 5 Scaffold)

Loads modular response template YAMLs (base-components.yaml, templates.yaml,
profiles.yaml, routing.yaml) when enabled, otherwise falls back to the
monolithic cortex-brain/response-templates.yaml.

Goals:
- Provide a stable API for routing and template retrieval
- Keep backward compatibility during migration

Usage:
    composer = TemplateComposer(project_root)
    composer.load()  # lazy-load by default
    tpl = composer.get_template_by_trigger("onboard")

Feature flag (env): CORTEX_TEMPLATES_MODULAR=1 to prefer modular set if present.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml


class TemplateComposer:
    def __init__(self, project_root: Path | str):
        self.project_root = Path(project_root)
        self.brain_path = self.project_root / "cortex-brain"
        self.modular_dir = self.brain_path / "response-templates"
        self.monolithic_file = self.brain_path / "response-templates.yaml"
        self._loaded = False
        self._use_modular = os.getenv("CORTEX_TEMPLATES_MODULAR", "0") == "1"

        # In-memory state
        self._components: Dict[str, Any] = {}
        self._templates: Dict[str, Any] = {}
        self._profiles: Dict[str, Any] = {}
        self._routing: Dict[str, List[str]] = {}

    # --------- Public API ---------
    def load(self) -> None:
        if self._loaded:
            return
        if self._use_modular and self._modular_available():
            self._load_modular()
        else:
            self._load_monolithic()
        self._loaded = True

    def get_routing_table(self) -> Dict[str, List[str]]:
        self.load()
        return dict(self._routing)

    def get_template(self, name: str) -> Optional[Dict[str, Any]]:
        self.load()
        return self._templates.get(name)

    def get_template_by_trigger(self, trigger: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Return (template_name, template_data) for a given trigger, if found."""
        self.load()
        t = trigger.lower().strip()
        for tpl_name, triggers in self._routing.items():
            if any(t == tr.lower() for tr in triggers):
                tpl = self._templates.get(tpl_name)
                if tpl is not None:
                    return tpl_name, tpl
        return None

    # --------- Loading helpers ---------
    def _modular_available(self) -> bool:
        # Require at least templates.yaml and routing.yaml to be present
        return (self.modular_dir / "templates.yaml").exists() and (self.modular_dir / "routing.yaml").exists()

    def _load_modular(self) -> None:
        components_path = self.modular_dir / "base-components.yaml"
        templates_path = self.modular_dir / "templates.yaml"
        profiles_path = self.modular_dir / "profiles.yaml"
        routing_path = self.modular_dir / "routing.yaml"

        if components_path.exists():
            self._components = self._safe_yaml_load(components_path).get("components", {})
        self._templates = self._safe_yaml_load(templates_path).get("templates", {})
        if profiles_path.exists():
            self._profiles = self._safe_yaml_load(profiles_path).get("profiles", {})

        raw_routing = self._safe_yaml_load(routing_path).get("routing", {})
        # Normalize routing to {template_name: [triggers]}
        routing: Dict[str, List[str]] = {}
        for key, val in raw_routing.items():
            if isinstance(val, dict) and "triggers" in val and isinstance(val["triggers"], list):
                routing[key] = [str(x) for x in val["triggers"]]
        self._routing = routing

    def _load_monolithic(self) -> None:
        data = self._safe_yaml_load(self.monolithic_file)
        # Extract templates and routing from monolith
        templates = data.get("templates", {})
        self._templates = templates if isinstance(templates, dict) else {}

        routing: Dict[str, List[str]] = {}
        if isinstance(self._templates, dict):
            for tpl_name, tpl in self._templates.items():
                if isinstance(tpl, dict):
                    triggers = tpl.get("triggers") or tpl.get("routing", {}).get("triggers")
                    if isinstance(triggers, list):
                        routing[tpl_name] = [str(x) for x in triggers]
        self._routing = routing

    @staticmethod
    def _safe_yaml_load(path: Path) -> Dict[str, Any]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            if not isinstance(data, dict):
                return {}
            return data
        except FileNotFoundError:
            return {}
        except Exception:
            # In scaffold, swallow errors; production code should log
            return {}
