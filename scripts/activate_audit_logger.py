#!/usr/bin/env python3
"""
Activate Audit Logger for Remediation Workflow

This script activates the enterprise audit logger with immediate integration
across all CORTEX orchestrators and establishes log review checkpoints.

Author: CORTEX Holistic Review Orchestrator
Date: 2026-01-05
"""

import sys
from pathlib import Path
from datetime import datetime
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

try:
    from src.logging.audit_logger import AuditLogger, LogLevel
except ImportError:
    # Fallback for alternative import structure
    from logging.audit_logger import AuditLogger, LogLevel


def activate_remediation_audit_logging():
    """
    Activate audit logging for remediation workflow
    
    Returns:
        AuditLogger: Configured logger instance
    """
    print("\n" + "="*60)
    print("🛡️ CORTEX Audit Logger Activation")
    print("="*60 + "\n")
    
    # Get logger instance
    print("📋 Step 1: Initializing audit logger...")
    logger = AuditLogger.get_instance()
    
    # Create log directory structure
    log_base = Path("logs/audit/remediation")
    session_dir = log_base / datetime.now().strftime("%Y-%m-%d") / f"session-{datetime.now().strftime('%H%M%S')}"
    session_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Log directory created: {session_dir}")
    
    # Configure for remediation context
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
            "planning",
            "ado",
            "vacuum",
            "cleanup",
            "investigation",
            "tdd",
            "debug",
            "refinement",
            "maintenance",
            "sanitization",
            "holistic_review"
        ],
        "thresholds": {
            "error_rate": 0.05,  # 5% max
            "performance_overhead": 5.0,  # 5ms max
            "recovery_success": 0.95,  # 95% min
            "buffer_warning": 0.8  # 80% buffer capacity
        }
    }
    
    print("\n📋 Step 2: Configuring audit logger...")
    logger.configure(config)
    print("✅ Configuration applied")
    
    # Log activation event
    print("\n📋 Step 3: Logging activation event...")
    activation_data = {
        "plan_id": "plan-369b7551-9c8b-43a6-9a32-efccbb68abaf",
        "activation_time": datetime.now().isoformat(),
        "config": config,
        "session_dir": str(session_dir),
        "activated_by": "scripts/activate_audit_logger.py"
    }
    
    logger.log(
        LogLevel.AUDIT,
        "Remediation audit logging activated",
        activation_data
    )
    print("✅ Activation event logged")
    
    # Flush to ensure logs written
    print("\n📋 Step 4: Flushing logs to disk...")
    logger.flush()
    print("✅ Logs flushed")
    
    # Verify log file created
    log_files = list(session_dir.glob("*.jsonl"))
    if log_files:
        print(f"\n✅ Log file created: {log_files[0].name}")
        print(f"   Size: {log_files[0].stat().st_size} bytes")
    else:
        print("\n⚠️  Warning: No log files found")
    
    # Save activation metadata
    metadata_file = session_dir / "activation-metadata.json"
    with open(metadata_file, "w") as f:
        json.dump(activation_data, f, indent=2)
    print(f"✅ Metadata saved: {metadata_file.name}")
    
    # Print summary
    print("\n" + "="*60)
    print("✅ AUDIT LOGGER ACTIVATED SUCCESSFULLY")
    print("="*60)
    print(f"\nSession Directory: {session_dir}")
    print(f"Orchestrators: {len(config['orchestrators'])}")
    print(f"Features Enabled: {len([k for k, v in config['features'].items() if v])}")
    print(f"Log Level: {config['log_level']}")
    print("\n" + "="*60 + "\n")
    
    return logger


def run_validation_tests(logger: AuditLogger):
    """
    Run validation tests to ensure logger is working
    
    Args:
        logger: Configured logger instance
    """
    print("\n" + "="*60)
    print("🧪 Running Validation Tests")
    print("="*60 + "\n")
    
    tests_passed = 0
    tests_total = 5
    
    # Test 1: Log entry creation
    print("Test 1: Log entry creation...")
    try:
        logger.log(LogLevel.INFO, "Validation test entry", {"test_id": 1})
        print("✅ PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 2: Different log levels
    print("\nTest 2: Different log levels...")
    try:
        logger.log(LogLevel.DEBUG, "Debug message", {"level": "debug"})
        logger.log(LogLevel.WARNING, "Warning message", {"level": "warning"})
        logger.log(LogLevel.ERROR, "Error message", {"level": "error"})
        print("✅ PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 3: Context data
    print("\nTest 3: Context data...")
    try:
        logger.log(LogLevel.AUDIT, "Context test", {
            "orchestrator": "test",
            "phase": 0,
            "operation": "validation"
        })
        print("✅ PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 4: Buffer operations
    print("\nTest 4: Buffer operations...")
    try:
        for i in range(10):
            logger.log(LogLevel.DEBUG, f"Buffer test {i}", {"index": i})
        logger.flush()
        print("✅ PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 5: Performance
    print("\nTest 5: Performance (<5ms overhead)...")
    try:
        import time
        iterations = 100
        start = time.time()
        for i in range(iterations):
            logger.log(LogLevel.DEBUG, "Performance test", {"iteration": i})
        duration = (time.time() - start) * 1000  # ms
        avg_duration = duration / iterations
        
        if avg_duration < 5.0:
            print(f"✅ PASSED (avg: {avg_duration:.2f}ms)")
            tests_passed += 1
        else:
            print(f"❌ FAILED (avg: {avg_duration:.2f}ms > 5ms)")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Summary
    print("\n" + "="*60)
    print(f"Validation Results: {tests_passed}/{tests_total} tests passed")
    print("="*60 + "\n")
    
    return tests_passed == tests_total


def main():
    """Main activation function"""
    try:
        # Activate logger
        logger = activate_remediation_audit_logging()
        
        # Run validation tests
        validation_passed = run_validation_tests(logger)
        
        if validation_passed:
            print("✅ All validation tests passed!")
            print("\n📋 Next Steps:")
            print("   1. Review logs in output directory")
            print("   2. Integrate logger into orchestrators")
            print("   3. Run phase checkpoint reviews")
            print("   4. Monitor performance and errors")
            return 0
        else:
            print("⚠️  Some validation tests failed - review output above")
            return 1
            
    except Exception as e:
        print(f"\n❌ ERROR: Activation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
