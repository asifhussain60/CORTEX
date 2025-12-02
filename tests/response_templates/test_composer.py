import os
from pathlib import Path

from src.response_templates.composer import TemplateComposer


def test_composer_falls_back_to_monolithic_and_routes_onboarding():
    # Ensure modular flag is off for fallback
    os.environ.pop("CORTEX_TEMPLATES_MODULAR", None)

    project_root = Path(__file__).resolve().parents[2]
    composer = TemplateComposer(project_root)

    # Should load monolithic templates and expose routing
    routing = composer.get_routing_table()
    assert isinstance(routing, dict) and len(routing) > 0

    # A known trigger in the monolithic file is 'onboard' -> template 'onboarding'
    result = composer.get_template_by_trigger("onboard")
    assert result is not None, "Expected to find a template for 'onboard'"
    tpl_name, tpl = result
    assert tpl_name == "onboarding"
    assert isinstance(tpl, dict)


def test_composer_uses_modular_when_enabled_if_present(monkeypatch):
    # Enable modular mode
    monkeypatch.setenv("CORTEX_TEMPLATES_MODULAR", "1")

    project_root = Path(__file__).resolve().parents[2]
    composer = TemplateComposer(project_root)

    routing = composer.get_routing_table()
    # Our scaffold includes a 'fallback' and 'planning_overview' entries in routing.yaml
    assert "fallback" in routing
    assert any(t.lower() == "fallback" for t in routing.get("fallback", []))
