"""
DEPRECATED: Discovery plugins moved to cortex.lens.discovery

This directory has been deprecated as part of LENS consolidation (2026-02-02).

OLD LOCATION: cortex.brain.discovery.{plugin}
NEW LOCATION: cortex.lens.discovery.{plugin}

MIGRATION:
  OLD: from cortex.brain.discovery.config_discovery import ConfigurationDiscovery
  NEW: from cortex.lens.discovery import ConfigurationDiscovery

Moved plugins:
- config_discovery.py → cortex/lens/discovery/config_discovery.py
- database_discovery.py → cortex/lens/discovery/database_discovery.py

This notice will be removed in next sprint. Update your imports now.

Authority: CORE-035 (Consolidation)
"""
