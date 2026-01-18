#!/usr/bin/env python3
"""
RA Domain Comprehensive Analysis Script
Extracts ALL information from C# codebase: classes, methods, dependencies, business rules

SCANNER CONFIGURATION (Updated from Structural Analysis):
- MAX_DEPTH: 5 levels (skip deeper Generated/ folders)
- SKIP_PATTERNS: ['**/Generated/**', '**/obj/**', '**/bin/**']
- TRAVERSAL: Breadth-first (most files at depth 2-3)
- BATCH_SIZE: Adaptive (9-10 files for large folders)
"""

import os
import json
from pathlib import Path
from tree_sitter import Language, Parser
import tree_sitter_c_sharp as tscsharp
from lxml import etree
from collections import defaultdict, deque
import re

# Scanner Configuration (from 02-structural-depth-analysis.md)
MAX_DEPTH = 5
SKIP_PATTERNS = ['**/Generated/**', '**/obj/**', '**/bin/**', '**/OpenApi/**']
BATCH_SIZE_LARGE = 9  # For folders with 40+ files (Entities, DTOs)
BATCH_SIZE_MEDIUM = 10  # For folders with 15-40 files (Services)

# Initialize C# parser
CS_LANGUAGE = Language(tscsharp.language())
parser = Parser(CS_LANGUAGE)

def should_skip_path(path):
    """Check if path matches skip patterns"""
    path_str = str(path)
    return any([
        'Generated' in path_str,
        'obj' in path_str,
        'bin' in path_str,
        'OpenApi' in path_str
    ])

def get_folder_depth(base_path, current_path):
    """Calculate depth from base path"""
    try:
        relative = current_path.relative_to(base_path)
        return len(relative.parts)
    except ValueError:
        return 0

def extract_xml_comments(code_bytes, line_number):
    """Extract XML documentation comments before a declaration"""
    lines = code_bytes.decode('utf-8', errors='ignore').split('\n')
    comments = []
    
    # Look backwards from line_number for XML comments
    for i in range(line_number - 1, max(0, line_number - 20), -1):
        line = lines[i].strip()
        if line.startswith('///'):
            comments.insert(0, line[3:].strip())
        elif line and not line.startswith('//'):
            break
    
    return ' '.join(comments) if comments else None

def analyze_csharp_file(filepath):
    """Comprehensive C# file analysis"""
    with open(filepath, 'rb') as f:
        code = f.read()
        tree = parser.parse(code)
    
    result = {
        'file': str(filepath),
        'namespaces': [],
        'classes': [],
        'interfaces': [],
        'enums': [],
        'methods': [],
        'properties': [],
        'attributes': []
    }
    
    def get_node_text(node):
        return node.text.decode('utf-8', errors='ignore') if node.text else ''
    
    def traverse(node, depth=0):
        node_type = node.type
        
        # Extract namespace
        if node_type == 'namespace_declaration':
            ns_name = next(
                (get_node_text(child) for child in node.children 
                 if child.type == 'identifier' or child.type == 'qualified_name'),
                'Unknown'
            )
            result['namespaces'].append(ns_name)
        
        # Extract class
        elif node_type == 'class_declaration':
            class_info = {
                'name': next((get_node_text(child) for child in node.children if child.type == 'identifier'), 'Unknown'),
                'line': node.start_point[0] + 1,
                'modifiers': [get_node_text(child) for child in node.children if child.type in ['public', 'private', 'protected', 'internal', 'static', 'abstract', 'sealed']],
                'xml_doc': extract_xml_comments(code, node.start_point[0])
            }
            
            # Check for base classes/interfaces
            base_list = next((child for child in node.children if child.type == 'base_list'), None)
            if base_list:
                class_info['inherits'] = [get_node_text(t) for t in base_list.children if t.type != ':' and t.type != ',']
            
            result['classes'].append(class_info)
        
        # Extract interface
        elif node_type == 'interface_declaration':
            result['interfaces'].append({
                'name': next((get_node_text(child) for child in node.children if child.type == 'identifier'), 'Unknown'),
                'line': node.start_point[0] + 1
            })
        
        # Extract enum
        elif node_type == 'enum_declaration':
            enum_name = next((get_node_text(child) for child in node.children if child.type == 'identifier'), 'Unknown')
            enum_members = []
            
            for child in node.children:
                if child.type == 'enum_member_declaration':
                    member_name = next((get_node_text(c) for c in child.children if c.type == 'identifier'), 'Unknown')
                    enum_members.append(member_name)
            
            result['enums'].append({
                'name': enum_name,
                'line': node.start_point[0] + 1,
                'members': enum_members
            })
        
        # Extract method
        elif node_type == 'method_declaration':
            method_info = {
                'name': next((get_node_text(child) for child in node.children if child.type == 'identifier'), 'Unknown'),
                'line': node.start_point[0] + 1,
                'modifiers': [get_node_text(child) for child in node.children if child.type in ['public', 'private', 'protected', 'internal', 'static', 'async', 'virtual', 'override']],
                'xml_doc': extract_xml_comments(code, node.start_point[0])
            }
            
            # Extract parameters
            param_list = next((child for child in node.children if child.type == 'parameter_list'), None)
            if param_list:
                params = []
                for param in param_list.children:
                    if param.type == 'parameter':
                        param_type = next((get_node_text(child) for child in param.children if child.type not in ['identifier', ',']), 'Unknown')
                        param_name = next((get_node_text(child) for child in param.children if child.type == 'identifier'), 'Unknown')
                        params.append({'type': param_type, 'name': param_name})
                method_info['parameters'] = params
            
            result['methods'].append(method_info)
        
        # Extract property
        elif node_type == 'property_declaration':
            prop_type = next((get_node_text(child) for child in node.children if child.type not in ['identifier', 'accessor_list', 'public', 'private', 'protected']), 'Unknown')
            prop_name = next((get_node_text(child) for child in node.children if child.type == 'identifier'), 'Unknown')
            
            result['properties'].append({
                'name': prop_name,
                'type': prop_type,
                'line': node.start_point[0] + 1
            })
        
        # Extract attributes
        elif node_type == 'attribute':
            attr_name = get_node_text(node.children[0]) if node.children else 'Unknown'
            result['attributes'].append({
                'name': attr_name,
                'line': node.start_point[0] + 1
            })
        
        # Traverse children
        for child in node.children:
            traverse(child, depth + 1)
    
    traverse(tree.root_node)
    
    return result

def analyze_csproj(filepath):
    """Extract all metadata from .csproj file"""
    tree = etree.parse(str(filepath))
    root = tree.getroot()
    
    # Remove namespace to simplify XPath queries
    for elem in root.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}')[1]
    
    result = {
        'project': str(filepath),
        'target_framework': None,
        'packages': [],
        'project_references': []
    }
    
    # Target framework
    tf = root.find('.//TargetFramework')
    if tf is not None:
        result['target_framework'] = tf.text
    
    # NuGet packages
    for pkg in root.findall('.//PackageReference'):
        result['packages'].append({
            'name': pkg.get('Include'),
            'version': pkg.get('Version')
        })
    
    # Project references
    for proj_ref in root.findall('.//ProjectReference'):
        result['project_references'].append(proj_ref.get('Include'))
    
    return result

def find_business_terms(code_text):
    """Extract potential business domain terms from code"""
    # Look for capitalized terms (likely domain concepts)
    words = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b', code_text)
    
    # Filter common programming terms
    programming_terms = {'String', 'Integer', 'Decimal', 'DateTime', 'Boolean', 'List', 'Dictionary', 
                        'Task', 'Async', 'Void', 'Public', 'Private', 'Static', 'Class', 'Interface'}
    
    business_terms = [w for w in words if w not in programming_terms]
    
    # Count frequency
    term_freq = defaultdict(int)
    for term in business_terms:
        term_freq[term] += 1
    
    return term_freq

def main():
    repo_path = Path('C:/PROJECTS/Product.Example')
    output_path = Path('C:/PROJECTS/CORTEX/cortex-brain/admin/RA-Domain/ast-outputs')
    output_path.mkdir(parents=True, exist_ok=True)
    
    results = {
        'files': [],
        'projects': [],
        'summary': {
            'total_files': 0,
            'total_classes': 0,
            'total_methods': 0,
            'total_projects': 0
        },
        'business_terms': defaultdict(int)
    }
    
    print("=" * 80)
    print("RA DOMAIN COMPREHENSIVE ANALYSIS")
    print("=" * 80)
    print(f"Scanner Config: MAX_DEPTH={MAX_DEPTH}, SKIP_PATTERNS={SKIP_PATTERNS}")
    print(f"Traversal: Breadth-first (optimized for avg depth 2.98)")
    
    # Collect C# files with depth filtering (breadth-first)
    print("\n[1/4] Collecting C# files (breadth-first, depth-aware)...")
    cs_files = []
    skipped_files = []
    
    # Use breadth-first queue
    queue = deque([(repo_path, 0)])  # (path, depth)
    
    while queue:
        current_path, depth = queue.popleft()
        
        if depth > MAX_DEPTH:
            continue
        
        if not current_path.is_dir():
            continue
        
        if should_skip_path(current_path):
            skipped_files.append(str(current_path))
            continue
        
        try:
            for item in current_path.iterdir():
                if item.is_file() and item.suffix == '.cs':
                    cs_files.append(item)
                elif item.is_dir():
                    queue.append((item, depth + 1))
        except PermissionError:
            print(f"  PERMISSION DENIED: {current_path}")
    
    print(f"Found {len(cs_files)} C# files (depth <= {MAX_DEPTH})")
    print(f"Skipped {len(skipped_files)} paths (Generated/, obj/, bin/)")
    
    # Analyze all C# files
    print("\n[2/4] Analyzing C# files...")
    
    for i, cs_file in enumerate(cs_files, 1):
        if i % 50 == 0:
            print(f"  Processed {i}/{len(cs_files)} files...")
        
        try:
            analysis = analyze_csharp_file(cs_file)
            results['files'].append(analysis)
            
            results['summary']['total_classes'] += len(analysis['classes'])
            results['summary']['total_methods'] += len(analysis['methods'])
            
            # Extract business terms
            with open(cs_file, 'r', encoding='utf-8', errors='ignore') as f:
                code_text = f.read()
                terms = find_business_terms(code_text)
                for term, count in terms.items():
                    results['business_terms'][term] += count
        
        except Exception as e:
            print(f"  ERROR analyzing {cs_file}: {e}")
    
    results['summary']['total_files'] = len(results['files'])
    
    # Analyze all project files
    print("\n[3/4] Analyzing .csproj files...")
    csproj_files = list(repo_path.rglob('*.csproj'))
    print(f"Found {len(csproj_files)} project files")
    
    for csproj in csproj_files:
        try:
            project_analysis = analyze_csproj(csproj)
            results['projects'].append(project_analysis)
        except Exception as e:
            print(f"  ERROR analyzing {csproj}: {e}")
    
    results['summary']['total_projects'] = len(results['projects'])
    
    # Save results
    print("\n[4/4] Saving results...")
    
    # Main analysis file
    output_file = output_path / 'complete-csharp-analysis.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    
    # Business terms (top 100)
    top_terms = sorted(results['business_terms'].items(), key=lambda x: x[1], reverse=True)[:100]
    terms_file = output_path / 'business-terms.json'
    with open(terms_file, 'w', encoding='utf-8') as f:
        json.dump(dict(top_terms), f, indent=2)
    
    # Summary report
    summary_file = output_path / 'analysis-summary.txt'
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("RA DOMAIN ANALYSIS SUMMARY\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total C# Files:    {results['summary']['total_files']}\n")
        f.write(f"Total Classes:     {results['summary']['total_classes']}\n")
        f.write(f"Total Methods:     {results['summary']['total_methods']}\n")
        f.write(f"Total Projects:    {results['summary']['total_projects']}\n\n")
        f.write("Top 20 Business Terms:\n")
        f.write("-" * 40 + "\n")
        for term, count in top_terms[:20]:
            f.write(f"  {term:30} {count:5}\n")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)
    print(f"\nResults saved to:")
    print(f"  - {output_file}")
    print(f"  - {terms_file}")
    print(f"  - {summary_file}")
    print(f"\nSummary:")
    print(f"  Total C# Files:    {results['summary']['total_files']}")
    print(f"  Total Classes:     {results['summary']['total_classes']}")
    print(f"  Total Methods:     {results['summary']['total_methods']}")
    print(f"  Total Projects:    {results['summary']['total_projects']}")
    print(f"\nTop 10 Business Terms:")
    for term, count in top_terms[:10]:
        print(f"  {term:30} {count:5}")
    print()

if __name__ == '__main__':
    main()
