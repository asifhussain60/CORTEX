"""
provider_factory — Env-driven factory for WorkItemProvider instances.

Reads the ``WORK_ITEM_SOURCE`` environment variable to select and
instantiate the correct concrete WorkItemProvider. Companies add a
new ``elif`` branch here when they introduce a new provider; no other
CORTEX files need to change.

Supported values of WORK_ITEM_SOURCE:
    "ado"  (default) — Azure DevOps via ADOWorkItemProvider
    Any other value  — raises ValueError with the unsupported source name

Required env vars per provider:
    ado:
        ADO_ORG_URL  — e.g. "https://dev.azure.com/your-org"
        ADO_PAT      — Personal Access Token (may be empty for managed identity)
        ADO_PROJECT  — Default project name

Authority: CORE-011 (type hints) · CORE-012 (docstrings) · CORE-035 (single canonical)
Phase: Phase 15 — Work Item Provider
AC-IDs: AC-P15-004, AC-P15-005
"""

from __future__ import annotations

import os

from cortex.repositories.work_item_provider import WorkItemProvider


def get_work_item_provider() -> WorkItemProvider:
    """
    Instantiate and return the configured WorkItemProvider.

    Reads ``WORK_ITEM_SOURCE`` from the environment (defaults to ``"ado"``).
    Raises ``ValueError`` for any unrecognised source value so misconfiguration
    fails loudly at startup rather than silently returning wrong data.

    Returns:
        A concrete WorkItemProvider ready to call.

    Raises:
        ValueError: When ``WORK_ITEM_SOURCE`` is set to an unknown value.

    Example::

        import os
        os.environ["WORK_ITEM_SOURCE"] = "ado"
        provider = get_work_item_provider()
        stories = provider.fetch_user_stories("MyProject")
    """
    source = os.getenv("WORK_ITEM_SOURCE", "ado").strip().lower()

    if source == "ado":
        from cortex.repositories.ado.ado_provider import ADOWorkItemProvider

        return ADOWorkItemProvider(
            org_url=os.getenv("ADO_ORG_URL", ""),
            pat=os.getenv("ADO_PAT", ""),
            project=os.getenv("ADO_PROJECT", ""),
        )

    # -----------------------------------------------------------------------
    # EXTENSIBILITY POINT
    # Add new providers here following the same pattern:
    #
    # elif source == "jira":
    #     from cortex.repositories.jira.jira_provider import JiraWorkItemProvider
    #     return JiraWorkItemProvider(
    #         base_url=os.getenv("JIRA_BASE_URL", ""),
    #         token=os.getenv("JIRA_API_TOKEN", ""),
    #         project_key=os.getenv("JIRA_PROJECT_KEY", ""),
    #     )
    #
    # elif source == "servicenow":
    #     from cortex.repositories.servicenow.sn_provider import ServiceNowProvider
    #     return ServiceNowProvider(...)
    # -----------------------------------------------------------------------

    raise ValueError(
        f"Unknown WORK_ITEM_SOURCE: {source!r}. "
        f"Supported values: 'ado'. "
        f"To add a new provider, implement WorkItemProvider and register it in "
        f"cortex/repositories/provider_factory.py."
    )
