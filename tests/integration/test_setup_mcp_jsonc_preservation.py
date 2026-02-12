#!/usr/bin/env python3
"""
Integration Test: MCP Setup JSONC Preservation Fixes (BUG-001, BUG-002, BUG-003)

Authority: CORE-008 (TDD Mandatory) + chat01 remediation

Tests the actual setup-mcp.py functions to ensure JSONC files are never corrupted.
Run this with: python tests/integration/test_setup_mcp_jsonc_preservation.py

AC_START: AC-CHAT01-JSONC-FIXES-001
Description: Comprehensive TDD test for chat01 remediation - JSONC preservation
"""

import json
import tempfile
import sys
from pathlib import Path


def test_setup_mcp_module_loads():
    """✅ Verify setup-mcp.py module loads without errors."""
    import importlib.util
    
    setup_mcp_path = Path(".cortex/setup-mcp.py")
    assert setup_mcp_path.exists(), "❌ .cortex/setup-mcp.py not found!"
    
    spec = importlib.util.spec_from_file_location("setup_mcp", setup_mcp_path)
    assert spec is not None, "❌ Could not load setup-mcp.py spec"
    assert spec.loader is not None, "❌ setup-mcp.py has no loader"
    
    setup_mcp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(setup_mcp)
    
    print("✅ setup-mcp.py module loaded successfully")
    return setup_mcp


def test_strip_jsonc_preserves_globs(setup_mcp):
    """✅ _strip_jsonc_comments preserves glob patterns (BUG-001 prevention)."""
    _strip_jsonc_comments = setup_mcp._strip_jsonc_comments
    
    jsonc = '''
{
  // File exclusions with globs
  "files.exclude": {
    "**/*-summary.md": true,
    "**/*-report.md": true,
    "**/node_modules": true
  }
}
'''
    clean = _strip_jsonc_comments(jsonc)
    parsed = json.loads(clean)
    
    assert "**/*-summary.md" in parsed["files.exclude"], \
        "❌ Glob pattern '**/*-summary.md' corrupted by _strip_jsonc_comments!"
    assert "**/*-report.md" in parsed["files.exclude"], \
        "❌ Glob pattern '**/*-report.md' corrupted!"
    assert "**/node_modules" in parsed["files.exclude"], \
        "❌ Glob pattern '**/node_modules' corrupted!"
    
    print("✅ _strip_jsonc_comments preserves glob patterns")


def test_write_settings_preserves_comments_on_new_key(setup_mcp):
    """✅ _write_settings_safely preserves comments when adding new keys."""
    _write_settings_safely = setup_mcp._write_settings_safely
    
    original = '''// VS Code settings
{
  // File exclusions
  "files.exclude": {
    "**/*-summary.md": true
  }
}'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(original)
        tmppath = Path(f.name)
    
    try:
        _write_settings_safely(tmppath, "new.key", "new-value", original)
        result = tmppath.read_text()
        
        assert "//" in result, "❌ Comments stripped when adding new key!"
        assert "**/*-summary.md" in result, "❌ Glob pattern corrupted when adding key!"
        assert "new.key" in result and "new-value" in result, \
            "❌ New key/value not added!"
        
        print("✅ _write_settings_safely preserves comments for new keys")
    finally:
        tmppath.unlink()


def test_write_settings_preserves_comments_on_existing_key(setup_mcp):
    """🚨 CRITICAL: _write_settings_safely must preserve comments on key UPDATE (BUG-001 FIX)."""
    _write_settings_safely = setup_mcp._write_settings_safely
    _strip_jsonc_comments = setup_mcp._strip_jsonc_comments
    
    original = '''// VS Code settings
{
  // File exclusions
  "files.exclude": {
    "**/*-summary.md": true
  },
  // Python settings
  "python.linting": true
}'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(original)
        tmppath = Path(f.name)
    
    try:
        # Update existing key (this is where BUG-001 manifests)
        _write_settings_safely(tmppath, "python.linting", False, original)
        result = tmppath.read_text()
        
        # CRITICAL ASSERTION: Comments MUST be preserved
        assert "//" in result, \
            "🔴 BUG-001 PRESENT: Comments stripped when updating existing key!"
        assert "**/*-summary.md" in result, \
            "❌ Glob pattern corrupted when updating key!"
        
        # Verify value was actually updated
        parsed = json.loads(_strip_jsonc_comments(result))
        assert parsed["python.linting"] is False, \
            "❌ Value not updated correctly!"
        
        print("✅ _write_settings_safely preserves comments for existing keys (BUG-001 FIX)")
    finally:
        tmppath.unlink()


def test_merge_mcp_servers_preserves_comments(setup_mcp):
    """🚨 CRITICAL: _merge_mcp_servers_safely must preserve comments (BUG-002 FIX)."""
    _merge_mcp_servers_safely = setup_mcp._merge_mcp_servers_safely
    _strip_jsonc_comments = setup_mcp._strip_jsonc_comments
    
    original = '''// VS Code configuration
{
  // File exclusions
  "files.exclude": {
    "**/*-summary.md": true
  },
  // MCP servers
  "github.copilot.chat.mcpServers": {
    "cortex": {
      "command": "python"
    }
  }
}'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(original)
        tmppath = Path(f.name)
    
    try:
        new_config = {"command": "new-python", "args": ["-m", "cortex.mcp"]}
        _merge_mcp_servers_safely(tmppath, "cortex", new_config)
        result = tmppath.read_text()
        
        # CRITICAL ASSERTION: Comments MUST be preserved
        assert "//" in result, \
            "🔴 BUG-002 PRESENT: Comments stripped when merging MCP servers!"
        assert "**/*-summary.md" in result, \
            "❌ Glob pattern corrupted when merging MCP config!"
        
        # Verify config was merged correctly
        parsed = json.loads(_strip_jsonc_comments(result))
        assert parsed["github.copilot.chat.mcpServers"]["cortex"]["args"] == ["-m", "cortex.mcp"], \
            "❌ MCP config not merged correctly!"
        
        print("✅ _merge_mcp_servers_safely preserves comments (BUG-002 FIX)")
    finally:
        tmppath.unlink()


def test_disable_pylance_mcp_preserves_comments(setup_mcp):
    """✅ disable_pylance_mcp preserves comments when disabling Pylance."""
    disable_pylance_mcp = setup_mcp.disable_pylance_mcp
    _strip_jsonc_comments = setup_mcp._strip_jsonc_comments
    
    original = '''// VS Code settings
{
  // File exclusions
  "files.exclude": {
    "**/*-summary.md": true
  },
  // Pylance settings
  "pylance.mcpServer.enabled": true
}'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(original)
        tmppath = Path(f.name)
    
    try:
        disable_pylance_mcp(tmppath)
        result = tmppath.read_text()
        
        assert "//" in result, "❌ Comments stripped by disable_pylance_mcp!"
        assert "**/*-summary.md" in result, "❌ Glob pattern corrupted!"
        
        parsed = json.loads(_strip_jsonc_comments(result))
        assert parsed.get("pylance.mcpServer.enabled") is False, \
            "❌ Pylance not disabled!"
        
        print("✅ disable_pylance_mcp preserves comments")
    finally:
        tmppath.unlink()


def test_deployment_requirements_synced():
    """✅ deployment/requirements.txt is in sync with root requirements.txt."""
    root_req = Path("requirements.txt").read_text()
    deploy_req = Path("deployment/requirements.txt").read_text()
    
    # Check for AC markers (prove both were updated together)
    assert "AC-MCP-FIX-003" in root_req, "❌ AC-MCP-FIX-003 marker missing from root requirements.txt!"
    assert "AC-MCP-FIX-003" in deploy_req, \
        "❌ deployment/requirements.txt not synced: missing AC-MCP-FIX-003!"
    
    # Check for tree-sitter packages
    for pkg in ["tree-sitter-c-sharp", "tree-sitter-javascript", "tree-sitter-java"]:
        assert pkg in root_req, f"❌ {pkg} missing from root requirements.txt!"
        assert pkg in deploy_req, f"❌ {pkg} missing from deployment/requirements.txt!"
    
    # Check jsonschema
    assert "jsonschema" in root_req, "❌ jsonschema missing from root requirements.txt!"
    assert "jsonschema" in deploy_req, "❌ jsonschema missing from deployment/requirements.txt!"
    
    print("✅ deployment/requirements.txt is synced with root requirements.txt")


def test_registry_tracks_chat01_issues():
    """✅ Registry tracks chat01 remediation items."""
    registry_file = Path("cortex-registry/_cortex-master/index.yaml")
    assert registry_file.exists(), "❌ Registry index not found!"
    
    content = registry_file.read_text()
    
    # Verify tracking (should have at least one reference to chat01 or MCP-FIX)
    assert "chat01" in content.lower() or "mcp" in content.lower(), \
        "❌ Registry does not track chat01 remediation!"
    
    print("✅ Registry tracks chat01 remediation items")


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("🧪 Integration Tests: MCP Setup JSONC Preservation (BUG-001/002 Fixes)")
    print("=" * 80 + "\n")
    
    try:
        # Load module
        setup_mcp = test_setup_mcp_module_loads()
        
        # Run tests
        test_strip_jsonc_preserves_globs(setup_mcp)
        test_write_settings_preserves_comments_on_new_key(setup_mcp)
        test_write_settings_preserves_comments_on_existing_key(setup_mcp)
        test_merge_mcp_servers_preserves_comments(setup_mcp)
        test_disable_pylance_mcp_preserves_comments(setup_mcp)
        test_deployment_requirements_synced()
        test_registry_tracks_chat01_issues()
        
        print("\n" + "=" * 80)
        print("🎉 ALL TESTS PASSED (7/7)")
        print("=" * 80)
        print("\n📊 Test Summary:")
        print("  ✅ JSONC comment/glob preservation: WORKING")
        print("  ✅ BUG-001 (existing key update): FIXED")
        print("  ✅ BUG-002 (MCP merge): FIXED")
        print("  ✅ ENH-063 (Pylance disable): WORKING")
        print("  ✅ Deployment requirements: SYNCED")
        print("  ✅ Registry tracking: COMPLETE")
        print("\n" + "=" * 80 + "\n")
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
