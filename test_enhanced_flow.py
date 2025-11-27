"""
Test script for Enhanced Flow implementation validation

Purpose: Verify Phase 2, Phase 4, and Phase 8 changes for post-setup onboarding
Author: Asif Hussain
Date: November 27, 2025
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_phase_2_consent_flag():
    """Test Phase 2: Verify onboarding_deferred flag added"""
    print("\n" + "="*80)
    print("TEST 1: Phase 2 Consent Update")
    print("="*80)
    
    try:
        from orchestrators.master_setup_orchestrator import MasterSetupOrchestrator
        
        # Create orchestrator
        orchestrator = MasterSetupOrchestrator(
            cortex_root=Path.cwd(),
            interactive=False
        )
        
        # Check if Phase 2 sets onboarding_deferred flag
        # This is a static check (need runtime test for full validation)
        print("✅ MasterSetupOrchestrator imports successfully")
        print("✅ Phase 2 implementation accessible")
        
        # Read source to verify flag exists
        source_file = Path(__file__).parent / "src" / "orchestrators" / "master_setup_orchestrator.py"
        source_code = source_file.read_text()
        
        if "'onboarding_deferred': True" in source_code:
            print("✅ Phase 2 has onboarding_deferred flag")
            return True
        else:
            print("❌ Phase 2 missing onboarding_deferred flag")
            return False
            
    except Exception as e:
        print(f"❌ Phase 2 test failed: {e}")
        return False


def test_phase_4_deferred():
    """Test Phase 4: Verify onboarding deferred to post-setup"""
    print("\n" + "="*80)
    print("TEST 2: Phase 4 Deferred")
    print("="*80)
    
    try:
        source_file = Path(__file__).parent / "src" / "orchestrators" / "master_setup_orchestrator.py"
        source_code = source_file.read_text()
        
        # Check for deferred implementation
        if "Phase 4: Onboarding deferred to post-setup" in source_code:
            print("✅ Phase 4 defers onboarding")
            
            # Verify it doesn't execute OnboardingOrchestrator in Phase 4
            phase_4_start = source_code.find("Phase 4: Onboarding deferred")
            phase_5_start = source_code.find("Phase 5: GitIgnore")
            
            if phase_4_start > 0 and phase_5_start > 0:
                phase_4_code = source_code[phase_4_start:phase_5_start]
                
                if "OnboardingOrchestrator(" not in phase_4_code:
                    print("✅ Phase 4 does NOT execute OnboardingOrchestrator")
                    return True
                else:
                    print("❌ Phase 4 still executes OnboardingOrchestrator")
                    return False
        else:
            print("❌ Phase 4 missing deferred implementation")
            return False
            
    except Exception as e:
        print(f"❌ Phase 4 test failed: {e}")
        return False


def test_phase_8_post_setup_prompt():
    """Test Phase 8: Verify post-setup onboarding prompt exists"""
    print("\n" + "="*80)
    print("TEST 3: Phase 8 Post-Setup Onboarding Prompt")
    print("="*80)
    
    try:
        source_file = Path(__file__).parent / "src" / "orchestrators" / "master_setup_orchestrator.py"
        source_code = source_file.read_text()
        
        # Check for Phase 8 implementation
        checks = {
            "Phase 8 header": "Phase 8: Post-Setup Onboarding Prompt" in source_code,
            "Interactive prompt": "Would you like to onboard your application now?" in source_code,
            "OnboardingOrchestrator call": "OnboardingOrchestrator(self.cortex_root)" in source_code,
            "User choice 'y'": "if onboard_now == 'y':" in source_code,
            "User choice 'n'": "else:" in source_code and "'user_choice': 'deferred'" in source_code,
            "Non-interactive handling": "'reason': 'non-interactive mode'" in source_code,
            "Error handling": "except Exception as e:" in source_code and "post_setup_onboarding" in source_code
        }
        
        passed = 0
        failed = 0
        
        for check_name, result in checks.items():
            if result:
                print(f"✅ {check_name}")
                passed += 1
            else:
                print(f"❌ {check_name}")
                failed += 1
        
        print(f"\nPhase 8 checks: {passed}/{len(checks)} passed")
        
        return failed == 0
        
    except Exception as e:
        print(f"❌ Phase 8 test failed: {e}")
        return False


def test_enhanced_flow_documentation():
    """Test: Verify documentation created"""
    print("\n" + "="*80)
    print("TEST 4: Enhanced Flow Documentation")
    print("="*80)
    
    try:
        doc_path = Path(__file__).parent / "cortex-brain" / "documents" / "implementation-guides" / "setup-enhanced-flow-guide.md"
        
        if doc_path.exists():
            print(f"✅ Documentation exists: {doc_path.name}")
            
            content = doc_path.read_text()
            
            # Check for key sections
            sections = [
                "## 🎯 Overview",
                "## 🔄 Workflow Comparison",
                "## 💬 User Experience",
                "## 🔧 Technical Implementation",
                "## 📊 Benefits",
                "## 🎯 User Scenarios"
            ]
            
            missing = []
            for section in sections:
                if section in content:
                    print(f"✅ {section}")
                else:
                    print(f"❌ {section}")
                    missing.append(section)
            
            if missing:
                print(f"\n⚠️  Missing {len(missing)} sections")
                return False
            else:
                print(f"\n✅ All {len(sections)} sections present")
                return True
        else:
            print(f"❌ Documentation not found: {doc_path}")
            return False
            
    except Exception as e:
        print(f"❌ Documentation test failed: {e}")
        return False


def main():
    """Run all Enhanced Flow validation tests"""
    print("\n" + "="*80)
    print("CORTEX ENHANCED FLOW - VALIDATION TESTS")
    print("="*80)
    print("\nPurpose: Verify Phase 2, Phase 4, Phase 8 implementation")
    print("File: src/orchestrators/master_setup_orchestrator.py")
    print("Documentation: cortex-brain/documents/implementation-guides/setup-enhanced-flow-guide.md")
    
    results = {
        "Phase 2: Consent Flag": test_phase_2_consent_flag(),
        "Phase 4: Deferred": test_phase_4_deferred(),
        "Phase 8: Post-Setup Prompt": test_phase_8_post_setup_prompt(),
        "Documentation": test_enhanced_flow_documentation()
    }
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{'='*80}")
    print(f"RESULTS: {passed}/{total} tests passed")
    print(f"{'='*80}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Enhanced Flow implementation complete!")
        print("\nNext steps:")
        print("1. Run 'setup cortex' to test interactive flow")
        print("2. Verify Phase 8 prompt appears after setup completes")
        print("3. Test both 'y' (onboard now) and 'n' (defer) choices")
        print("4. Verify 'onboard application' command works for deferred onboarding")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests failed - review implementation")
        return 1


if __name__ == "__main__":
    sys.exit(main())
