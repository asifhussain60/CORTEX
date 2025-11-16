# src.plugins.configuration_wizard_plugin

Configuration Wizard Plugin

Author: Syed Asif Hussain
Copyright: © 2024-2025 Syed Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms

Provides post-setup incremental configuration with auto-discovery.

Features:
- Auto-discover Oracle/SQL Server/PostgreSQL connections
- Scan code for REST API endpoints
- Validate connections before saving
- Interactive guided configuration
- Non-blocking - runs AFTER basic setup

Usage:
    # Interactive wizard (all features)
    cortex config:wizard
    
    # Add single database
    cortex config:add-database --interactive
    
    # Add single API
    cortex config:add-api --interactive
    
    # Auto-discover only (no prompts)
    cortex config:discover --auto
