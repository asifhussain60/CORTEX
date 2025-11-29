#!/usr/bin/env python3
"""
CORTEX Documentation Generator - Comprehensive Generation Script
Generates all CORTEX documentation including diagrams, API docs, and guides.
"""

from pathlib import Path
from typing import List, Dict, Any
import sys
import json
from datetime import datetime

# Add CORTEX root to path
cortex_root = Path(__file__).parent.parent
sys.path.insert(0, str(cortex_root))

def generate_all_documentation() -> Dict[str, Any]:
    """Generate all CORTEX documentation and return results."""
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'generated_files': [],
        'components': {},
        'summary': {}
    }
    
    print("🧠 CORTEX Documentation Generation")
    print("=" * 60)
    print()
    
    # Component 1: EPMO Documentation
    try:
        print("📊 Generating EPMO Documentation...")
        from src.epmo.documentation import generate_documentation
        
        epmo_result = generate_documentation(
            epmo_path=Path('src/epmo'),
            project_root=Path('.')
        )
        
        if epmo_result.get('status') == 'success':
            results['components']['epmo'] = {
                'status': 'success',
                'markdown_content_lines': len(epmo_result.get('markdown_content', '').split('\n')),
                'diagrams': len(epmo_result.get('mermaid_diagrams', [])),
                'image_prompts': len(epmo_result.get('image_prompts', [])),
                'visual_stats': epmo_result.get('visual_stats', {})
            }
            
            # Save EPMO markdown with UTF-8 encoding
            epmo_doc_path = Path('docs/architecture/epmo-documentation.md')
            epmo_doc_path.parent.mkdir(parents=True, exist_ok=True)
            epmo_doc_path.write_text(epmo_result.get('markdown_content', ''), encoding='utf-8')
            results['generated_files'].append(str(epmo_doc_path))
            
            print(f"  ✅ EPMO documentation generated: {epmo_doc_path}")
            print(f"     Diagrams: {len(epmo_result.get('mermaid_diagrams', []))}")
            print(f"     Image prompts: {len(epmo_result.get('image_prompts', []))}")
        else:
            results['components']['epmo'] = {'status': 'error', 'error': epmo_result.get('error')}
            print(f"  ❌ EPMO generation failed: {epmo_result.get('error')}")
            
    except Exception as e:
        results['components']['epmo'] = {'status': 'error', 'error': str(e)}
        print(f"  ⚠️ EPMO generation skipped: {e}")
    
    print()
    
    # Component 2: Mermaid Diagrams
    try:
        print("📈 Generating Mermaid Diagrams...")
        from src.epmo.documentation.mermaid_generator import MultiModalDiagramGenerator
        from src.epmo.documentation.models import EPMDocumentationModel
        
        # Create minimal model for diagram generation
        model = EPMDocumentationModel(
            module_name="CORTEX",
            module_path="src/",
            description="CORTEX Documentation Diagrams"
        )
        
        generator = MultiModalDiagramGenerator()
        diagrams_result = generator.generate_all_diagrams(model)
        
        if isinstance(diagrams_result, list) and len(diagrams_result) > 0:
            results['components']['diagrams'] = {
                'status': 'success',
                'count': len(diagrams_result),
                'types': [d.diagram_type if hasattr(d, 'diagram_type') else 'unknown' for d in diagrams_result]
            }
            
            # Save diagrams
            for idx, diagram in enumerate(diagrams_result):
                if hasattr(diagram, 'mermaid_syntax'):
                    diagram_path = Path(f'docs/diagrams/diagram-{idx+1}.mmd')
                    diagram_path.parent.mkdir(parents=True, exist_ok=True)
                    diagram_path.write_text(diagram.mermaid_syntax, encoding='utf-8')
                    results['generated_files'].append(str(diagram_path))
            
            print(f"  ✅ Generated {len(diagrams_result)} Mermaid diagrams")
        else:
            results['components']['diagrams'] = {'status': 'partial', 'message': 'No diagrams generated'}
            print(f"  ⚠️ No diagrams generated")
            
    except Exception as e:
        results['components']['diagrams'] = {'status': 'error', 'error': str(e)}
        print(f"  ❌ Diagram generation error: {e}")
    
    print()
    
    # Component 3: MkDocs Site Build
    try:
        print("📚 Building MkDocs Site...")
        import subprocess
        
        # Check if mkdocs.yml exists
        if Path('mkdocs.yml').exists():
            build_result = subprocess.run(
                ['mkdocs', 'build', '--clean'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if build_result.returncode == 0:
                results['components']['mkdocs'] = {
                    'status': 'success',
                    'site_dir': 'site/',
                    'output': build_result.stdout
                }
                print(f"  ✅ MkDocs site built successfully")
                results['generated_files'].append('site/')
            else:
                results['components']['mkdocs'] = {
                    'status': 'error',
                    'error': build_result.stderr
                }
                print(f"  ❌ MkDocs build failed: {build_result.stderr[:200]}")
        else:
            results['components']['mkdocs'] = {'status': 'skipped', 'reason': 'mkdocs.yml not found'}
            print(f"  ⚠️ MkDocs configuration not found")
            
    except subprocess.TimeoutExpired:
        results['components']['mkdocs'] = {'status': 'error', 'error': 'Build timeout (>60s)'}
        print(f"  ❌ MkDocs build timeout")
    except Exception as e:
        results['components']['mkdocs'] = {'status': 'error', 'error': str(e)}
        print(f"  ❌ MkDocs build error: {e}")
    
    print()
    
    # Component 4: API Documentation
    try:
        print("📖 Generating API Documentation...")
        from src.operations.update_documentation import DocumentationGenerator
        
        doc_gen = DocumentationGenerator(cortex_root=Path('.'))
        doc_gen.load_config()
        api_result = doc_gen.generate_api_reference()
        
        if api_result.get('success'):
            results['components']['api_docs'] = {
                'status': 'success',
                'modules_documented': api_result.get('modules_documented', 0)
            }
            print(f"  ✅ API documentation generated")
            
            # API docs saved by DocumentationGenerator
            if api_result.get('output_path'):
                results['generated_files'].append(api_result['output_path'])
        else:
            results['components']['api_docs'] = {'status': 'error', 'error': api_result.get('error')}
            print(f"  ❌ API generation failed")
            
    except Exception as e:
        results['components']['api_docs'] = {'status': 'error', 'error': str(e)}
        print(f"  ❌ API documentation error: {e}")
    
    print()
    
    # Summary
    print("=" * 60)
    print("📋 DOCUMENTATION GENERATION SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for c in results['components'].values() if c.get('status') == 'success')
    total = len(results['components'])
    
    results['summary'] = {
        'total_components': total,
        'successful': successful,
        'failed': total - successful,
        'files_generated': len(results['generated_files']),
        'completion_percentage': round((successful / total) * 100, 1) if total > 0 else 0
    }
    
    print(f"\n✅ Successful: {successful}/{total} components")
    print(f"📁 Files generated: {len(results['generated_files'])}")
    print(f"✨ Completion: {results['summary']['completion_percentage']}%")
    
    return results


def main():
    """Main entry point for documentation generation."""
    try:
        results = generate_all_documentation()
        
        # Save results to JSON
        results_path = Path('cortex-brain/documents/analysis/doc-generation-results.json')
        results_path.parent.mkdir(parents=True, exist_ok=True)
        results_path.write_text(json.dumps(results, indent=2))
        
        print(f"\n📊 Results saved to: {results_path}")
        
        # Print file list
        if results['generated_files']:
            print("\n📄 GENERATED FILES:")
            for idx, file_path in enumerate(results['generated_files'], 1):
                print(f"  {idx}. {file_path}")
        
        return 0 if results['summary']['successful'] > 0 else 1
        
    except Exception as e:
        print(f"\n❌ Documentation generation failed: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
