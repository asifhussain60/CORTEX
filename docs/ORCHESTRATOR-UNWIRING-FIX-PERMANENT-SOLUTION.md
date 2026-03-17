# Orchestrator Unwiring Permanent Solution

AC-PERMANENT-FIX-001 restored the registry persistence contract after registry regeneration was found to wipe active orchestrator wiring.

The permanent safeguard is `registry_template: false` in the persisted repo registry so automated refresh paths cannot replace the wired registry with a blank template.

This document exists as the durable explanation for the unwiring fix and the verification checks that enforce it.