"""Requirements Engineer — AC scenario generation from feature descriptions (GAP-129-02)."""

from __future__ import annotations

import re
from typing import Any, Dict, List


class RequirementsEngineer:
    """Generates Gherkin-format acceptance criteria from feature descriptions.

    Each AC scenario is a string in Given/When/Then format.
    """

    POSITIVE_TEMPLATES = [
        "Given {actor} is authenticated\n  When {actor} {action}\n  Then {outcome}",
        "Given {actor} has submitted {input}\n  When the system processes the request\n  Then {outcome}",
        "Given the feature is enabled\n  When {actor} accesses {feature_name}\n  Then {actor} sees the expected result",
    ]

    NEGATIVE_TEMPLATES = [
        "Given {actor} is not authenticated\n  When {actor} attempts to {action}\n  Then the system returns an error",
        "Given {actor} provides invalid input\n  When {actor} submits the form\n  Then the system displays a validation error",
    ]

    EDGE_TEMPLATES = [
        "Given {actor} has no data available\n  When {actor} views {feature_name}\n  Then an empty state message is displayed",
        "Given the system is under high load\n  When {actor} performs {action}\n  Then the response time remains within SLA",
    ]

    def generate_ac(
        self, feature_description: str, actor: str = "the user"
    ) -> List[str]:
        """Generate Gherkin acceptance criteria from a feature description.

        Returns a list of Gherkin scenario strings (Given/When/Then).
        Generates: 3 positive + 2 negative + 2 edge-case scenarios minimum.
        """
        action = self._extract_action(feature_description)
        outcome = self._extract_outcome(feature_description)
        input_phrase = self._extract_input(feature_description)
        feature_name = self._extract_feature_name(feature_description)

        context = {
            "actor": actor,
            "action": action,
            "outcome": outcome,
            "input": input_phrase,
            "feature_name": feature_name,
        }

        scenarios: List[str] = []

        for template in self.POSITIVE_TEMPLATES:
            scenarios.append(f"Scenario: Happy path\n  {template.format(**context)}")

        for template in self.NEGATIVE_TEMPLATES:
            scenarios.append(f"Scenario: Error case\n  {template.format(**context)}")

        for template in self.EDGE_TEMPLATES:
            scenarios.append(f"Scenario: Edge case\n  {template.format(**context)}")

        return scenarios

    def generate_ac_structured(
        self, feature_description: str, actor: str = "the user"
    ) -> List[Dict[str, str]]:
        """Return structured AC scenarios as dicts with type, given, when, then."""
        _LABEL_TO_TYPE = {
            "happy path": "positive",
            "error case": "negative",
            "edge case": "edge",
        }
        scenarios_raw = self.generate_ac(feature_description, actor)
        structured = []
        for scenario in scenarios_raw:
            lines = scenario.split("\n")
            raw_label = lines[0].replace("Scenario:", "").strip().lower() if lines else "unknown"
            scenario_type = _LABEL_TO_TYPE.get(raw_label, raw_label)
            given = next((l.strip().replace("Given ", "") for l in lines if "Given" in l), "")
            when = next((l.strip().replace("When ", "") for l in lines if "When" in l), "")
            then = next((l.strip().replace("Then ", "") for l in lines if "Then" in l), "")
            structured.append({"type": scenario_type, "given": given, "when": when, "then": then})
        return structured

    @staticmethod
    def _extract_action(description: str) -> str:
        verbs = re.findall(r"\b(view|create|edit|delete|submit|search|filter|export|import|upload|download|login|register)\b", description, re.IGNORECASE)
        if verbs:
            return f"{verbs[0].lower()}s the feature"
        return "performs the action"

    @staticmethod
    def _extract_outcome(description: str) -> str:
        if "sees" in description.lower() or "view" in description.lower():
            return "the result is displayed correctly"
        if "save" in description.lower() or "create" in description.lower():
            return "the item is saved successfully"
        return "the expected outcome is achieved"

    @staticmethod
    def _extract_input(description: str) -> str:
        match = re.search(r"\b(a|an|the)\s+(\w+\s+\w+)", description, re.IGNORECASE)
        return match.group(0) if match else "the required data"

    @staticmethod
    def _extract_feature_name(description: str) -> str:
        words = description.split()
        return " ".join(words[:3]) if len(words) >= 3 else description or "the feature"
