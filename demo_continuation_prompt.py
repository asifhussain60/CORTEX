"""
DEMONSTRATION: Session Management Continuation Prompt System
=============================================================

This script demonstrates the continuation prompt system in action.
Run this to see how the system automatically generates session handoff prompts.
"""

from pathlib import Path
from src.orchestration_4_0.base.base_orchestrator import BaseOrchestrator
import time


class DemoOrchestrator(BaseOrchestrator):
    """Demo orchestrator to showcase continuation prompt system."""
    
    def _setup(self, context):
        print("🎭 Setting up demo orchestrator...")
    
    def _register_phases(self):
        print("📋 Registering phases...")
        self.phase_manager.register_phase("phase1", "Data Collection", required=True)
        self.phase_manager.register_phase("phase2", "Analysis", required=True)
        self.phase_manager.register_phase("phase3", "Report Generation", required=True)
        self.phase_manager.register_phase("phase4", "Deployment", required=True)
    
    def _execute_phase(self, phase_name, context):
        print(f"▶️  Executing {phase_name}...")
        time.sleep(0.5)
        return {"status": "success", "phase": phase_name}
    
    def _teardown(self, context):
        print("🧹 Cleaning up...")
        return {"status": "cleanup_complete"}


def main():
    """Run the demonstration."""
    print("\n" + "="*70)
    print("🔄 SESSION MANAGEMENT CONTINUATION PROMPT DEMONSTRATION")
    print("="*70 + "\n")
    
    # Create demo plan directory
    demo_dir = Path("cortex-brain/documents/planning/active/demo-session-mgmt")
    demo_dir.mkdir(parents=True, exist_ok=True)
    (demo_dir / "tracking").mkdir(exist_ok=True)
    (demo_dir / "artifacts").mkdir(exist_ok=True)
    
    # Create some demo artifacts
    (demo_dir / "artifacts" / "data.json").write_text('{"sample": "data"}')
    (demo_dir / "artifacts" / "report.md").write_text("# Demo Report\n\nSample content.")
    
    print("📁 Demo plan directory created:")
    print(f"   {demo_dir.absolute()}\n")
    
    # Create orchestrator
    orchestrator = DemoOrchestrator(
        name="demo_session_mgmt",
        config={
            "token_warning_threshold": 2000,  # Low threshold for demo
            "continuation_prompt_enabled": True
        }
    )
    
    # Register phases
    orchestrator._register_phases()
    
    print("\n📊 Executing phases...\n")
    
    # Execute phases 1 and 2
    for phase in ["phase1", "phase2"]:
        orchestrator.phase_manager.start_phase(phase)
        orchestrator._execute_phase(phase, {})
        orchestrator.phase_manager.complete_phase(phase)
        print(f"✅ {phase} completed\n")
    
    # Check token usage
    print("🔍 Checking token usage...\n")
    token_status = orchestrator.check_token_usage()
    print(f"   Estimated tokens: {token_status['estimated_tokens']}")
    print(f"   Threshold: {token_status['threshold']}")
    print(f"   Percentage: {token_status['percentage']}%")
    print(f"   Should warn: {'⚠️  YES' if token_status['should_warn'] else '✅ NO'}\n")
    
    # Generate continuation prompt
    print("📝 Generating continuation prompt...\n")
    result = orchestrator.update_continuation_prompt(
        plan_name="demo-session-mgmt",
        plan_id="demo-123",
        plan_dir=demo_dir,
        current_phase={"number": 2, "name": "Analysis", "duration": "3h"},
        next_phase={"number": 3, "name": "Report Generation", "duration": "2h"}
    )
    
    if result:
        prompt_file = demo_dir / "tracking" / "CONTINUATION-PROMPT.md"
        print(f"✅ Continuation prompt generated!")
        print(f"   Location: {prompt_file.absolute()}\n")
        
        # Display the prompt
        print("="*70)
        print("📄 GENERATED CONTINUATION PROMPT:")
        print("="*70 + "\n")
        
        content = prompt_file.read_text(encoding="utf-8")
        print(content)
        
        print("\n" + "="*70)
        print("✨ DEMONSTRATION COMPLETE")
        print("="*70)
        print("\n💡 TIP: Copy the continuation instructions above to resume")
        print("   this plan in a new Copilot Chat session!")
        print(f"\n📂 View the full prompt file at:")
        print(f"   {prompt_file.absolute()}\n")
    else:
        print("❌ Failed to generate continuation prompt\n")


if __name__ == "__main__":
    main()
