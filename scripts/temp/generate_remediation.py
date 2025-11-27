#!/usr/bin/env python3
"""Generate detailed auto-remediation suggestions."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.operations.modules.admin.system_alignment_orchestrator import SystemAlignmentOrchestrator

def main():
    orchestrator = SystemAlignmentOrchestrator({'project_root': Path.cwd()})
    report = orchestrator.run_full_validation()
    
    # Create remediation directory
    remediation_dir = Path("cortex-brain/documents/remediation/2025-11-25")
    remediation_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n🔧 Generating {len(report.remediation_suggestions)} auto-remediation suggestions...\n")
    
    # Group by type
    wiring_suggestions = [s for s in report.remediation_suggestions if s.suggestion_type == "wiring"]
    test_suggestions = [s for s in report.remediation_suggestions if s.suggestion_type == "test"]
    doc_suggestions = [s for s in report.remediation_suggestions if s.suggestion_type == "documentation"]
    
    # 1. Wiring suggestions
    if wiring_suggestions:
        wiring_file = remediation_dir / "wiring-templates.yaml"
        print(f"📝 Generating {len(wiring_suggestions)} wiring templates...")
        
        with open(wiring_file, "w", encoding="utf-8") as f:
            f.write("# Auto-Generated Wiring Templates\n")
            f.write("# Add these to cortex-brain/response-templates.yaml\n\n")
            
            for suggestion in wiring_suggestions:
                f.write(f"\n# === {suggestion.feature_name} ===\n")
                f.write(suggestion.content)
                f.write("\n\n")
        
        print(f"   ✅ Saved to {wiring_file}")
    
    # 2. Test suggestions
    if test_suggestions:
        print(f"\n🧪 Generating {len(test_suggestions)} test skeletons...")
        
        for suggestion in test_suggestions:
            if suggestion.file_path:
                test_file = Path(suggestion.file_path)
                test_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(test_file, "w", encoding="utf-8") as f:
                    f.write(suggestion.content)
                
                print(f"   ✅ {test_file.relative_to(Path.cwd())}")
    
    # 3. Documentation suggestions
    if doc_suggestions:
        print(f"\n📚 Generating {len(doc_suggestions)} documentation templates...")
        
        for suggestion in doc_suggestions:
            if suggestion.file_path:
                doc_file = Path(suggestion.file_path)
                doc_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(doc_file, "w", encoding="utf-8") as f:
                    f.write(suggestion.content)
                
                print(f"   ✅ {doc_file.relative_to(Path.cwd())}")
    
    # Summary
    print(f"\n✨ Remediation generation complete!")
    print(f"\n📊 Summary:")
    print(f"   • Wiring templates: {len(wiring_suggestions)}")
    print(f"   • Test skeletons: {len(test_suggestions)}")
    print(f"   • Documentation: {len(doc_suggestions)}")
    print(f"\n📁 All files saved to: {remediation_dir}")
    
    # Next steps
    print(f"\n🚀 Next Steps:")
    print(f"   1. Review generated test skeletons in tests/")
    print(f"   2. Review wiring templates in {remediation_dir}/wiring-templates.yaml")
    print(f"   3. Review documentation in cortex-brain/documents/")
    print(f"   4. Run tests to verify functionality")
    print(f"   5. Re-run alignment: python run_alignment.py")

if __name__ == '__main__':
    main()
