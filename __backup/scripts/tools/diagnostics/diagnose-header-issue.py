#!/usr/bin/env python3
"""
Diagnose CORTEX brain icon and header injection issue.

This script investigates:
1. Whether the brain emoji can be rendered
2. Whether ResponseHeaderFooterManager initializes correctly
3. Whether wrap_cortex_response is being called in all code paths
4. Whether the header is being injected but stripped somewhere
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add CORTEX to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("CORTEX Brain Icon & Header Injection Diagnostic")
print("=" * 80)
print()

# TEST 1: Check brain emoji rendering
print("TEST 1: Brain Emoji Rendering")
print("-" * 80)
try:
    brain_emoji = "🧠"
    print(f"Brain emoji: {brain_emoji}")
    print(f"Emoji encoding: {brain_emoji.encode('utf-8')}")
    print(f"Emoji repr: {repr(brain_emoji)}")
    print(f"System stdout encoding: {sys.stdout.encoding}")
    
    # Try to render it
    test_string = f"## {brain_emoji} CORTEX Test"
    print(f"Test string: {test_string}")
    print("✅ Brain emoji renders correctly")
except Exception as e:
    print(f"❌ Brain emoji rendering failed: {e}")

print()

# TEST 2: Check ResponseHeaderFooterManager initialization
print("TEST 2: ResponseHeaderFooterManager Initialization")
print("-" * 80)
try:
    from src.infrastructure.response_header_footer_manager import (
        ResponseHeaderFooterManager,
        wrap_cortex_response,
        inject_cortex_header
    )
    
    manager = ResponseHeaderFooterManager()
    print(f"✅ Manager initialized successfully")
    print(f"  Config path: {manager.config_path}")
    print(f"  Timestamp: {manager.timestamp}")
    
    # Check header generation
    header_md = manager.generate_header("Test Operation", "6.0.0", "markdown")
    print(f"\nGenerated markdown header:")
    print(repr(header_md[:100]))
    
    if "🧠 CORTEX" in header_md:
        print("✅ Header contains brain icon and CORTEX")
    else:
        print("❌ Header is missing brain icon or CORTEX text")
    
except Exception as e:
    print(f"❌ Manager initialization failed: {e}")
    import traceback
    traceback.print_exc()

print()

# TEST 3: Check wrap_cortex_response function
print("TEST 3: wrap_cortex_response Function")
print("-" * 80)
try:
    test_content = "✅ Test Content\n\nThis is test content."
    wrapped = wrap_cortex_response(test_content, "Testing", "markdown")
    
    print(f"✅ wrap_cortex_response executed successfully")
    print(f"  Input length: {len(test_content)} chars")
    print(f"  Output length: {len(wrapped)} chars")
    
    if "🧠 CORTEX" in wrapped:
        print("✅ Wrapped response contains brain icon")
    else:
        print("❌ Wrapped response missing brain icon")
        
    print(f"\nFirst 150 chars of wrapped response:")
    print(repr(wrapped[:150]))
    
except Exception as e:
    print(f"❌ wrap_cortex_response failed: {e}")
    import traceback
    traceback.print_exc()

print()

# TEST 4: Check all call sites in main.py
print("TEST 4: Checking main.py for wrap_cortex_response usage")
print("-" * 80)
try:
    main_py = Path(__file__).parent / "src" / "main.py"
    if main_py.exists():
        with open(main_py) as f:
            content = f.read()
        
        # Count wrap_cortex_response calls
        wrap_count = content.count("wrap_cortex_response(")
        print(f"✅ Found {wrap_count} calls to wrap_cortex_response")
        
        # Check for direct print statements that might bypass wrapping
        lines = content.split('\n')
        suspicious_lines = []
        for i, line in enumerate(lines, 1):
            if 'print(' in line and 'wrapped_response' not in line and 'profile' not in line:
                # Exclude known non-problematic prints
                if not any(x in line for x in ['#', 'print(f"⚙️', 'print(f"\\n', 'print(`"CORTEX']):
                    suspicious_lines.append((i, line.strip()[:100]))
        
        if suspicious_lines:
            print(f"⚠️  Found {len(suspicious_lines)} potentially suspicious print statements:")
            for line_num, line_text in suspicious_lines[:5]:
                print(f"  Line {line_num}: {line_text}")
        else:
            print("✅ All print statements appear wrapped or benign")
            
    else:
        print(f"❌ main.py not found at {main_py}")
        
except Exception as e:
    print(f"❌ Failed to check main.py: {e}")

print()

# TEST 5: Check if GitHubCopilot prints are bypassing Python
print("TEST 5: Response Path Analysis")
print("-" * 80)
print("Analyzing response generation paths...")

try:
    # Check if responses go through MasterOrchestrator
    master_orch = Path(__file__).parent / "src" / "orchestrators" / "core" / "master_orchestrator.py"
    if master_orch.exists():
        with open(master_orch) as f:
            content = f.read()
        
        if "wrap_cortex_response" in content or "inject_cortex_header" in content:
            print("✅ MasterOrchestrator uses header injection")
        else:
            print("⚠️  MasterOrchestrator may not wrap responses")
            
except Exception as e:
    print(f"❌ Failed to check MasterOrchestrator: {e}")

print()
print("=" * 80)
print("Diagnostic Complete")
print("=" * 80)
print()
print("RECOMMENDATIONS:")
print("1. Ensure all response paths call wrap_cortex_response()")
print("2. Verify brain emoji can be encoded in current environment")
print("3. Check GitHubCopilot's response formatting pipeline")
print("4. Ensure header is not stripped during markdown rendering")
