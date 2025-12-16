#!/usr/bin/env python3
"""
Batch Entity Analysis Script
Analyzes specific C# entity files from input list
"""

import json
import sys
from pathlib import Path
from tree_sitter import Language, Parser
import tree_sitter_c_sharp as tscsharp

# Initialize C# parser
CS_LANGUAGE = Language(tscsharp.language())
parser = Parser(CS_LANGUAGE)

def extract_xml_comments(code_bytes, line_number):
    """Extract XML documentation comments before a declaration"""
    lines = code_bytes.decode('utf-8', errors='ignore').split('\n')
    comments = []
    
    for i in range(line_number - 1, max(0, line_number - 20), -1):
        line = lines[i].strip()
        if line.startswith('///'):
            comments.insert(0, line[3:].strip())
        elif line and not line.startswith('//'):
            break
    
    return ' '.join(comments) if comments else None

def get_node_text(node):
    """Extract text from tree-sitter node"""
    return node.text.decode('utf-8', errors='ignore') if node.text else ''

def analyze_entity_file(filepath):
    """Extract entity metadata: class name, properties, navigation properties, attributes"""
    with open(filepath, 'rb') as f:
        code = f.read()
        tree = parser.parse(code)
    
    result = {
        'file': str(filepath),
        'filename': Path(filepath).name,
        'namespace': None,
        'classes': []
    }
    
    def traverse(node):
        node_type = node.type
        
        # Extract namespace
        if node_type == 'namespace_declaration':
            ns_name = next(
                (get_node_text(child) for child in node.children 
                 if child.type == 'identifier' or child.type == 'qualified_name'),
                None
            )
            if ns_name:
                result['namespace'] = ns_name
        
        # Extract class
        elif node_type == 'class_declaration':
            class_name = next((get_node_text(child) for child in node.children if child.type == 'identifier'), None)
            if not class_name:
                return
            
            class_info = {
                'name': class_name,
                'line': node.start_point[0] + 1,
                'modifiers': [],
                'inherits': [],
                'properties': [],
                'navigation_properties': [],
                'attributes': [],
                'xml_doc': extract_xml_comments(code, node.start_point[0])
            }
            
            # Extract modifiers
            for child in node.children:
                if child.type in ['public', 'private', 'protected', 'internal', 'static', 'abstract', 'sealed', 'partial']:
                    class_info['modifiers'].append(get_node_text(child))
            
            # Extract base classes/interfaces
            base_list = next((child for child in node.children if child.type == 'base_list'), None)
            if base_list:
                for child in base_list.children:
                    if child.type != ':' and child.type != ',':
                        base_type = get_node_text(child).strip()
                        if base_type:
                            class_info['inherits'].append(base_type)
            
            # Extract properties
            for child in node.children:
                if child.type == 'property_declaration':
                    prop_name = next((get_node_text(c) for c in child.children if c.type == 'identifier'), None)
                    prop_type = None
                    
                    # Find type node
                    for c in child.children:
                        if c.type not in ['identifier', 'accessor_list', 'public', 'private', 'protected', 'internal', 'virtual', 'override']:
                            prop_type = get_node_text(c).strip()
                            break
                    
                    if prop_name and prop_type:
                        prop_info = {
                            'name': prop_name,
                            'type': prop_type,
                            'line': child.start_point[0] + 1,
                            'is_navigation': False,
                            'is_collection': False
                        }
                        
                        # Detect navigation properties (collections or entity references)
                        if 'ICollection' in prop_type or 'IList' in prop_type or 'List<' in prop_type:
                            prop_info['is_navigation'] = True
                            prop_info['is_collection'] = True
                        elif prop_type and not prop_type.startswith(('int', 'string', 'bool', 'decimal', 'DateTime', 'Guid')):
                            # Likely an entity reference
                            prop_info['is_navigation'] = True
                        
                        if prop_info['is_navigation']:
                            class_info['navigation_properties'].append(prop_info)
                        else:
                            class_info['properties'].append(prop_info)
            
            # Extract class-level attributes
            for child in node.children:
                if child.type == 'attribute_list':
                    for attr_child in child.children:
                        if attr_child.type == 'attribute':
                            attr_name = get_node_text(attr_child).strip()
                            if attr_name:
                                class_info['attributes'].append(attr_name)
            
            result['classes'].append(class_info)
        
        # Traverse children
        for child in node.children:
            traverse(child)
    
    traverse(tree.root_node)
    
    return result

def main():
    if len(sys.argv) < 3:
        print("Usage: python analyze_batch_entities.py <input_file_list.txt> <output.json>")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])
    
    print(f"Reading file list from: {input_file}")
    
    # Read file paths
    with open(input_file, 'r', encoding='utf-8') as f:
        file_paths = [line.strip() for line in f if line.strip()]
    
    print(f"Found {len(file_paths)} files to analyze")
    
    # Analyze each file
    results = []
    for i, filepath in enumerate(file_paths, 1):
        print(f"  [{i}/{len(file_paths)}] Analyzing {Path(filepath).name}...")
        try:
            entity_data = analyze_entity_file(filepath)
            results.append(entity_data)
        except Exception as e:
            print(f"    ERROR: {e}")
    
    # Save results
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    summary = {
        'batch_info': {
            'name': 'Batch 3.1 - First 10 Entities',
            'total_files': len(results),
            'total_classes': sum(len(r['classes']) for r in results),
            'total_properties': sum(sum(len(c['properties']) for c in r['classes']) for r in results),
            'total_navigation_properties': sum(sum(len(c['navigation_properties']) for c in r['classes']) for r in results)
        },
        'entities': results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✅ Analysis complete!")
    print(f"   Output: {output_file}")
    print(f"   Files analyzed: {summary['batch_info']['total_files']}")
    print(f"   Classes found: {summary['batch_info']['total_classes']}")
    print(f"   Properties: {summary['batch_info']['total_properties']}")
    print(f"   Navigation properties: {summary['batch_info']['total_navigation_properties']}")

if __name__ == '__main__':
    main()
