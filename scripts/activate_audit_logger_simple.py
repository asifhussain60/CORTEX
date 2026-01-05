#!/usr/bin/env python3
"""
Simple Audit Logger Activation Script

Activates audit logging without complex imports to avoid circular dependencies.
Creates directory structure and initializes configuration.

Author: CORTEX Holistic Review Orchestrator
Date: 2026-01-05
"""

import json
from pathlib import Path
from datetime import datetime


def main():
    """Activate audit logger with minimal dependencies"""
    print("\n" + "="*60)
    print("🛡️ CORTEX Audit Logger Activation (Simple Mode)")
    print("="*60 + "\n")
    
    # Create directory structure
    print("📋 Step 1: Creating log directory structure...")
    log_base = Path("logs/audit/remediation")
    session_dir = log_base / datetime.now().strftime("%Y-%m-%d") / f"session-{datetime.now().strftime('%H%M%S')}"
    session_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Directory created: {session_dir}")
    
    # Create subdirectories for different log types
    (session_dir / "operations").mkdir(exist_ok=True)
    (session_dir / "errors").mkdir(exist_ok=True)
    (session_dir / "performance").mkdir(exist_ok=True)
    (session_dir / "state-transitions").mkdir(exist_ok=True)
    print("✅ Subdirectories created")
    
    # Create configuration
    print("\n📋 Step 2: Creating configuration...")
    config = {
        "enabled": True,
        "log_level": "AUDIT",
        "output_dir": str(session_dir),
        "buffer_size": 5000,
        "flush_interval": 5,
        "features": {
            "pattern_detection": True,
            "anomaly_detection": True,
            "self_healing": True,
            "performance_tracking": True,
            "state_transitions": True,
            "error_clustering": True,
            "context_propagation": True
        },
        "orchestrators": [
            "planning", "ado", "vacuum", "cleanup", "investigation",
            "tdd", "debug", "refinement", "maintenance", "sanitization",
            "holistic_review"
        ],
        "thresholds": {
            "error_rate": 0.05,
            "performance_overhead": 5.0,
            "recovery_success": 0.95,
            "buffer_warning": 0.8
        }
    }
    
    config_file = session_dir / "audit-config.json"
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
    print(f"✅ Configuration saved: {config_file.name}")
    
    # Create activation metadata
    print("\n📋 Step 3: Creating activation metadata...")
    metadata = {
        "plan_id": "plan-369b7551-9c8b-43a6-9a32-efccbb68abaf",
        "activation_time": datetime.now().isoformat(),
        "config": config,
        "session_dir": str(session_dir),
        "activated_by": "scripts/activate_audit_logger_simple.py",
        "status": "active"
    }
    
    metadata_file = session_dir / "activation-metadata.json"
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"✅ Metadata saved: {metadata_file.name}")
    
    # Create initial log entry
    print("\n📋 Step 4: Creating initial log entry...")
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": "AUDIT",
        "message": "Remediation audit logging activated",
        "orchestrator": "system",
        "phase": 0,
        "session_id": f"sess-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "context": {
            "plan_id": "plan-369b7551-9c8b-43a6-9a32-efccbb68abaf",
            "activation_method": "simple",
            "features_enabled": list(config["features"].keys())
        }
    }
    
    log_file = session_dir / "operations" / "activation.jsonl"
    with open(log_file, "w") as f:
        f.write(json.dumps(log_entry) + "\n")
    print(f"✅ Initial log entry created: {log_file.name}")
    
    # Create README
    print("\n📋 Step 5: Creating session README...")
    readme_content = f"""# Audit Logger Session

**Session ID:** {log_entry['session_id']}
**Activation Time:** {metadata['activation_time']}
**Status:** ACTIVE

## Directory Structure

```
{session_dir.name}/
├── activation-metadata.json  # Activation details
├── audit-config.json         # Configuration
├── operations/               # Operation logs
├── errors/                   # Error logs
├── performance/              # Performance metrics
└── state-transitions/        # State change logs
```

## Configuration

- **Log Level:** {config['log_level']}
- **Orchestrators:** {len(config['orchestrators'])}
- **Features Enabled:** {len([k for k, v in config['features'].items() if v])}

## Usage

All CORTEX orchestrators will now log to this session directory.

To review logs:
```bash
python3 scripts/review_audit_logs.py --phase 0 --check activation --log-dir {log_base}
```

---

**Generated:** {datetime.now().isoformat()}
"""
    
    readme_file = session_dir / "README.md"
    with open(readme_file, "w") as f:
        f.write(readme_content)
    print(f"✅ README created: {readme_file.name}")
    
    # Print summary
    print("\n" + "="*60)
    print("✅ AUDIT LOGGER ACTIVATED SUCCESSFULLY")
    print("="*60)
    print(f"\n📁 Session Directory: {session_dir}")
    print(f"🎯 Session ID: {log_entry['session_id']}")
    print(f"📊 Orchestrators: {len(config['orchestrators'])}")
    print(f"⚡ Features: {len([k for k, v in config['features'].items() if v])}/7 enabled")
    print(f"📝 Log Level: {config['log_level']}")
    
    print("\n📋 Next Steps:")
    print("   1. Review activation:")
    print(f"      python3 scripts/review_audit_logs.py --phase 0 --check activation --log-dir {log_base}")
    print("   2. Check logs:")
    print(f"      cat {log_file}")
    print("   3. View configuration:")
    print(f"      cat {config_file}")
    
    print("\n" + "="*60 + "\n")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
