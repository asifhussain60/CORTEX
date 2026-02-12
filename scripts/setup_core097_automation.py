#!/usr/bin/env python3
"""
CORE-097 Cron Setup Script
AC_START: AC-WAVE-9-ENH-096-S5-002

Sets up weekly duplicate detection via cron/Task Scheduler.

Author: Asif Hussain
Date: 2026-02-12
"""

import os
import platform
import subprocess
import sys
from pathlib import Path

def setup_cron_unix():
    """Setup cron job on macOS/Linux"""
    cortex_root = Path(__file__).parent.parent.parent.parent
    venv_python = cortex_root / ".venv" / "bin" / "python"
    
    if not venv_python.exists():
        print("❌ Virtual environment not found at .venv/")
        print("   Run: python -m venv .venv && source .venv/bin/activate")
        return False
    
    cron_command = f"0 2 * * 0 cd {cortex_root} && {venv_python} -m cortex.orchestrators.support.duplication_detector_orchestrator --scheduled"
    
    print("🔧 Setting up cron job for CORE-097 duplicate detection...")
    print(f"   Schedule: Every Sunday at 2:00 AM")
    print(f"   Command: {cron_command}")
    print()
    
    # Check if cron job already exists
    try:
        current_cron = subprocess.run(
            ["crontab", "-l"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if "duplication_detector_orchestrator" in current_cron.stdout:
            print("⚠️  Cron job already exists")
            return True
        
        # Add new cron job
        new_cron = current_cron.stdout + f"\n{cron_command}\n"
        subprocess.run(
            ["crontab", "-"],
            input=new_cron,
            text=True,
            check=True
        )
        
        print("✅ Cron job added successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to setup cron: {e}")
        return False

def setup_task_scheduler_windows():
    """Setup Windows Task Scheduler job"""
    cortex_root = Path(__file__).parent.parent.parent.parent
    venv_python = cortex_root / ".venv" / "Scripts" / "python.exe"
    
    if not venv_python.exists():
        print("❌ Virtual environment not found at .venv\\Scripts\\")
        print("   Run: python -m venv .venv && .venv\\Scripts\\activate")
        return False
    
    task_name = "CORTEX_CORE097_DuplicateDetection"
    script_path = cortex_root / "cortex" / "orchestrators" / "support" / "duplication_detector_orchestrator.py"
    
    print("🔧 Setting up Windows Task Scheduler for CORE-097...")
    print(f"   Task: {task_name}")
    print(f"   Schedule: Every Sunday at 2:00 AM")
    print()
    
    # Create task via schtasks command
    try:
        cmd = [
            "schtasks", "/Create",
            "/TN", task_name,
            "/TR", f'"{venv_python}" -m cortex.orchestrators.support.duplication_detector_orchestrator --scheduled',
            "/SC", "WEEKLY",
            "/D", "SUN",
            "/ST", "02:00",
            "/F"  # Force overwrite if exists
        ]
        
        subprocess.run(cmd, check=True, cwd=str(cortex_root))
        print("✅ Task Scheduler job created successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to setup Task Scheduler: {e}")
        print("   Note: May require administrator privileges")
        return False

def main():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("CORE-097: Automated Duplicate Detection Setup")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    
    system = platform.system()
    
    if system in ["Darwin", "Linux"]:
        success = setup_cron_unix()
    elif system == "Windows":
        success = setup_task_scheduler_windows()
    else:
        print(f"❌ Unsupported platform: {system}")
        success = False
    
    print()
    if success:
        print("✅ CORE-097 automation setup complete")
        print("   Weekly duplicate detection will run every Sunday at 2:00 AM")
        print()
        print("Manual run: python -m cortex.orchestrators.support.duplication_detector_orchestrator")
    else:
        print("❌ Setup failed - see errors above")
        sys.exit(1)

if __name__ == "__main__":
    main()

# AC_COMPLETE: AC-WAVE-9-ENH-096-S5-002 ✅
