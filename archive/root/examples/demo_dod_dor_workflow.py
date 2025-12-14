"""
CORTEX Demo: DoD/DoR Workflow Integration
=========================================

Demonstrates how CORTEX processes user-provided Definition of Done (DoD),
Definition of Ready (DoR), and Acceptance Criteria through the Work Planner agent.

This demo showcases:
1. DoR Validation (Rule #21) - RIGHT BRAIN Strategic Planning
2. Planning Enhancement - Structuring implementation from AC
3. Test Generation - Converting AC to test cases
4. DoD Enforcement - Quality gates during execution

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import Dict, Any
from datetime import datetime


class DoDDoRWorkflowDemo:
    """
    Interactive demonstration of CORTEX's DoD/DoR workflow integration.
    
    Shows how Work Planner agent processes user-provided quality criteria
    and integrates them into the multi-agent development workflow.
    """
    
    def __init__(self):
        """Initialize demo."""
        self.demo_start_time = None
        self.steps_completed = []
    
    def run_demo(self) -> None:
        """Execute the complete DoD/DoR workflow demonstration."""
        print("\n" + "=" * 80)
        print("🧠 CORTEX Demo: DoD/DoR Workflow Integration")
        print("=" * 80)
        print("\nAuthor: Asif Hussain | © 2024-2025")
        print("\n📋 This demo showcases how CORTEX integrates user-provided quality")
        print("   criteria into its multi-agent workflow for intelligent development.\n")
        
        self.demo_start_time = datetime.now()
        
        # Demo Steps
        self._step_1_user_provides_criteria()
        self._step_2_dor_validation()
        self._step_3_work_planner_analysis()
        self._step_4_phase_generation()
        self._step_5_test_generation()
        self._step_6_dod_enforcement()
        self._step_7_summary()
    
    def _step_1_user_provides_criteria(self) -> None:
        """Step 1: Show user providing DoD, DoR, and AC with their request."""
        print("\n" + "─" * 80)
        print("📝 STEP 1: User Provides Quality Criteria")
        print("─" * 80)
        
        print("\n💬 User Request:")
        print('   "Add invoice PDF export feature"')
        
        print("\n📋 User-Provided Definition of Ready (DoR):")
        print("   ✓ User Story: 'As an admin, I want to export invoices as PDF'")
        print("   ✓ Acceptance Criteria:")
        print("      • AC1: User clicks export → PDF generates with company logo")
        print("      • AC2: Export handles invalid invoice ID gracefully")
        print("      • AC3: Bulk export supports up to 100 invoices")
        print("   ✓ Dependencies: iTextSharp PDF library installed")
        print("   ✓ Estimate: 6 hours total")
        
        print("\n✅ User-Provided Definition of Done (DoD):")
        print("   ✓ All 3 acceptance criteria tests pass")
        print("   ✓ Code coverage ≥85%")
        print("   ✓ PDF validates against PDF/A standard")
        print("   ✓ Documentation updated")
        
        self._pause_for_demo()
        self.steps_completed.append("criteria_provided")
    
    def _step_2_dor_validation(self) -> None:
        """Step 2: Show DoR validation by Work Planner."""
        print("\n" + "─" * 80)
        print("🧠 STEP 2: RIGHT BRAIN - Work Planner DoR Validation (Rule #21)")
        print("─" * 80)
        
        print("\n🔍 Work Planner Agent Analyzing DoR...")
        print("\n   Validation Checklist:")
        print("   [✓] User story clear and complete")
        print("   [✓] Acceptance criteria defined (3 scenarios)")
        print("   [✓] Testable outcomes specified")
        print("   [✓] Dependencies identified (iTextSharp)")
        print("   [✓] Estimate provided (6 hours)")
        print("   [✓] Scope bounded to single feature")
        
        print("\n✅ DoR Status: COMPLETE")
        print("\n💡 Work Planner Decision:")
        print("   • User provided comprehensive DoR")
        print("   • Skipping interactive DoR wizard")
        print("   • Creating work package from user criteria")
        print("   • Ready for implementation planning")
        
        self._pause_for_demo()
        self.steps_completed.append("dor_validated")
    
    def _step_3_work_planner_analysis(self) -> None:
        """Step 3: Show how Work Planner analyzes AC for planning."""
        print("\n" + "─" * 80)
        print("🎯 STEP 3: Work Planner Analyzes Acceptance Criteria")
        print("─" * 80)
        
        print("\n📊 Mapping AC to Implementation Phases...")
        
        print("\n   AC1: 'User clicks export → PDF generates with logo'")
        print("   └─→ Phase 1: Core PDF Generation Service (2 hours)")
        print("       • Create PDF generation service")
        print("       • Implement company logo embedding")
        print("       • Add invoice data formatting")
        
        print("\n   AC2: 'Export handles invalid invoice ID gracefully'")
        print("   └─→ Phase 2: Error Handling & Validation (2 hours)")
        print("       • Validate invoice ID before processing")
        print("       • Implement error response handling")
        print("       • Add user-friendly error messages")
        
        print("\n   AC3: 'Bulk export supports up to 100 invoices'")
        print("   └─→ Phase 3: Bulk Export Implementation (2 hours)")
        print("       • Create batch processing logic")
        print("       • Add progress tracking")
        print("       • Implement ZIP file packaging")
        
        print("\n✅ Planning Enhancement Complete:")
        print("   • 3 phases generated from 3 acceptance criteria")
        print("   • Each phase scoped to ~2 hours")
        print("   • Dependencies mapped: iTextSharp in Phase 1")
        print("   • Total estimate aligns with user's 6-hour estimate")
        
        self._pause_for_demo()
        self.steps_completed.append("planning_complete")
    
    def _step_4_phase_generation(self) -> None:
        """Step 4: Show structured phase breakdown."""
        print("\n" + "─" * 80)
        print("📦 STEP 4: Work Package Generated")
        print("─" * 80)
        
        print("\n🎯 Implementation Roadmap:")
        print("\n   ☐ Phase 1: Core PDF Generation (2h)")
        print("      • Task 1.1: Install iTextSharp library")
        print("      • Task 1.2: Create IPdfGenerationService interface")
        print("      • Task 1.3: Implement PdfGenerator class")
        print("      • Task 1.4: Add company logo embedding")
        print("      • DoD Check: AC1 test passes")
        
        print("\n   ☐ Phase 2: Error Handling (2h)")
        print("      • Task 2.1: Add invoice ID validation")
        print("      • Task 2.2: Create error handling middleware")
        print("      • Task 2.3: Implement error response models")
        print("      • DoD Check: AC2 test passes")
        
        print("\n   ☐ Phase 3: Bulk Export (2h)")
        print("      • Task 3.1: Create batch processor")
        print("      • Task 3.2: Add progress tracking")
        print("      • Task 3.3: Implement ZIP packaging")
        print("      • DoD Check: AC3 test passes")
        
        print("\n✅ Work Package Ready for LEFT BRAIN Execution")
        
        self._pause_for_demo()
        self.steps_completed.append("package_generated")
    
    def _step_5_test_generation(self) -> None:
        """Step 5: Show how AC converts to test cases."""
        print("\n" + "─" * 80)
        print("🧪 STEP 5: Test Generation from Acceptance Criteria")
        print("─" * 80)
        
        print("\n💡 LEFT BRAIN - Code Executor Agent")
        print("   Converting AC scenarios to test methods (TDD RED phase)...")
        
        print("\n   AC1 → Test Method:")
        print("   ```csharp")
        print("   [Fact]")
        print("   public async Task ExportInvoice_WithValidId_GeneratesPdfWithLogo()")
        print("   {")
        print("       // Arrange")
        print("       var invoiceId = 12345;")
        print("       ")
        print("       // Act")
        print("       var result = await _pdfService.GeneratePdf(invoiceId);")
        print("       ")
        print("       // Assert")
        print("       Assert.True(result.Success);")
        print("       Assert.EndsWith(\".pdf\", result.FilePath);")
        print("       Assert.True(result.ContainsLogo);")
        print("   }")
        print("   ```")
        
        print("\n   AC2 → Test Method:")
        print("   ```csharp")
        print("   [Fact]")
        print("   public async Task ExportInvoice_WithInvalidId_ReturnsError()")
        print("   {")
        print("       // Arrange")
        print("       var invalidId = -1;")
        print("       ")
        print("       // Act")
        print("       var result = await _pdfService.GeneratePdf(invalidId);")
        print("       ")
        print("       // Assert")
        print("       Assert.False(result.Success);")
        print("       Assert.Equal(\"Invalid invoice ID\", result.ErrorMessage);")
        print("   }")
        print("   ```")
        
        print("\n   AC3 → Test Method:")
        print("   ```csharp")
        print("   [Fact]")
        print("   public async Task BulkExport_UpTo100Invoices_GeneratesZip()")
        print("   {")
        print("       // Arrange")
        print("       var invoiceIds = Enumerable.Range(1, 100).ToList();")
        print("       ")
        print("       // Act")
        print("       var result = await _bulkExportService.ExportBulk(invoiceIds);")
        print("       ")
        print("       // Assert")
        print("       Assert.True(result.Success);")
        print("       Assert.Equal(100, result.ProcessedCount);")
        print("       Assert.EndsWith(\".zip\", result.FilePath);")
        print("   }")
        print("   ```")
        
        print("\n✅ Test Generation Complete:")
        print("   • 3 failing tests created (RED phase)")
        print("   • Each test maps directly to user's AC")
        print("   • Ready for GREEN phase implementation")
        
        self._pause_for_demo()
        self.steps_completed.append("tests_generated")
    
    def _step_6_dod_enforcement(self) -> None:
        """Step 6: Show DoD enforcement during development."""
        print("\n" + "─" * 80)
        print("✅ STEP 6: Definition of Done Enforcement (Rule #20)")
        print("─" * 80)
        
        print("\n🏥 LEFT BRAIN - Health Validator Agent")
        print("   Enforcing user's DoD criteria at pre-commit...")
        
        print("\n   Pre-Commit Validation Gates:")
        print("   [✓] All 3 acceptance criteria tests pass")
        print("       • AC1 test: ExportInvoice_WithValidId_GeneratesPdfWithLogo ✓")
        print("       • AC2 test: ExportInvoice_WithInvalidId_ReturnsError ✓")
        print("       • AC3 test: BulkExport_UpTo100Invoices_GeneratesZip ✓")
        
        print("\n   [✓] Code coverage ≥85% (User's requirement)")
        print("       • Current coverage: 87.3%")
        print("       • Exceeds user's 85% threshold ✓")
        
        print("\n   [✓] PDF validates against PDF/A standard")
        print("       • PDF/A validation: PASS")
        print("       • Standard compliance: PDF/A-1b ✓")
        
        print("\n   [✓] Documentation updated")
        print("       • API documentation: Updated ✓")
        print("       • README: Usage examples added ✓")
        
        print("\n✅ DoD Status: ALL CRITERIA MET")
        print("\n💚 Commit Allowed - Quality Gates Passed")
        print("   • User's specific DoD criteria enforced")
        print("   • No generic defaults used")
        print("   • Ready for code review and merge")
        
        self._pause_for_demo()
        self.steps_completed.append("dod_enforced")
    
    def _step_7_summary(self) -> None:
        """Step 7: Demo summary and benefits."""
        print("\n" + "─" * 80)
        print("🎉 STEP 7: Demo Summary")
        print("─" * 80)
        
        duration = (datetime.now() - self.demo_start_time).total_seconds()
        
        print("\n✅ Demonstration Complete!")
        print(f"   Duration: {duration:.1f} seconds")
        print(f"   Steps Completed: {len(self.steps_completed)}/7")
        
        print("\n🎯 Key Takeaways:")
        print("\n   1️⃣  RIGHT BRAIN validates user's DoR (Rule #21)")
        print("      • Skips interactive wizard when DoR complete")
        print("      • Creates work package from user criteria")
        
        print("\n   2️⃣  Work Planner structures implementation from AC")
        print("      • Maps each AC scenario to implementation phase")
        print("      • Breaks work into manageable tasks")
        print("      • Estimates effort automatically")
        
        print("\n   3️⃣  Code Executor converts AC to test cases")
        print("      • Each AC becomes a failing test (RED)")
        print("      • TDD workflow: RED → GREEN → REFACTOR")
        print("      • Ensures requirements are testable")
        
        print("\n   4️⃣  Health Validator enforces user's DoD (Rule #20)")
        print("      • User's criteria become quality gates")
        print("      • Blocks commits if DoD not met")
        print("      • Reports against YOUR specific requirements")
        
        print("\n💡 Benefits of Providing DoD/DoR/AC:")
        print("   ✓ Faster execution (no clarification needed)")
        print("   ✓ Your quality standards enforced consistently")
        print("   ✓ CORTEX learns your patterns over time")
        print("   ✓ Clear traceability through workflow")
        print("   ✓ Team alignment on quality gates")
        
        print("\n📚 Next Steps:")
        print("   1. Try providing DoD/DoR/AC with your next feature request")
        print("   2. Review src/tier0/governance.yaml for Rule #20 & #21")
        print("   3. Check src/workflows/stages/dod_dor_clarifier.py implementation")
        print("   4. Explore cortex-brain/protection-layers/ for enforcement rules")
        
        print("\n" + "=" * 80)
        print("Thank you for exploring CORTEX DoD/DoR Workflow Integration!")
        print("=" * 80 + "\n")
    
    def _pause_for_demo(self, delay: float = 2.0) -> None:
        """Pause briefly for demo effect."""
        import time
        time.sleep(delay)


def main():
    """Run the demo."""
    try:
        demo = DoDDoRWorkflowDemo()
        demo.run_demo()
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
