#!/usr/bin/env python3
"""
AC-TEMPLATE-007: Template Layer Integration
Integrate 3-layer template system into all orchestrators
"""

from pathlib import Path
import re

def integrate_template_renderer(orchestrator_file: Path) -> bool:
    """Add LayeredTemplateRenderer import and usage to orchestrator."""
    content = orchestrator_file.read_text()
    
    # Check if already integrated
    if 'LayeredTemplateRenderer' in content:
        return False
    
    # Find import section
    import_section_end = 0
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('from ') or line.startswith('import '):
            import_section_end = i + 1
    
    # Add import
    template_import = "from src.infrastructure.layered_template_renderer import LayeredTemplateRenderer"
    lines.insert(import_section_end, template_import)
    
    # Find orchestrator class __init__
    class_pattern = r'class (\w+Orchestrator|\w+Master).*?:'
    init_pattern = r'def __init__\(self.*?\):'
    
    # Add template renderer initialization
    init_found = False
    for i, line in enumerate(lines):
        if re.match(init_pattern, line.strip()):
            # Find end of __init__ body
            indent = len(line) - len(line.lstrip())
            j = i + 1
            while j < len(lines) and (not lines[j].strip() or len(lines[j]) - len(lines[j].lstrip()) > indent):
                j += 1
            
            # Insert template renderer initialization
            template_init = ' ' * (indent + 4) + "self.template_renderer = LayeredTemplateRenderer()"
            lines.insert(j, template_init)
            init_found = True
            break
    
    if not init_found:
        return False
    
    # Write back
    orchestrator_file.write_text('\n'.join(lines))
    return True

def main():
    """Integrate LayeredTemplateRenderer into all orchestrators."""
    orchestrator_dir = Path('src/orchestrators')
    orchestrator_files = []
    
    # Find all orchestrator Python files
    for py_file in orchestrator_dir.rglob('*.py'):
        if py_file.stem.endswith('_orchestrator') or py_file.stem.endswith('_master'):
            orchestrator_files.append(py_file)
    
    integrated = []
    skipped = []
    
    for orch_file in orchestrator_files:
        try:
            if integrate_template_renderer(orch_file):
                integrated.append(orch_file.name)
            else:
                skipped.append(orch_file.name)
        except Exception as e:
            print(f"⚠️  Error processing {orch_file.name}: {e}")
    
    print(f"✅ AC-TEMPLATE-007 Integration Complete")
    print(f"   Integrated: {len(integrated)} orchestrators")
    print(f"   Skipped (already integrated): {len(skipped)}")
    
    if integrated:
        print(f"\n📝 Integrated files:")
        for f in integrated[:10]:
            print(f"   • {f}")
        if len(integrated) > 10:
            print(f"   ... and {len(integrated) - 10} more")

if __name__ == "__main__":
    main()
